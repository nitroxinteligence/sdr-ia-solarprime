"""
Follow-up Workflow Async Helper
================================
Helper para executar operações assíncronas do workflow
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from services.evolution_api import evolution_client


async def execute_follow_up_async(
    lead_data: Dict[str, Any],
    follow_up_type: str,
    message: str
) -> Dict[str, Any]:
    """
    Executa as operações assíncronas do follow-up
    
    Args:
        lead_data: Dados do lead
        follow_up_type: Tipo de follow-up
        message: Mensagem a enviar
        
    Returns:
        Resultado da execução
    """
    try:
        # Enviar mensagem via WhatsApp
        result = await evolution_client.send_text_message(
            phone=lead_data['phone'],
            message=message
        )
        
        return {
            'success': True,
            'message_id': result.get('key', {}).get('id'),
            'sent_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem WhatsApp: {e}")
        return {
            'success': False,
            'error': str(e)
        }