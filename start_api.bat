@echo off
REM Script para iniciar a API FastAPI no Windows

echo.
echo ========================================
echo  DistroWiki API - Iniciando...
echo ========================================
echo.

cd /d "%~dp0"

REM Ativar venv se existir
if exist venv\Scripts\activate.bat (
    echo [*] Ativando virtual environment...
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment ativado
    echo.
)

REM Iniciar API
echo [*] Iniciando API FastAPI na porta 8000...
echo.

python -m uvicorn api.main:app --reload --port 8000

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar a API
    echo.
    echo Possíveis soluções:
    echo 1. pip install -r requirements.txt
    echo 2. Verificar se a porta 8000 está disponível
    echo.
    pause
)
