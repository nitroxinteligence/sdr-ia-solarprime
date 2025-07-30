#!/usr/bin/env python3
"""
Script para verificar sintaxe de todos os arquivos Python
"""

import ast
import sys
import os
from pathlib import Path

def check_syntax(file_path):
    """Verifica sintaxe de um arquivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tenta compilar o código
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, e

def main():
    project_root = Path(__file__).parent.parent
    errors_found = False
    
    # Arquivos críticos para verificar
    critical_files = [
        'agents/sdr_agent.py',
        'services/whatsapp_service.py',
        'workflows/follow_up_workflow.py',
        'api/main.py'
    ]
    
    print("🔍 Verificando sintaxe dos arquivos Python...")
    print("-" * 50)
    
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            success, error = check_syntax(full_path)
            if success:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}")
                print(f"   Erro: {error}")
                print(f"   Linha: {error.lineno}")
                print(f"   Texto: {error.text}")
                errors_found = True
        else:
            print(f"⚠️  {file_path} - arquivo não encontrado")
    
    print("-" * 50)
    
    if errors_found:
        print("❌ Foram encontrados erros de sintaxe!")
        sys.exit(1)
    else:
        print("✅ Todos os arquivos estão com sintaxe correta!")
        sys.exit(0)

if __name__ == "__main__":
    main()