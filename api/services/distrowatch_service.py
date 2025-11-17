"""
Serviço de scraping do DistroWatch.

Busca dados de distribuições Linux do DistroWatch.com,
fonte autorizada e atualizada com ranking mensal.
"""

import asyncio
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import httpx
from bs4 import BeautifulSoup

from ..models.distro import DistroMetadata, DistroFamily, DesktopEnvironment

logger = logging.getLogger(__name__)


class DistroWatchService:
    """Serviço para buscar dados do DistroWatch via scraping."""
    
    BASE_URL = "http://distrowatch.com"
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
        """Inicializa o serviço do DistroWatch."""
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={"User-Agent": self.USER_AGENT},
            follow_redirects=True,
            http2=False  # Desabilitar HTTP/2 para evitar problemas de conexão
        )
    
    async def close(self):
        """Fecha o cliente HTTP."""
        await self.client.aclose()
    
    async def fetch_ranking_list(self, limit: int = 290) -> List[Dict[str, Any]]:
        """
        Busca lista de distribuições do ranking do DistroWatch (Page Hit Ranking).
        
        Args:
            limit: Número máximo de distribuições para buscar (padrão: 290)
        
        Returns:
            Lista de dicionários com {'rank', 'slug', 'name', 'hpd'}
        """
        try:
            logger.info(f"Buscando ranking do DistroWatch (top {limit})...")
            
            # URL da página de ranking completo
            response = await self.client.get(f"{self.BASE_URL}/dwres.php?resource=popularity")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            distros = []
            
            # Encontrar especificamente a tabela "Last 1 month"
            target_table = None
            for th in soup.find_all('th', class_='Invert'):
                if 'Last 1 month' in th.get_text():
                    target_table = th.find_parent('table')
                    break
            
            if not target_table:
                logger.warning("Não encontrou tabela 'Last 1 month'")
                return []
            
            # Encontrar todas as linhas <tr> DESTA tabela específica
            rows = target_table.find_all('tr')
            
            for row in rows:
                # Buscar células de ranking
                rank_cell = row.find('th', class_='phr1')
                name_cell = row.find('td', class_='phr2')
                hpd_cell = row.find('td', class_='phr3')
                
                if rank_cell and name_cell and hpd_cell:
                    try:
                        rank = int(rank_cell.get_text(strip=True))
                        
                        # Extrair link e slug
                        link = name_cell.find('a')
                        if not link:
                            continue
                        
                        name = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        # Extrair slug do href: "https://distrowatch.com/cachyos" -> "cachyos"
                        slug = href.split('/')[-1]
                        
                        # Extrair HPD (hits per day) - remover caracteres não numéricos
                        hpd_text = hpd_cell.get_text(strip=True)
                        hpd_match = re.search(r'(\d+)', hpd_text)
                        hpd = int(hpd_match.group(1)) if hpd_match else 0
                        
                        distros.append({
                            'rank': rank,
                            'slug': slug,
                            'name': name,
                            'hpd': hpd
                        })
                        
                        if len(distros) >= limit:
                            break
                            
                    except (ValueError, AttributeError) as e:
                        continue
            
            logger.info(f"Encontradas {len(distros)} distribuições no ranking")
            return distros
            
        except Exception as e:
            logger.error(f"Erro ao buscar ranking: {e}")
            return []
    
    async def fetch_distro_by_slug(self, slug: str) -> Optional[DistroMetadata]:
        """
        Busca uma distribuição pelo slug (ex: 'cachyos', 'popos', 'arch').
        
        Args:
            slug: Slug da distribuição no DistroWatch.
        
        Returns:
            Objeto DistroMetadata ou None.
        """
        url = f"{self.BASE_URL}/table.php?distribution={slug}"
        return await self.fetch_distro_details(url, slug)
    
    async def fetch_distro_details(self, distro_url: str, identifier: str) -> Optional[DistroMetadata]:
        """
        Busca detalhes completos de uma distribuição.
        
        Args:
            distro_url: URL da página da distribuição.
            identifier: Nome ou slug da distribuição.
        
        Returns:
            Objeto DistroMetadata ou None.
        """
        try:
            logger.info(f"Buscando detalhes de {identifier}...")
            
            response = await self.client.get(distro_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair dados estruturados
            data = await self._parse_distro_page(soup)
            
            if not data:
                logger.warning(f"Não foi possível extrair dados de {identifier}")
                return None
            
            # Criar ID slug
            distro_id = identifier if '/' not in identifier else self._create_slug(identifier)
            
            # Construir URL padrão da logo
            logo_url = f"https://distrowatch.com/images/yvzhuwbpy/{distro_id}.png"
            
            return DistroMetadata(
                id=distro_id,
                name=data.get('name', identifier.title()),
                description=data.get('description'),
                os_type=data.get('os_type'),
                based_on=data.get('based_on'),
                family=data.get('family', DistroFamily.INDEPENDENT),
                origin=data.get('origin'),
                architecture=data.get('architecture'),
                desktop=data.get('desktop'),
                desktop_environments=data.get('desktop_environments', []),
                category=data.get('category'),
                status=data.get('status'),
                ranking=data.get('ranking'),
                rating=data.get('rating'),
                homepage=data.get('homepage'),
                logo=logo_url,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.warning(f"Erro ao buscar detalhes de {identifier}: {e}")
            return None
    
    async def fetch_all_from_ranking(self, limit: Optional[int] = None) -> List[DistroMetadata]:
        """
        Busca todas as distribuições do ranking do DistroWatch.
        
        Args:
            limit: Limite opcional de quantas distros buscar
        
        Returns:
            Lista de DistroMetadata
        """
        # Primeiro buscar lista do ranking
        ranking_list = await self.fetch_ranking_list()
        
        if limit:
            ranking_list = ranking_list[:limit]
        
        distros = []
        total = len(ranking_list)
        
        logger.info(f"Iniciando busca de {total} distribuições do ranking...")
        
        for i, item in enumerate(ranking_list, 1):
            try:
                slug = item['slug']
                rank = item['rank']
                
                logger.info(f"[{i}/{total}] Buscando #{rank} {slug}...")
                
                distro = await self.fetch_distro_by_slug(slug)
                
                if distro:
                    # Atualizar ranking se não foi capturado
                    if not distro.ranking:
                        distro.ranking = rank
                    distros.append(distro)
                    logger.info(f"✓ {distro.name} adicionada")
                else:
                    logger.warning(f"✗ Falhou: {slug}")
                
                # Rate limiting
                if i < total:
                    await asyncio.sleep(1.5)
                    
            except Exception as e:
                logger.error(f"Erro ao buscar {item.get('slug', '?')}: {e}")
                continue
        
        logger.info(f"Busca concluída: {len(distros)}/{total} distribuições obtidas")
        return distros
    
    async def _parse_distro_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Faz parsing completo da página de uma distribuição.
        
        Extrai campos do DistroWatch:
        - OS Type, Based on, Origin, Architecture, Desktop, Category, Status
        - Ranking (Popularity)
        - Rating (Average visitor rating)
        - Description
        - Homepage
        
        Args:
            soup: Objeto BeautifulSoup da página.
        
        Returns:
            Dicionário com dados extraídos.
        """
        data = {}
        
        try:
            # 1. Encontrar o <ul> que contém os metadados
            # (está logo após o logo da distribuição)
            uls = soup.find_all('ul')
            
            metadata_ul = None
            for ul in uls:
                # Verificar se este <ul> tem <li> com <b>OS Type:</b>
                first_li = ul.find('li')
                if first_li and first_li.find('b'):
                    label_text = first_li.find('b').get_text()
                    if 'OS Type' in label_text or 'Based on' in label_text:
                        metadata_ul = ul
                        break
            
            if not metadata_ul:
                logger.warning("Não encontrou <ul> de metadados")
                return {}
            
            # 2. Extrair metadados de cada <li>
            list_items = metadata_ul.find_all('li')
            
            for li in list_items:
                label_tag = li.find('b')
                if not label_tag:
                    continue
                
                label = label_tag.get_text(strip=True).replace(':', '').lower()
                
                # Extrair valor: pegar links diretos deste LI (sem recursão profunda)
                # O problema é que os LI podem estar aninhados incorretamente pelo parser
                # Vamos usar uma abordagem diferente: pegar apenas os <a> que são filhos diretos
                value_parts = []
                
                # Iterar pelos filhos diretos do <li>
                for child in li.children:
                    if hasattr(child, 'name'):
                        if child.name == 'a':
                            value_parts.append(child.get_text(strip=True))
                    elif isinstance(child, str):
                        text = child.strip()
                        if text and text not in [':', ',']:
                            value_parts.append(text)
                
                if value_parts:
                    value = ', '.join([p for p in value_parts if p])
                    # Remover label se estiver no início
                    label_full = label_tag.get_text(strip=True)
                    if value.startswith(label_full):
                        value = value[len(label_full):].strip(' ,:')
                else:
                    value = ""
                
                # Mapear campos
                if 'os type' in label:
                    data['os_type'] = value
                    
                elif 'based on' in label:
                    data['based_on'] = value
                    data['family'] = self._determine_family(value)
                    
                elif 'origin' in label:
                    data['origin'] = value
                    
                elif 'architecture' in label:
                    data['architecture'] = value
                    
                elif 'desktop' in label:
                    data['desktop'] = value
                    data['desktop_environments'] = self._parse_desktop_environments(value)
                    
                elif 'category' in label:
                    data['category'] = value
                    
                elif 'status' in label:
                    # Status pode estar dentro de <font> tag
                    # Extrair texto de qualquer elemento
                    font_tag = li.find('font')
                    if font_tag:
                        data['status'] = font_tag.get_text(strip=True)
                    else:
                        data['status'] = value
                    
                elif 'popularity' in label:
                    # Extrair ranking: "1 (4,342 hits per day)" -> ranking = 1
                    rank_match = re.search(r'^(\d+)', value)
                    if rank_match:
                        data['ranking'] = int(rank_match.group(1))
            
            # 2. Extrair nome do <h1>
            h1 = soup.find('h1')
            if h1:
                data['name'] = h1.get_text(strip=True)
            
            # 3. Extrair rating: buscar "Average visitor rating: 8.1/10"
            # Procurar por <b> tags que contenham o rating
            for b_tag in soup.find_all('b'):
                text = b_tag.get_text()
                if re.search(r'\d+\.\d+', text) and '/' not in text:
                    # Verificar se o contexto menciona rating
                    parent_text = b_tag.parent.get_text() if b_tag.parent else ""
                    if 'visitor rating' in parent_text.lower():
                        rating_match = re.search(r'(\d+\.\d+)', text)
                        if rating_match:
                            data['rating'] = float(rating_match.group(1))
                            break
            
            # 4. Extrair homepage da tabela Summary
            data['homepage'] = self._extract_homepage(soup)
            
            # 5. Extrair description (parágrafo após os metadados)
            data['description'] = self._extract_description(soup)
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao fazer parsing: {e}", exc_info=True)
            return {}
    
    def _determine_family(self, based_on: str) -> DistroFamily:
        """Determina a família com base no campo 'Based on'."""
        if not based_on:
            return DistroFamily.INDEPENDENT
            
        based_on_lower = based_on.lower()
        
        for key, family in self.FAMILY_MAPPING.items():
            if key in based_on_lower:
                return family
        
        return DistroFamily.INDEPENDENT
    
    def _parse_desktop_environments(self, desktop_str: str) -> List[DesktopEnvironment]:
        """Extrai lista de Desktop Environments de uma string."""
        if not desktop_str:
            return []
            
        desktop_lower = desktop_str.lower()
        envs = []
        
        for key, de in self.DE_MAPPING.items():
            if key in desktop_lower and de not in envs:
                envs.append(de)
        
        return envs if envs else [DesktopEnvironment.OTHER]
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrai descrição da distribuição.
        No DistroWatch, a descrição está após o </ul> de metadados,
        como texto direto antes do <br><br>.
        
        Exemplo no HTML:
        </ul>
        CachyOS is a Linux distribution based on Arch Linux...
        <br><br>
        """
        try:
            # Encontrar o UL de metadados
            uls = soup.find_all('ul')
            metadata_ul = None
            
            for ul in uls:
                first_li = ul.find('li')
                if first_li and first_li.find('b'):
                    label_text = first_li.find('b').get_text()
                    if 'OS Type' in label_text:
                        metadata_ul = ul
                        break
            
            if not metadata_ul:
                return None
            
            # Pegar o próximo elemento após o </ul>
            # A descrição está geralmente como texto direto
            next_sibling = metadata_ul.next_sibling
            
            while next_sibling:
                if isinstance(next_sibling, str):
                    text = next_sibling.strip()
                    # Descrição tem mais de 50 chars e contém palavras-chave
                    if len(text) > 50 and any(keyword in text.lower() for keyword in ['distribution', 'linux', 'based on', 'operating system', 'focuses on']):
                        # Limitar a 500 caracteres
                        if len(text) > 500:
                            return text[:500] + "..."
                        return text
                
                next_sibling = next_sibling.next_sibling
                
                # Parar se encontrar <br><br> ou outra tag relevante
                if hasattr(next_sibling, 'name') and next_sibling.name in ['br', 'b', 'table']:
                    break
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair descrição: {e}")
            return None
    
    def _extract_homepage(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrai URL da homepage da distribuição.
        No DistroWatch, está na tabela "Summary" como "Home Page".
        """
        try:
            # Procurar na tabela "Summary"
            tables = soup.find_all('table', class_='Info')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th', class_='Info')
                    if th and 'home page' in th.get_text().lower():
                        td = row.find('td', class_='Info')
                        if td:
                            link = td.find('a', href=True)
                            if link:
                                return link.get('href')
            
            return None
            
        except Exception:
            return None
    
    def _extract_logo(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrai URL da logo da distribuição.
        No DistroWatch, a logo está em uma tag <img> com src começando com 'images/'.
        """
        try:
            # Procurar pela imagem da logo (geralmente está no topo da página)
            # A logo tem src que começa com "images/yvzhuwbpy/" ou similar
            for img in soup.find_all('img'):
                src = img.get('src', '')
                # Logos das distros ficam em /images/yvzhuwbpy/
                if 'images/yvzhuwbpy/' in src or (src.startswith('images/') and not src.endswith('.gif')):
                    # Se for URL relativa, converter para absoluta
                    if not src.startswith('http'):
                        src = f"{self.BASE_URL}/{src}"
                    return src
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair logo: {e}")
            return None
    
    def _create_slug(self, name: str) -> str:
        """Cria um slug a partir do nome."""
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
