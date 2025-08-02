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

# 🚀 WHATSAPP TOOLS REMOVIDAS - Evolution API faz tudo automaticamente!
# Evolution API com splitMessages=True substitui TODAS as tools de WhatsApp:
# - from .whatsapp import (...)  # ❌ TODAS REMOVIDAS
# - MessageChunkingTool          # ❌ DELETADO - Evolution API chunking nativo  
# - MessageBufferTool            # ❌ DELETADO - Evolution API delay nativo
# - SendTextMessageTool          # ❌ DELETADO - Evolution API send nativo
# - Todas as outras WhatsApp tools também foram removidas

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

# 🚀 LISTA DE TOOLS ATUALIZADA - Sem WhatsApp tools (Evolution API faz tudo)
ALL_TOOLS = [
    # 🚀 WhatsApp tools REMOVIDAS - Evolution API substitui:
    # - SendTextMessageTool,     ❌ REMOVIDO - Evolution API send nativo
    # - MessageChunkingTool,     ❌ REMOVIDO - Evolution API splitMessages  
    # - MessageBufferTool,       ❌ REMOVIDO - Evolution API delay nativo
    # - Todas as outras WhatsApp tools também removidas
    
    # Kommo Tools (MANTIDAS)
    SearchKommoLeadTool,
    CreateKommoLeadTool,
    UpdateKommoLeadTool,
    UpdateKommoStageTool,
    AddKommoNoteTool,
    ScheduleKommoActivityTool,
    # Calendar Tools (MANTIDAS)
    CheckAvailabilityTool,
    CreateMeetingTool,
    UpdateMeetingTool,
    CancelMeetingTool,
    SendCalendarInviteTool,
    # Database Tools (MANTIDAS)
    CreateLeadTool,
    UpdateLeadTool,
    GetLeadTool,
    SaveMessageTool,
    UpdateConversationTool,
    ScheduleFollowUpTool,
    # Media Tools (MANTIDAS)
    ProcessImageTool,
    ProcessAudioTool,
    ProcessDocumentTool,
    # Utility Tools (MANTIDAS)
    ValidatePhoneTool,
    FormatCurrencyTool
]

__all__ = [
    # 🚀 WhatsApp Tools REMOVIDAS - Evolution API faz tudo automaticamente!
    # - 'SendTextMessageTool',     ❌ REMOVIDO - Evolution API send nativo
    # - 'MessageChunkingTool',     ❌ REMOVIDO - Evolution API splitMessages
    # - 'MessageBufferTool',       ❌ REMOVIDO - Evolution API delay nativo
    # - Todas as outras WhatsApp tools também removidas
    
    # Kommo Tools (MANTIDAS)
    'SearchKommoLeadTool',
    'CreateKommoLeadTool',
    'UpdateKommoLeadTool',
    'UpdateKommoStageTool',
    'AddKommoNoteTool',
    'ScheduleKommoActivityTool',
    # Calendar Tools (MANTIDAS)
    'CheckAvailabilityTool',
    'CreateMeetingTool',
    'UpdateMeetingTool',
    'CancelMeetingTool',
    'SendCalendarInviteTool',
    # Database Tools (MANTIDAS)
    'CreateLeadTool',
    'UpdateLeadTool',
    'GetLeadTool',
    'SaveMessageTool',
    'UpdateConversationTool',
    'ScheduleFollowUpTool',
    # Media Tools (MANTIDAS)
    'ProcessImageTool',
    'ProcessAudioTool',
    'ProcessDocumentTool',
    # Utility Tools (MANTIDAS)
    'ValidatePhoneTool',
    'FormatCurrencyTool',
    # Lista completa (ATUALIZADA)
    'ALL_TOOLS'
]