"""
Health Check API - Endpoints de saúde do sistema
"""
from fastapi import APIRouter, Request
from datetime import datetime
from typing import Dict, Any
from loguru import logger

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SDR IA SolarPrime"
    }

@router.get("/live")
async def liveness():
    """Liveness probe para Kubernetes"""
    return {"status": "alive"}

@router.get("/ready")
async def readiness(request: Request):
    """Readiness probe - verifica se o serviço está pronto"""
    try:
        # Verifica se os componentes principais estão inicializados
        checks = {
            "supabase": False,
            "evolution": False,
            "agent": False,
            "redis": False
        }
        
        # Verifica Supabase
        if hasattr(request.app.state, 'supabase'):
            checks["supabase"] = await request.app.state.supabase.test_connection()
        
        # Verifica Evolution API
        if hasattr(request.app.state, 'evolution'):
            checks["evolution"] = await request.app.state.evolution.test_connection()
        
        # Verifica Agente
        if hasattr(request.app.state, 'agent'):
            checks["agent"] = request.app.state.agent.is_ready()
        
        # Verifica Redis
        if hasattr(request.app.state, 'redis'):
            checks["redis"] = await request.app.state.redis.ping()
        
        # Sistema está pronto se todos os componentes críticos estão OK
        is_ready = checks["supabase"] and checks["evolution"] and checks["agent"]
        
        return {
            "ready": is_ready,
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no readiness check: {e}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/metrics")
async def metrics(request: Request):
    """Métricas do sistema para monitoramento"""
    try:
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "counters": {},
            "gauges": {},
            "histograms": {}
        }
        
        # Obtém métricas do Redis se disponível
        if hasattr(request.app.state, 'redis'):
            from app.integrations.redis_client import redis_client
            
            # Contadores
            metrics_data["counters"]["messages_processed"] = await redis_client.get_counter("messages_processed")
            metrics_data["counters"]["leads_created"] = await redis_client.get_counter("leads_created")
            metrics_data["counters"]["meetings_scheduled"] = await redis_client.get_counter("meetings_scheduled")
            
            # Gauges (valores atuais)
            connection_status = await redis_client.get("whatsapp:connection_status")
            if connection_status:
                metrics_data["gauges"]["whatsapp_connected"] = 1 if connection_status.get("state") == "open" else 0
        
        # Obtém estatísticas do banco se disponível
        if hasattr(request.app.state, 'supabase'):
            try:
                stats = await request.app.state.supabase.get_daily_stats()
                metrics_data["gauges"]["leads_today"] = stats.get("leads_today", 0)
                metrics_data["gauges"]["conversations_active"] = stats.get("conversations_active", 0)
            except:
                pass
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/dependencies")
async def check_dependencies(request: Request):
    """Verifica status de todas as dependências"""
    dependencies = {}
    
    # Supabase
    try:
        if hasattr(request.app.state, 'supabase'):
            connected = await request.app.state.supabase.test_connection()
            dependencies["supabase"] = {
                "status": "healthy" if connected else "unhealthy",
                "type": "database"
            }
    except Exception as e:
        dependencies["supabase"] = {
            "status": "unhealthy",
            "error": str(e),
            "type": "database"
        }
    
    # Evolution API
    try:
        if hasattr(request.app.state, 'evolution'):
            connected = await request.app.state.evolution.test_connection()
            dependencies["evolution_api"] = {
                "status": "healthy" if connected else "unhealthy",
                "type": "whatsapp"
            }
    except Exception as e:
        dependencies["evolution_api"] = {
            "status": "unhealthy",
            "error": str(e),
            "type": "whatsapp"
        }
    
    # Redis
    try:
        from app.integrations.redis_client import redis_client
        await redis_client.connect()
        if await redis_client.redis_client.ping():
            dependencies["redis"] = {
                "status": "healthy",
                "type": "cache"
            }
        else:
            dependencies["redis"] = {
                "status": "unhealthy",
                "type": "cache"
            }
    except Exception as e:
        dependencies["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "type": "cache"
        }
    
    # Google Calendar (funciona mas sem sync com Supabase)
    try:
        from app.config import settings
        if settings.google_service_account_email:
            dependencies["google_calendar"] = {
                "status": "configured",
                "type": "calendar",
                "message": "Funcionando sem sync Supabase"
            }
        else:
            dependencies["google_calendar"] = {
                "status": "not_configured",
                "type": "calendar"
            }
    except:
        dependencies["google_calendar"] = {
            "status": "not_configured",
            "type": "calendar"
        }
    
    # Kommo CRM (se configurado)
    try:
        from app.config import settings
        if settings.KOMMO_LONG_LIVED_TOKEN:
            dependencies["kommo_crm"] = {
                "status": "configured",
                "type": "crm"
            }
        else:
            dependencies["kommo_crm"] = {
                "status": "not_configured",
                "type": "crm"
            }
    except:
        dependencies["kommo_crm"] = {
            "status": "not_configured",
            "type": "crm"
        }
    
    # Determina status geral
    all_healthy = all(
        dep.get("status") in ["healthy", "configured"] 
        for dep in dependencies.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "dependencies": dependencies,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/info")
async def service_info():
    """Informações sobre o serviço"""
    from app.config import settings
    
    return {
        "service": "SDR IA SolarPrime",
        "version": "0.2.0",
        "environment": settings.ENVIRONMENT,
        "agent": "Helen Vieira",
        "company": "Solar Prime Boa Viagem",
        "features": {
            "whatsapp": True,
            "ai_qualification": True,
            "google_calendar": bool(settings.GOOGLE_SERVICE_ACCOUNT_PATH),
            "kommo_crm": bool(settings.KOMMO_LONG_LIVED_TOKEN),
            "follow_up": True,
            "reports": True
        },
        "business_hours": {
            "start": settings.BUSINESS_HOURS_START,
            "end": settings.BUSINESS_HOURS_END,
            "timezone": settings.TIMEZONE
        }
    }