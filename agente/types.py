"""
Re-export types from core.types for backwards compatibility
"""
from agente.core.types import *

__all__ = [
    "Lead",
    "LeadStage", 
    "LeadQualification",
    "PropertyType",
    "UrgencyLevel",
    "Conversation",
    "Message",
    "MessageRole",
    "MediaType",
    "FollowUp",
    "FollowUpType",
    "FollowUpStatus"
]