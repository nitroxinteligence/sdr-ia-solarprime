"""
Interface principal do Evolution API Service v2
Combina todos os serviços em uma API unificada e simples
"""

from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from loguru import logger

from .client import EvolutionClient
from .messages import MessageService
from .media import MediaService
from .webhooks import WebhookService
from .types import (
    MessageResponse,
    MediaType,
    WebhookEvent,
    InstanceStatus,
    InstanceState
)

from agente.core.config import AI_RESPONSE_DELAY_SECONDS, AI_TYPING_DELAY_MAX
import random


class EvolutionService:
    """
    Serviço principal do Evolution API v2
    
    Interface simplificada que combina todos os sub-serviços:
    - Mensagens de texto
    - Mídia (imagem, áudio, vídeo, documento)
    - Reações
    - Localização
    - Webhooks
    - Status da instância
    
    Características:
    - Design simples e modular
    - Sem complexidade desnecessária
    - Fácil de usar e manter
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        instance: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Inicializa o serviço Evolution API
        
        Args:
            base_url: URL base da API (usa config se não fornecido)
            api_key: Chave da API (usa config se não fornecido)
            instance: Nome da instância (usa config se não fornecido)
            timeout: Timeout padrão em segundos
        """
        # Cliente HTTP base
        self.client = EvolutionClient(
            base_url=base_url,
            api_key=api_key,
            instance=instance,
            timeout=timeout
        )
        
        # Serviços especializados
        self.messages = MessageService(self.client)
        self.media = MediaService(self.client)
        self.webhooks = WebhookService(self.client)
        
        logger.info(
            "Evolution Service v2 initialized",
            instance=self.client.instance,
            base_url=self.client.base_url
        )
    
    # === Métodos de Mensagem ===
    
    async def send_text_message(
        self,
        phone: str,
        text: str,
        delay: Optional[int] = None
    ) -> Optional[MessageResponse]:
        """
        Envia mensagem de texto com delay inteligente
        
        Args:
            phone: Número do destinatário
            text: Texto da mensagem
            delay: Delay customizado (calculado se None)
            
        Returns:
            MessageResponse ou None
        """
        # Calcula delay se não fornecido
        if delay is None:
            delay = self._calculate_typing_delay(text)
        
        return await self.messages.send_text(
            phone=phone,
            text=text,
            delay=delay
        )
    
    async def send_reaction(
        self,
        phone: str,
        message_id: str,
        reaction: str
    ) -> Optional[MessageResponse]:
        """
        Envia reação a uma mensagem
        
        Args:
            phone: Número do destinatário
            message_id: ID da mensagem
            reaction: Emoji da reação
            
        Returns:
            MessageResponse ou None
        """
        return await self.messages.send_reaction(
            phone=phone,
            message_id=message_id,
            reaction=reaction
        )
    
    async def send_location(
        self,
        phone: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None
    ) -> Optional[MessageResponse]:
        """
        Envia localização
        
        Args:
            phone: Número do destinatário
            latitude: Latitude
            longitude: Longitude
            name: Nome do local
            
        Returns:
            MessageResponse ou None
        """
        return await self.messages.send_location(
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            name=name
        )
    
    # === Métodos de Mídia ===
    
    async def send_media(
        self,
        phone: str,
        media_url: str,
        media_type: str,
        caption: Optional[str] = None
    ) -> Optional[MessageResponse]:
        """
        Envia mídia genérica
        
        Args:
            phone: Número do destinatário
            media_url: URL da mídia
            media_type: Tipo (image, audio, video, document)
            caption: Legenda (opcional)
            
        Returns:
            MessageResponse ou None
        """
        # Converte string para enum
        try:
            media_enum = MediaType(media_type)
        except ValueError:
            logger.error(f"Invalid media type: {media_type}")
            return None
        
        return await self.media.send_media(
            phone=phone,
            media_url=media_url,
            media_type=media_enum,
            caption=caption
        )
    
    async def send_image(
        self,
        phone: str,
        image_url: str,
        caption: Optional[str] = None
    ) -> Optional[MessageResponse]:
        """Envia imagem"""
        return await self.media.send_image(
            phone=phone,
            image_url=image_url,
            caption=caption
        )
    
    async def send_audio(
        self,
        phone: str,
        audio_url: str
    ) -> Optional[MessageResponse]:
        """Envia áudio"""
        return await self.media.send_audio(
            phone=phone,
            audio_url=audio_url
        )
    
    async def send_video(
        self,
        phone: str,
        video_url: str,
        caption: Optional[str] = None
    ) -> Optional[MessageResponse]:
        """Envia vídeo"""
        return await self.media.send_video(
            phone=phone,
            video_url=video_url,
            caption=caption
        )
    
    async def send_document(
        self,
        phone: str,
        document_url: str,
        caption: Optional[str] = None
    ) -> Optional[MessageResponse]:
        """Envia documento"""
        return await self.media.send_document(
            phone=phone,
            document_url=document_url,
            caption=caption
        )
    
    async def get_base64_from_media(self, message_id: str) -> Optional[str]:
        """
        Baixa mídia em base64
        
        Args:
            message_id: ID da mensagem
            
        Returns:
            String base64 ou None
        """
        return await self.media.get_base64_from_media(message_id)
    
    # === Métodos de Webhook e Status ===
    
    async def set_webhook(
        self,
        url: str,
        events: Optional[List[str]] = None
    ) -> bool:
        """
        Configura webhook
        
        Args:
            url: URL do webhook
            events: Lista de eventos (strings)
            
        Returns:
            True se configurado com sucesso
        """
        # Converte strings para enums
        event_enums = None
        if events:
            event_enums = []
            for event in events:
                try:
                    event_enums.append(WebhookEvent(event))
                except ValueError:
                    logger.warning(f"Unknown event: {event}")
        
        return await self.webhooks.set_webhook(url, event_enums)
    
    async def get_instance_status(self) -> Optional[Dict[str, Any]]:
        """
        Obtém status da instância
        
        Returns:
            Dict com state e error ou None
        """
        status = await self.webhooks.get_instance_status()
        if status:
            return {
                "state": status.state.value,
                "error": status.error
            }
        return None
    
    async def check_connection(self) -> bool:
        """
        Verifica se instância está conectada
        
        Returns:
            True se conectada
        """
        return await self.client.check_connection()
    
    async def connect_instance(self) -> bool:
        """
        Tenta conectar a instância
        
        Returns:
            True se conectou
        """
        return await self.webhooks.connect_instance()
    
    # === Métodos Utilitários ===
    
    def _calculate_typing_delay(self, text: str) -> int:
        """
        Calcula delay de digitação natural
        
        Args:
            text: Texto da mensagem
            
        Returns:
            Delay em segundos
        """
        # Base delay
        base_delay = AI_RESPONSE_DELAY_SECONDS
        
        # Adiciona baseado no tamanho
        words_count = len(text.split())
        typing_delay = base_delay + (words_count / 10)
        
        # Variação natural
        variation = typing_delay * 0.2
        typing_delay += random.uniform(-variation, variation)
        
        # Limites
        return max(2, min(int(typing_delay), AI_TYPING_DELAY_MAX))
    
    @staticmethod
    def parse_webhook_event(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa evento do webhook
        
        Args:
            data: Dados do webhook
            
        Returns:
            Dados processados
        """
        return WebhookService.parse_webhook_event(data)
    
    # === Context Manager ===
    
    async def close(self):
        """Fecha conexões"""
        await self.client.close()
    
    async def __aenter__(self):
        """Context manager entrada"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager saída"""
        await self.close()


# === Singleton Support ===

_evolution_service: Optional[EvolutionService] = None


def get_evolution_service() -> EvolutionService:
    """
    Retorna instância singleton do Evolution Service
    
    Returns:
        EvolutionService singleton
    """
    global _evolution_service
    if _evolution_service is None:
        _evolution_service = EvolutionService()
    return _evolution_service


@asynccontextmanager
async def evolution_service():
    """
    Context manager para Evolution Service
    
    Usage:
        async with evolution_service() as service:
            await service.send_text_message(...)
    """
    service = get_evolution_service()
    try:
        yield service
    finally:
        # Não fecha o singleton, apenas se fosse uma instância temporária
        pass