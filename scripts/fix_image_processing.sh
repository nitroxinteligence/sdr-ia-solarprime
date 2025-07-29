#!/bin/bash
# Script para corrigir processamento de imagens

echo "🔧 Corrigindo processamento de imagens..."

# Instalar dependências de imagem
echo "📦 Instalando dependências..."
pip install Pillow python-magic pdf2image

# No macOS, instalar libmagic
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detectado macOS - instalando libmagic..."
    if command -v brew &> /dev/null; then
        brew install libmagic
    else
        echo "⚠️  Homebrew não encontrado. Instale libmagic manualmente."
    fi
fi

# No Linux, instalar poppler-utils para pdf2image
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detectado Linux - instalando poppler-utils..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y poppler-utils libmagic1
    elif command -v yum &> /dev/null; then
        sudo yum install -y poppler-utils file-libs
    fi
fi

echo "✅ Dependências instaladas!"

# Executar teste
echo ""
echo "🧪 Executando teste com imagem válida..."
python tests/test_real_image.py

echo ""
echo "✅ Correção concluída!"
echo ""
echo "📝 Resumo das melhorias:"
echo "   • Validação de imagem antes do processamento"
echo "   • Suporte a formatos: PNG, JPEG, GIF, WebP"
echo "   • Detecção de imagens inválidas"
echo "   • Mensagens de erro mais claras"
echo "   • Correção automática de orientação EXIF"
echo ""
echo "💡 Próximos passos:"
echo "   1. Teste com fotos reais de contas de luz"
echo "   2. Execute: python tests/test_agno_integration.py"