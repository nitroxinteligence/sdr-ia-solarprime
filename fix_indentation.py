#!/usr/bin/env python3
"""
Corrige indentação do código híbrido
"""

import re

def fix_indentation():
    file_path = "app/agents/agentic_sdr.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir a indentação do bloco de knowledge base
    # O problema é que o código foi inserido com indentação errada
    
    # Primeiro, vamos remover a linha problemática
    content = content.replace('''

                # MELHORIA HÍBRIDA: SEMPRE consultar knowledge base (OBRIGATÓRIO)''', '''
                    
                    # MELHORIA HÍBRIDA: SEMPRE consultar knowledge base (OBRIGATÓRIO)''')
    
    # Ajustar a indentação do bloco try
    content = content.replace('''                knowledge_results = []
                try:''', '''                    knowledge_results = []
                    try:''')
    
    # Ajustar indentação das linhas dentro do try
    content = content.replace('''                    if message and len(message.strip()) > 2:  # Mensagem válida
                        emoji_logger.system_info("🔍 Consultando Knowledge Base (OBRIGATÓRIO)")
                        knowledge_results = await self.search_knowledge_base(message)
                        emoji_logger.system_info(f"✅ Knowledge Base: {len(knowledge_results)} resultados encontrados")
                except Exception as kb_error:
                    emoji_logger.system_warning(f"Knowledge Base falhou, continuando: {str(kb_error)[:50]}")
                    knowledge_results = []
                
                # Detectar se é primeiro contato ANTES de construir o prompt
                is_first_contact = self._is_first_contact(messages_history)
                emoji_logger.system_info(f"🎯 Primeiro contato detectado: {is_first_contact}")

                    # Preparar prompt com contexto completo AGNO-enhanced''', '''                        if message and len(message.strip()) > 2:  # Mensagem válida
                            emoji_logger.system_info("🔍 Consultando Knowledge Base (OBRIGATÓRIO)")
                            knowledge_results = await self.search_knowledge_base(message)
                            emoji_logger.system_info(f"✅ Knowledge Base: {len(knowledge_results)} resultados encontrados")
                    except Exception as kb_error:
                        emoji_logger.system_warning(f"Knowledge Base falhou, continuando: {str(kb_error)[:50]}")
                        knowledge_results = []
                    
                    # Detectar se é primeiro contato ANTES de construir o prompt
                    is_first_contact = self._is_first_contact(messages_history)
                    emoji_logger.system_info(f"🎯 Primeiro contato detectado: {is_first_contact}")
                    
                    # Preparar prompt com contexto completo AGNO-enhanced''')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Indentação corrigida!")

if __name__ == "__main__":
    fix_indentation()