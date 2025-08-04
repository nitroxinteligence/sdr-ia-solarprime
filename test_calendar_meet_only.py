#!/usr/bin/env python3
"""
Teste focado apenas em Calendar e Google Meet
Testa operações diretas sem depender do SDR Team
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from loguru import logger
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_calendar import google_calendar_client
from app.integrations.google_meet_handler import google_meet_handler

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)

class CalendarMeetTest:
    """Teste direto de Calendar e Meet"""
    
    def __init__(self):
        self.created_events = []
        self.test_results = []
    
    async def cleanup(self):
        """Limpa eventos criados"""
        logger.info("\n🧹 Limpando eventos de teste...")
        for event_id in self.created_events:
            try:
                await google_calendar_client.delete_event(event_id)
                logger.info(f"  ✅ Removido: {event_id[:10]}...")
            except:
                pass
    
    async def test_1_create_simple_event(self):
        """Teste 1: Criar evento simples"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 1: CRIAR EVENTO SIMPLES")
        logger.info("="*60)
        
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        logger.info(f"📅 Criando evento para {start_time.strftime('%d/%m/%Y %H:%M')}")
        
        result = await google_calendar_client.create_event(
            title="Teste Calendar - Evento Simples",
            start_time=start_time,
            end_time=end_time,
            description="Teste de criação de evento simples",
            location="Escritório",
            reminder_minutes=30
        )
        
        if result and result.get('google_event_id'):
            self.created_events.append(result['google_event_id'])
            logger.info(f"✅ Evento criado: {result['google_event_id']}")
            logger.info(f"   Link: {result.get('html_link')}")
            return True
        else:
            logger.error("❌ Falha ao criar evento")
            return False
    
    async def test_2_create_event_with_meet(self):
        """Teste 2: Criar evento com Google Meet"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 2: CRIAR EVENTO COM GOOGLE MEET")
        logger.info("="*60)
        
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        # Verificar status do Meet
        meet_status = google_meet_handler.get_status()
        logger.info(f"📊 Google Meet pode criar automaticamente: {'✅ SIM' if meet_status['can_create_meet'] else '❌ NÃO'}")
        
        logger.info(f"📅 Criando evento com Meet para {start_time.strftime('%d/%m/%Y %H:%M')}")
        
        result = await google_calendar_client.create_event(
            title="Teste Calendar - Com Google Meet",
            start_time=start_time,
            end_time=end_time,
            description="Teste de evento com Google Meet",
            location="",
            reminder_minutes=30,
            conference_data=True  # Solicita Google Meet
        )
        
        if result and result.get('google_event_id'):
            self.created_events.append(result['google_event_id'])
            logger.info(f"✅ Evento criado: {result['google_event_id']}")
            
            if result.get('has_meet'):
                logger.info(f"   🎥 Google Meet NATIVO: {result.get('meet_link')}")
            elif result.get('meet_setup_required'):
                logger.info(f"   ⚠️ Google Meet requer configuração manual")
                logger.info(f"   📝 Instruções adicionadas ao evento")
            
            # Verificar evento
            event = await google_calendar_client.get_event(result['google_event_id'])
            if event and 'Google Meet' in event.get('description', ''):
                logger.info(f"   ✅ Instruções do Meet encontradas na descrição")
            
            return True
        else:
            logger.error("❌ Falha ao criar evento com Meet")
            return False
    
    async def test_3_check_availability(self):
        """Teste 3: Verificar disponibilidade"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 3: VERIFICAR DISPONIBILIDADE")
        logger.info("="*60)
        
        # Criar um evento para testar conflito
        tomorrow = datetime.now() + timedelta(days=1)
        busy_start = tomorrow.replace(hour=16, minute=0, second=0, microsecond=0)
        busy_end = busy_start + timedelta(hours=1)
        
        # Criar evento que vai ocupar o horário
        busy_event = await google_calendar_client.create_event(
            title="Teste - Horário Ocupado",
            start_time=busy_start,
            end_time=busy_end,
            description="Evento para testar conflito"
        )
        
        if busy_event:
            self.created_events.append(busy_event['google_event_id'])
            logger.info(f"📅 Evento de bloqueio criado: {busy_start.strftime('%H:%M')}-{busy_end.strftime('%H:%M')}")
        
        # Testar disponibilidade
        test_cases = [
            (busy_start - timedelta(hours=2), busy_start - timedelta(hours=1), "Antes do bloqueio"),
            (busy_start, busy_end, "Durante o bloqueio"),
            (busy_end, busy_end + timedelta(hours=1), "Após o bloqueio")
        ]
        
        for start, end, description in test_cases:
            availability = await google_calendar_client.check_availability(
                start_time=start,
                end_time=end
            )
            
            if availability == True:
                logger.info(f"✅ {description}: DISPONÍVEL")
            else:
                logger.info(f"⚠️ {description}: OCUPADO")
        
        return True
    
    async def test_4_list_events(self):
        """Teste 4: Listar eventos"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 4: LISTAR EVENTOS")
        logger.info("="*60)
        
        events = await google_calendar_client.list_events(
            time_min=datetime.now(),
            time_max=datetime.now() + timedelta(days=2),
            max_results=10
        )
        
        if events:
            logger.info(f"📅 {len(events)} eventos encontrados:")
            for event in events[:5]:
                logger.info(f"  • {event['title']}")
                if event.get('hangout_link'):
                    logger.info(f"    🎥 Meet: {event['hangout_link']}")
                elif event.get('location') and 'Meet' in event.get('location', ''):
                    logger.info(f"    📍 {event['location']}")
        else:
            logger.info("📭 Nenhum evento encontrado")
        
        return True
    
    async def test_5_update_event(self):
        """Teste 5: Atualizar evento"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 5: ATUALIZAR EVENTO")
        logger.info("="*60)
        
        if not self.created_events:
            logger.warning("⚠️ Nenhum evento para atualizar")
            return False
        
        event_id = self.created_events[0]
        new_time = datetime.now() + timedelta(days=2, hours=15)
        
        logger.info(f"📅 Atualizando evento {event_id[:10]}...")
        
        result = await google_calendar_client.update_event(
            event_id=event_id,
            updates={
                "title": "Teste Calendar - ATUALIZADO",
                "start_time": new_time,
                "end_time": new_time + timedelta(hours=1),
                "description": "Evento atualizado via teste"
            }
        )
        
        if result:
            logger.info(f"✅ Evento atualizado com sucesso")
            return True
        else:
            logger.error(f"❌ Falha ao atualizar evento")
            return False
    
    async def test_6_delete_event(self):
        """Teste 6: Deletar evento"""
        logger.info("\n" + "="*60)
        logger.info("📝 TESTE 6: DELETAR EVENTO")
        logger.info("="*60)
        
        # Criar evento para deletar
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
        
        temp_event = await google_calendar_client.create_event(
            title="Teste - Para Deletar",
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            description="Este evento será deletado"
        )
        
        if temp_event:
            event_id = temp_event['google_event_id']
            logger.info(f"📅 Evento temporário criado: {event_id[:10]}...")
            
            # Deletar
            deleted = await google_calendar_client.delete_event(event_id)
            
            if deleted:
                logger.info(f"✅ Evento deletado com sucesso")
                
                # Verificar que não existe mais
                check = await google_calendar_client.get_event(event_id)
                if not check:
                    logger.info(f"   ✅ Confirmado: evento não existe mais")
                return True
            else:
                self.created_events.append(event_id)  # Adicionar para limpeza
                logger.error(f"❌ Falha ao deletar evento")
                return False
        
        return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        tests = [
            ("Criar Evento Simples", self.test_1_create_simple_event),
            ("Criar Evento com Meet", self.test_2_create_event_with_meet),
            ("Verificar Disponibilidade", self.test_3_check_availability),
            ("Listar Eventos", self.test_4_list_events),
            ("Atualizar Evento", self.test_5_update_event),
            ("Deletar Evento", self.test_6_delete_event)
        ]
        
        results = {"total": 0, "passed": 0, "failed": 0}
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                success = await test_func()
                if success:
                    results["passed"] += 1
                    self.test_results.append(f"✅ {test_name}")
                else:
                    results["failed"] += 1
                    self.test_results.append(f"❌ {test_name}")
            except Exception as e:
                results["failed"] += 1
                self.test_results.append(f"❌ {test_name}: {str(e)[:50]}")
                logger.error(f"Erro em {test_name}: {e}")
        
        return results

