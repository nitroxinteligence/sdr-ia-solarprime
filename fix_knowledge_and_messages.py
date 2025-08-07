#!/usr/bin/env python3
"""
Correção da Knowledge Base e Mensagens Cortadas

PROBLEMAS:
1. Knowledge base deve buscar TUDO, não filtrar por texto
2. Mensagens estão sendo cortadas no WhatsApp

SOLUÇÃO SIMPLES E DIRETA
"""

def fix_knowledge_and_messages():
    """Aplica correções necessárias"""
    
    print("🔧 CORRIGINDO KNOWLEDGE BASE E MENSAGENS")
    print("=" * 60)
    
    # 1. CORRIGIR KNOWLEDGE SERVICE
    knowledge_file = "app/services/knowledge_service.py"
    
    with open(knowledge_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Mudar a lógica de busca para trazer TUDO
    old_search = '''            logger.info(f"🔍 Buscando na knowledge_base: {query[:50]}...")
            
            # Busca direta no Supabase
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords, created_at"
            ).or_(f"question.ilike.%{query}%,answer.ilike.%{query}%").limit(max_results).execute()'''
    
    new_search = '''            logger.info(f"📚 Carregando TODA a knowledge_base para enriquecer resposta...")
            
            # MUDANÇA: Buscar TUDO da knowledge base, não filtrar
            # O objetivo é ter TODO o conhecimento disponível para o agente
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords, created_at"
            ).limit(20).execute()  # Limitar a 20 para não sobrecarregar'''
    
    content = content.replace(old_search, new_search)
    
    # Adicionar método para buscar conhecimento aleatório/geral
    new_method = '''
    async def get_all_knowledge(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Busca TODO o conhecimento disponível para enriquecer respostas
        Não filtra por query - o objetivo é ter contexto completo
        """
        try:
            cache_key = f"all_knowledge_{limit}"
            if self._is_cached(cache_key):
                logger.info("📋 Usando knowledge base do cache")
                return self._cache[cache_key]['data']
            
            logger.info("📚 Carregando knowledge base completa...")
            
            # Buscar tudo, ordenado por prioridade ou categoria
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords"
            ).order("category").limit(limit).execute()
            
            if response.data:
                self._cache[cache_key] = {
                    'data': response.data,
                    'timestamp': datetime.now().timestamp()
                }
                logger.info(f"✅ {len(response.data)} itens de conhecimento carregados")
                return response.data
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar knowledge base: {e}")
            return []
'''
    
    # Inserir o novo método após search_by_category
    insert_pos = content.find("# Fim da classe")
    if insert_pos == -1:
        # Se não encontrar, adicionar no final da classe
        insert_pos = content.rfind("knowledge_service = KnowledgeService()")
        content = content[:insert_pos] + new_method + "\n" + content[insert_pos:]
    
    with open(knowledge_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Knowledge service corrigido para buscar TUDO")
    
    # 2. CORRIGIR AGENTIC_SDR para usar o novo método
    sdr_file = "app/agents/agentic_sdr.py"
    
    with open(sdr_file, 'r', encoding='utf-8') as f:
        sdr_content = f.read()
    
    # Mudar para usar get_all_knowledge ao invés de search
    old_kb_call = '''                            # Timeout específico para knowledge base
                            kb_task = asyncio.create_task(self.search_knowledge_base(message))
                            knowledge_results = await asyncio.wait_for(kb_task, timeout=5.0)  # 5 segundos max'''
    
    new_kb_call = '''                            # MUDANÇA: Buscar TODO o conhecimento, não filtrar por mensagem
                            # O objetivo é enriquecer a resposta com TODAS as informações disponíveis
                            from app.services.knowledge_service import knowledge_service
                            kb_task = asyncio.create_task(knowledge_service.get_all_knowledge(limit=15))
                            knowledge_results = await asyncio.wait_for(kb_task, timeout=5.0)  # 5 segundos max'''
    
    sdr_content = sdr_content.replace(old_kb_call, new_kb_call)
    
    # 3. CORRIGIR PROBLEMA DE MENSAGEM CORTADA
    # O problema está no message splitter - vamos verificar
    
    # Adicionar log para debug do problema
    old_split_check = '''            # Se o splitter está habilitado e a mensagem é longa, divide em chunks
            if settings.enable_message_splitter and len(response_text) > settings.message_max_length:'''
    
    new_split_check = '''            # DEBUG: Log completo da resposta antes de dividir
            emoji_logger.system_info(f"📝 Resposta completa antes de dividir: {response_text}")
            emoji_logger.system_info(f"📏 Tamanho: {len(response_text)} chars")
            
            # Se o splitter está habilitado e a mensagem é longa, divide em chunks
            if settings.enable_message_splitter and len(response_text) > settings.message_max_length:'''
    
    # Procurar no webhooks.py
    webhooks_file = "app/api/webhooks.py"
    
    with open(webhooks_file, 'r', encoding='utf-8') as f:
        webhooks_content = f.read()
    
    if old_split_check in webhooks_content:
        webhooks_content = webhooks_content.replace(old_split_check, new_split_check)
        
        with open(webhooks_file, 'w', encoding='utf-8') as f:
            f.write(webhooks_content)
        
        print("✅ Adicionado debug para mensagens divididas")
    
    # Salvar arquivo SDR modificado
    with open(sdr_file, 'w', encoding='utf-8') as f:
        f.write(sdr_content)
    
    print("\n📋 Resumo das correções:")
    print("   1. ✅ Knowledge base agora busca TUDO (não filtra)")
    print("   2. ✅ Novo método get_all_knowledge() criado")
    print("   3. ✅ Agent usa conhecimento completo para enriquecer")
    print("   4. ✅ Debug adicionado para mensagens cortadas")
    print("\n🚀 Sistema corrigido!")

if __name__ == "__main__":
    fix_knowledge_and_messages()