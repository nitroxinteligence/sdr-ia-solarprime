"""
Evolution API Client - Integração com WhatsApp
"""
import httpx
import json
import asyncio
import base64
import random
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
from app.utils.logger import emoji_logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

class EvolutionAPIClient:
    """Cliente para integração com Evolution API v2"""
    
    def __init__(self):
        self.base_url = settings.evolution_api_url
        self.instance_name = settings.evolution_instance_name
        self.api_key = settings.evolution_api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "apikey": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    # ==================== INSTÂNCIA ====================
    
    async def create_instance(self) -> Dict[str, Any]:
        """Cria uma nova instância no Evolution API"""
        try:
            payload = {
                "instanceName": self.instance_name,
                "token": self.api_key,
                "qrcode": True,
                "integration": "WEBWHOOKS",
                "webhook_url": f"{settings.webhook_base_url}/webhooks/evolution",
                "webhook_by_events": True,
                "webhook_base64": True
            }
            
            response = await self.client.post(
                "/instance/create",
                json=payload
            )
            response.raise_for_status()
            
            emoji_logger.evolution_success(f"Instância {self.instance_name} criada")
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao criar instância: {e}")
            raise
    
    async def get_instance_info(self) -> Dict[str, Any]:
        """Obtém informações da instância"""
        try:
            response = await self.client.get(
                f"/instance/connectionState/{self.instance_name}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao obter info da instância: {e}")
            raise
    
    async def connect_instance(self) -> Dict[str, Any]:
        """Conecta a instância gerando QR Code"""
        try:
            response = await self.client.get(
                f"/instance/connect/{self.instance_name}"
            )
            response.raise_for_status()
            
            data = response.json()
            if "qrcode" in data:
                emoji_logger.evolution_success("QR Code gerado")
                emoji_logger.system_debug(f"QR Code: {data['qrcode'][:50]}...")
            
            return data
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao conectar instância: {e}")
            raise
    
    async def disconnect_instance(self) -> Dict[str, Any]:
        """Desconecta a instância"""
        try:
            response = await self.client.delete(
                f"/instance/logout/{self.instance_name}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao desconectar instância: {e}")
            raise
    
    # ==================== MENSAGENS ====================
    
    def calculate_reading_time(self, text: str) -> float:
        """
        Calcula tempo de leitura baseado no tamanho do texto
        
        Args:
            text: Texto para calcular tempo de leitura
            
        Returns:
            Tempo em segundos
        """
        if not settings.simulate_reading_time:
            return 0
        
        # Calcular número de palavras
        word_count = len(text.split())
        
        # Calcular tempo baseado em WPM (palavras por minuto)
        reading_time = (word_count / settings.reading_speed_wpm) * 60
        
        # Adicionar variação humana
        if settings.response_time_variation > 0:
            variation = reading_time * settings.response_time_variation
            reading_time += random.uniform(-variation, variation)
        
        # Limitar entre 0.5 e 5 segundos
        return max(0.5, min(reading_time, 5.0))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def send_text_message(
        self,
        phone: str,
        message: str,
        delay: Optional[float] = None,
        simulate_typing: bool = True
    ) -> Dict[str, Any]:
        """
        Envia mensagem de texto com timing humanizado
        
        Args:
            phone: Número do WhatsApp (5511999999999)
            message: Texto da mensagem
            delay: Delay customizado em segundos antes de enviar
            simulate_typing: Se deve simular digitação
        """
        try:
            # Formatar número
            phone = self._format_phone(phone)
            
            # Calcular delay apropriado
            if delay is None:
                # Verificar complexidade da mensagem
                is_complex = len(message) > 300 or "?" in message
                
                if is_complex:
                    delay = settings.response_delay_thinking
                else:
                    # Delay aleatório entre min e max
                    delay = random.uniform(
                        settings.response_delay_min,
                        settings.response_delay_max
                    )
            
            # Aguardar delay inicial
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Simular digitação se habilitado
            if simulate_typing:
                await self.send_typing(phone, len(message))
            
            # Preparar payload
            payload = {
                "number": phone,
                "text": message,
                "delay": int(settings.delay_between_messages * 1000)  # Delay entre mensagens múltiplas (ms)
            }
            
            response = await self.client.post(
                f"/message/sendText/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            emoji_logger.evolution_send(phone, "text", message_length=len(message), delay_used=round(delay, 2))
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar mensagem: {e}")
            raise
    
    async def send_typing(self, phone: str, message_length: int = 0, custom_duration: Optional[float] = None):
        """
        Simula digitação com timing dinâmico baseado no tamanho da mensagem
        
        Args:
            phone: Número do WhatsApp
            message_length: Tamanho da mensagem para calcular duração
            custom_duration: Duração customizada (sobrescreve cálculo)
        """
        try:
            phone = self._format_phone(phone)
            
            # Calcular duração baseada no tamanho da mensagem
            if custom_duration:
                duration = custom_duration
            else:
                # Determinar duração base
                if message_length < 50:
                    duration = settings.typing_duration_short
                elif message_length < 200:
                    duration = settings.typing_duration_medium
                else:
                    duration = settings.typing_duration_long
                
                # Adicionar tempo baseado na velocidade de digitação
                if settings.typing_speed_chars_per_second > 0:
                    typing_time = message_length / settings.typing_speed_chars_per_second
                    # Usar o maior entre duração configurada e tempo calculado
                    duration = max(duration, typing_time)
                
                # Adicionar variação humana se habilitado
                if settings.response_time_variation > 0:
                    variation = duration * settings.response_time_variation
                    duration += random.uniform(-variation, variation)
                
                # Limitar duração
                duration = max(1.0, min(duration, 15.0))  # Entre 1 e 15 segundos
            
            # Inicia digitação
            payload = {
                "number": phone,
                "delay": int(duration * 1000),
                "state": "composing"
            }
            
            response = await self.client.post(
                f"/chat/updatePresence/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            # Aguarda duração
            await asyncio.sleep(duration)
            
            # Para digitação
            payload["state"] = "paused"
            await self.client.post(
                f"/chat/updatePresence/{self.instance_name}",
                json=payload
            )
            
            emoji_logger.evolution_send(phone, "typing", duration_seconds=round(duration, 2), message_length=message_length)
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao simular digitação: {e}")
    
    async def send_reaction(self, phone: str, message_id: str, emoji: str):
        """
        Envia reação a uma mensagem
        
        Args:
            phone: Número do WhatsApp
            message_id: ID da mensagem
            emoji: Emoji para reagir
        """
        try:
            phone = self._format_phone(phone)
            
            payload = {
                "reactionMessage": {
                    "key": {
                        "remoteJid": f"{phone}@s.whatsapp.net",
                        "id": message_id
                    },
                    "reaction": emoji
                }
            }
            
            response = await self.client.post(
                f"/message/sendReaction/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            emoji_logger.evolution_send("reaction", "emoji", reaction=emoji)
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar reação: {e}")
            raise
    
    async def send_image(
        self,
        phone: str,
        image_path: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia imagem
        
        Args:
            phone: Número do WhatsApp
            image_path: Caminho da imagem
            caption: Legenda opcional
        """
        try:
            phone = self._format_phone(phone)
            
            # Ler imagem e converter para base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            payload = {
                "number": phone,
                "mediatype": "image",
                "media": f"data:image/jpeg;base64,{image_data}"
            }
            
            if caption:
                payload["caption"] = caption
            
            response = await self.client.post(
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            emoji_logger.evolution_send(phone, "image")
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar imagem: {e}")
            raise
    
    async def send_document(
        self,
        phone: str,
        document_path: str,
        filename: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia documento (PDF, etc)
        
        Args:
            phone: Número do WhatsApp
            document_path: Caminho do documento
            filename: Nome do arquivo
            caption: Legenda opcional
        """
        try:
            phone = self._format_phone(phone)
            
            # Ler documento e converter para base64
            with open(document_path, "rb") as f:
                doc_data = base64.b64encode(f.read()).decode()
            
            payload = {
                "number": phone,
                "mediatype": "document",
                "media": f"data:application/pdf;base64,{doc_data}",
                "fileName": filename
            }
            
            if caption:
                payload["caption"] = caption
            
            response = await self.client.post(
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            emoji_logger.evolution_send(phone, "document")
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar documento: {e}")
            raise
    
    async def send_audio(
        self,
        phone: str,
        audio_path: str,
        as_voice_note: bool = True
    ) -> Dict[str, Any]:
        """
        Envia áudio
        
        Args:
            phone: Número do WhatsApp
            audio_path: Caminho do áudio
            as_voice_note: Se True, envia como nota de voz
        """
        try:
            phone = self._format_phone(phone)
            
            # Ler áudio e converter para base64
            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()
            
            payload = {
                "number": phone,
                "mediatype": "audio",
                "media": f"data:audio/mpeg;base64,{audio_data}",
                "ptt": as_voice_note  # Push to talk (nota de voz)
            }
            
            response = await self.client.post(
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            emoji_logger.evolution_send(phone, "audio")
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar áudio: {e}")
            raise
    
    # ==================== CHATS ====================
    
    async def get_all_chats(self) -> List[Dict[str, Any]]:
        """Obtém todos os chats"""
        try:
            response = await self.client.get(
                f"/chat/findChats/{self.instance_name}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao obter chats: {e}")
            raise
    
    async def get_messages(
        self,
        phone: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Obtém mensagens de um chat
        
        Args:
            phone: Número do WhatsApp
            limit: Limite de mensagens
        """
        try:
            phone = self._format_phone(phone)
            
            response = await self.client.post(
                f"/chat/findMessages/{self.instance_name}",
                json={
                    "where": {
                        "remoteJid": f"{phone}@s.whatsapp.net"
                    },
                    "limit": limit
                }
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao obter mensagens: {e}")
            raise
    
    async def mark_as_read(self, phone: str, message_id: str):
        """
        Marca mensagem como lida
        
        Args:
            phone: Número do WhatsApp
            message_id: ID da mensagem
        """
        try:
            phone = self._format_phone(phone)
            
            payload = {
                "read_messages": [
                    {
                        "remoteJid": f"{phone}@s.whatsapp.net",
                        "id": message_id
                    }
                ]
            }
            
            response = await self.client.post(
                f"/chat/markMessageAsRead/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            logger.debug(f"Mensagem {message_id} marcada como lida")
            
        except Exception as e:
            logger.error(f"Erro ao marcar como lida: {e}")
    
    # ==================== PERFIL ====================
    
    async def get_profile_picture(self, phone: str) -> Optional[str]:
        """
        Obtém foto de perfil
        
        Args:
            phone: Número do WhatsApp
            
        Returns:
            URL da foto ou None
        """
        try:
            phone = self._format_phone(phone)
            
            response = await self.client.post(
                f"/chat/fetchProfilePictureUrl/{self.instance_name}",
                json={"number": phone}
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("profilePictureUrl")
            
        except Exception as e:
            logger.error(f"Erro ao obter foto de perfil: {e}")
            return None
    
    async def get_business_profile(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Obtém perfil business
        
        Args:
            phone: Número do WhatsApp
            
        Returns:
            Dados do perfil ou None
        """
        try:
            phone = self._format_phone(phone)
            
            response = await self.client.post(
                f"/chat/fetchBusinessProfile/{self.instance_name}",
                json={"number": phone}
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao obter perfil business: {e}")
            return None
    
    # ==================== WEBHOOKS ====================
    
    async def setup_webhook(self, webhook_url: str):
        """
        Configura webhook para receber eventos
        
        Args:
            webhook_url: URL do webhook
        """
        try:
            payload = {
                "url": webhook_url,
                "webhookByEvents": True,
                "webhookBase64": True,
                "events": [
                    "APPLICATION_STARTUP",
                    "QRCODE_UPDATED",
                    "CONNECTION_UPDATE",
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
                    "GROUPS_UPDATE",
                    "GROUP_PARTICIPANTS_UPDATE",
                    "NEW_JWT_TOKEN"
                ]
            }
            
            response = await self.client.post(
                f"/webhook/set/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Webhook configurado: {webhook_url}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
            raise
    
    async def get_webhook(self) -> Dict[str, Any]:
        """Obtém configuração atual do webhook"""
        try:
            response = await self.client.get(
                f"/webhook/get/{self.instance_name}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao obter webhook: {e}")
            raise
    
    # ==================== GRUPOS ====================
    
    async def send_text_to_group(
        self,
        group_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Envia mensagem para grupo
        
        Args:
            group_id: ID do grupo
            message: Texto da mensagem
        """
        try:
            payload = {
                "number": group_id,
                "text": message
            }
            
            response = await self.client.post(
                f"/message/sendText/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Mensagem enviada para grupo {group_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para grupo: {e}")
            raise
    
    async def get_group_info(self, group_id: str) -> Dict[str, Any]:
        """
        Obtém informações do grupo
        
        Args:
            group_id: ID do grupo
        """
        try:
            response = await self.client.post(
                f"/group/findGroupByJid/{self.instance_name}",
                json={"groupJid": group_id}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao obter info do grupo: {e}")
            raise
    
    # ==================== UTILS ====================
    
    def _format_phone(self, phone: str) -> str:
        """
        Formata número de telefone
        
        Args:
            phone: Número em qualquer formato
            
        Returns:
            Número formatado (5511999999999)
        """
        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do país se não tiver
        if not phone.startswith('55'):
            phone = '55' + phone
        
        # Remove 9 dígito se for número fixo
        if len(phone) == 13 and phone[4] == '9':
            # Verifica se é celular (começa com 9)
            pass
        
        return phone
    
    async def download_media(self, message_data: Dict[str, Any]) -> Optional[bytes]:
        """
        Baixa mídia de uma mensagem
        
        Args:
            message_data: Dados da mensagem com mídia
            
        Returns:
            Bytes da mídia ou None
        """
        try:
            if "mediaUrl" not in message_data:
                return None
            
            async with httpx.AsyncClient() as client:
                response = await client.get(message_data["mediaUrl"])
                response.raise_for_status()
                return response.content
                
        except Exception as e:
            logger.error(f"Erro ao baixar mídia: {e}")
            return None
    
    async def check_number_exists(self, phone: str) -> bool:
        """
        Verifica se número existe no WhatsApp
        
        Args:
            phone: Número do WhatsApp
            
        Returns:
            True se existe, False caso contrário
        """
        try:
            phone = self._format_phone(phone)
            
            response = await self.client.post(
                f"/chat/checkNumber/{self.instance_name}",
                json={"number": phone}
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("exists", False)
            
        except Exception as e:
            logger.error(f"Erro ao verificar número: {e}")
            return False
    
    async def close(self):
        """Fecha conexão do cliente"""
        await self.client.aclose()
    
    async def connect(self):
        """Conecta e verifica a instância"""
        try:
            # Verifica se a instância existe e está conectada
            info = await self.get_instance_info()
            
            if info.get("state") != "open":
                logger.info("Instância não conectada, gerando QR Code...")
                await self.connect_instance()
            
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Testa a conexão com a Evolution API"""
        try:
            info = await self.get_instance_info()
            return info.get("state") == "open"
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False


# Singleton global
evolution_client = EvolutionAPIClient()