#!/bin/bash

# Script para executar testes de race conditions
# Uso: ./run_race_condition_tests.sh

echo "🧪 EXECUTANDO TESTES DE RACE CONDITIONS - SDR IA SOLARPRIME"
echo "============================================================"

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.7+ para continuar."
    exit 1
fi

# Verificar se pip está disponível
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip para continuar."
    exit 1
fi

# Instalar dependências se necessário
echo "📦 Verificando dependências..."
pip3 install -q aiohttp

# Verificar se o servidor está rodando
echo "🔍 Verificando se o servidor está rodando..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Servidor detectado em localhost:8000"
else
    echo "❌ Servidor não detectado em localhost:8000"
    echo "💡 Inicie o servidor com: uvicorn agente.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🎯 Escolha o tipo de teste:"
echo "1. Teste crítico rápido (problemas específicos)"
echo "2. Teste completo de race conditions"
echo "3. Ambos os testes"
echo ""

read -p "Digite sua escolha (1-3): " choice

case $choice in
    1)
        echo "🚀 Executando teste crítico..."
        python3 test_critical_race_conditions.py
        ;;
    2)
        echo "🚀 Executando teste completo..."
        python3 test_race_condition_fixes.py
        ;;
    3)
        echo "🚀 Executando teste crítico primeiro..."
        python3 test_critical_race_conditions.py
        echo ""
        echo "🚀 Agora executando teste completo..."
        python3 test_race_condition_fixes.py
        ;;
    *)
        echo "❌ Escolha inválida. Saindo."
        exit 1
        ;;
esac

echo ""
echo "✅ Testes concluídos!"
echo "📄 Verifique os arquivos de relatório gerados (.json)"
echo ""