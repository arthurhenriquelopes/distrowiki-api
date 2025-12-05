# api/services/release_scraper.py

import httpx
from bs4 import BeautifulSoup
import re
from typing import Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

# Mapeamento: ID do seu sistema → ID do DistroWatch
DISTROWATCH_ID_MAP = {
    "popos": "pop",
    "cachyos": "cachyos",
}


async def get_latest_release_date(distro_id: str) -> str:
    """
    Scrape da data de última release do DistroWatch.

    Args:
        distro_id: ID da distro no seu sistema (ex: 'cachyos', 'ubuntu')

    Returns:
        Data no formato DD/MM/YYYY ou "Unknown" se não encontrar
    """
    dw_id = DISTROWATCH_ID_MAP.get(distro_id.lower(), distro_id.lower())
    url = f"https://distrowatch.com/table.php?distribution={dw_id}"

    # Headers para simular navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        async with httpx.AsyncClient(
            timeout=15.0, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(url)

            if response.status_code == 403:
                logger.error(f"🚫 {distro_id}: DistroWatch bloqueou (403)")
                return "Unknown"

            if response.status_code == 404:
                logger.warning(f"❌ DistroWatch page não encontrada: {url}")
                return "Unknown"

            # Buscar padrão: &nbsp;&bull; 2025-11-29:
            pattern = r"&nbsp;&bull;\s*(\d{4})-(\d{2})-(\d{2})"
            matches = re.findall(pattern, response.text)

            if matches:
                year, month, day = matches[0]
                date_formatted = f"{day}/{month}/{year}"
                logger.info(f"✅ {distro_id}: {date_formatted}")
                return date_formatted

            logger.warning(f"⚠️ {distro_id}: Não encontrou data em {url}")
            return "Unknown"

    except httpx.TimeoutException:
        logger.error(f"⏱️ {distro_id}: Timeout ao acessar {url}")
        return "Unknown"
    except Exception as e:
        logger.error(f"❌ {distro_id}: Erro - {e}")
        return "Unknown"


async def get_bulk_release_dates(distro_ids: list) -> dict:
    """
    Busca datas de múltiplas distros em paralelo.

    Returns:
        Dict com {distro_id: date_string}
    """
    tasks = [get_latest_release_date(distro_id) for distro_id in distro_ids]
    results = await asyncio.gather(*tasks)
    return dict(zip(distro_ids, results))
