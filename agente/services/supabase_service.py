"""
Serviço de integração com Supabase
Gerencia todas as operações de banco de dados
"""

import asyncio
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timedelta
from functools import wraps

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from gotrue.errors import AuthApiError
from postgrest.exceptions import APIError
from pydantic import BaseModel

from ..core.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from ..core.logger import get_logger
from ..core.types import (
    Lead, LeadStage, Conversation, Message, MessageRole,
    LeadQualification, FollowUp, FollowUpStatus, FollowUpType,
    AgentSession, MediaType
)


# Modelo Profile (caso não esteja em types.py)
class Profile(BaseModel):
    """Modelo de perfil do WhatsApp"""
    id: Optional[UUID] = None
    phone: str
    whatsapp_name: Optional[str] = None
    whatsapp_push_name: Optional[str] = None
    first_interaction_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None
    total_messages: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


logger = get_logger("supabase_service")


def convert_datetime_to_isostring(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte todos os campos datetime em um dicionário para strings ISO.
    
    Args:
        data: Dicionário com possíveis campos datetime
        
    Returns:
        Dicionário com datetimes convertidos para strings ISO
    """
    converted_data = data.copy()
    
    # Lista de campos que podem conter datetime
    datetime_fields = [
        'created_at', 'updated_at', 'started_at', 'ended_at', 
        'scheduled_at', 'executed_at', 'first_interaction_at', 
        'last_interaction_at', 'deleted_at'
    ]
    
    for field in datetime_fields:
        if field in converted_data and converted_data[field] is not None:
            value = converted_data[field]
            if isinstance(value, datetime):
                converted_data[field] = value.isoformat()
            elif isinstance(value, str):
                # Já é string, manter como está
                pass
    
    return converted_data


# Tipos de follow-up estendidos do banco de dados
EXTENDED_FOLLOW_UP_TYPES = [
    'first_contact',    # Primeiro follow-up após 30 minutos
    'reminder',         # Segundo follow-up após 24 horas
    'reengagement',     # Reengajamento após 48-72 horas
    'final',            # Follow-up final
    'qualification',    # Follow-up de qualificação
    'scheduling',       # Follow-up para agendamento
    'check_in',         # Check-in geral
    'nurture',          # Nutrição de lead
    'hot_lead_rescue'   # Resgate de lead quente (do enum original)
]


def retry_on_error(max_attempts: int = 3, delay: float = 1.0):
    """Decorator para retry em caso de erro"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Tentativa {attempt + 1}/{max_attempts} falhou: {str(e)}. "
                            f"Aguardando {wait_time}s antes de tentar novamente..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Todas as {max_attempts} tentativas falharam: {str(e)}")
            raise last_error
        return wrapper
    return decorator


