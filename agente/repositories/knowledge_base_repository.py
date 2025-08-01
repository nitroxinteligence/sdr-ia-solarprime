"""
Repository para gerenciamento da base de conhecimento (Knowledge Base)
Sistema RAG simples para SolarPrime
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime

from ..core.logger import setup_module_logger
from ..services import get_supabase_service
from ..utils.validators import sanitize_input

logger = setup_module_logger(__name__)

# Singleton instance
_knowledge_base_repository_instance = None


class KnowledgeBaseRepository:
    """
    Repository para gerenciamento da base de conhecimento da SolarPrime
    Sistema RAG simples e eficiente
    """

    def __init__(self):
        """Inicializa o repository com o serviço Supabase"""
        self.supabase = get_supabase_service()
        self._cache = {}  # Cache simples para consultas frequentes
        self._cache_ttl = 300  # 5 minutos

    async def search_knowledge(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca conhecimento relevante baseado na query
        
        Args:
            query: Termo de busca
            category: Categoria específica (opcional)
            limit: Número máximo de resultados
            
        Returns:
            Lista de conhecimentos relevantes
        """
        try:
            # Cache key
            cache_key = f"search_{query}_{category}_{limit}"
            
            # Verificar cache
            if cache_key in self._cache:
                cached_time, cached_data = self._cache[cache_key]
                if (datetime.now() - cached_time).seconds < self._cache_ttl:
                    logger.debug(f"Knowledge cache hit for: {query[:20]}...")
                    return cached_data

            logger.info(f"Searching knowledge base for: {query[:50]}...")
            
            # Sanitizar query
            query = sanitize_input(query)
            
            # Construir query PostgreSQL com full-text search
            select_query = """
                id, title, content, category, tags, priority,
                ts_rank(to_tsvector('portuguese', title || ' ' || content), plainto_tsquery('portuguese', %s)) as relevance
            """
            
            # Base da query - usar client.table() não supabase.table()
            base_query = self.supabase.client.table("knowledge_base").select(select_query)
            
            # Adicionar filtros
            if category:
                base_query = base_query.eq("category", category)
            
            # Filtrar apenas registros ativos
            base_query = base_query.eq("is_active", True)
            
            # Busca full-text
            base_query = base_query.textSearch("title,content", query, type="websearch", config="portuguese")
            
            # Ordenar por relevância e prioridade
            base_query = base_query.order("relevance", desc=True).order("priority", desc=True)
            
            # Limitar resultados
            base_query = base_query.limit(limit)
            
            # Executar query
            result = await base_query.execute()
            
            if result.data:
                # Processar resultados
                knowledge_items = []
                for item in result.data:
                    knowledge_items.append({
                        "id": item["id"],
                        "title": item["title"],
                        "content": item["content"],
                        "category": item["category"],
                        "tags": item.get("tags", []),
                        "priority": item.get("priority", 1),
                        "relevance": item.get("relevance", 0)
                    })
                
                # Atualizar cache
                self._cache[cache_key] = (datetime.now(), knowledge_items)
                
                logger.info(f"Found {len(knowledge_items)} knowledge items for: {query[:20]}...")
                return knowledge_items
            else:
                logger.info(f"No knowledge found for: {query[:20]}...")
                return []

        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []

    async def search_by_tags(
        self, 
        tags: List[str],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca conhecimento por tags específicas
        
        Args:
            tags: Lista de tags para buscar
            limit: Número máximo de resultados
            
        Returns:
            Lista de conhecimentos com as tags
        """
        try:
            logger.info(f"Searching knowledge by tags: {tags}")
            
            # Query por tags usando operador de array
            base_query = self.supabase.client.table("knowledge_base").select(
                "id, title, content, category, tags, priority"
            )
            
            # Filtrar por tags (qualquer tag da lista)
            base_query = base_query.filter("tags", "cs", f"{{{','.join(tags)}}}")
            
            # Filtrar apenas registros ativos
            base_query = base_query.eq("is_active", True)
            
            # Ordenar por prioridade
            base_query = base_query.order("priority", desc=True).order("created_at", desc=True)
            
            # Limitar resultados
            base_query = base_query.limit(limit)
            
            # Executar query
            result = await base_query.execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} knowledge items by tags")
                return result.data
            else:
                logger.info("No knowledge found for specified tags")
                return []

        except Exception as e:
            logger.error(f"Error searching knowledge by tags: {str(e)}")
            return []

    async def get_by_category(
        self, 
        category: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtém conhecimentos por categoria
        
        Args:
            category: Categoria desejada
            limit: Número máximo de resultados
            
        Returns:
            Lista de conhecimentos da categoria
        """
        try:
            logger.info(f"Getting knowledge by category: {category}")
            
            # Query por categoria
            result = await self.supabase.client.table("knowledge_base").select(
                "id, title, content, category, tags, priority"
            ).eq("category", category).eq("is_active", True).order(
                "priority", desc=True
            ).order("created_at", desc=True).limit(limit).execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} knowledge items in category: {category}")
                return result.data
            else:
                logger.info(f"No knowledge found in category: {category}")
                return []

        except Exception as e:
            logger.error(f"Error getting knowledge by category: {str(e)}")
            return []

    async def get_high_priority_knowledge(
        self, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtém conhecimentos de alta prioridade
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de conhecimentos prioritários
        """
        try:
            logger.info("Getting high priority knowledge")
            
            # Query por prioridade alta (>= 7)
            result = await self.supabase.client.table("knowledge_base").select(
                "id, title, content, category, tags, priority"
            ).gte("priority", 7).eq("is_active", True).order(
                "priority", desc=True
            ).order("created_at", desc=True).limit(limit).execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} high priority knowledge items")
                return result.data
            else:
                logger.info("No high priority knowledge found")
                return []

        except Exception as e:
            logger.error(f"Error getting high priority knowledge: {str(e)}")
            return []

    def clear_cache(self):
        """Limpa o cache de conhecimento"""
        self._cache.clear()
        logger.info("Knowledge base cache cleared")

    async def add_knowledge(
        self,
        title: str,
        content: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Adiciona novo conhecimento à base
        
        Args:
            title: Título do conhecimento
            content: Conteúdo
            category: Categoria (opcional)
            tags: Tags (opcional)
            priority: Prioridade (1-10)
            
        Returns:
            Conhecimento criado ou None se falhou
        """
        try:
            logger.info(f"Adding new knowledge: {title[:50]}...")
            
            # Dados para inserir
            knowledge_data = {
                "id": str(uuid4()),
                "title": sanitize_input(title),
                "content": sanitize_input(content),
                "category": category,
                "tags": tags or [],
                "priority": max(1, min(10, priority)),  # Garantir entre 1-10
                "is_active": True
            }
            
            # Inserir no Supabase
            result = await self.supabase.client.table("knowledge_base").insert(knowledge_data).execute()
            
            if result.data:
                # Limpar cache
                self.clear_cache()
                
                logger.info(f"Knowledge added successfully: {title[:30]}...")
                return result.data[0]
            else:
                logger.error(f"Failed to add knowledge: {title}")
                return None

        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            return None


def get_knowledge_base_repository() -> KnowledgeBaseRepository:
    """
    Retorna instância singleton do Knowledge Base Repository
    
    Returns:
        Instância do repository
    """
    global _knowledge_base_repository_instance
    if _knowledge_base_repository_instance is None:
        _knowledge_base_repository_instance = KnowledgeBaseRepository()
        logger.info("KnowledgeBaseRepository singleton created")
    return _knowledge_base_repository_instance