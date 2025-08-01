#!/usr/bin/env python3
"""
Script para adicionar exports de funções nos módulos de tools
"""
import os

# Database tools
database_init = """\"\"\"
Database Tools para persistência e gerenciamento de dados
\"\"\"

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
"""

# Media tools
media_init = """\"\"\"
Media Processing Tools para processamento de imagens, áudio e documentos
\"\"\"

from .process_image import ProcessImageTool
from .process_audio import ProcessAudioTool
from .process_document import ProcessDocumentTool

# Import function names for backward compatibility
from .process_image import process_image
from .process_audio import process_audio
from .process_document import process_document

__all__ = [
    # Function names
    'process_image',
    'process_audio',
    'process_document',
    # Tool classes
    'ProcessImageTool',
    'ProcessAudioTool',
    'ProcessDocumentTool'
]
"""

# Utility tools
utility_init = """\"\"\"
Utility Tools para funções utilitárias
\"\"\"

from .validate_phone import ValidatePhoneTool
from .format_currency import FormatCurrencyTool

# Import function names for backward compatibility
from .validate_phone import validate_phone
from .format_currency import format_currency

__all__ = [
    # Function names
    'validate_phone',
    'format_currency',
    # Tool classes
    'ValidatePhoneTool',
    'FormatCurrencyTool'
]
"""

# Write files
with open("agente/tools/database/__init__.py", "w") as f:
    f.write(database_init)
    
with open("agente/tools/media/__init__.py", "w") as f:
    f.write(media_init)
    
with open("agente/tools/utility/__init__.py", "w") as f:
    f.write(utility_init)

print("✅ Tool exports fixed!")