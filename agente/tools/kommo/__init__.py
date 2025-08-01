"""
Kommo CRM Tools para integração com o sistema
"""

# Import all Kommo tools
from .search_lead import (
    SearchKommoLeadTool,
    SearchLeadByPhoneTool
)
from .create_lead import CreateKommoLeadTool
from .update_lead import UpdateKommoLeadTool
from .update_stage import (
    UpdateKommoStageTool,
    GetLeadStageTool
)
from .add_note import (
    AddKommoNoteTool,
    AddQualificationNoteTool,
    AddInteractionLogTool
)
from .schedule_activity import (
    ScheduleKommoActivityTool,
    ScheduleFollowUpTool,
    ScheduleMeetingReminderTool
)

# Import the original function names for backward compatibility
from .search_lead import search_kommo_lead
from .create_lead import create_kommo_lead
from .update_lead import update_kommo_lead
from .update_stage import update_kommo_stage
from .add_note import add_kommo_note
from .schedule_activity import schedule_kommo_activity

# Export all tools
__all__ = [
    # Original function names
    'search_kommo_lead',
    'create_kommo_lead',
    'update_kommo_lead',
    'update_kommo_stage',
    'add_kommo_note',
    'schedule_kommo_activity',
    
    # Search tools
    'SearchKommoLeadTool',
    'SearchLeadByPhoneTool',
    
    # Create tool
    'CreateKommoLeadTool',
    
    # Update tools
    'UpdateKommoLeadTool',
    'UpdateKommoStageTool',
    'GetLeadStageTool',
    
    # Note tools
    'AddKommoNoteTool',
    'AddQualificationNoteTool',
    'AddInteractionLogTool',
    
    # Activity tools
    'ScheduleKommoActivityTool',
    'ScheduleFollowUpTool',
    'ScheduleMeetingReminderTool'
]