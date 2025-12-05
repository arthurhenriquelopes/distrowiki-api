# api/routes/enrich_sheets.py

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from ..services.google_sheets_service import GoogleSheetsService
from ..services.groq_service import enrich_distros_with_groq, SheetColumn, FIELD_PROMPTS
from ..services.release_scraper import get_bulk_release_dates
from ..security import get_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/enrich-sheets", tags=["Enriquecimento Sheets"])


@router.post("-manual/", dependencies=[Depends(get_api_key)])
async def enrich_sheets_manual_endpoint(
    fields: Optional[List[SheetColumn]] = Body(None, embed=True)
):
    """
    🔒 PROTEGIDO: Enriquecimento manual (retorna JSON sem atualizar planilha).
    """
    sheets_service = GoogleSheetsService()
    try:
        distros = await sheets_service.fetch_all_distros()
        distro_names = [distro.name for distro in distros if distro.name]
        enriched = await enrich_distros_with_groq(distro_names, fields)

        return JSONResponse(
            content={
                "results": enriched,
                "total_distros": len(distro_names),
                "total_enriched": len(enriched),
                "fields_enriched": [f.value for f in (fields or [])],
            }
        )
    finally:
        await sheets_service.close()


@router.post("-manual/by-name", dependencies=[Depends(get_api_key)])
async def enrich_specific_distros_manual_endpoint(
    names: List[str] = Body(..., embed=True),
    fields: Optional[List[SheetColumn]] = Body(None, embed=True),
):
    """
    🔒 PROTEGIDO: Enriquece distros específicas (manual - só retorna JSON).
    """
    enriched = await enrich_distros_with_groq(names, fields)
    return JSONResponse(
        content={
            "results": enriched,
            "total": len(enriched),
            "fields_enriched": [f.value for f in (fields or [])],
        }
    )


@router.post("/", dependencies=[Depends(get_api_key)])
async def enrich_sheets_auto_endpoint(
    fields: Optional[List[SheetColumn]] = Body(None, embed=True)
):
    """
    🔒 PROTEGIDO: Enriquecimento AUTOMÁTICO de TODAS as distros.
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
            SheetColumn.REQUIREMENTS,
        ]

        update_result = await sheets_service.update_enriched_data(
            enriched, fields_to_update
        )

        return JSONResponse(
            content={
                "enrichment": {
                    "total_distros": len(distro_names),
                    "total_enriched": len(enriched),
                    "fields_enriched": [f.value for f in fields_to_update],
                },
                "sheet_update": update_result,
                "results": enriched[:5],
            }
        )
    finally:
        await sheets_service.close()


@router.post("/by-name", dependencies=[Depends(get_api_key)])
async def enrich_specific_distros_auto_endpoint(
    names: List[str] = Body(..., embed=True),
    fields: Optional[List[SheetColumn]] = Body(None, embed=True),
):
    """
    🔒 PROTEGIDO: Enriquece distros específicas + scraping DistroWatch.

    Exemplo:
    {
        "names": ["CachyOS", "Ubuntu", "Fedora"],
        "fields": ["Latest Release", "CPU Score", "Desktop"]
    }
    """
    sheets_service = GoogleSheetsService()
    try:
        fields_to_update = fields or [
            SheetColumn.IDLE_RAM_USAGE,
            SheetColumn.CPU_SCORE,
            SheetColumn.IO_SCORE,
            SheetColumn.REQUIREMENTS,
        ]

        enriched_data = {}

        # 1. 🔍 SCRAPING do DistroWatch para Latest Release
        if SheetColumn.LATEST_RELEASE in fields_to_update:
            logger.info(
                f"🔍 Scraping Latest Release de {len(names)} distros do DistroWatch..."
            )

            # Buscar IDs das distros
            all_distros = await sheets_service.fetch_all_distros()
            name_to_id = {d.name: d.id for d in all_distros if d.name in names}

            # Scraping em paralelo
            release_dates = await get_bulk_release_dates(list(name_to_id.values()))

            # Mapear de volta para nomes
            for distro_name in names:
                distro_id = name_to_id.get(distro_name)
                if distro_id and distro_id in release_dates:
                    enriched_data[distro_name] = {
                        "Name": distro_name,
                        "Latest Release": release_dates[distro_id],
                    }
                    logger.info(f"  ✅ {distro_name}: {release_dates[distro_id]}")

        # 2. 🤖 Groq IA para outros campos
        fields_for_groq = [
            f for f in fields_to_update if f != SheetColumn.LATEST_RELEASE
        ]

        if fields_for_groq:
            logger.info(
                f"🤖 Enriquecendo via Groq: {[f.value for f in fields_for_groq]}"
            )
            groq_results = await enrich_distros_with_groq(names, fields_for_groq)

            # Merge resultados
            for item in groq_results:
                distro_name = item.get("Name")
                if distro_name in enriched_data:
                    enriched_data[distro_name].update(item)
                else:
                    enriched_data[distro_name] = item

        # Converter dict para lista
        enriched = list(enriched_data.values())

        # 3. 📝 Atualizar planilha
        update_result = await sheets_service.update_enriched_data(
            enriched, fields_to_update
        )

        return JSONResponse(
            content={
                "enrichment": {
                    "distros_requested": names,
                    "total_enriched": len(enriched),
                    "fields_enriched": [f.value for f in fields_to_update],
                },
                "sheet_update": update_result,
                "results": enriched,
            }
        )
    finally:
        await sheets_service.close()


# ========== ENDPOINTS PÚBLICOS ==========


@router.get("/available-columns")
async def get_available_columns():
    """✅ PÚBLICO: Retorna colunas disponíveis para enriquecimento."""
    return {
        "columns": [
            {
                "name": field.value,
                "key": field.name,
                "prompt_instruction": FIELD_PROMPTS[field],
            }
            for field in SheetColumn
        ],
        "total": len(SheetColumn),
        "default_fields": ["Idle RAM Usage", "CPU Score", "I/O Score", "Requirements"],
    }


@router.get("/column-groups")
async def get_column_groups():
    """✅ PÚBLICO: Retorna grupos pré-definidos de colunas."""
    return {
        "groups": {
            "performance": {
                "label": "Performance e Recursos",
                "columns": [
                    "Idle RAM Usage",
                    "CPU Score",
                    "I/O Score",
                    "Requirements",
                    "Image Size",
                ],
            },
            "basic_info": {
                "label": "Informações Básicas",
                "columns": ["Description", "Category", "OS Type", "Status", "Origin"],
            },
            "technical": {
                "label": "Detalhes Técnicos",
                "columns": ["Base", "Desktop", "Package Management", "Office Suite"],
            },
            "dates": {
                "label": "Datas e Lançamentos",
                "columns": ["Release Date", "Latest Release"],
            },
        }
    }
