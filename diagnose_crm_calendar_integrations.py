#!/usr/bin/env python3
"""
DIAGNÓSTICO CRÍTICO - Integração KommoCRM e Google Calendar
Verifica conectividade, configurações e funcionamento das tools
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

# CRÍTICO: Carregar .env explicitamente
from dotenv import load_dotenv
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Arquivo .env carregado: {env_file}")
else:
    print(f"❌ Arquivo .env não encontrado: {env_file}")

# Configurar environment
os.environ.setdefault('ENVIRONMENT', 'production')

from agente.services.kommo_service import get_kommo_service, KommoAPIError
from agente.services.calendar_service import get_calendar_service
from agente.core.config import (
    KOMMO_BASE_URL,
    KOMMO_LONG_LIVED_TOKEN,
    KOMMO_SUBDOMAIN,
    GOOGLE_SERVICE_ACCOUNT_EMAIL,
    GOOGLE_PRIVATE_KEY,
    GOOGLE_CALENDAR_ID,
    DISABLE_GOOGLE_CALENDAR
)


class IntegrationDiagnostic:
    """Diagnóstico completo das integrações CRM e Calendar"""
    
    def __init__(self):
        self.results = {
            'kommo': {'connected': False, 'errors': [], 'details': {}},
            'calendar': {'connected': False, 'errors': [], 'details': {}},
            'tools': {'kommo_tools_ok': False, 'calendar_tools_ok': False}
        }
    
    async def diagnose_kommo_integration(self):
        """Diagnóstica integração KommoCRM"""
        print("\n🔍 DIAGNÓSTICO KOMMO CRM")
        print("=" * 50)
        
        try:
            # Verificar configurações
            print("📋 Verificando configurações...")
            if not KOMMO_BASE_URL:
                self.results['kommo']['errors'].append("KOMMO_BASE_URL não configurada")
            if not KOMMO_LONG_LIVED_TOKEN:
                self.results['kommo']['errors'].append("KOMMO_LONG_LIVED_TOKEN não configurada")
            if not KOMMO_SUBDOMAIN:
                self.results['kommo']['errors'].append("KOMMO_SUBDOMAIN não configurada")
            
            print(f"   - Base URL: {'✅' if KOMMO_BASE_URL else '❌'} {KOMMO_BASE_URL}")
            print(f"   - Token: {'✅' if KOMMO_LONG_LIVED_TOKEN else '❌'} {'*' * 20 if KOMMO_LONG_LIVED_TOKEN else 'MISSING'}")
            print(f"   - Subdomain: {'✅' if KOMMO_SUBDOMAIN else '❌'} {KOMMO_SUBDOMAIN}")
            
            if self.results['kommo']['errors']:
                print(f"❌ Configurações incompletas: {len(self.results['kommo']['errors'])} erros")
                return
            
            # Testar conectividade
            print("\n🌐 Testando conectividade...")
            kommo_service = get_kommo_service()
            
            # Teste 1: Account info
            try:
                account_info = await kommo_service.get_account_info()
                if account_info:
                    self.results['kommo']['details']['account'] = account_info
                    print(f"✅ Conta conectada: {account_info.get('name', 'Unknown')}")
                else:
                    self.results['kommo']['errors'].append("Falha ao obter informações da conta")
                    print("❌ Falha ao conectar com conta")
            except Exception as e:
                self.results['kommo']['errors'].append(f"Erro ao conectar: {str(e)}")
                print(f"❌ Erro de conectividade: {e}")
                return
            
            # Teste 2: Pipelines
            try:
                pipelines = await kommo_service.get_pipelines()
                if pipelines:
                    self.results['kommo']['details']['pipelines'] = len(pipelines)
                    print(f"✅ Pipelines encontrados: {len(pipelines)}")
                    for pipeline in pipelines[:3]:  # Mostrar primeiros 3
                        print(f"   - {pipeline.get('name', 'Unknown')}")
            except Exception as e:
                self.results['kommo']['errors'].append(f"Erro ao buscar pipelines: {str(e)}")
                print(f"❌ Erro pipelines: {e}")
            
            # Teste 3: Custom Fields
            try:
                fields = await kommo_service.get_custom_fields('leads')
                if fields:
                    self.results['kommo']['details']['custom_fields'] = len(fields)
                    print(f"✅ Campos customizados: {len(fields)}")
            except Exception as e:
                self.results['kommo']['errors'].append(f"Erro ao buscar campos: {str(e)}")
                print(f"❌ Erro campos customizados: {e}")
            
            # Teste 4: Criar lead de teste
            try:
                test_lead_data = {
                    'name': f'Teste Diagnóstico {datetime.now().strftime("%H:%M:%S")}',
                    'custom_fields_values': [
                        {'field_id': 'PHONE', 'values': [{'value': '11999999999'}]}
                    ]
                }
                
                created_lead = await kommo_service.create_lead(test_lead_data)
                if created_lead and 'id' in created_lead:
                    lead_id = created_lead['id']
                    print(f"✅ Lead teste criado: ID {lead_id}")
                    
                    # Limpar lead teste
                    try:
                        await kommo_service.delete_lead(lead_id)
                        print(f"✅ Lead teste removido: ID {lead_id}")
                    except:
                        print(f"⚠️  Lead teste não removido: ID {lead_id}")
                    
                    self.results['kommo']['connected'] = True
                    self.results['kommo']['details']['test_lead'] = 'success'
                else:
                    self.results['kommo']['errors'].append("Falha ao criar lead de teste")
                    print("❌ Falha ao criar lead teste")
                    
            except Exception as e:
                self.results['kommo']['errors'].append(f"Erro ao criar lead teste: {str(e)}")
                print(f"❌ Erro lead teste: {e}")
            
        except Exception as e:
            self.results['kommo']['errors'].append(f"Erro geral Kommo: {str(e)}")
            print(f"❌ ERRO GERAL KOMMO: {e}")
    
    async def diagnose_calendar_integration(self):
        """Diagnóstica integração Google Calendar"""
        print("\n📅 DIAGNÓSTICO GOOGLE CALENDAR")
        print("=" * 50)
        
        try:
            # Verificar se está desabilitado
            if DISABLE_GOOGLE_CALENDAR:
                print("⚠️  Google Calendar DESABILITADO via configuração")
                self.results['calendar']['errors'].append("Google Calendar desabilitado")
                return
            
            # Verificar configurações
            print("📋 Verificando configurações...")
            if not GOOGLE_SERVICE_ACCOUNT_EMAIL:
                self.results['calendar']['errors'].append("GOOGLE_SERVICE_ACCOUNT_EMAIL não configurada")
            if not GOOGLE_PRIVATE_KEY:
                self.results['calendar']['errors'].append("GOOGLE_PRIVATE_KEY não configurada")
            if not GOOGLE_CALENDAR_ID:
                self.results['calendar']['errors'].append("GOOGLE_CALENDAR_ID não configurada")
            
            print(f"   - Service Account: {'✅' if GOOGLE_SERVICE_ACCOUNT_EMAIL else '❌'} {GOOGLE_SERVICE_ACCOUNT_EMAIL}")
            print(f"   - Private Key: {'✅' if GOOGLE_PRIVATE_KEY else '❌'} {'*' * 20 if GOOGLE_PRIVATE_KEY else 'MISSING'}")
            print(f"   - Calendar ID: {'✅' if GOOGLE_CALENDAR_ID else '❌'} {GOOGLE_CALENDAR_ID}")
            
            if self.results['calendar']['errors']:
                print(f"❌ Configurações incompletas: {len(self.results['calendar']['errors'])} erros")
                return
            
            # Testar conectividade
            print("\n🌐 Testando conectividade...")
            calendar_service = get_calendar_service()
            
            # Teste 1: Calendar info
            try:
                calendar_info = await calendar_service.get_calendar_info()
                if calendar_info:
                    self.results['calendar']['details']['calendar'] = calendar_info
                    print(f"✅ Calendário conectado: {calendar_info.get('summary', 'Unknown')}")
                else:
                    self.results['calendar']['errors'].append("Falha ao obter informações do calendário")
                    print("❌ Falha ao conectar com calendário")
            except Exception as e:
                self.results['calendar']['errors'].append(f"Erro ao conectar: {str(e)}")
                print(f"❌ Erro de conectividade: {e}")
                return
            
            # Teste 2: Listar eventos próximos
            try:
                now = datetime.now()
                events = await calendar_service.list_events(
                    start_time=now,
                    end_time=now + timedelta(days=7),
                    max_results=5
                )
                if events is not None:
                    self.results['calendar']['details']['events_count'] = len(events)
                    print(f"✅ Eventos próximos: {len(events)}")
                else:
                    print("⚠️  Não foi possível listar eventos")
            except Exception as e:
                self.results['calendar']['errors'].append(f"Erro ao listar eventos: {str(e)}")
                print(f"❌ Erro eventos: {e}")
            
            # Teste 3: Criar evento de teste
            try:
                test_event = {
                    'summary': f'Teste Diagnóstico {datetime.now().strftime("%H:%M:%S")}',
                    'start': {'dateTime': (datetime.now() + timedelta(hours=1)).isoformat()},
                    'end': {'dateTime': (datetime.now() + timedelta(hours=2)).isoformat()},
                    'description': 'Evento de teste criado pelo diagnóstico'
                }
                
                created_event = await calendar_service.create_event(test_event)
                if created_event and 'id' in created_event:
                    event_id = created_event['id']
                    print(f"✅ Evento teste criado: ID {event_id}")
                    
                    # Limpar evento teste
                    try:
                        await calendar_service.delete_event(event_id)
                        print(f"✅ Evento teste removido: ID {event_id}")
                    except:
                        print(f"⚠️  Evento teste não removido: ID {event_id}")
                    
                    self.results['calendar']['connected'] = True
                    self.results['calendar']['details']['test_event'] = 'success'
                else:
                    self.results['calendar']['errors'].append("Falha ao criar evento de teste")
                    print("❌ Falha ao criar evento teste")
                    
            except Exception as e:
                self.results['calendar']['errors'].append(f"Erro ao criar evento teste: {str(e)}")
                print(f"❌ Erro evento teste: {e}")
            
        except Exception as e:
            self.results['calendar']['errors'].append(f"Erro geral Calendar: {str(e)}")
            print(f"❌ ERRO GERAL CALENDAR: {e}")
    
    def diagnose_tools_registration(self):
        """Diagnóstica se as tools estão registradas corretamente"""
        print("\n🔧 DIAGNÓSTICO TOOLS REGISTRATION")
        print("=" * 50)
        
        try:
            # Importar agent e verificar tools
            from agente.core.agent import SDRAgent
            
            # Verificar se podemos criar o agente (sem inicializar completamente)
            print("📋 Verificando registro das tools no AGnO Agent...")
            
            # Verificar imports das tools
            kommo_tools_imported = False
            calendar_tools_imported = False
            
            try:
                from agente.tools.kommo import (
                    search_kommo_lead,
                    create_kommo_lead,
                    update_kommo_lead,
                    update_kommo_stage,
                    add_kommo_note,
                    schedule_kommo_activity
                )
                kommo_tools_imported = True
                print("✅ Tools Kommo importadas com sucesso")
            except Exception as e:
                print(f"❌ Erro importando tools Kommo: {e}")
            
            try:
                from agente.tools.calendar import (
                    check_availability,
                    create_meeting,
                    update_meeting,
                    cancel_meeting,
                    send_calendar_invite
                )
                calendar_tools_imported = True
                print("✅ Tools Calendar importadas com sucesso")
            except Exception as e:
                print(f"❌ Erro importando tools Calendar: {e}")
            
            self.results['tools']['kommo_tools_ok'] = kommo_tools_imported
            self.results['tools']['calendar_tools_ok'] = calendar_tools_imported
            
            # Verificar se agent pode ser inicializado
            try:
                # Só verifica se pode importar, não inicializa (evita API calls)
                agent_class = SDRAgent
                print("✅ Classe SDRAgent pode ser importada")
            except Exception as e:
                print(f"❌ Erro ao importar SDRAgent: {e}")
            
        except Exception as e:
            print(f"❌ ERRO GERAL TOOLS: {e}")
    
    def print_summary(self):
        """Imprime resumo do diagnóstico"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DO DIAGNÓSTICO")
        print("=" * 60)
        
        # Status Kommo
        kommo_status = "✅ CONECTADO" if self.results['kommo']['connected'] else "❌ FALHA"
        kommo_errors = len(self.results['kommo']['errors'])
        print(f"🔍 KOMMO CRM: {kommo_status}")
        if kommo_errors > 0:
            print(f"   └─ Erros: {kommo_errors}")
            for error in self.results['kommo']['errors'][:3]:  # Primeiros 3
                print(f"      • {error}")
        
        # Status Calendar  
        calendar_status = "✅ CONECTADO" if self.results['calendar']['connected'] else "❌ FALHA"
        calendar_errors = len(self.results['calendar']['errors'])
        print(f"📅 GOOGLE CALENDAR: {calendar_status}")
        if calendar_errors > 0:
            print(f"   └─ Erros: {calendar_errors}")
            for error in self.results['calendar']['errors'][:3]:  # Primeiros 3
                print(f"      • {error}")
        
        # Status Tools
        kommo_tools = "✅ OK" if self.results['tools']['kommo_tools_ok'] else "❌ FALHA"
        calendar_tools = "✅ OK" if self.results['tools']['calendar_tools_ok'] else "❌ FALHA"
        print(f"🔧 TOOLS KOMMO: {kommo_tools}")
        print(f"🔧 TOOLS CALENDAR: {calendar_tools}")
        
        # Status Geral
        all_ok = (
            self.results['kommo']['connected'] and 
            self.results['calendar']['connected'] and
            self.results['tools']['kommo_tools_ok'] and
            self.results['tools']['calendar_tools_ok']
        )
        
        print(f"\n🎯 STATUS GERAL: {'✅ TODAS INTEGRAÇÕES OK' if all_ok else '❌ PROBLEMAS DETECTADOS'}")
        
        if not all_ok:
            print("\n📋 PRÓXIMOS PASSOS:")
            if not self.results['kommo']['connected']:
                print("   1. Verificar configurações KOMMO_* no .env")
                print("   2. Validar token Kommo (pode ter expirado)")
            if not self.results['calendar']['connected']:
                print("   3. Verificar configurações GOOGLE_* no .env")
                print("   4. Validar Service Account permissions")
            if not (self.results['tools']['kommo_tools_ok'] and self.results['tools']['calendar_tools_ok']):
                print("   5. Verificar imports das tools")
                print("   6. Verificar AGnO Framework installation")
        
        return all_ok


async def main():
    """Executa diagnóstico completo"""
    print("🚀 DIAGNÓSTICO INTEGRAÇÃO CRM + CALENDAR")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    diagnostic = IntegrationDiagnostic()
    
    # Executar diagnósticos
    await diagnostic.diagnose_kommo_integration()
    await diagnostic.diagnose_calendar_integration()
    diagnostic.diagnose_tools_registration()
    
    # Resumo final
    all_ok = diagnostic.print_summary()
    
    print(f"\n⏰ Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Diagnóstico interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)