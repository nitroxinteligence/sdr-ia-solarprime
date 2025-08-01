"""
Unit tests for Kommo schedule_activity tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from freezegun import freeze_time

from agente.tools.kommo.schedule_activity import (
    schedule_kommo_activity,
    schedule_follow_up,
    schedule_meeting_reminder,
    ScheduleKommoActivityTool,
    ScheduleFollowUpTool,
    ScheduleMeetingReminderTool
)
from agente.services.kommo_service import KommoAPIError
from agente.core.config import BUSINESS_HOURS_START, BUSINESS_HOURS_END, BUSINESS_DAYS


@pytest.fixture
def mock_kommo_service():
    """Mock Kommo service for tests"""
    service = AsyncMock()
    service.get_lead = AsyncMock()
    service.create_task = AsyncMock()
    service.add_note = AsyncMock()
    return service


@pytest.fixture
def mock_lead():
    """Mock lead data"""
    return {
        "id": 12345,
        "name": "João Silva",
        "status_id": 1001,
        "pipeline_id": 2001
    }


@pytest.mark.asyncio
class TestScheduleKommoActivity:
    """Test cases for schedule_kommo_activity tool"""

    @freeze_time("2024-01-10 14:30:00")  # Wednesday
    async def test_schedule_activity_success(self, mock_kommo_service, mock_lead):
        """Test successful activity scheduling"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {
            "id": 99999,
            "created_at": "2024-01-10T14:30:00Z"
        }
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="call",
                description="Ligar para agendar visita técnica",
                due_date="2024-01-11",
                due_time="14:00",
                duration_minutes=30
            )
        
        # Assert
        assert result["success"] is True
        assert result["task_id"] == 99999
        assert result["lead_id"] == 12345
        assert result["lead_name"] == "João Silva"
        assert result["activity_type"] == "call"
        assert "2024-01-11T14:00" in result["due_datetime"]
        assert result["duration_minutes"] == 30
        
        # Verify task creation
        call_args = mock_kommo_service.create_task.call_args
        assert call_args.kwargs["lead_id"] == 12345
        assert "📞 Ligar para João Silva" in call_args.kwargs["text"]
        assert "Ligar para agendar visita técnica" in call_args.kwargs["text"]
        assert "⏱️ Duração estimada: 30 minutos" in call_args.kwargs["text"]

    async def test_schedule_activity_invalid_type(self):
        """Test scheduling with invalid activity type"""
        # Act
        result = await schedule_kommo_activity(
            lead_id=12345,
            activity_type="invalid_type",
            description="Test"
        )
        
        # Assert
        assert result["success"] is False
        assert "Tipo de atividade inválido" in result["error"]
        assert result["task_id"] is None

    async def test_schedule_activity_lead_not_found(self, mock_kommo_service):
        """Test scheduling when lead doesn't exist"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = KommoAPIError(
            status_code=404,
            message="Lead not found"
        )
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_kommo_activity(
                lead_id=99999,
                activity_type="call",
                description="Test"
            )
        
        # Assert
        assert result["success"] is False
        assert "não encontrado" in result["error"]

    @freeze_time("2024-01-10 14:30:00")  # Wednesday
    async def test_schedule_activity_next_business_day(self, mock_kommo_service, mock_lead):
        """Test scheduling for next business day when no date provided"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="email",
                description="Enviar proposta"
                # No due_date provided
            )
        
        # Assert
        assert result["success"] is True
        # Should be scheduled for Thursday (next business day)
        assert "2024-01-11T10:00" in result["due_datetime"]

    @freeze_time("2024-01-12 14:30:00")  # Friday
    async def test_schedule_activity_skip_weekend(self, mock_kommo_service, mock_lead):
        """Test that weekend days are skipped"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="meeting",
                description="Reunião de apresentação"
                # No due_date, should skip to Monday
            )
        
        # Assert
        assert result["success"] is True
        # Should be scheduled for Monday (skipping weekend)
        assert "2024-01-15T10:00" in result["due_datetime"]

    async def test_schedule_activity_business_hours_adjustment(self, mock_kommo_service, mock_lead):
        """Test business hours adjustment"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Test early morning adjustment
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="call",
                description="Test",
                due_date="2024-01-11",
                due_time="06:00"  # Before business hours
            )
        
        # Assert - should be adjusted to business hours start
        assert result["success"] is True
        assert f"2024-01-11T{BUSINESS_HOURS_START:02d}:00" in result["due_datetime"]
        
        # Test late evening adjustment
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="call",
                description="Test",
                due_date="2024-01-11",
                due_time="20:00"  # After business hours
            )
        
        # Assert - should be adjusted to before business hours end
        assert result["success"] is True
        assert f"2024-01-11T{BUSINESS_HOURS_END-1:02d}:00" in result["due_datetime"]

    async def test_schedule_activity_invalid_date_format(self):
        """Test scheduling with invalid date format"""
        # Act
        result = await schedule_kommo_activity(
            lead_id=12345,
            activity_type="call",
            description="Test",
            due_date="11/01/2024"  # Wrong format
        )
        
        # Assert
        assert result["success"] is False
        assert "Formato de data inválido" in result["error"]

    async def test_schedule_activity_invalid_time_format(self):
        """Test scheduling with invalid time format"""
        # Act
        result = await schedule_kommo_activity(
            lead_id=12345,
            activity_type="call",
            description="Test",
            due_date="2024-01-11",
            due_time="2:30 PM"  # Wrong format
        )
        
        # Assert
        assert result["success"] is False
        assert "Formato de hora inválido" in result["error"]

    async def test_schedule_activity_types(self, mock_kommo_service, mock_lead):
        """Test different activity types and their formatting"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        activity_mappings = {
            "call": "📞 Ligar para",
            "meeting": "🤝 Reunião com",
            "email": "📧 Enviar email para",
            "task": "📋 Tarefa:",
            "follow_up": "🔄 Follow-up com",
            "whatsapp": "📱 WhatsApp para"
        }
        
        for activity_type, expected_prefix in activity_mappings.items():
            with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
                # Act
                result = await schedule_kommo_activity(
                    lead_id=12345,
                    activity_type=activity_type,
                    description="Test description",
                    due_date="2024-01-11"
                )
            
            # Assert
            assert result["success"] is True
            
            # Verify task text format
            call_args = mock_kommo_service.create_task.call_args
            task_text = call_args.kwargs["text"]
            assert expected_prefix in task_text

    async def test_schedule_activity_note_addition(self, mock_kommo_service, mock_lead):
        """Test that a note is added when scheduling activity"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="meeting",
                description="Apresentação comercial",
                due_date="2024-01-11",
                due_time="15:00"
            )
        
        # Assert
        assert result["success"] is True
        
        # Verify note was added
        mock_kommo_service.add_note.assert_called_once()
        call_args = mock_kommo_service.add_note.call_args
        note_text = call_args[0][1]
        assert "✅ Atividade agendada: MEETING" in note_text
        assert "📅 Data/Hora: 11/01/2024 15:00" in note_text
        assert "📝 Descrição: Apresentação comercial" in note_text


