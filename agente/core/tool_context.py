"""
Tool Context Provider - Fornece contexto global para tools AGnO
"""

from typing import Dict, Any, Optional
from threading import local
from loguru import logger

# Thread-local storage para contexto atual
_context_storage = local()

class ToolContextProvider:
    """
    Provedor de contexto global para tools AGnO.
    
    Permite que tools acessem informações do contexto atual
    como phone number, lead data, etc.
    """
    
    @staticmethod
    def set_current_context(phone: str, context: Dict[str, Any]) -> None:
        """
        Define o contexto atual para as tools.
        
        Args:
            phone: Número de telefone atual
            context: Dados completos do contexto
        """
        try:
            _context_storage.phone = phone
            _context_storage.context = context
            _context_storage.active = True
            
            logger.debug(f"Contexto definido para tools: phone={phone[:4]}****")
            
        except Exception as e:
            logger.error(f"Erro ao definir contexto para tools: {e}")
    
    @staticmethod
    def get_current_phone() -> Optional[str]:
        """
        Obtém o número de telefone do contexto atual.
        
        Returns:
            str: Número de telefone ou None se não disponível
        """
        try:
            if hasattr(_context_storage, 'active') and _context_storage.active:
                return getattr(_context_storage, 'phone', None)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter telefone do contexto: {e}")
            return None
    
    @staticmethod
    def get_current_context() -> Optional[Dict[str, Any]]:
        """
        Obtém o contexto completo atual.
        
        Returns:
            Dict: Contexto completo ou None se não disponível
        """
        try:
            if hasattr(_context_storage, 'active') and _context_storage.active:
                return getattr(_context_storage, 'context', None)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto completo: {e}")
            return None
    
    @staticmethod
    def clear_context() -> None:
        """Limpa o contexto atual."""
        try:
            if hasattr(_context_storage, 'active'):
                _context_storage.active = False
                _context_storage.phone = None
                _context_storage.context = None
                
            logger.debug("Contexto limpo para tools")
            
        except Exception as e:
            logger.error(f"Erro ao limpar contexto: {e}")
    
    @staticmethod
    def is_context_active() -> bool:
        """
        Verifica se há contexto ativo.
        
        Returns:
            bool: True se há contexto ativo
        """
        try:
            return hasattr(_context_storage, 'active') and _context_storage.active
        except:
            return False

# Singleton instance
tool_context = ToolContextProvider()

# Convenience functions
def get_current_phone() -> Optional[str]:
    """Obtém telefone atual para tools."""
    return tool_context.get_current_phone()

def get_current_context() -> Optional[Dict[str, Any]]:
    """Obtém contexto atual para tools."""
    return tool_context.get_current_context()

def set_tool_context(phone: str, context: Dict[str, Any]) -> None:
    """Define contexto atual para tools."""
    return tool_context.set_current_context(phone, context)

def clear_tool_context() -> None:
    """Limpa contexto atual."""
    return tool_context.clear_context()