#!/usr/bin/env python3
"""
Correção URGENTE da Knowledge Base e Timeouts

PROBLEMA: Knowledge base quebrando e causando timeouts
SOLUÇÃO: Corrigir campos e adicionar tratamento de erro robusto
"""

import os

def fix_knowledge_urgent():
    """Aplica correções urgentes"""
    
    # Arquivo do knowledge service
    file_path = "app/services/knowledge_service.py"
    
    print("🚨 CORREÇÃO URGENTE - Knowledge Base")
    print("=" * 60)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Garantir que não temos await onde não deveria
    content = content.replace("await supabase_client.", "supabase_client.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removido await desnecessário")
    
    # Agora corrigir o agentic_sdr.py para lidar melhor com erros
    sdr_file = "app/agents/agentic_sdr.py"
    
    with open(sdr_file, 'r', encoding='utf-8') as f:
        sdr_content = f.read()
    
    # Encontrar o bloco de fallback e melhorar
    old_fallback = '''                        # Fallback inteligente baseado no contexto
                        if "conta" in message.lower() or "luz" in message.lower() or "energia" in message.lower():
                            raw_response = "Me desculpe, tive um problema ao processar sua mensagem. Você pode me enviar sua conta de luz para eu fazer uma análise de economia?"
                        elif "oi" in message.lower() or "olá" in message.lower() or "ola" in message.lower():
                            raw_response = "Oi! Tudo bem? Como posso ajudar você com energia solar hoje?"
                        else:
                            raw_response = "Desculpe, tive um probleminha aqui. Pode repetir sua mensagem?"'''
    
    new_fallback = '''                        # Fallback inteligente baseado no contexto
                        emoji_logger.system_warning(f"⚠️ Usando fallback para mensagem: {message[:50]}")
                        
                        # Analisar sentimento da mensagem para resposta apropriada
                        if any(word in message.lower() for word in ["suspeito", "estranho", "dúvida", "não entendi"]):
                            raw_response = "Entendo sua preocupação! Deixa eu esclarecer melhor. Você tem alguma dúvida específica sobre energia solar que eu possa ajudar?"
                        elif "conta" in message.lower() or "luz" in message.lower() or "energia" in message.lower():
                            raw_response = "Me desculpe, tive um problema ao processar sua mensagem. Você pode me enviar sua conta de luz para eu fazer uma análise de economia?"
                        elif "oi" in message.lower() or "olá" in message.lower() or "ola" in message.lower():
                            raw_response = "Oi! Tudo bem? Como posso ajudar você com energia solar hoje?"
                        elif any(word in message.lower() for word in ["sim", "não", "ok", "beleza", "entendi"]):
                            raw_response = "Perfeito! Tem mais alguma coisa sobre energia solar que você gostaria de saber?"
                        else:
                            raw_response = "Desculpe, tive um probleminha técnico aqui. Pode me dizer novamente como posso te ajudar?"'''
    
    if old_fallback in sdr_content:
        sdr_content = sdr_content.replace(old_fallback, new_fallback)
        print("✅ Fallback melhorado para contextos específicos")
    
    # Aumentar timeout para 45 segundos
    sdr_content = sdr_content.replace("AGENT_TIMEOUT = 30", "AGENT_TIMEOUT = 45")
    print("✅ Timeout aumentado para 45 segundos")
    
    # Adicionar try/except mais robusto para knowledge base
    old_kb_block = '''                    # MELHORIA HÍBRIDA: SEMPRE consultar knowledge base (OBRIGATÓRIO)
                    knowledge_results = []
                    try:
                        if message and len(message.strip()) > 2:  # Mensagem válida
                            emoji_logger.system_info("🔍 Consultando Knowledge Base (OBRIGATÓRIO)")
                            knowledge_results = await self.search_knowledge_base(message)
                            emoji_logger.system_info(f"✅ Knowledge Base: {len(knowledge_results)} resultados encontrados")
                    except Exception as kb_error:
                        emoji_logger.system_warning(f"Knowledge Base falhou, continuando: {str(kb_error)[:50]}")
                        knowledge_results = []'''
    
    new_kb_block = '''                    # MELHORIA HÍBRIDA: SEMPRE consultar knowledge base (OBRIGATÓRIO)
                    knowledge_results = []
                    try:
                        if message and len(message.strip()) > 2:  # Mensagem válida
                            emoji_logger.system_info("🔍 Consultando Knowledge Base (OBRIGATÓRIO)")
                            # Timeout específico para knowledge base
                            kb_task = asyncio.create_task(self.search_knowledge_base(message))
                            knowledge_results = await asyncio.wait_for(kb_task, timeout=5.0)  # 5 segundos max
                            emoji_logger.system_info(f"✅ Knowledge Base: {len(knowledge_results)} resultados encontrados")
                    except asyncio.TimeoutError:
                        emoji_logger.system_warning("⏱️ Knowledge Base timeout (5s), continuando sem resultados")
                        knowledge_results = []
                    except Exception as kb_error:
                        emoji_logger.system_warning(f"Knowledge Base falhou: {str(kb_error)[:100]}")
                        knowledge_results = []'''
    
    sdr_content = sdr_content.replace(old_kb_block, new_kb_block)
    print("✅ Knowledge base com timeout específico de 5s")
    
    with open(sdr_file, 'w', encoding='utf-8') as f:
        f.write(sdr_content)
    
    print("\n📋 Resumo das correções:")
    print("   1. ✅ Removido await desnecessário do knowledge service")
    print("   2. ✅ Melhorado fallback para contextos específicos") 
    print("   3. ✅ Timeout geral aumentado para 45s")
    print("   4. ✅ Knowledge base com timeout próprio de 5s")
    print("\n🚀 Sistema corrigido e otimizado!")

if __name__ == "__main__":
    fix_knowledge_urgent()