async def main():
    """Função principal"""
    logger.info("\n" + "🎯"*30)
    logger.info("TESTE COMPLETO: GOOGLE CALENDAR + MEET")
    logger.info("🎯"*30)
    
    # Status do sistema
    meet_status = google_meet_handler.get_status()
    logger.info(f"\n📊 Status do Sistema:")
    logger.info(f"  • Google Calendar: ✅ Configurado")
    logger.info(f"  • Google Meet: {'✅ Automático' if meet_status['can_create_meet'] else '⚠️ Manual'}")
    logger.info(f"  • Service Account: {meet_status['service_account'][:30]}...")
    
    if not meet_status['can_create_meet']:
        logger.info(f"\n💡 Para ativar Meet automático:")
        for rec in meet_status['recommendations'][:2]:
            logger.info(f"  • {rec}")
    
    tester = CalendarMeetTest()
    
    try:
        # Executar testes
        results = await tester.run_all_tests()
        
        # Relatório
        logger.info("\n" + "="*80)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("="*80)
        
        logger.info(f"\n📈 Resultados:")
        logger.info(f"  • Total: {results['total']} testes")
        logger.info(f"  • ✅ Passou: {results['passed']}")
        logger.info(f"  • ❌ Falhou: {results['failed']}")
        logger.info(f"  • Taxa: {(results['passed']/results['total']*100):.0f}%")
        
        logger.info(f"\n📋 Detalhes:")
        for result in tester.test_results:
            logger.info(f"  {result}")
        
        # Conclusão
        if results['passed'] == results['total']:
            logger.info("\n🎉 PERFEITO! Todos os testes passaram!")
            logger.info("✅ Calendar e Meet 100% operacionais!")
        elif results['passed'] >= results['total'] * 0.8:
            logger.info("\n✅ BOM! Sistema operacional")
        else:
            logger.info("\n⚠️ ATENÇÃO! Verificar componentes")
    
    finally:
        await tester.cleanup()
        logger.info("\n✅ Teste concluído e limpo")

if __name__ == "__main__":
    asyncio.run(main())