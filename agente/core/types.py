"""
Definições de tipos e interfaces para o sistema SDR Agent
"""

from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID


# ===========================
# ENUMS
# ===========================

class MessageRole(str, Enum):
    """Papéis possíveis nas mensagens"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MediaType(str, Enum):
    """Tipos de mídia suportados"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    STICKER = "sticker"


class LeadStage(str, Enum):
    """Estágios do lead no pipeline"""
    INITIAL_CONTACT = "INITIAL_CONTACT"
    IDENTIFYING = "IDENTIFYING"
    QUALIFYING = "QUALIFYING"
    QUALIFIED = "QUALIFIED"
    SCHEDULING = "SCHEDULING"
    SCHEDULED = "SCHEDULED"
    NOT_INTERESTED = "NOT_INTERESTED"
    LOST = "LOST"


class FollowUpType(str, Enum):
    """Tipos de follow-up"""
    REMINDER = "reminder"
    CHECK_IN = "check_in"
    REENGAGEMENT = "reengagement"
    NURTURE = "nurture"
    HOT_LEAD_RESCUE = "hot_lead_rescue"


class FollowUpStatus(str, Enum):
    """Status do follow-up"""
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UrgencyLevel(str, Enum):
    """Nível de urgência do lead"""
    HIGH = "alta"
    MEDIUM = "media"
    LOW = "baixa"


class PropertyType(str, Enum):
    """Tipo de propriedade"""
    HOUSE = "casa"
    APARTMENT = "apartamento"
    COMMERCIAL = "comercial"
    RURAL = "rural"


# ===========================
# MODELOS BASE
# ===========================

class BaseMessage(BaseModel):
    """Modelo base para mensagens"""
    content: str
    role: MessageRole
    timestamp: datetime = Field(default_factory=datetime.now)
    media_type: MediaType = MediaType.TEXT
    media_url: Optional[str] = None
    media_data: Optional[Dict[str, Any]] = None
    whatsapp_message_id: Optional[str] = None


class WhatsAppMessage(BaseModel):
    """Mensagem recebida do WhatsApp via Evolution API"""
    instance_id: str  # Ajustado para corresponder ao código do webhook
    phone: str
    name: Optional[str] = None  # pushName da Evolution API
    message: str
    message_id: str
    timestamp: Union[str, datetime]  # Evolution API envia como string ou int
    from_me: bool = False
    media_type: Optional[str] = None  # Pode ser string ou MediaType
    media_url: Optional[str] = None
    media_caption: Optional[str] = None
    quoted_message: Optional[Dict[str, Any]] = None


class Lead(BaseModel):
    """Modelo de Lead"""
    id: Optional[UUID] = None
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    document: Optional[str] = None  # CPF/CNPJ
    property_type: Optional[PropertyType] = None
    address: Optional[str] = None
    bill_value: Optional[float] = None
    consumption_kwh: Optional[int] = None
    current_stage: LeadStage = LeadStage.INITIAL_CONTACT
    qualification_score: int = 0
    interested: bool = True
    kommo_lead_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Backward compatibility fields
    phone: Optional[str] = None  # Alias for phone_number
    stage: Optional[str] = None  # Alias for current_stage
    status: Optional[str] = None
    score: Optional[int] = None  # Alias for qualification_score
    metadata: Optional[Dict[str, Any]] = None


class Conversation(BaseModel):
    """Modelo de Conversa"""
    id: Optional[UUID] = None
    lead_id: UUID
    session_id: str
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    total_messages: int = 0
    current_stage: Optional[str] = None
    sentiment: Optional[Literal["positivo", "neutro", "negativo"]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    phone: Optional[str] = None  # For backward compatibility
    metadata: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    """Modelo de Mensagem"""
    id: Optional[UUID] = None
    conversation_id: UUID
    whatsapp_message_id: Optional[str] = None
    role: MessageRole
    content: str
    media_type: Optional[MediaType] = None
    media_url: Optional[str] = None
    media_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Backward compatibility fields
    timestamp: Optional[datetime] = None  # Alias for created_at
    direction: Optional[str] = None  # "incoming" or "outgoing"


class LeadQualification(BaseModel):
    """Modelo de Qualificação do Lead"""
    id: Optional[UUID] = None
    lead_id: UUID
    has_own_property: Optional[bool] = None
    decision_maker: Optional[bool] = None
    urgency_level: Optional[UrgencyLevel] = None
    objections: List[str] = Field(default_factory=list)
    solutions_presented: List[str] = Field(default_factory=list)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    qualification_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FollowUp(BaseModel):
    """Modelo de Follow-up"""
    id: Optional[UUID] = None
    lead_id: UUID
    scheduled_at: datetime
    type: FollowUpType
    message: str
    status: FollowUpStatus = FollowUpStatus.PENDING
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    attempt_number: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AgentSession(BaseModel):
    """Modelo de Sessão do Agente"""
    id: Optional[UUID] = None
    session_id: str
    phone_number: str
    state: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_interaction: datetime = Field(default_factory=datetime.now)


# ===========================
# TIPOS DE RESPOSTA
# ===========================

class CalendarSlot(BaseModel):
    """Slot disponível no calendário"""
    start: datetime
    end: datetime
    duration_minutes: int = 60


class CalendarEvent(BaseModel):
    """Evento do calendário"""
    id: str
    title: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    attendees: List[str] = Field(default_factory=list)
    location: str = "Online via Google Meet"
    meet_link: Optional[str] = None
    status: str = "confirmed"


class KommoLead(BaseModel):
    """Lead no Kommo CRM"""
    id: int
    name: str
    price: int = 0
    status_id: int
    pipeline_id: int
    created_at: int
    updated_at: int
    custom_fields_values: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[Dict[str, Any]]] = None


class AnalysisResult(BaseModel):
    """Resultado de análise de mídia"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    error: Optional[str] = None
    confidence: float = 0.0


# ===========================
# TIPOS PARA TOOLS
# ===========================

class MessageChunk(BaseModel):
    """Chunk de mensagem para envio"""
    text: str
    delay_ms: int
    words: int
    chars: int


class BufferedMessages(BaseModel):
    """Mensagens consolidadas do buffer"""
    consolidated_content: str
    message_count: int
    detected_intents: List[str] = Field(default_factory=list)
    requires_immediate_response: bool = False
    time_span_seconds: float = 0.0
    media_messages: List[Dict[str, Any]] = Field(default_factory=list)


# ===========================
# TIPOS DE REQUISIÇÃO/RESPOSTA
# ===========================

class WebhookPayload(BaseModel):
    """Payload recebido do webhook Evolution API"""
    event: str
    instance: Dict[str, Any]
    data: Dict[str, Any]
    destination: Optional[str] = None
    date_time: Optional[str] = None
    sender: Optional[str] = None
    server_url: Optional[str] = None
    api_key: Optional[str] = None


class AgentResponse(BaseModel):
    """Resposta do agente"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    chunks: Optional[List[MessageChunk]] = None
    follow_up_scheduled: bool = False