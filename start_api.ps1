# Script para iniciar a API DistroWiki
# Uso: .\start_api.ps1

Write-Host "`n🚀 Iniciando DistroWiki API...`n" -ForegroundColor Cyan

# Verificar se está no diretório correto
if (-not (Test-Path "api\main.py")) {
    Write-Host "❌ Erro: Execute este script do diretório raiz do projeto" -ForegroundColor Red
    exit 1
}

# Verificar se venv existe
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Erro: Ambiente virtual não encontrado" -ForegroundColor Red
    Write-Host "Execute: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Iniciar servidor
Write-Host "📡 Iniciando servidor FastAPI..." -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor White
Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n⌨️  Pressione Ctrl+C para parar o servidor`n" -ForegroundColor Yellow

# Aguardar 2 segundos e abrir navegador
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8000/docs"
} | Out-Null

# Executar servidor
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
