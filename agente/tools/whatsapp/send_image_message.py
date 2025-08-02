"""
SendImageMessageTool - Envia mensagem de imagem via WhatsApp
Versão atualizada para novo Evolution API Service v2
"""

from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from agente.services import get_evolution_service


@tool(show_result=True)
async def send_image_message(
    phone: str,
    image_url: str,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envia mensagem de imagem via WhatsApp
    
    Args:
        phone: Número de telefone do destinatário (formato: 5511999999999)
        image_url: URL da imagem (jpg, png, gif, webp, etc)
        caption: Legenda/texto opcional para acompanhar a imagem
    
    Returns:
        Dict com status do envio:
        - success: bool - Se a imagem foi enviada com sucesso
        - message_id: str - ID da mensagem no WhatsApp (se sucesso)
        - error: str - Mensagem de erro (se falhou)
        - phone: str - Número formatado usado no envio
        - media_type: str - Tipo de mídia enviada (sempre "image")
        - has_caption: bool - Se incluiu caption
    
    Examples:
        >>> await send_image_message("5511999999999", "https://example.com/photo.jpg")
        {"success": True, "message_id": "3EB0C767D097E9ECFE8E", "phone": "5511999999999", "media_type": "image", "has_caption": False}
        
        >>> await send_image_message("5511999999999", "https://example.com/diagram.png", "Veja este diagrama")
        {"success": True, "message_id": "3EB0C767D097E9ECFE8F", "phone": "5511999999999", "media_type": "image", "has_caption": True}
    """
    try:
        # Log da operação
        logger.info(
            "Enviando mensagem de imagem via WhatsApp",
            phone=phone[:4] + "****",
            image_url=image_url,
            has_caption=bool(caption)
        )
        
        # Validação básica da URL
        if not image_url or not image_url.startswith(('http://', 'https://')):
            logger.error(
                "URL de imagem inválida",
                image_url=image_url
            )
            return {
                "success": False,
                "error": "URL de imagem inválida - deve começar com http:// ou https://",
                "phone": phone,
                "media_type": "image",
                "has_caption": bool(caption)
            }
        
        # Obtém serviço Evolution API v2
        evolution = get_evolution_service()
        
        # Envia imagem usando o novo método específico
        result = await evolution.send_image(
            phone=phone,
            image_url=image_url,
            caption=caption
        )
        
        if result:
            logger.success(
                "Mensagem de imagem enviada com sucesso",
                phone=phone,
                message_id=result.key.id,
                has_caption=bool(caption)
            )
            
            return {
                "success": True,
                "message_id": result.key.id,
                "phone": phone,
                "media_type": "image",
                "has_caption": bool(caption)
            }
        else:
            logger.error(
                "Falha ao enviar mensagem de imagem",
                phone=phone
            )
            
            return {
                "success": False,
                "error": "Falha ao enviar imagem - verifique conexão da instância",
                "phone": phone,
                "media_type": "image",
                "has_caption": bool(caption)
            }
            
    except Exception as e:
        logger.error(
            f"Erro ao enviar mensagem de imagem: {str(e)}",
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro ao enviar imagem: {str(e)}",
            "phone": phone,
            "media_type": "image",
            "has_caption": bool(caption)
        }


# Export da tool
SendImageMessageTool = send_image_message