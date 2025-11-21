"""
Serviço de integração com Google Sheets.

Busca dados de distribuições Linux diretamente do Google Sheets.
Utiliza API pública sem autenticação (sheets públicas) para leitura.
Utiliza OAuth 2.0 para escrita (atualização automática).
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..models.distro import DistroMetadata, DistroFamily, DesktopEnvironment

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Serviço para buscar dados do Google Sheets."""
    
    # IDs e configuração
    SHEET_ID = "1ObKRlMRWtABnau6lZTT6en1BajVkV6m2LtLhXEHZ_Zk"
    SHEET_NAME = "distrowiki_complete"
    
    # URL da API do Google Sheets (v4)
    SHEETS_API_URL = "https://sheets.googleapis.com/v4/spreadsheets"
    
    # Headers para requisição
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    TIMEOUT = 30.0
    
    # OAuth 2.0 Scopes
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # Caminhos para credenciais
    CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    TOKEN_FILE = os.getenv('GOOGLE_TOKEN_FILE', 'token.json')
    
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
        self._sheets_service = None
    
    async def close(self):
        """Fecha o cliente HTTP."""
        await self.client.aclose()
    
    def _get_credentials(self) -> Optional[Credentials]:
        """
        Obtém credenciais OAuth 2.0 para acesso ao Google Sheets.
        
        Returns:
            Credentials ou None se não configurado.
        """
        creds = None
        
        # Verificar se já existe token
        if os.path.exists(self.TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
            except Exception as e:
                logger.warning(f"Erro ao carregar token: {e}")
        
        # Se não tem credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Token OAuth renovado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao renovar token: {e}")
                    creds = None
            
            if not creds and os.path.exists(self.CREDENTIALS_FILE):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.CREDENTIALS_FILE, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.info("Autenticação OAuth realizada com sucesso")
                except Exception as e:
                    logger.error(f"Erro na autenticação OAuth: {e}")
                    return None
            
            # Salvar token para próximas execuções
            if creds:
                try:
                    with open(self.TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    logger.info("Token salvo com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao salvar token: {e}")
        
        return creds
    
    def _get_sheets_service(self):
        """
        Obtém serviço do Google Sheets API com OAuth.
        
        Returns:
            Serviço do Google Sheets API.
        """
        if not self._sheets_service:
            creds = self._get_credentials()
            if not creds:
                raise ValueError("Credenciais OAuth não configuradas. Configure credentials.json")
            
            self._sheets_service = build('sheets', 'v4', credentials=creds)
        
        return self._sheets_service
    
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
            
            # Criar objeto com todos os campos do Google Sheets
            distro = DistroMetadata(
                id=distro_id,
                name=name,
                summary=data.get("description", "").strip() or None,
                description=data.get("description", "").strip() or None,
                logo=data.get("logo", "").strip() or None,
                logo_url=data.get("logo url", "").strip() or None,
                os_type=data.get("os type", "").strip() or None,
                family=family,
                based_on=base or None,
                origin=data.get("origin", "").strip() or None,
                desktop=desktop_str or None,
                desktop_environments=desktop_environments,
                category=data.get("category", "").strip() or None,
                status=data.get("status", "").strip() or None,
                idle_ram_usage=data.get("idle ram usage", "").strip() or None,
                image_size=data.get("image size", "").strip() or None,
                office_suite=data.get("office suite", "").strip() or None,
                price=data.get("price (r$)", "").strip() or None,
                latest_release_date=release_date,
                homepage=data.get("website", "").strip() or None,
                package_manager=data.get("package management", "").strip() or None,
                architecture=data.get("architecture", "").strip() or None,
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
        
        # Se for apenas um ano (4 dígitos), usar 1º de janeiro daquele ano
        if date_str.isdigit() and len(date_str) == 4:
            try:
                return datetime(int(date_str), 1, 1)
            except ValueError:
                pass
        
        # Tentar vários formatos completos
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
    
    def update_distro_data(self, enriched_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Atualiza dados enriquecidos no Google Sheets.
        
        Args:
            enriched_data: Lista de dados enriquecidos pelo GROQ.
                          Cada item deve ter: name, ram_idle, cpu_score, io_score, requisitos
        
        Returns:
            Dicionário com resultado da operação.
        """
        try:
            service = self._get_sheets_service()
            
            # Primeiro, buscar os headers e dados atuais
            result = service.spreadsheets().values().get(
                spreadsheetId=self.SHEET_ID,
                range=f"{self.SHEET_NAME}!A1:Z1000"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return {"error": "Planilha vazia"}
            
            # Headers na primeira linha
            headers = [h.lower().strip() for h in values[0]]
            
            # Encontrar índices das colunas que precisamos atualizar
            try:
                name_col = headers.index('name')
                ram_col = headers.index('idle ram usage')
                cpu_col = headers.index('cpu score') if 'cpu score' in headers else None
                io_col = headers.index('i/o score') if 'i/o score' in headers else None
                req_col = headers.index('requirements') if 'requirements' in headers else None
            except ValueError as e:
                return {"error": f"Coluna não encontrada: {e}"}
            
            # Criar mapa de nome -> índice de linha
            name_to_row = {}
            for i, row in enumerate(values[1:], start=2):  # Começa em 2 (linha 1 é header)
                if len(row) > name_col:
                    name_to_row[row[name_col].strip().lower()] = i
            
            # Preparar atualizações em batch
            updates = []
            updated_count = 0
            errors = []
            
            for item in enriched_data:
                name = item.get('name', '').strip()
                if not name:
                    continue
                
                # Verificar se há erro no enriquecimento
                if 'error' in item:
                    errors.append(f"{name}: {item['error']}")
                    continue
                
                # Encontrar a linha correspondente
                row_index = name_to_row.get(name.lower())
                if not row_index:
                    errors.append(f"{name}: não encontrado na planilha")
                    continue
                
                # Atualizar RAM Idle
                if 'ram_idle' in item:
                    col_letter = self._col_number_to_letter(ram_col + 1)
                    updates.append({
                        'range': f"{self.SHEET_NAME}!{col_letter}{row_index}",
                        'values': [[str(item['ram_idle'])]]
                    })
                
                # Atualizar CPU Score
                if 'cpu_score' in item and cpu_col is not None:
                    col_letter = self._col_number_to_letter(cpu_col + 1)
                    updates.append({
                        'range': f"{self.SHEET_NAME}!{col_letter}{row_index}",
                        'values': [[str(item['cpu_score'])]]
                    })
                
                # Atualizar I/O Score
                if 'io_score' in item and io_col is not None:
                    col_letter = self._col_number_to_letter(io_col + 1)
                    updates.append({
                        'range': f"{self.SHEET_NAME}!{col_letter}{row_index}",
                        'values': [[str(item['io_score'])]]
                    })
                
                # Atualizar Requirements (campo em inglês)
                if 'requirements' in item and req_col is not None:
                    col_letter = self._col_number_to_letter(req_col + 1)
                    updates.append({
                        'range': f"{self.SHEET_NAME}!{col_letter}{row_index}",
                        'values': [[str(item['requirements'])]]
                    })
                    logger.info(f"Adicionando requirements '{item['requirements']}' para {name}")
                elif 'requirements' in item and req_col is None:
                    logger.warning(f"Coluna 'requirements' não encontrada no Sheets para atualizar {name}")
                elif 'requirements' not in item:
                    logger.warning(f"Campo 'requirements' não retornado pelo GROQ para {name}")
                
                updated_count += 1
            
            # Executar todas as atualizações em batch
            if updates:
                body = {
                    'valueInputOption': 'USER_ENTERED',
                    'data': updates
                }
                
                result = service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.SHEET_ID,
                    body=body
                ).execute()
                
                logger.info(f"Google Sheets atualizado: {updated_count} distros, {result.get('totalUpdatedCells', 0)} células")
            
            return {
                "success": True,
                "updated": updated_count,
                "total_cells": result.get('totalUpdatedCells', 0) if updates else 0,
                "errors": errors if errors else None
            }
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao atualizar Google Sheets: {e}")
            return {"error": f"Erro HTTP: {e}"}
        except Exception as e:
            logger.error(f"Erro ao atualizar Google Sheets: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _col_number_to_letter(self, col: int) -> str:
        """
        Converte número de coluna (1-indexed) para letra (A, B, C, ..., Z, AA, AB, ...).
        
        Args:
            col: Número da coluna (1 = A, 2 = B, etc.)
        
        Returns:
            Letra(s) da coluna.
        """
        result = ""
        while col > 0:
            col -= 1
            result = chr(65 + (col % 26)) + result
            col //= 26
        return result
