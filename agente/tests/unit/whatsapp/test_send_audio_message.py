"""
Unit tests for send_audio_message tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agente.tools.whatsapp.send_audio_message import send_audio_message


@pytest.mark.asyncio
async def test_send_audio_message_success(mock_evolution_service):
    """Test successful audio message sending"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/audio.mp3"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8C"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8C"
    assert result["phone"] == phone
    assert result["media_type"] == "audio"
    assert result["has_caption"] is False
    
    # Verify service was called correctly
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=audio_url,
        media_type="audio",
        caption=None
    )


@pytest.mark.asyncio
async def test_send_audio_message_with_caption(mock_evolution_service):
    """Test sending audio with caption"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/voice.ogg"
    caption = "Ouça este áudio importante sobre energia solar"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8D"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url, caption)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8D"
    assert result["phone"] == phone
    assert result["media_type"] == "audio"
    assert result["has_caption"] is True
    
    # Verify service was called with caption
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=audio_url,
        media_type="audio",
        caption=caption
    )


@pytest.mark.asyncio
async def test_send_audio_message_invalid_url(mock_evolution_service):
    """Test sending audio with invalid URL"""
    # Arrange
    phone = "5511999999999"
    audio_url = "invalid-url"
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is False
    assert "URL de áudio inválida" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "audio"
    assert result["has_caption"] is False
    
    # Verify service was not called
    mock_evolution_service.send_media.assert_not_called()


@pytest.mark.asyncio
async def test_send_audio_message_empty_url(mock_evolution_service):
    """Test sending audio with empty URL"""
    # Arrange
    phone = "5511999999999"
    audio_url = ""
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is False
    assert "URL de áudio inválida" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "audio"
    
    # Verify service was not called
    mock_evolution_service.send_media.assert_not_called()


@pytest.mark.asyncio
async def test_send_audio_message_various_formats(mock_evolution_service):
    """Test sending audio with various valid formats"""
    # Arrange
    test_formats = [
        "https://example.com/audio.mp3",
        "https://example.com/audio.ogg",
        "https://example.com/audio.opus",
        "https://example.com/audio.wav",
        "https://example.com/audio.m4a",
        "https://example.com/audio.aac",
        "https://example.com/audio.flac",
        "https://example.com/audio.webm",
    ]
    
    phone = "5511999999999"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8E"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        for audio_url in test_formats:
            # Reset mock
            mock_evolution_service.send_media.reset_mock()
            
            # Act
            result = await send_audio_message(phone, audio_url)
            
            # Assert
            assert result["success"] is True
            assert result["phone"] == phone
            assert result["media_type"] == "audio"
            
            # Verify service was called
            mock_evolution_service.send_media.assert_called_once()


@pytest.mark.asyncio
async def test_send_audio_message_empty_response(mock_evolution_service):
    """Test handling empty response from Evolution API"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/audio.mp3"
    
    # Mock empty response
    mock_evolution_service.send_media.return_value = None
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is False
    assert "resposta vazia da API" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "audio"


@pytest.mark.asyncio
async def test_send_audio_message_exception(mock_evolution_service):
    """Test handling exceptions during audio sending"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/audio.mp3"
    error_message = "Connection timeout"
    
    # Mock exception
    mock_evolution_service.send_media.side_effect = Exception(error_message)
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is False
    assert error_message in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "audio"


@pytest.mark.asyncio
async def test_send_audio_message_missing_message_id(mock_evolution_service):
    """Test handling response without message ID"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/audio.mp3"
    
    # Mock response without key/id
    mock_evolution_service.send_media.return_value = {
        "status": "sent",
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == ""  # Should handle missing ID gracefully
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_audio_message_http_url(mock_evolution_service):
    """Test sending audio with HTTP URL (not HTTPS)"""
    # Arrange
    phone = "5511999999999"
    audio_url = "http://example.com/audio.mp3"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8F"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is True  # HTTP URLs are allowed
    assert result["message_id"] == "3EB0C767D097E9ECFE8F"
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_audio_message_long_caption(mock_evolution_service):
    """Test sending audio with very long caption"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/audio.mp3"
    caption = "Esta é uma legenda muito longa para o áudio. " * 30  # Very long caption
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE90"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url, caption)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE90"
    assert result["has_caption"] is True
    
    # Verify the full caption was passed
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=audio_url,
        media_type="audio",
        caption=caption
    )


@pytest.mark.asyncio
async def test_send_audio_message_special_chars_in_caption(mock_evolution_service):
    """Test sending audio with special characters in caption"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/audio.mp3"
    caption = "🎵 Podcast SolarPrime #01\n\n✨ Economize até 95% na conta de luz!"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE91"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url, caption)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE91"
    assert result["has_caption"] is True


@pytest.mark.asyncio
async def test_send_audio_message_url_with_query_params(mock_evolution_service):
    """Test sending audio with query parameters in URL"""
    # Arrange
    phone = "5511999999999"
    audio_url = "https://example.com/stream?audio=podcast.mp3&session=abc123"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE92"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_audio_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_audio_message(phone, audio_url)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE92"
    
    # Verify URL was passed correctly
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=audio_url,
        media_type="audio",
        caption=None
    )