"""
Mapeamento de IDs DistroWiki -> DistroWatch.

O DistroWatch usa IDs específicos nas URLs que podem diferir
dos IDs usados no DistroWiki. Este arquivo mapeia as diferenças.

Formato: distrowiki_id -> distrowatch_id
"""

# Mapeamento de IDs que diferem entre DistroWiki e DistroWatch
# Chave: ID do DistroWiki
# Valor: ID do DistroWatch
DISTROWIKI_TO_DISTROWATCH = {
    # Arch-based
    "archlinux": "arch",
    "artixlinux": "artix",
    "arcolinux": "arco",
    "endeavouros": "endeavour",
    
    # Debian/Ubuntu-based
    "linuxmint": "mint",
    "ubuntustudio": "ubuntustudio",
    "ubuntukylin": "ubuntukylin",
    "ubuntucinnamon": "ubuntucinnamon",
    "ubuntuunity": "ubuntuunity",
    "mxlinux": "mx",
    "popos": "pop",
    "pop_os": "pop",
    "kdeneon": "neon",
    
    # RHEL-based
    "almalinux": "alma",
    "alma": "alma",
    "rockylinux": "rocky",
    
    # SUSE-based
    "opensuse": "opensuse",
    "opensusetumbleweed": "opensuse",
    "opensuselead": "opensuse",
    
    # BSD
    "dragonflybsd": "dragonfly",
    "ghostbsd": "ghostbsd",
    "truenas": "truenas",
    
    # Outros
    "cachyos": "cachy",
    "nobara": "nobara",
    "peppermint": "peppermint",
    "sparky": "sparky",
    "nitrux": "nitrux",
    "garuda": "garuda",
    "zorin": "zorin",
    "solus": "solus",
    "void": "void",
    "nixos": "nixos",
    "gentoo": "gentoo",
    "deepin": "deepin",
    "elementary": "elementary",
    "manjaro": "manjaro",
    "fedora": "fedora",
    "debian": "debian",
    "ubuntu": "ubuntu",
    "alpine": "alpine",
    "antix": "antix",
    "kali": "kali",
    "tails": "tails",
    "parrot": "parrot",
    "qubes": "qubes",
    
    # IDs que já estão corretos (não precisam de mapeamento)
    # mas incluímos para referência
}

# IDs do DistroWatch que não existem (distros muito novas/obscuras)
DISTROWATCH_UNKNOWN = [
    "holoiso",      # Está na "Waiting List" do DistroWatch
    "tigeros",      # Está na "Waiting List" do DistroWatch
    "locos",        # Não existe no DistroWatch
    "anduinos",     # Não existe no DistroWatch
]


def get_distrowatch_id(distrowiki_id: str) -> str:
    """
    Converte ID do DistroWiki para ID do DistroWatch.
    
    Args:
        distrowiki_id: ID usado no DistroWiki
        
    Returns:
        ID usado no DistroWatch
    """
    # Normalizar para lowercase
    normalized = distrowiki_id.lower().strip()
    
    # Verificar mapeamento explícito
    if normalized in DISTROWIKI_TO_DISTROWATCH:
        return DISTROWIKI_TO_DISTROWATCH[normalized]
    
    # Tentar remover sufixos comuns
    if normalized.endswith("linux"):
        without_linux = normalized[:-5]
        if without_linux in DISTROWIKI_TO_DISTROWATCH:
            return DISTROWIKI_TO_DISTROWATCH[without_linux]
        return without_linux
    
    if normalized.endswith("os"):
        without_os = normalized[:-2]
        if without_os in DISTROWIKI_TO_DISTROWATCH:
            return DISTROWIKI_TO_DISTROWATCH[without_os]
    
    # Retornar como está
    return normalized


def get_distrowiki_id(distrowatch_id: str) -> str:
    """
    Converte ID do DistroWatch para ID do DistroWiki.
    
    Args:
        distrowatch_id: ID usado no DistroWatch
        
    Returns:
        ID usado no DistroWiki
    """
    # Inverter o mapeamento
    reverse_map = {v: k for k, v in DISTROWIKI_TO_DISTROWATCH.items()}
    
    normalized = distrowatch_id.lower().strip()
    
    if normalized in reverse_map:
        return reverse_map[normalized]
    
    return normalized


# Mapeamento completo de todos os IDs conhecidos
# Para referência e atualização da planilha
ALL_DISTRO_ID_MAPPINGS = [
    # (distrowiki_current, distrowatch_correct, nome_display)
    ("archlinux", "arch", "Arch Linux"),
    ("artixlinux", "artix", "Artix Linux"),
    ("arcolinux", "arco", "ArcoLinux"),
    ("endeavouros", "endeavour", "EndeavourOS"),
    ("linuxmint", "mint", "Linux Mint"),
    ("mxlinux", "mx", "MX Linux"),
    ("popos", "pop", "Pop!_OS"),
    ("kdeneon", "neon", "KDE Neon"),
    ("almalinux", "alma", "AlmaLinux"),
    ("rockylinux", "rocky", "Rocky Linux"),
    ("opensuse", "opensuse", "openSUSE"),
    ("dragonflybsd", "dragonfly", "DragonFly BSD"),
    ("cachyos", "cachy", "CachyOS"),
]
