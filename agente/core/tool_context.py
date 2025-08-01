"""
Tool Context Provider - Fornece contexto global para tools AGnO
CORREÇÃO ASYNC: Usar contextvars em vez de threading.local para suporte async/await
"""

from typing import Dict, Any, Optional
from contextvars import ContextVar
from loguru import logger

# Context variables para contexto atual (suporte async/await)
_current_phone: ContextVar[Optional[str]] = ContextVar('current_phone', default=None)
_current_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('current_context', default=None)
_context_active: ContextVar[bool] = ContextVar('context_active', default=False)

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
            _current_phone.set(phone)
            _current_context.set(context)
            _context_active.set(True)
            
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
            if _context_active.get():
                return _current_phone.get()
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
            if _context_active.get():
                return _current_context.get()
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto completo: {e}")
            return None
    
    @staticmethod
    def clear_context() -> None:
        """Limpa o contexto atual."""
        try:
            _context_active.set(False)
            _current_phone.set(None)
            _current_context.set(None)
                
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
            return _context_active.get()
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