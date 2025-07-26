#!/usr/bin/env python3
"""
Script para corrigir problemas de indentação
"""

import re
import sys
from pathlib import Path

def fix_indentation(file_path):
    """Corrige problemas de indentação em arquivo Python"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    in_multiline_string = False
    string_delimiter = None
    
    for i, line in enumerate(lines):
        # Verificar se estamos em uma string multiline
        if not in_multiline_string:
            # Verificar início de string multiline
            if '"""' in line or "'''" in line:
                if line.count('"""') % 2 == 1:
                    in_multiline_string = True
                    string_delimiter = '"""'
                elif line.count("'''") % 2 == 1:
                    in_multiline_string = True
                    string_delimiter = "'''"
        else:
            # Verificar fim de string multiline
            if string_delimiter in line:
                if line.count(string_delimiter) % 2 == 1:
                    in_multiline_string = False
        
        # Se não estamos em uma string multiline, verificar indentação
        if not in_multiline_string:
            # Remover espaços extras no início
            stripped = line.lstrip()
            if stripped and not line.startswith('#'):
                # Calcular indentação correta
                indent_level = 0
                
                # Procurar padrões que indicam nível de indentação
                if i > 0:
                    prev_line = lines[i-1].rstrip()
                    if prev_line.endswith(':'):
                        # Linha anterior termina com ':', aumentar indentação
                        prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                        indent_level = prev_indent + 4
                    else:
                        # Manter mesma indentação ou deduzir do contexto
                        # Procurar linha não vazia anterior
                        for j in range(i-1, -1, -1):
                            if lines[j].strip() and not lines[j].strip().startswith('#'):
                                prev_indent = len(lines[j]) - len(lines[j].lstrip())
                                
                                # Se a linha atual começa com palavras-chave que reduzem indentação
                                if stripped.startswith(('else:', 'elif ', 'except:', 'except ', 'finally:', 'except Exception')):
                                    indent_level = prev_indent - 4
                                elif stripped.startswith(('return', 'raise', 'break', 'continue', 'pass')):
                                    indent_level = prev_indent
                                else:
                                    indent_level = prev_indent
                                break
                
                # Garantir que a indentação seja múltiplo de 4
                indent_level = max(0, indent_level)
                indent_level = (indent_level // 4) * 4
                
                # Aplicar indentação correta
                fixed_line = ' ' * indent_level + stripped
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Arquivo corrigido: {file_path}")

if __name__ == "__main__":
    # Arquivos a corrigir
    files_to_fix = [
        "api/routes/instance.py",
        "api/routes/health.py",
        "api/routes/webhook_admin.py",
        "api/routes/webhooks.py",
        "services/whatsapp_service.py"
    ]
    
    for file_path in files_to_fix:
        try:
            fix_indentation(file_path)
        except Exception as e:
            print(f"❌ Erro ao corrigir {file_path}: {e}")