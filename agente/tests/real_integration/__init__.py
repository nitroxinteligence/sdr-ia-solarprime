"""
Real Integration Tests - SDR IA SolarPrime

Testes de integração com APIs reais (não mocks).
Estes testes fazem chamadas reais para:
- Google Calendar API
- Kommo CRM API  
- Evolution WhatsApp API
- Supabase Database

IMPORTANTE: 
- Usa ambiente de TESTE isolado
- Não impacta dados de produção
- Cleanup automático após cada teste
- Rate limiting para não esgotar quotas
"""

# Test environment validation
import os
import warnings

def validate_test_environment():
    """Valida que estamos em ambiente de testes"""
    
    # Check for test environment markers
    is_test_env = any([
        os.getenv('ENVIRONMENT') == 'test',
        os.getenv('TESTING') == 'true', 
        os.getenv('PYTEST_RUNNING') == 'true',
        'test' in os.getenv('GOOGLE_CALENDAR_ID', '').lower(),
        'test' in os.getenv('KOMMO_SUBDOMAIN', '').lower()
    ])
    
    if not is_test_env:
        warnings.warn(
            "⚠️  REAL INTEGRATION TESTS - Certifique-se que está em ambiente de TESTE!\n"
            "Configure ENVIRONMENT=test ou use credenciais de teste.",
            UserWarning,
            stacklevel=2
        )

# Validate on import
validate_test_environment()