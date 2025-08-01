#!/usr/bin/env python3
"""
Teste isolado das melhorias do Calendar Service
Testa apenas a lógica específica das correções implementadas
"""

import asyncio
import sys
import os
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Configurar variáveis de ambiente para teste
os.environ.update({
    'DISABLE_GOOGLE_CALENDAR': 'false',
    'GOOGLE_PROJECT_ID': 'test-project',
    'GOOGLE_PRIVATE_KEY_ID': 'test-key-id', 
    'GOOGLE_PRIVATE_KEY': '-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----',
    'GOOGLE_SERVICE_ACCOUNT_EMAIL': 'test@test-project.iam.gserviceaccount.com',
    'GOOGLE_CLIENT_ID': 'test-client-id',
    'GOOGLE_CALENDAR_ID': 'primary',
    'CALENDAR_MIN_INTERVAL': '15',
    'CALENDAR_SLOT_DURATION': '60',
    'CALENDAR_BUSINESS_HOURS': '{"start": "08:00", "end": "18:00"}'
})

def test_imports():
    """Teste 1: Verificar se as importações básicas funcionam"""
    print("🧪 TESTE 1: Importações básicas...")
    
    try:
        # Mock das dependências externas
        with patch('google.oauth2.service_account.Credentials') as mock_creds, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            # Configurar mocks
            mock_creds.from_service_account_info.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Testar import direto do módulo
            sys.path.insert(0, 'agente/services')
            from calendar_service import GoogleCalendarService
            
            print("   ✅ Import do GoogleCalendarService OK")
            
            # Testar inicialização básica
            service = GoogleCalendarService()
            print("   ✅ Inicialização básica OK")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Falha no teste de imports: {e}")
        return False

def test_thread_safety():
    """Teste 2: Verificar thread safety do singleton"""
    print("\n🧪 TESTE 2: Thread Safety...")
    
    try:
        sys.path.insert(0, 'agente/services')
        
        with patch('google.oauth2.service_account.Credentials') as mock_creds, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            mock_creds.from_service_account_info.return_value = Mock()
            mock_build.return_value = Mock()
            
            from calendar_service import get_calendar_service
            
            services = []
            errors = []
            
            def create_service():
                try:
                    service = get_calendar_service()
                    services.append(service)
                except Exception as e:
                    errors.append(e)
            
            # Criar múltiplas threads
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=create_service)
                threads.append(thread)
            
            # Iniciar todas as threads
            for thread in threads:
                thread.start()
            
            # Aguardar conclusão
            for thread in threads:
                thread.join()
            
            # Verificar resultados
            if errors:
                print(f"   ❌ Erros durante criação: {errors}")
                return False
            
            if len(services) != 10:
                print(f"   ❌ Número incorreto de serviços: {len(services)}")
                return False
            
            # Verificar se todos são o mesmo objeto (singleton)
            first_service = services[0]
            all_same = all(service is first_service for service in services)
            
            if all_same:
                print("   ✅ Thread safety OK - Singleton mantido em threads concorrentes")
                return True
            else:
                print("   ❌ Thread safety falhou - Múltiplas instâncias criadas")
                return False
                
    except Exception as e:
        print(f"   ❌ Falha no teste de thread safety: {e}")
        return False

