#!/usr/bin/env python3
"""
Testes unitários para o TypingController
Garantir que typing funciona APENAS quando agente responde
"""

import pytest
from app.services.typing_controller import (
    TypingController,
    TypingContext,
    TypingDecision,
    should_show_typing_for_user_message,
    should_show_typing_for_agent_response
)


class TestTypingController:
    """Testes completos do TypingController"""
    
    def test_user_message_never_shows_typing(self):
        """Quando usuário envia mensagem, NUNCA deve mostrar typing"""
        controller = TypingController(enable_typing=True)
        
        # Testar com diferentes tamanhos de mensagem
        for message_length in [0, 10, 100, 1000]:
            decision = controller.should_show_typing(
                TypingContext.USER_MESSAGE,
                message_length
            )
            assert decision.should_show is False
            assert "usuário" in decision.reason.lower()
    
    def test_agent_response_shows_typing(self):
        """Quando agente responde, SEMPRE deve mostrar typing"""
        controller = TypingController(enable_typing=True)
        
        decision = controller.should_show_typing(
            TypingContext.AGENT_RESPONSE,
            100
        )
        assert decision.should_show is True
        assert decision.duration is not None
        assert "agente" in decision.reason.lower()
    
    def test_system_message_never_shows_typing(self):
        """Mensagens do sistema NUNCA devem mostrar typing"""
        controller = TypingController(enable_typing=True)
        
        decision = controller.should_show_typing(
            TypingContext.SYSTEM_MESSAGE,
            50
        )
        assert decision.should_show is False
        assert "sistema" in decision.reason.lower()
    
    def test_media_upload_never_shows_typing(self):
        """Upload de mídia NUNCA deve mostrar typing"""
        controller = TypingController(enable_typing=True)
        
        decision = controller.should_show_typing(
            TypingContext.MEDIA_UPLOAD,
            0
        )
        assert decision.should_show is False
        assert "mídia" in decision.reason.lower()
    
    def test_global_disable_overrides_all(self):
        """Se typing está globalmente desabilitado, NUNCA mostrar"""
        controller = TypingController(enable_typing=False)
        
        # Mesmo para resposta do agente
        decision = controller.should_show_typing(
            TypingContext.AGENT_RESPONSE,
            100
        )
        assert decision.should_show is False
        assert "globalmente desabilitado" in decision.reason.lower()
    
    def test_duration_calculation(self):
        """Testa cálculo de duração do typing"""
        controller = TypingController(enable_typing=True)
        
        # Mensagem vazia = 2 segundos
        decision = controller.should_show_typing(
            TypingContext.AGENT_RESPONSE,
            0
        )
        assert decision.duration == 2.0
        
        # 50 chars = 1 segundo
        decision = controller.should_show_typing(
            TypingContext.AGENT_RESPONSE,
            50
        )
        assert decision.duration == 1.0
        
        # 350 chars = 7 segundos (máximo)
        decision = controller.should_show_typing(
            TypingContext.AGENT_RESPONSE,
            350
        )
        assert decision.duration == 7.0
        
        # 1000 chars = ainda 7 segundos (máximo)
        decision = controller.should_show_typing(
            TypingContext.AGENT_RESPONSE,
            1000
        )
        assert decision.duration == 7.0
    
    def test_convenience_functions(self):
        """Testa funções de conveniência"""
        # Usuário nunca mostra typing
        assert should_show_typing_for_user_message() is False
        
        # Agente sempre mostra typing
        decision = should_show_typing_for_agent_response(100)
        assert decision.should_show is True
        assert decision.duration > 0


class TestIntegrationScenarios:
    """Testes de cenários reais de integração"""
    
    def test_webhook_receiving_user_message(self):
        """Simula webhook recebendo mensagem do usuário"""
        controller = TypingController(enable_typing=True)
        
        # Webhook recebe mensagem
        user_message = "Olá, quero saber sobre energia solar"
        
        # Decisão: não mostrar typing
        decision = controller.should_show_typing(
            TypingContext.USER_MESSAGE,
            len(user_message)
        )
        
        assert decision.should_show is False
        # NÃO deve haver delay ou typing aqui
    
    def test_agent_processing_response(self):
        """Simula agente processando e respondendo"""
        controller = TypingController(enable_typing=True)
        
        # Agente gera resposta
        agent_response = "Olá! Fico feliz com seu interesse em energia solar..."
        
        # Decisão: mostrar typing
        decision = controller.should_show_typing(
            TypingContext.AGENT_RESPONSE,
            len(agent_response)
        )
        
        assert decision.should_show is True
        assert 1.0 <= decision.duration <= 7.0
    
    def test_production_scenario(self):
        """Cenário completo de produção"""
        controller = TypingController(enable_typing=True)
        
        # 1. Usuário envia áudio
        decision = controller.should_show_typing(TypingContext.USER_MESSAGE, 0)
        assert decision.should_show is False
        
        # 2. Sistema transcreve (não mostra typing)
        decision = controller.should_show_typing(TypingContext.SYSTEM_MESSAGE, 0)
        assert decision.should_show is False
        
        # 3. Agente processa e responde
        decision = controller.should_show_typing(TypingContext.AGENT_RESPONSE, 150)
        assert decision.should_show is True
        assert decision.duration == 3.0  # 150 chars / 50 chars/s


if __name__ == "__main__":
    # Executar testes
    print("🧪 Executando testes do TypingController...")
    pytest.main([__file__, "-v", "--color=yes"])