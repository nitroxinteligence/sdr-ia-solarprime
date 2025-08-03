"""
Webhooks API - Recebe eventos da Evolution API
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import base64
import json
from datetime import datetime
from loguru import logger
from app.utils.logger import emoji_logger
from app.integrations.supabase_client import supabase_client
from app.integrations.redis_client import redis_client
from app.integrations.evolution import evolution_client
from app.agents.agentic_sdr import get_agentic_sdr  # Importa o AGENTIC SDR
from app.config import settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Instância global do AGENTIC SDR
agentic_agent = None

async def get_agentic_agent():
    """Obtém ou cria instância do AGENTIC SDR"""
    global agentic_agent
    if agentic_agent is None:
        agentic_agent = await get_agentic_sdr()
    return agentic_agent

@router.post("/evolution")
async def evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook principal da Evolution API
    Recebe todos os eventos do WhatsApp
    """
    try:
        # Recebe dados do webhook
        data = await request.json()
        
        # Log do evento recebido
        event = data.get("event")
        instance = data.get("instance")
        
        emoji_logger.webhook_receive("/evolution", "evolution-api", event=event, instance=instance)
        
        # Processa eventos específicos
        if event == "MESSAGES_UPSERT":
            # Nova mensagem recebida
            background_tasks.add_task(
                process_new_message,
                data.get("data", {})
            )
            
        elif event == "CONNECTION_UPDATE":
            # Status da conexão mudou
            await process_connection_update(data.get("data", {}))
            
        elif event == "QRCODE_UPDATED":
            # QR Code atualizado
            await process_qrcode_update(data.get("data", {}))
            
        elif event == "MESSAGES_UPDATE":
            # Status de mensagem atualizado (entregue, lida, etc)
            await process_message_update(data.get("data", {}))
            
        elif event == "PRESENCE_UPDATE":
            # Status de presença (online, digitando, etc)
            await process_presence_update(data.get("data", {}))
            
        return {"status": "ok", "event": event}
        
    except Exception as e:
        emoji_logger.system_error("Webhook Evolution", str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def process_new_message(data: Dict[str, Any]):
    """
    Processa nova mensagem recebida
    
    Args:
        data: Dados da mensagem
    """
    try:
        # Extrai informações da mensagem
        messages = data.get("messages", [])
        if not messages:
            return
        
        message = messages[0]  # Pega primeira mensagem
        
        # Informações básicas
        key = message.get("key", {})
        remote_jid = key.get("remoteJid", "")
        from_me = key.get("fromMe", False)
        message_id = key.get("id", "")
        
        # Ignora mensagens enviadas por nós
        if from_me:
            return
        
        # Extrai número do telefone
        phone = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
        
        # Verifica se é grupo
        is_group = "@g.us" in remote_jid
        if is_group:
            # Por enquanto, ignora mensagens de grupo
            emoji_logger.webhook_process(f"Mensagem de grupo ignorada: {remote_jid}")
            return
        
        # Extrai conteúdo da mensagem
        message_content = extract_message_content(message)
        
        if not message_content:
            emoji_logger.system_warning(f"Mensagem sem conteúdo de {phone}")
            return
        
        emoji_logger.evolution_receive(phone, "text", preview=message_content[:100])
        
        # Verifica rate limit
        if not await redis_client.check_rate_limit(
            f"message:{phone}",
            max_requests=10,
            window_seconds=60
        ):
            emoji_logger.system_warning(f"Rate limit excedido para {phone}")
            await evolution_client.send_text_message(
                phone,
                "⚠️ Você está enviando muitas mensagens. Por favor, aguarde um momento.",
                delay=1
            )
            return
        
        # Busca ou cria lead no banco
        lead = await supabase_client.get_lead_by_phone(phone)
        
        if not lead:
            # Cria novo lead
            lead = await supabase_client.create_lead({
                "phone": phone,
                "first_message": message_content,
                "source": "whatsapp",
                "status": "new",
                "created_at": datetime.now().isoformat()
            })
            
            emoji_logger.supabase_insert("leads", 1, phone=phone)
        
        # Busca ou cria conversa
        conversation = await supabase_client.get_conversation_by_phone(phone)
        if not conversation:
            conversation = await supabase_client.create_conversation(phone, lead["id"])
        
        # Salva mensagem no banco
        await supabase_client.save_message({
            "conversation_id": conversation["id"],
            "content": message_content,
            "sender": "user",
            "metadata": {
                "message_id": message_id,
                "raw_data": message
            }
        })
        
        # Cache da conversa
        await redis_client.cache_conversation(
            phone,
            {
                "lead_id": lead["id"],
                "conversation_id": conversation["id"],
                "last_message": message_content,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Processa com o AGENTIC SDR
        agentic = await get_agentic_agent()
        
        # Simular tempo de leitura da mensagem recebida
        if settings.simulate_reading_time:
            reading_time = evolution_client.calculate_reading_time(message_content)
            if reading_time > 0:
                await asyncio.sleep(reading_time)
                emoji_logger.webhook_process(f"Tempo de leitura simulado: {round(reading_time, 2)}s")
        
        # Preparar mídia se houver
        media_data = None
        if message.get("message", {}).get("imageMessage"):
            img_msg = message["message"]["imageMessage"]
            media_data = {
                "type": "image",
                "mimetype": img_msg.get("mimetype", "image/jpeg"),
                "caption": img_msg.get("caption", ""),
                "data": img_msg.get("jpegThumbnail", "")  # Base64 da imagem
            }
        elif message.get("message", {}).get("documentMessage"):
            doc_msg = message["message"]["documentMessage"]
            media_data = {
                "type": "document",
                "mimetype": doc_msg.get("mimetype", "application/pdf"),
                "fileName": doc_msg.get("fileName", "documento"),
                "data": ""  # Seria necessário baixar o documento
            }
        elif message.get("message", {}).get("audioMessage"):
            audio_msg = message["message"]["audioMessage"]
            media_data = {
                "type": "audio",
                "mimetype": audio_msg.get("mimetype", "audio/ogg"),
                "ptt": audio_msg.get("ptt", False),
                "data": ""  # Seria necessário baixar o áudio
            }
        
        # Processa mensagem com análise contextual inteligente
        response = await agentic.process_message(
            phone=phone,
            message=message_content,
            lead_data=lead,
            conversation_id=conversation["id"],
            media=media_data
        )
        
        # Envia resposta
        if response:
            # Delay antes de enviar mídia se houver
            if media_data and settings.delay_before_media > 0:
                await asyncio.sleep(settings.delay_before_media)
            
            # Enviar resposta com timing humanizado
            await evolution_client.send_text_message(
                phone,
                response,
                delay=None,  # Deixar o método calcular automaticamente
                simulate_typing=True
            )
            
            # Delay após mídia se houver
            if media_data and settings.delay_after_media > 0:
                await asyncio.sleep(settings.delay_after_media)
            
            # Salva resposta no banco
            await supabase_client.save_message({
                "conversation_id": conversation["id"],
                "content": response,
                "sender": "assistant",
                "metadata": {
                    "agent": "agentic_sdr",
                    "context_analyzed": True,
                    "messages_analyzed": 100
                }
            })
            
            # Atualiza analytics
            await redis_client.increment_counter("messages_processed")
            await redis_client.increment_counter(f"messages:{phone}")
        
    except Exception as e:
        emoji_logger.system_error("Webhook Message Processing", str(e))
        # Não lança exceção para não travar o webhook

def extract_message_content(message: Dict[str, Any]) -> Optional[str]:
    """
    Extrai conteúdo da mensagem baseado no tipo
    
    Args:
        message: Dados da mensagem
        
    Returns:
        Conteúdo extraído ou None
    """
    try:
        msg = message.get("message", {})
        
        # Texto simples
        if "conversation" in msg:
            return msg["conversation"]
        
        # Texto com contexto (resposta, etc)
        if "extendedTextMessage" in msg:
            return msg["extendedTextMessage"].get("text", "")
        
        # Imagem com legenda
        if "imageMessage" in msg:
            caption = msg["imageMessage"].get("caption", "")
            if caption:
                return f"[Imagem recebida] {caption}"
            return "[Imagem recebida]"
        
        # Documento
        if "documentMessage" in msg:
            filename = msg["documentMessage"].get("fileName", "documento")
            return f"[Documento recebido: {filename}]"
        
        # Áudio/nota de voz
        if "audioMessage" in msg:
            is_ptt = msg["audioMessage"].get("ptt", False)
            if is_ptt:
                return "[Nota de voz recebida]"
            return "[Áudio recebido]"
        
        # Vídeo
        if "videoMessage" in msg:
            caption = msg["videoMessage"].get("caption", "")
            if caption:
                return f"[Vídeo recebido] {caption}"
            return "[Vídeo recebido]"
        
        # Localização
        if "locationMessage" in msg:
            lat = msg["locationMessage"].get("degreesLatitude")
            lon = msg["locationMessage"].get("degreesLongitude")
            return f"[Localização recebida: {lat}, {lon}]"
        
        # Contato
        if "contactMessage" in msg:
            name = msg["contactMessage"].get("displayName", "Contato")
            return f"[Contato recebido: {name}]"
        
        # Sticker
        if "stickerMessage" in msg:
            return "[Sticker recebido]"
        
        # Reação
        if "reactionMessage" in msg:
            emoji = msg["reactionMessage"].get("text", "")
            return f"[Reação: {emoji}]"
        
        # Template button reply
        if "templateButtonReplyMessage" in msg:
            text = msg["templateButtonReplyMessage"].get("selectedDisplayText", "")
            return text
        
        # List reply
        if "listResponseMessage" in msg:
            title = msg["listResponseMessage"].get("title", "")
            return title
        
        # Buttons reply
        if "buttonsResponseMessage" in msg:
            text = msg["buttonsResponseMessage"].get("selectedDisplayText", "")
            return text
        
        emoji_logger.system_warning(f"Tipo de mensagem não reconhecido: {list(msg.keys())}")
        return None
        
    except Exception as e:
        emoji_logger.system_error("Message Content Extraction", str(e))
        return None

async def process_connection_update(data: Dict[str, Any]):
    """
    Processa atualização de status da conexão
    
    Args:
        data: Dados do evento
    """
    try:
        state = data.get("state")
        status_reason = data.get("statusReason")
        
        emoji_logger.evolution_webhook("CONNECTION_UPDATE", "whatsapp", state=state, reason=status_reason)
        
        # Salva status no Redis
        await redis_client.set(
            "whatsapp:connection_status",
            {
                "state": state,
                "status_reason": status_reason,
                "timestamp": datetime.now().isoformat()
            },
            ttl=3600
        )
        
        # Se desconectou, tenta reconectar
        if state == "close":
            emoji_logger.system_warning("WhatsApp desconectado, tentando reconectar")
            # TODO: Implementar reconexão automática
            
    except Exception as e:
        emoji_logger.system_error("Connection Update", str(e))

async def process_qrcode_update(data: Dict[str, Any]):
    """
    Processa atualização do QR Code
    
    Args:
        data: Dados do evento
    """
    try:
        qrcode = data.get("qrcode", {})
        code = qrcode.get("code")
        
        if code:
            emoji_logger.evolution_webhook("QR_CODE_UPDATED", "whatsapp", qr_preview=code[:50])
            
            # Salva QR Code no Redis para exibição posterior
            await redis_client.set(
                "whatsapp:qrcode",
                {
                    "code": code,
                    "timestamp": datetime.now().isoformat()
                },
                ttl=180  # QR Code expira em 3 minutos
            )
            
    except Exception as e:
        emoji_logger.system_error("QR Code Update", str(e))

async def process_message_update(data: Dict[str, Any]):
    """
    Processa atualização de status de mensagem
    
    Args:
        data: Dados do evento
    """
    try:
        messages = data.get("messages", [])
        
        for message in messages:
            key = message.get("key", {})
            message_id = key.get("id")
            remote_jid = key.get("remoteJid", "")
            
            # Status da mensagem
            status = message.get("status")
            
            # 1 = enviada, 2 = entregue, 3 = lida
            if status == 2:
                logger.debug(f"Mensagem {message_id} entregue para {remote_jid}")
            elif status == 3:
                logger.debug(f"Mensagem {message_id} lida por {remote_jid}")
                
                # Atualiza analytics
                phone = remote_jid.split("@")[0]
                await redis_client.increment_counter(f"messages_read:{phone}")
                
    except Exception as e:
        logger.error(f"Erro ao processar message update: {e}")

async def process_presence_update(data: Dict[str, Any]):
    """
    Processa atualização de presença (online, digitando, etc)
    
    Args:
        data: Dados do evento
    """
    try:
        presences = data.get("presences", {})
        
        for jid, presence_data in presences.items():
            phone = jid.split("@")[0] if "@" in jid else jid
            last_seen = presence_data.get("lastSeen")
            
            # Salva última visualização no cache
            if last_seen:
                await redis_client.set(
                    f"presence:{phone}",
                    {
                        "last_seen": last_seen,
                        "timestamp": datetime.now().isoformat()
                    },
                    ttl=300  # 5 minutos
                )
                
    except Exception as e:
        logger.error(f"Erro ao processar presence update: {e}")

@router.get("/health")
async def webhook_health():
    """Health check do webhook"""
    try:
        # Verifica conexão com WhatsApp
        connection_status = await redis_client.get("whatsapp:connection_status")
        
        return {
            "status": "healthy",
            "whatsapp_connected": connection_status.get("state") == "open" if connection_status else False,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/test")
async def test_webhook(data: Dict[str, Any]):
    """
    Endpoint de teste para webhook
    """
    logger.info(f"Teste de webhook recebido: {data}")
    return {"status": "ok", "received": data}