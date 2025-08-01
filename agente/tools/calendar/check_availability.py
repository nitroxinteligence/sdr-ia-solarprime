"""
Tool para verificar disponibilidade no calendário
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from agno.tools import tool
from loguru import logger

from ...services import get_calendar_service
from ...core.types import CalendarSlot


@tool(show_result=True)
async def check_availability(
    date: str,
    duration_minutes: int = 60,
    timezone: str = "America/Sao_Paulo",
    check_days_ahead: int = 1
) -> Dict[str, any]:
    """
    Verifica disponibilidade no calendário em uma data específica.
    
    Args:
        date: Data para verificar (formato: YYYY-MM-DD)
        duration_minutes: Duração da reunião em minutos (padrão: 60)
        timezone: Timezone para verificação (padrão: America/Sao_Paulo)
        check_days_ahead: Quantos dias à frente verificar (padrão: 1)
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - available_slots: lista de slots disponíveis
            - total_slots: total de slots encontrados
            - business_hours: horário comercial utilizado
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Verificando disponibilidade para {date} com duração de {duration_minutes} minutos")
        
        # Obter serviço de calendário
        calendar = get_calendar_service()
        
        if not calendar.is_available():
            logger.warning("Serviço do Google Calendar não está disponível")
            return {
                "success": False,
                "error": "Serviço do Google Calendar não está disponível",
                "available_slots": [],
                "total_slots": 0
            }
        
        # Converter data string para datetime
        try:
            start_date = datetime.strptime(date, "%Y-%m-%d")
            start_date = start_date.replace(hour=8, minute=0, second=0, tzinfo=ZoneInfo(timezone))
        except ValueError:
            return {
                "success": False,
                "error": f"Formato de data inválido. Use YYYY-MM-DD. Recebido: {date}",
                "available_slots": [],
                "total_slots": 0
            }
        
        # Calcular período de verificação
        end_date = start_date + timedelta(days=check_days_ahead)
        
        # Verificar disponibilidade usando FreeBusy
        available_slots = await calendar.check_availability(
            date_start=start_date,
            date_end=end_date,
            timezone=timezone
        )
        
        # Filtrar slots pela duração solicitada
        if duration_minutes != 60:
            filtered_slots = []
            for slot in available_slots:
                slot_duration = (slot.end - slot.start).total_seconds() / 60
                if slot_duration >= duration_minutes:
                    # Ajustar o slot para a duração solicitada
                    adjusted_slot = CalendarSlot(
                        start=slot.start,
                        end=slot.start + timedelta(minutes=duration_minutes),
                        duration_minutes=duration_minutes
                    )
                    filtered_slots.append(adjusted_slot)
            available_slots = filtered_slots
        
        # Formatar slots para resposta
        formatted_slots = []
        for slot in available_slots:
            formatted_slots.append({
                "date": slot.start.strftime("%Y-%m-%d"),
                "start_time": slot.start.strftime("%H:%M"),
                "end_time": slot.end.strftime("%H:%M"),
                "duration_minutes": slot.duration_minutes,
                "timezone": timezone,
                "iso_start": slot.start.isoformat(),
                "iso_end": slot.end.isoformat()
            })
        
        # Horário comercial
        business_hours = {
            "weekdays": {
                "start": "08:00",
                "end": "18:00"
            },
            "saturday": {
                "start": "08:00",
                "end": "13:00"
            },
            "sunday": "closed"
        }
        
        logger.success(f"Encontrados {len(formatted_slots)} slots disponíveis para {date}")
        
        return {
            "success": True,
            "available_slots": formatted_slots,
            "total_slots": len(formatted_slots),
            "business_hours": business_hours,
            "query_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days_checked": check_days_ahead
            },
            "requested_duration": duration_minutes,
            "timezone": timezone
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar disponibilidade: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao verificar disponibilidade: {str(e)}",
            "available_slots": [],
            "total_slots": 0
        }


# Exportar tool
CheckAvailabilityTool = check_availability