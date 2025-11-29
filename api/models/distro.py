"""
Modelos de dados para distribuições Linux.

Define as estruturas de dados utilizadas na API de catálogo de distros,
conforme especificado no Módulo 1.
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class DistroFamily(str, Enum):
    """Família/base da distribuição Linux."""
    DEBIAN = "Debian"
    UBUNTU = "Ubuntu"
    FEDORA = "Fedora"
    ARCH = "Arch"
    OPENSUSE = "openSUSE"
    GENTOO = "Gentoo"
    SLACKWARE = "Slackware"
    INDEPENDENT = "Independent"
    OTHER = "Other"


class DesktopEnvironment(str, Enum):
    """Ambientes de desktop disponíveis."""
    GNOME = "GNOME"
    KDE = "KDE Plasma"
    XFCE = "Xfce"
    MATE = "MATE"
    CINNAMON = "Cinnamon"
    LXDE = "LXDE"
    LXQT = "LXQt"
    BUDGIE = "Budgie"
    PANTHEON = "Pantheon"
    DEEPIN = "Deepin"
    I3 = "i3"
    SWAY = "Sway"
    CUSTOM = "Custom"
    OTHER = "Other"


class DistroMetadata(BaseModel):
    """
    Metadados de uma distribuição Linux.
    
    Inclui dados enriquecidos via IA do Google Sheets.
    """
    
    id: str = Field(
        ...,
        description="Identificador único da distribuição",
        example="cachyos"
    )
    
    name: str = Field(
        ...,
        description="Nome oficial da distribuição",
        example="CachyOS"
    )
    
    description: Optional[str] = Field(
        None,
        description="Descrição completa da distribuição",
        example="CachyOS is a Linux distribution based on Arch Linux..."
    )
    
    os_type: Optional[str] = Field(
        None,
        description="Tipo do sistema operacional",
        example="Linux"
    )
    
    based_on: Optional[str] = Field(
        None,
        description="Distribuição base",
        example="Arch"
    )
    
    family: DistroFamily = Field(
        DistroFamily.INDEPENDENT,
        description="Família/base da distribuição",
        example="Arch"
    )
    
    origin: Optional[str] = Field(
        None,
        description="País de origem",
        example="Germany"
    )
    
    architecture: Optional[str] = Field(
        None,
        description="Arquiteturas suportadas",
        example="x86_64, ARM64"
    )
    
    desktop_environments: List[DesktopEnvironment] = Field(
        default_factory=list,
        description="Lista de ambientes gráficos disponíveis",
        example=["KDE Plasma", "GNOME"]
    )
    
    category: Optional[str] = Field(
        None,
        description="Categoria principal da distribuição",
        example="Desktop/Gaming"
    )
    
    status: Optional[str] = Field(
        None,
        description="Status de desenvolvimento",
        example="Active"
    )
    
    ranking: Optional[int] = Field(
        None,
        description="Posição no ranking do DistroWatch",
        example=1
    )
    
    rating: Optional[float] = Field(
        None,
        description="Avaliação média (0-10)",
        example=8.1
    )
    
    homepage: Optional[str] = Field(
        None,
        description="URL do site oficial",
        example="https://cachyos.org/"
    )
    
    logo: Optional[str] = Field(
        None,
        description="URL da logo da distribuição",
        example="https://distrowatch.com/images/cachyos.png"
    )
    
    # ====== CAMPOS DE PERFORMANCE (Enriquecidos via IA) ======
    
    idle_ram_usage: Optional[int] = Field(
        None,
        description="Uso de RAM em idle (MB)",
        example=800
    )
    
    cpu_score: Optional[int] = Field(
        None,
        description="Score de performance de CPU (1-10)",
        example=8
    )
    
    io_score: Optional[int] = Field(
        None,
        description="Score de performance de I/O (1-10)",
        example=9
    )
    
    requirements: Optional[str] = Field(
        None,
        description="Requisitos de hardware: Leve, Médio ou Alto",
        example="Médio"
    )
    
    package_management: Optional[str] = Field(
        None,
        description="Gerenciador de pacotes principal",
        example="pacman"
    )
    
    image_size: Optional[float] = Field(
        None,
        description="Tamanho típico da ISO em GB",
        example=2.5
    )
    
    office_suite: Optional[str] = Field(
        None,
        description="Suite de escritório incluída",
        example="LibreOffice"
    )
    
    # ====== FIM CAMPOS DE PERFORMANCE ======
    
    summary: Optional[str] = Field(
        None,
        description="[DEPRECATED] Use 'description'",
    )
    
    latest_release_date: Optional[str] = Field(
        None,
        description="Data da última versão lançada (formato DD/MM/AAAA)",
        example="24/11/2025"
    )
    
    release_year: Optional[int] = Field(
        None,
        description="Ano de lançamento original da distribuição",
        example=2021
    )
    
    class Config:
        """Configuração do modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "id": "cachyos",
                "name": "CachyOS",
                "description": "Arch-based distribution optimized for performance",
                "os_type": "Linux",
                "family": "Arch",
                "category": "Desktop/Performance",
                "desktop_environments": ["KDE Plasma"],
                "idle_ram_usage": 800,
                "cpu_score": 9,
                "io_score": 9,
                "requirements": "Médio",
                "package_management": "pacman",
                "image_size": 2.5,
                "latest_release_date": "15/11/2025",
                "release_year": 2021,
                "homepage": "https://cachyos.org/"
            }
        }


class DistroListResponse(BaseModel):
    """Resposta do endpoint GET /distros."""
    
    distros: List[DistroMetadata] = Field(
        ...,
        description="Lista de distribuições"
    )
    
    total: int = Field(
        ...,
        description="Total de distribuições disponíveis",
        example=81
    )
    
    page: int = Field(
        1,
        description="Página atual",
        example=1
    )
    
    page_size: int = Field(
        20,
        description="Tamanho da página",
        example=20
    )
    
    cache_timestamp: Optional[datetime] = Field(
        None,
        description="Timestamp do cache utilizado"
    )
