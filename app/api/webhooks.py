"""
Webhooks API - Recebe eventos da Evolution API
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List, Union
import asyncio
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
from app.services.message_buffer import MessageBuffer, set_message_buffer
from app.services.message_splitter import MessageSplitter, set_message_splitter
from app.utils.agno_media_detection import AGNOMediaDetector

router = APIRouter(prefix="/webhook", tags=["webhooks"])  # Mudado para /webhook (sem 's')

# Instância global do AGENTIC SDR
agentic_agent = None

# Instâncias dos serviços de mensagem
message_buffer = None
message_splitter = None

# Instância do detector AGNO para validação de mídia
agno_detector = AGNOMediaDetector()

def detect_media_format(media_data: Any) -> str:
    """
    Detecta o formato da mídia recebida
    
    Args:
        media_data: Dados da mídia em qualquer formato
        
    Returns:
        Tipo do formato: 'base64', 'data_url', 'url', 'bytes', 'unknown'
    """
    if media_data is None:
        return 'unknown'
    
    if isinstance(media_data, str):
        # Verifica se é uma data URL
        if media_data.startswith("data:"):
            logger.info("Formato detectado: Data URL")
            return 'data_url'
        # Verifica se é uma URL HTTP/HTTPS
        elif media_data.startswith(("http://", "https://")):
            logger.info("Formato detectado: URL para download")
            return 'url'
        # Se é uma string longa, provavelmente é base64
        elif len(media_data) > 50:  # Threshold reduzido para pegar thumbnails pequenos
            # Tenta validar se é base64 válido
            try:
                # Tenta decodificar um pequeno pedaço para verificar
                import base64 as b64
                test_sample = media_data[:100] if len(media_data) >= 100 else media_data
                test = b64.b64decode(test_sample)
                logger.info("Formato detectado: Base64 válido")
                return 'base64'
            except:
                logger.info("Formato detectado: String não-base64")
                return 'unknown'
        else:
            return 'unknown'
    elif isinstance(media_data, bytes):
        logger.info(f"Formato detectado: Bytes ({len(media_data)} bytes)")
        return 'bytes'
    else:
        logger.info(f"Formato desconhecido: {type(media_data)}")
        return 'unknown'

def extract_base64_from_data_url(data_url: str) -> str:
    """
    Extrai o base64 de uma data URL
    
    Args:
        data_url: Data URL completa (ex: data:image/jpeg;base64,...)
        
    Returns:
        Apenas a parte base64
    """
    if ";base64," in data_url:
        return data_url.split(";base64,")[1]
    return data_url

async def get_agentic_agent():
    """Obtém ou cria instância do AGENTIC SDR"""
    global agentic_agent
    if agentic_agent is None:
        agentic_agent = await get_agentic_sdr()
    return agentic_agent

def get_message_buffer_instance():
    """Obtém instância do Message Buffer (deve ser inicializado no startup)"""
    from app.services.message_buffer import get_message_buffer
    buffer = get_message_buffer()
    if buffer is None:
        # Fallback para criação se não inicializado (não deveria acontecer)
        logger.warning("Message Buffer não foi inicializado no startup!")
        buffer = MessageBuffer(
            timeout=settings.message_buffer_timeout,
            max_size=10
        )
        set_message_buffer(buffer)
    return buffer

def get_message_splitter_instance():
    """Obtém instância do Message Splitter (deve ser inicializado no startup)"""
    from app.services.message_splitter import get_message_splitter
    splitter = get_message_splitter()
    if splitter is None:
        # Fallback para criação se não inicializado (não deveria acontecer)
        logger.warning("Message Splitter não foi inicializado no startup!")
        splitter = MessageSplitter(
            max_length=settings.message_max_length,
            add_indicators=settings.message_add_indicators
        )
        set_message_splitter(splitter)
    return splitter

@router.post("/whatsapp/{event_type}")
async def whatsapp_dynamic_webhook(
    event_type: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook dinâmico para eventos específicos do WhatsApp
    Captura URLs como /webhook/whatsapp/messages-upsert
    """
    try:
        # Converter event_type de kebab-case para UPPER_SNAKE_CASE
        # Ex: messages-upsert -> MESSAGES_UPSERT
        event = event_type.upper().replace("-", "_")
        
        # Recebe dados do webhook
        data = await request.json()
        
        # Log do evento recebido
        emoji_logger.webhook_receive(f"/whatsapp/{event_type}", "evolution-api", event=event)
        
        # Processa eventos específicos baseado no tipo
        if event == "MESSAGES_UPSERT":
            # Nova mensagem recebida - passar apenas o 'data' interno
            # Evolution API v2: event está no nível superior, dados em 'data'
            actual_data = data.get("data", data)  # Pega 'data' se existir, senão usa o próprio data
            background_tasks.add_task(
                process_new_message,
                actual_data
            )
            
        elif event == "CONNECTION_UPDATE":
            # Status da conexão mudou
            await process_connection_update(data)
            
        elif event == "QRCODE_UPDATED":
            # QR Code atualizado
            await process_qrcode_update(data)
            
        elif event == "MESSAGES_UPDATE":
            # Status de mensagem atualizado (entregue, lida, etc)
            await process_message_update(data)
            
        elif event == "PRESENCE_UPDATE":
            # Status de presença (online, digitando, etc)
            await process_presence_update(data)
            
        elif event == "CHATS_UPDATE":
            # Atualização de chats
            logger.info(f"Chat update recebido: {data}")
            # TODO: Implementar processamento de chats_update se necessário
            
        elif event == "CONTACTS_UPDATE":
            # Atualização de contatos
            logger.info(f"Contacts update recebido: {data}")
            # TODO: Implementar processamento de contacts_update se necessário
        
        else:
            logger.warning(f"Evento não reconhecido: {event}")
            
        return {"status": "ok", "event": event}
        
    except Exception as e:
        emoji_logger.system_error(f"Webhook WhatsApp {event_type}", str(e))
        # Não lança exceção para não travar o webhook
        return {"status": "error", "message": str(e)}

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
            # Nova mensagem recebida - Evolution API v2
            actual_data = data.get("data", data)
            background_tasks.add_task(
                process_new_message,
                actual_data
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
        data: Dados da mensagem (Evolution API v2)
    """
    try:
        emoji_logger.webhook_process("Iniciando processamento de nova mensagem")
        
        # Evolution API v2: mensagem vem diretamente em 'data'
        # Não é mais um array 'messages', é um objeto direto
        if not data:
            emoji_logger.system_warning("Payload vazio")
            return
        
        # A mensagem ESTÁ diretamente no data (não em data.messages)
        message = data
        emoji_logger.webhook_process(f"Mensagem extraída: {message.get('key', {}).get('id', 'unknown')}")
        
        # Informações básicas
        key = message.get("key", {})
        remote_jid = key.get("remoteJid", "")
        from_me = key.get("fromMe", False)
        message_id = key.get("id", "")
        
        # Ignora mensagens enviadas por nós
        if from_me:
            emoji_logger.webhook_process("Mensagem própria ignorada")
            return
        
        # Extrai número do telefone
        phone = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
        
        # Verifica se é grupo
        is_group = "@g.us" in remote_jid
        if is_group:
            # Por enquanto, ignora mensagens de grupo
            emoji_logger.webhook_process(f"Mensagem de grupo ignorada: {remote_jid}")
            return
        
        emoji_logger.webhook_process(f"Processando mensagem de {phone}")
        
        # Extrai conteúdo da mensagem
        message_content = extract_message_content(message)
        
        if not message_content:
            emoji_logger.system_warning(f"Mensagem sem conteúdo de {phone}")
            # Log do payload para debug
            logger.debug(f"Payload completo: {message}")
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
        
        # Se o buffer está habilitado, adiciona mensagem ao buffer
        if settings.enable_message_buffer:
            buffer = get_message_buffer_instance()
            
            # Adiciona mensagem ao buffer (sem callback complexo)
            await buffer.add_message(
                phone=phone,
                content=message_content,
                message_data=message
            )
            # O buffer chama process_message_with_agent internamente quando pronto
        else:
            # Processa imediatamente sem buffer
            await process_message_with_agent(
                phone=phone,
                message_content=message_content,
                original_message=message,
                message_id=message_id
            )
            
    except Exception as e:
        emoji_logger.system_error("Webhook Message Processing", str(e))
        logger.exception("Erro detalhado no processamento:")
        # Não lança exceção para não travar o webhook

async def process_message_with_agent(
    phone: str,
    message_content: str,
    original_message: Dict[str, Any],
    message_id: str
):
    """
    Processa mensagem com o agente AGENTIC SDR
    
    Args:
        phone: Número do telefone
        message_content: Conteúdo da mensagem (pode ser combinado)
        original_message: Dados originais da mensagem
        message_id: ID da mensagem
    """
    try:
        # Busca ou cria lead no banco
        lead = await supabase_client.get_lead_by_phone(phone)
        
        if not lead:
            # Cria novo lead
            lead = await supabase_client.create_lead({
                "phone_number": phone,
                "current_stage": "INITIAL_CONTACT",
                "qualification_status": "PENDING",
                "interested": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
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
            "role": "user",  # Campo obrigatório
            "sender": "user",
            "media_data": {  # Usar media_data em vez de metadata
                "message_id": message_id,
                "raw_data": original_message
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
        emoji_logger.webhook_process("Obtendo instância do AGENTIC SDR")
        agentic = await get_agentic_agent()
        emoji_logger.webhook_process("AGENTIC SDR obtido com sucesso")
        
        # Simular tempo de leitura da mensagem recebida
        if settings.simulate_reading_time:
            reading_time = evolution_client.calculate_reading_time(message_content)
            if reading_time > 0:
                await asyncio.sleep(reading_time)
                emoji_logger.webhook_process(f"Tempo de leitura simulado: {round(reading_time, 2)}s")
        
        # Preparar mídia se houver
        media_data = None
        if original_message.get("message", {}).get("imageMessage"):
            img_msg = original_message["message"]["imageMessage"]
            
            # ===== LOG DETALHADO PARA DEBUG =====
            emoji_logger.system_info("📸 IMAGEM DETECTADA - Analisando estrutura...")
            logger.info(f"Campos disponíveis na imageMessage: {list(img_msg.keys())}")
            
            # Verificar jpegThumbnail primeiro (pode já vir em base64)
            jpeg_thumbnail = img_msg.get("jpegThumbnail", "")
            if jpeg_thumbnail:
                # Analisar formato do thumbnail
                if isinstance(jpeg_thumbnail, str):
                    logger.info(f"jpegThumbnail é string, tamanho: {len(jpeg_thumbnail)} chars")
                    logger.info(f"jpegThumbnail primeiros 50 chars: {jpeg_thumbnail[:50]}")
                    # Verificar se já é base64 válido
                    if len(jpeg_thumbnail) > 100 and not jpeg_thumbnail.startswith('http'):
                        logger.info("jpegThumbnail parece ser base64 válido")
                elif isinstance(jpeg_thumbnail, bytes):
                    logger.info(f"jpegThumbnail é bytes, tamanho: {len(jpeg_thumbnail)} bytes")
                    logger.info(f"jpegThumbnail primeiros bytes (hex): {jpeg_thumbnail[:20].hex()}")
            
            # Verificar outros campos de mídia
            if img_msg.get("mediaKey"):
                logger.info(f"mediaKey presente: {img_msg['mediaKey'][:20]}...")
            if img_msg.get("directPath"):
                logger.info(f"directPath presente: {img_msg['directPath'][:50]}...")
            if img_msg.get("url"):
                logger.info(f"URL presente: {img_msg['url'][:50]}...")
            
            # Tentar usar jpegThumbnail primeiro (mais rápido e já disponível)
            image_base64 = None
            
            # Validar formato do jpegThumbnail usando detect_media_format
            if jpeg_thumbnail:
                format_detected = detect_media_format(jpeg_thumbnail)
                logger.info(f"📸 jpegThumbnail formato detectado: {format_detected}")
                
                if format_detected == "base64":
                    # É base64 válido, usar direto
                    image_base64 = jpeg_thumbnail
                    emoji_logger.system_info(f"✅ jpegThumbnail validado como base64: {len(image_base64)} chars")
                    
                elif format_detected == "data_url":
                    # É data URL, extrair base64
                    image_base64 = extract_base64_from_data_url(jpeg_thumbnail)
                    emoji_logger.system_info(f"✅ Extraído base64 de data URL: {len(image_base64)} chars")
                    
                elif format_detected == "bytes":
                    # São bytes, converter para base64
                    try:
                        import base64 as b64_module
                        image_base64 = b64_module.b64encode(jpeg_thumbnail).decode('utf-8')
                        emoji_logger.system_info(f"✅ Convertido bytes para base64: {len(image_base64)} chars")
                    except:
                        logger.warning("Falha ao converter bytes para base64")
                else:
                    logger.warning(f"jpegThumbnail em formato não reconhecido: {format_detected}")
            
            # IMPORTANTE: Se thumbnail for muito pequena (<5KB), baixar imagem completa
            if image_base64 and len(image_base64) < 5000 and img_msg.get("url"):
                logger.info(f"🔍 Thumbnail muito pequena ({len(image_base64)} chars), baixando imagem completa...")
                image_base64 = None  # Resetar para baixar completa
            
            # Se não tem imagem válida ainda, baixar completa
            if not image_base64 and img_msg.get("url"):
                try:
                    emoji_logger.webhook_process(f"Baixando imagem completa de: {img_msg['url'][:50]}...")
                    
                    # Baixar imagem completa usando Evolution API
                    image_bytes = await evolution_client.download_media({"mediaUrl": img_msg["url"]})
                    
                    if image_bytes:
                        # Log dos primeiros bytes para debug
                        logger.info(f"Imagem baixada, primeiros 20 bytes (hex): {image_bytes[:20].hex()}")
                        
                        # Converter bytes para base64
                        import base64
                        import base64 as b64_module
                        image_base64 = b64_module.b64encode(image_bytes).decode('utf-8')
                        emoji_logger.webhook_process(f"Imagem completa baixada: {len(image_base64)} caracteres")
                    else:
                        emoji_logger.system_warning("Falha ao baixar imagem completa")
                        
                except Exception as download_error:
                    emoji_logger.system_warning(f"Erro ao baixar imagem: {download_error}")
            
            # Validar com AGNO detector se o base64 é uma imagem válida
            if image_base64:
                try:
                    # Decodificar base64 para verificar magic bytes
                    import base64 as b64_module
                    img_bytes = b64_module.b64decode(image_base64)
                    detection_result = agno_detector.detect_media_type(img_bytes)
                    
                    if detection_result.get('detected'):
                        detected_format = detection_result.get('format', 'unknown')
                        logger.info(f"🔍 AGNO validou mídia: {detected_format}")
                        emoji_logger.system_info(f"✅ Imagem validada ({detected_format}): {len(image_base64)} chars")
                    else:
                        logger.warning(f"⚠️ AGNO não reconheceu formato da imagem: {detection_result.get('magic_bytes', 'N/A')}")
                        emoji_logger.system_warning(f"Imagem com formato desconhecido, tentando processar mesmo assim")
                except Exception as agno_error:
                    logger.warning(f"Erro na validação AGNO: {agno_error}")
                    emoji_logger.system_info(f"✅ Imagem pronta (sem validação AGNO): {len(image_base64)} chars")
                    
            media_data = {
                "type": "image",
                "mimetype": img_msg.get("mimetype", "image/jpeg"),
                "caption": img_msg.get("caption", ""),
                "data": image_base64,  # Imagem completa (se >5KB) ou thumbnail
                "has_full_image": bool(image_base64 and len(image_base64) > 5000),  # True se é imagem completa
                "file_size": img_msg.get("fileLength", 0)
            }
        elif original_message.get("message", {}).get("documentMessage"):
            doc_msg = original_message["message"]["documentMessage"]
            
            # ===== LOG DETALHADO PARA DEBUG =====
            emoji_logger.system_info("📄 DOCUMENTO DETECTADO - Analisando estrutura...")
            logger.info(f"Campos disponíveis no documentMessage: {list(doc_msg.keys())}")
            logger.info(f"Nome do arquivo: {doc_msg.get('fileName', 'N/A')}")
            logger.info(f"Mimetype: {doc_msg.get('mimetype', 'N/A')}")
            
            # Verificar se há thumbnail ou dados inline
            if doc_msg.get("jpegThumbnail"):
                thumb = doc_msg["jpegThumbnail"]
                if isinstance(thumb, str):
                    logger.info(f"Documento tem thumbnail string: {len(thumb)} chars")
                elif isinstance(thumb, bytes):
                    logger.info(f"Documento tem thumbnail bytes: {len(thumb)} bytes")
            
            # Tentar baixar o documento completo
            document_base64 = None
            
            if doc_msg.get("url"):
                try:
                    emoji_logger.webhook_process(f"Baixando documento: {doc_msg.get('fileName', 'documento')}")
                    
                    # Baixar documento usando Evolution API
                    doc_bytes = await evolution_client.download_media({"mediaUrl": doc_msg["url"]})
                    
                    if doc_bytes:
                        import base64
                        import base64 as b64_module
                        document_base64 = b64_module.b64encode(doc_bytes).decode('utf-8')
                        emoji_logger.webhook_process(f"Documento baixado: {len(document_base64)} caracteres")
                    else:
                        emoji_logger.system_warning("Falha ao baixar documento")
                        
                except Exception as download_error:
                    emoji_logger.system_warning(f"Erro ao baixar documento: {download_error}")
            
            media_data = {
                "type": "document",
                "mimetype": doc_msg.get("mimetype", "application/pdf"),
                "fileName": doc_msg.get("fileName", "documento"),
                "data": document_base64 or "",  # Documento completo ou vazio
                "has_content": bool(document_base64),
                "file_size": doc_msg.get("fileLength", 0)
            }
        elif original_message.get("message", {}).get("audioMessage"):
            audio_msg = original_message["message"]["audioMessage"]
            
            # ===== LOG DETALHADO PARA DEBUG =====
            emoji_logger.system_info("🎵 ÁUDIO DETECTADO - Analisando estrutura...")
            logger.info(f"Campos disponíveis no audioMessage: {list(audio_msg.keys())}")
            logger.info(f"Mimetype: {audio_msg.get('mimetype', 'N/A')}")
            logger.info(f"Duração: {audio_msg.get('seconds', 'N/A')} segundos")
            logger.info(f"É nota de voz (ptt): {audio_msg.get('ptt', False)}")
            
            # Verificar se há dados inline
            if audio_msg.get("mediaKey"):
                logger.info(f"mediaKey presente: {audio_msg['mediaKey'][:20]}...")
            if audio_msg.get("directPath"):
                logger.info(f"directPath presente: {audio_msg['directPath'][:50]}...")
            
            # Tentar baixar o áudio completo
            audio_base64 = None
            
            if audio_msg.get("url"):
                try:
                    emoji_logger.webhook_process(f"Baixando áudio/nota de voz")
                    
                    # Baixar áudio usando Evolution API
                    audio_bytes = await evolution_client.download_media({"mediaUrl": audio_msg["url"]})
                    
                    if audio_bytes:
                        # Log dos primeiros bytes para debug
                        logger.info(f"Áudio baixado, primeiros 20 bytes (hex): {audio_bytes[:20].hex()}")
                        
                        # Validar com AGNO antes de converter para base64
                        audio_detection = agno_detector.detect_media_type(audio_bytes)
                        if audio_detection.get('detected'):
                            detected_audio_format = audio_detection.get('format', 'unknown')
                            logger.info(f"🔍 AGNO validou áudio: {detected_audio_format}")
                        else:
                            logger.warning(f"⚠️ AGNO não reconheceu formato do áudio: {audio_detection.get('magic_bytes', 'N/A')}, continuando...")
                        
                        import base64 as b64_module
                        audio_base64 = b64_module.b64encode(audio_bytes).decode('utf-8')
                        emoji_logger.webhook_process(f"Áudio baixado e validado: {len(audio_base64)} caracteres")
                    else:
                        emoji_logger.system_warning("Falha ao baixar áudio")
                        
                except Exception as download_error:
                    emoji_logger.system_warning(f"Erro ao baixar áudio: {download_error}")
            
            media_data = {
                "type": "audio",
                "mimetype": audio_msg.get("mimetype", "audio/ogg"),
                "ptt": audio_msg.get("ptt", False),
                "data": audio_base64 or "",  # Áudio completo ou vazio
                "has_content": bool(audio_base64),
                "duration": audio_msg.get("seconds", 0)
            }
        
        # Processa mensagem com análise contextual inteligente
        emoji_logger.webhook_process(f"Chamando AGENTIC SDR para processar: {message_content[:50]}...")
        
        # IMPORTANTE: Enviar typing ANTES de processar (mostra que está "pensando")
        try:
            # Estima tempo de processamento baseado no tamanho da mensagem
            estimated_processing_time = max(3.0, min(len(message_content) * 0.05, 10.0))
            emoji_logger.webhook_process(f"Enviando typing por ~{estimated_processing_time:.1f}s enquanto processa...")
            
            # Envia typing sem bloquear o processamento
            asyncio.create_task(evolution_client.send_typing(phone, duration_seconds=estimated_processing_time))
            
        except Exception as typing_error:
            emoji_logger.system_warning(f"Erro ao enviar typing inicial: {typing_error}")
            # Continua mesmo se falhar o typing
        
        try:
            response = await agentic.process_message(
                phone=phone,
                message=message_content,
                lead_data=lead,
                conversation_id=conversation["id"],
                media=media_data
            )
            
            emoji_logger.webhook_process(f"Resposta recebida do AGENTIC SDR: {response[:100] if response else 'NENHUMA'}...")
            
        except Exception as agent_error:
            emoji_logger.system_error("AGENTIC SDR", f"Erro ao processar: {agent_error}")
            response = None
        
        # Envia resposta
        if response:
            emoji_logger.webhook_process(f"Enviando resposta para {phone}")
            
            # Delay antes de enviar mídia se houver
            if media_data and settings.delay_before_media > 0:
                await asyncio.sleep(settings.delay_before_media)
            
            # Se o splitter está habilitado e a mensagem é longa, divide em chunks
            if settings.enable_message_splitter and len(response) > settings.message_max_length:
                splitter = get_message_splitter_instance()
                chunks = splitter.split_message(response)
                
                emoji_logger.system_info(
                    f"Mensagem dividida em {len(chunks)} partes",
                    phone=phone,
                    original_length=len(response)
                )
                
                # Envia cada chunk com delay entre eles
                for i, chunk in enumerate(chunks):
                    try:
                        # Delay entre chunks (exceto o primeiro)
                        if i > 0 and settings.message_chunk_delay > 0:
                            await asyncio.sleep(settings.message_chunk_delay)
                        
                        result = await evolution_client.send_text_message(
                            phone,
                            chunk,
                            delay=None,  # Deixar o método calcular automaticamente
                            simulate_typing=False  # Já enviamos typing antes, não precisa mais
                        )
                        emoji_logger.evolution_send(phone, "text", preview=chunk[:50])
                        emoji_logger.system_info(f"Chunk {i+1}/{len(chunks)} enviado. ID: {result.get('key', {}).get('id', 'N/A')}")
                        
                    except Exception as send_error:
                        emoji_logger.system_error("Evolution API", f"Erro ao enviar chunk {i+1}: {send_error}")
                        # Continua tentando enviar os próximos chunks
            else:
                # Envia mensagem única (sem dividir)
                try:
                    result = await evolution_client.send_text_message(
                        phone,
                        response,
                        delay=None,  # Deixar o método calcular automaticamente
                        simulate_typing=False  # Já enviamos typing antes, não precisa mais
                    )
                    emoji_logger.evolution_send(phone, "text", preview=response[:50])
                    emoji_logger.system_info(f"Mensagem enviada com sucesso. ID: {result.get('key', {}).get('id', 'N/A')}")
                    
                except Exception as send_error:
                    emoji_logger.system_error("Evolution API", f"Erro ao enviar mensagem: {send_error}")
                    # Re-lançar para não silenciar o erro
                    raise
            
            # Delay após mídia se houver
            if media_data and settings.delay_after_media > 0:
                await asyncio.sleep(settings.delay_after_media)
            
            # Salva resposta no banco
            await supabase_client.save_message({
                "conversation_id": conversation["id"],
                "content": response,
                "role": "assistant",  # Campo obrigatório
                "sender": "assistant",
                "media_data": {  # Usar media_data em vez de metadata
                    "agent": "agentic_sdr",
                    "context_analyzed": True,
                    "messages_analyzed": 100
                }
            })
            
            # Atualiza analytics
            await redis_client.increment_counter("messages_processed")
            await redis_client.increment_counter(f"messages:{phone}")
            
            emoji_logger.webhook_process("Mensagem processada com sucesso!")
        else:
            emoji_logger.system_warning(f"Nenhuma resposta gerada para {phone}")
        
    except Exception as e:
        emoji_logger.system_error("Agent Message Processing", str(e))
        logger.exception("Erro detalhado no processamento com agente:")
        # Não lança exceção para não travar o webhook

def extract_message_content(message: Dict[str, Any]) -> Optional[str]:
    """
    Extrai conteúdo da mensagem baseado no tipo (Evolution API v2)
    
    Args:
        message: Dados da mensagem
        
    Returns:
        Conteúdo extraído ou None
    """
    try:
        # Evolution API v2: message já está no nível correto
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