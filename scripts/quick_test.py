#!/usr/bin/env python3
"""
Teste Rápido do Agente SDR com AGnO
===================================
Script simples para testar se o agente está funcionando
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import create_sdr_agent
from config.agent_config import config

async def quick_test():
    print("🤖 Teste Rápido - SDR SolarPrime com AGnO Framework\n")
    
    try:
        # Verifica API Key
        if not config.gemini.api_key or config.gemini.api_key == "YOUR_GEMINI_API_KEY_HERE":
            print("❌ ERRO: Configure sua GEMINI_API_KEY no arquivo .env")
            print("📝 Edite o arquivo .env e adicione sua chave real")
            return
        
        print("✅ API Key configurada")
        
        # Cria agente
        print("🔧 Criando agente Luna...")
        agent = create_sdr_agent()
        print("✅ Agente criado com sucesso!")
        
        # Testa conversa
        print("\n🗣️ Iniciando conversa de teste...")
        phone = "+5511999999999"
        
        # Mensagem inicial
        response, metadata = await agent.start_conversation(phone)
        print(f"\n🤖 Luna: {response}")
        print(f"📊 Estágio: {metadata.get('stage')}")
        
        # Simula resposta do usuário
        user_message = "Oi Luna! Tenho interesse em saber mais sobre energia solar."
        print(f"\n👤 Você: {user_message}")
        
        # Processa resposta
        response, metadata = await agent.process_message(user_message, phone)
        print(f"\n🤖 Luna: {response}")
        print(f"📊 Estágio: {metadata.get('stage')}")
        print(f"📊 Sentimento: {metadata.get('sentiment')}")
        
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("\n💡 Execute 'python scripts/test_agent.py' para teste completo")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n🔍 Verifique:")
        print("1. Sua GEMINI_API_KEY está correta no .env")
        print("2. Você tem conexão com a internet")
        print("3. O ambiente virtual está ativado")

if __name__ == "__main__":
    asyncio.run(quick_test())