"""
Configuração para Testes Reais - SDR IA SolarPrime

Framework de testes que funciona com APIs reais em ambiente de teste isolado.
Inclui fixtures, markers, cleanup automático e safety mechanisms.
"""

import pytest
import os
import asyncio
import warnings
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

# Import dos serviços reais
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Configurar markers do pytest
def pytest_configure(config):
    """Configurar markers customizados para testes reais"""
    config.addinivalue_line(
        "markers", "integration_real: Testes de integração com APIs reais (podem ser lentos)"
    )
    config.addinivalue_line(
        "markers", "e2e_real: Testes end-to-end completos sem mocks (muito lentos)"
    )
    config.addinivalue_line(
        "markers", "performance_real: Testes de performance e load testing (muito lentos)"
    )
    config.addinivalue_line(
        "markers", "requires_test_env: Requer ambiente de teste configurado"
    )

def pytest_runtest_setup(item):
    """Setup executado antes de cada teste"""
    # Verificar se teste requer ambiente de teste
    if item.get_closest_marker("requires_test_env"):
        if not _is_test_environment():
            pytest.skip("Teste requer ambiente de teste configurado")

def _is_test_environment() -> bool:
    """Verifica se estamos em ambiente de teste"""
    return any([
        os.getenv('ENVIRONMENT') == 'test',
        os.getenv('TESTING') == 'true',
        os.getenv('PYTEST_RUNNING') == 'true',
        'test' in os.getenv('GOOGLE_CALENDAR_ID', '').lower(),
        'test' in os.getenv('KOMMO_SUBDOMAIN', '').lower()
    ])

