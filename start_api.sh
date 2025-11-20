#!/bin/bash

# Script para iniciar a API DistroWiki rapidamente
# Autor: DistroWiki Team
# Uso: ./start_api.sh

set -e  # Para em caso de erro

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🚀 DistroWiki API Startup Script   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

# Verifica se está no diretório correto
if [ ! -f "api/main.py" ]; then
    echo -e "${RED}❌ Erro: Execute este script do diretório raiz do projeto (distrowiki-api)${NC}"
    exit 1
fi

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Erro: Python3 não encontrado. Instale o Python 3.8+${NC}"
    exit 1
fi

# Verifica/cria ambiente virtual
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}📦 Ambiente virtual não encontrado. Criando...${NC}"
    
    # Tenta criar venv
    if ! python3 -m venv venv 2>/dev/null; then
        echo -e "${RED}❌ Erro ao criar ambiente virtual${NC}"
        echo -e "${YELLOW}💡 No Ubuntu/Debian, instale: ${NC}${BLUE}sudo apt install python3-venv${NC}"
        echo -e "${YELLOW}💡 No Fedora/RHEL, instale: ${NC}${BLUE}sudo dnf install python3-virtualenv${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}\n"
fi

# Ativa o ambiente virtual
echo -e "${BLUE}🔧 Ativando ambiente virtual...${NC}"
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}❌ Erro: Arquivo activate não encontrado em venv/bin/${NC}"
    echo -e "${YELLOW}💡 Recrie o venv manualmente: ${NC}${BLUE}rm -rf venv && python3 -m venv venv${NC}"
    exit 1
fi

source venv/bin/activate

# Verifica/instala dependências
if [ ! -f "venv/bin/uvicorn" ]; then
    echo -e "${YELLOW}📥 Instalando dependências...${NC}"
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo -e "${GREEN}✅ Dependências instaladas${NC}\n"
fi

# Cria diretório de cache se não existir
if [ ! -d "data/cache" ]; then
    echo -e "${BLUE}📁 Criando diretório de cache...${NC}"
    mkdir -p data/cache
    echo -e "${GREEN}✅ Diretório de cache criado${NC}\n"
fi

# Verifica se a porta 8000 está em uso
if command -v lsof &> /dev/null && lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta 8000 já está em uso!${NC}"
    echo -e "${YELLOW}Deseja matar o processo? (s/n)${NC}"
    read -r -n 1 response
    echo
    if [[ "$response" =~ ^([sS]|[yY])$ ]]; then
        echo -e "${YELLOW}� Matando processo na porta 8000...${NC}"
        kill -9 $(lsof -t -i:8000) 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✅ Processo finalizado${NC}\n"
    else
        echo -e "${RED}❌ Abortando. Libere a porta 8000 manualmente.${NC}"
        exit 1
    fi
fi

# Informações do servidor
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      🎯 Servidor Configurado          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e "${BLUE}📍 Host:${NC}      0.0.0.0:8000"
echo -e "${BLUE}📚 Docs:${NC}      http://localhost:8000/docs"
echo -e "${BLUE}❤️  Health:${NC}    http://localhost:8000/health"
echo -e "${BLUE}🔥 Modo:${NC}      Development (hot-reload)"
echo -e "\n${YELLOW}⌨️  Pressione Ctrl+C para parar o servidor${NC}\n"

# Aguardar 3 segundos e abrir navegador em segundo plano
(sleep 3 && xdg-open "http://localhost:8000/docs" 2>/dev/null) &

# Inicia o servidor
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload