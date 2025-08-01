"""
SendTextMessageTool - Envia mensagem de texto via WhatsApp usando Evolution API
CORREÇÃO CAMADA 1: Wrapper síncrono para resolver RuntimeWarning AGnO Framework
"""

from typing import Dict, Any, Optional
# from agno.tools import tool  # Removido - causa RuntimeWarning
from loguru import logger

from ...services import get_evolution_service
from ...core.types import MessageRole
from ...core.tool_monitoring import monitor_tool
from ..core.agno_async_executor import AGnOAsyncExecutor


# CAMADA 1: Correção RuntimeWarning AGnO Framework agno/models/base.py:467
# Wrapper síncrono resolve: RuntimeWarning: coroutine 'send_text_message' was never awaited
@monitor_tool("whatsapp.send_text_message")
async def _send_text_message_async(
    text: str,
    phone: Optional[str] = None,
    delay: Optional[float] = None
) -> Dict[str, Any]:
    """
    Envia mensagem de texto via WhatsApp com simulação de digitação natural.
    
    Args:
        text: Texto da mensagem a ser enviada
        phone: Número de telefone do destinatário (opcional, obtido do contexto se não fornecido)
        delay: Delay customizado em segundos (opcional, calculado automaticamente se não fornecido)
    
    Returns:
        Dict com status do envio:
        - success: bool - Se a mensagem foi enviada com sucesso
        - message_id: str - ID da mensagem no WhatsApp (se sucesso)
        - error: str - Mensagem de erro (se falhou)
        - phone: str - Número formatado usado no envio
        - delay_applied: int - Delay aplicado em segundos
    
    Examples:
        >>> await send_text_message("Olá! Como posso ajudar?")  # Phone do contexto
        {"success": True, "message_id": "3EB0C767D097E9ECFE8A", "phone": "5511999999999", "delay_applied": 3}
        
        >>> await send_text_message("Mensagem específica", phone="5511999999999", delay=5)
        {"success": True, "message_id": "3EB0C767D097E9ECFE8B", "phone": "5511999999999", "delay_applied": 5}
    """
    try:
        # Obter phone do contexto se não fornecido
        if phone is None:
            from ...core.tool_context import get_current_phone
            phone = get_current_phone()
            
            if phone is None:
                logger.error("Phone não fornecido e não encontrado no contexto")
                return {
                    "success": False,
                    "error": "Número de telefone não disponível - forneça phone ou configure contexto",
                    "phone": None,
                    "delay_applied": 0
                }
            
            logger.debug(f"Phone obtido do contexto: {phone[:4]}****")
        
        # Log da operação
        logger.info(
            "Enviando mensagem de texto via WhatsApp",
            phone=phone[:4] + "****",  # Mascarar para segurança
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


# CAMADA 1: Criar wrapper síncrono com nome curto (evita truncamento)
# Resolve RuntimeWarning AGnO Framework
send_msg = AGnOAsyncExecutor.wrap_async_tool(_send_text_message_async)
send_msg.__name__ = "send_msg"  # Nome curto para evitar truncamento AGnO

# Export da tool - mantém compatibilidade
SendTextMessageTool = send_msg
send_text_message = send_msg  # Alias para compatibilidade