# Fixtures para ambiente de teste
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup global do ambiente de teste"""
    # Validar ambiente de teste
    if not _is_test_environment():
        warnings.warn(
            "⚠️  TESTES REAIS - Configure ambiente de teste!\n"
            "Use ENVIRONMENT=test e credenciais de teste.",
            UserWarning
        )
    
    # Configurar variáveis de ambiente para testes
    os.environ['PYTEST_RUNNING'] = 'true'
    
    # Log início dos testes
    print("\n🧪 INICIANDO TESTES REAIS - AMBIENTE DE TESTE")
    print("=" * 50)
    
    yield
    
    # Cleanup global após todos os testes
    print("\n✅ TESTES REAIS CONCLUÍDOS")

@pytest.fixture
def test_session_id():
    """ID único para cada sessão de teste"""
    return f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

@pytest.fixture
async def cleanup_tracker():
    """Tracker para limpeza automática após testes"""
    cleanup_actions = []
    
    def add_cleanup(action, *args, **kwargs):
        """Adiciona uma ação de limpeza"""
        cleanup_actions.append((action, args, kwargs))
    
    yield add_cleanup
    
    # Executar todas as ações de limpeza
    for action, args, kwargs in reversed(cleanup_actions):
        try:
            if asyncio.iscoroutinefunction(action):
                await action(*args, **kwargs)
            else:
                action(*args, **kwargs)
        except Exception as e:
            print(f"⚠️  Erro no cleanup: {e}")

# Fixtures para Google Calendar real
@pytest.fixture
async def real_google_calendar():
    """Cliente real do Google Calendar para testes"""
    # Verificar se ambiente está configurado
    required_vars = [
        'GOOGLE_PROJECT_ID',
        'GOOGLE_PRIVATE_KEY', 
        'GOOGLE_SERVICE_ACCOUNT_EMAIL',
        'GOOGLE_CALENDAR_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.skip(f"Google Calendar não configurado: {missing_vars}")
    
    try:
        from agente.services.calendar_service import get_calendar_service
        service = get_calendar_service()
        
        if not service.is_available():
            pytest.skip("Google Calendar service não disponível")
        
        # Teste básico de conectividade
        await service._rate_limited_execute(
            service.service.calendars().get,
            calendarId=service.calendar_id
        )
        
        yield service
        
    except Exception as e:
        pytest.skip(f"Falha ao conectar Google Calendar: {e}")

@pytest.fixture
async def real_kommo_crm():
    """Cliente real do Kommo CRM para testes"""
    required_vars = [
        'KOMMO_SUBDOMAIN',
        'KOMMO_LONG_LIVED_TOKEN'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.skip(f"Kommo CRM não configurado: {missing_vars}")
    
    try:
        from agente.services.kommo_service import get_kommo_service
        service = get_kommo_service()
        
        # Teste básico de conectividade
        # await service.test_connection()  # Se existir
        
        yield service
        
    except Exception as e:
        pytest.skip(f"Falha ao conectar Kommo CRM: {e}")

@pytest.fixture
async def real_evolution_api():
    """Cliente real da Evolution API para testes"""
    required_vars = [
        'EVOLUTION_API_URL',
        'EVOLUTION_API_KEY',
        'EVOLUTION_INSTANCE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.skip(f"Evolution API não configurada: {missing_vars}")
    
    try:
        from agente.services.evolution_service import get_evolution_service
        service = get_evolution_service()
        
        # Teste básico de conectividade
        # connection_status = await service.check_connection()
        # if not connection_status.get('connected'):
        #     pytest.skip("Evolution API não conectada")
        
        yield service
        
    except Exception as e:
        pytest.skip(f"Falha ao conectar Evolution API: {e}")

@pytest.fixture
async def real_supabase_db():
    """Cliente real do Supabase para testes"""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.skip(f"Supabase não configurado: {missing_vars}")
    
    try:
        from agente.services.supabase_service import get_supabase_service
        service = get_supabase_service()
        
        # Teste básico de conectividade
        # await service.test_connection()
        
        yield service
        
    except Exception as e:
        pytest.skip(f"Falha ao conectar Supabase: {e}")

# Fixtures para dados de teste
@pytest.fixture
def test_lead_data(test_session_id):
    """Dados de lead para testes"""
    return {
        'name': f'Test User {test_session_id}',
        'phone': f'5511999{test_session_id[-6:]}',  # Usar últimos 6 chars do session_id
        'email': f'test.{test_session_id}@example.com',
        'stage': 'IDENTIFICATION',
        'source': 'test_automation',
        'test_session_id': test_session_id
    }

@pytest.fixture
def test_calendar_event_data(test_session_id):
    """Dados de evento de calendário para testes"""
    start_time = datetime.now() + timedelta(days=1, hours=10)  # Amanhã às 10h
    
    return {
        'title': f'[TESTE] Reunião {test_session_id}',
        'description': f'Evento de teste criado pela automação - Session: {test_session_id}',
        'start_time': start_time,
        'duration_minutes': 60,
        'attendees': [f'test.{test_session_id}@example.com'],
        'test_session_id': test_session_id
    }

# Fixtures para rate limiting nos testes
@pytest.fixture
async def rate_limiter():
    """Rate limiter para não esgotar quotas das APIs"""
    import asyncio
    
    last_call_times = {}
    
    async def rate_limit(service_name: str, min_interval: float = 1.0):
        """Aplica rate limiting entre chamadas"""
        now = asyncio.get_event_loop().time()
        last_call = last_call_times.get(service_name, 0)
        
        time_since_last = now - last_call
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            print(f"⏳ Rate limiting {service_name}: aguardando {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        
        last_call_times[service_name] = asyncio.get_event_loop().time()
    
    return rate_limit

# Helper functions para testes
def assert_no_test_data_in_production():
    """Garante que não há dados de teste em produção"""
    if os.getenv('ENVIRONMENT') == 'production':
        raise AssertionError("❌ NUNCA execute testes reais em produção!")

def get_test_config() -> Dict[str, Any]:
    """Configuração específica para testes"""
    return {
        'environment': os.getenv('ENVIRONMENT', 'unknown'),
        'google_calendar_id': os.getenv('GOOGLE_CALENDAR_ID'),
        'kommo_subdomain': os.getenv('KOMMO_SUBDOMAIN'),
        'evolution_instance': os.getenv('EVOLUTION_INSTANCE'),
        'test_timeout': int(os.getenv('TEST_TIMEOUT', '300')),  # 5 minutos default
        'max_retries': int(os.getenv('TEST_MAX_RETRIES', '3'))
    }

# Export principais
__all__ = [
    'setup_test_environment',
    'test_session_id', 
    'cleanup_tracker',
    'real_google_calendar',
    'real_kommo_crm',
    'real_evolution_api', 
    'real_supabase_db',
    'test_lead_data',
    'test_calendar_event_data',
    'rate_limiter',
    'assert_no_test_data_in_production',
    'get_test_config'
]