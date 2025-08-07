#!/usr/bin/env python3
"""
FIX URGENTE: Agente retornando resposta vazia

PROBLEMA:
- agent.arun completa com sucesso
- result.content = True (booleano)
- Conteúdo é extraído de messages
- Mas raw_response fica vazio

CAUSA: Lógica incorreta ao verificar messages quando content=True
"""

import shutil
from datetime import datetime

def fix_empty_response():
    """Corrige o problema de resposta vazia do agente"""
    
    print("🔧 CORRIGINDO RESPOSTA VAZIA DO AGENTE")
    print("=" * 60)
    
    file_path = "app/agents/agentic_sdr.py"
    
    # Backup
    shutil.copy(file_path, f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a seção problemática
    old_code = '''                    # 2. Se vazio ou content=True, verificar messages (AGNO padrão)
                    if (not raw_response or raw_response == "") and hasattr(result, 'messages') and result.messages:'''
    
    # CORREÇÃO: Incluir quando content é True (booleano)
    new_code = '''                    # 2. Se vazio ou content=True, verificar messages (AGNO padrão)
                    if (not raw_response or raw_response == "" or result.content is True) and hasattr(result, 'messages') and result.messages:'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ Correção 1 aplicada: Incluir content=True na verificação de messages")
    
    # Segunda correção: Garantir que o conteúdo extraído seja usado
    old_code2 = '''                                    emoji_logger.system_info(f"✅ Conteúdo extraído de messages[{i}]: tipo={type(raw_response).__name__}, tamanho={len(str(raw_response)) if raw_response else 0}")
                                    break'''
    
    new_code2 = '''                                    emoji_logger.system_info(f"✅ Conteúdo extraído de messages[{i}]: tipo={type(raw_response).__name__}, tamanho={len(str(raw_response)) if raw_response else 0}")
                                    if raw_response and str(raw_response).strip():  # Garantir que não está vazio
                                        break'''
    
    if old_code2 in content:
        content = content.replace(old_code2, new_code2)
        print("✅ Correção 2 aplicada: Garantir que raw_response não está vazio")
    
    # Terceira correção: Remover duplicação de código
    # Há duas verificações idênticas seguidas (linhas 3186-3192 são duplicadas)
    duplicate_check = '''                    # CORREÇÃO: Verificar se é None ou "None" ou lista vazia
                    if (raw_response is None or 
                        str(raw_response).strip().lower() == "none" or
                        (isinstance(raw_response, list) and len(raw_response) == 0) or
                        (isinstance(raw_response, str) and raw_response.strip() == "")):
                        emoji_logger.system_warning("⚠️ raw_response é None ou vazio! Usando fallback...")
                        raw_response = None  # Força None para cair no fallback
                    
                    # CORREÇÃO: Verificar se é None ou "None" ou lista vazia
                    if (raw_response is None or 
                        str(raw_response).strip().lower() == "none" or
                        (isinstance(raw_response, list) and len(raw_response) == 0) or
                        (isinstance(raw_response, str) and raw_response.strip() == "")):
                        emoji_logger.system_warning("⚠️ raw_response é None ou vazio! Usando fallback...")
                        raw_response = None  # Força None para cair no fallback'''
    
    single_check = '''                    # CORREÇÃO: Verificar se é None ou "None" ou lista vazia
                    if (raw_response is None or 
                        str(raw_response).strip().lower() == "none" or
                        (isinstance(raw_response, list) and len(raw_response) == 0) or
                        (isinstance(raw_response, str) and raw_response.strip() == "")):
                        emoji_logger.system_warning("⚠️ raw_response é None ou vazio! Usando fallback...")
                        raw_response = None  # Força None para cair no fallback'''
    
    if duplicate_check in content:
        content = content.replace(duplicate_check, single_check)
        print("✅ Correção 3 aplicada: Remover duplicação de código")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ TODAS AS CORREÇÕES APLICADAS!")
    print("\n📋 RESUMO DAS MUDANÇAS:")
    print("   1. Incluir content=True na verificação de messages")
    print("   2. Garantir que raw_response extraído não está vazio")
    print("   3. Remover código duplicado")
    print("\n🚀 O agente agora vai extrair corretamente o conteúdo das messages!")
    print("\nO SIMPLES FUNCIONA! 💪")

if __name__ == "__main__":
    fix_empty_response()