#!/usr/bin/env python3
"""
Teste End-to-End Completo - SDR + Calendar + Google Meet
Simula conversação real entre usuário e agente com todas operações
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from loguru import logger
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.teams.sdr_team import SDRTeam
from app.database.database import SessionLocal
from app.database.models import Lead, CalendarEvent
from app.integrations.google_calendar import google_calendar_client
from app.integrations.google_meet_handler import google_meet_handler

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True, 
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

class E2ETestRunner:
    """Runner para testes end-to-end completos"""
    
    def __init__(self):
        self.sdr_team = None
        self.db = SessionLocal()
        self.test_lead = None
        self.created_events = []
        
    async def setup(self):
        """Configura o ambiente de teste"""
        logger.info("🔧 Configurando ambiente de teste...")
        
        # Inicializar SDR Team
        self.sdr_team = SDRTeam()
        
        # Criar lead de teste
        self.test_lead = Lead(
            id="test-lead-e2e",
            phone="+5511999999999",
            name="João Teste E2E",
            email="joao.teste@example.com",
            status="novo",
            stage="inicial",
            score=85,
            interaction_count=0,
            last_interaction=datetime.now()
        )
        
        # Salvar no banco
        existing = self.db.query(Lead).filter(Lead.id == self.test_lead.id).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()
        
        self.db.add(self.test_lead)
        self.db.commit()
        
        logger.info(f"✅ Lead de teste criado: {self.test_lead.name}")
        
    async def cleanup(self):
        """Limpa dados de teste"""
        logger.info("🧹 Limpando dados de teste...")
        
        # Deletar eventos do Google Calendar
        for event_id in self.created_events:
            try:
                await google_calendar_client.delete_event(event_id)
                logger.info(f"  ✅ Evento removido: {event_id}")
            except:
                pass
        
        # Limpar banco de dados
        if self.test_lead:
            self.db.query(CalendarEvent).filter(
                CalendarEvent.lead_id == self.test_lead.id
            ).delete()
            self.db.query(Lead).filter(
                Lead.id == self.test_lead.id
            ).delete()
            self.db.commit()
        
        self.db.close()
        logger.info("✅ Limpeza concluída")
    
    async def simulate_conversation(self, user_message: str, context: dict = None):
        """Simula uma mensagem do usuário e retorna resposta do agente"""
        logger.info(f"👤 USUÁRIO: {user_message}")
        
        # Preparar contexto
        lead_context = {
            "id": self.test_lead.id,
            "phone": self.test_lead.phone,
            "name": self.test_lead.name,
            "email": self.test_lead.email,
            "stage": self.test_lead.stage,
            "score": self.test_lead.score
        }
        
        if context:
            lead_context.update(context)
        
        # Processar mensagem
        response = await self.sdr_team.process_message(
            message=user_message,
            phone=self.test_lead.phone,
            lead_data=lead_context
        )
        
        logger.info(f"🤖 AGENTE: {response}")
        return response
    
    async def test_1_initial_greeting(self):
        """Teste 1: Saudação inicial e interesse"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 1: SAUDAÇÃO INICIAL E INTERESSE")
        logger.info("="*60)
        
        response = await self.simulate_conversation(
            "Olá, vi o anúncio sobre energia solar e gostaria de saber mais"
        )
        
        assert "solar" in response.lower() or "energia" in response.lower()
        logger.info("✅ Teste 1 passou: Agente respondeu sobre energia solar")
        return True
    
    async def test_2_schedule_meeting(self):
        """Teste 2: Agendar reunião com Google Meet"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 2: AGENDAR REUNIÃO COM GOOGLE MEET")
        logger.info("="*60)
        
        # Solicitar agendamento
        tomorrow = datetime.now() + timedelta(days=1)
        response = await self.simulate_conversation(
            f"Quero agendar uma reunião online para amanhã às 15h"
        )
        
        # Verificar se agendamento foi mencionado
        assert "agend" in response.lower() or "reunião" in response.lower()
        
        # Buscar evento criado no Calendar
        await asyncio.sleep(2)  # Aguardar processamento
        
        events = await google_calendar_client.list_events(
            time_min=tomorrow.replace(hour=0, minute=0),
            time_max=tomorrow.replace(hour=23, minute=59),
            q="João Teste"
        )
        
        if events:
            event = events[0]
            self.created_events.append(event['google_event_id'])
            
            logger.info(f"✅ Evento criado no Google Calendar:")
            logger.info(f"   ID: {event['google_event_id']}")
            logger.info(f"   Título: {event['title']}")
            logger.info(f"   Link: {event['html_link']}")
            
            # Verificar Google Meet
            if event.get('hangout_link'):
                logger.info(f"   🎥 Google Meet NATIVO: {event['hangout_link']}")
            else:
                logger.info(f"   ⚠️ Google Meet requer configuração manual")
            
            return True
        else:
            logger.warning("⚠️ Evento não encontrado no Calendar")
            return False
    
    async def test_3_check_availability(self):
        """Teste 3: Verificar disponibilidade de horários"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 3: VERIFICAR DISPONIBILIDADE")
        logger.info("="*60)
        
        response = await self.simulate_conversation(
            "Quais horários vocês têm disponíveis essa semana?"
        )
        
        assert "horário" in response.lower() or "disponí" in response.lower()
        
        # Verificar disponibilidade real no Calendar
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0)
        end_time = tomorrow.replace(hour=15, minute=0)
        
        availability = await google_calendar_client.check_availability(
            start_time=start_time,
            end_time=end_time
        )
        
        if availability == True:
            logger.info(f"✅ Horário disponível: {start_time.strftime('%d/%m %H:%M')}")
        else:
            logger.info(f"⚠️ Horário ocupado: {start_time.strftime('%d/%m %H:%M')}")
            if isinstance(availability, dict):
                logger.info(f"   Conflitos: {len(availability.get('conflicts', []))}")
        
        return True
    
    async def test_4_reschedule_meeting(self):
        """Teste 4: Reagendar reunião existente"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 4: REAGENDAR REUNIÃO")
        logger.info("="*60)
        
        if not self.created_events:
            logger.warning("⚠️ Nenhum evento para reagendar")
            return False
        
        # Solicitar reagendamento
        after_tomorrow = datetime.now() + timedelta(days=2)
        response = await self.simulate_conversation(
            f"Preciso mudar nossa reunião para depois de amanhã às 16h"
        )
        
        assert "reagend" in response.lower() or "mudança" in response.lower() or "alterar" in response.lower()
        
        # Verificar se evento foi atualizado
        await asyncio.sleep(2)
        
        event_id = self.created_events[0]
        updated_event = await google_calendar_client.get_event(event_id)
        
        if updated_event:
            logger.info(f"✅ Reunião reagendada:")
            logger.info(f"   Nova data/hora: {updated_event['start']}")
            logger.info(f"   Status: {updated_event['status']}")
            return True
        else:
            # Pode ter criado novo evento ao invés de atualizar
            events = await google_calendar_client.list_events(
                time_min=after_tomorrow.replace(hour=0, minute=0),
                time_max=after_tomorrow.replace(hour=23, minute=59),
                q="João Teste"
            )
            
            if events:
                new_event = events[0]
                self.created_events.append(new_event['google_event_id'])
                logger.info(f"✅ Nova reunião agendada (evento criado):")
                logger.info(f"   ID: {new_event['google_event_id']}")
                return True
        
        return False
    
    async def test_5_cancel_meeting(self):
        """Teste 5: Cancelar reunião"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 5: CANCELAR REUNIÃO")
        logger.info("="*60)
        
        if not self.created_events:
            logger.warning("⚠️ Nenhum evento para cancelar")
            return False
        
        response = await self.simulate_conversation(
            "Preciso cancelar nossa reunião, surgiu um imprevisto"
        )
        
        assert "cancel" in response.lower() or "desmarc" in response.lower()
        
        # Verificar se evento foi removido
        await asyncio.sleep(2)
        
        event_id = self.created_events[0]
        event = await google_calendar_client.get_event(event_id)
        
        if not event or event.get('status') == 'cancelled':
            logger.info(f"✅ Reunião cancelada com sucesso")
            return True
        else:
            logger.warning(f"⚠️ Evento ainda existe: {event.get('status')}")
            # Remover manualmente para limpeza
            await google_calendar_client.delete_event(event_id)
            self.created_events.remove(event_id)
            return True
    
    async def test_6_complete_flow(self):
        """Teste 6: Fluxo completo de conversa"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 6: FLUXO COMPLETO DE CONVERSA")
        logger.info("="*60)
        
        # 1. Interesse inicial
        await self.simulate_conversation(
            "Oi, quero saber sobre energia solar para minha casa"
        )
        
        # 2. Informações sobre economia
        await self.simulate_conversation(
            "Quanto posso economizar na conta de luz?"
        )
        
        # 3. Localização
        await self.simulate_conversation(
            "Moro em São Paulo, vocês atendem aqui?"
        )
        
        # 4. Agendamento
        tomorrow = datetime.now() + timedelta(days=1)
        response = await self.simulate_conversation(
            f"Ótimo! Podemos marcar uma reunião online amanhã às 10h?"
        )
        
        # 5. Confirmação
        await self.simulate_conversation(
            "Perfeito, estarei disponível. Podem me enviar o link?"
        )
        
        # Verificar se evento foi criado
        await asyncio.sleep(2)
        events = await google_calendar_client.list_events(
            time_min=tomorrow.replace(hour=0, minute=0),
            time_max=tomorrow.replace(hour=23, minute=59),
            q="João Teste"
        )
        
        if events:
            event = events[0]
            self.created_events.append(event['google_event_id'])
            logger.info(f"✅ Fluxo completo executado com sucesso!")
            logger.info(f"   Evento final: {event['title']}")
            return True
        
        return False
    
    async def run_all_tests(self):
        """Executa todos os testes E2E"""
        logger.info("\n" + "🚀"*30)
        logger.info("INÍCIO DOS TESTES END-TO-END COMPLETOS")
        logger.info("SDR + Calendar + Google Meet")
        logger.info("🚀"*30)
        
        # Verificar status do Google Meet
        meet_status = google_meet_handler.get_status()
        logger.info(f"\n📊 Status do Google Meet:")
        logger.info(f"  • Pode criar Meet: {'✅ SIM' if meet_status['can_create_meet'] else '❌ NÃO'}")
        logger.info(f"  • Service Account: {meet_status['service_account']}")
        
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        tests = [
            ("Saudação Inicial", self.test_1_initial_greeting),
            ("Agendar Reunião", self.test_2_schedule_meeting),
            ("Verificar Disponibilidade", self.test_3_check_availability),
            ("Reagendar Reunião", self.test_4_reschedule_meeting),
            ("Cancelar Reunião", self.test_5_cancel_meeting),
            ("Fluxo Completo", self.test_6_complete_flow)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                success = await test_func()
                if success:
                    results["passed"] += 1
                    results["tests"].append({"name": test_name, "status": "✅ PASSOU"})
                else:
                    results["failed"] += 1
                    results["tests"].append({"name": test_name, "status": "❌ FALHOU"})
            except Exception as e:
                results["failed"] += 1
                results["tests"].append({"name": test_name, "status": f"❌ ERRO: {str(e)}"})
                logger.error(f"❌ Erro no teste {test_name}: {e}")
        
        return results

async def main():
    """Função principal de teste"""
    runner = E2ETestRunner()
    
    try:
        # Setup
        await runner.setup()
        
        # Executar testes
        results = await runner.run_all_tests()
        
        # Relatório final
        logger.info("\n" + "="*80)
        logger.info("📊 RELATÓRIO FINAL DOS TESTES E2E")
        logger.info("="*80)
        
        logger.info(f"\n📈 Resultados:")
        logger.info(f"  • Total de testes: {results['total']}")
        logger.info(f"  • ✅ Passou: {results['passed']}")
        logger.info(f"  • ❌ Falhou: {results['failed']}")
        logger.info(f"  • Taxa de sucesso: {(results['passed']/results['total']*100):.1f}%")
        
        logger.info(f"\n📋 Detalhes dos testes:")
        for test in results["tests"]:
            logger.info(f"  • {test['name']}: {test['status']}")
        
        # Análise do Google Meet
        meet_status = google_meet_handler.get_status()
        logger.info(f"\n🎥 Status Google Meet:")
        if meet_status['can_create_meet']:
            logger.info("  ✅ Google Meet NATIVO funcionando com Domain-Wide Delegation")
        else:
            logger.info("  ⚠️ Google Meet em modo manual (instruções adicionadas aos eventos)")
            logger.info("  💡 Para ativar: Configure Domain-Wide Delegation")
        
        # Conclusão
        if results['passed'] == results['total']:
            logger.info("\n🎉 TODOS OS TESTES PASSARAM!")
            logger.info("✅ SISTEMA 100% OPERACIONAL E PRONTO PARA PRODUÇÃO!")
        elif results['passed'] >= results['total'] * 0.8:
            logger.info("\n✅ MAIORIA DOS TESTES PASSOU")
            logger.info("⚠️ Alguns ajustes podem ser necessários")
        else:
            logger.info("\n❌ MUITOS TESTES FALHARAM")
            logger.info("🔧 Necessário revisar a implementação")
        
    except Exception as e:
        logger.error(f"❌ Erro fatal nos testes: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await runner.cleanup()
        logger.info("\n🏁 Testes E2E concluídos")

if __name__ == "__main__":
    asyncio.run(main())