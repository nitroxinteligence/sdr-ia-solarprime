"""
WhatsApp Service V2
===================
Serviço WhatsApp otimizado com AGnO Framework e performance <30s
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
import asyncio
import os
import tempfile
import uuid
from pathlib import Path
import base64

from services.evolution_api import evolution_client
from agents.parallel_processor import parallel_processor
from services.cache_service import cache_service, invalidate_lead_cache
from utils.reasoning_metrics import log_reasoning, get_reasoning_report
from services.analytics_service import analytics_service

logger = logging.getLogger(__name__)


class WhatsAppServiceV2:
    """Serviço WhatsApp v2 com processamento paralelo e otimizado"""
    
    def __init__(self):
        self.sessions = {}  # Cache de sessões ativas
        self._initialized = False
        
    async def initialize(self):
        """Inicializa recursos necessários"""
        if not self._initialized:
            await parallel_processor.initialize()
            self._initialized = True
            logger.info("WhatsApp Service V2 inicializado")
        
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa webhook com performance otimizada"""
        start_time = datetime.now()
        
        # Garantir inicialização
        await self.initialize()
        
        try:
            event_type = payload.get("event")
            
            # Normalizar nome do evento
            if event_type:
                event_type = event_type.upper().replace(".", "_")
            
            if event_type == "MESSAGES_UPSERT":
                result = await self._handle_new_message(payload)
            elif event_type == "MESSAGES_UPDATE":
                result = await self._handle_message_update(payload)
            elif event_type == "CONNECTION_UPDATE":
                result = await self._handle_connection_update(payload)
            else:
                logger.warning(f"Evento não tratado: {event_type}")
                result = {"status": "ignored", "event": event_type}
                
            # Log tempo total
            total_time = (datetime.now() - start_time).total_seconds()
            result['webhook_processing_time'] = total_time
            
            return result
                
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def _handle_new_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa nova mensagem com otimizações"""
        data = payload.get("data", {})
        
        # Ignorar mensagens próprias
        if data.get("key", {}).get("fromMe", False):
            return {"status": "ignored", "reason": "own_message"}
        
        # Extrair informações
        message_info = self._extract_message_info(data)
        
        # Validar dados essenciais
        if not all([message_info["id"], message_info["from"]]):
            return {"status": "error", "reason": "missing_data"}
        
        # Ignorar grupos
        if "@g.us" in message_info["from"]:
            return {"status": "ignored", "reason": "group_message"}
        
        # Processar em paralelo com timeout agressivo
        try:
            # Marcar como lida e simular digitação em paralelo
            async_tasks = [
                evolution_client.mark_as_read(
                    message_id=message_info["id"],
                    phone=message_info["from"]
                ),
                evolution_client.send_typing(
                    phone=message_info["from"],
                    duration=1000  # Apenas 1 segundo
                )
            ]
            
            # Executar em paralelo sem esperar (fire and forget)
            asyncio.create_task(asyncio.gather(*async_tasks, return_exceptions=True))
            
            # Preparar dados para processamento
            message_data = {
                'phone': message_info["from"],
                'content': message_info["content"],
                'message_id': message_info["id"],
                'media_type': message_info["type"] if message_info["type"] != "text" else None,
                'media_data': None
            }
            
            # Processar mídia se houver (em paralelo)
            if message_info["type"] in ["image", "audio", "document"]:
                media_task = self._download_media_optimized(
                    message_info["id"],
                    message_info["type"]
                )
                
                # Iniciar download mas não esperar
                media_future = asyncio.create_task(media_task)
                
                # Dar 2 segundos para o download
                try:
                    message_data['media_data'] = await asyncio.wait_for(media_future, timeout=2.0)
                except asyncio.TimeoutError:
                    logger.warning("Timeout no download de mídia, processando sem ela")
                    
            # Processar mensagem com parallel processor
            response, metadata = await parallel_processor.process_message_optimized(message_data)
            
            # Enviar resposta imediatamente
            send_task = evolution_client.send_text_message(
                phone=message_info["from"],
                message=response
            )
            
            # Enviar reação se apropriado (em paralelo)
            if metadata.get("should_react") and metadata.get("reaction_emoji"):
                reaction_task = evolution_client.send_reaction(
                    phone=message_info["from"],
                    message_id=message_info["id"],
                    emoji=metadata["reaction_emoji"]
                )
                asyncio.create_task(reaction_task)
                
            # Aguardar envio da mensagem
            await send_task
            
            # Logar métricas (assíncrono)
            asyncio.create_task(self._log_metrics(message_info, metadata))
            
            return {
                "status": "success",
                "message_id": message_info["id"],
                "response_sent": True,
                "processing_time": metadata.get('total_processing_time', 0)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            
            # Enviar mensagem de erro
            try:
                await evolution_client.send_text_message(
                    phone=message_info["from"],
                    message="Desculpe, tive um probleminha. Já volto! 🔧"
                )
            except:
                pass
                
            return {"status": "error", "error": str(e)}
    
    def _extract_message_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai informações da mensagem (otimizado)"""
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
        
        # Processar tipos de mensagem (simplificado)
        if "conversation" in message:
            info["content"] = message["conversation"]
        elif "extendedTextMessage" in message:
            info["content"] = message["extendedTextMessage"]["text"]
        elif "imageMessage" in message:
            info["type"] = "image"
            info["content"] = message["imageMessage"].get("caption", "")
        elif "audioMessage" in message:
            info["type"] = "audio"
        elif "documentMessage" in message:
            info["type"] = "document"
            info["content"] = message["documentMessage"].get("caption", "")
            
        return info
    
    async def _download_media_optimized(self, message_id: str, media_type: str) -> Optional[bytes]:
        """Download otimizado de mídia com cache"""
        cache_key = f"media:{message_id}"
        
        # Tentar cache primeiro
        cached = await cache_service.get_or_compute(
            key=cache_key,
            compute_fn=lambda: evolution_client.download_media(message_id),
            ttl=3600  # 1 hora
        )
        
        return cached if cached else None
    
    async def _log_metrics(self, message_info: Dict[str, Any], metadata: Dict[str, Any]):
        """Loga métricas de forma assíncrona"""
        try:
            # Analytics
            await analytics_service.track_event(
                event_type="message_processed",
                event_data={
                    "message_type": message_info["type"],
                    "stage": metadata.get("stage"),
                    "response_time": metadata.get("total_processing_time", 0)
                },
                session_id=message_info.get("from")
            )
            
            # Reasoning metrics se houver
            if metadata.get("reasoning_data"):
                log_reasoning(
                    session_id=message_info["from"],
                    reasoning_data=metadata["reasoning_data"],
                    metadata={
                        "response_time": metadata.get("total_processing_time", 0),
                        "stage": metadata.get("stage", "UNKNOWN")
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro ao logar métricas: {e}")
    
    async def _handle_message_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa atualização de status (simplificado)"""
        data = payload.get("data", [])
        
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else []
            
        update_count = len(data)
        
        return {"status": "success", "updates": update_count}
    
    async def _handle_connection_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mudança de conexão"""
        data = payload.get("data", {})
        state = data.get("state")
        
        logger.info(f"Status da conexão WhatsApp: {state}")
        
        if state == "close":
            logger.error("WhatsApp desconectado! Verificar QR Code.")
            
        return {"status": "success", "connection_state": state}
    
    async def send_message(
        self, 
        phone: str, 
        message: str,
        quoted_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia mensagem diretamente"""
        try:
            result = await evolution_client.send_text_message(
                phone=phone,
                message=message,
                quoted_message_id=quoted_message_id
            )
            
            # Invalidar cache do lead
            await invalidate_lead_cache(phone)
            
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
        """Obtém métricas de reasoning"""
        return get_reasoning_report(phone)
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        return parallel_processor.get_performance_stats()


# Instância global
whatsapp_service_v2 = WhatsAppServiceV2()