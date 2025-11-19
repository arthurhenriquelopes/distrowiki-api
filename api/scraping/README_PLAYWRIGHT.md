# Módulo de Scraping - DistroWatch (Playwright)

Módulo modular para scraping de distribuições Linux do DistroWatch usando **Playwright** com modo stealth.

## 🎭 Por que Playwright?

- ✅ **Sem IP ban**: Simula navegador real
- ✅ **Modo Stealth**: Anti-detecção de bots
- ✅ **Comportamento Humano**: Delays, scroll, movimento de mouse
- ✅ **JavaScript Renderizado**: Acessa conteúdo dinâmico
- ✅ **Sem Proxies**: Não precisa de proxies rotativos

## 📋 Características

- ✅ **Playwright Stealth**: Scripts anti-detecção integrados
- ✅ **Comportamento Humanizado**: Simula usuário real
- ✅ **Headless/Headed**: Rode com ou sem interface
- ✅ **Background Tasks**: Scraping executado em background via FastAPI
- ✅ **Monitoramento**: Endpoints para monitorar progresso e status
- ✅ **Modular**: Pode ser facilmente removido sem afetar o resto da API

## 🚀 Instalação

### 1. Instalar Playwright

```bash
pip install playwright beautifulsoup4 lxml
```

### 2. Instalar navegadores do Playwright

```bash
playwright install chromium
```

## 🎯 Como Usar

### 1. Iniciar Scraping (Headless - sem interface)

```bash
curl -X POST "http://localhost:8000/scraping/start" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 10,
    "headless": true
  }'
```

### 2. Iniciar Scraping (Headed - com interface para debug)

```bash
curl -X POST "http://localhost:8000/scraping/start" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 5,
    "headless": false
  }'
```

### 3. Monitorar Progresso

```bash
curl "http://localhost:8000/scraping/status"
```

### 4. Obter Resultados

```bash
curl "http://localhost:8000/scraping/results"
```

## 📡 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/scraping/` | Informações do módulo |
| GET | `/scraping/status` | Status do scraping |
| GET | `/scraping/results` | Resultados do scraping |
| POST | `/scraping/start` | Iniciar scraping |
| POST | `/scraping/stop` | Parar scraping |

## 🏗️ Arquitetura

```
api/scraping/
├── __init__.py                      # Exporta scraping_router
├── distrowatch_playwright.py        # Scraper com Playwright
├── playwright_stealth_scraper.py    # Base stealth (modelo)
├── routes.py                        # Endpoints FastAPI
├── requirements.txt                 # Dependências
└── README.md                        # Esta documentação
```

## 🔧 Configuração

### Parâmetros do Scraping

```json
{
  "limit": 10,        // Número de distros (null = todas)
  "headless": true    // false = abre navegador visível
}
```

### Exemplo Direto em Python

```python
from api.scraping.distrowatch_playwright import DistroWatchPlaywrightScraper

# Usando context manager
with DistroWatchPlaywrightScraper(headless=True) as scraper:
    # Scrape da lista (top 10)
    distros = scraper.scrape_distro_list()
    
    # Scrape de detalhes
    details = scraper.scrape_distro_details(distros[0]['url'])
    
    # Scrape completo
    all_data = scraper.scrape_all(limit=5)
```

## ⚙️ Modo Stealth

O scraper inclui várias técnicas anti-detecção:

1. **Navigator.webdriver** - Removido
2. **User-Agent** - Realista (Linux + Chrome)
3. **Headers** - Accept-Language, DNT, etc
4. **Comportamento Humano**:
   - Movimento aleatório do mouse
   - Scroll aleatório
   - Delays variáveis (1-6s)
5. **Chrome Runtime** - Emulado
6. **Viewport** - 1920x1080

## 🐛 Troubleshooting

### "Playwright not found"
```bash
pip install playwright
playwright install chromium
```

### "Chromium executable not found"
```bash
playwright install chromium
```

### Scraping muito lento
- Reduza o `limit` para testar
- Use `headless=true` para melhor performance
- Ajuste delays em `distrowatch_playwright.py`

### Tabela não encontrada
- A estrutura HTML do DistroWatch pode ter mudado
- Verifique e ajuste os seletores em `distrowatch_playwright.py`
- Use `headless=false` para ver visualmente

## 📊 Performance

- **Headless**: ~3-5s por distro
- **Headed**: ~4-7s por distro (mais lento)
- **Lista completa**: ~1-2s

## 🗑️ Remoção do Módulo

Para remover completamente o módulo de scraping:

1. **Remover import** em `api/main.py`:
```python
# Remover esta linha:
from .scraping import scraping_router
```

2. **Remover registro** em `api/main.py`:
```python
# Remover esta linha:
app.include_router(scraping_router)
```

3. **Deletar pasta**:
```bash
rm -rf api/scraping/
```

Pronto! O módulo está completamente removido sem afetar o resto da API.

## 📝 Exemplo Completo

```bash
# 1. Instalar dependências
pip install playwright beautifulsoup4 lxml
playwright install chromium

# 2. Iniciar API
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# 3. Iniciar scraping (5 distros, headless)
curl -X POST "http://localhost:8000/scraping/start" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5, "headless": true}'

# 4. Aguardar ~20-30s

# 5. Ver resultados
curl "http://localhost:8000/scraping/results" | python3 -m json.tool
```

## 📚 Recursos

- [Playwright Python](https://playwright.dev/python/)
- [DistroWatch](https://distrowatch.com)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

## 🎓 Dicas

1. **Use headless=false para debug** - Veja o navegador em ação
2. **Comece com limit pequeno** - Teste com 2-5 distros primeiro
3. **Respeite o DistroWatch** - Use delays adequados
4. **Ajuste seletores** - A estrutura HTML pode mudar

## 📄 Licença

Este módulo segue a mesma licença do projeto principal (MIT).
