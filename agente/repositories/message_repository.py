"""
Repository para gerenciamento de mensagens do SDR Agent
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from ..core.types import Message, MessageRole, MediaType
from ..core.logger import setup_module_logger
from ..services import get_supabase_service
from ..utils.validators import sanitize_input

logger = setup_module_logger(__name__)

# Singleton instance
_message_repository_instance = None


class MessageRepository:
    """
    Repository responsável pelo gerenciamento de mensagens no banco de dados
    """

    def __init__(self):
        """Inicializa o repository com o serviço Supabase"""
        self.supabase = get_supabase_service()
        self._message_cache = {}  # Cache opcional para últimas mensagens
        self._cache_ttl = 300  # 5 minutos de cache

    async def save_user_message(
        self,
        conversation_id: UUID,
        content: str,
        whatsapp_id: str,
        media: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Salva mensagem do usuário usando o SupabaseService

        Args:
            conversation_id: ID da conversa
            content: Conteúdo da mensagem
            whatsapp_id: ID da mensagem no WhatsApp
            media: Dados de mídia opcional

        Returns:
            Message: Mensagem salva
        """
        try:
            # Cria objeto Message (validação será feita no SupabaseService)
            message = Message(
                id=uuid4(),
                conversation_id=conversation_id,
                whatsapp_message_id=whatsapp_id,
                role=MessageRole.USER,
                content=sanitize_input(
                    content, max_length=5000
                ),  # Sanitização básica mantida
                media_type=(
                    MediaType(media.get("type", "text"))
                    if media and media.get("type")
                    else None
                ),
                media_url=media.get("url") if media else None,
                media_data=media,
                created_at=datetime.now(),
            )

            # Salva usando SupabaseService com retry logic
            saved_message = await self.supabase.save_message(message)

            # Incrementa contador de mensagens na conversa
            self._increment_message_count(conversation_id)

            # Invalida cache
            self._invalidate_cache(conversation_id)

            logger.info(f"Mensagem do usuário salva: {saved_message.id}")
            return saved_message

        except Exception as e:
            logger.error(f"Erro ao salvar mensagem do usuário: {e}")
            raise

    async def save_assistant_message(
        self, conversation_id: UUID, content: str, chunks: Optional[List[str]] = None
    ) -> Message:
        """
        Salva mensagem do assistente usando o SupabaseService

        Args:
            conversation_id: ID da conversa
            content: Conteúdo da mensagem
            chunks: Lista de chunks da mensagem para tracking

        Returns:
            Message: Mensagem salva
        """
        try:
            # Prepara media_data para tracking de chunks
            media_data = None
            if chunks:
                media_data = {
                    "chunks": chunks,
                    "chunk_count": len(chunks),
                    "total_delay_ms": sum(
                        self._calculate_chunk_delay(chunk) for chunk in chunks
                    ),
                }

            # Cria objeto Message (validação será feita no SupabaseService)
            message = Message(
                id=uuid4(),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=sanitize_input(
                    content, max_length=5000
                ),  # Sanitização básica mantida
                media_data=media_data,
                created_at=datetime.now(),
            )

            # Salva usando SupabaseService com retry logic
            saved_message = await self.supabase.save_message(message)

            # Incrementa contador de mensagens na conversa
            self._increment_message_count(conversation_id)

            # Invalida cache
            self._invalidate_cache(conversation_id)

            logger.info(f"Mensagem do assistente salva: {saved_message.id}")
            return saved_message

        except Exception as e:
            logger.error(f"Erro ao salvar mensagem do assistente: {e}")
            raise

    async def save_message(self, message: Message) -> Message:
        """
        Método genérico para salvar mensagem - delega para o SupabaseService

        Args:
            message: Objeto Message a ser salvo

        Returns:
            Message: Mensagem salva com ID atualizado
        """
        try:
            # Usa o SupabaseService diretamente para manter consistência
            saved_message = await self.supabase.save_message(message)

            # Incrementa contador de mensagens na conversa
            self._increment_message_count(message.conversation_id)

            # Invalida cache
            self._invalidate_cache(message.conversation_id)

            logger.info(
                f"Mensagem salva através do método genérico: {saved_message.id}"
            )
            return saved_message

        except Exception as e:
            logger.error(f"Erro ao salvar mensagem através do método genérico: {e}")
            raise

    def get_conversation_messages(
        self, conversation_id: UUID, limit: int = 100
    ) -> List[Message]:
        """
        Busca mensagens de uma conversa

        Args:
            conversation_id: ID da conversa
            limit: Limite de mensagens

        Returns:
            List[Message]: Lista de mensagens ordenadas por data (mais recentes primeiro)
        """
        try:
            # Verifica cache primeiro
            cache_key = f"conv_{conversation_id}_{limit}"
            if cache_key in self._message_cache:
                cached_data = self._message_cache[cache_key]
                if (
                    datetime.now() - cached_data["timestamp"]
                ).seconds < self._cache_ttl:
                    logger.debug(
                        f"Retornando mensagens do cache para conversa "
                        f"{conversation_id}"
                    )
                    return cached_data["messages"]

            # Busca no banco
            result = (
                self.supabase.client.table("messages")
                .select("*")
                .eq("conversation_id", str(conversation_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            if result.data:
                messages = [self._row_to_message(row) for row in result.data]

                # Atualiza cache
                self._message_cache[cache_key] = {
                    "messages": messages,
                    "timestamp": datetime.now(),
                }

                logger.info(
                    f"Encontradas {len(messages)} mensagens para conversa "
                    f"{conversation_id}"
                )
                return messages
            else:
                logger.info(
                    f"Nenhuma mensagem encontrada para conversa "
                    f"{conversation_id}"
                )
                return []

        except Exception as e:
            logger.error(f"Erro ao buscar mensagens da conversa: {e}")
            raise

    def get_last_messages_by_phone(self, phone: str, limit: int = 100) -> List[Message]:
        """
        Busca últimas mensagens de um telefone (join com conversations)

        Args:
            phone: Número de telefone
            limit: Limite de mensagens

        Returns:
            List[Message]: Lista de mensagens ordenadas por data (mais recentes primeiro)
        """
        try:
            # Primeiro busca as conversas do telefone
            conversations_result = (
                self.supabase.client.table("conversations")
                .select("id")
                .eq("phone", phone)
                .execute()
            )

            if not conversations_result.data:
                logger.info(f"Nenhuma conversa encontrada para telefone {phone}")
                return []

            # Extrai IDs das conversas
            conversation_ids = [conv["id"] for conv in conversations_result.data]

            # Busca mensagens de todas as conversas
            result = (
                self.supabase.client.table("messages")
                .select("*")
                .in_("conversation_id", conversation_ids)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            if result.data:
                messages = [self._row_to_message(row) for row in result.data]
                logger.info(
                    f"Encontradas {len(messages)} mensagens para telefone "
                    f"{phone}"
                )
                return messages
            else:
                logger.info(f"Nenhuma mensagem encontrada para telefone {phone}")
                return []

        except Exception as e:
            logger.error(f"Erro ao buscar mensagens por telefone: {e}")
            raise

    def search_messages(self, query: str, phone: Optional[str] = None) -> List[Message]:
        """
        Busca mensagens por conteúdo (full-text search)

        Args:
            query: Termo de busca
            phone: Filtrar por telefone (opcional)

        Returns:
            List[Message]: Lista de mensagens encontradas
        """
        try:
            # Sanitiza query
            sanitized_query = sanitize_input(query, max_length=100)

            # Inicia query base
            messages_query = (
                self.supabase.client.table("messages")
                .select("*")
                .ilike("content", f"%{sanitized_query}%")
                .order("created_at", desc=True)
                .limit(100)
            )

            # Se fornecido telefone, filtra por conversas desse telefone
            if phone:
                # Busca conversas do telefone
                conversations_result = (
                    self.supabase.client.table("conversations")
                    .select("id")
                    .eq("phone", phone)
                    .execute()
                )

                if conversations_result.data:
                    conversation_ids = [
                        conv["id"] for conv in conversations_result.data
                    ]
                    messages_query = messages_query.in_(
                        "conversation_id", conversation_ids
                    )
                else:
                    return []  # Sem conversas para esse telefone

            # Executa busca
            result = messages_query.execute()

            if result.data:
                messages = [self._row_to_message(row) for row in result.data]
                logger.info(
                    f"Encontradas {len(messages)} mensagens para query '{query}'"
                )
                return messages
            else:
                logger.info(f"Nenhuma mensagem encontrada para query '{query}'")
                return []

        except Exception as e:
            logger.error(f"Erro ao buscar mensagens: {e}")
            raise

    async def save_media_message(
        self,
        conversation_id: UUID,
        media_type: MediaType,
        media_url: str,
        caption: Optional[str] = None,
        whatsapp_id: Optional[str] = None,
    ) -> Message:
        """
        Salva mensagem de mídia usando o SupabaseService

        Args:
            conversation_id: ID da conversa
            media_type: Tipo de mídia
            media_url: URL da mídia
            caption: Legenda opcional
            whatsapp_id: ID da mensagem no WhatsApp

        Returns:
            Message: Mensagem salva
        """
        try:
            # Usa a legenda como conteúdo ou indica o tipo de mídia
            content = caption if caption else f"[{media_type.value}]"

            # Prepara media_data
            media_data = {
                "caption": caption,
                "media_type": media_type.value,
                "media_url": media_url,
            }

            # Cria objeto Message (validação será feita no SupabaseService)
            message = Message(
                id=uuid4(),
                conversation_id=conversation_id,
                whatsapp_message_id=whatsapp_id,
                role=MessageRole.USER,
                content=sanitize_input(
                    content, max_length=1000
                ),  # Sanitização básica mantida
                media_type=media_type,
                media_url=media_url,
                media_data=media_data,
                created_at=datetime.now(),
            )

            # Salva usando SupabaseService com retry logic
            saved_message = await self.supabase.save_message(message)

            # Incrementa contador de mensagens na conversa
            self._increment_message_count(conversation_id)

            # Invalida cache
            self._invalidate_cache(conversation_id)

            logger.info(
                f"Mensagem de mídia salva: {saved_message.id} ({media_type.value})"
            )
            return saved_message

        except Exception as e:
            logger.error(f"Erro ao salvar mensagem de mídia: {e}")
            raise

    def mark_messages_as_read(self, conversation_id: UUID) -> int:
        """
        Marca mensagens como lidas (atualiza timestamp de leitura)

        Args:
            conversation_id: ID da conversa

        Returns:
            int: Quantidade de mensagens marcadas como lidas
        """
        try:
            # Busca mensagens não lidas
            # Como não temos campo is_read, simulamos atualizando updated_at

            # Conta mensagens da conversa
            count_result = (
                self.supabase.client.table("messages")
                .select("id", count="exact")
                .eq("conversation_id", str(conversation_id))
                .execute()
            )

            message_count = count_result.count if count_result.count else 0

            # Atualiza timestamp de leitura na conversa
            update_result = (
                self.supabase.client.table("conversations")
                .update({"last_read_at": datetime.now().isoformat()})
                .eq("id", str(conversation_id))
                .execute()
            )

            if update_result.data:
                logger.info(
                    f"Marcadas {message_count} mensagens como lidas na "
                    f"conversa {conversation_id}"
                )
                return message_count
            else:
                return 0

        except Exception as e:
            logger.error(f"Erro ao marcar mensagens como lidas: {e}")
            raise

    def get_unread_count(self, lead_id: UUID) -> int:
        """
        Conta mensagens não lidas de um lead

        Args:
            lead_id: ID do lead

        Returns:
            int: Quantidade de mensagens não lidas
        """
        try:
            # Busca conversas do lead
            conversations_result = (
                self.supabase.client.table("conversations")
                .select("id, last_read_at")
                .eq("lead_id", str(lead_id))
                .execute()
            )

            if not conversations_result.data:
                return 0

            total_unread = 0

            for conv in conversations_result.data:
                # Se temos last_read_at, conta mensagens após essa data
                if conv.get("last_read_at"):
                    result = (
                        self.supabase.client.table("messages")
                        .select("id", count="exact")
                        .eq("conversation_id", conv["id"])
                        .gt("created_at", conv["last_read_at"])
                        .execute()
                    )
                else:
                    # Se não tem last_read_at, conta todas as mensagens
                    result = (
                        self.supabase.client.table("messages")
                        .select("id", count="exact")
                        .eq("conversation_id", conv["id"])
                        .execute()
                    )

                if result.count:
                    total_unread += result.count

            logger.info(f"Lead {lead_id} tem {total_unread} mensagens não lidas")
            return total_unread

        except Exception as e:
            logger.error(f"Erro ao contar mensagens não lidas: {e}")
            raise

    # Métodos auxiliares privados

    def _row_to_message(self, row: Dict[str, Any]) -> Message:
        """
        Converte linha do banco para objeto Message

        Args:
            row: Dados da linha

        Returns:
            Message: Objeto Message
        """
        return Message(
            id=UUID(row["id"]),
            conversation_id=UUID(row["conversation_id"]),
            whatsapp_message_id=row.get("whatsapp_message_id"),
            role=MessageRole(row["role"]),
            content=row["content"],
            media_type=(
                MediaType(row["media_type"]) if row.get("media_type") else None
            ),
            media_url=row.get("media_url"),
            media_data=row.get("media_data"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _increment_message_count(self, conversation_id: UUID):
        """
        Incrementa contador de mensagens na conversa e no profile

        Args:
            conversation_id: ID da conversa
        """
        try:
            # Incrementa na conversa - usar conv_id baseado na mensagem de erro
            self.supabase.client.rpc(
                "increment_conversation_messages",
                {"conv_id": str(conversation_id)},
            ).execute()

            # Busca lead_id da conversa para incrementar no profile
            conv_result = (
                self.supabase.client.table("conversations")
                .select("lead_id")
                .eq("id", str(conversation_id))
                .single()
                .execute()
            )

            if conv_result.data:
                lead_id = conv_result.data["lead_id"]
                
                # Buscar phone do lead para atualizar profile (profiles usa phone_number, não lead_id)
                lead_result = (
                    self.supabase.client.table("leads")
                    .select("phone_number")
                    .eq("id", lead_id)
                    .single()
                    .execute()
                )
                
                if lead_result.data:
                    phone_number = lead_result.data["phone_number"]
                    
                    # Incrementa no profile usando phone_number (campo correto da tabela)
                    self.supabase.client.table("profiles").update({
                        "total_messages": "total_messages + 1"  # PostgreSQL expression
                    }).eq("phone_number", phone_number).execute()

        except Exception as e:
            logger.warning(f"Erro ao incrementar contador de mensagens: {e}")
            # Não propaga erro para não impedir salvamento da mensagem

    def _calculate_chunk_delay(self, chunk: str) -> int:
        """
        Calcula delay em ms para um chunk de texto

        Args:
            chunk: Texto do chunk

        Returns:
            int: Delay em milissegundos
        """
        # Aproximadamente 60 palavras por minuto = 1 palavra por segundo
        # Adiciona variação para parecer mais natural
        words = len(chunk.split())
        base_delay = words * 1000  # 1 segundo por palavra

        # Adiciona pequena variação (±20%)
        import random

        variation = random.uniform(0.8, 1.2)

        return int(base_delay * variation)

    def _invalidate_cache(self, conversation_id: UUID):
        """
        Invalida cache relacionado a uma conversa

        Args:
            conversation_id: ID da conversa
        """
        # Remove entradas do cache que contém o conversation_id
        keys_to_remove = []
        for key in self._message_cache:
            if str(conversation_id) in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._message_cache[key]

        logger.debug(f"Cache invalidado para conversa {conversation_id}")


# Singleton instance
_message_repository = None


def get_message_repository() -> MessageRepository:
    """
    Retorna instância singleton do MessageRepository

    Returns:
        MessageRepository: Instância do repository
    """
    global _message_repository_instance
    if _message_repository_instance is None:
        _message_repository_instance = MessageRepository()
    return _message_repository_instance
