"""
Evolution API Service - Integração com WhatsApp via Evolution API
Gerencia envio de mensagens, mídia, reações e configurações da instância
"""

import asyncio
import httpx
import base64
from typing import Optional, Dict, Any, Union
from datetime import datetime
import random
import time

from agente.core.config import (
    EVOLUTION_API_URL,
    EVOLUTION_API_KEY,
    EVOLUTION_INSTANCE_NAME,
    AI_RESPONSE_DELAY_SECONDS,
    AI_TYPING_DELAY_MAX
)
from agente.core.logger import logger, log_api_request, log_api_response, setup_module_logger
from agente.utils.formatters import format_phone_number

# Logger específico para o módulo
module_logger = setup_module_logger("evolution_service")

# Request Queue - Controle inteligente para múltiplas conversas simultâneas
_request_queue = asyncio.Queue(maxsize=1000)  # Fila para 1000 mensagens
_queue_processor_task = None
_processing = False


class EvolutionAPIService:
    """
    Serviço para integração com Evolution API
    
    Gerencia:
    - Envio de mensagens de texto com simulação de digitação
    - Envio de mídia (imagens, documentos, áudio, vídeo)
    - Reações a mensagens
    - Envio de localização
    - Status da instância
    - Configuração de webhooks
    - Download de mídia em base64
    """
    
    def __init__(self):
        """Inicializa o serviço com configurações da Evolution API"""
        self.base_url = EVOLUTION_API_URL
        self.instance = EVOLUTION_INSTANCE_NAME
        self.headers = {
            'apikey': EVOLUTION_API_KEY,
            'Content-Type': 'application/json'
        }
        # Cliente HTTP com timeout de 30 segundos
        self.client = httpx.AsyncClient(timeout=30.0, headers=self.headers)
        
        module_logger.info(
            "Evolution API Service initialized",
            instance=self.instance,
            base_url=self.base_url,
            queue_info={
                "max_queue_size": _request_queue.maxsize,
                "current_queue_size": _request_queue.qsize(),
                "processor_running": _processing
            }
        )
    
    def _calculate_typing_delay(self, text: str) -> int:
        """
        Calcula delay de digitação baseado no tamanho da mensagem
        
        Args:
            text: Texto da mensagem
            
        Returns:
            Delay em segundos (entre 2 e 15)
        """
        # Base delay configurado
        base_delay = AI_RESPONSE_DELAY_SECONDS
        
        # Calcula delay adicional baseado no número de palavras
        words_count = len(text.split())
        
        # Aproximadamente 1 segundo a cada 10 palavras
        typing_delay = base_delay + (words_count / 10)
        
        # Adiciona variação aleatória de ±20% para parecer mais natural
        variation = typing_delay * 0.2
        typing_delay += random.uniform(-variation, variation)
        
        # Limita entre 2 e 15 segundos
        typing_delay = max(2, min(typing_delay, AI_TYPING_DELAY_MAX))
        
        return int(typing_delay)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 3,
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Faz requisição HTTP com retry e tratamento de erros
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            data: Dados para enviar
            retry_count: Número de tentativas
            timeout: Timeout em segundos
            
        Returns:
            Resposta da API ou None em caso de erro
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retry_count):
            try:
                start_time = datetime.now()
                
                # Log da requisição
                log_api_request(
                    service="evolution_api",
                    endpoint=endpoint,
                    method=method,
                    attempt=attempt + 1,
                    data_keys=list(data.keys()) if data else None
                )
                
                # Faz a requisição com timeout
                if method == "GET":
                    response = await self.client.get(url, timeout=timeout)
                elif method == "POST":
                    response = await self.client.post(url, json=data, timeout=timeout)
                elif method == "PUT":
                    response = await self.client.put(url, json=data, timeout=timeout)
                elif method == "DELETE":
                    response = await self.client.delete(url, timeout=timeout)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")
                
                # Calcula duração
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log da resposta
                log_api_response(
                    service="evolution_api",
                    endpoint=endpoint,
                    status=response.status_code,
                    duration=duration
                )
                
                # Verifica status
                if response.status_code >= 200 and response.status_code < 300:
                    return response.json() if response.text else {}
                
                # Log de erro para status não-2xx
                module_logger.warning(
                    f"Evolution API returned non-2xx status",
                    status=response.status_code,
                    response=response.text[:500]  # Primeiros 500 caracteres
                )
                
                # Se for 4xx, não tenta novamente
                if 400 <= response.status_code < 500:
                    return None
                
            except httpx.TimeoutException as e:
                module_logger.error(
                    f"Evolution API timeout after {timeout}s: {str(e)}",
                    endpoint=endpoint,
                    timeout=timeout,
                    attempt=attempt + 1
                )
            except httpx.HTTPError as e:
                module_logger.error(
                    f"Evolution API HTTP error: {type(e).__name__}: {str(e)}",
                    endpoint=endpoint,
                    error=str(e),
                    error_type=type(e).__name__,
                    attempt=attempt + 1
                )
            except Exception as e:
                module_logger.error(
                    f"Evolution API unexpected error: {type(e).__name__}: {str(e)}",
                    endpoint=endpoint,
                    error=str(e),
                    error_type=type(e).__name__,
                    attempt=attempt + 1
                )
            
            # Exponential backoff
            if attempt < retry_count - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                module_logger.info(f"Retrying in {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
        
        module_logger.error(
            f"Evolution API request failed after {retry_count} attempts",
            endpoint=endpoint
        )
        return None
    
    async def send_text_message(
        self,
        phone: str,
        text: str,
        delay: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Envia mensagem de texto com simulação de digitação
        
        Args:
            phone: Número do destinatário
            text: Texto da mensagem
            delay: Delay customizado em segundos (opcional)
            
        Returns:
            Resposta da API ou None em caso de erro
        """
        # Formata número de telefone
        formatted_phone = format_phone_number(phone)
        
        # Calcula delay se não foi fornecido
        if delay is None:
            delay = self._calculate_typing_delay(text)
        
        module_logger.info(
            f"Sending text message",
            phone=formatted_phone,
            text_length=len(text),
            delay=delay
        )
        
        # Dados da mensagem
        data = {
            "number": formatted_phone,
            "text": text,
            "delay": delay * 1000  # Evolution API espera em milissegundos
        }
        
        # Envia mensagem
        response = await self._make_request(
            method="POST",
            endpoint=f"/message/sendText/{self.instance}",
            data=data
        )
        
        if response:
            module_logger.info(
                f"Text message sent successfully",
                phone=formatted_phone,
                message_id=response.get("key", {}).get("id")
            )
        else:
            module_logger.error(
                f"Failed to send text message",
                phone=formatted_phone
            )
        
        return response
    
    async def send_media(
        self,
        phone: str,
        media_url: str,
        media_type: str,
        caption: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Envia mídia (imagem, documento, áudio, vídeo)
        
        Args:
            phone: Número do destinatário
            media_url: URL da mídia
            media_type: Tipo da mídia (image, document, audio, video)
            caption: Legenda da mídia (opcional)
            
        Returns:
            Resposta da API ou None em caso de erro
        """
        # Formata número de telefone
        formatted_phone = format_phone_number(phone)
        
        module_logger.info(
            f"Sending media",
            phone=formatted_phone,
            media_type=media_type,
            has_caption=bool(caption)
        )
        
        # Mapeia tipo de mídia para endpoint correto
        endpoint_map = {
            "image": "sendImage",
            "document": "sendDocument",
            "audio": "sendAudio",
            "video": "sendVideo"
        }
        
        endpoint_method = endpoint_map.get(media_type)
        if not endpoint_method:
            module_logger.error(f"Invalid media type: {media_type}")
            return None
        
        # Dados da mídia
        data = {
            "number": formatted_phone,
            "mediaUrl": media_url
        }
        
        # Adiciona caption se fornecida
        if caption:
            data["caption"] = caption
        
        # Envia mídia
        response = await self._make_request(
            method="POST",
            endpoint=f"/message/{endpoint_method}/{self.instance}",
            data=data
        )
        
        if response:
            module_logger.info(
                f"Media sent successfully",
                phone=formatted_phone,
                media_type=media_type,
                message_id=response.get("key", {}).get("id")
            )
        else:
            module_logger.error(
                f"Failed to send media",
                phone=formatted_phone,
                media_type=media_type
            )
        
        return response
    
    async def send_reaction(
        self,
        phone: str,
        message_key: str,
        reaction: str
    ) -> Optional[Dict[str, Any]]:
        """
        Envia reação a uma mensagem
        
        Args:
            phone: Número do destinatário
            message_key: ID da mensagem para reagir
            reaction: Emoji da reação
            
        Returns:
            Resposta da API ou None em caso de erro
        """
        # Formata número de telefone
        formatted_phone = format_phone_number(phone)
        
        module_logger.info(
            f"Sending reaction",
            phone=formatted_phone,
            message_key=message_key,
            reaction=reaction
        )
        
        # Dados da reação
        data = {
            "number": formatted_phone,
            "reaction": {
                "value": reaction,
                "msgId": message_key
            }
        }
        
        # Envia reação
        response = await self._make_request(
            method="POST",
            endpoint=f"/message/sendReaction/{self.instance}",
            data=data
        )
        
        if response:
            module_logger.info(
                f"Reaction sent successfully",
                phone=formatted_phone,
                reaction=reaction
            )
        else:
            module_logger.error(
                f"Failed to send reaction",
                phone=formatted_phone
            )
        
        return response
    
    async def send_location(
        self,
        phone: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Envia localização
        
        Args:
            phone: Número do destinatário
            latitude: Latitude
            longitude: Longitude
            name: Nome do local (opcional)
            
        Returns:
            Resposta da API ou None em caso de erro
        """
        # Formata número de telefone
        formatted_phone = format_phone_number(phone)
        
        module_logger.info(
            f"Sending location",
            phone=formatted_phone,
            latitude=latitude,
            longitude=longitude,
            location_name=name
        )
        
        # Dados da localização
        data = {
            "number": formatted_phone,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }
        
        # Adiciona nome se fornecido
        if name:
            data["location"]["name"] = name
        
        # Envia localização
        response = await self._make_request(
            method="POST",
            endpoint=f"/message/sendLocation/{self.instance}",
            data=data
        )
        
        if response:
            module_logger.info(
                f"Location sent successfully",
                phone=formatted_phone
            )
        else:
            module_logger.error(
                f"Failed to send location",
                phone=formatted_phone
            )
        
        return response
    
    async def get_instance_status(self) -> Optional[Dict[str, Any]]:
        """
        Obtém status da instância
        
        Returns:
            Status da instância ou None em caso de erro
        """
        module_logger.info("Getting instance status")
        
        response = await self._make_request(
            method="GET",
            endpoint=f"/instance/connectionState/{self.instance}"
        )
        
        if response:
            status = response.get("state", "unknown")
            module_logger.info(
                f"Instance status retrieved",
                status=status,
                instance=self.instance
            )
        else:
            module_logger.error("Failed to get instance status")
        
        return response
    
    async def set_webhook(self, webhook_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Configura webhook da instância
        
        Args:
            webhook_config: Configuração do webhook contendo:
                - url: URL do webhook
                - webhook_by_events: True para receber eventos separados
                - events: Lista de eventos para receber
                
        Returns:
            Resposta da API ou None em caso de erro
        """
        module_logger.info(
            f"Setting webhook",
            url=webhook_config.get("url"),
            events=webhook_config.get("events", [])
        )
        
        # Garante que webhook_by_events está habilitado
        webhook_config["webhook_by_events"] = True
        
        response = await self._make_request(
            method="POST",
            endpoint=f"/webhook/set/{self.instance}",
            data=webhook_config
        )
        
        if response:
            module_logger.info("Webhook configured successfully")
        else:
            module_logger.error("Failed to configure webhook")
        
        return response
    
    async def get_base64_from_media(self, message_key: str) -> Optional[str]:
        """
        Obtém mídia em base64
        
        Args:
            message_key: ID da mensagem com mídia
            
        Returns:
            String base64 da mídia ou None em caso de erro
        """
        module_logger.info(
            f"Getting media in base64",
            message_key=message_key
        )
        
        response = await self._make_request(
            method="GET",
            endpoint=f"/message/getBase64FromMediaMessage/{self.instance}?messageId={message_key}"
        )
        
        if response and "base64" in response:
            module_logger.info(
                f"Media retrieved successfully",
                message_key=message_key,
                size=len(response["base64"])
            )
            return response["base64"]
        else:
            module_logger.error(
                f"Failed to get media",
                message_key=message_key
            )
            return None
    
    async def close(self):
        """Fecha cliente HTTP"""
        await self.client.aclose()
        module_logger.info("Evolution API Service closed")
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    @staticmethod
    def get_queue_stats() -> Dict[str, Any]:
        """
        Retorna estatísticas da fila de requisições
        
        Returns:
            Dict com estatísticas da fila
        """
        return {
            "max_queue_size": _request_queue.maxsize,
            "current_queue_size": _request_queue.qsize(),
            "queue_available_slots": _request_queue.maxsize - _request_queue.qsize(),
            "queue_processor_running": _processing
        }


# Singleton instance
_evolution_service: Optional[EvolutionAPIService] = None


def get_evolution_service() -> EvolutionAPIService:
    """
    Retorna instância singleton do Evolution API Service
    
    Returns:
        Instância do serviço
    """
    global _evolution_service
    if _evolution_service is None:
        _evolution_service = EvolutionAPIService()
    return _evolution_service