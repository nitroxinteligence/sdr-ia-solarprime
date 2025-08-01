"""
Tool para cancelar reuniões no Google Calendar
"""

from typing import Dict, Optional
from loguru import logger

from ...services import get_calendar_service


# CRÍTICO: AGnO Framework bug com @tool decorator em async functions
# Removendo @tool decorator conforme documentação oficial AGnO
# Issue #2296: https://github.com/agno-agi/agno/issues/2296
async def cancel_meeting(
    meeting_id: str,
    reason: Optional[str] = None,
    send_notifications: bool = True
) -> Dict[str, any]:
    """
    Cancela uma reunião existente no Google Calendar e notifica os participantes.
    
    Args:
        meeting_id: ID da reunião no Google Calendar
        reason: Motivo do cancelamento (opcional)
        send_notifications: Se deve enviar notificações de cancelamento aos participantes
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - cancelled: bool indicando se foi cancelada
            - meeting_id: ID da reunião cancelada
            - reason: motivo do cancelamento
            - notifications_sent: se notificações foram enviadas
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Cancelando reunião ID: {meeting_id}")
        
        # Obter serviço de calendário
        calendar = get_calendar_service()
        
        if not calendar.is_available():
            logger.warning("Serviço do Google Calendar não está disponível")
            return {
                "success": False,
                "cancelled": False,
                "error": "Serviço do Google Calendar não está disponível",
                "meeting_id": meeting_id,
                "notifications_sent": False
            }
        
        # Obter dados da reunião antes de cancelar (para log)
        try:
            # Buscar evento atual para obter informações
            from datetime import datetime, timedelta
            from zoneinfo import ZoneInfo
            
            now = datetime.now(ZoneInfo("America/Sao_Paulo"))
            events = await calendar.get_calendar_events(
                time_min=now - timedelta(days=365),
                time_max=now + timedelta(days=365),
                timezone="America/Sao_Paulo"
            )
            
            meeting_info = None
            for event in events:
                if event.id == meeting_id:
                    meeting_info = {
                        "title": event.title,
                        "date": event.start.strftime("%Y-%m-%d"),
                        "time": event.start.strftime("%H:%M"),
                        "attendees": len(event.attendees)
                    }
                    break
                    
            logger.info(f"Informações da reunião a cancelar: {meeting_info}")
            
        except Exception as e:
            logger.warning(f"Não foi possível obter informações da reunião: {e}")
            meeting_info = None
        
        # Cancelar a reunião
        cancelled = await calendar.cancel_event(
            event_id=meeting_id,
            send_notifications=send_notifications
        )
        
        if not cancelled:
            return {
                "success": False,
                "cancelled": False,
                "error": "Falha ao cancelar reunião no calendário",
                "meeting_id": meeting_id,
                "notifications_sent": False
            }
        
        # Preparar mensagem de resposta
        if reason:
            message = f"Reunião cancelada com sucesso. Motivo: {reason}"
        else:
            message = "Reunião cancelada com sucesso"
            
        if send_notifications:
            message += ". Participantes foram notificados."
        
        logger.success(f"Reunião {meeting_id} cancelada com sucesso")
        
        result = {
            "success": True,
            "cancelled": True,
            "meeting_id": meeting_id,
            "reason": reason or "Não especificado",
            "notifications_sent": send_notifications,
            "message": message
        }
        
        # Adicionar informações da reunião se disponíveis
        if meeting_info:
            result["cancelled_meeting"] = meeting_info
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao cancelar reunião: {e}", exc_info=True)
        return {
            "success": False,
            "cancelled": False,
            "error": f"Erro ao cancelar reunião: {str(e)}",
            "meeting_id": meeting_id,
            "notifications_sent": False
        }


# Exportar tool
CancelMeetingTool = cancel_meeting