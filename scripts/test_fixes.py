#!/usr/bin/env python3
"""
Teste Rápido das Correções
=========================
Testa se o agente mantém contexto corretamente
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from loguru import logger

async def test_context_persistence():
    """Testa se o contexto é mantido entre mensagens"""
    print("🧪 Testando Persistência de Contexto\n")
    
    agent = SDRAgent()
    phone = "5511999999999"
    
    # Teste 1: Iniciar conversa
    print("1️⃣ Iniciando conversa...")
    response1, meta1 = await agent.start_conversation(phone)
    print(f"✅ Resposta inicial recebida")
    print(f"   Stage: {meta1['stage']}\n")
    
    # Teste 2: Enviar "oi"
    print("2️⃣ Enviando 'oi'...")
    response2, meta2 = await agent.process_message("oi", phone)
    print(f"✅ Resposta: {response2[:100]}...")
    print(f"   Stage: {meta2['stage']}")
    print(f"   Lead info: {meta2['lead_info']}\n")
    
    # Teste 3: Enviar nome
    print("3️⃣ Enviando nome 'Mateus'...")
    response3, meta3 = await agent.process_message("mateus", phone)
    print(f"✅ Resposta: {response3[:100]}...")
    print(f"   Stage: {meta3['stage']}")
    print(f"   Lead info: {meta3['lead_info']}")
    
    # Verificações
    print("\n📊 VERIFICAÇÕES:")
    
    # Verifica se salvou o nome
    if meta3['lead_info'].get('name') == 'Mateus':
        print("✅ Nome foi salvo corretamente!")
    else:
        print(f"❌ Nome não foi salvo. Lead info: {meta3['lead_info']}")
    
    # Verifica se não repetiu apresentação
    if "Luna" in response3 and "consultora" in response3:
        print("❌ ERRO: Agente se apresentou novamente!")
    else:
        print("✅ Agente não repetiu apresentação")
    
    # Verifica mudança de estágio
    if meta3['stage'] != "INITIAL_CONTACT":
        print(f"✅ Estágio mudou para: {meta3['stage']}")
    else:
        print("⚠️  Estágio ainda em INITIAL_CONTACT")
    
    # Teste 4: Enviar tipo de imóvel
    print("\n4️⃣ Enviando 'na minha residência'...")
    response4, meta4 = await agent.process_message("na minha residência", phone)
    print(f"✅ Resposta: {response4[:100]}...")
    print(f"   Stage: {meta4['stage']}")
    print(f"   Lead info: {meta4['lead_info']}")
    
    # Verifica se manteve o nome
    if meta4['lead_info'].get('name') == 'Mateus':
        print("✅ Nome foi mantido!")
    else:
        print(f"❌ Nome foi perdido! Lead info: {meta4['lead_info']}")
    
    # Mostra resumo da conversa
    print("\n📝 RESUMO DA CONVERSA:")
    summary = agent.get_conversation_summary(phone)
    print(f"   Total de mensagens: {summary['conversation_count']}")
    print(f"   Estágio atual: {summary['current_stage']}")
    print(f"   Informações coletadas: {summary['lead_info']}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_context_persistence())