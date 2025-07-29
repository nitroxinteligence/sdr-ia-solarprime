"""
SolarPrime Knowledge Base
=========================
Base de conhecimento especializada em energia solar usando AGnO Framework
"""

from typing import List, Dict, Any, Optional
from loguru import logger
from agno.agent import AgentKnowledge
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector
from services.database import supabase_client
import os


class SolarPrimeKnowledge(AgentKnowledge):
    """Knowledge base especializada para SolarPrime"""
    
    def __init__(self):
        """Initialize knowledge base with Supabase backend"""
        # Embedder para gerar embeddings dos textos
        embedder = OpenAIEmbedder(
            id="text-embedding-3-small",
            dimensions=1536
        )
        
        # Configurar conexão com Supabase PostgreSQL
        # Usar connection string direta do banco (não o pooler)
        db_url = os.getenv("SUPABASE_DATABASE_URL")
        
        if not db_url:
            # Fallback para construir a URL se não estiver no .env
            logger.warning("SUPABASE_DATABASE_URL não encontrada no .env")
            supabase_url = os.getenv("SUPABASE_URL", "")
            project_id = supabase_url.split("//")[1].split(".")[0] if supabase_url else ""
            db_url = f"postgresql://postgres:[YOUR-PASSWORD]@db.{project_id}.supabase.co:5432/postgres"
        
        try:
            # Usar PgVector nativo do AGnO
            vector_db = PgVector(
                table_name="knowledge_base",
                db_url=db_url,
                embedder=embedder,
                search_type="hybrid"  # Busca híbrida para melhor resultado
            )
            logger.info("✅ PgVector configurado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível conectar ao PgVector: {e}")
            logger.info("Usando fallback sem busca vetorial")
            
            # Fallback: criar um adapter mínimo
            class MinimalVectorDB:
                def __init__(self):
                    self.embedder = embedder
                    
            vector_db = MinimalVectorDB()
        
        # Inicializar AgentKnowledge
        super().__init__(
            vector_db=vector_db,
            embedder=embedder,
            search_type="mmr",  # Maximum Marginal Relevance para diversidade
            num_documents=3
        )
        
        # Guardar referência ao cliente Supabase como atributo privado
        self._supabase = supabase_client
        
    def load_from_supabase(self) -> None:
        """Carrega conhecimento existente do Supabase"""
        try:
            # Buscar todos os documentos da knowledge_base
            result = self._supabase.table('knowledge_base')\
                .select('*')\
                .execute()
                
            if result.data:
                logger.info(f"Loaded {len(result.data)} knowledge items from Supabase")
                
                # Adicionar ao índice usando load_text
                for item in result.data:
                    # Formatar documento para o AgentKnowledge
                    doc_content = f"Categoria: {item['category']}\nPergunta: {item['question']}\nResposta: {item['answer']}"
                    
                    # Usar load_text do AGnO
                    self.load_text(doc_content)
                    
        except Exception as e:
            logger.error(f"Error loading knowledge from Supabase: {e}")
            
    def search_by_keywords_sync(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Busca conhecimento por palavras-chave (síncrono)"""
        try:
            result = self._supabase.rpc(
                'search_knowledge_by_keywords',
                {'search_keywords': keywords}
            ).execute()
            
            # Remove match_count da resposta (usado apenas para ordenação)
            if result.data:
                for item in result.data:
                    item.pop('match_count', None)
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error searching by keywords: {e}")
            return []
            
            
            
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Formata resultados da busca para uso pelo agente"""
        if not results:
            return "Nenhuma informação encontrada na base de conhecimento."
            
        formatted = []
        for i, result in enumerate(results, 1):
            if 'question' in result and 'answer' in result:
                formatted.append(f"{i}. P: {result['question']}\n   R: {result['answer']}")
            else:
                # Para resultados do AgentKnowledge search
                content = result.get('content', '')
                formatted.append(f"{i}. {content}")
                
        return "\n\n".join(formatted)
        
    def get_relevant_knowledge(self, query: str, max_results: int = 3) -> str:
        """Busca e formata conhecimento relevante para uma consulta"""
        try:
            # Usar o método search do AGnO (que já lida com embeddings)
            results = self.search(query, num_documents=max_results)
            
            # Se não encontrar resultados suficientes com busca semântica,
            # complementar com busca por keywords
            if len(results) < max_results:
                # Extrair palavras-chave da query
                keywords = [word.lower() for word in query.split() if len(word) > 3]
                
                if keywords:
                    keyword_results = self.search_by_keywords_sync(keywords)
                    
                    # Adicionar resultados únicos
                    existing_contents = {r.get('content', '') for r in results}
                    for kr in keyword_results[:max_results - len(results)]:
                        content = f"Categoria: {kr['category']}\nPergunta: {kr['question']}\nResposta: {kr['answer']}"
                        if content not in existing_contents:
                            results.append({
                                'content': content,
                                'metadata': {'id': kr['id'], 'category': kr['category']}
                            })
            
            return self.format_search_results(results)
            
        except Exception as e:
            logger.error(f"Error getting relevant knowledge: {e}")
            # Fallback para busca por keywords se houver erro
            try:
                keywords = [word.lower() for word in query.split() if len(word) > 3]
                if keywords:
                    keyword_results = self.search_by_keywords_sync(keywords)[:max_results]
                    formatted_results = []
                    for kr in keyword_results:
                        formatted_results.append({
                            'content': f"Categoria: {kr['category']}\nPergunta: {kr['question']}\nResposta: {kr['answer']}",
                            'metadata': {'id': kr['id'], 'category': kr['category']}
                        })
                    return self.format_search_results(formatted_results)
            except:
                pass
            
            return "Erro ao buscar informações na base de conhecimento."