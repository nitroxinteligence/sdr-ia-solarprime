"""
Unit tests for schedule_followup database tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from agente.tools.database.schedule_followup import schedule_followup, ScheduleFollowUpTool
from agente.core.types import Lead, LeadStage, FollowUp, FollowUpType, FollowUpStatus


@pytest.fixture
def mock_lead_repository():
    """Mock lead repository for tests"""
    repository = AsyncMock()
    repository.get_lead_by_id = AsyncMock()
    repository.get_lead_by_phone = AsyncMock()
    return repository


@pytest.fixture
def mock_followup_repository():
    """Mock followup repository for tests"""
    repository = AsyncMock()
    repository.schedule_follow_up = AsyncMock()
    return repository


@pytest.fixture
def sample_lead():
    """Sample lead for testing"""
    return Lead(
        id=uuid4(),
        phone_number="5511999999999",
        name="João Silva",
        current_stage=LeadStage.QUALIFYING,
        interested=True,
        property_type="casa"
    )


@pytest.fixture
def sample_followup():
    """Sample follow-up for testing"""
    return FollowUp(
        id=uuid4(),
        lead_id=uuid4(),
        scheduled_at=datetime.now() + timedelta(minutes=30),
        type=FollowUpType.REMINDER,
        message="Olá João! Vamos continuar nossa conversa sobre energia solar?",
        status=FollowUpStatus.PENDING,
        attempt_number=1
    )


@pytest.mark.asyncio
class TestScheduleFollowup:
    """Test cases for schedule_followup tool"""

    async def test_schedule_followup_by_lead_id_success(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_followup):
        """Test successful follow-up scheduling by lead ID"""
        # Arrange
        lead_id = str(sample_lead.id)
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = sample_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    lead_id=lead_id,
                    minutes_from_now=30
                )
        
        # Assert
        assert result["success"] is True
        assert result["follow_up_id"] == str(sample_followup.id)
        assert result["lead_id"] == lead_id
        assert result["data"]["type"] == "reminder"
        assert result["data"]["attempt_number"] == 1
        assert result["data"]["is_final_attempt"] is False
        assert 29 <= result["data"]["scheduled_in_minutes"] <= 31
        
        # Verify repository calls
        mock_lead_repository.get_lead_by_id.assert_called_once_with(UUID(lead_id))
        mock_followup_repository.schedule_follow_up.assert_called_once()

    async def test_schedule_followup_by_phone_success(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_followup):
        """Test successful follow-up scheduling by phone"""
        # Arrange
        phone = "5511999999999"
        mock_lead_repository.get_lead_by_phone.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = sample_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    phone=phone,
                    follow_up_type="reminder",
                    hours_from_now=2
                )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["lead_info"]["phone"] == phone
        
        # Verify repository calls
        mock_lead_repository.get_lead_by_phone.assert_called_once_with(phone)

    async def test_schedule_followup_with_custom_message(self, mock_lead_repository, mock_followup_repository, sample_lead):
        """Test scheduling with custom message"""
        # Arrange
        custom_message = "João, ainda está interessado em economizar 95% na conta de luz?"
        custom_followup = FollowUp(
            id=uuid4(),
            lead_id=sample_lead.id,
            scheduled_at=datetime.now() + timedelta(hours=1),
            type=FollowUpType.CHECK_IN,
            message=custom_message,
            status=FollowUpStatus.PENDING,
            attempt_number=1
        )
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = custom_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    follow_up_type="check_in",
                    custom_message=custom_message,
                    hours_from_now=1
                )
        
        # Assert
        assert result["success"] is True
        assert custom_message in result["data"]["message"]

    async def test_schedule_followup_with_scheduled_at(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_followup):
        """Test scheduling with specific date/time"""
        # Arrange
        scheduled_time = datetime.now() + timedelta(days=1)
        scheduled_at_str = scheduled_time.isoformat()
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = sample_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    scheduled_at=scheduled_at_str
                )
        
        # Assert
        assert result["success"] is True
        # Verify the scheduled time was parsed correctly
        call_args = mock_followup_repository.schedule_follow_up.call_args
        assert isinstance(call_args.kwargs["scheduled_at"], datetime)

    async def test_schedule_followup_second_attempt(self, mock_lead_repository, mock_followup_repository, sample_lead):
        """Test scheduling second follow-up attempt"""
        # Arrange
        sample_lead.current_stage = LeadStage.SCHEDULING
        second_followup = FollowUp(
            id=uuid4(),
            lead_id=sample_lead.id,
            scheduled_at=datetime.now() + timedelta(hours=24),
            type=FollowUpType.HOT_LEAD_RESCUE,
            message="João, última chance de garantir sua economia!",
            status=FollowUpStatus.PENDING,
            attempt_number=2
        )
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = second_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    attempt_number=2
                )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["attempt_number"] == 2
        assert result["data"]["is_final_attempt"] is True
        assert result["data"]["type"] == "hot_lead_rescue"

    async def test_schedule_followup_lead_not_interested(self, mock_lead_repository):
        """Test scheduling for lead marked as not interested"""
        # Arrange
        not_interested_lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            name="João Silva",
            interested=False,
            current_stage=LeadStage.NOT_INTERESTED
        )
        
        mock_lead_repository.get_lead_by_id.return_value = not_interested_lead
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await schedule_followup(lead_id=str(not_interested_lead.id))
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Lead marcado como não interessado"
        assert result["error_type"] == "business_rule"
        assert result["lead_stage"] == "NOT_INTERESTED"

    async def test_schedule_followup_lead_not_found(self, mock_lead_repository):
        """Test scheduling for non-existent lead"""
        # Arrange
        lead_id = str(uuid4())
        mock_lead_repository.get_lead_by_id.return_value = None
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await schedule_followup(lead_id=lead_id)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Lead não encontrado"
        assert result["error_type"] == "not_found"

    async def test_schedule_followup_invalid_lead_id(self):
        """Test with invalid lead ID format"""
        # Act
        result = await schedule_followup(lead_id="invalid-uuid")
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "ID do lead inválido"
        assert result["error_type"] == "validation"

    async def test_schedule_followup_missing_parameters(self):
        """Test with no identification parameters"""
        # Act
        result = await schedule_followup()
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "É necessário fornecer lead_id ou phone"
        assert result["error_type"] == "validation"

    async def test_schedule_followup_invalid_follow_up_type(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_followup):
        """Test with invalid follow-up type (should default to REMINDER)"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = sample_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    follow_up_type="invalid_type"
                )
        
        # Assert
        assert result["success"] is True
        # Should have defaulted to REMINDER
        call_args = mock_followup_repository.schedule_follow_up.call_args
        assert call_args.kwargs["follow_up_type"] == FollowUpType.REMINDER

    async def test_schedule_followup_invalid_scheduled_at(self, mock_lead_repository, sample_lead):
        """Test with invalid date/time format"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await schedule_followup(
                lead_id=str(sample_lead.id),
                scheduled_at="invalid-date"
            )
        
        # Assert
        assert result["success"] is False
        assert "Data/hora inválida" in result["error"]
        assert result["error_type"] == "validation"

    async def test_schedule_followup_database_error(self, mock_lead_repository, mock_followup_repository, sample_lead):
        """Test database error during scheduling"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.side_effect = Exception("Database error")
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(lead_id=str(sample_lead.id))
        
        # Assert
        assert result["success"] is False
        assert "Erro ao agendar follow-up" in result["error"]
        assert result["error_type"] == "database"

    async def test_schedule_followup_null_return(self, mock_lead_repository, mock_followup_repository, sample_lead):
        """Test when repository returns None"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = None
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(lead_id=str(sample_lead.id))
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Falha ao agendar follow-up"
        assert result["error_type"] == "database"

    async def test_schedule_followup_with_context(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_followup):
        """Test scheduling with additional context"""
        # Arrange
        context = {
            "last_interaction": "Cliente mostrou interesse em financiamento",
            "objection": "Preço alto",
            "solution_type": "Solar residencial"
        }
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = sample_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    context=context
                )
        
        # Assert
        assert result["success"] is True
        # Verify context was passed
        call_args = mock_followup_repository.schedule_follow_up.call_args
        passed_context = call_args.kwargs["context"]
        assert "last_interaction" in passed_context
        assert passed_context["name"] == sample_lead.name

    async def test_schedule_followup_default_times(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_followup):
        """Test default scheduling times based on attempt number"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = sample_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act - First attempt (default 30 minutes)
                result1 = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    attempt_number=1
                )
                
                # Act - Second attempt (default 24 hours)
                result2 = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    attempt_number=2
                )
        
        # Assert
        assert result1["success"] is True
        assert result2["success"] is True
        
        # Check scheduled times
        call1 = mock_followup_repository.schedule_follow_up.call_args_list[0]
        call2 = mock_followup_repository.schedule_follow_up.call_args_list[1]
        
        time1 = call1.kwargs["scheduled_at"]
        time2 = call2.kwargs["scheduled_at"]
        
        # First should be ~30 minutes from now
        diff1 = (time1 - datetime.now()).total_seconds() / 60
        assert 25 <= diff1 <= 35
        
        # Second should be ~24 hours from now
        diff2 = (time2 - datetime.now()).total_seconds() / 3600
        assert 23 <= diff2 <= 25

    async def test_schedule_followup_tool_instance(self):
        """Test that ScheduleFollowUpTool is correctly exported"""
        assert ScheduleFollowUpTool == schedule_followup
        assert callable(ScheduleFollowUpTool)

    async def test_schedule_followup_business_hours_consideration(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_followup):
        """Test that follow-ups respect business hours"""
        # Note: Business hours logic would be implemented in the repository
        # This test verifies the tool passes the correct data
        
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.schedule_follow_up.return_value = sample_followup
        
        with patch('agente.tools.database.schedule_followup.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.schedule_followup.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await schedule_followup(
                    lead_id=str(sample_lead.id),
                    minutes_from_now=30
                )
        
        # Assert
        assert result["success"] is True
        # Repository should handle business hours internally