#!/usr/bin/env python3
"""
Test Calendar Integration with SDR Agent
========================================
Script para testar a integração completa do Google Calendar com o SDR Agent
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from agents.sdr_agent_v2 import SDRAgentV2
from config.config import Config
from repositories.lead_repository import lead_repository
from services.database import db


async def test_sdr_calendar_integration():
    """Testa a integração do Calendar através do SDR Agent"""
    
    print("\n🤖 TESTE DE INTEGRAÇÃO SDR AGENT + GOOGLE CALENDAR\n")
    print("="*60)
    
    # 1. Inicializar configuração e agente
    print("\n1️⃣ Inicializando SDR Agent V2...")
    try:
        config = Config()
        agent = SDRAgentV2(config)
        await agent.initialize()
        print("✅ Agent inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar agent: {e}")
        return
    
    # 2. Criar lead de teste
    test_phone = "+5511999999999"
    print(f"\n2️⃣ Criando lead de teste: {test_phone}")
    
    try:
        # Criar ou atualizar lead
        from models.lead import LeadCreate
        lead_data = LeadCreate(
            phone_number=test_phone,
            name="João Teste Calendar",
            email="teste@example.com"
        )
        lead = await lead_repository.create_or_update(lead_data)
        print(f"✅ Lead criado/atualizado: {lead.name}")
    except Exception as e:
        print(f"❌ Erro ao criar lead: {e}")
        return
    
    # 3. Testar agendamento via agent
    print("\n3️⃣ Testando agendamento de reunião...")
    
    # Simular mensagem pedindo agendamento
    message = "Oi! Gostaria de agendar uma reunião para conhecer melhor a SolarPrime. Vocês têm horário amanhã?"
    
    try:
        response, metadata = await agent.process_message(
            message=message,
            phone_number=test_phone
        )
        
        print(f"\n💬 Usuário: {message}")
        print(f"🤖 Agent: {response}")
        print(f"📊 Metadata: {metadata}")
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")
    
    # 4. Testar escolha de horário
    print("\n4️⃣ Testando escolha de horário...")
    
    # Simular escolha de horário
    tomorrow = datetime.now() + timedelta(days=1)
    message2 = f"Pode ser amanhã às 14h?"
    
    try:
        response2, metadata2 = await agent.process_message(
            message=message2,
            phone_number=test_phone
        )
        
        print(f"\n💬 Usuário: {message2}")
        print(f"🤖 Agent: {response2}")
        print(f"📊 Metadata: {metadata2}")
        
    except Exception as e:
        print(f"❌ Erro ao processar escolha de horário: {e}")
    
    # 5. Verificar se a reunião foi agendada
    print("\n5️⃣ Verificando dados do lead...")
    
    try:
        # Recarregar lead
        updated_lead = await lead_repository.get_by_phone(test_phone)
        if updated_lead:
            print(f"✅ Lead atualizado:")
            print(f"   - Nome: {updated_lead.name}")
            print(f"   - Estágio: {updated_lead.current_stage}")
            print(f"   - Reunião: {updated_lead.meeting_scheduled_at}")
            print(f"   - Event ID: {updated_lead.google_event_id}")
        else:
            print("❌ Lead não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao verificar lead: {e}")
    
    # 6. Testar reagendamento
    print("\n6️⃣ Testando reagendamento...")
    
    message3 = "Preciso mudar nossa reunião para sexta-feira às 10h"
    
    try:
        response3, metadata3 = await agent.process_message(
            message=message3,
            phone_number=test_phone
        )
        
        print(f"\n💬 Usuário: {message3}")
        print(f"🤖 Agent: {response3}")
        
    except Exception as e:
        print(f"❌ Erro ao testar reagendamento: {e}")
    
    # 7. Testar cancelamento
    print("\n7️⃣ Testando cancelamento...")
    
    message4 = "Preciso cancelar nossa reunião"
    
    try:
        response4, metadata4 = await agent.process_message(
            message=message4,
            phone_number=test_phone
        )
        
        print(f"\n💬 Usuário: {message4}")
        print(f"🤖 Agent: {response4}")
        
    except Exception as e:
        print(f"❌ Erro ao testar cancelamento: {e}")
    
    print("\n" + "="*60)
    print("✅ TESTE DE INTEGRAÇÃO CONCLUÍDO!")
    print("\nVerifique:")
    print("1. Google Calendar - Os eventos foram criados/modificados")
    print("2. Banco de dados - Os leads foram atualizados")
    print("3. Logs - Para detalhes da execução")


async def test_calendar_tools_directly():
    """Testa as tools do Calendar diretamente"""
    
    print("\n🔧 TESTE DIRETO DAS CALENDAR TOOLS\n")
    print("="*60)
    
    from agents.tools.google_calendar_tools import (
        schedule_solar_meeting,
        get_available_slots,
        check_next_meeting
    )
    
    test_phone = "+5511888888888"
    
    # 1. Criar lead de teste
    print("\n1️⃣ Criando lead para teste direto...")
    try:
        from models.lead import LeadCreate
        lead_data = LeadCreate(
            phone_number=test_phone,
            name="Maria Teste Tools",
            email="maria@example.com"
        )
        lead = await lead_repository.create_or_update(lead_data)
        print(f"✅ Lead criado: {lead.name}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # 2. Testar get_available_slots
    print("\n2️⃣ Testando busca de horários disponíveis...")
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        # As tools do AGnO são funções diretas
        result = await get_available_slots(date=tomorrow)
        slots = result if isinstance(result, list) else []
        print(f"✅ Horários disponíveis para {tomorrow}:")
        for slot in slots[:5]:
            print(f"   - {slot}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Testar agendamento direto
    print("\n3️⃣ Testando agendamento direto...")
    try:
        # Chamar a função diretamente
        result = await schedule_solar_meeting(
            lead_phone=test_phone,
            date=tomorrow,
            time="15:00",
            lead_name="Maria Teste Tools"
        )
        print(f"✅ Resultado: {result['status']}")
        print(f"   Mensagem: {result.get('mensagem', '')}")
        if result['status'] == 'sucesso':
            print(f"   Event ID: {result.get('event_id', '')}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 4. Verificar próxima reunião
    print("\n4️⃣ Testando verificação de reunião...")
    try:
        # Chamar diretamente
        meeting_info = await check_next_meeting(lead_phone=test_phone)
        print(f"✅ Status: {meeting_info['status']}")
        print(f"   {meeting_info['mensagem']}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "="*60)
    print("✅ TESTE DIRETO CONCLUÍDO!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Testar integração Calendar + SDR Agent")
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Testar tools diretamente (sem agent)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Executar todos os testes"
    )
    
    args = parser.parse_args()
    
    if args.direct:
        asyncio.run(test_calendar_tools_directly())
    elif args.full:
        asyncio.run(test_calendar_tools_directly())
        print("\n" + "🔄"*30 + "\n")
        asyncio.run(test_sdr_calendar_integration())
    else:
        asyncio.run(test_sdr_calendar_integration())