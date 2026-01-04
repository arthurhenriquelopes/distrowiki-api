"""Script para encontrar distros com dados inválidos na planilha."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from api.services.google_sheets_service import GoogleSheetsService

async def main():
    s = GoogleSheetsService()
    distros = await s.fetch_all_distros()
    await s.close()
    
    # Distros com mensagem de erro na descrição
    errors = [x for x in distros if x.description and 'foi possível encontrar' in (x.description or '')]
    print(f"\n=== Distros com ERRO na descrição ({len(errors)}) ===")
    for x in errors:
        print(f"  - {x.name} ({x.id})")
    
    # Distros com data inválida (época Unix ou muito recente)
    invalid_dates = []
    for x in distros:
        date = x.latest_release_date
        if date:
            if '1970' in str(date) or '1969' in str(date):
                invalid_dates.append((x.name, date, "Época Unix"))
            elif '2026-01-03' in str(date) or '2026-01-02' in str(date):
                invalid_dates.append((x.name, date, "Data atual (fallback)"))
    
    print(f"\n=== Distros com DATA inválida ({len(invalid_dates)}) ===")
    for name, date, reason in invalid_dates:
        print(f"  - {name}: {date} ({reason})")

asyncio.run(main())
