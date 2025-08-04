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

from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Image as AgnoImage
# OpenAI via requests - contorna problemas do SDK
try:
    import requests
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SimpleOpenAIWrapper:
    """
    Wrapper OpenAI usando requests diretos para evitar problemas do SDK
    """
    def __init__(self, api_key, id="o3-mini", max_tokens=4000, temperature=0.7):
        if not OPENAI_AVAILABLE:
            raise ImportError("requests não disponível")
            
        import requests
        self.api_key = api_key
        self.model_id = id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = "https://api.openai.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def run(self, message, **kwargs):
        """Interface compatível com AGNO usando requests diretos"""
        try:
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": str(message)}],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            raise Exception(f"OpenAI o3-mini falhou: {e}")
    
    def __str__(self):
        return f"SimpleOpenAI({self.model_id})"
from agno.memory import AgentMemory
from agno.storage.postgres import PostgresStorage
from agno.knowledge import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.tools import tool
from loguru import logger
from app.utils.logger import emoji_logger
from app.utils.optional_storage import OptionalStorage
from app.utils.agno_media_detection import agno_media_detector

from app.config import settings
from app.integrations.supabase_client import supabase_client
from app.teams.sdr_team import SDRTeam

# AGNO Framework Enhancement - Context utilities apenas
from app.services.agno_context_agent import format_context_with_agno


