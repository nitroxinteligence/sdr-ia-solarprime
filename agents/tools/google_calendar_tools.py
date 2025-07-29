"""
Google Calendar Tools for SDR Agent
===================================
Ferramentas customizadas de Google Calendar para o agente SDR
Integra com AGnO Framework GoogleCalendarTools
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
from loguru import logger
from agno.tools import tool
from agno.tools.googlecalendar import GoogleCalendarTools

from config.google_calendar_config import google_calendar_config
from services.google_calendar_service import get_google_calendar_service
from repositories.lead_repository import lead_repository


@tool
async def schedule_solar_meeting(
    lead_phone: str,
    date: str,
    time: str,
    lead_name: Optional[str] = None,
    meeting_type: str = "initial_meeting"
) -> Dict[str, Any]:
    """
    Agenda uma reunião para apresentação da SolarPrime
    
    Args:
        lead_phone: Telefone do lead
        date: Data no formato DD/MM/YYYY
        time: Horário no formato HH:MM
        lead_name: Nome do lead (opcional)
        meeting_type: Tipo de reunião (initial_meeting, follow_up_meeting, contract_signing)
    
    Returns:
        Dict com status do agendamento e link do evento
    """
    try:
        logger.info(f"📅 Agendando reunião: {date} {time} para {lead_phone}")
        
        # Buscar dados do lead
        lead = await lead_repository.get_lead_by_phone(lead_phone)
        if not lead:
            return {
                "status": "erro",
                "mensagem": "Lead não encontrado. Por favor, forneça suas informações primeiro."
            }
        
        # Preparar dados do lead
        lead_data = {
            'id': str(lead.id),
            'name': lead_name or lead.name,
            'phone': lead_phone,
            'email': lead.email,
            'bill_value': lead.bill_value or 0,
            'consumption_kwh': lead.consumption_kwh or 0,
            'solution_interest': lead.solution_interest or 'A definir',
            'crm_link': lead.kommo_lead_id or '#'
        }
        
        # Converter data e hora
        try:
            # Parse da data brasileira
            day, month, year = date.split('/')
            hour, minute = time.split(':')
            
            meeting_datetime = datetime(
                int(year), int(month), int(day),
                int(hour), int(minute)
            )
            
            # Validar horário comercial
            if not _is_business_hours(meeting_datetime):
                return {
                    "status": "horário_inválido",
                    "mensagem": "Por favor, escolha um horário entre 9h e 18h de segunda a sexta.",
                    "horarios_disponiveis": await get_available_slots(date)
                }
            
        except ValueError:
            return {
                "status": "erro",
                "mensagem": "Formato de data ou hora inválido. Use DD/MM/AAAA e HH:MM"
            }
        
        # Obter serviço do Google Calendar
        calendar_service = get_google_calendar_service()
        
        # Obter template
        template = google_calendar_config.get_event_template(meeting_type)
        
        # Formatar título e descrição
        title = template['title'].format(lead_name=lead_data['name'])
        description = template['description'].format(**lead_data)
        
        # Criar evento
        event_result = await calendar_service.create_event(
            title=title,
            start_datetime=meeting_datetime,
            description=description,
            location=google_calendar_config.meeting_location,
            attendees=[lead.email] if lead.email else None,
            lead_data=lead_data
        )
        
        if event_result:
            # Atualizar lead com informações da reunião
            await lead_repository.update_lead(
                lead_id=lead.id,
                meeting_scheduled_at=meeting_datetime,
                current_stage='MEETING_SCHEDULED',
                notes=f"Reunião agendada para {date} às {time}"
            )
            
            return {
                "status": "sucesso",
                "mensagem": f"""✅ Reunião agendada com sucesso!

📅 Data: {date}
🕐 Horário: {time}
📍 Local: {google_calendar_config.meeting_location}

Enviaremos lembretes:
- 1 dia antes
- 1 hora antes
- 15 minutos antes

Link do evento: {event_result['link']}""",
                "event_id": event_result['id'],
                "event_link": event_result['link']
            }
        else:
            return {
                "status": "erro",
                "mensagem": "Não foi possível agendar a reunião. Por favor, tente novamente."
            }
            
    except Exception as e:
        logger.error(f"Erro ao agendar reunião: {e}")
        return {
            "status": "erro",
            "mensagem": "Ocorreu um erro ao agendar. Nosso time entrará em contato."
        }


@tool
async def reschedule_meeting(
    lead_phone: str,
    new_date: str,
    new_time: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reagenda uma reunião existente
    
    Args:
        lead_phone: Telefone do lead
        new_date: Nova data no formato DD/MM/YYYY
        new_time: Novo horário no formato HH:MM
        reason: Motivo do reagendamento (opcional)
    
    Returns:
        Dict com status do reagendamento
    """
    try:
        logger.info(f"🔄 Reagendando reunião para {lead_phone}")
        
        # Buscar lead e evento atual
        lead = await lead_repository.get_lead_by_phone(lead_phone)
        if not lead or not lead.meeting_scheduled_at:
            return {
                "status": "erro",
                "mensagem": "Não encontrei uma reunião agendada para reagendar."
            }
        
        # TODO: Buscar event_id do banco ou metadata
        # Por ora, vamos criar um novo evento
        
        # Converter nova data e hora
        try:
            day, month, year = new_date.split('/')
            hour, minute = new_time.split(':')
            
            new_datetime = datetime(
                int(year), int(month), int(day),
                int(hour), int(minute)
            )
            
        except ValueError:
            return {
                "status": "erro",
                "mensagem": "Formato de data ou hora inválido. Use DD/MM/AAAA e HH:MM"
            }
        
        # Agendar nova reunião
        result = await schedule_solar_meeting(
            lead_phone=lead_phone,
            date=new_date,
            time=new_time,
            lead_name=lead.name,
            meeting_type="follow_up_meeting"
        )
        
        if result['status'] == 'sucesso':
            # Adicionar informação sobre reagendamento
            result['mensagem'] = f"✅ Reunião reagendada com sucesso!\n\n{result['mensagem']}"
            
            # Registrar motivo se fornecido
            if reason:
                await lead_repository.update_lead(
                    lead_id=lead.id,
                    notes=f"Reunião reagendada. Motivo: {reason}"
                )
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao reagendar reunião: {e}")
        return {
            "status": "erro",
            "mensagem": "Ocorreu um erro ao reagendar. Por favor, tente novamente."
        }


