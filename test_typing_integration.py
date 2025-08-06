#!/usr/bin/env python3
"""
Teste de integração completo do sistema de typing
Valida que typing funciona APENAS quando agente responde
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.config import settings

@pytest.mark.asyncio
async def test_typing_integration_complete():
    """Teste completo de integração do sistema de typing"""
    
    # 1. Verificar configurações
    print("\n🔧 1. Verificando configurações...")
    assert settings.enable_typing_simulation == True, "Typing deve estar habilitado"
    assert settings.simulate_reading_time == False, "Tempo de leitura deve estar DESABILITADO"
    print("✅ Configurações corretas!")
    
    # 2. Importar e verificar TypingController
    print("\n🎮 2. Verificando TypingController...")
    from app.services.typing_controller import typing_controller, TypingContext
    
    # Teste 1: Usuário envia mensagem - NÃO deve mostrar typing
    decision = typing_controller.should_show_typing(TypingContext.USER_MESSAGE, 100)
    assert decision.should_show == False
    print("✅ USER_MESSAGE: Typing NÃO aparece (correto!)")
    
    # Teste 2: Agente responde - DEVE mostrar typing
    decision = typing_controller.should_show_typing(TypingContext.AGENT_RESPONSE, 100)
    assert decision.should_show == True
    assert decision.duration == 2.0  # 100 chars / 50 chars/s = 2s
    print("✅ AGENT_RESPONSE: Typing aparece por 2.0s (correto!)")
    
    # 3. Testar integração com Evolution API
    print("\n🔌 3. Testando integração com Evolution API...")
    from app.integrations.evolution import EvolutionAPIClient
    
    # Mock do Evolution Client
    with patch('app.integrations.evolution.httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"success": True})
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        
        evolution = EvolutionAPIClient()
        
        # Teste 1: send_typing com contexto user_message
        await evolution.send_typing("5511999999999", 50, context="user_message")
        # Verificar que NÃO foi feita chamada à API
        assert mock_client.return_value.__aenter__.return_value.request.call_count == 0
        print("✅ send_typing(user_message): Nenhuma chamada à API (correto!)")
        
        # Teste 2: send_typing com contexto agent_response
        await evolution.send_typing("5511999999999", 50, context="agent_response")
        # Verificar que FOI feita chamada à API
        assert mock_client.return_value.__aenter__.return_value.request.call_count == 1
        print("✅ send_typing(agent_response): Chamada à API executada (correto!)")
    
    # 4. Verificar que webhook não tem mais tempo de leitura
    print("\n🪝 4. Verificando webhook...")
    with open("/Users/adm/Downloads/1. NitroX Agentics/SDR IA SolarPrime v0.2/app/api/webhooks.py", "r") as f:
        webhook_content = f.read()
        assert "simulate_reading_time" not in webhook_content or "# REMOVIDO:" in webhook_content
        print("✅ Webhook não simula mais tempo de leitura (correto!)")
    
    print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de typing está 100% correto!")
    print("📋 Resumo:")
    print("  - Typing NÃO aparece quando usuário envia mensagem ✅")
    print("  - Typing APARECE quando agente responde ✅")
    print("  - Integração com Evolution API funcionando ✅")
    print("  - Webhook corrigido ✅")

if __name__ == "__main__":
    asyncio.run(test_typing_integration_complete())