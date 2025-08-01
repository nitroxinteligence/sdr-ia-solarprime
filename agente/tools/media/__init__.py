"""
Media Processing Tools para processamento de imagens, áudio e documentos
"""

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
