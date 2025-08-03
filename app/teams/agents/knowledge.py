"""
KnowledgeAgent - Agente Especializado em Gestão de Conhecimento e RAG
Responsável por busca vetorial, gestão de documentos e respostas baseadas em conhecimento
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import hashlib

from agno import Agent
from agno.tools import tool
from agno.knowledge import KnowledgeBase
from loguru import logger

from app.integrations.supabase_client import supabase_client
from app.services.embeddings_manager import EmbeddingsManager


class DocumentType(Enum):
    """Tipos de documentos"""
    PRODUCT_INFO = "product_info"           # Informações de produto
    PRICING = "pricing"                      # Preços e planos
    FAQ = "faq"                              # Perguntas frequentes
    TECHNICAL = "technical"                  # Especificações técnicas
    TESTIMONIAL = "testimonial"              # Depoimentos de clientes
    CASE_STUDY = "case_study"                # Casos de sucesso
    LEGAL = "legal"                          # Termos e contratos
    TRAINING = "training"                    # Material de treinamento


class KnowledgeAgent:
    """
    Agente especializado em gestão de conhecimento
    Implementa RAG (Retrieval-Augmented Generation) para respostas precisas
    """
    
    def __init__(self, model, storage):
        """
        Inicializa o agente de conhecimento
        
        Args:
            model: Modelo LLM a ser usado
            storage: Storage para persistência
        """
        self.model = model
        self.storage = storage
        
        # Gerenciador de embeddings
        self.embeddings_manager = EmbeddingsManager()
        
        # Knowledge base do AGnO
        self.knowledge_base = KnowledgeBase(
            store=storage,
            embedder=self.embeddings_manager.get_embedder()
        )
        
        # Configurações de RAG
        self.rag_config = {
            "chunk_size": 500,           # Tamanho dos chunks de texto
            "chunk_overlap": 50,          # Sobreposição entre chunks
            "similarity_threshold": 0.7,  # Threshold de similaridade
            "max_results": 50,             # Máximo de resultados por busca
            "rerank_results": True        # Se deve reranquear resultados
        }
        
        # Cache de documentos
        self.document_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Tools do agente
        self.tools = [
            self.search_knowledge,
            self.add_document,
            self.update_document,
            self.get_document_by_id,
            self.search_similar_questions,
            self.extract_key_facts,
            self.generate_answer_with_sources,
            self.manage_knowledge_categories
        ]
        
        # Criar o agente
        self.agent = Agent(
            name="Knowledge Specialist",
            model=self.model,
            role="""Você é um especialista em gestão de conhecimento e RAG.
            
            Suas responsabilidades:
            1. Buscar informações relevantes na base de conhecimento
            2. Fornecer respostas precisas baseadas em documentos
            3. Gerenciar e organizar a base de conhecimento
            4. Identificar gaps de conhecimento
            5. Garantir accuracy e relevância das respostas
            
            Princípios RAG:
            - Sempre cite as fontes das informações
            - Priorize informações mais recentes
            - Combine múltiplas fontes quando necessário
            - Identifique quando não há informação suficiente
            - Mantenha contexto e coerência nas respostas
            
            Especialidades:
            - Energia solar e sustentabilidade
            - Produtos e serviços Solar Prime
            - Legislação e incentivos fiscais
            - Casos de sucesso e economia""",
            
            tools=self.tools,
            instructions=[
                "Busque sempre nas fontes mais relevantes",
                "Combine informações de múltiplos documentos",
                "Cite as fontes utilizadas",
                "Identifique informações desatualizadas",
                "Sugira atualizações quando necessário",
                "Mantenha um tom educativo e informativo"
            ]
        )
        
        logger.info("✅ KnowledgeAgent inicializado")
    
    async def load_knowledge_base(self):
        """Carrega base de conhecimento do Supabase"""
        try:
            # Buscar documentos do banco
            documents = await supabase_client.client.table("knowledge_base")\
                .select("*")\
                .eq("is_active", True)\
                .execute()
            
            if documents.data:
                for doc in documents.data:
                    # Adicionar ao knowledge base
                    await self.knowledge_base.add_document(
                        content=doc["content"],
                        metadata={
                            "id": doc["id"],
                            "title": doc["title"],
                            "category": doc["category"],
                            "source": doc.get("source"),
                            "created_at": doc["created_at"],
                            "tags": doc.get("tags", [])
                        }
                    )
                
                logger.info(f"📚 Carregados {len(documents.data)} documentos na base de conhecimento")
            
            # Carregar embeddings se existirem
            await self.embeddings_manager.load_embeddings()
            
        except Exception as e:
            logger.error(f"Erro ao carregar knowledge base: {e}")
    
    @tool
    async def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Busca informações na base de conhecimento
        
        Args:
            query: Consulta de busca
            category: Categoria específica (opcional)
            limit: Número máximo de resultados
            include_metadata: Se deve incluir metadados
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            # Verificar cache
            cache_key = f"{query}_{category}_{limit}"
            if cache_key in self.document_cache:
                cached = self.document_cache[cache_key]
                if (datetime.now() - cached["timestamp"]).seconds < self.cache_ttl:
                    logger.info("📋 Resultado do cache")
                    return cached["results"]
            
            # Busca vetorial
            results = await self.knowledge_base.search(
                query=query,
                limit=limit,
                filter_metadata={"category": category} if category else None
            )
            
            # Formatar resultados
            formatted_results = []
            for result in results:
                doc = {
                    "content": result.content[:500],  # Limitar tamanho
                    "score": result.score,
                    "id": result.id
                }
                
                if include_metadata and result.metadata:
                    doc["metadata"] = {
                        "title": result.metadata.get("title"),
                        "category": result.metadata.get("category"),
                        "source": result.metadata.get("source"),
                        "tags": result.metadata.get("tags", [])
                    }
                
                formatted_results.append(doc)
            
            # Reranquear se configurado
            if self.rag_config["rerank_results"] and len(formatted_results) > 1:
                formatted_results = await self._rerank_results(
                    query, formatted_results
                )
            
            # Atualizar cache
            self.document_cache[cache_key] = {
                "results": formatted_results,
                "timestamp": datetime.now()
            }
            
            logger.info(f"🔍 Encontrados {len(formatted_results)} documentos para: {query}")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    @tool
    async def add_document(
        self,
        title: str,
        content: str,
        category: str,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Adiciona novo documento à base de conhecimento
        
        Args:
            title: Título do documento
            content: Conteúdo do documento
            category: Categoria do documento
            source: Fonte do documento (opcional)
            tags: Tags relacionadas (opcional)
            
        Returns:
            Status da operação
        """
        try:
            # Gerar hash único para evitar duplicatas
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Verificar se já existe
            existing = await supabase_client.client.table("knowledge_base")\
                .select("id")\
                .eq("content_hash", content_hash)\
                .execute()
            
            if existing.data:
                return {
                    "success": False,
                    "error": "Documento já existe",
                    "existing_id": existing.data[0]["id"]
                }
            
            # Preparar documento
            doc_data = {
                "title": title,
                "content": content,
                "category": category,
                "source": source or "manual_upload",
                "tags": tags or [],
                "content_hash": content_hash,
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            
            # Salvar no banco
            result = await supabase_client.client.table("knowledge_base")\
                .insert(doc_data)\
                .execute()
            
            if result.data:
                doc_id = result.data[0]["id"]
                
                # Adicionar ao knowledge base
                await self.knowledge_base.add_document(
                    content=content,
                    metadata={
                        "id": doc_id,
                        "title": title,
                        "category": category,
                        "source": source,
                        "tags": tags
                    }
                )
                
                # Gerar embeddings
                chunks = self._chunk_text(content)
                for i, chunk in enumerate(chunks):
                    embedding = await self.embeddings_manager.create_embedding(chunk)
                    
                    # Salvar embedding
                    await supabase_client.client.table("embeddings").insert({
                        "document_id": doc_id,
                        "chunk_index": i,
                        "chunk_text": chunk,
                        "embedding": embedding.tolist(),
                        "metadata": {
                            "title": title,
                            "category": category
                        }
                    }).execute()
                
                logger.info(f"✅ Documento adicionado: {title}")
                
                return {
                    "success": True,
                    "document_id": doc_id,
                    "chunks_created": len(chunks),
                    "message": f"Documento '{title}' adicionado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao salvar documento"
                }
                
        except Exception as e:
            logger.error(f"Erro ao adicionar documento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def update_document(
        self,
        document_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza documento existente
        
        Args:
            document_id: ID do documento
            updates: Campos a atualizar
            
        Returns:
            Status da atualização
        """
        try:
            # Atualizar no banco
            result = await supabase_client.client.table("knowledge_base")\
                .update({
                    **updates,
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("id", document_id)\
                .execute()
            
            if result.data:
                # Se o conteúdo foi atualizado, regenerar embeddings
                if "content" in updates:
                    # Deletar embeddings antigas
                    await supabase_client.client.table("embeddings")\
                        .delete()\
                        .eq("document_id", document_id)\
                        .execute()
                    
                    # Gerar novas embeddings
                    chunks = self._chunk_text(updates["content"])
                    for i, chunk in enumerate(chunks):
                        embedding = await self.embeddings_manager.create_embedding(chunk)
                        
                        await supabase_client.client.table("embeddings").insert({
                            "document_id": document_id,
                            "chunk_index": i,
                            "chunk_text": chunk,
                            "embedding": embedding.tolist()
                        }).execute()
                
                # Limpar cache
                self.document_cache.clear()
                
                logger.info(f"📝 Documento {document_id} atualizado")
                
                return {
                    "success": True,
                    "document_id": document_id,
                    "message": "Documento atualizado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": "Documento não encontrado"
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar documento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def get_document_by_id(
        self,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca documento por ID
        
        Args:
            document_id: ID do documento
            
        Returns:
            Documento completo ou None
        """
        try:
            result = await supabase_client.client.table("knowledge_base")\
                .select("*")\
                .eq("id", document_id)\
                .single()\
                .execute()
            
            if result.data:
                return result.data
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar documento: {e}")
            return None
    
    @tool
    async def search_similar_questions(
        self,
        question: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Busca perguntas similares já respondidas
        
        Args:
            question: Pergunta do usuário
            limit: Número de resultados
            
        Returns:
            Lista de perguntas similares com respostas
        """
        try:
            # Buscar em FAQs
            faq_results = await self.search_knowledge(
                query=question,
                category="faq",
                limit=limit
            )
            
            # Buscar em histórico de conversas
            # TODO: Implementar busca no histórico
            
            similar_questions = []
            for result in faq_results:
                # Extrair pergunta e resposta
                content = result["content"]
                if "?" in content:
                    parts = content.split("?", 1)
                    q = parts[0] + "?"
                    a = parts[1].strip() if len(parts) > 1 else ""
                    
                    similar_questions.append({
                        "question": q,
                        "answer": a,
                        "similarity": result["score"]
                    })
            
            return similar_questions
            
        except Exception as e:
            logger.error(f"Erro ao buscar perguntas similares: {e}")
            return []
    
    @tool
    async def extract_key_facts(
        self,
        topic: str,
        max_facts: int = 5
    ) -> List[str]:
        """
        Extrai fatos-chave sobre um tópico
        
        Args:
            topic: Tópico de interesse
            max_facts: Número máximo de fatos
            
        Returns:
            Lista de fatos importantes
        """
        try:
            # Buscar documentos relevantes
            documents = await self.search_knowledge(
                query=topic,
                limit=10
            )
            
            if not documents:
                return []
            
            # Combinar conteúdo
            combined_content = "\n".join([d["content"] for d in documents])
            
            # Usar LLM para extrair fatos
            prompt = f"""
            Extraia os {max_facts} fatos mais importantes sobre {topic} do texto abaixo.
            Retorne apenas os fatos, um por linha, sem numeração.
            
            Texto:
            {combined_content[:2000]}
            """
            
            response = await self.model.generate(prompt)
            
            # Parse dos fatos
            facts = [
                fact.strip() 
                for fact in response.split("\n") 
                if fact.strip()
            ][:max_facts]
            
            return facts
            
        except Exception as e:
            logger.error(f"Erro ao extrair fatos: {e}")
            return []
    
    @tool
    async def generate_answer_with_sources(
        self,
        question: str,
        include_sources: bool = True,
        max_sources: int = 3
    ) -> Dict[str, Any]:
        """
        Gera resposta com citação de fontes
        
        Args:
            question: Pergunta do usuário
            include_sources: Se deve incluir fontes
            max_sources: Número máximo de fontes
            
        Returns:
            Resposta com fontes citadas
        """
        try:
            # Buscar documentos relevantes
            documents = await self.search_knowledge(
                query=question,
                limit=max_sources * 2  # Buscar mais para ter opções
            )
            
            if not documents:
                return {
                    "answer": "Desculpe, não encontrei informações sobre isso na base de conhecimento.",
                    "sources": [],
                    "confidence": "low"
                }
            
            # Selecionar melhores fontes
            top_docs = documents[:max_sources]
            
            # Preparar contexto
            context = "\n\n---\n\n".join([
                f"Fonte {i+1}: {doc['content']}"
                for i, doc in enumerate(top_docs)
            ])
            
            # Gerar resposta
            prompt = f"""
            Baseado nas fontes abaixo, responda a pergunta de forma completa e precisa.
            Se incluir informações de uma fonte específica, mencione [Fonte X].
            
            Pergunta: {question}
            
            Contexto:
            {context}
            
            Resposta:
            """
            
            response = await self.model.generate(prompt)
            
            # Determinar confiança
            avg_score = sum(d["score"] for d in top_docs) / len(top_docs)
            confidence = "high" if avg_score > 0.8 else "medium" if avg_score > 0.6 else "low"
            
            result = {
                "answer": response,
                "confidence": confidence
            }
            
            if include_sources:
                result["sources"] = [
                    {
                        "title": doc.get("metadata", {}).get("title", "Sem título"),
                        "category": doc.get("metadata", {}).get("category", "geral"),
                        "relevance": doc["score"]
                    }
                    for doc in top_docs
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return {
                "answer": "Erro ao processar sua pergunta.",
                "sources": [],
                "confidence": "low",
                "error": str(e)
            }
    
    @tool
    async def manage_knowledge_categories(
        self,
        action: str,  # list/add/remove/rename
        category_name: Optional[str] = None,
        new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gerencia categorias da base de conhecimento
        
        Args:
            action: Ação a executar
            category_name: Nome da categoria
            new_name: Novo nome (para rename)
            
        Returns:
            Resultado da operação
        """
        try:
            if action == "list":
                # Listar categorias únicas
                result = await supabase_client.client.table("knowledge_base")\
                    .select("category")\
                    .execute()
                
                categories = list(set([
                    doc["category"] 
                    for doc in result.data 
                    if doc["category"]
                ]))
                
                return {
                    "success": True,
                    "categories": sorted(categories),
                    "count": len(categories)
                }
            
            elif action == "add":
                # Categoria é criada automaticamente ao adicionar documento
                return {
                    "success": True,
                    "message": f"Categoria '{category_name}' será criada ao adicionar documentos"
                }
            
            elif action == "rename":
                if not category_name or not new_name:
                    return {
                        "success": False,
                        "error": "Nome atual e novo são obrigatórios"
                    }
                
                # Renomear categoria
                result = await supabase_client.client.table("knowledge_base")\
                    .update({"category": new_name})\
                    .eq("category", category_name)\
                    .execute()
                
                count = len(result.data) if result.data else 0
                
                return {
                    "success": True,
                    "message": f"{count} documentos atualizados",
                    "old_name": category_name,
                    "new_name": new_name
                }
            
            elif action == "remove":
                # Desativar documentos da categoria
                result = await supabase_client.client.table("knowledge_base")\
                    .update({"is_active": False})\
                    .eq("category", category_name)\
                    .execute()
                
                count = len(result.data) if result.data else 0
                
                return {
                    "success": True,
                    "message": f"{count} documentos desativados",
                    "category": category_name
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Ação '{action}' não reconhecida"
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerenciar categorias: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Métodos auxiliares privados
    
    def _chunk_text(self, text: str) -> List[str]:
        """Divide texto em chunks para embeddings"""
        chunks = []
        words = text.split()
        
        chunk_size = self.rag_config["chunk_size"]
        overlap = self.rag_config["chunk_overlap"]
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Reranqueia resultados para melhor relevância"""
        try:
            # Implementação simples de reranking
            # Em produção, usar modelo específico de reranking
            
            for result in results:
                # Boost para matches exatos
                if query.lower() in result["content"].lower():
                    result["score"] *= 1.2
                
                # Boost para categoria relevante
                if result.get("metadata", {}).get("category") == "faq":
                    result["score"] *= 1.1
            
            # Reordenar por score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no reranking: {e}")
            return results