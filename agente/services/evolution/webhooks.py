"""
Serviço de webhooks para Evolution API v2
Gerencia configuração de webhooks e processamento de eventos
"""

from typing import List, Optional, Dict, Any
from loguru import logger

from .client import EvolutionClient
from .types import WebhookConfig, WebhookEvent, InstanceStatus


class WebhookService:
    """
    Serviço para gerenciar webhooks
    
    Responsabilidades:
    - Configuração de webhook
    - Verificação de status da instância
    - Processamento de eventos (delegado ao usuário)
    """
    
    def __init__(self, client: EvolutionClient):
        """
        Inicializa serviço de webhooks
        
        Args:
            client: Cliente HTTP Evolution API
        """
        self.client = client
    
    async def set_webhook(
        self,
        url: str,
        events: Optional[List[WebhookEvent]] = None
    ) -> bool:
        """
        Configura webhook para receber eventos
        
        Args:
            url: URL do webhook
            events: Lista de eventos para receber (None = todos)
            
        Returns:
            True se configurado com sucesso
        """
        # Eventos padrão se não especificados
        if events is None:
            events = [
                WebhookEvent.CONNECTION_UPDATE,
                WebhookEvent.MESSAGES_UPSERT,
                WebhookEvent.MESSAGES_UPDATE
            ]
        
        # Cria configuração
        config = WebhookConfig(
            url=url,
            events=events,
            webhook_by_events=True
        )
        
        logger.info(
            f"Setting webhook",
            url=url,
            events=[e.value for e in events]
        )
        
        # Configura webhook
        response = await self.client.post(
            self.client.instance_endpoint("/webhook/set"),
            data=config.to_dict()
        )
        
        if response:
            logger.info(
                f"Webhook configured successfully",
                url=url,
                instance=self.client.instance
            )
            return True
        else:
            logger.error(
                f"Failed to configure webhook",
                url=url
            )
            return False
    
    async def get_instance_status(self) -> Optional[InstanceStatus]:
        """
        Obtém status da instância
        
        Returns:
            InstanceStatus ou None
        """
        logger.debug(f"Getting instance status")
        
        response = await self.client.get(
            self.client.instance_endpoint("/instance/connectionState")
        )
        
        if response:
            status = InstanceStatus.from_dict(response)
            logger.info(
                f"Instance status",
                state=status.state.value,
                error=status.error
            )
            return status
        else:
            logger.error(f"Failed to get instance status")
            return None
    
    async def connect_instance(self) -> bool:
        """
        Tenta conectar a instância
        
        Returns:
            True se conectou ou já estava conectada
        """
        # Verifica status atual
        status = await self.get_instance_status()
        if status and status.state == InstanceStatus.OPEN:
            logger.info(f"Instance already connected")
            return True
        
        logger.info(f"Attempting to connect instance")
        
        # Tenta conectar
        response = await self.client.get(
            self.client.instance_endpoint("/instance/instanceConnect"),
            timeout=60  # Conexão pode demorar
        )
        
        if response:
            logger.info(f"Instance connection initiated")
            return True
        else:
            logger.error(f"Failed to connect instance")
            return False
    
    @staticmethod
    def parse_webhook_event(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa evento do webhook para formato padronizado
        
        Args:
            data: Dados brutos do webhook
            
        Returns:
            Dados processados e padronizados
        """
        # Identifica tipo de evento
        event_type = data.get("event")
        
        # Processa mensagem recebida
        if event_type == WebhookEvent.MESSAGES_UPSERT.value:
            message = data.get("data", {})
            key = message.get("key", {})
            
            # Extrai informações relevantes
            return {
                "type": "message",
                "from": key.get("remoteJid", "").replace("@s.whatsapp.net", ""),
                "message_id": key.get("id"),
                "text": message.get("message", {}).get("conversation", ""),
                "media": _extract_media_info(message),
                "timestamp": message.get("messageTimestamp"),
                "from_me": key.get("fromMe", False)
            }
        
        # Processa atualização de conexão
        elif event_type == WebhookEvent.CONNECTION_UPDATE.value:
            state = data.get("data", {}).get("state", "close")
            return {
                "type": "connection",
                "state": state,
                "connected": state == "open"
            }
        
        # Processa atualização de mensagem (lida, etc)
        elif event_type == WebhookEvent.MESSAGES_UPDATE.value:
            update = data.get("data", {})
            return {
                "type": "message_update",
                "message_id": update.get("key", {}).get("id"),
                "status": update.get("update", {}).get("status"),
                "from": update.get("key", {}).get("remoteJid", "").replace("@s.whatsapp.net", "")
            }
        
        # Evento não reconhecido
        else:
            logger.warning(f"Unknown webhook event type: {event_type}")
            return {
                "type": "unknown",
                "event": event_type,
                "data": data
            }


def _extract_media_info(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extrai informações de mídia da mensagem
    
    Args:
        message: Mensagem do webhook
        
    Returns:
        Informações de mídia ou None
    """
    msg_content = message.get("message", {})
    
    # Verifica cada tipo de mídia
    if "imageMessage" in msg_content:
        return {
            "type": "image",
            "mimetype": msg_content["imageMessage"].get("mimetype"),
            "caption": msg_content["imageMessage"].get("caption")
        }
    elif "audioMessage" in msg_content:
        return {
            "type": "audio",
            "mimetype": msg_content["audioMessage"].get("mimetype"),
            "duration": msg_content["audioMessage"].get("seconds")
        }
    elif "videoMessage" in msg_content:
        return {
            "type": "video",
            "mimetype": msg_content["videoMessage"].get("mimetype"),
            "caption": msg_content["videoMessage"].get("caption")
        }
    elif "documentMessage" in msg_content:
        return {
            "type": "document",
            "mimetype": msg_content["documentMessage"].get("mimetype"),
            "filename": msg_content["documentMessage"].get("fileName")
        }
    
    return None