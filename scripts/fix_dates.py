"""Script para corrigir datas inválidas na planilha - versão simplificada."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from api.services.google_sheets_service import GoogleSheetsService

# Datas corretas pesquisadas manualmente
CORRECT_DATES = {
    "Loc-OS": "2025-12-29",      # Loc-OS 24 
    "Omarchy": "2025-12-15",     # Omarchy 3.2.3
    "Bazzite": "2024-10-29",     # Bazzite 41
}

async def main():
    sheets = GoogleSheetsService()
    
    print("=== Corrigindo datas inválidas ===\n")
    
    try:
        # Obter token
        access_token = await sheets._get_access_token()
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Buscar headers
        url_headers = f"{sheets.SHEETS_API_URL}/{sheets.SHEET_ID}/values/{sheets.SHEET_NAME}!1:1"
        resp = await sheets.client.get(url_headers, headers=headers)
        resp.raise_for_status()
        headers_row = resp.json().get('values', [[]])[0]
        column_map = {h: i for i, h in enumerate(headers_row)}
        
        # Encontrar coluna Latest Release
        date_col_idx = column_map.get("Latest Release")
        if date_col_idx is None:
            print("ERRO: Coluna 'Latest Release' não encontrada!")
            print(f"Colunas disponíveis: {list(column_map.keys())}")
            await sheets.close()
            return
        
        date_col_letter = sheets._get_column_letter(date_col_idx)
        print(f"Coluna 'Latest Release': {date_col_letter} (index {date_col_idx})")
        
        # Buscar coluna de nomes
        url_names = f"{sheets.SHEETS_API_URL}/{sheets.SHEET_ID}/values/{sheets.SHEET_NAME}!A:A"
        resp = await sheets.client.get(url_names, headers=headers)
        resp.raise_for_status()
        names_column = resp.json().get('values', [])
        name_to_row = {row[0]: i + 1 for i, row in enumerate(names_column) if row}
        
        # Preparar batch update
        batch_data = []
        for name, date in CORRECT_DATES.items():
            if name in name_to_row:
                row = name_to_row[name]
                batch_data.append({
                    'range': f"{sheets.SHEET_NAME}!{date_col_letter}{row}",
                    'values': [[date]]
                })
                print(f"  ✓ {name} (linha {row}): {date}")
            else:
                print(f"  ✗ {name}: Não encontrado na planilha")
        
        if batch_data:
            url_batch = f"{sheets.SHEETS_API_URL}/{sheets.SHEET_ID}/values:batchUpdate"
            resp = await sheets.client.post(
                url_batch,
                json={"valueInputOption": "RAW", "data": batch_data},
                headers=headers,
            )
            resp.raise_for_status()
            print(f"\n✅ Atualizado com sucesso! {len(batch_data)} células")
        else:
            print("\n⚠️ Nenhuma célula para atualizar")
            
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    await sheets.close()

asyncio.run(main())
