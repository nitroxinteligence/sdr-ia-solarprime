"""
Unit tests for check_availability calendar tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agente.tools.calendar.check_availability import check_availability, CheckAvailabilityTool
from agente.core.types import CalendarSlot


@pytest.fixture
def mock_calendar_service():
    """Mock Calendar service for tests"""
    service = AsyncMock()
    service.is_available = MagicMock(return_value=True)
    service.check_availability = AsyncMock()
    return service


@pytest.mark.asyncio
class TestCheckAvailability:
    """Test cases for check_availability tool"""

    async def test_check_availability_success(self, mock_calendar_service):
        """Test successful availability check with available slots"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        start_date = datetime(2024, 1, 15, 9, 0, tzinfo=ZoneInfo(timezone))
        
        mock_slots = [
            CalendarSlot(
                start=start_date,
                end=start_date + timedelta(hours=1),
                duration_minutes=60
            ),
            CalendarSlot(
                start=start_date + timedelta(hours=2),
                end=start_date + timedelta(hours=3),
                duration_minutes=60
            ),
            CalendarSlot(
                start=start_date + timedelta(hours=5),
                end=start_date + timedelta(hours=6),
                duration_minutes=60
            )
        ]
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(
                date=date_str,
                duration_minutes=60,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["total_slots"] == 3
        assert len(result["available_slots"]) == 3
        
        # Verify first slot
        first_slot = result["available_slots"][0]
        assert first_slot["date"] == "2024-01-15"
        assert first_slot["start_time"] == "09:00"
        assert first_slot["end_time"] == "10:00"
        assert first_slot["duration_minutes"] == 60
        assert first_slot["timezone"] == timezone
        
        # Verify business hours
        assert result["business_hours"]["weekdays"]["start"] == "08:00"
        assert result["business_hours"]["weekdays"]["end"] == "18:00"
        
        # Verify call
        mock_calendar_service.check_availability.assert_called_once()

    async def test_check_availability_no_service(self, mock_calendar_service):
        """Test when Google Calendar service is not available"""
        # Arrange
        mock_calendar_service.is_available.return_value = False
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(date="2024-01-15")
        
        # Assert
        assert result["success"] is False
        assert "não está disponível" in result["error"]
        assert result["total_slots"] == 0
        assert result["available_slots"] == []

    async def test_check_availability_invalid_date_format(self, mock_calendar_service):
        """Test with invalid date format"""
        # Act
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            result = await check_availability(date="15/01/2024")  # Wrong format
        
        # Assert
        assert result["success"] is False
        assert "Formato de data inválido" in result["error"]
        assert "YYYY-MM-DD" in result["error"]
        assert result["total_slots"] == 0

    async def test_check_availability_30_minute_slots(self, mock_calendar_service):
        """Test filtering for 30-minute slots"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        start_date = datetime(2024, 1, 15, 9, 0, tzinfo=ZoneInfo(timezone))
        
        # Create mix of slot sizes
        mock_slots = [
            CalendarSlot(  # 90 minutes - can fit 30 min
                start=start_date,
                end=start_date + timedelta(minutes=90),
                duration_minutes=90
            ),
            CalendarSlot(  # 20 minutes - too small
                start=start_date + timedelta(hours=2),
                end=start_date + timedelta(hours=2, minutes=20),
                duration_minutes=20
            ),
            CalendarSlot(  # 45 minutes - can fit 30 min
                start=start_date + timedelta(hours=3),
                end=start_date + timedelta(hours=3, minutes=45),
                duration_minutes=45
            )
        ]
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(
                date=date_str,
                duration_minutes=30,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["total_slots"] == 2  # Only 2 slots are big enough
        assert all(slot["duration_minutes"] == 30 for slot in result["available_slots"])

    async def test_check_availability_multiple_days(self, mock_calendar_service):
        """Test checking availability across multiple days"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        start_date = datetime(2024, 1, 15, 9, 0, tzinfo=ZoneInfo(timezone))
        
        # Slots across 3 days
        mock_slots = [
            CalendarSlot(  # Day 1
                start=start_date,
                end=start_date + timedelta(hours=1),
                duration_minutes=60
            ),
            CalendarSlot(  # Day 2
                start=start_date + timedelta(days=1, hours=1),
                end=start_date + timedelta(days=1, hours=2),
                duration_minutes=60
            ),
            CalendarSlot(  # Day 3
                start=start_date + timedelta(days=2, hours=2),
                end=start_date + timedelta(days=2, hours=3),
                duration_minutes=60
            )
        ]
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(
                date=date_str,
                check_days_ahead=3
            )
        
        # Assert
        assert result["success"] is True
        assert result["total_slots"] == 3
        assert result["query_period"]["days_checked"] == 3
        
        # Verify different dates
        dates = [slot["date"] for slot in result["available_slots"]]
        assert "2024-01-15" in dates
        assert "2024-01-16" in dates
        assert "2024-01-17" in dates

    async def test_check_availability_america_recife_timezone(self, mock_calendar_service):
        """Test with America/Recife timezone (Solar Prime's location)"""
        # Arrange
        timezone = "America/Recife"
        date_str = "2024-01-15"
        start_date = datetime(2024, 1, 15, 9, 0, tzinfo=ZoneInfo(timezone))
        
        mock_slots = [
            CalendarSlot(
                start=start_date,
                end=start_date + timedelta(hours=1),
                duration_minutes=60
            )
        ]
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(
                date=date_str,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["timezone"] == timezone
        assert result["available_slots"][0]["timezone"] == timezone

    async def test_check_availability_no_slots_available(self, mock_calendar_service):
        """Test when no slots are available"""
        # Arrange
        mock_calendar_service.check_availability.return_value = []
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(date="2024-01-15")
        
        # Assert
        assert result["success"] is True
        assert result["total_slots"] == 0
        assert result["available_slots"] == []

    async def test_check_availability_saturday_hours(self, mock_calendar_service):
        """Test Saturday business hours information"""
        # Arrange
        mock_calendar_service.check_availability.return_value = []
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(date="2024-01-13")  # Saturday
        
        # Assert
        assert result["success"] is True
        assert result["business_hours"]["saturday"]["start"] == "08:00"
        assert result["business_hours"]["saturday"]["end"] == "13:00"
        assert result["business_hours"]["sunday"] == "closed"

    async def test_check_availability_exception_handling(self, mock_calendar_service):
        """Test exception handling during availability check"""
        # Arrange
        mock_calendar_service.check_availability.side_effect = Exception("Calendar API error")
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(date="2024-01-15")
        
        # Assert
        assert result["success"] is False
        assert "Erro ao verificar disponibilidade" in result["error"]
        assert "Calendar API error" in result["error"]
        assert result["total_slots"] == 0

    async def test_check_availability_iso_format_in_response(self, mock_calendar_service):
        """Test that ISO format timestamps are included in response"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        start_date = datetime(2024, 1, 15, 14, 30, tzinfo=ZoneInfo(timezone))
        
        mock_slots = [
            CalendarSlot(
                start=start_date,
                end=start_date + timedelta(hours=1),
                duration_minutes=60
            )
        ]
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(date=date_str)
        
        # Assert
        assert result["success"] is True
        slot = result["available_slots"][0]
        assert "iso_start" in slot
        assert "iso_end" in slot
        assert "T" in slot["iso_start"]  # ISO format check
        assert "T" in slot["iso_end"]

    async def test_check_availability_commercial_solar_duration(self, mock_calendar_service):
        """Test checking availability for commercial solar meetings (60 minutes)"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        start_date = datetime(2024, 1, 15, 10, 0, tzinfo=ZoneInfo(timezone))
        
        # Mix of different duration slots
        mock_slots = [
            CalendarSlot(  # 2 hours - good for commercial
                start=start_date,
                end=start_date + timedelta(hours=2),
                duration_minutes=120
            ),
            CalendarSlot(  # 30 minutes - too short for commercial
                start=start_date + timedelta(hours=3),
                end=start_date + timedelta(hours=3, minutes=30),
                duration_minutes=30
            )
        ]
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(
                date=date_str,
                duration_minutes=60,  # Commercial meeting duration
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["total_slots"] == 1  # Only the 2-hour slot fits
        assert result["requested_duration"] == 60

    async def test_check_availability_tool_instance(self):
        """Test that CheckAvailabilityTool is correctly exported"""
        assert CheckAvailabilityTool == check_availability
        assert callable(CheckAvailabilityTool)

    async def test_check_availability_with_business_context(self, mock_calendar_service):
        """Test availability check considering Solar Prime business context"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"  # Tuesday
        start_date = datetime(2024, 1, 15, 8, 0, tzinfo=ZoneInfo(timezone))
        
        # Create slots covering full business day
        mock_slots = []
        for hour in range(8, 18):  # 8:00 to 18:00
            slot_start = start_date.replace(hour=hour)
            mock_slots.append(CalendarSlot(
                start=slot_start,
                end=slot_start + timedelta(hours=1),
                duration_minutes=60
            ))
        
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act
            result = await check_availability(
                date=date_str,
                duration_minutes=30,  # Residential meeting
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["total_slots"] == 10  # All slots can fit 30-min meetings
        
        # Verify all slots are within business hours
        for slot in result["available_slots"]:
            hour = int(slot["start_time"].split(":")[0])
            assert 8 <= hour < 18

    async def test_check_availability_edge_case_end_of_day(self, mock_calendar_service):
        """Test edge case where slot would extend beyond business hours"""
        # Arrange
        timezone = "America/Sao_Paulo"
        date_str = "2024-01-15"
        
        # Create a slot at 17:30 (90 minutes available)
        start_date = datetime(2024, 1, 15, 17, 30, tzinfo=ZoneInfo(timezone))
        mock_slots = [
            CalendarSlot(
                start=start_date,
                end=start_date + timedelta(minutes=90),
                duration_minutes=90
            )
        ]
        mock_calendar_service.check_availability.return_value = mock_slots
        
        with patch('agente.tools.calendar.check_availability.get_calendar_service', return_value=mock_calendar_service):
            # Act - Request 60-minute slot
            result = await check_availability(
                date=date_str,
                duration_minutes=60,
                timezone=timezone
            )
        
        # Assert
        assert result["success"] is True
        assert result["total_slots"] == 1
        # The slot should be adjusted to fit within business hours
        slot = result["available_slots"][0]
        assert slot["start_time"] == "17:30"
        assert slot["duration_minutes"] == 60