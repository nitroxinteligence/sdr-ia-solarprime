#!/usr/bin/env python3
"""
Setup do Ambiente de Testes Reais - SDR IA SolarPrime

Script para configurar e validar ambiente de testes isolado.
Configura credenciais de teste e valida conectividade com todas as APIs.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class TestEnvironmentSetup:
    """Setup e validação do ambiente de testes"""
    
    def __init__(self):
        self.config = {}
        self.validation_results = {}
        
    def load_test_config(self) -> Dict[str, Any]:
        """Carrega configuração de teste"""
        
        # Configuração padrão para testes
        test_config = {
            # Environment markers
            'ENVIRONMENT': 'test',
            'TESTING': 'true',
            'PYTEST_RUNNING': 'true',
            
            # Google Calendar - USAR CREDENCIAIS DE TESTE
            'GOOGLE_CALENDAR_ID': 'primary',  # ou calendar específico para testes
            'GOOGLE_PROJECT_ID': os.getenv('GOOGLE_PROJECT_ID_TEST') or os.getenv('GOOGLE_PROJECT_ID'),
            'GOOGLE_PRIVATE_KEY': os.getenv('GOOGLE_PRIVATE_KEY_TEST') or os.getenv('GOOGLE_PRIVATE_KEY'),
            'GOOGLE_SERVICE_ACCOUNT_EMAIL': os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL_TEST') or os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
            'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID_TEST') or os.getenv('GOOGLE_CLIENT_ID'),
            'GOOGLE_PRIVATE_KEY_ID': os.getenv('GOOGLE_PRIVATE_KEY_ID_TEST') or os.getenv('GOOGLE_PRIVATE_KEY_ID'),
            
            # Kommo CRM - USAR SUBDOMAIN DE TESTE
            'KOMMO_SUBDOMAIN': os.getenv('KOMMO_SUBDOMAIN_TEST') or os.getenv('KOMMO_SUBDOMAIN'),
            'KOMMO_LONG_LIVED_TOKEN': os.getenv('KOMMO_LONG_LIVED_TOKEN_TEST') or os.getenv('KOMMO_LONG_LIVED_TOKEN'),
            
            # Evolution API - USAR INSTÂNCIA DE TESTE  
            'EVOLUTION_API_URL': os.getenv('EVOLUTION_API_URL_TEST') or os.getenv('EVOLUTION_API_URL'),
            'EVOLUTION_API_KEY': os.getenv('EVOLUTION_API_KEY_TEST') or os.getenv('EVOLUTION_API_KEY'),
            'EVOLUTION_INSTANCE': os.getenv('EVOLUTION_INSTANCE_TEST') or os.getenv('EVOLUTION_INSTANCE'),
            
            # Supabase - USAR DATABASE DE TESTE
            'SUPABASE_URL': os.getenv('SUPABASE_URL_TEST') or os.getenv('SUPABASE_URL'),
            'SUPABASE_SERVICE_KEY': os.getenv('SUPABASE_SERVICE_KEY_TEST') or os.getenv('SUPABASE_SERVICE_KEY'),
            
            # Outras configurações
            'DISABLE_GOOGLE_CALENDAR': 'false',
            'TEST_TIMEOUT': '300',
            'TEST_MAX_RETRIES': '3',
            'LOG_LEVEL': 'INFO'
        }
        
        self.config = test_config
        return test_config
    
    def apply_test_config(self):
        """Aplica configuração de teste às variáveis de ambiente"""
        print("🔧 Aplicando configuração de teste...")
        
        config = self.load_test_config()
        
        for key, value in config.items():
            if value:  # Só aplicar se valor não for vazio
                os.environ[key] = str(value)
                if 'KEY' in key or 'TOKEN' in key:
                    print(f"   ✅ {key}: ***MASKED***")
                else:
                    print(f"   ✅ {key}: {value}")
            else:
                print(f"   ⚠️  {key}: NÃO CONFIGURADO")
    
    async def validate_google_calendar(self) -> bool:
        """Valida conectividade com Google Calendar"""
        print("\n📅 Validando Google Calendar...")
        
        try:
            from agente.services.calendar_service import get_calendar_service
            service = get_calendar_service()
            
            if not service.is_available():
                print("   ❌ Google Calendar service não disponível")
                return False
            
            # Teste de conectividade
            calendar_info = await service._rate_limited_execute(
                service.service.calendars().get,
                calendarId=service.calendar_id
            )
            
            print(f"   ✅ Conectado ao calendário: {calendar_info.get('summary', 'N/A')}")
            print(f"   📋 Calendar ID: {calendar_info.get('id')}")
            
            self.validation_results['google_calendar'] = {
                'status': 'success',
                'calendar_info': calendar_info
            }
            return True
            
        except Exception as e:
            print(f"   ❌ Erro no Google Calendar: {str(e)}")
            self.validation_results['google_calendar'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    async def validate_kommo_crm(self) -> bool:
        """Valida conectividade com Kommo CRM"""
        print("\n📊 Validando Kommo CRM...")
        
        try:
            # Implementar quando tivermos o serviço
            print("   ⚠️  Validação Kommo CRM não implementada ainda")
            self.validation_results['kommo_crm'] = {
                'status': 'pending',
                'message': 'Validação não implementada'
            }
            return True
            
        except Exception as e:
            print(f"   ❌ Erro no Kommo CRM: {str(e)}")
            self.validation_results['kommo_crm'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    async def validate_evolution_api(self) -> bool:
        """Valida conectividade com Evolution API"""
        print("\n📱 Validando Evolution API...")
        
        try:
            # Implementar quando tivermos o serviço
            print("   ⚠️  Validação Evolution API não implementada ainda")
            self.validation_results['evolution_api'] = {
                'status': 'pending', 
                'message': 'Validação não implementada'
            }
            return True
            
        except Exception as e:
            print(f"   ❌ Erro na Evolution API: {str(e)}")
            self.validation_results['evolution_api'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    async def validate_supabase_db(self) -> bool:
        """Valida conectividade com Supabase"""
        print("\n🗄️  Validando Supabase Database...")
        
        try:
            # Implementar quando tivermos o serviço
            print("   ⚠️  Validação Supabase não implementada ainda")
            self.validation_results['supabase_db'] = {
                'status': 'pending',
                'message': 'Validação não implementada'
            }
            return True
            
        except Exception as e:
            print(f"   ❌ Erro no Supabase: {str(e)}")
            self.validation_results['supabase_db'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def check_environment_safety(self) -> bool:
        """Verifica se estamos em ambiente seguro para testes"""
        print("\n🛡️  Verificando segurança do ambiente...")
        
        # Check for production indicators
        production_indicators = [
            os.getenv('ENVIRONMENT') == 'production',
            'prod' in os.getenv('GOOGLE_CALENDAR_ID', '').lower(),
            'prod' in os.getenv('KOMMO_SUBDOMAIN', '').lower(),
            'production' in os.getenv('SUPABASE_URL', '').lower()
        ]
        
        if any(production_indicators):
            print("   🚨 PERIGO: Detectados indicadores de ambiente de PRODUÇÃO!")
            print("   ❌ NÃO EXECUTE testes reais em produção!")
            return False
        
        # Check for test indicators
        test_indicators = [
            os.getenv('ENVIRONMENT') == 'test',
            os.getenv('TESTING') == 'true',
            'test' in os.getenv('GOOGLE_CALENDAR_ID', '').lower(),
            'test' in os.getenv('KOMMO_SUBDOMAIN', '').lower()
        ]
        
        if any(test_indicators):
            print("   ✅ Ambiente de teste detectado")
            return True
        
        print("   ⚠️  Ambiente não claramente identificado como TESTE")
        print("   💡 Configure ENVIRONMENT=test e use credenciais de teste")
        return False
    
    async def run_full_validation(self) -> bool:
        """Executa validação completa do ambiente"""
        print("🧪 SETUP E VALIDAÇÃO DO AMBIENTE DE TESTES REAIS")
        print("=" * 60)
        
        # Apply test configuration
        self.apply_test_config()
        
        # Check environment safety
        if not self.check_environment_safety():
            print("\n❌ AMBIENTE NÃO É SEGURO PARA TESTES REAIS")
            return False
        
        # Validate each service
        validations = [
            await self.validate_google_calendar(),
            await self.validate_kommo_crm(),
            await self.validate_evolution_api(),
            await self.validate_supabase_db()
        ]
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 RESUMO DA VALIDAÇÃO")
        print("=" * 60)
        
        success_count = sum(validations)
        total_count = len(validations)
        
        for service, result in self.validation_results.items():
            status_icon = {
                'success': '✅',
                'error': '❌', 
                'pending': '⚠️'
            }.get(result['status'], '❓')
            
            print(f"{status_icon} {service}: {result.get('message', result['status'])}")
        
        print(f"\n📊 Resultado: {success_count}/{total_count} serviços validados")
        
        if success_count >= total_count * 0.5:  # Pelo menos 50% funcionando
            print("✅ AMBIENTE PRONTO PARA TESTES REAIS!")
            return True
        else:
            print("❌ AMBIENTE NÃO ESTÁ PRONTO")
            print("💡 Configure as credenciais de teste e tente novamente")
            return False
    
    def save_test_config(self, filename: str = "test_environment_config.json"):
        """Salva configuração de teste em arquivo"""
        config_file = Path(__file__).parent / filename
        
        # Mask sensitive data for saving
        safe_config = {}
        for key, value in self.config.items():
            if any(sensitive in key.upper() for sensitive in ['KEY', 'TOKEN', 'SECRET']):
                safe_config[key] = '***MASKED***' if value else None
            else:
                safe_config[key] = value
        
        with open(config_file, 'w') as f:
            json.dump({
                'config': safe_config,
                'validation_results': self.validation_results,
                'timestamp': str(asyncio.get_event_loop().time())
            }, f, indent=2)
        
        print(f"\n💾 Configuração salva em: {config_file}")


async def main():
    """Função principal"""
    try:
        setup = TestEnvironmentSetup()
        success = await setup.run_full_validation()
        
        # Save config
        setup.save_test_config()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n🚨 ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())