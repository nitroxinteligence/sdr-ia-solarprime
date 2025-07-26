"""
Conversation Model
==================
Modelo para conversas do WhatsApp
"""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from models.base import BaseDBModel


class Conversation(BaseDBModel):
    """Modelo de Conversa"""
    
    lead_id: UUID = Field(..., description="ID do lead")
    session_id: str = Field(..., description="ID único da sessão")
    
    # Timeline
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(None, description="Quando a conversa terminou")
    
    # Métricas
    total_messages: int = Field(0, description="Total de mensagens trocadas")
    current_stage: Optional[str] = Field(None, description="Estágio atual da conversa")
    sentiment: Optional[str] = Field("neutro", description="Sentimento: positivo, neutro, negativo")
    
    # Status
    is_active: bool = Field(True, description="Se a conversa está ativa")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "5511999999999_20240115",
                "total_messages": 10,
                "current_stage": "QUALIFICATION",
                "sentiment": "positivo",
                "is_active": True
            }
        }


class ConversationCreate(BaseModel):
    """Schema para criação de conversa"""
    lead_id: UUID
    session_id: str
    current_stage: Optional[str] = "INITIAL_CONTACT"
    
    
class ConversationUpdate(BaseModel):
    """Schema para atualização de conversa"""
    ended_at: Optional[datetime] = None
    total_messages: Optional[int] = None
    current_stage: Optional[str] = None
    sentiment: Optional[str] = None
    is_active: Optional[bool] = None