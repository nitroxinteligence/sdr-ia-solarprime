#!/bin/bash

echo "🔍 Testando google-genai dentro do Docker..."
echo ""

# Executar o diagnóstico dentro do container
echo "📦 Executando diagnóstico no container..."
docker-compose exec app python diagnose_google_genai.py

echo ""
echo "📋 Listando pacotes Python instalados no container..."
docker-compose exec app pip list | grep -E "(google|genai|generative)"

echo ""
echo "🔧 Tentando instalar google-genai manualmente no container..."
docker-compose exec app pip install google-genai

echo ""
echo "📋 Verificando novamente os pacotes..."
docker-compose exec app pip list | grep -E "(google|genai|generative)"

echo ""
echo "🧪 Testando importação direta..."
docker-compose exec app python -c "
try:
    import google_genai
    print('✅ google_genai importado com sucesso!')
except ImportError as e:
    print(f'❌ Erro ao importar google_genai: {e}')
    
try:
    import google.generativeai
    print('✅ google.generativeai importado com sucesso!')
except ImportError as e:
    print(f'❌ Erro ao importar google.generativeai: {e}')
"

echo ""
echo "✅ Teste concluído!"