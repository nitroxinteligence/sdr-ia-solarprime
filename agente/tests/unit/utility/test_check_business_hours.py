"""
Unit tests for business hours checking functionality.

This tests the business hours logic that would be used in a check_business_hours tool.
"""

import pytest
import pytest_asyncio
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional


class TestCheckBusinessHours:
    """Test suite for business hours checking functionality."""
    
    def check_business_hours(
        self,
        check_time: Optional[datetime] = None,
        timezone_str: str = "America/Recife",
        business_hours: Dict[str, Any] = None,
        business_days: list = None
    ) -> Dict[str, Any]:
        """
        Check if current time is within business hours.
        
        This simulates what a check_business_hours tool would do.
        """
        # Default business hours configuration
        if business_hours is None:
            business_hours = {
                "start": time(8, 0),   # 8:00 AM
                "end": time(18, 0),    # 6:00 PM
            }
            
        if business_days is None:
            business_days = [1, 2, 3, 4, 5]  # Monday to Friday (ISO weekday)
            
        # Get current time in specified timezone
        tz = ZoneInfo(timezone_str)
        if check_time is None:
            current_time = datetime.now(tz)
        else:
            # Ensure the provided time has the correct timezone
            if check_time.tzinfo is None:
                current_time = check_time.replace(tzinfo=tz)
            else:
                current_time = check_time.astimezone(tz)
                
        # Extract components
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_weekday = current_time.isoweekday()  # 1=Monday, 7=Sunday
        current_date = current_time.date()
        
        # Check if it's a business day
        is_business_day = current_weekday in business_days
        
        # Check if within business hours
        start_minutes = business_hours["start"].hour * 60 + business_hours["start"].minute
        end_minutes = business_hours["end"].hour * 60 + business_hours["end"].minute
        current_minutes = current_hour * 60 + current_minute
        
        is_within_hours = start_minutes <= current_minutes < end_minutes
        is_open = is_business_day and is_within_hours
        
        # Calculate time until next opening
        if not is_open:
            next_open = self._calculate_next_open_time(
                current_time, business_hours, business_days, tz
            )
            minutes_until_open = int((next_open - current_time).total_seconds() / 60)
        else:
            next_open = None
            minutes_until_open = 0
            
        # Calculate time until closing (if open)
        if is_open:
            closing_time = current_time.replace(
                hour=business_hours["end"].hour,
                minute=business_hours["end"].minute,
                second=0,
                microsecond=0
            )
            minutes_until_close = int((closing_time - current_time).total_seconds() / 60)
        else:
            minutes_until_close = None
            
        # Get day name in Portuguese
        day_names_pt = {
            1: "Segunda-feira",
            2: "Terça-feira",
            3: "Quarta-feira",
            4: "Quinta-feira",
            5: "Sexta-feira",
            6: "Sábado",
            7: "Domingo"
        }
        
        return {
            "is_open": is_open,
            "is_business_day": is_business_day,
            "is_within_hours": is_within_hours,
            "current_time": current_time.isoformat(),
            "current_day": day_names_pt[current_weekday],
            "current_weekday": current_weekday,
            "business_hours": {
                "start": business_hours["start"].strftime("%H:%M"),
                "end": business_hours["end"].strftime("%H:%M")
            },
            "business_days": business_days,
            "timezone": timezone_str,
            "next_open_time": next_open.isoformat() if next_open else None,
            "minutes_until_open": minutes_until_open,
            "minutes_until_close": minutes_until_close,
            "message": self._get_status_message(
                is_open, is_business_day, is_within_hours,
                minutes_until_open, minutes_until_close,
                day_names_pt[current_weekday]
            )
        }
        
    def _calculate_next_open_time(
        self,
        current_time: datetime,
        business_hours: Dict[str, Any],
        business_days: list,
        tz: ZoneInfo
    ) -> datetime:
        """Calculate the next business opening time."""
        next_open = current_time
        
        # Start from tomorrow if already past business hours today
        if (current_time.hour * 60 + current_time.minute >= 
            business_hours["end"].hour * 60 + business_hours["end"].minute):
            next_open = next_open + timedelta(days=1)
            
        # Find next business day
        while next_open.isoweekday() not in business_days:
            next_open = next_open + timedelta(days=1)
            
        # Set to opening time
        next_open = next_open.replace(
            hour=business_hours["start"].hour,
            minute=business_hours["start"].minute,
            second=0,
            microsecond=0
        )
        
        return next_open
        
    def _get_status_message(
        self,
        is_open: bool,
        is_business_day: bool,
        is_within_hours: bool,
        minutes_until_open: int,
        minutes_until_close: Optional[int],
        current_day: str
    ) -> str:
        """Generate a human-readable status message."""
        if is_open:
            if minutes_until_close <= 30:
                return f"Aberto. Fechamos em {minutes_until_close} minutos."
            else:
                hours = minutes_until_close // 60
                return f"Aberto. Fechamos em {hours} horas."
        else:
            if not is_business_day:
                return f"Fechado. {current_day} não é dia útil. Abrimos na próxima segunda-feira."
            elif not is_within_hours:
                if minutes_until_open < 60:
                    return f"Fechado. Abrimos em {minutes_until_open} minutos."
                elif minutes_until_open < 1440:  # Less than 24 hours
                    hours = minutes_until_open // 60
                    return f"Fechado. Abrimos em {hours} horas."
                else:
                    days = minutes_until_open // 1440
                    return f"Fechado. Abrimos em {days} dias."
            else:
                return "Fechado."
    
    @pytest.mark.asyncio
    async def test_check_business_hours_during_business_hours(self):
        """Test checking during business hours."""
        # Monday at 10:00 AM
        test_time = datetime(2024, 1, 15, 10, 0, 0)  # Monday
        result = self.check_business_hours(check_time=test_time)
        
        assert result["is_open"] is True
        assert result["is_business_day"] is True
        assert result["is_within_hours"] is True
        assert result["current_day"] == "Segunda-feira"
        assert result["minutes_until_close"] == 480  # 8 hours * 60 minutes
        assert result["minutes_until_open"] == 0
        assert "Aberto" in result["message"]
        
    @pytest.mark.asyncio
    async def test_check_business_hours_outside_business_hours(self):
        """Test checking outside business hours."""
        # Monday at 7:00 AM (before opening)
        test_time = datetime(2024, 1, 15, 7, 0, 0)  # Monday
        result = self.check_business_hours(check_time=test_time)
        
        assert result["is_open"] is False
        assert result["is_business_day"] is True
        assert result["is_within_hours"] is False
        assert result["minutes_until_open"] == 60  # 1 hour
        assert result["minutes_until_close"] is None
        assert "Abrimos em 1 horas" in result["message"]
        
    @pytest.mark.asyncio
    async def test_check_business_hours_on_weekend(self):
        """Test checking on weekend."""
        # Saturday at 10:00 AM
        test_time = datetime(2024, 1, 13, 10, 0, 0)  # Saturday
        result = self.check_business_hours(check_time=test_time)
        
        assert result["is_open"] is False
        assert result["is_business_day"] is False
        assert result["current_day"] == "Sábado"
        assert result["next_open_time"] is not None
        assert "não é dia útil" in result["message"]
        
    @pytest.mark.asyncio
    async def test_check_business_hours_different_timezones(self):
        """Test with different Brazilian timezones."""
        test_time = datetime(2024, 1, 15, 10, 0, 0)
        
        # Recife (UTC-3)
        result_recife = self.check_business_hours(
            check_time=test_time,
            timezone_str="America/Recife"
        )
        
        # São Paulo (UTC-3, but may have DST)
        result_sp = self.check_business_hours(
            check_time=test_time,
            timezone_str="America/Sao_Paulo"
        )
        
        # Manaus (UTC-4)
        result_manaus = self.check_business_hours(
            check_time=test_time,
            timezone_str="America/Manaus"
        )
        
        # All should process correctly
        assert "timezone" in result_recife
        assert "timezone" in result_sp
        assert "timezone" in result_manaus
        
    @pytest.mark.asyncio
    async def test_check_business_hours_edge_cases(self):
        """Test edge cases around opening and closing times."""
        # Exactly at opening time
        test_time = datetime(2024, 1, 15, 8, 0, 0)  # Monday 8:00 AM
        result = self.check_business_hours(check_time=test_time)
        assert result["is_open"] is True
        assert result["minutes_until_close"] == 600  # 10 hours
        
        # One minute before closing
        test_time = datetime(2024, 1, 15, 17, 59, 0)  # Monday 5:59 PM
        result = self.check_business_hours(check_time=test_time)
        assert result["is_open"] is True
        assert result["minutes_until_close"] == 1
        assert "Fechamos em 1 minutos" in result["message"]
        
        # Exactly at closing time
        test_time = datetime(2024, 1, 15, 18, 0, 0)  # Monday 6:00 PM
        result = self.check_business_hours(check_time=test_time)
        assert result["is_open"] is False
        
    @pytest.mark.asyncio
    async def test_check_business_hours_custom_configuration(self):
        """Test with custom business hours configuration."""
        custom_hours = {
            "start": time(9, 30),   # 9:30 AM
            "end": time(17, 30),    # 5:30 PM
        }
        custom_days = [1, 2, 3, 4, 5, 6]  # Monday to Saturday
        
        # Saturday at 10:00 AM
        test_time = datetime(2024, 1, 13, 10, 0, 0)  # Saturday
        result = self.check_business_hours(
            check_time=test_time,
            business_hours=custom_hours,
            business_days=custom_days
        )
        
        assert result["is_open"] is True  # Saturday is now a business day
        assert result["is_business_day"] is True
        assert result["business_hours"]["start"] == "09:30"
        assert result["business_hours"]["end"] == "17:30"
        
    @pytest.mark.asyncio
    async def test_check_business_hours_next_open_calculation(self):
        """Test calculation of next opening time."""
        # Friday at 7:00 PM (after closing)
        test_time = datetime(2024, 1, 19, 19, 0, 0)  # Friday
        result = self.check_business_hours(check_time=test_time)
        
        assert result["is_open"] is False
        assert result["next_open_time"] is not None
        
        # Should open next Monday at 8:00 AM
        next_open = datetime.fromisoformat(result["next_open_time"])
        assert next_open.isoweekday() == 1  # Monday
        assert next_open.hour == 8
        assert next_open.minute == 0
        
    @pytest.mark.asyncio
    async def test_check_business_hours_minutes_until_open(self):
        """Test calculation of minutes until opening."""
        # Sunday at 10:00 PM
        test_time = datetime(2024, 1, 14, 22, 0, 0)  # Sunday
        result = self.check_business_hours(check_time=test_time)
        
        # Should open Monday at 8:00 AM (10 hours away)
        assert result["minutes_until_open"] == 600  # 10 hours * 60 minutes
        
    @pytest.mark.asyncio
    async def test_check_business_hours_all_weekdays(self):
        """Test all weekdays are correctly identified."""
        weekday_tests = [
            (datetime(2024, 1, 15), 1, "Segunda-feira", True),   # Monday
            (datetime(2024, 1, 16), 2, "Terça-feira", True),     # Tuesday
            (datetime(2024, 1, 17), 3, "Quarta-feira", True),    # Wednesday
            (datetime(2024, 1, 18), 4, "Quinta-feira", True),    # Thursday
            (datetime(2024, 1, 19), 5, "Sexta-feira", True),     # Friday
            (datetime(2024, 1, 20), 6, "Sábado", False),         # Saturday
            (datetime(2024, 1, 21), 7, "Domingo", False),        # Sunday
        ]
        
        for date, expected_weekday, expected_name, expected_business_day in weekday_tests:
            test_time = date.replace(hour=10, minute=0, second=0)
            result = self.check_business_hours(check_time=test_time)
            
            assert result["current_weekday"] == expected_weekday
            assert result["current_day"] == expected_name
            assert result["is_business_day"] == expected_business_day
            
    @pytest.mark.asyncio
    async def test_check_business_hours_message_variations(self):
        """Test different status message variations."""
        # 30 minutes before closing
        test_time = datetime(2024, 1, 15, 17, 30, 0)  # Monday 5:30 PM
        result = self.check_business_hours(check_time=test_time)
        assert "Fechamos em 30 minutos" in result["message"]
        
        # 2 hours before closing
        test_time = datetime(2024, 1, 15, 16, 0, 0)  # Monday 4:00 PM
        result = self.check_business_hours(check_time=test_time)
        assert "Fechamos em 2 horas" in result["message"]
        
        # Weekend
        test_time = datetime(2024, 1, 13, 10, 0, 0)  # Saturday
        result = self.check_business_hours(check_time=test_time)
        assert "Sábado não é dia útil" in result["message"]
        
    @pytest.mark.asyncio
    async def test_check_business_hours_solar_prime_context(self):
        """Test business hours in Solar Prime context (Recife timezone)."""
        # Typical business scenario
        business_scenarios = [
            # Morning before opening
            (datetime(2024, 1, 15, 7, 30, 0), False, "Abrimos em 30 minutos"),
            # During business hours
            (datetime(2024, 1, 15, 14, 0, 0), True, "Aberto"),
            # Lunch time (still open)
            (datetime(2024, 1, 15, 12, 30, 0), True, "Aberto"),
            # After hours
            (datetime(2024, 1, 15, 19, 0, 0), False, "Fechado"),
        ]
        
        for test_time, expected_open, expected_message_part in business_scenarios:
            result = self.check_business_hours(
                check_time=test_time,
                timezone_str="America/Recife"
            )
            assert result["is_open"] == expected_open
            assert expected_message_part in result["message"]
            
    @pytest.mark.asyncio
    async def test_check_business_hours_holiday_simulation(self):
        """Test behavior on holidays (simulated as weekend)."""
        # Christmas (if it falls on a weekday, it's treated as weekend)
        # For this test, we'll use a Saturday as a holiday proxy
        holiday = datetime(2024, 12, 25, 10, 0, 0)  # Wednesday, but treating as holiday
        
        # With standard configuration, Wednesday is a business day
        result = self.check_business_hours(check_time=holiday)
        
        # In real implementation, holidays would need special handling
        # For now, we test that weekends are properly identified as non-business days
        saturday = datetime(2024, 1, 13, 10, 0, 0)
        result = self.check_business_hours(check_time=saturday)
        assert result["is_business_day"] is False
        
    @pytest.mark.asyncio
    async def test_check_business_hours_timezone_awareness(self):
        """Test that timezone handling works correctly."""
        # Create a UTC time
        utc_time = datetime(2024, 1, 15, 13, 0, 0, tzinfo=timezone.utc)  # 1:00 PM UTC
        
        # Check in Recife timezone (UTC-3)
        result = self.check_business_hours(
            check_time=utc_time,
            timezone_str="America/Recife"
        )
        
        # 1:00 PM UTC = 10:00 AM Recife time
        # Should be open
        assert result["is_open"] is True
        
    @pytest.mark.asyncio
    async def test_check_business_hours_iso_format_output(self):
        """Test that times are returned in ISO format."""
        test_time = datetime(2024, 1, 15, 10, 30, 45)
        result = self.check_business_hours(check_time=test_time)
        
        # Check ISO format
        assert "T" in result["current_time"]
        if result["next_open_time"]:
            assert "T" in result["next_open_time"]
            
        # Verify we can parse it back
        parsed_time = datetime.fromisoformat(result["current_time"])
        assert parsed_time is not None