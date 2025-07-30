"""
Lead Model
==========
Modelo para leads (potenciais clientes)
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr
from models.base import BaseDBModel


class Lead(BaseDBModel):
    """Modelo de Lead"""
    
    # Identificação
    phone_number: str = Field(..., description="Número de telefone (único)")
    name: Optional[str] = Field(None, description="Nome completo")
    email: Optional[EmailStr] = Field(None, description="Email")
    document: Optional[str] = Field(None, description="CPF ou CNPJ")
    
    # Informações da propriedade
    property_type: Optional[str] = Field(None, description="Tipo: casa, apartamento, comercial")
    address: Optional[str] = Field(None, description="Endereço completo")
    
    # Dados da conta de luz
    bill_value: Optional[Decimal] = Field(None, description="Valor da conta de luz")
    consumption_kwh: Optional[int] = Field(None, description="Consumo em kWh")
    
    # Qualificação
    current_stage: str = Field("INITIAL_CONTACT", description="Estágio atual do lead")
    qualification_score: Optional[int] = Field(None, ge=0, le=100, description="Score de qualificação")
    interested: bool = Field(True, description="Se está interessado")
    qualification_status: Optional[str] = Field("PENDING", description="Status de qualificação: PENDING, QUALIFIED, NOT_QUALIFIED")
    
    # Critérios de qualificação
    is_decision_maker: Optional[bool] = Field(None, description="Se é o decisor principal")
    has_solar_system: Optional[bool] = Field(None, description="Se já possui sistema solar")
    wants_new_solar_system: Optional[bool] = Field(None, description="Se quer instalar novo sistema solar")
    has_active_contract: Optional[bool] = Field(None, description="Se tem contrato de energia vigente")
    contract_end_date: Optional[datetime] = Field(None, description="Data de término do contrato atual")
    solution_interest: Optional[str] = Field(None, description="Tipo de solução de interesse")
    
    # Observações e notas
    notes: Optional[str] = Field(None, description="Observações gerais sobre o lead")
    
    # Integrações
    kommo_lead_id: Optional[str] = Field(None, description="ID do lead no Kommo CRM")
    
    # Google Calendar
    google_event_id: Optional[str] = Field(None, description="ID do evento no Google Calendar")
    meeting_scheduled_at: Optional[datetime] = Field(None, description="Data/hora da reunião agendada")
    meeting_type: Optional[str] = Field("initial_meeting", description="Tipo de reunião")
    meeting_status: Optional[str] = Field("scheduled", description="Status da reunião")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "5511999999999",
                "name": "João Silva",
                "email": "joao@email.com",
                "property_type": "casa",
                "bill_value": 450.00,
                "consumption_kwh": 350,
                "current_stage": "QUALIFICATION",
                "qualification_score": 85
            }
        }


class LeadCreate(BaseModel):
    """Schema para criação de lead"""
    phone_number: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    
class LeadUpdate(BaseModel):
    """Schema para atualização de lead"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    document: Optional[str] = None
    property_type: Optional[str] = None
    address: Optional[str] = None
    bill_value: Optional[Decimal] = None
    consumption_kwh: Optional[int] = None
    current_stage: Optional[str] = None
    qualification_score: Optional[int] = None
    interested: Optional[bool] = None
    qualification_status: Optional[str] = None
    is_decision_maker: Optional[bool] = None
    has_solar_system: Optional[bool] = None
    wants_new_solar_system: Optional[bool] = None
    has_active_contract: Optional[bool] = None
    contract_end_date: Optional[datetime] = None
    solution_interest: Optional[str] = None
    notes: Optional[str] = None
    kommo_lead_id: Optional[str] = None
    google_event_id: Optional[str] = None
    meeting_scheduled_at: Optional[datetime] = None
    meeting_type: Optional[str] = None
    meeting_status: Optional[str] = None