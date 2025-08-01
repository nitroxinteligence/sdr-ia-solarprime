"""
Test script for Google Calendar Service
"""

import asyncio
from datetime import datetime, timedelta
from agente.services.calendar_service import GoogleCalendarService


async def test_calendar_service():
    """Test the calendar service functionality"""
    # Initialize service
    calendar_service = GoogleCalendarService()
    
    if not calendar_service.is_available():
        print("❌ Google Calendar service is not available. Check your configuration.")
        return
    
    print("✅ Google Calendar service initialized successfully")
    
    # Test 1: Check availability for the next 7 days
    print("\n📅 Testing availability check...")
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    available_slots = await calendar_service.check_availability(start_date, end_date)
    print(f"Found {len(available_slots)} available slots in the next 7 days")
    
    # Show first 5 slots
    for i, slot in enumerate(available_slots[:5]):
        print(f"  Slot {i+1}: {slot.start.strftime('%Y-%m-%d %H:%M')} - {slot.end.strftime('%H:%M')}")
    
    # Test 2: Get existing events
    print("\n📆 Testing get calendar events...")
    events = await calendar_service.get_calendar_events(start_date, end_date)
    print(f"Found {len(events)} existing events in the next 7 days")
    
    for event in events[:3]:
        print(f"  - {event.title} at {event.start.strftime('%Y-%m-%d %H:%M')}")
        if event.meet_link:
            print(f"    Meet link: {event.meet_link}")
    
    # Test 3: Quick add (commented out to avoid creating test events)
    # print("\n🚀 Testing quick add...")
    # quick_event = await calendar_service.quick_add("Meeting tomorrow at 3pm")
    # if quick_event:
    #     print(f"Created quick event: {quick_event.title} at {quick_event.start}")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_calendar_service())