"""
Evolution API Client v2
=======================
Cliente completo para integração com Evolution API v2 (WhatsApp)
"""

import httpx
from typing import Optional, Dict, Any, List, Union
import logging
from datetime import datetime
import asyncio
import base64
from pathlib import Path
import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)


class EvolutionAPIClient:
    """Cliente para integração com Evolution API v2 - Singleton persistente"""
    
    def __init__(self):
        # Configurações base
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "solarprime")
        
        # Remover /manager da URL base se existir
        if self.base_url.endswith('/manager'):
            self.base_url = self.base_url[:-8]
        
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Cliente HTTP com retry e configurações otimizadas
        self.client = None
        self._client_lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Inicializa o cliente HTTP - deve ser chamado uma vez no startup"""
        if not self._initialized:
            async with self._client_lock:
                if not self._initialized:
                    logger.info(f"Inicializando Evolution API Client - URL: {self.base_url}")
                    self.client = httpx.AsyncClient(
                        base_url=self.base_url,
                        headers=self.headers,
                        timeout=httpx.Timeout(30.0, connect=10.0),
                        limits=httpx.Limits(
                            max_keepalive_connections=10,
                            max_connections=20,
                            keepalive_expiry=30.0
                        ),
                        follow_redirects=True
                    )
                    self._initialized = True
                    logger.info("✅ Evolution API Client inicializado com sucesso")
    
    async def _ensure_initialized(self):
        """Garante que o cliente foi inicializado"""
        if not self._initialized or self.client is None:
            await self.initialize()
    
    async def close(self):
        """Fecha o cliente explicitamente - apenas no shutdown"""
        if self.client:
            logger.info("Fechando Evolution API Client...")
            await self.client.aclose()
            self.client = None
            self._initialized = False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError)
    )
    async def check_connection(self) -> Dict[str, Any]:
        """Verifica conexão e status da instância"""
        await self._ensure_initialized()
        try:
            # Verificar status da instância
            response = await self.client.get(f"/instance/connectionState/{self.instance_name}")
            response.raise_for_status()
            
            data = response.json()
            
            # A resposta vem no formato: {"instance": {"instanceName": "...", "state": "..."}}
            if "instance" in data and isinstance(data["instance"], dict):
                state = data["instance"].get("state", "unknown")
                # Retornar no formato esperado pelos outros componentes
                result = {
                    "state": state,
                    "instanceName": data["instance"].get("instanceName", self.instance_name),
                    "raw_response": data
                }
            else:
                # Fallback para formato antigo
                result = data
                state = data.get("state", "unknown")
            
            logger.info(f"Status da instância {self.instance_name}: {state}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao verificar conexão: {e.response.status_code}")
            return {"state": "error", "error": str(e)}
        except Exception as e:
            logger.error(f"Erro ao verificar Evolution API: {e}")
            return {"state": "error", "error": str(e)}
    
    async def send_text_message(
        self,
        phone: str,
        message: str,
        quoted_message_id: Optional[str] = None,
        delay: Optional[int] = None
    ) -> Dict[str, Any]:
        """Envia mensagem de texto"""
        await self._ensure_initialized()
        
        # Formatar número
        formatted_phone = self._format_phone_number(phone)
        
        # Delay padrão de 2 segundos
        if delay is None:
            delay = int(os.getenv("AI_RESPONSE_DELAY_SECONDS", "2")) * 1000
        
        payload = {
            "number": formatted_phone,
            "text": message,
            "delay": delay
        }
        
        if quoted_message_id:
            payload["quoted"] = {"key": {"id": quoted_message_id}}
        
        try:
            response = await self.client.post(
                f"/message/sendText/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Mensagem enviada para {formatted_phone}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar mensagem: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            raise
    
    async def send_typing(
        self,
        phone: str,
        duration: int = 3000
    ):
        """Simula digitação"""
        await self._ensure_initialized()
        
        typing_enabled = os.getenv("TYPING_SIMULATION_ENABLED", "true").lower() == "true"
        if not typing_enabled:
            return
        
        formatted_phone = self._format_phone_number(phone)
        
        payload = {
            "number": formatted_phone,
            "delay": duration
        }
        
        try:
            await self.client.post(
                f"/chat/sendPresence/{self.instance_name}",
                json=payload
            )
            logger.debug(f"Simulando digitação para {formatted_phone}")
        except Exception as e:
            logger.warning(f"Erro ao simular digitação: {e}")
    
    async def send_media_message(
        self,
        phone: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia mídia (imagem, vídeo, documento)"""
        await self._ensure_initialized()
        
        formatted_phone = self._format_phone_number(phone)
        
        endpoints = {
            "image": "sendImage",
            "video": "sendVideo", 
            "document": "sendDocument",
            "audio": "sendAudio"
        }
        
        if media_type not in endpoints:
            raise ValueError(f"Tipo de mídia inválido: {media_type}")
        
        payload = {
            "number": formatted_phone,
            "mediaUrl": media_url
        }
        
        if caption and media_type in ["image", "video"]:
            payload["caption"] = caption
        
        try:
            response = await self.client.post(
                f"/message/{endpoints[media_type]}/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao enviar mídia: {e}")
            raise
    
    async def download_media(
        self,
        message_id: str
    ) -> Optional[bytes]:
        """Baixa mídia recebida"""
        await self._ensure_initialized()
        
        try:
            # Endpoint correto conforme documentação Evolution API v2
            response = await self.client.post(
                f"/chat/getBase64FromMediaMessage/{self.instance_name}",
                json={
                    "message": {
                        "key": {
                            "id": message_id
                        }
                    }
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if "base64" in data:
                return base64.b64decode(data["base64"])
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao baixar mídia: {e}")
            return None
    
    async def get_profile_picture(
        self,
        phone: str
    ) -> Optional[str]:
        """Obtém foto de perfil"""
        await self._ensure_initialized()
        
        formatted_phone = self._format_phone_number(phone)
        
        try:
            response = await self.client.post(
                f"/chat/fetchProfilePictureUrl/{self.instance_name}",
                json={"number": formatted_phone}
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("profilePictureUrl")
            
        except Exception as e:
            logger.warning(f"Erro ao obter foto de perfil: {e}")
            return None
    
    async def send_poll(
        self,
        phone: str,
        question: str,
        options: List[str],
        multiple_answers: bool = False
    ) -> Dict[str, Any]:
        """Envia enquete (poll)"""
        await self._ensure_initialized()
        
        formatted_phone = self._format_phone_number(phone)
        
        payload = {
            "number": formatted_phone,
            "name": question,
            "selectableCount": 0 if multiple_answers else 1,
            "values": options,
            "delay": int(os.getenv("AI_RESPONSE_DELAY_SECONDS", "2")) * 1000
        }
        
        try:
            response = await self.client.post(
                f"/message/sendPoll/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao enviar enquete: {e}")
            raise
    
    async def send_reaction(
        self,
        phone: str,
        message_id: str,
        emoji: str
    ) -> Dict[str, Any]:
        """Envia reação a uma mensagem"""
        await self._ensure_initialized()
        
        formatted_phone = self._format_phone_number(phone)
        
        # Formato correto conforme documentação Evolution API v2
        payload = {
            "key": {
                "remoteJid": formatted_phone,
                "fromMe": False,  # Mensagem do usuário
                "id": message_id
            },
            "reaction": emoji
        }
        
        try:
            response = await self.client.post(
                f"/message/sendReaction/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao enviar reação: {e}")
            raise
    
    async def send_sticker(
        self,
        phone: str,
        sticker_url: str
    ) -> Dict[str, Any]:
        """Envia sticker"""
        await self._ensure_initialized()
        
        formatted_phone = self._format_phone_number(phone)
        
        payload = {
            "number": formatted_phone,
            "stickerUrl": sticker_url,
            "delay": int(os.getenv("AI_RESPONSE_DELAY_SECONDS", "2")) * 1000
        }
        
        try:
            response = await self.client.post(
                f"/message/sendSticker/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao enviar sticker: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def create_webhook(
        self,
        webhook_url: str,
        events: List[str] = None,
        webhook_by_events: bool = False,
        webhook_base64: bool = False
    ) -> Dict[str, Any]:
        """Configura webhook com suporte completo à v2"""
        await self._ensure_initialized()
        
        if events is None:
            events = [
                "APPLICATION_STARTUP",
                "QRCODE_UPDATED",
                "MESSAGES_SET",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "MESSAGES_DELETE",
                "SEND_MESSAGE",
                "CONTACTS_SET",
                "CONTACTS_UPSERT",
                "CONTACTS_UPDATE",
                "PRESENCE_UPDATE",
                "CHATS_SET",
                "CHATS_UPSERT",
                "CHATS_UPDATE",
                "CHATS_DELETE",
                "GROUPS_UPSERT",
                "GROUP_UPDATE",
                "GROUP_PARTICIPANTS_UPDATE",
                "CONNECTION_UPDATE",
                "LABELS_EDIT",
                "LABELS_ASSOCIATION",
                "CALL",
                "TYPEBOT_START",
                "TYPEBOT_CHANGE_STATUS"
            ]
        
        # A API espera o payload dentro de uma propriedade 'webhook'
        payload = {
            "webhook": {
                "enabled": True,
                "url": webhook_url,
                "webhookByEvents": webhook_by_events,
                "webhookBase64": webhook_base64,
                "events": events
            }
        }
        
        logger.debug(f"Configurando webhook com payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = await self.client.post(
                f"/webhook/set/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Webhook configurado para instância {self.instance_name}: {webhook_url}")
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao configurar webhook: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
            raise
    
    def _format_phone_number(self, phone: str) -> str:
        """Formata número de telefone para o padrão do WhatsApp"""
        
        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se não tiver
        if not phone.startswith('55'):
            phone = '55' + phone
        
        # Adicionar sufixo do WhatsApp
        if '@' not in phone:
            phone = phone + '@s.whatsapp.net'
        
        return phone
    
    async def mark_as_read(
        self,
        message_id: str,
        phone: str
    ):
        """Marca mensagem como lida"""
        await self._ensure_initialized()
        
        formatted_phone = self._format_phone_number(phone)
        
        payload = {
            "number": formatted_phone,
            "messageId": message_id
        }
        
        try:
            await self.client.post(
                f"/chat/markMessageAsRead/{self.instance_name}",
                json=payload
            )
            logger.debug(f"Mensagem {message_id} marcada como lida")
        except Exception as e:
            logger.warning(f"Erro ao marcar como lida: {e}")
    
    # ===== MÉTODOS DE GERENCIAMENTO DE INSTÂNCIA =====
    
    async def get_instance_info(self) -> Dict[str, Any]:
        """Obtém informações da instância"""
        await self._ensure_initialized()
        try:
            response = await self.client.get(f"/instance/fetchInstances/{self.instance_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter info da instância: {e}")
            return {}
    
    async def create_instance(self) -> Dict[str, Any]:
        """Cria nova instância"""
        await self._ensure_initialized()
        payload = {
            "instanceName": self.instance_name,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True,
            "mobile": False,
            "businessId": ""
        }
        
        try:
            response = await self.client.post("/instance/create", json=payload)
            response.raise_for_status()
            logger.info(f"Instância {self.instance_name} criada com sucesso")
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao criar instância: {e}")
            raise
    
    async def get_qrcode(self) -> Optional[Dict[str, Any]]:
        """Obtém QR Code para conectar"""
        await self._ensure_initialized()
        try:
            response = await self.client.get(f"/instance/qrcode/{self.instance_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter QR Code: {e}")
            return None
    
    async def logout_instance(self) -> bool:
        """Desconecta instância do WhatsApp"""
        await self._ensure_initialized()
        try:
            response = await self.client.delete(f"/instance/logout/{self.instance_name}")
            response.raise_for_status()
            logger.info(f"Instância {self.instance_name} desconectada")
            return True
        except Exception as e:
            logger.error(f"Erro ao desconectar instância: {e}")
            return False
    
    async def delete_instance(self) -> bool:
        """Deleta instância completamente"""
        await self._ensure_initialized()
        try:
            response = await self.client.delete(f"/instance/delete/{self.instance_name}")
            response.raise_for_status()
            logger.info(f"Instância {self.instance_name} deletada")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar instância: {e}")
            return False
    
    async def restart_instance(self) -> bool:
        """Reinicia instância"""
        await self._ensure_initialized()
        try:
            response = await self.client.put(f"/instance/restart/{self.instance_name}")
            response.raise_for_status()
            logger.info(f"Instância {self.instance_name} reiniciada")
            return True
        except Exception as e:
            logger.error(f"Erro ao reiniciar instância: {e}")
            return False
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """Obtém configuração atual do webhook"""
        await self._ensure_initialized()
        try:
            response = await self.client.get(f"/webhook/find/{self.instance_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter info do webhook: {e}")
            return {}


# Instância global singleton
evolution_client = EvolutionAPIClient()