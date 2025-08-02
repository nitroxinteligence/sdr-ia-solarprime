# 04. API e Webhooks - FastAPI + Evolution API

Este documento detalha a implementação da API REST com FastAPI e a integração com Evolution API para processamento de mensagens WhatsApp em produção.

## 📋 Índice

1. [Arquitetura da API](#1-arquitetura-da-api)
2. [Configuração do FastAPI](#2-configuração-do-fastapi)
3. [Evolution API Setup](#3-evolution-api-setup)
4. [Sistema de Webhooks](#4-sistema-de-webhooks)
5. [Processamento de Mensagens](#5-processamento-de-mensagens)
6. [Filas com Celery](#6-filas-com-celery)
7. [Segurança e Autenticação](#7-segurança-e-autenticação)
8. [Rate Limiting e Throttling](#8-rate-limiting-e-throttling)
9. [Monitoramento e Logs](#9-monitoramento-e-logs)
10. [Testes e Validação](#10-testes-e-validação)

---

## 1. Arquitetura da API

### 1.1 Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                    ARQUITETURA API                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  WhatsApp → Evolution API → Webhook → FastAPI → Queue  │
│                                           ↓             │
│                                    Celery Worker        │
│                                           ↓             │
│                                     Agente AGnO         │
│                                           ↓             │
│  WhatsApp ← Evolution API ← Response ← FastAPI         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Componentes:                                           │
│  • FastAPI (API REST)                                   │
│  • Uvicorn (ASGI Server)                               │
│  • Celery (Task Queue)                                 │
│  • Redis (Message Broker)                               │
│  • Evolution API (WhatsApp)                            │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Fluxo de Dados

1. **Recepção**: Evolution API recebe mensagem do WhatsApp
2. **Webhook**: Envia para endpoint FastAPI
3. **Validação**: API valida origem e conteúdo
4. **Queue**: Mensagem enviada para fila Celery
5. **Processamento**: Worker processa com agente
6. **Resposta**: Envia resposta via Evolution API

---

## 2. Configuração do FastAPI

### 2.1 Estrutura Base da API

```python
# api/main.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional

from api.routes import webhooks, health, leads, analytics
from config.settings import settings
from services.redis_service import redis_client
from services.database import init_db

logger = logging.getLogger(__name__)

# Lifespan para startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação SDR SolarPrime...")
    
    # Inicializar banco de dados
    await init_db()
    
    # Conectar Redis
    await redis_client.connect()
    
    # Verificar Evolution API
    from services.evolution_api import check_connection
    if not await check_connection():
        logger.warning("Evolution API não está acessível")
    
    logger.info("Aplicação iniciada com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")
    await redis_client.close()
    logger.info("Aplicação encerrada")

# Criar aplicação
app = FastAPI(
    title="SDR IA SolarPrime API",
    description="API do Agente de Vendas Inteligente para Energia Solar",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de segurança
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Incluir rotas
app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# Tratamento global de erros
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": "Ocorreu um erro inesperado",
        "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "app": "SDR IA SolarPrime",
        "version": "1.0.0",
        "status": "operational"
    }
```

### 2.2 Configurações de Produção

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Ambiente
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["https://solarprime.com.br"]
    ALLOWED_HOSTS: List[str] = ["api.solarprime.com.br", "localhost"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Webhook Security
    WEBHOOK_SECRET: str
    EVOLUTION_API_KEY: str
    
    # Evolution API
    EVOLUTION_API_URL: str = "http://localhost:8080"
    EVOLUTION_INSTANCE_NAME: str = "solarprime"
    EVOLUTION_INSTANCE_TOKEN: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    REDIS_TIMEOUT: int = 5
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_TIMEOUT: int = 300  # 5 minutos
    
    # Database
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Gemini
    GEMINI_API_KEY: str
    
    # Kommo
    KOMMO_CLIENT_ID: str
    KOMMO_CLIENT_SECRET: str
    KOMMO_SUBDOMAIN: str
    
    # Business Logic
    AI_RESPONSE_DELAY_SECONDS: int = 2
    TYPING_SIMULATION_ENABLED: bool = True
    MAX_MESSAGE_LENGTH: int = 4096
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2.3 Middleware de Segurança

```python
# api/middleware/security.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import uuid
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de segurança para produção"""
    
    async def dispatch(self, request: Request, call_next):
        # Adicionar request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Adicionar headers de segurança
        start_time = time.time()
        
        # Log da requisição
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host} [ID: {request_id}]"
        )
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar headers de segurança
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Log do tempo de resposta
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(
            f"Response: {response.status_code} "
            f"[{process_time:.3f}s] [ID: {request_id}]"
        )
        
        return response

class WebhookSignatureMiddleware(BaseHTTPMiddleware):
    """Valida assinatura dos webhooks"""
    
    def __init__(self, app, webhook_secret: str):
        super().__init__(app)
        self.webhook_secret = webhook_secret
    
    async def dispatch(self, request: Request, call_next):
        # Aplicar apenas em rotas de webhook
        if request.url.path.startswith("/webhook"):
            # Verificar assinatura
            signature = request.headers.get("X-Webhook-Signature")
            
            if not signature:
                logger.warning(f"Webhook sem assinatura de {request.client.host}")
                raise HTTPException(status_code=401, detail="Missing signature")
            
            # Calcular assinatura esperada
            body = await request.body()
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.error(f"Assinatura inválida de {request.client.host}")
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Recriar request com body
            async def receive():
                return {"type": "http.request", "body": body}
            
            request._receive = receive
        
        return await call_next(request)
```

---

## 3. Evolution API Setup

### 3.1 Cliente Evolution API

```python
# services/evolution_api.py
import httpx
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import asyncio
import base64
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)

class EvolutionAPIClient:
    """Cliente para integração com Evolution API"""
    
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.EVOLUTION_INSTANCE_NAME
        self.instance_token = settings.EVOLUTION_INSTANCE_TOKEN
        
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Cliente HTTP com retry
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def check_connection(self) -> bool:
        """Verifica conexão com Evolution API"""
        try:
            response = await self.client.get("/instance/connectionState")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao verificar Evolution API: {e}")
            return False
    
    async def send_text_message(
        self,
        phone: str,
        message: str,
        quoted_message_id: Optional[str] = None,
        delay: Optional[int] = None
    ) -> Dict[str, Any]:
        """Envia mensagem de texto"""
        
        # Formatar número
        formatted_phone = self._format_phone_number(phone)
        
        payload = {
            "number": formatted_phone,
            "text": message,
            "delay": delay or settings.AI_RESPONSE_DELAY_SECONDS * 1000
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
        
        if not settings.TYPING_SIMULATION_ENABLED:
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
        
        try:
            response = await self.client.post(
                f"/chat/getBase64/{self.instance_name}",
                json={"messageId": message_id}
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
    
    async def create_webhook(
        self,
        webhook_url: str,
        events: List[str] = None
    ) -> Dict[str, Any]:
        """Configura webhook"""
        
        if events is None:
            events = [
                "MESSAGES_UPSERT",
                "CONNECTION_UPDATE",
                "MESSAGES_UPDATE"
            ]
        
        payload = {
            "url": webhook_url,
            "webhook_by_events": False,
            "events": events
        }
        
        try:
            response = await self.client.put(
                f"/webhook/set/{self.instance_name}",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Webhook configurado: {webhook_url}")
            return response.json()
            
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

# Instância global
evolution_client = EvolutionAPIClient()
```

### 3.2 Configuração de Webhooks

```python
# scripts/setup_webhooks.py
import asyncio
import os
from dotenv import load_dotenv
from services.evolution_api import EvolutionAPIClient

load_dotenv()

async def setup_webhooks():
    """Configura webhooks na Evolution API"""
    
    webhook_url = f"{os.getenv('API_BASE_URL')}/webhook/whatsapp"
    
    async with EvolutionAPIClient() as client:
        # Configurar webhook
        result = await client.create_webhook(
            webhook_url=webhook_url,
            events=[
                "MESSAGES_UPSERT",      # Novas mensagens
                "MESSAGES_UPDATE",      # Atualizações de status
                "CONNECTION_UPDATE",    # Status da conexão
                "GROUP_UPDATE",         # Atualizações de grupos
                "GROUP_PARTICIPANTS_UPDATE"  # Participantes de grupos
            ]
        )
        
        print(f"Webhook configurado: {result}")
        
        # Verificar status da conexão
        if await client.check_connection():
            print("✅ Evolution API conectada e funcionando!")
        else:
            print("❌ Evolution API não está conectada")

if __name__ == "__main__":
    asyncio.run(setup_webhooks())
```

---

## 4. Sistema de Webhooks

### 4.1 Roteador de Webhooks

```python
# api/routes/webhooks.py
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

from services.webhook_processor import WebhookProcessor
from services.tasks import process_message_task
from models.webhook import WebhookPayload, MessageEvent
from api.dependencies import verify_webhook_signature

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: Dict[str, Any],
    _: None = Depends(verify_webhook_signature)
):
    """Recebe webhooks da Evolution API"""
    
    try:
        # Log do webhook recebido
        logger.info(f"Webhook recebido: {payload.get('event', 'unknown')}")
        
        # Processar diferentes tipos de eventos
        event_type = payload.get("event")
        
        if event_type == "MESSAGES_UPSERT":
            # Nova mensagem recebida
            await handle_new_message(payload, background_tasks)
            
        elif event_type == "MESSAGES_UPDATE":
            # Atualização de status de mensagem
            await handle_message_update(payload)
            
        elif event_type == "CONNECTION_UPDATE":
            # Mudança no status da conexão
            await handle_connection_update(payload)
            
        elif event_type in ["GROUP_UPDATE", "GROUP_PARTICIPANTS_UPDATE"]:
            # Atualizações de grupo
            await handle_group_update(payload)
        
        else:
            logger.warning(f"Evento não tratado: {event_type}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}", exc_info=True)
        # Retornar sucesso para evitar retry do Evolution
        return {"status": "success", "error": str(e)}

async def handle_new_message(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Processa nova mensagem"""
    
    data = payload.get("data", {})
    
    # Ignorar mensagens próprias
    if data.get("key", {}).get("fromMe", False):
        logger.debug("Ignorando mensagem própria")
        return
    
    # Extrair informações da mensagem
    message_data = {
        "id": data.get("key", {}).get("id"),
        "from": data.get("key", {}).get("remoteJid"),
        "timestamp": data.get("messageTimestamp"),
        "pushName": data.get("pushName"),
        "message": data.get("message", {}),
        "instanceName": payload.get("instance")
    }
    
    # Validar dados essenciais
    if not all([message_data["id"], message_data["from"]]):
        logger.warning("Mensagem sem dados essenciais")
        return
    
    # Ignorar grupos (por enquanto)
    if "@g.us" in message_data["from"]:
        logger.debug("Ignorando mensagem de grupo")
        return
    
    # Enviar para fila de processamento
    process_message_task.delay(message_data)
    
    logger.info(f"Mensagem {message_data['id']} enviada para processamento")

async def handle_message_update(payload: Dict[str, Any]):
    """Processa atualização de status de mensagem"""
    
    data = payload.get("data", [])
    
    for update in data:
        message_id = update.get("key", {}).get("id")
        status = update.get("update", {}).get("status")
        
        if message_id and status:
            # Atualizar status no banco
            from services.message_service import update_message_status
            await update_message_status(message_id, status)
            
            logger.debug(f"Status da mensagem {message_id}: {status}")

async def handle_connection_update(payload: Dict[str, Any]):
    """Processa mudança de status da conexão"""
    
    data = payload.get("data", {})
    state = data.get("state")
    
    logger.info(f"Status da conexão: {state}")
    
    # Notificar se desconectado
    if state == "close":
        # Enviar alerta
        logger.error("WhatsApp desconectado!")
        # TODO: Implementar notificação para admin

async def handle_group_update(payload: Dict[str, Any]):
    """Processa atualizações de grupo"""
    
    # Por enquanto, apenas logar
    event_type = payload.get("event")
    group_id = payload.get("data", {}).get("id")
    
    logger.info(f"Atualização de grupo {group_id}: {event_type}")
```

### 4.2 Processador de Mensagens

```python
# services/webhook_processor.py
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import json

from services.transcription_service import TranscriptionService
from services.ocr_service import OCRService
from services.evolution_api import evolution_client

logger = logging.getLogger(__name__)

class WebhookProcessor:
    """Processa diferentes tipos de mensagens do webhook"""
    
    def __init__(self):
        self.transcription_service = TranscriptionService()
        self.ocr_service = OCRService()
    
    async def process_message(
        self,
        message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Processa mensagem e extrai conteúdo"""
        
        message = message_data.get("message", {})
        processed = {
            "id": message_data["id"],
            "from": message_data["from"],
            "sender_name": message_data.get("pushName", ""),
            "timestamp": message_data["timestamp"],
            "type": "text",
            "content": "",
            "media_url": None,
            "metadata": {}
        }
        
        # Processar diferentes tipos de mensagem
        if "conversation" in message:
            # Mensagem de texto simples
            processed["content"] = message["conversation"]
            
        elif "extendedTextMessage" in message:
            # Mensagem de texto com metadados
            processed["content"] = message["extendedTextMessage"]["text"]
            
        elif "imageMessage" in message:
            # Mensagem de imagem
            processed["type"] = "image"
            processed["content"] = message["imageMessage"].get("caption", "")
            processed["media_url"] = await self._process_media(
                message_data["id"],
                "image"
            )
            
            # Tentar OCR se for conta de luz
            if "conta" in processed["content"].lower() or "luz" in processed["content"].lower():
                ocr_text = await self.ocr_service.extract_text(processed["media_url"])
                if ocr_text:
                    processed["metadata"]["ocr_text"] = ocr_text
            
        elif "audioMessage" in message:
            # Mensagem de áudio
            processed["type"] = "audio"
            audio_url = await self._process_media(message_data["id"], "audio")
            
            # Transcrever áudio
            transcription = await self.transcription_service.transcribe(audio_url)
            processed["content"] = transcription
            processed["media_url"] = audio_url
            processed["metadata"]["duration"] = message["audioMessage"].get("seconds", 0)
            
        elif "documentMessage" in message:
            # Documento
            processed["type"] = "document"
            processed["content"] = message["documentMessage"].get("caption", "")
            processed["media_url"] = await self._process_media(
                message_data["id"],
                "document"
            )
            processed["metadata"]["filename"] = message["documentMessage"].get("fileName", "")
            processed["metadata"]["mimetype"] = message["documentMessage"].get("mimetype", "")
            
        elif "videoMessage" in message:
            # Vídeo
            processed["type"] = "video"
            processed["content"] = message["videoMessage"].get("caption", "")
            processed["media_url"] = await self._process_media(
                message_data["id"],
                "video"
            )
            
        elif "locationMessage" in message:
            # Localização
            processed["type"] = "location"
            loc = message["locationMessage"]
            processed["content"] = f"Localização: {loc.get('latitude')}, {loc.get('longitude')}"
            processed["metadata"]["location"] = {
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
                "name": loc.get("name", "")
            }
        
        else:
            # Tipo não suportado
            logger.warning(f"Tipo de mensagem não suportado: {list(message.keys())}")
            return None
        
        return processed
    
    async def _process_media(
        self,
        message_id: str,
        media_type: str
    ) -> Optional[str]:
        """Processa e salva mídia"""
        
        try:
            # Baixar mídia
            media_data = await evolution_client.download_media(message_id)
            
            if not media_data:
                logger.error(f"Falha ao baixar mídia {message_id}")
                return None
            
            # Salvar temporariamente
            # Em produção, usar S3 ou similar
            import tempfile
            import uuid
            
            extension = {
                "image": ".jpg",
                "audio": ".ogg",
                "video": ".mp4",
                "document": ".pdf"
            }.get(media_type, ".bin")
            
            filename = f"{uuid.uuid4()}{extension}"
            filepath = f"/tmp/{filename}"
            
            with open(filepath, "wb") as f:
                f.write(media_data)
            
            logger.info(f"Mídia salva: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao processar mídia: {e}")
            return None
```

---

## 5. Processamento de Mensagens

### 5.1 Serviço de Transcrição

```python
# services/transcription_service.py
import os
import logging
from typing import Optional
import openai
from pathlib import Path

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Serviço de transcrição de áudio"""
    
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.max_file_size = 25 * 1024 * 1024  # 25MB
    
    async def transcribe(
        self,
        audio_path: str,
        language: str = "pt"
    ) -> str:
        """Transcreve áudio usando Whisper"""
        
        try:
            # Verificar arquivo
            if not os.path.exists(audio_path):
                logger.error(f"Arquivo não encontrado: {audio_path}")
                return "[Erro ao transcrever áudio]"
            
            file_size = os.path.getsize(audio_path)
            if file_size > self.max_file_size:
                logger.error(f"Arquivo muito grande: {file_size} bytes")
                return "[Áudio muito longo para transcrição]"
            
            # Transcrever com Whisper
            with open(audio_path, "rb") as audio_file:
                response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            transcription = response.text
            logger.info(f"Áudio transcrito com sucesso: {len(transcription)} caracteres")
            
            return transcription
            
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {e}")
            return "[Erro ao transcrever áudio]"
```

### 5.2 Serviço de OCR

```python
# services/ocr_service.py
import os
import logging
from typing import Optional, Dict, Any
import pytesseract
from PIL import Image
import re

logger = logging.getLogger(__name__)

class OCRService:
    """Serviço de OCR para extrair texto de imagens"""
    
    def __init__(self):
        # Configurar Tesseract
        self.lang = "por"  # Português
    
    async def extract_text(
        self,
        image_path: str
    ) -> Optional[str]:
        """Extrai texto de imagem"""
        
        try:
            if not os.path.exists(image_path):
                logger.error(f"Imagem não encontrada: {image_path}")
                return None
            
            # Abrir imagem
            image = Image.open(image_path)
            
            # Aplicar OCR
            text = pytesseract.image_to_string(image, lang=self.lang)
            
            logger.info(f"OCR extraiu {len(text)} caracteres")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erro no OCR: {e}")
            return None
    
    async def extract_bill_value(
        self,
        image_path: str
    ) -> Optional[float]:
        """Extrai valor da conta de luz"""
        
        text = await self.extract_text(image_path)
        
        if not text:
            return None
        
        # Padrões para encontrar valor
        patterns = [
            r'Total\s*a\s*pagar[:\s]*R\$?\s*([0-9.,]+)',
            r'Valor\s*total[:\s]*R\$?\s*([0-9.,]+)',
            r'Total[:\s]*R\$?\s*([0-9.,]+)',
            r'R\$\s*([0-9.,]+)\s*(?:total|a\s*pagar)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                # Converter para float
                value_str = value_str.replace('.', '').replace(',', '.')
                
                try:
                    value = float(value_str)
                    logger.info(f"Valor extraído da conta: R$ {value}")
                    return value
                except ValueError:
                    continue
        
        logger.warning("Não foi possível extrair valor da conta")
        return None
```

---

## 6. Filas com Celery

### 6.1 Configuração do Celery

```python
# services/celery_app.py
from celery import Celery
from celery.signals import setup_logging
import logging
from config.settings import settings

# Criar aplicação Celery
celery_app = Celery(
    "sdr_solarprime",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["services.tasks"]
)

# Configurações
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    
    # Configurações de performance
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    
    # Retry
    task_default_retry_delay=60,  # 1 minuto
    task_max_retries=3,
    
    # Timeouts
    task_soft_time_limit=300,  # 5 minutos
    task_time_limit=600,       # 10 minutos
    
    # Beat schedule para tarefas agendadas
    beat_schedule={
        "check-pending-followups": {
            "task": "services.tasks.check_pending_followups",
            "schedule": 60.0,  # A cada minuto
        },
        "generate-weekly-report": {
            "task": "services.tasks.generate_weekly_report",
            "schedule": {
                "type": "crontab",
                "day_of_week": settings.REPORT_DAY_OF_WEEK,
                "hour": settings.REPORT_TIME.split(":")[0],
                "minute": settings.REPORT_TIME.split(":")[1]
            }
        },
        "cleanup-old-media": {
            "task": "services.tasks.cleanup_old_media",
            "schedule": 3600.0,  # A cada hora
        }
    }
)

# Configurar logging
@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from config.logging import LOGGING_CONFIG
    dictConfig(LOGGING_CONFIG)
```

### 6.2 Tasks Assíncronas

```python
# services/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta

from services.webhook_processor import WebhookProcessor
from services.message_service import MessageService
from services.agent_service import AgentService
from services.evolution_api import evolution_client
from services.followup_service import FollowUpService
from services.report_service import ReportService

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3)
def process_message_task(self, message_data: Dict[str, Any]):
    """Processa mensagem recebida"""
    
    try:
        # Executar processamento assíncrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            process_message_async(message_data)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
        
        # Retry com backoff exponencial
        retry_in = 2 ** self.request.retries
        raise self.retry(exc=e, countdown=retry_in)

async def process_message_async(message_data: Dict[str, Any]):
    """Processamento assíncrono da mensagem"""
    
    # Processar mensagem
    processor = WebhookProcessor()
    processed_message = await processor.process_message(message_data)
    
    if not processed_message:
        logger.warning("Mensagem não pôde ser processada")
        return
    
    # Salvar mensagem no banco
    message_service = MessageService()
    saved_message = await message_service.save_message(processed_message)
    
    # Marcar como lida
    await evolution_client.mark_as_read(
        message_id=processed_message["id"],
        phone=processed_message["from"]
    )
    
    # Simular digitação
    await evolution_client.send_typing(
        phone=processed_message["from"],
        duration=3000
    )
    
    # Processar com agente
    agent_service = AgentService()
    response = await agent_service.process_message(
        message=processed_message["content"],
        sender_id=processed_message["from"],
        sender_name=processed_message["sender_name"],
        message_type=processed_message["type"],
        media_url=processed_message["media_url"],
        metadata=processed_message["metadata"]
    )
    
    # Enviar resposta
    if response:
        await evolution_client.send_text_message(
            phone=processed_message["from"],
            message=response,
            quoted_message_id=processed_message["id"]
        )
        
        # Salvar resposta
        await message_service.save_message({
            "from": "assistant",
            "content": response,
            "type": "text",
            "timestamp": datetime.utcnow().timestamp()
        })
    
    logger.info(f"Mensagem {processed_message['id']} processada com sucesso")

@shared_task
def check_pending_followups():
    """Verifica follow-ups pendentes"""
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        followup_service = FollowUpService()
        count = loop.run_until_complete(
            followup_service.process_pending_followups()
        )
        
        if count > 0:
            logger.info(f"{count} follow-ups processados")
        
        return count
        
    except Exception as e:
        logger.error(f"Erro ao processar follow-ups: {e}")
        raise

@shared_task
def send_followup_message(lead_id: str, followup_type: str):
    """Envia mensagem de follow-up"""
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        followup_service = FollowUpService()
        result = loop.run_until_complete(
            followup_service.send_followup(lead_id, followup_type)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao enviar follow-up: {e}")
        raise

@shared_task
def generate_weekly_report():
    """Gera relatório semanal"""
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        report_service = ReportService()
        report = loop.run_until_complete(
            report_service.generate_weekly_report()
        )
        
        # Enviar para grupo do WhatsApp
        if report and settings.WHATSAPP_GROUP_ID:
            loop.run_until_complete(
                evolution_client.send_text_message(
                    phone=settings.WHATSAPP_GROUP_ID,
                    message=report
                )
            )
        
        logger.info("Relatório semanal gerado e enviado")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        raise

@shared_task
def cleanup_old_media():
    """Limpa arquivos de mídia antigos"""
    
    try:
        # Limpar arquivos temporários com mais de 24h
        import os
        from pathlib import Path
        
        temp_dir = Path("/tmp")
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        cleaned = 0
        for file in temp_dir.glob("*"):
            if file.is_file():
                # Verificar idade do arquivo
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if mtime < cutoff_time:
                    try:
                        file.unlink()
                        cleaned += 1
                    except Exception as e:
                        logger.warning(f"Erro ao deletar {file}: {e}")
        
        logger.info(f"{cleaned} arquivos temporários limpos")
        return cleaned
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")
        raise
```

---

## 7. Segurança e Autenticação

### 7.1 Sistema de Autenticação JWT

```python
# api/auth.py
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    """Serviço de autenticação"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica senha"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gera hash da senha"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(
        subject: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Cria token JWT"""
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decodifica token JWT"""
        
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

# Dependência para rotas protegidas
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Obtém usuário atual do token"""
    
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    return user_id
```

### 7.2 Validação de Webhook

```python
# api/dependencies.py
from fastapi import Request, HTTPException, Header
import hmac
import hashlib
from typing import Optional

from config.settings import settings

async def verify_webhook_signature(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None)
):
    """Verifica assinatura do webhook"""
    
    if not settings.WEBHOOK_SECRET:
        # Sem secret configurado, aceitar tudo (desenvolvimento)
        return
    
    if not x_webhook_signature:
        raise HTTPException(
            status_code=401,
            detail="Assinatura ausente"
        )
    
    # Calcular assinatura esperada
    body = await request.body()
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Comparar de forma segura
    if not hmac.compare_digest(x_webhook_signature, expected_signature):
        raise HTTPException(
            status_code=401,
            detail="Assinatura inválida"
        )
```

---

## 8. Rate Limiting e Throttling

### 8.1 Rate Limiter

```python
# api/middleware/rate_limit.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting"""
    
    def __init__(
        self,
        app,
        calls_per_minute: int = 60,
        calls_per_hour: int = 1000
    ):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        
        # Contadores
        self.minute_calls = defaultdict(list)
        self.hour_calls = defaultdict(list)
        
        # Lock para thread safety
        self.lock = asyncio.Lock()
    
    async def dispatch(self, request: Request, call_next):
        # Identificar cliente
        client_id = self._get_client_id(request)
        
        # Verificar rate limit
        async with self.lock:
            if not await self._check_rate_limit(client_id):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit excedido"
                )
        
        # Processar requisição
        response = await call_next(request)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Identifica cliente pela IP ou token"""
        
        # Tentar pegar do header de autenticação
        auth = request.headers.get("Authorization")
        if auth:
            return f"auth:{auth}"
        
        # Usar IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Verifica se cliente está dentro do limite"""
        
        now = datetime.now()
        
        # Limpar chamadas antigas
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        self.minute_calls[client_id] = [
            call for call in self.minute_calls[client_id]
            if call > minute_ago
        ]
        
        self.hour_calls[client_id] = [
            call for call in self.hour_calls[client_id]
            if call > hour_ago
        ]
        
        # Verificar limites
        if len(self.minute_calls[client_id]) >= self.calls_per_minute:
            return False
        
        if len(self.hour_calls[client_id]) >= self.calls_per_hour:
            return False
        
        # Registrar chamada
        self.minute_calls[client_id].append(now)
        self.hour_calls[client_id].append(now)
        
        return True
```

### 8.2 Circuit Breaker

```python
# services/circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker para serviços externos"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com proteção de circuit breaker"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar"""
        
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > 
            timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        """Registra sucesso"""
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Registra falha"""
        
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
```

---

## 9. Monitoramento e Logs

### 9.1 Configuração de Logs

```python
# config/logging.py
import logging.config
from config.settings import settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "": {  # Root logger
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file", "error_file"]
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        }
    }
}

# Aplicar configuração
logging.config.dictConfig(LOGGING_CONFIG)
```

### 9.2 Integração com Sentry

```python
# config/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from config.settings import settings

def setup_sentry():
    """Configura Sentry para monitoramento de erros"""
    
    if not settings.SENTRY_DSN:
        return
    
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes={400, 401, 403, 404, 405}
            ),
            CeleryIntegration(),
            RedisIntegration(),
            SqlalchemyIntegration()
        ],
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        profiles_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        attach_stacktrace=True,
        send_default_pii=False,
        
        # Filtros
        before_send=before_send_filter,
        
        # Performance
        _experiments={
            "profiles_sample_rate": 0.1,
        }
    )

def before_send_filter(event, hint):
    """Filtra eventos antes de enviar para Sentry"""
    
    # Remover dados sensíveis
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        
        # Remover tokens e senhas
        sensitive_fields = ["password", "token", "api_key", "secret"]
        for field in sensitive_fields:
            if field in data:
                data[field] = "[REDACTED]"
    
    return event
```

### 9.3 Health Checks

```python
# api/routes/health.py
from fastapi import APIRouter, status
from typing import Dict, Any
import psutil
import aioredis
from datetime import datetime

from config.settings import settings
from services.database import check_db_connection
from services.evolution_api import evolution_client

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """Health check detalhado"""
    
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Verificar banco de dados
    try:
        db_ok = await check_db_connection()
        health["checks"]["database"] = {
            "status": "healthy" if db_ok else "unhealthy",
            "responsive": db_ok
        }
    except Exception as e:
        health["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "unhealthy"
    
    # Verificar Redis
    try:
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        await redis.close()
        
        health["checks"]["redis"] = {
            "status": "healthy",
            "responsive": True
        }
    except Exception as e:
        health["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "unhealthy"
    
    # Verificar Evolution API
    try:
        evolution_ok = await evolution_client.check_connection()
        health["checks"]["evolution_api"] = {
            "status": "healthy" if evolution_ok else "unhealthy",
            "connected": evolution_ok
        }
    except Exception as e:
        health["checks"]["evolution_api"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Métricas do sistema
    health["metrics"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
    
    return health

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, str]:
    """Verifica se aplicação está pronta"""
    
    # Verificar dependências críticas
    try:
        # Banco deve estar acessível
        if not await check_db_connection():
            return {"status": "not_ready", "reason": "database"}
        
        # Redis deve estar acessível
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        await redis.close()
        
        return {"status": "ready"}
        
    except Exception as e:
        return {
            "status": "not_ready",
            "reason": str(e)
        }
```

---

## 10. Testes e Validação

### 10.1 Testes de Integração

```python
# tests/test_webhooks.py
import pytest
from fastapi.testclient import TestClient
import json
import hmac
import hashlib

from api.main import app
from config.settings import settings

client = TestClient(app)

def generate_webhook_signature(payload: dict) -> str:
    """Gera assinatura para teste"""
    body = json.dumps(payload).encode()
    return hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

class TestWebhooks:
    """Testes dos webhooks"""
    
    def test_webhook_without_signature(self):
        """Testa webhook sem assinatura"""
        response = client.post(
            "/webhook/whatsapp",
            json={"event": "test"}
        )
        assert response.status_code == 401
    
    def test_webhook_with_invalid_signature(self):
        """Testa webhook com assinatura inválida"""
        response = client.post(
            "/webhook/whatsapp",
            json={"event": "test"},
            headers={"X-Webhook-Signature": "invalid"}
        )
        assert response.status_code == 401
    
    def test_webhook_message_upsert(self):
        """Testa recepção de nova mensagem"""
        payload = {
            "event": "MESSAGES_UPSERT",
            "instance": "test",
            "data": {
                "key": {
                    "id": "MSG123",
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "conversation": "Olá, quero saber sobre energia solar"
                },
                "messageTimestamp": 1234567890,
                "pushName": "João Silva"
            }
        }
        
        signature = generate_webhook_signature(payload)
        
        response = client.post(
            "/webhook/whatsapp",
            json=payload,
            headers={"X-Webhook-Signature": signature}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_webhook_ignore_own_message(self):
        """Testa ignorar mensagens próprias"""
        payload = {
            "event": "MESSAGES_UPSERT",
            "instance": "test",
            "data": {
                "key": {
                    "id": "MSG123",
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": True  # Mensagem própria
                },
                "message": {
                    "conversation": "Resposta do bot"
                }
            }
        }
        
        signature = generate_webhook_signature(payload)
        
        response = client.post(
            "/webhook/whatsapp",
            json=payload,
            headers={"X-Webhook-Signature": signature}
        )
        
        assert response.status_code == 200
        # Não deve processar
```

### 10.2 Testes de Carga

```python
# tests/load_test.py
import asyncio
import aiohttp
import time
from typing import List
import statistics

async def send_request(session: aiohttp.ClientSession, url: str, payload: dict):
    """Envia requisição de teste"""
    start = time.time()
    
    try:
        async with session.post(url, json=payload) as response:
            await response.text()
            return {
                "status": response.status,
                "time": time.time() - start,
                "error": None
            }
    except Exception as e:
        return {
            "status": 0,
            "time": time.time() - start,
            "error": str(e)
        }

async def load_test(
    url: str,
    num_requests: int,
    concurrent: int
):
    """Executa teste de carga"""
    
    payload = {
        "event": "MESSAGES_UPSERT",
        "data": {
            "key": {"id": "TEST", "fromMe": False},
            "message": {"conversation": "Teste de carga"}
        }
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for i in range(num_requests):
            task = send_request(session, url, payload)
            tasks.append(task)
            
            # Limitar concorrência
            if len(tasks) >= concurrent:
                results = await asyncio.gather(*tasks)
                tasks = []
        
        # Processar restantes
        if tasks:
            results = await asyncio.gather(*tasks)
    
    # Análise dos resultados
    times = [r["time"] for r in results if r["status"] == 200]
    errors = [r for r in results if r["status"] != 200]
    
    print(f"Total requests: {num_requests}")
    print(f"Successful: {len(times)}")
    print(f"Failed: {len(errors)}")
    
    if times:
        print(f"Average time: {statistics.mean(times):.3f}s")
        print(f"Min time: {min(times):.3f}s")
        print(f"Max time: {max(times):.3f}s")
        print(f"Median time: {statistics.median(times):.3f}s")

if __name__ == "__main__":
    # Executar teste
    asyncio.run(load_test(
        url="http://localhost:8000/webhook/whatsapp",
        num_requests=1000,
        concurrent=50
    ))
```

### 10.3 Script de Deploy

```bash
#!/bin/bash
# scripts/deploy_api.sh

set -e

echo "🚀 Iniciando deploy da API..."

# Variáveis
APP_DIR="/home/solarprime/sdr-solarprime"
BACKUP_DIR="/home/solarprime/backups"

# Criar backup
echo "📦 Criando backup..."
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz" $APP_DIR

# Atualizar código
echo "📥 Atualizando código..."
cd $APP_DIR
git pull origin main

# Instalar dependências
echo "📚 Instalando dependências..."
source venv/bin/activate
pip install -r requirements.txt

# Executar migrações
echo "🗄️ Executando migrações..."
python scripts/run_migrations.py

# Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo systemctl restart sdr-api
sudo systemctl restart sdr-celery
sudo systemctl restart sdr-celery-beat

# Verificar saúde
echo "🏥 Verificando saúde da aplicação..."
sleep 5
curl -f http://localhost:8000/health || exit 1

echo "✅ Deploy concluído com sucesso!"
```

---

## 🎉 Conclusão

Parabéns! Você implementou uma API robusta e pronta para produção.

### Checklist de Conclusão:
- [ ] FastAPI configurado com segurança
- [ ] Evolution API integrada
- [ ] Sistema de webhooks funcionando
- [ ] Processamento de mensagens multimodais
- [ ] Filas com Celery implementadas
- [ ] Autenticação e segurança configuradas
- [ ] Rate limiting ativo
- [ ] Monitoramento configurado
- [ ] Testes implementados
- [ ] Scripts de deploy prontos

### Próximos Passos:
1. Configurar Evolution API na VPS
2. Implementar integração Kommo: [05-kommo-integracao.md](05-kommo-integracao.md)
3. Testar fluxo completo
4. Ajustar rate limits conforme necessário

---

**💡 Dica**: Execute os testes de carga antes de ir para produção para garantir que o sistema aguenta o volume esperado.