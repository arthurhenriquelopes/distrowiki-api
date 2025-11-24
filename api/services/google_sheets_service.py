"""
Serviço de integração com Google Sheets.

Busca dados de distribuições Linux diretamente do Google Sheets.
Utiliza API pública sem autenticação (sheets públicas) para leitura.
Utiliza Service Account para escrita (atualização).
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
import os
import json
from ..models.distro import DistroMetadata, DistroFamily, DesktopEnvironment


logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Serviço para buscar e atualizar dados do Google Sheets."""
    
    # IDs e configuração
    SHEET_ID = "1ObKRlMRWtABnau6lZTT6en1BajVkV6m2LtLhXEHZ_Zk"
    SHEET_NAME = "distrowiki_complete"
    
    # URL da API do Google Sheets (v4)
    SHEETS_API_URL = "https://sheets.googleapis.com/v4/spreadsheets"
    
    # Headers para requisição
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    TIMEOUT = 30.0
    
    # Mapeamento de famílias
    FAMILY_MAPPING = {
        "debian": DistroFamily.DEBIAN,
        "ubuntu": DistroFamily.UBUNTU,
        "fedora": DistroFamily.FEDORA,
        "red hat": DistroFamily.FEDORA,
        "rhel": DistroFamily.FEDORA,
        "arch": DistroFamily.ARCH,
        "arch linux": DistroFamily.ARCH,
        "opensuse": DistroFamily.OPENSUSE,
        "suse": DistroFamily.OPENSUSE,
        "gentoo": DistroFamily.GENTOO,
        "slackware": DistroFamily.SLACKWARE,
        "independent": DistroFamily.INDEPENDENT,
    }
    
    # Mapeamento de Desktop Environments
    DE_MAPPING = {
        "gnome": DesktopEnvironment.GNOME,
        "kde": DesktopEnvironment.KDE,
        "plasma": DesktopEnvironment.KDE,
        "xfce": DesktopEnvironment.XFCE,
        "mate": DesktopEnvironment.MATE,
        "cinnamon": DesktopEnvironment.CINNAMON,
        "lxde": DesktopEnvironment.LXDE,
        "lxqt": DesktopEnvironment.LXQT,
        "budgie": DesktopEnvironment.BUDGIE,
        "pantheon": DesktopEnvironment.PANTHEON,
        "deepin": DesktopEnvironment.DEEPIN,
        "i3": DesktopEnvironment.I3,
        "sway": DesktopEnvironment.SWAY,
    }
    
    def __init__(self):
        """Inicializa o serviço do Google Sheets."""
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={"User-Agent": self.USER_AGENT},
            follow_redirects=True,
        )
        
        # Credenciais para escrita (opcional - só se existir arquivo)
        self.credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        self.access_token = None
    
    async def close(self):
        """Fecha o cliente HTTP."""
        await self.client.aclose()
    
    async def fetch_all_distros(self) -> List[DistroMetadata]:
        """
        Busca todas as distribuições do Google Sheets.
        
        Returns:
            Lista de DistroMetadata.
        """
        try:
            logger.info(f"Buscando dados de Google Sheets (ID: {self.SHEET_ID}, Sheet: {self.SHEET_NAME})...")
            
            # Usar exportação CSV do Google Sheets (mais simples que API)
            csv_url = f"https://docs.google.com/spreadsheets/d/{self.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={self.SHEET_NAME}"
            
            response = await self.client.get(csv_url)
            response.raise_for_status()
            
            # Parse CSV
            lines = response.text.strip().split('\n')
            
            if len(lines) < 2:
                logger.warning("Google Sheets retornou dados vazios")
                return []
            
            # Primeira linha são headers
            headers = self._parse_csv_line(lines[0])
            
            distros = []
            
            # Processar cada linha (exceto header)
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                try:
                    row_data = self._parse_csv_line(line)
                    
                    # Mapear dados da linha para DistroMetadata
                    distro = self._parse_distro_row(headers, row_data)
                    
                    if distro:
                        distros.append(distro)
                        
                except Exception as e:
                    logger.warning(f"Erro ao processar linha do Sheets: {e}")
                    continue
            
            logger.info(f"Total de {len(distros)} distribuições processadas do Google Sheets")
            return distros
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do Google Sheets: {e}", exc_info=True)
            raise
    
    def _parse_csv_line(self, line: str) -> List[str]:
        """
        Parse de linha CSV com suporte a aspas.
        
        Args:
            line: Linha CSV.
        
        Returns:
            Lista de valores.
        """
        values = []
        current = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                values.append(current.strip().strip('"'))
                current = ""
            else:
                current += char
        
        values.append(current.strip().strip('"'))
        return values
    
    def _parse_distro_row(self, headers: List[str], row_data: List[str]) -> Optional[DistroMetadata]:
        """
        Converte uma linha do Sheets em DistroMetadata.
        
        Args:
            headers: Lista de nomes de colunas.
            row_data: Dados da linha.
        
        Returns:
            DistroMetadata ou None se inválido.
        """
        try:
            # Criar dicionário de dados
            data = {}
            for i, header in enumerate(headers):
                if i < len(row_data):
                    data[header.lower().strip()] = row_data[i].strip()
            
            # Extrair campos obrigatórios
            name = data.get("name", "").strip()
            if not name:
                return None
            
            # ID: usar nome normalizado
            distro_id = data.get("distro id", "").strip() or self._normalize_id(name)
            
            # Family/Base
            base = data.get("base", "").strip() or data.get("os type", "").strip()
            family = self._map_family(base)
            
            # Desktop Environments
            desktop_str = data.get("desktop", "").strip()
            desktop_environments = self._parse_desktop_environments(desktop_str)
            
            # Data de lançamento
            release_date_str = data.get("release date", "").strip()
            release_date = self._parse_date(release_date_str)
            
            # Criar objeto
            distro = DistroMetadata(
                id=distro_id,
                name=name,
                summary=data.get("description", "").strip() or None,
                description=data.get("description", "").strip() or None,
                logo_url=data.get("logo", "").strip() or None,
                family=family,
                based_on=base or None,
                origin=data.get("origin", "").strip() or None,
                desktop_environments=desktop_environments,
                category=data.get("category", "").strip() or None,
                status=data.get("status", "").strip() or None,
                latest_release_date=release_date,
                homepage=data.get("website", "").strip() or None,
                package_manager=data.get("package management", "").strip() or None,
                architecture=data.get("os type", "").strip() or None,
                rating=self._parse_rating(data.get("price (r$)", "")),
            )
            
            return distro
            
        except Exception as e:
            logger.warning(f"Erro ao parsear linha de distro: {e}")
            return None
    
    def _normalize_id(self, name: str) -> str:
        """
        Normaliza nome para ID.
        
        Args:
            name: Nome da distro.
        
        Returns:
            ID normalizado.
        """
        return name.lower().replace(" ", "-").replace("/", "-")
    
    def _map_family(self, family_str: str) -> str:
        """
        Mapeia string de família para enum.
        
        Args:
            family_str: String de família.
        
        Returns:
            Valor de DistroFamily.
        """
        if not family_str:
            return DistroFamily.INDEPENDENT
        
        family_lower = family_str.lower().strip()
        
        for key, value in self.FAMILY_MAPPING.items():
            if key in family_lower:
                return value
        
        return DistroFamily.INDEPENDENT
    
    def _parse_desktop_environments(self, desktop_str: str) -> List[str]:
        """
        Parse de ambientes gráficos separados por vírgula.
        
        Args:
            desktop_str: String de DEs.
        
        Returns:
            Lista de DEs mapeados.
        """
        if not desktop_str:
            return []
        
        des = []
        for de_item in desktop_str.split(','):
            de_lower = de_item.strip().lower()
            
            for key, value in self.DE_MAPPING.items():
                if key in de_lower:
                    if value not in des:
                        des.append(value)
                    break
        
        return des
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse de data em vários formatos.
        
        Args:
            date_str: String de data.
        
        Returns:
            datetime ou None.
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Tentar vários formatos
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Não foi possível parsear data: {date_str}")
        return None
    
    def _parse_rating(self, price_str: str) -> float:
        """
        Extrai número de preço/rating.
        
        Args:
            price_str: String de preço.
        
        Returns:
            Número como float (0-100 para compatibilidade).
        """
        if not price_str:
            return 0.0
        
        try:
            # Tentar extrair número
            import re
            match = re.search(r'[\d.]+', price_str.replace(',', '.'))
            if match:
                value = float(match.group())
                # Se for preço, converter para rating (0-100)
                if value > 100:
                    return 100.0  # Distribuições Linux são grátis/baratas
                return value
        except Exception:
            pass
        
        return 0.0
    
    # ============================================
    # MÉTODOS PARA ATUALIZAÇÃO DA PLANILHA
    # ============================================
    
    async def _get_access_token(self) -> str:
        """
        Obtém access token usando Service Account credentials.
        Suporta arquivo local OU variáveis de ambiente (Vercel).
        
        Returns:
            Access token válido para Google Sheets API.
        """
        try:
            from google.oauth2 import service_account
            import google.auth.transport.requests
            
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            
            # MÉTODO 1: Variáveis de ambiente (Vercel/Produção)
            if os.getenv("GCP_PRIVATE_KEY"):
                logger.info("Usando credenciais GCP de variáveis de ambiente")
                credentials_info = {
                    "type": "service_account",
                    "project_id": os.getenv("GCP_PROJECT_ID"),
                    "private_key": os.getenv("GCP_PRIVATE_KEY").replace('\\n', '\n'),
                    "client_email": os.getenv("GCP_SERVICE_ACCOUNT_EMAIL"),
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
                creds = service_account.Credentials.from_service_account_info(
                    credentials_info, scopes=SCOPES
                )
            
            # MÉTODO 2: Arquivo local (Desenvolvimento)
            elif self.credentials_file and os.path.exists(self.credentials_file):
                logger.info("Usando credenciais de arquivo local")
                with open(self.credentials_file, 'r') as f:
                    credentials_info = json.load(f)
                creds = service_account.Credentials.from_service_account_info(
                    credentials_info, scopes=SCOPES
                )
            
            else:
                raise ValueError(
                    "Credenciais não encontradas. Configure:\n"
                    "- Local: GOOGLE_CREDENTIALS_FILE=credentials.json\n"
                    "- Vercel: GCP_PRIVATE_KEY, GCP_PROJECT_ID, GCP_SERVICE_ACCOUNT_EMAIL"
                )
            
            # Obter token
            request = google.auth.transport.requests.Request()
            creds.refresh(request)
            
            return creds.token
            
        except Exception as e:
            logger.error(f"Erro ao obter access token: {e}")
            raise
    

    async def update_enriched_data(
        self, 
        enriched_data: List[Dict[str, Any]], 
        fields: List[Any]
    ) -> Dict[str, Any]:
        """
        Atualiza a planilha com os dados enriquecidos via Google Sheets API v4.
        
        Args:
            enriched_data: Lista de dicionários com dados enriquecidos
            fields: Lista de SheetColumn enums que foram enriquecidos
        
        Returns:
            dict com informações sobre a atualização
        """
        try:
            # Obter access token
            access_token = await self._get_access_token()
            
            # Headers com autenticação
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # 1. Buscar header da planilha (primeira linha)
            range_header = f"{self.SHEET_NAME}!1:1"
            url_get_header = f"{self.SHEETS_API_URL}/{self.SHEET_ID}/values/{range_header}"
            
            response = await self.client.get(url_get_header, headers=headers)
            response.raise_for_status()
            
            header_data = response.json()
            headers_row = header_data.get('values', [[]])[0]
            
            # Criar mapeamento de coluna para índice
            column_map = {header: idx for idx, header in enumerate(headers_row)}
            
            # 2. Buscar coluna Name para encontrar linhas
            range_names = f"{self.SHEET_NAME}!A:A"
            url_get_names = f"{self.SHEETS_API_URL}/{self.SHEET_ID}/values/{range_names}"
            
            response = await self.client.get(url_get_names, headers=headers)
            response.raise_for_status()
            
            names_data = response.json()
            names_column = names_data.get('values', [])
            
            # Criar mapeamento de nome para linha
            name_to_row = {}
            for idx, row in enumerate(names_column):
                if row and len(row) > 0:
                    name_to_row[row[0]] = idx + 1  # Sheets usa índice base 1
            
            # 3. Preparar dados para batch update
            batch_data = []
            updates_count = 0
            errors = []
            
            for enriched_item in enriched_data:
                if 'error' in enriched_item:
                    errors.append(enriched_item)
                    continue
                
                distro_name = enriched_item.get('Name')
                if not distro_name or distro_name not in name_to_row:
                    logger.warning(f"Distro não encontrada na planilha: {distro_name}")
                    continue
                
                row_number = name_to_row[distro_name]
                
                # Para cada campo enriquecido
                for field in fields:
                    field_value = field.value  # Nome da coluna (ex: "Idle RAM Usage")
                    
                    if field_value in enriched_item and field_value in column_map:
                        col_idx = column_map[field_value]
                        col_letter = self._get_column_letter(col_idx)
                        cell_range = f"{self.SHEET_NAME}!{col_letter}{row_number}"
                        value = enriched_item[field_value]
                        
                        batch_data.append({
                            'range': cell_range,
                            'values': [[value]]
                        })
                        updates_count += 1
            
            # 4. Executar batch update
            if batch_data:
                url_batch_update = f"{self.SHEETS_API_URL}/{self.SHEET_ID}/values:batchUpdate"
                
                payload = {
                    'valueInputOption': 'USER_ENTERED',
                    'data': batch_data
                }
                
                response = await self.client.post(
                    url_batch_update,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                logger.info(f"Planilha atualizada: {updates_count} células")
                
                return {
                    'success': True,
                    'updated_cells': result.get('totalUpdatedCells', 0),
                    'updated_ranges': len(batch_data),
                    'message': f'{updates_count} células atualizadas com sucesso',
                    'errors': errors if errors else None
                }
            else:
                return {
                    'success': False,
                    'message': 'Nenhum dado para atualizar',
                    'errors': errors if errors else None
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar planilha: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro ao atualizar planilha: {str(e)}'
            }

    @staticmethod
    def _get_column_letter(col_idx: int) -> str:
        """
        Converte índice numérico para letra de coluna (0 -> A, 1 -> B, etc.).
        
        Args:
            col_idx: Índice da coluna (base 0).
        
        Returns:
            Letra da coluna.
        """
        result = ""
        while col_idx >= 0:
            result = chr(col_idx % 26 + 65) + result
            col_idx = col_idx // 26 - 1
        return result
