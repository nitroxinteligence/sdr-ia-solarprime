"""
Main API V2 - Otimizada com AGnO Framework
==========================================
API principal com performance <30s
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from config.config import config
from config.agent_config import config as agent_config
from services.evolution_api import evolution_client
from services.connection_monitor import connection_monitor
from services.whatsapp_service_v2 import whatsapp_service_v2
from workflows.follow_up_workflow import follow_up_scheduler
from monitoring.performance_monitor import performance_monitor
from api.routes import health, webhooks, admin, webhook_admin
from utils.logging_config import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação SDR IA SolarPrime V2...")
    
    try:
        # Inicializar serviços em paralelo
        import asyncio
        await asyncio.gather(
            whatsapp_service_v2.initialize(),
            connection_monitor.start(),
            follow_up_scheduler.start() if agent_config.enable_follow_up else asyncio.sleep(0)
        )
        
        logger.info("✅ Aplicação iniciada com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar aplicação: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")
    
    # Parar serviços
    try:
        await connection_monitor.stop()
    except Exception as e:
        logger.warning(f"Erro ao parar monitor de conexão: {e}")
        
    try:
        await follow_up_scheduler.stop()
    except Exception as e:
        logger.warning(f"Erro ao parar follow-up scheduler: {e}")
    
    # Fechar cliente Evolution API
    try:
        await evolution_client.close()
    except Exception as e:
        logger.warning(f"Erro ao fechar cliente Evolution API: {e}")
    
    # Gerar relatório final de performance
    try:
        report = await performance_monitor.generate_performance_report()
        logger.info(f"SLA Achievement: {report['sla_achievement']}")
    except Exception as e:
        logger.warning(f"Erro ao gerar relatório final: {e}")
    
    logger.info("Aplicação encerrada")


# Criar aplicação
app = FastAPI(
    title="SDR IA SolarPrime V2",
    description="API de vendas inteligente com AGnO Framework - Performance <30s",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None
)


# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de hosts confiáveis
if config.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=config.allowed_hosts
    )


# Middleware de performance
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Monitora performance de todas as requisições"""
    start_time = datetime.now()
    
    # Processar requisição
    response = await call_next(request)
    
    # Calcular tempo
    duration = (datetime.now() - start_time).total_seconds()
    
    # Adicionar header
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    # Log se demorou muito
    if duration > 5:  # Requisições HTTP devem ser rápidas
        logger.warning(f"Slow HTTP request: {request.url.path} took {duration:.2f}s")
    
    return response


# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Incluir rotas
app.include_router(health.router)
app.include_router(webhooks.router)
app.include_router(admin.router)
app.include_router(webhook_admin.router)


# Rota raiz
@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "name": "SDR IA SolarPrime V2",
        "version": "2.0.0",
        "status": "operational",
        "performance_target": "<30s",
        "framework": "AGnO",
        "features": {
            "ai_agent": "✅ Google Gemini 2.5 Pro",
            "knowledge_base": "✅ Supabase Vector DB",
            "follow_up": "✅ AGnO Workflows",
            "multimodal": "✅ Native Support",
            "caching": "✅ 2-Level Cache",
            "monitoring": "✅ Real-time Performance"
        },
        "endpoints": {
            "health": "/health",
            "webhooks": "/webhook/whatsapp",
            "admin": "/admin",
            "docs": "/docs" if config.debug else None
        }
    }


# Performance endpoint
@app.get("/performance")
async def performance_stats():
    """Estatísticas de performance em tempo real"""
    metrics = performance_monitor.get_metrics_summary()
    alerts = performance_monitor.get_recent_alerts(hours=1)
    cache_stats = whatsapp_service_v2.get_performance_stats()
    
    return {
        "status": "monitoring",
        "timestamp": datetime.now().isoformat(),
        "sla_target": "<30 seconds",
        "metrics": metrics,
        "recent_alerts": alerts,
        "cache_performance": cache_stats,
        "recommendations": _get_performance_recommendations(metrics)
    }


def _get_performance_recommendations(metrics: dict) -> list:
    """Gera recomendações baseadas nas métricas"""
    recommendations = []
    
    for func, data in metrics.items():
        if 'response_time' in data:
            rt = data['response_time']
            if rt['average'] > 25:
                recommendations.append(f"⚠️ {func} está próximo do limite de 30s")
            if rt['max'] > 30:
                recommendations.append(f"🚨 {func} excedeu 30s pelo menos uma vez")
            if rt['average'] < 15:
                recommendations.append(f"✅ {func} está com excelente performance")
                
    return recommendations


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug,
        log_level="debug" if config.debug else "info"
    )