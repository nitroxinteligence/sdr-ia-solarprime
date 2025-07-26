"""
Analytics Model
===============
Modelo para eventos de analytics
"""

from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from models.base import BaseDBModel


class Analytics(BaseDBModel):
    """Modelo de Analytics"""
    
    lead_id: Optional[UUID] = Field(None, description="ID do lead (opcional)")
    
    # Evento
    event_type: str = Field(..., description="Tipo do evento")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Dados do evento")
    
    # Contexto
    session_id: Optional[str] = Field(None, description="ID da sessão")
    user_agent: Optional[str] = Field(None, description="User agent")
    ip_address: Optional[str] = Field(None, description="IP do cliente")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "qualification_completed",
                "event_data": {
                    "score": 85,
                    "stage": "SCHEDULING",
                    "duration_seconds": 300
                }
            }
        }


class AnalyticsCreate(BaseModel):
    """Schema para criação de evento analytics"""
    lead_id: Optional[UUID] = None
    event_type: str
    event_data: Dict[str, Any] = {}
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None