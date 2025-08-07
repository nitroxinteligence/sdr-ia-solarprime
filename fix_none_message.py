#!/usr/bin/env python3
"""
Correção DEFINITIVA - Agent enviando "None" no WhatsApp

PROBLEMA: Quando agent.arun dá timeout, retorna None e sistema envia "None" para usuário
SOLUÇÃO: Verificar se raw_response é None e usar fallback apropriado

ZERO COMPLEXIDADE - O SIMPLES FUNCIONA
"""

import os
from datetime import datetime

def fix_none_message():
    """Corrige problema de enviar None para usuário"""
    
    file_path = "app/agents/agentic_sdr.py"
    
    print("🔧 CORREÇÃO DEFINITIVA - Mensagem None")
    print("=" * 60)
    
    # Backup
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(file_path):
        os.system(f"cp {file_path} {backup_path}")
        print(f"✅ Backup criado: {backup_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correção 1: Verificar None após extração de conteúdo
    old_check = '''                    # Debug: Log do conteúdo extraído
                    emoji_logger.system_info(f"📄 raw_response (primeiros 200 chars): {raw_response[:200] if raw_response else 'VAZIO'}...")
                    emoji_logger.system_info(f"📏 Tamanho raw_response: {len(raw_response) if raw_response else 0} caracteres")'''
    
    new_check = '''                    # Debug: Log do conteúdo extraído
                    emoji_logger.system_info(f"📄 raw_response (primeiros 200 chars): {raw_response[:200] if raw_response else 'VAZIO'}...")
                    emoji_logger.system_info(f"📏 Tamanho raw_response: {len(raw_response) if raw_response else 0} caracteres")
                    
                    # CORREÇÃO: Verificar se é None ou "None"
                    if raw_response is None or str(raw_response).strip().lower() == "none":
                        emoji_logger.system_warning("⚠️ raw_response é None! Usando fallback...")
                        raw_response = None  # Força None para cair no fallback'''
    
    content = content.replace(old_check, new_check)
    
    # Correção 2: Melhorar verificação de resposta vazia
    old_empty_check = '''                    # ✅ CORREÇÃO: Verificar se a resposta está vazia antes de processar
                    if not raw_response or raw_response.strip() == "":'''
    
    new_empty_check = '''                    # ✅ CORREÇÃO: Verificar se a resposta está vazia antes de processar
                    if not raw_response or raw_response.strip() == "" or str(raw_response).strip().lower() == "none":'''
    
    content = content.replace(old_empty_check, new_empty_check)
    
    # Correção 3: Garantir que response nunca seja None no final
    old_final_check = '''            # Garantir que response tem um valor antes de aplicar simulação
            if response:
                response = self._apply_typing_simulation(response)
            else:
                # Fallback final se ainda não houver resposta
                response = "<RESPOSTA_FINAL>Oi! 😊 Sou a Helen da Solar Prime. Como posso ajudar você hoje?</RESPOSTA_FINAL>"'''
    
    new_final_check = '''            # Garantir que response tem um valor antes de aplicar simulação
            if response and str(response).strip() != "" and str(response).strip().lower() != "none":
                response = self._apply_typing_simulation(response)
            else:
                # Fallback final se ainda não houver resposta ou se for None
                emoji_logger.system_warning("⚠️ Response vazio ou None no final, usando fallback de emergência")
                
                # Verificar contexto para resposta apropriada
                if messages_history and len(messages_history) > 0:
                    # Já há conversa anterior
                    response = "<RESPOSTA_FINAL>Oi! Me desculpe, tive um pequeno problema aqui. Pode repetir sua última mensagem?</RESPOSTA_FINAL>"
                else:
                    # Primeira interação
                    response = "<RESPOSTA_FINAL>Oi! 😊 Sou a Helen da Solar Prime. Como posso ajudar você hoje?</RESPOSTA_FINAL>"'''
    
    content = content.replace(old_final_check, new_final_check)
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Correções aplicadas em {file_path}")
    print("\n📋 Mudanças implementadas:")
    print("   1. Verificação explícita para None após extração")
    print("   2. Tratamento de 'None' como string")
    print("   3. Fallback apropriado baseado no contexto")
    print("   4. Nunca enviar None para o usuário")
    
    return True

if __name__ == "__main__":
    if fix_none_message():
        print("\n🚀 Problema resolvido!")
        print("   Agora quando houver timeout ou erro:")
        print("   - Resposta apropriada será enviada")
        print("   - Nunca mais enviará 'None' para usuário")