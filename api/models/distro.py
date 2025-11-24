"""
Modelos de dados para distribuições Linux.

Define as estruturas de dados utilizadas na API de catálogo de distros,
conforme especificado no Módulo 1.
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class DistroFamily(str, Enum):
    """Família/base da distribuição Linux."""
    DEBIAN = "debian"
    UBUNTU = "ubuntu"
    FEDORA = "fedora"
    ARCH = "arch"
    OPENSUSE = "opensuse"
    GENTOO = "gentoo"
    SLACKWARE = "slackware"
    INDEPENDENT = "independent"
    OTHER = "other"


class DesktopEnvironment(str, Enum):
    """Ambientes de desktop disponíveis."""
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    MATE = "mate"
    CINNAMON = "cinnamon"
    LXDE = "lxde"
    LXQT = "lxqt"
    BUDGIE = "budgie"
    PANTHEON = "pantheon"
    DEEPIN = "deepin"
    I3 = "i3"
    SWAY = "sway"
    CUSTOM = "custom"
    OTHER = "other"


class DistroMetadata(BaseModel):
    """
    Metadados de uma distribuição Linux extraídos do DistroWatch.
    
    Campos principais:
    - id: identificador único (slug do DistroWatch)
    - name: nome da distribuição
    - description: descrição completa da distribuição
    - os_type: tipo do sistema (Linux, BSD, etc)
    - based_on: distribuição base
    - family: família/base da distro (enum)
    - origin: país de origem
    - architecture: arquiteturas suportadas
    - desktop: ambiente desktop principal
    - desktop_environments: lista de DEs disponíveis
    - category: categorias (Desktop, Server, etc)
    - status: status (Active, Dormant, etc)
    - ranking: posição no ranking do DistroWatch
    - rating: avaliação média dos usuários
    - homepage: site oficial
    """
    
    id: str = Field(
        ...,
        description="Identificador único da distribuição (slug do DistroWatch)",
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
        description="Família/base da distribuição (determinada automaticamente)",
        example="arch"
    )
    
    origin: Optional[str] = Field(
        None,
        description="País de origem",
        example="Germany"
    )
    
    architecture: Optional[str] = Field(
        None,
        description="Arquiteturas suportadas",
        example="x86_64, x86-64-v3"
    )
    
    desktop: Optional[str] = Field(
        None,
        description="Ambiente desktop principal",
        example="KDE Plasma"
    )
    
    desktop_environments: List[DesktopEnvironment] = Field(
        default_factory=list,
        description="Lista de ambientes gráficos disponíveis",
        example=["kde", "gnome"]
    )
    
    category: Optional[str] = Field(
        None,
        description="Categorias da distribuição",
        example="Desktop, Live Medium"
    )
    
    status: Optional[str] = Field(
        None,
        description="Status da distribuição",
        example="Active"
    )
    
    ranking: Optional[int] = Field(
        None,
        description="Posição no ranking do DistroWatch (menor = mais popular)",
        example=1
    )
    
    rating: Optional[float] = Field(
        None,
        description="Avaliação média dos usuários (0-10)",
        example=8.1
    )
    
    homepage: Optional[str] = Field(
        None,
        description="URL do site oficial",
        example="https://cachyos.org/"
    )
    
    logo: Optional[str] = Field(
        None,
        description="URL da logo da distribuição no DistroWatch",
        example="https://distrowatch.com/images/yvzhuwbpy/cachyos.png"
    )
    
    # Metadados para compatibilidade (deprecated)
    summary: Optional[str] = Field(
        None,
        description="[DEPRECATED] Use 'description' - Resumo breve",
    )
    
    latest_release_date: Optional[datetime] = Field(
        None,
        description="Data do último lançamento estável",
    )
    
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp da última atualização dos dados"
    )
    
    class Config:
        """Configuração do modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "id": "cachyos",
                "name": "CachyOS",
                "description": "CachyOS is a Linux distribution based on Arch Linux. It focuses on speed and security optimisations...",
                "os_type": "Linux",
                "based_on": "Arch",
                "family": "arch",
                "origin": "Germany",
                "architecture": "x86_64, x86-64-v3",
                "desktop": "KDE Plasma",
                "desktop_environments": ["kde"],
                "category": "Desktop, Live Medium",
                "status": "Active",
                "ranking": 1,
                "rating": 8.1,
                "homepage": "https://cachyos.org/",
                "last_updated": "2025-11-06T10:00:00Z"
            }
        }


class DistroListResponse(BaseModel):
    """
    Resposta do endpoint GET /distros.
    
    Inclui lista de distribuições e metadados de paginação.
    """
    
    distros: List[DistroMetadata] = Field(
        ...,
        description="Lista de distribuições"
    )
    
    total: int = Field(
        ...,
        description="Total de distribuições disponíveis",
        example=50
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
    
    class Config:
        """Configuração do modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "distros": [
                    {
                        "id": "ubuntu",
                        "name": "Ubuntu",
                        "summary": "Distribuição Linux baseada em Debian",
                        "family": "debian",
                        "desktop_environments": ["gnome"],
                        "latest_release_date": "2024-10-01T00:00:00Z",
                        "homepage": "https://ubuntu.com"
                    }
                ],
                "total": 50,
                "page": 1,
                "page_size": 20,
                "cache_timestamp": "2025-11-06T10:00:00Z"
            }
        }
