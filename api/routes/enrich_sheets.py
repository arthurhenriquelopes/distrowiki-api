
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from ..services.google_sheets_service import GoogleSheetsService
from ..services.groq_service import enrich_distros_with_groq

router = APIRouter(prefix="/enrich-sheets", tags=["Enriquecimento Sheets"])

@router.post("/by-name")
async def enrich_by_name_endpoint(names: list[str] = Body(..., embed=True)):
    """
    Recebe uma lista de nomes de distros e retorna os dados enriquecidos via Groq.
    Exemplo de body:
    {
        "names": ["Ubuntu", "Fedora"]
    }
    """
    enriched = await enrich_distros_with_groq(names)
    return JSONResponse(content={"results": enriched})

@router.post("/")
async def enrich_sheets_endpoint():
    """
    Enriquecimento manual dos dados do Google Sheets via Groq.
    Busca nomes das distros, enriquece via IA e retorna dados para atualização manual.
    """
    sheets_service = GoogleSheetsService()
    try:
        # Busca todas as distros da planilha
        distros = await sheets_service.fetch_all_distros()
        # Extrai os nomes das distros
        distro_names = [distro.name for distro in distros if distro.name]
        # Enriquecimento via Groq
        enriched = await enrich_distros_with_groq(distro_names)
        return JSONResponse(content={"results": enriched})
    finally:
        await sheets_service.close()
