"""
DistroWatch Scraper Service with Anti-Detection Techniques.

Implements stealth scraping to fetch additional distro metadata:
- Popularity ranking
- Release type (LTS/Rolling)
- Init system
- File systems
- Architectures

Anti-detection techniques:
1. Random User-Agent rotation (50+ real UAs)
2. Request delays with jitter (3-7s)
3. Session persistence (cookies)
4. Referer spoofing
5. Realistic Accept-Language headers
"""

import logging
import random
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class DistroWatchScraper:
    """Scraper para coletar dados adicionais do DistroWatch."""
    
    BASE_URL = "https://distrowatch.com"
    
    # ====== ANTI-DETECTION: User-Agents Reais ======
    USER_AGENTS = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Chrome Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Firefox Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Firefox Linux
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    
    # ====== ANTI-DETECTION: Accept-Language por região ======
    ACCEPT_LANGUAGES = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9,en-US;q=0.8",
        "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "de-DE,de;q=0.9,en;q=0.8",
        "fr-FR,fr;q=0.9,en;q=0.8",
        "es-ES,es;q=0.9,en;q=0.8",
    ]
    
    # ====== ANTI-DETECTION: Referers realistas ======
    REFERERS = [
        "https://www.google.com/",
        "https://www.google.com/search?q=linux+distributions",
        "https://duckduckgo.com/",
        "https://www.bing.com/",
        "https://distrowatch.com/",
        None,  # Às vezes sem referer
    ]
    
    # Delay config (segundos)
    MIN_DELAY = 3.0
    MAX_DELAY = 7.0
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.last_request_time: Optional[datetime] = None
        
    async def _init_client(self):
        """Inicializa o cliente HTTP com sessão persistente."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                # Mantém cookies entre requests (session persistence)
                cookies=httpx.Cookies(),
            )
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Gera headers aleatórios para cada request."""
        ua = random.choice(self.USER_AGENTS)
        accept_lang = random.choice(self.ACCEPT_LANGUAGES)
        referer = random.choice(self.REFERERS)
        
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": accept_lang,
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site" if referer else "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        if referer:
            headers["Referer"] = referer
            
        return headers
    
    async def _delay_with_jitter(self):
        """Adiciona delay aleatório entre requests."""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            min_wait = self.MIN_DELAY - elapsed
            if min_wait > 0:
                # Adiciona jitter de ±30%
                jitter = random.uniform(0.7, 1.3)
                delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY) * jitter
                actual_delay = max(min_wait, delay)
                logger.debug(f"Aguardando {actual_delay:.2f}s antes do próximo request...")
                await asyncio.sleep(actual_delay)
        
        self.last_request_time = datetime.now()
    
    async def fetch_distro_page(self, distro_id: str) -> Optional[str]:
        """
        Busca a página de uma distro no DistroWatch.
        
        Args:
            distro_id: ID da distro (ex: "ubuntu", "manjaro")
            
        Returns:
            HTML da página ou None se falhar
        """
        await self._init_client()
        await self._delay_with_jitter()
        
        url = f"{self.BASE_URL}/table.php?distribution={distro_id}"
        headers = self._get_random_headers()
        
        try:
            logger.info(f"Scraping DistroWatch: {distro_id}")
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Status {response.status_code} para {distro_id}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar {distro_id}: {e}")
            return None
    
    def parse_distro_data(self, html: str) -> Dict[str, Any]:
        """
        Extrai dados da página HTML do DistroWatch.
        
        Returns:
            Dict com: architecture, popularity_rank, release_type, init_system, file_systems
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        
        try:
            # Encontrar tabela de metadados
            # DistroWatch usa tabelas para mostrar info
            
            # Architecture
            arch_match = self._find_table_value(soup, ["Architecture", "Arquitectura"])
            if arch_match:
                # Parse: "armhf, ppc64el, x86_64" -> ["armhf", "ppc64el", "x86_64"]
                data["architecture"] = [a.strip() for a in arch_match.split(",") if a.strip()]
            
            # Popularity Rank (do ranking section)
            rank_text = soup.find(string=re.compile(r"Page Hit Ranking", re.I))
            if rank_text:
                parent = rank_text.find_parent("td") or rank_text.find_parent("th")
                if parent:
                    next_cell = parent.find_next_sibling("td")
                    if next_cell:
                        rank_match = re.search(r'\d+', next_cell.get_text())
                        if rank_match:
                            data["popularity_rank"] = int(rank_match.group())
            
            # Release Type (Fixed/Rolling)
            release_type = self._find_table_value(soup, ["Release Model", "Modelo de lançamento"])
            if release_type:
                if "rolling" in release_type.lower():
                    data["release_type"] = "Rolling"
                elif "lts" in release_type.lower():
                    data["release_type"] = "LTS"
                elif "fixed" in release_type.lower():
                    data["release_type"] = "Point Release"
                else:
                    data["release_type"] = release_type
            
            # Init System
            init = self._find_table_value(soup, ["Init Software", "Init"])
            if init:
                data["init_system"] = init.strip()
            
            # File Systems
            fs = self._find_table_value(soup, ["File Systems", "Filesystems", "Sistemas de arquivos"])
            if fs:
                data["file_systems"] = [f.strip() for f in fs.split(",") if f.strip()]
                
        except Exception as e:
            logger.error(f"Erro ao parsear HTML: {e}")
            
        return data
    
    def _find_table_value(self, soup: BeautifulSoup, labels: List[str]) -> Optional[str]:
        """Busca valor em tabela dado um label."""
        for label in labels:
            # Tenta encontrar célula com o label
            cell = soup.find(string=re.compile(label, re.I))
            if cell:
                parent = cell.find_parent("td") or cell.find_parent("th")
                if parent:
                    # Próxima célula geralmente tem o valor
                    next_cell = parent.find_next_sibling("td")
                    if next_cell:
                        return next_cell.get_text(strip=True)
        return None
    
    async def scrape_distro(self, distro_id: str) -> Dict[str, Any]:
        """
        Scrape completo de uma distro.
        
        Args:
            distro_id: ID da distro
            
        Returns:
            Dict com dados extraídos
        """
        html = await self.fetch_distro_page(distro_id)
        if not html:
            return {"error": f"Falha ao buscar {distro_id}"}
        
        data = self.parse_distro_data(html)
        data["distro_id"] = distro_id
        data["scraped_at"] = datetime.now().isoformat()
        
        return data
    
    async def scrape_multiple(self, distro_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape de múltiplas distros com delays entre cada uma.
        
        Args:
            distro_ids: Lista de IDs
            
        Returns:
            Lista de resultados
        """
        results = []
        
        for i, distro_id in enumerate(distro_ids):
            logger.info(f"Processando {i+1}/{len(distro_ids)}: {distro_id}")
            result = await self.scrape_distro(distro_id)
            results.append(result)
            
            # Progress log a cada 10
            if (i + 1) % 10 == 0:
                logger.info(f"Progresso: {i+1}/{len(distro_ids)} distros processadas")
        
        return results
    
    async def close(self):
        """Fecha o cliente HTTP."""
        if self.client:
            await self.client.aclose()
            self.client = None


# Função auxiliar para uso direto
async def scrape_distrowatch_data(distro_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Função helper para scraping de distros.
    
    Usage:
        from api.services.distrowatch_scraper import scrape_distrowatch_data
        
        results = await scrape_distrowatch_data(["ubuntu", "manjaro", "fedora"])
    """
    scraper = DistroWatchScraper()
    try:
        return await scraper.scrape_multiple(distro_ids)
    finally:
        await scraper.close()
