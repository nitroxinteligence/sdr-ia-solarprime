"""
AGENTIC SDR - Agente Principal Conversacional Ultra-Humanizado
Com análise contextual inteligente das últimas 100 mensagens
"""

import asyncio
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import base64

from agno import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAI
from agno.memory import Memory
from agno.storage.postgres import PostgresStorage
from agno.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.tools import tool
from loguru import logger
from app.utils.logger import emoji_logger

from app.config import settings
from app.integrations.supabase_client import supabase_client
from app.teams.sdr_team import SDRTeam


class ConversationContext(Enum):
    """Contextos de conversa detectados"""
    INITIAL_CONTACT = "initial_contact"
    QUALIFICATION_NEEDED = "qualification_needed"
    HIGH_VALUE_LEAD = "high_value_lead"
    SCHEDULING_READY = "scheduling_ready"
    OBJECTION_HANDLING = "objection_handling"
    TECHNICAL_QUESTIONS = "technical_questions"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    COMPLEX_NEGOTIATION = "complex_negotiation"
    DOCUMENT_ANALYSIS = "document_analysis"
    CRM_UPDATE_NEEDED = "crm_update_needed"


class EmotionalState(Enum):
    """Estados emocionais do AGENTIC SDR"""
    ENTUSIASMADA = "entusiasmada"
    EMPATICA = "empatica"
    CANSADA = "cansada"
    DETERMINADA = "determinada"
    FRUSTRADA_SUTIL = "frustrada_sutil"
    CURIOSA = "curiosa"
    SATISFEITA = "satisfeita"