@tool
async def cancel_meeting(
    lead_phone: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cancela uma reunião agendada
    
    Args:
        lead_phone: Telefone do lead
        reason: Motivo do cancelamento (opcional)
    
    Returns:
        Dict com status do cancelamento
    """
    try:
        logger.info(f"❌ Cancelando reunião para {lead_phone}")
        
        # Buscar lead
        lead = await lead_repository.get_lead_by_phone(lead_phone)
        if not lead or not lead.meeting_scheduled_at:
            return {
                "status": "erro",
                "mensagem": "Não encontrei uma reunião agendada para cancelar."
            }
        
        # TODO: Implementar cancelamento real no Google Calendar
        # Por ora, apenas atualizar o banco
        
        # Atualizar lead
        await lead_repository.update_lead(
            lead_id=lead.id,
            meeting_scheduled_at=None,
            current_stage='QUALIFICATION',
            notes=f"Reunião cancelada. Motivo: {reason or 'Não especificado'}"
        )
        
        return {
            "status": "sucesso",
            "mensagem": """❌ Reunião cancelada.

Que pena! Quando quiser remarcar, é só me avisar.
Estou aqui para ajudar você a economizar na conta de luz! ☀️"""
        }
        
    except Exception as e:
        logger.error(f"Erro ao cancelar reunião: {e}")
        return {
            "status": "erro",
            "mensagem": "Ocorreu um erro ao cancelar. Por favor, tente novamente."
        }


@tool
async def get_available_slots(date: str) -> List[str]:
    """
    Retorna horários disponíveis para agendamento em uma data
    
    Args:
        date: Data no formato DD/MM/YYYY
    
    Returns:
        Lista de horários disponíveis no formato HH:MM
    """
    try:
        # Converter data
        day, month, year = date.split('/')
        target_date = datetime(int(year), int(month), int(day))
        
        # Obter serviço
        calendar_service = get_google_calendar_service()
        
        # Buscar disponibilidade
        available_slots = await calendar_service.check_availability(
            date=target_date,
            duration_minutes=google_calendar_config.default_meeting_duration,
            work_hours=(
                google_calendar_config.business_hours_start,
                google_calendar_config.business_hours_end
            )
        )
        
        # Formatar slots
        return [slot['start'] for slot in available_slots]
        
    except Exception as e:
        logger.error(f"Erro ao buscar horários disponíveis: {e}")
        # Retornar horários padrão se falhar
        return [
            "09:00", "10:00", "11:00",
            "14:00", "15:00", "16:00", "17:00"
        ]


@tool
async def check_next_meeting(lead_phone: str) -> Dict[str, Any]:
    """
    Verifica a próxima reunião agendada para um lead
    
    Args:
        lead_phone: Telefone do lead
    
    Returns:
        Dict com informações da próxima reunião
    """
    try:
        lead = await lead_repository.get_lead_by_phone(lead_phone)
        
        if not lead or not lead.meeting_scheduled_at:
            return {
                "status": "sem_reunião",
                "mensagem": "Você ainda não tem reunião agendada. Quer agendar agora?"
            }
        
        # Verificar se a reunião é futura
        if lead.meeting_scheduled_at > datetime.now():
            return {
                "status": "agendada",
                "data": lead.meeting_scheduled_at.strftime("%d/%m/%Y"),
                "horario": lead.meeting_scheduled_at.strftime("%H:%M"),
                "mensagem": f"""📅 Sua reunião está agendada:

Data: {lead.meeting_scheduled_at.strftime("%d/%m/%Y")}
Horário: {lead.meeting_scheduled_at.strftime("%H:%M")}
Local: {google_calendar_config.meeting_location}

Precisa reagendar?"""
            }
        else:
            return {
                "status": "passada",
                "mensagem": "Sua reunião já passou. Gostaria de agendar uma nova?"
            }
            
    except Exception as e:
        logger.error(f"Erro ao verificar reunião: {e}")
        return {
            "status": "erro",
            "mensagem": "Não consegui verificar sua reunião. Tente novamente."
        }


def _is_business_hours(dt: datetime) -> bool:
    """Verifica se o horário está dentro do expediente"""
    # Verificar dia da semana (0 = segunda, 6 = domingo)
    if dt.weekday() not in google_calendar_config.business_days:
        return False
    
    # Verificar horário
    hour = dt.hour
    return (
        google_calendar_config.business_hours_start <= hour < 
        google_calendar_config.business_hours_end
    )


# Exportar tools para uso no agente
calendar_tools = [
    schedule_solar_meeting,
    reschedule_meeting,
    cancel_meeting,
    get_available_slots,
    check_next_meeting
]