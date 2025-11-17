"""Sistema de cache para dados da API."""

from .cache_manager import CacheManager, get_cache_manager

__all__ = [
    "CacheManager",
    "get_cache_manager"
]
