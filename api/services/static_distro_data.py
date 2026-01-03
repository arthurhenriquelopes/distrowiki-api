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
    
    # === Ubuntu Flavors ===
    "kubuntu": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "xubuntu": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "lubuntu": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntumate": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntubudgie": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntustudio": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntukylin": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntucinnamon": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntuunity": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "edubuntu": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "lmde": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    
    # === Arch-based (more) ===
    "archcraft": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "biglinux": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "blendos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "rebornos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "bluestar": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Debian-based (more) ===
    "devuan": {
        "init_system": "sysvinit, OpenRC, runit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686", "ARM64"],
    },
    "kdeneon": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "pureos": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "trisquel": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "linuxlite": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "endless": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "nitrux": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "spirallinux": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "siduction": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "sparkylinux": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling/Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "q4os": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686", "ARM64"],
    },
    
    # === Security/Privacy Distros ===
    "tails": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "parrotos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    "qubes": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    
    # === Slackware-based ===
    "slackware": {
        "init_system": "sysvinit",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "slax": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "porteus": {
        "init_system": "sysvinit",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    
    # === BSD and Non-Linux ===
    "freebsd": {
        "init_system": "rc",
        "file_systems": ["UFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "openbsd": {
        "init_system": "rc",
        "file_systems": ["FFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "netbsd": {
        "init_system": "rc",
        "file_systems": ["FFS", "LFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "ghostbsd": {
        "init_system": "OpenRC",
        "file_systems": ["UFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "dragonflybsd": {
        "init_system": "rc",
        "file_systems": ["HAMMER2", "UFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "midnightbsd": {
        "init_system": "rc",
        "file_systems": ["UFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "haiku": {
        "init_system": "launch_daemon",
        "file_systems": ["BFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "kolibrios": {
        "init_system": "Native",
        "file_systems": ["FAT32", "ext2"],
        "release_type": "Rolling",
        "architecture": ["x86"],
    },
    "openindiana": {
        "init_system": "SMF",
        "file_systems": ["ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Other independent ===
    "pclinuxos": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "mageia": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "puppylinux": {
        "init_system": "sysvinit",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "tinycore": {
        "init_system": "BusyBox init",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "slitaz": {
        "init_system": "BusyBox init",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "i686"],
    },
    "calculate": {
        "init_system": "OpenRC, systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "chimeralinux": {
        "init_system": "dinit",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Gaming/Steam ===
    "steamos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "holoiso": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "bazzite": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "chromeos": {
        "init_system": "upstart",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === ARM/Embedded ===
    "raspberrypios": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["ARM64", "ARM32"],
    },
    "asahi": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["ARM64"],
    },
    
    # === Enterprise ===
    "rhel": {
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    "oracle": {
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Regional/Niche ===
    "canaima": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "primtux": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "tuxedoos": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "pikaos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "vanilla": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "regataos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "omarchy": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Obscure/New ===
    "anduinos": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "aerynos": {
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "bros": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "tigeros": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "locos": {
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
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
