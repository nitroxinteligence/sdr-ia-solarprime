"""
Repository para gerenciamento de conversas
Implementa a lógica de negócio para conversas do sistema
"""

from typing import List, Optional, Dict, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from loguru import logger

from ..core.types import Conversation, Message, MessageRole, MediaType
from ..core.logger import setup_module_logger
from ..services import get_supabase_service
from ..utils.formatters import format_datetime, format_relative_time

logger = setup_module_logger(__name__)

CONVERSATION_TIMEOUT_MINUTES = 30

# Singleton instance
_conversation_repository_instance = None


class ConversationRepository:
    """
    Repository responsável pela gestão de conversas do sistema.
    
    Implementa:
    - Criação e finalização de conversas
    - Controle de timeout (30 minutos)
    - Histórico formatado para contexto do agente
    - Atualização de estágios
    - Metadata de conversas (duração, mensagens, sentiment)
    """
    
    def __init__(self):
        """Inicializa o repository com o serviço Supabase"""
        self.supabase = get_supabase_service()
        self._conversation_cache: Dict[UUID, Conversation] = {}
        logger.info("ConversationRepository inicializado")
    
    async def start_conversation(self, lead_id: UUID, session_id: str) -> Conversation:
        """
        Cria uma nova conversa para um lead.
        
        Args:
            lead_id: ID do lead
            session_id: ID da sessão Evolution API
            
        Returns:
            Conversa criada
            
        Note:
            Finaliza automaticamente conversas anteriores ativas do mesmo lead
        """
        try:
            # Verificar se há conversa ativa e finalizar
            active_conversation = await self.get_active_conversation(lead_id)
            if active_conversation:
                logger.info(f"Finalizando conversa ativa anterior: {active_conversation.id}")
                await self.end_conversation(
                    active_conversation.id,
                    summary="Conversa finalizada automaticamente ao iniciar nova conversa"
                )
            
            # Criar nova conversa
            conversation = Conversation(
                lead_id=lead_id,
                session_id=session_id,
                started_at=datetime.now(),
                is_active=True,
                total_messages=0,
                sentiment="neutro"
            )
            
            created_conversation = await self.supabase.create_conversation(conversation)
            
            # Adicionar ao cache
            if created_conversation.id:
                self._conversation_cache[created_conversation.id] = created_conversation
            
            logger.info(f"✅ Nova conversa iniciada: {created_conversation.id} para lead {lead_id}")
            return created_conversation
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar conversa: {str(e)}")
            raise
    
    async def get_or_create_conversation(self, phone: str, session_id: str) -> Tuple[Conversation, bool]:
        """
        Busca conversa ativa ou cria uma nova.
        
        Args:
            phone: Número de telefone do lead
            session_id: ID da sessão Evolution API
            
        Returns:
            Tupla (conversation, is_new) onde is_new indica se foi criada
            
        Note:
            Verifica timeout antes de retornar conversa existente
        """
        try:
            # Buscar ou criar lead automaticamente
            try:
                lead = await self.supabase.get_or_create_lead(
                    phone=phone,
                    name=f"Lead {phone[-4:]}"  # Nome padrão baseado nos últimos 4 dígitos
                )
                logger.info(f"Lead obtido/criado para: {phone} (ID: {lead.id})")
            except Exception as lead_error:
                logger.error(f"Erro ao obter/criar lead para {phone}: {lead_error}")
                # Fallback: tentar apenas buscar
                lead = await self.supabase.get_lead_by_phone(phone)
                if not lead or not lead.id:
                    logger.error(f"Lead não encontrado e não foi possível criar para: {phone}")
                    raise ValueError(f"Lead não encontrado para telefone: {phone}")
            
            # Buscar conversa ativa
            active_conversation = await self.get_active_conversation(lead.id)
            
            if active_conversation:
                # Verificar timeout
                is_timed_out = await self.check_conversation_timeout(active_conversation.id)
                if is_timed_out:
                    logger.info(f"Conversa {active_conversation.id} expirou por timeout")
                    await self.end_conversation(
                        active_conversation.id,
                        summary="Conversa finalizada por timeout (30 minutos de inatividade)"
                    )
                    # Criar nova conversa
                    new_conversation = await self.start_conversation(lead.id, session_id)
                    return (new_conversation, True)
                else:
                    # Atualizar session_id se mudou
                    if active_conversation.session_id != session_id:
                        logger.info(f"Atualizando session_id da conversa {active_conversation.id}")
                        # Aqui você poderia implementar um update do session_id se necessário
                    return (active_conversation, False)
            else:
                # Criar nova conversa
                new_conversation = await self.start_conversation(lead.id, session_id)
                return (new_conversation, True)
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar/criar conversa: {str(e)}")
            raise
    
    async def get_active_conversation(self, lead_id: UUID) -> Optional[Conversation]:
        """
        Busca a conversa ativa de um lead.
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Conversa ativa ou None
            
        Note:
            Não verifica timeout, apenas retorna se is_active=True
        """
        try:
            # Verificar cache primeiro
            for conv in self._conversation_cache.values():
                if conv.lead_id == lead_id and conv.is_active:
                    return conv
            
            # Buscar no banco
            conversation = await self.supabase.get_active_conversation(lead_id)
            
            # Adicionar ao cache se encontrado
            if conversation and conversation.id:
                self._conversation_cache[conversation.id] = conversation
            
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar conversa ativa: {str(e)}")
            raise
    
    async def end_conversation(self, conversation_id: UUID, summary: Optional[str] = None) -> Conversation:
        """
        Finaliza uma conversa ativa.
        
        Args:
            conversation_id: ID da conversa
            summary: Resumo opcional da conversa
            
        Returns:
            Conversa atualizada
        """
        try:
            # Finalizar no banco
            updated_conversation = await self.supabase.end_conversation(conversation_id)
            
            # Se tiver resumo, poderíamos salvar em um campo metadata
            if summary:
                logger.info(f"Conversa finalizada com resumo: {summary}")
            
            # Remover do cache
            if conversation_id in self._conversation_cache:
                del self._conversation_cache[conversation_id]
            
            # Calcular duração
            if updated_conversation.started_at and updated_conversation.ended_at:
                duration = updated_conversation.ended_at - updated_conversation.started_at
                logger.info(
                    f"✅ Conversa {conversation_id} finalizada. "
                    f"Duração: {duration}, Mensagens: {updated_conversation.total_messages}"
                )
            
            return updated_conversation
            
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar conversa: {str(e)}")
            raise
    
    async def get_conversation_history(self, phone: str, limit: int = 100) -> List[Dict]:
        """
        Retorna o histórico de conversas formatado para contexto do agente.
        
        Args:
            phone: Número de telefone do lead
            limit: Número máximo de mensagens
            
        Returns:
            Lista de mensagens formatadas para o agente:
            [
                {
                    "role": "user",
                    "content": "mensagem",
                    "timestamp": "10:30",
                    "media": {"type": "image", "url": "..."} # se houver
                },
                {
                    "role": "assistant",
                    "content": "resposta",
                    "timestamp": "10:31"
                }
            ]
        """
        try:
            # Buscar mensagens do lead
            messages = await self.supabase.get_last_messages(phone, limit=limit)
            
            if not messages:
                logger.info(f"Nenhuma mensagem encontrada para {phone}")
                return []
            
            # Formatar mensagens para o contexto
            formatted_history = []
            
            # Inverter ordem para cronológica (mais antigas primeiro)
            messages.reverse()
            
            for msg in messages:
                formatted_msg = {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": format_datetime(msg.created_at, format="time")
                }
                
                # Adicionar informações de mídia se houver
                if msg.media_type and msg.media_type != MediaType.TEXT:
                    formatted_msg["media"] = {
                        "type": msg.media_type.value
                    }
                    if msg.media_url:
                        formatted_msg["media"]["url"] = msg.media_url
                    if msg.media_data:
                        formatted_msg["media"]["data"] = msg.media_data
                
                formatted_history.append(formatted_msg)
            
            logger.info(f"✅ Histórico formatado: {len(formatted_history)} mensagens para {phone}")
            return formatted_history
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar histórico de conversas: {str(e)}")
            raise
    
    async def update_conversation_stage(self, conversation_id: UUID, stage: str) -> Conversation:
        """
        Atualiza o estágio atual da conversa.
        
        Args:
            conversation_id: ID da conversa
            stage: Novo estágio
            
        Returns:
            Conversa atualizada
        """
        try:
            # Por enquanto, vamos usar o método genérico do Supabase
            # Em uma implementação completa, poderíamos ter um método específico
            result = await self.supabase.client.table("conversations") \
                .update({"current_stage": stage, "updated_at": datetime.now().isoformat()}) \
                .eq("id", str(conversation_id)) \
                .execute()
            
            if result.data and len(result.data) > 0:
                updated_conversation = Conversation(**result.data[0])
                
                # Atualizar cache
                if conversation_id in self._conversation_cache:
                    self._conversation_cache[conversation_id] = updated_conversation
                
                logger.info(f"✅ Estágio da conversa {conversation_id} atualizado para: {stage}")
                return updated_conversation
            else:
                raise ValueError(f"Conversa não encontrada: {conversation_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar estágio da conversa: {str(e)}")
            raise
    
    async def get_active_conversations(self, limit: int = 50) -> List[Conversation]:
        """
        Lista todas as conversas ativas.
        
        Args:
            limit: Número máximo de conversas
            
        Returns:
            Lista de conversas ativas ordenadas por última atualização
        """
        try:
            result = await self.supabase.client.table("conversations") \
                .select("*") \
                .eq("is_active", True) \
                .order("updated_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if result.data:
                conversations = [Conversation(**conv) for conv in result.data]
                logger.info(f"✅ {len(conversations)} conversas ativas encontradas")
                return conversations
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar conversas ativas: {str(e)}")
            raise
    
    async def check_conversation_timeout(self, conversation_id: UUID) -> bool:
        """
        Verifica se uma conversa expirou por timeout (30 minutos).
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            True se expirou, False caso contrário
        """
        try:
            # Buscar última mensagem da conversa
            result = await self.supabase.client.table("messages") \
                .select("created_at") \
                .eq("conversation_id", str(conversation_id)) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            
            if not result.data:
                # Se não há mensagens, verificar tempo de criação da conversa
                conv_result = await self.supabase.client.table("conversations") \
                    .select("started_at") \
                    .eq("id", str(conversation_id)) \
                    .single() \
                    .execute()
                
                if conv_result.data:
                    started_at = datetime.fromisoformat(conv_result.data["started_at"].replace("Z", "+00:00"))
                    time_since_start = datetime.now() - started_at
                    return time_since_start > timedelta(minutes=CONVERSATION_TIMEOUT_MINUTES)
                return True
            
            # Verificar tempo desde última mensagem
            last_message_time = datetime.fromisoformat(result.data[0]["created_at"].replace("Z", "+00:00"))
            time_since_last_message = datetime.now() - last_message_time
            
            is_timed_out = time_since_last_message > timedelta(minutes=CONVERSATION_TIMEOUT_MINUTES)
            
            if is_timed_out:
                logger.info(
                    f"Conversa {conversation_id} expirou. "
                    f"Última mensagem: {format_relative_time(last_message_time)}"
                )
            
            return is_timed_out
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar timeout da conversa: {str(e)}")
            # Em caso de erro, assumir que não expirou
            return False
    
    async def update_conversation_metadata(
        self,
        conversation_id: UUID,
        total_messages: Optional[int] = None,
        sentiment: Optional[str] = None
    ) -> Conversation:
        """
        Atualiza metadata da conversa (total de mensagens, sentiment, etc).
        
        Args:
            conversation_id: ID da conversa
            total_messages: Novo total de mensagens
            sentiment: Novo sentiment (positivo, neutro, negativo)
            
        Returns:
            Conversa atualizada
        """
        try:
            update_data = {"updated_at": datetime.now().isoformat()}
            
            if total_messages is not None:
                update_data["total_messages"] = total_messages
            
            if sentiment is not None:
                if sentiment not in ["positivo", "neutro", "negativo"]:
                    logger.warning(f"Sentiment inválido: {sentiment}. Usando 'neutro'")
                    sentiment = "neutro"
                update_data["sentiment"] = sentiment
            
            result = await self.supabase.client.table("conversations") \
                .update(update_data) \
                .eq("id", str(conversation_id)) \
                .execute()
            
            if result.data and len(result.data) > 0:
                updated_conversation = Conversation(**result.data[0])
                
                # Atualizar cache
                if conversation_id in self._conversation_cache:
                    self._conversation_cache[conversation_id] = updated_conversation
                
                logger.info(f"✅ Metadata da conversa {conversation_id} atualizada")
                return updated_conversation
            else:
                raise ValueError(f"Conversa não encontrada: {conversation_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar metadata da conversa: {str(e)}")
            raise
    
    async def get_conversation_stats(self, conversation_id: UUID) -> Dict:
        """
        Retorna estatísticas da conversa.
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            Dicionário com estatísticas:
            {
                "total_messages": int,
                "duration_minutes": float,
                "messages_per_minute": float,
                "last_message_time": datetime,
                "is_timed_out": bool
            }
        """
        try:
            # Buscar conversa
            conv_result = await self.supabase.client.table("conversations") \
                .select("*") \
                .eq("id", str(conversation_id)) \
                .single() \
                .execute()
            
            if not conv_result.data:
                raise ValueError(f"Conversa não encontrada: {conversation_id}")
            
            conversation = Conversation(**conv_result.data)
            
            # Calcular duração
            if conversation.ended_at:
                duration = conversation.ended_at - conversation.started_at
            else:
                duration = datetime.now() - conversation.started_at
            
            duration_minutes = duration.total_seconds() / 60
            
            # Calcular mensagens por minuto
            messages_per_minute = (
                conversation.total_messages / duration_minutes 
                if duration_minutes > 0 else 0
            )
            
            # Verificar timeout
            is_timed_out = await self.check_conversation_timeout(conversation_id)
            
            # Buscar última mensagem
            last_msg_result = await self.supabase.client.table("messages") \
                .select("created_at") \
                .eq("conversation_id", str(conversation_id)) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            
            last_message_time = None
            if last_msg_result.data:
                last_message_time = datetime.fromisoformat(
                    last_msg_result.data[0]["created_at"].replace("Z", "+00:00")
                )
            
            stats = {
                "total_messages": conversation.total_messages,
                "duration_minutes": round(duration_minutes, 2),
                "messages_per_minute": round(messages_per_minute, 2),
                "last_message_time": last_message_time,
                "is_timed_out": is_timed_out,
                "sentiment": conversation.sentiment,
                "current_stage": conversation.current_stage
            }
            
            logger.info(f"✅ Estatísticas da conversa {conversation_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar estatísticas da conversa: {str(e)}")
            raise


    async def get_or_create(self, phone: str) -> Conversation:
        """
        Alias for get_or_create_conversation for compatibility.
        
        Args:
            phone: Phone number
            
        Returns:
            Conversation object
        """
        conversation_data = await self.get_or_create_conversation(phone, f"session_{phone}")
        return conversation_data[0] if isinstance(conversation_data, tuple) else conversation_data
    
    async def update_last_message_at(self, conversation_id: UUID, timestamp: datetime) -> bool:
        """
        Updates the last_message_at timestamp for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            timestamp: Timestamp of the last message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.supabase.client.table("conversations") \
                .update({
                    "last_message_at": timestamp.isoformat(),
                    "updated_at": datetime.now().isoformat()
                }) \
                .eq("id", str(conversation_id)) \
                .execute()
            
            if result.data:
                logger.debug(f"Updated last_message_at for conversation {conversation_id}")
                return True
            else:
                logger.warning(f"No conversation found with ID {conversation_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating last_message_at for conversation {conversation_id}: {e}")
            return False


def get_conversation_repository() -> ConversationRepository:
    """
    Retorna instância singleton do ConversationRepository
    
    Returns:
        Instância do ConversationRepository
    """
    global _conversation_repository_instance
    
    if _conversation_repository_instance is None:
        _conversation_repository_instance = ConversationRepository()
    
    return _conversation_repository_instance