class SupabaseService:
    """
    Serviço responsável por todas as operações com o banco de dados Supabase.
    
    Implementa operações CRUD para todas as tabelas do sistema com:
    - Retry logic para maior resiliência
    - Logging contextualizado
    - Type hints completos
    - Conversão automática entre modelos Pydantic e dicionários
    """
    
    def __init__(self):
        """Inicializa o cliente Supabase com as credenciais de serviço"""
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar configurados")
        
        # Configurações do cliente
        options = ClientOptions(
            auto_refresh_token=True,
            persist_session=True
        )
        
        # Criar cliente com service key (bypass RLS)
        self.client: Client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_KEY,
            options=options
        )
        
        logger.info("✅ Supabase Service inicializado com sucesso")
    
    # ===========================
    # OPERAÇÕES COM LEADS
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def create_lead(self, lead: Lead) -> Lead:
        """
        Cria um novo lead no banco de dados.
        
        Args:
            lead: Objeto Lead com os dados do novo lead
            
        Returns:
            Lead criado com ID e timestamps preenchidos
            
        Raises:
            APIError: Se houver erro na criação
        """
        try:
            # Converter para dict e remover campos None
            lead_data = lead.model_dump(exclude_none=True, exclude={"id", "created_at", "updated_at"})
            
            # Converter enums para strings
            if "current_stage" in lead_data:
                lead_data["current_stage"] = lead_data["current_stage"].value
            if "property_type" in lead_data:
                lead_data["property_type"] = lead_data["property_type"].value
            
            # Converter datetime para strings ISO
            lead_data = convert_datetime_to_isostring(lead_data)
            
            # Executar insert
            result = await asyncio.to_thread(
                lambda: self.client.table("leads").insert(lead_data).execute()
            )
            
            if result.data and len(result.data) > 0:
                created_lead = Lead(**result.data[0])
                logger.info(f"✅ Lead criado: {created_lead.phone_number} (ID: {created_lead.id})")
                return created_lead
            else:
                raise ValueError("Nenhum dado retornado após criação do lead")
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar lead: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_lead_by_phone(self, phone: str) -> Optional[Lead]:
        """
        Busca um lead pelo número de telefone.
        
        Args:
            phone: Número de telefone do lead
            
        Returns:
            Lead encontrado ou None se não existir
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table("leads")
                .select("*")
                .eq("phone_number", phone)
                .maybe_single()  # Corrigido: maybe_single() em vez de single()
                .execute()
            )
            
            # Verificação robusta para maybe_single() que pode retornar None
            if result and hasattr(result, 'data') and result.data:
                return Lead(**result.data)
            return None
            
        except APIError as e:
            # Tratamento específico para erro PGRST116
            if "PGRST116" in str(e) or "JSON object requested, multiple (or no) rows returned" in str(e):
                logger.info(f"Lead não encontrado para telefone: {phone} (PGRST116)")
                return None
            elif "No rows found" in str(e):
                logger.info(f"Lead não encontrado para telefone: {phone}")
                return None
            logger.error(f"❌ Erro ao buscar lead por telefone: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_or_create_lead(self, phone: str, name: str = None, **kwargs) -> Lead:
        """
        Busca um lead pelo telefone ou cria um novo se não existir usando UPSERT atômico.
        
        Implementa ON CONFLICT DO UPDATE para resolver race conditions quando
        múltiplas requisições tentam criar leads com o mesmo phone_number.
        
        Args:
            phone: Número de telefone do lead
            name: Nome do lead (opcional)
            **kwargs: Outros campos do lead
            
        Returns:
            Lead encontrado ou criado
        """
        try:
            # Primeiro tentar buscar lead existente para otimização
            existing_lead = await self.get_lead_by_phone(phone)
            if existing_lead:
                logger.info(f"Lead existente encontrado: {phone}")
                return existing_lead
            
            # Se não encontrou, usar UPSERT atômico
            from ..core.types import Lead, LeadStage
            
            lead_data = {
                "phone_number": phone,
                "name": name or f"Lead {phone[-4:]}",  # Nome padrão se não fornecido
                "current_stage": LeadStage.INITIAL_CONTACT,
                "qualification_score": 0,
                "interested": True,
                **kwargs  # Campos adicionais fornecidos
            }
            
            # Converter enums para strings
            if "current_stage" in lead_data:
                lead_data["current_stage"] = lead_data["current_stage"].value
            if "property_type" in lead_data and hasattr(lead_data["property_type"], "value"):
                lead_data["property_type"] = lead_data["property_type"].value
            
            # Converter datetime para strings ISO
            lead_data = convert_datetime_to_isostring(lead_data)
            
            # Usar UPSERT atômico com ON CONFLICT DO UPDATE
            result = await asyncio.to_thread(
                lambda: self.client.table("leads")
                .upsert(lead_data, on_conflict="phone_number", ignore_duplicates=False)
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                created_lead = Lead(**result.data[0])
                logger.info(f"✅ Lead criado/atualizado atomicamente: {phone} (ID: {created_lead.id})")
                return created_lead
            else:
                raise ValueError("Nenhum dado retornado após criar/atualizar lead")
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar/criar lead: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def update_lead(self, phone: str, **kwargs) -> Lead:
        """
        Atualiza dados de um lead existente.
        
        Args:
            phone: Número de telefone do lead
            **kwargs: Campos a serem atualizados
            
        Returns:
            Lead atualizado
            
        Raises:
            ValueError: Se o lead não for encontrado
        """
        try:
            # Remover campos que não devem ser atualizados
            update_data = {k: v for k, v in kwargs.items() 
                          if k not in ["id", "created_at", "phone_number"]}
            
            # Converter enums para strings
            if "current_stage" in update_data and hasattr(update_data["current_stage"], "value"):
                update_data["current_stage"] = update_data["current_stage"].value
            if "property_type" in update_data and hasattr(update_data["property_type"], "value"):
                update_data["property_type"] = update_data["property_type"].value
            
            # Adicionar timestamp de atualização
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Converter datetime para strings ISO
            update_data = convert_datetime_to_isostring(update_data)
            
            result = await asyncio.to_thread(
                lambda: self.client.table("leads")
                .update(update_data)
                .eq("phone_number", phone)
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                updated_lead = Lead(**result.data[0])
                logger.info(f"✅ Lead atualizado: {phone}")
                return updated_lead
            else:
                raise ValueError(f"Lead não encontrado: {phone}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar lead: {str(e)}")
            raise
    
    # ===========================
    # OPERAÇÕES COM CONVERSAS
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """
        Cria uma nova conversa no banco de dados usando UPSERT atômico.
        
        Implementa ON CONFLICT DO UPDATE para resolver race conditions quando
        múltiplas requisições tentam criar conversas com o mesmo session_id.
        
        Args:
            conversation: Objeto Conversation com os dados da nova conversa
            
        Returns:
            Conversa criada ou atualizada com ID preenchido
        """
        try:
            # Converter para dict
            conv_data = conversation.model_dump(exclude_none=True, exclude={"id", "created_at", "updated_at"})
            
            # Converter UUID para string se necessário
            if "lead_id" in conv_data and isinstance(conv_data["lead_id"], UUID):
                conv_data["lead_id"] = str(conv_data["lead_id"])
            
            # Converter datetime para strings ISO
            conv_data = convert_datetime_to_isostring(conv_data)
            
            # Implementar UPSERT atômico usando ON CONFLICT DO UPDATE
            # Se session_id já existe, atualizar ao invés de falhar
            result = await asyncio.to_thread(
                lambda: self.client.table("conversations")
                .upsert(conv_data, on_conflict="session_id", ignore_duplicates=False)
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                created_conv = Conversation(**result.data[0])
                logger.info(f"✅ Conversa criada/atualizada: {created_conv.session_id} (ID: {created_conv.id})")
                return created_conv
            else:
                raise ValueError("Nenhum dado retornado após criar/atualizar conversa")
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar/atualizar conversa: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_active_conversation(self, lead_id: UUID) -> Optional[Conversation]:
        """
        Busca a conversa ativa de um lead.
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Conversa ativa ou None se não houver
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table("conversations")
                .select("*")
                .eq("lead_id", str(lead_id))
                .eq("is_active", True)
                .order("started_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                return Conversation(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar conversa ativa: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def end_conversation(self, conversation_id: UUID) -> Conversation:
        """
        Finaliza uma conversa ativa.
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            Conversa atualizada
        """
        try:
            update_data = {
                "is_active": False,
                "ended_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Converter datetime para strings ISO
            update_data = convert_datetime_to_isostring(update_data)
            
            result = await asyncio.to_thread(
                lambda: self.client.table("conversations")
                .update(update_data)
                .eq("id", str(conversation_id))
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                updated_conv = Conversation(**result.data[0])
                logger.info(f"✅ Conversa finalizada: {conversation_id}")
                return updated_conv
            else:
                raise ValueError(f"Conversa não encontrada: {conversation_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar conversa: {str(e)}")
            raise
    
    # ===========================
    # OPERAÇÕES COM MENSAGENS
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def save_message(self, message: Message) -> Message:
        """
        Salva uma mensagem no banco de dados.
        
        Args:
            message: Objeto Message com os dados da mensagem
            
        Returns:
            Mensagem salva com ID preenchido
        """
        try:
            # Converter para dict
            msg_data = message.model_dump(exclude_none=True, exclude={"id"})
            
            # Converter enums e UUIDs
            if "role" in msg_data:
                msg_data["role"] = msg_data["role"].value
            if "media_type" in msg_data and msg_data["media_type"]:
                msg_data["media_type"] = msg_data["media_type"].value
            if "conversation_id" in msg_data and isinstance(msg_data["conversation_id"], UUID):
                msg_data["conversation_id"] = str(msg_data["conversation_id"])
            
            # Converter datetime para strings ISO
            msg_data = convert_datetime_to_isostring(msg_data)
            
            result = await asyncio.to_thread(
                lambda: self.client.table("messages").insert(msg_data).execute()
            )
            
            if result.data and len(result.data) > 0:
                created_msg = Message(**result.data[0])
                logger.debug(f"✅ Mensagem salva: {created_msg.id}")
                return created_msg
            else:
                raise ValueError("Nenhum dado retornado após salvar mensagem")
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar mensagem: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_last_messages(self, phone: str, limit: int = 100) -> List[Message]:
        """
        Busca as últimas mensagens de um número de telefone.
        
        Esta é uma operação especial que busca mensagens através do relacionamento
        lead -> conversation -> messages.
        
        Args:
            phone: Número de telefone do lead
            limit: Número máximo de mensagens a retornar (padrão: 100)
            
        Returns:
            Lista de mensagens ordenadas por created_at (mais recentes primeiro)
        """
        try:
            # Primeiro buscar o lead
            lead = await self.get_lead_by_phone(phone)
            if not lead or not lead.id:
                logger.info(f"Lead não encontrado para buscar mensagens: {phone}")
                return []
            
            # Buscar todas as conversas do lead
            conversations_result = await asyncio.to_thread(
                lambda: self.client.table("conversations")
                .select("id")
                .eq("lead_id", str(lead.id))
                .execute()
            )
            
            if not conversations_result.data:
                logger.info(f"Nenhuma conversa encontrada para o lead: {phone}")
                return []
            
            # Extrair IDs das conversas
            conversation_ids = [conv["id"] for conv in conversations_result.data]
            
            # Buscar mensagens de todas as conversas
            messages_result = await asyncio.to_thread(
                lambda: self.client.table("messages")
                .select("*")
                .in_("conversation_id", conversation_ids)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            if messages_result.data:
                messages = [Message(**msg) for msg in messages_result.data]
                logger.info(f"✅ {len(messages)} mensagens recuperadas para {phone}")
                return messages
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar últimas mensagens: {str(e)}")
            raise
    
    # ===========================
    # OPERAÇÕES COM QUALIFICAÇÃO
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def save_qualification(self, qualification: LeadQualification) -> LeadQualification:
        """
        Salva ou atualiza a qualificação de um lead.
        
        Args:
            qualification: Objeto LeadQualification com os dados
            
        Returns:
            Qualificação salva/atualizada
        """
        try:
            # Converter para dict
            qual_data = qualification.model_dump(exclude_none=True, exclude={"id", "created_at", "updated_at"})
            
            # Converter enums e UUIDs
            if "urgency_level" in qual_data and hasattr(qual_data["urgency_level"], "value"):
                qual_data["urgency_level"] = qual_data["urgency_level"].value
            if "lead_id" in qual_data and isinstance(qual_data["lead_id"], UUID):
                qual_data["lead_id"] = str(qual_data["lead_id"])
            
            # Converter datetime para strings ISO
            qual_data = convert_datetime_to_isostring(qual_data)
            
            # Verificar se já existe qualificação para este lead
            existing = await asyncio.to_thread(
                lambda: self.client.table("lead_qualifications")
                .select("id")
                .eq("lead_id", qual_data["lead_id"])
                .execute()
            )
            
            if existing.data and len(existing.data) > 0:
                # Atualizar existente
                qual_data["updated_at"] = datetime.now().isoformat()
                result = await asyncio.to_thread(
                    lambda: self.client.table("lead_qualifications")
                    .update(qual_data)
                    .eq("lead_id", qual_data["lead_id"])
                    .execute()
                )
            else:
                # Criar nova
                result = await asyncio.to_thread(
                    lambda: self.client.table("lead_qualifications")
                    .insert(qual_data)
                    .execute()
                )
            
            if result.data and len(result.data) > 0:
                saved_qual = LeadQualification(**result.data[0])
                logger.info(f"✅ Qualificação salva para lead: {qual_data['lead_id']}")
                return saved_qual
            else:
                raise ValueError("Nenhum dado retornado após salvar qualificação")
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar qualificação: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_qualification(self, lead_id: UUID) -> Optional[LeadQualification]:
        """
        Busca a qualificação de um lead.
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Qualificação do lead ou None se não existir
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table("lead_qualifications")
                .select("*")
                .eq("lead_id", str(lead_id))
                .single()
                .execute()
            )
            
            if result.data:
                return LeadQualification(**result.data)
            return None
            
        except APIError as e:
            if "No rows found" in str(e):
                logger.info(f"Qualificação não encontrada para lead: {lead_id}")
                return None
            logger.error(f"❌ Erro ao buscar qualificação: {str(e)}")
            raise
    
    # ===========================
    # OPERAÇÕES COM FOLLOW-UPS
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def create_follow_up(self, follow_up: FollowUp) -> FollowUp:
        """
        Cria um novo follow-up.
        
        Args:
            follow_up: Objeto FollowUp com os dados
            
        Returns:
            Follow-up criado com ID preenchido
        """
        try:
            # Converter para dict
            fu_data = follow_up.model_dump(exclude_none=True, exclude={"id", "created_at", "updated_at"})
            
            # Extrair attempt_number para metadata
            attempt_number = fu_data.pop("attempt_number", 1)
            
            # Converter enums e UUIDs
            if "type" in fu_data:
                # Converter enum para string - o banco aceita tipos estendidos além do enum
                if hasattr(fu_data["type"], "value"):
                    fu_data["type"] = fu_data["type"].value
                # Validar se o tipo é aceito pelo banco
                elif fu_data["type"] not in EXTENDED_FOLLOW_UP_TYPES:
                    logger.warning(f"Tipo de follow-up não reconhecido: {fu_data['type']}")
            if "status" in fu_data:
                fu_data["status"] = fu_data["status"].value
            if "lead_id" in fu_data and isinstance(fu_data["lead_id"], UUID):
                fu_data["lead_id"] = str(fu_data["lead_id"])
            
            # Adicionar attempt_number ao metadata
            if "metadata" not in fu_data:
                fu_data["metadata"] = {}
            fu_data["metadata"]["attempt_number"] = attempt_number
            
            # Converter datetime para strings ISO
            fu_data = convert_datetime_to_isostring(fu_data)
            
            result = await asyncio.to_thread(
                lambda: self.client.table("follow_ups").insert(fu_data).execute()
            )
            
            if result.data and len(result.data) > 0:
                # Reconstruir o objeto com attempt_number
                created_data = result.data[0]
                if "metadata" in created_data and "attempt_number" in created_data["metadata"]:
                    created_data["attempt_number"] = created_data["metadata"]["attempt_number"]
                created_fu = FollowUp(**created_data)
                logger.info(f"✅ Follow-up criado: {created_fu.id} para {created_fu.scheduled_at}")
                return created_fu
            else:
                raise ValueError("Nenhum dado retornado após criar follow-up")
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar follow-up: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_pending_follow_ups(self, limit: int = 100) -> List[FollowUp]:
        """
        Busca follow-ups pendentes que já deveriam ter sido executados.
        
        Args:
            limit: Número máximo de follow-ups a retornar
            
        Returns:
            Lista de follow-ups pendentes
        """
        try:
            current_time = datetime.now().isoformat()
            
            result = await asyncio.to_thread(
                lambda: self.client.table("follow_ups")
                .select("*")
                .eq("status", FollowUpStatus.PENDING.value)
                .lte("scheduled_at", current_time)
                .order("scheduled_at", desc=False)
                .limit(limit)
                .execute()
            )
            
            if result.data:
                follow_ups = []
                for fu_data in result.data:
                    # Extrair attempt_number do metadata se existir
                    if "metadata" in fu_data and fu_data["metadata"] and "attempt_number" in fu_data["metadata"]:
                        fu_data["attempt_number"] = fu_data["metadata"]["attempt_number"]
                    follow_ups.append(FollowUp(**fu_data))
                logger.info(f"✅ {len(follow_ups)} follow-ups pendentes encontrados")
                return follow_ups
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar follow-ups pendentes: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def update_follow_up_status(
        self, 
        follow_up_id: UUID, 
        status: FollowUpStatus,
        result: Optional[Dict[str, Any]] = None
    ) -> FollowUp:
        """
        Atualiza o status de um follow-up.
        
        Args:
            follow_up_id: ID do follow-up
            status: Novo status
            result: Resultado da execução (opcional)
            
        Returns:
            Follow-up atualizado
        """
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.now().isoformat()
            }
            
            if status == FollowUpStatus.EXECUTED:
                update_data["executed_at"] = datetime.now().isoformat()
            
            if result:
                update_data["result"] = result
            
            result = await asyncio.to_thread(
                lambda: self.client.table("follow_ups")
                .update(update_data)
                .eq("id", str(follow_up_id))
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                updated_fu = FollowUp(**result.data[0])
                logger.info(f"✅ Follow-up atualizado: {follow_up_id} -> {status.value}")
                return updated_fu
            else:
                raise ValueError(f"Follow-up não encontrado: {follow_up_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar follow-up: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_lead_follow_ups(self, lead_id: UUID, status: Optional[FollowUpStatus] = None) -> List[FollowUp]:
        """
        Busca follow-ups de um lead específico.
        
        Args:
            lead_id: ID do lead
            status: Status específico para filtrar (opcional)
            
        Returns:
            Lista de follow-ups do lead
        """
        try:
            query = self.client.table("follow_ups").select("*").eq("lead_id", str(lead_id))
            
            if status:
                query = query.eq("status", status.value)
            
            result = await asyncio.to_thread(
                lambda: query.order("scheduled_at", desc=True).execute()
            )
            
            if result.data:
                follow_ups = []
                for fu_data in result.data:
                    # Extrair attempt_number do metadata se existir
                    if "metadata" in fu_data and fu_data["metadata"] and "attempt_number" in fu_data["metadata"]:
                        fu_data["attempt_number"] = fu_data["metadata"]["attempt_number"]
                    follow_ups.append(FollowUp(**fu_data))
                return follow_ups
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar follow-ups do lead: {str(e)}")
            raise
    
    # ===========================
    # OPERAÇÕES COM SESSÕES
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def save_agent_session(self, session: AgentSession) -> AgentSession:
        """
        Salva ou atualiza uma sessão do agente.
        
        Args:
            session: Objeto AgentSession com os dados
            
        Returns:
            Sessão salva/atualizada
        """
        try:
            # Converter para dict
            session_data = session.model_dump(exclude_none=True, exclude={"id", "created_at", "updated_at"})
            
            # Converter datetime para strings ISO
            session_data = convert_datetime_to_isostring(session_data)
            
            # Verificar se já existe sessão
            existing = await asyncio.to_thread(
                lambda: self.client.table("agent_sessions")
                .select("id")
                .eq("session_id", session_data["session_id"])
                .execute()
            )
            
            if existing.data and len(existing.data) > 0:
                # Atualizar existente
                session_data["updated_at"] = datetime.now().isoformat()
                result = await asyncio.to_thread(
                    lambda: self.client.table("agent_sessions")
                    .update(session_data)
                    .eq("session_id", session_data["session_id"])
                    .execute()
                )
            else:
                # Criar nova
                result = await asyncio.to_thread(
                    lambda: self.client.table("agent_sessions")
                    .insert(session_data)
                    .execute()
                )
            
            if result.data and len(result.data) > 0:
                saved_session = AgentSession(**result.data[0])
                logger.debug(f"✅ Sessão salva: {saved_session.session_id}")
                return saved_session
            else:
                raise ValueError("Nenhum dado retornado após salvar sessão")
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar sessão: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_agent_session(self, session_id: str) -> Optional[AgentSession]:
        """
        Busca uma sessão do agente.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Sessão encontrada ou None
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table("agent_sessions")
                .select("*")
                .eq("session_id", session_id)
                .single()
                .execute()
            )
            
            if result.data:
                return AgentSession(**result.data)
            return None
            
        except APIError as e:
            if "No rows found" in str(e):
                logger.info(f"Sessão não encontrada: {session_id}")
                return None
            logger.error(f"❌ Erro ao buscar sessão: {str(e)}")
            raise
    
    # ===========================
    # OPERAÇÕES COM PROFILES
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def create_or_update_profile(self, profile: Profile) -> Profile:
        """
        Cria ou atualiza um perfil do WhatsApp.
        
        Args:
            profile: Objeto Profile com os dados
            
        Returns:
            Profile criado ou atualizado
        """
        try:
            # Converter para dict
            profile_data = profile.model_dump(exclude_none=True, exclude={"id", "created_at", "updated_at"})
            
            # Converter datetime para strings ISO
            profile_data = convert_datetime_to_isostring(profile_data)
            
            # Verificar se já existe perfil para este telefone
            existing = await asyncio.to_thread(
                lambda: self.client.table("profiles")
                .select("id")
                .eq("phone", profile_data["phone"])
                .execute()
            )
            
            if existing.data and len(existing.data) > 0:
                # Atualizar existente
                profile_data["updated_at"] = datetime.now().isoformat()
                profile_data["last_interaction_at"] = datetime.now().isoformat()
                
                # Incrementar total_messages se fornecido
                if "total_messages" in profile_data:
                    # Buscar valor atual
                    current = await asyncio.to_thread(
                        lambda: self.client.table("profiles")
                        .select("total_messages")
                        .eq("phone", profile_data["phone"])
                        .single()
                        .execute()
                    )
                    if current.data:
                        profile_data["total_messages"] = current.data.get("total_messages", 0) + 1
                
                result = await asyncio.to_thread(
                    lambda: self.client.table("profiles")
                    .update(profile_data)
                    .eq("phone", profile_data["phone"])
                    .execute()
                )
            else:
                # Criar novo
                profile_data["first_interaction_at"] = datetime.now().isoformat()
                profile_data["last_interaction_at"] = datetime.now().isoformat()
                result = await asyncio.to_thread(
                    lambda: self.client.table("profiles")
                    .insert(profile_data)
                    .execute()
                )
            
            if result.data and len(result.data) > 0:
                saved_profile = Profile(**result.data[0])
                logger.info(f"✅ Profile salvo: {saved_profile.phone}")
                return saved_profile
            else:
                raise ValueError("Nenhum dado retornado após salvar profile")
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar profile: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_profile_by_phone(self, phone: str) -> Optional[Profile]:
        """
        Busca um perfil pelo número de telefone.
        
        Args:
            phone: Número de telefone
            
        Returns:
            Profile encontrado ou None
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table("profiles")
                .select("*")
                .eq("phone", phone)
                .single()
                .execute()
            )
            
            if result.data:
                return Profile(**result.data)
            return None
            
        except APIError as e:
            if "No rows found" in str(e):
                logger.info(f"Profile não encontrado: {phone}")
                return None
            logger.error(f"❌ Erro ao buscar profile: {str(e)}")
            raise
    
    # ===========================
    # OPERAÇÕES AUXILIARES
    # ===========================
    
    @retry_on_error(max_attempts=3)
    async def get_leads_by_stage(self, stage: LeadStage, limit: int = 100) -> List[Lead]:
        """
        Busca leads em um estágio específico.
        
        Args:
            stage: Estágio do lead
            limit: Número máximo de leads a retornar
            
        Returns:
            Lista de leads no estágio especificado
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table("leads")
                .select("*")
                .eq("current_stage", stage.value)
                .eq("interested", True)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            if result.data:
                leads = [Lead(**lead) for lead in result.data]
                logger.info(f"✅ {len(leads)} leads encontrados no estágio {stage.value}")
                return leads
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar leads por estágio: {str(e)}")
            raise
    
    @retry_on_error(max_attempts=3)
    async def get_recent_leads(self, hours: int = 24, limit: int = 100) -> List[Lead]:
        """
        Busca leads criados nas últimas X horas.
        
        Args:
            hours: Número de horas no passado
            limit: Número máximo de leads a retornar
            
        Returns:
            Lista de leads recentes
        """
        try:
            since_date = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            result = await asyncio.to_thread(
                lambda: self.client.table("leads")
                .select("*")
                .gte("created_at", since_date)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            if result.data:
                leads = [Lead(**lead) for lead in result.data]
                logger.info(f"✅ {len(leads)} leads criados nas últimas {hours} horas")
                return leads
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar leads recentes: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """
        Verifica se a conexão com o Supabase está funcionando.
        
        Returns:
            True se a conexão está OK, False caso contrário
        """
        try:
            # Fazer uma query simples para testar a conexão
            await asyncio.to_thread(
                lambda: self.client.table("leads").select("id").limit(1).execute()
            )
            logger.info("✅ Supabase health check: OK")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase health check falhou: {str(e)}")
            return False


# Instância singleton do serviço
_supabase_service: Optional[SupabaseService] = None


def get_supabase_service() -> SupabaseService:
    """
    Retorna a instância singleton do SupabaseService.
    
    Returns:
        Instância do SupabaseService
    """
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service