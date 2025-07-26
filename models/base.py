"""
Base Model
==========
Modelo base para todos os modelos do banco de dados
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class BaseDBModel(BaseModel):
    """Modelo base com campos comuns"""
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    
    def dict(self, **kwargs):
        """Override dict to ensure UUID serialization"""
        data = super().dict(**kwargs)
        # Converter UUIDs para string
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
        return data