#!/usr/bin/env python3
"""
Quick Google Calendar Health Check
Fast validation script for CI/CD and monitoring
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agente.services.calendar_service import get_calendar_service
from agente.core.config import DISABLE_GOOGLE_CALENDAR

async def quick_check():
    """Quick health check for Google Calendar service"""
    
    # Check if service is disabled
    if DISABLE_GOOGLE_CALENDAR:
        print("⚠️  Google Calendar está desabilitado")
        return True  # Not an error if intentionally disabled
    
    try:
        # Initialize service
        service = get_calendar_service()
        
        if not service.is_available():
            print("❌ Serviço Google Calendar não está disponível")
            return False
        
        # Quick connectivity test
        await service._rate_limited_execute(
            service.service.calendars().get,
            calendarId=service.calendar_id
        )
        
        print("✅ Google Calendar está funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Falha no Google Calendar: {str(e)}")
        return False

if __name__ == "__main__":
    is_healthy = asyncio.run(quick_check())
    sys.exit(0 if is_healthy else 1)