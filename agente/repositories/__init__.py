"""
Repositories do sistema SDR Agent
"""

from .lead_repository import LeadRepository, get_lead_repository
from .conversation_repository import ConversationRepository, get_conversation_repository
from .message_repository import MessageRepository, get_message_repository
from .followup_repository import FollowUpRepository, get_followup_repository

__all__ = [
    'LeadRepository',
    'get_lead_repository',
    'ConversationRepository',
    'get_conversation_repository',
    'MessageRepository',
    'get_message_repository',
    'FollowUpRepository',
    'get_followup_repository'
]