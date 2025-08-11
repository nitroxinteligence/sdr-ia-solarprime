"""
KnowledgeService - Serviço Simples para Consultas à Base de Conhecimento
Substitui o KnowledgeAgent com implementação direta e mais simples
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from loguru import logger

from app.integrations.supabase_client import supabase_client
# EmbeddingsManager REMOVIDO - não necessário para busca direta no Supabase


class KnowledgeService:
    """
    Serviço simples para consultas à base de conhecimento
    Foca apenas na funcionalidade essencial sem complexidade de agente
    """
    
    def __init__(self):
        """Inicializa o serviço de conhecimento"""
        # EmbeddingsManager removido - busca direta no Supabase é mais simples
        
        # Configurações simples
        self.similarity_threshold = 0.7
        self.max_results = 5
        
        # Cache simples em memória
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
        
        logger.info("✅ KnowledgeService inicializado (versão simplificada)")
    
    async def search_knowledge_base(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca na base de conhecimento do Supabase
        
        Args:
            query: Termo de busca
            max_results: Máximo de resultados
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            # Verificar cache primeiro
            cache_key = f"search_{query}_{max_results}"
            if self._is_cached(cache_key):
                logger.info(f"📋 Cache hit para query: {query[:30]}...")
                return self._cache[cache_key]['data']
            
            logger.info(f"📚 Carregando TODA a knowledge_base para enriquecer resposta...")
            
            # MUDANÇA: Buscar TUDO da knowledge base, não filtrar
            # O objetivo é ter TODO o conhecimento disponível para o agente
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords, created_at"
            ).limit(20).execute()  # Limitar a 20 para não sobrecarregar
            
            if response.data:
                # Cachear resultado
                self._cache[cache_key] = {
                    'data': response.data,
                    'timestamp': datetime.now().timestamp()
                }
                
                logger.info(f"✅ Encontrados {len(response.data)} documentos")
                return response.data
            else:
                logger.info("ℹ️ Nenhum documento encontrado")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro na busca knowledge_base: {e}")
            return []
    
    async def search_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca documentos por categoria
        
        Args:
            category: Categoria (solutions, pricing, faq, etc)
            limit: Limite de resultados
            
        Returns:
            Lista de documentos da categoria
        """
        try:
            cache_key = f"category_{category}_{limit}"
            if self._is_cached(cache_key):
                return self._cache[cache_key]['data']
            
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords"
            ).eq("category", category).limit(limit).execute()
            
            if response.data:
                self._cache[cache_key] = {
                    'data': response.data,
                    'timestamp': datetime.now().timestamp()
                }
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro na busca por categoria: {e}")
            return []
    
    async def get_solar_solutions_info(self) -> Dict[str, Any]:
        """
        Retorna informações das soluções solares (método específico)
        
        Returns:
            Informações estruturadas das soluções
        """
        try:
            # Buscar soluções específicas
            solutions = await self.search_by_category("solutions", limit=20)
            
            if solutions:
                return {
                    "solutions": solutions,
                    "count": len(solutions),
                    "categories": list(set([sol.get("tags", "").split(",")[0] for sol in solutions if sol.get("tags")]))
                }
            else:
                # Fallback com informações básicas
                return {
                    "solutions": [
                        {
                            "title": "Assinatura Comercial",
                            "content": "20% desconto líquido garantido sobre toda conta, usina fica sua após 6 anos",
                            "category": "commercial"
                        },
                        {
                            "title": "Geração Própria",
                            "content": "Sistema fotovoltaico no local, economia até 90%, garantia 25 anos",
                            "category": "residential"
                        }
                    ],
                    "count": 2,
                    "categories": ["commercial", "residential"]
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar soluções: {e}")
            return {"solutions": [], "count": 0, "categories": []}
    
    async def get_pricing_info(self, solution_type: str = None) -> Dict[str, Any]:
        """
        Busca informações de preços
        
        Args:
            solution_type: Tipo da solução (opcional)
            
        Returns:
            Informações de preços
        """
        try:
            query = "preço OR valor OR custo OR investimento"
            if solution_type:
                query += f" AND {solution_type}"
            
            pricing_docs = await self.search_knowledge_base(query, max_results=10)
            
            return {
                "pricing_documents": pricing_docs,
                "count": len(pricing_docs)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar preços: {e}")
            return {"pricing_documents": [], "count": 0}
    
    async def get_faq_answers(self, question: str) -> List[Dict[str, Any]]:
        """
        Busca respostas em FAQ
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            Lista de respostas de FAQ
        """
        try:
            # Buscar em FAQ
            faq_results = await self.search_by_category("faq")
            
            # Filtrar resultados relevantes
            relevant_faqs = []
            for faq in faq_results:
                if any(word.lower() in faq.get("content", "").lower() for word in question.split()):
                    relevant_faqs.append(faq)
            
            return relevant_faqs[:3]  # Top 3 mais relevantes
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar FAQ: {e}")
            return []
    
    def _is_cached(self, key: str) -> bool:
        """Verifica se um item está cached e não expirou"""
        if key not in self._cache:
            return False
        
        cache_time = self._cache[key]['timestamp']
        current_time = datetime.now().timestamp()
        
        if current_time - cache_time > self._cache_ttl:
            del self._cache[key]
            return False
        
        return True
    
    def clear_cache(self):
        """Limpa o cache"""
        self._cache.clear()
        logger.info("🧹 Cache do KnowledgeService limpo")


# Instância global

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

knowledge_service = KnowledgeService()