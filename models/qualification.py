"""
Lead Qualification Model
========================
Modelo para qualificação de leads
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from models.base import BaseDBModel


class LeadQualification(BaseDBModel):
    """Modelo de Qualificação de Lead"""
    
    lead_id: UUID = Field(..., description="ID do lead")
    
    # Critérios de qualificação
    has_own_property: Optional[bool] = Field(None, description="Possui imóvel próprio")
    decision_maker: Optional[bool] = Field(None, description="É tomador de decisão")
    urgency_level: Optional[str] = Field(None, description="Nível de urgência: alta, média, baixa")
    
    # Objeções e soluções
    objections: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Lista de objeções levantadas"
    )
    solutions_presented: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Soluções apresentadas"
    )
    
    # Dados extraídos
    extracted_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dados extraídos durante a qualificação"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "has_own_property": True,
                "decision_maker": True,
                "urgency_level": "alta",
                "objections": [
                    {"type": "price", "description": "Achou o investimento alto"}
                ],
                "solutions_presented": [
                    {"type": "financing", "description": "Ofereceu parcelamento em 60x"}
                ]
            }
        }


class QualificationCreate(BaseModel):
    """Schema para criação de qualificação"""
    lead_id: UUID
    has_own_property: Optional[bool] = None
    decision_maker: Optional[bool] = None
    urgency_level: Optional[str] = None
    

class QualificationUpdate(BaseModel):
    """Schema para atualização de qualificação"""
    has_own_property: Optional[bool] = None
    decision_maker: Optional[bool] = None
    urgency_level: Optional[str] = None
    objections: Optional[List[Dict[str, Any]]] = None
    solutions_presented: Optional[List[Dict[str, Any]]] = None
    extracted_data: Optional[Dict[str, Any]] = None