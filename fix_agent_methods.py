#!/usr/bin/env python3
"""
fix_agent_methods.py - Correção específica dos métodos dos agentes
Corrige problemas com decorators @tool e parâmetros self
"""

import os
import re
import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_crm_agent_tools():
    """Corrige métodos com @tool no CRM Agent"""
    crm_path = Path("app/teams/agents/crm.py")
    
    if not crm_path.exists():
        print(f"⚠️ Arquivo não encontrado: {crm_path}")
        return False
    
    print(f"🔧 Corrigindo CRM Agent (métodos @tool)...")
    
    with open(crm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_lines = lines.copy()
    changes_made = 0
    
    # Procurar por métodos com @tool que não tem self como primeiro parâmetro após self
    i = 0
    while i < len(lines):
        # Verificar se é um decorator @tool
        if '@tool' in lines[i]:
            # Procurar a definição do método nas próximas linhas
            for j in range(i+1, min(i+5, len(lines))):
                if 'def ' in lines[j] or 'async def ' in lines[j]:
                    # Verificar se tem self
                    if 'self,' not in lines[j] and 'self)' not in lines[j]:
                        # Adicionar self se não tiver
                        if '(' in lines[j]:
                            # Encontrar onde colocar self
                            indent = len(lines[j]) - len(lines[j].lstrip())
                            if 'async def' in lines[j]:
                                pattern = r'(async def \w+\()'
                            else:
                                pattern = r'(def \w+\()'
                            
                            new_line = re.sub(pattern, r'\1self, ', lines[j])
                            if new_line != lines[j]:
                                lines[j] = new_line
                                changes_made += 1
                                print(f"  ✅ Corrigido método na linha {j+1}")
                    break
        i += 1
    
    if changes_made > 0:
        # Salvar backup
        backup_path = crm_path.with_suffix('.py.backup2')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(original_lines)
        print(f"  📦 Backup salvo em: {backup_path}")
        
        # Salvar correções
        with open(crm_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  ✅ {changes_made} correções aplicadas no CRM Agent")
    else:
        print("  ℹ️ CRM Agent já está correto")
    
    return True

def fix_calendar_agent_schedule():
    """Corrige o método schedule_meeting para verificar slots disponíveis"""
    calendar_path = Path("app/teams/agents/calendar.py")
    
    if not calendar_path.exists():
        print(f"⚠️ Arquivo não encontrado: {calendar_path}")
        return False
    
    print(f"🔧 Corrigindo Calendar Agent (schedule_meeting)...")
    
    with open(calendar_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Adicionar verificação de slots disponíveis
    # Procurar por find_available_slots e adicionar verificação
    pattern = r'(available_slots = .*?find_available_slots.*?\n)'
    
    def add_check(match):
        line = match.group(1)
        indent = len(line) - len(line.lstrip())
        return line + ' ' * indent + 'if not available_slots:\n' + \
               ' ' * (indent + 4) + 'logger.warning("Nenhum slot disponível encontrado")\n' + \
               ' ' * (indent + 4) + 'available_slots = []\n'
    
    # Aplicar a correção apenas se não existir já
    if 'if not available_slots:' not in content:
        new_content = re.sub(pattern, add_check, content)
        if new_content != content:
            content = new_content
            print("  ✅ Adicionada verificação de slots vazios")
    
    # Verificar acesso a índices sem proteção
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'available_slots[0]' in line and i > 0:
            # Verificar se tem proteção antes
            prev_line = lines[i-1]
            if 'if ' not in prev_line and 'available_slots' in line:
                # Adicionar proteção
                indent = len(line) - len(line.lstrip())
                protected = f"{' ' * indent}if available_slots and len(available_slots) > 0:\n{' ' * (indent + 4)}{line.lstrip()}"
                lines[i] = protected
                print(f"  ✅ Protegido acesso a índice na linha {i+1}")
    
    content = '\n'.join(lines)
    
    if content != original_content:
        # Salvar backup
        backup_path = calendar_path.with_suffix('.py.backup3')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  📦 Backup salvo em: {backup_path}")
        
        # Salvar correções
        with open(calendar_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Correções aplicadas no Calendar Agent")
    else:
        print("  ℹ️ Calendar Agent já está correto")
    
    return True

def add_self_to_methods():
    """Adiciona self a métodos que precisam"""
    agents = [
        "app/teams/agents/crm.py",
        "app/teams/agents/qualification.py"
    ]
    
    for agent_path in agents:
        path = Path(agent_path)
        if not path.exists():
            continue
            
        print(f"🔧 Verificando {agent_path}...")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Métodos que precisam de self
        methods_to_fix = [
            'create_or_update_lead',
            'classify_lead_temperature', 
            'update_lead_stage',
            'get_lead_by_phone'
        ]
        
        for method in methods_to_fix:
            # Padrão para encontrar método sem self
            pattern = rf'((?:async )?def {method}\()(?!self)'
            replacement = r'\1self, '
            
            # Aplicar correção
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                print(f"  ✅ Adicionado self ao método {method}")
        
        if content != original:
            # Backup
            backup_path = path.with_suffix('.py.backup_final')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Salvar
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Correções aplicadas em {agent_path}")

def main():
    """Executa todas as correções"""
    print("="*60)
    print("🚀 CORREÇÃO DEFINITIVA DOS AGENTES")
    print("="*60)
    
    print("\n📝 Iniciando correções específicas...\n")
    
    # Executar correções
    fix_crm_agent_tools()
    fix_calendar_agent_schedule()
    add_self_to_methods()
    
    print("\n" + "="*60)
    print("🎉 CORREÇÕES APLICADAS!")
    print("="*60)
    print("\n📌 Teste novamente com:")
    print("   python test_calendar_meet_only.py")
    print("   python test_e2e_simplified.py")
    
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)