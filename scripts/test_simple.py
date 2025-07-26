#!/usr/bin/env python3
"""
Teste Simples do Agente SDR
===========================
Testa se o agente funciona corretamente
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from loguru import logger

async def test_agent():
    """Testa o agente SDR"""
    print("🧪 Teste Simples do SDR SolarPrime\n")
    
    try:
        # Cria o agente
        print("1️⃣ Criando agente...")
        agent = SDRAgent()
        print("✅ Agente criado com sucesso!\n")
        
        # Testa iniciar conversa
        print("2️⃣ Iniciando conversa...")
        phone = "5511999999999"
        greeting, metadata = await agent.start_conversation(phone)
        
        print(f"✅ Conversa iniciada!")
        print(f"📱 Telefone: {phone}")
        print(f"💬 Resposta: {greeting[:100]}...")
        print(f"📊 Metadados: {metadata}\n")
        
        # Testa processar mensagem
        print("3️⃣ Processando mensagem do usuário...")
        user_message = "Olá! Quero saber mais sobre energia solar"
        response, metadata = await agent.process_message(user_message, phone)
        
        print(f"✅ Mensagem processada!")
        print(f"👤 Usuário: {user_message}")
        print(f"🤖 Resposta: {response[:100]}...")
        print(f"📊 Stage: {metadata.get('stage')}")
        print(f"📊 Sentiment: {metadata.get('sentiment')}\n")
        
        # Testa análise de interesse
        print("4️⃣ Testando pergunta sobre custo...")
        user_message = "Mas isso não é muito caro?"
        response, metadata = await agent.process_message(user_message, phone)
        
        print(f"✅ Pergunta sobre custo processada!")
        print(f"👤 Usuário: {user_message}")
        print(f"🤖 Resposta: {response[:150]}...")
        
        print("\n✅ TODOS OS TESTES PASSARAM!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        logger.exception("Erro detalhado:")
        return False

if __name__ == "__main__":
    # Executa o teste
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)