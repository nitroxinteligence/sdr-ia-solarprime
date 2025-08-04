"""
Webhook para receber eventos do Kommo CRM
"""
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
from loguru import logger
from datetime import datetime

router = APIRouter(prefix="/webhook/kommo", tags=["kommo"])

@router.post("/events")
async def kommo_webhook(request: Request):
    """
    Recebe eventos do Kommo CRM
    """
    try:
        # Receber dados do webhook
        data = await request.json()
        
        # Log do evento recebido
        logger.info(f"📥 Evento Kommo recebido: {data.get('event_type', 'unknown')}")
        
        # Por enquanto, apenas confirmar recebimento
        # Futuramente podemos processar eventos específicos como:
        # - lead.created
        # - lead.updated
        # - lead.status_changed
        # - lead.deleted
        
        return {"status": "ok", "received_at": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook Kommo: {e}")
        # Retornar 200 mesmo com erro para evitar retry infinito
        return {"status": "error", "message": str(e)}

@router.get("/events")
async def kommo_webhook_test():
    """
    Endpoint de teste para verificar se o webhook está funcionando
    """
    return {
        "status": "ok",
        "message": "Kommo webhook endpoint is working",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/")
async def kommo_webhook_root(request: Request):
    """
    Rota alternativa para receber eventos (caso o Kommo não use /events)
    """
    try:
        data = await request.json()
        logger.info(f"📥 Evento Kommo recebido na rota raiz: {data}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return {"status": "error"}