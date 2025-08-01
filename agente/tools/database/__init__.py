"""
Database Tools para persistência e gerenciamento de dados
"""

from .create_lead import CreateLeadTool
from .update_lead import UpdateLeadTool
from .get_lead import GetLeadTool
from .save_message import SaveMessageTool
from .update_conversation import UpdateConversationTool
from .schedule_followup import ScheduleFollowUpTool

# Import function names for backward compatibility
from .create_lead import create_lead
from .update_lead import update_lead
from .get_lead import get_lead
from .save_message import save_message
from .update_conversation import update_conversation
from .schedule_followup import schedule_followup

__all__ = [
    # Function names
    'create_lead',
    'update_lead',
    'get_lead',
    'save_message',
    'update_conversation',
    'schedule_followup',
    # Tool classes
    'CreateLeadTool',
    'UpdateLeadTool',
    'GetLeadTool',
    'SaveMessageTool',
    'UpdateConversationTool',
    'ScheduleFollowUpTool'
]