class IntelligentModelFallback:
    """
    Wrapper inteligente para gerenciar fallback automático entre modelos
    Detecta erros Gemini e automaticamente usa OpenAI o3-mini
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.primary_model = None
        self.fallback_model = None
        self.current_model = None
        # Importar o detector de mídia como atributo da classe
        self.agno_media_detector = agno_media_detector
        self.fallback_active = False
        
        # Configurações de retry para Gemini
        self.max_retry_attempts = getattr(settings, 'gemini_retry_attempts', 2)  # 2 tentativas de retry
        self.retry_delay = getattr(settings, 'gemini_retry_delay', 5.0)  # 5 segundos entre tentativas
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa os modelos primário e fallback"""
        try:
            # Modelo primário (Gemini)
            if "gemini" in self.settings.primary_ai_model.lower():
                self.primary_model = Gemini(
                    id=self.settings.primary_ai_model,
                    api_key=self.settings.google_api_key,
                    temperature=self.settings.ai_temperature,
                    max_output_tokens=self.settings.ai_max_tokens
                )
                emoji_logger.system_ready("Modelo primário Gemini configurado", 
                                         model=self.settings.primary_ai_model)
            
            # Modelo fallback (OpenAI o3-mini)  
            if self.settings.enable_model_fallback and self.settings.openai_api_key and OPENAI_AVAILABLE:
                try:
                    # Usar wrapper customizado OpenAI (compatível)
                    self.fallback_model = SimpleOpenAIWrapper(
                        api_key=self.settings.openai_api_key,
                        id="o3-mini",
                        max_tokens=self.settings.ai_max_tokens,
                        temperature=self.settings.ai_temperature
                    )
                    emoji_logger.system_ready("Modelo fallback OpenAI o3-mini configurado")
                        
                except Exception as e:
                    emoji_logger.system_warning(f"Falha ao configurar OpenAI o3-mini fallback: {e}")
                    self.fallback_model = None
            else:
                if not OPENAI_AVAILABLE:
                    emoji_logger.system_warning("OpenAI não disponível - fallback desabilitado")
                elif not self.settings.openai_api_key:
                    emoji_logger.system_warning("OPENAI_API_KEY não configurada - fallback desabilitado")
                else:
                    emoji_logger.system_warning("Fallback desabilitado por configuração")
                self.fallback_model = None
            
            # Define modelo atual
            self.current_model = self.primary_model
            
        except Exception as e:
            emoji_logger.system_error(f"Erro na inicialização de modelos: {e}")
            raise
    
    def _is_gemini_error(self, error) -> bool:
        """Detecta se é um erro que requer fallback"""
        error_str = str(error).lower()
        
        # Erros que requerem fallback
        fallback_triggers = [
            "500 internal",
            "503 service unavailable", 
            "502 bad gateway",
            "timeout",
            "connection error",
            "server error",
            "internal error has occurred"
        ]
        
        return any(trigger in error_str for trigger in fallback_triggers)
    
    def _should_retry_with_fallback(self, error) -> bool:
        """Determina se deve tentar fallback"""
        return (
            not self.fallback_active and  # Não estamos já usando fallback
            self.fallback_model is not None and  # Temos modelo fallback
            self._is_gemini_error(error)  # É um erro que requer fallback
        )
    
    async def _retry_with_backoff(self, message: str, **kwargs):
        """
        Tenta executar o Gemini com retry e backoff
        Retorna a resposta ou None se todas as tentativas falharem
        """
        import asyncio
        
        last_error = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                emoji_logger.system_info(f"🔄 Retry Gemini - Tentativa {attempt + 1}/{self.max_retry_attempts}")
                
                # Tenta executar o modelo primário
                response = self.primary_model.invoke(message, **kwargs)
                
                if attempt > 0:
                    emoji_logger.system_ready(f"✅ Gemini recuperado após {attempt + 1} tentativa(s)")
                
                return response
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Só faz retry se for erro temporário do Gemini
                if self._is_gemini_error(e):
                    if attempt < self.max_retry_attempts - 1:
                        emoji_logger.system_warning(
                            f"⚠️ Erro Gemini: {e}. Aguardando {self.retry_delay}s antes da próxima tentativa..."
                        )
                        await asyncio.sleep(self.retry_delay)
                    else:
                        emoji_logger.system_warning(
                            f"❌ Gemini falhou após {self.max_retry_attempts} tentativas"
                        )
                else:
                    # Se não for erro temporário, não faz retry
                    emoji_logger.system_warning(f"❌ Erro Gemini não recuperável: {e}")
                    raise e
        
        # Se chegou aqui, todas as tentativas falharam
        return None
    
    async def run(self, message: str, **kwargs):
        """
        Executa o modelo com retry inteligente e fallback
        Fluxo: Gemini → Retry (se erro 500/503) → Fallback OpenAI (se retry falhar)
        """
        # Se já estamos usando fallback, usa direto
        if self.fallback_active and self.current_model == self.fallback_model:
            try:
                response = self.fallback_model.run(message, **kwargs)
                emoji_logger.system_info("📍 Usando fallback OpenAI o3-mini")
                return response
            except Exception as e:
                emoji_logger.system_error("Fallback OpenAI também falhou", error=str(e))
                raise e
        
        # Tenta com modelo primário (Gemini)
        try:
            if self.primary_model:
                response = self.primary_model.invoke(message, **kwargs)
                
                # Se estava usando fallback e Gemini funcionou, desativa fallback
                if self.fallback_active:
                    emoji_logger.system_ready("✅ Gemini recuperado, desativando fallback")
                    self.fallback_active = False
                    self.current_model = self.primary_model
                
                return response
                
        except Exception as e:
            emoji_logger.system_warning(f"⚠️ Erro inicial no Gemini: {e}")
            
            # Se é erro temporário do Gemini, tenta retry
            if self._is_gemini_error(e):
                emoji_logger.system_info("🔄 Iniciando retry automático do Gemini...")
                
                # Tenta com retry
                retry_response = await self._retry_with_backoff(message, **kwargs)
                
                if retry_response is not None:
                    return retry_response
                
                # Se retry falhou e temos fallback, ativa OpenAI
                if self.fallback_model is not None:
                    emoji_logger.system_warning("🔄 Retry esgotado, ativando fallback OpenAI o3-mini...")
                    
                    try:
                        self.current_model = self.fallback_model
                        self.fallback_active = True
                        
                        response = self.fallback_model.run(message, **kwargs)
                        emoji_logger.system_ready("✅ Fallback OpenAI o3-mini ativado com sucesso")
                        return response
                        
                    except Exception as fallback_error:
                        emoji_logger.system_error("Fallback OpenAI também falhou", error=str(fallback_error))
                        # Volta para modelo primário para próxima tentativa
                        self.current_model = self.primary_model
                        self.fallback_active = False
                        raise fallback_error
                else:
                    emoji_logger.system_error("Retry falhou e não há fallback configurado", error=str(e))
                    raise e
            else:
                # Erro não recuperável, não faz retry
                emoji_logger.system_error("Erro não recuperável no Gemini", error=str(e))
                raise e
    
    def reset_to_primary(self):
        """Força volta ao modelo primário"""
        if self.primary_model:
            self.current_model = self.primary_model
            self.fallback_active = False
            emoji_logger.system_info("Modelo resetado para primário (Gemini)")
    
    def get_current_model_info(self) -> dict:
        """Retorna informações do modelo atual"""
        return {
            "current_model": self.current_model.__class__.__name__ if self.current_model else None,
            "fallback_active": self.fallback_active,
            "has_fallback": self.fallback_model is not None
        }


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
        
        # Importar o detector de mídia como atributo da classe
        self.agno_media_detector = agno_media_detector
        
        # Armazenar referência ao settings
        self.settings = settings
        
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
        
        # Configuração do PostgreSQL/Supabase para storage com fallback
        # Storage persistente com fallback para memória se PostgreSQL não disponível
        self.storage = OptionalStorage(
            table_name="agentic_sdr_sessions",  # Nome da tabela para sessões do agente
            db_url=settings.get_postgres_url(),  # URL já inclui autenticação
            schema="public",  # Schema do Supabase
            auto_upgrade_schema=True  # Auto-atualiza schema se necessário
        )
        
        # Setup models BEFORE Memory (needed for fallback)
        self._setup_models()
        
        # Memory v2 com multi-usuário e persistência
        # Tenta criar Memory com storage, fallback para sem persistência
        try:
            self.memory = AgentMemory(
                db=self.storage,  # db é o parâmetro correto para storage
                create_user_memories=True,
                create_session_summary=True
            )
            emoji_logger.system_ready("Memory", status="com persistência")
        except Exception as e:
            emoji_logger.system_warning(f"Memory sem persistência: {str(e)[:50]}...")
            # Memory without persistence needs model parameter
            self.memory = AgentMemory(
                create_user_memories=True,
                create_session_summary=True
            )
        
        # PgVector para embeddings e busca semântica (opcional)
        try:
            self.vector_db = PgVector(
                table_name="agentic_knowledge",  # table_name is the first required parameter
                db_url=settings.get_postgres_url()
                # Removed embedder parameter as it expects an Embedder object, not a dict
            )
            
            # Knowledge base com RAG
            self.knowledge = AgentKnowledge(
                vector_db=self.vector_db,
                num_documents=10
                # Removed unsupported parameters: search_type, rerank, reranker
            )
            emoji_logger.system_ready("Knowledge base", status="ativo")
        except Exception as e:
            emoji_logger.system_warning(f"Knowledge base não disponível: {str(e)[:50]}...")
            self.vector_db = None
            self.knowledge = None
        
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
        
        tool_names = []
        for t in self.tools:
            if hasattr(t, '__name__'):
                tool_names.append(t.__name__)
            elif hasattr(t, 'name'):
                tool_names.append(t.name)
            else:
                tool_names.append(str(t))
        emoji_logger.agentic_thinking(f"Tools habilitadas: {len(self.tools)}", 
                                      tools=tool_names)
        
        # Criar o agente principal
        self._create_agentic_agent()
        
        emoji_logger.agentic_start("Sistema inicializado com sucesso", 
                                   context_enabled=self.context_analysis_enabled,
                                   reasoning_enabled=self.reasoning_enabled,
                                   multimodal_enabled=self.multimodal_enabled)
    
    def _setup_models(self):
        """Configura modelos com fallback inteligente para OpenAI o3-mini"""
        try:
            # Usar novo sistema de fallback inteligente
            self.intelligent_model = IntelligentModelFallback(settings)
            
            # Para compatibilidade, manter referência self.model
            self.model = self.intelligent_model.current_model
            
            # Modelo de reasoning - Gemini 2.0 Flash Thinking (se habilitado)
            if self.reasoning_enabled and settings.google_api_key:
                try:
                    self.reasoning_model = Gemini(
                        id="gemini-2.0-flash-thinking-exp-01-21",
                        api_key=settings.google_api_key,
                        thinking_budget=8192,
                        include_thoughts=True
                    )
                    emoji_logger.system_ready("Modelo reasoning configurado", model="gemini-2.0-flash-thinking")
                except Exception as e:
                    emoji_logger.system_warning(f"Reasoning model falhou, usando modelo principal: {e}")
                    self.reasoning_model = self.intelligent_model.current_model
            else:
                self.reasoning_model = self.intelligent_model.current_model
            
            # Log status final
            model_info = self.intelligent_model.get_current_model_info()
            emoji_logger.system_ready("Sistema de modelos configurado", 
                                     primary_model=settings.primary_ai_model,
                                     fallback_available=model_info['has_fallback'],
                                     reasoning_enabled=self.reasoning_enabled)
                
        except Exception as e:
            emoji_logger.system_error(f"Erro crítico na configuração de modelos: {e}")
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
            model=self.intelligent_model.current_model,
            instructions=enhanced_prompt,
            tools=self.tools,
            memory=self.memory,
            knowledge=self.knowledge,
            show_tool_calls=True,
            markdown=True,
            debug_mode=settings.debug,
            # Context includes personality configurations
            context={
                "emotional_state": self.emotional_state.value,
                "cognitive_load": self.cognitive_load,
                "current_time": datetime.now().strftime("%H:%M"),
                "day_of_week": datetime.now().strftime("%A")
            }
        )
    
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
    
    async def get_last_100_messages(self, identifier: str) -> List[Dict[str, Any]]:
        """
        Busca as últimas 100 mensagens do Supabase
        
        Args:
            identifier: Número do telefone ou conversation_id
            
        Returns:
            Lista com últimas 100 mensagens
        """
        try:
            conversation_id = None
            
            # Determinar se é phone ou conversation_id
            if identifier.startswith('conv_') or len(identifier) > 15:
                # Parece ser conversation_id
                conversation_id = identifier
                emoji_logger.system_info(f"Buscando mensagens por conversation_id: {conversation_id}")
            else:
                # Parece ser phone
                emoji_logger.system_info(f"Buscando mensagens por phone: {identifier}")
                conversation = await supabase_client.get_conversation_by_phone(identifier)
                if not conversation:
                    emoji_logger.system_warning(f"Conversa não encontrada para phone: {identifier}")
                    return []
                conversation_id = conversation["id"]
                emoji_logger.system_info(f"Conversation_id encontrado: {conversation_id}")
            
            # Buscar últimas 100 mensagens
            emoji_logger.system_info(f"Executando query para conversation_id: {conversation_id}")
            query = supabase_client.client.table("messages")\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=True)\
                .limit(100)
            
            response = query.execute()  # Removido await - cliente síncrono
            messages = response.data if response.data else []
            
            emoji_logger.system_info(f"Query executada, {len(messages)} mensagens encontradas")
            
            # Reverter para ordem cronológica
            messages.reverse()
            
            emoji_logger.supabase_success(f"Mensagens recuperadas: {len(messages)}",
                                         execution_time=0.1)
            
            return messages
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao buscar mensagens: {e}",
                                       table="conversations")
            return []
    
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
    
    async def process_multimodal_content(
        self,
        media_type: str,
        media_data: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa conteúdo multimodal (imagens, áudio, documentos)
        
        Args:
            media_type: Tipo de mídia (image, audio, document, pdf)
            media_data: Dados da mídia em base64
            caption: Legenda opcional
            
        Returns:
            Análise do conteúdo multimodal com estrutura padronizada
        """
        # Função helper para detectar formato
        def detect_and_clean_base64(data: str) -> tuple[str, str]:
            """
            Detecta e limpa dados base64
            Retorna: (base64_limpo, formato_detectado)
            """
            if not data:
                return "", "empty"
            
            # Se começa com data URL, extrair apenas o base64
            if data.startswith("data:"):
                if ";base64," in data:
                    clean_data = data.split(";base64,")[1]
                    return clean_data, "data_url"
                return "", "invalid_data_url"
            
            # Se é URL HTTP, não é base64
            if data.startswith(("http://", "https://")):
                return "", "url"
            
            # Verificar se é base64 válido
            if len(data) > 50:
                try:
                    # Tenta decodificar uma amostra
                    import base64
                    test = base64.b64decode(data[:100], validate=True)
                    return data, "base64"
                except:
                    # Pode ser texto ou outro formato
                    return "", "invalid"
            
            return "", "too_short"
        import time
        start_time = time.time()
        
        try:
            # Log detalhado de início
            emoji_logger.system_info("═" * 50)
            emoji_logger.system_info(f"🎯 MULTIMODAL: Iniciando processamento")
            emoji_logger.system_info(f"📌 Tipo: {media_type.upper()}")
            emoji_logger.system_info(f"📊 Tamanho dados base64: {len(media_data):,} caracteres")
            emoji_logger.system_info(f"💬 Caption: {caption[:50] + '...' if caption and len(caption) > 50 else caption or 'Sem legenda'}")
            emoji_logger.system_info(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            emoji_logger.system_info("═" * 50)
            
            # Verificar se análise multimodal está habilitada
            if not self.multimodal_enabled:
                emoji_logger.system_warning("Análise multimodal desabilitada nas configurações")
                return {
                    "type": media_type,
                    "enabled": False,
                    "message": "Análise multimodal desabilitada"
                }
            
            # Validar entrada
            if not media_data:
                emoji_logger.system_warning(f"❌ MULTIMODAL: Dados vazios para {media_type}")
                emoji_logger.system_warning(f"⏱️ Tempo decorrido: {time.time() - start_time:.2f}s")
                return {
                    "type": media_type,
                    "error": "Dados de mídia não fornecidos"
                }
            
            # Validar tipo de mídia
            valid_types = ["image", "audio", "document", "pdf", "video"]
            if media_type not in valid_types:
                emoji_logger.system_warning(f"❌ MULTIMODAL: Tipo inválido '{media_type}'")
                emoji_logger.system_warning(f"📝 Tipos válidos: {', '.join(valid_types)}")
                return {
                    "type": media_type,
                    "error": f"Tipo de mídia '{media_type}' não suportado"
                }
            if media_type == "image":
                # AGNO Framework - Processamento nativo de imagens
                emoji_logger.system_info("🌆 " + "=" * 45)
                emoji_logger.system_info("🌆 PROCESSAMENTO DE IMAGEM INICIADO")
                emoji_logger.system_info("🌆 " + "=" * 45)
                
                # Validar e limpar base64
                clean_base64, format_type = detect_and_clean_base64(media_data)
                
                emoji_logger.system_info(f"🔍 IMAGEM - Formato detectado: {format_type}")
                
                if format_type in ["empty", "invalid", "too_short", "url"]:
                    emoji_logger.system_warning(f"❌ IMAGEM: Formato inválido - {format_type}")
                    if format_type == "url":
                        emoji_logger.system_warning("💡 Dica: URL detectada, precisa baixar primeiro")
                    return {
                        "type": "image",
                        "error": f"Dados de imagem inválidos (formato: {format_type})",
                        "status": "invalid_format",
                        "format_detected": format_type
                    }
                
                # Usar o base64 limpo
                media_data = clean_base64
                
                if not media_data:
                    emoji_logger.system_warning("❌ IMAGEM: Dados vazios após limpeza")
                    return {
                        "type": "image",
                        "error": "Dados de imagem vazios",
                        "status": "no_data"
                    }
                
                # Verificar tamanho da imagem
                data_size = len(media_data)
                estimated_bytes = (data_size * 3) // 4  # Estimativa de bytes decodificados
                estimated_kb = estimated_bytes / 1024
                estimated_mb = estimated_kb / 1024
                
                emoji_logger.system_info(f"📈 IMAGEM - Métricas:")
                emoji_logger.system_info(f"  • Base64: {data_size:,} caracteres")
                emoji_logger.system_info(f"  • Estimado: {estimated_bytes:,} bytes ({estimated_kb:.1f} KB / {estimated_mb:.2f} MB)")
                
                # Se a imagem é muito pequena, provavelmente é só thumbnail
                is_thumbnail = data_size < 50000  # Menos de 50KB em base64
                if is_thumbnail:
                    emoji_logger.system_warning("⚠️ IMAGEM: Possível thumbnail detectada (<50KB)")
                elif estimated_mb > 2:
                    emoji_logger.system_warning(f"⚠️ IMAGEM: Tamanho grande ({estimated_mb:.2f} MB) - pode causar lentidão")
                
                # Preparar prompt específico para análise
                # As instruções detalhadas estão no arquivo prompt-agente.md
                analysis_prompt = f"""Analise esta imagem e extraia TODAS as informações visíveis de forma detalhada.
                {f'Contexto fornecido pelo usuário: {caption}' if caption else ''}
                
                {'⚠️ ATENÇÃO: Esta pode ser apenas uma miniatura de baixa resolução. Faça o melhor possível com o que consegue ver.' if is_thumbnail else ''}
                
                Por favor, extraia e mencione especificamente todos os valores, datas, nomes e informações relevantes que conseguir identificar na imagem."""
                
                try:
                    # AGNO Framework Solution: Usar agno.media.Image nativo
                    import base64
                    import google.generativeai as genai
                    
                    emoji_logger.system_info("🔍 Etapa 1/4: Decodificando base64...")
                    
                    # AGNO Framework Solution: Usar agno.media.Image nativo
                    # Validar dados
                    if not media_data:
                        raise ValueError("Dados da imagem vazios")
                    
                    # Decodificar base64 para bytes
                    decode_start = time.time()
                    image_bytes = base64.b64decode(media_data)
                    original_size = len(image_bytes)
                    decode_time = time.time() - decode_start
                    
                    emoji_logger.system_info(f"✅ Decodificação completa em {decode_time:.2f}s")
                    emoji_logger.system_info(f"  • Tamanho real: {original_size:,} bytes")
                    emoji_logger.system_info(f"  • Taxa compressão: {(1 - original_size/data_size)*100:.1f}%")
                    
                    # AGNO Framework - Detecção robusta de formato de imagem
                    emoji_logger.system_info("🔍 Etapa 2/4: Detectando formato da imagem...")
                    detect_start = time.time()
                    detection_result = self.agno_media_detector.detect_media_type(image_bytes)
                    detect_time = time.time() - detect_start
                    
                    if not detection_result['detected']:
                        emoji_logger.system_warning(f"❌ IMAGEM: Formato não reconhecido")
                        emoji_logger.system_warning(f"  • Magic bytes: {detection_result.get('magic_bytes', 'N/A')}")
                        emoji_logger.system_warning(f"  • Tempo detecção: {detect_time:.2f}s")
                    else:
                        emoji_logger.system_info(f"✅ Formato detectado: {detection_result['format'].upper()}")
                        emoji_logger.system_info(f"  • Confiança: {detection_result.get('confidence', 'N/A')}")
                        emoji_logger.system_info(f"  • Tempo detecção: {detect_time:.2f}s")
                        # Usar fallback suggestion
                        fallback_msg = detection_result.get('fallback_suggestion', 'Formato não suportado')
                        return {
                            "type": "image",
                            "error": f"Formato não suportado: {fallback_msg}",
                            "status": "unsupported_format",
                            "agno_detection": detection_result
                        }
                    
                    format_hint = detection_result['format']
                    agno_params = detection_result['recommended_params']
                    emoji_logger.agentic_thinking(f"AGNO detectou: {format_hint} (confiança: {detection_result['confidence']})")
                    
                    # Criar objeto AGNO Image com bytes da imagem usando parâmetros detectados
                    try:
                        agno_image = AgnoImage(
                            content=image_bytes,
                            format=agno_params['format'],
                            detail=agno_params['detail']
                        )
                        emoji_logger.agentic_thinking("AGNO Image criado com sucesso")
                        
                        # Usar o agente AGNO para análise da imagem
                        # IMPORTANTE: Usar Gemini com capacidades multimodais
                        from agno.models.google import Gemini
                        from app.config import settings
                        
                        # Criar modelo Gemini com capacidades Vision
                        gemini_model = Gemini(
                            id="gemini-2.5-pro",  # Modelo principal com Vision API
                            api_key=settings.google_api_key
                        )
                        
                        # Criar agente temporário para análise de imagem com Gemini Vision
                        temp_agent = Agent(
                            model=gemini_model,
                            markdown=True,
                            show_tool_calls=False,
                            instructions="Você é um assistente especializado em análise de imagens e documentos. Extraia todas as informações relevantes de forma detalhada."
                        )
                        
                        # Processar imagem com AGNO nativo
                        emoji_logger.agentic_thinking("Enviando para AGNO Agent com Gemini Vision...")
                        response = temp_agent.run(
                            analysis_prompt,
                            images=[agno_image]
                        )
                        
                        # Extrair conteúdo da resposta AGNO
                        if hasattr(response, 'content'):
                            analysis_content = response.content
                        elif isinstance(response, dict) and 'content' in response:
                            analysis_content = response['content']
                        elif isinstance(response, str):
                            analysis_content = response
                        else:
                            analysis_content = str(response)
                            
                    except Exception as agno_error:
                        emoji_logger.system_warning(f"AGNO Image processamento falhou: {str(agno_error)}")
                        
                        # Fallback: tentar processamento direto com PIL+Gemini se AGNO falhar
                        from io import BytesIO
                        from PIL import Image as PILImage
                        import google.generativeai as genai
                        
                        try:
                            img = PILImage.open(BytesIO(image_bytes))
                            
                            # Configurar Gemini diretamente como fallback
                            from app.config import settings
                            genai.configure(api_key=settings.google_api_key)
                            model = genai.GenerativeModel('gemini-2.5-pro')
                            
                            # Enviar imagem com prompt
                            response = model.generate_content([analysis_prompt, img])
                            analysis_content = response.text if hasattr(response, 'text') else str(response)
                            
                            emoji_logger.system_info("Fallback PIL+Gemini bem-sucedido")
                            
                        except Exception as fallback_error:
                            emoji_logger.system_error("Fallback completo", f"Erro: {str(fallback_error)}")
                            return {
                                "type": "image",
                                "error": f"Não foi possível processar a imagem: {str(fallback_error)}",
                                "status": "error",
                                "suggestion": "Tente enviar a imagem em formato JPEG ou PNG"
                            }
                        
                    emoji_logger.agentic_multimodal("Análise de imagem concluída com sucesso")
                    
                    # Verificar se é conta de luz através da interpretação do Gemini
                    bill_keywords = ["conta", "energia", "kwh", "tarifa", "consumo", "fatura"]
                    is_bill = any(word in analysis_content.lower() for word in bill_keywords)
                    
                    if is_bill:
                        emoji_logger.agentic_multimodal("Conta de luz detectada", media_type="bill_image")
                        return {
                            "type": "bill_image",
                            "needs_analysis": True,
                            "content": analysis_content
                        }
                    else:
                        # Imagem genérica
                        return {
                            "type": "image",
                            "content": analysis_content,
                            "caption": caption,
                            "processed": True
                        }
                    
                except Exception as img_error:
                    emoji_logger.system_error("Vision API", f"Erro ao analisar imagem: {str(img_error)[:100]}")
                    
                    # Tentar extrair informações do erro para diagnóstico
                    error_details = str(img_error)
                    if "quota" in error_details.lower():
                        error_msg = "Limite de API excedido"
                    elif "invalid" in error_details.lower():
                        error_msg = "Formato de imagem inválido"
                    elif "timeout" in error_details.lower():
                        error_msg = "Timeout na análise"
                    else:
                        error_msg = f"Erro na análise: {str(img_error)[:100]}"
                    
                    return {
                        "type": "image",
                        "error": error_msg,
                        "status": "error",
                        "is_thumbnail": is_thumbnail
                    }
            
            elif media_type == "audio":
                # Processar áudio (transcrição)
                emoji_logger.system_info("Processamento de áudio solicitado")
                
                # Verificar se transcrição está habilitada
                if not self.settings.enable_voice_message_transcription:
                    return {
                        "type": "audio",
                        "status": "disabled",
                        "message": "Transcrição de áudio desabilitada"
                    }
                
                # Usar o novo AudioTranscriber
                try:
                    from app.services.audio_transcriber import audio_transcriber
                    
                    emoji_logger.agentic_thinking("Transcrevendo áudio com AudioTranscriber...")
                    
                    # Detectar mimetype do áudio (geralmente audio/ogg no WhatsApp)
                    mimetype = "audio/ogg"  # Padrão do WhatsApp
                    
                    # Transcrever
                    result = await audio_transcriber.transcribe_from_base64(
                        media_data,
                        mimetype=mimetype,
                        language="pt-BR"
                    )
                    
                    if result["status"] == "success":
                        # Processar transcrição com o agente
                        transcribed_text = result["text"]
                        
                        # Criar contexto para o agente
                        audio_context = f"""O cliente enviou um áudio dizendo:
                        
                        \"{transcribed_text}\"
                        
                        Por favor, responda adequadamente ao que foi dito no áudio."""
                        
                        # Processar com o agente
                        if hasattr(self.agent, 'arun'):
                            agent_response = await self.agent.arun(audio_context)
                        else:
                            agent_response = await self.agent.run(audio_context)
                        
                        emoji_logger.agentic_multimodal(
                            f"Audio transcrito com sucesso: {len(transcribed_text)} caracteres",
                            media_type="audio",
                            duration=result.get("duration", 0)
                        )
                        
                        return {
                            "type": "audio",
                            "transcription": transcribed_text,
                            "response": agent_response,
                            "duration": result.get("duration", 0),
                            "engine": result.get("engine", "unknown"),
                            "status": "transcribed"
                        }
                    elif result["status"] == "unclear":
                        return {
                            "type": "audio",
                            "status": "unclear",
                            "message": "Não foi possível compreender o áudio claramente",
                            "transcription": result.get("text", "")
                        }
                    else:
                        emoji_logger.system_warning(f"❌ ÁUDIO: Erro na transcrição")
                        emoji_logger.system_warning(f"  • Erro: {result.get('error', 'Erro desconhecido')}")
                        emoji_logger.system_warning(f"  • Tempo total: {time.time() - start_time:.2f}s")
                        return {
                            "type": "audio",
                            "status": "error",
                            "message": f"Erro na transcrição: {result.get('error', 'Erro desconhecido')}"
                        }
                        
                except Exception as e:
                    emoji_logger.system_warning(f"Erro ao transcrever áudio: {e}")
                    return {
                        "type": "audio",
                        "status": "error",
                        "message": f"Erro ao processar áudio: {str(e)}"
                    }
            
            elif media_type in ["document", "pdf"]:
                # AGNO Framework - Processamento nativo de documentos
                emoji_logger.agentic_multimodal("Processando documento com AGNO Framework nativo")
                
                try:
                    # AGNO Framework Solution: Usar document readers nativos
                    import base64
                    from io import BytesIO
                    
                    # Decodificar base64 para bytes
                    document_bytes = base64.b64decode(media_data)
                    original_size = len(document_bytes)
                    emoji_logger.agentic_multimodal(f"Documento decodificado: {original_size:,} bytes")
                    
                    # AGNO Framework - Detecção robusta de formato de documento
                    detection_result = self.agno_media_detector.detect_media_type(document_bytes)
                    
                    if not detection_result['detected']:
                        emoji_logger.system_warning(f"Formato de documento não reconhecido pelo AGNO: {detection_result.get('magic_bytes', 'N/A')}")
                        # Usar fallback suggestion
                        fallback_msg = detection_result.get('fallback_suggestion', 'Formato não suportado')
                        return {
                            "type": "document",
                            "error": f"Formato não suportado: {fallback_msg}",
                            "status": "unsupported_format",
                            "agno_detection": detection_result
                        }
                    
                    document_type = detection_result['format']
                    agno_params = detection_result['recommended_params']
                    is_pdf = document_type == 'pdf'
                    is_docx = document_type == 'docx'
                    
                    emoji_logger.agentic_thinking(f"AGNO detectou documento: {document_type} (confiança: {detection_result['confidence']})")
                    
                    # Determinar tipo e usar AGNO reader apropriado
                    extracted_text = ""
                    doc_metadata = {}
                    
                    if is_pdf:
                        try:
                            # AGNO PDFReader nativo
                            from agno.document import PDFReader
                            
                            emoji_logger.agentic_thinking("Usando AGNO PDFReader...")
                            
                            # Criar BytesIO stream para PDFReader
                            pdf_stream = BytesIO(document_bytes)
                            
                            # Usar AGNO PDFReader
                            pdf_reader = PDFReader(pdf=pdf_stream)
                            extracted_text = pdf_reader.read()
                            
                            document_type = "pdf"
                            doc_metadata = {
                                "reader": "agno_pdf_reader",
                                "format": "pdf",
                                "size_bytes": original_size
                            }
                            
                            emoji_logger.agentic_thinking("AGNO PDFReader processamento concluído")
                            
                        except Exception as pdf_error:
                            emoji_logger.system_warning(f"AGNO PDFReader falhou: {str(pdf_error)}")
                            
                            # Fallback para processamento manual se AGNO falhar
                            try:
                                import pypdf
                                from io import BytesIO
                                
                                pdf_stream = BytesIO(document_bytes)
                                reader = pypdf.PdfReader(pdf_stream)
                                
                                text_parts = []
                                for page_num, page in enumerate(reader.pages):
                                    page_text = page.extract_text()
                                    if page_text:
                                        text_parts.append(f"--- Página {page_num + 1} ---\n{page_text}")
                                
                                extracted_text = "\n\n".join(text_parts)
                                document_type = "pdf"
                                doc_metadata = {
                                    "reader": "pypdf_fallback",
                                    "format": "pdf",
                                    "pages": len(reader.pages),
                                    "size_bytes": original_size
                                }
                                
                                emoji_logger.system_info("Fallback pypdf bem-sucedido")
                                
                            except Exception as fallback_error:
                                raise Exception(f"PDF processing failed: {str(fallback_error)}")
                    
                    elif is_docx:
                        try:
                            # AGNO DocxReader nativo
                            from agno.document import DocxReader
                            
                            emoji_logger.agentic_thinking("Usando AGNO DocxReader...")
                            
                            # Criar BytesIO stream para DocxReader
                            docx_stream = BytesIO(document_bytes)
                            
                            # Usar AGNO DocxReader
                            docx_reader = DocxReader(file=docx_stream)
                            extracted_text = docx_reader.read()
                            
                            document_type = "docx"
                            doc_metadata = {
                                "reader": "agno_docx_reader",
                                "format": "docx",
                                "size_bytes": original_size
                            }
                            
                            emoji_logger.agentic_thinking("AGNO DocxReader processamento concluído")
                            
                        except Exception as docx_error:
                            emoji_logger.system_warning(f"AGNO DocxReader falhou: {str(docx_error)}")
                            
                            # Fallback para processamento manual se AGNO falhar
                            try:
                                import docx
                                from io import BytesIO
                                
                                docx_stream = BytesIO(document_bytes)
                                doc = docx.Document(docx_stream)
                                
                                paragraphs = []
                                for paragraph in doc.paragraphs:
                                    if paragraph.text.strip():
                                        paragraphs.append(paragraph.text.strip())
                                
                                extracted_text = "\n\n".join(paragraphs)
                                document_type = "docx"
                                doc_metadata = {
                                    "reader": "python_docx_fallback",
                                    "format": "docx",
                                    "paragraphs": len(paragraphs),
                                    "size_bytes": original_size
                                }
                                
                                emoji_logger.system_info("Fallback python-docx bem-sucedido")
                                
                            except Exception as fallback_error:
                                raise Exception(f"DOCX processing failed: {str(fallback_error)}")
                    
                    else:
                        # Formato não suportado pelos readers AGNO
                        raise Exception(f"Formato de documento não suportado. Magic bytes: {magic_bytes[:8].hex()}")
                    
                    # Processar resultado
                    result = {
                        "status": "success",
                        "text": extracted_text,
                        "document_type": document_type,
                        "metadata": doc_metadata
                    }
                    
                    if result["status"] == "success":
                        extracted_text = result["text"]
                        doc_type = result.get("document_type", "documento")
                        
                        # Criar contexto para o agente
                        doc_context = f"""O cliente enviou um {doc_type} com o seguinte conteúdo:
                        
                        {extracted_text[:3000]}...
                        
                        Documento completo: {result.get('pages', 'N/A')} página(s)
                        Tipo identificado: {doc_type}
                        
                        Por favor, analise o documento e:
                        1. Identifique as informações principais
                        2. Se for uma conta de luz, extraia valor e consumo
                        3. Se for outro documento, resuma os pontos importantes"""
                        
                        # Processar com o agente
                        if hasattr(self.agent, 'arun'):
                            agent_response = await self.agent.arun(doc_context)
                        else:
                            agent_response = await self.agent.run(doc_context)
                        
                        emoji_logger.agentic_multimodal(
                            f"Documento processado: {doc_type}, {len(extracted_text)} caracteres",
                            media_type="document",
                            pages=result.get("pages", 0)
                        )
                        
                        return {
                            "type": "document",
                            "document_type": doc_type,
                            "content": extracted_text[:5000],  # Limitar resposta
                            "analysis": agent_response,
                            "pages": result.get("pages", 0),
                            "method": result.get("method", "unknown"),
                            "status": "processed"
                        }
                    elif result["status"] == "no_text":
                        # PDF escaneado (precisa OCR)
                        return {
                            "type": "document",
                            "status": "scanned",
                            "message": "Documento parece ser escaneado. Tente enviar como imagem para análise visual.",
                            "pages": result.get("pages", 0)
                        }
                    else:
                        return {
                            "type": "document",
                            "status": "error",
                            "message": f"Erro ao processar documento: {result.get('error', 'Erro desconhecido')}"
                        }
                        
                except Exception as e:
                    emoji_logger.system_warning(f"Erro ao processar documento: {e}")
                    return {
                        "type": "document",
                        "status": "error",
                        "message": f"Erro ao processar documento: {str(e)}"
                    }
            
            elif media_type == "video":
                # Processar vídeo
                emoji_logger.system_info("Processamento de vídeo solicitado")
                return {
                    "type": "video",
                    "status": "not_supported",
                    "message": "Processamento de vídeo não implementado"
                }
            
            # Tipo desconhecido (não deveria chegar aqui devido à validação)
            return {
                "type": media_type,
                "processed": False,
                "message": f"Tipo {media_type} não tem processamento específico"
            }
            
        except Exception as e:
            # Log de erro detalhado
            emoji_logger.system_error("Multimodal Processing", f"Erro ao processar {media_type}: {str(e)[:200]}")
            logger.exception(f"Erro completo no processamento multimodal de {media_type}:")
            
            # Métricas finais de erro
            total_time = time.time() - start_time
            emoji_logger.system_info("═" * 50)
            emoji_logger.system_info(f"❌ MULTIMODAL: Processamento falhou")
            emoji_logger.system_info(f"  • Tipo: {media_type}")
            emoji_logger.system_info(f"  • Erro: {type(e).__name__}")
            emoji_logger.system_info(f"  • Mensagem: {str(e)[:100]}")
            emoji_logger.system_info(f"  • Tempo total: {total_time:.2f}s")
            emoji_logger.system_info("═" * 50)
            
            return {
                "type": media_type,
                "error": str(e),
                "status": "error",
                "message": f"Erro ao processar {media_type}",
                "processing_time": total_time
            }
    
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
        """Inicializa recursos do agente com fallback robusto"""
        try:
            # Carregar knowledge base do SUPABASE (não de arquivos locais!)
            await self._load_knowledge_from_supabase()
            
            # Inicializar SDR Team se necessário (com fallback)
            try:
                if not self.sdr_team:
                    from app.teams.sdr_team import create_sdr_team
                    self.sdr_team = create_sdr_team()
                    await self.sdr_team.initialize()
                    emoji_logger.system_ready("SDR Team inicializado")
            except Exception as team_error:
                emoji_logger.system_warning(f"SDR Team não inicializado: {str(team_error)[:50]}")
                self.sdr_team = None
                # Continuar sem SDR Team
            
            self.is_initialized = True
            emoji_logger.system_ready("AGENTIC SDR", startup_time=0.5)
            
        except Exception as e:
            emoji_logger.system_error("AGENTIC SDR", f"Erro crítico na inicialização: {e}")
            # Marcar como inicializado mesmo com erro para permitir funcionamento básico
            self.is_initialized = True
    
    async def _load_knowledge_from_supabase(self):
        """Carrega knowledge base diretamente do Supabase"""
        try:
            if not self.knowledge:
                emoji_logger.system_warning("AgentKnowledge não disponível - pulando carregamento")
                return
            
            emoji_logger.system_info("Carregando knowledge base do Supabase...")
            
            # Buscar documentos da tabela knowledge_base
            from app.integrations.supabase_client import supabase_client
            
            # Query para buscar todos os documentos ativos
            result = supabase_client.client.table("knowledge_base").select("*").execute()
            
            if result.data and len(result.data) > 0:
                # Processar cada documento
                docs_loaded = 0
                for doc in result.data:
                    try:
                        # Extrair campos do documento
                        doc_id = doc.get("id")
                        title = doc.get("title", "")
                        content = doc.get("content", "")
                        category = doc.get("category", "")
                        tags = doc.get("tags", [])
                        
                        # Verificar se tem conteúdo
                        if not content:
                            continue
                        
                        # Criar texto formatado para o knowledge base
                        formatted_text = f"""
                        Título: {title}
                        Categoria: {category}
                        Tags: {', '.join(tags) if tags else 'N/A'}
                        
                        {content}
                        """
                        
                        # Adicionar ao knowledge base usando método correto
                        if hasattr(self.knowledge, 'load_text'):
                            self.knowledge.load_text(
                                text=formatted_text,
                                metadata={
                                    "id": doc_id,
                                    "title": title,
                                    "category": category,
                                    "tags": tags,
                                    "source": "supabase"
                                }
                            )
                            docs_loaded += 1
                        elif hasattr(self.knowledge, 'add'):
                            self.knowledge.add(
                                text=formatted_text,
                                metadata={
                                    "id": doc_id,
                                    "title": title,
                                    "category": category,
                                    "tags": tags,
                                    "source": "supabase"
                                }
                            )
                            docs_loaded += 1
                            
                    except Exception as doc_error:
                        emoji_logger.system_warning(f"Erro ao carregar doc {doc.get('id')}: {str(doc_error)[:50]}")
                        continue
                
                emoji_logger.system_ready(f"Knowledge base carregada do Supabase", 
                                        documents_loaded=docs_loaded,
                                        total_documents=len(result.data))
            else:
                emoji_logger.system_warning("Nenhum documento encontrado na knowledge_base do Supabase")
                
        except Exception as e:
            emoji_logger.system_error("Knowledge Base Loader", f"Erro ao carregar do Supabase: {str(e)[:100]}")
            # Não lançar erro - continuar sem knowledge base
    
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
        # Inicializar response para evitar erro de variável não definida
        response = None
        
        try:
            emoji_logger.agentic_thinking(f"Processando mensagem de {phone}: {message[:50]}...")
            
            if not self.is_initialized:
                await self.initialize()
            
            # 1. Tentar análise contextual (com fallback)
            try:
                # Verificar se a função está disponível e é callable
                if hasattr(self, 'analyze_conversation_context') and callable(self.analyze_conversation_context):
                    context_analysis = await self.analyze_conversation_context(phone, message)
                else:
                    raise AttributeError("analyze_conversation_context não está disponível")
            except Exception as ctx_error:
                emoji_logger.system_warning(f"Análise contextual falhou: {str(ctx_error)}")
                # Fallback para contexto básico
                context_analysis = {
                    "primary_context": ConversationContext.INITIAL_CONTACT.value,
                    "lead_engagement_level": "medium",
                    "decision_stage": "awareness",
                    "recommended_action": "Continuar conversa naturalmente"
                }
            
            # 2. Detectar gatilhos emocionais e obter histórico (com fallback)
            messages_history = []
            try:
                # Buscar histórico de mensagens (será usado para contexto e análise emocional)
                messages_history = await self.get_last_100_messages(conversation_id) if conversation_id else []
                emoji_logger.system_info(f"Histórico carregado: {len(messages_history)} mensagens")
                emotional_triggers = await self.detect_emotional_triggers(messages_history)
            except Exception as emo_error:
                emoji_logger.system_warning(f"Análise emocional falhou: {str(emo_error)[:50]}")
                emotional_triggers = {"dominant_emotion": "neutral", "enabled": False}
            
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
            
            # 4. Decidir inteligentemente sobre SDR Team (com fallback)
            try:
                should_call, recommended_agent, reasoning = await self.should_call_sdr_team(
                    context_analysis,
                    message
                )
            except Exception as decision_error:
                emoji_logger.system_warning(f"Decisão SDR Team falhou: {str(decision_error)[:50]}")
                should_call = False
                recommended_agent = None
                reasoning = "Processamento direto devido a erro"
            
            # 5. Se precisar do SDR Team E contexto justificar
            if should_call and recommended_agent and self.sdr_team:
                try:
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
                except Exception as team_error:
                    emoji_logger.system_warning(f"SDR Team falhou: {str(team_error)[:50]}")
                    # Fallback para resposta direta
                    response = None
                
            # Se não tem resposta do Team ou não chamou Team
            if not response:
                # 6. AGENTIC SDR resolve sozinha (90% dos casos)
                emoji_logger.agentic_thinking("Processando mensagem diretamente")
                
                try:
                    # Formatar contexto com AGNO Framework (enhanced formatting)
                    formatted_history = format_context_with_agno(
                        message_history=messages_history or [],
                        multimodal_result=multimodal_result,
                        phone=phone
                    )
                    
                    # AGNO Framework já formatou multimodal + histórico no formatted_history
                    
                    # Preparar prompt com contexto completo AGNO-enhanced
                    contextual_prompt = f"""
                    CONTEXTO DO LEAD:
                    - Nome: {lead_data.get('name', 'Não informado') if lead_data else 'Não informado'}
                    - Telefone: {phone}
                    - Estágio: {lead_data.get('current_stage', 'INITIAL_CONTACT') if lead_data else 'INITIAL_CONTACT'}
                    - Status: {lead_data.get('qualification_status', 'PENDING') if lead_data else 'PENDING'}
                    
                    {formatted_history}
                    
                    MENSAGEM ATUAL DO CLIENTE: {message}
                    
                    Análise Contextual:
                    - Contexto Principal: {context_analysis.get('primary_context')}
                    - Engajamento: {context_analysis.get('lead_engagement_level')}
                    - Estágio: {context_analysis.get('decision_stage')}
                    - Ação Recomendada: {context_analysis.get('recommended_action')}
                    
                    Estado Emocional do Lead:
                    - Emoção Dominante: {emotional_triggers.get('dominant_emotion')}
                    - Urgência: {context_analysis.get('urgency_level')}
                    
                    Responda de forma natural, empática e personalizada, levando em conta todo o contexto e histórico da conversa.
                    """
                    
                    # Usar reasoning para casos complexos
                    # Em AGNO v1.7.6, usar run()
                    if self.reasoning_enabled and context_analysis.get("complexity_score", 0) > 0.5:
                        result = await self.reasoning_model.run(contextual_prompt)
                    else:
                        # Usar arun() para suporte assíncrono
                        if hasattr(self.agent, 'arun'):
                            result = await self.agent.arun(contextual_prompt)
                        else:
                            # Fallback para run() se arun() não estiver disponível
                            result = await self.agent.run(contextual_prompt)
                    
                    response = result.content if hasattr(result, 'content') else str(result)
                    
                except Exception as agent_error:
                    emoji_logger.system_error("AGENTIC SDR", f"Erro ao gerar resposta: {agent_error}")
                    # Fallback para resposta padrão
                    response = None
            
            # Garantir que SEMPRE temos uma resposta
            if not response or response.strip() == "":
                emoji_logger.system_warning("Nenhuma resposta gerada, usando fallback")
                # Resposta fallback baseada no contexto
                if "oi" in message.lower() or "olá" in message.lower() or "ola" in message.lower():
                    response = "Oi! 😊 Tudo bem? Sou a Helen da Solar Prime! Como posso ajudar você hoje?"
                elif "bom dia" in message.lower():
                    response = "Bom dia! ☀️ Que legal você entrar em contato! Sou a Helen da Solar Prime. Em que posso ajudar?"
                elif "boa tarde" in message.lower():
                    response = "Boa tarde! 😊 Obrigada por entrar em contato com a Solar Prime! Sou a Helen, como posso ajudar?"
                elif "boa noite" in message.lower():
                    response = "Boa noite! 🌙 Que bom falar com você! Sou a Helen da Solar Prime. Como posso ajudar?"
                else:
                    response = "Olá! Sou a Helen da Solar Prime 😊 Vi sua mensagem e adoraria ajudar! Você tem interesse em economizar na conta de luz com energia solar?"
            
            # 7. Ajustar estado emocional da Helen
            try:
                self._update_emotional_state(emotional_triggers, context_analysis)
            except:
                pass  # Ignorar erros não críticos
            
            # 8. Memória é gerenciada automaticamente pelo Agent no AGNO v1.7.6
            # O Agent salva automaticamente as interações quando configurado com memory
            # Não precisa chamar explicitamente memory.add()
            
            # 9. Aplicar simulação de digitação natural
            # Garantir que response tem um valor antes de aplicar simulação
            if response:
                response = self._apply_typing_simulation(response)
            else:
                # Fallback final se ainda não houver resposta
                response = "Oi! 😊 Sou a Helen da Solar Prime. Como posso ajudar você hoje?"
            
            emoji_logger.agentic_response(f"Resposta gerada: {response[:100]}...")
            
            return response
            
        except Exception as e:
            emoji_logger.system_error("AGENTIC SDR", f"Erro crítico ao processar: {e}")
            # Resposta de emergência mais natural
            emergency_responses = [
                "Oi! 😊 Sou a Helen da Solar Prime! Como posso ajudar você hoje com energia solar?",
                "Olá! Que bom você entrar em contato! 🌟 Sou a Helen, especialista em energia solar. Em que posso ajudar?",
                "Oi! Tudo bem? Sou a Helen da Solar Prime! 💚 Você tem interesse em economizar na conta de luz?"
            ]
            import random
            return random.choice(emergency_responses)
    
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
        
        # Em AGNO v1.7.6, usar run()
        # Usar arun() para suporte assíncrono
        if hasattr(self.agent, 'arun'):
            result = await self.agent.arun(personalization_prompt)
        else:
            # Fallback para run() se arun() não estiver disponível
            result = await self.agent.run(personalization_prompt)
        return result.content if hasattr(result, 'content') else str(result)
    
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
        """Retorna o texto sem modificação - typing é feito via Evolution API"""
        # IMPORTANTE: Esta função NÃO deve modificar o texto!
        # O indicador "digitando..." é enviado corretamente via Evolution API em webhooks.py
        # Qualquer quebra de linha aqui causa problemas no WhatsApp
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