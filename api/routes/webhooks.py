"""
Webhook Routes
==============
Rotas para receber webhooks da Evolution API
"""

from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks, Body, Depends
from typing import Dict, Any, Optional
import logging
import hmac
import hashlib
import os
import json
import ipaddress
from datetime import datetime

from services.whatsapp_service import whatsapp_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])


def validate_webhook_ip(request: Request) -> bool:
    """Valida IP de origem do webhook"""
    allowed_ips = os.getenv("ALLOWED_WEBHOOK_IPS", "").split(",")
    
    if not allowed_ips or allowed_ips == [""]:
        return True  # Se não configurado, permite todos
    
    client_ip = request.client.host
    
    # Verificar se IP está na lista permitida
    for allowed_ip in allowed_ips:
        allowed_ip = allowed_ip.strip()
        if not allowed_ip:
            continue
            
        try:
            # Suporta ranges CIDR
            if "/" in allowed_ip:
                network = ipaddress.ip_network(allowed_ip, strict=False)
                if ipaddress.ip_address(client_ip) in network:
                    return True
            elif client_ip == allowed_ip:
                return True
        except ValueError:
            logger.error(f"IP inválido na configuração: {allowed_ip}")
    
    logger.warning(f"Webhook rejeitado de IP não autorizado: {client_ip}")
    return False


async def validate_webhook_security(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_webhook_signature: Optional[str] = Header(None),
    body: bytes = Body(...)
) -> bytes:
    """Valida segurança do webhook (IP e assinatura)"""
    
    # Verificar IP primeiro
    if not validate_webhook_ip(request):
        raise HTTPException(status_code=403, detail="IP not allowed")
    
    # Se validação de assinatura não está ativada, retornar body
    if os.getenv("WEBHOOK_VALIDATE_SIGNATURE", "false").lower() != "true":
        return body
    
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    if not webhook_secret:
        logger.warning("WEBHOOK_SECRET não configurado mas validação está ativada")
        return body
    
    # Tentar diferentes headers de assinatura
    signature = x_hub_signature_256 or x_webhook_signature
    
    if not signature:
        logger.warning("Webhook recebido sem assinatura")
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Calcular assinatura esperada
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Comparar assinaturas
    # Alguns serviços prefixam com "sha256="
    if signature.startswith("sha256="):
        signature = signature[7:]
    
    if not hmac.compare_digest(signature, expected_signature):
        logger.warning("Assinatura de webhook inválida")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return body


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    body: Dict[str, Any] = Body(...)
):
    """
    Recebe webhooks da Evolution API
    
    Este endpoint recebe eventos do WhatsApp através da Evolution API,
    incluindo mensagens, atualizações de status e mudanças de conexão.
    
    Segurança:
    - Validação de IP de origem (opcional)
    - Validação de assinatura HMAC (opcional)
    - Processamento assíncrono para resposta rápida
    """
    
    try:
        # Usar o body diretamente
        payload = body
        
        # Log do evento recebido
        event_type = payload.get("event", "UNKNOWN")
        instance = payload.get("instance", "unknown")
        
        logger.info(f"Webhook recebido: {event_type} da instância {instance}")
        logger.debug(f"Payload completo: {json.dumps(payload, ensure_ascii=False)}")
        
        # Processar webhook em background para responder rápido
        background_tasks.add_task(
            process_webhook_async,
            payload,
            event_type
        )
        
        # Evolution API espera 200 OK mesmo se não processamos
        return {
            "status": "ok",
            "event": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}", exc_info=True)
        
        # Ainda retorna 200 para Evolution API não reenviar
        return {
            "status": "error",
            "error": "Internal processing error",
            "timestamp": datetime.now().isoformat()
        }


async def process_webhook_async(payload: Dict[str, Any], event_type: str):
    """Processa webhook de forma assíncrona"""
    
    start_time = datetime.now()
    
    try:
        result = await whatsapp_service.process_webhook(payload)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000  # em ms
        
        # Atualizar métricas
        from api.routes.webhook_admin import update_webhook_metrics
        
        if result.get("status") == "error":
            logger.error(f"Erro no processamento: {result.get('error')}")
            update_webhook_metrics(event_type, success=False)
            await log_webhook_metric(event_type, "error", {
                "error": result.get('error'),
                "processing_time": processing_time
            })
        else:
            logger.info(f"Webhook processado com sucesso em {processing_time:.2f}ms")
            update_webhook_metrics(event_type, success=True, processing_time=processing_time)
            await log_webhook_metric(event_type, "success", {
                "processing_time": processing_time,
                "message_id": result.get("message_id")
            })
            
    except Exception as e:
        logger.error(f"Erro fatal no processamento do webhook: {e}", exc_info=True)
        update_webhook_metrics(event_type, success=False)
        await log_webhook_metric(event_type, "fatal_error", {"error": str(e)})


async def log_webhook_metric(event_type: str, status: str, details: Dict[str, Any]):
    """Registra métricas do webhook"""
    
    # TODO: Implementar envio para sistema de métricas (Prometheus, CloudWatch, etc)
    # Por enquanto, apenas log estruturado
    logger.info(f"Webhook metric: {event_type} - {status}", extra={
        "metric_type": "webhook_processing",
        "event_type": event_type,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })


@router.post("/test")
async def test_webhook():
    """Endpoint de teste para webhooks"""
    
    # Simular webhook de mensagem
    test_payload = {
        "event": "MESSAGES_UPSERT",
        "instance": "test",
        "data": {
            "key": {
                "id": "TEST123",
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False
            },
            "message": {
                "conversation": "Olá, quero saber sobre energia solar"
            },
            "messageTimestamp": 1234567890,
            "pushName": "Teste"
        }
    }
    
    result = await whatsapp_service.process_webhook(test_payload)
    
    return {
        "status": "test_completed",
        "result": result
    }


@router.get("/status")
async def webhook_status():
    """Verifica status e configuração do webhook"""
    
    # Testar normalização de eventos
    test_events = [
        "messages.upsert",
        "MESSAGES_UPSERT",
        "connection.update",
        "CONNECTION_UPDATE"
    ]
    
    normalized_events = {}
    for event in test_events:
        normalized = event.upper().replace(".", "_") if event else event
        normalized_events[event] = normalized
    
    return {
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.1-debug",  # Versão com debug
        "event_normalization_test": normalized_events,
        "config": {
            "signature_validation": os.getenv("WEBHOOK_VALIDATE_SIGNATURE", "false"),
            "ip_validation": bool(os.getenv("ALLOWED_WEBHOOK_IPS")),
            "webhook_secret_configured": bool(os.getenv("WEBHOOK_SECRET")),
            "evolution_api_configured": bool(os.getenv("EVOLUTION_API_URL")),
            "base_url": os.getenv("WEBHOOK_BASE_URL", "not_configured")
        },
        "security": {
            "https_required": os.getenv("ENVIRONMENT") == "production",
            "rate_limiting": bool(os.getenv("RATE_LIMIT_PER_MINUTE"))
        }
    }