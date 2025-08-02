"""
Serviço de mídia para Evolution API v2
Gerencia envio e download de mídia (imagens, áudio, vídeo, documentos)
"""

from typing import Optional, Dict, Any
from loguru import logger

from .client import EvolutionClient
from .types import MediaMessage, MediaType, MessageResponse
from agente.utils.formatters import format_phone_number


class MediaService:
    """
    Serviço para gerenciar mídia
    
    Responsabilidades:
    - Envio de imagens
    - Envio de áudio
    - Envio de vídeo
    - Envio de documentos
    - Download de mídia em base64
    """
    
    def __init__(self, client: EvolutionClient):
        """
        Inicializa serviço de mídia
        
        Args:
            client: Cliente HTTP Evolution API
        """
        self.client = client
        
        # Mapeamento de tipo para endpoint
        self.endpoint_map = {
            MediaType.IMAGE: "sendImage",
            MediaType.AUDIO: "sendAudio",
            MediaType.VIDEO: "sendVideo",
            MediaType.DOCUMENT: "sendDocument"
        }
    
    async def send_media(
        self,
        phone: str,
        media_url: str,
        media_type: MediaType,
        caption: Optional[str] = None,
        delay: int = 0
    ) -> Optional[MessageResponse]:
        """
        Envia mídia genérica
        
        Args:
            phone: Número do destinatário
            media_url: URL da mídia
            media_type: Tipo da mídia
            caption: Legenda (opcional)
            delay: Delay em segundos
            
        Returns:
            MessageResponse ou None
        """
        # Formata número
        formatted_phone = format_phone_number(phone)
        
        # Verifica se tipo é válido
        if media_type not in self.endpoint_map:
            logger.error(
                f"Invalid media type",
                media_type=media_type,
                valid_types=list(self.endpoint_map.keys())
            )
            return None
        
        # Cria mensagem de mídia
        media_msg = MediaMessage(
            number=formatted_phone,
            mediaUrl=media_url,
            mediaType=media_type,
            caption=caption,
            delay=delay
        )
        
        logger.info(
            f"Sending {media_type.value}",
            phone=formatted_phone,
            media_url=media_url,
            has_caption=bool(caption),
            delay=delay
        )
        
        # Endpoint específico para tipo de mídia
        endpoint = self.endpoint_map[media_type]
        
        # Envia mídia
        response = await self.client.post(
            self.client.instance_endpoint(f"/message/{endpoint}"),
            data=media_msg.to_dict()
        )
        
        if response:
            msg_response = MessageResponse.from_dict(response)
            logger.info(
                f"{media_type.value} sent successfully",
                phone=formatted_phone,
                message_id=msg_response.key.id
            )
            return msg_response
        else:
            logger.error(
                f"Failed to send {media_type.value}",
                phone=formatted_phone
            )
            return None
    
    async def send_image(
        self,
        phone: str,
        image_url: str,
        caption: Optional[str] = None,
        delay: int = 0
    ) -> Optional[MessageResponse]:
        """
        Envia imagem
        
        Args:
            phone: Número do destinatário
            image_url: URL da imagem
            caption: Legenda (opcional)
            delay: Delay em segundos
            
        Returns:
            MessageResponse ou None
        """
        return await self.send_media(
            phone=phone,
            media_url=image_url,
            media_type=MediaType.IMAGE,
            caption=caption,
            delay=delay
        )
    
    async def send_audio(
        self,
        phone: str,
        audio_url: str,
        delay: int = 0
    ) -> Optional[MessageResponse]:
        """
        Envia áudio
        
        Args:
            phone: Número do destinatário
            audio_url: URL do áudio
            delay: Delay em segundos
            
        Returns:
            MessageResponse ou None
        """
        return await self.send_media(
            phone=phone,
            media_url=audio_url,
            media_type=MediaType.AUDIO,
            caption=None,  # Áudio não tem caption
            delay=delay
        )
    
    async def send_video(
        self,
        phone: str,
        video_url: str,
        caption: Optional[str] = None,
        delay: int = 0
    ) -> Optional[MessageResponse]:
        """
        Envia vídeo
        
        Args:
            phone: Número do destinatário
            video_url: URL do vídeo
            caption: Legenda (opcional)
            delay: Delay em segundos
            
        Returns:
            MessageResponse ou None
        """
        return await self.send_media(
            phone=phone,
            media_url=video_url,
            media_type=MediaType.VIDEO,
            caption=caption,
            delay=delay
        )
    
    async def send_document(
        self,
        phone: str,
        document_url: str,
        caption: Optional[str] = None,
        delay: int = 0
    ) -> Optional[MessageResponse]:
        """
        Envia documento
        
        Args:
            phone: Número do destinatário
            document_url: URL do documento
            caption: Legenda (opcional)
            delay: Delay em segundos
            
        Returns:
            MessageResponse ou None
        """
        return await self.send_media(
            phone=phone,
            media_url=document_url,
            media_type=MediaType.DOCUMENT,
            caption=caption,
            delay=delay
        )
    
    async def get_base64_from_media(self, message_id: str) -> Optional[str]:
        """
        Baixa mídia em base64
        
        Args:
            message_id: ID da mensagem com mídia
            
        Returns:
            String base64 ou None
        """
        logger.info(
            f"Downloading media as base64",
            message_id=message_id
        )
        
        # Faz download
        response = await self.client.get(
            self.client.instance_endpoint("/message/getBase64FromMediaMessage"),
            params={"messageId": message_id}
        )
        
        if response and "base64" in response:
            base64_data = response["base64"]
            logger.info(
                f"Media downloaded successfully",
                message_id=message_id,
                size=len(base64_data)
            )
            return base64_data
        else:
            logger.error(
                f"Failed to download media",
                message_id=message_id
            )
            return None