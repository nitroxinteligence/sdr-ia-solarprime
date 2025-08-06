"""
Testes para o Typing Controller
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.typing_controller import (
    TypingController, 
    TypingContext, 
    TypingRequest,
    get_typing_controller,
    reset_typing_controller
)

@pytest.fixture
def mock_evolution_client():
    """Mock do Evolution API Client"""
    client = Mock()
    client.send_typing = AsyncMock()
    return client

@pytest.fixture
def typing_controller(mock_evolution_client):
    """Instância do Typing Controller para testes"""
    # Reset singleton
    reset_typing_controller()
    
    # Mock settings
    with patch('app.services.typing_controller.settings') as mock_settings:
        mock_settings.enable_typing_simulation = True
        controller = TypingController(mock_evolution_client)
        yield controller

class TestTypingController:
    """Testes do Typing Controller"""
    
    def test_should_show_typing_agent_thinking(self, typing_controller):
        """Deve mostrar typing quando agente está pensando"""
        assert typing_controller.should_show_typing(TypingContext.AGENT_THINKING) is True
    
    def test_should_not_show_typing_user_message(self, typing_controller):
        """NÃO deve mostrar typing para mensagem do usuário"""
        assert typing_controller.should_show_typing(TypingContext.USER_MESSAGE) is False
    
    def test_should_not_show_typing_system_message(self, typing_controller):
        """NÃO deve mostrar typing para mensagem do sistema"""
        assert typing_controller.should_show_typing(TypingContext.SYSTEM_MESSAGE) is False
    
    def test_should_not_show_typing_when_disabled(self, typing_controller):
        """NÃO deve mostrar typing quando desabilitado globalmente"""
        typing_controller.disable_typing()
        assert typing_controller.should_show_typing(TypingContext.AGENT_THINKING) is False
    
    @pytest.mark.asyncio
    async def test_send_typing_agent_thinking(self, typing_controller, mock_evolution_client):
        """Deve enviar typing para contexto AGENT_THINKING"""
        request = TypingRequest(
            phone="5511999999999",
            context=TypingContext.AGENT_THINKING,
            message_length=100
        )
        
        result = await typing_controller.send_typing(request)
        
        assert result is True
        mock_evolution_client.send_typing.assert_called_once_with(
            phone="5511999999999",
            message_length=100,
            duration_seconds=None
        )
    
    @pytest.mark.asyncio
    async def test_not_send_typing_user_message(self, typing_controller, mock_evolution_client):
        """NÃO deve enviar typing para contexto USER_MESSAGE"""
        request = TypingRequest(
            phone="5511999999999",
            context=TypingContext.USER_MESSAGE,
            message_length=50
        )
        
        result = await typing_controller.send_typing(request)
        
        assert result is False
        mock_evolution_client.send_typing.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_notify_agent_thinking_helper(self, typing_controller, mock_evolution_client):
        """Teste do método helper notify_agent_thinking"""
        await typing_controller.notify_agent_thinking("5511999999999", 150)
        
        mock_evolution_client.send_typing.assert_called_once_with(
            phone="5511999999999",
            message_length=150,
            duration_seconds=None
        )
    
    @pytest.mark.asyncio
    async def test_typing_error_handling(self, typing_controller, mock_evolution_client):
        """Deve tratar erros gracefully"""
        mock_evolution_client.send_typing.side_effect = Exception("API Error")
        
        request = TypingRequest(
            phone="5511999999999",
            context=TypingContext.AGENT_THINKING
        )
        
        result = await typing_controller.send_typing(request)
        
        assert result is False  # Retorna False em caso de erro
    
    def test_singleton_pattern(self, mock_evolution_client):
        """Testa padrão singleton"""
        reset_typing_controller()
        
        controller1 = get_typing_controller(mock_evolution_client)
        controller2 = get_typing_controller(mock_evolution_client)
        
        assert controller1 is controller2  # Mesma instância

if __name__ == "__main__":
    pytest.main([__file__, "-v"])