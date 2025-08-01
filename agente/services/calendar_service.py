"""
Google Calendar Service for managing meetings and calendar operations
Uses Service Account authentication for Google Calendar API
"""

import asyncio
import threading
import time
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

from agente.core.config import (
    GOOGLE_SERVICE_ACCOUNT_EMAIL,
    GOOGLE_PRIVATE_KEY,
    GOOGLE_PROJECT_ID,
    GOOGLE_PRIVATE_KEY_ID,
    GOOGLE_CLIENT_ID,
    GOOGLE_CALENDAR_ID,
    CALENDAR_MIN_INTERVAL,
    CALENDAR_SLOT_DURATION,
    CALENDAR_BUSINESS_HOURS,
    DISABLE_GOOGLE_CALENDAR
)
from agente.core.types import CalendarSlot, CalendarEvent
from agente.core.logger import get_logger

logger = get_logger(__name__)


class GoogleCalendarService:
    """Service for Google Calendar operations with Service Account authentication
    
    Thread-safe singleton with rate limiting and robust error handling
    following Google Calendar API v3 2025 best practices.
    """
    
    # Rate limiting constants
    MAX_REQUESTS_PER_SECOND = 10
    MAX_REQUESTS_PER_MINUTE = 600
    BACKOFF_BASE_DELAY = 1.0
    BACKOFF_MAX_DELAY = 60.0
    MAX_RETRIES = 3
    
    def __init__(self):
        """Initialize Google Calendar service with Service Account credentials"""
        self.service = None
        self.credentials = None
        self.calendar_id = GOOGLE_CALENDAR_ID or 'primary'
        self.timezone = 'America/Sao_Paulo'
        
        # Rate limiting tracking
        self._request_times = []
        self._rate_limit_lock = threading.Lock()
        
        if not DISABLE_GOOGLE_CALENDAR:
            # Validate required environment variables only when not disabled
            self._validate_environment()
            try:
                # Simplified credentials info (Google 2025 standards)
                credentials_info = {
                    "type": "service_account",
                    "project_id": GOOGLE_PROJECT_ID,
                    "private_key_id": GOOGLE_PRIVATE_KEY_ID,
                    "private_key": GOOGLE_PRIVATE_KEY.replace('\\n', '\n'),
                    "client_email": GOOGLE_SERVICE_ACCOUNT_EMAIL,
                    "client_id": GOOGLE_CLIENT_ID,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                }
                
                # Create credentials with proper scopes
                self.credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=[
                        'https://www.googleapis.com/auth/calendar',
                        'https://www.googleapis.com/auth/calendar.events'
                    ]
                )
                
                # Build the service with proper error handling
                self.service = build('calendar', 'v3', credentials=self.credentials)
                
                # Test connectivity
                self._test_connectivity()
                logger.info("Google Calendar service initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Google Calendar service: {str(e)}")
                self.service = None
    
    def _validate_environment(self) -> None:
        """Validate required environment variables"""
        required_vars = {
            'GOOGLE_PROJECT_ID': GOOGLE_PROJECT_ID,
            'GOOGLE_PRIVATE_KEY': GOOGLE_PRIVATE_KEY,
            'GOOGLE_SERVICE_ACCOUNT_EMAIL': GOOGLE_SERVICE_ACCOUNT_EMAIL
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def _test_connectivity(self) -> None:
        """Test connection to Google Calendar API"""
        try:
            # Simple connectivity test
            self.service.calendars().get(
                calendarId=self.calendar_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise ValueError(f"Calendar '{self.calendar_id}' not found or not accessible")
            elif e.resp.status == 403:
                raise ValueError("Service account lacks necessary Calendar permissions")
            else:
                raise
    
    async def _rate_limited_execute(self, request_func, *args, **kwargs):
        """Execute request with rate limiting and exponential backoff"""
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                # Rate limiting check
                await self._enforce_rate_limits()
                
                # Execute request in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, 
                    lambda: request_func(*args, **kwargs).execute()
                )
                
            except HttpError as e:
                error_code = e.resp.status
                
                # Handle specific error codes
                if error_code == 401:
                    # Unauthorized - refresh credentials
                    logger.warning("Credentials expired, refreshing...")
                    if self.credentials.expired:
                        self.credentials.refresh(Request())
                    
                    if attempt < self.MAX_RETRIES:
                        continue
                    else:
                        raise ValueError("Authentication failed - check service account credentials")
                
                elif error_code == 403:
                    # Forbidden - permissions or quota issue
                    error_details = str(e)
                    if "quota" in error_details.lower() or "limit" in error_details.lower():
                        logger.warning(f"Quota exceeded on attempt {attempt + 1}")
                        if attempt < self.MAX_RETRIES:
                            await self._exponential_backoff(attempt)
                            continue
                    raise ValueError(f"Insufficient permissions or quota exceeded: {error_details}")
                
                elif error_code == 429:
                    # Rate limit exceeded
                    logger.warning(f"Rate limit exceeded on attempt {attempt + 1}")
                    if attempt < self.MAX_RETRIES:
                        await self._exponential_backoff(attempt + 2)  # Extra delay for rate limits
                        continue
                    else:
                        raise ValueError("Rate limit exceeded - too many requests")
                
                elif error_code >= 500:
                    # Server errors - retry with backoff
                    logger.warning(f"Server error {error_code} on attempt {attempt + 1}")
                    if attempt < self.MAX_RETRIES:
                        await self._exponential_backoff(attempt)
                        continue
                    else:
                        raise ValueError(f"Google Calendar API server error: {error_code}")
                
                else:
                    # Other HTTP errors - don't retry
                    raise ValueError(f"Google Calendar API error {error_code}: {str(e)}")
            
            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    logger.warning(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                    await self._exponential_backoff(attempt)
                    continue
                else:
                    raise
    
    async def _enforce_rate_limits(self) -> None:
        """Enforce rate limiting constraints"""
        with self._rate_limit_lock:
            now = time.time()
            
            # Clean old request times
            self._request_times = [t for t in self._request_times if now - t < 60]
            
            # Check per-minute limit
            if len(self._request_times) >= self.MAX_REQUESTS_PER_MINUTE:
                sleep_time = 60 - (now - self._request_times[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
            
            # Check per-second limit (last 10 requests)
            recent_requests = [t for t in self._request_times if now - t < 1]
            if len(recent_requests) >= self.MAX_REQUESTS_PER_SECOND:
                await asyncio.sleep(1)
            
            # Record this request
            self._request_times.append(now)
    
    async def _exponential_backoff(self, attempt: int) -> None:
        """Apply exponential backoff with jitter"""
        delay = min(
            self.BACKOFF_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1),
            self.BACKOFF_MAX_DELAY
        )
        logger.info(f"Applying exponential backoff: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    async def check_availability(
        self, 
        date_start: datetime, 
        date_end: datetime,
        timezone: Optional[str] = None
    ) -> List[CalendarSlot]:
        """
        Check calendar availability using FreeBusy API
        
        Args:
            date_start: Start datetime for availability check
            date_end: End datetime for availability check
            timezone: Timezone for the check (default: America/Sao_Paulo)
            
        Returns:
            List of available CalendarSlot objects
        """
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return []
        
        timezone = timezone or self.timezone
        
        try:
            # Ensure datetimes are timezone-aware
            if date_start.tzinfo is None:
                date_start = date_start.replace(tzinfo=ZoneInfo(timezone))
            if date_end.tzinfo is None:
                date_end = date_end.replace(tzinfo=ZoneInfo(timezone))
            
            # Prepare FreeBusy query
            body = {
                "timeMin": date_start.isoformat(),
                "timeMax": date_end.isoformat(),
                "timeZone": timezone,
                "items": [{"id": self.calendar_id}]
            }
            
            # Execute FreeBusy query with rate limiting
            freebusy_result = await self._rate_limited_execute(
                self.service.freebusy().query,
                body=body
            )
            
            # Extract busy periods
            busy_periods = []
            calendar_data = freebusy_result.get('calendars', {}).get(self.calendar_id, {})
            for busy in calendar_data.get('busy', []):
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                busy_periods.append((busy_start, busy_end))
            
            # Calculate available slots
            available_slots = []
            current_time = date_start
            
            while current_time < date_end:
                slot_end = current_time + timedelta(minutes=CALENDAR_SLOT_DURATION)
                
                # Check if slot is within business hours
                if (current_time.time() >= CALENDAR_BUSINESS_HOURS['start'] and 
                    slot_end.time() <= CALENDAR_BUSINESS_HOURS['end']):
                    
                    # Check if slot conflicts with any busy period
                    is_available = True
                    for busy_start, busy_end in busy_periods:
                        # Add buffer time between meetings
                        buffer_start = busy_start - timedelta(minutes=CALENDAR_MIN_INTERVAL)
                        buffer_end = busy_end + timedelta(minutes=CALENDAR_MIN_INTERVAL)
                        
                        if not (slot_end <= buffer_start or current_time >= buffer_end):
                            is_available = False
                            break
                    
                    if is_available:
                        available_slots.append(CalendarSlot(
                            start=current_time,
                            end=slot_end,
                            duration_minutes=CALENDAR_SLOT_DURATION
                        ))
                
                # Move to next slot
                current_time = slot_end
            
            logger.info(f"Found {len(available_slots)} available slots between {date_start} and {date_end}")
            return available_slots
            
        except (ValueError, HttpError, Exception) as e:
            logger.error(f"Error checking calendar availability: {str(e)}")
            return []
    
    async def create_meeting(
        self,
        title: str,
        description: str,
        start_time: datetime,
        duration_minutes: int = 60,
        attendees: Optional[List[str]] = None,
        timezone: Optional[str] = None
    ) -> Optional[CalendarEvent]:
        """
        Create a meeting with Google Meet link
        
        Args:
            title: Meeting title
            description: Meeting description
            start_time: Meeting start time
            duration_minutes: Meeting duration in minutes (default: 60)
            attendees: List of attendee email addresses
            timezone: Timezone for the meeting (default: America/Sao_Paulo)
            
        Returns:
            CalendarEvent object if successful, None otherwise
        """
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return None
        
        timezone = timezone or self.timezone
        attendees = attendees or []
        
        try:
            # Ensure start_time is timezone-aware
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=ZoneInfo(timezone))
            
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Build basic event body (following Google API Python Client documentation)
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 hours
                        {'method': 'popup', 'minutes': 10},       # 10 minutes
                    ],
                }
            }
            
            # Add attendees only if provided (to avoid Domain-Wide Delegation issues)
            if attendees and len(attendees) > 0:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # No conference data for now - basic calendar events only
            conference_data_version = 0
            
            # Create event using rate limiting (simplified approach from documentation)
            created_event = await self._rate_limited_execute(
                self.service.events().insert,
                calendarId=self.calendar_id,
                body=event,
                sendUpdates='none'  # Don't send notifications to avoid permission issues
            )
            
            # No Google Meet link for basic events
            meet_link = None
            
            # Convert to CalendarEvent
            calendar_event = CalendarEvent(
                id=created_event['id'],
                title=created_event['summary'],
                description=created_event.get('description'),
                start=datetime.fromisoformat(created_event['start']['dateTime'].replace('Z', '+00:00')),
                end=datetime.fromisoformat(created_event['end']['dateTime'].replace('Z', '+00:00')),
                attendees=attendees or [],
                location="Presencial ou Online",
                meet_link=meet_link,
                status=created_event.get('status', 'confirmed'),
                event_id=created_event['id']  # Add event_id for compatibility
            )
            
            logger.info(f"Created meeting '{title}' at {start_time} with ID: {calendar_event.id}")
            return calendar_event
            
        except (ValueError, HttpError, Exception) as e:
            logger.error(f"Error creating meeting: {str(e)}")
            return None
    
    async def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any]
    ) -> Optional[CalendarEvent]:
        """
        Update an existing calendar event
        
        Args:
            event_id: ID of the event to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated CalendarEvent if successful, None otherwise
        """
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return None
        
        try:
            # Get current event with rate limiting
            current_event = await self._rate_limited_execute(
                self.service.events().get,
                calendarId=self.calendar_id,
                eventId=event_id
            )
            
            # Apply updates
            for key, value in updates.items():
                if key == 'title':
                    current_event['summary'] = value
                elif key == 'description':
                    current_event['description'] = value
                elif key == 'start_time':
                    if isinstance(value, datetime):
                        if value.tzinfo is None:
                            value = value.replace(tzinfo=ZoneInfo(self.timezone))
                        current_event['start']['dateTime'] = value.isoformat()
                elif key == 'end_time':
                    if isinstance(value, datetime):
                        if value.tzinfo is None:
                            value = value.replace(tzinfo=ZoneInfo(self.timezone))
                        current_event['end']['dateTime'] = value.isoformat()
                elif key == 'attendees':
                    current_event['attendees'] = [{'email': email} for email in value]
            
            # Update event with rate limiting
            updated_event = await self._rate_limited_execute(
                self.service.events().update,
                calendarId=self.calendar_id,
                eventId=event_id,
                body=current_event,
                sendUpdates='all'  # 2025 best practice
            )
            
            # Convert to CalendarEvent
            meet_link = None
            conference_data = updated_event.get('conferenceData', {})
            entry_points = conference_data.get('entryPoints', [])
            for entry_point in entry_points:
                if entry_point.get('entryPointType') == 'video':
                    meet_link = entry_point.get('uri')
                    break
            
            calendar_event = CalendarEvent(
                id=updated_event['id'],
                title=updated_event['summary'],
                description=updated_event.get('description'),
                start=datetime.fromisoformat(updated_event['start']['dateTime'].replace('Z', '+00:00')),
                end=datetime.fromisoformat(updated_event['end']['dateTime'].replace('Z', '+00:00')),
                attendees=[att['email'] for att in updated_event.get('attendees', [])],
                location="Online via Google Meet",
                meet_link=meet_link,
                status=updated_event.get('status', 'confirmed')
            )
            
            logger.info(f"Updated event {event_id}")
            return calendar_event
            
        except (ValueError, HttpError, Exception) as e:
            logger.error(f"Error updating event: {str(e)}")
            return None
    
    async def cancel_event(
        self,
        event_id: str,
        send_notifications: bool = True
    ) -> bool:
        """
        Cancel a calendar event
        
        Args:
            event_id: ID of the event to cancel
            send_notifications: Whether to send cancellation notifications
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return False
        
        try:
            # Delete event with rate limiting
            await self._rate_limited_execute(
                self.service.events().delete,
                calendarId=self.calendar_id,
                eventId=event_id,
                sendNotifications=send_notifications
            )
            
            logger.info(f"Cancelled event {event_id}")
            return True
            
        except (ValueError, HttpError, Exception) as e:
            logger.error(f"Error cancelling event: {str(e)}")
            return False
    
    async def get_calendar_events(
        self,
        time_min: datetime,
        time_max: datetime,
        timezone: Optional[str] = None
    ) -> List[CalendarEvent]:
        """
        Get calendar events within a time range
        
        Args:
            time_min: Start of time range
            time_max: End of time range
            timezone: Timezone for the query (default: America/Sao_Paulo)
            
        Returns:
            List of CalendarEvent objects
        """
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return []
        
        timezone = timezone or self.timezone
        
        try:
            # Ensure datetimes are timezone-aware
            if time_min.tzinfo is None:
                time_min = time_min.replace(tzinfo=ZoneInfo(timezone))
            if time_max.tzinfo is None:
                time_max = time_max.replace(tzinfo=ZoneInfo(timezone))
            
            # Query events with rate limiting
            events_result = await self._rate_limited_execute(
                self.service.events().list,
                calendarId=self.calendar_id,
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            )
            
            events = events_result.get('items', [])
            calendar_events = []
            
            for event in events:
                # Skip all-day events
                if 'dateTime' not in event['start']:
                    continue
                
                # Extract Google Meet link
                meet_link = None
                conference_data = event.get('conferenceData', {})
                entry_points = conference_data.get('entryPoints', [])
                for entry_point in entry_points:
                    if entry_point.get('entryPointType') == 'video':
                        meet_link = entry_point.get('uri')
                        break
                
                calendar_event = CalendarEvent(
                    id=event['id'],
                    title=event.get('summary', 'No title'),
                    description=event.get('description'),
                    start=datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00')),
                    end=datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00')),
                    attendees=[att['email'] for att in event.get('attendees', [])],
                    location=event.get('location', 'Online via Google Meet'),
                    meet_link=meet_link,
                    status=event.get('status', 'confirmed')
                )
                calendar_events.append(calendar_event)
            
            logger.info(f"Retrieved {len(calendar_events)} events between {time_min} and {time_max}")
            return calendar_events
            
        except (ValueError, HttpError, Exception) as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return []
    
    async def quick_add(self, text: str) -> Optional[CalendarEvent]:
        """
        Quick add an event using natural language
        
        Args:
            text: Natural language description of the event
            
        Returns:
            CalendarEvent if successful, None otherwise
        """
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return None
        
        try:
            # Use Google Calendar's natural language parsing with rate limiting
            created_event = await self._rate_limited_execute(
                self.service.events().quickAdd,
                calendarId=self.calendar_id,
                text=text
            )
            
            # Convert to CalendarEvent
            meet_link = None
            conference_data = created_event.get('conferenceData', {})
            entry_points = conference_data.get('entryPoints', [])
            for entry_point in entry_points:
                if entry_point.get('entryPointType') == 'video':
                    meet_link = entry_point.get('uri')
                    break
            
            # Handle both all-day and timed events
            if 'dateTime' in created_event['start']:
                start = datetime.fromisoformat(created_event['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(created_event['end']['dateTime'].replace('Z', '+00:00'))
            else:
                # For all-day events, use date only
                start = datetime.fromisoformat(created_event['start']['date'])
                end = datetime.fromisoformat(created_event['end']['date'])
            
            calendar_event = CalendarEvent(
                id=created_event['id'],
                title=created_event.get('summary', 'Quick Event'),
                description=created_event.get('description'),
                start=start,
                end=end,
                attendees=[att['email'] for att in created_event.get('attendees', [])],
                location=created_event.get('location', 'Online via Google Meet'),
                meet_link=meet_link,
                status=created_event.get('status', 'confirmed')
            )
            
            logger.info(f"Quick added event: {text}")
            return calendar_event
            
        except (ValueError, HttpError, Exception) as e:
            logger.error(f"Error in quick add: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if Google Calendar service is available"""
        return self.service is not None and not DISABLE_GOOGLE_CALENDAR


# Thread-safe singleton implementation
_calendar_service = None
_calendar_service_lock = threading.Lock()


def get_calendar_service() -> GoogleCalendarService:
    """Get or create thread-safe singleton instance of GoogleCalendarService"""
    global _calendar_service
    
    # Double-checked locking pattern for thread safety
    if _calendar_service is None:
        with _calendar_service_lock:
            if _calendar_service is None:
                _calendar_service = GoogleCalendarService()
    
    return _calendar_service