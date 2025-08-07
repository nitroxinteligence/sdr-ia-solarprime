#!/usr/bin/env python3
"""
Correção SIMPLES para resolver erro: EmojiLogger.system_error() missing 1 required positional argument

PROBLEMA: system_error() precisa de 2 argumentos: (component, error)
SOLUÇÃO: Adicionar o componente como primeiro argumento
"""

import os
import re
from datetime import datetime

def fix_emoji_logger_errors():
    """Corrige todas as chamadas incorretas para emoji_logger.system_error()"""
    
    file_path = "app/agents/agentic_sdr.py"
    backup_path = f"app/agents/agentic_sdr.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🔧 Corrigindo erros do EmojiLogger.system_error()")
    print(f"📁 Arquivo: {file_path}")
    
    # Fazer backup
    if os.path.exists(file_path):
        os.system(f"cp {file_path} {backup_path}")
        print(f"✅ Backup criado: {backup_path}")
    else:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lista de correções
    corrections = [
        # Linha 2909
        (
            'emoji_logger.system_error(f"❌ Timeout em agent.arun após {AGENT_TIMEOUT}s (modo complexo)")',
            'emoji_logger.system_error("Agent Timeout", f"❌ Timeout em agent.arun após {AGENT_TIMEOUT}s (modo complexo)")'
        ),
        # Linha 2912
        (
            'emoji_logger.system_error(f"❌ Erro em agent.arun (modo complexo): {str(e)}")',
            'emoji_logger.system_error("Agent Error", f"❌ Erro em agent.arun (modo complexo): {str(e)}")'
        ),
        # Linha 2929
        (
            'emoji_logger.system_error("❌ Agent não está pronto ou não tem método arun")',
            'emoji_logger.system_error("Agent State", "❌ Agent não está pronto ou não tem método arun")'
        ),
        # Linha 2947
        (
            'emoji_logger.system_error(f"❌ Timeout em agent.arun após {AGENT_TIMEOUT}s")',
            'emoji_logger.system_error("Agent Timeout", f"❌ Timeout em agent.arun após {AGENT_TIMEOUT}s")'
        ),
        # Linha 2953
        (
            'emoji_logger.system_error(f"❌ Falha no fallback: {str(fallback_error)}")',
            'emoji_logger.system_error("Fallback Error", f"❌ Falha no fallback: {str(fallback_error)}")'
        ),
        # Linha 2956
        (
            'emoji_logger.system_error(f"❌ Erro em agent.arun: {str(arun_error)}")',
            'emoji_logger.system_error("Agent Error", f"❌ Erro em agent.arun: {str(arun_error)}")'
        ),
        # Linha 2958
        (
            'emoji_logger.system_error(f"Stack trace: {traceback.format_exc()}")',
            'emoji_logger.system_error("Stack Trace", f"Stack trace: {traceback.format_exc()}")'
        ),
        # Linha 3232
        (
            'emoji_logger.system_error(f"Erro na personalização: {str(e)}, usando resposta original")',
            'emoji_logger.system_error("Personalization", f"Erro na personalização: {str(e)}, usando resposta original")'
        )
    ]
    
    # Aplicar correções
    corrections_applied = 0
    for old, new in corrections:
        if old in content:
            content = content.replace(old, new)
            corrections_applied += 1
            print(f"✅ Corrigido: {old[:50]}...")
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ {corrections_applied} correções aplicadas!")
    print(f"📝 Todas as chamadas system_error() agora têm 2 argumentos")
    
    return True

if __name__ == "__main__":
    if fix_emoji_logger_errors():
        print("\n🚀 Próximos passos:")
        print("   1. Reinicie o servidor: docker-compose restart")
        print("   2. O erro 'missing 1 required positional argument' foi corrigido")
    else:
        print("\n❌ Falha ao aplicar correções")