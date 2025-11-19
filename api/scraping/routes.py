"""Rotas para scraping"""
import logging
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)
scraping_router = APIRouter(prefix="/scraping", tags=["Scraping"])

@scraping_router.get("/scraped-data")
async def get_scraped_data(skip: int = 0, limit: int = 100):
    cache_file = Path("data/cache/distros_scraped.json")
    if not cache_file.exists():
        raise HTTPException(status_code=404, detail="Dados não disponíveis")
    with open(cache_file, 'r') as f:
        data = json.load(f)
    distros = data.get('distros', [])
    return {"success": True, "total": len(distros), "distros": distros[skip:skip+limit]}

@scraping_router.get("/status")
async def get_status():
    cache_file = Path("data/cache/distros_scraped.json")
    if not cache_file.exists():
        return {"available": False}
    with open(cache_file, 'r') as f:
        data = json.load(f)
    return {"available": True, "scraped_at": data.get('scraped_at'), "total": data.get('total', 0)}
