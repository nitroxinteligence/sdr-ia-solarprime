"""
SolarPrime Knowledge Base (Simplified Version)
==============================================
Versão simplificada que usa apenas Supabase Client (sem conexão direta ao PostgreSQL)
"""

from typing import List, Dict, Any, Optional
from loguru import logger
from services.database import supabase_client
import numpy as np
from datetime import datetime


class SolarPrimeKnowledgeSimple:
    """Knowledge base simplificada usando apenas Supabase Client"""
    
    def __init__(self):
        """Initialize knowledge base"""
        self.initialized = False
        self.knowledge_items = []
        logger.info("SolarPrime Knowledge (Simplified) inicializado")
    
    async def load_from_supabase(self) -> None:
        """Carrega knowledge base do Supabase"""
        try:
            # Buscar todos os itens da knowledge base
            response = supabase_client.table("knowledge_base").select("*").execute()
            
            if response.data:
                self.knowledge_items = response.data
                self.initialized = True
                logger.info(f"Carregados {len(self.knowledge_items)} itens da knowledge base")
            else:
                logger.warning("Nenhum item encontrado na knowledge base")
                self.initialized = False
                
        except Exception as e:
            logger.error(f"Erro ao carregar knowledge base: {e}")
            self.initialized = False
    
    async def get_relevant_knowledge(self, query: str, max_results: int = 3) -> str:
        """
        Busca conhecimento relevante (versão simplificada sem embeddings)
        Usa busca por palavras-chave e categorias
        """
        if not self.initialized:
            return ""
        
        query_lower = query.lower()
        scored_items = []
        
        # Sistema de pontuação simples
        for item in self.knowledge_items:
            score = 0
            
            # Verificar categoria
            category = item.get("category", "").lower()
            if any(word in category for word in query_lower.split()):
                score += 3
            
            # Verificar pergunta
            question = item.get("question", "").lower()
            if any(word in question for word in query_lower.split() if len(word) > 3):
                score += 2
            
            # Verificar keywords
            keywords = item.get("keywords", [])
            if keywords:
                for keyword in keywords:
                    if keyword.lower() in query_lower:
                        score += 2
            
            # Verificar resposta
            answer = item.get("answer", "").lower()
            if any(word in answer for word in query_lower.split() if len(word) > 4):
                score += 1
            
            if score > 0:
                scored_items.append((score, item))
        
        # Ordenar por score e pegar os melhores
        scored_items.sort(key=lambda x: x[0], reverse=True)
        top_items = scored_items[:max_results]
        
        # Formatar resultados
        if not top_items:
            return ""
        
        results = []
        for score, item in top_items:
            results.append(f"**{item['category']}**: {item['answer']}")
        
        return "\n\n".join(results)
    
    async def add_knowledge(self, category: str, question: str, answer: str, keywords: List[str] = None) -> bool:
        """Adiciona novo conhecimento"""
        try:
            data = {
                "category": category,
                "question": question,
                "answer": answer,
                "keywords": keywords or [],
                "metadata": {
                    "source": "manual",
                    "created_by": "system"
                }
            }
            
            response = supabase_client.table("knowledge_base").insert(data).execute()
            
            if response.data:
                # Recarregar knowledge base
                await self.load_from_supabase()
                logger.info(f"Conhecimento adicionado: {category} - {question}")
                return True
            else:
                logger.error("Falha ao adicionar conhecimento")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao adicionar conhecimento: {e}")
            return False
    
    async def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Busca conhecimento por categoria"""
        try:
            response = supabase_client.table("knowledge_base")\
                .select("*")\
                .eq("category", category)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Erro ao buscar por categoria: {e}")
            return []
    
    def get_all_categories(self) -> List[str]:
        """Retorna todas as categorias disponíveis"""
        if not self.initialized:
            return []
        
        categories = set()
        for item in self.knowledge_items:
            if "category" in item:
                categories.add(item["category"])
        
        return sorted(list(categories))
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da knowledge base"""
        if not self.initialized:
            return {
                "total_items": 0,
                "categories": [],
                "initialized": False
            }
        
        categories_count = {}
        for item in self.knowledge_items:
            cat = item.get("category", "Unknown")
            categories_count[cat] = categories_count.get(cat, 0) + 1
        
        return {
            "total_items": len(self.knowledge_items),
            "categories": self.get_all_categories(),
            "categories_count": categories_count,
            "initialized": True,
            "last_loaded": datetime.now().isoformat()
        }


# Teste rápido
if __name__ == "__main__":
    import asyncio
    
    async def test():
        kb = SolarPrimeKnowledgeSimple()
        await kb.load_from_supabase()
        
        # Testar busca
        result = await kb.get_relevant_knowledge("energia solar economia")
        print("Resultado da busca:")
        print(result)
        
        # Estatísticas
        stats = kb.get_stats()
        print("\nEstatísticas:")
        print(f"Total de itens: {stats['total_items']}")
        print(f"Categorias: {', '.join(stats['categories'])}")
    
    asyncio.run(test())