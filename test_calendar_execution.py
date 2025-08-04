#!/usr/bin/env python3
"""
Script de teste para verificar se o CalendarAgent está executando agendamentos reais
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.teams.sdr_team import SDRTeam
from app.utils.logger import emoji_logger
from loguru import logger

async def test_calendar_execution():
    """Testa a execução real de agendamento"""
    
    print("=" * 60)
    print("🧪 TESTE DE EXECUÇÃO REAL DO CALENDARAGENT")
    print("=" * 60)
    
    # Criar instância do SDR Team
    sdr_team = SDRTeam()
    
    # Inicializar
    await sdr_team.initialize()
    
    # Simular contexto enriquecido com recomendação do CalendarAgent
    test_context = {
        "phone": "11999887766",
        "message": "Quero agendar uma reunião amanhã às 14h",
        "lead_data": {
            "id": "test_lead_123",
            "name": "João Teste",
            "email": "joao.teste@example.com",
            "phone_number": "11999887766"
        },
        "conversation_id": "test_conv_123",
        "context_analysis": {
            "primary_context": "scheduling_request",
            "decision_stage": "scheduling",
            "lead_engagement_level": "high",
            "urgency_level": "medium",
            "qualification_signals": {
                "bill_value": 500,
                "has_decision_power": True,
                "timeline_mentioned": True
            },
            "recommended_action": "schedule_meeting"
        },
        "emotional_triggers": {
            "dominant_emotion": "interested",
            "frustration_indicators": False,
            "excitement_indicators": True
        },
        "recommended_agent": "CalendarAgent",  # IMPORTANTE: Isso ativa a execução real
        "reasoning": "Cliente solicitou agendamento explicitamente"
    }
    
    print("\n📋 Contexto de teste:")
    print(f"  - Mensagem: {test_context['message']}")
    print(f"  - Lead: {test_context['lead_data']['name']}")
    print(f"  - Email: {test_context['lead_data']['email']}")
    print(f"  - Agente recomendado: {test_context['recommended_agent']}")
    
    print("\n🚀 Executando processo_message_with_context...")
    print("-" * 40)
    
    try:
        # Executar processamento com contexto
        response = await sdr_team.process_message_with_context(test_context)
        
        print("\n✅ RESPOSTA DO SISTEMA:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        # Verificar se a resposta indica sucesso
        if "Event ID:" in response or "ID do Evento:" in response:
            print("\n🎉 SUCESSO! Agendamento foi EXECUTADO (não simulado)")
            print("   - A resposta contém ID do evento real do Google Calendar")
        elif "confirmada" in response.lower():
            print("\n⚠️ POSSÍVEL SUCESSO - Verificar logs para confirmar execução real")
        else:
            print("\n❌ FALHA - Resposta não indica agendamento real")
            
    except Exception as e:
        print(f"\n❌ ERRO durante execução: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICAÇÃO DOS LOGS:")
    print("  Procure por estas mensagens nos logs:")
    print("  - '🗓️ ATIVANDO CalendarAgent para EXECUÇÃO REAL'")
    print("  - '✅ CalendarAgent disponível - EXECUTANDO AGENDAMENTO REAL'")
    print("  - '🚀 CRIANDO EVENTO REAL:'")
    print("  - '✅ REUNIÃO AGENDADA COM SUCESSO! Event ID:'")
    print("=" * 60)

if __name__ == "__main__":
    print("\n🔧 Iniciando teste de execução real do CalendarAgent...")
    asyncio.run(test_calendar_execution())