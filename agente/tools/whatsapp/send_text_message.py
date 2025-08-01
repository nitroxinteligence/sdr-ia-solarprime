"""
SendTextMessageTool - Envia mensagem de texto via WhatsApp usando Evolution API
"""

from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from ...services import get_evolution_service
from ...core.types import MessageRole
from ...core.tool_monitoring import monitor_tool


@tool(show_result=True)
@monitor_tool("whatsapp.send_text_message")
async def send_text_message(
    phone: str,
    text: str,
    delay: Optional[int] = None
) -> Dict[str, Any]:
    """
    Envia mensagem de texto via WhatsApp com simulação de digitação natural.
    
    Args:
        phone: Número de telefone do destinatário (formato: 5511999999999)
        text: Texto da mensagem a ser enviada
        delay: Delay customizado em segundos (opcional, calculado automaticamente se não fornecido)
    
    Returns:
        Dict com status do envio:
        - success: bool - Se a mensagem foi enviada com sucesso
        - message_id: str - ID da mensagem no WhatsApp (se sucesso)
        - error: str - Mensagem de erro (se falhou)
        - phone: str - Número formatado usado no envio
        - delay_applied: int - Delay aplicado em segundos
    
    Examples:
        >>> await send_text_message("5511999999999", "Olá! Como posso ajudar?")
        {"success": True, "message_id": "3EB0C767D097E9ECFE8A", "phone": "5511999999999", "delay_applied": 3}
        
        >>> await send_text_message("5511999999999", "Mensagem com delay específico", delay=5)
        {"success": True, "message_id": "3EB0C767D097E9ECFE8B", "phone": "5511999999999", "delay_applied": 5}
    """
    try:
        # Log da operação
        logger.info(
            "Enviando mensagem de texto via WhatsApp",
            phone=phone,
            text_length=len(text),
            custom_delay=delay
        )
        
        # Obtém serviço Evolution API
        evolution = get_evolution_service()
        
        # Envia mensagem com simulação de digitação
        result = await evolution.send_text_message(
            phone=phone,
            text=text,
            delay=delay
        )
        
        if result:
            # Extrai informações relevantes
            message_id = result.get("key", {}).get("id", "")
            
            # Calcula delay aplicado (se não foi customizado)
            applied_delay = delay if delay is not None else evolution._calculate_typing_delay(text)
            
            logger.success(
                "Mensagem de texto enviada com sucesso",
                phone=phone,
                message_id=message_id,
                delay_applied=applied_delay
            )
            
            return {
                "success": True,
                "message_id": message_id,
                "phone": phone,
                "delay_applied": applied_delay
            }
        else:
            logger.error(
                "Falha ao enviar mensagem de texto",
                phone=phone
            )
            
            return {
                "success": False,
                "error": "Falha ao enviar mensagem - resposta vazia da API",
                "phone": phone,
                "delay_applied": 0
            }
            
    except Exception as e:
        logger.error(
            f"Erro ao enviar mensagem de texto: {str(e)}",
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro ao enviar mensagem: {str(e)}",
            "phone": phone,
            "delay_applied": 0
        }


# Export da tool
SendTextMessageTool = send_text_message