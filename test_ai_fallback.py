#!/usr/bin/env python3
"""
Teste do Sistema de Fallback AI
===============================
Testa o funcionamento do fallback de Gemini para OpenAI
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.sdr_agent import SDRAgent
from loguru import logger
import sys

# Configurar logging
logger.remove()
logger.add(sys.stdout, level="DEBUG")

# Carregar variáveis de ambiente
load_dotenv()


async def test_fallback():
    """Testa o sistema de fallback"""
    
    print("=== TESTE DO SISTEMA DE FALLBACK AI ===\n")
    
    # Verificar configuração
    print("1. Verificando configuração:")
    print(f"   - Gemini API Key: {'✅ Configurada' if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'YOUR_GEMINI_API_KEY_HERE' else '❌ Não configurada'}")
    print(f"   - OpenAI API Key: {'✅ Configurada' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'YOUR_OPENAI_API_KEY_HERE' else '❌ Não configurada'}")
    print(f"   - Fallback habilitado: {'✅ Sim' if os.getenv('ENABLE_FALLBACK', 'true').lower() == 'true' else '❌ Não'}")
    print(f"   - Modelo Gemini: {os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')}")
    print(f"   - Modelo OpenAI: {os.getenv('OPENAI_MODEL', 'gpt-4.1-nano')}")
    print(f"   - Max tentativas: {os.getenv('MAX_AI_RETRIES', '3')}")
    print()
    
    # Criar agente
    print("2. Inicializando agente SDR...")
    try:
        agent = SDRAgent()
        print("   ✅ Agente inicializado com sucesso")
        
        # Verificar modelos
        if agent.model:
            print("   ✅ Modelo Gemini configurado")
        if agent.fallback_model:
            print("   ✅ Modelo OpenAI (fallback) configurado")
        else:
            print("   ⚠️  Modelo OpenAI (fallback) NÃO configurado")
        print()
        
    except Exception as e:
        print(f"   ❌ Erro ao inicializar agente: {e}")
        return
    
    # Testar processamento
    print("3. Testando processamento de mensagem...")
    
    test_messages = [
        "Olá, quero saber sobre energia solar",
        "Meu nome é João Silva",
        "Moro em uma casa",
        "Minha conta de luz vem cerca de R$ 500"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Teste {i}: '{message}'")
        try:
            response, metadata = await agent.process_message(
                message=message,
                phone_number="5511999999999",
                message_id=f"TEST_{i}"
            )
            
            print(f"   ✅ Resposta recebida ({len(response)} caracteres)")
            print(f"   Modelo usado: {metadata.get('model_used', 'unknown')}")
            print(f"   Tempo de resposta: {metadata.get('response_time', 'N/A')}s")
            
            # Mostrar primeiros 100 caracteres da resposta
            preview = response[:100] + "..." if len(response) > 100 else response
            print(f"   Preview: {preview}")
            
        except Exception as e:
            print(f"   ❌ Erro ao processar: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")


if __name__ == "__main__":
    asyncio.run(test_fallback())