class AgenticSDR:
    """
    Agente Principal AGENTIC SDR Ultra-Humanizado
    
    Características:
    - Análise contextual inteligente das últimas 100 mensagens
    - Personalidade ultra-humanizada com estados emocionais
    - Multimodal (imagens, áudio, documentos)
    - Reasoning para casos complexos
    - Memory persistente com pgvector
    - Decision engine inteligente para SDR Team
    """
    
    def __init__(self):
        """Inicializa o AGENTIC SDR com todas as capacidades"""
        self.is_initialized = False
        
        # Configurações de funcionalidades baseadas no .env
        self.context_analysis_enabled = settings.enable_context_analysis
        self.reasoning_enabled = settings.agno_reasoning_enabled
        self.multimodal_enabled = settings.enable_multimodal_analysis
        self.knowledge_search_enabled = settings.enable_knowledge_base
        self.sentiment_analysis_enabled = settings.enable_sentiment_analysis
        self.emotional_triggers_enabled = settings.enable_emotional_triggers
        self.lead_scoring_enabled = settings.enable_lead_scoring
        self.emoji_usage_enabled = settings.enable_emoji_usage
        
        # Estado emocional e cognitivo
        self.emotional_state = EmotionalState.ENTUSIASMADA
        self.cognitive_load = 0.0
        self.conversations_today = 0
        self.last_break_time = datetime.now()
        
        # Configuração do PostgreSQL/Supabase para storage
        postgres_config = {
            "db_url": settings.get_postgres_url(),
            "service_key": settings.supabase_service_key
        }
        
        # Storage persistente
        self.storage = PostgresStorage(**postgres_config)
        
        # Memory v2 com multi-usuário e persistência
        self.memory = Memory(
            store=self.storage,
            create_user_memories=True,
            create_session_summary=True,
            add_datetime_to_messages=True
        )
        
        # PgVector para embeddings e busca semântica
        self.vector_db = PgVector(
            db_url=settings.get_postgres_url(),
            collection="agentic_knowledge",
            embedder={"provider": "openai", "model": "text-embedding-3-small"}
        )
        
        # Knowledge base com RAG
        self.knowledge = Knowledge(
            vector_db=self.vector_db,
            search_type="hybrid",  # Busca híbrida (semântica + keyword)
            num_documents=10,
            rerank=True,
            reranker={"provider": "cohere", "model": "rerank-v3.5"}
        )
        
        # Configurar modelo principal com fallback
        self._setup_models()
        
        # SDR Team para tarefas especializadas
        self.sdr_team = None
        
        # Context analyzer tools - apenas habilitar as ferramentas configuradas
        self.tools = []
        
        # Adicionar ferramentas baseadas nas configurações
        if self.context_analysis_enabled:
            self.tools.append(self.analyze_conversation_context)
            self.tools.append(self.get_last_100_messages)
        
        if self.emotional_triggers_enabled:
            self.tools.append(self.detect_emotional_triggers)
        
        # Sempre incluir decisão do SDR Team
        self.tools.append(self.should_call_sdr_team)
        
        if self.multimodal_enabled:
            self.tools.append(self.process_multimodal_content)
        
        if self.knowledge_search_enabled:
            self.tools.append(self.search_knowledge_base)
        
        emoji_logger.agentic_thinking(f"Tools habilitadas: {len(self.tools)}", 
                                      tools=[t.__name__ for t in self.tools])
        
        # Criar o agente principal
        self._create_agentic_agent()
        
        emoji_logger.agentic_start("Sistema inicializado com sucesso", 
                                   context_enabled=self.context_analysis_enabled,
                                   reasoning_enabled=self.reasoning_enabled,
                                   multimodal_enabled=self.multimodal_enabled)
    
    def _setup_models(self):
        """Configura modelos com fallback inteligente baseado nas configurações"""
        try:
            # Usar modelo configurado no .env
            primary_model = settings.primary_ai_model
            
            if "gemini" in primary_model.lower():
                # Modelo principal - Gemini configurável
                self.model = Gemini(
                    id=primary_model,
                    api_key=settings.google_api_key,
                    temperature=settings.ai_temperature,
                    max_tokens=settings.ai_max_tokens
                )
                
                # Modelo de reasoning - Gemini 2.0 Flash Thinking
                if self.reasoning_enabled:
                    self.reasoning_model = Gemini(
                        id="gemini-2.0-flash-thinking-exp-01-21",
                        api_key=settings.google_api_key,
                        reasoning=True,
                        reasoning_effort="high",
                        stream_reasoning=settings.enable_streaming_responses
                    )
                else:
                    self.reasoning_model = self.model
                
                emoji_logger.system_ready("Modelos configurados", 
                                         primary_model=primary_model,
                                         reasoning_enabled=self.reasoning_enabled)
            else:
                # OpenAI como modelo primário
                self.model = OpenAI(
                    id=primary_model,
                    api_key=settings.openai_api_key,
                    temperature=settings.ai_temperature,
                    max_tokens=settings.ai_max_tokens
                )
                self.reasoning_model = self.model
                
        except Exception as e:
            if settings.enable_model_fallback:
                emoji_logger.system_warning(f"Erro com {primary_model}, usando fallback: {e}",
                                           fallback_model=settings.fallback_ai_model)
                
                # Fallback configurável
                fallback_model = settings.fallback_ai_model
                
                if "gemini" in fallback_model.lower():
                    self.model = Gemini(
                        id=fallback_model,
                        api_key=settings.google_api_key,
                        temperature=settings.ai_temperature
                    )
                else:
                    self.model = OpenAI(
                        id=fallback_model,
                        api_key=settings.openai_api_key,
                        temperature=settings.ai_temperature
                    )
                
                self.reasoning_model = self.model
            else:
                raise
    
    def _create_agentic_agent(self):
        """Cria o agente AGENTIC SDR com personalidade completa"""
        
        # Carregar prompt completo do AGENTIC SDR
        with open("app/prompts/prompt-agente.md", "r", encoding="utf-8") as f:
            agentic_prompt = f.read()
        
        # Adicionar instruções de análise contextual
        enhanced_prompt = agentic_prompt + """

## 🧠 ANÁLISE CONTEXTUAL INTELIGENTE

Você SEMPRE deve:
1. Buscar e analisar as últimas 100 mensagens da conversa
2. Entender o contexto completo antes de responder
3. Detectar padrões e necessidades não explícitas
4. Decidir inteligentemente quando acionar especialistas

### Sistema de Decisão Contextual
Analise TODOS os seguintes fatores antes de decidir:
- Histórico completo da conversa
- Estágio atual do lead no funil
- Complexidade da solicitação
- Necessidade de expertise especializada
- Urgência e prioridade
- Estado emocional do lead

### Quando Acionar SDR Team
APENAS quando detectar necessidade REAL de:
- Qualificação técnica avançada
- Agendamento com múltiplas validações
- Análise de conta de luz com cálculos
- Follow-up estratégico complexo
- Atualização crítica no CRM
- Conhecimento técnico muito específico

LEMBRE-SE: Você resolve 90% das conversas sozinha!
"""
        
        self.agent = Agent(
            name="AGENTIC SDR",
            model=self.model,
            role=enhanced_prompt,
            tools=self.tools,
            memory=self.memory,
            knowledge=self.knowledge,
            show_tool_calls=True,
            markdown=True,
            debug_mode=settings.debug,
            # Configurações de personalidade
            system_prompt_kwargs={
                "emotional_state": self.emotional_state.value,
                "cognitive_load": self.cognitive_load,
                "current_time": datetime.now().strftime("%H:%M"),
                "day_of_week": datetime.now().strftime("%A")
            }
        )
    
    @tool
    async def analyze_conversation_context(
        self,
        phone: str,
        current_message: str
    ) -> Dict[str, Any]:
        """
        Analisa contexto completo da conversa
        
        Args:
            phone: Número do telefone
            current_message: Mensagem atual
            
        Returns:
            Análise contextual completa
        """
        try:
            # Buscar últimas 100 mensagens
            messages = await self.get_last_100_messages(phone)
            
            # Análise de padrões
            context_analysis = {
                "message_count": len(messages),
                "conversation_duration": self._calculate_duration(messages),
                "lead_engagement_level": self._analyze_engagement(messages),
                "detected_intents": self._detect_intents(messages),
                "emotional_trajectory": self._analyze_emotional_trajectory(messages),
                "key_topics": self._extract_key_topics(messages),
                "qualification_signals": self._detect_qualification_signals(messages),
                "objections_raised": self._extract_objections(messages),
                "decision_stage": self._determine_decision_stage(messages),
                "urgency_level": self._assess_urgency(messages, current_message)
            }
            
            # Determinar contexto principal
            context_analysis["primary_context"] = self._determine_primary_context(
                context_analysis
            )
            
            # Recomendação de ação
            context_analysis["recommended_action"] = self._recommend_action(
                context_analysis
            )
            
            emoji_logger.agentic_context(f"Contexto identificado: {context_analysis['primary_context']}",
                                        messages_analyzed=len(messages),
                                        context_type=context_analysis['primary_context'])
            
            return context_analysis
            
        except Exception as e:
            emoji_logger.system_error("AGENTIC SDR", f"Erro na análise contextual: {e}")
            return {
                "primary_context": ConversationContext.INITIAL_CONTACT.value,
                "error": str(e)
            }
    
    @tool
    async def get_last_100_messages(self, phone: str) -> List[Dict[str, Any]]:
        """
        Busca as últimas 100 mensagens do Supabase
        
        Args:
            phone: Número do telefone
            
        Returns:
            Lista com últimas 100 mensagens
        """
        try:
            # Buscar conversa
            conversation = await supabase_client.get_conversation_by_phone(phone)
            if not conversation:
                return []
            
            # Buscar últimas 100 mensagens
            query = supabase_client.client.table("messages")\
                .select("*")\
                .eq("conversation_id", conversation["id"])\
                .order("created_at", desc=True)\
                .limit(100)
            
            response = await query.execute()
            messages = response.data if response.data else []
            
            # Reverter para ordem cronológica
            messages.reverse()
            
            emoji_logger.supabase_success(f"Mensagens recuperadas: {len(messages)}",
                                         execution_time=0.1)
            
            return messages
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao buscar mensagens: {e}",
                                       table="conversations")
            return []
    
    @tool
    async def detect_emotional_triggers(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detecta gatilhos emocionais na conversa
        
        Args:
            messages: Histórico de mensagens
            
        Returns:
            Gatilhos emocionais detectados
        """
        # Verificar se análise emocional está habilitada
        if not self.emotional_triggers_enabled:
            return {
                "enabled": False,
                "message": "Análise emocional desabilitada"
            }
        
        triggers = {
            "frustration_indicators": 0,
            "excitement_indicators": 0,
            "hesitation_indicators": 0,
            "urgency_indicators": 0,
            "trust_indicators": 0
        }
        
        # Palavras-chave para cada emoção
        frustration_words = ["demora", "difícil", "complicado", "não entendo", "problema"]
        excitement_words = ["ótimo", "excelente", "adorei", "perfeito", "maravilha"]
        hesitation_words = ["não sei", "talvez", "preciso pensar", "dúvida", "será"]
        urgency_words = ["urgente", "rápido", "agora", "hoje", "imediato"]
        trust_words = ["confio", "acredito", "verdade", "sério", "garantia"]
        
        for msg in messages[-20:]:  # Últimas 20 mensagens
            content = msg.get("content", "").lower()
            
            for word in frustration_words:
                if word in content:
                    triggers["frustration_indicators"] += 1
            
            for word in excitement_words:
                if word in content:
                    triggers["excitement_indicators"] += 1
            
            for word in hesitation_words:
                if word in content:
                    triggers["hesitation_indicators"] += 1
            
            for word in urgency_words:
                if word in content:
                    triggers["urgency_indicators"] += 1
            
            for word in trust_words:
                if word in content:
                    triggers["trust_indicators"] += 1
        
        # Determinar estado emocional dominante
        max_trigger = max(triggers, key=triggers.get)
        triggers["dominant_emotion"] = max_trigger.replace("_indicators", "")
        
        return triggers
    
    @tool
    async def should_call_sdr_team(
        self,
        context_analysis: Dict[str, Any],
        current_message: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Decide inteligentemente se deve chamar SDR Team
        
        Args:
            context_analysis: Análise contextual completa
            current_message: Mensagem atual
            
        Returns:
            (deve_chamar, agente_especifico, razão)
        """
        # Análise multi-fatorial para decisão
        decision_factors = {
            "complexity_score": 0,
            "specialization_needed": False,
            "confidence_level": 1.0,
            "recommended_agent": None,
            "reasoning": []
        }
        
        # Fator 1: Complexidade da solicitação
        if any(word in current_message.lower() for word in 
               ["agendar", "reunião", "marcar", "horário", "disponibilidade"]):
            decision_factors["complexity_score"] += 0.4
            decision_factors["recommended_agent"] = "CalendarAgent"
            decision_factors["reasoning"].append("Solicitação de agendamento detectada")
        
        # Fator 2: Análise de conta necessária
        if context_analysis.get("has_bill_image") or \
           "conta de luz" in current_message.lower():
            decision_factors["complexity_score"] += 0.5
            decision_factors["recommended_agent"] = "BillAnalyzerAgent"
            decision_factors["reasoning"].append("Análise de conta necessária")
        
        # Fator 3: Lead de alto valor
        qualification_signals = context_analysis.get("qualification_signals", {})
        if qualification_signals.get("bill_value", 0) > 4000:
            decision_factors["complexity_score"] += 0.3
            if not decision_factors["recommended_agent"]:
                decision_factors["recommended_agent"] = "QualificationAgent"
            decision_factors["reasoning"].append("Lead de alto valor detectado")
        
        # Fator 4: Múltiplas objeções
        if len(context_analysis.get("objections_raised", [])) > 2:
            decision_factors["complexity_score"] += 0.4
            decision_factors["reasoning"].append("Múltiplas objeções necessitam tratamento especializado")
        
        # Fator 5: Estágio avançado no funil
        if context_analysis.get("decision_stage") in ["negotiation", "closing"]:
            decision_factors["complexity_score"] += 0.3
            decision_factors["reasoning"].append("Estágio avançado requer expertise")
        
        # Fator 6: Necessidade de follow-up estratégico
        if context_analysis.get("conversation_duration", 0) > 24:  # horas
            decision_factors["complexity_score"] += 0.2
            if not decision_factors["recommended_agent"]:
                decision_factors["recommended_agent"] = "FollowUpAgent"
            decision_factors["reasoning"].append("Follow-up estratégico necessário")
        
        # Decisão final baseada em threshold inteligente
        should_call = decision_factors["complexity_score"] >= 0.7
        
        if should_call:
            reason = f"Score de complexidade: {decision_factors['complexity_score']:.2f}. " + \
                    ". ".join(decision_factors["reasoning"])
            
            emoji_logger.agentic_decision(f"Chamar SDR Team - {decision_factors['recommended_agent']}",
                                         score=decision_factors['complexity_score'],
                                         recommended_agent=decision_factors['recommended_agent'])
            return True, decision_factors["recommended_agent"], reason
        
        emoji_logger.agentic_decision("AGENTIC SDR resolve sozinha",
                                     score=decision_factors['complexity_score'])
        return False, None, "AGENTIC SDR pode resolver esta conversa"
    
    @tool
    async def process_multimodal_content(
        self,
        media_type: str,
        media_data: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa conteúdo multimodal (imagens, áudio, documentos)
        
        Args:
            media_type: Tipo de mídia
            media_data: Dados da mídia (base64)
            caption: Legenda opcional
            
        Returns:
            Análise do conteúdo multimodal
        """
        try:
            # Verificar se análise multimodal está habilitada
            if not self.multimodal_enabled:
                return {
                    "enabled": False,
                    "message": "Análise multimodal desabilitada"
                }
            if media_type == "image":
                # Usar GPT-4 Vision ou Gemini Vision
                result = await self.agent.run(
                    f"Analise esta imagem: {caption or 'Sem legenda'}",
                    images=[media_data]
                )
                
                # Verificar se é conta de luz
                if any(word in result.content.lower() for word in 
                       ["conta", "energia", "kwh", "tarifa", "consumo"]):
                    return {
                        "type": "bill_image",
                        "needs_analysis": True,
                        "content": result.content
                    }
            
            elif media_type == "audio":
                # Processar áudio (transcrição)
                # TODO: Integrar com serviço de transcrição
                return {
                    "type": "audio",
                    "transcription": "Áudio recebido - processamento em desenvolvimento"
                }
            
            elif media_type in ["document", "pdf"]:
                # Processar documento
                from agno.document_reader import PDFReader
                reader = PDFReader()
                content = reader.load_data(base64.b64decode(media_data))
                
                return {
                    "type": "document",
                    "content": content,
                    "pages": len(content)
                }
            
            return {"type": media_type, "processed": True}
            
        except Exception as e:
            emoji_logger.agentic_multimodal(f"Erro no processamento: {e}",
                                           media_type=media_data.get('type') if media_data else 'unknown')
            return {"type": media_type, "error": str(e)}
    
    @tool
    async def search_knowledge_base(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca na knowledge base com RAG
        
        Args:
            query: Query de busca
            filters: Filtros opcionais
            
        Returns:
            Documentos relevantes
        """
        try:
            # Verificar se knowledge base está habilitada
            if not self.knowledge_search_enabled:
                return []
            results = await self.knowledge.search(
                query=query,
                filters=filters or {},
                distance_metric="cosine"
            )
            
            return [
                {
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "score": doc.score
                }
                for doc in results
            ]
            
        except Exception as e:
            emoji_logger.team_knowledge(f"Erro na busca: {e}")
            return []
    
    # Métodos auxiliares privados
    def _calculate_duration(self, messages: List[Dict[str, Any]]) -> float:
        """Calcula duração da conversa em horas"""
        if len(messages) < 2:
            return 0
        
        first_msg = datetime.fromisoformat(messages[0]["created_at"])
        last_msg = datetime.fromisoformat(messages[-1]["created_at"])
        
        return (last_msg - first_msg).total_seconds() / 3600
    
    def _analyze_engagement(self, messages: List[Dict[str, Any]]) -> str:
        """Analisa nível de engajamento do lead"""
        if not messages:
            return "low"
        
        # Calcular métricas de engajamento
        user_messages = [m for m in messages if m.get("sender") == "user"]
        avg_response_length = sum(len(m.get("content", "")) for m in user_messages) / max(len(user_messages), 1)
        response_frequency = len(user_messages) / max(self._calculate_duration(messages), 1)
        
        if avg_response_length > 50 and response_frequency > 2:
            return "high"
        elif avg_response_length > 20 and response_frequency > 1:
            return "medium"
        else:
            return "low"
    
    def _detect_intents(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Detecta intenções na conversa"""
        intents = []
        
        intent_keywords = {
            "save_money": ["economizar", "desconto", "reduzir", "conta alta"],
            "install_solar": ["instalar", "painéis", "usina", "solar"],
            "get_information": ["como funciona", "informações", "saber mais", "entender"],
            "schedule_meeting": ["reunião", "agendar", "marcar", "conversar"],
            "compare_options": ["diferença", "comparar", "melhor", "opções"]
        }
        
        for msg in messages:
            content = msg.get("content", "").lower()
            for intent, keywords in intent_keywords.items():
                if any(kw in content for kw in keywords) and intent not in intents:
                    intents.append(intent)
        
        return intents
    
    def _analyze_emotional_trajectory(self, messages: List[Dict[str, Any]]) -> str:
        """Analisa trajetória emocional da conversa"""
        if not messages:
            return "neutral"
        
        # Simplificado: análise das últimas mensagens
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        
        positive_count = 0
        negative_count = 0
        
        for msg in recent_messages:
            content = msg.get("content", "").lower()
            
            # Palavras positivas
            if any(word in content for word in ["ótimo", "excelente", "perfeito", "adorei", "sim"]):
                positive_count += 1
            
            # Palavras negativas
            if any(word in content for word in ["não", "difícil", "caro", "problema", "dúvida"]):
                negative_count += 1
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_key_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extrai tópicos principais da conversa"""
        topics = []
        
        topic_keywords = {
            "pricing": ["preço", "valor", "custo", "investimento"],
            "savings": ["economia", "desconto", "redução"],
            "contract": ["contrato", "prazo", "fidelidade"],
            "installation": ["instalação", "obra", "telhado"],
            "guarantee": ["garantia", "segurança", "risco"]
        }
        
        for msg in messages:
            content = msg.get("content", "").lower()
            for topic, keywords in topic_keywords.items():
                if any(kw in content for kw in keywords) and topic not in topics:
                    topics.append(topic)
        
        return topics
    
    def _detect_qualification_signals(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detecta sinais de qualificação do lead"""
        signals = {
            "bill_value": 0,
            "has_decision_power": False,
            "timeline_mentioned": False,
            "budget_discussed": False,
            "competitor_mentioned": False
        }
        
        for msg in messages:
            content = msg.get("content", "").lower()
            
            # Detectar valor da conta
            import re
            valores = re.findall(r'r\$?\s*(\d+\.?\d*)', content)
            if valores:
                signals["bill_value"] = max(signals["bill_value"], 
                                           max(float(v.replace(".", "")) for v in valores))
            
            # Detectar poder de decisão
            if any(word in content for word in ["eu decido", "sou o responsável", "minha empresa"]):
                signals["has_decision_power"] = True
            
            # Timeline
            if any(word in content for word in ["este mês", "urgente", "logo", "quando"]):
                signals["timeline_mentioned"] = True
            
            # Budget
            if any(word in content for word in ["orçamento", "investimento", "posso pagar"]):
                signals["budget_discussed"] = True
            
            # Concorrência
            if any(word in content for word in ["origo", "setta", "outro fornecedor"]):
                signals["competitor_mentioned"] = True
        
        return signals
    
    def _extract_objections(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extrai objeções mencionadas"""
        objections = []
        
        objection_patterns = {
            "price": ["muito caro", "não tenho dinheiro", "fora do orçamento"],
            "trust": ["não confio", "é golpe", "enganação"],
            "timing": ["não é o momento", "depois", "ano que vem"],
            "need": ["não preciso", "não vale a pena", "satisfeito"],
            "competitor": ["já tenho", "outro fornecedor", "contrato vigente"]
        }
        
        for msg in messages:
            content = msg.get("content", "").lower()
            for objection_type, patterns in objection_patterns.items():
                if any(p in content for p in patterns) and objection_type not in objections:
                    objections.append(objection_type)
        
        return objections
    
    def _determine_decision_stage(self, messages: List[Dict[str, Any]]) -> str:
        """Determina estágio de decisão do lead"""
        if len(messages) < 5:
            return "awareness"
        
        # Análise simplificada baseada em palavras-chave
        recent_content = " ".join([m.get("content", "") for m in messages[-10:]])
        
        if any(word in recent_content.lower() for word in ["fechado", "vamos fazer", "aceito"]):
            return "decision"
        elif any(word in recent_content.lower() for word in ["quanto", "como funciona", "garantias"]):
            return "consideration"
        elif any(word in recent_content.lower() for word in ["interessante", "me conta mais"]):
            return "interest"
        else:
            return "awareness"
    
    def _assess_urgency(self, messages: List[Dict[str, Any]], current_message: str) -> str:
        """Avalia nível de urgência"""
        urgency_keywords = {
            "high": ["urgente", "agora", "hoje", "imediato"],
            "medium": ["esta semana", "breve", "logo"],
            "low": ["futuramente", "talvez", "vou pensar"]
        }
        
        combined_text = current_message.lower() + " " + \
                       " ".join([m.get("content", "") for m in messages[-5:]])
        
        for level, keywords in urgency_keywords.items():
            if any(kw in combined_text for kw in keywords):
                return level
        
        return "medium"
    
    def _determine_primary_context(self, analysis: Dict[str, Any]) -> str:
        """Determina contexto principal da conversa"""
        # Lógica de priorização baseada na análise
        
        if analysis.get("decision_stage") == "decision" and \
           analysis.get("qualification_signals", {}).get("bill_value", 0) > 4000:
            return ConversationContext.SCHEDULING_READY.value
        
        if len(analysis.get("objections_raised", [])) > 1:
            return ConversationContext.OBJECTION_HANDLING.value
        
        if analysis.get("qualification_signals", {}).get("bill_value", 0) > 6000:
            return ConversationContext.HIGH_VALUE_LEAD.value
        
        if analysis.get("lead_engagement_level") == "high" and \
           len(analysis.get("detected_intents", [])) > 2:
            return ConversationContext.QUALIFICATION_NEEDED.value
        
        if "technical" in analysis.get("key_topics", []):
            return ConversationContext.TECHNICAL_QUESTIONS.value
        
        if analysis.get("conversation_duration", 0) > 24:
            return ConversationContext.FOLLOW_UP_REQUIRED.value
        
        return ConversationContext.INITIAL_CONTACT.value
    
    def _recommend_action(self, analysis: Dict[str, Any]) -> str:
        """Recomenda ação baseada na análise"""
        context = analysis.get("primary_context")
        
        action_map = {
            ConversationContext.SCHEDULING_READY.value: "Agendar reunião com o consultor",
            ConversationContext.OBJECTION_HANDLING.value: "Tratar objeções com empatia e dados",
            ConversationContext.HIGH_VALUE_LEAD.value: "Priorizar atendimento personalizado",
            ConversationContext.QUALIFICATION_NEEDED.value: "Qualificar lead com perguntas-chave",
            ConversationContext.TECHNICAL_QUESTIONS.value: "Fornecer informações técnicas detalhadas",
            ConversationContext.FOLLOW_UP_REQUIRED.value: "Reengajar com oferta especial",
            ConversationContext.INITIAL_CONTACT.value: "Iniciar rapport e descobrir necessidades"
        }
        
        return action_map.get(context, "Continuar conversa naturalmente")
    
    async def initialize(self):
        """Inicializa recursos do agente"""
        try:
            # Carregar knowledge base
            await self.knowledge.load_documents([
                "data/solar_prime_info.txt",
                "data/produtos_solucoes.txt",
                "data/objecoes_respostas.txt"
            ])
            
            # Inicializar SDR Team se necessário
            if not self.sdr_team:
                from app.teams.sdr_team import create_sdr_team
                self.sdr_team = create_sdr_team()
                await self.sdr_team.initialize()
            
            self.is_initialized = True
            emoji_logger.system_ready("AGENTIC SDR", startup_time=0.5)
            
        except Exception as e:
            emoji_logger.system_error("AGENTIC SDR", f"Erro na inicialização: {e}")
            raise
    
    async def process_message(
        self,
        phone: str,
        message: str,
        lead_data: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        media: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Processa mensagem com análise contextual inteligente
        
        Args:
            phone: Número do telefone
            message: Mensagem recebida
            lead_data: Dados do lead
            conversation_id: ID da conversa
            media: Mídia anexada
            
        Returns:
            Resposta do AGENTIC SDR
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 1. SEMPRE fazer análise contextual completa
            context_analysis = await self.analyze_conversation_context(phone, message)
            
            # 2. Detectar gatilhos emocionais
            messages_history = await self.get_last_100_messages(phone)
            emotional_triggers = await self.detect_emotional_triggers(messages_history)
            
            # 3. Processar multimodal se necessário
            multimodal_result = None
            if media:
                multimodal_result = await self.process_multimodal_content(
                    media.get("type"),
                    media.get("data", ""),
                    media.get("caption")
                )
                
                # Adicionar ao contexto
                context_analysis["has_media"] = True
                context_analysis["media_analysis"] = multimodal_result
            
            # 4. Decidir inteligentemente sobre SDR Team
            should_call, recommended_agent, reasoning = await self.should_call_sdr_team(
                context_analysis,
                message
            )
            
            # 5. Se precisar do SDR Team E contexto justificar
            if should_call and recommended_agent:
                emoji_logger.team_delegate(recommended_agent, reasoning)
                
                # Preparar contexto enriquecido para o Team
                enriched_context = {
                    "phone": phone,
                    "message": message,
                    "lead_data": lead_data,
                    "conversation_id": conversation_id,
                    "context_analysis": context_analysis,
                    "emotional_triggers": emotional_triggers,
                    "recommended_agent": recommended_agent,
                    "reasoning": reasoning,
                    "multimodal_result": multimodal_result
                }
                
                # Chamar SDR Team com contexto completo
                team_response = await self.sdr_team.process_message_with_context(
                    enriched_context
                )
                
                # AGENTIC SDR ainda personaliza a resposta final
                response = await self._personalize_team_response(
                    team_response,
                    emotional_triggers
                )
                
            else:
                # 6. AGENTIC SDR resolve sozinha (90% dos casos)
                emoji_logger.agentic_thinking("Processando mensagem diretamente")
                
                # Preparar prompt com contexto completo
                contextual_prompt = f"""
                Mensagem do lead: {message}
                
                Análise Contextual:
                - Contexto Principal: {context_analysis.get('primary_context')}
                - Engajamento: {context_analysis.get('lead_engagement_level')}
                - Estágio: {context_analysis.get('decision_stage')}
                - Ação Recomendada: {context_analysis.get('recommended_action')}
                
                Estado Emocional do Lead:
                - Emoção Dominante: {emotional_triggers.get('dominant_emotion')}
                - Urgência: {context_analysis.get('urgency_level')}
                
                {"Mídia anexada: " + str(multimodal_result) if multimodal_result else ""}
                
                Responda de forma natural, empática e personalizada.
                """
                
                # Usar reasoning para casos complexos
                if context_analysis.get("complexity_score", 0) > 0.5:
                    result = await self.reasoning_model.run(contextual_prompt)
                else:
                    result = await self.agent.run(contextual_prompt)
                
                response = result.content
            
            # 7. Ajustar estado emocional da Helen
            self._update_emotional_state(emotional_triggers, context_analysis)
            
            # 8. Salvar na memória
            await self.memory.add(
                message=message,
                user_id=phone,
                metadata={
                    "context_analysis": context_analysis,
                    "emotional_state": self.emotional_state.value,
                    "sdr_team_used": should_call
                }
            )
            
            # 9. Aplicar simulação de digitação natural
            response = self._apply_typing_simulation(response)
            
            return response
            
        except Exception as e:
            emoji_logger.system_error("AGENTIC SDR", f"Erro ao processar mensagem: {e}")
            return "Oi! Desculpa, tive um probleminha aqui 😅 Você pode repetir?"
    
    async def _personalize_team_response(
        self,
        team_response: str,
        emotional_triggers: Dict[str, Any]
    ) -> str:
        """Personaliza resposta do Team com toque do AGENTIC SDR"""
        
        # Adicionar personalização baseada no estado emocional
        personalization_prompt = f"""
        Resposta técnica: {team_response}
        
        Emoção do lead: {emotional_triggers.get('dominant_emotion')}
        Seu estado emocional: {self.emotional_state.value}
        
        Reescreva mantendo a informação mas com seu toque pessoal,
        empatia e naturalidade. Mantenha breve e direto.
        """
        
        result = await self.agent.run(personalization_prompt)
        return result.content
    
    def _update_emotional_state(
        self,
        emotional_triggers: Dict[str, Any],
        context_analysis: Dict[str, Any]
    ):
        """Atualiza estado emocional do AGENTIC SDR baseado na conversa"""
        
        # Lógica simplificada de transição de estados
        dominant_emotion = emotional_triggers.get("dominant_emotion")
        
        if dominant_emotion == "frustration" and \
           emotional_triggers.get("frustration_indicators", 0) > 3:
            self.emotional_state = EmotionalState.FRUSTRADA_SUTIL
        
        elif dominant_emotion == "excitement":
            self.emotional_state = EmotionalState.ENTUSIASMADA
        
        elif dominant_emotion == "hesitation":
            self.emotional_state = EmotionalState.EMPATICA
        
        elif context_analysis.get("decision_stage") == "decision":
            self.emotional_state = EmotionalState.DETERMINADA
        
        elif self.conversations_today > 20:
            self.emotional_state = EmotionalState.CANSADA
        
        # Incrementar contador de conversas
        self.conversations_today += 1
        
        emoji_logger.agentic_thinking(f"Estado emocional atualizado: {self.emotional_state.value}",
                                     emotional_state=self.emotional_state.value)
    
    def _apply_typing_simulation(self, text: str) -> str:
        """Aplica simulação de digitação natural"""
        
        # Quebrar em mensagens menores (WhatsApp natural)
        if len(text) > 100:
            # Encontrar pontos naturais de quebra
            sentences = text.split(". ")
            
            result = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < 80:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        result.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                result.append(current_chunk.strip())
            
            # Juntar com quebras naturais
            return "\n".join(result)
        
        return text
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do agente"""
        return {
            "emotional_state": self.emotional_state.value,
            "conversations_today": self.conversations_today,
            "cognitive_load": self.cognitive_load,
            "is_initialized": self.is_initialized
        }


# Factory function
def create_agentic_sdr() -> AgenticSDR:
    """Cria e retorna instância do AGENTIC SDR"""
    return AgenticSDR()


# Singleton global
agentic_sdr_instance = None

async def get_agentic_sdr() -> AgenticSDR:
    """Retorna instância singleton do AGENTIC SDR"""
    global agentic_sdr_instance
    
    if agentic_sdr_instance is None:
        agentic_sdr_instance = AgenticSDR()
        await agentic_sdr_instance.initialize()
    
    return agentic_sdr_instance