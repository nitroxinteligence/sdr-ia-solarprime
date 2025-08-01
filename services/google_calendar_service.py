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
from google.oauth2 import service_account
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


def create_service_account_from_env() -> bool:
    """Cria arquivo JSON de service account a partir de variáveis de ambiente"""
    try:
        # Verificar se todas as variáveis necessárias estão definidas
        required_vars = [
            'GOOGLE_SERVICE_ACCOUNT_EMAIL',
            'GOOGLE_PRIVATE_KEY',
            'GOOGLE_PROJECT_ID'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.warning(f"⚠️ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
            return False
        
        # Criar estrutura do service account
        service_account_info = {
            "type": "service_account",
            "project_id": os.getenv('GOOGLE_PROJECT_ID'),
            "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID', ''),
            "private_key": os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
            "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv('GOOGLE_CERT_URL', '')
        }
        
        # Criar diretório se não existir
        os.makedirs('credentials', exist_ok=True)
        
        # Salvar arquivo
        service_account_path = 'credentials/google_service_account.json'
        with open(service_account_path, 'w') as f:
            json.dump(service_account_info, f, indent=2)
        
        logger.info(f"✅ Arquivo de service account criado em: {service_account_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar arquivo de service account: {e}")
        return False


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
        
        # Determinar qual método de autenticação usar
        self.use_service_account = os.getenv('GOOGLE_USE_SERVICE_ACCOUNT', 'true').lower() == 'true'
        
        # Paths para credenciais
        if self.use_service_account:
            self.service_account_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_PATH', 'credentials/google_service_account.json')
        else:
            # Fallback para OAuth (mantém compatibilidade)
            self.credentials_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH', 'credentials/google_calendar_credentials.json')
            self.token_path = os.getenv('GOOGLE_CALENDAR_TOKEN_PATH', 'credentials/google_calendar_token.pickle')
        
        # ID do calendário - pode ser email do usuário ou ID específico
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        # Configurações de negócio
        self.default_duration_minutes = 60
        self.reminder_minutes = [1440, 60]  # 1 dia antes, 1 hora antes
        
        # Inicializar serviço
        self._initialize_service()
        
    def _initialize_service(self):
        """Inicializa o serviço do Google Calendar com autenticação"""
        try:
            if self.use_service_account:
                # Usar Service Account (recomendado para servidores)
                self._initialize_with_service_account()
            else:
                # Usar OAuth (para desenvolvimento local)
                self._initialize_with_oauth()
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Google Calendar service: {e}")
            self.service = None
    
    def _initialize_with_service_account(self):
        """Inicializa usando Service Account - ideal para servidores"""
        try:
            # Verificar se arquivo de service account existe
            if not os.path.exists(self.service_account_path):
                logger.info("📝 Arquivo de service account não encontrado, tentando criar a partir de variáveis de ambiente...")
                if not create_service_account_from_env():
                    logger.error("❌ Não foi possível criar arquivo de service account")
                    logger.info("💡 Configure as variáveis de ambiente:")
                    logger.info("   - GOOGLE_SERVICE_ACCOUNT_EMAIL")
                    logger.info("   - GOOGLE_PRIVATE_KEY")
                    logger.info("   - GOOGLE_PROJECT_ID")
                    return
            
            # Carregar credenciais do service account
            self.credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=self.SCOPES
            )
            
            # Se houver um email para impersonar (útil para Google Workspace)
            impersonate_email = os.getenv('GOOGLE_CALENDAR_OWNER_EMAIL')
            if impersonate_email:
                logger.info(f"👤 Impersonando usuário: {impersonate_email}")
                self.credentials = self.credentials.with_subject(impersonate_email)
            
            # Criar serviço
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.success("✅ Google Calendar service inicializado com Service Account")
            
            # Log do calendário que será usado
            logger.info(f"📅 Usando calendário: {self.calendar_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar com Service Account: {e}")
            raise
    
    def _initialize_with_oauth(self):
        """Inicializa usando OAuth - para desenvolvimento local"""
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
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    
                    # Para desenvolvimento local
                    self.credentials = flow.run_local_server(
                        port=0,
                        success_message='A autenticação foi concluída! Você pode fechar esta janela.',
                        open_browser=True
                    )
                
                # Salvar token para próximas execuções
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Criar serviço
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.success("✅ Google Calendar service inicializado com OAuth")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar com OAuth: {e}")
            raise
    
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
            
            # Criar evento com timeout de 10 segundos
            loop = asyncio.get_event_loop()
            created_event = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.service.events().insert(
                        calendarId=self.calendar_id,
                        body=event,
                        sendNotifications=True
                    ).execute()
                ),
                timeout=10.0
            )
            
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
            # Buscar evento atual com timeout de 10 segundos
            loop = asyncio.get_event_loop()
            event = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.service.events().get(
                        calendarId=self.calendar_id,
                        eventId=event_id
                    ).execute()
                ),
                timeout=10.0
            )
            
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
            
            # Atualizar evento com timeout de 10 segundos
            updated_event = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.service.events().update(
                        calendarId=self.calendar_id,
                        eventId=event_id,
                        body=event,
                        sendNotifications=True
                    ).execute()
                ),
                timeout=10.0
            )
            
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
            # Cancelar evento com timeout de 10 segundos
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.service.events().delete(
                        calendarId=self.calendar_id,
                        eventId=event_id,
                        sendNotifications=send_notifications
                    ).execute()
                ),
                timeout=10.0
            )
            
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
            
            # Buscar eventos com timeout de 10 segundos
            loop = asyncio.get_event_loop()
            events_result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.service.events().list(
                        calendarId=self.calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                ),
                timeout=10.0
            )
            
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
            # Seção 1: Informações Básicas do Cliente
            parts.append("📋 INFORMAÇÕES DO CLIENTE\n")
            
            if lead_data.get('name'):
                parts.append(f"👤 Nome: {lead_data['name']}")
            
            if lead_data.get('phone'):
                parts.append(f"📱 Telefone: {lead_data['phone']}")
            
            if lead_data.get('email'):
                parts.append(f"📧 Email: {lead_data['email']}")
            
            # Seção 2: Dados de Consumo e Interesse
            parts.append("\n💡 DADOS DE CONSUMO E INTERESSE\n")
            
            if lead_data.get('bill_value'):
                parts.append(f"💰 Valor atual da conta: R$ {lead_data['bill_value']}")
                # Calcular economia potencial
                economia = float(lead_data['bill_value']) * 0.95
                parts.append(f"💸 Economia potencial (95%): R$ {economia:.2f}/mês")
            
            if lead_data.get('consumption_kwh'):
                parts.append(f"⚡ Consumo mensal: {lead_data['consumption_kwh']} kWh")
            
            if lead_data.get('solution_interest'):
                parts.append(f"🎯 Solução de interesse: {lead_data['solution_interest']}")
            
            if lead_data.get('address'):
                parts.append(f"📍 Endereço: {lead_data['address']}")
            
            if lead_data.get('current_discount'):
                parts.append(f"💳 Desconto atual: {lead_data['current_discount']}%")
            
            # Seção 3: Status de Qualificação
            parts.append("\n🎯 STATUS DE QUALIFICAÇÃO\n")
            
            if lead_data.get('qualification_score'):
                score = lead_data['qualification_score']
                status_emoji = "🔥" if score >= 80 else "⚡" if score >= 60 else "❄️"
                parts.append(f"{status_emoji} Score de qualificação: {score}/100")
            
            if lead_data.get('current_stage'):
                parts.append(f"📊 Estágio atual: {lead_data['current_stage']}")
            
            # Critérios de qualificação
            parts.append("\n✅ CRITÉRIOS DE QUALIFICAÇÃO:")
            parts.append(f"• É decisor: {lead_data.get('is_decision_maker', 'N/A')}")
            parts.append(f"• Tem sistema solar: {lead_data.get('has_solar_system', 'N/A')}")
            
            if lead_data.get('has_solar_system') == 'Sim':
                parts.append(f"  → Quer novo sistema: {lead_data.get('wants_new_solar_system', 'N/A')}")
            
            parts.append(f"• Tem contrato vigente: {lead_data.get('has_active_contract', 'N/A')}")
            
            if lead_data.get('has_active_contract') == 'Sim':
                parts.append(f"  → Término do contrato: {lead_data.get('contract_end_date', 'N/A')}")
            
            # Seção 4: Resumo da Conversa
            if lead_data.get('conversation_summary'):
                parts.append("\n💬 RESUMO DA CONVERSA\n")
                parts.append("="*40)
                # Limitar o resumo para não ficar muito longo
                summary = lead_data['conversation_summary']
                if len(summary) > 1000:
                    summary = summary[:1000] + "\n... (resumo truncado)"
                parts.append(summary)
                parts.append("="*40)
            
            # Seção 5: Observações e Notas
            if lead_data.get('notes'):
                parts.append(f"\n📝 OBSERVAÇÕES DO AGENTE:\n{lead_data['notes']}")
            
            # Seção 6: Links e Referências
            parts.append("\n🔗 LINKS E REFERÊNCIAS\n")
            
            # Link do CRM
            if lead_data.get('crm_link') and lead_data['crm_link'] != '#':
                parts.append(f"📊 CRM: {lead_data['crm_link']}")
            
            # Adicionar data/hora de criação do evento
            parts.append(f"\n⏰ Evento criado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        
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