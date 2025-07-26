#!/bin/bash
#
# Test Runner Script
# ==================
# Script para executar testes de integração Evolution API
#

set -e

echo "🧪 Executando testes de integração Evolution API..."
echo "=============================================="

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Execute este script do diretório raiz do projeto"
    exit 1
fi

# Verificar se pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo "📦 Instalando pytest..."
    pip install pytest pytest-asyncio pytest-cov
fi

# Opções de teste
TEST_TYPE=${1:-"all"}
COVERAGE=${2:-"yes"}

case $TEST_TYPE in
    "unit")
        echo "📋 Executando testes unitários..."
        if [ "$COVERAGE" = "yes" ]; then
            pytest tests/unit/ -v --cov=services --cov-report=html --cov-report=term
        else
            pytest tests/unit/ -v
        fi
        ;;
    
    "integration")
        echo "🔗 Executando testes de integração..."
        if [ "$COVERAGE" = "yes" ]; then
            pytest tests/test_evolution_integration.py -v --cov=services --cov-report=html --cov-report=term
        else
            pytest tests/test_evolution_integration.py -v
        fi
        ;;
    
    "evolution")
        echo "🌐 Executando apenas testes Evolution API..."
        pytest tests/test_evolution_integration.py::TestEvolutionAPIClient -v
        ;;
    
    "whatsapp")
        echo "💬 Executando apenas testes WhatsApp Service..."
        pytest tests/test_evolution_integration.py::TestWhatsAppService -v
        ;;
    
    "monitor")
        echo "📊 Executando apenas testes Connection Monitor..."
        pytest tests/test_evolution_integration.py::TestConnectionMonitor -v
        ;;
    
    "full")
        echo "🚀 Executando testes de integração completa..."
        pytest tests/test_evolution_integration.py::TestFullIntegration -v
        ;;
    
    "all"|*)
        echo "✅ Executando todos os testes..."
        if [ "$COVERAGE" = "yes" ]; then
            pytest -v --cov=services --cov=api --cov-report=html --cov-report=term
        else
            pytest -v
        fi
        ;;
esac

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Testes executados com sucesso!"
    
    if [ "$COVERAGE" = "yes" ] && [ -d "htmlcov" ]; then
        echo "📊 Relatório de cobertura gerado em: htmlcov/index.html"
    fi
else
    echo ""
    echo "❌ Alguns testes falharam. Verifique os logs acima."
    exit 1
fi

# Dicas úteis
echo ""
echo "💡 Dicas:"
echo "  - Use './scripts/run_tests.sh unit' para executar apenas testes unitários"
echo "  - Use './scripts/run_tests.sh integration' para executar apenas testes de integração"
echo "  - Use './scripts/run_tests.sh evolution' para testar apenas o cliente Evolution API"
echo "  - Use './scripts/run_tests.sh all no' para executar sem cobertura (mais rápido)"
echo "  - Adicione '-k pattern' ao pytest para filtrar testes específicos"