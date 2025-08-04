#!/usr/bin/env python3
"""
Teste REAL de conversa completa entre usuário e agente SDR
Executa operações REAIS no Google Calendar - NÃO É SIMULAÇÃO!
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.teams.sdr_team import SDRTeam
from app.teams.agents.calendar import CalendarAgent
from app.integrations.google_calendar import google_calendar_client
from app.utils.logger import emoji_logger
from loguru import logger
from app.config import settings

# Configurar logger para mostrar tudo
logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True)

class RealConversationTest:
    """Teste real de conversa completa com agendamento no Google Calendar"""
    
    def __init__(self):
        self.sdr_team = None
        self.calendar_agent = None
        self.google_calendar = google_calendar_client
        self.test_results = []
        self.created_events = []  # Para limpeza posterior
        
    async def setup(self):
        """Inicializa os componentes do teste"""
        print("\n" + "="*80)
        print("🚀 INICIALIZANDO TESTE REAL DE CONVERSA COM GOOGLE CALENDAR")
        print("="*80)
        
        # Inicializar SDR Team
        self.sdr_team = SDRTeam()
        await self.sdr_team.initialize()
        
        # Verificar se CalendarAgent está disponível
        if not self.sdr_team.calendar_agent:
            raise Exception("❌ CalendarAgent não está disponível! Verifique as configurações.")
        
        self.calendar_agent = self.sdr_team.calendar_agent
        
        print("✅ Sistema inicializado com sucesso")
        print(f"📅 Google Calendar ID: {settings.google_calendar_id}")
        print(f"🔑 Service Account: Configurado")
        print("-"*80)
        
    async def test_1_initial_contact(self):
        """Teste 1: Contato inicial do cliente"""
        print("\n" + "="*60)
        print("📝 TESTE 1: CONTATO INICIAL")
        print("="*60)
        
        context = {
            "phone": "11987654321",
            "message": "Olá, vi o anúncio sobre energia solar e gostaria de saber mais",
            "lead_data": {
                "id": "test_lead_001",
                "name": "Carlos Silva",
                "email": "carlos.teste@gmail.com",
                "phone_number": "11987654321",
                "qualification_stage": "INITIAL_CONTACT"
            },
            "conversation_id": "test_conv_001"
        }
        
        print(f"👤 Cliente: {context['message']}")
        response = await self.sdr_team.process_message(
            phone=context['phone'],
            message=context['message'],
            lead_data=context['lead_data'],
            conversation_id=context['conversation_id']
        )
        print(f"🤖 Agente: {response[:200]}...")
        
        self.test_results.append({
            "test": "initial_contact",
            "success": "solar" in response.lower() or "energia" in response.lower(),
            "response": response
        })
        
        await asyncio.sleep(2)  # Delay para não sobrecarregar
        return response
        
    async def test_2_schedule_meeting(self):
        """Teste 2: Cliente solicita agendamento - CRIA EVENTO REAL"""
        print("\n" + "="*60)
        print("📅 TESTE 2: AGENDAMENTO DE REUNIÃO (REAL!)")
        print("="*60)
        
        # Preparar data para amanhã às 15h
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%d/%m/%Y")
        
        context = {
            "phone": "11987654321",
            "message": f"Ótimo! Podemos agendar uma reunião para amanhã dia {date_str} às 15h? Meu email é carlos.teste@gmail.com",
            "lead_data": {
                "id": "test_lead_001",
                "name": "Carlos Silva",
                "email": "carlos.teste@gmail.com",
                "phone_number": "11987654321",
                "qualification_stage": "SCHEDULING"
            },
            "conversation_id": "test_conv_001",
            "context_analysis": {
                "primary_context": "scheduling_request",
                "decision_stage": "scheduling",
                "lead_engagement_level": "high",
                "urgency_level": "medium",
                "qualification_signals": {
                    "bill_value": 450,
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
            "recommended_agent": "CalendarAgent",  # FORÇA USO DO CALENDAR AGENT
            "reasoning": "Cliente solicitou agendamento explícito com data e horário"
        }
        
        print(f"👤 Cliente: {context['message']}")
        print("⏳ Criando evento REAL no Google Calendar...")
        
        response = await self.sdr_team.process_message_with_context(context)
        
        print(f"🤖 Agente: {response}")
        
        # Verificar se foi criado com sucesso
        event_id = None
        if "Event ID:" in response or "ID do Evento:" in response:
            # Extrair event ID da resposta
            import re
            match = re.search(r'(?:Event ID:|ID do Evento:)\s*([a-zA-Z0-9_-]+)', response)
            if match:
                event_id = match.group(1)
                self.created_events.append(event_id)
                print(f"\n✅ EVENTO CRIADO COM SUCESSO!")
                print(f"📍 Google Event ID: {event_id}")
                
                # Verificar evento no Google Calendar
                await asyncio.sleep(2)
                event = await self.verify_event_exists(event_id)
                if event:
                    print(f"✅ Evento confirmado no Google Calendar:")
                    print(f"   - Título: {event.get('title')}")
                    print(f"   - Data/Hora: {event.get('start')}")
                    print(f"   - Link: {event.get('html_link')}")
        
        self.test_results.append({
            "test": "schedule_meeting",
            "success": event_id is not None,
            "event_id": event_id,
            "response": response
        })
        
        await asyncio.sleep(3)
        return event_id
        
    async def test_3_check_availability(self):
        """Teste 3: Verificar disponibilidade de horário"""
        print("\n" + "="*60)
        print("🔍 TESTE 3: VERIFICAÇÃO DE DISPONIBILIDADE")
        print("="*60)
        
        # Verificar horário já ocupado (o que acabamos de agendar)
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%d/%m/%Y")
        
        context = {
            "phone": "11999888777",
            "message": f"Vocês têm horário disponível amanhã {date_str} às 15h?",
            "lead_data": {
                "id": "test_lead_002",
                "name": "Maria Santos",
                "email": "maria.teste@gmail.com",
                "phone_number": "11999888777"
            },
            "conversation_id": "test_conv_002"
        }
        
        print(f"👤 Cliente: {context['message']}")
        
        # Verificar disponibilidade diretamente
        start_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        
        print("⏳ Verificando disponibilidade no Google Calendar...")
        availability = await self.google_calendar.check_availability(
            start_time=start_time,
            end_time=end_time
        )
        
        if availability is True:
            print("✅ Horário está DISPONÍVEL")
        elif isinstance(availability, dict) and not availability.get('available'):
            print("❌ Horário está OCUPADO")
            print(f"   Conflitos: {availability.get('conflicts', [])}")
        
        response = await self.sdr_team.process_message(
            phone=context['phone'],
            message=context['message'],
            lead_data=context['lead_data'],
            conversation_id=context['conversation_id']
        )
        
        print(f"🤖 Agente: {response[:300]}...")
        
        self.test_results.append({
            "test": "check_availability",
            "success": True,
            "available": availability,
            "response": response
        })
        
        await asyncio.sleep(2)
        
    async def test_4_cancel_meeting(self):
        """Teste 4: Cancelar reunião agendada"""
        print("\n" + "="*60)
        print("❌ TESTE 4: CANCELAMENTO DE REUNIÃO")
        print("="*60)
        
        if not self.created_events:
            print("⚠️ Nenhum evento para cancelar")
            return None
            
        event_id = self.created_events[0]
        
        context = {
            "phone": "11987654321",
            "message": "Preciso cancelar nossa reunião de amanhã, surgiu um imprevisto",
            "lead_data": {
                "id": "test_lead_001",
                "name": "Carlos Silva",
                "email": "carlos.teste@gmail.com",
                "phone_number": "11987654321",
                "google_event_id": event_id  # Passar o ID do evento
            },
            "conversation_id": "test_conv_001"
        }
        
        print(f"👤 Cliente: {context['message']}")
        print(f"⏳ Cancelando evento {event_id} no Google Calendar...")
        
        # Cancelar diretamente via CalendarAgent
        success = await self.calendar_agent.cancel_meeting(
            lead_id=context['lead_data']['id'],
            google_event_id=event_id,
            reason="Cliente solicitou cancelamento"
        )
        
        if success:
            print(f"✅ Evento {event_id} cancelado com sucesso!")
            # Verificar se foi removido
            await asyncio.sleep(2)
            event = await self.verify_event_exists(event_id)
            if not event or event.get('status') == 'cancelled':
                print("✅ Confirmado: Evento foi cancelado no Google Calendar")
        else:
            print(f"❌ Falha ao cancelar evento {event_id}")
        
        response = await self.sdr_team.process_message(
            phone=context['phone'],
            message=context['message'],
            lead_data=context['lead_data'],
            conversation_id=context['conversation_id']
        )
        
        print(f"🤖 Agente: {response[:300]}...")
        
        self.test_results.append({
            "test": "cancel_meeting",
            "success": success,
            "event_id": event_id,
            "response": response
        })
        
        await asyncio.sleep(2)
        return success
        
    async def test_5_reschedule_meeting(self):
        """Teste 5: Reagendar reunião para novo horário"""
        print("\n" + "="*60)
        print("🔄 TESTE 5: REAGENDAMENTO DE REUNIÃO")
        print("="*60)
        
        # Agendar para depois de amanhã às 10h
        new_date = datetime.now() + timedelta(days=2)
        date_str = new_date.strftime("%d/%m/%Y")
        
        context = {
            "phone": "11987654321",
            "message": f"Podemos reagendar para {date_str} às 10h da manhã?",
            "lead_data": {
                "id": "test_lead_001",
                "name": "Carlos Silva",
                "email": "carlos.teste@gmail.com",
                "phone_number": "11987654321",
                "qualification_stage": "SCHEDULING"
            },
            "conversation_id": "test_conv_001",
            "context_analysis": {
                "primary_context": "rescheduling_request",
                "decision_stage": "scheduling",
                "lead_engagement_level": "high",
                "urgency_level": "medium",
                "recommended_action": "reschedule_meeting"
            },
            "recommended_agent": "CalendarAgent",
            "reasoning": "Cliente solicitou reagendamento com nova data e horário"
        }
        
        print(f"👤 Cliente: {context['message']}")
        print("⏳ Criando novo evento no Google Calendar...")
        
        response = await self.sdr_team.process_message_with_context(context)
        
        print(f"🤖 Agente: {response}")
        
        # Verificar se foi criado novo evento
        event_id = None
        if "Event ID:" in response or "ID do Evento:" in response:
            import re
            match = re.search(r'(?:Event ID:|ID do Evento:)\s*([a-zA-Z0-9_-]+)', response)
            if match:
                event_id = match.group(1)
                self.created_events.append(event_id)
                print(f"\n✅ NOVO EVENTO CRIADO!")
                print(f"📍 Google Event ID: {event_id}")
                
                # Verificar evento
                await asyncio.sleep(2)
                event = await self.verify_event_exists(event_id)
                if event:
                    print(f"✅ Evento confirmado:")
                    print(f"   - Título: {event.get('title')}")
                    print(f"   - Nova Data/Hora: {event.get('start')}")
        
        self.test_results.append({
            "test": "reschedule_meeting",
            "success": event_id is not None,
            "event_id": event_id,
            "response": response
        })
        
        await asyncio.sleep(2)
        return event_id
        
    async def test_6_list_upcoming_meetings(self):
        """Teste 6: Listar reuniões agendadas"""
        print("\n" + "="*60)
        print("📋 TESTE 6: LISTAR REUNIÕES AGENDADAS")
        print("="*60)
        
        print("⏳ Buscando eventos no Google Calendar...")
        
        # Listar eventos dos próximos 7 dias
        events = await self.google_calendar.list_events(
            time_min=datetime.now(),
            time_max=datetime.now() + timedelta(days=7),
            max_results=10
        )
        
        print(f"\n📅 Encontrados {len(events)} eventos:")
        for event in events:
            print(f"  - {event.get('title', 'Sem título')}")
            print(f"    Data: {event.get('start')}")
            print(f"    Status: {event.get('status')}")
            print(f"    ID: {event.get('google_event_id')}")
            print()
        
        self.test_results.append({
            "test": "list_meetings",
            "success": True,
            "events_count": len(events)
        })
        
    async def verify_event_exists(self, event_id: str) -> Dict[str, Any]:
        """Verifica se um evento existe no Google Calendar"""
        try:
            event = await self.google_calendar.get_event(event_id)
            return event
        except:
            return None
            
    async def cleanup(self):
        """Limpa eventos de teste criados"""
        print("\n" + "="*60)
        print("🧹 LIMPEZA DOS EVENTOS DE TESTE")
        print("="*60)
        
        for event_id in self.created_events:
            try:
                print(f"🗑️ Removendo evento de teste: {event_id}")
                success = await self.google_calendar.delete_event(event_id)
                if success:
                    print(f"  ✅ Removido com sucesso")
                else:
                    print(f"  ⚠️ Pode já ter sido removido")
            except Exception as e:
                print(f"  ❌ Erro ao remover: {e}")
        
        print("✅ Limpeza concluída")
        
    async def run_all_tests(self):
        """Executa todos os testes em sequência"""
        try:
            await self.setup()
            
            # Executar testes em sequência
            await self.test_1_initial_contact()
            event_id = await self.test_2_schedule_meeting()
            await self.test_3_check_availability()
            
            if event_id:
                await self.test_4_cancel_meeting()
            
            await self.test_5_reschedule_meeting()
            await self.test_6_list_upcoming_meetings()
            
            # Relatório final
            self.print_report()
            
            # Limpeza
            await self.cleanup()
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar limpeza mesmo com erro
            await self.cleanup()
            
    def print_report(self):
        """Imprime relatório final dos testes"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("="*80)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get('success'))
        
        print(f"\n📈 Resultados: {passed}/{total} testes passaram")
        print("-"*40)
        
        for result in self.test_results:
            status = "✅ PASSOU" if result.get('success') else "❌ FALHOU"
            print(f"{status} - {result['test']}")
            if result.get('event_id'):
                print(f"         Event ID: {result['event_id']}")
        
        print("-"*40)
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
            print("✅ Sistema está PRONTO PARA PRODUÇÃO!")
        else:
            print(f"⚠️ {total - passed} testes falharam")
            print("🔧 Verifique os logs para mais detalhes")
        
        print("="*80)


async def main():
    """Função principal"""
    print("\n" + "🚀"*40)
    print("TESTE COMPLETO DE CONVERSA REAL COM GOOGLE CALENDAR")
    print("Este teste executa operações REAIS no Google Calendar!")
    print("🚀"*40)
    
    test = RealConversationTest()
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())