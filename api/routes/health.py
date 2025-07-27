"""
Health Check Routes
===================
Rotas para verificação de saúde da aplicação
"""

from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime
import os

from services.evolution_api import evolution_client

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.1",  # Atualizado para verificar deploy
        "agent": "Luna - SDR IA SolarPrime",
        "deploy_date": "2025-07-27T21:30:00Z"  # Marca temporal do deploy
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
    
    # Verificar AGnO Framework
    try:
        import agno
        health["checks"]["agno_framework"] = {
            "status": "healthy",
            "version": getattr(agno, '__version__', '1.7.4')
        }
    except Exception as e:
        health["checks"]["agno_framework"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "unhealthy"
    
    # Verificar Gemini
    try:
        from google import genai
        health["checks"]["gemini"] = {
            "status": "healthy",
            "api_key_configured": bool(os.getenv("GEMINI_API_KEY"))
        }
    except Exception as e:
        health["checks"]["gemini"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "unhealthy"
    
    # Verificar Evolution API
    try:
        evolution_ok = await evolution_client.check_connection()
        health["checks"]["evolution_api"] = {
            "status": "healthy" if evolution_ok else "unhealthy",
            "connected": evolution_ok,
            "url": os.getenv("EVOLUTION_API_URL", "not_configured")
        }
    except Exception as e:
        health["checks"]["evolution_api"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Verificar configurações
    health["checks"]["configuration"] = {
        "evolution_api_key": bool(os.getenv("EVOLUTION_API_KEY")),
        "evolution_instance": bool(os.getenv("EVOLUTION_INSTANCE_NAME")),
        "webhook_secret": bool(os.getenv("WEBHOOK_SECRET")),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    return health


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, str]:
    """Verifica se aplicação está pronta"""
    
    try:
        # Verificar AGnO
        import agno
        
        # Verificar Gemini
        if not os.getenv("GEMINI_API_KEY"):
            return {"status": "not_ready", "reason": "GEMINI_API_KEY not configured"}
        
        # Verificar Evolution API
        if not os.getenv("EVOLUTION_API_URL"):
            return {"status": "not_ready", "reason": "EVOLUTION_API_URL not configured"}
        
        return {"status": "ready"}
        
    except Exception as e:
        return {
            "status": "not_ready",
            "reason": str(e)
        }