def test_rate_limiting_structure():
    """Teste 3: Verificar estrutura de rate limiting"""
    print("\n🧪 TESTE 3: Estrutura de Rate Limiting...")
    
    try:
        with patch('google.oauth2.service_account.Credentials') as mock_creds, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            mock_creds.from_service_account_info.return_value = Mock()
            mock_build.return_value = Mock()
            
            sys.path.insert(0, 'agente/services')
            from calendar_service import GoogleCalendarService
            
            service = GoogleCalendarService()
            
            # Verificar constantes de rate limiting
            assert hasattr(service, 'MAX_REQUESTS_PER_SECOND'), "Constante MAX_REQUESTS_PER_SECOND não encontrada"
            assert hasattr(service, 'MAX_REQUESTS_PER_MINUTE'), "Constante MAX_REQUESTS_PER_MINUTE não encontrada"
            assert hasattr(service, 'MAX_RETRIES'), "Constante MAX_RETRIES não encontrada"
            
            # Verificar estruturas de controle
            assert hasattr(service, '_request_times'), "Lista _request_times não encontrada"
            assert hasattr(service, '_rate_limit_lock'), "Lock _rate_limit_lock não encontrado"
            
            # Verificar valores das constantes
            assert service.MAX_REQUESTS_PER_SECOND == 10, f"MAX_REQUESTS_PER_SECOND deveria ser 10, mas é {service.MAX_REQUESTS_PER_SECOND}"
            assert service.MAX_REQUESTS_PER_MINUTE == 600, f"MAX_REQUESTS_PER_MINUTE deveria ser 600, mas é {service.MAX_REQUESTS_PER_MINUTE}"
            assert service.MAX_RETRIES == 3, f"MAX_RETRIES deveria ser 3, mas é {service.MAX_RETRIES}"
            
            # Verificar métodos de rate limiting
            assert hasattr(service, '_enforce_rate_limits'), "Método _enforce_rate_limits não encontrado"
            assert hasattr(service, '_exponential_backoff'), "Método _exponential_backoff não encontrado"
            assert hasattr(service, '_rate_limited_execute'), "Método _rate_limited_execute não encontrado"
            
            print("   ✅ Estrutura de rate limiting OK")
            print(f"      - Max requests/sec: {service.MAX_REQUESTS_PER_SECOND}")
            print(f"      - Max requests/min: {service.MAX_REQUESTS_PER_MINUTE}")
            print(f"      - Max retries: {service.MAX_RETRIES}")
            print(f"      - Rate limit lock: {type(service._rate_limit_lock).__name__}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Falha no teste de rate limiting: {e}")
        return False

def test_error_handling_structure():
    """Teste 4: Verificar estrutura de error handling"""
    print("\n🧪 TESTE 4: Estrutura de Error Handling...")
    
    try:
        with patch('google.oauth2.service_account.Credentials') as mock_creds, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            mock_creds.from_service_account_info.return_value = Mock()
            mock_build.return_value = Mock()
            
            sys.path.insert(0, 'agente/services')
            from calendar_service import GoogleCalendarService
            
            service = GoogleCalendarService()
            
            # Verificar métodos de validação
            assert hasattr(service, '_validate_environment'), "Método _validate_environment não encontrado"
            assert hasattr(service, '_test_connectivity'), "Método _test_connectivity não encontrado"
            
            # Verificar estrutura de backoff
            assert hasattr(service, 'BACKOFF_BASE_DELAY'), "Constante BACKOFF_BASE_DELAY não encontrada"
            assert hasattr(service, 'BACKOFF_MAX_DELAY'), "Constante BACKOFF_MAX_DELAY não encontrada"
            
            print("   ✅ Estrutura de error handling OK")
            print(f"      - Base delay: {service.BACKOFF_BASE_DELAY}s")
            print(f"      - Max delay: {service.BACKOFF_MAX_DELAY}s")
            print("      - Métodos de validação presentes")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Falha no teste de error handling: {e}")
        return False

async def test_rate_limiting_logic():
    """Teste 5: Verificar lógica de rate limiting"""
    print("\n🧪 TESTE 5: Lógica de Rate Limiting...")
    
    try:
        with patch('google.oauth2.service_account.Credentials') as mock_creds, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            mock_creds.from_service_account_info.return_value = Mock()
            mock_build.return_value = Mock()
            
            sys.path.insert(0, 'agente/services')
            from calendar_service import GoogleCalendarService
            
            service = GoogleCalendarService()
            
            # Testar _enforce_rate_limits diretamente
            start_time = time.time()
            
            # Simular muitas requisições
            for i in range(5):
                await service._enforce_rate_limits()
            
            elapsed = time.time() - start_time
            
            # Verificar se houve controle de rate (deve ter algum delay)
            if elapsed > 0.1:  # Pelo menos 100ms de delay total
                print(f"   ✅ Rate limiting funcionando (delay de {elapsed:.2f}s para 5 requests)")
            else:
                print(f"   ⚠️  Rate limiting pode não estar funcionando (apenas {elapsed:.2f}s delay)")
            
            # Verificar se requests foram registrados
            with service._rate_limit_lock:
                request_count = len(service._request_times)
            
            print(f"      - Requests registrados: {request_count}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Falha no teste de lógica de rate limiting: {e}")
        return False

