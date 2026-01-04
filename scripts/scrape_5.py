"""Scraping rápido das 5 primeiras distros."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from api.services.distrowatch_scraper import DistroWatchScraper
from api.services.google_sheets_service import GoogleSheetsService
from enum import Enum

# Definir enum para campos
class EnrichmentField(Enum):
    LATEST_RELEASE = "Latest Release"
    INIT_SYSTEM = "Init System"
    ARCHITECTURE = "Architecture"

async def main():
    print("=== Scraping das 5 Primeiras Distros ===\n")
    
    sheets = GoogleSheetsService()
    scraper = DistroWatchScraper()
    
    # Buscar distros da planilha
    distros = await sheets.fetch_all_distros()
    distros_to_scrape = list(distros)[:5]
    
    print(f"Distros a processar: {[d.id for d in distros_to_scrape]}\n")
    
    enriched_data = []
    
    for i, distro in enumerate(distros_to_scrape, 1):
        distro_id = distro.id
        distro_name = distro.name
        print(f"[{i}/5] Scraping: {distro_id}")
        
        try:
            html = await scraper.fetch_distro_page(distro_id)
            
            if html:
                data = scraper.parse_distro_data(html)
                
                # Mostrar dados encontrados
                print(f"  → latest_release: {data.get('latest_release')}")
                print(f"  → init_system: {data.get('init_system')}")
                print(f"  → popularity_rank: {data.get('popularity_rank')}")
                
                # Preparar dados para update
                if data.get('latest_release') or data.get('init_system'):
                    enriched_item = {"Name": distro_name}
                    if data.get('latest_release'):
                        enriched_item["Latest Release"] = data['latest_release']
                    if data.get('init_system'):
                        enriched_item["Init System"] = data['init_system']
                    enriched_data.append(enriched_item)
                    print(f"  ✓ Adicionado à fila de update")
            else:
                print(f"  ✗ Falha ao buscar página")
                
        except Exception as e:
            print(f"  ✗ Erro: {e}")
    
    # Fazer batch update
    if enriched_data:
        print(f"\n📝 Atualizando {len(enriched_data)} distros na planilha...")
        fields = [EnrichmentField.LATEST_RELEASE, EnrichmentField.INIT_SYSTEM]
        result = await sheets.update_enriched_data(enriched_data, fields)
        print(f"Resultado: {result}")
    else:
        print("\n⚠️ Nenhum dado para atualizar")
    
    await scraper.close()
    await sheets.close()
    print("\n✅ Concluído!")

asyncio.run(main())
