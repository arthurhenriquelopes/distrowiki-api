"""Rotas da API."""

from .distros import router as distros_router, logo_router
from .enrich_sheets import router as enrich_sheets_router

__all__ = [
    "distros_router",
    "logo_router",
    "enrich_sheets_router",
]
