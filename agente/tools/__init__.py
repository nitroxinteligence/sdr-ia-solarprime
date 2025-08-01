"""
Tools AGnO para o SDR Agent

Exporta todas as 30 tools organizadas por categoria:
- WhatsApp Tools (8)
- Kommo Tools (6)
- Calendar Tools (5)
- Database Tools (6)
- Media Tools (3)
- Utility Tools (2)
"""

# WhatsApp Tools
from .whatsapp import (
    SendTextMessageTool,
    SendAudioMessageTool,
    SendImageMessageTool,
    SendDocumentMessageTool,
    SendLocationMessageTool,
    TypeSimulationTool,
    MessageChunkingTool,
    MessageBufferTool
)

# Kommo Tools
from .kommo import (
    SearchKommoLeadTool,
    CreateKommoLeadTool,
    UpdateKommoLeadTool,
    UpdateKommoStageTool,
    AddKommoNoteTool,
    ScheduleKommoActivityTool
)

# Calendar Tools
from .calendar import (
    CheckAvailabilityTool,
    CreateMeetingTool,
    UpdateMeetingTool,
    CancelMeetingTool,
    SendCalendarInviteTool
)

# Database Tools
from .database import (
    CreateLeadTool,
    UpdateLeadTool,
    GetLeadTool,
    SaveMessageTool,
    UpdateConversationTool,
    ScheduleFollowUpTool
)

# Media Tools
from .media import (
    ProcessImageTool,
    ProcessAudioTool,
    ProcessDocumentTool
)

# Utility Tools
from .utility import (
    ValidatePhoneTool,
    FormatCurrencyTool
)

# Lista de todas as tools para facilitar registro
ALL_TOOLS = [
    # WhatsApp
    SendTextMessageTool,
    SendAudioMessageTool,
    SendImageMessageTool,
    SendDocumentMessageTool,
    SendLocationMessageTool,
    TypeSimulationTool,
    MessageChunkingTool,
    MessageBufferTool,
    # Kommo
    SearchKommoLeadTool,
    CreateKommoLeadTool,
    UpdateKommoLeadTool,
    UpdateKommoStageTool,
    AddKommoNoteTool,
    ScheduleKommoActivityTool,
    # Calendar
    CheckAvailabilityTool,
    CreateMeetingTool,
    UpdateMeetingTool,
    CancelMeetingTool,
    SendCalendarInviteTool,
    # Database
    CreateLeadTool,
    UpdateLeadTool,
    GetLeadTool,
    SaveMessageTool,
    UpdateConversationTool,
    ScheduleFollowUpTool,
    # Media
    ProcessImageTool,
    ProcessAudioTool,
    ProcessDocumentTool,
    # Utility
    ValidatePhoneTool,
    FormatCurrencyTool
]

__all__ = [
    # WhatsApp Tools
    'SendTextMessageTool',
    'SendAudioMessageTool',
    'SendImageMessageTool',
    'SendDocumentMessageTool',
    'SendLocationMessageTool',
    'TypeSimulationTool',
    'MessageChunkingTool',
    'MessageBufferTool',
    # Kommo Tools
    'SearchKommoLeadTool',
    'CreateKommoLeadTool',
    'UpdateKommoLeadTool',
    'UpdateKommoStageTool',
    'AddKommoNoteTool',
    'ScheduleKommoActivityTool',
    # Calendar Tools
    'CheckAvailabilityTool',
    'CreateMeetingTool',
    'UpdateMeetingTool',
    'CancelMeetingTool',
    'SendCalendarInviteTool',
    # Database Tools
    'CreateLeadTool',
    'UpdateLeadTool',
    'GetLeadTool',
    'SaveMessageTool',
    'UpdateConversationTool',
    'ScheduleFollowUpTool',
    # Media Tools
    'ProcessImageTool',
    'ProcessAudioTool',
    'ProcessDocumentTool',
    # Utility Tools
    'ValidatePhoneTool',
    'FormatCurrencyTool',
    # Lista completa
    'ALL_TOOLS'
]