"""Rotas da API DistroWiki."""

from .distros import router as distros_router
from .enrich_sheets import router as enrich_sheets_router

__all__ = [
    "distros_router",
    "enrich_sheets_router"
]
