"""
Webhooks API - Recebe eventos da Evolution API
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List, Union
import asyncio
import base64
import json
import re
from datetime import datetime
from loguru import logger
from app.utils.logger import emoji_logger
from app.integrations.supabase_client import supabase_client
from app.integrations.redis_client import redis_client
from app.integrations.evolution import evolution_client
from app.agents.agentic_sdr import create_agentic_sdr  # Importa o AGENTIC SDR
from app.config import settings
from app.services.message_buffer import MessageBuffer, set_message_buffer
from app.services.message_splitter import MessageSplitter, set_message_splitter
from app.utils.agno_media_detection import AGNOMediaDetector

router = APIRouter(prefix="/webhook", tags=["webhooks"])  # Mudado para /webhook (sem 's')

# REMOVIDO: Instância global do AGENTIC SDR - agora criamos nova instância por requisição

# Instâncias dos serviços de mensagem
message_buffer = None
message_splitter = None

# Instância do detector AGNO para validação de mídia
agno_detector = AGNOMediaDetector()

def sanitize_final_response(text: str) -> str:
    """
    Sanitiza agressivamente o texto final para garantir conformidade total 
    com as regras de formatação do WhatsApp, removendo todo o markdown e emojis.
    
    Args:
        text: Texto a ser sanitizado
        
    Returns:
        Texto limpo sem formatação incorreta
    """
    if not isinstance(text, str):
        return ""

    # 1. Remover emojis (padrão Unicode abrangente)
    emoji_pattern = re.compile("["
                               u"\U0001f600-\U0001f64f"  # emoticons
                               u"\U0001f300-\U0001f5ff"  # symbols & pictographs
                               u"\U0001f680-\U0001f6ff"  # transport & map symbols
                               u"\U0001f1e0-\U0001f1ff"  # flags (ios)
                               u"\u2600-\u26ff"          # miscellaneous symbols
                               u"\u2700-\u27bf"          # dingbats
                               u"\u2300-\u23ff"          # misc technical
                               u"\ufe0f"                # variation selector
                               u"\u200d"                # zero width joiner
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    # 2. Remover todo o markdown (negrito duplo, itálico, etc.)
    # Remove **, *, _, __, ~, `, etc.
    text = re.sub(r'\*{2,}', '', text)  # Remove ** (markdown duplo)
    text = re.sub(r'[_~`]', '', text)   # Remove outros markdowns

    # 3. Remover enumerações e juntar linhas
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove padrões como "1. ", "- ", "* " no início da linha
        cleaned_line = re.sub(r'^\s*\d+\.\s*|^\s*[-*]\s*', '', line.strip())
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    text = ' '.join(cleaned_lines)

    # 4. Remover espaços duplos e limpar
    text = ' '.join(text.split())

    return text.strip()

def extract_final_response(full_response: str) -> str:
    """
    Extrai apenas a resposta final das tags <RESPOSTA_FINAL>
    
    Args:
        full_response: Resposta completa do LLM incluindo raciocínio
        
    Returns:
        Apenas o conteúdo dentro das tags RESPOSTA_FINAL
    """
    try:
        # Busca o conteúdo entre as tags <RESPOSTA_FINAL> e </RESPOSTA_FINAL>
        pattern = r'<RESPOSTA_FINAL>(.*?)</RESPOSTA_FINAL>'
        match = re.search(pattern, full_response, re.DOTALL | re.IGNORECASE)
        
        if match:
            # Extrai e limpa o conteúdo
            final_response = match.group(1).strip()
            emoji_logger.system_debug(f"✅ Resposta final extraída com sucesso: {final_response[:50]}...")
            
            # 🚨 VALIDAÇÃO DE SEGURANÇA: Verificar se está pedindo dados proibidos
            forbidden_terms = [
                'cpf', 'c.p.f', 'cadastro de pessoa', 'documento',
                'rg', 'r.g', 'identidade', 'cnh', 'c.n.h',
                'carteira de motorista', 'carteira de identidade',
                'dados bancários', 'conta bancária', 'senha',
                'cartão de crédito', 'dados do cartão'
            ]
            
            response_lower = final_response.lower()
            contains_forbidden = any(term in response_lower for term in forbidden_terms)
            
            if contains_forbidden:
                emoji_logger.system_warning("🚨 ALERTA: Resposta contém solicitação de dados proibidos!")
                emoji_logger.system_warning(f"Resposta bloqueada: {final_response[:100]}...")
                
                # Retornar resposta segura
                safe_response = "Ótimo! Para eu fazer uma proposta personalizada de economia, preciso apenas saber o valor da sua conta de luz. Quanto você está pagando em média?"
                emoji_logger.system_debug(f"✅ Resposta substituída por versão segura")
                return safe_response
            
            return final_response
        else:
            # 🚨 CORREÇÃO CRÍTICA: NUNCA retornar conteúdo bruto ou raciocínio interno
            emoji_logger.system_error("extract_final_response", "🚨 TAGS <RESPOSTA_FINAL> NÃO ENCONTRADAS - BLOQUEANDO VAZAMENTO")
            emoji_logger.system_error("extract_final_response", f"📝 Conteúdo original (primeiros 200 chars): {full_response[:200]}...")
            
            # ✅ RESPOSTA SEGURA: fallback controlado que não vaza raciocínio
            safe_fallback = "Oi! Desculpe, estou processando sua mensagem. Me dê só um minutinho que já te respondo! 😊"
            
            emoji_logger.system_warning(f"🔒 Usando resposta segura para evitar vazamento de raciocínio interno")
            return safe_fallback
                
    except Exception as e:
        emoji_logger.system_error("extract_final_response", f"🚨 ERRO CRÍTICO ao extrair resposta: {e}")
        emoji_logger.system_error("extract_final_response", f"📝 Conteúdo que causou erro (primeiros 200 chars): {full_response[:200] if full_response else 'None'}...")
        
        # 🚨 CORREÇÃO CRÍTICA: NUNCA retornar resposta completa em caso de erro
        # ✅ RESPOSTA SEGURA: fallback de emergência que não vaza raciocínio
        emergency_fallback = "Oi! Tive um probleminha técnico processando sua mensagem. Me dê só um momento que já resolvo! 🔧"
        
        emoji_logger.system_warning(f"🔒 Usando resposta de emergência para evitar vazamento em caso de erro")
        return emergency_fallback

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

# Cache global do agente - SINGLETON para performance
_cached_agent = None
_agent_lock = asyncio.Lock()

async def get_agentic_agent():
    """Retorna instância única e reutilizável do agente (Singleton)"""
    global _cached_agent
    
    async with _agent_lock:
        if _cached_agent is None:
            emoji_logger.webhook_process("🚀 Criando AgenticSDR singleton pela primeira vez...")
            _cached_agent = await create_agentic_sdr()
            emoji_logger.system_ready("✅ AgenticSDR singleton criado e pronto!")
        
        return _cached_agent

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
        # PARALELIZAÇÃO MÁXIMA: Busca lead + conversa + agente em paralelo com tratamento de erros
        lead_task = asyncio.create_task(supabase_client.get_lead_by_phone(phone))
        conversation_task = asyncio.create_task(supabase_client.get_conversation_by_phone(phone))
        agent_task = asyncio.create_task(get_agentic_agent())  # Pré-carrega agente
        
        # Aguarda todas as tasks com tratamento de erros
        results = await asyncio.gather(
            lead_task,
            conversation_task,
            agent_task,
            return_exceptions=True
        )
        
        # Processar resultados com tratamento de erros
        lead_result, conv_result, agent_result = results
        
        # Verificar lead
        if isinstance(lead_result, Exception):
            emoji_logger.system_error("Lead Fetch", f"Erro ao buscar lead: {lead_result}")
            lead = None
        else:
            lead = lead_result
        
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
        
        # Preparar dados da mensagem enquanto busca conversa
        message_data = {
            "content": message_content,
            "role": "user",
            "sender": "user",
            "media_data": {
                "message_id": message_id,
                "raw_data": original_message
            }
        }
        
        # Verificar conversa
        if isinstance(conv_result, Exception):
            emoji_logger.system_error("Conversation Fetch", f"Erro ao buscar conversa: {conv_result}")
            conversation = None
        else:
            conversation = conv_result
        
        if not conversation:
            conversation = await supabase_client.create_conversation(phone, lead["id"])
        
        # OTIMIZAÇÃO: Executar em PARALELO - salvar mensagem + cache
        message_data["conversation_id"] = conversation["id"]
        
        save_tasks = [
            supabase_client.save_message(message_data),
            redis_client.cache_conversation(
                phone,
                {
                    "lead_id": lead["id"],
                    "conversation_id": conversation["id"],
                    "last_message": message_content,
                    "timestamp": datetime.now().isoformat()
                }
            )
        ]
        
        # Executar tarefas em paralelo
        await asyncio.gather(*save_tasks, return_exceptions=True)
        
        # OTIMIZAÇÃO: Agente já está sendo carregado em paralelo
        emoji_logger.webhook_process("Aguardando AGENTIC SDR pré-carregado...")
        
        # Verificar agente
        if isinstance(agent_result, Exception):
            emoji_logger.system_error("Agent Load", f"Erro ao carregar agente: {agent_result}")
            # Tentar criar agente novamente (fallback)
            try:
                agentic = await get_agentic_agent()
            except Exception as e:
                emoji_logger.system_error("Agent Fallback", f"Falha no fallback do agente: {e}")
                raise HTTPException(status_code=503, detail="Agente temporariamente indisponível")
        else:
            agentic = agent_result
            
        emoji_logger.webhook_process("AGENTIC SDR pronto para uso")
        
        # REMOVIDO: Não simular tempo de leitura quando usuário envia mensagem
        # Isso estava causando typing aparecer quando não deveria
        
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
            
            # Sempre priorizar imagem completa para melhor qualidade
            image_base64 = None
            
            
            # SEMPRE tentar baixar imagem completa primeiro para máxima qualidade
            if img_msg.get("url"):
                try:
                    emoji_logger.webhook_process(f"Baixando imagem completa de: {img_msg['url'][:50]}...")
                    
                    # Baixar imagem completa usando Evolution API
                    # Passar todos os dados necessários incluindo mediaKey para descriptografia
                    media_download_data = {
                        "mediaUrl": img_msg["url"],
                        "mediaType": "image"
                    }
                    
                    # Adicionar mediaKey se disponível
                    if img_msg.get("mediaKey"):
                        media_download_data["mediaKey"] = img_msg["mediaKey"]
                        logger.info(f"🔐 Incluindo mediaKey para descriptografia")
                    
                    image_bytes = await evolution_client.download_media(media_download_data)
                    
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
            
            # NÃO usar thumbnail - sempre exigir imagem completa
            if not image_base64:
                emoji_logger.system_error("Webhook Message Processing", "❌ Falha ao obter imagem completa")
                logger.error("Não foi possível baixar a imagem completa. Thumbnail não é aceita para garantir qualidade.")
                
                # Retornar erro informativo para o usuário
                media_data = {
                    "type": "image",
                    "error": "Não foi possível baixar a imagem. Por favor, tente enviar novamente.",
                    "data": None,
                    "has_full_image": False
                }
                return original_message, media_data
            
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
            
            # SEMPRE baixar o documento completo (thumbnails de PDF não são úteis)
            document_base64 = None
            
            if doc_msg.get("url"):
                try:
                    emoji_logger.webhook_process(f"Baixando documento: {doc_msg.get('fileName', 'documento')}")
                    
                    # Baixar documento usando Evolution API
                    # Passar todos os dados necessários incluindo mediaKey para descriptografia
                    media_download_data = {
                        "mediaUrl": doc_msg["url"],
                        "mediaType": "document"
                    }
                    
                    # Adicionar mediaKey se disponível
                    if doc_msg.get("mediaKey"):
                        media_download_data["mediaKey"] = doc_msg["mediaKey"]
                        logger.info(f"🔐 Incluindo mediaKey para descriptografia de documento")
                    
                    doc_bytes = await evolution_client.download_media(media_download_data)
                    
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
                    # Passar todos os dados necessários incluindo mediaKey para descriptografia
                    media_download_data = {
                        "mediaUrl": audio_msg["url"],
                        "mediaType": "audio"
                    }
                    
                    # Adicionar mediaKey se disponível
                    if audio_msg.get("mediaKey"):
                        media_download_data["mediaKey"] = audio_msg["mediaKey"]
                        logger.info(f"🔐 Incluindo mediaKey para descriptografia de áudio")
                    
                    audio_bytes = await evolution_client.download_media(media_download_data)
                    
                    if audio_bytes:
                        # Log dos primeiros bytes para debug
                        logger.info(f"Áudio baixado, primeiros 20 bytes (hex): {audio_bytes[:20].hex()}")
                        
                        # Validar com AGNO antes de converter para base64
                        audio_detection = agno_detector.detect_media_type(audio_bytes)
                        if audio_detection.get('detected'):
                            detected_audio_format = audio_detection.get('format', 'unknown')
                            logger.info(f"🔍 AGNO validou áudio: {detected_audio_format}")
                        elif audio_detection.get('is_encrypted'):
                            logger.warning(f"⚠️ Áudio criptografado detectado: {audio_detection.get('magic_bytes', 'N/A')}")
                            logger.info("🔓 Áudio do WhatsApp geralmente é Opus criptografado, continuando com processamento...")
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
        elif original_message.get("message", {}).get("videoMessage"):
            video_msg = original_message["message"]["videoMessage"]
            
            # ===== LOG DETALHADO PARA DEBUG =====
            emoji_logger.system_info("🎬 VÍDEO DETECTADO - Analisando estrutura...")
            logger.info(f"Campos disponíveis no videoMessage: {list(video_msg.keys())}")
            logger.info(f"Mimetype: {video_msg.get('mimetype', 'N/A')}")
            logger.info(f"Duração: {video_msg.get('seconds', 'N/A')} segundos")
            logger.info(f"Caption: {video_msg.get('caption', 'N/A')}")
            
            # Verificar se há mediaKey
            if video_msg.get("mediaKey"):
                logger.info(f"mediaKey presente: {video_msg['mediaKey'][:20]}...")
            if video_msg.get("directPath"):
                logger.info(f"directPath presente: {video_msg['directPath'][:50]}...")
            
            # Tentar baixar o vídeo completo
            video_base64 = None
            
            if video_msg.get("url"):
                try:
                    emoji_logger.webhook_process(f"Baixando vídeo")
                    
                    # Baixar vídeo usando Evolution API
                    # Passar todos os dados necessários incluindo mediaKey para descriptografia
                    media_download_data = {
                        "mediaUrl": video_msg["url"],
                        "mediaType": "video"
                    }
                    
                    # Adicionar mediaKey se disponível
                    if video_msg.get("mediaKey"):
                        media_download_data["mediaKey"] = video_msg["mediaKey"]
                        logger.info(f"🔐 Incluindo mediaKey para descriptografia de vídeo")
                    
                    video_bytes = await evolution_client.download_media(media_download_data)
                    
                    if video_bytes:
                        # Log dos primeiros bytes para debug
                        logger.info(f"Vídeo baixado, primeiros 20 bytes (hex): {video_bytes[:20].hex()}")
                        
                        # Validar com AGNO
                        video_detection = agno_detector.detect_media_type(video_bytes)
                        if video_detection.get('detected'):
                            detected_video_format = video_detection.get('format', 'unknown')
                            logger.info(f"🔍 AGNO validou vídeo: {detected_video_format}")
                        else:
                            logger.warning(f"⚠️ AGNO não reconheceu formato do vídeo: {video_detection.get('magic_bytes', 'N/A')}")
                        
                        import base64 as b64_module
                        video_base64 = b64_module.b64encode(video_bytes).decode('utf-8')
                        emoji_logger.webhook_process(f"Vídeo baixado: {len(video_base64)} caracteres")
                    else:
                        emoji_logger.system_warning("Falha ao baixar vídeo")
                        
                except Exception as download_error:
                    emoji_logger.system_warning(f"Erro ao baixar vídeo: {download_error}")
            
            media_data = {
                "type": "video",
                "mimetype": video_msg.get("mimetype", "video/mp4"),
                "caption": video_msg.get("caption", ""),
                "data": video_base64 or "",  # Vídeo completo ou vazio
                "has_content": bool(video_base64),
                "duration": video_msg.get("seconds", 0),
                "file_size": video_msg.get("fileLength", 0)
            }
        elif original_message.get("message", {}).get("stickerMessage"):
            sticker_msg = original_message["message"]["stickerMessage"]
            
            # ===== LOG DETALHADO PARA DEBUG =====
            emoji_logger.system_info("🎨 STICKER DETECTADO - Analisando estrutura...")
            logger.info(f"Campos disponíveis no stickerMessage: {list(sticker_msg.keys())}")
            logger.info(f"Mimetype: {sticker_msg.get('mimetype', 'N/A')}")
            logger.info(f"É animado: {sticker_msg.get('isAnimated', False)}")
            
            # Verificar se há mediaKey
            if sticker_msg.get("mediaKey"):
                logger.info(f"mediaKey presente: {sticker_msg['mediaKey'][:20]}...")
            if sticker_msg.get("directPath"):
                logger.info(f"directPath presente: {sticker_msg['directPath'][:50]}...")
            
            # Tentar baixar o sticker
            sticker_base64 = None
            
            if sticker_msg.get("url"):
                try:
                    emoji_logger.webhook_process(f"Baixando sticker/figurinha")
                    
                    # Baixar sticker usando Evolution API
                    # Passar todos os dados necessários incluindo mediaKey para descriptografia
                    media_download_data = {
                        "mediaUrl": sticker_msg["url"],
                        "mediaType": "sticker"  # WhatsApp usa "WhatsApp Image Keys" para stickers
                    }
                    
                    # Adicionar mediaKey se disponível
                    if sticker_msg.get("mediaKey"):
                        media_download_data["mediaKey"] = sticker_msg["mediaKey"]
                        logger.info(f"🔐 Incluindo mediaKey para descriptografia de sticker")
                    
                    sticker_bytes = await evolution_client.download_media(media_download_data)
                    
                    if sticker_bytes:
                        # Log dos primeiros bytes para debug
                        logger.info(f"Sticker baixado, primeiros 20 bytes (hex): {sticker_bytes[:20].hex()}")
                        
                        # Validar com AGNO
                        sticker_detection = agno_detector.detect_media_type(sticker_bytes)
                        if sticker_detection.get('detected'):
                            detected_sticker_format = sticker_detection.get('format', 'unknown')
                            logger.info(f"🔍 AGNO validou sticker: {detected_sticker_format}")
                        else:
                            logger.warning(f"⚠️ AGNO não reconheceu formato do sticker: {sticker_detection.get('magic_bytes', 'N/A')}")
                        
                        import base64 as b64_module
                        sticker_base64 = b64_module.b64encode(sticker_bytes).decode('utf-8')
                        emoji_logger.webhook_process(f"Sticker baixado: {len(sticker_base64)} caracteres")
                    else:
                        emoji_logger.system_warning("Falha ao baixar sticker")
                        
                except Exception as download_error:
                    emoji_logger.system_warning(f"Erro ao baixar sticker: {download_error}")
            
            media_data = {
                "type": "sticker",
                "mimetype": sticker_msg.get("mimetype", "image/webp"),
                "data": sticker_base64 or "",  # Sticker completo ou vazio
                "has_content": bool(sticker_base64),
                "is_animated": sticker_msg.get("isAnimated", False),
                "file_size": sticker_msg.get("fileLength", 0)
            }
        
        # Processa mensagem com análise contextual inteligente
        emoji_logger.webhook_process(f"Chamando AGENTIC SDR para processar: {message_content[:50]}...")
        
        # Obter estado emocional atual da conversa
        current_emotional_state = await supabase_client.get_conversation_emotional_state(conversation["id"])
        
        # Variável para capturar erro do agente
        agent_error = None
        
        try:
            response = await agentic.process_message(
                phone=phone,
                message=message_content,
                lead_data=lead,
                conversation_id=conversation["id"],
                media=media_data,
                message_id=message_id,
                current_emotional_state=current_emotional_state
            )
            
            # Verificar se é estrutura enriquecida ou string simples (compatibilidade)
            if isinstance(response, dict):
                response_text = response.get("text", "")
                reaction = response.get("reaction")
                reply_to = response.get("reply_to")
            else:
                # Compatibilidade com resposta string simples
                response_text = response
                reaction = None
                reply_to = None
            
            # ===== EXTRAÇÃO DA RESPOSTA FINAL =====
            # Extrai apenas o conteúdo dentro das tags <RESPOSTA_FINAL>
            response_text = extract_final_response(response_text)
            # ======================================
            
            # ===== SANITIZAÇÃO AGRESSIVA (CAMADA 2 CRÍTICA) =====
            # Remove emojis, markdown duplo, enumerações e formata para WhatsApp
            response_text = sanitize_final_response(response_text)
            # ==================================================
            
            emoji_logger.webhook_process(f"Resposta recebida do AGENTIC SDR: {response_text[:100] if response_text else 'NENHUMA'}...")
            
        except Exception as e:
            agent_error = e  # Captura o erro para uso posterior
            emoji_logger.system_error("AGENTIC SDR", f"Erro ao processar: {agent_error}")
            
            # RETRY INTELIGENTE: Tentar novamente com nova instância
            retry_count = 0
            max_retries = 3
            response = None
            
            while retry_count < max_retries and response is None:
                retry_count += 1
                emoji_logger.webhook_process(f"Tentando novamente ({retry_count}/{max_retries})...")
                
                try:
                    # Criar NOVA instância para o retry - limpa qualquer estado problemático
                    new_agent = await create_agentic_sdr()
                    
                    # Pequeno delay exponencial entre tentativas
                    await asyncio.sleep(retry_count * 0.5)
                    
                    # Tentar processar novamente
                    response = await new_agent.process_message(
                        phone=phone,
                        message=message_content,
                        lead_data=lead,
                        conversation_id=conversation["id"],
                        media=media_data,
                        message_id=message_id
                    )
                    
                    if response:
                        emoji_logger.webhook_process(f"Sucesso no retry {retry_count}!")
                        break
                        
                except Exception as retry_error:
                    emoji_logger.system_warning(f"Retry {retry_count} falhou: {retry_error}")
                    continue
        
        # Envia resposta
        if response:
            # response agora pode ser dict ou string (compatibilidade)
            if isinstance(response, dict):
                response_text = response.get("text", "")
                # reaction e reply_to já foram extraídos acima
            else:
                response_text = response
            
            # ===== EXTRAÇÃO DA RESPOSTA FINAL =====
            # Extrai apenas o conteúdo dentro das tags <RESPOSTA_FINAL>
            response_text = extract_final_response(response_text)
            # ======================================
            
            # ===== SANITIZAÇÃO AGRESSIVA (CAMADA 2 CRÍTICA) =====
            # Remove emojis, markdown duplo, enumerações e formata para WhatsApp
            response_text = sanitize_final_response(response_text)
            # ==================================================
                
            emoji_logger.webhook_process(f"Enviando resposta para {phone}")
            
            # Enviar reação se houver
            if reaction:
                try:
                    emoji_logger.webhook_process(f"Tentando enviar reação '{reaction}' para mensagem ID: {message_id}")
                    reaction_result = await evolution_client.send_reaction(phone, message_id, reaction)
                    emoji_logger.webhook_process(f"Reação enviada com sucesso: {reaction}")
                    emoji_logger.system_debug(f"Resposta da API para reação: {reaction_result}")
                    # Pequeno delay após reação
                    await asyncio.sleep(0.5)
                except Exception as reaction_error:
                    emoji_logger.system_error("Reaction Send", f"Erro ao enviar reação '{reaction}': {reaction_error}")
                    emoji_logger.system_debug(f"Message ID usado: {message_id}")
                    emoji_logger.system_debug(f"Phone usado: {phone}")
            
            # Delay antes de enviar mídia se houver
            if media_data and settings.delay_before_media > 0:
                await asyncio.sleep(settings.delay_before_media)
            
            # Se o splitter está habilitado e a mensagem é longa, divide em chunks
            if settings.enable_message_splitter and len(response_text) > settings.message_max_length:
                splitter = get_message_splitter_instance()
                chunks = splitter.split_message(response_text)
                
                emoji_logger.system_info(
                    f"Mensagem dividida em {len(chunks)} partes",
                    phone=phone,
                    original_length=len(response_text)
                )
                
                # Envia cada chunk com delay entre eles
                for i, chunk in enumerate(chunks):
                    try:
                        # Delay entre chunks (exceto o primeiro)
                        if i > 0 and settings.message_chunk_delay > 0:
                            await asyncio.sleep(settings.message_chunk_delay)
                        
                        # Para chunks, usar reply apenas no primeiro
                        if i == 0 and reply_to:
                            result = await evolution_client.send_reply(
                                phone,
                                reply_to,
                                chunk,
                                simulate_typing=True
                            )
                        else:
                            result = await evolution_client.send_text_message(
                                phone,
                                chunk,
                                delay=None,  # Deixar o método calcular automaticamente
                                simulate_typing=True
                            )
                        emoji_logger.evolution_send(phone, "text", preview=chunk[:50])
                        emoji_logger.system_info(f"Chunk {i+1}/{len(chunks)} enviado. ID: {result.get('key', {}).get('id', 'N/A')}")
                        
                    except Exception as send_error:
                        emoji_logger.system_error("Evolution API", f"Erro ao enviar chunk {i+1}: {send_error}")
                        # Continua tentando enviar os próximos chunks
            else:
                # Envia mensagem única (sem dividir)
                try:
                    # Usar reply se foi solicitado
                    if reply_to:
                        result = await evolution_client.send_reply(
                            phone,
                            reply_to,
                            response_text,
                            simulate_typing=True
                        )
                    else:
                        result = await evolution_client.send_text_message(
                            phone,
                            response_text,
                            delay=None,  # Deixar o método calcular automaticamente
                            simulate_typing=True
                        )
                    emoji_logger.evolution_send(phone, "text", preview=response_text[:50])
                    emoji_logger.system_info(f"Mensagem enviada com sucesso. ID: {result.get('key', {}).get('id', 'N/A')}")
                    
                except Exception as send_error:
                    emoji_logger.system_error("Evolution API", f"Erro ao enviar mensagem: {send_error}")
                    # Re-lançar para não silenciar o erro
                    raise
            
            # Delay após mídia se houver
            if media_data and settings.delay_after_media > 0:
                await asyncio.sleep(settings.delay_after_media)
            
            # Salva resposta no banco (usando texto sanitizado)
            await supabase_client.save_message({
                "conversation_id": conversation["id"],
                "content": response_text,  # CORREÇÃO: Usar texto sanitizado em vez do response bruto
                "role": "assistant",  # Campo obrigatório
                "sender": "assistant",
                "media_data": {  # Usar media_data em vez de metadata
                    "agent": "agentic_sdr",
                    "context_analyzed": True,
                    "messages_analyzed": 100,
                    "sanitized": True  # Marcador de que o texto foi sanitizado
                }
            })
            
            # Atualiza analytics
            await redis_client.increment_counter("messages_processed")
            await redis_client.increment_counter(f"messages:{phone}")
            
            emoji_logger.webhook_process("Mensagem processada com sucesso!")
            
            # 🚀 FOLLOW-UP POR INATIVIDADE - "O SIMPLES FUNCIONA SEMPRE"
            # Agendar follow-up de 30 minutos para verificar se usuário respondeu
            await _schedule_inactivity_followup(lead["id"], phone, conversation["id"])
            
        else:
            emoji_logger.system_warning(f"Nenhuma resposta gerada para {phone} após todas as tentativas")
            
            # Resposta contextual inteligente baseada no erro
            if agent_error and evolution_client:
                contextual_response = None
                
                if "timeout" in str(agent_error).lower():
                    contextual_response = "Oi! Vi sua mensagem... só um minutinho que te respondo"
                elif "rate" in str(agent_error).lower() or "limit" in str(agent_error).lower():
                    contextual_response = "Nossa, muita gente interessada em energia solar agora! Me dá uns minutinhos que já te respondo"
                elif "connection" in str(agent_error).lower():
                    contextual_response = "Eu não entendi rs. Pode explicar sua pergunta?"
                
                # Envia resposta contextual se disponível
                if contextual_response:
                    try:
                        # Sanitizar resposta contextual por segurança
                        contextual_response = sanitize_final_response(contextual_response)
                        
                        # CORREÇÃO: Usar método correto do evolution_client
                        await evolution_client.send_text_message(
                            phone,
                            contextual_response,
                            simulate_typing=False,  # NÃO simular typing para respostas de erro
                            delay=0  # Sem delay
                        )
                        emoji_logger.webhook_process("Resposta contextual enviada")
                    except Exception as e:
                        emoji_logger.system_warning(f"Falha ao enviar resposta contextual: {e}")
        
    except Exception as e:
        emoji_logger.system_error("Agent Message Processing", str(e))
        logger.exception("Erro detalhado no processamento com agente:")
        
        # Última tentativa de recuperação com nova instância
        try:
            emoji_logger.webhook_process("Tentativa final de recuperação...")
            recovery_agent = await create_agentic_sdr()
            await asyncio.sleep(1)  # Delay de 1 segundo
            
            response = await recovery_agent.process_message(
                phone=phone,
                message=message_content,
                lead_data=lead,
                conversation_id=conversation["id"],
                media=media_data,
                message_id=message_id
            )
            
            if response:
                # Processar resposta recuperada
                if isinstance(response, dict):
                    response_text = response.get("text", "")
                else:
                    response_text = response
                
                # ===== EXTRAÇÃO DA RESPOSTA FINAL =====
                # Extrai apenas o conteúdo dentro das tags <RESPOSTA_FINAL>
                response_text = extract_final_response(response_text)
                # ======================================
                
                # ===== SANITIZAÇÃO AGRESSIVA (CAMADA 2 CRÍTICA) =====
                # Remove emojis, markdown duplo, enumerações e formata para WhatsApp
                response_text = sanitize_final_response(response_text)
                # ==================================================
                    
                if response_text:
                    # CORREÇÃO: Usar método correto do evolution_client
                    await evolution_client.send_text_message(
                        phone,
                        response_text,
                        simulate_typing=True,  # Simular typing normal para resposta do agente
                        delay=0  # Sem delay adicional
                    )
                    emoji_logger.webhook_process("Recuperação bem-sucedida!")
                    
        except Exception as recovery_error:
            emoji_logger.system_error("Recovery failed", str(recovery_error))
            # Falha silenciosa - melhor não responder do que parecer robô

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

# 🚀 FOLLOW-UP POR INATIVIDADE - IMPLEMENTAÇÃO ULTRA-SIMPLES
async def _schedule_inactivity_followup(lead_id: str, phone: str, conversation_id: str):
    """
    Agenda follow-up de inatividade de 30 minutos após agente responder
    Usa infraestrutura existente - ZERO COMPLEXIDADE
    """
    try:
        from datetime import timedelta
        from app.utils.time_utils import get_business_aware_datetime
        
        # CORREÇÃO: Agendamento respeitando horário comercial e fuso horário correto
        scheduled_time = get_business_aware_datetime(minutes_from_now=30)
        
        # Buscar última mensagem do usuário para armazenar como referência
        last_user_message_query = supabase_client.client.table("messages")\
            .select("created_at")\
            .eq("conversation_id", conversation_id)\
            .eq("sender", "user")\
            .order("created_at", desc=True)\
            .limit(1)
        
        last_user_msg = last_user_message_query.execute()
        last_user_time = None
        if last_user_msg.data:
            last_user_time = last_user_msg.data[0]["created_at"]
        
        # Criar registro na tabela follow_ups (usa estrutura existente)
        # CRUCIAL: Timestamp atual da resposta do agente para validação de inatividade
        agent_response_timestamp = datetime.now().isoformat()
        
        followup_data = {
            "lead_id": lead_id,
            "scheduled_at": scheduled_time.isoformat(),
            "type": "reengagement",  # Tipo na tabela  
            "follow_up_type": "IMMEDIATE_REENGAGEMENT",  # Subtipo (template)
            "message": "",  # CORREÇÃO: Vazio para usar mensagem inteligente gerada pelo followup_executor
            "status": "pending",
            "priority": "high",
            "metadata": {
                "phone": phone,
                "conversation_id": conversation_id,
                "trigger": "agent_response_30min",
                "last_user_message_at": last_user_time,
                "agent_response_timestamp": agent_response_timestamp,  # NOVO: Para validação
                "scheduled_reason": "User inactivity check after agent response",
                "message_type": "intelligent_reengagement"  # Flag para usar IA
            }
        }
        
        result = supabase_client.client.table("follow_ups").insert(followup_data).execute()
        
        if result.data:
            emoji_logger.system_info(f"⏰ Follow-up de 30min agendado para {phone} às {scheduled_time.strftime('%H:%M')}")
            
            # NÃO agendar follow-up de 24h imediatamente
            # Será agendado pelo próprio FollowUpExecutorService se o usuário não responder ao de 30min
            emoji_logger.system_info(f"📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min")
            
        else:
            emoji_logger.system_error("Follow-up", "Falha ao agendar follow-up de inatividade")
            
    except Exception as e:
        emoji_logger.system_error("Follow-up", f"Erro ao agendar follow-up: {e}")
        # Não re-lançar erro para não quebrar o fluxo principal

@router.post("/test")
async def test_webhook(data: Dict[str, Any]):
    """
    Endpoint de teste para webhook
    """
    logger.info(f"Teste de webhook recebido: {data}")
    return {"status": "ok", "received": data}