"""
Repository para gerenciamento da base de conhecimento (Knowledge Base)
Sistema RAG simples para SolarPrime - SCHEMA CORRETO
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..core.logger import setup_module_logger
from ..services import get_supabase_service
from ..utils.validators import sanitize_input

logger = setup_module_logger(__name__)

# Singleton instance
_knowledge_base_repository_instance = None


class KnowledgeBaseRepository:
    """
    Repository para gerenciamento da base de conhecimento da SolarPrime
    Schema real: id, category, question, answer, keywords, metadata, embedding
    """

    def __init__(self):
        """Inicializa o repository com o serviço Supabase"""
        self.supabase = get_supabase_service()

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
            logger.info(f"Searching knowledge base for: {query[:50]}...")
            
            # Sanitizar query
            sanitized_query = sanitize_input(query, max_length=200)
            
            # Query base com campos corretos
            base_query = self.supabase.client.table("knowledge_base").select(
                "id, category, question, answer, keywords, metadata"
            )
            
            # Filtro de categoria se especificado
            if category:
                base_query = base_query.eq("category", category)
            
            # Busca full-text usando text_search nos campos question,answer
            base_query = base_query.text_search(
                "question,answer", 
                sanitized_query,
                config="portuguese"
            )
            
            # Ordenar por created_at (mais recentes primeiro)
            base_query = base_query.order("created_at", desc=True)
            
            # Limitar resultados
            base_query = base_query.limit(limit)
            
            # Executar query
            result = base_query.execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} knowledge items")
                return result.data
            else:
                logger.info("No knowledge found")
                return []

        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []

    def search_by_keywords(
        self, 
        keywords: List[str],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca conhecimento por keywords específicas
        
        Args:
            keywords: Lista de keywords para buscar
            limit: Número máximo de resultados
            
        Returns:
            Lista de conhecimentos com as keywords
        """
        try:
            logger.info(f"Searching knowledge by keywords: {keywords}")
            
            # Query por keywords usando operador de array
            result = self.supabase.client.table("knowledge_base").select(
                "id, category, question, answer, keywords, metadata"
            ).overlaps("keywords", keywords).order(
                "created_at", desc=True
            ).limit(limit).execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} knowledge items by keywords")
                return result.data
            else:
                logger.info("No knowledge found for specified keywords")
                return []

        except Exception as e:
            logger.error(f"Error searching knowledge by keywords: {str(e)}")
            return []

    def get_by_category(
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
            result = self.supabase.client.table("knowledge_base").select(
                "id, category, question, answer, keywords, metadata"
            ).eq("category", category).order(
                "created_at", desc=True
            ).limit(limit).execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} knowledge items in category: {category}")
                return result.data
            else:
                logger.info(f"No knowledge found in category: {category}")
                return []

        except Exception as e:
            logger.error(f"Error getting knowledge by category: {str(e)}")
            return []

    def get_recent_knowledge(
        self, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtém conhecimentos mais recentes
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de conhecimentos recentes
        """
        try:
            logger.info("Getting recent knowledge")
            
            # Query por data de criação
            result = self.supabase.client.table("knowledge_base").select(
                "id, category, question, answer, keywords, metadata"
            ).order("created_at", desc=True).limit(limit).execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} recent knowledge items")
                return result.data
            else:
                logger.info("No recent knowledge found")
                return []

        except Exception as e:
            logger.error(f"Error getting recent knowledge: {str(e)}")
            return []

    def add_knowledge(
        self,
        category: str,
        question: str,
        answer: str,
        keywords: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Adiciona novo conhecimento à base
        
        Args:
            category: Categoria do conhecimento
            question: Pergunta
            answer: Resposta
            keywords: Keywords (opcional)
            metadata: Metadados adicionais (opcional)
            
        Returns:
            Conhecimento criado ou None se falhou
        """
        try:
            logger.info(f"Adding new knowledge: {question[:50]}...")
            
            # Dados para inserir
            knowledge_data = {
                "id": str(uuid4()),
                "category": sanitize_input(category),
                "question": sanitize_input(question),
                "answer": sanitize_input(answer),
                "keywords": keywords or [],
                "metadata": metadata or {}
            }
            
            # Inserir no Supabase
            result = self.supabase.client.table("knowledge_base").insert(knowledge_data).execute()
            
            if result.data:
                logger.info(f"Knowledge added successfully: {question[:30]}...")
                return result.data[0]
            else:
                logger.error(f"Failed to add knowledge: {question}")
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