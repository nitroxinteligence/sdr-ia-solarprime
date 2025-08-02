"""
Evolution API Service - Nova implementação modular
Serviço simplificado e essencial para integração com WhatsApp
"""

from .client import EvolutionClient
from .messages import MessageService
from .media import MediaService
from .webhooks import WebhookService
from .service import EvolutionService, get_evolution_service, evolution_service
from .types import (
    MessageStatus,
    MediaType,
    WebhookEvent,
    InstanceState,
    TextMessage,
    MediaMessage,
    ReactionMessage,
    LocationMessage,
    MessageResponse,
    MessageKey,
    InstanceStatus,
    WebhookConfig
)

__all__ = [
    # Main Service
    'EvolutionService',
    'get_evolution_service',
    'evolution_service',
    
    # Client
    'EvolutionClient',
    
    # Services
    'MessageService',
    'MediaService',
    'WebhookService',
    
    # Types
    'MessageStatus',
    'MediaType',
    'WebhookEvent',
    'InstanceState',
    'TextMessage',
    'MediaMessage',
    'ReactionMessage',
    'LocationMessage',
    'MessageResponse',
    'MessageKey',
    'InstanceStatus',
    'WebhookConfig'
]

# Versão do módulo
__version__ = '2.0.0'