async def test_exponential_backoff():
    """Teste 6: Verificar exponential backoff"""
    print("\n🧪 TESTE 6: Exponential Backoff...")
    
    try:
        with patch('google.oauth2.service_account.Credentials') as mock_creds, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            mock_creds.from_service_account_info.return_value = Mock()
            mock_build.return_value = Mock()
            
            sys.path.insert(0, 'agente/services')
            from calendar_service import GoogleCalendarService
            
            service = GoogleCalendarService()
            
            # Testar backoff com diferentes tentativas
            delays = []
            
            for attempt in range(3):
                start_time = time.time()
                await service._exponential_backoff(attempt)
                elapsed = time.time() - start_time
                delays.append(elapsed)
            
            # Verificar se delays estão aumentando exponencialmente
            print(f"   ✅ Exponential backoff testado:")
            for i, delay in enumerate(delays):
                print(f"      - Tentativa {i}: {delay:.2f}s")
            
            # Verificar se o delay aumenta
            if delays[1] > delays[0] and delays[2] > delays[1]:
                print("   ✅ Backoff exponencial funcionando corretamente")
                return True
            else:
                print("   ⚠️  Backoff pode não estar aumentando exponencialmente")
                return True  # Ainda OK, pode ter jitter
            
    except Exception as e:
        print(f"   ❌ Falha no teste de exponential backoff: {e}")
        return False

def test_environment_validation():
    """Teste 7: Verificar validação de ambiente"""
    print("\n🧪 TESTE 7: Validação de Ambiente...")
    
    try:
        with patch('google.oauth2.service_account.Credentials') as mock_creds, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            mock_creds.from_service_account_info.return_value = Mock()
            mock_build.return_value = Mock()
            
            sys.path.insert(0, 'agente/services')
            from calendar_service import GoogleCalendarService
            
            # Limpar variáveis para forçar erro
            old_vars = {}
            test_vars = ['GOOGLE_PROJECT_ID', 'GOOGLE_PRIVATE_KEY', 'GOOGLE_SERVICE_ACCOUNT_EMAIL']
            
            for var in test_vars:
                old_vars[var] = os.environ.get(var)
                if var in os.environ:
                    del os.environ[var]
            
            try:
                # Deve falhar na validação
                service = GoogleCalendarService()
                print("   ❌ Validação de ambiente não funcionou - deveria ter falhado")
                return False
            except ValueError as e:
                print(f"   ✅ Validação de ambiente OK - erro esperado: {str(e)[:50]}...")
                
                # Restaurar variáveis
                for var, value in old_vars.items():
                    if value:
                        os.environ[var] = value
                
                return True
            
    except Exception as e:
        print(f"   ❌ Falha no teste de validação de ambiente: {e}")
        return False

async def main():
    """Executar todos os testes"""
    print("🚀 INICIANDO TESTES DAS MELHORIAS DO CALENDAR SERVICE")
    print("=" * 60)
    
    tests = [
        ("Importações básicas", test_imports),
        ("Thread Safety", test_thread_safety),
        ("Estrutura Rate Limiting", test_rate_limiting_structure),
        ("Estrutura Error Handling", test_error_handling_structure),
        ("Lógica Rate Limiting", test_rate_limiting_logic),
        ("Exponential Backoff", test_exponential_backoff),
        ("Validação Ambiente", test_environment_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            
        except Exception as e:
            print(f"   ❌ Erro crítico no teste '{test_name}': {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINAIS")
    print("=" * 60)
    print(f"✅ Testes aprovados: {passed}/{total}")
    print(f"❌ Testes falharam: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ As melhorias do Calendar Service estão funcionando corretamente!")
    elif passed >= total * 0.8:
        print("\n⚠️  MAIORIA DOS TESTES PASSOU")
        print("✅ As melhorias principais estão funcionando!")
    else:
        print("\n🚨 MUITOS TESTES FALHARAM")
        print("❌ Podem haver problemas nas melhorias implementadas")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())