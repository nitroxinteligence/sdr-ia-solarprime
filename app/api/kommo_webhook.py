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
        # Tentar receber dados em diferentes formatos
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            try:
                data = await request.json()
            except:
                # Se falhar, tentar como texto
                body = await request.body()
                if body:
                    data = {"raw_data": body.decode('utf-8', errors='ignore')}
                else:
                    data = {"event": "empty_body"}
        elif "application/x-www-form-urlencoded" in content_type:
            # Kommo pode enviar como form data
            form_data = await request.form()
            data = dict(form_data)
        else:
            # Receber como texto raw
            body = await request.body()
            if body:
                data = {"raw_data": body.decode('utf-8', errors='ignore')}
            else:
                data = {"event": "ping"}
        
        # Log do evento recebido (apenas em debug para não poluir o log)
        if data != {"event": "ping"}:
            logger.debug(f"📥 Evento Kommo recebido: {data}")
        
        # Processar eventos específicos se necessário
        if isinstance(data, dict):
            event_type = data.get('event_type') or data.get('event') or 'unknown'
            
            # Processar apenas eventos importantes
            if event_type in ['lead.created', 'lead.updated', 'lead.status_changed']:
                logger.info(f"📌 Evento Kommo importante: {event_type}")
        
        # Sempre retornar 200 OK para o Kommo
        return {"status": "ok", "received_at": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado no webhook Kommo: {e}")
        # Retornar 200 mesmo com erro para evitar retry infinito
        return {"status": "ok", "error_handled": True}

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