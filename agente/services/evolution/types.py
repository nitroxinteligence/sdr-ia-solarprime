"""
Tipos e dataclasses para Evolution API v2
Define estruturas de dados tipadas para garantir type safety
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List


class MessageStatus(Enum):
    """Status de mensagem"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MediaType(Enum):
    """Tipos de mídia suportados"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class WebhookEvent(Enum):
    """Eventos do webhook"""
    CONNECTION_UPDATE = "connection.update"
    MESSAGES_SET = "messages.set"
    MESSAGES_UPSERT = "messages.upsert"
    MESSAGES_UPDATE = "messages.update"
    MESSAGES_DELETE = "messages.delete"
    SEND_MESSAGE = "send.message"


class InstanceState(Enum):
    """Estados da instância"""
    OPEN = "open"
    CLOSE = "close"
    CONNECTING = "connecting"


@dataclass
class MessageKey:
    """Identificador único de mensagem"""
    id: str
    fromMe: bool
    remoteJid: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageKey':
        """Cria MessageKey a partir de dicionário"""
        return cls(
            id=data.get('id', ''),
            fromMe=data.get('fromMe', False),
            remoteJid=data.get('remoteJid', '')
        )


@dataclass
class TextMessage:
    """Mensagem de texto"""
    number: str
    text: str
    delay: int = 0
    linkPreview: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para API"""
        return {
            "number": self.number,
            "text": self.text,
            "delay": self.delay,
            "linkPreview": self.linkPreview,
            "mentionsEveryOne": False,
            "mentioned": []
        }


@dataclass
class MediaMessage:
    """Mensagem de mídia"""
    number: str
    mediaUrl: str
    mediaType: MediaType
    caption: Optional[str] = None
    delay: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para API"""
        data = {
            "number": self.number,
            "mediaUrl": self.mediaUrl,
            "delay": self.delay
        }
        if self.caption:
            data["caption"] = self.caption
        return data


@dataclass
class ReactionMessage:
    """Reação a mensagem"""
    number: str
    reaction: str
    msgId: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para API"""
        return {
            "number": self.number,
            "reaction": {
                "value": self.reaction,
                "msgId": self.msgId
            }
        }


@dataclass
class LocationMessage:
    """Mensagem de localização"""
    number: str
    latitude: float
    longitude: float
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para API"""
        location = {
            "latitude": self.latitude,
            "longitude": self.longitude
        }
        if self.name:
            location["name"] = self.name
            
        return {
            "number": self.number,
            "location": location
        }


@dataclass
class InstanceStatus:
    """Status da instância"""
    state: InstanceState
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InstanceStatus':
        """Cria InstanceStatus a partir de dicionário"""
        state_str = data.get('state', 'close')
        try:
            state = InstanceState(state_str)
        except ValueError:
            state = InstanceState.CLOSE
            
        return cls(
            state=state,
            error=data.get('error')
        )


@dataclass
class WebhookConfig:
    """Configuração de webhook"""
    url: str
    events: List[WebhookEvent]
    webhook_by_events: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para API"""
        return {
            "url": self.url,
            "webhook_by_events": self.webhook_by_events,
            "events": [event.value for event in self.events]
        }


@dataclass
class MessageResponse:
    """Resposta de envio de mensagem"""
    key: MessageKey
    status: MessageStatus
    message: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageResponse':
        """Cria MessageResponse a partir de dicionário"""
        key_data = data.get('key', {})
        status_str = data.get('status', 'pending')
        
        try:
            status = MessageStatus(status_str)
        except ValueError:
            status = MessageStatus.PENDING
            
        return cls(
            key=MessageKey.from_dict(key_data),
            status=status,
            message=data.get('message')
        )