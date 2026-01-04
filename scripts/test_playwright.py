"""Teste do scraper com Playwright - versão melhorada."""
import asyncio
import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from dotenv import load_dotenv
load_dotenv()

from api.services.distrowatch_scraper import DistroWatchScraper

async def main():
    print("=== Teste do Scraper com Playwright ===\n")
    
    scraper = DistroWatchScraper()
    
    # Testar uma distro
    test_distro = "ubuntu"
    
    print(f"Testando: {test_distro}")
    print("-" * 40)
    
    try:
        html = await scraper.fetch_distro_page(test_distro)
        
        if html:
            print(f"✓ HTML recebido: {len(html)} bytes")
            
            # Parsear dados
            result = scraper.parse_distro_data(html)
            
            print(f"\nDados extraídos:")
            print(f"  - popularity_rank: {result.get('popularity_rank')}")
            print(f"  - architecture: {result.get('architecture')}")
            print(f"  - init_system: {result.get('init_system')}")
            print(f"  - release_type: {result.get('release_type')}")
            print(f"  - file_systems: {result.get('file_systems')}")
        else:
            print("✗ Falha ao buscar página")
    except Exception as e:
        print(f"Erro durante scraping: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        await scraper.close()
        print("\n✓ Scraper fechado")
    except Exception as e:
        print(f"Erro ao fechar scraper (ignorado): {e}")

asyncio.run(main())
