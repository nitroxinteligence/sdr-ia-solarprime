#!/usr/bin/env python3
"""
Correção DEFINITIVA para extração de conteúdo do RunResponse

PROBLEMA: RunResponse tem content=None mas tem messages com o conteúdo
SOLUÇÃO: Verificar messages quando content está vazio

ZERO COMPLEXIDADE - O SIMPLES FUNCIONA
"""

import os
from datetime import datetime

def fix_runresponse_extraction():
    """Corrige extração de conteúdo do RunResponse"""
    
    file_path = "app/agents/agentic_sdr.py"
    
    print("🔧 CORREÇÃO DEFINITIVA - Extração RunResponse")
    print("=" * 60)
    
    # Backup
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(file_path):
        os.system(f"cp {file_path} {backup_path}")
        print(f"✅ Backup criado: {backup_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a seção de extração de conteúdo
    extraction_start = content.find("# Extrair conteúdo da resposta")
    if extraction_start == -1:
        print("❌ Não encontrou seção de extração de conteúdo")
        return False
    
    # Encontrar o fim da seção (próximo else:)
    extraction_end = content.find("# Debug: Log do conteúdo extraído", extraction_start)
    if extraction_end == -1:
        print("❌ Não encontrou fim da seção de extração")
        return False
    
    # Substituir toda a seção
    new_extraction = '''                    # Extrair conteúdo da resposta - CORREÇÃO DEFINITIVA AGNO RunResponse
                    raw_response = None
                    
                    # 1. Primeiro tentar content (mais comum)
                    if hasattr(result, 'content') and result.content:
                        raw_response = result.content
                        emoji_logger.system_info(f"✅ Conteúdo extraído de result.content")
                    
                    # 2. Se content vazio, verificar messages (AGNO RunResponse padrão)
                    elif hasattr(result, 'messages') and result.messages:
                        emoji_logger.system_info(f"📬 result.content vazio, verificando messages ({len(result.messages)} mensagens)")
                        # Procurar última mensagem do assistant
                        for msg in reversed(result.messages):
                            if hasattr(msg, 'role') and msg.role == 'assistant':
                                if hasattr(msg, 'content') and msg.content:
                                    raw_response = msg.content
                                    emoji_logger.system_info(f"✅ Conteúdo extraído de messages[assistant]")
                                    break
                                elif hasattr(msg, 'text') and msg.text:
                                    raw_response = msg.text
                                    emoji_logger.system_info(f"✅ Conteúdo extraído de messages[assistant].text")
                                    break
                    
                    # 3. Verificar outros atributos comuns
                    if not raw_response:
                        if hasattr(result, 'text') and result.text:
                            raw_response = result.text
                            emoji_logger.system_info(f"✅ Conteúdo extraído de result.text")
                        elif hasattr(result, 'message') and result.message:
                            raw_response = result.message
                            emoji_logger.system_info(f"✅ Conteúdo extraído de result.message")
                        elif hasattr(result, 'reasoning_content') and result.reasoning_content:
                            raw_response = result.reasoning_content
                            emoji_logger.system_info(f"✅ Conteúdo extraído de result.reasoning_content")
                    
                    # 4. Se ainda vazio, tentar dict
                    if not raw_response and isinstance(result, dict):
                        raw_response = result.get('content') or result.get('text') or result.get('message')
                        if raw_response:
                            emoji_logger.system_info(f"✅ Conteúdo extraído de result dict")
                    
                    # 5. Debug completo se ainda vazio
                    if not raw_response:
                        emoji_logger.system_error("Response Extraction", f"Falha total na extração!")
                        emoji_logger.system_error("Response Extraction", f"Tipo: {type(result)}")
                        emoji_logger.system_error("Response Extraction", f"Atributos: {[attr for attr in dir(result) if not attr.startswith('_')]}")
                        if hasattr(result, 'messages') and result.messages:
                            emoji_logger.system_error("Response Extraction", f"Messages[0]: {result.messages[0] if result.messages else 'vazio'}")
                        if hasattr(result, 'status'):
                            emoji_logger.system_error("Response Extraction", f"Status: {result.status}")
                        
                        # Último recurso - converter para string
                        raw_response = str(result)
                    
                    '''
    
    # Inserir a nova extração
    before_extraction = content[:extraction_start]
    after_extraction = content[extraction_end:]
    
    content = before_extraction + new_extraction + after_extraction
    
    # Salvar arquivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Correção aplicada em {file_path}")
    print("\n📋 Mudanças implementadas:")
    print("   1. Verificação completa de result.messages")
    print("   2. Busca por mensagem do assistant")
    print("   3. Debug detalhado se falhar")
    print("   4. Múltiplos fallbacks para extração")
    
    return True

if __name__ == "__main__":
    if fix_runresponse_extraction():
        print("\n🚀 Próximos passos:")
        print("   1. Reinicie o servidor: docker-compose restart")
        print("   2. Teste novamente e verifique logs")
        print("   3. O conteúdo deve ser extraído de result.messages")