#!/usr/bin/env python3
"""
fix_agent_tools_properly.py - Solução definitiva para @tool decorator em agentes

O problema: O decorator @tool da biblioteca agno não funciona bem com métodos de classe
que têm 'self' como primeiro parâmetro.

A solução: Criar funções wrapper que capturam a instância via closure e aplicar @tool nelas.
"""

import os
import sys
from pathlib import Path
import re
from typing import List, Tuple
import ast
import textwrap

def create_tool_wrapper_solution():
    """
    Cria um arquivo com a solução adequada para usar @tool com métodos de classe
    """
    
    solution_code = '''
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
'''
    
    # Salvar a solução
    solution_path = Path("app/teams/agents/tool_wrapper.py")
    solution_path.write_text(solution_code)
    print(f"✅ Criado arquivo de solução: {solution_path}")
    
    return solution_path


def patch_crm_agent():
    """
    Aplica patch no CRMAgent para usar a solução de wrapper
    """
    crm_path = Path("app/teams/agents/crm.py")
    
    # Ler o arquivo
    content = crm_path.read_text()
    
    # Remover todos os @tool decorators dos métodos
    content = re.sub(r'^\s*@tool\s*\n', '', content, flags=re.MULTILINE)
    
    # Adicionar import do tool_wrapper no início
    import_line = "from app.teams.agents.tool_wrapper import ToolRegistry, create_tool_from_method\n"
    
    # Encontrar onde adicionar o import
    import_section_end = content.find('\n\nclass')
    if import_section_end > 0:
        content = content[:import_section_end] + '\n' + import_line + content[import_section_end:]
    
    # Modificar o __init__ para usar ToolRegistry
    init_pattern = r'(def __init__\(self.*?\):.*?)(self\.tools = \[.*?\])'
    
    def replace_init(match):
        init_def = match.group(1)
        
        new_init = """
        # Tool Registry para gerenciar tools
        self.tool_registry = ToolRegistry()
        
        # Registrar métodos como tools após inicialização completa
        self._tools_registered = False"""
        
        return init_def + new_init
    
    content = re.sub(init_pattern, replace_init, content, flags=re.DOTALL)
    
    # Adicionar método para registrar tools
    register_method = '''
    def _register_tools(self):
        """Registra métodos como tools usando ToolRegistry"""
        if self._tools_registered:
            return
            
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
                
        self._tools_registered = True
        self.tools = self.tool_registry.get_tools()
        
        # Atualizar tools do agente
        if hasattr(self, 'agent'):
            self.agent.tools = self.tools
    '''
    
    # Adicionar o método após o __init__
    init_end = content.find('    async def initialize(self):')
    if init_end > 0:
        content = content[:init_end] + register_method + '\n' + content[init_end:]
    
    # Modificar o método initialize para chamar _register_tools
    initialize_pattern = r'(async def initialize\(self\):.*?self\._initialized = True)'
    
    def add_register_call(match):
        original = match.group(0)
        return original + '\n            self._register_tools()'
    
    content = re.sub(initialize_pattern, add_register_call, content, flags=re.DOTALL)
    
    # Salvar arquivo corrigido
    crm_path.write_text(content)
    print(f"✅ CRMAgent corrigido com tool wrapper solution")
    
    return crm_path


def patch_qualification_agent():
    """
    Aplica patch no QualificationAgent para usar a solução de wrapper
    """
    qual_path = Path("app/teams/agents/qualification.py")
    
    # Ler o arquivo
    content = qual_path.read_text()
    
    # Remover todos os @tool decorators dos métodos
    content = re.sub(r'^\s*@tool\s*\n', '', content, flags=re.MULTILINE)
    
    # Adicionar import do tool_wrapper no início
    import_line = "from app.teams.agents.tool_wrapper import ToolRegistry, create_tool_from_method\n"
    
    # Encontrar onde adicionar o import
    import_section_end = content.find('\n\nclass')
    if import_section_end > 0:
        content = content[:import_section_end] + '\n' + import_line + content[import_section_end:]
    
    # Modificar o __init__ para usar ToolRegistry
    init_pattern = r'(def __init__\(self.*?\):.*?)(self\.tools = \[.*?\])'
    
    def replace_init(match):
        init_def = match.group(1)
        
        new_init = """
        # Tool Registry para gerenciar tools
        self.tool_registry = ToolRegistry()
        
        # Registrar métodos como tools
        self._register_tools()
        
        # Obter tools registrados
        self.tools = self.tool_registry.get_tools()"""
        
        return init_def + new_init
    
    content = re.sub(init_pattern, replace_init, content, flags=re.DOTALL)
    
    # Adicionar método para registrar tools
    register_method = '''
    def _register_tools(self):
        """Registra métodos como tools usando ToolRegistry"""
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
    '''
    
    # Adicionar o método após o __init__
    # Encontrar o final do __init__
    init_end_pattern = r'(logger\.info\("✅ QualificationAgent inicializado"\))'
    insert_pos = content.find(init_end_pattern)
    if insert_pos > 0:
        # Encontrar o fim do método __init__
        next_method = content.find('\n    async def', insert_pos)
        if next_method > 0:
            content = content[:next_method] + '\n' + register_method + content[next_method:]
    
    # Salvar arquivo corrigido
    qual_path.write_text(content)
    print(f"✅ QualificationAgent corrigido com tool wrapper solution")
    
    return qual_path


def main():
    """
    Executa a correção completa dos agentes
    """
    print("🚀 Iniciando correção definitiva dos agentes com @tool decorator")
    print("=" * 60)
    
    try:
        # Passo 1: Criar solução de wrapper
        print("\n📝 Passo 1: Criando solução de tool wrapper...")
        create_tool_wrapper_solution()
        
        # Passo 2: Aplicar patch no CRMAgent
        print("\n🔧 Passo 2: Aplicando correção no CRMAgent...")
        patch_crm_agent()
        
        # Passo 3: Aplicar patch no QualificationAgent
        print("\n🔧 Passo 3: Aplicando correção no QualificationAgent...")
        patch_qualification_agent()
        
        print("\n" + "=" * 60)
        print("✅ CORREÇÃO COMPLETA!")
        print("\n📋 Próximos passos:")
        print("1. Teste a aplicação com: python test_basic.py")
        print("2. Se funcionar, teste com WhatsApp")
        print("3. Monitore os logs para verificar se os tools estão funcionando")
        
        print("\n💡 Como funciona a solução:")
        print("- Criamos um ToolRegistry que gerencia os tools")
        print("- Cada método é transformado em uma função via closure")
        print("- O @tool decorator é aplicado na função wrapper")
        print("- A instância (self) é capturada no closure")
        
    except Exception as e:
        print(f"\n❌ Erro durante correção: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())