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
from services.message_buffer_service import message_buffer_service
from agents.sdr_agent import create_sdr_agent
from utils.reasoning_metrics import log_reasoning, get_reasoning_report
from services.analytics_service import analytics_service
from agents.tools.message_chunker_tool import chunk_message_standalone
from utils.message_formatter import format_message_for_whatsapp
from services.follow_up_service import follow_up_service
from services.kommo_follow_up_service import kommo_follow_up_service
from config.messages import get_error_message, get_special_message, SPECIAL_SITUATIONS

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
        
        # Verificar se deve adicionar ao buffer ou processar imediatamente
        phone = message_info["from"]
        
        # Log detalhado da mensagem recebida
        logger.info(f"📥 Nova mensagem de {phone}: '{message_info['content'][:50]}...' (tipo: {message_info['type']}, id: {message_info['id']})")
        
        # Preparar dados da mensagem para o buffer
        buffer_message_data = {
            "id": message_info["id"],
            "content": message_info["content"],
            "type": message_info["type"],
            "media_data": message_info["media_data"],
            "timestamp": datetime.fromtimestamp(message_info["timestamp"]).isoformat() if message_info["timestamp"] else datetime.now().isoformat(),
            "pushName": message_info["pushName"]
        }
        
        # Callback para processar mensagens consolidadas
        async def process_buffered_callback(messages: List[Dict[str, Any]]):
            logger.info(f"📋 Callback do buffer acionado para {phone} com {len(messages)} mensagens")
            await self._process_buffered_messages(phone, messages)
        
        # Obter status do buffer antes de adicionar
        buffer_status = await message_buffer_service.get_buffer_status(phone)
        logger.debug(f"📊 Status do buffer antes: {buffer_status}")
        
        # Tentar adicionar ao buffer
        added_to_buffer = await message_buffer_service.add_message(
            phone=phone,
            message_data=buffer_message_data,
            process_callback=process_buffered_callback
        )
        
        if added_to_buffer:
            # Obter status atualizado do buffer
            buffer_status_after = await message_buffer_service.get_buffer_status(phone)
            logger.info(f"✅ Mensagem {message_info['id']} adicionada ao buffer para {phone} - Status: {buffer_status_after}")
            return {
                "status": "buffered",
                "message_id": message_info["id"],
                "buffer_active": True,
                "buffer_size": buffer_status_after.get("buffer_size", 0)
            }
        else:
            # Processar imediatamente se buffer desabilitado ou em processamento
            logger.warning(f"⚠️ Buffer não disponível para {phone} - processando mensagem imediatamente")
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
                "mimetype": message["imageMessage"].get("mimetype", "image/jpeg"),
                "url": message["imageMessage"].get("url", ""),
                "directPath": message["imageMessage"].get("directPath", ""),
                "mediaKey": message["imageMessage"].get("mediaKey", "")
            }
            
        elif "audioMessage" in message:
            # Mensagem de áudio
            info["type"] = "audio"
            info["media_data"] = {
                "duration": message["audioMessage"].get("seconds", 0),
                "mimetype": message["audioMessage"].get("mimetype", "audio/ogg"),
                "url": message["audioMessage"].get("url", ""),
                "directPath": message["audioMessage"].get("directPath", ""),
                "mediaKey": message["audioMessage"].get("mediaKey", "")
            }
            
        elif "documentMessage" in message:
            # Documento
            info["type"] = "document"
            info["content"] = message["documentMessage"].get("caption", "")
            info["media_data"] = {
                "filename": message["documentMessage"].get("fileName", ""),
                "mimetype": message["documentMessage"].get("mimetype", ""),
                "url": message["documentMessage"].get("url", ""),
                "directPath": message["documentMessage"].get("directPath", ""),
                "mediaKey": message["documentMessage"].get("mediaKey", "")
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
            # Verificar se é comando especial #CLEAR
            if message_info["content"].strip().upper() == "#CLEAR":
                return await self._handle_clear_command(phone, message_info)
            
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
                media_data=media_data,
                message_id=message_info["id"]  # Passar message_id
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
            
            # Enviar reação se apropriado
            if metadata.get("should_react") and metadata.get("reaction_emoji"):
                try:
                    await evolution_client.send_reaction(
                        phone=message_info["from"],
                        message_id=message_info["id"],
                        emoji=metadata["reaction_emoji"]
                    )
                    logger.info(f"Reação {metadata['reaction_emoji']} enviada para {message_info['from']}")
                except Exception as e:
                    logger.warning(f"Erro ao enviar reação: {e}")
            
            # Verificar se deve usar chunking
            if metadata.get('use_chunking', True) and len(response) > 100:
                # Enviar resposta em chunks
                await self._send_chunked_messages(
                    phone=message_info["from"],
                    message=response,
                    metadata=metadata
                )
            else:
                # Formatar mensagem antes de enviar
                formatted_response = format_message_for_whatsapp(response)
                
                # Enviar resposta única
                await evolution_client.send_text_message(
                    phone=message_info["from"],
                    message=formatted_response
                    # Removido quoted_message_id para não marcar mensagens individuais
                )
                
            logger.info(f"Resposta enviada para {message_info['from']}")
            
            # Criar follow-up automático se habilitado
            if metadata.get('stage') not in ['SCHEDULED', 'NOT_INTERESTED']:
                # Usar follow-up do Kommo se disponível
                if metadata.get('lead_id') and kommo_follow_up_service:
                    try:
                        # Agendar follow-up via Kommo
                        kommo_success = await kommo_follow_up_service.schedule_follow_up(
                            lead_id=metadata.get('lead_id'),
                            follow_up_number=1  # Primeiro follow-up
                        )
                        
                        if kommo_success:
                            logger.info(f"Follow-up Kommo agendado para lead {metadata.get('lead_id')}")
                    except Exception as e:
                        logger.error(f"Erro ao agendar follow-up Kommo: {e}")
                
                # Também criar follow-up local (fallback)
                follow_up_result = await follow_up_service.create_follow_up_after_message(
                    phone_number=message_info["from"],
                    lead_id=metadata.get('lead_id'),
                    message_sent=response,
                    stage=metadata.get('stage')
                )
                
                if follow_up_result['status'] == 'success':
                    logger.info(f"Follow-up agendado para {message_info['from']} em {follow_up_result['minutes_until']} minutos")
                elif follow_up_result['status'] == 'error':
                    logger.warning(f"Erro ao criar follow-up: {follow_up_result.get('message')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            
            # Enviar mensagem de erro mais humanizada
            error_message = get_error_message("ERRO_TECNICO")
            
            try:
                await evolution_client.send_text_message(
                    phone=message_info["from"],
                    message=error_message
                )
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem de erro para {message_info['from']}: {e}")
                
        return None
    
    async def _send_chunked_messages(
        self,
        phone: str,
        message: str,
        metadata: Dict[str, Any]
    ):
        """
        Envia mensagem dividida em chunks para criar conversação mais natural
        """
        try:
            # Obter configuração de chunking
            chunking_enabled = os.getenv("MESSAGE_CHUNKING_ENABLED", "true").lower() == "true"
            
            if not chunking_enabled:
                # Se desabilitado, enviar mensagem completa
                await evolution_client.send_text_message(phone=phone, message=message)
                return
            
            # Analisar estágio e contexto para chunking
            stage = metadata.get('stage', 'INITIAL_CONTACT')
            
            # Configurar parâmetros baseados no estágio e configurações do .env
            join_probability = float(os.getenv("CHUNK_JOIN_PROBABILITY", "0.6"))
            max_chunk_words = int(os.getenv("CHUNK_MAX_WORDS", "30"))
            max_chars_per_chunk = int(os.getenv("CHUNK_MAX_CHARS", "1200"))
            
            # Ajustar baseado no estágio
            if stage == 'INITIAL_CONTACT':
                join_probability = max(0.3, join_probability - 0.2)  # Mais chunks na saudação
                max_chunk_words = min(20, max_chunk_words)
            elif stage in ['QUALIFICATION', 'DISCOVERY']:
                join_probability = min(0.8, join_probability + 0.1)  # Menos chunks em explicações
                max_chunk_words = min(35, max_chunk_words + 5)
            
            # Dividir mensagem em chunks
            chunk_result = await chunk_message_standalone(
                message=message,
                join_probability=join_probability,
                max_chunk_words=max_chunk_words,
                max_chars_per_chunk=max_chars_per_chunk
            )
            
            chunks = chunk_result.get("chunks", [message])
            delays = chunk_result.get("delays", [2000] * len(chunks))
            
            logger.info(f"Enviando mensagem em {len(chunks)} chunks para {phone}")
            
            # Enviar cada chunk com delay e typing simulation
            for i, (chunk, delay) in enumerate(zip(chunks, delays)):
                # Simular digitação (exceto para o primeiro chunk)
                if i > 0:
                    typing_duration = min(delay, 3000)  # Máximo 3s de typing
                    await evolution_client.send_typing(
                        phone=phone,
                        duration=typing_duration
                    )
                    # Aguardar um pouco antes de enviar
                    await asyncio.sleep(typing_duration / 1000)
                
                # Formatar chunk antes de enviar (garantir formatação correta)
                formatted_chunk = format_message_for_whatsapp(chunk)
                
                # Enviar chunk
                await evolution_client.send_text_message(
                    phone=phone,
                    message=formatted_chunk,
                    delay=100 if i > 0 else 0  # Delay mínimo entre mensagens
                )
                
                # Pequena pausa entre chunks (se não for o último)
                if i < len(chunks) - 1:
                    pause = min(delay / 2, 1000) / 1000  # Metade do delay ou 1s
                    await asyncio.sleep(pause)
            
            # Rastrear evento
            await analytics_service.track_event(
                event_type="chunked_message_sent",
                event_data={
                    "chunk_count": len(chunks),
                    "total_length": len(message),
                    "stage": stage,
                    "total_time": chunk_result.get("total_reading_time", 0)
                },
                session_id=phone
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagens em chunks: {e}")
            # Fallback: enviar mensagem completa
            await evolution_client.send_text_message(phone=phone, message=message)
    
    async def _process_media(
        self, 
        message_id: str, 
        media_type: str,
        media_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Processa e baixa mídia com cache e múltiplas estratégias"""
        
        try:
            logger.info(f"📦 Processando mídia {media_type}: {message_id}")
            logger.debug(f"🔍 Media info recebida: {media_info}")
            
            # Verificar cache primeiro
            cached_media = await self.redis_service.get_media(message_id)
            
            if cached_media:
                logger.debug(f"📦 Mídia {message_id} recuperada do cache")
                media_data = cached_media
            else:
                # Extrair URL da mídia para fallback
                media_url = media_info.get("url", "")
                if not media_url and media_info.get("directPath"):
                    # Construir URL se temos directPath
                    media_url = f"https://mmg.whatsapp.net{media_info['directPath']}"
                
                # Baixar mídia com fallback para URL direta
                media_data = await evolution_client.download_media(
                    message_id=message_id,
                    media_url=media_url
                )
                
                if not media_data:
                    logger.error(f"❌ Falha ao baixar mídia {message_id} após todas as tentativas")
                    return None
                
                # IMPORTANTE: Validar que é conteúdo real
                logger.info(f"✅ Mídia baixada: {len(media_data)} bytes")
                
                if len(media_data) < 100:
                    logger.error(f"⚠️ Conteúdo suspeito (muito pequeno): {len(media_data)} bytes")
                    logger.warning("💡 Tentando download novamente ou considere usar fallback")
                    # Aqui poderia implementar retry ou estratégia alternativa
                    return None
                
                # Cachear mídia
                await self.redis_service.cache_media(message_id, media_data)
                logger.success(f"✅ Mídia {message_id} cacheada com sucesso ({len(media_data)} bytes)")
            
            # Determinar extensão baseada no mimetype ou tipo
            mimetype = media_info.get("mimetype", "")
            extension = ".bin"  # default
            
            if "pdf" in mimetype:
                extension = ".pdf"
            elif "image" in mimetype or media_type == "image":
                if "png" in mimetype:
                    extension = ".png"
                elif "gif" in mimetype:
                    extension = ".gif"
                else:
                    extension = ".jpg"
            elif "audio" in mimetype or media_type == "audio":
                extension = ".ogg"
            elif media_type == "document":
                # Tentar extrair extensão do filename
                original_filename = media_info.get("filename", "")
                if original_filename and "." in original_filename:
                    extension = os.path.splitext(original_filename)[1]
                else:
                    extension = ".pdf"  # Assumir PDF para documentos
            
            filename = f"{uuid.uuid4()}{extension}"
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Salvar arquivo com conteúdo completo
            with open(filepath, "wb") as f:
                f.write(media_data)
            
            logger.info(f"💾 Mídia salva: {filepath} ({len(media_data)} bytes)")
            
            # Verificar se o arquivo foi salvo corretamente
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                logger.success(f"✅ Arquivo verificado: {os.path.getsize(filepath)} bytes")
            else:
                logger.error(f"❌ Erro ao salvar arquivo ou arquivo vazio")
            
            # Retornar dados completos para o agente
            return {
                "path": filepath,
                "base64": base64.b64encode(media_data).decode(),  # Sempre incluir base64
                "mimetype": media_info.get("mimetype", ""),
                "filename": media_info.get("filename", filename),
                "content": media_data,  # Conteúdo binário direto
                "size": len(media_data),  # Tamanho para verificação
                "original_filename": media_info.get("filename", "")  # Nome original
            }
                
        except Exception as e:
            logger.error(f"Erro ao processar mídia: {e}")
            return None
    
    async def _handle_message_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa atualização de status de mensagem"""
        
        data = payload.get("data", [])
        
        # Garantir que data é uma lista
        if not isinstance(data, list):
            if isinstance(data, dict):
                data = [data]
            else:
                logger.warning(f"Formato inesperado de data em message_update: {type(data)}")
                return {"status": "error", "reason": "invalid_data_format"}
        
        update_count = 0
        for update in data:
            if isinstance(update, dict):
                message_id = update.get("key", {}).get("id")
                status = update.get("update", {}).get("status")
                
                if message_id and status:
                    logger.debug(f"Status da mensagem {message_id}: {status}")
                    update_count += 1
        
        return {"status": "success", "updates": update_count}
    
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
            # Formatar mensagem antes de enviar
            formatted_message = format_message_for_whatsapp(message)
            
            result = await evolution_client.send_text_message(
                phone=phone,
                message=formatted_message,
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
    
    async def _process_buffered_messages(self, phone: str, messages: List[Dict[str, Any]]):
        """Processa múltiplas mensagens que foram bufferizadas"""
        
        start_time = datetime.now()
        
        try:
            logger.info(f"🔄 Iniciando processamento de {len(messages)} mensagens bufferizadas de {phone}")
            
            # Log detalhado de cada mensagem no buffer
            for i, msg in enumerate(messages):
                logger.debug(f"  📝 Mensagem {i+1}/{len(messages)}: '{msg.get('content', '')[:50]}...' (id: {msg.get('id')})")
            
            # Consolidar informações das mensagens
            consolidated_content = []
            media_items = []
            first_message_id = None
            last_message_id = None
            
            for i, msg in enumerate(messages):
                if i == 0:
                    first_message_id = msg.get("id")
                last_message_id = msg.get("id")
                
                # Adicionar conteúdo textual
                if msg.get("type") == "text" and msg.get("content"):
                    consolidated_content.append(msg["content"])
                
                # Coletar mídia
                if msg.get("type") in ["image", "audio", "document"] and msg.get("media_data"):
                    media_items.append({
                        "type": msg["type"],
                        "content": msg.get("content", ""),
                        "media_data": msg["media_data"],
                        "message_id": msg["id"]
                    })
            
            # Criar mensagem consolidada
            final_content = " ".join(consolidated_content)
            logger.info(f"📄 Conteúdo consolidado ({len(final_content)} chars): '{final_content[:100]}...'")
            
            # Se não houver conteúdo de texto mas houver mídia
            if not final_content and media_items:
                if len(media_items) == 1:
                    media_type_name = {
                        "image": "uma imagem",
                        "audio": "um áudio",
                        "document": "um documento"
                    }.get(media_items[0]['type'], "um arquivo")
                    final_content = f"Recebi {media_type_name}!"
                else:
                    final_content = f"Recebi {len(media_items)} arquivos!"
            
            # Criar message_info consolidado
            consolidated_message_info = {
                "id": last_message_id,  # Usar ID da última mensagem
                "from": phone,
                "timestamp": int(datetime.now().timestamp()),
                "pushName": messages[0].get("pushName", "") if messages else "",
                "type": "text",  # Usar "text" ao invés de "buffered" para evitar problema de constraint
                "content": final_content,
                "media_data": None,
                "buffered_messages": messages,  # Manter referência às mensagens originais
                "buffered_count": len(messages),
                "has_media": len(media_items) > 0,
                "media_items": media_items
            }
            
            # Marcar primeira mensagem como lida
            if first_message_id:
                await evolution_client.mark_as_read(
                    message_id=first_message_id,
                    phone=phone
                )
            
            # Simular digitação por tempo proporcional ao conteúdo
            typing_duration = min(3000 + (len(final_content) * 20), 8000)  # 3-8 segundos
            await evolution_client.send_typing(
                phone=phone,
                duration=typing_duration
            )
            
            # Processar com o agente usando o conteúdo consolidado
            logger.info(f"🤖 Enviando conteúdo consolidado para o agente processar...")
            
            # Determinar tipo de mídia correto
            actual_media_type = None
            actual_media_data = None
            if media_items:
                # Pegar o tipo real da primeira mídia
                actual_media_type = media_items[0]['type']
                actual_media_data = media_items[0]['media_data']
                logger.info(f"📸 Mídia detectada no buffer: tipo={actual_media_type}")
            
            response, metadata = await self.agent.process_message(
                message=final_content,
                phone_number=phone,
                media_type=actual_media_type,
                media_data=actual_media_data,
                message_id=last_message_id
            )
            
            # Adicionar metadados específicos do buffer
            metadata["is_buffered"] = True
            metadata["buffered_count"] = len(messages)
            metadata["buffer_time_span"] = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"💬 Agente gerou resposta ({len(response)} chars): '{response[:100]}...'")
            
            # Rastrear evento
            await analytics_service.track_event(
                event_type="buffered_messages_processed",
                event_data={
                    "message_count": len(messages),
                    "has_media": len(media_items) > 0,
                    "media_count": len(media_items),
                    "consolidated_length": len(final_content),
                    "processing_time": metadata["buffer_time_span"],
                    "stage": metadata.get("stage")
                },
                session_id=phone
            )
            
            # Enviar resposta
            if response:
                # Usar chunking para mensagens bufferizadas também
                if metadata.get('use_chunking', True) and len(response) > 100:
                    await self._send_chunked_messages(
                        phone=phone,
                        message=response,
                        metadata=metadata
                    )
                else:
                    # Formatar mensagem antes de enviar
                    formatted_response = format_message_for_whatsapp(response)
                    
                    await evolution_client.send_text_message(
                        phone=phone,
                        message=formatted_response
                        # Não citar mensagem específica quando for buffer
                    )
                
                logger.info(f"Resposta enviada para {len(messages)} mensagens bufferizadas de {phone}")
                
                # Criar follow-up automático se habilitado
                if metadata.get('stage') not in ['SCHEDULED', 'NOT_INTERESTED']:
                    follow_up_result = await follow_up_service.create_follow_up_after_message(
                        phone_number=phone,
                        lead_id=metadata.get('lead_id'),
                        message_sent=response,
                        stage=metadata.get('stage')
                    )
                    
                    if follow_up_result['status'] == 'success':
                        logger.info(f"Follow-up agendado para {phone} em {follow_up_result['minutes_until']} minutos")
                    elif follow_up_result['status'] == 'error':
                        logger.warning(f"Erro ao criar follow-up: {follow_up_result.get('message')}")
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagens bufferizadas: {e}", exc_info=True)
            
            # Enviar mensagem de erro
            name = messages[0].get("pushName", "") if messages else ""
            error_message = get_special_message("multiplas_mensagens", name)
            
            try:
                await evolution_client.send_text_message(
                    phone=phone,
                    message=error_message
                )
            except Exception as send_error:
                logger.error(f"Erro ao enviar mensagem de erro: {send_error}")
    
    async def _handle_clear_command(self, phone: str, message_info: Dict[str, Any]) -> str:
        """Processa comando #CLEAR para limpar histórico da conversa"""
        
        try:
            logger.info(f"Comando #CLEAR recebido de {phone}")
            
            # Importar repositórios necessários
            from repositories.message_repository import message_repository
            from repositories.conversation_repository import conversation_repository
            from repositories.lead_repository import lead_repository
            
            # 1. Limpar mensagens do banco de dados
            conversation = await conversation_repository.get_conversation_by_phone(phone)
            if conversation:
                await message_repository.delete_conversation_messages(conversation.id)
                logger.info(f"Mensagens deletadas para conversa {conversation.id}")
                
                # 2. Resetar conversa
                await conversation_repository.reset_conversation(conversation.id)
                logger.info(f"Conversa {conversation.id} resetada")
            
            # 3. Limpar cache Redis
            await self.redis_service.clear_conversation_state(phone)
            logger.info(f"Cache Redis limpo para {phone}")
            
            # 4. Limpar memória do agente
            # O agente será recriado na próxima mensagem
            if phone in self.sessions:
                del self.sessions[phone]
                logger.info(f"Sessão do agente removida para {phone}")
            
            # 5. Limpar lead se existir
            lead = await lead_repository.get_lead_by_phone(phone)
            if lead:
                await lead_repository.delete_lead(lead.id)
                logger.info(f"Lead {lead.id} deletado")
            
            # 6. Limpar follow-ups pendentes
            await follow_up_service.cancel_all_follow_ups_for_phone(phone)
            logger.info(f"Follow-ups cancelados para {phone}")
            
            # 7. Limpar buffer de mensagens se houver
            await message_buffer_service.clear_buffer(phone)
            logger.info(f"Buffer de mensagens limpo para {phone}")
            
            # Enviar confirmação
            # Tentar obter o nome do lead
            from repositories.lead_repository import lead_repository
            lead = await lead_repository.get_lead_by_phone(phone)
            name = lead.name if lead and lead.name else message_info.get("pushName", "")
            
            confirmation_message = get_special_message("comando_clear", name)
            
            await evolution_client.send_text_message(
                phone=phone,
                message=confirmation_message
            )
            
            logger.info(f"Comando #CLEAR executado com sucesso para {phone}")
            return confirmation_message
            
        except Exception as e:
            logger.error(f"Erro ao executar comando #CLEAR: {e}", exc_info=True)
            
            # Usar mensagem de erro genérica mais amigável
            error_message = get_error_message("ERRO_TECNICO")
            
            await evolution_client.send_text_message(
                phone=phone,
                message=error_message
            )
            
            return error_message


# Instância global
whatsapp_service = WhatsAppService()