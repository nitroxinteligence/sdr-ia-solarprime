"""
Send Reaction Tool para AGnO Framework
Envia reações (emojis) a mensagens específicas via Evolution API
"""

import asyncio
import random
from typing import Optional, Dict, Any, List
from datetime import datetime

from agno.tools import tool
from agente.core.logger import logger, setup_module_logger
from agente.services import get_evolution_service

# Logger específico para o módulo
module_logger = setup_module_logger("send_reaction_tool")

# Reações disponíveis por categoria - APENAS ✅ 👍 ❤️
REACTIONS = {
    "positive": ["❤️", "👍"],
    "confirmation": ["✅", "👍"],
    "media_approval": ["✅", "👍"],
    "spontaneous": ["❤️"],
    "energy_related": ["✅", "👍"],
    "appreciation": ["❤️", "👍"]
}

# Configurações de probabilidade
SPONTANEOUS_PROBABILITY = 0.15  # 15% chance de reação espontânea
MEDIA_REACTION_PROBABILITY = 0.80  # 80% chance de reagir a mídia


def get_reactions_by_category(category: str) -> List[str]:
    """
    Obtém reações por categoria
    
    Args:
        category: Categoria de reação
        
    Returns:
        Lista de emojis da categoria
    """
    return REACTIONS.get(category, REACTIONS["positive"])


def should_react_spontaneously() -> bool:
    """
    Determina se deve reagir espontaneamente baseado em probabilidade
    
    Returns:
        True se deve reagir espontaneamente
    """
    return random.random() < SPONTANEOUS_PROBABILITY


def should_react_to_media() -> bool:
    """
    Determina se deve reagir a mídia baseado em probabilidade
    
    Returns:
        True se deve reagir à mídia
    """
    return random.random() < MEDIA_REACTION_PROBABILITY


def select_contextual_reaction(
    context: str = "general",
    media_type: Optional[str] = None
) -> str:
    """
    Seleciona reação baseada no contexto
    
    Args:
        context: Contexto da conversa
        media_type: Tipo de mídia (se aplicável)
        
    Returns:
        Emoji de reação selecionado
    """
    # Determinar categoria baseada no contexto
    if media_type:
        category = "media_approval"
    elif "energia" in context.lower() or "solar" in context.lower():
        category = "energy_related"
    elif any(word in context.lower() for word in ["obrigad", "grato", "valeu"]):
        category = "appreciation"
    elif any(word in context.lower() for word in ["sim", "perfeito", "ótimo", "excelente"]):
        category = "confirmation"
    else:
        category = "spontaneous"
    
    # Selecionar reação aleatória da categoria
    available_reactions = get_reactions_by_category(category)
    return random.choice(available_reactions)


@tool(show_result=True)
async def send_reaction(
    phone: str,
    message_key: str,
    reaction: Optional[str] = None,
    context: str = "general",
    media_type: Optional[str] = None,
    force_send: bool = False
) -> Dict[str, Any]:
    """
    Envia reação a uma mensagem específica
    
    Args:
        phone: Número de telefone do destinatário
        message_key: ID da mensagem para reagir
        reaction: Emoji específico (opcional - será selecionado automaticamente)
        context: Contexto da conversa para seleção inteligente
        media_type: Tipo de mídia (image, audio, document)
        force_send: Força o envio ignorando probabilidades
        
    Returns:
        Resultado do envio da reação
    """
    try:
        module_logger.info(
            "Sending reaction",
            phone=phone[:4] + "****",
            message_key=message_key,
            reaction=reaction,
            context=context,
            media_type=media_type,
            force_send=force_send
        )
        
        # Se não forçado, verificar probabilidades
        if not force_send:
            if media_type:
                # Reação a mídia
                if not should_react_to_media():
                    module_logger.debug("Skipping media reaction based on probability")
                    return {
                        "success": True,
                        "skipped": True,
                        "reason": "probability_check",
                        "phone": phone
                    }
            else:
                # Reação espontânea
                if not should_react_spontaneously():
                    module_logger.debug("Skipping spontaneous reaction based on probability")
                    return {
                        "success": True,
                        "skipped": True,
                        "reason": "probability_check",
                        "phone": phone
                    }
        
        # Selecionar reação se não foi especificada
        if not reaction:
            reaction = select_contextual_reaction(context, media_type)
        
        # Adicionar delay natural para parecer mais humano
        if not force_send:
            delay = random.uniform(0.5, 2.0)  # 0.5 a 2.0 segundos
            module_logger.debug(f"Adding natural delay: {delay:.1f}s")
            await asyncio.sleep(delay)
        
        # Enviar reação via Evolution API
        evolution_service = get_evolution_service()
        
        result = await evolution_service.send_reaction(
            phone=phone,
            message_key=message_key,
            reaction=reaction
        )
        
        if result:
            module_logger.info(
                "Reaction sent successfully",
                phone=phone[:4] + "****",
                reaction=reaction,
                context=context
            )
            
            return {
                "success": True,
                "reaction": reaction,
                "phone": phone,
                "message_key": message_key,
                "context": context,
                "evolution_response": result
            }
        else:
            module_logger.error(
                "Failed to send reaction",
                phone=phone[:4] + "****",
                reaction=reaction
            )
            
            return {
                "success": False,
                "error": "Evolution API failed to send reaction",
                "phone": phone,
                "reaction": reaction
            }
    
    except Exception as e:
        module_logger.error(
            f"Error sending reaction: {str(e)}",
            phone=phone[:4] + "****",
            message_key=message_key,
            reaction=reaction
        )
        
        return {
            "success": False,
            "error": str(e),
            "phone": phone,
            "reaction": reaction
        }


# Exportar a tool para o AgentCore
SendReactionTool = send_reaction