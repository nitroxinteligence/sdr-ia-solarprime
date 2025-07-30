#!/bin/bash
# Script para forçar deploy após force push
# Use este script no servidor se tiver acesso SSH

echo "🔄 Forçando atualização do repositório..."

# Salvar diretório atual
CURRENT_DIR=$(pwd)

# Ir para o diretório do app (ajuste conforme necessário)
cd /app || cd /home/app || cd /var/www/app || { echo "❌ Diretório do app não encontrado"; exit 1; }

echo "📍 Diretório atual: $(pwd)"

# Fazer backup dos arquivos .env se existirem
if [ -f .env ]; then
    echo "💾 Fazendo backup do .env..."
    cp .env .env.backup
fi

echo "🔄 Resetando repositório..."
git fetch --all
git reset --hard origin/main
git clean -fd

echo "✅ Repositório atualizado!"
echo "📝 Último commit:"
git log -1 --oneline

# Restaurar .env se havia backup
if [ -f .env.backup ]; then
    echo "♻️ Restaurando .env..."
    mv .env.backup .env
fi

# Instalar dependências
if [ -f requirements.txt ]; then
    echo "📦 Instalando dependências Python..."
    pip install -r requirements.txt
fi

echo "✅ Deploy forçado concluído!"
echo "🚀 Reinicie o serviço para aplicar as mudanças"

# Voltar ao diretório original
cd "$CURRENT_DIR"