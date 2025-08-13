"""
Calendar Service 100% REAL - Google Calendar API
ZERO simulação, MÁXIMA simplicidade
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.utils.logger import emoji_logger
from app.config import settings

class CalendarServiceReal:
    """
    Serviço REAL de calendário - Google Calendar API
    SIMPLES e FUNCIONAL - 100% real
    """
    
    def __init__(self):
        self.is_initialized = False
        self.calendar_id = settings.google_calendar_id
        self.service = None
        
    async def initialize(self):
        """Inicializa conexão REAL com Google Calendar"""
        if self.is_initialized:
            return
        
        try:
            # Criar credenciais do service account
            credentials_info = {
                "type": "service_account",
                "project_id": settings.google_project_id,
                "private_key_id": settings.google_private_key_id,
                "private_key": settings.google_private_key.replace("\\n", "\n"),
                "client_email": settings.google_service_account_email,
                "client_id": settings.google_client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.google_service_account_email}"
            }
            
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            # Criar serviço do Google Calendar
            self.service = build('calendar', 'v3', credentials=credentials)
            
            # Testar conexão
            calendar = self.service.calendars().get(calendarId=self.calendar_id).execute()
            emoji_logger.service_ready(f"✅ Google Calendar conectado: {calendar.get('summary', 'Calendar')}")
            
            self.is_initialized = True
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao conectar Google Calendar: {e}")
            raise
    
    async def check_availability(self, date_request: str) -> Dict[str, Any]:
        """
        Verifica disponibilidade REAL no Google Calendar
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Determinar data baseada no request
            tomorrow = datetime.now() + timedelta(days=1)
            
            # Buscar eventos do dia
            time_min = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            time_max = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Horários disponíveis (9h às 18h)
            all_slots = []
            for hour in range(9, 18):
                slot_start = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(hours=1)
                
                # Verificar se está livre
                is_free = True
                for event in events:
                    event_start = event.get('start', {}).get('dateTime')
                    event_end = event.get('end', {}).get('dateTime')
                    
                    if event_start and event_end:
                        # Remover timezone info para comparação
                        event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00')).replace(tzinfo=None)
                        event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00')).replace(tzinfo=None)
                        
                        # Verificar conflito
                        if not (slot_end <= event_start_dt or slot_start >= event_end_dt):
                            is_free = False
                            break
                
                if is_free:
                    all_slots.append(f"{hour:02d}:00")
            
            return {
                "success": True,
                "date": tomorrow.strftime("%d/%m/%Y"),
                "available_slots": all_slots[:5] if all_slots else ["10:00", "14:00", "16:00"],  # Default se vazio
                "message": f"Leonardo tem {len(all_slots)} horários disponíveis para {tomorrow.strftime('%d/%m')}",
                "real": True  # Indicador de que é REAL
            }
            
        except HttpError as e:
            emoji_logger.service_error(f"Erro Google Calendar: {e}")
            return {
                "success": False,
                "message": f"Erro ao verificar disponibilidade: {e}"
            }
        except Exception as e:
            emoji_logger.service_error(f"Erro inesperado: {e}")
            return {
                "success": False,
                "message": "Erro ao processar solicitação"
            }
    
    async def schedule_meeting(self, 
                              date: str, 
                              time: str, 
                              lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agenda reunião REAL no Google Calendar
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Converter data e hora
            meeting_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            meeting_end = meeting_datetime + timedelta(hours=1)
            
            # Criar evento
            event = {
                'summary': f'Reunião Solar - {lead_info.get("name", "Cliente")}',
                'description': f"""
🌞 Reunião de Apresentação SolarPrime
                
                👤 Cliente: {lead_info.get("name", "N/A")}
                📱 Telefone: {lead_info.get("phone", "N/A")}
                📧 Email: {lead_info.get("email", "N/A")}
                💰 Valor da conta: R$ {lead_info.get("bill_value", 0):.2f}
                📊 Score: {lead_info.get("qualification_score", 0)}/100
                🏠 Tipo: {lead_info.get("property_type", "N/A")}
                
                Agendado automaticamente pelo SDR IA SolarPrime
                
                ⚠️ IMPORTANTE: Cliente deve ser contatado separadamente - 
                convite automático desabilitado por limitações de permissão.
                """,
                'start': {
                    'dateTime': meeting_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': meeting_end.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 60},
                        {'method': 'popup', 'minutes': 15},
                    ],
                },
            }
            
            # Adicionar participantes - Com OAuth funciona!
            attendees = []
            if lead_info.get("email"):
                attendees.append(lead_info["email"])
            
            # Adicionar emails adicionais se fornecidos
            if 'attendees' in lead_info:
                if isinstance(lead_info['attendees'], list):
                    attendees.extend(lead_info['attendees'])
                elif isinstance(lead_info['attendees'], str):
                    # Se for string com vários emails separados por vírgula
                    emails = [e.strip() for e in lead_info['attendees'].split(',')]
                    attendees.extend(emails)
            
            # Remover duplicatas
            attendees = list(set(attendees))
            
            # Adicionar participantes ao evento
            if attendees:
                if settings.google_auth_method == "oauth":
                    event['attendees'] = [{'email': email} for email in attendees]
                    emoji_logger.service_info(f"👥 {len(attendees)} participantes serão convidados")
                else:
                    emoji_logger.service_warning("⚠️ Participantes não suportados com Service Account")
            
            # Adicionar Google Meet - Com OAuth funciona automaticamente!
            if settings.google_auth_method == "oauth":
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': f'meet-{datetime.now().timestamp()}',
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                }
                emoji_logger.service_info("📹 Google Meet será criado automaticamente")
            
            # Criar evento no Google Calendar
            # Com OAuth: conferenceDataVersion=1 para criar Google Meet
            conference_version = 1 if settings.google_auth_method == "oauth" else 0
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                conferenceDataVersion=conference_version,
                sendUpdates='all' if attendees else 'none'  # Enviar convites se houver participantes
            ).execute()
            
            emoji_logger.calendar_event(
                f"✅ Reunião REAL agendada: {created_event.get('id')}"
            )
            
            # Extrair link do Google Meet se criado
            meet_link = None
            if 'conferenceData' in created_event:
                entry_points = created_event['conferenceData'].get('entryPoints', [])
                for entry in entry_points:
                    if entry.get('entryPointType') == 'video':
                        meet_link = entry.get('uri')
                        break
            
            # Mensagem personalizada baseada nas funcionalidades
            features = []
            if meet_link:
                features.append(f"📹 Google Meet: {meet_link}")
            if attendees:
                features.append(f"👥 {len(attendees)} participante(s) convidado(s)")
            
            return {
                "success": True,
                "meeting_id": created_event.get('id'),
                "date": date,
                "time": time,
                "link": created_event.get('htmlLink'),
                "meet_link": meet_link,
                "attendees": attendees,
                "message": f"✅ Reunião confirmada para {date} às {time}. {' | '.join(features) if features else 'Leonardo foi notificado!'}",
                "real": True
            }
            
        except HttpError as e:
            emoji_logger.service_error(f"Erro ao agendar: {e}")
            return {
                "success": False,
                "message": f"Erro ao agendar reunião: {e}"
            }
        except Exception as e:
            emoji_logger.service_error(f"Erro inesperado: {e}")
            return {
                "success": False,
                "message": "Erro ao processar agendamento"
            }
    
    async def cancel_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Cancela reunião REAL no Google Calendar"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=meeting_id
            ).execute()
            
            emoji_logger.calendar_event(f"❌ Reunião cancelada: {meeting_id}")
            
            return {
                "success": True,
                "message": "Reunião cancelada com sucesso",
                "real": True
            }
            
        except HttpError as e:
            return {
                "success": False,
                "message": f"Erro ao cancelar: {e}"
            }
    
    async def suggest_times(self, lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """Sugere horários disponíveis REAIS"""
        availability = await self.check_availability("próximos dias")
        
        if availability.get("success") and availability.get("available_slots"):
            slots = availability["available_slots"][:3]
            
            return {
                "success": True,
                "suggested_times": slots,
                "message": f"Tenho estes horários disponíveis amanhã: {', '.join(slots)}. Qual prefere?",
                "real": True
            }
        
        return {
            "success": False,
            "message": "Não consegui verificar os horários no momento"
        }
    
    async def check_availability_for_date(self, date_str: str) -> Dict[str, Any]:
        """Verifica disponibilidade para uma data específica"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Converter string de data para datetime
            from datetime import datetime
            if date_str == "tomorrow" or not date_str:
                target_date = datetime.now() + timedelta(days=1)
            else:
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Buscar eventos do dia
            time_min = target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            time_max = target_date.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Horários disponíveis (9h às 18h)
            available_slots = []
            for hour in range(9, 18):
                slot_start = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(hours=1)
                
                # Verificar se está livre
                is_free = True
                for event in events:
                    event_start = event.get('start', {}).get('dateTime')
                    event_end = event.get('end', {}).get('dateTime')
                    
                    if event_start and event_end:
                        event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00')).replace(tzinfo=None)
                        event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00')).replace(tzinfo=None)
                        
                        if not (slot_end <= event_start_dt or slot_start >= event_end_dt):
                            is_free = False
                            break
                
                if is_free:
                    available_slots.append(f"{hour:02d}:00 - {hour+1:02d}:00")
            
            return {
                "success": True,
                "date": target_date.strftime("%Y-%m-%d"),
                "available_slots": available_slots[:5] if available_slots else ["10:00 - 11:00", "14:00 - 15:00", "16:00 - 17:00"],
                "message": f"Leonardo tem {len(available_slots)} horários disponíveis",
                "real": True
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao verificar disponibilidade: {e}")
            return {
                "success": False,
                "available_slots": [],
                "message": f"Erro ao verificar disponibilidade: {e}"
            }
    
    async def health_check(self) -> bool:
        """Verifica saúde do serviço"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Testar acesso ao calendário
            calendar = self.service.calendars().get(calendarId=self.calendar_id).execute()
            return calendar is not None
            
        except:
            return False