"""
Google OAuth 2.0 Handler - Arquitetura Modular Simples
Gerencia autenticação OAuth para Google Calendar com suporte a Google Meet e Participantes
"""

from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime, timedelta
import asyncio
import aiohttp
from urllib.parse import urlencode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.utils.logger import emoji_logger


class GoogleOAuthHandler:
    """
    Handler OAuth 2.0 para Google Calendar
    Zero complexidade, máxima funcionalidade
    """
    
    # Scopes necessários para Calendar + Meet + Participantes
    # NOTA: Google Meet é criado automaticamente com Calendar API v3
    # Não existe scope separado para Meet - ele usa o scope do Calendar
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',  # Full calendar access (inclui Meet)
        'https://www.googleapis.com/auth/calendar.events',  # Events management
    ]
    
    def __init__(self):
        """Inicializa o handler OAuth"""
        self.client_id = settings.google_oauth_client_id
        self.client_secret = settings.google_oauth_client_secret
        self.redirect_uri = settings.google_oauth_redirect_uri
        self.refresh_token = settings.google_oauth_refresh_token
        
        # Cache de credenciais
        self._credentials: Optional[Credentials] = None
        self._credentials_expire: Optional[datetime] = None
        
        emoji_logger.service_info("🔐 GoogleOAuthHandler inicializado")
    
    def get_google_auth_url(self) -> str:
        """
        Gera URL de autorização OAuth para o usuário
        
        Returns:
            URL para redirecionar o usuário para autorização
        """
        try:
            emoji_logger.service_info(f"🔐 Gerando URL OAuth com Client ID: {self.client_id[:20]}...")
            
            if not self.client_id or not self.client_secret:
                emoji_logger.service_error("❌ Client ID ou Secret não configurados!")
                raise ValueError("Google OAuth Client ID e Secret devem estar configurados no .env")
            
            # Configurar flow OAuth com endpoints v2 (OpenID Connect compliant)
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                    }
                },
                scopes=self.SCOPES
            )
            
            # IMPORTANTE: redirect_uri deve ser configurado ANTES de gerar a URL
            flow.redirect_uri = self.redirect_uri
            
            # Debug: verificar se redirect_uri está configurado
            emoji_logger.service_info(f"🔗 Redirect URI configurado: {self.redirect_uri}")
            
            # Gerar URL com parâmetros adicionais
            authorization_url, state = flow.authorization_url(
                access_type='offline',  # Para obter refresh token
                include_granted_scopes='true',  # Incremental authorization
                prompt='consent'  # Força consentimento para garantir refresh token
            )
            
            emoji_logger.service_info(f"✅ URL de autorização gerada: {authorization_url[:50]}...")
                        # FIX OAUTH URL ENCODING: Corrigir codificação + para %20 no scope
            # PROBLEMA: Python urllib codifica espaços como '+' mas Google OAuth espera '%20'
            # ANÁLISE: '+' no scope causa falha de parsing que afeta parâmetros subsequentes
            authorization_url = authorization_url.replace(
                '+', '%20'
            )
            
            emoji_logger.service_info(f"🔧 URL corrigida - substituído '+' por '%20': {authorization_url[:50]}...")
            
            return authorization_url
            
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao gerar URL de autorização: {e}")
            raise
    
    async def handle_google_callback(self, code: str) -> Dict[str, Any]:
        """
        Processa callback do Google após autorização
        
        Args:
            code: Código de autorização do Google
            
        Returns:
            Dict com informações do token obtido
        """
        try:
            # Configurar flow OAuth com endpoints v2 (OpenID Connect compliant)
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                    }
                },
                scopes=self.SCOPES
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Trocar código por tokens
            flow.fetch_token(code=code)
            
            # Obter credenciais
            credentials = flow.credentials
            
            # Salvar refresh token
            if credentials.refresh_token:
                # Salvar no arquivo .env (produção: usar vault seguro)
                await self._save_refresh_token(credentials.refresh_token)
                
                emoji_logger.service_info("✅ Refresh token salvo com sucesso!")
                
                return {
                    "success": True,
                    "message": "Autorização concluída com sucesso",
                    "access_token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
                    "scopes": credentials.scopes
                }
            else:
                emoji_logger.service_warning("⚠️ Refresh token não obtido - revogue acesso e tente novamente")
                return {
                    "success": False,
                    "message": "Refresh token não obtido. Revogue acesso em https://myaccount.google.com/permissions e tente novamente",
                    "access_token": credentials.token
                }
                
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro no callback OAuth: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar autorização: {str(e)}"
            }
    
    async def _save_refresh_token(self, refresh_token: str):
        """
        Salva refresh token no arquivo .env
        NOTA: Em produção, usar um vault seguro como HashiCorp Vault ou AWS Secrets Manager
        
        Args:
            refresh_token: Token a ser salvo
        """
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            
            # Ler arquivo .env atual
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Atualizar ou adicionar GOOGLE_OAUTH_REFRESH_TOKEN
            token_found = False
            for i, line in enumerate(lines):
                if line.startswith('GOOGLE_OAUTH_REFRESH_TOKEN='):
                    lines[i] = f'GOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}\n'
                    token_found = True
                    break
            
            if not token_found:
                lines.append(f'\n# OAuth Refresh Token (gerado automaticamente)\n')
                lines.append(f'GOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}\n')
            
            # Salvar arquivo atualizado
            with open(env_path, 'w') as f:
                f.writelines(lines)
            
            # Atualizar configuração em runtime
            settings.google_oauth_refresh_token = refresh_token
            self.refresh_token = refresh_token
            
            emoji_logger.service_info(f"💾 Refresh token salvo em {env_path}")
            
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao salvar refresh token: {e}")
            raise
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Obtém credenciais OAuth válidas
        Usa refresh token para obter novo access token quando necessário
        
        Returns:
            Credenciais OAuth válidas ou None se não disponível
        """
        try:
            # Verificar cache
            if self._credentials and self._credentials.valid:
                return self._credentials
            
            # Verificar se temos refresh token
            if not self.refresh_token:
                emoji_logger.service_warning("⚠️ Refresh token não disponível - autorização necessária")
                return None
            
            # Criar credenciais com refresh token
            credentials = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES
            )
            
            # Refresh se necessário
            if not credentials.valid:
                request = Request()
                credentials.refresh(request)
                emoji_logger.service_info("🔄 Access token renovado com sucesso")
            
            # Atualizar cache
            self._credentials = credentials
            
            return credentials
            
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao obter credenciais: {e}")
            return None
    
    def build_calendar_service(self):
        """
        Constrói serviço do Google Calendar com credenciais OAuth
        
        Returns:
            Serviço do Google Calendar ou None se falhar
        """
        try:
            credentials = self.get_credentials()
            
            if not credentials:
                emoji_logger.service_error("❌ Credenciais não disponíveis para construir serviço")
                return None
            
            # Construir serviço
            service = build('calendar', 'v3', credentials=credentials)
            
            emoji_logger.service_info("✅ Serviço Google Calendar construído com OAuth")
            return service
            
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao construir serviço: {e}")
            return None
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com Google Calendar API
        
        Returns:
            Dict com status da conexão e informações do usuário
        """
        try:
            service = self.build_calendar_service()
            
            if not service:
                return {
                    "success": False,
                    "message": "Serviço não disponível - autorização necessária"
                }
            
            # Testar listando calendários
            calendar_list = service.calendarList().list().execute()
            primary_calendar = next(
                (cal for cal in calendar_list.get('items', []) if cal.get('primary')),
                None
            )
            
            if primary_calendar:
                user_email = primary_calendar.get('summary', 'Unknown')
                calendar_id = primary_calendar.get('id')
                
                emoji_logger.service_info(f"✅ Conectado como: {user_email}")
                
                return {
                    "success": True,
                    "message": "Conexão estabelecida com sucesso",
                    "user_email": user_email,
                    "calendar_id": calendar_id,
                    "calendars": len(calendar_list.get('items', [])),
                    "can_create_meets": True,  # OAuth sempre pode criar Meets
                    "can_invite_attendees": True  # OAuth sempre pode convidar
                }
            else:
                return {
                    "success": False,
                    "message": "Nenhum calendário encontrado"
                }
                
        except HttpError as e:
            emoji_logger.service_error(f"❌ Erro HTTP ao testar conexão: {e}")
            return {
                "success": False,
                "message": f"Erro de API: {e.reason}",
                "status_code": e.resp.status
            }
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao testar conexão: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
    
    def create_event_with_meet(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str] = None,
        description: str = None,
        location: str = None
    ) -> Dict[str, Any]:
        """
        Cria evento com Google Meet e participantes
        
        Args:
            title: Título do evento
            start_time: Horário de início
            end_time: Horário de fim
            attendees: Lista de emails dos participantes
            description: Descrição do evento
            location: Localização (opcional)
            
        Returns:
            Dict com informações do evento criado
        """
        try:
            service = self.build_calendar_service()
            
            if not service:
                return {
                    "success": False,
                    "message": "Serviço não disponível - autorização necessária"
                }
            
            # Preparar evento
            event = {
                'summary': title,
                'description': description or '',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': settings.timezone or 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': settings.timezone or 'America/Sao_Paulo',
                },
                # Google Meet - com OAuth funciona perfeitamente!
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'meet-{datetime.now().timestamp()}',
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
                # Participantes - com OAuth funciona perfeitamente!
                'attendees': [{'email': email} for email in (attendees or [])],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 dia antes
                        {'method': 'popup', 'minutes': 30},  # 30 minutos antes
                    ],
                },
            }
            
            if location:
                event['location'] = location
            
            # Criar evento com conferência
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,  # Necessário para criar Google Meet
                sendUpdates='all'  # Enviar convites para todos os participantes
            ).execute()
            
            # Extrair informações importantes
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            meet_link = None
            
            # Extrair link do Google Meet
            if 'conferenceData' in created_event:
                entry_points = created_event['conferenceData'].get('entryPoints', [])
                for entry in entry_points:
                    if entry.get('entryPointType') == 'video':
                        meet_link = entry.get('uri')
                        break
            
            emoji_logger.service_info(
                f"✅ Evento criado com Google Meet!\n"
                f"   📅 ID: {event_id}\n"
                f"   🔗 Calendar: {event_link}\n"
                f"   📹 Meet: {meet_link}\n"
                f"   👥 Participantes: {len(attendees or [])}"
            )
            
            return {
                "success": True,
                "event_id": event_id,
                "event_link": event_link,
                "meet_link": meet_link,
                "title": title,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "attendees": attendees or [],
                "message": "Evento criado com sucesso com Google Meet e participantes!"
            }
            
        except HttpError as e:
            emoji_logger.service_error(f"❌ Erro HTTP ao criar evento: {e}")
            return {
                "success": False,
                "message": f"Erro de API: {e.reason}",
                "status_code": e.resp.status
            }
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao criar evento: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }


# Singleton instance
_oauth_handler: Optional[GoogleOAuthHandler] = None


def get_oauth_handler() -> GoogleOAuthHandler:
    """
    Obtém instância singleton do OAuth handler
    
    Returns:
        Instância do GoogleOAuthHandler
    """
    global _oauth_handler
    if _oauth_handler is None:
        _oauth_handler = GoogleOAuthHandler()
    return _oauth_handler