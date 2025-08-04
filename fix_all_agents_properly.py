#!/usr/bin/env python3
"""
fix_all_agents_properly.py - Solução definitiva para o problema @tool
Remove todos os @tool dos métodos e cria wrappers adequados
"""

import os
import re
import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def remove_tool_decorators(file_path):
    """Remove todos os decorators @tool de um arquivo"""
    
    if not file_path.exists():
        print(f"⚠️ Arquivo não encontrado: {file_path}")
        return False
    
    print(f"🔧 Processando {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_lines = lines.copy()
    changes_made = 0
    
    # Procurar por @tool e remover
    i = 0
    while i < len(lines):
        if lines[i].strip() == '@tool':
            # Remover a linha @tool
            lines.pop(i)
            changes_made += 1
            print(f"  ✅ Removido @tool na linha {i+1}")
            # Não incrementar i porque removemos uma linha
        else:
            i += 1
    
    if changes_made > 0:
        # Salvar backup
        backup_path = file_path.with_suffix('.py.backup_tool')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(original_lines)
        print(f"  📦 Backup salvo em: {backup_path}")
        
        # Salvar correções
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  ✅ {changes_made} decorators @tool removidos")
    else:
        print(f"  ℹ️ Nenhum @tool encontrado")
    
    return True

def create_wrapper_for_agent(agent_file, agent_class_name):
    """Cria wrappers para os métodos de um agent"""
    
    file_path = Path(agent_file)
    if not file_path.exists():
        print(f"⚠️ Arquivo não encontrado: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar métodos que precisam de wrapper (antigos @tool)
    # Procurar por async def method_name(self, ...) que sejam públicos
    pattern = r'async def ([a-z_]+[a-z0-9_]*)\(self[,\)]'
    methods = re.findall(pattern, content)
    
    # Filtrar métodos que parecem ser tools (não começam com _)
    tool_methods = [m for m in methods if not m.startswith('_') and m != 'initialize']
    
    if not tool_methods:
        print(f"  ℹ️ Nenhum método tool encontrado em {agent_class_name}")
        return True
    
    print(f"  📝 Criando wrappers para {len(tool_methods)} métodos em {agent_class_name}")
    
    # Criar código do wrapper
    wrapper_code = f"""
    def _create_tools(self):
        \"\"\"Cria tools usando wrappers para os métodos\"\"\"
        from agno.tools import tool
        tools = []
        
"""
    
    for method in tool_methods:
        wrapper_code += f"""        @tool
        async def {method}_tool(*args, **kwargs):
            return await self.{method}(*args, **kwargs)
        {method}_tool.__name__ = '{method}'
        tools.append({method}_tool)
        
"""
    
    wrapper_code += """        return tools
"""
    
    # Verificar se já existe _create_tools
    if '_create_tools' not in content:
        # Adicionar o método _create_tools antes do último método ou no final da classe
        # Encontrar o final da classe __init__
        init_end = content.find('def __init__')
        if init_end != -1:
            # Encontrar o próximo def após __init__
            next_def = content.find('\n    def ', init_end + 10)
            if next_def != -1:
                # Inserir antes do próximo método
                content = content[:next_def] + '\n' + wrapper_code + content[next_def:]
            else:
                # Adicionar no final da classe
                content = content + '\n' + wrapper_code
        
        # Atualizar o __init__ para usar _create_tools
        init_pattern = r'(self\.tools = \[)[^\]]*(\])'
        replacement = r'\1*self._create_tools()\2'
        content = re.sub(init_pattern, replacement, content)
        
        # Salvar arquivo atualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Wrappers criados para {agent_class_name}")
        return True
    else:
        print(f"  ℹ️ {agent_class_name} já tem _create_tools")
        return True

def main():
    """Executa todas as correções"""
    print("="*60)
    print("🚀 CORREÇÃO DEFINITIVA - PROBLEMA @tool")
    print("="*60)
    
    print("\n📝 Removendo decorators @tool...\n")
    
    # Lista de agents para corrigir
    agents = [
        ("app/teams/agents/qualification.py", "QualificationAgent"),
        ("app/teams/agents/calendar.py", "CalendarAgent"),
        ("app/teams/agents/followup.py", "FollowUpAgent"),
        ("app/teams/agents/knowledge.py", "KnowledgeAgent"),
        ("app/teams/agents/crm.py", "CRMAgent"),
        ("app/teams/agents/bill_analyzer.py", "BillAnalyzerAgent")
    ]
    
    # Passo 1: Remover todos os @tool
    for agent_file, _ in agents:
        remove_tool_decorators(Path(agent_file))
    
    print("\n📝 Criando wrappers para métodos...\n")
    
    # Passo 2: Criar wrappers
    for agent_file, agent_class in agents:
        create_wrapper_for_agent(agent_file, agent_class)
    
    print("\n" + "="*60)
    print("🎉 CORREÇÕES APLICADAS!")
    print("="*60)
    print("\n📌 Teste com:")
    print("   python test_final_validation.py")
    
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)