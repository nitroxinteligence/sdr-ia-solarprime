#!/usr/bin/env python3
"""
Script de Teste para Google Calendar Integration
Valida conexão, autenticação e operações básicas
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar configurações e cliente
from app.config import Settings
from app.integrations.google_calendar import GoogleCalendarClient
from app.teams.agents.calendar import CalendarAgent
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

class GoogleCalendarTester:
    """Classe para testar integração com Google Calendar"""
    
    def __init__(self):
        self.settings = Settings()
        self.calendar_client = None
        self.test_event_id = None
        
    def test_configurations(self):
        """Testa se as configurações estão carregadas corretamente"""
        logger.info("=" * 60)
        logger.info("🔧 TESTE 1: Verificando Configurações")
        logger.info("=" * 60)
        
        configs = {
            "enable_calendar_agent": self.settings.enable_calendar_agent,
            "enable_calendar_integration": self.settings.enable_calendar_integration,
            "enable_sdr_team": self.settings.enable_sdr_team,
            "google_service_account_email": self.settings.google_service_account_email,
            "google_project_id": self.settings.google_project_id,
            "google_calendar_id": self.settings.google_calendar_id,
            "google_calendar_enabled": not self.settings.disable_google_calendar,  # Verifica se está habilitado
        }
        
        all_ok = True
        for key, value in configs.items():
            if key == "google_calendar_enabled":
                # Para o calendário estar habilitado, disable_google_calendar deve ser False
                if value:
                    logger.success(f"✅ Google Calendar está HABILITADO")
                else:
                    logger.error(f"❌ Google Calendar está DESABILITADO")
                    all_ok = False
            elif value:
                logger.success(f"✅ {key}: {value if not key.startswith('google_private') else '***'}")
            else:
                logger.error(f"❌ {key}: NÃO CONFIGURADO")
                all_ok = False
        
        if all_ok:
            logger.success("✅ Todas as configurações estão OK!")
        else:
            logger.error("❌ Algumas configurações estão faltando")
        
        return all_ok
    
    def test_authentication(self):
        """Testa autenticação com Google Calendar"""
        logger.info("\n" + "=" * 60)
        logger.info("🔐 TESTE 2: Autenticação Google Calendar")
        logger.info("=" * 60)
        
        try:
            self.calendar_client = GoogleCalendarClient()
            
            if self.calendar_client.service:
                logger.success("✅ Autenticação bem-sucedida!")
                logger.info(f"📧 Service Account: {self.calendar_client.credentials.service_account_email}")
                logger.info(f"📅 Calendar ID: {self.calendar_client.calendar_id}")
                return True
            else:
                logger.error("❌ Falha na autenticação")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            return False
    
    async def test_list_events(self):
        """Testa listagem de eventos"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 TESTE 3: Listando Eventos")
        logger.info("=" * 60)
        
        if not self.calendar_client:
            logger.error("❌ Cliente não autenticado")
            return False
        
        try:
            # Listar eventos dos próximos 7 dias
            events = await self.calendar_client.list_events(
                time_min=datetime.now(),
                time_max=datetime.now() + timedelta(days=7),
                max_results=10
            )
            
            if events:
                logger.success(f"✅ {len(events)} eventos encontrados:")
                for event in events[:3]:  # Mostrar apenas os 3 primeiros
                    logger.info(f"  📅 {event.get('title', 'Sem título')}")
                    if event.get('start'):
                        start = event['start'].get('dateTime', event['start'].get('date', ''))
                        logger.info(f"     🕐 {start}")
            else:
                logger.info("📭 Nenhum evento encontrado nos próximos 7 dias")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar eventos: {e}")
            return False
    
    async def test_create_event(self):
        """Testa criação de evento"""
        logger.info("\n" + "=" * 60)
        logger.info("➕ TESTE 4: Criando Evento de Teste")
        logger.info("=" * 60)
        
        if not self.calendar_client:
            logger.error("❌ Cliente não autenticado")
            return False
        
        try:
            # Criar evento de teste para amanhã às 14h
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=30)
            
            logger.info(f"📅 Criando evento para {start_time.strftime('%d/%m/%Y às %H:%M')}")
            
            result = await self.calendar_client.create_event(
                title="[TESTE] Reunião SDR IA - Solar Prime",
                start_time=start_time,
                end_time=end_time,
                description="Evento de teste criado pelo sistema SDR IA",
                location="Online - Google Meet",
                # Removido attendees - Service Account não pode convidar sem Domain-Wide Delegation
                reminder_minutes=15,
                conference_data=False  # Temporariamente desabilitado - Service Account não pode criar Meet sem Domain-Wide Delegation
            )
            
            if result and result.get('google_event_id'):
                self.test_event_id = result['google_event_id']
                logger.success(f"✅ Evento criado com sucesso!")
                logger.info(f"   🆔 ID: {self.test_event_id}")
                logger.info(f"   🔗 Link: {result.get('html_link', 'N/A')}")
                if result.get('hangout_link'):
                    logger.info(f"   📹 Meet: {result['hangout_link']}")
                return True
            else:
                logger.error("❌ Falha ao criar evento")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar evento: {e}")
            return False
    
    async def test_check_availability(self):
        """Testa verificação de disponibilidade"""
        logger.info("\n" + "=" * 60)
        logger.info("🔍 TESTE 5: Verificando Disponibilidade")
        logger.info("=" * 60)
        
        if not self.calendar_client:
            logger.error("❌ Cliente não autenticado")
            return False
        
        try:
            # Verificar disponibilidade para amanhã às 15h
            tomorrow = datetime.now() + timedelta(days=1)
            check_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
            end_time = check_time + timedelta(minutes=30)
            
            logger.info(f"🕐 Verificando disponibilidade para {check_time.strftime('%d/%m/%Y às %H:%M')}")
            
            available = await self.calendar_client.check_availability(
                start_time=check_time,
                end_time=end_time
            )
            
            if available is True:
                logger.success("✅ Horário disponível!")
            elif isinstance(available, dict) and not available.get('available'):
                logger.warning("⚠️ Horário ocupado")
                conflicts = available.get('conflicts', [])
                for conflict in conflicts:
                    logger.info(f"   ⛔ Conflito: {conflict.get('start')} - {conflict.get('end')}")
            else:
                logger.info(f"📊 Resultado: {available}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar disponibilidade: {e}")
            return False
    
    async def test_delete_event(self):
        """Testa exclusão de evento"""
        logger.info("\n" + "=" * 60)
        logger.info("🗑️ TESTE 6: Deletando Evento de Teste")
        logger.info("=" * 60)
        
        if not self.calendar_client or not self.test_event_id:
            logger.warning("⚠️ Nenhum evento de teste para deletar")
            return True
        
        try:
            logger.info(f"🗑️ Deletando evento {self.test_event_id}")
            
            success = await self.calendar_client.delete_event(
                event_id=self.test_event_id,
                send_notifications=False
            )
            
            if success:
                logger.success("✅ Evento deletado com sucesso!")
                self.test_event_id = None
                return True
            else:
                logger.error("❌ Falha ao deletar evento")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao deletar evento: {e}")
            return False
    
    async def test_calendar_agent(self):
        """Testa o CalendarAgent"""
        logger.info("\n" + "=" * 60)
        logger.info("🤖 TESTE 7: CalendarAgent")
        logger.info("=" * 60)
        
        if not self.settings.enable_calendar_agent:
            logger.warning("⚠️ CalendarAgent está desabilitado")
            return False
        
        try:
            # Importar dependências do agente
            from agno.models.google import Gemini
            from agno.storage.postgres import PostgresStorage
            
            # Criar modelo e storage
            model = Gemini(
                id="gemini-2.5-pro",
                api_key=self.settings.google_api_key
            )
            
            storage = PostgresStorage(
                db_url=self.settings.supabase_db_url,
                table_name="agent_sessions"  # Adicionar table_name obrigatório
            )
            
            # Criar CalendarAgent
            logger.info("🤖 Inicializando CalendarAgent...")
            try:
                calendar_agent = CalendarAgent(
                    model=model,
                    storage=storage
                )
            except Exception as agent_err:
                # Se falhar, tentar sem storage
                logger.warning(f"⚠️ Erro com storage, tentando sem persistência: {agent_err}")
                calendar_agent = CalendarAgent(
                    model=model,
                    storage=None  # Tentar sem storage
                )
            
            logger.success("✅ CalendarAgent inicializado com sucesso!")
            logger.info(f"   📋 Tools disponíveis: {len(calendar_agent.tools)}")
            
            # Testar check_availability
            logger.info("🔍 Testando tool check_availability...")
            result = await calendar_agent.check_availability(
                date="05/08/2025",
                time="14:00",
                duration_minutes=30
            )
            
            if result:
                logger.success(f"✅ Tool funcionando: Disponível = {result.get('available')}")
            
            return True
            
        except ImportError as e:
            logger.error(f"❌ Erro de importação: {e}")
            logger.info("💡 Instale as dependências: pip install agno")
            return False
        except Exception as e:
            logger.error(f"❌ Erro no CalendarAgent: {e}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        logger.info("🚀 INICIANDO TESTES DO GOOGLE CALENDAR")
        logger.info("=" * 60)
        
        results = {}
        
        # Teste 1: Configurações
        results['configs'] = self.test_configurations()
        
        # Teste 2: Autenticação
        results['auth'] = self.test_authentication()
        
        if results['auth']:
            # Teste 3: Listar eventos
            results['list'] = await self.test_list_events()
            
            # Teste 4: Criar evento
            results['create'] = await self.test_create_event()
            
            # Teste 5: Verificar disponibilidade
            results['availability'] = await self.test_check_availability()
            
            # Teste 6: Deletar evento
            results['delete'] = await self.test_delete_event()
            
            # Teste 7: CalendarAgent
            results['agent'] = await self.test_calendar_agent()
        
        # Resumo dos resultados
        logger.info("\n" + "=" * 60)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("=" * 60)
        
        test_names = {
            'configs': 'Configurações',
            'auth': 'Autenticação',
            'list': 'Listar Eventos',
            'create': 'Criar Evento',
            'availability': 'Verificar Disponibilidade',
            'delete': 'Deletar Evento',
            'agent': 'CalendarAgent'
        }
        
        all_passed = True
        for key, name in test_names.items():
            if key in results:
                if results[key]:
                    logger.success(f"✅ {name}: PASSOU")
                else:
                    logger.error(f"❌ {name}: FALHOU")
                    all_passed = False
        
        logger.info("=" * 60)
        if all_passed:
            logger.success("🎉 TODOS OS TESTES PASSARAM!")
        else:
            logger.warning("⚠️ Alguns testes falharam. Verifique os logs acima.")
        
        return all_passed

async def main():
    """Função principal"""
    tester = GoogleCalendarTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())