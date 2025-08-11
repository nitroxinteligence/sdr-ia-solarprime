#!/bin/bash
# Script para configurar .env no Docker
# Copia o .env local para o container se necessário

if [ -f ".env" ]; then
    echo "✅ Arquivo .env encontrado localmente"
    
    # Se estiver rodando no Docker, copia para /app/
    if [ -d "/app" ]; then
        cp .env /app/.env
        echo "✅ .env copiado para /app/.env"
    fi
else
    echo "⚠️ Arquivo .env não encontrado"
fi