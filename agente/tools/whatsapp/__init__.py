"""
WhatsApp Tools para integração com Evolution API
"""

from .send_text_message import SendTextMessageTool
from .send_audio_message import SendAudioMessageTool
from .send_image_message import SendImageMessageTool
from .send_document_message import SendDocumentMessageTool
from .send_location_message import SendLocationMessageTool
from .send_greetings import SendGreetingsTool
from .type_simulation import TypeSimulationTool
from .message_chunking import MessageChunkingTool
from .message_buffer import MessageBufferTool, ClearBufferTool, GetBufferStatusTool
from .send_reaction import SendReactionTool

# Import function names for backward compatibility
from .send_text_message import send_text_message
from .send_audio_message import send_audio_message
from .send_image_message import send_image_message
from .send_document_message import send_document_message
from .send_location_message import send_location_message
from .send_greetings import send_greetings
from .type_simulation import type_simulation
from .message_chunking import message_chunking
from .message_buffer import message_buffer
from .send_reaction import send_reaction

__all__ = [
    # Function names
    'send_text_message',
    'send_audio_message',
    'send_image_message',
    'send_document_message',
    'send_location_message',
    'send_greetings',
    'type_simulation',
    'message_chunking',
    'message_buffer',
    'send_reaction',
    # Tool classes
    'SendTextMessageTool',
    'SendAudioMessageTool',
    'SendImageMessageTool',
    'SendDocumentMessageTool',
    'SendLocationMessageTool',
    'SendGreetingsTool',
    'TypeSimulationTool',
    'MessageChunkingTool',
    'MessageBufferTool',
    'ClearBufferTool',
    'GetBufferStatusTool',
    'SendReactionTool'
]