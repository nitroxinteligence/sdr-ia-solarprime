"""
Unit tests for save_message database tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID, uuid4

from agente.tools.database.save_message import save_message, SaveMessageTool
from agente.core.types import Message, MessageRole, MediaType, Conversation


@pytest.fixture
def mock_message_repository():
    """Mock message repository for tests"""
    repository = AsyncMock()
    repository.save_message = AsyncMock()
    return repository


@pytest.fixture
def mock_conversation_repository():
    """Mock conversation repository for tests"""
    repository = AsyncMock()
    repository.get_conversation_by_id = AsyncMock()
    repository.update_conversation = AsyncMock()
    return repository


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing"""
    return Conversation(
        id=uuid4(),
        lead_id=uuid4(),
        session_id="test-session-123",
        total_messages=5,
        is_active=True,
        started_at=datetime.now()
    )


@pytest.fixture
def sample_message():
    """Sample message for testing"""
    return Message(
        id=uuid4(),
        conversation_id=uuid4(),
        role=MessageRole.USER,
        content="Olá, quero saber sobre energia solar",
        media_type=MediaType.TEXT,
        created_at=datetime.now()
    )


@pytest.mark.asyncio
class TestSaveMessage:
    """Test cases for save_message tool"""

    async def test_save_text_message_success(self, mock_message_repository, mock_conversation_repository, sample_conversation, sample_message):
        """Test successful text message save"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        content = "Olá, quero saber sobre energia solar"
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = sample_message
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content=content,
                    role="user"
                )
        
        # Assert
        assert result["success"] is True
        assert result["message_id"] == str(sample_message.id)
        assert result["conversation_id"] == str(sample_message.conversation_id)
        assert result["data"]["role"] == "user"
        assert result["data"]["content"] == content
        assert result["data"]["media_type"] == "text"
        assert result["data"]["has_media"] is False
        
        # Verify repository calls
        mock_conversation_repository.get_conversation_by_id.assert_called_once_with(UUID(conversation_id))
        mock_message_repository.save_message.assert_called_once()
        mock_conversation_repository.update_conversation.assert_called_once()

    async def test_save_message_with_media(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test saving message with media"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        media_message = Message(
            id=uuid4(),
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content="Foto da conta de luz",
            media_type=MediaType.IMAGE,
            media_url="https://media.example.com/image123.jpg",
            media_data={"analysis": {"bill_value": 500}},
            created_at=datetime.now()
        )
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = media_message
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content="Foto da conta de luz",
                    role="user",
                    media_type="image",
                    media_url="https://media.example.com/image123.jpg",
                    media_data={"analysis": {"bill_value": 500}}
                )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["media_type"] == "image"
        assert result["data"]["has_media"] is True
        assert "media_info" in result
        assert result["media_info"]["type"] == "image"
        assert result["media_info"]["url"] == "https://media.example.com/image123.jpg"
        assert result["media_info"]["has_data"] is True
        assert "analysis" in result["media_info"]["data_keys"]

    async def test_save_assistant_message(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test saving assistant message"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        assistant_message = Message(
            id=uuid4(),
            conversation_id=sample_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Olá! Sou a Helen da SolarPrime. Como posso ajudar?",
            media_type=MediaType.TEXT,
            created_at=datetime.now()
        )
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = assistant_message
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content="Olá! Sou a Helen da SolarPrime. Como posso ajudar?",
                    role="assistant"
                )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["role"] == "assistant"

    async def test_save_message_with_whatsapp_id(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test saving message with WhatsApp message ID"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        whatsapp_id = "wamid.HBgNNTUxMTk5OTk5OTk5ORIO0FBQUlTQTQyNTY3ODkwMTIzNDU2Nzg5MEIA"
        
        message_with_wa_id = Message(
            id=uuid4(),
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content="Test message",
            whatsapp_message_id=whatsapp_id,
            created_at=datetime.now()
        )
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = message_with_wa_id
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content="Test message",
                    whatsapp_message_id=whatsapp_id
                )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["whatsapp_message_id"] == whatsapp_id

    async def test_save_message_invalid_conversation_id(self):
        """Test with invalid conversation ID format"""
        # Act
        result = await save_message(
            conversation_id="invalid-uuid",
            content="Test message"
        )
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "ID de conversa inválido"
        assert result["error_type"] == "validation"

    async def test_save_message_invalid_role(self):
        """Test with invalid role"""
        # Act
        result = await save_message(
            conversation_id=str(uuid4()),
            content="Test message",
            role="invalid_role"
        )
        
        # Assert
        assert result["success"] is False
        assert "Role inválido" in result["error"]
        assert result["error_type"] == "validation"

    async def test_save_message_conversation_not_found(self, mock_conversation_repository):
        """Test saving message for non-existent conversation"""
        # Arrange
        conversation_id = str(uuid4())
        mock_conversation_repository.get_conversation_by_id.return_value = None
        
        with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await save_message(
                conversation_id=conversation_id,
                content="Test message"
            )
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Conversa não encontrada"
        assert result["error_type"] == "not_found"

    async def test_save_message_invalid_media_type(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test with invalid media type (should default to TEXT)"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        text_message = Message(
            id=uuid4(),
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content="Test message",
            media_type=MediaType.TEXT,  # Should default to TEXT
            created_at=datetime.now()
        )
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = text_message
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content="Test message",
                    media_type="invalid_type"
                )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["media_type"] == "text"

    async def test_save_message_database_error(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test database error during save"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.side_effect = Exception("Database error")
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content="Test message"
                )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao salvar mensagem" in result["error"]
        assert result["error_type"] == "database"

    async def test_save_message_null_return(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test when repository returns None"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = None
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content="Test message"
                )
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Falha ao salvar mensagem no banco de dados"
        assert result["error_type"] == "database"

    async def test_save_message_update_counter_error_continues(self, mock_message_repository, mock_conversation_repository, sample_conversation, sample_message):
        """Test that counter update errors don't fail the operation"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = sample_message
        mock_conversation_repository.update_conversation.side_effect = Exception("Update error")
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content="Test message"
                )
        
        # Assert - Message save should still succeed
        assert result["success"] is True
        assert result["message_id"] == str(sample_message.id)

    async def test_save_long_message_truncation(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test that long messages are truncated in response"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        long_content = "A" * 200  # 200 characters
        
        long_message = Message(
            id=uuid4(),
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content=long_content,
            created_at=datetime.now()
        )
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = long_message
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await save_message(
                    conversation_id=conversation_id,
                    content=long_content
                )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]["content"]) == 103  # 100 chars + "..."
        assert result["data"]["content"].endswith("...")

    async def test_save_message_tool_instance(self):
        """Test that SaveMessageTool is correctly exported"""
        assert SaveMessageTool == save_message
        assert callable(SaveMessageTool)

    async def test_save_message_concurrent_saves(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test concurrent message saves"""
        # Arrange
        import asyncio
        conversation_id = str(sample_conversation.id)
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_message_repository.save_message.return_value = sample_conversation
        
        with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
            with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                # Act - Simulate concurrent saves
                tasks = [
                    save_message(conversation_id=conversation_id, content=f"Message {i}")
                    for i in range(5)
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assert - All should succeed
        for result in results:
            if isinstance(result, dict):
                assert result.get("success") is True

    async def test_save_message_all_media_types(self, mock_message_repository, mock_conversation_repository, sample_conversation):
        """Test saving messages with all supported media types"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        media_types = ["text", "image", "audio", "video", "document", "sticker"]
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        
        for media_type in media_types:
            message = Message(
                id=uuid4(),
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content=f"{media_type} content",
                media_type=MediaType(media_type),
                created_at=datetime.now()
            )
            mock_message_repository.save_message.return_value = message
            
            with patch('agente.tools.database.save_message.get_message_repository', return_value=mock_message_repository):
                with patch('agente.tools.database.save_message.get_conversation_repository', return_value=mock_conversation_repository):
                    # Act
                    result = await save_message(
                        conversation_id=conversation_id,
                        content=f"{media_type} content",
                        media_type=media_type
                    )
            
            # Assert
            assert result["success"] is True
            assert result["data"]["media_type"] == media_type