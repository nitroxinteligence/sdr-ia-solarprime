"""
Kommo CRM Models
================
Modelos de dados para integração com Kommo CRM
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    """Status do lead no pipeline"""
    NEW = "new"
    IN_QUALIFICATION = "in_qualification"
    QUALIFIED = "qualified"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_CONFIRMED = "meeting_confirmed"
    IN_NEGOTIATION = "in_negotiation"
    PROPOSAL_SENT = "proposal_sent"
    WON = "won"
    LOST = "lost"


class SolutionType(str, Enum):
    """Tipo de solução solar"""
    OWN_PLANT = "usina_propria"
    PARTNER_PLANT = "usina_parceira"
    DISCOUNT_HIGH = "desconto_alto"
    DISCOUNT_LOW = "desconto_baixo"
    INVESTMENT = "investimento"


class TaskType(str, Enum):
    """Tipo de tarefa no Kommo"""
    CALL = "call"
    MEET = "meet"
    EMAIL = "email"


class NoteType(str, Enum):
    """Tipo de nota no Kommo"""
    COMMON = "common"
    CALL_IN = "call_in"
    CALL_OUT = "call_out"
    SMS_IN = "sms_in"
    SMS_OUT = "sms_out"


class KommoLead(BaseModel):
    """Modelo de Lead do Kommo"""
    name: str = Field(..., description="Nome do lead")
    phone: str = Field(..., description="Telefone principal")
    whatsapp: str = Field(..., description="WhatsApp do lead")
    email: Optional[str] = Field(None, description="Email do lead")
    energy_bill_value: Optional[float] = Field(None, description="Valor da conta de luz")
    solution_type: Optional[SolutionType] = Field(None, description="Tipo de solução identificada")
    current_discount: Optional[str] = Field(None, description="Desconto atual do concorrente")
    competitor: Optional[str] = Field(None, description="Nome do concorrente")
    qualification_score: int = Field(0, ge=0, le=100, description="Score de qualificação")
    ai_notes: str = Field("", description="Notas da IA sobre o lead")
    tags: List[str] = Field(default_factory=list, description="Tags do lead")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Campos customizados adicionais")
    responsible_user_id: Optional[int] = Field(None, description="ID do usuário responsável")
    pipeline_id: Optional[int] = Field(None, description="ID do pipeline")
    status_id: Optional[int] = Field(None, description="ID do estágio no pipeline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "João Silva",
                "phone": "+5511999999999",
                "whatsapp": "+5511999999999",
                "email": "joao@email.com",
                "energy_bill_value": 450.00,
                "solution_type": "usina_propria",
                "qualification_score": 85,
                "ai_notes": "Cliente interessado em economia, mora em casa própria",
                "tags": ["WhatsApp Lead", "Lead Quente"]
            }
        }


class KommoContact(BaseModel):
    """Modelo de Contato do Kommo"""
    id: Optional[int] = Field(None, description="ID do contato")
    name: str = Field(..., description="Nome do contato")
    phone: str = Field(..., description="Telefone")
    whatsapp: str = Field(..., description="WhatsApp")
    email: Optional[str] = Field(None, description="Email")
    lead_ids: List[int] = Field(default_factory=list, description="IDs dos leads associados")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")


class KommoTask(BaseModel):
    """Modelo de Tarefa do Kommo"""
    text: str = Field(..., description="Descrição da tarefa")
    task_type: TaskType = Field(TaskType.CALL, description="Tipo da tarefa")
    complete_till: datetime = Field(..., description="Prazo para conclusão")
    responsible_user_id: Optional[int] = Field(None, description="ID do responsável")
    entity_type: str = Field("leads", description="Tipo de entidade")
    entity_id: int = Field(..., description="ID da entidade")
    is_completed: bool = Field(False, description="Se está concluída")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Ligar para follow-up - WhatsApp sem resposta",
                "task_type": "call",
                "complete_till": "2024-01-20T10:00:00",
                "entity_type": "leads",
                "entity_id": 12345
            }
        }


class KommoNote(BaseModel):
    """Modelo de Nota do Kommo"""
    entity_type: str = Field("leads", description="Tipo de entidade")
    entity_id: int = Field(..., description="ID da entidade")
    note_type: NoteType = Field(NoteType.COMMON, description="Tipo da nota")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros adicionais")
    text: str = Field(..., description="Texto da nota")
    created_at: Optional[datetime] = Field(None, description="Data de criação")


class KommoWebhookEvent(BaseModel):
    """Evento de webhook do Kommo"""
    event_type: str = Field(..., description="Tipo do evento")
    account_id: int = Field(..., description="ID da conta")
    entity_type: str = Field(..., description="Tipo de entidade")
    entity_id: int = Field(..., description="ID da entidade")
    data: Dict[str, Any] = Field(..., description="Dados do evento")
    timestamp: datetime = Field(..., description="Timestamp do evento")


class KommoResponse(BaseModel):
    """Resposta padrão da API Kommo"""
    total_items: Optional[int] = Field(None, alias="_total_items", description="Total de itens")
    page: Optional[int] = Field(None, alias="_page", description="Página atual")
    page_count: Optional[int] = Field(None, alias="_page_count", description="Total de páginas")
    links: Optional[Dict[str, str]] = Field(None, alias="_links", description="Links de navegação")
    embedded: Optional[Dict[str, List[Dict]]] = Field(None, alias="_embedded", description="Dados embarcados")


class KommoCustomField(BaseModel):
    """Campo customizado do Kommo"""
    field_id: int = Field(..., description="ID do campo")
    field_name: Optional[str] = Field(None, description="Nome do campo")
    field_code: Optional[str] = Field(None, description="Código do campo")
    field_type: Optional[str] = Field(None, description="Tipo do campo")
    values: List[Dict[str, Any]] = Field(..., description="Valores do campo")


class KommoPipeline(BaseModel):
    """Pipeline do Kommo"""
    id: int = Field(..., description="ID do pipeline")
    name: str = Field(..., description="Nome do pipeline")
    sort: int = Field(100, description="Ordem de exibição")
    is_main: bool = Field(False, description="Se é o pipeline principal")
    is_unsorted_on: bool = Field(True, description="Se tem fase não distribuída")
    is_archive: bool = Field(False, description="Se está arquivado")
    account_id: int = Field(..., description="ID da conta")
    embedded: Optional[Dict[str, List[Dict]]] = Field(None, alias="_embedded", description="Estágios do pipeline")