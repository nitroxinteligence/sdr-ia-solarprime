#!/bin/bash
# Deploy rápido no Railway

echo "🚀 Deploy Rápido SDR IA no Railway"
echo "=================================="
echo ""

# Verificar se Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI não encontrado!"
    echo ""
    echo "📦 Instale com:"
    echo "   brew install railway"
    echo "   ou"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Login no Railway
echo "🔐 Fazendo login no Railway..."
railway login

# Criar projeto
echo "📁 Criando novo projeto..."
railway init

# Configurar variáveis
echo "🔧 Configurando variáveis de ambiente..."
railway variables set GEMINI_API_KEY=$GEMINI_API_KEY
railway variables set EVOLUTION_API_URL=$EVOLUTION_API_URL
railway variables set EVOLUTION_API_KEY=$EVOLUTION_API_KEY
railway variables set EVOLUTION_INSTANCE_NAME=$EVOLUTION_INSTANCE_NAME
railway variables set SUPABASE_URL=$SUPABASE_URL
railway variables set SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
railway variables set SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY

# Deploy
echo "🚀 Fazendo deploy..."
railway up

# Gerar domínio
echo "🌐 Gerando URL pública..."
railway domain

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📝 Próximos passos:"
echo "1. Copie a URL gerada acima"
echo "2. Execute: python scripts/update_webhook_production.py"
echo "3. Cole a URL quando solicitado"
echo ""