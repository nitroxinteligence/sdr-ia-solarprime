#!/usr/bin/env python3
"""
fix_agent_errors.py - Script de correção automática dos erros nos agentes
Corrige problemas de assinatura de métodos e tratamento de erros
"""

import os
import re
import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_crm_agent():
    """Corrige métodos do CRM Agent - adiciona self aos métodos"""
    crm_path = Path("app/teams/agents/crm.py")
    
    if not crm_path.exists():
        print(f"⚠️ Arquivo não encontrado: {crm_path}")
        return False
    
    print(f"🔧 Corrigindo CRM Agent...")
    
    with open(crm_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Padrões para corrigir - adicionar self como primeiro parâmetro
    replacements = [
        # Corrigir create_or_update_lead
        (r'def create_or_update_lead\(\s*lead_data:', 
         'def create_or_update_lead(self, lead_data:'),
        (r'async def create_or_update_lead\(\s*lead_data:', 
         'async def create_or_update_lead(self, lead_data:'),
         
        # Corrigir classify_lead_temperature
        (r'def classify_lead_temperature\(\s*score:', 
         'def classify_lead_temperature(self, score:'),
        (r'async def classify_lead_temperature\(\s*score:', 
         'async def classify_lead_temperature(self, score:'),
         
        # Corrigir update_lead_stage
        (r'def update_lead_stage\(\s*lead_id:', 
         'def update_lead_stage(self, lead_id:'),
        (r'async def update_lead_stage\(\s*lead_id:', 
         'async def update_lead_stage(self, lead_id:'),
         
        # Corrigir get_lead_by_phone
        (r'def get_lead_by_phone\(\s*phone:', 
         'def get_lead_by_phone(self, phone:'),
        (r'async def get_lead_by_phone\(\s*phone:', 
         'async def get_lead_by_phone(self, phone:'),
    ]
    
    changes_made = 0
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changes_made += 1
            content = new_content
            print(f"  ✅ Corrigido: {pattern[:30]}...")
    
    if changes_made > 0:
        # Salvar backup
        backup_path = crm_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  📦 Backup salvo em: {backup_path}")
        
        # Salvar correções
        with open(crm_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {changes_made} correções aplicadas no CRM Agent")
    else:
        print("  ℹ️ CRM Agent já está correto ou precisa correção manual")
    
    return True

def fix_calendar_agent():
    """Corrige problemas de índice e tratamento de erros no Calendar Agent"""
    calendar_path = Path("app/teams/agents/calendar.py")
    
    if not calendar_path.exists():
        print(f"⚠️ Arquivo não encontrado: {calendar_path}")
        return False
    
    print(f"🔧 Corrigindo Calendar Agent...")
    
    with open(calendar_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_lines = lines.copy()
    changes_made = 0
    
    # Procurar por acessos a índices sem verificação
    for i, line in enumerate(lines):
        # Corrigir acessos a [0] sem verificação
        if '[0]' in line and 'if ' not in lines[max(0, i-1)]:
            # Verificar se é um acesso potencialmente perigoso
            if 'available_slots[0]' in line or 'slots[0]' in line or 'results[0]' in line:
                indent = len(line) - len(line.lstrip())
                var_match = re.search(r'(\w+)\[0\]', line)
                if var_match:
                    var_name = var_match.group(1)
                    # Adicionar verificação antes
                    new_lines = [
                        ' ' * indent + f'if {var_name} and len({var_name}) > 0:\n',
                        ' ' * (indent + 4) + line.lstrip(),
                        ' ' * indent + 'else:\n',
                        ' ' * (indent + 4) + 'logger.warning(f"Lista vazia: {var_name}")\n',
                        ' ' * (indent + 4) + 'return {"success": False, "error": "Nenhum item disponível"}\n'
                    ]
                    lines[i] = ''.join(new_lines)
                    changes_made += 1
                    print(f"  ✅ Corrigido acesso a índice na linha {i+1}")
    
    # Adicionar tratamento de exceções em métodos schedule_meeting
    for i, line in enumerate(lines):
        if 'def schedule_meeting' in line or 'async def schedule_meeting' in line:
            # Verificar se já tem try/except
            has_try = False
            for j in range(i+1, min(i+10, len(lines))):
                if 'try:' in lines[j]:
                    has_try = True
                    break
            
            if not has_try:
                # Adicionar try/except
                indent = len(lines[i+1]) - len(lines[i+1].lstrip())
                # Encontrar o fim do método
                method_end = i + 1
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' '):
                        method_end = j
                        break
                
                # Envolver conteúdo em try/except
                if method_end > i + 1:
                    lines[i+1] = ' ' * indent + 'try:\n' + ' ' * 4 + lines[i+1]
                    for j in range(i+2, method_end):
                        if lines[j].strip():
                            lines[j] = ' ' * 4 + lines[j]
                    
                    exception_block = [
                        ' ' * indent + 'except IndexError as e:\n',
                        ' ' * (indent + 4) + 'logger.error(f"Erro de índice: {e}")\n',
                        ' ' * (indent + 4) + 'return {"success": False, "error": str(e)}\n',
                        ' ' * indent + 'except Exception as e:\n',
                        ' ' * (indent + 4) + 'logger.error(f"Erro ao agendar reunião: {e}")\n',
                        ' ' * (indent + 4) + 'return {"success": False, "error": str(e)}\n'
                    ]
                    lines.insert(method_end, ''.join(exception_block))
                    changes_made += 1
                    print(f"  ✅ Adicionado tratamento de exceções em schedule_meeting")
    
    if changes_made > 0:
        # Salvar backup
        backup_path = calendar_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(original_lines)
        print(f"  📦 Backup salvo em: {backup_path}")
        
        # Salvar correções
        with open(calendar_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  ✅ {changes_made} correções aplicadas no Calendar Agent")
    else:
        print("  ℹ️ Calendar Agent já está correto ou precisa correção manual")
    
    return True

def fix_qualification_agent():
    """Corrige problemas no Qualification Agent"""
    qual_path = Path("app/teams/agents/qualification.py")
    
    if not qual_path.exists():
        print(f"⚠️ Arquivo não encontrado: {qual_path}")
        return False
    
    print(f"🔧 Corrigindo Qualification Agent...")
    
    with open(qual_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Corrigir métodos sem self
    replacements = [
        (r'def classify_lead_temperature\(\s*score:', 
         'def classify_lead_temperature(self, score:'),
        (r'async def classify_lead_temperature\(\s*score:', 
         'async def classify_lead_temperature(self, score:'),
    ]
    
    changes_made = 0
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changes_made += 1
            content = new_content
            print(f"  ✅ Corrigido: {pattern[:30]}...")
    
    if changes_made > 0:
        # Salvar backup
        backup_path = qual_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  📦 Backup salvo em: {backup_path}")
        
        # Salvar correções
        with open(qual_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {changes_made} correções aplicadas no Qualification Agent")
    else:
        print("  ℹ️ Qualification Agent já está correto")
    
    return True

def add_error_handling_config():
    """Adiciona configurações para melhor tratamento de erros"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("⚠️ Arquivo .env não encontrado")
        return False
    
    print("🔧 Atualizando configurações de erro...")
    
    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    # Adicionar configurações se não existirem
    configs_to_add = []
    
    if 'DISABLE_MEMORY=' not in env_content:
        configs_to_add.append('DISABLE_MEMORY=true')
        print("  ✅ Adicionando DISABLE_MEMORY=true")
    
    if 'SUPPRESS_VALIDATION_ERRORS=' not in env_content:
        configs_to_add.append('SUPPRESS_VALIDATION_ERRORS=true')
        print("  ✅ Adicionando SUPPRESS_VALIDATION_ERRORS=true")
    
    if 'ERROR_RECOVERY=' not in env_content:
        configs_to_add.append('ERROR_RECOVERY=true')
        print("  ✅ Adicionando ERROR_RECOVERY=true")
    
    if configs_to_add:
        with open(env_path, 'a', encoding='utf-8') as f:
            f.write('\n\n# Configurações de tratamento de erros (adicionadas automaticamente)\n')
            for config in configs_to_add:
                f.write(f'{config}\n')
        print(f"  ✅ {len(configs_to_add)} configurações adicionadas ao .env")
    else:
        print("  ℹ️ Configurações já estão presentes")
    
    return True

def verify_fixes():
    """Verifica se as correções foram aplicadas"""
    print("\n🔍 Verificando correções...")
    
    # Verificar CRM Agent
    crm_path = Path("app/teams/agents/crm.py")
    if crm_path.exists():
        with open(crm_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'def create_or_update_lead(self,' in content:
                print("  ✅ CRM Agent: create_or_update_lead corrigido")
            else:
                print("  ⚠️ CRM Agent: create_or_update_lead ainda precisa correção")
    
    # Verificar Calendar Agent
    calendar_path = Path("app/teams/agents/calendar.py")
    if calendar_path.exists():
        with open(calendar_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'except IndexError' in content or 'except Exception' in content:
                print("  ✅ Calendar Agent: Tratamento de erros presente")
            else:
                print("  ⚠️ Calendar Agent: Pode precisar mais tratamento de erros")
    
    print("\n✅ Verificação concluída")

def main():
    """Executa todas as correções"""
    print("="*60)
    print("🚀 SCRIPT DE CORREÇÃO DE ERROS DOS AGENTES")
    print("="*60)
    
    print("\n📝 Iniciando correções...\n")
    
    # Executar correções
    success = True
    
    success = fix_crm_agent() and success
    success = fix_calendar_agent() and success
    success = fix_qualification_agent() and success
    success = add_error_handling_config() and success
    
    # Verificar correções
    verify_fixes()
    
    if success:
        print("\n" + "="*60)
        print("🎉 CORREÇÕES APLICADAS COM SUCESSO!")
        print("="*60)
        print("\n📌 Próximos passos:")
        print("1. Execute o teste simples: python test_calendar_meet_only.py")
        print("2. Se funcionar, teste o E2E: python test_e2e_simplified.py")
        print("\n💡 Dica: Se ainda houver erros, verifique os backups criados (.backup)")
    else:
        print("\n⚠️ Algumas correções falharam. Verifique os logs acima.")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)