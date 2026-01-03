"""Script para adicionar popularity_rank ao static_distro_data.py"""
import re

# Ler arquivo
with open('api/services/static_distro_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Rankings do DistroWatch (aproximado Jan 2026)
rankings = {
    'linuxmint': 1, 'debian': 2, 'ubuntu': 3, 'mxlinux': 4, 'endeavouros': 5,
    'fedora': 6, 'opensuse': 7, 'manjaro': 8, 'popos': 9, 'archlinux': 10,
    'zorin': 11, 'elementary': 12, 'kali': 13, 'garuda': 14, 'antix': 15,
    'lmde': 16, 'kubuntu': 17, 'opensusetumbleweed': 18, 'artixlinux': 19, 'cachyos': 20,
    'nixos': 21, 'gentoo': 22, 'void': 23, 'solus': 24, 'kdeneon': 25,
    'arcolinux': 26, 'sparkylinux': 27, 'nobara': 28, 'peppermint': 29, 'alpine': 30,
    'devuan': 31, 'deepin': 32, 'slackware': 33, 'bodhi': 34, 'bunsenlabs': 35,
    'mageia': 36, 'pclinuxos': 37, 'xubuntu': 38, 'lubuntu': 39, 'tails': 40,
    'ubuntumate': 41, 'alma': 42, 'rockylinux': 43, 'parrotos': 44, 'qubes': 45,
    'puppylinux': 46, 'linuxlite': 47, 'biglinux': 48, 'freebsd': 49, 'ghostbsd': 50,
    'siduction': 51, 'q4os': 52, 'endless': 53, 'archcraft': 54, 'pureos': 55,
    'centos': 56, 'sparky': 57, 'trisquel': 58, 'calculate': 59, 'spirallinux': 60,
    'ubuntustudio': 61, 'ubuntubudgie': 62, 'nitrux': 63, 'porteus': 64, 'slax': 65,
    'dragonflybsd': 66, 'openbsd': 67, 'netbsd': 68, 'haiku': 69, 'raspberrypios': 70,
    'ubuntukylin': 71, 'ubuntucinnamon': 72, 'ubuntuunity': 73, 'edubuntu': 74, 'blendos': 75,
    'rebornos': 76, 'chimeralinux': 77, 'steamos': 78, 'holoiso': 79, 'bazzite': 80,
    'asahi': 81, 'vanilla': 82, 'pikaos': 83, 'rhel': 84, 'oracle': 85,
    'bluestar': 86, 'tinycore': 87, 'slitaz': 88, 'kolibrios': 89, 'openindiana': 90,
    'midnightbsd': 91, 'canaima': 92, 'primtux': 93, 'tuxedoos': 94, 'regataos': 95,
    'chromeos': 96, 'omarchy': 97, 'anduinos': 98, 'aerynos': 99, 'bros': 100,
    'tigeros': 101, 'locos': 102,
}

count = 0
for distro, rank in rankings.items():
    # Pattern: "distro": {\n        "init_system":
    pattern = rf'("{distro}": {{\r?\n        "init_system":)'
    replacement = f'"{distro}": {{\n        "popularity_rank": {rank},\n        "init_system":'
    new_content, n = re.subn(pattern, replacement, content)
    if n > 0:
        content = new_content
        count += 1
        print(f"  + {distro}: rank {rank}")

# Salvar arquivo
with open('api/services/static_distro_data.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal: {count} distros atualizadas com popularity_rank!")
