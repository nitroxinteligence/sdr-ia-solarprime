#!/bin/bash
# =============================================================================
# Script de Desenvolvimento - SDR IA SolarPrime
# =============================================================================
# Facilita o desenvolvimento local verificando dependências e serviços
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "============================================================="
echo "         SDR IA SolarPrime - Ambiente de Desenvolvimento      "
echo "============================================================="
echo -e "${NC}"

# Função para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 instalado${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 não encontrado${NC}"
        return 1
    fi
}

# Função para verificar serviço
check_service() {
    if lsof -Pi :$2 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $1 rodando na porta $2${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $1 não está rodando na porta $2${NC}"
        return 1
    fi
}

# 1. Verificar Python
echo -e "\n${BLUE}📦 Verificando dependências...${NC}"
echo "-------------------------------------------------------------"

if ! check_command python3; then
    echo -e "${RED}Python 3 é necessário!${NC}"
    echo "Instale com: brew install python3"
    exit 1
fi

# 2. Verificar ambiente virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🔧 Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# 3. Ativar ambiente virtual
echo -e "\n${BLUE}🐍 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# 4. Instalar/atualizar dependências
echo -e "\n${BLUE}📦 Verificando dependências Python...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 5. Verificar arquivo .env
echo -e "\n${BLUE}🔐 Verificando configuração...${NC}"
echo "-------------------------------------------------------------"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado!${NC}"
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env criado - Configure suas variáveis de ambiente!${NC}"
else
    echo -e "${GREEN}✅ .env encontrado${NC}"
fi

# 6. Verificar serviços locais
echo -e "\n${BLUE}🔍 Verificando serviços locais...${NC}"
echo "-------------------------------------------------------------"

REDIS_RUNNING=false
EVOLUTION_RUNNING=false

if check_service "Redis" 6379; then
    REDIS_RUNNING=true
fi

if check_service "Evolution API" 8080; then
    EVOLUTION_RUNNING=true
fi

# 7. Oferecer para iniciar serviços
echo -e "\n${BLUE}🚀 Opções de inicialização:${NC}"
echo "-------------------------------------------------------------"

if [ "$REDIS_RUNNING" = false ]; then
    echo -e "${YELLOW}Redis não está rodando.${NC}"
    echo "Para iniciar Redis com Docker:"
    echo -e "${BLUE}docker run -d -p 6379:6379 --name redis-dev redis:alpine${NC}"
    echo ""
fi

if [ "$EVOLUTION_RUNNING" = false ]; then
    echo -e "${YELLOW}Evolution API não está rodando.${NC}"
    echo "Para iniciar Evolution API com Docker:"
    echo -e "${BLUE}docker run -d -p 8080:8080 --name evolution-dev evolution-api/evolution-api${NC}"
    echo ""
fi

# 8. Criar diretórios necessários
echo -e "\n${BLUE}📁 Verificando diretórios...${NC}"
echo "-------------------------------------------------------------"

directories=("logs" "temp" "uploads" "data")
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✅ Diretório $dir criado${NC}"
    else
        echo -e "${GREEN}✅ Diretório $dir OK${NC}"
    fi
done

# 9. Iniciar aplicação
echo -e "\n${BLUE}🚀 Iniciando aplicação...${NC}"
echo "============================================================="
echo -e "${GREEN}"
echo "A aplicação será iniciada em modo desenvolvimento."
echo ""
if [ "$REDIS_RUNNING" = false ] || [ "$EVOLUTION_RUNNING" = false ]; then
    echo -e "${YELLOW}⚠️  ATENÇÃO: Alguns serviços não estão disponíveis:${NC}"
    [ "$REDIS_RUNNING" = false ] && echo -e "${YELLOW}   - Cache em memória será usado (Redis não disponível)${NC}"
    [ "$EVOLUTION_RUNNING" = false ] && echo -e "${YELLOW}   - WhatsApp não funcionará (Evolution API não disponível)${NC}"
    echo ""
fi
echo -e "${GREEN}Pressione Ctrl+C para parar a aplicação.${NC}"
echo "============================================================="
echo -e "${NC}"

# 10. Iniciar servidor
export ENVIRONMENT=development
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000