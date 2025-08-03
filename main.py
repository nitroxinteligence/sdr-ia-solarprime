"""
SDR IA Solar Prime - Aplicação Principal
Powered by AGnO Teams Framework
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger
from app.utils.logger import emoji_logger

from app.config import settings
from app.api import health, webhooks, teams
from app.integrations.supabase_client import supabase_client
from app.integrations.redis_client import redis_client
from app.teams import create_sdr_team

# Configuração do logger
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    # Startup
    emoji_logger.system_start("SDR IA Solar Prime v0.2")
    
    try:
        # Conecta ao Redis
        await redis_client.connect()
        emoji_logger.system_ready("Redis")
        
        # Testa conexão com Supabase
        await supabase_client.test_connection()
        emoji_logger.system_ready("Supabase")
        
        # Inicializa o Team SDR
        team = await create_sdr_team()
        emoji_logger.system_ready("SDR Team", members_count=len(team.team.members))
        
        # Inicializa campos do CRM automaticamente
        if hasattr(team, 'crm_agent'):
            await team.crm_agent.initialize()
            emoji_logger.system_ready("Kommo CRM")
        
        emoji_logger.system_ready("SDR IA Solar Prime", startup_time=3.0)
        
    except Exception as e:
        emoji_logger.system_error("SDR IA Solar Prime", f"Erro na inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    emoji_logger.system_info("Encerrando SDR IA Solar Prime...")
    
    try:
        # Desconecta do Redis
        await redis_client.disconnect()
        emoji_logger.system_info("Redis desconectado")
        
        emoji_logger.system_info("SDR IA Solar Prime encerrado com sucesso")
        
    except Exception as e:
        emoji_logger.system_error("Shutdown", str(e))

# Cria aplicação FastAPI
app = FastAPI(
    title="SDR IA Solar Prime",
    description="Sistema Inteligente de Vendas para Energia Solar - Powered by AGnO Teams",
    version="0.2.0",
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if hasattr(settings, 'cors_origins') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra rotas
app.include_router(health.router)
app.include_router(webhooks.router)
app.include_router(teams.router)  # Rota principal do Teams

# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Tratamento global de exceções
    """
    emoji_logger.system_error("Global Exception Handler", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An error occurred",
            "path": str(request.url)
        }
    )

# Rota raiz
@app.get("/")
async def root():
    """
    Endpoint raiz - Informações da API
    """
    return {
        "name": "SDR IA Solar Prime",
        "version": "0.2.0",
        "framework": "AGnO Teams",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "webhooks": "/webhooks",
            "teams": "/teams"
        },
        "documentation": "/docs",
        "team_mode": "COORDINATE"
    }

# Health check principal
@app.get("/health")
async def health_check():
    """
    Health check geral do sistema
    """
    try:
        # Verifica Redis
        redis_status = await redis_client.ping()
        
        # Verifica Supabase
        supabase_status = await supabase_client.test_connection()
        
        # Status do Team
        team_status = "ready"  # Simplificado para evitar criar múltiplas instâncias
        
        return {
            "status": "healthy",
            "services": {
                "redis": "connected" if redis_status else "disconnected",
                "supabase": "connected" if supabase_status else "disconnected",
                "team": team_status
            }
        }
    except Exception as e:
        emoji_logger.system_error("Health Check", str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    # Configurações do servidor
    host = settings.api_host if hasattr(settings, 'api_host') else "0.0.0.0"
    port = settings.api_port if hasattr(settings, 'api_port') else 8000
    reload = settings.debug if hasattr(settings, 'debug') else False
    
    emoji_logger.system_start(f"Servidor Uvicorn em {host}:{port}")
    
    # Inicia servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info" if not reload else "debug"
    )