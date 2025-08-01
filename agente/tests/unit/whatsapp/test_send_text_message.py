"""
Unit tests for send_text_message tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agente.tools.whatsapp.send_text_message import send_text_message


@pytest.mark.asyncio
async def test_send_text_message_success(mock_evolution_service):
    """Test successful text message sending with automatic delay calculation"""
    # Arrange
    phone = "5511999999999"
    text = "Olá! Sou a Helen da SolarPrime. Como posso ajudar?"
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8A"},
        "messageTimestamp": "1234567890"
    }
    mock_evolution_service._calculate_typing_delay.return_value = 3
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8A"
    assert result["phone"] == phone
    assert result["delay_applied"] == 3
    
    # Verify service was called correctly
    mock_evolution_service.send_text_message.assert_called_once_with(
        phone=phone,
        text=text,
        delay=None
    )


@pytest.mark.asyncio
async def test_send_text_message_with_custom_delay(mock_evolution_service):
    """Test sending text message with custom delay"""
    # Arrange
    phone = "5511999999999"
    text = "Mensagem com delay específico"
    custom_delay = 5
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8B"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text, delay=custom_delay)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8B"
    assert result["phone"] == phone
    assert result["delay_applied"] == custom_delay
    
    # Verify service was called with custom delay
    mock_evolution_service.send_text_message.assert_called_once_with(
        phone=phone,
        text=text,
        delay=custom_delay
    )


@pytest.mark.asyncio
async def test_send_text_message_empty_response(mock_evolution_service):
    """Test handling empty response from Evolution API"""
    # Arrange
    phone = "5511999999999"
    text = "Test message"
    
    # Mock empty response
    mock_evolution_service.send_text_message.return_value = None
    mock_evolution_service._calculate_typing_delay.return_value = 2
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert
    assert result["success"] is False
    assert result["error"] == "Falha ao enviar mensagem - resposta vazia da API"
    assert result["phone"] == phone
    assert result["delay_applied"] == 0


@pytest.mark.asyncio
async def test_send_text_message_exception(mock_evolution_service):
    """Test handling exceptions during message sending"""
    # Arrange
    phone = "5511999999999"
    text = "Test message"
    error_message = "Connection timeout"
    
    # Mock exception
    mock_evolution_service.send_text_message.side_effect = Exception(error_message)
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert
    assert result["success"] is False
    assert error_message in result["error"]
    assert result["phone"] == phone
    assert result["delay_applied"] == 0


@pytest.mark.asyncio
async def test_send_text_message_invalid_phone(mock_evolution_service):
    """Test sending message with invalid phone number format"""
    # Arrange
    phone = "invalid_phone"
    text = "Test message"
    
    # Mock exception due to invalid phone
    mock_evolution_service.send_text_message.side_effect = ValueError("Invalid phone number format")
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert
    assert result["success"] is False
    assert "Invalid phone number format" in result["error"]
    assert result["phone"] == phone
    assert result["delay_applied"] == 0


@pytest.mark.asyncio
async def test_send_text_message_empty_text(mock_evolution_service):
    """Test sending empty text message"""
    # Arrange
    phone = "5511999999999"
    text = ""
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8C"},
        "messageTimestamp": "1234567890"
    }
    mock_evolution_service._calculate_typing_delay.return_value = 2
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert - Should still attempt to send
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8C"
    assert result["phone"] == phone
    assert result["delay_applied"] == 2


@pytest.mark.asyncio
async def test_send_text_message_very_long_text(mock_evolution_service):
    """Test sending very long text message"""
    # Arrange
    phone = "5511999999999"
    text = "Lorem ipsum " * 500  # Very long text
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8D"},
        "messageTimestamp": "1234567890"
    }
    mock_evolution_service._calculate_typing_delay.return_value = 15  # Max delay
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8D"
    assert result["phone"] == phone
    assert result["delay_applied"] == 15  # Should be capped at max


@pytest.mark.asyncio
async def test_send_text_message_special_characters(mock_evolution_service):
    """Test sending text with special characters and emojis"""
    # Arrange
    phone = "5511999999999"
    text = "Olá! 😊 Como está? \n\nAqui estão alguns caracteres especiais: @#$%&*()[]{}'"
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8E"},
        "messageTimestamp": "1234567890"
    }
    mock_evolution_service._calculate_typing_delay.return_value = 4
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8E"
    assert result["phone"] == phone
    assert result["delay_applied"] == 4
    
    # Verify the text was passed correctly
    mock_evolution_service.send_text_message.assert_called_once_with(
        phone=phone,
        text=text,
        delay=None
    )


@pytest.mark.asyncio
async def test_send_text_message_missing_message_id(mock_evolution_service):
    """Test handling response without message ID"""
    # Arrange
    phone = "5511999999999"
    text = "Test message"
    
    # Mock response without key/id
    mock_evolution_service.send_text_message.return_value = {
        "status": "sent",
        "messageTimestamp": "1234567890"
    }
    mock_evolution_service._calculate_typing_delay.return_value = 3
    
    # Patch the get_evolution_service function
    with pytest.mock.patch('agente.tools.whatsapp.send_text_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_text_message(phone, text)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == ""  # Should handle missing ID gracefully
    assert result["phone"] == phone
    assert result["delay_applied"] == 3