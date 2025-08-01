"""
Unit tests for cancel_meeting calendar tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agente.tools.calendar.cancel_meeting import cancel_meeting, CancelMeetingTool
from agente.core.types import CalendarEvent


@pytest.fixture
def mock_calendar_service():
    """Mock Calendar service for tests"""
    service = AsyncMock()
    service.is_available = MagicMock(return_value=True)
    service.get_calendar_events = AsyncMock()
    service.cancel_event = AsyncMock()
    return service


@pytest.mark.asyncio
class TestCancelMeeting:
    """Test cases for cancel_meeting tool"""

    async def test_cancel_meeting_success(self, mock_calendar_service):
        """Test successful meeting cancellation"""
        # Arrange
        meeting_id = "event-123"
        reason = "Cliente solicitou reagendamento"
        timezone = "America/Sao_Paulo"
        
        # Mock existing event for info retrieval
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar - João Silva",
            description="Reunião sobre energia solar",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["joao@example.com", "vendedor@solarprime.com"],
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                reason=reason,
                send_notifications=True
            )
        
        # Assert
        assert result["success"] is True
        assert result["cancelled"] is True
        assert result["meeting_id"] == meeting_id
        assert result["reason"] == reason
        assert result["notifications_sent"] is True
        assert "Participantes foram notificados" in result["message"]
        
        # Verify meeting info was captured
        assert "cancelled_meeting" in result
        assert result["cancelled_meeting"]["title"] == "Reunião Solar - João Silva"
        assert result["cancelled_meeting"]["attendees"] == 2
        
        # Verify calls
        mock_calendar_service.cancel_event.assert_called_once_with(
            event_id=meeting_id,
            send_notifications=True
        )

    async def test_cancel_meeting_no_service(self, mock_calendar_service):
        """Test when Google Calendar service is not available"""
        # Arrange
        mock_calendar_service.is_available.return_value = False
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id="event-123")
        
        # Assert
        assert result["success"] is False
        assert result["cancelled"] is False
        assert "não está disponível" in result["error"]
        assert result["notifications_sent"] is False

    async def test_cancel_meeting_without_reason(self, mock_calendar_service):
        """Test cancelling meeting without providing reason"""
        # Arrange
        meeting_id = "event-456"
        mock_calendar_service.get_calendar_events.return_value = []  # No event info
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                send_notifications=False
            )
        
        # Assert
        assert result["success"] is True
        assert result["cancelled"] is True
        assert result["reason"] == "Não especificado"
        assert result["notifications_sent"] is False
        assert "Reunião cancelada com sucesso" in result["message"]
        assert "notificados" not in result["message"]

    async def test_cancel_meeting_without_notifications(self, mock_calendar_service):
        """Test cancelling meeting without sending notifications"""
        # Arrange
        meeting_id = "event-789"
        mock_calendar_service.get_calendar_events.return_value = []
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                reason="Teste interno",
                send_notifications=False
            )
        
        # Assert
        assert result["success"] is True
        assert result["notifications_sent"] is False
        assert "notificados" not in result["message"]

    async def test_cancel_meeting_event_not_found(self, mock_calendar_service):
        """Test cancelling when event info cannot be retrieved"""
        # Arrange
        meeting_id = "event-not-found"
        mock_calendar_service.get_calendar_events.return_value = []  # Event not found
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id=meeting_id)
        
        # Assert
        assert result["success"] is True
        assert result["cancelled"] is True
        assert "cancelled_meeting" not in result  # No meeting info available

    async def test_cancel_meeting_info_retrieval_error(self, mock_calendar_service):
        """Test when error occurs retrieving meeting info but cancellation proceeds"""
        # Arrange
        meeting_id = "event-error-info"
        mock_calendar_service.get_calendar_events.side_effect = Exception("API error")
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id=meeting_id)
        
        # Assert
        assert result["success"] is True
        assert result["cancelled"] is True
        assert "cancelled_meeting" not in result

    async def test_cancel_meeting_cancellation_fails(self, mock_calendar_service):
        """Test when calendar service fails to cancel the event"""
        # Arrange
        meeting_id = "event-fail"
        mock_calendar_service.get_calendar_events.return_value = []
        mock_calendar_service.cancel_event.return_value = False
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id=meeting_id)
        
        # Assert
        assert result["success"] is False
        assert result["cancelled"] is False
        assert "Falha ao cancelar reunião" in result["error"]

    async def test_cancel_meeting_exception_handling(self, mock_calendar_service):
        """Test exception handling during meeting cancellation"""
        # Arrange
        meeting_id = "event-exception"
        mock_calendar_service.cancel_event.side_effect = Exception("Calendar API error")
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id=meeting_id)
        
        # Assert
        assert result["success"] is False
        assert result["cancelled"] is False
        assert "Erro ao cancelar reunião" in result["error"]
        assert "Calendar API error" in result["error"]

    async def test_cancel_meeting_residential_solar(self, mock_calendar_service):
        """Test cancelling a residential solar meeting (30 minutes)"""
        # Arrange
        meeting_id = "event-residential"
        timezone = "America/Sao_Paulo"
        
        # Mock residential meeting (30 minutes)
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Solar Residencial - Maria Santos",
            description="Consulta sobre energia solar residencial",
            start=datetime(2024, 1, 15, 10, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 10, 30, tzinfo=ZoneInfo(timezone)),
            attendees=["maria@example.com"],
            meet_link="https://meet.google.com/residential",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                reason="Cliente preferiu visita presencial"
            )
        
        # Assert
        assert result["success"] is True
        assert result["cancelled_meeting"]["title"] == "Solar Residencial - Maria Santos"
        assert result["reason"] == "Cliente preferiu visita presencial"

    async def test_cancel_meeting_commercial_solar(self, mock_calendar_service):
        """Test cancelling a commercial solar meeting (60 minutes)"""
        # Arrange
        meeting_id = "event-commercial"
        timezone = "America/Sao_Paulo"
        
        # Mock commercial meeting (60 minutes)
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Solar Comercial - Empresa XYZ",
            description="Proposta solar para empresa",
            start=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 16, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["empresa@example.com", "vendedor@solarprime.com", "tecnico@solarprime.com"],
            meet_link="https://meet.google.com/commercial",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                reason="Empresa adiou decisão para próximo trimestre"
            )
        
        # Assert
        assert result["success"] is True
        assert result["cancelled_meeting"]["attendees"] == 3
        assert "Comercial" in result["cancelled_meeting"]["title"]

    async def test_cancel_meeting_past_event(self, mock_calendar_service):
        """Test cancelling a past event"""
        # Arrange
        meeting_id = "event-past"
        timezone = "America/Sao_Paulo"
        
        # Mock past event
        past_date = datetime.now(ZoneInfo(timezone)) - timedelta(days=7)
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar Passada",
            description="Esta reunião já ocorreu",
            start=past_date,
            end=past_date + timedelta(hours=1),
            attendees=["cliente@example.com"],
            meet_link="https://meet.google.com/past",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                reason="Limpeza de eventos antigos"
            )
        
        # Assert
        assert result["success"] is True
        assert result["cancelled"] is True

    async def test_cancel_meeting_future_event(self, mock_calendar_service):
        """Test cancelling a future event"""
        # Arrange
        meeting_id = "event-future"
        timezone = "America/Sao_Paulo"
        
        # Mock future event (next month)
        future_date = datetime.now(ZoneInfo(timezone)) + timedelta(days=30)
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar Futura",
            description="Reunião agendada para próximo mês",
            start=future_date,
            end=future_date + timedelta(hours=1),
            attendees=["cliente@example.com"],
            meet_link="https://meet.google.com/future",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                reason="Cliente cancelou com antecedência"
            )
        
        # Assert
        assert result["success"] is True
        assert result["cancelled"] is True

    async def test_cancel_meeting_america_recife_timezone(self, mock_calendar_service):
        """Test cancelling meeting with America/Recife timezone"""
        # Arrange
        meeting_id = "event-recife"
        timezone = "America/Recife"
        
        # Mock event in Recife timezone
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar Recife",
            description="Reunião em Recife",
            start=datetime(2024, 1, 15, 11, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 12, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["cliente.recife@example.com"],
            meet_link="https://meet.google.com/recife",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id=meeting_id)
        
        # Assert
        assert result["success"] is True
        assert result["cancelled_meeting"]["title"] == "Reunião Solar Recife"

    async def test_cancel_meeting_tool_instance(self):
        """Test that CancelMeetingTool is correctly exported"""
        assert CancelMeetingTool == cancel_meeting
        assert callable(CancelMeetingTool)

    async def test_cancel_meeting_with_long_reason(self, mock_calendar_service):
        """Test cancelling with a detailed reason"""
        # Arrange
        meeting_id = "event-detailed"
        long_reason = ("Cliente informou que precisa adiar a reunião devido a "
                      "viagem de negócios inesperada. Solicitou reagendamento "
                      "para segunda quinzena de fevereiro.")
        
        mock_calendar_service.get_calendar_events.return_value = []
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(
                meeting_id=meeting_id,
                reason=long_reason
            )
        
        # Assert
        assert result["success"] is True
        assert result["reason"] == long_reason

    async def test_cancel_meeting_search_window(self, mock_calendar_service):
        """Test the search window for finding meetings (365 days past and future)"""
        # Arrange
        meeting_id = "event-search"
        timezone = "America/Sao_Paulo"
        now = datetime.now(ZoneInfo(timezone))
        
        # Verify the search window used
        mock_calendar_service.get_calendar_events.return_value = []
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id=meeting_id)
        
        # Assert
        assert result["success"] is True
        
        # Verify the search was called with appropriate time range
        call_args = mock_calendar_service.get_calendar_events.call_args
        time_min = call_args.kwargs["time_min"]
        time_max = call_args.kwargs["time_max"]
        
        # Should search approximately 1 year in past and future
        assert (now - time_min).days >= 364
        assert (time_max - now).days >= 364

    async def test_cancel_meeting_no_attendees(self, mock_calendar_service):
        """Test cancelling meeting with no attendees"""
        # Arrange
        meeting_id = "event-no-attendees"
        timezone = "America/Sao_Paulo"
        
        # Mock event with empty attendees
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Interna",
            description="Reunião sem participantes externos",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],  # No attendees
            meet_link="https://meet.google.com/internal",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_calendar_service.cancel_event.return_value = True
        
        with patch('agente.tools.calendar.cancel_meeting.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await cancel_meeting(meeting_id=meeting_id)
        
        # Assert
        assert result["success"] is True
        assert result["cancelled_meeting"]["attendees"] == 0