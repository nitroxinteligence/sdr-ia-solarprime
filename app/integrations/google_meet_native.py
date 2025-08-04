"""
Google Meet Native Integration
Implementação nativa usando Google Meet REST API v2
100% Google - Sem soluções alternativas
"""

import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.apps import meet_v2
from google.apps.meet_v2 import SpacesServiceClient, Space, SpaceConfig
from google.api_core import exceptions as api_exceptions
from app.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class GoogleMeetNativeClient:
    """
    Cliente nativo para Google Meet REST API v2
    Cria e gerencia meeting spaces usando Service Account
    
    Features:
    - Criação de meeting spaces persistentes
    - Links profissionais meet.google.com/xxx-xxxx-xxx
    - Integração completa com Google Calendar
    - 100% nativo Google - sem alternativas
    """
    
    # Scopes necessários para Meet API
    # NOTA: Meet API v2 usa scopes diferentes do Calendar
    SCOPES = [
        'https://www.googleapis.com/auth/meetings.space.created',
        'https://www.googleapis.com/auth/meetings.space.readonly',
        'https://www.googleapis.com/auth/calendar',  # Para integração com Calendar
        'https://www.googleapis.com/auth/calendar.events'  # Para criar eventos
    ]
    
    def __init__(self):
        """Inicializa o cliente do Google Meet"""
        self.client = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Autentica com Google Meet usando Service Account
        Usa as mesmas credenciais do Calendar
        """
        try:
            # Verificar se Meet está habilitado
            if hasattr(settings, 'disable_google_meet') and settings.disable_google_meet:
                logger.warning("Google Meet está desabilitado nas configurações")
                return
            
            # Caminho para o arquivo de credenciais Service Account
            service_account_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'credentials',
                'google_service_account.json'
            )
            
            # Verificar se arquivo existe
            if not os.path.exists(service_account_file):
                # Tentar criar do ambiente se não existir
                if settings.google_private_key and settings.google_service_account_email:
                    credentials_info = {
                        "type": "service_account",
                        "project_id": settings.google_project_id,
                        "private_key_id": settings.google_private_key_id,
                        "private_key": settings.google_private_key,
                        "client_email": settings.google_service_account_email,
                        "client_id": settings.google_client_id,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.google_service_account_email}"
                    }
                    
                    # Criar credenciais do dicionário
                    self.credentials = service_account.Credentials.from_service_account_info(
                        credentials_info,
                        scopes=self.SCOPES
                    )
                else:
                    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {service_account_file}")
            else:
                # Criar credenciais do arquivo
                self.credentials = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=self.SCOPES
                )
            
            # Criar cliente do Meet API v2
            self.client = SpacesServiceClient(credentials=self.credentials)
            
            logger.info("✅ Google Meet API v2 autenticado com sucesso")
            logger.info(f"📧 Service Account: {self.credentials.service_account_email}")
            
        except Exception as e:
            logger.error(f"❌ Erro na autenticação do Google Meet: {e}")
            self.client = None
    
    async def create_meeting_space(
        self,
        title: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        access_type: str = "OPEN",
        entry_point_access: str = "ALL"
    ) -> Optional[Dict[str, Any]]:
        """
        Cria um meeting space no Google Meet
        
        Args:
            title: Título da reunião (opcional)
            start_time: Hora de início (opcional, para expiração automática)
            end_time: Hora de término (opcional, para expiração automática)
            access_type: Tipo de acesso (OPEN, TRUSTED, RESTRICTED)
            entry_point_access: Quem pode entrar (ALL, CREATOR_APP_ONLY)
            
        Returns:
            Dict com informações do meeting space ou None se falhar
        """
        if not self.client:
            logger.error("Cliente do Google Meet não está disponível")
            return None
        
        try:
            # Preparar configuração do space
            config = SpaceConfig()
            
            # Configurar tipo de acesso
            if access_type == "OPEN":
                config.access_type = SpaceConfig.AccessType.OPEN
            elif access_type == "TRUSTED":
                config.access_type = SpaceConfig.AccessType.TRUSTED
            elif access_type == "RESTRICTED":
                config.access_type = SpaceConfig.AccessType.RESTRICTED
            else:
                config.access_type = SpaceConfig.AccessType.OPEN
            
            # Configurar quem pode entrar
            if entry_point_access == "ALL":
                config.entry_point_access = SpaceConfig.EntryPointAccess.ALL
            elif entry_point_access == "CREATOR_APP_ONLY":
                config.entry_point_access = SpaceConfig.EntryPointAccess.CREATOR_APP_ONLY
            else:
                config.entry_point_access = SpaceConfig.EntryPointAccess.ALL
            
            # Criar o space
            space = Space()
            space.config = config
            
            # Se tiver horários, configurar expiração
            # NOTA: Meet API v2 não suporta expiração automática diretamente
            # mas podemos armazenar para gerenciamento posterior
            
            # Criar o meeting space
            created_space = self.client.create_space(space=space)
            
            if created_space:
                # Extrair informações importantes
                result = {
                    'success': True,
                    'space_name': created_space.name,
                    'meeting_uri': created_space.meeting_uri,
                    'meeting_code': created_space.meeting_code,
                    'active_conference': created_space.active_conference,
                    'config': {
                        'access_type': access_type,
                        'entry_point_access': entry_point_access
                    }
                }
                
                logger.info(f"✅ Meeting Space criado: {created_space.meeting_code}")
                logger.info(f"🔗 Meet Link: {created_space.meeting_uri}")
                
                return result
            
            return None
            
        except api_exceptions.PermissionDenied as e:
            logger.error(f"❌ Permissão negada ao criar Meeting Space: {e}")
            logger.info("💡 Verifique se a Meet API está habilitada no Google Cloud Console")
            logger.info("💡 Verifique as permissões do Service Account")
            return None
            
        except api_exceptions.InvalidArgument as e:
            logger.error(f"❌ Argumentos inválidos ao criar Meeting Space: {e}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar Meeting Space: {e}")
            logger.info("💡 Pode ser necessário habilitar a Google Meet API no Console")
            return None
    
    async def get_meeting_space(self, space_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de um meeting space existente
        
        Args:
            space_name: Nome do space (formato: spaces/xxx)
            
        Returns:
            Dict com informações do space ou None se não encontrado
        """
        if not self.client:
            logger.error("Cliente do Google Meet não está disponível")
            return None
        
        try:
            # Buscar o space
            space = self.client.get_space(name=space_name)
            
            if space:
                return {
                    'space_name': space.name,
                    'meeting_uri': space.meeting_uri,
                    'meeting_code': space.meeting_code,
                    'active_conference': space.active_conference,
                    'config': {
                        'access_type': str(space.config.access_type),
                        'entry_point_access': str(space.config.entry_point_access)
                    }
                }
            
            return None
            
        except api_exceptions.NotFound:
            logger.warning(f"Meeting Space não encontrado: {space_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar Meeting Space: {e}")
            return None
    
    async def end_meeting_space(self, space_name: str) -> bool:
        """
        Encerra um meeting space ativo
        
        Args:
            space_name: Nome do space (formato: spaces/xxx)
            
        Returns:
            True se encerrado com sucesso, False caso contrário
        """
        if not self.client:
            logger.error("Cliente do Google Meet não está disponível")
            return False
        
        try:
            # Encerrar conference ativa no space
            self.client.end_active_conference(name=f"{space_name}")
            
            logger.info(f"✅ Meeting Space encerrado: {space_name}")
            return True
            
        except api_exceptions.NotFound:
            logger.warning(f"Meeting Space não encontrado ou sem conferência ativa: {space_name}")
            return True  # Considera sucesso se não há conferência ativa
            
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar Meeting Space: {e}")
            return False
    
    async def create_meeting_with_calendar_integration(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Cria um meeting space e prepara dados para integração com Calendar
        
        Args:
            title: Título da reunião
            start_time: Hora de início
            end_time: Hora de término
            description: Descrição da reunião
            
        Returns:
            Dict com informações do meeting e dados para Calendar
        """
        # Criar o meeting space
        meeting_result = await self.create_meeting_space(
            title=title,
            start_time=start_time,
            end_time=end_time,
            access_type="OPEN",
            entry_point_access="ALL"
        )
        
        if not meeting_result or not meeting_result.get('success'):
            logger.error("Falha ao criar Meeting Space")
            return None
        
        # Preparar informações para o Calendar
        meet_link = meeting_result.get('meeting_uri')
        meet_code = meeting_result.get('meeting_code')
        
        # Formatar descrição com informações do Meet
        enhanced_description = f"""{description}

📹 Google Meet Nativo
🔗 Link da Reunião: {meet_link}
📝 Código da Reunião: {meet_code}

Como participar:
1. Clique no link acima no horário marcado
2. Ou acesse meet.google.com e digite o código: {meet_code}
3. Permita acesso à câmera e microfone quando solicitado

✅ 100% Google Meet Nativo - Solução Oficial"""
        
        return {
            'success': True,
            'meeting_uri': meet_link,
            'meeting_code': meet_code,
            'space_name': meeting_result.get('space_name'),
            'enhanced_description': enhanced_description,
            'calendar_integration': {
                'location': f"Google Meet: {meet_code}",
                'conference_notes': f"Meeting Code: {meet_code}",
                'meeting_link': meet_link
            }
        }
    
    def is_available(self) -> bool:
        """Verifica se o cliente está disponível e autenticado"""
        return self.client is not None

# Singleton instance
google_meet_native_client = GoogleMeetNativeClient()