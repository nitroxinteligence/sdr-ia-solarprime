
"""
Tool Wrapper Solution para Agentes com @tool decorator
Este módulo fornece uma solução limpa para usar o decorator @tool com métodos de classe
"""

from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from agno.tools import tool
from loguru import logger


def create_tool_from_method(method: Callable, instance: Any) -> Callable:
    """
    Cria uma função tool a partir de um método de instância
    
    Args:
        method: O método da classe
        instance: A instância da classe
        
    Returns:
        Função decorada com @tool que pode ser usada pelo agno
    """
    # Obter a assinatura do método sem 'self'
    import inspect
    sig = inspect.signature(method)
    params = list(sig.parameters.values())[1:]  # Remover 'self'
    
    # Criar nova assinatura sem 'self'
    new_sig = sig.replace(parameters=params)
    
    # Criar wrapper function
    @wraps(method)
    async def wrapper(*args, **kwargs):
        """Wrapper que chama o método original com a instância"""
        return await method(instance, *args, **kwargs)
    
    # Aplicar a nova assinatura
    wrapper.__signature__ = new_sig
    
    # Aplicar o decorator @tool
    return tool(wrapper)


class ToolRegistry:
    """
    Registry para gerenciar tools de agentes
    """
    
    def __init__(self):
        self.tools = []
        
    def register_method_as_tool(self, method: Callable, instance: Any, name: Optional[str] = None):
        """
        Registra um método como tool
        
        Args:
            method: Método a ser registrado
            instance: Instância da classe
            name: Nome opcional para o tool
        """
        tool_func = create_tool_from_method(method, instance)
        if name:
            tool_func.__name__ = name
        self.tools.append(tool_func)
        return tool_func
        
    def get_tools(self) -> List[Callable]:
        """Retorna todos os tools registrados"""
        return self.tools


# Exemplo de uso com CRMAgent
class CRMAgentFixed:
    """
    Versão corrigida do CRMAgent com tools funcionais
    """
    
    def __init__(self, model, storage):
        self.model = model
        self.storage = storage
        
        # Registry para tools
        self.tool_registry = ToolRegistry()
        
        # Registrar métodos como tools
        self._register_tools()
        
    def _register_tools(self):
        """Registra todos os métodos como tools"""
        # Registrar cada método que precisa ser um tool
        methods_to_register = [
            'create_or_update_lead',
            'create_contact',
            'create_deal',
            'update_deal_stage',
            'add_note',
            'add_task',
            'search_entity',
            'sync_lead_to_crm',
            'get_deal_history'
        ]
        
        for method_name in methods_to_register:
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                self.tool_registry.register_method_as_tool(method, self, method_name)
                
    def get_tools(self) -> List[Callable]:
        """Retorna os tools para o agente"""
        return self.tool_registry.get_tools()
        
    # Métodos originais sem @tool decorator
    async def create_or_update_lead(self, lead_data: Dict[str, Any], update_if_exists: bool = True) -> Dict[str, Any]:
        """
        Cria ou atualiza lead no Kommo
        
        Args:
            lead_data: Dados do lead
            update_if_exists: Se deve atualizar caso já exista
            
        Returns:
            Resultado da operação
        """
        # Implementação original aqui
        pass
    
    # ... outros métodos ...


# Exemplo de uso com QualificationAgent
class QualificationAgentFixed:
    """
    Versão corrigida do QualificationAgent com tools funcionais
    """
    
    def __init__(self, model, storage):
        self.model = model
        self.storage = storage
        
        # Registry para tools
        self.tool_registry = ToolRegistry()
        
        # Registrar métodos como tools
        self._register_tools()
        
    def _register_tools(self):
        """Registra todos os métodos como tools"""
        methods_to_register = [
            'calculate_qualification_score',
            'check_qualification_criteria',
            'classify_lead_temperature',
            'determine_next_action',
            'save_qualification_data'
        ]
        
        for method_name in methods_to_register:
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                self.tool_registry.register_method_as_tool(method, self, method_name)
                
    def get_tools(self) -> List[Callable]:
        """Retorna os tools para o agente"""
        return self.tool_registry.get_tools()
        
    # Métodos originais sem @tool decorator
    async def calculate_qualification_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula score de qualificação do lead
        
        Args:
            lead_data: Dados do lead
            
        Returns:
            Score e detalhes
        """
        # Implementação original aqui
        pass
    
    # ... outros métodos ...
