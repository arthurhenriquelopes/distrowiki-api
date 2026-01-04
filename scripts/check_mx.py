"""Verificar dados do MX Linux na planilha."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from api.services.sheets import GoogleSheetsService

async def main():
    svc = GoogleSheetsService()
    
    print("Buscando MX Linux na planilha...")
    data = await svc.get_distro("mxlinux")
    
    if data:
        print(f"Nome: {data.get('name')}")
        print(f"Latest Release: '{data.get('latest_release_date')}'")
        print(f"Release Model: '{data.get('release_model')}'")
        print(f"Family: {data.get('family')}")
        print(f"Ranking: {data.get('ranking')}")
    else:
        print("MX Linux não encontrado!")
    
    await svc.close()

asyncio.run(main())
