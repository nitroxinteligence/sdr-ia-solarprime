"""
FastAPI Main Application
========================
API principal para o SDR SolarPrime
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import Optional
import asyncio

from api.routes import webhooks, health, instance, webhook_admin, auth, kommo_webhooks, diagnostics
from services.evolution_api import evolution_client
from services.connection_monitor import connection_monitor
from middleware.rate_limiter import RateLimiter, RateLimiterMiddleware
from workflows.follow_up_workflow import follow_up_scheduler
from config.agent_config import config as agent_config

# Importar validador de startup
try:
    from api.startup_config import validate_startup_config
except ImportError:
    validate_startup_config = None

logger = logging.getLogger(__name__)

# Variável global para a task de reconfiguração do webhook
webhook_reconfigure_task: Optional[asyncio.Task] = None


async def webhook_reconfigure_loop():
    """Loop que reconfigura o webhook periodicamente"""
    interval_minutes = int(os.getenv("WEBHOOK_RECONFIGURE_INTERVAL", "30"))
    interval_seconds = interval_minutes * 60
    
    logger.info(f"Iniciando loop de reconfiguração de webhook a cada {interval_minutes} minutos")
    
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            
            logger.info("⏰ Executando reconfiguração automática do webhook...")
            
            # Importar aqui para evitar importação circular
            from api.routes.webhook_admin import reconfigure_webhook
            
            # Chamar a função diretamente (sem dependências do FastAPI)
            webhook_base_url = os.getenv("WEBHOOK_BASE_URL")
            if not webhook_base_url:
                if os.getenv("ENVIRONMENT", "development") == "production":
                    service_name = os.getenv("SERVICE_NAME", "sdr-ia")
                    webhook_base_url = f"http://{service_name}:8000"
                else:
                    webhook_base_url = "http://localhost:8000"
            
            webhook_url = f"{webhook_base_url}/webhook/whatsapp"
            
            # Verificar se URL mudou
            current_config = await evolution_client.get_webhook_info()
            current_url = current_config.get("webhook", {}).get("url", "")
            
            if current_url != webhook_url:
                logger.warning(f"⚠️ Webhook URL mudou! Atual: {current_url}, Esperado: {webhook_url}")
                
                # Reconfigurar
                result = await evolution_client.create_webhook(
                    webhook_url=webhook_url,
                    events=["MESSAGES_UPSERT", "MESSAGES_UPDATE", "CONNECTION_UPDATE", "PRESENCE_UPDATE", "QRCODE_UPDATED"],
                    webhook_by_events=False,
                    webhook_base64=False
                )
                
                if result:
                    logger.success("✅ Webhook reconfigurado automaticamente!")
                else:
                    logger.error("❌ Falha na reconfiguração automática do webhook")
            else:
                logger.info("✅ Webhook URL está correto, nenhuma ação necessária")
                
        except Exception as e:
            logger.error(f"Erro no loop de reconfiguração do webhook: {e}")
            # Continuar executando mesmo com erro
            await asyncio.sleep(60)  # Aguardar 1 minuto antes de tentar novamente


# Lifespan para startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação SDR SolarPrime...")
    
    # Validar configuração no startup
    if validate_startup_config:
        if not validate_startup_config():
            logger.error("❌ Validação de configuração falhou!")
            # Em desenvolvimento, continuar mesmo com erro
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise RuntimeError("Configuração inválida para produção")
    
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
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.info("ℹ️ Evolution API não disponível em desenvolvimento")
            logger.info("💡 A aplicação funcionará sem WhatsApp")
        else:
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
    
    # Iniciar Follow-up Scheduler se configurado
    if agent_config.enable_follow_up:
        try:
            asyncio.create_task(follow_up_scheduler.start())
            logger.info("✅ Follow-up scheduler iniciado")
            logger.info(f"  📅 Verificando follow-ups a cada 1 minuto")
            logger.info(f"  ⏰ Primeiro follow-up após {agent_config.follow_up_delay_minutes} minutos")
            logger.info(f"  ⏰ Segundo follow-up após {agent_config.follow_up_second_delay_hours} horas")
        except Exception as scheduler_error:
            logger.error(f"❌ Erro ao iniciar follow-up scheduler: {scheduler_error}")
            # Não falhar a aplicação se o scheduler falhar
    
    # Iniciar reconfiguração automática de webhook em produção
    global webhook_reconfigure_task
    if os.getenv("ENVIRONMENT", "development") == "production":
        if os.getenv("WEBHOOK_AUTO_RECONFIGURE", "true").lower() == "true":
            try:
                webhook_reconfigure_task = asyncio.create_task(webhook_reconfigure_loop())
                logger.info("✅ Reconfiguração automática de webhook iniciada")
                logger.info(f"  🔄 Verificando webhook a cada {os.getenv('WEBHOOK_RECONFIGURE_INTERVAL', '30')} minutos")
            except Exception as e:
                logger.error(f"❌ Erro ao iniciar reconfiguração automática de webhook: {e}")
    
    logger.info("Aplicação iniciada com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")
    
    # Parar monitor de conexão
    try:
        await connection_monitor.stop()
    except Exception as e:
        logger.warning(f"Erro ao parar monitor de conexão: {e}")
    
    # Parar follow-up scheduler
    if agent_config.enable_follow_up:
        try:
            await follow_up_scheduler.stop()
            logger.info("✅ Follow-up scheduler parado")
        except Exception as e:
            logger.warning(f"Erro ao parar follow-up scheduler: {e}")
    
    # Parar reconfiguração automática de webhook
    if webhook_reconfigure_task and not webhook_reconfigure_task.done():
        webhook_reconfigure_task.cancel()
        try:
            await webhook_reconfigure_task
        except asyncio.CancelledError:
            logger.info("✅ Reconfiguração automática de webhook parada")
    
    # Fechar cliente Evolution API
    try:
        await evolution_client.close()
    except Exception as e:
        logger.warning(f"Erro ao fechar cliente Evolution API: {e}")
    
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
app.include_router(auth.router, tags=["authentication"])
app.include_router(kommo_webhooks.router, tags=["kommo-webhooks"])
app.include_router(diagnostics.router, tags=["diagnostics"])

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