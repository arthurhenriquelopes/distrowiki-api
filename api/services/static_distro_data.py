"""
Dados estáticos de distros conhecidas.

Como o DistroWatch tem rate limiting agressivo (403 Forbidden),
usamos dados estáticos para distros populares como fallback.

Estes dados são atualizados manualmente ou via scraping quando possível.
"""

# Mapeamento de dados estáticos para distros populares
# Formato: distro_id -> {init_system, file_systems, release_type, architecture}
STATIC_DISTRO_DATA = {
    # === Debian-based ===
    "ubuntu": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "debian": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "linuxmint": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "mxlinux": {
        "init_system": "sysvinit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "antix": {
        "init_system": "runit, s6, sysvinit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "popos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "elementary": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "zorin": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "kali": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Arch-based ===
    "archlinux": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "F2FS", "JFS", "ReiserFS", "XFS", "ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "manjaro": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    "endeavouros": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "garuda": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "artixlinux": {
        "init_system": "OpenRC, runit, s6, dinit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "cachyos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "arcolinux": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Fedora-based ===
    "fedora": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "nobara": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "alma": {
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    "rockylinux": {
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    "centos": {
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === openSUSE ===
    "opensuse": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "opensusetumbleweed": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Independent ===
    "nixos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Rolling/Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "void": {
        "init_system": "runit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "gentoo": {
        "init_system": "OpenRC, systemd",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS", "ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "solus": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "alpine": {
        "init_system": "OpenRC",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    
    # === Other popular distros ===
    "deepin": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "peppermint": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "sparky": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling/Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "bodhi": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "bunsenlabs": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
}


def get_static_data(distro_id: str) -> dict:
    """
    Retorna dados estáticos para uma distro.
    
    Args:
        distro_id: ID da distro
        
    Returns:
        Dict com dados ou dict vazio se não encontrado
    """
    return STATIC_DISTRO_DATA.get(distro_id.lower(), {})


def has_static_data(distro_id: str) -> bool:
    """Verifica se existe dados estáticos para a distro."""
    return distro_id.lower() in STATIC_DISTRO_DATA
