"""
Unit tests for update_conversation database tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from agente.tools.database.update_conversation import update_conversation, UpdateConversationTool
from agente.core.types import Conversation


@pytest.fixture
def mock_conversation_repository():
    """Mock conversation repository for tests"""
    repository = AsyncMock()
    repository.get_conversation_by_id = AsyncMock()
    repository.update_conversation = AsyncMock()
    return repository


@pytest.fixture
def mock_session_repository():
    """Mock session repository for tests"""
    repository = AsyncMock()
    repository.update_session_state = AsyncMock()
    return repository


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing"""
    return Conversation(
        id=uuid4(),
        lead_id=uuid4(),
        session_id="session-123",
        total_messages=10,
        current_stage="QUALIFYING",
        sentiment="neutro",
        is_active=True,
        started_at=datetime.now() - timedelta(minutes=30)
    )


@pytest.mark.asyncio
class TestUpdateConversation:
    """Test cases for update_conversation tool"""

    async def test_update_conversation_success(self, mock_conversation_repository, sample_conversation):
        """Test successful conversation update"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        updated_conv = Conversation(
            **sample_conversation.dict(),
            session_id="new-session-456",
            current_stage="QUALIFIED",
            sentiment="positivo"
        )
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.return_value = updated_conv
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(
                conversation_id=conversation_id,
                session_id="new-session-456",
                current_stage="QUALIFIED",
                sentiment="positivo"
            )
        
        # Assert
        assert result["success"] is True
        assert result["conversation_id"] == conversation_id
        assert result["updated_fields"] == ["session_id", "current_stage", "sentiment"]
        assert result["data"]["session_id"] == "new-session-456"
        assert result["data"]["current_stage"] == "QUALIFIED"
        assert result["data"]["sentiment"] == "positivo"
        
        # Verify repository calls
        mock_conversation_repository.get_conversation_by_id.assert_called_once_with(UUID(conversation_id))
        mock_conversation_repository.update_conversation.assert_called_once()

    async def test_update_conversation_end_conversation(self, mock_conversation_repository, sample_conversation):
        """Test ending a conversation"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        ended_at = datetime.now()
        ended_conv = Conversation(
            **sample_conversation.dict(),
            is_active=False,
            ended_at=ended_at
        )
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.return_value = ended_conv
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(
                conversation_id=conversation_id,
                end_conversation=True
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["is_active"] is False
        assert result["data"]["ended_at"] is not None
        assert result["data"]["duration_minutes"] is not None
        
        # Verify update data
        update_data = mock_conversation_repository.update_conversation.call_args[0][1]
        assert update_data["is_active"] is False
        assert "ended_at" in update_data

    async def test_update_conversation_with_state_data(self, mock_conversation_repository, mock_session_repository, sample_conversation):
        """Test updating conversation with session state data"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        state_data = {
            "last_question": "Qual o valor da sua conta?",
            "awaiting_response": True,
            "context": {"stage": "bill_analysis"}
        }
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.return_value = sample_conversation
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            with patch('agente.tools.database.update_conversation.get_session_repository', return_value=mock_session_repository):
                # Act
                result = await update_conversation(
                    conversation_id=conversation_id,
                    state_data=state_data
                )
        
        # Assert
        assert result["success"] is True
        assert result["session_state_updated"] is True
        
        # Verify session update was called
        mock_session_repository.update_session_state.assert_called_once_with(
            sample_conversation.session_id,
            state_data
        )

    async def test_update_conversation_invalid_id(self):
        """Test with invalid conversation ID"""
        # Act
        result = await update_conversation(
            conversation_id="invalid-uuid",
            current_stage="QUALIFIED"
        )
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "ID de conversa inválido"
        assert result["error_type"] == "validation"

    async def test_update_conversation_not_found(self, mock_conversation_repository):
        """Test updating non-existent conversation"""
        # Arrange
        conversation_id = str(uuid4())
        mock_conversation_repository.get_conversation_by_id.return_value = None
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(
                conversation_id=conversation_id,
                current_stage="QUALIFIED"
            )
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Conversa não encontrada"
        assert result["error_type"] == "not_found"

    async def test_update_conversation_invalid_sentiment(self, mock_conversation_repository, sample_conversation):
        """Test with invalid sentiment value"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.return_value = sample_conversation
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(
                conversation_id=conversation_id,
                sentiment="invalid_sentiment"  # Should be positivo, neutro, or negativo
            )
        
        # Assert
        assert result["success"] is True
        # Invalid sentiment should not be in update data
        update_data = mock_conversation_repository.update_conversation.call_args[0][1]
        assert "sentiment" not in update_data

    async def test_update_conversation_no_updates(self, mock_conversation_repository, sample_conversation):
        """Test when no fields need updating"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(conversation_id=conversation_id)
        
        # Assert
        assert result["success"] is True
        assert result["message"] == "Nenhuma atualização necessária"
        
        # Verify update was not called
        mock_conversation_repository.update_conversation.assert_not_called()

    async def test_update_conversation_is_active(self, mock_conversation_repository, sample_conversation):
        """Test updating is_active status"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        updated_conv = Conversation(**sample_conversation.dict(), is_active=False)
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.return_value = updated_conv
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(
                conversation_id=conversation_id,
                is_active=False
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["is_active"] is False

    async def test_update_conversation_database_error(self, mock_conversation_repository, sample_conversation):
        """Test database error during update"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.side_effect = Exception("Database error")
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(
                conversation_id=conversation_id,
                current_stage="QUALIFIED"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao atualizar conversa" in result["error"]
        assert result["error_type"] == "database"

    async def test_update_conversation_session_state_error_continues(self, mock_conversation_repository, mock_session_repository, sample_conversation):
        """Test that session state errors don't fail the operation"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        state_data = {"test": "data"}
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.return_value = sample_conversation
        mock_session_repository.update_session_state.side_effect = Exception("Session error")
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            with patch('agente.tools.database.update_conversation.get_session_repository', return_value=mock_session_repository):
                # Act
                result = await update_conversation(
                    conversation_id=conversation_id,
                    state_data=state_data
                )
        
        # Assert - Should still succeed
        assert result["success"] is True
        assert result["session_state_updated"] is False

    async def test_update_conversation_duration_calculation(self, mock_conversation_repository):
        """Test duration calculation when ending conversation"""
        # Arrange
        started_at = datetime.now() - timedelta(minutes=45, seconds=30)
        ended_at = datetime.now()
        
        conversation = Conversation(
            id=uuid4(),
            lead_id=uuid4(),
            session_id="test-session",
            started_at=started_at,
            is_active=True
        )
        
        ended_conversation = Conversation(
            **conversation.dict(),
            is_active=False,
            ended_at=ended_at
        )
        
        conversation_id = str(conversation.id)
        mock_conversation_repository.get_conversation_by_id.return_value = conversation
        mock_conversation_repository.update_conversation.return_value = ended_conversation
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act
            result = await update_conversation(
                conversation_id=conversation_id,
                end_conversation=True
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["duration_minutes"] is not None
        # Should be approximately 45.5 minutes
        assert 45 <= result["data"]["duration_minutes"] <= 46

    async def test_update_conversation_tool_instance(self):
        """Test that UpdateConversationTool is correctly exported"""
        assert UpdateConversationTool == update_conversation
        assert callable(UpdateConversationTool)

    async def test_update_conversation_concurrent_updates(self, mock_conversation_repository, sample_conversation):
        """Test handling concurrent updates"""
        # Arrange
        import asyncio
        conversation_id = str(sample_conversation.id)
        
        mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
        mock_conversation_repository.update_conversation.return_value = sample_conversation
        
        with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
            # Act - Simulate concurrent updates
            tasks = [
                update_conversation(conversation_id=conversation_id, current_stage=f"STAGE_{i}")
                for i in range(3)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assert - At least one should succeed
        successes = [r for r in results if isinstance(r, dict) and r.get("success")]
        assert len(successes) >= 1

    async def test_update_conversation_all_sentiments(self, mock_conversation_repository, sample_conversation):
        """Test updating with all valid sentiment values"""
        # Arrange
        conversation_id = str(sample_conversation.id)
        valid_sentiments = ["positivo", "neutro", "negativo"]
        
        for sentiment in valid_sentiments:
            updated_conv = Conversation(**sample_conversation.dict(), sentiment=sentiment)
            
            mock_conversation_repository.get_conversation_by_id.return_value = sample_conversation
            mock_conversation_repository.update_conversation.return_value = updated_conv
            
            with patch('agente.tools.database.update_conversation.get_conversation_repository', return_value=mock_conversation_repository):
                # Act
                result = await update_conversation(
                    conversation_id=conversation_id,
                    sentiment=sentiment
                )
            
            # Assert
            assert result["success"] is True
            assert result["data"]["sentiment"] == sentiment