"""
Message Model
=============
Modelo para mensagens do WhatsApp
"""

from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from models.base import BaseDBModel


class Message(BaseDBModel):
    """Modelo de Mensagem"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    whatsapp_message_id: Optional[str] = Field(None, description="ID da mensagem no WhatsApp")
    
    # Conteúdo
    role: str = Field(..., description="Role: user ou assistant")
    content: str = Field(..., description="Conteúdo da mensagem")
    
    # Mídia
    media_type: Optional[str] = Field(None, description="Tipo: image, audio, document, video")
    media_url: Optional[str] = Field(None, description="URL da mídia")
    media_data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais da mídia")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "whatsapp_message_id": "MSG123456",
                "role": "user",
                "content": "Olá, quero saber sobre energia solar",
                "media_type": None,
                "media_url": None
            }
        }


class MessageCreate(BaseModel):
    """Schema para criação de mensagem"""
    conversation_id: UUID
    whatsapp_message_id: Optional[str] = None
    role: str
    content: str
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    media_data: Optional[Dict[str, Any]] = None