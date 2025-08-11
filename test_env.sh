#!/bin/bash
# Script para executar testes com variáveis de ambiente mínimas

export EVOLUTION_API_URL="http://localhost:8080"
export EVOLUTION_API_KEY="test_key"
export EVOLUTION_INSTANCE_NAME="test_instance"
export GOOGLE_API_KEY="test_google_key"
export DATABASE_URL="postgresql://test:test@localhost/test"

# Executar o teste
python test_phase2_validation.py