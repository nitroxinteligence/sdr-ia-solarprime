#!/usr/bin/env python
"""
Test Script - Verificação das Melhorias do Google Calendar
==========================================================
Testa as correções e melhorias implementadas na integração com Google Calendar
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger

# Carregar variáveis de ambiente
load_dotenv()

# Imports necessários
from agents.tools.google_calendar_tools import (
    schedule_solar_meeting,
    reschedule_meeting,
    cancel_meeting,
    check_next_meeting
)
from repositories.lead_repository import lead_repository
from models.lead import LeadCreate, LeadUpdate
from uuid import uuid4


async def test_enriched_calendar_integration():
    """Testa a integração enriquecida com Google Calendar"""
    
    print("\n=== TESTE DE INTEGRAÇÃO GOOGLE CALENDAR ENRIQUECIDA ===\n")
    
    # 1. Criar um lead de teste completo
    test_phone = f"5511{str(uuid4().int)[:9]}"  # Número único
    print(f"📱 Criando lead de teste: {test_phone}")
    
    lead = await lead_repository.create(LeadCreate(
        phone_number=test_phone,
        name="João Silva Teste",
        email="joao.teste@example.com"
    ))
    
    # 2. Atualizar lead com dados completos de qualificação
    print("📝 Atualizando dados de qualificação do lead...")
    
    await lead_repository.update(lead.id, LeadUpdate(
        bill_value=5500.00,  # Acima de R$ 4.000
        consumption_kwh=450,
        is_decision_maker=True,
        has_solar_system=False,
        has_active_contract=False,
        qualification_status="QUALIFIED",
        qualification_score=85,
        current_stage="SCHEDULING",
        solution_interest="Usina Própria - Investimento",
        notes="Lead muito interessado. Mora em casa própria com telhado amplo. Quer reduzir custos fixos. Perguntou sobre financiamento.",
        kommo_lead_id="123456"  # ID fictício para teste
    ))
    
    # Recarregar lead atualizado
    lead = await lead_repository.get(lead.id)
    
    # 3. Tentar agendar reunião
    print("\n📅 Testando agendamento de reunião com dados enriquecidos...")
    
    # Data para amanhã às 14h
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow.weekday() >= 5:  # Se for fim de semana
        tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))  # Próxima segunda
    
    date_str = tomorrow.strftime("%d/%m/%Y")
    time_str = "14:00"
    
    result = await schedule_solar_meeting(
        lead_phone=test_phone,
        date=date_str,
        time=time_str,
        lead_name=lead.name,
        meeting_type="initial_meeting"
    )
    
    print(f"\nResultado do agendamento:")
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result.get('mensagem', 'N/A')}")
    
    if result['status'] == 'sucesso':
        print(f"Event ID: {result.get('event_id', 'N/A')}")
        print(f"Event Link: {result.get('event_link', 'N/A')}")
        
        # Verificar se o google_event_id foi salvo
        lead_updated = await lead_repository.get(lead.id)
        print(f"\n✅ Google Event ID salvo no banco: {lead_updated.google_event_id}")
        
        # 4. Testar reagendamento
        print("\n🔄 Testando reagendamento...")
        
        new_date = (tomorrow + timedelta(days=1)).strftime("%d/%m/%Y")
        new_time = "15:00"
        
        reschedule_result = await reschedule_meeting(
            lead_phone=test_phone,
            new_date=new_date,
            new_time=new_time,
            reason="Cliente solicitou mudança de horário por compromisso urgente"
        )
        
        print(f"\nResultado do reagendamento:")
        print(f"Status: {reschedule_result['status']}")
        print(f"Mensagem: {reschedule_result.get('mensagem', 'N/A')}")
        
        # 5. Verificar próxima reunião
        print("\n📋 Verificando dados da reunião...")
        
        meeting_info = await check_next_meeting(test_phone)
        print(f"Status: {meeting_info['status']}")
        print(f"Informações: {meeting_info.get('mensagem', 'N/A')}")
        
        # 6. Testar cancelamento
        print("\n❌ Testando cancelamento...")
        
        cancel_result = await cancel_meeting(
            lead_phone=test_phone,
            reason="Teste de cancelamento - ignorar"
        )
        
        print(f"\nResultado do cancelamento:")
        print(f"Status: {cancel_result['status']}")
        print(f"Mensagem: {cancel_result.get('mensagem', 'N/A')}")
        
        # Verificar se o google_event_id foi removido
        lead_final = await lead_repository.get(lead.id)
        print(f"\n✅ Google Event ID após cancelamento: {lead_final.google_event_id}")
        
    else:
        print(f"\n❌ Erro no agendamento: {result.get('mensagem', 'Erro desconhecido')}")
        if 'erros_qualificacao' in result:
            print("\nErros de qualificação:")
            for erro in result['erros_qualificacao']:
                print(f"  • {erro}")
    
    # 7. Limpar dados de teste
    print("\n🧹 Limpando dados de teste...")
    await lead_repository.delete(lead.id)
    
    print("\n✅ Teste concluído!")


async def test_qualification_validation():
    """Testa a validação de critérios de qualificação"""
    
    print("\n=== TESTE DE VALIDAÇÃO DE QUALIFICAÇÃO ===\n")
    
    # Criar lead não qualificado
    test_phone = f"5511{str(uuid4().int)[:9]}"
    print(f"📱 Criando lead NÃO qualificado: {test_phone}")
    
    lead = await lead_repository.create(LeadCreate(
        phone_number=test_phone,
        name="Maria Teste Não Qualificada",
        email="maria.teste@example.com"
    ))
    
    # Dados que NÃO atendem aos critérios
    await lead_repository.update(lead.id, LeadUpdate(
        bill_value=3000.00,  # Abaixo de R$ 4.000 ❌
        is_decision_maker=False,  # Não é decisor ❌
        has_solar_system=True,  # Já tem sistema ❌
        wants_new_solar_system=False,  # Não quer novo ❌
        has_active_contract=True,  # Tem contrato vigente ❌
        qualification_status="NOT_QUALIFIED"
    ))
    
    # Tentar agendar reunião (deve falhar)
    print("\n📅 Tentando agendar reunião para lead não qualificado...")
    
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow.weekday() >= 5:
        tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))
    
    result = await schedule_solar_meeting(
        lead_phone=test_phone,
        date=tomorrow.strftime("%d/%m/%Y"),
        time="10:00"
    )
    
    print(f"\nResultado esperado: FALHA")
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result.get('mensagem', 'N/A')}")
    
    if 'erros_qualificacao' in result:
        print("\n❌ Erros de qualificação detectados:")
        for erro in result['erros_qualificacao']:
            print(f"  • {erro}")
    
    # Limpar
    await lead_repository.delete(lead.id)
    
    print("\n✅ Teste de validação concluído!")


if __name__ == "__main__":
    print("🚀 Iniciando testes de integração Google Calendar enriquecida...")
    
    # Executar testes
    asyncio.run(test_enriched_calendar_integration())
    asyncio.run(test_qualification_validation())
    
    print("\n🎉 Todos os testes concluídos!")