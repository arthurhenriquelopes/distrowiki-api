"""Rotas da API."""

from .distros import router as distros_router, logo_router

__all__ = ["distros_router", "logo_router"]
