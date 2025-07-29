#!/bin/bash
# Script para iniciar o servidor SDR IA SolarPrime
# Garante que apenas 1 worker seja usado para evitar problemas de concorrência

# Carregar variáveis de ambiente
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Definir número de workers (padrão: 1)
WORKERS=${UVICORN_WORKERS:-1}

# Verificar se está em produção
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🚀 Iniciando servidor em modo PRODUÇÃO com $WORKERS worker(s)"
    uvicorn api.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers $WORKERS \
        --log-level info \
        --access-log
else
    echo "🔧 Iniciando servidor em modo DESENVOLVIMENTO com $WORKERS worker(s)"
    uvicorn api.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers $WORKERS \
        --reload \
        --log-level debug
fi