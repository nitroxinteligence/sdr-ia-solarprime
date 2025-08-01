"""
End-to-End Real Tests - SDR IA SolarPrime

Testes E2E completos sem mocks que validam:
- Fluxo completo de qualificação de leads
- Integração WhatsApp → AI → Google Calendar → Kommo
- Data consistency across all services
- Recovery scenarios quando serviços falham

CARACTERÍSTICAS:
- Zero mocks - todas as integrações são reais
- Ambiente de teste isolado
- Cleanup completo após cada teste
- Validação de data consistency
- Recovery e rollback testing
"""

from .conftest import *  # Import shared fixtures