"""
Módulo de Scraping - DistroWatch
Scraping modular de distribuições Linux do DistroWatch usando proxies.
"""

from .routes import scraping_router

__all__ = ["scraping_router"]
