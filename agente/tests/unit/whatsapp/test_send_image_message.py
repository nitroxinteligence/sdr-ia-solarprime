"""
Unit tests for send_image_message tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agente.tools.whatsapp.send_image_message import send_image_message


@pytest.mark.asyncio
async def test_send_image_message_success(mock_evolution_service):
    """Test successful image message sending"""
    # Arrange
    phone = "5511999999999"
    image_url = "https://example.com/photo.jpg"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8E"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8E"
    assert result["phone"] == phone
    assert result["media_type"] == "image"
    assert result["has_caption"] is False
    
    # Verify service was called correctly
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=image_url,
        media_type="image",
        caption=None
    )


@pytest.mark.asyncio
async def test_send_image_message_with_caption(mock_evolution_service):
    """Test sending image with caption"""
    # Arrange
    phone = "5511999999999"
    image_url = "https://example.com/diagram.png"
    caption = "Veja este diagrama explicativo sobre energia solar"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE8F"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url, caption)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE8F"
    assert result["phone"] == phone
    assert result["media_type"] == "image"
    assert result["has_caption"] is True
    
    # Verify service was called with caption
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=image_url,
        media_type="image",
        caption=caption
    )


@pytest.mark.asyncio
async def test_send_image_message_invalid_url(mock_evolution_service):
    """Test sending image with invalid URL"""
    # Arrange
    phone = "5511999999999"
    image_url = "invalid-url"
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url)
    
    # Assert
    assert result["success"] is False
    assert "URL de imagem inválida" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "image"
    assert result["has_caption"] is False
    
    # Verify service was not called
    mock_evolution_service.send_media.assert_not_called()


@pytest.mark.asyncio
async def test_send_image_message_empty_url(mock_evolution_service):
    """Test sending image with empty URL"""
    # Arrange
    phone = "5511999999999"
    image_url = ""
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url)
    
    # Assert
    assert result["success"] is False
    assert "URL de imagem inválida" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "image"
    
    # Verify service was not called
    mock_evolution_service.send_media.assert_not_called()


@pytest.mark.asyncio
async def test_send_image_message_various_extensions(mock_evolution_service):
    """Test sending images with various valid extensions"""
    # Arrange
    test_cases = [
        ("https://example.com/photo.jpg", True),
        ("https://example.com/photo.jpeg", True),
        ("https://example.com/photo.png", True),
        ("https://example.com/photo.gif", True),
        ("https://example.com/photo.webp", True),
        ("https://example.com/photo.bmp", True),
        ("https://example.com/photo.svg", True),
        ("https://example.com/photo.JPG", True),  # Uppercase
        ("https://example.com/photo?format=jpg", True),  # Query param
        ("https://example.com/photo.txt", False),  # Invalid extension
    ]
    
    phone = "5511999999999"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE90"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        for image_url, should_warn in test_cases:
            # Reset mock
            mock_evolution_service.send_media.reset_mock()
            
            # Act
            result = await send_image_message(phone, image_url)
            
            # Assert
            assert result["success"] is True
            assert result["phone"] == phone
            
            # Verify service was called
            mock_evolution_service.send_media.assert_called_once()


@pytest.mark.asyncio
async def test_send_image_message_empty_response(mock_evolution_service):
    """Test handling empty response from Evolution API"""
    # Arrange
    phone = "5511999999999"
    image_url = "https://example.com/photo.jpg"
    
    # Mock empty response
    mock_evolution_service.send_media.return_value = None
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url)
    
    # Assert
    assert result["success"] is False
    assert "resposta vazia da API" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "image"


@pytest.mark.asyncio
async def test_send_image_message_exception(mock_evolution_service):
    """Test handling exceptions during image sending"""
    # Arrange
    phone = "5511999999999"
    image_url = "https://example.com/photo.jpg"
    error_message = "Connection timeout"
    
    # Mock exception
    mock_evolution_service.send_media.side_effect = Exception(error_message)
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url)
    
    # Assert
    assert result["success"] is False
    assert error_message in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "image"


@pytest.mark.asyncio
async def test_send_image_message_missing_message_id(mock_evolution_service):
    """Test handling response without message ID"""
    # Arrange
    phone = "5511999999999"
    image_url = "https://example.com/photo.jpg"
    
    # Mock response without key/id
    mock_evolution_service.send_media.return_value = {
        "status": "sent",
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == ""  # Should handle missing ID gracefully
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_image_message_http_url(mock_evolution_service):
    """Test sending image with HTTP URL (not HTTPS)"""
    # Arrange
    phone = "5511999999999"
    image_url = "http://example.com/photo.jpg"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE91"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url)
    
    # Assert
    assert result["success"] is True  # HTTP URLs are allowed
    assert result["message_id"] == "3EB0C767D097E9ECFE91"
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_image_message_long_caption(mock_evolution_service):
    """Test sending image with very long caption"""
    # Arrange
    phone = "5511999999999"
    image_url = "https://example.com/photo.jpg"
    caption = "Esta é uma legenda muito longa. " * 50  # Very long caption
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE92"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url, caption)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE92"
    assert result["has_caption"] is True
    
    # Verify the full caption was passed
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=image_url,
        media_type="image",
        caption=caption
    )


@pytest.mark.asyncio
async def test_send_image_message_special_chars_in_caption(mock_evolution_service):
    """Test sending image with special characters in caption"""
    # Arrange
    phone = "5511999999999"
    image_url = "https://example.com/photo.jpg"
    caption = "Promoção! 🌟 50% de desconto\n\nDetalhes: @solar_prime #energia"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE93"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_image_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_image_message(phone, image_url, caption)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE93"
    assert result["has_caption"] is True