#!/usr/bin/env python3
"""
Executar TESTES REAIS do Google Calendar diretamente com Python
Contorna problemas do pytest e conftest
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Setup do ambiente
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Carrega .env
env_path = root_dir / '.env'
load_dotenv(env_path)
os.environ['PYTEST_RUNNING'] = 'true'

print("🚀 EXECUTANDO TESTES REAIS DO GOOGLE CALENDAR")
print("=" * 60)

# Importa as classes de teste
from agente.tests.real_integration.test_calendar_authentication_real import TestGoogleCalendarAuthenticationReal
from agente.tests.real_integration.test_google_calendar_real import TestGoogleCalendarReal

def run_authentication_tests():
    """Executa testes de autenticação."""
    print("\n🔐 TESTES DE AUTENTICAÇÃO REAL")
    print("=" * 40)
    
    test_class = TestGoogleCalendarAuthenticationReal()
    test_class.test_prefix = "[TEST-AUTH]"
    test_class.timeout = 30
    
    tests_run = 0
    tests_passed = 0
    
    # Lista de métodos de teste
    test_methods = [
        'test_service_account_credentials_creation',
        'test_calendar_service_build', 
        'test_real_api_authentication',
        'test_calendar_service_integration',
        'test_rate_limiting_authentication',
        'test_environment_validation'
    ]
    
    for test_name in test_methods:
        print(f"\n🧪 Executando: {test_name}")
        print("-" * 50)
        
        try:
            test_method = getattr(test_class, test_name)
            test_method()
            print(f"✅ PASSOU: {test_name}")
            tests_passed += 1
        except Exception as e:
            print(f"❌ FALHOU: {test_name}")
            print(f"   Erro: {str(e)}")
        
        tests_run += 1
    
    print(f"\n📊 RESULTADOS AUTENTICAÇÃO: {tests_passed}/{tests_run} testes passaram")
    return tests_passed, tests_run

def run_crud_tests():
    """Executa testes CRUD."""
    print("\n📝 TESTES CRUD REAL")
    print("=" * 40)
    
    test_class = TestGoogleCalendarReal()
    test_class.test_prefix = "[TEST-CRUD]"
    test_class.created_events = []
    test_class.test_calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
    
    tests_run = 0
    tests_passed = 0
    
    # Lista de métodos de teste
    test_methods = [
        'test_create_event_real',
        'test_complete_crud_cycle_real'
    ]
    
    for test_name in test_methods:
        print(f"\n🧪 Executando: {test_name}")
        print("-" * 50)
        
        try:
            test_method = getattr(test_class, test_name)
            test_method()
            print(f"✅ PASSOU: {test_name}")
            tests_passed += 1
        except Exception as e:
            print(f"❌ FALHOU: {test_name}")
            print(f"   Erro: {str(e)}")
        
        tests_run += 1
    
    # Cleanup de eventos criados
    if hasattr(test_class, 'created_events') and test_class.created_events:
        print("\n🗑️ LIMPEZA DE EVENTOS DE TESTE")
        try:
            service = test_class._create_calendar_service()
            for event_id in test_class.created_events:
                try:
                    service.events().delete(
                        calendarId=test_class.test_calendar_id,
                        eventId=event_id
                    ).execute()
                    print(f"   ✅ Removido: {event_id}")
                except:
                    print(f"   ⚠️ Não foi possível remover: {event_id}")
        except Exception as e:
            print(f"   ❌ Erro na limpeza: {e}")
    
    print(f"\n📊 RESULTADOS CRUD: {tests_passed}/{tests_run} testes passaram")
    return tests_passed, tests_run

def main():
    """Função principal."""
    print("Carregando configurações...")
    
    # Verifica se as credenciais estão disponíveis
    required_vars = [
        'GOOGLE_SERVICE_ACCOUNT_EMAIL',
        'GOOGLE_PRIVATE_KEY', 
        'GOOGLE_PROJECT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ ERRO: Variáveis faltando: {', '.join(missing_vars)}")
        return
    
    print("✅ Credenciais carregadas com sucesso")
    
    # Executa os testes
    total_passed = 0
    total_run = 0
    
    # Testes de autenticação
    auth_passed, auth_run = run_authentication_tests()
    total_passed += auth_passed
    total_run += auth_run
    
    # Testes CRUD
    crud_passed, crud_run = run_crud_tests()
    total_passed += crud_passed
    total_run += crud_run
    
    # Resultado final
    print("\n" + "=" * 60)
    print("🏆 RESULTADO FINAL DOS TESTES REAIS")
    print("=" * 60)
    print(f"📊 Total de testes: {total_run}")
    print(f"✅ Testes passaram: {total_passed}")
    print(f"❌ Testes falharam: {total_run - total_passed}")
    print(f"📈 Taxa de sucesso: {(total_passed/total_run)*100:.1f}%")
    
    if total_passed == total_run:
        print("\n🎉 TODOS OS TESTES REAIS PASSARAM!")
        print("   A integração com Google Calendar está funcionando perfeitamente!")
    else:
        print(f"\n⚠️ {total_run - total_passed} teste(s) falharam")
        print("   Verifique os logs acima para detalhes")
    
    print("=" * 60)

if __name__ == "__main__":
    main()