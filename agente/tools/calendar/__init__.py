"""
Calendar Tools para integração com Google Calendar
"""

from .check_availability import CheckAvailabilityTool
from .create_meeting import CreateMeetingTool
from .update_meeting import UpdateMeetingTool
from .cancel_meeting import CancelMeetingTool
from .send_invite import SendCalendarInviteTool

# Import function names for backward compatibility
from .check_availability import check_availability
from .create_meeting import create_meeting
from .update_meeting import update_meeting
from .cancel_meeting import cancel_meeting
from .send_invite import send_calendar_invite

__all__ = [
    # Function names
    'check_availability',
    'create_meeting',
    'update_meeting',
    'cancel_meeting',
    'send_calendar_invite',
    # Tool classes
    'CheckAvailabilityTool',
    'CreateMeetingTool',
    'UpdateMeetingTool',
    'CancelMeetingTool',
    'SendCalendarInviteTool'
]