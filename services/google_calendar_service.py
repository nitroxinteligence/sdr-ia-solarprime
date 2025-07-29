"""
Google Calendar Service
=======================
Serviço para integração com Google Calendar API
Gerencia criação, atualização e cancelamento de reuniões
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

# Google Calendar API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# AGnO Framework
from agno.tools.googlecalendar import GoogleCalendarTools

# Configurações locais
from config.config import Config


class GoogleCalendarService:
    """Serviço para gerenciar eventos no Google Calendar"""
    
    # Escopos necessários para gerenciar eventos
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, config: Config):
        self.config = config
        self.service = None
        self.credentials = None
        self.calendar_id = 'primary'  # Usar calendário principal
        
        # Paths para credenciais
        self.credentials_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH', 'credentials/google_calendar_credentials.json')
        self.token_path = os.getenv('GOOGLE_CALENDAR_TOKEN_PATH', 'credentials/google_calendar_token.pickle')
        
        # Configurações de negócio
        self.default_duration_minutes = 60
        self.reminder_minutes = [1440, 60]  # 1 dia antes, 1 hora antes
        
        # Inicializar serviço
        self._initialize_service()
        
    def _initialize_service(self):
        """Inicializa o serviço do Google Calendar com autenticação"""
        try:
            # Verificar se existe token salvo
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Se não há credenciais válidas
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # Renovar token
                    self.credentials.refresh(Request())
                else:
                    # Fazer novo fluxo de autenticação
                    if not os.path.exists(self.credentials_path):
                        logger.error(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
                        logger.info("Por favor, baixe as credenciais do Google Cloud Console")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    # Para aplicativo desktop, usar porta 0 (dinâmica) é mais seguro
                    self.credentials = flow.run_local_server(
                        port=0,  # Porta dinâmica
                        success_message='A autenticação foi concluída! Você pode fechar esta janela.',
                        open_browser=True
                    )
                
                # Salvar token para próximas execuções
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Criar serviço
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.success("✅ Google Calendar service inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Google Calendar service: {e}")
            self.service = None
    
    async def create_event(
        self,
        title: str,
        start_datetime: datetime,
        end_datetime: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        lead_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Cria um evento no Google Calendar
        
        Args:
            title: Título do evento
            start_datetime: Data/hora de início
            end_datetime: Data/hora de fim (opcional, padrão 1 hora)
            description: Descrição do evento
            location: Local do evento
            attendees: Lista de emails dos participantes
            lead_data: Dados do lead para enriquecer o evento
            
        Returns:
            Dict com dados do evento criado ou None se falhar
        """
        if not self.service:
            logger.error("Serviço do Google Calendar não inicializado")
            return None
        
        try:
            # Calcular fim se não fornecido
            if not end_datetime:
                end_datetime = start_datetime + timedelta(minutes=self.default_duration_minutes)
            
            # Preparar evento
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': m} for m in self.reminder_minutes
                    ],
                },
            }
            
            # Adicionar descrição enriquecida
            if description or lead_data:
                event['description'] = self._generate_event_description(description, lead_data)
            
            # Adicionar localização
            if location:
                event['location'] = location
            
            # Adicionar participantes
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
                event['sendUpdates'] = 'all'  # Enviar convites
            
            # Adicionar propriedades privadas (metadata)
            if lead_data:
                event['extendedProperties'] = {
                    'private': {
                        'lead_id': str(lead_data.get('id', '')),
                        'lead_phone': lead_data.get('phone', ''),
                        'lead_name': lead_data.get('name', ''),
                        'solution_type': lead_data.get('solution_interest', ''),
                        'bill_value': str(lead_data.get('bill_value', 0)),
                        'source': 'sdr_agent'
                    }
                }
            
            # Criar evento
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendNotifications=True
            ).execute()
            
            logger.success(f"✅ Evento criado: {created_event.get('htmlLink')}")
            
            return {
                'id': created_event['id'],
                'link': created_event.get('htmlLink'),
                'start': created_event['start']['dateTime'],
                'end': created_event['end']['dateTime'],
                'status': 'confirmed'
            }
            
        except HttpError as e:
            logger.error(f"❌ Erro HTTP ao criar evento: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao criar evento: {e}")
            return None
    
    async def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Atualiza um evento existente
        
        Args:
            event_id: ID do evento
            updates: Dicionário com campos a atualizar
            
        Returns:
            Dict com dados do evento atualizado ou None se falhar
        """
        if not self.service:
            logger.error("Serviço do Google Calendar não inicializado")
            return None
        
        try:
            # Buscar evento atual
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Aplicar atualizações
            for key, value in updates.items():
                if key == 'start_datetime':
                    event['start'] = {
                        'dateTime': value.isoformat(),
                        'timeZone': 'America/Sao_Paulo'
                    }
                elif key == 'end_datetime':
                    event['end'] = {
                        'dateTime': value.isoformat(),
                        'timeZone': 'America/Sao_Paulo'
                    }
                elif key in ['summary', 'description', 'location']:
                    event[key] = value
                elif key == 'attendees':
                    event['attendees'] = [{'email': email} for email in value]
            
            # Atualizar evento
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
                sendNotifications=True
            ).execute()
            
            logger.success(f"✅ Evento atualizado: {event_id}")
            
            return {
                'id': updated_event['id'],
                'link': updated_event.get('htmlLink'),
                'start': updated_event['start']['dateTime'],
                'end': updated_event['end']['dateTime'],
                'status': updated_event['status']
            }
            
        except HttpError as e:
            logger.error(f"❌ Erro HTTP ao atualizar evento: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar evento: {e}")
            return None
    
    async def cancel_event(
        self,
        event_id: str,
        send_notifications: bool = True
    ) -> bool:
        """
        Cancela um evento
        
        Args:
            event_id: ID do evento
            send_notifications: Se deve enviar notificações de cancelamento
            
        Returns:
            True se cancelou com sucesso
        """
        if not self.service:
            logger.error("Serviço do Google Calendar não inicializado")
            return False
        
        try:
            # Cancelar evento
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendNotifications=send_notifications
            ).execute()
            
            logger.success(f"✅ Evento cancelado: {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Evento não encontrado: {event_id}")
            else:
                logger.error(f"❌ Erro HTTP ao cancelar evento: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao cancelar evento: {e}")
            return False
    
    async def list_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Lista eventos do calendário
        
        Args:
            start_date: Data inicial (padrão: agora)
            end_date: Data final (padrão: 7 dias)
            max_results: Número máximo de resultados
            
        Returns:
            Lista de eventos
        """
        if not self.service:
            logger.error("Serviço do Google Calendar não inicializado")
            return []
        
        try:
            # Definir período padrão
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=7)
            
            # Buscar eventos
            # Formatar datas corretamente para a API
            if start_date.tzinfo:
                time_min = start_date.isoformat()
            else:
                time_min = start_date.isoformat() + 'Z'
                
            if end_date.tzinfo:
                time_max = end_date.isoformat()
            else:
                time_max = end_date.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Formatar resposta
            formatted_events = []
            for event in events:
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'Sem título'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'link': event.get('htmlLink'),
                    'attendees': [a.get('email') for a in event.get('attendees', [])],
                    'location': event.get('location'),
                    'status': event.get('status')
                })
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar eventos: {e}")
            return []
    
    async def check_availability(
        self,
        date: datetime,
        duration_minutes: int = 60,
        work_hours: Tuple[int, int] = (9, 18)
    ) -> List[Dict[str, Any]]:
        """
        Verifica disponibilidade e retorna horários livres
        
        Args:
            date: Data para verificar
            duration_minutes: Duração da reunião em minutos
            work_hours: Horário de trabalho (início, fim)
            
        Returns:
            Lista de horários disponíveis
        """
        if not self.service:
            return []
        
        try:
            # Definir início e fim do dia com timezone
            import pytz
            tz = pytz.timezone('America/Sao_Paulo')
            start_datetime = tz.localize(datetime.combine(date.date(), datetime.min.time().replace(hour=work_hours[0])))
            end_datetime = tz.localize(datetime.combine(date.date(), datetime.min.time().replace(hour=work_hours[1])))
            
            # Buscar eventos do dia
            busy_times = await self.list_events(start_datetime, end_datetime)
            
            # Encontrar slots livres
            available_slots = []
            current_time = start_datetime
            
            while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
                # Verificar se o horário está livre
                is_available = True
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                for event in busy_times:
                    event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                    
                    # Verificar sobreposição
                    if not (slot_end <= event_start or current_time >= event_end):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        'start': current_time.strftime('%H:%M'),
                        'end': slot_end.strftime('%H:%M'),
                        'datetime': current_time.isoformat()
                    })
                
                # Avançar 30 minutos
                current_time += timedelta(minutes=30)
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade: {e}")
            return []
    
    def _generate_event_description(
        self,
        custom_description: Optional[str],
        lead_data: Optional[Dict[str, Any]]
    ) -> str:
        """Gera descrição detalhada do evento com dados do lead"""
        parts = []
        
        if custom_description:
            parts.append(custom_description)
            parts.append("\n" + "="*50 + "\n")
        
        if lead_data:
            parts.append("📋 INFORMAÇÕES DO CLIENTE\n")
            
            if lead_data.get('name'):
                parts.append(f"👤 Nome: {lead_data['name']}")
            
            if lead_data.get('phone'):
                parts.append(f"📱 Telefone: {lead_data['phone']}")
            
            if lead_data.get('email'):
                parts.append(f"📧 Email: {lead_data['email']}")
            
            if lead_data.get('bill_value'):
                parts.append(f"💰 Valor atual da conta: R$ {lead_data['bill_value']}")
            
            if lead_data.get('consumption_kwh'):
                parts.append(f"⚡ Consumo mensal: {lead_data['consumption_kwh']} kWh")
            
            if lead_data.get('solution_interest'):
                parts.append(f"🎯 Solução de interesse: {lead_data['solution_interest']}")
            
            if lead_data.get('address'):
                parts.append(f"📍 Endereço: {lead_data['address']}")
            
            if lead_data.get('current_discount'):
                parts.append(f"💳 Desconto atual: {lead_data['current_discount']}%")
            
            # Adicionar link do CRM se disponível
            if lead_data.get('crm_link'):
                parts.append(f"\n🔗 Link no CRM: {lead_data['crm_link']}")
            
            # Adicionar observações
            if lead_data.get('notes'):
                parts.append(f"\n📝 Observações:\n{lead_data['notes']}")
        
        return "\n".join(parts)


# Instância global
google_calendar_service = None

def get_google_calendar_service() -> GoogleCalendarService:
    """Retorna instância do serviço Google Calendar"""
    global google_calendar_service
    if google_calendar_service is None:
        from config.config import Config
        google_calendar_service = GoogleCalendarService(Config())
    return google_calendar_service