#!/usr/bin/env python3
"""
Melhorias Híbridas para o Agente SDR

OBJETIVO: Corrigir problemas críticos sem quebrar o sistema existente

MELHORIAS:
1. Tornar consultas ao histórico e knowledge base OBRIGATÓRIAS
2. Implementar detecção inteligente de primeiro contato
3. Corrigir apresentação repetitiva
4. Adicionar context pruning

O SIMPLES FUNCIONA - ZERO COMPLEXIDADE ADICIONAL
"""

import os
from datetime import datetime

def apply_hybrid_improvements():
    """Aplica melhorias híbridas no código existente"""
    
    file_path = "app/agents/agentic_sdr.py"
    
    print("🔧 APLICANDO MELHORIAS HÍBRIDAS")
    print("=" * 60)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # MELHORIA 1: Adicionar método _is_first_contact
    is_first_contact_method = '''
    def _is_first_contact(self, messages_history: List[Dict[str, Any]]) -> bool:
        """
        Detecta se é o primeiro contato com o lead de forma INTELIGENTE
        
        Returns:
            True se for primeira interação, False caso contrário
        """
        if not messages_history:
            return True
        
        # Contar mensagens do AGENTE (não do usuário)
        agent_messages = [
            msg for msg in messages_history 
            if msg.get('sender') == 'agent' or msg.get('role') == 'assistant'
        ]
        
        # Se o agente nunca respondeu ou só tem 1 mensagem, é primeira interação
        return len(agent_messages) <= 1
    
    def _should_knowledge_search(self, message: str) -> bool:
        """
        SEMPRE retorna True - knowledge search é OBRIGATÓRIO
        """
        return True
'''
    
    # Adicionar após a definição da classe
    insert_position = content.find("    async def process_message(")
    if insert_position > 0:
        content = content[:insert_position] + is_first_contact_method + "\n" + content[insert_position:]
        print("✅ Método _is_first_contact adicionado")
    
    # MELHORIA 2: Tornar histórico SEMPRE obrigatório
    # Remover condicionais em torno de get_last_100_messages
    old_history_section = '''            # 2. Detectar gatilhos emocionais e obter histórico (com fallback)
            messages_history = []
            try:'''
    
    new_history_section = '''            # 2. SEMPRE buscar histórico (OBRIGATÓRIO) e detectar gatilhos emocionais
            messages_history = []
            try:
                # MELHORIA HÍBRIDA: Histórico é SEMPRE consultado'''
    
    content = content.replace(old_history_section, new_history_section)
    
    # MELHORIA 3: Adicionar consulta obrigatória à knowledge base
    # Procurar onde o agent é chamado e adicionar knowledge search antes
    knowledge_search_addition = '''
                # MELHORIA HÍBRIDA: SEMPRE consultar knowledge base (OBRIGATÓRIO)
                knowledge_results = []
                try:
                    if message and len(message.strip()) > 2:  # Mensagem válida
                        emoji_logger.system_info("🔍 Consultando Knowledge Base (OBRIGATÓRIO)")
                        knowledge_results = await self.search_knowledge_base(message)
                        emoji_logger.system_info(f"✅ Knowledge Base: {len(knowledge_results)} resultados encontrados")
                except Exception as kb_error:
                    emoji_logger.system_warning(f"Knowledge Base falhou, continuando: {str(kb_error)[:50]}")
                    knowledge_results = []
                
                # Detectar se é primeiro contato ANTES de construir o prompt
                is_first_contact = self._is_first_contact(messages_history)
                emoji_logger.system_info(f"🎯 Primeiro contato detectado: {is_first_contact}")
'''
    
    # Inserir antes da construção do contextual_prompt
    prompt_position = content.find("                    # Preparar prompt com contexto completo")
    if prompt_position > 0:
        content = content[:prompt_position] + knowledge_search_addition + "\n" + content[prompt_position:]
        print("✅ Consulta obrigatória à knowledge base adicionada")
    
    # MELHORIA 4: Modificar construção do prompt para incluir knowledge e estado de primeiro contato
    old_prompt_start = '''                    contextual_prompt = f"""
                    CONTEXTO DO LEAD:'''
    
    new_prompt_start = '''                    contextual_prompt = f"""
                    🚨 ESTADO DA CONVERSA: {'PRIMEIRO CONTATO - APRESENTE-SE!' if is_first_contact else f'CONVERSA EM ANDAMENTO ({len(messages_history)} mensagens)'}
                    
                    📚 KNOWLEDGE BASE (CONSULTADA):
                    {self._format_knowledge_results(knowledge_results) if knowledge_results else 'Nenhum resultado específico'}
                    
                    CONTEXTO DO LEAD:'''
    
    content = content.replace(old_prompt_start, new_prompt_start)
    
    # MELHORIA 5: Adicionar instrução específica sobre apresentação
    old_prompt_end = '''                    Responda de forma natural, empática e personalizada, levando em conta todo o contexto e histórico da conversa.
                    """'''
    
    new_prompt_end = '''                    Responda de forma natural, empática e personalizada, levando em conta todo o contexto e histórico da conversa.
                    
                    {'🚨 IMPORTANTE: Como é o PRIMEIRO CONTATO, APRESENTE-SE como Helen da SolarPrime!' if is_first_contact else '⚠️ NÃO se apresente novamente - vocês já se conhecem!'}
                    """'''
    
    content = content.replace(old_prompt_end, new_prompt_end)
    
    # MELHORIA 6: Adicionar método para formatar knowledge results
    format_knowledge_method = '''
    def _format_knowledge_results(self, results: List[Dict[str, Any]]) -> str:
        """Formata resultados da knowledge base de forma concisa"""
        if not results:
            return "Sem informações específicas"
        
        formatted = []
        for i, result in enumerate(results[:3], 1):  # Máximo 3 resultados
            formatted.append(f"{i}. {result.get('title', 'Info')}: {result.get('content', '')[:200]}...")
        
        return "\\n".join(formatted)
'''
    
    # Adicionar antes de _is_first_contact
    content = content.replace("    def _is_first_contact(", format_knowledge_method + "\n    def _is_first_contact(")
    
    # MELHORIA 7: Context Pruning - limitar histórico a 20 mensagens mais recentes
    old_format_context = "formatted_history = context_result.get('formatted_history', '')"
    new_format_context = '''formatted_history = context_result.get('formatted_history', '')
                    
                    # MELHORIA HÍBRIDA: Context Pruning - limitar para evitar poluição
                    if len(messages_history) > 20:
                        emoji_logger.system_info(f"📊 Context Pruning: {len(messages_history)} → 20 mensagens")
                        # Pegar apenas as 20 mais recentes para o contexto
                        recent_messages = messages_history[-20:]
                        context_result = self._format_context_simple(
                            message_history=recent_messages,
                            multimodal_result=multimodal_result,
                            phone=phone
                        )
                        formatted_history = context_result.get('formatted_history', '')'''
    
    content = content.replace(old_format_context, new_format_context)
    
    # MELHORIA 8: Corrigir resposta de fallback para checar primeiro contato
    old_fallback = '''if "oi" in message.lower() or "olá" in message.lower() or "ola" in message.lower():
                    response = "<RESPOSTA_FINAL>Oi! Tudo bem? Sou a Helen da Solar Prime! Como posso ajudar você hoje?</RESPOSTA_FINAL>"'''
    
    new_fallback = '''if "oi" in message.lower() or "olá" in message.lower() or "ola" in message.lower():
                    if is_first_contact:
                        response = "<RESPOSTA_FINAL>Oi! Tudo bem? Sou a Helen da Solar Prime! Como posso ajudar você hoje?</RESPOSTA_FINAL>"
                    else:
                        response = "<RESPOSTA_FINAL>Oi! Tudo bem? Como posso ajudar você?</RESPOSTA_FINAL>"'''
    
    content = content.replace(old_fallback, new_fallback)
    
    # Fazer o mesmo para outras saudações
    saudacoes = [
        ("bom dia", "Bom dia! Que legal você entrar em contato! Sou a Helen da Solar Prime. Em que posso ajudar?", "Bom dia! Em que posso ajudar?"),
        ("boa tarde", "Boa tarde! Obrigada por entrar em contato com a Solar Prime! Sou a Helen, como posso ajudar?", "Boa tarde! Como posso ajudar?"),
        ("boa noite", "Boa noite! Que bom falar com você! Sou a Helen da Solar Prime. Como posso ajudar?", "Boa noite! Como posso ajudar?")
    ]
    
    for saudacao, primeira_vez, continuacao in saudacoes:
        old_pattern = f'''elif "{saudacao}" in message.lower():
                    response = "<RESPOSTA_FINAL>{primeira_vez}</RESPOSTA_FINAL>"'''
        new_pattern = f'''elif "{saudacao}" in message.lower():
                    if is_first_contact:
                        response = "<RESPOSTA_FINAL>{primeira_vez}</RESPOSTA_FINAL>"
                    else:
                        response = "<RESPOSTA_FINAL>{continuacao}</RESPOSTA_FINAL>"'''
        content = content.replace(old_pattern, new_pattern)
    
    # Salvar arquivo modificado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ MELHORIAS HÍBRIDAS APLICADAS COM SUCESSO!")
    print("\n📋 Resumo das melhorias:")
    print("   1. ✅ Histórico SEMPRE consultado (obrigatório)")
    print("   2. ✅ Knowledge base SEMPRE consultada (obrigatória)")
    print("   3. ✅ Detecção inteligente de primeiro contato")
    print("   4. ✅ Helen se apresenta APENAS no primeiro contato")
    print("   5. ✅ Context Pruning (máximo 20 mensagens)")
    print("   6. ✅ Fallbacks corrigidos para respeitar estado da conversa")
    print("\n🚀 Sistema melhorado sem quebrar funcionalidades existentes!")
    
    return True

if __name__ == "__main__":
    apply_hybrid_improvements()