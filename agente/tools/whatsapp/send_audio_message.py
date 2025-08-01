"""
SendAudioMessageTool - Envia mensagem de áudio via WhatsApp usando Evolution API
"""

from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from ...services import get_evolution_service
from ...core.types import MediaType


@tool(show_result=True)
async def send_audio_message(
    audio_url: str,
    phone: Optional[str] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envia mensagem de áudio via WhatsApp.
    
    Args:
        audio_url: URL do arquivo de áudio (mp3, ogg, opus, etc)
        phone: Número de telefone do destinatário (opcional, obtido do contexto se não fornecido)
        caption: Legenda/texto opcional para acompanhar o áudio
    
    Returns:
        Dict com status do envio:
        - success: bool - Se o áudio foi enviado com sucesso
        - message_id: str - ID da mensagem no WhatsApp (se sucesso)
        - error: str - Mensagem de erro (se falhou)
        - phone: str - Número formatado usado no envio
        - media_type: str - Tipo de mídia enviada (sempre "audio")
        - has_caption: bool - Se incluiu caption
    
    Examples:
        >>> await send_audio_message("5511999999999", "https://example.com/audio.mp3")
        {"success": True, "message_id": "3EB0C767D097E9ECFE8C", "phone": "5511999999999", "media_type": "audio", "has_caption": False}
        
        >>> await send_audio_message("5511999999999", "https://example.com/voice.ogg", "Ouça este áudio importante")
        {"success": True, "message_id": "3EB0C767D097E9ECFE8D", "phone": "5511999999999", "media_type": "audio", "has_caption": True}
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
                    "media_type": "audio",
                    "has_caption": bool(caption)
                }
        
        # Log da operação
        logger.info(
            "Enviando mensagem de áudio via WhatsApp",
            phone=phone[:4] + "****",
            audio_url=audio_url,
            has_caption=bool(caption)
        )
        
        # Validação básica da URL
        if not audio_url or not audio_url.startswith(('http://', 'https://')):
            logger.error(
                "URL de áudio inválida",
                audio_url=audio_url
            )
            return {
                "success": False,
                "error": "URL de áudio inválida - deve começar com http:// ou https://",
                "phone": phone,
                "media_type": "audio",
                "has_caption": bool(caption)
            }
        
        # Obtém serviço Evolution API
        evolution = get_evolution_service()
        
        # Envia áudio
        result = await evolution.send_media(
            phone=phone,
            media_url=audio_url,
            media_type="audio",
            caption=caption
        )
        
        if result:
            # Extrai informações relevantes
            message_id = result.get("key", {}).get("id", "")
            
            logger.success(
                "Mensagem de áudio enviada com sucesso",
                phone=phone,
                message_id=message_id,
                has_caption=bool(caption)
            )
            
            return {
                "success": True,
                "message_id": message_id,
                "phone": phone,
                "media_type": "audio",
                "has_caption": bool(caption)
            }
        else:
            logger.error(
                "Falha ao enviar mensagem de áudio",
                phone=phone
            )
            
            return {
                "success": False,
                "error": "Falha ao enviar áudio - resposta vazia da API",
                "phone": phone,
                "media_type": "audio",
                "has_caption": bool(caption)
            }
            
    except Exception as e:
        logger.error(
            f"Erro ao enviar mensagem de áudio: {str(e)}",
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro ao enviar áudio: {str(e)}",
            "phone": phone,
            "media_type": "audio",
            "has_caption": bool(caption)
        }


# Export da tool
SendAudioMessageTool = send_audio_message