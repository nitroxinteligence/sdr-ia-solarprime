#!/bin/bash

echo "🔧 Reconstruindo Docker sem cache..."

# Para todos os containers
docker-compose down

# Remove imagens antigas
docker rmi sdr-ia-solarprime-python-app:latest || true

# Reconstrói sem cache
docker-compose build --no-cache

# Inicia os containers
docker-compose up -d

echo "✅ Docker reconstruído sem cache!"
echo ""
echo "📊 Verificando status dos containers:"
docker-compose ps

echo ""
echo "📝 Verificando logs da aplicação:"
docker-compose logs -n 50 app