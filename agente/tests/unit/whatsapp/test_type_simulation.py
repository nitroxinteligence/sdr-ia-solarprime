"""
Unit tests for type_simulation tool
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from agente.tools.whatsapp.type_simulation import simulate_typing


@pytest.mark.asyncio
async def test_simulate_typing_success(mock_evolution_service):
    """Test successful typing simulation with message sending"""
    # Arrange
    phone = "5511999999999"
    text = "Olá! Como posso ajudar você hoje?"
    
    # Mock the Evolution service response
    mock_evolution_service._calculate_typing_delay.return_value = 3.2
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE94"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text)
    
    # Assert
    assert result["success"] is True
    assert 2.5 <= result["typing_duration"] <= 3.9  # Allow for timing variations
    assert result["words_count"] == 6
    assert result["chars_count"] == 34
    assert result["message_sent"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE94"
    
    # Verify message was sent after typing
    mock_evolution_service.send_text_message.assert_called_once_with(
        phone=phone,
        text=text,
        delay=0
    )


@pytest.mark.asyncio
async def test_simulate_typing_without_sending(mock_evolution_service):
    """Test typing simulation without sending message"""
    # Arrange
    phone = "5511999999999"
    text = "Mensagem longa para simular digitação"
    
    # Mock the Evolution service
    mock_evolution_service._calculate_typing_delay.return_value = 5.7
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text, send_after=False)
    
    # Assert
    assert result["success"] is True
    assert 5.0 <= result["typing_duration"] <= 6.5  # Allow for timing variations
    assert result["words_count"] == 5
    assert result["chars_count"] == 38
    assert result["message_sent"] is False
    assert "message_id" not in result
    
    # Verify message was NOT sent
    mock_evolution_service.send_text_message.assert_not_called()


@pytest.mark.asyncio
async def test_simulate_typing_custom_delay(mock_evolution_service):
    """Test typing simulation with custom delay"""
    # Arrange
    phone = "5511999999999"
    text = "Test message"
    custom_delay = 4.5
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE95"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text, custom_delay=custom_delay)
    
    # Assert
    assert result["success"] is True
    assert 4.0 <= result["typing_duration"] <= 5.0  # Custom delay with variations
    assert result["words_count"] == 2
    assert result["chars_count"] == 12
    assert result["message_sent"] is True


@pytest.mark.asyncio
async def test_simulate_typing_very_short_delay(mock_evolution_service):
    """Test typing simulation with delay below minimum threshold"""
    # Arrange
    phone = "5511999999999"
    text = "Hi"
    custom_delay = 0.5  # Below minimum
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE96"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text, custom_delay=custom_delay)
    
    # Assert
    assert result["success"] is True
    assert result["typing_duration"] >= 0.8  # Should be clamped to at least 1.0
    assert result["words_count"] == 1
    assert result["chars_count"] == 2


@pytest.mark.asyncio
async def test_simulate_typing_very_long_delay(mock_evolution_service):
    """Test typing simulation with delay above maximum threshold"""
    # Arrange
    phone = "5511999999999"
    text = "Test"
    custom_delay = 20  # Above maximum
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE97"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text, custom_delay=custom_delay)
    
    # Assert
    assert result["success"] is True
    assert result["typing_duration"] <= 16  # Should be clamped to max (15) + variations


@pytest.mark.asyncio
async def test_simulate_typing_send_failure(mock_evolution_service):
    """Test typing simulation when message sending fails"""
    # Arrange
    phone = "5511999999999"
    text = "Test message"
    
    # Mock the Evolution service
    mock_evolution_service._calculate_typing_delay.return_value = 3.0
    mock_evolution_service.send_text_message.return_value = None  # Send failure
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text, send_after=True)
    
    # Assert
    assert result["success"] is True  # Typing succeeded
    assert result["typing_duration"] >= 2.5
    assert result["message_sent"] is False
    assert result["error"] == "Simulação OK, mas falha ao enviar mensagem"


@pytest.mark.asyncio
async def test_simulate_typing_exception(mock_evolution_service):
    """Test handling exceptions during typing simulation"""
    # Arrange
    phone = "5511999999999"
    text = "Test message"
    error_message = "Network error"
    
    # Mock exception during delay calculation
    mock_evolution_service._calculate_typing_delay.side_effect = Exception(error_message)
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text)
    
    # Assert
    assert result["success"] is False
    assert error_message in result["error"]
    assert result["typing_duration"] == 0
    assert result["words_count"] == 2
    assert result["chars_count"] == 12
    assert result["message_sent"] is False


@pytest.mark.asyncio
async def test_simulate_typing_empty_text(mock_evolution_service):
    """Test typing simulation with empty text"""
    # Arrange
    phone = "5511999999999"
    text = ""
    
    # Mock the Evolution service
    mock_evolution_service._calculate_typing_delay.return_value = 2.0
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE98"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text)
    
    # Assert
    assert result["success"] is True
    assert result["words_count"] == 0
    assert result["chars_count"] == 0
    assert result["message_sent"] is True


@pytest.mark.asyncio
async def test_simulate_typing_multiline_text(mock_evolution_service):
    """Test typing simulation with multiline text"""
    # Arrange
    phone = "5511999999999"
    text = """Olá! Sou a Helen da SolarPrime.
    
    Gostaria de saber mais sobre energia solar?
    Podemos agendar uma conversa."""
    
    # Mock the Evolution service
    mock_evolution_service._calculate_typing_delay.return_value = 6.5
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE99"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution_service):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            # Act
            result = await simulate_typing(phone, text)
    
    # Assert
    assert result["success"] is True
    assert result["typing_duration"] >= 5.5
    assert result["words_count"] == 17
    assert result["chars_count"] == len(text)
    assert result["message_sent"] is True


@pytest.mark.asyncio
async def test_simulate_typing_sleep_interruption():
    """Test handling of sleep interruption during typing simulation"""
    # Arrange
    phone = "5511999999999"
    text = "Test message"
    
    # Create a mock evolution service
    mock_evolution = AsyncMock()
    mock_evolution._calculate_typing_delay.return_value = 5.0
    
    # Mock asyncio.sleep to raise CancelledError
    async def mock_sleep(duration):
        if duration > 1:
            raise asyncio.CancelledError()
        await asyncio.sleep(0.01)  # Small actual delay
    
    # Patch the get_evolution_service function and AI_TYPING_DELAY_MAX
    with patch('agente.tools.whatsapp.type_simulation.get_evolution_service', return_value=mock_evolution):
        with patch('agente.tools.whatsapp.type_simulation.AI_TYPING_DELAY_MAX', 15):
            with patch('asyncio.sleep', side_effect=mock_sleep):
                # Act
                result = await simulate_typing(phone, text, send_after=False)
    
    # Assert
    assert result["success"] is False
    assert "CancelledError" in result["error"]
    assert result["typing_duration"] == 0