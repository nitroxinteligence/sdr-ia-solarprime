#!/bin/bash

echo "========================================"
echo "🚀 INICIANDO SISTEMA SEM KOMMO"
echo "========================================"

# Parar servidor atual
pkill -f "python main.py" 2>/dev/null

# Desabilitar Kommo
export ENABLE_KOMMO_AUTO_SYNC=false
export ENABLE_CRM_AGENT=false

echo "✅ Kommo desabilitado"
echo "▶️  Iniciando servidor..."

cd "/Users/adm/Downloads/1. NitroX Agentics/SDR IA SolarPrime v0.2"
python main.py