"""
Unit tests for create_meeting calendar tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agente.tools.calendar.create_meeting import create_meeting, CreateMeetingTool
from agente.core.types import CalendarEvent, CalendarSlot


@pytest.fixture
def mock_calendar_service():
    """Mock Calendar service for tests"""
    service = AsyncMock()
    service.is_available = MagicMock(return_value=True)
    service.check_availability = AsyncMock()
    service.create_meeting = AsyncMock()
    return service


@pytest.mark.asyncio
class TestCreateMeeting:
    """Test cases for create_meeting tool"""

    async def test_create_meeting_success(self, mock_calendar_service):
        """Test successful meeting creation"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        time_str = "14:00"
        start_datetime = datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability check - slot is available
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=datetime(2024, 1, 15, 13, 0, tzinfo=ZoneInfo(timezone)),
                end=datetime(2024, 1, 15, 16, 0, tzinfo=ZoneInfo(timezone)),
                duration_minutes=180
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-123",
            title="Reunião Solar - João Silva",
            description="Reunião sobre energia solar",
            start=start_datetime,
            end=start_datetime + timedelta(hours=1),
            attendees=["joao@example.com"],
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Reunião Solar - João Silva",
                date=date_str,
                start_time=time_str,
                duration_minutes=60,
                description="Reunião sobre energia solar",
                attendees=["joao@example.com"],
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["id"] == "event-123"
        assert result["meeting"]["title"] == "Reunião Solar - João Silva"
        assert result["meeting"]["date"] == "2024-01-15"
        assert result["meeting"]["start_time"] == "14:00"
        assert result["meeting"]["end_time"] == "15:00"
        assert result["meeting"]["duration_minutes"] == 60
        assert result["meet_link"] == "https://meet.google.com/abc-defg-hij"
        assert "calendar.google.com" in result["calendar_link"]
        
        # Verify calls
        mock_calendar_service.check_availability.assert_called_once()
        mock_calendar_service.create_meeting.assert_called_once()

    async def test_create_meeting_no_service(self, mock_calendar_service):
        """Test when Google Calendar service is not available"""
        # Arrange
        mock_calendar_service.is_available.return_value = False
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-15",
                start_time="14:00"
            )
        
        # Assert
        assert result["success"] is False
        assert "não está disponível" in result["error"]
        assert result["meeting"] is None
        assert result["meet_link"] is None

    async def test_create_meeting_invalid_date_format(self, mock_calendar_service):
        """Test with invalid date format"""
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Test Meeting",
                date="15/01/2024",  # Wrong format
                start_time="14:00"
            )
        
        # Assert
        assert result["success"] is False
        assert "Formato de data/hora inválido" in result["error"]
        assert "YYYY-MM-DD" in result["error"]

    async def test_create_meeting_invalid_time_format(self, mock_calendar_service):
        """Test with invalid time format"""
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-15",
                start_time="2PM"  # Wrong format
            )
        
        # Assert
        assert result["success"] is False
        assert "Formato de data/hora inválido" in result["error"]
        assert "HH:MM" in result["error"]

    async def test_create_meeting_sunday_rejection(self, mock_calendar_service):
        """Test that meetings cannot be scheduled on Sundays"""
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act - January 14, 2024 is a Sunday
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-14",
                start_time="10:00"
            )
        
        # Assert
        assert result["success"] is False
        assert "domingos" in result["error"]

    async def test_create_meeting_saturday_hours(self, mock_calendar_service):
        """Test Saturday business hours restriction"""
        # Test too early on Saturday
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-13",  # Saturday
                start_time="07:00"
            )
        
        assert result["success"] is False
        assert "sábados" in result["error"]
        assert "8h e 13h" in result["error"]
        
        # Test too late on Saturday
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-13",  # Saturday
                start_time="14:00"
            )
        
        assert result["success"] is False
        assert "sábados" in result["error"]

    async def test_create_meeting_weekday_hours(self, mock_calendar_service):
        """Test weekday business hours restriction"""
        # Test too early on weekday
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-15",  # Monday
                start_time="07:00"
            )
        
        assert result["success"] is False
        assert "8h e 18h" in result["error"]
        
        # Test too late on weekday
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-15",  # Monday
                start_time="19:00"
            )
        
        assert result["success"] is False
        assert "8h e 18h" in result["error"]

    async def test_create_meeting_time_conflict(self, mock_calendar_service):
        """Test when requested time slot is not available"""
        # Arrange
        timezone = "America/Sao_Paulo"
        mock_calendar_service.check_availability.return_value = []  # No slots available
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-15",
                start_time="14:00",
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is False
        assert "não disponível" in result["error"]
        assert "check_availability" in result["suggestion"]

    async def test_create_meeting_30_minute_duration(self, mock_calendar_service):
        """Test creating a 30-minute meeting for residential solar"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        time_str = "10:00"
        start_datetime = datetime(2024, 1, 15, 10, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime,
                end=start_datetime + timedelta(hours=1),
                duration_minutes=60
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-456",
            title="Solar Residencial - Maria Santos",
            description="Consulta sobre energia solar residencial",
            start=start_datetime,
            end=start_datetime + timedelta(minutes=30),
            attendees=["maria@example.com"],
            meet_link="https://meet.google.com/xyz-abcd-efg",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Solar Residencial - Maria Santos",
                date=date_str,
                start_time=time_str,
                duration_minutes=30,  # Residential meeting duration
                attendees=["maria@example.com"]
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["duration_minutes"] == 30
        assert result["meeting"]["end_time"] == "10:30"

    async def test_create_meeting_default_description(self, mock_calendar_service):
        """Test that default description is added when not provided"""
        # Arrange
        timezone = "America/Sao_Paulo"
        start_datetime = datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime - timedelta(hours=1),
                end=start_datetime + timedelta(hours=2),
                duration_minutes=180
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-789",
            title="Test Meeting",
            description="Reunião: Test Meeting\n\nAgendada via SDR IA SolarPrime",
            start=start_datetime,
            end=start_datetime + timedelta(hours=1),
            attendees=[],
            meet_link="https://meet.google.com/test",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-15",
                start_time="14:00"
                # No description provided
            )
        
        # Assert
        assert result["success"] is True
        assert "SDR IA SolarPrime" in result["meeting"]["description"]

    async def test_create_meeting_multiple_attendees(self, mock_calendar_service):
        """Test creating meeting with multiple attendees"""
        # Arrange
        timezone = "America/Sao_Paulo"
        attendees = ["cliente@example.com", "vendedor@solarprime.com", "tecnico@solarprime.com"]
        start_datetime = datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime - timedelta(hours=1),
                end=start_datetime + timedelta(hours=2),
                duration_minutes=180
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-multi",
            title="Reunião Técnica Solar",
            description="Discussão técnica sobre instalação",
            start=start_datetime,
            end=start_datetime + timedelta(hours=1),
            attendees=attendees,
            meet_link="https://meet.google.com/multi",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Reunião Técnica Solar",
                date="2024-01-15",
                start_time="14:00",
                attendees=attendees,
                description="Discussão técnica sobre instalação"
            )
        
        # Assert
        assert result["success"] is True
        assert len(result["meeting"]["attendees"]) == 3
        assert all(email in result["meeting"]["attendees"] for email in attendees)

    async def test_create_meeting_america_recife_timezone(self, mock_calendar_service):
        """Test creating meeting with America/Recife timezone"""
        # Arrange
        timezone = "America/Recife"
        date_str = "2024-01-15"
        time_str = "09:00"
        start_datetime = datetime(2024, 1, 15, 9, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime - timedelta(hours=1),
                end=start_datetime + timedelta(hours=2),
                duration_minutes=180
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-recife",
            title="Reunião Solar Recife",
            description="Reunião em Recife",
            start=start_datetime,
            end=start_datetime + timedelta(hours=1),
            attendees=[],
            meet_link="https://meet.google.com/recife",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Reunião Solar Recife",
                date=date_str,
                start_time=time_str,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["timezone"] == timezone

    async def test_create_meeting_exception_handling(self, mock_calendar_service):
        """Test exception handling during meeting creation"""
        # Arrange
        timezone = "America/Sao_Paulo"
        start_datetime = datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability check passes
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime - timedelta(hours=1),
                end=start_datetime + timedelta(hours=2),
                duration_minutes=180
            )
        ]
        
        # But creation fails
        mock_calendar_service.create_meeting.side_effect = Exception("Google Calendar API error")
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Test Meeting",
                date="2024-01-15",
                start_time="14:00"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao criar reunião" in result["error"]
        assert "Google Calendar API error" in result["error"]

    async def test_create_meeting_edge_case_end_of_business_hour(self, mock_calendar_service):
        """Test creating meeting that ends exactly at business hour limit"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        time_str = "17:00"  # 5 PM start
        duration = 60  # Would end at 6 PM (business hour limit)
        start_datetime = datetime(2024, 1, 15, 17, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime,
                end=start_datetime + timedelta(hours=1),
                duration_minutes=60
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-edge",
            title="End of Day Meeting",
            description="Meeting at end of business hours",
            start=start_datetime,
            end=start_datetime + timedelta(minutes=duration),
            attendees=[],
            meet_link="https://meet.google.com/edge",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="End of Day Meeting",
                date=date_str,
                start_time=time_str,
                duration_minutes=duration
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["end_time"] == "18:00"

    async def test_create_meeting_buffer_time_consideration(self, mock_calendar_service):
        """Test that availability check considers buffer time between meetings"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        time_str = "14:00"
        start_datetime = datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability - exactly fits the requested slot
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime,
                end=start_datetime + timedelta(minutes=60),
                duration_minutes=60
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-buffer",
            title="Buffer Test Meeting",
            description="Testing buffer considerations",
            start=start_datetime,
            end=start_datetime + timedelta(minutes=60),
            attendees=[],
            meet_link="https://meet.google.com/buffer",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Buffer Test Meeting",
                date=date_str,
                start_time=time_str,
                duration_minutes=60
            )
        
        # Assert
        assert result["success"] is True
        # Verify the exact requested time was used
        assert result["meeting"]["start_time"] == "14:00"
        assert result["meeting"]["end_time"] == "15:00"

    async def test_create_meeting_tool_instance(self):
        """Test that CreateMeetingTool is correctly exported"""
        assert CreateMeetingTool == create_meeting
        assert callable(CreateMeetingTool)

    async def test_create_meeting_without_meet_link(self, mock_calendar_service):
        """Test handling when Google Meet link is not generated"""
        # Arrange
        timezone = "America/Sao_Paulo"
        start_datetime = datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime - timedelta(hours=1),
                end=start_datetime + timedelta(hours=2),
                duration_minutes=180
            )
        ]
        
        # Mock created event without meet link
        mock_event = CalendarEvent(
            id="event-no-meet",
            title="Meeting Without Meet",
            description="No Google Meet link",
            start=start_datetime,
            end=start_datetime + timedelta(hours=1),
            attendees=[],
            meet_link=None,  # No meet link
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Meeting Without Meet",
                date="2024-01-15",
                start_time="14:00"
            )
        
        # Assert
        assert result["success"] is True
        assert result["meet_link"] is None

    async def test_create_meeting_commercial_solar_duration(self, mock_calendar_service):
        """Test creating a 60-minute meeting for commercial solar"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        time_str = "15:00"
        start_datetime = datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone))
        
        # Mock availability
        mock_calendar_service.check_availability.return_value = [
            CalendarSlot(
                start=start_datetime - timedelta(hours=1),
                end=start_datetime + timedelta(hours=2),
                duration_minutes=180
            )
        ]
        
        # Mock created event
        mock_event = CalendarEvent(
            id="event-commercial",
            title="Solar Comercial - Empresa XYZ",
            description="Proposta solar para empresa",
            start=start_datetime,
            end=start_datetime + timedelta(minutes=60),
            attendees=["empresa@example.com"],
            meet_link="https://meet.google.com/commercial",
            status="confirmed"
        )
        mock_calendar_service.create_meeting.return_value = mock_event
        
        with patch('agente.tools.calendar.create_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await create_meeting(
                title="Solar Comercial - Empresa XYZ",
                date=date_str,
                start_time=time_str,
                duration_minutes=60,  # Commercial meeting duration
                attendees=["empresa@example.com"],
                description="Proposta solar para empresa"
            )
        
        # Assert
        assert result["success"] is True
        assert result["meeting"]["duration_minutes"] == 60
        assert "Comercial" in result["meeting"]["title"]