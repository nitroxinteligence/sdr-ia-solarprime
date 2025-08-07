#!/usr/bin/env python3
"""
Teste da correção do Knowledge Service

PROBLEMA: 'SupabaseClient' object has no attribute 'supabase'
SOLUÇÃO: Usar 'client' ao invés de 'supabase'
"""

import asyncio
from app.services.knowledge_service import knowledge_service
from app.utils.logger import emoji_logger

async def test_knowledge_search():
    """Testa busca na knowledge base"""
    print("\n🧪 TESTANDO CORREÇÃO DO KNOWLEDGE SERVICE")
    print("=" * 60)
    
    # Teste 1: Busca simples
    print("\n📝 Teste 1: Busca por 'energia solar'")
    try:
        results = await knowledge_service.search_knowledge_base("energia solar", max_results=3)
        print(f"✅ Busca funcionou! {len(results)} resultados encontrados")
        for i, result in enumerate(results, 1):
            print(f"   {i}. Q: {result.get('question', 'Sem pergunta')[:50]}...")
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
    
    # Teste 2: Busca por categoria
    print("\n📝 Teste 2: Busca por categoria 'solutions'")
    try:
        results = await knowledge_service.search_by_category("solutions", limit=3)
        print(f"✅ Busca por categoria funcionou! {len(results)} resultados")
    except Exception as e:
        print(f"❌ Erro na busca por categoria: {e}")
    
    # Teste 3: Busca vazia
    print("\n📝 Teste 3: Busca com termo sem resultados")
    try:
        results = await knowledge_service.search_knowledge_base("xyzabc123", max_results=3)
        print(f"✅ Busca vazia funcionou! {len(results)} resultados (esperado: 0)")
    except Exception as e:
        print(f"❌ Erro na busca vazia: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_knowledge_search())