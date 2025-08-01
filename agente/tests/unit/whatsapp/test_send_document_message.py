"""
Unit tests for send_document_message tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agente.tools.whatsapp.send_document_message import send_document_message


@pytest.mark.asyncio
async def test_send_document_message_success(mock_evolution_service):
    """Test successful document message sending"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/contract.pdf"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE90"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE90"
    assert result["phone"] == phone
    assert result["media_type"] == "document"
    assert result["has_caption"] is False
    assert result["document_type"] == "pdf"
    
    # Verify service was called correctly
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=document_url,
        media_type="document",
        caption=None
    )


@pytest.mark.asyncio
async def test_send_document_message_with_caption_and_filename(mock_evolution_service):
    """Test sending document with caption and custom filename"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/report.pdf"
    caption = "Relatório mensal de energia"
    filename = "Relatorio_Janeiro_2024.pdf"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE91"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url, caption, filename)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE91"
    assert result["phone"] == phone
    assert result["media_type"] == "document"
    assert result["has_caption"] is True
    assert result["document_type"] == "pdf"
    
    # Verify service was called with combined caption
    expected_caption = f"{filename}\n\n{caption}"
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=document_url,
        media_type="document",
        caption=expected_caption
    )


@pytest.mark.asyncio
async def test_send_document_message_filename_only(mock_evolution_service):
    """Test sending document with filename but no caption"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/document.pdf"
    filename = "Contrato_SolarPrime.pdf"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE92"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url, None, filename)
    
    # Assert
    assert result["success"] is True
    assert result["has_caption"] is False  # No caption provided
    
    # Verify service was called with filename as caption
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=document_url,
        media_type="document",
        caption=filename
    )


@pytest.mark.asyncio
async def test_send_document_message_various_types(mock_evolution_service):
    """Test sending documents with various file types"""
    # Arrange
    test_cases = [
        ("https://example.com/file.pdf", "pdf"),
        ("https://example.com/file.doc", "doc"),
        ("https://example.com/file.docx", "docx"),
        ("https://example.com/file.xls", "xls"),
        ("https://example.com/file.xlsx", "xlsx"),
        ("https://example.com/file.ppt", "ppt"),
        ("https://example.com/file.pptx", "pptx"),
        ("https://example.com/file.txt", "txt"),
        ("https://example.com/file.csv", "csv"),
        ("https://example.com/file.zip", "zip"),
        ("https://example.com/file.rar", "rar"),
        ("https://example.com/file.unknown", "unknown"),
    ]
    
    phone = "5511999999999"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE93"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        for document_url, expected_type in test_cases:
            # Reset mock
            mock_evolution_service.send_media.reset_mock()
            
            # Act
            result = await send_document_message(phone, document_url)
            
            # Assert
            assert result["success"] is True
            assert result["document_type"] == expected_type
            
            # Verify service was called
            mock_evolution_service.send_media.assert_called_once()


@pytest.mark.asyncio
async def test_send_document_message_invalid_url(mock_evolution_service):
    """Test sending document with invalid URL"""
    # Arrange
    phone = "5511999999999"
    document_url = "invalid-url"
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is False
    assert "URL de documento inválida" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "document"
    assert result["document_type"] == "unknown"
    
    # Verify service was not called
    mock_evolution_service.send_media.assert_not_called()


@pytest.mark.asyncio
async def test_send_document_message_empty_url(mock_evolution_service):
    """Test sending document with empty URL"""
    # Arrange
    phone = "5511999999999"
    document_url = ""
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is False
    assert "URL de documento inválida" in result["error"]
    assert result["document_type"] == "unknown"
    
    # Verify service was not called
    mock_evolution_service.send_media.assert_not_called()


@pytest.mark.asyncio
async def test_send_document_message_empty_response(mock_evolution_service):
    """Test handling empty response from Evolution API"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/document.pdf"
    
    # Mock empty response
    mock_evolution_service.send_media.return_value = None
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is False
    assert "resposta vazia da API" in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "document"
    assert result["document_type"] == "pdf"


@pytest.mark.asyncio
async def test_send_document_message_exception(mock_evolution_service):
    """Test handling exceptions during document sending"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/document.pdf"
    error_message = "Connection timeout"
    
    # Mock exception
    mock_evolution_service.send_media.side_effect = Exception(error_message)
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is False
    assert error_message in result["error"]
    assert result["phone"] == phone
    assert result["media_type"] == "document"
    assert result["document_type"] == "unknown"


@pytest.mark.asyncio
async def test_send_document_message_uppercase_extension(mock_evolution_service):
    """Test document type detection with uppercase extensions"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/document.PDF"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE94"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is True
    assert result["document_type"] == "pdf"  # Should detect despite uppercase


@pytest.mark.asyncio
async def test_send_document_message_url_with_query_params(mock_evolution_service):
    """Test document type detection with query parameters in URL"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/download?file=report.xlsx&token=abc123"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE95"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is True
    assert result["document_type"] == "xlsx"  # Should detect from query param


@pytest.mark.asyncio
async def test_send_document_message_missing_message_id(mock_evolution_service):
    """Test handling response without message ID"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/document.pdf"
    
    # Mock response without key/id
    mock_evolution_service.send_media.return_value = {
        "status": "sent",
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == ""  # Should handle missing ID gracefully
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_document_message_special_chars_in_caption(mock_evolution_service):
    """Test sending document with special characters in caption"""
    # Arrange
    phone = "5511999999999"
    document_url = "https://example.com/document.pdf"
    caption = "Proposta Especial! 💰 Economia de 50%\n\n#SolarPrime @energia_solar"
    
    # Mock the Evolution service response
    mock_evolution_service.send_media.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE96"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_document_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_document_message(phone, document_url, caption)
    
    # Assert
    assert result["success"] is True
    assert result["has_caption"] is True
    
    # Verify caption was passed correctly
    mock_evolution_service.send_media.assert_called_once_with(
        phone=phone,
        media_url=document_url,
        media_type="document",
        caption=caption
    )