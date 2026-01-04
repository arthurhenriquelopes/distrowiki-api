"""Debug: ver estrutura HTML do DistroWatch."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from api.services.distrowatch_scraper import DistroWatchScraper
from bs4 import BeautifulSoup

async def main():
    scraper = DistroWatchScraper()
    
    # Testar uma distro conhecida
    test_distro = "ubuntu"  # Usar uma popular para garantir HTML
    
    print(f"=== Testando estrutura de: {test_distro} ===")
    
    html = await scraper.fetch_distro_page(test_distro)
    
    if html is None:
        print("ERRO: Não foi possível buscar a página")
        await scraper.close()
        return
    
    print(f"HTML recebido: {len(html)} bytes")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Procurar por labels importantes
    labels_to_find = [
        "Architecture",
        "Init Software",
        "Release Model",
        "File Systems",
        "Page Hit Ranking",
        "Last Update"
    ]
    
    print("\n=== Procurando labels ===")
    for label in labels_to_find:
        found = soup.find(string=lambda t: t and label.lower() in t.lower())
        if found:
            print(f"✓ '{label}': Encontrado")
            # Mostrar contexto
            parent = found.find_parent("td") or found.find_parent("th")
            if parent:
                next_cell = parent.find_next_sibling("td")
                if next_cell:
                    print(f"    Valor: {next_cell.get_text(strip=True)[:100]}")
        else:
            print(f"✗ '{label}': NÃO encontrado")
    
    # Mostrar todas as tables
    print("\n=== Tabelas encontradas ===")
    tables = soup.find_all("table")
    print(f"Total de tabelas: {len(tables)}")
    
    for i, table in enumerate(tables[:5]):
        th_cells = table.find_all("th")
        if th_cells:
            print(f"  Tabela {i}: {[th.get_text(strip=True)[:20] for th in th_cells[:5]]}")
    
    await scraper.close()

asyncio.run(main())
