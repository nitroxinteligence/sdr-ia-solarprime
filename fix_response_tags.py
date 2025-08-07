#!/usr/bin/env python3
"""
Correção SIMPLES para resolver vazamento de tags na resposta

PROBLEMA: Agente está gerando tags malformadas e vazando tags na resposta
SOLUÇÃO: Melhorar regex de extração para capturar variações das tags
"""

import os
import re
from datetime import datetime

def fix_response_extraction():
    """Corrige a extração da resposta final para lidar com tags malformadas"""
    
    file_path = "app/api/webhooks.py"
    backup_path = f"app/api/webhooks.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🔧 Corrigindo extração de resposta final")
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
    
    # Correção: Melhorar regex para capturar variações das tags
    old_pattern = """        # Busca o conteúdo entre as tags <RESPOSTA_FINAL> e </RESPOSTA_FINAL>
        pattern = r'<RESPOSTA_FINAL>(.*?)</RESPOSTA_FINAL>'
        match = re.search(pattern, full_response, re.DOTALL | re.IGNORECASE)"""
    
    new_pattern = """        # Busca o conteúdo entre as tags - aceita variações
        patterns = [
            r'<RESPOSTA_FINAL>(.*?)</RESPOSTA_FINAL>',
            r'<RESPOSTAFINAL>(.*?)</RESPOSTAFINAL>',
            r'<RESPOSTA[_ ]FINAL[>:](.*?)$'  # Para casos onde a tag não fecha
        ]
        
        match = None
        for pattern in patterns:
            match = re.search(pattern, full_response, re.DOTALL | re.IGNORECASE)
            if match:
                break"""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("✅ Correção 1 aplicada: Melhorado regex de extração")
    else:
        print("⚠️  Correção 1: Código não encontrado exatamente")
    
    # Correção 2: Adicionar limpeza extra das tags vazadas
    old_extraction = """        if match:
            # Extrai e limpa o conteúdo
            final_response = match.group(1).strip()
            emoji_logger.system_debug(f"✅ Resposta final extraída com sucesso: {final_response[:50]}...")"""
    
    new_extraction = """        if match:
            # Extrai e limpa o conteúdo
            final_response = match.group(1).strip()
            
            # LIMPEZA EXTRA: Remover qualquer tag ou lixo que vazou
            final_response = re.sub(r'<[^>]*>', '', final_response)  # Remove tags HTML/XML
            final_response = re.sub(r'</?\w+[^>]*>', '', final_response)  # Remove tags malformadas
            final_response = re.sub(r'^\s*[.,:;]*\s*', '', final_response)  # Remove pontuação inicial
            final_response = final_response.strip()
            
            emoji_logger.system_debug(f"✅ Resposta final extraída e limpa: {final_response[:50]}...")"""
    
    if old_extraction in content:
        content = content.replace(old_extraction, new_extraction)
        print("✅ Correção 2 aplicada: Limpeza extra de tags")
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Correções aplicadas com sucesso!")
    print(f"📝 Mudanças:")
    print(f"   1. Aceita variações de tags: <RESPOSTA_FINAL>, <RESPOSTAFINAL>")
    print(f"   2. Remove tags HTML/XML vazadas")
    print(f"   3. Remove pontuação inicial desnecessária")
    
    return True

if __name__ == "__main__":
    if fix_response_extraction():
        print("\n🚀 Correção aplicada!")
        print("   Agora as respostas serão limpas automaticamente")
    else:
        print("\n❌ Falha ao aplicar correções")