# 🤖 GitHub Actions Scraper

Sistema de scraping automatizado usando GitHub Actions que roda diariamente nos servidores do GitHub.

## 📋 Como Funciona

1. **GitHub Actions** roda automaticamente todos os dias às 3h UTC
2. Instala Python, Playwright e Chromium
3. Executa o scraper do DistroWatch
4. Salva resultados em `data/cache/distros_scraped.json`
5. Faz commit automático dos dados atualizados
6. API lê os dados do arquivo JSON

## 🚀 Vantagens

- ✅ **100% Gratuito** - usa infraestrutura do GitHub
- ✅ **Sem bloqueios de rede** - servidores do GitHub têm acesso ao DistroWatch
- ✅ **Automático** - roda diariamente sem intervenção
- ✅ **Histórico** - commits mostram histórico de atualizações
- ✅ **Pode executar manualmente** via interface do GitHub

## 📦 Arquivos

```
.github/workflows/
  └── scrape-distrowatch.yml    # GitHub Action workflow
scrape_runner.py                 # Script Python standalone
data/cache/
  └── distros_scraped.json       # Dados scraped (auto-gerado)
```

## 🎯 Como Usar

### 1. Ativar GitHub Actions

1. Vá em `Settings` > `Actions` > `General`
2. Ative "Allow all actions and reusable workflows"
3. Em "Workflow permissions", marque "Read and write permissions"

### 2. Executar Manualmente

1. Vá em `Actions` no GitHub
2. Clique em "Scrape DistroWatch"
3. Clique em "Run workflow"
4. Selecione branch `main`
5. Clique em "Run workflow"

### 3. Acessar Dados via API

```bash
# Dados do último scraping
curl https://api.distrowiki.com/scraping/scraped-data

# Status do scraping local
curl https://api.distrowiki.com/scraping/status
```

## ⏰ Schedule

Por padrão, roda **diariamente às 3h UTC (0h BRT)**. Para mudar:

```yaml
schedule:
  - cron: '0 3 * * *'  # 3h UTC todos os dias
  # - cron: '0 */6 * * *'  # A cada 6 horas
  # - cron: '0 0 * * 0'    # Aos domingos à meia-noite
```

## 🔍 Monitoramento

- **Logs**: `Actions` > `Scrape DistroWatch` > Ver run específico
- **Commits**: Histórico mostra atualizações automáticas
- **Arquivo**: `data/cache/distros_scraped.json` tem timestamp

## 📊 Estrutura dos Dados

```json
{
  "scraped_at": "2025-11-19T22:00:00",
  "scraped_by": "github-actions",
  "total": 100,
  "distros": [
    {
      "rank": "1",
      "name": "MX Linux",
      "url": "https://distrowatch.com/table.php?distribution=mx",
      "popularity_score": "2847"
    }
  ],
  "metadata": {
    "source": "distrowatch.com",
    "scraper": "playwright",
    "version": "1.0.0"
  }
}
```

## 🛠️ Desenvolvimento Local

Testar o scraper localmente:

```bash
# Instalar dependências
pip install playwright beautifulsoup4 lxml playwright-stealth
playwright install chromium

# Executar scraper
python scrape_runner.py
```

## 🚨 Troubleshooting

### Action falha com erro de permissão
- Verifique se "Read and write permissions" está ativado
- Settings > Actions > General > Workflow permissions

### Scraping retorna 0 distros
- Verifique logs do Action para ver erros específicos
- DistroWatch pode estar temporariamente indisponível

### Dados não aparecem na API
- Verifique se o arquivo `data/cache/distros_scraped.json` existe
- Certifique-se que o Action completou com sucesso

## 📈 Limites do GitHub Actions

- ✅ 2.000 minutos/mês (Free tier)
- ✅ Cada run ~5-10 minutos
- ✅ ~200-400 execuções/mês possíveis
- ✅ Suficiente para scraping diário

## 🔐 Segurança

- Não requer tokens ou credenciais extras
- Usa `GITHUB_TOKEN` automático do Actions
- Commits assinados pelo bot do GitHub
- Dados públicos do DistroWatch

## 📝 Notas

- **Primeira execução**: Faça manualmente para testar
- **Timezone**: UTC (ajuste cron se necessário)
- **Limit**: Padrão é 100 distros (top 100)
- **Fallback**: API local ainda funciona independentemente
