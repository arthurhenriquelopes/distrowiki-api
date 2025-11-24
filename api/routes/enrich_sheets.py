from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from ..services.google_sheets_service import GoogleSheetsService
from ..services.groq_service import enrich_distros_with_groq, SheetColumn, FIELD_PROMPTS
from ..security import get_api_key  # ← ADICIONAR ISSO


router = APIRouter(prefix="/enrich-sheets", tags=["Enriquecimento Sheets"])


@router.post(
    "-manual/",
    dependencies=[Depends(get_api_key)]  # ← PROTEGER
)
async def enrich_sheets_manual_endpoint(
    fields: Optional[List[SheetColumn]] = Body(None, embed=True)
):
    """
    🔒 PROTEGIDO: Requer API Key no header X-API-Key
    
    Enriquecimento manual dos dados do Google Sheets via Groq.
    """
    sheets_service = GoogleSheetsService()
    try:
        distros = await sheets_service.fetch_all_distros()
        distro_names = [distro.name for distro in distros if distro.name]
        enriched = await enrich_distros_with_groq(distro_names, fields)
        
        return JSONResponse(content={
            "results": enriched,
            "total_distros": len(distro_names),
            "total_enriched": len(enriched),
            "fields_enriched": [f.value for f in (fields or [])]
        })
    finally:
        await sheets_service.close()

@router.post("-manual/by-name")
async def enrich_specific_distros_manual_endpoint(
    names: List[str] = Body(..., embed=True),
    fields: Optional[List[SheetColumn]] = Body(None, embed=True),
    api_key: str = Depends(get_api_key)
):
    """
    🔒 PROTEGIDO: Enriquece distros específicas (manual - só retorna JSON).
    """
    enriched = await enrich_distros_with_groq(names, fields)
    return JSONResponse(content={
        "results": enriched,
        "total": len(enriched),
        "fields_enriched": [f.value for f in (fields or [])]
    })


@router.post(
    "/",
    dependencies=[Depends(get_api_key)]  # ← PROTEGER
)
async def enrich_sheets_auto_endpoint(
    fields: Optional[List[SheetColumn]] = Body(None, embed=True)
):
    """
    🔒 PROTEGIDO: Requer API Key no header X-API-Key
    
    Enriquecimento AUTOMÁTICO: atualiza a planilha diretamente.
    """
    sheets_service = GoogleSheetsService()
    try:
        distros = await sheets_service.fetch_all_distros()
        distro_names = [distro.name for distro in distros if distro.name]
        enriched = await enrich_distros_with_groq(distro_names, fields)
        
        fields_to_update = fields or [
            SheetColumn.IDLE_RAM_USAGE,
            SheetColumn.CPU_SCORE,
            SheetColumn.IO_SCORE,
            SheetColumn.REQUIREMENTS
        ]
        
        update_result = await sheets_service.update_enriched_data(enriched, fields_to_update)
        
        return JSONResponse(content={
            "enrichment": {
                "total_distros": len(distro_names),
                "total_enriched": len(enriched),
                "fields_enriched": [f.value for f in fields_to_update]
            },
            "sheet_update": update_result,
            "results": enriched[:5]
        })
    finally:
        await sheets_service.close()

@router.post(
    "/by-name",
    dependencies=[Depends(get_api_key)]
)
async def enrich_specific_distros_auto_endpoint(
    names: List[str] = Body(..., embed=True),
    fields: Optional[List[SheetColumn]] = Body(None, embed=True)
):
    """
    🔒 PROTEGIDO: Enriquece distros específicas E atualiza a planilha automaticamente.
    
    Exemplo - Enriquecer Package Management de 3 distros BSD:
    {
        "names": ["MidnightBSD", "NetBSD", "OpenBSD"],
        "fields": ["Package Management"]
    }
    
    Exemplo - Enriquecer múltiplos campos:
    {
        "names": ["Ubuntu", "Fedora"],
        "fields": ["Idle RAM Usage", "CPU Score", "Desktop"]
    }
    """
    sheets_service = GoogleSheetsService()
    try:
        # 1. Enriquecer via Groq apenas as distros especificadas
        enriched = await enrich_distros_with_groq(names, fields)
        
        # 2. Atualizar a planilha automaticamente
        fields_to_update = fields or [
            SheetColumn.IDLE_RAM_USAGE,
            SheetColumn.CPU_SCORE,
            SheetColumn.IO_SCORE,
            SheetColumn.REQUIREMENTS
        ]
        
        update_result = await sheets_service.update_enriched_data(
            enriched, 
            fields_to_update
        )
        
        return JSONResponse(content={
            "enrichment": {
                "distros_requested": names,
                "total_enriched": len(enriched),
                "fields_enriched": [f.value for f in fields_to_update]
            },
            "sheet_update": update_result,
            "results": enriched
        })
    finally:
        await sheets_service.close()


# Endpoints públicos (sem proteção)
@router.get("/available-columns")
async def get_available_columns():
    """✅ PÚBLICO: Retorna colunas disponíveis."""
    return {
        "columns": [
            {"name": field.value, "key": field.name, "prompt_instruction": FIELD_PROMPTS[field]} 
            for field in SheetColumn
        ],
        "total": len(SheetColumn),
        "default_fields": ["Idle RAM Usage", "CPU Score", "I/O Score", "Requirements"]
    }


@router.get("/column-groups")
async def get_column_groups():
    """✅ PÚBLICO: Retorna grupos pré-definidos."""
    return {
        "groups": {
            "performance": {
                "label": "Performance e Recursos",
                "columns": ["Idle RAM Usage", "CPU Score", "I/O Score", "Requirements", "Image Size"]
            },
            "basic_info": {
                "label": "Informações Básicas",
                "columns": ["Description", "Category", "OS Type", "Status"]
            },
            "technical": {
                "label": "Detalhes Técnicos",
                "columns": ["Base", "Desktop", "Package Management", "Office Suite"]
            }
        }
    }
