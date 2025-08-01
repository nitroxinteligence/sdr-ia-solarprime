"""
Integration tests for Google Calendar API.

These tests verify the actual integration with Google Calendar API.
They should be run with proper service account credentials or mocking.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone
import pytz

from agente.services.calendar_service import CalendarService
from agente.core.config import GOOGLE_SERVICE_ACCOUNT_KEY


@pytest.mark.integration
class TestGoogleCalendarIntegration:
    """Integration tests for Google Calendar API service."""
    
    @pytest_asyncio.fixture
    async def calendar_service(self):
        """Create Calendar service instance."""
        service = CalendarService()
        return service
    
    @pytest_asyncio.fixture
    def mock_calendar_api(self):
        """Mock Google Calendar API client."""
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        return mock_service, mock_events
    
    @pytest.mark.asyncio
    async def test_check_availability_integration(self, calendar_service, mock_calendar_api):
        """Test checking calendar availability."""
        mock_service, mock_events = mock_calendar_api
        
        # Mock calendar events response
        brazil_tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(brazil_tz)
        
        mock_events.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "event1",
                    "summary": "Reunião Solar - João Silva",
                    "start": {"dateTime": (now + timedelta(hours=2)).isoformat()},
                    "end": {"dateTime": (now + timedelta(hours=3)).isoformat()}
                },
                {
                    "id": "event2",
                    "summary": "Reunião Solar - Maria Santos",
                    "start": {"dateTime": (now + timedelta(hours=5)).isoformat()},
                    "end": {"dateTime": (now + timedelta(hours=6)).isoformat()}
                }
            ]
        }
        
        # Patch the service
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.check_availability(
                date=now.date() + timedelta(days=1),
                duration_minutes=30
            )
        
        # Verify API calls
        mock_events.list.assert_called_once()
        call_kwargs = mock_events.list.call_args[1]
        assert "calendarId" in call_kwargs
        assert "timeMin" in call_kwargs
        assert "timeMax" in call_kwargs
        assert call_kwargs["singleEvents"] is True
        
        # Verify result
        assert isinstance(result, list)
        assert all("time" in slot for slot in result)
        assert all("available" in slot for slot in result)
    
    @pytest.mark.asyncio
    async def test_create_event_integration(self, calendar_service, mock_calendar_api):
        """Test creating a calendar event."""
        mock_service, mock_events = mock_calendar_api
        
        # Mock event creation response
        brazil_tz = pytz.timezone("America/Sao_Paulo")
        start_time = datetime.now(brazil_tz) + timedelta(days=1, hours=2)
        
        mock_events.insert.return_value.execute.return_value = {
            "id": "new-event-id",
            "summary": "Reunião Solar - João Silva",
            "start": {"dateTime": start_time.isoformat()},
            "end": {"dateTime": (start_time + timedelta(minutes=30)).isoformat()},
            "attendees": [{"email": "joao@example.com"}],
            "conferenceData": {
                "entryPoints": [
                    {
                        "entryPointType": "video",
                        "uri": "https://meet.google.com/abc-defg-hij"
                    }
                ]
            }
        }
        
        # Patch the service
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.create_event(
                title="Reunião Solar - João Silva",
                start_time=start_time,
                duration_minutes=30,
                attendee_email="joao@example.com",
                description="Reunião para apresentação da proposta de energia solar"
            )
        
        # Verify API call
        mock_events.insert.assert_called_once()
        call_kwargs = mock_events.insert.call_args[1]
        assert "calendarId" in call_kwargs
        assert "body" in call_kwargs
        
        # Verify event body
        event_body = call_kwargs["body"]
        assert event_body["summary"] == "Reunião Solar - João Silva"
        assert len(event_body["attendees"]) == 1
        assert event_body["attendees"][0]["email"] == "joao@example.com"
        
        # Verify result
        assert result["id"] == "new-event-id"
        assert result["success"] is True
        assert "meet_link" in result
    
    @pytest.mark.asyncio
    async def test_update_event_integration(self, calendar_service, mock_calendar_api):
        """Test updating a calendar event."""
        mock_service, mock_events = mock_calendar_api
        
        # Mock get event response
        brazil_tz = pytz.timezone("America/Sao_Paulo")
        current_start = datetime.now(brazil_tz) + timedelta(days=1)
        
        mock_events.get.return_value.execute.return_value = {
            "id": "existing-event-id",
            "summary": "Reunião Solar - João Silva",
            "start": {"dateTime": current_start.isoformat()},
            "end": {"dateTime": (current_start + timedelta(minutes=30)).isoformat()},
            "attendees": [{"email": "joao@example.com"}]
        }
        
        # Mock update response
        new_start = current_start + timedelta(hours=2)
        mock_events.update.return_value.execute.return_value = {
            "id": "existing-event-id",
            "summary": "Reunião Solar - João Silva",
            "start": {"dateTime": new_start.isoformat()},
            "end": {"dateTime": (new_start + timedelta(minutes=30)).isoformat()},
            "attendees": [{"email": "joao@example.com"}]
        }
        
        # Patch the service
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.update_event(
                event_id="existing-event-id",
                start_time=new_start
            )
        
        # Verify API calls
        mock_events.get.assert_called_once_with(
            calendarId="primary",
            eventId="existing-event-id"
        )
        mock_events.update.assert_called_once()
        
        # Verify result
        assert result["id"] == "existing-event-id"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_delete_event_integration(self, calendar_service, mock_calendar_api):
        """Test deleting a calendar event."""
        mock_service, mock_events = mock_calendar_api
        
        # Mock delete response (no content)
        mock_events.delete.return_value.execute.return_value = None
        
        # Patch the service
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.delete_event(
                event_id="event-to-delete"
            )
        
        # Verify API call
        mock_events.delete.assert_called_once_with(
            calendarId="primary",
            eventId="event-to-delete",
            sendUpdates="all"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["deleted"] is True
    
    @pytest.mark.asyncio
    async def test_business_hours_integration(self, calendar_service, mock_calendar_api):
        """Test business hours constraints."""
        mock_service, mock_events = mock_calendar_api
        
        # Mock empty calendar (all slots available)
        mock_events.list.return_value.execute.return_value = {"items": []}
        
        # Test weekday availability
        brazil_tz = pytz.timezone("America/Sao_Paulo")
        weekday = datetime(2024, 1, 15, 10, 0, tzinfo=brazil_tz)  # Monday
        
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            # Should have slots from 9:00 to 18:00
            result = await calendar_service.check_availability(
                date=weekday.date(),
                duration_minutes=30
            )
        
        # Verify business hours slots
        times = [slot["time"] for slot in result if slot["available"]]
        assert "09:00" in times
        assert "17:30" in times  # Last 30-min slot
        assert "18:00" not in times  # Would end after business hours
        assert "08:30" not in times  # Before business hours
    
    @pytest.mark.asyncio
    async def test_weekend_availability(self, calendar_service, mock_calendar_api):
        """Test weekend availability constraints."""
        mock_service, mock_events = mock_calendar_api
        
        # Mock empty calendar
        mock_events.list.return_value.execute.return_value = {"items": []}
        
        # Test Saturday (limited hours)
        brazil_tz = pytz.timezone("America/Sao_Paulo")
        saturday = datetime(2024, 1, 20, 10, 0, tzinfo=brazil_tz)  # Saturday
        
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.check_availability(
                date=saturday.date(),
                duration_minutes=30
            )
        
        # Saturday should have limited hours (8:00-13:00)
        times = [slot["time"] for slot in result if slot["available"]]
        assert "08:00" in times
        assert "12:30" in times  # Last slot
        assert "13:00" not in times  # Would end after Saturday hours
        
        # Test Sunday (no availability)
        sunday = datetime(2024, 1, 21, 10, 0, tzinfo=brazil_tz)  # Sunday
        
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.check_availability(
                date=sunday.date(),
                duration_minutes=30
            )
        
        # Sunday should have no available slots
        available_slots = [slot for slot in result if slot["available"]]
        assert len(available_slots) == 0
    
    @pytest.mark.asyncio
    async def test_conflict_detection(self, calendar_service, mock_calendar_api):
        """Test calendar conflict detection."""
        mock_service, mock_events = mock_calendar_api
        
        # Mock calendar with existing events
        brazil_tz = pytz.timezone("America/Sao_Paulo")
        date = datetime.now(brazil_tz).date() + timedelta(days=1)
        
        mock_events.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "event1",
                    "summary": "Existing Meeting",
                    "start": {"dateTime": f"{date}T10:00:00-03:00"},
                    "end": {"dateTime": f"{date}T11:00:00-03:00"}
                },
                {
                    "id": "event2",
                    "summary": "Another Meeting",
                    "start": {"dateTime": f"{date}T14:00:00-03:00"},
                    "end": {"dateTime": f"{date}T15:00:00-03:00"}
                }
            ]
        }
        
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.check_availability(
                date=date,
                duration_minutes=60
            )
        
        # Verify conflicts are detected
        slot_10 = next(s for s in result if s["time"] == "10:00")
        slot_14 = next(s for s in result if s["time"] == "14:00")
        slot_12 = next(s for s in result if s["time"] == "12:00")
        
        assert not slot_10["available"]  # Conflicts with event1
        assert not slot_14["available"]  # Conflicts with event2
        assert slot_12["available"]  # No conflict
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, calendar_service, mock_calendar_api):
        """Test handling of Google Calendar API errors."""
        mock_service, mock_events = mock_calendar_api
        
        # Test authentication error
        from googleapiclient.errors import HttpError
        mock_error = HttpError(
            resp=MagicMock(status=401),
            content=b'{"error": "unauthorized"}'
        )
        mock_events.list.return_value.execute.side_effect = mock_error
        
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.check_availability(
                date=datetime.now().date()
            )
        
        # Should handle error gracefully
        assert result == []
    
    @pytest.mark.asyncio
    async def test_timezone_handling(self, calendar_service, mock_calendar_api):
        """Test proper timezone handling."""
        mock_service, mock_events = mock_calendar_api
        
        # Create event with specific timezone
        brazil_tz = pytz.timezone("America/Sao_Paulo")
        start_time = datetime(2024, 1, 15, 14, 0, tzinfo=brazil_tz)
        
        mock_events.insert.return_value.execute.return_value = {
            "id": "tz-test-event",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "America/Sao_Paulo"},
            "end": {"dateTime": (start_time + timedelta(minutes=30)).isoformat()}
        }
        
        with patch.object(calendar_service, '_get_calendar_service', return_value=mock_service):
            result = await calendar_service.create_event(
                title="Timezone Test",
                start_time=start_time,
                duration_minutes=30
            )
        
        # Verify timezone was preserved
        call_kwargs = mock_events.insert.call_args[1]
        event_body = call_kwargs["body"]
        assert event_body["start"]["timeZone"] == "America/Sao_Paulo"