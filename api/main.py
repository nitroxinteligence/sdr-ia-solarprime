"""
FastAPI Main Application
========================
API principal para o SDR SolarPrime
"""

# Importar módulo de compatibilidade antes de qualquer outra coisa
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import google_genai_compat
except ImportError:
    pass

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import Optional
import asyncio

from api.routes import webhooks, health, instance, webhook_admin
from services.evolution_api import evolution_client
from services.connection_monitor import connection_monitor
from middleware.rate_limiter import RateLimiter, RateLimiterMiddleware

logger = logging.getLogger(__name__)

# Lifespan para startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação SDR SolarPrime...")
    
    # Rate limiter já foi configurado antes do app iniciar
    logger.info("✅ Rate limiter já configurado")
    
    # Inicializar Evolution API Client
    try:
        await evolution_client.initialize()
        
        # Verificar conexão
        connection_status = await evolution_client.check_connection()
        
        if connection_status.get("state") == "open":
            logger.info("✅ Evolution API conectada e WhatsApp online")
            
            # Configurar webhook automaticamente
            webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
            webhook_endpoint = f"{webhook_url}/webhook/whatsapp"
            
            try:
                # Verificar se webhook já está configurado
                webhook_info = await evolution_client.get_webhook_info()
                
                if not webhook_info or webhook_info.get("url") != webhook_endpoint:
                    # Configurar novo webhook
                    logger.info(f"Configurando webhook: {webhook_endpoint}")
                    
                    # Selecionar apenas eventos essenciais para SDR
                    essential_events = [
                        "MESSAGES_UPSERT",      # Novas mensagens
                        "MESSAGES_UPDATE",      # Status de mensagens
                        "CONNECTION_UPDATE",    # Status da conexão
                        "PRESENCE_UPDATE",      # Presença (online/offline)
                        "QRCODE_UPDATED"        # QR Code atualizado
                    ]
                    
                    webhook_result = await evolution_client.create_webhook(
                        webhook_url=webhook_endpoint,
                        events=essential_events,
                        webhook_by_events=False,
                        webhook_base64=False
                    )
                    
                    if webhook_result:
                        logger.info("✅ Webhook configurado com sucesso")
                    else:
                        logger.warning("⚠️ Falha ao configurar webhook")
                else:
                    logger.info("✅ Webhook já está configurado corretamente")
                    
            except Exception as webhook_error:
                logger.error(f"❌ Erro ao configurar webhook: {webhook_error}")
                
        elif connection_status.get("state") == "close":
            logger.warning("⚠️ WhatsApp desconectado - necessário escanear QR Code")
            
            # Tentar obter QR Code
            qr_info = await evolution_client.get_qrcode()
            if qr_info and qr_info.get("qrcode"):
                logger.info(f"📱 QR Code disponível: {qr_info.get('qrcode', {}).get('base64', '')[:50]}...")
                
        else:
            logger.warning(f"⚠️ Evolution API em estado desconhecido: {connection_status.get('state')}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar Evolution API: {e}")
        # Não falhar a aplicação se Evolution API estiver offline
    
    # Iniciar monitor de conexão se configurado
    if os.getenv("CONNECTION_MONITOR_ENABLED", "true").lower() == "true":
        try:
            # Aguardar um pouco para garantir que Evolution API está pronta
            await asyncio.sleep(2)
            await connection_monitor.start()
            logger.info("✅ Monitor de conexão WhatsApp iniciado")
        except Exception as monitor_error:
            logger.error(f"❌ Erro ao iniciar monitor de conexão: {monitor_error}")
            # Não falhar a aplicação se o monitor falhar
    
    logger.info("Aplicação iniciada com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")
    
    # Parar monitor de conexão
    try:
        await connection_monitor.stop()
    except:
        pass
    
    # Fechar cliente Evolution API
    try:
        await evolution_client.close()
    except:
        pass
    
    logger.info("Aplicação encerrada")

# Criar aplicação
app = FastAPI(
    title="SDR IA SolarPrime API",
    description="API do Agente de Vendas Inteligente para Energia Solar",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    lifespan=lifespan
)

# Inicializar rate limiter antes de adicionar middlewares
rate_limiter = RateLimiter()

# Configurar CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de segurança
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# Adicionar rate limiter middleware
app.add_middleware(RateLimiterMiddleware, rate_limiter=rate_limiter)

# Iniciar task de limpeza do rate limiter no startup
@app.on_event("startup")
async def startup_rate_limiter():
    await rate_limiter.start_cleanup_task()
    logger.info("✅ Rate limiter cleanup task iniciada")

# Incluir rotas
app.include_router(webhooks.router, tags=["webhooks"])
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(instance.router, prefix="/instance", tags=["instance"])
app.include_router(webhook_admin.router, tags=["webhook-admin"])

# Tratamento global de erros
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": "Ocorreu um erro inesperado",
        "request_id": getattr(request.state, 'request_id', None)
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "app": "SDR IA SolarPrime",
        "version": "1.0.0",
        "status": "operational",
        "agent": "Luna - Agente de IA SolarPrime"
    }