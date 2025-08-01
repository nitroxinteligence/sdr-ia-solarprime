"""
SendGreetingsTool - Envia mensagem de cumprimento personalizada baseada no horário
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ...core.tool_monitoring import monitor_tool
from ..core.agno_async_executor import AGnOAsyncExecutor
from .send_text_message import _send_text_message_async


@monitor_tool("whatsapp.send_greetings")
async def _send_greetings_async(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    delay: Optional[float] = None
) -> Dict[str, Any]:
    """
    Envia mensagem de cumprimento personalizada baseada no horário.
    
    Args:
        name: Nome do destinatário (opcional)
        phone: Número de telefone do destinatário (opcional, obtido do contexto se não fornecido)
        delay: Delay customizado em segundos (opcional)
    
    Returns:
        Dict com status do envio:
        - success: bool - Se a mensagem foi enviada com sucesso
        - message_id: str - ID da mensagem no WhatsApp (se sucesso)
        - error: str - Mensagem de erro (se falhou)
        - phone: str - Número formatado usado no envio
        - greeting_used: str - Cumprimento usado
        - delay_applied: int - Delay aplicado em segundos
    
    Examples:
        >>> await send_greetings("João")
        {"success": True, "message_id": "3EB0C767D097E9ECFE8A", "greeting_used": "Oi João, boa tarde!"}
        
        >>> await send_greetings()  # Phone do contexto, sem nome
        {"success": True, "message_id": "3EB0C767D097E9ECFE8B", "greeting_used": "Oi, boa tarde!"}
    """
    try:
        # Gerar cumprimento baseado no horário
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greetings = [
                "Oi{name_part}, bom dia! ☀️",
                "Olá{name_part}, bom dia! 😊",
                "Bom dia{name_part}! ☀️"
            ]
        elif 12 <= hour < 18:
            greetings = [
                "Oi{name_part}, boa tarde! 😊",
                "Olá{name_part}, boa tarde! ☀️",
                "Boa tarde{name_part}! 😊"
            ]
        else:
            greetings = [
                "Oi{name_part}, boa noite! 🌙",
                "Olá{name_part}, boa noite! 😊",
                "Boa noite{name_part}! 🌙"
            ]
        
        # Escolher cumprimento aleatório
        import random
        greeting_template = random.choice(greetings)
        
        # Personalizar com nome se fornecido
        name_part = f" {name}" if name else ""
        greeting_text = greeting_template.format(name_part=name_part)
        
        logger.info(
            "Enviando cumprimento personalizado",
            name=name,
            hour=hour,
            greeting=greeting_text[:50] + "..." if len(greeting_text) > 50 else greeting_text
        )
        
        # Usar ferramenta de envio de texto existente
        result = await _send_text_message_async(
            text=greeting_text,
            phone=phone,
            delay=delay
        )
        
        # Adicionar informações específicas do cumprimento
        if result.get("success"):
            result["greeting_used"] = greeting_text
            logger.success(
                "Cumprimento enviado com sucesso",
                greeting=greeting_text
            )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Erro ao enviar cumprimento: {str(e)}",
            name=name,
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro ao enviar cumprimento: {str(e)}",
            "phone": phone,
            "greeting_used": None,
            "delay_applied": 0
        }


# Wrapper síncrono com nome curto (evita truncamento AGnO)
send_greetings = AGnOAsyncExecutor.wrap_async_tool(_send_greetings_async)
send_greetings.__name__ = "send_greetings"

# Export da tool - mantém compatibilidade
SendGreetingsTool = send_greetings