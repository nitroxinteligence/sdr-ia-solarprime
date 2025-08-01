"""
Tool para criar reuniões no Google Calendar com Google Meet
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from loguru import logger

from ...services import get_calendar_service
from ...core.types import CalendarEvent
from ..core.agno_async_executor import AGnOAsyncExecutor


# CAMADA 2: Correção truncamento AGnO Framework
# create_meeting (14 chars) → create_meet (11 chars)
async def _create_meeting_async(
    title: str,
    date: str,
    start_time: str,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    timezone: str = "America/Sao_Paulo",
    send_notifications: bool = True
) -> Dict[str, any]:
    """
    Cria uma reunião no Google Calendar com link do Google Meet.
    
    Args:
        title: Título da reunião
        date: Data da reunião (formato: YYYY-MM-DD)
        start_time: Horário de início (formato: HH:MM)
        duration_minutes: Duração em minutos (padrão: 60)
        description: Descrição da reunião
        attendees: Lista de emails dos participantes
        timezone: Timezone da reunião (padrão: America/Sao_Paulo)
        send_notifications: Se deve enviar notificações aos participantes
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - meeting: dados da reunião criada
            - meet_link: link do Google Meet
            - calendar_link: link para o evento no Google Calendar
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Criando reunião: {title} em {date} às {start_time}")
        
        # Obter serviço de calendário
        calendar = get_calendar_service()
        
        if not calendar.is_available():
            logger.warning("Serviço do Google Calendar não está disponível")
            return {
                "success": False,
                "error": "Serviço do Google Calendar não está disponível",
                "meeting": None,
                "meet_link": None
            }
        
        # Converter data e hora para datetime
        try:
            date_parts = date.split("-")
            time_parts = start_time.split(":")
            
            start_datetime = datetime(
                year=int(date_parts[0]),
                month=int(date_parts[1]),
                day=int(date_parts[2]),
                hour=int(time_parts[0]),
                minute=int(time_parts[1]),
                tzinfo=ZoneInfo(timezone)
            )
        except (ValueError, IndexError):
            return {
                "success": False,
                "error": f"Formato de data/hora inválido. Use YYYY-MM-DD para data e HH:MM para hora",
                "meeting": None,
                "meet_link": None
            }
        
        # Verificar se o horário está dentro do horário comercial
        weekday = start_datetime.weekday()  # 0=Segunda, 6=Domingo
        hour = start_datetime.hour
        end_hour = (start_datetime + timedelta(minutes=duration_minutes)).hour
        
        if weekday == 6:  # Domingo
            return {
                "success": False,
                "error": "Não é possível agendar reuniões aos domingos",
                "meeting": None,
                "meet_link": None
            }
        elif weekday == 5:  # Sábado
            if hour < 8 or end_hour > 13:
                return {
                    "success": False,
                    "error": "Aos sábados, reuniões devem ser entre 8h e 13h",
                    "meeting": None,
                    "meet_link": None
                }
        else:  # Segunda a Sexta
            if hour < 8 or end_hour > 18:
                return {
                    "success": False,
                    "error": "Reuniões devem ser entre 8h e 18h em dias úteis",
                    "meeting": None,
                    "meet_link": None
                }
        
        # Verificar disponibilidade antes de criar
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        available_slots = await calendar.check_availability(
            date_start=start_datetime,
            date_end=end_datetime,
            timezone=timezone
        )
        
        # Verificar se o horário está disponível
        is_available = False
        for slot in available_slots:
            if slot.start <= start_datetime and slot.end >= end_datetime:
                is_available = True
                break
        
        if not is_available:
            logger.warning(f"Horário não disponível: {start_datetime}")
            return {
                "success": False,
                "error": f"Horário não disponível. Por favor, verifique a disponibilidade primeiro.",
                "meeting": None,
                "meet_link": None,
                "suggestion": "Use a tool check_availability para ver horários disponíveis"
            }
        
        # Preparar descrição
        if not description:
            description = f"Reunião: {title}\n\nAgendada via SDR IA SolarPrime"
        else:
            description += "\n\nAgendada via SDR IA SolarPrime"
        
        # Criar a reunião
        event = await calendar.create_meeting(
            title=title,
            description=description,
            start_time=start_datetime,
            duration_minutes=duration_minutes,
            attendees=attendees or [],
            timezone=timezone
        )
        
        if not event:
            return {
                "success": False,
                "error": "Falha ao criar reunião no calendário",
                "meeting": None,
                "meet_link": None
            }
        
        # Construir link do Google Calendar
        calendar_link = f"https://calendar.google.com/calendar/event?eid={event.id}"
        
        logger.success(f"Reunião criada com sucesso: {event.id} - {title}")
        
        return {
            "success": True,
            "meeting": {
                "id": event.id,
                "title": event.title,
                "date": start_datetime.strftime("%Y-%m-%d"),
                "start_time": start_datetime.strftime("%H:%M"),
                "end_time": (start_datetime + timedelta(minutes=duration_minutes)).strftime("%H:%M"),
                "duration_minutes": duration_minutes,
                "timezone": timezone,
                "description": event.description,
                "attendees": event.attendees,
                "status": event.status
            },
            "meet_link": event.meet_link,
            "calendar_link": calendar_link,
            "message": f"Reunião '{title}' criada com sucesso para {date} às {start_time}"
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar reunião: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao criar reunião: {str(e)}",
            "meeting": None,
            "meet_link": None
        }


# CAMADA 2: Wrapper síncrono com nome curto (evita truncamento)
# Resolve: create_meeting (14 chars) → create_meet (11 chars)
create_meet = AGnOAsyncExecutor.wrap_async_tool(_create_meeting_async)
create_meet.__name__ = "create_meet"  # Nome curto para evitar truncamento AGnO

# Export da tool - mantém compatibilidade
CreateMeetingTool = create_meet
create_meeting = create_meet  # Alias para compatibilidade