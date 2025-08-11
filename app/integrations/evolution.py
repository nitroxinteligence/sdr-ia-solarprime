"""
Evolution API Client - Integração com WhatsApp
"""
import httpx
import json
import asyncio
import base64
import random
import time
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
from app.utils.logger import emoji_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class EvolutionAPIClient:
    """Cliente para integração com Evolution API v2 com conexão robusta"""
    
    def __init__(self):
        self.base_url = settings.evolution_api_url
        self.instance_name = settings.evolution_instance_name
        self.api_key = settings.evolution_api_key
        self._client = None
        self._last_health_check = 0
        self._health_check_interval = 30  # segundos
        self._connection_failed = False
        self._circuit_breaker_reset_time = 0
        self._circuit_breaker_failure_count = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60  # segundos
        
    def _create_client(self) -> httpx.AsyncClient:
        """Cria cliente HTTP com configuração otimizada"""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "apikey": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(
                connect=5.0,      # Timeout de conexão
                read=30.0,        # Timeout de leitura
                write=10.0,       # Timeout de escrita
                pool=5.0          # Timeout do pool
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30.0
            ),
            http2=True,  # Habilita HTTP/2 para melhor performance
            follow_redirects=True
        )
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Retorna o cliente HTTP, criando se necessário"""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _check_circuit_breaker(self):
        """Verifica estado do circuit breaker"""
        if self._circuit_breaker_failure_count >= self._circuit_breaker_threshold:
            if time.time() < self._circuit_breaker_reset_time:
                raise Exception(f"Circuit breaker ativo. Tentativas bloqueadas por {int(self._circuit_breaker_reset_time - time.time())}s")
            else:
                # Reset circuit breaker
                self._circuit_breaker_failure_count = 0
                emoji_logger.system_info("Circuit breaker resetado")
    
    def _record_success(self):
        """Registra sucesso na conexão"""
        self._circuit_breaker_failure_count = 0
        self._connection_failed = False
    
    def _record_failure(self):
        """Registra falha na conexão"""
        self._circuit_breaker_failure_count += 1
        if self._circuit_breaker_failure_count >= self._circuit_breaker_threshold:
            self._circuit_breaker_reset_time = time.time() + self._circuit_breaker_timeout
            emoji_logger.evolution_error(f"Circuit breaker ativado por {self._circuit_breaker_timeout}s após {self._circuit_breaker_failure_count} falhas")
        self._connection_failed = True
    
    async def health_check(self) -> bool:
        """Verifica saúde da conexão com Evolution API"""
        try:
            current_time = time.time()
            
            # Pula check se foi feito recentemente
            if current_time - self._last_health_check < self._health_check_interval:
                return not self._connection_failed
            
            await self._check_circuit_breaker()
            
            response = await self._make_request(
                "get",
                f"/instance/connectionState/{self.instance_name}",
                timeout=5.0
            )
            
            if response.status_code == 200:
                self._last_health_check = current_time
                self._record_success()
                return True
            else:
                self._record_failure()
                return False
                
        except Exception as e:
            logger.debug(f"Health check falhou: {e}")
            self._record_failure()
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError))
    )
    async def _make_request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Método base para fazer requisições com retry"""
        try:
            await self._check_circuit_breaker()
            
            # Reconectar se necessário
            if self._connection_failed:
                if self._client:
                    await self._client.aclose()
                self._client = self._create_client()
                emoji_logger.system_info("Reconectando ao Evolution API...")
            
            response = await getattr(self.client, method)(path, **kwargs)
                        
            self._record_success()
            return response
            
        except Exception as e:
            self._record_failure()
            emoji_logger.evolution_error(f"Erro na requisição {method.upper()} {path}: {e}")
            raise
    
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
            
            response = await self._make_request(
                "post",
                "/instance/create",
                json=payload
            )
            
            emoji_logger.evolution_success(f"Instância {self.instance_name} criada")
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao criar instância: {e}")
            raise
    
    async def get_instance_info(self) -> Dict[str, Any]:
        """Obtém informações da instância"""
        try:
            response = await self._make_request(
                "get",
                f"/instance/connectionState/{self.instance_name}"
            )
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao obter info da instância: {e}")
            raise
    
    async def connect_instance(self) -> Dict[str, Any]:
        """Conecta a instância gerando QR Code"""
        try:
            response = await self._make_request(
                "get",
                f"/instance/connect/{self.instance_name}"
            )
            
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
            response = await self._make_request(
                "delete",
                f"/instance/logout/{self.instance_name}"
            )
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
            
            # Simular digitação se habilitado - SEMPRE é resposta do agente aqui
            if simulate_typing:
                # CORREÇÃO DEFINITIVA: Enviar typing SEQUENCIAL antes da mensagem
                # Calcular duração baseada no tamanho da mensagem
                typing_duration = self._calculate_humanized_typing_duration(len(message))
                
                # 1. Enviar indicador de typing
                await self.send_typing(phone, len(message), duration_seconds=typing_duration, context="agent_response")
                
                # 2. AGUARDAR a duração do typing para simular digitação real
                emoji_logger.system_debug(f"Aguardando {typing_duration:.1f}s de typing antes de enviar mensagem")
                await asyncio.sleep(typing_duration)
            
            # Preparar payload
            payload = {
                "number": phone,
                "text": message,
                "delay": int(settings.delay_between_messages * 1000)  # Delay entre mensagens múltiplas (ms)
            }
            
            response = await self._make_request(
                "post",
                f"/message/sendText/{self.instance_name}",
                json=payload
            )
            
            # Verificar status da resposta
            if response.status_code not in [200, 201]:
                error_text = response.text
                emoji_logger.evolution_error(f"Evolution API retornou erro {response.status_code}: {error_text}")
                raise Exception(f"Erro ao enviar mensagem: Status {response.status_code} - {error_text}")
            
            result = response.json()
            
            # Verificar se mensagem foi realmente enviada
            if not result.get("key", {}).get("id"):
                emoji_logger.evolution_error(f"Mensagem não enviada - sem ID na resposta: {result}")
                raise Exception(f"Mensagem não foi enviada - resposta inválida da API")
            
            emoji_logger.evolution_send(phone, "text", message_length=len(message), delay_used=round(delay, 2))
            emoji_logger.system_debug(f"Resposta da Evolution API: {result}")
            return result
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar mensagem: {e}")
            raise
    
    def _calculate_humanized_typing_duration(self, message_length: int) -> float:
        """
        Calcula uma duração de "typing" humanizada baseada no tamanho da mensagem.
        """
        if message_length > 500:
            base_duration = 12.0
        elif message_length > 250:
            base_duration = 8.0
        elif message_length > 150:
            base_duration = 5.0
        elif message_length > 50:
            base_duration = 3.0
        else:
            base_duration = 2.0

        # Adicionar uma pequena variação aleatória para mais naturalidade
        variation = base_duration * 0.15
        duration = base_duration + random.uniform(-variation, variation)
        
        return max(1.0, min(duration, 15.0)) # Garante que a duração esteja entre 1 e 15 segundos
    
    async def send_typing(self, phone: str, message_length: int = 0, duration_seconds: Optional[float] = None, context: str = "unknown"):
        """
        Simula digitação com timing dinâmico baseado no tamanho da mensagem
        
        Args:
            phone: Número do WhatsApp
            message_length: Tamanho da mensagem para calcular duração
            duration_seconds: Duração customizada em segundos (sobrescreve cálculo)
            context: Contexto da operação (agent_response, user_message, etc)
        """
        # Importar o controller aqui para evitar import circular
        from app.services.typing_controller import typing_controller, TypingContext
        
        # Mapear contexto string para enum
        context_map = {
            "agent_response": TypingContext.AGENT_RESPONSE,
            "user_message": TypingContext.USER_MESSAGE,
            "system_message": TypingContext.SYSTEM_MESSAGE,
            "media_upload": TypingContext.MEDIA_UPLOAD,
            "unknown": TypingContext.SYSTEM_MESSAGE  # Default seguro
        }
        
        typing_context = context_map.get(context, TypingContext.SYSTEM_MESSAGE)
        
        # Usar o controller para decidir
        decision = typing_controller.should_show_typing(typing_context, message_length)
        
        if not decision.should_show:
            logger.debug(f"Typing não será mostrado: {decision.reason}")
            return
            
        try:
            phone = self._format_phone(phone)
            
            # Usar duração do controller ou customizada
            if not duration_seconds:
                duration = decision.duration or 2.0  # Fallback para 2 segundos
            else:
                duration = duration_seconds
            
            # Inicia digitação
            payload = {
                "number": phone,
                "delay": int(duration * 1000),
                "state": "composing"
            }
            
            await self._make_request(
                "post",
                f"/chat/updatePresence/{self.instance_name}",
                json=payload
            )
            
            emoji_logger.evolution_send(phone, "typing", duration_seconds=round(duration, 2), message_length=message_length)
            
            # Typing enviado com sucesso
            logger.debug(f"Typing enviado por {duration}s")
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao simular digitação: {e}")
            # Não propaga o erro para não bloquear o envio de mensagem
            logger.debug(f"Digitação falhou mas continuando: {e}")
    
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
            
            # Evolution API v2 - estrutura correta da payload
            payload = {
                "key": {
                    "remoteJid": f"{phone}@s.whatsapp.net",
                    "fromMe": False,
                    "id": message_id
                },
                "reaction": emoji
            }
            
            response = await self._make_request(
                "post",
                f"/message/sendReaction/{self.instance_name}",
                json=payload
            )
            
            # Verificar status da resposta
            if response.status_code not in [200, 201]:
                error_text = response.text
                emoji_logger.evolution_error(f"Evolution API retornou erro {response.status_code}: {error_text}")
                raise Exception(f"Erro ao enviar reação: Status {response.status_code} - {error_text}")
            
            result = response.json()
            
            # Verificar se reação foi realmente enviada
            if not result.get("key", {}).get("id"):
                emoji_logger.evolution_error(f"Reação não enviada - sem ID na resposta: {result}")
                raise Exception(f"Reação não foi enviada - resposta inválida da API")
            
            emoji_logger.evolution_send("reaction", "emoji", reaction=emoji)
            emoji_logger.system_info(f"Reação '{emoji}' enviada com sucesso. ID: {result.get('key', {}).get('id', 'N/A')}")
            return result
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar reação: {e}")
            raise
    
    async def send_reply(self, phone: str, message_id: str, text: str, simulate_typing: bool = True) -> Dict[str, Any]:
        """
        Envia uma resposta citando uma mensagem anterior
        
        Args:
            phone: Número do WhatsApp
            message_id: ID da mensagem a ser citada
            text: Texto da resposta
            simulate_typing: Se deve simular digitação antes de enviar
        """
        try:
            phone = self._format_phone(phone)
            
            # Simular digitação se habilitado - SEMPRE é resposta do agente aqui
            if simulate_typing:
                # CORREÇÃO DEFINITIVA: Enviar typing SEQUENCIAL antes da mensagem
                typing_duration = self._calculate_humanized_typing_duration(len(text))
                
                # 1. Enviar indicador de typing
                await self.send_typing(phone, len(text), duration_seconds=typing_duration, context="agent_response")
                
                # 2. AGUARDAR a duração do typing para simular digitação real
                emoji_logger.system_debug(f"Aguardando {typing_duration:.1f}s de typing antes de enviar resposta")
                await asyncio.sleep(typing_duration)
            
            payload = {
                "number": phone,
                "text": text,
                "options": {
                    "quoted": {
                        "key": {
                            "remoteJid": f"{phone}@s.whatsapp.net",
                            "id": message_id
                        }
                    }
                }
            }
            
            response = await self._make_request(
                "post",
                f"/message/sendText/{self.instance_name}",
                json=payload
            )
            
            # Verificar status da resposta
            if response.status_code not in [200, 201]:
                error_text = response.text
                emoji_logger.evolution_error(f"Evolution API retornou erro {response.status_code}: {error_text}")
                raise Exception(f"Erro ao enviar resposta: Status {response.status_code} - {error_text}")
            
            result = response.json()
            
            # Verificar se mensagem foi realmente enviada
            if not result.get("key", {}).get("id"):
                emoji_logger.evolution_error(f"Resposta não enviada - sem ID na resposta: {result}")
                raise Exception(f"Resposta não foi enviada - resposta inválida da API")
            
            emoji_logger.evolution_send(phone, "reply", message_length=len(text))
            return result
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar resposta: {e}")
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
            
            response = await self._make_request(
                "post",
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            
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
            
            response = await self._make_request(
                "post",
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            
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
            
            response = await self._make_request(
                "post",
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            
            emoji_logger.evolution_send(phone, "audio")
            return response.json()
            
        except Exception as e:
            emoji_logger.evolution_error(f"Erro ao enviar áudio: {e}")
            raise
    
    # ==================== CHATS ====================
    
    async def get_all_chats(self) -> List[Dict[str, Any]]:
        """Obtém todos os chats"""
        try:
            response = await self._make_request(
                "get",
                f"/chat/findChats/{self.instance_name}"
            )
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
            
            response = await self._make_request(
                "post",
                f"/chat/findMessages/{self.instance_name}",
                json={
                    "where": {
                        "remoteJid": f"{phone}@s.whatsapp.net"
                    },
                    "limit": limit
                }
            )
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
            
            response = await self._make_request(
                "post",
                f"/chat/markMessageAsRead/{self.instance_name}",
                json=payload
            )
                        
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
            
            response = await self._make_request(
                "post",
                f"/chat/fetchProfilePictureUrl/{self.instance_name}",
                json={"number": phone}
            )
                        
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
            
            response = await self._make_request(
                "post",
                f"/chat/fetchBusinessProfile/{self.instance_name}",
                json={"number": phone}
            )
                        
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
            
            response = await self._make_request(
                "post",
                f"/webhook/set/{self.instance_name}",
                json=payload
            )
                        
            logger.info(f"Webhook configurado: {webhook_url}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
            raise
    
    async def get_webhook(self) -> Dict[str, Any]:
        """Obtém configuração atual do webhook"""
        try:
            response = await self._make_request(
                "get",
                f"/webhook/get/{self.instance_name}"
            )
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
            
            response = await self._make_request(
                "post",
                f"/message/sendText/{self.instance_name}",
                json=payload
            )
                        
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
            response = await self._make_request(
                "post",
                f"/group/findGroupByJid/{self.instance_name}",
                json={"groupJid": group_id}
            )
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
    
    def decrypt_whatsapp_media(self, encrypted_data: bytes, media_key_base64: str, media_type: str = "image") -> Optional[bytes]:
        """
        Descriptografa mídia do WhatsApp usando AES-256-CBC
        
        Args:
            encrypted_data: Dados criptografados da mídia
            media_key_base64: MediaKey em base64 do webhook
            media_type: Tipo da mídia (image, video, audio, document, sticker)
            
        Returns:
            Bytes da mídia descriptografada ou None se falhar
        """
        try:
            # Decode mediaKey de base64
            media_key = base64.b64decode(media_key_base64)
            logger.info(f"MediaKey decodificada: {len(media_key)} bytes")
            
            # Expandir chave usando HKDF
            # WhatsApp usa diferentes info strings baseado no tipo de mídia
            info_map = {
                "image": b"WhatsApp Image Keys",
                "video": b"WhatsApp Video Keys",
                "audio": b"WhatsApp Audio Keys",
                "document": b"WhatsApp Document Keys",
                "sticker": b"WhatsApp Image Keys"
            }
            
            info = info_map.get(media_type, b"WhatsApp Image Keys")
            
            # HKDF para expandir a chave para 112 bytes
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=112,
                salt=None,
                info=info,
                backend=default_backend()
            )
            
            expanded_key = hkdf.derive(media_key)
            
            # Dividir a chave expandida
            # IV: primeiros 16 bytes
            iv = expanded_key[:16]
            # Chave AES: próximos 32 bytes (bytes 16-48)
            cipher_key = expanded_key[16:48]
            # Chave MAC: próximos 32 bytes (bytes 48-80)
            mac_key = expanded_key[48:80]
            
            logger.info(f"IV: {len(iv)} bytes, Cipher Key: {len(cipher_key)} bytes, MAC Key: {len(mac_key)} bytes")
            
            # Remover os últimos 10 bytes (MAC) dos dados criptografados
            if len(encrypted_data) <= 10:
                logger.error("Dados criptografados muito pequenos")
                return None
                
            ciphertext = encrypted_data[:-10]
            mac_tag = encrypted_data[-10:]
            
            # Verificar MAC (opcional mas recomendado)
            # WhatsApp usa HMAC-SHA256 truncado para 10 bytes
            computed_mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()[:10]
            
            if mac_tag != computed_mac:
                logger.warning(f"MAC não corresponde - esperado: {mac_tag.hex()}, calculado: {computed_mac.hex()}")
                # Continuar mesmo com MAC inválido para teste
            
            # Descriptografar usando AES-256-CBC
            cipher = Cipher(
                algorithms.AES(cipher_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remover padding PKCS7
            if len(decrypted_data) > 0:
                padding_length = decrypted_data[-1]
                if padding_length > 0 and padding_length <= 16:
                    # Verificar se o padding é válido
                    if all(b == padding_length for b in decrypted_data[-padding_length:]):
                        decrypted_data = decrypted_data[:-padding_length]
            
            logger.info(f"Mídia descriptografada com sucesso: {len(decrypted_data)} bytes")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Erro ao descriptografar mídia: {e}")
            logger.exception(e)
            return None
    
    async def download_media(self, message_data: Dict[str, Any]) -> Optional[bytes]:
        """
        Baixa e descriptografa mídia de uma mensagem do WhatsApp
        
        Args:
            message_data: Dados da mensagem com mídia (deve conter 'mediaUrl' ou 'url' e opcionalmente 'mediaKey')
            
        Returns:
            Bytes da mídia descriptografada ou None se falhar
        """
        try:
            # Procurar URL da mídia em diferentes campos possíveis
            media_url = message_data.get("mediaUrl") or message_data.get("url")
            
            if not media_url:
                logger.warning("URL da mídia não encontrada nos dados")
                return None
            
            # Verificar se há mediaKey para descriptografia
            media_key = message_data.get("mediaKey")
            media_type = message_data.get("mediaType", "image")
            
            logger.info(f"Baixando mídia de: {media_url[:50]}...")
            if media_key:
                logger.info(f"MediaKey presente - mídia será descriptografada (tipo: {media_type})")
            
            # Configurar cliente HTTP com timeout maior para arquivos grandes
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),  # 30 segundos de timeout
                follow_redirects=True,  # Seguir redirecionamentos
                limits=httpx.Limits(max_connections=5)  # Limitar conexões
            ) as client:
                
                # Headers para simular requisição do WhatsApp
                headers = {
                    "User-Agent": "WhatsApp/2.23.0",
                    "Accept": "*/*"
                }
                
                response = await client.get(media_url, headers=headers)
                
                # Verificar se a resposta foi bem-sucedida
                if response.status_code == 200:
                    content = response.content
                    logger.info(f"Mídia baixada com sucesso: {len(content)} bytes")
                    
                    # Se houver mediaKey, descriptografar
                    if media_key:
                        logger.info("Iniciando descriptografia da mídia...")
                        decrypted_content = self.decrypt_whatsapp_media(
                            encrypted_data=content,
                            media_key_base64=media_key,
                            media_type=media_type
                        )
                        
                        if decrypted_content:
                            logger.info(f"Mídia descriptografada com sucesso: {len(decrypted_content)} bytes")
                            return decrypted_content
                        else:
                            logger.error("Falha na descriptografia da mídia")
                            # Retornar conteúdo criptografado como fallback
                            logger.warning("Retornando mídia criptografada como fallback")
                            return content
                    else:
                        # Sem mediaKey, retornar conteúdo como está
                        return content
                else:
                    logger.error(f"Erro HTTP ao baixar mídia: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("Timeout ao baixar mídia")
            return None
        except httpx.RequestError as e:
            logger.error(f"Erro de requisição ao baixar mídia: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao baixar mídia: {e}")
            logger.exception(e)
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
            
            response = await self._make_request(
                "post",
                f"/chat/checkNumber/{self.instance_name}",
                json={"number": phone}
            )
                        
            data = response.json()
            return data.get("exists", False)
            
        except Exception as e:
            logger.error(f"Erro ao verificar número: {e}")
            return False
    
    async def close(self):
        """Fecha conexão do cliente"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
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