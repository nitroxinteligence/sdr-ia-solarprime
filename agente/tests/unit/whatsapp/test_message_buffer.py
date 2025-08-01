"""
Unit tests for message_buffer tool
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from agente.tools.whatsapp.message_buffer import (
    buffer_message,
    clear_buffer,
    get_buffer_status,
    _message_buffers,
    _buffer_locks
)


@pytest.fixture(autouse=True)
async def cleanup_buffers():
    """Cleanup message buffers before and after each test"""
    # Clear all buffers before test
    _message_buffers.clear()
    _buffer_locks.clear()
    yield
    # Clear all buffers after test
    _message_buffers.clear()
    _buffer_locks.clear()


@pytest.mark.asyncio
async def test_buffer_message_single_message(mock_evolution_service):
    """Test adding a single message to buffer without sending"""
    # Arrange
    phone = "5511999999999"
    message = "Primeira parte da resposta..."
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await buffer_message(phone, message)
    
    # Assert
    assert result["success"] is True
    assert result["buffer_size"] == 1
    assert result["message_added"] is True
    assert result["sent"] is False
    assert result["time_until_send_ms"] == 3000
    
    # Verify message is in buffer
    assert len(_message_buffers[phone]) == 1
    assert _message_buffers[phone][0]["message"] == message


@pytest.mark.asyncio
async def test_buffer_message_force_send(mock_evolution_service):
    """Test force sending buffered messages"""
    # Arrange
    phone = "5511999999999"
    message1 = "Primeira parte..."
    message2 = "Segunda parte..."
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE99"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution_service):
        # Act - Add first message
        result1 = await buffer_message(phone, message1)
        assert result1["sent"] is False
        
        # Act - Add second message and force send
        result2 = await buffer_message(phone, message2, force_send=True)
    
    # Assert
    assert result2["success"] is True
    assert result2["buffer_size"] == 0  # Buffer should be cleared
    assert result2["message_added"] is True
    assert result2["sent"] is True
    assert result2["consolidated_message"] == f"{message1}\n\n{message2}"
    
    # Verify service was called with consolidated message
    mock_evolution_service.send_text_message.assert_called_once_with(
        phone=phone,
        text=f"{message1}\n\n{message2}"
    )


@pytest.mark.asyncio
async def test_buffer_message_max_buffer_size(mock_evolution_service):
    """Test automatic sending when buffer reaches max size"""
    # Arrange
    phone = "5511999999999"
    max_buffer_size = 3
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE9A"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution_service):
        # Act - Add messages up to max buffer size
        for i in range(max_buffer_size - 1):
            result = await buffer_message(phone, f"Mensagem {i+1}", max_buffer_size=max_buffer_size)
            assert result["sent"] is False
        
        # Add one more message to trigger send
        result = await buffer_message(phone, f"Mensagem {max_buffer_size}", max_buffer_size=max_buffer_size)
    
    # Assert
    assert result["success"] is True
    assert result["sent"] is True
    assert result["buffer_size"] == 0  # Buffer should be cleared
    
    # Verify all messages were consolidated
    expected_message = "\n\n".join([f"Mensagem {i+1}" for i in range(max_buffer_size)])
    assert expected_message in result["consolidated_message"]


@pytest.mark.asyncio
async def test_buffer_message_timeout_trigger():
    """Test automatic sending after timeout"""
    # Arrange
    phone = "5511999999999"
    message = "Test message"
    consolidate_after_ms = 100  # Very short timeout for testing
    
    # Create mock evolution service
    mock_evolution = AsyncMock()
    mock_evolution.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE9B"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution):
        # Act - Add message with auto_send enabled
        result = await buffer_message(
            phone, 
            message, 
            consolidate_after_ms=consolidate_after_ms,
            auto_send=True
        )
        
        # Assert - Message should be in buffer
        assert result["sent"] is False
        assert result["buffer_size"] == 1
        
        # Wait for auto-send to trigger
        await asyncio.sleep((consolidate_after_ms + 50) / 1000)  # Wait a bit more than timeout
        
        # Give some time for the auto-send task to complete
        await asyncio.sleep(0.1)
        
        # Verify message was sent
        mock_evolution.send_text_message.assert_called_once()


@pytest.mark.asyncio
async def test_buffer_message_send_failure(mock_evolution_service):
    """Test handling of send failures"""
    # Arrange
    phone = "5511999999999"
    message = "Test message"
    
    # Mock send failure
    mock_evolution_service.send_text_message.return_value = None
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await buffer_message(phone, message, force_send=True)
    
    # Assert
    assert result["success"] is True
    assert result["sent"] is False
    assert result["buffer_size"] == 1  # Message should remain in buffer
    
    # Verify buffer still contains the message
    assert len(_message_buffers[phone]) == 1


@pytest.mark.asyncio
async def test_buffer_message_exception_handling(mock_evolution_service):
    """Test handling of exceptions during message sending"""
    # Arrange
    phone = "5511999999999"
    message = "Test message"
    error_message = "Connection error"
    
    # Mock exception
    mock_evolution_service.send_text_message.side_effect = Exception(error_message)
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution_service):
        # Act
        result = await buffer_message(phone, message, force_send=True)
    
    # Assert
    assert result["success"] is True  # Buffer operation succeeds despite send failure
    assert result["sent"] is False
    assert result["buffer_size"] == 1  # Message remains in buffer


@pytest.mark.asyncio
async def test_clear_buffer_success():
    """Test clearing buffer for a specific phone"""
    # Arrange
    phone = "5511999999999"
    
    # Add some messages to buffer
    _message_buffers[phone] = [
        {"message": "Message 1", "timestamp": datetime.now(), "sent": False},
        {"message": "Message 2", "timestamp": datetime.now(), "sent": False}
    ]
    
    # Act
    result = await clear_buffer(phone)
    
    # Assert
    assert result["success"] is True
    assert result["messages_cleared"] == 2
    assert len(_message_buffers[phone]) == 0


@pytest.mark.asyncio
async def test_clear_buffer_empty():
    """Test clearing an already empty buffer"""
    # Arrange
    phone = "5511999999999"
    
    # Act
    result = await clear_buffer(phone)
    
    # Assert
    assert result["success"] is True
    assert result["messages_cleared"] == 0


@pytest.mark.asyncio
async def test_get_buffer_status_single_phone():
    """Test getting buffer status for a specific phone"""
    # Arrange
    phone = "5511999999999"
    message = "Test message with more than fifty characters to test truncation in status"
    
    # Add message to buffer
    _message_buffers[phone] = [{
        "message": message,
        "timestamp": datetime.now() - timedelta(seconds=5),
        "sent": False
    }]
    
    # Act
    result = await get_buffer_status(phone)
    
    # Assert
    assert result["success"] is True
    assert result["phone"] == phone
    assert result["buffer_size"] == 1
    assert len(result["messages"]) == 1
    
    # Check message truncation
    status_message = result["messages"][0]
    assert status_message["message"].endswith("...")
    assert len(status_message["message"]) == 53  # 50 chars + "..."
    assert 4.5 <= status_message["age_seconds"] <= 5.5  # Allow for timing variations
    assert status_message["sent"] is False


@pytest.mark.asyncio
async def test_get_buffer_status_all_phones():
    """Test getting buffer status for all phones"""
    # Arrange
    phone1 = "5511999999999"
    phone2 = "5511888888888"
    
    # Add messages to buffers
    _message_buffers[phone1] = [
        {"message": "Message 1", "timestamp": datetime.now(), "sent": False}
    ]
    _message_buffers[phone2] = [
        {"message": "Message 2", "timestamp": datetime.now() - timedelta(seconds=10), "sent": False},
        {"message": "Message 3", "timestamp": datetime.now(), "sent": False}
    ]
    
    # Act
    result = await get_buffer_status()
    
    # Assert
    assert result["success"] is True
    assert result["total_phones"] == 2
    assert phone1 in result["buffers"]
    assert phone2 in result["buffers"]
    
    # Check individual buffer stats
    assert result["buffers"][phone1]["buffer_size"] == 1
    assert result["buffers"][phone2]["buffer_size"] == 2
    assert 9.5 <= result["buffers"][phone2]["oldest_message_age"] <= 10.5


@pytest.mark.asyncio
async def test_buffer_message_concurrent_access():
    """Test concurrent access to the same phone buffer"""
    # Arrange
    phone = "5511999999999"
    
    # Create mock evolution service
    mock_evolution = AsyncMock()
    mock_evolution.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE9C"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution):
        # Act - Create multiple concurrent buffer operations
        tasks = []
        for i in range(5):
            task = buffer_message(phone, f"Concurrent message {i+1}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    # Assert - All operations should succeed
    for result in results:
        assert result["success"] is True
    
    # Verify all messages are in buffer
    assert len(_message_buffers[phone]) == 5


@pytest.mark.asyncio
async def test_buffer_message_no_auto_send():
    """Test buffer behavior with auto_send disabled"""
    # Arrange
    phone = "5511999999999"
    message = "Test message"
    consolidate_after_ms = 100  # Very short timeout
    
    # Create mock evolution service
    mock_evolution = AsyncMock()
    mock_evolution.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE9D"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution):
        # Act - Add message with auto_send disabled
        result = await buffer_message(
            phone, 
            message, 
            consolidate_after_ms=consolidate_after_ms,
            auto_send=False
        )
        
        # Assert - Message should be in buffer
        assert result["sent"] is False
        assert result["buffer_size"] == 1
        
        # Wait longer than timeout
        await asyncio.sleep((consolidate_after_ms + 100) / 1000)
        
        # Verify message was NOT sent
        mock_evolution.send_text_message.assert_not_called()
        
        # Buffer should still contain the message
        assert len(_message_buffers[phone]) == 1


@pytest.mark.asyncio
async def test_buffer_message_empty_message_force_send(mock_evolution_service):
    """Test force sending with empty message (used by auto-send)"""
    # Arrange
    phone = "5511999999999"
    
    # Add a message to buffer first
    _message_buffers[phone] = [{
        "message": "Existing message",
        "timestamp": datetime.now(),
        "sent": False
    }]
    
    # Mock the Evolution service response
    mock_evolution_service.send_text_message.return_value = {
        "key": {"id": "3EB0C767D097E9ECFE9E"},
        "messageTimestamp": "1234567890"
    }
    
    # Patch the get_evolution_service function
    with patch('agente.tools.whatsapp.message_buffer.get_evolution_service', return_value=mock_evolution_service):
        # Act - Force send with empty message
        result = await buffer_message(phone, "", force_send=True)
    
    # Assert
    assert result["success"] is True
    assert result["message_added"] is False  # Empty message not added
    assert result["sent"] is True
    assert result["consolidated_message"] == "Existing message"
    assert result["buffer_size"] == 0  # Buffer cleared