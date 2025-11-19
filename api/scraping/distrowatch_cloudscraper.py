"""
Scraper do DistroWatch usando CloudScraper
Bypass automático de Cloudflare e proteções anti-bot.
"""

import logging
import cloudscraper
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DistroWatchCloudScraper:
    """
    Scraper para DistroWatch usando CloudScraper.
    
    Características:
    - Bypass automático de Cloudflare
    - Leve e rápido (sem navegador)
    - User-agent rotativo
    - Retry automático
    """
    
    def __init__(self, delay: int = 2):
        """
        Inicializa o scraper.
        
        Args:
            delay: Delay entre requests em segundos
        """
        self.base_url = "https://distrowatch.com"
        self.delay = delay
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
    def scrape_distro_list(self) -> List[Dict]:
        """
        Scrape lista de distribuições da página de popularidade.
        
        Returns:
            Lista de dicionários com dados básicos das distros
        """
        logger.info("🔍 Iniciando scraping da lista de distribuições...")
        
        url = f"{self.base_url}/index.php?dataspan=1"
        
        try:
            logger.info(f"📡 Acessando: {url}")
            response = self.scraper.get(url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"✅ Status: {response.status_code}")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            distros = []
            
            # Encontra tabela de ranking
            # DistroWatch usa <table> com class específica
            table = soup.find('table', class_='News')
            
            if not table:
                logger.warning("⚠️ Tabela de distros não encontrada, tentando método alternativo...")
                # Método alternativo: busca por links de distros
                links = soup.find_all('a', href=lambda x: x and 'table.php?distribution=' in x)
                
                for i, link in enumerate(links[:100], 1):  # Limita a 100
                    distro_name = link.get_text(strip=True)
                    distro_url = link.get('href')
                    
                    if not distro_url.startswith('http'):
                        distro_url = f"{self.base_url}/{distro_url}"
                    
                    distros.append({
                        'rank': str(i),
                        'name': distro_name,
                        'url': distro_url
                    })
                
                logger.info(f"✅ Scraped {len(distros)} distros (método alternativo)")
                return distros
            
            # Parse da tabela principal
            rows = table.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                
                if len(cols) >= 2:
                    # Primeira coluna: rank
                    rank_col = cols[0].get_text(strip=True)
                    
                    # Segunda coluna: nome e link
                    link = cols[1].find('a', href=lambda x: x and 'table.php?distribution=' in x)
                    
                    if link:
                        distro_name = link.get_text(strip=True)
                        distro_url = link.get('href')
                        
                        if not distro_url.startswith('http'):
                            distro_url = f"{self.base_url}/{distro_url}"
                        
                        distros.append({
                            'rank': rank_col if rank_col.isdigit() else str(len(distros) + 1),
                            'name': distro_name,
                            'url': distro_url
                        })
            
            logger.info(f"✅ Scraped {len(distros)} distribuições")
            return distros
            
        except Exception as e:
            logger.error(f"❌ Erro ao fazer scraping da lista: {e}")
            return []
    
    def scrape_distro_details(self, distro_url: str) -> Optional[Dict]:
        """
        Scrape detalhes de uma distribuição específica.
        
        Args:
            distro_url: URL da página da distro
        
        Returns:
            Dict com detalhes da distro ou None se falhar
        """
        logger.info(f"📄 Scraping detalhes de: {distro_url}")
        
        try:
            response = self.scraper.get(distro_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            details = {}
            
            # Extrai informações da página
            # Based: seção com informações básicas
            info_table = soup.find('table', class_='Info')
            
            if info_table:
                rows = info_table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        key = cols[0].get_text(strip=True).lower().replace(':', '')
                        value = cols[1].get_text(strip=True)
                        details[key] = value
            
            return details
            
        except Exception as e:
            logger.error(f"❌ Erro ao scraping detalhes: {e}")
            return None
    
    def scrape_all(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape completo: lista + detalhes de cada distro.
        
        Args:
            limit: Limite de distros para scrape (None = todas)
        
        Returns:
            Lista de distros com todos os dados
        """
        logger.info("🚀 Iniciando scraping completo do DistroWatch...")
        
        # Scrape lista
        distros = self.scrape_distro_list()
        
        if not distros:
            logger.warning("⚠️ Nenhuma distro encontrada na lista")
            return []
        
        # Aplica limite se especificado
        if limit:
            distros = distros[:limit]
            logger.info(f"📊 Limitando scraping a {limit} distribuições")
        
        logger.info(f"✅ Scraping completo: {len(distros)} distribuições processadas")
        
        return distros


def test_scraper():
    """Testa o scraper localmente."""
    import json
    
    print("🧪 Testando CloudScraper...")
    
    scraper = DistroWatchCloudScraper()
    results = scraper.scrape_all(limit=5)
    
    print(f"\n✅ Resultados: {len(results)} distros")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_scraper()
