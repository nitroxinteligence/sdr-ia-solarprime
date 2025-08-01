"""
Tool para enviar convite de calendário via WhatsApp
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from agno.tools import tool
from loguru import logger

from ...services import get_calendar_service, get_evolution_service


@tool(show_result=True, stop_after_tool_call=True)
async def send_calendar_invite(
    phone_number: str,
    meeting_id: str,
    custom_message: Optional[str] = None,
    include_meet_link: bool = True,
    include_ics_file: bool = False
) -> Dict[str, any]:
    """
    Envia convite de calendário para uma reunião via WhatsApp.
    
    Args:
        phone_number: Número de WhatsApp do destinatário (formato: 5511999999999)
        meeting_id: ID da reunião no Google Calendar
        custom_message: Mensagem personalizada (opcional)
        include_meet_link: Se deve incluir o link do Google Meet
        include_ics_file: Se deve gerar e enviar arquivo .ics (não implementado)
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - message_sent: bool indicando se mensagem foi enviada
            - meeting_details: detalhes da reunião
            - whatsapp_message_id: ID da mensagem enviada
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Enviando convite da reunião {meeting_id} para {phone_number}")
        
        # Obter serviços
        calendar = get_calendar_service()
        whatsapp = get_evolution_service()
        
        if not calendar.is_available():
            logger.warning("Serviço do Google Calendar não está disponível")
            return {
                "success": False,
                "message_sent": False,
                "error": "Serviço do Google Calendar não está disponível",
                "meeting_details": None
            }
        
        # Buscar informações da reunião
        try:
            now = datetime.now(ZoneInfo("America/Sao_Paulo"))
            events = await calendar.get_calendar_events(
                time_min=now - datetime.timedelta(days=30),
                time_max=now + datetime.timedelta(days=365),
                timezone="America/Sao_Paulo"
            )
            
            meeting = None
            for event in events:
                if event.id == meeting_id:
                    meeting = event
                    break
                    
            if not meeting:
                return {
                    "success": False,
                    "message_sent": False,
                    "error": f"Reunião com ID {meeting_id} não encontrada",
                    "meeting_details": None
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar reunião: {e}")
            return {
                "success": False,
                "message_sent": False,
                "error": f"Erro ao buscar informações da reunião: {str(e)}",
                "meeting_details": None
            }
        
        # Formatar detalhes da reunião
        meeting_details = {
            "title": meeting.title,
            "date": meeting.start.strftime("%d/%m/%Y"),
            "day_of_week": _get_weekday_name(meeting.start.weekday()),
            "start_time": meeting.start.strftime("%H:%M"),
            "end_time": meeting.end.strftime("%H:%M"),
            "duration_minutes": int((meeting.end - meeting.start).total_seconds() / 60),
            "meet_link": meeting.meet_link if include_meet_link else None
        }
        
        # Construir mensagem
        if custom_message:
            message = custom_message + "\n\n"
        else:
            message = "🗓️ *Confirmação de Reunião - SolarPrime*\n\n"
        
        message += f"📌 *{meeting.title}*\n"
        message += f"📅 Data: {meeting_details['date']} ({meeting_details['day_of_week']})\n"
        message += f"⏰ Horário: {meeting_details['start_time']} às {meeting_details['end_time']}\n"
        message += f"⏱️ Duração: {meeting_details['duration_minutes']} minutos\n"
        
        if include_meet_link and meeting.meet_link:
            message += f"\n💻 *Link da Reunião:*\n{meeting.meet_link}\n"
            message += "\n_Clique no link acima para participar da reunião no horário agendado._\n"
        
        if meeting.description:
            message += f"\n📝 *Detalhes:*\n{meeting.description}\n"
        
        message += "\n✅ *Dicas para a reunião:*\n"
        message += "• Teste sua conexão de internet antes\n"
        message += "• Prepare suas dúvidas sobre energia solar\n"
        message += "• Tenha em mãos sua conta de energia\n"
        
        message += "\n⚠️ _Caso precise reagendar, entre em contato conosco._"
        
        # Enviar mensagem via WhatsApp
        try:
            # Formatar número se necessário
            if not phone_number.startswith("55"):
                phone_number = "55" + phone_number
                
            # Enviar mensagem
            result = await whatsapp.send_text_message(
                to=phone_number,
                text=message
            )
            
            if result.get("success"):
                whatsapp_message_id = result.get("message_id")
                logger.success(f"Convite enviado com sucesso para {phone_number}")
                
                return {
                    "success": True,
                    "message_sent": True,
                    "meeting_details": meeting_details,
                    "whatsapp_message_id": whatsapp_message_id,
                    "phone_number": phone_number,
                    "message": "Convite de calendário enviado com sucesso via WhatsApp"
                }
            else:
                return {
                    "success": False,
                    "message_sent": False,
                    "error": f"Falha ao enviar mensagem WhatsApp: {result.get('error')}",
                    "meeting_details": meeting_details
                }
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {e}")
            return {
                "success": False,
                "message_sent": False,
                "error": f"Erro ao enviar mensagem: {str(e)}",
                "meeting_details": meeting_details
            }
        
    except Exception as e:
        logger.error(f"Erro ao enviar convite de calendário: {e}", exc_info=True)
        return {
            "success": False,
            "message_sent": False,
            "error": f"Erro ao processar convite: {str(e)}",
            "meeting_details": None
        }


def _get_weekday_name(weekday: int) -> str:
    """Retorna o nome do dia da semana em português"""
    days = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }
    return days.get(weekday, "")


# Exportar tool
SendCalendarInviteTool = send_calendar_invite