import os
import logging
from groq import Groq
from typing import List, Dict, Any, Optional
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)

# Enum com campos da planilha que podem ser enriquecidos via IA
class SheetColumn(str, Enum):
    DESCRIPTION = "Description"
    IDLE_RAM_USAGE = "Idle RAM Usage"
    CPU_SCORE = "CPU Score"
    IO_SCORE = "I/O Score"
    REQUIREMENTS = "Requirements"
    OFFICE_SUITE = "Office Suite"
    CATEGORY = "Category"
    DESKTOP = "Desktop"
    IMAGE_SIZE = "Image Size"
    OS_TYPE = "OS Type"
    BASE = "Base"
    ORIGIN = "Origin"
    STATUS = "Status"
    PACKAGE_MANAGEMENT = "Package Management"
    RELEASE_DATE = "Release Date"
    LATEST_RELEASE = "Latest Release"
    WEBSITE = "Website"
    PRICE = "Price (R$)" 

# Descrições para o prompt da IA
FIELD_PROMPTS = {
    SheetColumn.DESCRIPTION: "uma descrição concisa em português da distribuição (máx. 200 caracteres)",
    SheetColumn.IDLE_RAM_USAGE: (
        "Analise a distribuição Linux e, levando em conta o ambiente gráfico, forneça um valor "
        "realista de uso de RAM em idle em MB (APENAS o número, inteiro). CONTEXTO E FAIXAS REALISTAS:\n"
        "- Lightweight (LXDE, LXQt, Xfce, i3, Openbox): 300-600 MB\n"
        "- Medium (MATE, Cinnamon, Budgie): 600-900 MB\n"
        "- Heavy (GNOME, KDE Plasma, Pantheon): 800-1500 MB\n"
        "- Gaming/specialized (Steam Deck, HoloISO, Garuda): 1200-2500 MB\n"
        "- Enterprise/server (RHEL, Ubuntu Server - minimal install): 200-400 MB\n\n"
        "EXAMPLES:\n"
        "- Ubuntu (GNOME): ~1200 MB\n"
        "- Fedora (GNOME): ~1300 MB\n"
        "- KDE Neon: ~1100 MB\n"
        "- Pop!_OS (GNOME): ~1400 MB\n"
        "- Linux Mint (Cinnamon): ~800 MB\n"
        "- Manjaro (KDE): ~900 MB\n"
        "- Arch (i3): ~350 MB\n"
        "- Lubuntu (LXQt): ~450 MB\n\n"
        "Com base na categoria da distro e no ambiente gráfico, retorne SOMENTE um número inteiro em MB (ex: 1200). "
        "Não retorne texto, unidades ou valores abaixo de 300 MB para distribuições desktop."
    ),
    SheetColumn.CPU_SCORE: "score de performance de CPU de 1 a 10 (1=lento, 10=muito rápido)",
    SheetColumn.IO_SCORE: "score de performance de I/O de 1 a 10 (1=lento, 10=muito rápido)",
    SheetColumn.REQUIREMENTS: "requisitos de hardware: 'Leve', 'Médio' ou 'Alto'",
    SheetColumn.OFFICE_SUITE: "suite de escritório padrão incluída (ex: LibreOffice, OnlyOffice, nenhuma)",
    SheetColumn.CATEGORY: "categoria principal: Desktop, Server, IoT, Education, Gaming, etc.",
    SheetColumn.DESKTOP: "ambiente desktop padrão (GNOME, KDE, XFCE, etc.)",
    SheetColumn.IMAGE_SIZE: "tamanho típico da ISO em GB (ex: 2.5)",
    SheetColumn.OS_TYPE: "tipo do SO: Linux, BSD, etc.",
    SheetColumn.BASE: "distribuição base (Debian, Arch, Independent, etc.)",
    SheetColumn.ORIGIN: "país de origem",
    SheetColumn.STATUS: "status: Active, Discontinued, Beta",
    SheetColumn.PACKAGE_MANAGEMENT: "gerenciador de pacotes principal (apt, pacman, dnf, etc.)",
    SheetColumn.RELEASE_DATE: "data do lançamento original da distribuição no formato DD/MM/AAAA",
    SheetColumn.LATEST_RELEASE: "data da última versão lançada no formato DD/MM/AAAA",
    SheetColumn.WEBSITE: "URL completa da homepage oficial da distribuição linux.",
    SheetColumn.PRICE: "modelo de preço: 'Gratuito', 'Pago', 'Freemium' ou 'Doações' (a maioria é Gratuito)",
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").split(",")
GROQ_API_KEY = [key.strip() for key in GROQ_API_KEY if key.strip()]

def validate_ram_idle(distro_name: str, desktop_env: str, ram_value: int) -> int:
    """Valida e corrige valores de RAM idle irrealistas.

    Args:
        distro_name: nome da distribuição
        desktop_env: ambiente gráfico (string)
        ram_value: valor retornado pela IA (MB)

    Returns:
        Valor inteiro de RAM em MB ajustado dentro do range esperado.
    """
    # Mapeamento de Desktop Environment para range esperado
    de_ranges = {
        'gnome': (900, 1600),
        'kde plasma': (800, 1400),
        'kde': (800, 1400),
        'xfce': (400, 700),
        'lxqt': (350, 600),
        'lxde': (300, 550),
        'mate': (600, 900),
        'cinnamon': (700, 1000),
        'budgie': (700, 1000),
        'i3': (300, 500),
        'sway': (300, 500),
        'openbox': (300, 500),
        'pantheon': (800, 1200),
        'deepin': (900, 1300),
    }

    # Distros especiais que sempre têm consumo alto
    gaming_distros = ['holoiso', 'garuda', 'nobara', 'popos', 'cachyos', 'deepin', 'steamos', 'endeavouros', 'regataos']

    de_lower = desktop_env.lower() if desktop_env else ''
    min_ram, max_ram = de_ranges.get(de_lower, (600, 1200))  # Default médio

    # Gaming distros têm piso mais alto
    if any(gaming in distro_name.lower() for gaming in gaming_distros):
        min_ram = max(min_ram, 1000)
        max_ram = max(max_ram, 2000)

    # Se valor está fora do range, ajustar
    try:
        ram_int = int(ram_value)
    except Exception:
        logger.warning(f"{distro_name}: valor de RAM inválido recebido: {ram_value}. Usando mínimo {min_ram}")
        return min_ram

    if ram_int < min_ram:
        logger.warning(f"{distro_name}: RAM {ram_int} MB muito baixo, ajustando para {min_ram} MB")
        return min_ram

    if ram_int > max_ram:
        logger.warning(f"{distro_name}: RAM {ram_int} MB muito alto, ajustando para {max_ram} MB")
        return max_ram

    return ram_int


async def enrich_distros_with_groq(
    distro_names: List[str],
    fields: List[SheetColumn] = None,
    desktop_envs: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Enriquecimento dinâmico dos dados das distros via Groq API.

    Args:
        distro_names: Lista de nomes das distribuições
        fields: Lista de colunas da planilha para enriquecer. Se None, usa campos padrão.
    """
    if fields is None or len(fields) == 0:
        fields = [
            SheetColumn.DESKTOP,
            SheetColumn.IDLE_RAM_USAGE,
            SheetColumn.CPU_SCORE,
            SheetColumn.IO_SCORE,
            SheetColumn.REQUIREMENTS,
        ]

    results = []
    for name in distro_names:
        field_lines = [f'  "{field.value}": {FIELD_PROMPTS[field]}' for field in fields]

        prompt = (
            f"Para a distribuição Linux '{name}', forneça os seguintes dados em formato JSON. "
            f"Responda APENAS o JSON puro, sem explicações ou markdown:\n"
            "{\n" + ",\n".join(field_lines) + "\n}\n\n"
            "IMPORTANTE: Use as chaves exatas entre aspas duplas como mostrado acima."
        )

        success = False
        for api_key in GROQ_API_KEY:
            groq_client = Groq(api_key=api_key)
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.2,
                )

                content = response.choices[0].message.content
                content = re.sub(r"``````", "", content).strip()

                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    enriched = json.loads(match.group())
                    enriched["Name"] = name

                    # 1. Pegar Desktop Environment da própria resposta da IA
                    desktop_env = (
                        enriched.get("Desktop") or enriched.get("desktop") or ""
                    )

                    # 2. Validar RAM se presente (usar nome exato da chave)
                    if "Idle RAM Usage" in enriched:
                        raw_value = enriched["Idle RAM Usage"]

                        # Extrair número do valor (pode vir como "1200 MB", "1200", etc)
                        try:
                            ram_digits = re.search(r"\d+", str(raw_value))
                            if ram_digits:
                                ram_val = int(ram_digits.group())
                            else:
                                ram_val = int(raw_value)
                        except:
                            logger.warning(
                                f"{name}: Valor de RAM inválido: {raw_value}"
                            )
                            ram_val = 800  # Default médio

                        # Aplicar validação
                        validated_ram = validate_ram_idle(name, desktop_env, ram_val)
                        enriched["Idle RAM Usage"] = validated_ram
                        logger.info(
                            f"{name} ({desktop_env}): RAM validado = {validated_ram} MB"
                        )

                    # 3. Validar CPU Score se presente
                    if "CPU Score" in enriched:
                        try:
                            cpu = int(enriched["CPU Score"])
                            enriched["CPU Score"] = max(1, min(10, cpu))
                        except:
                            enriched["CPU Score"] = 7

                    # 4. Validar I/O Score se presente
                    if "I/O Score" in enriched:
                        try:
                            io = int(enriched["I/O Score"])
                            enriched["I/O Score"] = max(1, min(10, io))
                        except:
                            enriched["I/O Score"] = 7

                    results.append(enriched)
                else:
                    results.append({"Name": name, "error": "Formato inesperado"})
                success = True
                break

            except Exception as e:
                error_message = str(e).lower()
                if (
                    "quota" in error_message
                    or "limit" in error_message
                    or "rate" in error_message
                ):
                    continue
                logger.error(f"Erro ao enriquecer {name}: {e}")
                results.append({"Name": name, "error": str(e)})
                success = True
                break

        if not success:
            results.append(
                {"Name": name, "error": "Todas as chaves Groq falharam ou expiraram."}
            )

    return results
