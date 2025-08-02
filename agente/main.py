"""
Main entry point for the modular SDR Agent.

This module integrates the new modular agent with the existing
webhook infrastructure from api/main.py.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from loguru import logger

from agente.core.config import (
    PORT,
    HOST,
    DEBUG,
    LOG_LEVEL,
    ENVIRONMENT
)
from agente.core.types import WhatsAppMessage
from agente.core.agent import SDRAgent
from agente.core.reaction_manager import get_reaction_manager
from agente.core.auto_chunking import get_auto_chunking_manager
from agente.core.monitoring import (
    setup_sentry,
    capture_agent_error,
    capture_agent_event,
    set_user_context,
    add_breadcrumb
)

# Initialize the agent globally
agent: SDRAgent = None

# DEDUPLICATED MESSAGE CACHE - Previne mensagens duplicadas por message_id
# Cache simples em memória para IDs de mensagens processadas
_processed_message_ids = set()
_max_cache_size = 10000  # Máximo de IDs na cache


def is_message_already_processed(message_id: str) -> bool:
    """
    Verifica se uma mensagem já foi processada
    
    Args:
        message_id: ID da mensagem do WhatsApp
        
    Returns:
        True se já foi processada, False caso contrário
    """
    return message_id in _processed_message_ids


def mark_message_as_processed(message_id: str) -> None:
    """
    Marca uma mensagem como processada na cache de deduplicação
    
    Args:
        message_id: ID da mensagem do WhatsApp
    """
    global _processed_message_ids
    
    # Limitar tamanho da cache
    if len(_processed_message_ids) >= _max_cache_size:
        # Remove 20% dos IDs mais antigos (FIFO simples)
        remove_count = _max_cache_size // 5
        for _ in range(remove_count):
            _processed_message_ids.pop()
    
    _processed_message_ids.add(message_id)
    logger.debug(f"Message ID marked as processed: {message_id}")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events.
    """
    global agent
    
    # Startup
    logger.info("🚀 Starting modular SDR Agent...")
    
    # Setup Sentry monitoring
    sentry_initialized = setup_sentry()
    if sentry_initialized:
        logger.info("📊 Sentry monitoring enabled")
        capture_agent_event(
            "SDR Agent Starting",
            "lifecycle",
            {"environment": ENVIRONMENT, "debug": DEBUG}
        )
    
    try:
        # Initialize agent
        agent = SDRAgent()
        await agent.start()
        
        logger.info("✅ SDR Agent started successfully")
        
        # Log startup event
        if sentry_initialized:
            capture_agent_event(
                "SDR Agent Started Successfully",
                "lifecycle",
                {"environment": ENVIRONMENT}
            )
        
    except Exception as e:
        logger.error(f"❌ Failed to start SDR Agent: {e}")
        
        # Capture startup error
        capture_agent_error(
            e,
            context={
                "phase": "startup",
                "environment": ENVIRONMENT
            }
        )
        raise
    
    yield
    
    # Shutdown
    logger.info("🔌 Shutting down SDR Agent...")
    
    try:
        if agent:
            await agent.shutdown()
        
        logger.info("✅ SDR Agent shutdown complete")
        
        # Log shutdown event
        capture_agent_event(
            "SDR Agent Shutdown",
            "lifecycle",
            {"environment": ENVIRONMENT}
        )
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
        
        # Capture shutdown error
        capture_agent_error(
            e,
            context={
                "phase": "shutdown",
                "environment": ENVIRONMENT
            }
        )


# Create FastAPI app
app = FastAPI(
    title="SDR Agent - Helen Vieira",
    description="Modular SDR Agent for Solar Prime using AGnO Framework",
    version="2.0.0",
    lifespan=lifespan
)

