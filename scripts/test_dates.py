"""Script para testar parsing de datas em distros específicas."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from api.services.distrowatch_scraper import DistroWatchScraper

async def main():
    # Distros com datas inválidas
    test_distros = ["locos", "omarchy", "bazzite"]
    
    scraper = DistroWatchScraper()
    
    for distro_id in test_distros:
        print(f"\n=== Testando: {distro_id} ===")
        
        try:
            # Buscar HTML
            html = await scraper.fetch_distro_page(distro_id)
            
            if html is None:
                print(f"  ERRO: Não foi possível buscar a página")
                continue
            
            print(f"  HTML recebido: {len(html)} bytes")
            
            # Parsear dados
            result = scraper.parse_distro_data(html)
            
            print(f"  latest_release: {result.get('latest_release')}")
            print(f"  popularity_rank: {result.get('popularity_rank')}")
            print(f"  architecture: {result.get('architecture')}")
            print(f"  init_system: {result.get('init_system')}")
            print(f"  file_systems: {result.get('file_systems')}")
            print(f"  release_type: {result.get('release_type')}")

        except Exception as e:
            print(f"  Exceção: {e}")
            import traceback
            traceback.print_exc()
        
        # Delay entre requests
        print("  Aguardando 15s...")
        await asyncio.sleep(15)
    
    await scraper.close()

asyncio.run(main())
