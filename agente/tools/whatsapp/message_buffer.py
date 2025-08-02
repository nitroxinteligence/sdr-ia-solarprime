"""
MessageBufferTool - Gerencia buffer de mensagens para envio natural e consolidado
Versão simplificada usando novo Evolution API Service v2
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from agno.tools import tool
from loguru import logger

from agente.services import get_evolution_service


# Buffer global de mensagens por telefone
_message_buffers: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
_buffer_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


@tool(show_result=True, stop_after_tool_call=False)
async def buffer_message(
    phone: str,
    message: str,
    consolidate_after_ms: int = 3000,
    max_buffer_size: int = 5,
    auto_send: bool = True,
    force_send: bool = False
) -> Dict[str, Any]:
    """
    Adiciona mensagem ao buffer para consolidação e envio otimizado
    
    Esta ferramenta gerencia um buffer de mensagens por telefone, permitindo
    consolidar múltiplas mensagens em uma única antes do envio, evitando
    spam e criando uma experiência mais natural de conversa.
    
    Args:
        phone: Número de telefone do destinatário (formato: 5511999999999)
        message: Mensagem a ser adicionada ao buffer
        consolidate_after_ms: Tempo em ms para aguardar antes de consolidar (padrão: 3000)
        max_buffer_size: Número máximo de mensagens no buffer antes de forçar envio (padrão: 5)
        auto_send: Se deve enviar automaticamente após timeout (padrão: True)
        force_send: Se deve forçar envio imediato do buffer (padrão: False)
    
    Returns:
        Dict com status do buffer:
        - success: bool - Se a operação foi realizada com sucesso
        - buffer_size: int - Número de mensagens no buffer após operação
        - message_added: bool - Se a mensagem foi adicionada ao buffer
        - sent: bool - Se mensagens foram enviadas
        - consolidated_message: str - Mensagem consolidada enviada (se sent=True)
        - time_until_send_ms: int - Tempo restante até envio automático
        - error: str - Mensagem de erro (se falhou)
    
    Examples:
        >>> await buffer_message("5511999999999", "Primeira parte da resposta...")
        {"success": True, "buffer_size": 1, "message_added": True, "sent": False, "time_until_send_ms": 3000}
        
        >>> await buffer_message("5511999999999", "Segunda parte...", force_send=True)
        {"success": True, "buffer_size": 0, "message_added": True, "sent": True, "consolidated_message": "Primeira parte...\\n\\nSegunda parte..."}
    """
    try:
        logger.info(
            "Processando mensagem no buffer",
            phone=phone,
            message_length=len(message),
            force_send=force_send,
            auto_send=auto_send
        )
        
        # Obtém lock para o telefone específico
        async with _buffer_locks[phone]:
            buffer = _message_buffers[phone]
            
            # Adiciona timestamp se não existe
            if message and not force_send:
                buffer.append({
                    "message": message,
                    "timestamp": datetime.now(),
                    "sent": False
                })
                logger.debug(
                    f"Mensagem adicionada ao buffer",
                    phone=phone,
                    buffer_size=len(buffer)
                )
            
            # Verifica condições de envio
            should_send = False
            send_reason = None
            
            if force_send:
                should_send = True
                send_reason = "forced"
            elif len(buffer) >= max_buffer_size:
                should_send = True
                send_reason = "buffer_full"
            elif buffer and (datetime.now() - buffer[0]["timestamp"]).total_seconds() * 1000 >= consolidate_after_ms:
                should_send = True
                send_reason = "timeout"
            
            # Calcula tempo restante
            time_until_send_ms = 0
            if buffer and not should_send:
                oldest_timestamp = buffer[0]["timestamp"]
                elapsed_ms = (datetime.now() - oldest_timestamp).total_seconds() * 1000
                time_until_send_ms = max(0, consolidate_after_ms - elapsed_ms)
            
            # Envia se necessário
            sent = False
            consolidated_message = ""
            
            if should_send and buffer:
                # Consolida mensagens
                messages_to_send = [msg["message"] for msg in buffer if not msg["sent"]]
                
                if messages_to_send:
                    # Agrupa mensagens com quebras apropriadas
                    consolidated_message = "\n\n".join(messages_to_send)
                    
                    logger.info(
                        f"Consolidando e enviando {len(messages_to_send)} mensagens",
                        phone=phone,
                        reason=send_reason,
                        total_length=len(consolidated_message)
                    )
                    
                    # Usa o novo serviço Evolution API v2
                    evolution = get_evolution_service()
                    
                    try:
                        result = await evolution.send_text_message(
                            phone=phone,
                            text=consolidated_message
                        )
                        
                        if result:
                            sent = True
                            # Limpa buffer após envio bem-sucedido
                            _message_buffers[phone].clear()
                            
                            logger.success(
                                "Buffer consolidado e enviado com sucesso",
                                phone=phone,
                                messages_count=len(messages_to_send),
                                consolidated_length=len(consolidated_message)
                            )
                        else:
                            logger.error(
                                "Falha ao enviar buffer consolidado",
                                phone=phone
                            )
                            
                    except Exception as send_error:
                        logger.error(
                            f"Erro ao enviar buffer: {str(send_error)}",
                            phone=phone
                        )
            
            # Agenda envio automático se configurado
            if auto_send and buffer and not sent and time_until_send_ms > 0:
                asyncio.create_task(
                    _schedule_auto_send(phone, time_until_send_ms, consolidate_after_ms, max_buffer_size)
                )
            
            return {
                "success": True,
                "buffer_size": len(buffer),
                "message_added": bool(message) and not force_send,
                "sent": sent,
                "consolidated_message": consolidated_message if sent else "",
                "time_until_send_ms": int(time_until_send_ms)
            }
            
    except Exception as e:
        logger.error(
            f"Erro no gerenciamento do buffer: {str(e)}",
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro no buffer: {str(e)}",
            "buffer_size": len(_message_buffers.get(phone, [])),
            "message_added": False,
            "sent": False,
            "consolidated_message": "",
            "time_until_send_ms": 0
        }


async def _schedule_auto_send(
    phone: str,
    wait_ms: int,
    consolidate_after_ms: int,
    max_buffer_size: int
):
    """
    Agenda envio automático do buffer após timeout
    
    Args:
        phone: Número do telefone
        wait_ms: Tempo de espera em milissegundos
        consolidate_after_ms: Configuração original de consolidação
        max_buffer_size: Tamanho máximo do buffer
    """
    try:
        # Aguarda o tempo especificado
        await asyncio.sleep(wait_ms / 1000)
        
        # Verifica se ainda há mensagens para enviar
        async with _buffer_locks[phone]:
            if _message_buffers[phone]:
                logger.debug(
                    f"Auto-send triggered para {phone}",
                    buffer_size=len(_message_buffers[phone])
                )
                
                # Chama buffer_message com force_send
                await buffer_message(
                    phone=phone,
                    message="",  # Sem nova mensagem
                    consolidate_after_ms=consolidate_after_ms,
                    max_buffer_size=max_buffer_size,
                    auto_send=False,  # Evita loop infinito
                    force_send=True
                )
                
    except Exception as e:
        logger.error(
            f"Erro no auto-send do buffer: {str(e)}",
            phone=phone
        )


@tool(show_result=True)
async def clear_buffer(phone: str) -> Dict[str, Any]:
    """
    Limpa o buffer de mensagens para um telefone específico
    
    Args:
        phone: Número de telefone para limpar o buffer
    
    Returns:
        Dict com resultado:
        - success: bool - Se o buffer foi limpo
        - messages_cleared: int - Número de mensagens removidas
    """
    try:
        async with _buffer_locks[phone]:
            messages_count = len(_message_buffers[phone])
            _message_buffers[phone].clear()
            
            logger.info(
                f"Buffer limpo",
                phone=phone,
                messages_cleared=messages_count
            )
            
            return {
                "success": True,
                "messages_cleared": messages_count
            }
            
    except Exception as e:
        logger.error(
            f"Erro ao limpar buffer: {str(e)}",
            phone=phone
        )
        
        return {
            "success": False,
            "messages_cleared": 0,
            "error": str(e)
        }


@tool(show_result=True)
async def get_buffer_status(phone: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtém status do buffer de mensagens
    
    Args:
        phone: Número de telefone específico (opcional, retorna todos se não fornecido)
    
    Returns:
        Dict com status do(s) buffer(s)
    """
    try:
        if phone:
            # Status de um telefone específico
            async with _buffer_locks[phone]:
                buffer = _message_buffers[phone]
                return {
                    "success": True,
                    "phone": phone,
                    "buffer_size": len(buffer),
                    "messages": [
                        {
                            "message": msg["message"][:50] + "..." if len(msg["message"]) > 50 else msg["message"],
                            "age_seconds": (datetime.now() - msg["timestamp"]).total_seconds(),
                            "sent": msg["sent"]
                        }
                        for msg in buffer
                    ]
                }
        else:
            # Status de todos os buffers
            all_status = {}
            for phone, buffer in _message_buffers.items():
                async with _buffer_locks[phone]:
                    all_status[phone] = {
                        "buffer_size": len(buffer),
                        "oldest_message_age": (
                            (datetime.now() - buffer[0]["timestamp"]).total_seconds()
                            if buffer else 0
                        )
                    }
            
            return {
                "success": True,
                "total_phones": len(all_status),
                "buffers": all_status
            }
            
    except Exception as e:
        logger.error(f"Erro ao obter status do buffer: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# Exports das tools
MessageBufferTool = buffer_message
ClearBufferTool = clear_buffer
GetBufferStatusTool = get_buffer_status

# Alias para compatibilidade
message_buffer = buffer_message