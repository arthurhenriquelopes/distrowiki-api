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
        "popularity_rank": 3,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "debian": {
        "popularity_rank": 2,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "linuxmint": {
        "popularity_rank": 1,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "mxlinux": {
        "popularity_rank": 4,
        "init_system": "sysvinit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "antix": {
        "popularity_rank": 15,
        "init_system": "runit, s6, sysvinit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "popos": {
        "popularity_rank": 9,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "elementary": {
        "popularity_rank": 12,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "zorin": {
        "popularity_rank": 11,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "kali": {
        "popularity_rank": 13,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Arch-based ===
    "archlinux": {
        "popularity_rank": 10,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "F2FS", "JFS", "ReiserFS", "XFS", "ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "manjaro": {
        "popularity_rank": 8,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    "endeavouros": {
        "popularity_rank": 5,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "garuda": {
        "popularity_rank": 14,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "artixlinux": {
        "popularity_rank": 19,
        "init_system": "OpenRC, runit, s6, dinit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "cachyos": {
        "popularity_rank": 20,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "arcolinux": {
        "popularity_rank": 26,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Fedora-based ===
    "fedora": {
        "popularity_rank": 6,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "nobara": {
        "popularity_rank": 28,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "alma": {
        "popularity_rank": 42,
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    "rockylinux": {
        "popularity_rank": 43,
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    "centos": {
        "popularity_rank": 56,
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === openSUSE ===
    "opensuse": {
        "popularity_rank": 7,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "opensusetumbleweed": {
        "popularity_rank": 18,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Independent ===
    "nixos": {
        "popularity_rank": 21,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Rolling/Point Release",
        "architecture": ["x86_64", "ARM64"],
    },
    "void": {
        "popularity_rank": 23,
        "init_system": "runit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "gentoo": {
        "popularity_rank": 22,
        "init_system": "OpenRC, systemd",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS", "ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "solus": {
        "popularity_rank": 24,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "alpine": {
        "popularity_rank": 30,
        "init_system": "OpenRC",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    
    # === Other popular distros ===
    "deepin": {
        "popularity_rank": 32,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "peppermint": {
        "popularity_rank": 29,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "sparky": {
        "popularity_rank": 57,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling/Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "bodhi": {
        "popularity_rank": 34,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "bunsenlabs": {
        "popularity_rank": 35,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    
    # === Ubuntu Flavors ===
    "kubuntu": {
        "popularity_rank": 17,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "xubuntu": {
        "popularity_rank": 38,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "lubuntu": {
        "popularity_rank": 39,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntumate": {
        "popularity_rank": 41,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntubudgie": {
        "popularity_rank": 62,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntustudio": {
        "popularity_rank": 61,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntukylin": {
        "popularity_rank": 71,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntucinnamon": {
        "popularity_rank": 72,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "ubuntuunity": {
        "popularity_rank": 73,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "edubuntu": {
        "popularity_rank": 74,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "lmde": {
        "popularity_rank": 16,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    
    # === Arch-based (more) ===
    "archcraft": {
        "popularity_rank": 54,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "biglinux": {
        "popularity_rank": 48,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "blendos": {
        "popularity_rank": 75,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "rebornos": {
        "popularity_rank": 76,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "bluestar": {
        "popularity_rank": 86,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Debian-based (more) ===
    "devuan": {
        "popularity_rank": 31,
        "init_system": "sysvinit, OpenRC, runit",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686", "ARM64"],
    },
    "kdeneon": {
        "popularity_rank": 25,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "pureos": {
        "popularity_rank": 55,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "trisquel": {
        "popularity_rank": 58,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "linuxlite": {
        "popularity_rank": 47,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "endless": {
        "popularity_rank": 53,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "nitrux": {
        "popularity_rank": 63,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "spirallinux": {
        "popularity_rank": 60,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "siduction": {
        "popularity_rank": 51,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "sparkylinux": {
        "popularity_rank": 27,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling/Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "q4os": {
        "popularity_rank": 52,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686", "ARM64"],
    },
    
    # === Security/Privacy Distros ===
    "tails": {
        "popularity_rank": 40,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "parrotos": {
        "popularity_rank": 44,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    "qubes": {
        "popularity_rank": 45,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    
    # === Slackware-based ===
    "slackware": {
        "popularity_rank": 33,
        "init_system": "sysvinit",
        "file_systems": ["Btrfs", "ext4", "JFS", "ReiserFS", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "slax": {
        "popularity_rank": 65,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "porteus": {
        "popularity_rank": 64,
        "init_system": "sysvinit",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    
    # === BSD and Non-Linux ===
    "freebsd": {
        "popularity_rank": 49,
        "init_system": "rc",
        "file_systems": ["UFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "openbsd": {
        "popularity_rank": 67,
        "init_system": "rc",
        "file_systems": ["FFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "netbsd": {
        "popularity_rank": 68,
        "init_system": "rc",
        "file_systems": ["FFS", "LFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "ARM64", "i686"],
    },
    "ghostbsd": {
        "popularity_rank": 50,
        "init_system": "OpenRC",
        "file_systems": ["UFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "dragonflybsd": {
        "popularity_rank": 66,
        "init_system": "rc",
        "file_systems": ["HAMMER2", "UFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "midnightbsd": {
        "popularity_rank": 91,
        "init_system": "rc",
        "file_systems": ["UFS", "ZFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "haiku": {
        "popularity_rank": 69,
        "init_system": "launch_daemon",
        "file_systems": ["BFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "kolibrios": {
        "popularity_rank": 89,
        "init_system": "Native",
        "file_systems": ["FAT32", "ext2"],
        "release_type": "Rolling",
        "architecture": ["x86"],
    },
    "openindiana": {
        "popularity_rank": 90,
        "init_system": "SMF",
        "file_systems": ["ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Other independent ===
    "pclinuxos": {
        "popularity_rank": 37,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "mageia": {
        "popularity_rank": 36,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "puppylinux": {
        "popularity_rank": 46,
        "init_system": "sysvinit",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "tinycore": {
        "popularity_rank": 87,
        "init_system": "BusyBox init",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "slitaz": {
        "popularity_rank": 88,
        "init_system": "BusyBox init",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "i686"],
    },
    "calculate": {
        "popularity_rank": 59,
        "init_system": "OpenRC, systemd",
        "file_systems": ["Btrfs", "ext4", "XFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "chimeralinux": {
        "popularity_rank": 77,
        "init_system": "dinit",
        "file_systems": ["Btrfs", "ext4", "XFS", "ZFS"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Gaming/Steam ===
    "steamos": {
        "popularity_rank": 78,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "holoiso": {
        "popularity_rank": 79,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "bazzite": {
        "popularity_rank": 80,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "chromeos": {
        "popularity_rank": 96,
        "init_system": "upstart",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === ARM/Embedded ===
    "raspberrypios": {
        "popularity_rank": 70,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["ARM64", "ARM32"],
    },
    "asahi": {
        "popularity_rank": 81,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["ARM64"],
    },
    
    # === Enterprise ===
    "rhel": {
        "popularity_rank": 84,
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    "oracle": {
        "popularity_rank": 85,
        "init_system": "systemd",
        "file_systems": ["ext4", "XFS"],
        "release_type": "LTS",
        "architecture": ["x86_64", "ARM64"],
    },
    
    # === Regional/Niche ===
    "canaima": {
        "popularity_rank": 92,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "primtux": {
        "popularity_rank": 93,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64", "i686"],
    },
    "tuxedoos": {
        "popularity_rank": 94,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "pikaos": {
        "popularity_rank": 83,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "vanilla": {
        "popularity_rank": 82,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "regataos": {
        "popularity_rank": 95,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "omarchy": {
        "popularity_rank": 97,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    
    # === Obscure/New ===
    "anduinos": {
        "popularity_rank": 98,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "aerynos": {
        "popularity_rank": 99,
        "init_system": "systemd",
        "file_systems": ["Btrfs", "ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "bros": {
        "popularity_rank": 100,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Rolling",
        "architecture": ["x86_64"],
    },
    "tigeros": {
        "popularity_rank": 101,
        "init_system": "systemd",
        "file_systems": ["ext4"],
        "release_type": "Point Release",
        "architecture": ["x86_64"],
    },
    "locos": {
        "popularity_rank": 102,
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
