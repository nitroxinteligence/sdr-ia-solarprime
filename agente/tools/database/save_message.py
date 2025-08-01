"""
Tool para salvar mensagem na conversa (com suporte multimodal)
"""

from agno.tools import tool
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from ...repositories import get_message_repository, get_conversation_repository
from ...core.types import Message, MessageRole, MediaType
from ...core.logger import setup_module_logger

logger = setup_module_logger(__name__)


@tool(show_result=True)
async def save_message(
    conversation_id: str,
    content: str,
    role: str = "user",
    whatsapp_message_id: Optional[str] = None,
    media_type: Optional[str] = None,
    media_url: Optional[str] = None,
    media_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Salva mensagem na conversa (com suporte multimodal)

    Args:
        conversation_id: ID da conversa (UUID)
        content: Conteúdo da mensagem
        role: Papel da mensagem (user, assistant, system)
        whatsapp_message_id: ID da mensagem no WhatsApp
        media_type: Tipo de mídia (text, image, audio, video, document, sticker)
        media_url: URL da mídia
        media_data: Dados adicionais da mídia (metadata, análise, etc.)

    Returns:
        Dict com sucesso e ID da mensagem salva
    """
    try:
        logger.info(f"Salvando mensagem na conversa {conversation_id}")

        # Valida conversation_id
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            logger.error(f"ID de conversa inválido: {conversation_id}")
            return {
                "success": False,
                "error": "ID de conversa inválido",
                "error_type": "validation",
            }

        # Valida role
        try:
            message_role = MessageRole(role.lower())
        except ValueError:
            logger.error(f"Role inválido: {role}")
            return {
                "success": False,
                "error": "Role inválido. Use: user, assistant ou system",
                "error_type": "validation",
            }

        # Valida media_type se fornecido
        if media_type:
            try:
                media_type_enum = MediaType(media_type.lower())
            except ValueError:
                logger.warning(f"Tipo de mídia inválido: {media_type}, usando TEXT")
                media_type_enum = MediaType.TEXT
        else:
            media_type_enum = MediaType.TEXT

        # Verifica se a conversa existe
        conv_repo = get_conversation_repository()
        conversation = await conv_repo.get_conversation_by_id(conv_uuid)

        if not conversation:
            logger.error(f"Conversa não encontrada: {conversation_id}")
            return {
                "success": False,
                "error": "Conversa não encontrada",
                "error_type": "not_found",
            }

        # Prepara dados da mensagem
        message_data = {
            "id": uuid4(),  # Gera UUID antes de salvar
            "conversation_id": conv_uuid,
            "role": message_role,
            "content": content,
            "media_type": (
                media_type_enum if media_type_enum != MediaType.TEXT else None
            ),  # Não salva TEXT explicitamente
            "created_at": datetime.now(),
        }

        # Adiciona dados opcionais
        if whatsapp_message_id:
            message_data["whatsapp_message_id"] = whatsapp_message_id
        if media_url:
            message_data["media_url"] = media_url
        if media_data:
            message_data["media_data"] = media_data

        # Salva a mensagem
        message_repo = get_message_repository()
        message = await message_repo.save_message(Message(**message_data))

        if not message:
            logger.error("Falha ao salvar mensagem")
            return {
                "success": False,
                "error": "Falha ao salvar mensagem no banco de dados",
                "error_type": "database",
            }

        # Atualiza contador de mensagens na conversa
        try:
            await conv_repo.update_conversation(
                conv_uuid, {"total_messages": conversation.total_messages + 1}
            )
        except Exception as e:
            logger.warning(f"Erro ao atualizar contador de mensagens: {e}")

        logger.success(f"Mensagem salva com sucesso: ID={message.id}")

        # Prepara resposta
        result = {
            "success": True,
            "message_id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "data": {
                "role": (
                    message.role.value
                    if hasattr(message.role, "value")
                    else message.role
                ),
                "content": (
                    message.content[:100] + "..."
                    if len(message.content) > 100
                    else message.content
                ),
                "media_type": (
                    message.media_type.value
                    if message.media_type and hasattr(message.media_type, "value")
                    else message.media_type
                ),
                "has_media": bool(message.media_url or message.media_data),
                "whatsapp_message_id": message.whatsapp_message_id,
                "created_at": (
                    message.created_at.isoformat() if message.created_at else None
                ),
            },
        }

        # Adiciona informações de mídia se houver
        if message.media_url or message.media_data:
            result["media_info"] = {
                "type": media_type_enum.value,
                "url": message.media_url,
                "has_data": bool(message.media_data),
                "data_keys": (
                    list(message.media_data.keys()) if message.media_data else []
                ),
            }

        return result

    except Exception as e:
        logger.error(f"Erro inesperado ao salvar mensagem: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao salvar mensagem: {str(e)}",
            "error_type": "database",
        }


# Exporta a tool
SaveMessageTool = save_message
