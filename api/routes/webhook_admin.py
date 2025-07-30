"""
Webhook Admin Routes
===================
Rotas administrativas para gerenciamento e monitoramento de webhooks
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import os
from collections import defaultdict

from services.evolution_api import evolution_client
from api.auth import verify_admin_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/webhook", tags=["webhook-admin"])

# Armazenar métricas em memória (em produção, use Redis ou banco de dados)
webhook_metrics = {
    "total_received": 0,
    "total_processed": 0,
    "total_errors": 0,
    "events_count": defaultdict(int),
    "last_received": None,
    "last_error": None,
    "hourly_stats": defaultdict(lambda: {"received": 0, "errors": 0}),
    "processing_times": []
}


@router.get("/config", dependencies=[Depends(verify_admin_api_key)])
async def get_webhook_config() -> Dict[str, Any]:
    """
    Obtém configuração atual do webhook na Evolution API
    
    Requer autenticação com API key de admin
    """
    try:
        config = await evolution_client.get_webhook_info()
        
        # Adicionar informações do ambiente
        env_config = {
            "environment": {
                "webhook_base_url": os.getenv("WEBHOOK_BASE_URL", "not_configured"),
                "signature_validation": os.getenv("WEBHOOK_VALIDATE_SIGNATURE", "false"),
                "ip_validation": bool(os.getenv("ALLOWED_WEBHOOK_IPS")),
                "instance_name": os.getenv("EVOLUTION_INSTANCE_NAME", "unknown")
            }
        }
        
        return {
            "evolution_config": config,
            "app_config": env_config,
            "status": "configured" if config.get("webhook", {}).get("enabled") else "not_configured"
        }
            
    except Exception as e:
        logger.error(f"Erro ao obter configuração do webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configure", dependencies=[Depends(verify_admin_api_key)])
async def configure_webhook(
    webhook_url: Optional[str] = None,
    events: Optional[List[str]] = None,
    enabled: bool = True
) -> Dict[str, Any]:
    """
    Configura ou atualiza webhook na Evolution API
    
    Args:
        webhook_url: URL do webhook (usa WEBHOOK_BASE_URL se não fornecido)
        events: Lista de eventos (usa padrão se não fornecido)
        enabled: Se o webhook deve estar ativo
    """
    try:
        # Usar URL do ambiente se não fornecida
        if not webhook_url:
            base_url = os.getenv("WEBHOOK_BASE_URL")
            if not base_url:
                raise HTTPException(
                    status_code=400,
                    detail="webhook_url não fornecida e WEBHOOK_BASE_URL não configurada"
                )
            webhook_url = f"{base_url}/webhook/whatsapp"
        
        # Usar eventos padrão se não fornecidos
        if not events:
            events = [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "CONNECTION_UPDATE",
                "QRCODE_UPDATED",
                "SEND_MESSAGE",
                "PRESENCE_UPDATE"
            ]
        
        if enabled:
            result = await evolution_client.create_webhook(
                webhook_url=webhook_url,
                events=events,
                webhook_by_events=False,
                webhook_base64=False
            )
        else:
            # Desabilitar webhook
            result = await evolution_client.create_webhook(
                webhook_url=webhook_url,
                events=[],
                webhook_by_events=False,
                webhook_base64=False
            )
            result["webhook"]["enabled"] = False
        
        logger.info(f"Webhook configurado: {webhook_url} - Ativo: {enabled}")
        
        return {
            "status": "success",
            "webhook_url": webhook_url,
            "enabled": enabled,
            "events_count": len(events),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_webhook_metrics(
    hours: int = Query(default=24, ge=1, le=168)
) -> Dict[str, Any]:
    """
    Retorna métricas dos webhooks
    
    Args:
        hours: Número de horas para análise (padrão: 24, máx: 168)
    """
    # Calcular estatísticas das últimas N horas
    now = datetime.now()
    cutoff_time = now - timedelta(hours=hours)
    
    # Filtrar estatísticas horárias relevantes
    hourly_data = []
    for hour_key, stats in webhook_metrics["hourly_stats"].items():
        try:
            hour_time = datetime.fromisoformat(hour_key)
            if hour_time >= cutoff_time:
                hourly_data.append({
                    "hour": hour_key,
                    "received": stats["received"],
                    "errors": stats["errors"]
                })
        except:
            continue
    
    # Calcular médias de tempo de processamento
    avg_processing_time = 0
    if webhook_metrics["processing_times"]:
        recent_times = webhook_metrics["processing_times"][-100:]  # Últimos 100
        avg_processing_time = sum(recent_times) / len(recent_times)
    
    return {
        "summary": {
            "total_received": webhook_metrics["total_received"],
            "total_processed": webhook_metrics["total_processed"],
            "total_errors": webhook_metrics["total_errors"],
            "error_rate": (
                webhook_metrics["total_errors"] / webhook_metrics["total_received"]
                if webhook_metrics["total_received"] > 0 else 0
            ),
            "last_received": webhook_metrics["last_received"],
            "last_error": webhook_metrics["last_error"],
            "avg_processing_time_ms": round(avg_processing_time, 2)
        },
        "events_breakdown": dict(webhook_metrics["events_count"]),
        "hourly_stats": sorted(hourly_data, key=lambda x: x["hour"], reverse=True),
        "time_range": {
            "hours": hours,
            "from": cutoff_time.isoformat(),
            "to": now.isoformat()
        }
    }


@router.post("/test", dependencies=[Depends(verify_admin_api_key)])
async def send_test_webhook() -> Dict[str, Any]:
    """
    Envia um webhook de teste para verificar se está funcionando
    """
    test_payload = {
        "event": "TEST_WEBHOOK",
        "instance": os.getenv("EVOLUTION_INSTANCE_NAME", "test"),
        "data": {
            "timestamp": datetime.now().isoformat(),
            "message": "Este é um webhook de teste enviado pelo admin",
            "source": "webhook_admin"
        }
    }
    
    try:
        # Tentar enviar para o próprio endpoint
        import httpx
        
        webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
        webhook_url = f"{webhook_url}/webhook/whatsapp"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=test_payload,
                timeout=10.0
            )
            
            return {
                "status": "sent",
                "webhook_url": webhook_url,
                "response_status": response.status_code,
                "response_body": response.json() if response.status_code == 200 else None,
                "test_payload": test_payload
            }
            
    except Exception as e:
        logger.error(f"Erro ao enviar webhook de teste: {e}")
        return {
            "status": "error",
            "error": str(e),
            "webhook_url": webhook_url,
            "test_payload": test_payload
        }


@router.delete("/metrics", dependencies=[Depends(verify_admin_api_key)])
async def reset_metrics() -> Dict[str, Any]:
    """
    Reseta as métricas dos webhooks
    """
    global webhook_metrics
    
    # Salvar snapshot antes de resetar
    snapshot = {
        "reset_at": datetime.now().isoformat(),
        "metrics_before_reset": dict(webhook_metrics)
    }
    
    # Resetar métricas
    webhook_metrics = {
        "total_received": 0,
        "total_processed": 0,
        "total_errors": 0,
        "events_count": defaultdict(int),
        "last_received": None,
        "last_error": None,
        "hourly_stats": defaultdict(lambda: {"received": 0, "errors": 0}),
        "processing_times": []
    }
    
    logger.info("Métricas de webhook resetadas")
    
    return {
        "status": "reset",
        "snapshot": snapshot
    }


@router.get("/health")
async def webhook_health_check() -> Dict[str, Any]:
    """
    Verifica saúde do sistema de webhooks
    """
    health_status = "healthy"
    issues = []
    
    # Verificar se está recebendo webhooks
    if webhook_metrics["last_received"]:
        time_since_last = datetime.now() - webhook_metrics["last_received"]
        if time_since_last > timedelta(minutes=30):
            health_status = "warning"
            issues.append(f"Nenhum webhook recebido há {time_since_last.total_seconds() / 60:.0f} minutos")
    else:
        health_status = "warning"
        issues.append("Nenhum webhook recebido ainda")
    
    # Verificar taxa de erro
    if webhook_metrics["total_received"] > 100:  # Só verifica após 100 webhooks
        error_rate = webhook_metrics["total_errors"] / webhook_metrics["total_received"]
        if error_rate > 0.1:  # Mais de 10% de erro
            health_status = "unhealthy"
            issues.append(f"Taxa de erro alta: {error_rate:.1%}")
    
    # Verificar configuração
    try:
        webhook_config = await evolution_client.get_webhook_info()
        if not webhook_config.get("webhook", {}).get("enabled"):
            health_status = "unhealthy"
            issues.append("Webhook não está habilitado na Evolution API")
    except Exception as e:
        health_status = "unhealthy"
        issues.append(f"Não foi possível verificar Evolution API: {e}")
    
    return {
        "status": health_status,
        "issues": issues,
        "metrics": {
            "last_received": webhook_metrics["last_received"],
            "total_today": webhook_metrics["total_received"],
            "errors_today": webhook_metrics["total_errors"]
        },
        "timestamp": datetime.now().isoformat()
    }


# Função auxiliar para atualizar métricas (chamada pelos webhooks)
def update_webhook_metrics(event_type: str, success: bool, processing_time: float = None):
    """Atualiza métricas dos webhooks"""
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0).isoformat()
    
    webhook_metrics["total_received"] += 1
    webhook_metrics["events_count"][event_type] += 1
    webhook_metrics["last_received"] = datetime.now()
    webhook_metrics["hourly_stats"][current_hour]["received"] += 1
    
    if success:
        webhook_metrics["total_processed"] += 1
        if processing_time:
            webhook_metrics["processing_times"].append(processing_time)
            # Manter apenas últimos 1000 tempos
            if len(webhook_metrics["processing_times"]) > 1000:
                webhook_metrics["processing_times"] = webhook_metrics["processing_times"][-1000:]
    else:
        webhook_metrics["total_errors"] += 1
        webhook_metrics["last_error"] = datetime.now()
        webhook_metrics["hourly_stats"][current_hour]["errors"] += 1


@router.post("/reconfigure", dependencies=[Depends(verify_admin_api_key)])
async def reconfigure_webhook() -> Dict[str, Any]:
    """
    Reconfigura o webhook da Evolution API
    
    Este endpoint é útil quando o webhook URL muda no EasyPanel.
    Ele força uma reconfiguração com a URL correta.
    """
    try:
        # Obter configuração atual
        current_config = await evolution_client.get_webhook_info()
        logger.info(f"Configuração atual do webhook: {current_config}")
        
        # Configurar URL do webhook baseado no ambiente
        webhook_base_url = os.getenv("WEBHOOK_BASE_URL")
        if not webhook_base_url:
            # Tentar determinar automaticamente
            if os.getenv("ENVIRONMENT", "development") == "production":
                # Em produção no EasyPanel, usar nome do serviço interno
                service_name = os.getenv("SERVICE_NAME", "sdr-ia")
                webhook_base_url = f"http://{service_name}:8000"
            else:
                webhook_base_url = "http://localhost:8000"
        
        webhook_url = f"{webhook_base_url}/webhook/whatsapp"
        
        # Eventos essenciais para SDR
        essential_events = [
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "CONNECTION_UPDATE",
            "PRESENCE_UPDATE",
            "QRCODE_UPDATED"
        ]
        
        # Configurar webhook
        logger.info(f"Reconfigurando webhook para: {webhook_url}")
        result = await evolution_client.create_webhook(
            webhook_url=webhook_url,
            events=essential_events,
            webhook_by_events=False,
            webhook_base64=False
        )
        
        if result:
            logger.info("✅ Webhook reconfigurado com sucesso")
            return {
                "status": "success",
                "webhook_url": webhook_url,
                "events": essential_events,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao reconfigurar webhook")
            
    except Exception as e:
        logger.error(f"Erro ao reconfigurar webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao reconfigurar webhook: {str(e)}"
        )


@router.get("/auto-reconfigure/status")
async def get_auto_reconfigure_status() -> Dict[str, Any]:
    """
    Verifica o status da reconfiguração automática do webhook
    """
    from api.main import webhook_reconfigure_task
    
    task_running = webhook_reconfigure_task is not None and not webhook_reconfigure_task.done()
    
    return {
        "auto_reconfigure_enabled": task_running,
        "interval_minutes": int(os.getenv("WEBHOOK_RECONFIGURE_INTERVAL", "30")),
        "webhook_base_url": os.getenv("WEBHOOK_BASE_URL", "auto-detect"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }