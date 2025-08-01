"""
Unit tests for send_location_message tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agente.tools.whatsapp.send_location_message import send_location_message


@pytest.mark.asyncio
async def test_send_location_message_success(mock_evolution_service):
    """Test successful location message sending"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    
    # Mock the Evolution service response
    mock_evolution_service.send_location.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE92"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE92"
    assert result["phone"] == phone
    assert result["location"]["lat"] == latitude
    assert result["location"]["lng"] == longitude
    assert result["has_name"] is False
    
    # Verify service was called correctly
    mock_evolution_service.send_location.assert_called_once_with(
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        name=None
    )


@pytest.mark.asyncio
async def test_send_location_message_with_name_and_address(mock_evolution_service):
    """Test sending location with name and address"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    name = "SolarPrime Boa Viagem"
    address = "Av. Conselheiro Aguiar, 3456 - Boa Viagem, Recife - PE"
    
    # Mock the Evolution service response
    mock_evolution_service.send_location.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE93"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude, name, address)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == "3EB0C767D097E9ECFE93"
    assert result["phone"] == phone
    assert result["location"]["lat"] == latitude
    assert result["location"]["lng"] == longitude
    assert result["has_name"] is True
    
    # Verify service was called with combined name and address
    expected_location_name = f"{name}\n{address}"
    mock_evolution_service.send_location.assert_called_once_with(
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        name=expected_location_name
    )


@pytest.mark.asyncio
async def test_send_location_message_with_name_only(mock_evolution_service):
    """Test sending location with name but no address"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    name = "SolarPrime Escritório Central"
    
    # Mock the Evolution service response
    mock_evolution_service.send_location.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE94"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude, name)
    
    # Assert
    assert result["success"] is True
    assert result["has_name"] is True
    
    # Verify service was called with name only
    mock_evolution_service.send_location.assert_called_once_with(
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        name=name
    )


@pytest.mark.asyncio
async def test_send_location_message_with_address_only(mock_evolution_service):
    """Test sending location with address but no name"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    address = "Rua dos Navegantes, 123 - Boa Viagem"
    
    # Mock the Evolution service response
    mock_evolution_service.send_location.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE95"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude, None, address)
    
    # Assert
    assert result["success"] is True
    assert result["has_name"] is False  # Name parameter was None
    
    # Verify service was called with address as name
    mock_evolution_service.send_location.assert_called_once_with(
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        name=address
    )


@pytest.mark.asyncio
async def test_send_location_message_invalid_latitude_too_low(mock_evolution_service):
    """Test sending location with latitude below valid range"""
    # Arrange
    phone = "5511999999999"
    latitude = -91.0  # Below -90
    longitude = -34.8963
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is False
    assert "Latitude inválida" in result["error"]
    assert "-90 e 90" in result["error"]
    assert result["location"]["lat"] == latitude
    assert result["location"]["lng"] == longitude
    
    # Verify service was not called
    mock_evolution_service.send_location.assert_not_called()


@pytest.mark.asyncio
async def test_send_location_message_invalid_latitude_too_high(mock_evolution_service):
    """Test sending location with latitude above valid range"""
    # Arrange
    phone = "5511999999999"
    latitude = 91.0  # Above 90
    longitude = -34.8963
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is False
    assert "Latitude inválida" in result["error"]
    assert "-90 e 90" in result["error"]
    
    # Verify service was not called
    mock_evolution_service.send_location.assert_not_called()


@pytest.mark.asyncio
async def test_send_location_message_invalid_longitude_too_low(mock_evolution_service):
    """Test sending location with longitude below valid range"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -181.0  # Below -180
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is False
    assert "Longitude inválida" in result["error"]
    assert "-180 e 180" in result["error"]
    assert result["location"]["lat"] == latitude
    assert result["location"]["lng"] == longitude
    
    # Verify service was not called
    mock_evolution_service.send_location.assert_not_called()


@pytest.mark.asyncio
async def test_send_location_message_invalid_longitude_too_high(mock_evolution_service):
    """Test sending location with longitude above valid range"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = 181.0  # Above 180
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is False
    assert "Longitude inválida" in result["error"]
    assert "-180 e 180" in result["error"]
    
    # Verify service was not called
    mock_evolution_service.send_location.assert_not_called()


@pytest.mark.asyncio
async def test_send_location_message_boundary_values(mock_evolution_service):
    """Test sending location with boundary coordinate values"""
    # Arrange
    test_cases = [
        (90.0, 180.0),    # North Pole, International Date Line
        (-90.0, -180.0),  # South Pole, International Date Line
        (0.0, 0.0),       # Equator, Prime Meridian
        (45.5, -122.5),   # Regular coordinates
    ]
    
    phone = "5511999999999"
    
    # Mock the Evolution service response
    mock_evolution_service.send_location.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE96"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        for latitude, longitude in test_cases:
            # Reset mock
            mock_evolution_service.send_location.reset_mock()
            
            # Act
            result = await send_location_message(phone, latitude, longitude)
            
            # Assert
            assert result["success"] is True
            assert result["location"]["lat"] == latitude
            assert result["location"]["lng"] == longitude
            
            # Verify service was called
            mock_evolution_service.send_location.assert_called_once()


@pytest.mark.asyncio
async def test_send_location_message_empty_response(mock_evolution_service):
    """Test handling empty response from Evolution API"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    
    # Mock empty response
    mock_evolution_service.send_location.return_value = None
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is False
    assert "resposta vazia da API" in result["error"]
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_location_message_exception(mock_evolution_service):
    """Test handling exceptions during location sending"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    error_message = "Connection timeout"
    
    # Mock exception
    mock_evolution_service.send_location.side_effect = Exception(error_message)
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is False
    assert error_message in result["error"]
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_location_message_missing_message_id(mock_evolution_service):
    """Test handling response without message ID"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    
    # Mock response without key/id
    mock_evolution_service.send_location.return_value = {
        "status": "sent",
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is True
    assert result["message_id"] == ""  # Should handle missing ID gracefully
    assert result["phone"] == phone


@pytest.mark.asyncio
async def test_send_location_message_special_chars_in_name(mock_evolution_service):
    """Test sending location with special characters in name"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.1127
    longitude = -34.8963
    name = "🌟 SolarPrime - Energia Solar #1"
    address = "Av. Boa Viagem, 3456 - Recife/PE 🏢"
    
    # Mock the Evolution service response
    mock_evolution_service.send_location.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE97"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude, name, address)
    
    # Assert
    assert result["success"] is True
    assert result["has_name"] is True
    
    # Verify special characters were passed correctly
    expected_location_name = f"{name}\n{address}"
    mock_evolution_service.send_location.assert_called_once_with(
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        name=expected_location_name
    )


@pytest.mark.asyncio
async def test_send_location_message_float_precision(mock_evolution_service):
    """Test sending location with high precision coordinates"""
    # Arrange
    phone = "5511999999999"
    latitude = -8.112734567890123
    longitude = -34.896345678901234
    
    # Mock the Evolution service response
    mock_evolution_service.send_location.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE98"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.send_location_message.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await send_location_message(phone, latitude, longitude)
    
    # Assert
    assert result["success"] is True
    assert result["location"]["lat"] == latitude
    assert result["location"]["lng"] == longitude
    
    # Verify exact coordinates were passed
    mock_evolution_service.send_location.assert_called_once_with(
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        name=None
    )