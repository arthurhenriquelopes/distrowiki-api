"""
Rotas da API para distribuições Linux.
"""

import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Query, Header

from ..models.distro import DistroMetadata, DistroListResponse
from ..services.google_sheets_service import GoogleSheetsService
from ..cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependência para CacheManager
def get_cache_manager() -> CacheManager:
    """Retorna instância do CacheManager."""
    return CacheManager()


@router.get("/distros", response_model=DistroListResponse)
async def get_distros(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    family: Optional[str] = Query(None, description="Filtrar por família"),
    sort_by: Optional[str] = Query("name", description="Campo para ordenação"),
    order: Optional[str] = Query("asc", description="Ordem: asc ou desc"),
    force_refresh: bool = Query(False, description="Forçar atualização do cache"),
    cache_manager: CacheManager = Depends(get_cache_manager),
):
    """
    Retorna lista paginada de distribuições Linux.
    
    - **page**: Número da página (padrão: 1)
    - **page_size**: Tamanho da página (padrão: 20, máx: 100)
    - **family**: Filtrar por família (ex: Debian, Arch)
    - **sort_by**: Campo para ordenação (name, rating, etc)
    - **order**: asc ou desc
    - **force_refresh**: Se true, ignora cache e busca dados atualizados
    """
    try:
        # Verificar se tem cache válido
        cached_data = None if force_refresh else cache_manager.get_distros_cache()
        
        if cached_data:
            logger.info("Usando dados do cache")
            distros = cached_data
        else:
            logger.info("Buscando dados do Google Sheets...")
            sheets_service = GoogleSheetsService()
            distros = await sheets_service.fetch_all_distros()
            await sheets_service.close()
            
            # Salvar no cache
            cache_manager.save_distros_cache(distros)
            logger.info(f"Cache atualizado com {len(distros)} distros")
        
        # Filtrar por família se especificado
        if family:
            distros = [d for d in distros if d.family.lower() == family.lower()]
        
        # Ordenar
        reverse = (order.lower() == "desc")
        if sort_by == "name":
            distros.sort(key=lambda x: x.name.lower(), reverse=reverse)
        elif sort_by == "rating":
            distros.sort(key=lambda x: x.rating or 0, reverse=reverse)
        elif sort_by == "family":
            distros.sort(key=lambda x: x.family.lower(), reverse=reverse)
        
        # Paginar
        total = len(distros)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = distros[start:end]
        
        return DistroListResponse(
            distros=paginated,
            total=total,
            page=page,
            page_size=page_size,
            cache_timestamp=None
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar distros: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/distros/{distro_id}", response_model=DistroMetadata)
async def get_distro_by_id(
    distro_id: str,
    force_refresh: bool = Query(False, description="Forçar atualização do cache"),
    cache_manager: CacheManager = Depends(get_cache_manager),
):
    """
    Retorna detalhes de uma distribuição específica pelo ID.
    
    - **distro_id**: ID único da distribuição (ex: ubuntu, fedora)
    - **force_refresh**: Se true, ignora cache
    """
    try:
        # Verificar cache
        cached_data = None if force_refresh else cache_manager.get_distros_cache()
        
        if cached_data:
            distros = cached_data
        else:
            sheets_service = GoogleSheetsService()
            distros = await sheets_service.fetch_all_distros()
            await sheets_service.close()
            cache_manager.save_distros_cache(distros)
        
        # Buscar distro pelo ID
        distro = next((d for d in distros if d.id == distro_id), None)
        
        if not distro:
            raise HTTPException(
                status_code=404,
                detail=f"Distribuição '{distro_id}' não encontrada"
            )
        
        return distro
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar distro {distro_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/refresh", 
    summary="Força atualização do cache de distros",
    response_model=Dict[str, Any]
)
async def refresh_distros_cache(
    api_key: str = Header(..., alias="X-API-Key", description="API Key para autenticação"),
):
    """
    Remove o cache de distros forçando nova busca nos próximos requests.
    
    Requer autenticação via API Key no header X-API-Key.
    
    **Uso:**
    ```
    curl -X POST 'http://localhost:8000/cache/refresh' \\
      -H 'X-API-Key: YOUR_API_KEY'
    ```
    """
    # Verificar API Key
    expected_key = os.getenv("API_KEY")
    if not expected_key or api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida ou ausente. Use header X-API-Key."
        )
    
    try:
        # Deletar cache de distros usando Path diretamente
        cache_file = Path("data/cache/distro_cache.json")
        
        if cache_file.exists():
            cache_file.unlink()
            logger.info(f"Cache de distros removido: {cache_file}")
            return {
                "success": True,
                "message": "Cache removido com sucesso",
                "cache_file": str(cache_file),
                "timestamp": datetime.utcnow().isoformat(),
                "next_request": "Próximo GET /distros irá buscar dados atualizados do Sheets"
            }
        else:
            return {
                "success": True,
                "message": "Cache já estava vazio",
                "cache_file": str(cache_file),
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erro ao remover cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover cache: {str(e)}"
        )


@router.delete("/cache/distros",
    summary="Remove cache de distros (público com confirmação)",
    response_model=Dict[str, Any]
)
async def clear_distros_cache(
    confirm: bool = Query(False, description="Confirmar remoção do cache"),
):
    """
    Remove o cache de distros se confirm=true.
    
    **Uso:**
    ```
    curl -X DELETE 'http://localhost:8000/cache/distros?confirm=true'
    ```
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Adicione ?confirm=true para confirmar a remoção do cache"
        )
    
    try:
        # Deletar cache usando Path diretamente
        cache_file = Path("data/cache/distro_cache.json")
        
        if cache_file.exists():
            cache_file.unlink()
            logger.info(f"Cache removido via endpoint público: {cache_file}")
            return {
                "success": True,
                "message": "Cache removido com sucesso",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Cache já estava vazio",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao remover cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
