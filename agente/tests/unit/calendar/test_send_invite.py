"""
Unit tests for send_calendar_invite tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agente.tools.calendar.send_invite import send_calendar_invite, SendCalendarInviteTool, _get_weekday_name
from agente.core.types import CalendarEvent


@pytest.fixture
def mock_calendar_service():
    """Mock Calendar service for tests"""
    service = AsyncMock()
    service.is_available = MagicMock(return_value=True)
    service.get_calendar_events = AsyncMock()
    return service


@pytest.fixture
def mock_evolution_service():
    """Mock Evolution service for tests"""
    service = AsyncMock()
    service.send_text_message = AsyncMock()
    return service


@pytest.mark.asyncio
class TestSendCalendarInvite:
    """Test cases for send_calendar_invite tool"""

    async def test_send_invite_success(self, mock_calendar_service, mock_evolution_service):
        """Test successful calendar invite sending"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-123"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting event
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar - João Silva",
            description="Discussão sobre instalação de painéis solares",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["joao@example.com"],
            meet_link="https://meet.google.com/abc-defg-hij",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        
        # Mock WhatsApp send success
        mock_evolution_service.send_text_message.return_value = {
            "success": True,
            "message_id": "whatsapp-msg-123"
        }
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is True
        assert result["message_sent"] is True
        assert result["whatsapp_message_id"] == "whatsapp-msg-123"
        assert result["phone_number"] == phone_number
        
        # Verify meeting details
        meeting_details = result["meeting_details"]
        assert meeting_details["title"] == "Reunião Solar - João Silva"
        assert meeting_details["date"] == "15/01/2024"
        assert meeting_details["day_of_week"] == "Segunda-feira"
        assert meeting_details["start_time"] == "14:00"
        assert meeting_details["end_time"] == "15:00"
        assert meeting_details["duration_minutes"] == 60
        assert meeting_details["meet_link"] == "https://meet.google.com/abc-defg-hij"
        
        # Verify WhatsApp message was sent
        mock_evolution_service.send_text_message.assert_called_once()
        call_args = mock_evolution_service.send_text_message.call_args
        assert call_args.kwargs["to"] == phone_number
        message_text = call_args.kwargs["text"]
        
        # Verify message content
        assert "Confirmação de Reunião" in message_text
        assert "João Silva" in message_text
        assert "15/01/2024" in message_text
        assert "14:00 às 15:00" in message_text
        assert "https://meet.google.com/abc-defg-hij" in message_text

    async def test_send_invite_no_calendar_service(self, mock_calendar_service, mock_evolution_service):
        """Test when Google Calendar service is not available"""
        # Arrange
        mock_calendar_service.is_available.return_value = False
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number="5511999999999",
                    meeting_id="event-123"
                )
        
        # Assert
        assert result["success"] is False
        assert result["message_sent"] is False
        assert "não está disponível" in result["error"]

    async def test_send_invite_meeting_not_found(self, mock_calendar_service, mock_evolution_service):
        """Test when meeting is not found"""
        # Arrange
        mock_calendar_service.get_calendar_events.return_value = []  # No meetings found
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number="5511999999999",
                    meeting_id="event-not-found"
                )
        
        # Assert
        assert result["success"] is False
        assert result["message_sent"] is False
        assert "não encontrada" in result["error"]

    async def test_send_invite_custom_message(self, mock_calendar_service, mock_evolution_service):
        """Test sending invite with custom message"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-123"
        custom_message = "Olá! Estamos ansiosos para discutir sua solução solar!"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar",
            description="Reunião importante",
            start=datetime(2024, 1, 15, 10, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 10, 30, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/test",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-custom"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id,
                    custom_message=custom_message
                )
        
        # Assert
        assert result["success"] is True
        
        # Verify custom message is included
        call_args = mock_evolution_service.send_text_message.call_args
        message_text = call_args.kwargs["text"]
        assert custom_message in message_text

    async def test_send_invite_without_meet_link(self, mock_calendar_service, mock_evolution_service):
        """Test sending invite when meeting has no Google Meet link"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-no-meet"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting without meet link
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Presencial",
            description="Reunião será presencial",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link=None,  # No meet link
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-123"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id,
                    include_meet_link=True
                )
        
        # Assert
        assert result["success"] is True
        assert result["meeting_details"]["meet_link"] is None
        
        # Verify no meet link in message
        call_args = mock_evolution_service.send_text_message.call_args
        message_text = call_args.kwargs["text"]
        assert "Link da Reunião" not in message_text

    async def test_send_invite_exclude_meet_link(self, mock_calendar_service, mock_evolution_service):
        """Test excluding meet link even when available"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-123"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting with meet link
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar",
            description="Reunião online",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/test",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-123"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id,
                    include_meet_link=False  # Exclude meet link
                )
        
        # Assert
        assert result["success"] is True
        assert result["meeting_details"]["meet_link"] is None
        
        # Verify no meet link in message
        call_args = mock_evolution_service.send_text_message.call_args
        message_text = call_args.kwargs["text"]
        assert "https://meet.google.com" not in message_text

    async def test_send_invite_phone_number_formatting(self, mock_calendar_service, mock_evolution_service):
        """Test phone number formatting (adding country code)"""
        # Arrange
        phone_number = "11999999999"  # Without country code
        meeting_id = "event-123"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Test Meeting",
            description="Test",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/test",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-123"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is True
        
        # Verify phone was formatted with country code
        call_args = mock_evolution_service.send_text_message.call_args
        assert call_args.kwargs["to"] == "5511999999999"

    async def test_send_invite_saturday_meeting(self, mock_calendar_service, mock_evolution_service):
        """Test sending invite for Saturday meeting"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-saturday"
        timezone = "America/Sao_Paulo"
        
        # Mock Saturday meeting
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar Sábado",
            description="Atendimento especial de sábado",
            start=datetime(2024, 1, 13, 10, 0, tzinfo=ZoneInfo(timezone)),  # Saturday
            end=datetime(2024, 1, 13, 11, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/saturday",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-saturday"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is True
        assert result["meeting_details"]["day_of_week"] == "Sábado"

    async def test_send_invite_whatsapp_error(self, mock_calendar_service, mock_evolution_service):
        """Test when WhatsApp message sending fails"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-123"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Test Meeting",
            description="Test",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/test",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        
        # Mock WhatsApp failure
        mock_evolution_service.send_text_message.return_value = {
            "success": False,
            "error": "WhatsApp service unavailable"
        }
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is False
        assert result["message_sent"] is False
        assert "WhatsApp service unavailable" in result["error"]
        assert result["meeting_details"] is not None  # Meeting details still returned

    async def test_send_invite_whatsapp_exception(self, mock_calendar_service, mock_evolution_service):
        """Test exception during WhatsApp sending"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-123"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Test Meeting",
            description="Test",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/test",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        
        # Mock WhatsApp exception
        mock_evolution_service.send_text_message.side_effect = Exception("Network error")
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is False
        assert result["message_sent"] is False
        assert "Network error" in result["error"]

    async def test_send_invite_30_minute_residential(self, mock_calendar_service, mock_evolution_service):
        """Test sending invite for 30-minute residential meeting"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-residential"
        timezone = "America/Sao_Paulo"
        
        # Mock 30-minute meeting
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
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-res"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is True
        assert result["meeting_details"]["duration_minutes"] == 30
        
        # Verify message mentions 30 minutes
        call_args = mock_evolution_service.send_text_message.call_args
        message_text = call_args.kwargs["text"]
        assert "30 minutos" in message_text

    async def test_send_invite_60_minute_commercial(self, mock_calendar_service, mock_evolution_service):
        """Test sending invite for 60-minute commercial meeting"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-commercial"
        timezone = "America/Sao_Paulo"
        
        # Mock 60-minute meeting
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Solar Comercial - Empresa XYZ",
            description="Proposta solar para empresa",
            start=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 16, 0, tzinfo=ZoneInfo(timezone)),
            attendees=["empresa@example.com"],
            meet_link="https://meet.google.com/commercial",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-com"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is True
        assert result["meeting_details"]["duration_minutes"] == 60
        
        # Verify message mentions 60 minutes
        call_args = mock_evolution_service.send_text_message.call_args
        message_text = call_args.kwargs["text"]
        assert "60 minutos" in message_text

    async def test_weekday_name_helper(self):
        """Test _get_weekday_name helper function"""
        assert _get_weekday_name(0) == "Segunda-feira"
        assert _get_weekday_name(1) == "Terça-feira"
        assert _get_weekday_name(2) == "Quarta-feira"
        assert _get_weekday_name(3) == "Quinta-feira"
        assert _get_weekday_name(4) == "Sexta-feira"
        assert _get_weekday_name(5) == "Sábado"
        assert _get_weekday_name(6) == "Domingo"
        assert _get_weekday_name(7) == ""  # Invalid

    async def test_send_invite_with_description(self, mock_calendar_service, mock_evolution_service):
        """Test that meeting description is included in the invite"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-desc"
        timezone = "America/Sao_Paulo"
        meeting_description = "Vamos discutir:\n- Análise de consumo\n- Proposta personalizada\n- Financiamento"
        
        # Mock meeting with description
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Consulta Solar Completa",
            description=meeting_description,
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/desc",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-desc"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is True
        
        # Verify description is in message
        call_args = mock_evolution_service.send_text_message.call_args
        message_text = call_args.kwargs["text"]
        assert "Detalhes:" in message_text
        assert meeting_description in message_text

    async def test_send_invite_tool_instance(self):
        """Test that SendCalendarInviteTool is correctly exported"""
        assert SendCalendarInviteTool == send_calendar_invite
        assert callable(SendCalendarInviteTool)

    async def test_send_invite_general_exception(self, mock_calendar_service, mock_evolution_service):
        """Test general exception handling"""
        # Arrange
        mock_calendar_service.get_calendar_events.side_effect = Exception("Unexpected error")
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number="5511999999999",
                    meeting_id="event-123"
                )
        
        # Assert
        assert result["success"] is False
        assert result["message_sent"] is False
        assert "Erro ao processar convite" in result["error"]
        assert "Unexpected error" in result["error"]

    async def test_send_invite_tips_section(self, mock_calendar_service, mock_evolution_service):
        """Test that meeting tips are included in the message"""
        # Arrange
        phone_number = "5511999999999"
        meeting_id = "event-tips"
        timezone = "America/Sao_Paulo"
        
        # Mock meeting
        mock_event = CalendarEvent(
            id=meeting_id,
            title="Reunião Solar",
            description="Reunião de apresentação",
            start=datetime(2024, 1, 15, 14, 0, tzinfo=ZoneInfo(timezone)),
            end=datetime(2024, 1, 15, 15, 0, tzinfo=ZoneInfo(timezone)),
            attendees=[],
            meet_link="https://meet.google.com/tips",
            status="confirmed"
        )
        mock_calendar_service.get_calendar_events.return_value = [mock_event]
        mock_evolution_service.send_text_message.return_value = {"success": True, "message_id": "msg-tips"}
        
        with patch('agente.tools.calendar.send_invite.get_calendar_service', return_value=mock_calendar_service):
            with patch('agente.tools.calendar.send_invite.get_evolution_service', return_value=mock_evolution_service):
                # Act
                result = await send_calendar_invite(
                    phone_number=phone_number,
                    meeting_id=meeting_id
                )
        
        # Assert
        assert result["success"] is True
        
        # Verify tips are included
        call_args = mock_evolution_service.send_text_message.call_args
        message_text = call_args.kwargs["text"]
        assert "Dicas para a reunião" in message_text
        assert "Teste sua conexão" in message_text
        assert "conta de energia" in message_text
        assert "reagendar" in message_text