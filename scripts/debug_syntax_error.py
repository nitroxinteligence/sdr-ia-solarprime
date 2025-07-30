#!/usr/bin/env python3
"""
Script para debugar o erro de sintaxe em produção
Adicione este script ao projeto e execute em produção para descobrir o problema
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== DEBUG SYNTAX ERROR ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print("")

# Tentar importar e ver onde falha
try:
    print("1. Tentando importar api.main...")
    import api.main
    print("✅ api.main importado com sucesso")
except SyntaxError as e:
    print(f"❌ SyntaxError em: {e.filename}")
    print(f"   Linha: {e.lineno}")
    print(f"   Texto: {e.text}")
    print(f"   Mensagem: {e.msg}")
    
    # Tentar ler a linha problemática
    if e.filename and os.path.exists(e.filename):
        print("\n📄 Contexto do erro:")
        with open(e.filename, 'r') as f:
            lines = f.readlines()
            start = max(0, e.lineno - 5)
            end = min(len(lines), e.lineno + 5)
            
            for i in range(start, end):
                marker = ">>>" if i + 1 == e.lineno else "   "
                print(f"{marker} {i+1:4d}: {lines[i].rstrip()}")
    
    # Procurar por "markdown" duplicado
    if e.filename:
        print("\n🔍 Procurando por 'markdown' no arquivo...")
        with open(e.filename, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
        markdown_lines = []
        for i, line in enumerate(lines):
            if 'markdown' in line.lower():
                markdown_lines.append((i + 1, line.strip()))
        
        if markdown_lines:
            print(f"Encontradas {len(markdown_lines)} linhas com 'markdown':")
            for line_num, line in markdown_lines:
                print(f"   Linha {line_num}: {line}")
        else:
            print("   Nenhuma linha com 'markdown' encontrada")
            
except Exception as e:
    print(f"❌ Erro inesperado: {type(e).__name__}: {e}")

print("\n=== FIM DO DEBUG ===")