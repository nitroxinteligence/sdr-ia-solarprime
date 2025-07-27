"""
WhatsApp Service v2
===================
Serviço completo para integração com WhatsApp via Evolution API v2
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio
import os
import tempfile
import uuid
from pathlib import Path
import base64

from services.evolution_api import evolution_client
# from services.redis_service import redis_service
from services.redis_fallback import get_redis_fallback_service
from agents.sdr_agent import create_sdr_agent
from utils.reasoning_metrics import log_reasoning, get_reasoning_report
from services.analytics_service import analytics_service

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Serviço principal para integração com WhatsApp"""
    
    def __init__(self):
        self.agent = create_sdr_agent()
        self.sessions = {}  # Cache de sessões ativas
        self.redis_service = get_redis_fallback_service()
        
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa webhook recebido da Evolution API"""
        
        try:
            event_type = payload.get("event")
            
            # Normalizar nome do evento (Evolution API v2 usa minúsculas com ponto)
            if event_type:
                event_type = event_type.upper().replace(".", "_")
            
            if event_type == "MESSAGES_UPSERT":
                # Nova mensagem recebida
                return await self._handle_new_message(payload)
                
            elif event_type == "MESSAGES_UPDATE":
                # Atualização de status de mensagem
                return await self._handle_message_update(payload)
                
            elif event_type == "CONNECTION_UPDATE":
                # Mudança no status da conexão
                return await self._handle_connection_update(payload)
                
            else:
                logger.warning(f"Evento não tratado: {event_type}")
                return {"status": "ignored", "event": event_type}
                
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def _handle_new_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa nova mensagem"""
        
        data = payload.get("data", {})
        
        # Ignorar mensagens próprias
        if data.get("key", {}).get("fromMe", False):
            logger.debug("Ignorando mensagem própria")
            return {"status": "ignored", "reason": "own_message"}
        
        # Extrair informações da mensagem
        message_info = self._extract_message_info(data)
        
        # Validar dados essenciais
        if not all([message_info["id"], message_info["from"]]):
            logger.warning("Mensagem sem dados essenciais")
            return {"status": "error", "reason": "missing_data"}
        
        # Ignorar grupos (por enquanto)
        if "@g.us" in message_info["from"]:
            logger.debug("Ignorando mensagem de grupo")
            return {"status": "ignored", "reason": "group_message"}
        
        # Processar mensagem
        response = await self._process_message(message_info)
        
        return {
            "status": "success",
            "message_id": message_info["id"],
            "response_sent": bool(response)
        }
    
    def _extract_message_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai informações da mensagem"""
        
        message = data.get("message", {})
        
        info = {
            "id": data.get("key", {}).get("id"),
            "from": data.get("key", {}).get("remoteJid"),
            "timestamp": data.get("messageTimestamp"),
            "pushName": data.get("pushName", ""),
            "type": "text",
            "content": "",
            "media_data": None
        }
        
        # Processar diferentes tipos de mensagem
        if "conversation" in message:
            # Mensagem de texto simples
            info["content"] = message["conversation"]
            
        elif "extendedTextMessage" in message:
            # Mensagem de texto com metadados
            info["content"] = message["extendedTextMessage"]["text"]
            
        elif "imageMessage" in message:
            # Mensagem de imagem
            info["type"] = "image"
            info["content"] = message["imageMessage"].get("caption", "")
            info["media_data"] = {
                "mimetype": message["imageMessage"].get("mimetype", "image/jpeg")
            }
            
        elif "audioMessage" in message:
            # Mensagem de áudio
            info["type"] = "audio"
            info["media_data"] = {
                "duration": message["audioMessage"].get("seconds", 0),
                "mimetype": message["audioMessage"].get("mimetype", "audio/ogg")
            }
            
        elif "documentMessage" in message:
            # Documento
            info["type"] = "document"
            info["content"] = message["documentMessage"].get("caption", "")
            info["media_data"] = {
                "filename": message["documentMessage"].get("fileName", ""),
                "mimetype": message["documentMessage"].get("mimetype", "")
            }
            
        elif "pollCreationMessage" in message:
            # Enquete
            info["type"] = "poll"
            poll_data = message["pollCreationMessage"]
            info["content"] = poll_data.get("name", "")
            info["media_data"] = {
                "options": [opt.get("name", "") for opt in poll_data.get("options", [])]
            }
            
        elif "reactionMessage" in message:
            # Reação
            info["type"] = "reaction"
            reaction = message["reactionMessage"]
            info["content"] = reaction.get("text", "")
            info["media_data"] = {
                "message_id": reaction.get("key", {}).get("id"),
                "emoji": reaction.get("text", "")
            }
            
        elif "stickerMessage" in message:
            # Sticker
            info["type"] = "sticker"
            sticker = message["stickerMessage"]
            info["media_data"] = {
                "mimetype": sticker.get("mimetype", "image/webp"),
                "is_animated": sticker.get("isAnimated", False)
            }
            
        elif "locationMessage" in message:
            # Localização
            info["type"] = "location"
            location = message["locationMessage"]
            info["content"] = location.get("name", "")
            info["media_data"] = {
                "latitude": location.get("degreesLatitude"),
                "longitude": location.get("degreesLongitude"),
                "address": location.get("address", "")
            }
            
        return info
    
    async def _process_message(self, message_info: Dict[str, Any]) -> Optional[str]:
        """Processa mensagem com o agente"""
        
        start_time = datetime.now()
        phone = message_info["from"]
        
        try:
            # Verificar cache de conversa
            cached_state = await self.redis_service.get_conversation_state(phone)
            if cached_state:
                logger.debug(f"Estado da conversa recuperado do cache para {phone}")
            
            # Marcar como lida
            await evolution_client.mark_as_read(
                message_id=message_info["id"],
                phone=phone
            )
            
            # Simular digitação
            await evolution_client.send_typing(
                phone=phone,
                duration=3000
            )
            
            # Processar mídia se houver
            media_data = None
            if message_info["type"] in ["image", "audio", "document"]:
                media_data = await self._process_media(
                    message_info["id"],
                    message_info["type"],
                    message_info.get("media_data", {})
                )
            
            # Processar com agente
            response, metadata = await self.agent.process_message(
                message=message_info["content"],
                phone_number=message_info["from"],
                media_type=message_info["type"] if media_data else None,
                media_data=media_data
            )
            
            # Rastrear evento de analytics
            await analytics_service.track_event(
                event_type="message_processed",
                event_data={
                    "message_type": message_info["type"],
                    "stage": metadata.get("stage"),
                    "sentiment": metadata.get("sentiment"),
                    "response_time": (datetime.now() - start_time).total_seconds()
                },
                session_id=message_info.get("from")
            )
            
            # Logar métricas de reasoning se houver
            if metadata.get("reasoning_data"):
                response_time = (datetime.now() - start_time).total_seconds()
                log_reasoning(
                    session_id=message_info["from"],
                    reasoning_data=metadata["reasoning_data"],
                    metadata={
                        "response_time": response_time,
                        "stage": metadata.get("stage", "UNKNOWN"),
                        "sentiment": metadata.get("sentiment", "neutro")
                    }
                )
            
            # Enviar resposta
            if response:
                await evolution_client.send_text_message(
                    phone=message_info["from"],
                    message=response,
                    quoted_message_id=message_info["id"]
                )
                
                logger.info(f"Resposta enviada para {message_info['from']}")
                return response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            
            # Enviar mensagem de erro genérica
            error_message = (
                "Desculpe, encontrei um problema ao processar sua mensagem. "
                "Por favor, tente novamente em alguns instantes."
            )
            
            try:
                await evolution_client.send_text_message(
                    phone=message_info["from"],
                    message=error_message
                )
            except:
                pass
                
        return None
    
    async def _process_media(
        self, 
        message_id: str, 
        media_type: str,
        media_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Processa e baixa mídia com cache"""
        
        try:
            # Verificar cache primeiro
            cached_media = await self.redis_service.get_media(message_id)
            
            if cached_media:
                logger.debug(f"Mídia {message_id} recuperada do cache")
                media_data = cached_media
            else:
                # Baixar mídia
                media_data = await evolution_client.download_media(message_id)
                
                if not media_data:
                    logger.error(f"Falha ao baixar mídia {message_id}")
                    return None
                
                # Cachear mídia
                await self.redis_service.cache_media(message_id, media_data)
            
            # Salvar temporariamente
            extension = {
                "image": ".jpg",
                "audio": ".ogg",
                "document": ".pdf"
            }.get(media_type, ".bin")
            
            filename = f"{uuid.uuid4()}{extension}"
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            with open(filepath, "wb") as f:
                f.write(media_data)
            
            logger.info(f"Mídia salva temporariamente: {filepath}")
            
            # Retornar dados para o agente
            return {
                "path": filepath,
                "base64": base64.b64encode(media_data).decode() if media_type == "image" else None,
                "mimetype": media_info.get("mimetype", ""),
                "filename": media_info.get("filename", filename)
            }
                
        except Exception as e:
            logger.error(f"Erro ao processar mídia: {e}")
            return None
    
    async def _handle_message_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa atualização de status de mensagem"""
        
        data = payload.get("data", [])
        
        for update in data:
            message_id = update.get("key", {}).get("id")
            status = update.get("update", {}).get("status")
            
            if message_id and status:
                logger.debug(f"Status da mensagem {message_id}: {status}")
        
        return {"status": "success", "updates": len(data)}
    
    async def _handle_connection_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mudança de status da conexão"""
        
        data = payload.get("data", {})
        state = data.get("state")
        
        logger.info(f"Status da conexão WhatsApp: {state}")
        
        # Notificar se desconectado
        if state == "close":
            logger.error("WhatsApp desconectado! Verificar QR Code.")
            # TODO: Implementar notificação para admin
        
        return {"status": "success", "connection_state": state}
    
    async def send_message(
        self, 
        phone: str, 
        message: str,
        quoted_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia mensagem para número específico"""
        
        try:
            result = await evolution_client.send_text_message(
                phone=phone,
                message=message,
                quoted_message_id=quoted_message_id
            )
            
            return {
                "status": "success",
                "message_id": result.get("key", {}).get("id")
            }
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_reasoning_metrics(self, phone: str) -> Dict[str, Any]:
        """Obtém métricas de reasoning para um número"""
        
        return get_reasoning_report(phone)
    
    async def send_poll(
        self,
        phone: str,
        question: str,
        options: List[str],
        multiple_answers: bool = False
    ) -> Dict[str, Any]:
        """Envia enquete para número"""
        
        try:
            result = await evolution_client.send_poll(
                phone=phone,
                question=question,
                options=options,
                multiple_answers=multiple_answers
            )
            
            return {
                "status": "success",
                "message_id": result.get("key", {}).get("id")
            }
                
        except Exception as e:
            logger.error(f"Erro ao enviar enquete: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_reaction(
        self,
        phone: str,
        message_id: str,
        emoji: str = "👍"
    ) -> Dict[str, Any]:
        """Envia reação a mensagem"""
        
        try:
            result = await evolution_client.send_reaction(
                phone=phone,
                message_id=message_id,
                emoji=emoji
            )
            
            return {
                "status": "success",
                "reaction_sent": True
            }
                
        except Exception as e:
            logger.error(f"Erro ao enviar reação: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def handle_reaction(self, reaction_info: Dict[str, Any]):
        """Processa reação recebida"""
        
        emoji = reaction_info.get("content", "")
        from_phone = reaction_info.get("from", "")
        
        # Rastrear evento de analytics
        await analytics_service.track_event(
            event_type="reaction_received",
            event_data={
                "emoji": emoji,
                "from": from_phone
            },
            session_id=from_phone
        )
        
        # Por enquanto, apenas logar
        logger.info(f"Reação {emoji} recebida de {from_phone}")
    
    async def handle_poll_response(self, poll_info: Dict[str, Any]):
        """Processa resposta de enquete"""
        
        # TODO: Implementar lógica para processar respostas de enquete
        logger.info(f"Resposta de enquete recebida: {poll_info}")


# Instância global
whatsapp_service = WhatsAppService()