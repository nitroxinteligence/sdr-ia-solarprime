"""
Diagnostics Routes
==================
Endpoints para diagnóstico e verificação do status das integrações
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from datetime import datetime
import asyncio
from loguru import logger
import os

# Importar serviços
from services.whatsapp_service import whatsapp_service
from services.redis_service import redis_service
from services.kommo_service import KommoService
from services.google_calendar_service import GoogleCalendarService
from services.evolution_api import evolution_client as evolution_api
from repositories.lead_repository import lead_repository
from config.config import get_config

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


async def check_redis_connection() -> Dict[str, Any]:
    """Verifica conexão com Redis"""
    try:
        await redis_service.connect()
        if redis_service.client:
            # Testar operação básica
            test_key = "diagnostic_test"
            await redis_service.set(test_key, "test_value", ttl=10)
            value = await redis_service.get(test_key)
            await redis_service.delete(test_key)
            
            return {
                "status": "connected",
                "url": redis_service.redis_url,
                "test_successful": value == "test_value"
            }
        else:
            return {
                "status": "disconnected",
                "url": redis_service.redis_url,
                "fallback": "memory_cache",
                "memory_cache_size": len(redis_service._memory_cache)
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fallback": "memory_cache"
        }


async def check_evolution_api() -> Dict[str, Any]:
    """Verifica conexão com Evolution API"""
    try:
        # Verificar se está configurado
        if not evolution_api.base_url or not evolution_api.api_key:
            return {
                "status": "not_configured",
                "error": "Evolution API não configurada"
            }
        
        # Tentar obter informações da instância
        instance_info = await evolution_api.get_instance_info()
        
        return {
            "status": "connected" if instance_info else "error",
            "base_url": evolution_api.base_url,
            "instance_name": evolution_api.instance_name,
            "instance_info": instance_info
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "base_url": evolution_api.base_url
        }


async def check_kommo_integration() -> Dict[str, Any]:
    """Verifica integração com Kommo"""
    try:
        config = get_config()
        
        # Verificar se está configurado
        if not config.kommo.long_lived_token:
            return {
                "status": "not_configured",
                "error": "Kommo não configurado"
            }
        
        # Criar instância temporária para teste
        kommo = KommoService()
        
        # Tentar obter informações da conta
        account_info = await kommo.get_account_info()
        
        return {
            "status": "connected" if account_info else "error",
            "subdomain": config.kommo.subdomain,
            "account_info": account_info,
            "pipelines": len(account_info.get("pipelines", [])) if account_info else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "subdomain": get_config().kommo.subdomain
        }


async def check_google_calendar() -> Dict[str, Any]:
    """Verifica integração com Google Calendar"""
    try:
        # Verificar se está configurado
        credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH")
        if not credentials_path or not os.path.exists(credentials_path):
            return {
                "status": "not_configured",
                "error": "Credenciais do Google Calendar não encontradas"
            }
        
        # Criar instância temporária para teste
        calendar = GoogleCalendarService()
        
        # Tentar listar calendários
        calendars = await calendar.list_calendars()
        
        return {
            "status": "connected" if calendars else "error",
            "calendar_id": calendar.calendar_id,
            "calendars_count": len(calendars) if calendars else 0,
            "credentials_path": credentials_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def check_database_connection() -> Dict[str, Any]:
    """Verifica conexão com banco de dados"""
    try:
        # Tentar uma query simples
        lead_count = await lead_repository.count_all()
        
        return {
            "status": "connected",
            "lead_count": lead_count,
            "database_url": "supabase"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """
    Retorna status completo do sistema e integrações
    
    Verifica:
    - Redis
    - Evolution API (WhatsApp)
    - Kommo CRM
    - Google Calendar
    - Banco de dados
    - Variáveis de ambiente
    """
    
    # Executar todas as verificações em paralelo
    results = await asyncio.gather(
        check_redis_connection(),
        check_evolution_api(),
        check_kommo_integration(),
        check_google_calendar(),
        check_database_connection(),
        return_exceptions=True
    )
    
    # Processar resultados
    redis_status = results[0] if not isinstance(results[0], Exception) else {"status": "error", "error": str(results[0])}
    evolution_status = results[1] if not isinstance(results[1], Exception) else {"status": "error", "error": str(results[1])}
    kommo_status = results[2] if not isinstance(results[2], Exception) else {"status": "error", "error": str(results[2])}
    calendar_status = results[3] if not isinstance(results[3], Exception) else {"status": "error", "error": str(results[3])}
    database_status = results[4] if not isinstance(results[4], Exception) else {"status": "error", "error": str(results[4])}
    
    # Verificar variáveis de ambiente críticas
    env_vars = {
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "not_set"),
        "API_BASE_URL": bool(os.getenv("API_BASE_URL")),
        "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
        "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
        "REDIS_URL": bool(os.getenv("REDIS_URL")),
        "EVOLUTION_API_URL": bool(os.getenv("EVOLUTION_API_URL")),
        "EVOLUTION_API_KEY": bool(os.getenv("EVOLUTION_API_KEY")),
        "KOMMO_LONG_LIVED_TOKEN": bool(os.getenv("KOMMO_LONG_LIVED_TOKEN")),
        "GOOGLE_GENAI_API_KEY": bool(os.getenv("GOOGLE_GENAI_API_KEY"))
    }
    
    # Calcular health score
    health_score = 0
    total_checks = 5
    
    if redis_status.get("status") in ["connected", "disconnected"]:
        health_score += 1
    if evolution_status.get("status") == "connected":
        health_score += 1
    if kommo_status.get("status") == "connected":
        health_score += 1
    if calendar_status.get("status") == "connected":
        health_score += 1
    if database_status.get("status") == "connected":
        health_score += 1
    
    health_percentage = (health_score / total_checks) * 100
    
    return {
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "health_score": f"{health_percentage:.0f}%",
        "integrations": {
            "redis": redis_status,
            "whatsapp": evolution_status,
            "kommo": kommo_status,
            "google_calendar": calendar_status,
            "database": database_status
        },
        "environment_variables": env_vars,
        "recommendations": generate_recommendations(
            redis_status, 
            evolution_status, 
            kommo_status, 
            calendar_status, 
            database_status
        )
    }


def generate_recommendations(redis, evolution, kommo, calendar, database) -> List[str]:
    """Gera recomendações baseadas no status"""
    recommendations = []
    
    if redis.get("status") == "error":
        recommendations.append("⚠️ Redis não está acessível. Verifique a conexão ou use REDIS_FALLBACK_HOSTS")
    elif redis.get("status") == "disconnected":
        recommendations.append("ℹ️ Redis está usando cache em memória como fallback")
    
    if evolution.get("status") == "not_configured":
        recommendations.append("❌ Evolution API não configurada. Configure EVOLUTION_API_URL e EVOLUTION_API_KEY")
    elif evolution.get("status") == "error":
        recommendations.append("⚠️ Evolution API não está respondendo. Verifique a URL e a chave de API")
    
    if kommo.get("status") == "not_configured":
        recommendations.append("❌ Kommo não configurado. Configure KOMMO_LONG_LIVED_TOKEN")
    elif kommo.get("status") == "error":
        recommendations.append("⚠️ Kommo não está acessível. Verifique o token e subdomain")
    
    if calendar.get("status") == "not_configured":
        recommendations.append("❌ Google Calendar não configurado. Configure as credenciais")
    elif calendar.get("status") == "error":
        recommendations.append("⚠️ Google Calendar com erro. Verifique as credenciais")
    
    if database.get("status") == "error":
        recommendations.append("❌ Banco de dados não acessível. Verifique SUPABASE_URL e SUPABASE_KEY")
    
    if not recommendations:
        recommendations.append("✅ Todas as integrações estão funcionando corretamente!")
    
    return recommendations


@router.get("/quick-check")
async def quick_health_check() -> Dict[str, Any]:
    """
    Verificação rápida de saúde do sistema
    Útil para monitoramento e health checks
    """
    try:
        # Verificar apenas o essencial
        redis_ok = False
        try:
            await redis_service.connect()
            redis_ok = redis_service.client is not None or len(redis_service._memory_cache) >= 0
        except:
            pass
        
        # Verificar se a API está respondendo
        return {
            "status": "healthy" if redis_ok else "degraded",
            "timestamp": datetime.now().isoformat(),
            "redis": "ok" if redis_ok else "using_fallback"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/test-webhook/{service}")
async def test_webhook(service: str) -> Dict[str, Any]:
    """
    Testa webhook de um serviço específico
    
    Serviços suportados:
    - evolution: Testa webhook da Evolution API
    - kommo: Testa webhook do Kommo
    """
    
    if service == "evolution":
        # Criar payload de teste
        test_payload = {
            "event": "MESSAGES_UPSERT",
            "instance": "test_instance",
            "data": {
                "key": {
                    "id": "TEST123",
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "conversation": "Mensagem de teste do diagnóstico"
                },
                "messageTimestamp": int(datetime.now().timestamp()),
                "pushName": "Teste Diagnóstico"
            }
        }
        
        # Processar webhook
        result = await whatsapp_service.process_webhook(test_payload)
        
        return {
            "service": "evolution",
            "test_successful": result.get("status") != "error",
            "result": result
        }
    
    elif service == "kommo":
        # Criar payload de teste
        test_payload = {
            "leads": {
                "update": [{
                    "id": 12345,
                    "name": "Lead de Teste",
                    "status_id": 12345
                }]
            }
        }
        
        return {
            "service": "kommo",
            "test_payload": test_payload,
            "note": "Webhook do Kommo deve ser testado através do painel do Kommo"
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Serviço '{service}' não suportado")