"""
Tool para agendar atividades e tarefas para leads no Kommo CRM
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from agno.tools import tool
from loguru import logger

from ...services.kommo_service import get_kommo_service, KommoAPIError
from ...core.config import BUSINESS_HOURS_START, BUSINESS_HOURS_END, BUSINESS_DAYS


@tool(show_result=True, stop_after_tool_call=True)
async def schedule_kommo_activity(
    lead_id: int,
    activity_type: str,
    description: str,
    due_date: Optional[str] = None,
    due_time: Optional[str] = None,
    duration_minutes: Optional[int] = 30,
    responsible_user: Optional[int] = None
) -> Dict[str, Any]:
    """
    Agenda uma atividade/tarefa para um lead no Kommo CRM.
    
    Args:
        lead_id: ID do lead no Kommo
        activity_type: Tipo de atividade (call, meeting, email, task)
        description: Descrição da atividade
        due_date: Data de vencimento (formato: YYYY-MM-DD). Se não fornecida, usa próximo dia útil
        due_time: Hora de vencimento (formato: HH:MM). Se não fornecida, usa 10:00
        duration_minutes: Duração estimada em minutos (padrão: 30)
        responsible_user: ID do usuário responsável (opcional)
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - task_id: ID da tarefa criada
            - lead_id: ID do lead
            - due_datetime: data/hora de vencimento
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Agendando atividade '{activity_type}' para lead {lead_id}")
        
        # Validar tipo de atividade
        valid_types = ["call", "meeting", "email", "task", "follow_up", "whatsapp"]
        if activity_type.lower() not in valid_types:
            return {
                "success": False,
                "error": f"Tipo de atividade inválido. Use um dos: {', '.join(valid_types)}",
                "task_id": None,
                "lead_id": lead_id,
                "due_datetime": None
            }
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Verificar se lead existe
        try:
            lead = await kommo.get_lead(lead_id)
            lead_name = lead.get('name', 'Lead sem nome')
        except KommoAPIError as e:
            if e.status_code == 404:
                return {
                    "success": False,
                    "error": f"Lead {lead_id} não encontrado",
                    "task_id": None,
                    "lead_id": lead_id,
                    "due_datetime": None
                }
            raise
        
        # Processar data/hora de vencimento
        if due_date:
            try:
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                return {
                    "success": False,
                    "error": "Formato de data inválido. Use YYYY-MM-DD",
                    "task_id": None,
                    "lead_id": lead_id,
                    "due_datetime": None
                }
        else:
            # Usar próximo dia útil
            due_datetime = datetime.now()
            while True:
                due_datetime += timedelta(days=1)
                if str(due_datetime.weekday() + 1) in BUSINESS_DAYS:
                    break
        
        # Adicionar horário
        if due_time:
            try:
                time_parts = due_time.split(":")
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                due_datetime = due_datetime.replace(hour=hour, minute=minute)
            except (ValueError, IndexError):
                return {
                    "success": False,
                    "error": "Formato de hora inválido. Use HH:MM",
                    "task_id": None,
                    "lead_id": lead_id,
                    "due_datetime": None
                }
        else:
            # Usar horário padrão (10:00)
            due_datetime = due_datetime.replace(hour=10, minute=0)
        
        # Garantir que está dentro do horário comercial
        if due_datetime.hour < BUSINESS_HOURS_START:
            due_datetime = due_datetime.replace(hour=BUSINESS_HOURS_START, minute=0)
        elif due_datetime.hour >= BUSINESS_HOURS_END:
            due_datetime = due_datetime.replace(hour=BUSINESS_HOURS_END - 1, minute=0)
        
        # Mapear tipo de atividade para emoji e prefixo
        activity_mapping = {
            "call": "📞 Ligar para",
            "meeting": "🤝 Reunião com",
            "email": "📧 Enviar email para",
            "task": "📋 Tarefa:",
            "follow_up": "🔄 Follow-up com",
            "whatsapp": "📱 WhatsApp para"
        }
        
        # Construir texto da tarefa
        prefix = activity_mapping.get(activity_type.lower(), "📋")
        task_text = f"{prefix} {lead_name}"
        if description:
            task_text += f"\n\n{description}"
        
        if duration_minutes:
            task_text += f"\n\n⏱️ Duração estimada: {duration_minutes} minutos"
        
        # Criar tarefa no Kommo
        task = await kommo.create_task(
            lead_id=lead_id,
            text=task_text,
            complete_till=due_datetime
        )
        
        # Adicionar nota sobre a atividade agendada
        note_text = f"✅ Atividade agendada: {activity_type.upper()}\n"
        note_text += f"📅 Data/Hora: {due_datetime.strftime('%d/%m/%Y %H:%M')}\n"
        if description:
            note_text += f"📝 Descrição: {description}"
        
        try:
            await kommo.add_note(lead_id, note_text)
        except Exception as e:
            logger.warning(f"Erro ao adicionar nota sobre atividade: {e}")
        
        logger.success(
            f"Atividade '{activity_type}' agendada para lead {lead_id} em {due_datetime}"
        )
        
        return {
            "success": True,
            "task_id": task.get('id'),
            "lead_id": lead_id,
            "lead_name": lead_name,
            "activity_type": activity_type,
            "due_datetime": due_datetime.isoformat(),
            "duration_minutes": duration_minutes,
            "message": f"Atividade '{activity_type}' agendada com sucesso para {due_datetime.strftime('%d/%m/%Y %H:%M')}"
        }
        
    except KommoAPIError as e:
        logger.error(f"Erro da API do Kommo ao agendar atividade: {e}")
        return {
            "success": False,
            "task_id": None,
            "lead_id": lead_id,
            "due_datetime": None,
            "error": f"Erro da API do Kommo: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao agendar atividade: {e}")
        return {
            "success": False,
            "task_id": None,
            "lead_id": lead_id,
            "due_datetime": None,
            "error": f"Erro inesperado: {str(e)}"
        }