# Add Sentry middleware for request tracking
@app.middleware("http")
async def sentry_middleware(request: Request, call_next):
    """Add Sentry breadcrumbs for all requests."""
    add_breadcrumb(
        message=f"{request.method} {request.url.path}",
        category="http",
        level="info",
        data={
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params)
        }
    )
    
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    """Root endpoint with agent status."""
    return {
        "agent": "Helen Vieira - SDR SolarPrime",
        "version": "2.0.0",
        "status": "online" if agent else "offline",
        "framework": "AGnO",
        "environment": ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if agent is initialized
        if not agent:
            raise HTTPException(
                status_code=503,
                detail="Agent not initialized"
            )
        
        # Get session count
        session_count = await agent.session_manager.get_active_sessions_count()
        
        return {
            "status": "healthy",
            "agent": "online",
            "active_sessions": session_count,
            "environment": ENVIRONMENT,
            "deduplication_cache": {
                "total_processed_messages": len(_processed_message_ids),
                "cache_limit": _max_cache_size,
                "cache_utilization": f"{(len(_processed_message_ids) / _max_cache_size) * 100:.1f}%"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    WhatsApp webhook endpoint for receiving messages.
    Compatible with Evolution API v2.
    """
    try:
        # Parse webhook data with validation
        data = await request.json()
        
        # Validate data structure
        if not isinstance(data, dict):
            logger.warning(f"Invalid webhook data type: {type(data)}")
            return {"status": "ignored", "reason": "invalid_data_type"}
        
        # Extract and normalize event name (handle both formats: "PRESENCE_UPDATE" and "presence.update")
        event = data.get("event", "")
        if isinstance(event, str):
            # Normalize event name: PRESENCE_UPDATE -> presence.update
            event = event.lower().replace("_", ".")
        
        # Extract instance data
        instance = data.get("instance", {})
        
        # Log webhook for debugging (detailed in debug mode, summary in info mode)
        if DEBUG:
            logger.debug(f"Webhook received - Event: {event}, Full Data: {data}")
        else:
            logger.info(f"Webhook received - Event: {event}")
        
        # Handle different event types
        if event == "messages.upsert":
            # New message received - based on Evolution API v2 official documentation
            message_data = data.get("data", {})
            
            # Robust validation for message data structure
            if not isinstance(message_data, dict):
                logger.error(f"🚨 MESSAGES_UPSERT: Invalid data structure - Expected dict, got {type(message_data)}")
                if DEBUG:
                    logger.debug(f"Raw webhook data: {data}")
                    logger.debug(f"Raw message_data: {message_data}")
                return {
                    "status": "error", 
                    "reason": "invalid_message_data_structure", 
                    "expected": "dict", 
                    "received": str(type(message_data)),
                    "debug_info": str(message_data) if DEBUG else None
                }
            
            # Extract key information with additional validation
            key = message_data.get("key", {}) if isinstance(message_data.get("key"), dict) else {}
            message = message_data.get("message", {}) if isinstance(message_data.get("message"), dict) else {}
            push_name = message_data.get("pushName", "") if isinstance(message_data.get("pushName"), str) else ""
            
            # Validate key structure (Evolution API v2 structure validation)
            if not key or not isinstance(key, dict):
                logger.warning(f"🚨 MESSAGES_UPSERT: Missing or invalid 'key' structure in message_data")
                if DEBUG:
                    logger.debug(f"Key data: {key}, Type: {type(key)}")
                return {"status": "ignored", "reason": "missing_key_structure"}
            
            # Get phone number (remove @s.whatsapp.net suffix) with validation
            remote_jid = key.get("remoteJid", "") if isinstance(key.get("remoteJid"), str) else ""
            if not remote_jid:
                logger.warning(f"🚨 MESSAGES_UPSERT: Missing remoteJid in key structure")
                if DEBUG:
                    logger.debug(f"Key structure: {key}")
                return {"status": "ignored", "reason": "missing_remote_jid"}
            
            phone = remote_jid.replace("@s.whatsapp.net", "") if "@s.whatsapp.net" in remote_jid else remote_jid
            
            # Get message ID for deduplication
            message_id = key.get("id", "")
            if not message_id:
                logger.warning(f"🚨 MESSAGES_UPSERT: Missing message ID in key structure")
                return {"status": "ignored", "reason": "missing_message_id"}
            
            # DEDUPLICATION: Check if message already processed
            if is_message_already_processed(message_id):
                logger.info(f"🔄 Skipping duplicate message {message_id} from {phone} (already processed)")
                return {"status": "ignored", "reason": "duplicate_message", "message_id": message_id, "phone": phone}
            
            # Skip if message is from us (fromMe = true) - Evolution API v2 behavior
            from_me = key.get("fromMe", False)
            if from_me:
                logger.debug(f"✅ Skipping our own message to {phone} (fromMe=true)")
                return {"status": "ignored", "reason": "own_message", "phone": phone}
            
            # Validate message structure (Evolution API v2)
            if not message or not isinstance(message, dict):
                logger.warning(f"🚨 MESSAGES_UPSERT: Missing or invalid 'message' structure")
                if DEBUG:
                    logger.debug(f"Message data: {message}, Type: {type(message)}")
                return {"status": "ignored", "reason": "missing_message_structure"}
            
            # Extract message content with robust validation
            text_message = None
            media_url = None
            media_type = None
            
            # Text message - Evolution API v2 message types
            if "conversation" in message and isinstance(message.get("conversation"), str):
                text_message = message["conversation"]
            elif "extendedTextMessage" in message and isinstance(message.get("extendedTextMessage"), dict):
                ext_msg = message["extendedTextMessage"]
                text_message = ext_msg.get("text", "") if isinstance(ext_msg.get("text"), str) else ""
            
            # Image message
            elif "imageMessage" in message:
                image_msg = message["imageMessage"]
                text_message = image_msg.get("caption", "")
                media_type = "image"
                # Media URL would need to be downloaded via Evolution API
                
            # Audio message
            elif "audioMessage" in message:
                media_type = "audio"
                # Audio would need to be downloaded and transcribed
                
            # Document message
            elif "documentMessage" in message:
                doc_msg = message["documentMessage"]
                text_message = doc_msg.get("caption", "")
                media_type = "document"
                # Document would need to be downloaded
            
            # Skip if no valid message content
            if not text_message and not media_type:
                logger.debug(f"No valid message content from {phone}")
                return {"status": "ignored", "reason": "no_content"}
            
            # Create WhatsApp message object - Evolution API v2 real structure
            # Handle both instance formats: string or dict
            if isinstance(instance, dict):
                instance_id = instance.get("instanceId", instance.get("instanceName", ""))
            else:
                # Evolution API sends instance as string, instanceId is in data
                instance_id = message_data.get("instanceId", str(instance))
            
            whatsapp_msg = WhatsAppMessage(
                instance_id=instance_id,
                phone=phone,
                name=push_name,
                message=text_message or "",
                message_id=message_id,
                timestamp=str(message_data.get("messageTimestamp", "")),
                media_url=media_url,
                media_type=media_type
            )
            
            # DEDUPLICATION: Mark message as processed BEFORE background task
            # Isso previne duplicações mesmo se o background task falhar
            mark_message_as_processed(message_id)
            
            # Process message in background (webhook retorna 200 imediatamente)
            background_tasks.add_task(process_message_async, whatsapp_msg)
            
            logger.info(f"📥 Message accepted for background processing: {message_id} from {phone}")
            
            return {
                "status": "accepted",
                "message_id": whatsapp_msg.message_id,
                "phone": phone,
                "deduplication": "enabled"
            }
        
        # Handle other events
        elif event == "connection.update":
            # Connection status update
            state = data.get("data", {}).get("state", "")
            logger.info(f"WhatsApp connection state: {state}")
            return {"status": "ok", "event": event, "state": state}
        
        elif event == "messages.update":
            # Message status update (delivered, read, etc.)
            return {"status": "ok", "event": event}
        
        elif event == "presence.update":
            # User presence status update (online, typing, etc.)
            presence_data = data.get("data", {})
            
            if isinstance(presence_data, dict):
                user_id = presence_data.get("id", "")
                presences = presence_data.get("presences", {})
                
                # Extract presence status for logging
                if presences and isinstance(presences, dict):
                    for jid, presence_info in presences.items():
                        if isinstance(presence_info, dict):
                            status = presence_info.get("lastKnownPresence", "unknown")
                            logger.debug(f"Presence update - User: {jid}, Status: {status}")
                        else:
                            logger.debug(f"Presence update - User: {jid}, Raw info: {presence_info}")
                else:
                    logger.debug(f"Presence update - User: {user_id}, No detailed presence data")
            else:
                logger.debug(f"Presence update - Invalid data structure: {type(presence_data)}")
            
            return {"status": "ok", "event": event}
        
        elif event == "qrcode.updated":
            # QR Code update event
            qr_data = data.get("data", {})
            logger.info(f"QR Code updated for instance: {instance.get('instanceName', 'unknown')}")
            return {"status": "ok", "event": event}
        
        else:
            # Unknown event
            logger.debug(f"Unknown webhook event: {event}")
            return {"status": "ignored", "event": event}
        
    except ValueError as e:
        # JSON parsing error
        logger.error(f"Error parsing webhook JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    except Exception as e:
        # Enhanced error logging for Evolution API webhook debugging
        logger.error(f"🚨 WEBHOOK ERROR: {e}")
        logger.error(f"🚨 ERROR TYPE: {type(e).__name__}")
        logger.error(f"🚨 ERROR LINE: {e.__traceback__.tb_lineno if e.__traceback__ else 'unknown'}")
        
        # Log request information for debugging
        try:
            body = await request.body()
            body_str = body.decode('utf-8', errors='ignore')
            logger.error(f"🚨 REQUEST BODY: {body_str}")
            
            # Try to parse as JSON for better debugging
            try:
                import json
                parsed_data = json.loads(body_str)
                logger.error(f"🚨 PARSED JSON: {json.dumps(parsed_data, indent=2)}")
                
                # Specific Evolution API debugging
                event_type = parsed_data.get('event', 'unknown')
                data_type = type(parsed_data.get('data', {}))
                logger.error(f"🚨 EVENT: {event_type}, DATA TYPE: {data_type}")
                
                if event_type == 'messages.upsert' or event_type == 'MESSAGES_UPSERT':
                    data_content = parsed_data.get('data', {})
                    logger.error(f"🚨 MESSAGES_UPSERT DATA: {data_content}")
                    logger.error(f"🚨 DATA KEYS: {list(data_content.keys()) if isinstance(data_content, dict) else 'not_dict'}")
                    
            except json.JSONDecodeError as json_error:
                logger.error(f"🚨 JSON PARSE ERROR: {json_error}")
                
        except Exception as body_error:
            logger.error(f"🚨 Could not read request body: {body_error}")
        
        # Capture exception details for Evolution API specific debugging
        import traceback
        logger.error(f"🚨 FULL TRACEBACK:\n{traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Webhook processing error: {str(e)}",
                "error_type": type(e).__name__,
                "event": event if 'event' in locals() else 'unknown',
                "timestamp": datetime.now().isoformat()
            }
        )


async def process_message_async(message: WhatsAppMessage):
    """
    Process message asynchronously.
    
    Args:
        message: WhatsApp message to process
    """
    try:
        logger.info(f"Processing message from {message.phone}: {message.message[:50]}...")
        
        # Set user context for Sentry
        set_user_context(message.phone, message.name)
        
        # Add breadcrumb
        add_breadcrumb(
            message="Processing WhatsApp message",
            category="message",
            level="info",
            data={
                "phone": message.phone[:4] + "****",
                "message_id": message.message_id,
                "has_media": bool(message.media_url)
            }
        )
        
        # 🚨 CRÍTICO: Salvar mensagem do usuário ANTES do processamento
        # Usar context dict para armazenar dados da conversa em vez de modificar Pydantic
        message_context = {
            "conversation_id": None,
            "conversation": None,
            "is_new_conversation": False,
            "save_error": None
        }
        
        try:
            from agente.repositories import get_conversation_repository, get_message_repository
            
            conv_repo = get_conversation_repository()
            msg_repo = get_message_repository()
            
            # Obter/criar conversa (com lead automático) - agora com UPSERT atômico
            conversation, is_new = await conv_repo.get_or_create_conversation(
                phone=message.phone,
                session_id=message.instance_id or "default"
            )
            
            # Armazenar no context dict
            message_context["conversation_id"] = conversation.id
            message_context["conversation"] = conversation
            message_context["is_new_conversation"] = is_new
            
            if is_new:
                logger.info(f"✅ Nova conversa criada para {message.phone}: {conversation.id}")
            else:
                logger.info(f"✅ Conversa existente encontrada para {message.phone}: {conversation.id}")
            
            # Preparar dados de mídia se houver
            media_data = None
            if message.media_url or message.media_type:
                media_data = {
                    "type": message.media_type or "text",
                    "url": message.media_url
                }
            
            # Salvar mensagem do usuário no banco ANTES de processar
            user_message = await msg_repo.save_user_message(
                conversation_id=conversation.id,
                content=message.message or "[mensagem vazia]",
                whatsapp_id=message.message_id,
                media=media_data
            )
            
            logger.info(f"💾 Mensagem do usuário salva: {user_message.id} (conversa: {conversation.id})")
            
        except Exception as save_error:
            logger.error(f"❌ ERRO ao salvar mensagem do usuário: {save_error}")
            message_context["save_error"] = str(save_error)
            # Não bloqueamos o processamento por erro de salvamento
        
        # Process reactions FIRST (before agent processing)
        reaction_manager = get_reaction_manager()
        reaction_results = await reaction_manager.process_message_reactions(message)
        
        # Log reaction results
        if reaction_results["total_reactions_sent"] > 0:
            logger.info(
                f"✨ Sent {reaction_results['total_reactions_sent']} reaction(s) to {message.phone}",
                media_reaction=bool(reaction_results["media_reaction"]),
                spontaneous_reaction=bool(reaction_results["spontaneous_reaction"])
            )
        
        # Process with agent
        response = await agent.process_message(message)
        
        if response.success:
            logger.info(f"✅ Message processed successfully for {message.phone}")
            
            # 🚨 CRÍTICO: Salvar resposta do agente no banco APÓS processamento
            if response.message and message_context["conversation_id"] is not None:
                try:
                    from agente.repositories import get_message_repository
                    
                    msg_repo = get_message_repository()
                    
                    # Salvar resposta do agente usando context dict
                    agent_message = await msg_repo.save_assistant_message(
                        conversation_id=message_context["conversation_id"],
                        content=response.message
                    )
                    
                    logger.info(f"💾 Resposta do agente salva: {agent_message.id} (conversa: {message_context['conversation_id']})")
                    
                except Exception as save_error:
                    logger.error(f"❌ ERRO ao salvar resposta do agente: {save_error}")
                    # Não bloqueamos o envio por erro de salvamento
            
            # CRÍTICO: Enviar resposta de volta para o WhatsApp (com auto-chunking)
            if response.message:
                try:
                    # 🧼 SANITIZAÇÃO OBRIGATÓRIA: Remover vazamentos internos do AGnO ANTES do auto-chunking
                    from agente.core.response_sanitizer import get_response_sanitizer
                    
                    response_sanitizer = get_response_sanitizer()
                    clean_message = response_sanitizer.sanitize_response(response.message)
                    
                    # Log se houve sanitização
                    if clean_message != response.message:
                        logger.info(
                            f"🧼 ResponseSanitizer aplicado - vazamentos removidos",
                            original_length=len(response.message),
                            sanitized_length=len(clean_message),
                            phone=message.phone[:4] + "****"
                        )
                    
                    # Usar auto-chunking manager para envio inteligente com mensagem limpa
                    auto_chunking = get_auto_chunking_manager()
                    
                    # Processar e enviar com chunking automático se necessário
                    send_result = await auto_chunking.process_and_send_chunks(
                        phone=message.phone,
                        text=clean_message  # ← MENSAGEM LIMPA sem vazamentos
                    )
                    
                    if send_result.get("success"):
                        if send_result.get("chunked"):
                            # Mensagem foi dividida em chunks
                            total_chunks = send_result.get("total_chunks", 1)
                            successful_chunks = send_result.get("successful_chunks", 0)
                            logger.info(
                                f"📤 Response sent to WhatsApp for {message.phone} in {total_chunks} chunk(s) "
                                f"({successful_chunks} successful)"
                            )
                        else:
                            # Mensagem enviada normalmente
                            logger.info(f"📤 Response sent to WhatsApp for {message.phone} (single message)")
                    else:
                        # Falha no envio
                        error_msg = send_result.get("error", "Unknown error")
                        logger.error(f"❌ Failed to send WhatsApp response: {error_msg}")
                        logger.error(f"   - Phone: {message.phone}")
                        logger.error(f"   - Response length: {len(response.message)} chars")
                        
                except Exception as send_error:
                    logger.error(f"❌ Error sending WhatsApp response: {send_error}")
            
            # Log successful processing
            capture_agent_event(
                "Message Processed Successfully",
                "message_processing",
                {
                    "phone": message.phone[:4] + "****",
                    "message_length": len(message.message),
                    "response_length": len(response.message) if response.message else 0
                }
            )
        else:
            logger.error(f"❌ Failed to process message for {message.phone}: {response.error}")
            
            # Capture processing error
            capture_agent_event(
                "Message Processing Failed",
                "message_processing",
                {
                    "phone": message.phone[:4] + "****",
                    "error": response.error
                },
                level="error"
            )
            
    except Exception as e:
        error_str = str(e)
        error_type = type(e).__name__
        
        # Enhanced error logging with context
        logger.error(f"Error in async message processing: {error_type}: {error_str}")
        logger.error(f"Message context: phone={message.phone[:4]}****, id={message.message_id}")
        logger.error(f"Message save context: {message_context}")
        
        # Specific error handling for known issues
        if "duplicate key value violates unique constraint" in error_str:
            logger.warning("Database constraint violation detected - likely resolved by UPSERT improvements")
        elif "WhatsAppMessage" in error_str and "conversation_id" in error_str:
            logger.warning("Pydantic field access error detected - likely resolved by context dict approach")
        elif "connection" in error_str.lower() or "timeout" in error_str.lower():
            logger.error("Network/connection issue detected - may need retry mechanism")
        
        # Capture exception with enhanced context
        capture_agent_error(
            e,
            context={
                "phase": "message_processing",
                "phone": message.phone[:4] + "****",
                "message_id": message.message_id,
                "error_type": error_type,
                "message_context": message_context,
                "has_media": bool(message.media_url),
                "instance_id": message.instance_id
            }
        )


@app.post("/send-message")
async def send_message_endpoint(request: Request):
    """
    Endpoint to send a message directly.
    Useful for testing and manual interventions.
    """
    try:
        data = await request.json()
        
        phone = data.get("phone")
        message = data.get("message")
        
        if not phone or not message:
            raise HTTPException(
                status_code=400,
                detail="Phone and message are required"
            )
        
        # Create message object
        whatsapp_msg = WhatsAppMessage(
            instance_id="manual",
            phone=phone,
            name="Manual Send",
            message=message,
            message_id=f"manual_{datetime.now().timestamp()}",
            timestamp=str(int(datetime.now().timestamp()))
        )
        
        # Process with agent
        response = await agent.process_message(whatsapp_msg)
        
        return {
            "success": response.success,
            "message": response.message if response.success else None,
            "error": response.error if not response.success else None
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def get_active_sessions():
    """Get information about active sessions."""
    try:
        count = await agent.session_manager.get_active_sessions_count()
        
        # Get session details
        sessions = []
        for phone, session in agent.session_manager.active_sessions.items():
            stats = agent.session_manager.get_session_stats(phone)
            sessions.append({
                "phone": phone,
                "conversation_id": session.get("conversation_id"),
                "state": session.get("state"),
                "duration_seconds": stats.get("duration_seconds", 0),
                "message_count": session.get("message_count", 0),
                "is_idle": stats.get("is_idle", False)
            })
        
        return {
            "total": count,
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def run():
    """Run the FastAPI application."""
    import uvicorn
    
    logger.info(f"Starting SDR Agent API on {HOST}:{PORT}")
    
    uvicorn.run(
        "agente.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    run()