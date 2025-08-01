"""
SendTextMessageTool - Envia mensagem de texto via WhatsApp usando Evolution API
CORREÇÃO CAMADA 2: Controle de concorrência para resolver AGnO Framework multiple calls
"""

import asyncio
from typing import Dict, Any, Optional
# from agno.tools import tool  # Removido - causa RuntimeWarning
from loguru import logger

from ...services import get_evolution_service
from ...core.types import MessageRole
from ...core.tool_monitoring import monitor_tool
from ..core.agno_async_executor import AGnOAsyncExecutor

# CAMADA 2: Controle de concorrência - AGnO Framework Issue #2296
# Semáforo global para controlar chamadas simultâneas da ferramenta
_message_send_semaphore = asyncio.Semaphore(1)  # Apenas 1 mensagem por vez

# CAMADA 3: Lock global para controlar concorrência entre threads
# Necessário porque AGnOAsyncExecutor cria threads separadas
import threading
_thread_lock = threading.Lock()


# CAMADA 1: Correção RuntimeWarning AGnO Framework agno/models/base.py:467
# CAMADA 2: Controle de concorrência AGnO Framework Issue #2296
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
    # CAMADA 2: Controle de concorrência - AGnO Framework Issue #2296
    # Semáforo garante que apenas uma mensagem seja enviada por vez
    async with _message_send_semaphore:
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
            
            # Log da operação com controle de concorrência
            logger.info(
                "Enviando mensagem de texto via WhatsApp [SEQUENCIAL]",
                phone=phone[:4] + "****",  # Mascarar para segurança
                text_length=len(text),
                custom_delay=delay
            )
            
            # Obtém serviço Evolution API
            evolution = get_evolution_service()
            
            # Envia mensagem com simulação de digitação (agora sequencial)
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
                    "Mensagem de texto enviada com sucesso [SEQUENCIAL]",
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
                    "Falha ao enviar mensagem de texto [SEQUENCIAL]",
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
                f"Erro ao enviar mensagem de texto [SEQUENCIAL]: {str(e)}",
                phone=phone,
                error_type=type(e).__name__
            )
            
            return {
                "success": False,
                "error": f"Erro ao enviar mensagem: {str(e)}",
                "phone": phone,
                "delay_applied": 0
            }


def get_message_semaphore_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas do controle de concorrência (semáforo + thread lock)
    
    Returns:
        Dict com estatísticas de controle de concorrência
    """
    waiters = getattr(_message_send_semaphore, '_waiters', None)
    waiting_count = len(waiters) if waiters is not None else 0
    
    return {
        "semaphore_value": _message_send_semaphore._value,
        "max_concurrent_messages": 1,
        "currently_sending": _message_send_semaphore._value == 0,
        "waiting_count": waiting_count,
        "thread_lock_available": not _thread_lock.locked(),
        "thread_lock_locked": _thread_lock.locked(),
        "concurrency_layers": ["async_semaphore", "thread_lock"]
    }


# CAMADA 1: Criar wrapper síncrono com controle de concorrência entre threads
# Resolve RuntimeWarning AGnO Framework + controla concorrência
def _create_thread_safe_wrapper(async_func):
    """Cria wrapper síncrono com controle de thread-level concurrency"""
    def sync_wrapper(*args, **kwargs):
        logger.info(f"[THREAD-LOCK] Aguardando lock para envio de mensagem...")
        
        # CAMADA 3: Lock entre threads (AGnOAsyncExecutor ThreadPoolExecutor)
        with _thread_lock:
            logger.info(f"[THREAD-LOCK] Lock obtido - executando mensagem sequencialmente")
            
            # Usar o wrapper padrão do AGnO dentro do lock
            return AGnOAsyncExecutor.wrap_async_tool(async_func)(*args, **kwargs)
    
    sync_wrapper.__name__ = async_func.__name__
    sync_wrapper.__doc__ = async_func.__doc__
    return sync_wrapper

send_msg = _create_thread_safe_wrapper(_send_text_message_async)
send_msg.__name__ = "send_msg"  # Nome curto para evitar truncamento AGnO

# Export da tool - mantém compatibilidade
SendTextMessageTool = send_msg
send_text_message = send_msg  # Alias para compatibilidade