@pytest.mark.asyncio
class TestScheduleFollowUp:
    """Test cases for schedule_follow_up tool"""

    @freeze_time("2024-01-10 14:30:00")  # Wednesday
    async def test_schedule_follow_up_next_day(self, mock_kommo_service, mock_lead):
        """Test scheduling follow-up for next day"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_follow_up(
                lead_id=12345,
                days_from_now=1,
                message="Verificar interesse na proposta",
                time="11:00"
            )
        
        # Assert
        assert result["success"] is True
        assert result["activity_type"] == "follow_up"
        assert "2024-01-11T11:00" in result["due_datetime"]

    @freeze_time("2024-01-12 14:30:00")  # Friday
    async def test_schedule_follow_up_skip_weekend(self, mock_kommo_service, mock_lead):
        """Test that follow-up skips weekend days"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_follow_up(
                lead_id=12345,
                days_from_now=3  # Should skip to Wednesday
            )
        
        # Assert
        assert result["success"] is True
        # Friday + 3 business days = Wednesday
        assert "2024-01-17T10:00" in result["due_datetime"]

    async def test_schedule_follow_up_error_handling(self, mock_kommo_service):
        """Test error handling in follow-up scheduling"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Test error")
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_follow_up(
                lead_id=12345
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao agendar follow-up" in result["error"]


@pytest.mark.asyncio
class TestScheduleMeetingReminder:
    """Test cases for schedule_meeting_reminder tool"""

    async def test_schedule_meeting_reminder_success(self, mock_kommo_service, mock_lead):
        """Test successful meeting reminder scheduling"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_meeting_reminder(
                lead_id=12345,
                meeting_datetime="2024-01-15 14:00",
                location="Escritório Central",
                notes="Levar proposta impressa"
            )
        
        # Assert
        assert result["success"] is True
        assert result["activity_type"] == "meeting"
        assert result["location"] == "Escritório Central"
        assert result["meeting_datetime"] == "2024-01-15 14:00"
        # Reminder should be 1 hour before
        assert "2024-01-15T13:00" in result["due_datetime"]
        
        # Verify task details
        call_args = mock_kommo_service.create_task.call_args
        assert call_args.kwargs["duration_minutes"] == 60
        
        # Check description format
        description = call_args.kwargs["description"]
        assert "📍 Local: Escritório Central" in description
        assert "📝 Notas: Levar proposta impressa" in description

    async def test_schedule_meeting_reminder_online(self, mock_kommo_service, mock_lead):
        """Test meeting reminder for online meeting"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.create_task.return_value = {"id": 99999}
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_meeting_reminder(
                lead_id=12345,
                meeting_datetime="2024-01-15 10:00"
                # location defaults to "Online"
            )
        
        # Assert
        assert result["success"] is True
        assert result["location"] == "Online"

    async def test_schedule_meeting_reminder_invalid_datetime(self):
        """Test meeting reminder with invalid datetime format"""
        # Act
        result = await schedule_meeting_reminder(
            lead_id=12345,
            meeting_datetime="15/01/2024 14:00"  # Wrong format
        )
        
        # Assert
        assert result["success"] is False
        assert "Formato de data/hora inválido" in result["error"]

    async def test_schedule_meeting_reminder_error(self, mock_kommo_service):
        """Test error handling in meeting reminder"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Test error")
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await schedule_meeting_reminder(
                lead_id=12345,
                meeting_datetime="2024-01-15 14:00"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao agendar lembrete" in result["error"]

    async def test_tool_instances(self):
        """Test that all tool instances are correctly exported"""
        assert ScheduleKommoActivityTool == schedule_kommo_activity
        assert ScheduleFollowUpTool == schedule_follow_up
        assert ScheduleMeetingReminderTool == schedule_meeting_reminder
        assert callable(ScheduleKommoActivityTool)
        assert callable(ScheduleFollowUpTool)
        assert callable(ScheduleMeetingReminderTool)

    async def test_schedule_activity_api_errors(self, mock_kommo_service, mock_lead):
        """Test handling of various API errors"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        
        # Test rate limit error
        mock_kommo_service.create_task.side_effect = KommoAPIError(
            status_code=429,
            message="Too Many Requests"
        )
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="call",
                description="Test"
            )
        
        assert result["success"] is False
        assert "429" in result["error"] or "Too Many Requests" in result["error"]
        
        # Test authentication error
        mock_kommo_service.create_task.side_effect = KommoAPIError(
            status_code=401,
            message="Unauthorized"
        )
        
        with patch('agente.tools.kommo.schedule_activity.get_kommo_service', return_value=mock_kommo_service):
            result = await schedule_kommo_activity(
                lead_id=12345,
                activity_type="call",
                description="Test"
            )
        
        assert result["success"] is False
        assert "401" in result["error"] or "Unauthorized" in result["error"]