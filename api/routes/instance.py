"""
Instance Management Routes
==========================
Rotas para gerenciar instância Evolution API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime

from services.evolution_api import evolution_client
from services.connection_monitor import connection_monitor

logger = logging.getLogger(__name__)
router = APIRouter()


def require_api_key(api_key: str) -> bool:
    """Verifica API key para endpoints administrativos"""
    expected_key = os.getenv("ADMIN_API_KEY")
    
    if not expected_key:
        return True  # Se não configurado, permite acesso (desenvolvimento)
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="API key inválida"
        )
    
    return True


@router.get("/status")
async def get_instance_status():
    """Obtém status atual da instância e conexão"""
    
    try:
        # Status da conexão
        connection_status = await connection_monitor.get_current_status()
        
        # Informações da instância
        instance_info = await evolution_client.get_instance_info()
        
        # Estatísticas de uptime
        uptime_stats = connection_monitor.get_uptime_stats()
        
        return {
            "instance_name": evolution_client.instance_name,
            "connection": connection_status,
            "instance_info": instance_info,
            "uptime_stats": uptime_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter status da instância"
        )


@router.get("/qrcode")
async def get_qrcode():
    """Obtém QR Code para conectar WhatsApp"""
    
    try:
        qr_data = await evolution_client.get_qrcode()
        
        if not qr_data:
            raise HTTPException(
                status_code=404,
                detail="QR Code não disponível"
            )
        
        return qr_data
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter QR Code: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter QR Code"
        )


@router.post("/restart")
async def restart_instance(
    api_key: str = Depends(require_api_key)
):
    """Reinicia instância do WhatsApp"""
    
    try:
        success = await evolution_client.restart_instance()
        
        if success:
            return {
                "status": "success",
                "message": "Instância reiniciada com sucesso"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Falha ao reiniciar instância"
            )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reiniciar instância: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao reiniciar instância"
        )


@router.post("/logout")
async def logout_instance(
    api_key: str = Depends(require_api_key)
):
    """Desconecta WhatsApp da instância"""
    
    try:
        success = await evolution_client.logout_instance()
        
        if success:
            return {
                "status": "success",
                "message": "WhatsApp desconectado"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Falha ao desconectar WhatsApp"
            )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desconectar: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao desconectar WhatsApp"
        )


@router.post("/reconnect")
async def force_reconnect(
    api_key: str = Depends(require_api_key)
):
    """Força reconexão do WhatsApp"""
    
    try:
        success = await connection_monitor.force_reconnect()
        
        if success:
            return {
                "status": "success",
                "message": "Reconexão realizada com sucesso"
            }
        else:
            return {
                "status": "error",
                "message": "Falha na reconexão - verifique os logs"
            }
            
    except Exception as e:
        logger.error(f"Erro ao forçar reconexão: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao forçar reconexão"
        )


@router.get("/webhook")
async def get_webhook_config():
    """Obtém configuração atual do webhook"""
    
    try:
        webhook_info = await evolution_client.get_webhook_info()
        
        return webhook_info or {
            "status": "not_configured",
            "message": "Webhook não configurado"
        }
            
    except Exception as e:
        logger.error(f"Erro ao obter webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter configuração do webhook"
        )


@router.post("/webhook/reset")
async def reset_webhook(
    api_key: str = Depends(require_api_key)
):
    """Reconfigura webhook para URL padrão"""
    
    try:
        webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
        webhook_endpoint = f"{webhook_url}/webhook/whatsapp"
        
        result = await evolution_client.create_webhook(
            webhook_url=webhook_endpoint,
            events=None,  # Usar eventos padrão
            webhook_by_events=False,
            webhook_base64=False
        )
        
        return {
            "status": "success",
            "webhook_url": webhook_endpoint,
            "result": result
            }
            
    except Exception as e:
        logger.error(f"Erro ao resetar webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao resetar webhook"
        )