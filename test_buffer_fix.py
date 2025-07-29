#!/usr/bin/env python3
"""
Test Buffer Fix
===============
Testa a correção do erro de process_buffered_messages
"""

import asyncio
import os
import sys
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.sdr_agent import create_sdr_agent


async def test_agent():
    """Testa se o agente processa mensagens corretamente"""
    
    print("🧪 Testando SDRAgent com mensagem consolidada...")
    
    # Criar agente
    agent = create_sdr_agent()
    
    # Testar com mensagem consolidada
    phone = "5511999999999"
    consolidated_message = "Olá tudo bem? Gostaria de saber sobre energia solar para minha casa"
    
    try:
        # Processar mensagem
        response, metadata = await agent.process_message(
            message=consolidated_message,
            phone_number=phone,
            media_type=None,
            media_data=None,
            message_id=f"TEST_{datetime.now().timestamp()}"
        )
        
        print(f"✅ Sucesso! Resposta: {response[:100]}...")
        print(f"📊 Metadata: {metadata}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent())