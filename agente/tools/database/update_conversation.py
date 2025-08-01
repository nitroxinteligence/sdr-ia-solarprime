"""
Tool para atualizar sessão da conversa
"""

from agno.tools import tool
from loguru import logger
from typing import Optional, Dict, Any, Literal
from uuid import UUID
from datetime import datetime

from ...repositories import get_conversation_repository
from ...core.logger import setup_module_logger

logger = setup_module_logger(__name__)


@tool(show_result=True)
async def update_conversation(
    conversation_id: str,
    session_id: Optional[str] = None,
    current_stage: Optional[str] = None,
    sentiment: Optional[Literal["positivo", "neutro", "negativo"]] = None,
    is_active: Optional[bool] = None,
    end_conversation: bool = False,
    state_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Atualiza sessão da conversa
    
    Args:
        conversation_id: ID da conversa (UUID)
        session_id: Novo ID de sessão
        current_stage: Estágio atual da conversa
        sentiment: Sentimento da conversa (positivo, neutro, negativo)
        is_active: Se a conversa está ativa
        end_conversation: Se deve encerrar a conversa
        state_data: Dados de estado da conversa (contexto, variáveis, etc.)
    
    Returns:
        Dict com sucesso e dados atualizados da conversa
    """
    try:
        logger.info(f"Atualizando conversa {conversation_id}")
        
        # Valida conversation_id
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            logger.error(f"ID de conversa inválido: {conversation_id}")
            return {
                "success": False,
                "error": "ID de conversa inválido",
                "error_type": "validation"
            }
        
        # Busca a conversa
        conv_repo = get_conversation_repository()
        conversation = await conv_repo.get_conversation_by_id(conv_uuid)
        
        if not conversation:
            logger.error(f"Conversa não encontrada: {conversation_id}")
            return {
                "success": False,
                "error": "Conversa não encontrada",
                "error_type": "not_found"
            }
        
        # Prepara dados para atualização
        update_data = {}
        
        if session_id is not None:
            update_data["session_id"] = session_id
            
        if current_stage is not None:
            update_data["current_stage"] = current_stage
            
        if sentiment is not None:
            if sentiment not in ["positivo", "neutro", "negativo"]:
                logger.warning(f"Sentimento inválido: {sentiment}")
            else:
                update_data["sentiment"] = sentiment
                
        if is_active is not None:
            update_data["is_active"] = bool(is_active)
            
        if end_conversation:
            update_data["is_active"] = False
            update_data["ended_at"] = datetime.now()
            logger.info("Encerrando conversa")
        
        # Se não há nada para atualizar, retorna sucesso
        if not update_data and not state_data:
            logger.warning("Nenhum campo para atualizar")
            return {
                "success": True,
                "message": "Nenhuma atualização necessária",
                "conversation_id": str(conversation_id),
                "data": {
                    "session_id": conversation.session_id,
                    "current_stage": conversation.current_stage,
                    "sentiment": conversation.sentiment,
                    "is_active": conversation.is_active,
                    "total_messages": conversation.total_messages
                }
            }
        
        # Atualiza a conversa
        updated_conversation = await conv_repo.update_conversation(conv_uuid, update_data)
        
        # Atualiza estado da sessão se fornecido
        session_updated = False
        if state_data:
            try:
                # Importa o repository de sessão se necessário
                from ...repositories.session_repository import get_session_repository
                session_repo = get_session_repository()
                
                # Atualiza o estado da sessão
                await session_repo.update_session_state(
                    conversation.session_id,
                    state_data
                )
                session_updated = True
                logger.info(f"Estado da sessão atualizado com {len(state_data)} campos")
            except Exception as e:
                logger.warning(f"Erro ao atualizar estado da sessão: {e}")
        
        logger.success(f"Conversa atualizada com sucesso: ID={conversation_id}")
        
        # Prepara resposta
        result = {
            "success": True,
            "conversation_id": str(conv_uuid),
            "updated_fields": list(update_data.keys()),
            "session_state_updated": session_updated,
            "data": {
                "session_id": updated_conversation.session_id,
                "lead_id": str(updated_conversation.lead_id),
                "current_stage": updated_conversation.current_stage,
                "sentiment": updated_conversation.sentiment,
                "is_active": updated_conversation.is_active,
                "total_messages": updated_conversation.total_messages,
                "started_at": updated_conversation.started_at.isoformat() if updated_conversation.started_at else None,
                "ended_at": updated_conversation.ended_at.isoformat() if updated_conversation.ended_at else None,
                "duration_minutes": None
            }
        }
        
        # Calcula duração se a conversa foi encerrada
        if updated_conversation.ended_at and updated_conversation.started_at:
            duration = updated_conversation.ended_at - updated_conversation.started_at
            result["data"]["duration_minutes"] = round(duration.total_seconds() / 60, 2)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar conversa: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao atualizar conversa: {str(e)}",
            "error_type": "database"
        }


# Exporta a tool
UpdateConversationTool = update_conversation