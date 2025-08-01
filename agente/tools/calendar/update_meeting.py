"""
Tool para atualizar reuniões existentes no Google Calendar
"""

from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from agno.tools import tool
from loguru import logger

from ...services import get_calendar_service


@tool(show_result=True)
async def update_meeting(
    meeting_id: str,
    title: Optional[str] = None,
    date: Optional[str] = None,
    start_time: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    timezone: str = "America/Sao_Paulo"
) -> Dict[str, any]:
    """
    Atualiza dados de uma reunião existente no Google Calendar.
    
    Args:
        meeting_id: ID da reunião no Google Calendar
        title: Novo título da reunião (opcional)
        date: Nova data (formato: YYYY-MM-DD) (opcional)
        start_time: Novo horário de início (formato: HH:MM) (opcional)
        duration_minutes: Nova duração em minutos (opcional)
        description: Nova descrição (opcional)
        attendees: Nova lista de emails dos participantes (opcional)
        timezone: Timezone da reunião (padrão: America/Sao_Paulo)
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - meeting: dados atualizados da reunião
            - meet_link: link do Google Meet
            - changes: lista de alterações realizadas
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Atualizando reunião ID: {meeting_id}")
        
        # Obter serviço de calendário
        calendar = get_calendar_service()
        
        if not calendar.is_available():
            logger.warning("Serviço do Google Calendar não está disponível")
            return {
                "success": False,
                "error": "Serviço do Google Calendar não está disponível",
                "meeting": None,
                "changes": []
            }
        
        # Preparar dicionário de atualizações
        updates: Dict[str, Any] = {}
        changes = []
        
        # Processar título
        if title is not None:
            updates["title"] = title
            changes.append(f"Título alterado para: {title}")
        
        # Processar descrição
        if description is not None:
            updates["description"] = description
            changes.append("Descrição atualizada")
        
        # Processar participantes
        if attendees is not None:
            updates["attendees"] = attendees
            changes.append(f"Participantes atualizados: {len(attendees)} convidados")
        
        # Processar data e hora
        if date is not None or start_time is not None:
            try:
                # Se forneceu nova data/hora, precisa processar ambos
                if date and start_time:
                    date_parts = date.split("-")
                    time_parts = start_time.split(":")
                    
                    new_start = datetime(
                        year=int(date_parts[0]),
                        month=int(date_parts[1]),
                        day=int(date_parts[2]),
                        hour=int(time_parts[0]),
                        minute=int(time_parts[1]),
                        tzinfo=ZoneInfo(timezone)
                    )
                    
                    updates["start_time"] = new_start
                    changes.append(f"Data/hora alterada para: {date} às {start_time}")
                    
                    # Se forneceu duração, calcular novo fim
                    if duration_minutes is not None:
                        new_end = new_start + timedelta(minutes=duration_minutes)
                        updates["end_time"] = new_end
                        changes.append(f"Duração alterada para: {duration_minutes} minutos")
                else:
                    return {
                        "success": False,
                        "error": "Para alterar data/hora, forneça tanto 'date' quanto 'start_time'",
                        "meeting": None,
                        "changes": []
                    }
                    
            except (ValueError, IndexError):
                return {
                    "success": False,
                    "error": "Formato de data/hora inválido. Use YYYY-MM-DD para data e HH:MM para hora",
                    "meeting": None,
                    "changes": []
                }
        
        # Se não há atualizações
        if not updates:
            return {
                "success": False,
                "error": "Nenhuma alteração foi especificada",
                "meeting": None,
                "changes": []
            }
        
        # Verificar horário comercial se alterou data/hora
        if "start_time" in updates:
            new_start = updates["start_time"]
            weekday = new_start.weekday()
            hour = new_start.hour
            
            if weekday == 6:  # Domingo
                return {
                    "success": False,
                    "error": "Não é possível agendar reuniões aos domingos",
                    "meeting": None,
                    "changes": []
                }
            elif weekday == 5:  # Sábado
                if hour < 8 or hour >= 13:
                    return {
                        "success": False,
                        "error": "Aos sábados, reuniões devem ser entre 8h e 13h",
                        "meeting": None,
                        "changes": []
                    }
            else:  # Segunda a Sexta
                if hour < 8 or hour >= 18:
                    return {
                        "success": False,
                        "error": "Reuniões devem ser entre 8h e 18h em dias úteis",
                        "meeting": None,
                        "changes": []
                    }
        
        # Atualizar evento
        updated_event = await calendar.update_event(
            event_id=meeting_id,
            updates=updates
        )
        
        if not updated_event:
            return {
                "success": False,
                "error": "Falha ao atualizar reunião no calendário",
                "meeting": None,
                "changes": []
            }
        
        # Construir link do Google Calendar
        calendar_link = f"https://calendar.google.com/calendar/event?eid={updated_event.id}"
        
        logger.success(f"Reunião {meeting_id} atualizada com sucesso")
        
        return {
            "success": True,
            "meeting": {
                "id": updated_event.id,
                "title": updated_event.title,
                "date": updated_event.start.strftime("%Y-%m-%d"),
                "start_time": updated_event.start.strftime("%H:%M"),
                "end_time": updated_event.end.strftime("%H:%M"),
                "duration_minutes": int((updated_event.end - updated_event.start).total_seconds() / 60),
                "timezone": timezone,
                "description": updated_event.description,
                "attendees": updated_event.attendees,
                "status": updated_event.status
            },
            "meet_link": updated_event.meet_link,
            "calendar_link": calendar_link,
            "changes": changes,
            "message": f"Reunião atualizada com sucesso. {len(changes)} alterações realizadas."
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar reunião: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao atualizar reunião: {str(e)}",
            "meeting": None,
            "changes": []
        }


# Exportar tool
UpdateMeetingTool = update_meeting