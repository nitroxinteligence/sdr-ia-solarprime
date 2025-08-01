"""
Unit tests for update_meeting calendar tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agente.tools.calendar.update_meeting import update_meeting, UpdateMeetingTool
from agente.core.types import CalendarEvent


@pytest.fixture
def mock_calendar_service():
    """Mock Calendar service for tests"""
    service = AsyncMock()
    service.is_available = MagicMock(return_value=True)
    service.update_event = AsyncMock()
    return service


@pytest.mark.asyncio
class TestUpdateMeeting:
    """Test cases for update_meeting tool"""

    async def test_update_meeting_title_success(self, mock_calendar_service):
        """Test successful meeting title update"""
        # Arrange
        meeting_id = "event-123"
        new_title = "Reunião Solar Atualizada - João Silva"
        timezone = "America/Sao_Paulo"
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title=new_title,
            description="Reunião sobre energia solar",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["joao@example.com"],
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                title=new_title
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["title"] == new_title
        assert result["meeting"]["id"] == meeting_id
        assert len(result["changes"]) == 1
        assert "Título alterado para" in result["changes"][0]
        
        # Verify call
        mock_calendar_service.update_event.assert_called_once_with(
            event_id=meeting_id,
            updates={"title": new_title}
        )

    async def test_update_meeting_no_service(self, mock_calendar_service):
        """Test when Google Calendar service is not available"""
        # Arrange
        mock_calendar_service.is_available.return_value = False
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id="event-123",
                title="New Title"
            )
        
        # Assert
        assert result["success"] is False
        assert "não está disponível" in result["error"]
        assert result["meeting"] is None
        assert result["changes"] == []

    async def test_update_meeting_date_and_time(self, mock_calendar_service):
        """Test updating meeting date and time"""
        # Arrange
        meeting_id = "event-123"
        new_date = "2024-01-20"
        new_time = "10:00"
        timezone = "America/Sao_Paulo"
        new_start = datetime(2024, 1, 20, 10, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar",
            description="Reunião remarcada",
            start=new_start,
            end=new_start + timedelta(hours=1),
            attendees=["cliente@example.com"],
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                date=new_date,
                start_time=new_time,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["date"] == "2024-01-20"
        assert result["meeting"]["start_time"] == "10:00"
        assert "Data/hora alterada para" in result["changes"][0]

    async def test_update_meeting_missing_date_or_time(self, mock_calendar_service):
        """Test that both date and time must be provided together"""
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Test with only date
            result = await update_meeting(
                meeting_id="event-123",
                date="2024-01-20"
                # Missing start_time
            )
        
        assert result["success"] is False
        assert "forneça tanto 'date' quanto 'start_time'" in result["error"]
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Test with only time
            result = await update_meeting(
                meeting_id="event-123",
                start_time="10:00"
                # Missing date
            )
        
        assert result["success"] is False
        assert "forneça tanto 'date' quanto 'start_time'" in result["error"]

    async def test_update_meeting_invalid_date_format(self, mock_calendar_service):
        """Test with invalid date/time format"""
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id="event-123",
                date="20/01/2024",  # Wrong format
                start_time="10:00"
            )
        
        # Assert
        assert result["success"] is False
        assert "Formato de data/hora inválido" in result["error"]
        assert "YYYY-MM-DD" in result["error"]

    async def test_update_meeting_with_duration(self, mock_calendar_service):
        """Test updating meeting duration"""
        # Arrange
        meeting_id = "event-123"
        new_date = "2024-01-20"
        new_time = "14:00"
        new_duration = 90  # 1.5 hours
        timezone = "America/Sao_Paulo"
        new_start = datetime(2024, 1, 20, 14, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Estendida",
            description="Reunião com duração atualizada",
            start=new_start,
            end=new_start + timedelta(minutes=new_duration),
            attendees=["cliente@example.com"],
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                date=new_date,
                start_time=new_time,
                duration_minutes=new_duration,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["duration_minutes"] == 90
        assert result["meeting"]["end_time"] == "15:30"
        assert "Duração alterada para" in str(result["changes"])

    async def test_update_meeting_sunday_rejection(self, mock_calendar_service):
        """Test that meetings cannot be moved to Sundays"""
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act - January 21, 2024 is a Sunday
            result = await update_meeting(
                meeting_id="event-123",
                date="2024-01-21",
                start_time="10:00"
            )
        
        # Assert
        assert result["success"] is False
        assert "domingos" in result["error"]

    async def test_update_meeting_saturday_hours(self, mock_calendar_service):
        """Test Saturday business hours restriction when updating"""
        # Test moving to Saturday outside business hours
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            result = await update_meeting(
                meeting_id="event-123",
                date="2024-01-20",  # Saturday
                start_time="14:00"  # After 1 PM
            )
        
        assert result["success"] is False
        assert "sábados" in result["error"]
        assert "8h e 13h" in result["error"]

    async def test_update_meeting_weekday_hours(self, mock_calendar_service):
        """Test weekday business hours restriction when updating"""
        # Test moving to too early on weekday
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            result = await update_meeting(
                meeting_id="event-123",
                date="2024-01-22",  # Monday
                start_time="07:00"  # Before 8 AM
            )
        
        assert result["success"] is False
        assert "8h e 18h" in result["error"]

    async def test_update_meeting_description(self, mock_calendar_service):
        """Test updating meeting description"""
        # Arrange
        meeting_id = "event-123"
        new_description = "Atualização: Incluir discussão sobre baterias solares"
        timezone = "America/Sao_Paulo"
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar",
            description=new_description,
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["cliente@example.com"],
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                description=new_description
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["description"] == new_description
        assert "Descrição atualizada" in result["changes"][0]

    async def test_update_meeting_attendees(self, mock_calendar_service):
        """Test updating meeting attendees"""
        # Arrange
        meeting_id = "event-123"
        new_attendees = ["cliente@example.com", "vendedor@solarprime.com", "tecnico@solarprime.com"]
        timezone = "America/Sao_Paulo"
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar",
            description="Reunião com equipe completa",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=new_attendees,
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                attendees=new_attendees
            )
        
        # Assert
        assert result["success"] is True
        assert len(result["meeting"]["attendees"]) == 3
        assert "3 convidados" in result["changes"][0]

    async def test_update_meeting_multiple_fields(self, mock_calendar_service):
        """Test updating multiple fields at once"""
        # Arrange
        meeting_id = "event-123"
        new_title = "Reunião Solar Remarcada"
        new_date = "2024-01-25"
        new_time = "16:00"
        new_duration = 45
        new_attendees = ["novo_cliente@example.com"]
        timezone = "America/Sao_Paulo"
        new_start = datetime(2024, 1, 25, 16, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title=new_title,
            description="Reunião completamente atualizada",
            start=new_start,
            end=new_start + timedelta(minutes=new_duration),
            attendees=new_attendees,
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                title=new_title,
                date=new_date,
                start_time=new_time,
                duration_minutes=new_duration,
                attendees=new_attendees
            )
        
        # Assert
        assert result["success"] is True
        assert len(result["changes"]) >= 3  # Title, date/time, duration, attendees
        assert result["meeting"]["title"] == new_title
        assert result["meeting"]["date"] == "2024-01-25"
        assert result["meeting"]["start_time"] == "16:00"
        assert result["meeting"]["duration_minutes"] == 45

    async def test_update_meeting_no_changes(self, mock_calendar_service):
        """Test when no changes are specified"""
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act - No update fields provided
            result = await update_meeting(meeting_id="event-123")
        
        # Assert
        assert result["success"] is False
        assert "Nenhuma alteração foi especificada" in result["error"]

    async def test_update_meeting_exception_handling(self, mock_calendar_service):
        """Test exception handling during meeting update"""
        # Arrange
        mock_calendar_service.update_event.side_effect = Exception("Google Calendar API error")
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id="event-123",
                title="New Title"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao atualizar reunião" in result["error"]
        assert "Google Calendar API error" in result["error"]

    async def test_update_meeting_update_fails(self, mock_calendar_service):
        """Test when calendar service returns None for update"""
        # Arrange
        mock_calendar_service.update_event.return_value = None
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id="event-123",
                title="New Title"
            )
        
        # Assert
        assert result["success"] is False
        assert "Falha ao atualizar reunião" in result["error"]

    async def test_update_meeting_america_recife_timezone(self, mock_calendar_service):
        """Test updating meeting with America/Recife timezone"""
        # Arrange
        meeting_id = "event-123"
        new_date = "2024-01-25"
        new_time = "11:00"
        timezone = "America/Recife"
        new_start = datetime(2024, 1, 25, 11, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar Recife",
            description="Reunião em Recife",
            start=new_start,
            end=new_start + timedelta(hours=1),
            attendees=[],
            meet_link="https://meet.google.com/recife",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                date=new_date,
                start_time=new_time,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["timezone"] == timezone

    async def test_update_meeting_tool_instance(self):
        """Test that UpdateMeetingTool is correctly exported"""
        assert UpdateMeetingTool == update_meeting
        assert callable(UpdateMeetingTool)

    async def test_update_meeting_residential_to_commercial_duration(self, mock_calendar_service):
        """Test updating a 30-minute residential meeting to 60-minute commercial"""
        # Arrange
        meeting_id = "event-residential"
        new_duration = 60  # Upgrading to commercial duration
        timezone = "America/Sao_Paulo"
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar - Upgrade Comercial",
            description="Cliente mudou para proposta comercial",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["empresa@example.com"],
            meet_link="https://meet.google.com/commercial",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                date="2024-01-15",
                start_time="14:00",
                duration_minutes=new_duration,
                title="Reunião Solar - Upgrade Comercial"
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["duration_minutes"] == 60
        assert "Duração alterada para: 60 minutos" in str(result["changes"])

    async def test_update_meeting_success_message(self, mock_calendar_service):
        """Test the success message format"""
        # Arrange
        meeting_id = "event-123"
        timezone = "America/Sao_Paulo"
        
        # Mock updated event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Updated Meeting",
            description="Updated description",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["test@example.com"],
            meet_link="https://meet.google.com/test",
            status="confirmed"
        )
        mock_calendar_service.update_event.return_value = mock_event
        
        with patch('agente.tools.calendar.update_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await update_meeting(
                meeting_id=meeting_id,
                title="Updated Meeting",
                description="Updated description"
            )
        
        # Assert
        assert result["success"] is True
        assert "Reunião atualizada com sucesso" in result["message"]
        assert "2 alterações realizadas" in result["message"]