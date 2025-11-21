import os
from groq import Groq
from typing import List, Dict, Any

# Suporte a múltiplas chaves Groq
GROQ_API_KEYS = os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", "")).split(",")
GROQ_API_KEYS = [key.strip() for key in GROQ_API_KEYS if key.strip()]

async def enrich_distros_with_groq(distro_names: List[str]) -> List[Dict[str, Any]]:
    """
    Enriquecimento dos dados das distros via Groq API, com ciclo de chaves.
    """
    results = []
    for name in distro_names:
        prompt = (
            f"Para a distribuição Linux '{name}', informe os seguintes dados em formato JSON. Responda só o JSON puro, sem explicações:\n"
            "{\n"
            "  'ram_idle': <RAM em MB>,\n"
            "  'cpu_score': <score de 1 a 10>,\n"
            "  'io_score': <score de 1 a 10>,\n"
            "  'requisitos': <Leve|Médio|Alto>\n"
            "}"
        )
        success = False
        for api_key in GROQ_API_KEYS:
            groq_client = Groq(api_key=api_key)
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.2
                )
                import json, re
                content = response.choices[0].message.content
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    enriched = json.loads(match.group().replace("'", '"'))
                    enriched['name'] = name
                    results.append(enriched)
                else:
                    results.append({"name": name, "error": "Formato inesperado"})
                success = True
                break
            except Exception as e:
                # Se erro de quota, tenta próxima chave
                if hasattr(e, 'args') and any('quota' in str(arg).lower() or 'limit' in str(arg).lower() for arg in e.args):
                    continue
                results.append({"name": name, "error": str(e)})
                success = True
                break
        if not success:
            results.append({"name": name, "error": "Todas as chaves Groq falharam ou expiraram."})
    return results
