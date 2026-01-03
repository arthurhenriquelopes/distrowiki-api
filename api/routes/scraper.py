"""
Rotas para enriquecer dados via scraping do DistroWatch.
"""

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import List, Optional
import logging
from ..services.distrowatch_scraper import DistroWatchScraper, scrape_distrowatch_data
from ..services.google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/distrowatch/scrape")
async def scrape_distrowatch(
    distro_ids: List[str],
    background_tasks: BackgroundTasks,
    update_sheet: bool = Query(False, description="Atualizar Google Sheets com os dados")
):
    """
    Inicia scraping do DistroWatch para as distros especificadas.
    
    Args:
        distro_ids: Lista de IDs das distros (ex: ["ubuntu", "manjaro"])
        update_sheet: Se True, atualiza o Google Sheets automaticamente
        
    Returns:
        Status do scraping
    """
    if len(distro_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Máximo de 10 distros por vez para evitar bloqueio"
        )
    
    logger.info(f"Iniciando scraping para {len(distro_ids)} distros: {distro_ids}")
    
    try:
        results = await scrape_distrowatch_data(distro_ids)
        
        # Contar sucessos e falhas
        successes = [r for r in results if "error" not in r]
        failures = [r for r in results if "error" in r]
        
        return {
            "status": "completed",
            "total": len(results),
            "success_count": len(successes),
            "failure_count": len(failures),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erro no scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/distrowatch/single/{distro_id}")
async def scrape_single_distro(distro_id: str):
    """
    Scrape de uma única distro.
    
    Args:
        distro_id: ID da distro (ex: "ubuntu")
        
    Returns:
        Dados extraídos
    """
    scraper = DistroWatchScraper()
    try:
        result = await scraper.scrape_distro(distro_id)
        return result
    finally:
        await scraper.close()


@router.get("/distrowatch/test")
async def test_scraper():
    """
    Testa o scraper com Ubuntu (distro mais popular).
    """
    scraper = DistroWatchScraper()
    try:
        result = await scraper.scrape_distro("ubuntu")
        return {
            "status": "ok",
            "message": "Scraper funcionando",
            "sample_data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        await scraper.close()
