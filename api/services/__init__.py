"""Serviços de integração com fontes de dados externas."""

from .distrowatch_service import DistroWatchService
from .google_sheets_service import GoogleSheetsService

__all__ = [
    "DistroWatchService",
    "GoogleSheetsService"
]
