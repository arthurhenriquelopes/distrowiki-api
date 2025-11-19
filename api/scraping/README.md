# Módulo de Scraping - DistroWatch

Módulo modular para scraping de distribuições Linux do DistroWatch usando proxies rotativos.

## 📋 Características

- ✅ **Rotação de Proxies**: Sistema automático de rotação de proxies para evitar IP ban
- ✅ **Rate Limiting**: Delays inteligentes entre requisições
- ✅ **Retry Automático**: Fallback e retry em caso de falhas
- ✅ **Background Tasks**: Scraping executado em background via FastAPI
- ✅ **Monitoramento**: Endpoints para monitorar progresso e status
- ✅ **Modular**: Pode ser facilmente removido sem afetar o resto da API

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install beautifulsoup4 requests lxml
```

Ou usando o requirements.txt do módulo:

```bash
pip install -r api/scraping/requirements.txt
```

### 2. Adicionar Proxies

```bash
curl -X POST "http://localhost:8000/scraping/proxies" \
  -H "Content-Type: application/json" \
  -d '{
    "proxy_urls": [
      "http://proxy1.example.com:8080",
      "http://proxy2.example.com:8080"
    ]
  }'
```

### 3. Validar Proxies

```bash
curl -X POST "http://localhost:8000/scraping/proxies/validate"
```

### 4. Iniciar Scraping

```bash
curl -X POST "http://localhost:8000/scraping/start" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 10,
    "use_proxies": true
  }'
```

### 5. Monitorar Progresso

```bash
curl "http://localhost:8000/scraping/status"
```

### 6. Obter Resultados

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
| GET | `/scraping/proxies` | Estatísticas dos proxies |
| POST | `/scraping/proxies` | Adicionar proxies |
| POST | `/scraping/proxies/validate` | Validar proxies |

## 🏗️ Arquitetura

```
api/scraping/
├── __init__.py           # Exporta scraping_router
├── proxy_manager.py      # Gerenciamento de proxies
├── distrowatch_scraper.py # Lógica de scraping
├── routes.py             # Endpoints FastAPI
├── requirements.txt      # Dependências
└── README.md            # Esta documentação
```

## 🔧 Configuração

### ProxyManager

```python
from api.scraping.proxy_manager import ProxyManager

# Criar gerenciador com proxies
proxy_manager = ProxyManager(
    proxies=[
        "http://proxy1.com:8080",
        "http://proxy2.com:8080"
    ],
    max_failures=3  # Máximo de falhas antes de desativar
)

# Obter proxy aleatório
proxy = proxy_manager.get_random_proxy()

# Reportar falha
proxy_manager.report_failure(proxy)

# Estatísticas
stats = proxy_manager.get_stats()
```

### DistroWatchScraper

```python
from api.scraping.distrowatch_scraper import DistroWatchScraper

# Criar scraper
scraper = DistroWatchScraper(proxy_manager)

# Scrape lista de distros
distros = scraper.scrape_distro_list()

# Scrape detalhes de uma distro
details = scraper.scrape_distro_details("https://distrowatch.com/table.php?distribution=ubuntu")

# Scrape completo (lista + detalhes)
all_distros = scraper.scrape_all(limit=10)
```

## ⚠️ Considerações Importantes

### Proxies
- **Use proxies éticos e legais**
- Proxies gratuitos podem ser lentos ou instáveis
- Considere usar serviços de proxy pagos para melhor performance
- Respeite os termos de serviço do DistroWatch

### Rate Limiting
- O scraper já inclui delays aleatórios entre requisições
- Não abuse do DistroWatch - eles fornecem dados gratuitamente
- Considere fazer scraping em horários de baixo tráfego

### Estrutura HTML
- A estrutura do DistroWatch pode mudar sem aviso
- Os seletores CSS/XPath podem precisar de ajustes
- Teste regularmente para garantir funcionamento

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

## 📝 Exemplo de Uso Completo

```python
import asyncio
from api.scraping.proxy_manager import ProxyManager
from api.scraping.distrowatch_scraper import DistroWatchScraper

async def main():
    # 1. Configurar proxies
    proxy_manager = ProxyManager([
        "http://proxy1.com:8080",
        "http://proxy2.com:8080"
    ])
    
    # 2. Criar scraper
    scraper = DistroWatchScraper(proxy_manager)
    
    # 3. Scrape completo (limitado a 5 distros)
    distros = scraper.scrape_all(limit=5)
    
    # 4. Processar resultados
    for distro in distros:
        print(f"Nome: {distro.get('name')}")
        print(f"URL: {distro.get('url')}")
        print(f"Baseado em: {distro.get('based_on')}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🐛 Troubleshooting

### "Nenhum proxy ativo disponível"
- Valide seus proxies: `POST /scraping/proxies/validate`
- Adicione mais proxies: `POST /scraping/proxies`
- Verifique se os proxies estão online

### "IP ban do DistroWatch"
- Adicione mais proxies ao pool
- Aumente os delays entre requisições
- Aguarde algumas horas antes de tentar novamente

### "Erro ao parsear HTML"
- A estrutura do DistroWatch pode ter mudado
- Verifique e ajuste os seletores em `distrowatch_scraper.py`
- Consulte o HTML atual do DistroWatch para referência

## 📚 Recursos

- [DistroWatch](https://distrowatch.com)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Docs](https://requests.readthedocs.io/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

## 📄 Licença

Este módulo segue a mesma licença do projeto principal (MIT).
