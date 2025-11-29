import os
from groq import Groq
from typing import List, Dict, Any
from enum import Enum
import json
import re

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

# Descrições para o prompt da IA
FIELD_PROMPTS = {
    SheetColumn.DESCRIPTION: "uma descrição concisa em português da distribuição (máx. 200 caracteres)",
    SheetColumn.IDLE_RAM_USAGE: "uso de RAM em idle em MB (apenas o número)",
    SheetColumn.CPU_SCORE: "score de performance de CPU de 1 a 10",
    SheetColumn.IO_SCORE: "score de performance de I/O de 1 a 10",
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
    SheetColumn.LATEST_RELEASE: "data da última versão lançada no formato DD/MM/AAAA"
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").split(",")
GROQ_API_KEY = [key.strip() for key in GROQ_API_KEY if key.strip()]

async def enrich_distros_with_groq(
    distro_names: List[str], 
    fields: List[SheetColumn] = None
) -> List[Dict[str, Any]]:
    """
    Enriquecimento dinâmico dos dados das distros via Groq API.
    
    Args:
        distro_names: Lista de nomes das distribuições
        fields: Lista de colunas da planilha para enriquecer. Se None, usa campos padrão.
    """
    if fields is None or len(fields) == 0:
        fields = [
            SheetColumn.IDLE_RAM_USAGE,
            SheetColumn.CPU_SCORE,
            SheetColumn.IO_SCORE,
            SheetColumn.REQUIREMENTS
        ]
    
    results = []
    for name in distro_names:
        field_lines = [
            f'  "{field.value}": {FIELD_PROMPTS[field]}'
            for field in fields
        ]
        
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
                    max_tokens=300,
                    temperature=0.2
                )
                
                content = response.choices[0].message.content
                content = re.sub(r'```json|```', '', content).strip()
                
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    enriched = json.loads(match.group())
                    enriched['Name'] = name
                    results.append(enriched)
                else:
                    results.append({"Name": name, "error": "Formato inesperado"})
                success = True
                break
            except Exception as e:
                error_message = str(e).lower()
                if 'quota' in error_message or 'limit' in error_message or 'rate' in error_message:
                    continue
                results.append({"Name": name, "error": str(e)})
                success = True
                break
        
        if not success:
            results.append({"Name": name, "error": "Todas as chaves Groq falharam ou expiraram."})
    
    return results
