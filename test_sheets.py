#!/usr/bin/env python3
"""
Script de teste para Google Sheets Service.
Execute: python test_sheets.py
"""

import asyncio
import sys
from pathlib import Path

# Adicionar API ao path
sys.path.insert(0, str(Path(__file__).parent))

from api.services.google_sheets_service import GoogleSheetsService


async def test_fetch():
    """Testa busca de dados do Google Sheets."""
    print("🔍 Testando Google Sheets Service...")
    print()
    
    service = GoogleSheetsService()
    
    try:
        print("📊 Buscando dados do Google Sheets...")
        distros = await service.fetch_all_distros()
        
        print(f"✅ Sucesso! {len(distros)} distribuições encontradas")
        print()
        
        if distros:
            print("📋 Primeiras 3 distribuições:")
            for i, distro in enumerate(distros[:3]):
                print()
                print(f"  {i+1}. {distro.name}")
                print(f"     ID: {distro.id}")
                print(f"     Family: {distro.family}")
                print(f"     Homepage: {distro.homepage}")
                print(f"     DEs: {', '.join(distro.desktop_environments) if distro.desktop_environments else 'N/A'}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(test_fetch())
