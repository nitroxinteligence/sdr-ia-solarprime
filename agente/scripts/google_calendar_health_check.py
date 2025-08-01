#!/usr/bin/env python3
"""
Google Calendar Health Check Script
Validates Google Calendar service connectivity and credentials
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agente.core.config import (
    GOOGLE_SERVICE_ACCOUNT_EMAIL,
    GOOGLE_PRIVATE_KEY,
    GOOGLE_PROJECT_ID,
    GOOGLE_CALENDAR_ID,
    DISABLE_GOOGLE_CALENDAR
)
from agente.services.calendar_service import get_calendar_service
from agente.core.logger import get_logger

logger = get_logger(__name__)

class GoogleCalendarHealthChecker:
    """Comprehensive health checker for Google Calendar integration"""
    
    def __init__(self):
        self.service = None
        self.test_results = {}
    
    async def run_all_checks(self) -> dict:
        """Run all health checks and return results"""
        print("🔍 Iniciando verificação de saúde do Google Calendar...")
        print("=" * 60)
        
        # Environment validation
        await self._check_environment()
        
        # Service initialization
        await self._check_service_initialization()
        
        if self.service and self.service.is_available():
            # API connectivity
            await self._check_api_connectivity()
            
            # Calendar permissions
            await self._check_calendar_permissions()
            
            # Rate limiting functionality
            await self._check_rate_limiting()
            
            # Basic operations
            await self._check_basic_operations()
        
        # Generate report
        return self._generate_report()
    
    async def _check_environment(self):
        """Check environment variables"""
        print("1. Verificando variáveis de ambiente...")
        
        required_vars = {
            'GOOGLE_PROJECT_ID': GOOGLE_PROJECT_ID,
            'GOOGLE_PRIVATE_KEY': GOOGLE_PRIVATE_KEY,
            'GOOGLE_SERVICE_ACCOUNT_EMAIL': GOOGLE_SERVICE_ACCOUNT_EMAIL,
            'GOOGLE_CALENDAR_ID': GOOGLE_CALENDAR_ID
        }
        
        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)
                print(f"   ❌ {var_name}: AUSENTE")
            else:
                # Mask sensitive values
                if 'KEY' in var_name:
                    display_value = f"{var_value[:20]}..." if len(var_value) > 20 else var_value
                else:
                    display_value = var_value
                print(f"   ✅ {var_name}: {display_value}")
        
        if DISABLE_GOOGLE_CALENDAR:
            print("   ⚠️  DISABLE_GOOGLE_CALENDAR está habilitado")
            self.test_results['environment'] = {
                'status': 'warning',
                'message': 'Google Calendar está desabilitado'
            }
        elif missing_vars:
            self.test_results['environment'] = {
                'status': 'failed',
                'message': f'Variáveis ausentes: {", ".join(missing_vars)}'
            }
        else:
            self.test_results['environment'] = {
                'status': 'passed',
                'message': 'Todas as variáveis de ambiente estão configuradas'
            }
    
    async def _check_service_initialization(self):
        """Check service initialization"""
        print("\n2. Verificando inicialização do serviço...")
        
        try:
            self.service = get_calendar_service()
            
            if self.service.service is None:
                print("   ❌ Serviço não foi inicializado")
                self.test_results['initialization'] = {
                    'status': 'failed',
                    'message': 'Falha na inicialização do serviço'
                }
            else:
                print("   ✅ Serviço inicializado com sucesso")
                print(f"   📅 Calendar ID: {self.service.calendar_id}")
                print(f"   🌍 Timezone: {self.service.timezone}")
                self.test_results['initialization'] = {
                    'status': 'passed',
                    'message': 'Serviço inicializado corretamente'
                }
        
        except Exception as e:
            print(f"   ❌ Erro na inicialização: {str(e)}")
            self.test_results['initialization'] = {
                'status': 'failed',
                'message': f'Erro na inicialização: {str(e)}'
            }
    
    async def _check_api_connectivity(self):
        """Check API connectivity"""
        print("\n3. Verificando conectividade com a API...")
        
        try:
            # Test basic API call - get calendar metadata
            calendar_info = await self.service._rate_limited_execute(
                self.service.service.calendars().get,
                calendarId=self.service.calendar_id
            )
            
            print("   ✅ Conectividade com API confirmada")
            print(f"   📊 Calendar: {calendar_info.get('summary', 'N/A')}")
            print(f"   🆔 ID: {calendar_info.get('id', 'N/A')}")
            
            self.test_results['connectivity'] = {
                'status': 'passed',
                'message': 'Conectividade com API funcionando',
                'calendar_info': calendar_info
            }
        
        except Exception as e:
            print(f"   ❌ Falha na conectividade: {str(e)}")
            self.test_results['connectivity'] = {
                'status': 'failed',
                'message': f'Falha na conectividade: {str(e)}'
            }
    
    async def _check_calendar_permissions(self):
        """Check calendar permissions"""
        print("\n4. Verificando permissões do calendário...")
        
        try:
            # Test reading events
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            
            events = await self.service.get_calendar_events(now, tomorrow)
            print(f"   ✅ Permissão de leitura: OK ({len(events)} eventos encontrados)")
            
            # Check ACL (Access Control List)
            try:
                acl_rules = await self.service._rate_limited_execute(
                    self.service.service.acl().list,
                    calendarId=self.service.calendar_id
                )
                print(f"   ✅ Permissões ACL: {len(acl_rules.get('items', []))} regras")
            except Exception as e:
                print(f"   ⚠️  Não foi possível verificar ACL: {str(e)}")
            
            self.test_results['permissions'] = {
                'status': 'passed',
                'message': 'Permissões básicas funcionando',
                'events_count': len(events)
            }
        
        except Exception as e:
            print(f"   ❌ Falha nas permissões: {str(e)}")
            self.test_results['permissions'] = {
                'status': 'failed',
                'message': f'Falha nas permissões: {str(e)}'
            }
    
    async def _check_rate_limiting(self):
        """Check rate limiting functionality"""
        print("\n5. Verificando rate limiting...")
        
        try:
            # Test rate limiting by making multiple rapid requests
            start_time = datetime.now()
            
            # Make 5 rapid requests
            tasks = []
            for i in range(5):
                tasks.append(
                    self.service._rate_limited_execute(
                        self.service.service.calendars().get,
                        calendarId=self.service.calendar_id
                    )
                )
            
            await asyncio.gather(*tasks)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"   ✅ Rate limiting funcionando (5 requests em {elapsed:.2f}s)")
            
            # Check rate limiting data structures
            with self.service._rate_limit_lock:
                request_count = len(self.service._request_times)
                print(f"   📊 Requests rastreados: {request_count}")
            
            self.test_results['rate_limiting'] = {
                'status': 'passed',
                'message': f'Rate limiting funcionando ({elapsed:.2f}s para 5 requests)',
                'elapsed_time': elapsed
            }
        
        except Exception as e:
            print(f"   ❌ Falha no rate limiting: {str(e)}")
            self.test_results['rate_limiting'] = {
                'status': 'failed',
                'message': f'Falha no rate limiting: {str(e)}'
            }
    
    async def _check_basic_operations(self):
        """Check basic calendar operations"""
        print("\n6. Verificando operações básicas...")
        
        try:
            # Test availability check
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            
            available_slots = await self.service.check_availability(now, tomorrow)
            print(f"   ✅ Verificação de disponibilidade: {len(available_slots)} slots encontrados")
            
            # Test creating a test event (and immediately deleting it)
            test_event_time = now + timedelta(hours=1)
            test_event = await self.service.create_meeting(
                title="[TESTE] Health Check Event",
                description="Evento de teste criado pelo health check",
                start_time=test_event_time,
                duration_minutes=30
            )
            
            if test_event:
                print("   ✅ Criação de evento: OK")
                
                # Test event deletion
                deleted = await self.service.cancel_event(test_event.id, send_notifications=False)
                if deleted:
                    print("   ✅ Exclusão de evento: OK")
                else:
                    print("   ⚠️  Exclusão de evento: Falhou")
            else:
                print("   ❌ Criação de evento: Falhou")
            
            self.test_results['basic_operations'] = {
                'status': 'passed',
                'message': 'Operações básicas funcionando',
                'available_slots': len(available_slots),
                'event_created': test_event is not None
            }
        
        except Exception as e:
            print(f"   ❌ Falha nas operações básicas: {str(e)}")
            self.test_results['basic_operations'] = {
                'status': 'failed',
                'message': f'Falha nas operações básicas: {str(e)}'
            }
    
    def _generate_report(self) -> dict:
        """Generate final health check report"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DE SAÚDE")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'passed')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'failed')
        warning_tests = sum(1 for result in self.test_results.values() if result['status'] == 'warning')
        total_tests = len(self.test_results)
        
        print(f"📊 Testes executados: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Falharam: {failed_tests}")
        print(f"⚠️  Avisos: {warning_tests}")
        
        if failed_tests == 0 and warning_tests == 0:
            print("\n🎉 STATUS GERAL: SAUDÁVEL")
            overall_status = 'healthy'
        elif failed_tests == 0:
            print("\n⚠️  STATUS GERAL: SAUDÁVEL COM AVISOS")
            overall_status = 'healthy_with_warnings'
        else:
            print("\n🚨 STATUS GERAL: PROBLEMAS DETECTADOS")
            overall_status = 'unhealthy'
        
        print("\n📝 Detalhes dos testes:")
        for test_name, result in self.test_results.items():
            status_icon = {'passed': '✅', 'failed': '❌', 'warning': '⚠️'}[result['status']]
            print(f"   {status_icon} {test_name}: {result['message']}")
        
        return {
            'overall_status': overall_status,
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'detailed_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Main health check function"""
    try:
        checker = GoogleCalendarHealthChecker()
        results = await checker.run_all_checks()
        
        # Exit with appropriate code
        if results['overall_status'] == 'healthy':
            sys.exit(0)
        elif results['overall_status'] == 'healthy_with_warnings':
            sys.exit(1)
        else:
            sys.exit(2)
    
    except Exception as e:
        print(f"\n🚨 ERRO CRÍTICO NO HEALTH CHECK: {str(e)}")
        logger.error(f"Health check failed with critical error: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())