@tool(show_result=True)
async def schedule_follow_up(
    lead_id: int,
    days_from_now: int = 1,
    message: str = "Realizar follow-up com o lead",
    time: str = "10:00"
) -> Dict[str, Any]:
    """
    Agenda um follow-up simplificado para um lead.
    
    Args:
        lead_id: ID do lead no Kommo
        days_from_now: Número de dias a partir de hoje (padrão: 1)
        message: Mensagem do follow-up
        time: Horário do follow-up (formato: HH:MM)
        
    Returns:
        Dict contendo resultado da operação
    """
    try:
        logger.info(f"Agendando follow-up para lead {lead_id} em {days_from_now} dias")
        
        # Calcular data do follow-up
        follow_up_date = datetime.now()
        days_added = 0
        
        while days_added < days_from_now:
            follow_up_date += timedelta(days=1)
            # Pular fins de semana se necessário
            if str(follow_up_date.weekday() + 1) in BUSINESS_DAYS:
                days_added += 1
        
        # Formatar data
        due_date = follow_up_date.strftime("%Y-%m-%d")
        
        # Usar a função principal para agendar
        return await schedule_kommo_activity(
            lead_id=lead_id,
            activity_type="follow_up",
            description=message,
            due_date=due_date,
            due_time=time
        )
        
    except Exception as e:
        logger.error(f"Erro ao agendar follow-up: {e}")
        return {
            "success": False,
            "task_id": None,
            "lead_id": lead_id,
            "due_datetime": None,
            "error": f"Erro ao agendar follow-up: {str(e)}"
        }


@tool(show_result=True)
async def schedule_meeting_reminder(
    lead_id: int,
    meeting_datetime: str,
    location: str = "Online",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Agenda um lembrete de reunião para um lead.
    
    Args:
        lead_id: ID do lead no Kommo
        meeting_datetime: Data/hora da reunião (formato: YYYY-MM-DD HH:MM)
        location: Local da reunião (padrão: Online)
        notes: Notas adicionais sobre a reunião
        
    Returns:
        Dict contendo resultado da operação
    """
    try:
        logger.info(f"Agendando lembrete de reunião para lead {lead_id}")
        
        # Parsear data/hora da reunião
        try:
            meeting_dt = datetime.strptime(meeting_datetime, "%Y-%m-%d %H:%M")
        except ValueError:
            return {
                "success": False,
                "error": "Formato de data/hora inválido. Use YYYY-MM-DD HH:MM",
                "task_id": None,
                "lead_id": lead_id,
                "due_datetime": None
            }
        
        # Criar descrição da reunião
        description = f"📍 Local: {location}"
        if notes:
            description += f"\n\n📝 Notas: {notes}"
        
        # Agendar lembrete 1 hora antes da reunião
        reminder_dt = meeting_dt - timedelta(hours=1)
        
        # Usar a função principal para agendar
        result = await schedule_kommo_activity(
            lead_id=lead_id,
            activity_type="meeting",
            description=description,
            due_date=reminder_dt.strftime("%Y-%m-%d"),
            due_time=reminder_dt.strftime("%H:%M"),
            duration_minutes=60
        )
        
        if result["success"]:
            result["meeting_datetime"] = meeting_datetime
            result["location"] = location
            result["message"] = f"Lembrete de reunião agendado para {reminder_dt.strftime('%d/%m/%Y %H:%M')}"
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao agendar lembrete de reunião: {e}")
        return {
            "success": False,
            "task_id": None,
            "lead_id": lead_id,
            "due_datetime": None,
            "error": f"Erro ao agendar lembrete: {str(e)}"
        }


# Exportar tools
ScheduleKommoActivityTool = schedule_kommo_activity
ScheduleFollowUpTool = schedule_follow_up
ScheduleMeetingReminderTool = schedule_meeting_reminder