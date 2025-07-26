"""
Follow-up Model
===============
Modelo para follow-ups automáticos
"""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from models.base import BaseDBModel


class FollowUp(BaseDBModel):
    """Modelo de Follow-up"""
    
    lead_id: UUID = Field(..., description="ID do lead")
    
    # Agendamento
    scheduled_at: datetime = Field(..., description="Quando executar o follow-up")
    type: str = Field(..., description="Tipo: reminder, check_in, reengagement")
    
    # Conteúdo
    message: str = Field(..., description="Mensagem a ser enviada")
    
    # Status
    status: str = Field("pending", description="Status: pending, executed, failed, cancelled")
    executed_at: Optional[datetime] = Field(None, description="Quando foi executado")
    
    # Resultado
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado da execução")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "scheduled_at": "2024-01-16T10:00:00",
                "type": "reminder",
                "message": "Oi! Você teve tempo de pensar sobre a proposta de energia solar?",
                "status": "pending"
            }
        }


class FollowUpCreate(BaseModel):
    """Schema para criação de follow-up"""
    lead_id: UUID
    scheduled_at: datetime
    type: str
    message: str
    

class FollowUpUpdate(BaseModel):
    """Schema para atualização de follow-up"""
    scheduled_at: Optional[datetime] = None
    message: Optional[str] = None
    status: Optional[str] = None
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None