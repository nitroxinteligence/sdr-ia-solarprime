"""
Google OAuth Handler com fallback seguro
ZERO COMPLEXIDADE - OAuth opcional
"""

from typing import Optional, Dict, Any
from app.utils.logger import emoji_logger
from app.config import settings
import os

class GoogleOAuthSafe:
    """Handler OAuth que funciona mesmo sem credenciais"""
    
    def __init__(self):
        """Inicializa OAuth de forma segura"""
        self.service = None
        self.enabled = False
        
        # Verifica se OAuth está configurado
        if self._check_oauth_config():
            try:
                from app.integrations.google_oauth_handler import GoogleOAuthHandler
                self.oauth_handler = GoogleOAuthHandler()
                self.service = self.oauth_handler.service
                self.enabled = bool(self.service)
                
                if self.enabled:
                    emoji_logger.info("Service", "✅ OAuth configurado com sucesso")
                else:
                    emoji_logger.warning("Service", "⚠️ OAuth disponível mas não autorizado")
            except Exception as e:
                emoji_logger.warning("Service", f"⚠️ OAuth opcional não configurado: {str(e)}")
                self.enabled = False
        else:
            emoji_logger.info("Service", "ℹ️ OAuth desabilitado - funcionando sem Google Calendar")
    
    def _check_oauth_config(self) -> bool:
        """Verifica se configuração OAuth existe"""
        # Verifica se credentials existem
        credentials_path = os.path.join("credentials", "client_secret.json")
        if not os.path.exists(credentials_path):
            return False
            
        # Verifica se calendário está habilitado
        if not settings.ENABLE_CALENDAR_AGENT:
            return False
            
        return True
    
    def is_enabled(self) -> bool:
        """Retorna se OAuth está disponível"""
        return self.enabled
    
    def get_service(self):
        """Retorna serviço OAuth ou None"""
        return self.service
    
    async def create_event(self, event_data: Dict[str, Any]) -> Optional[Dict]:
        """Cria evento se OAuth estiver disponível"""
        if not self.enabled or not self.service:
            emoji_logger.warning("Service", "⚠️ OAuth não disponível - evento não criado")
            return None
            
        try:
            # Delega para o handler real
            return await self.oauth_handler.create_calendar_event(event_data)
        except Exception as e:
            emoji_logger.error("Service", f"❌ Erro ao criar evento: {str(e)}")
            return None

# Instância global segura
_oauth_safe_instance = None

def get_oauth_safe() -> GoogleOAuthSafe:
    """Retorna instância singleton do OAuth seguro"""
    global _oauth_safe_instance
    if _oauth_safe_instance is None:
        _oauth_safe_instance = GoogleOAuthSafe()
    return _oauth_safe_instance