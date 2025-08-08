"""
AGENTIC SDR - Agente Principal Conversacional Ultra-Humanizado
Com análise contextual inteligente das últimas 100 mensagens
"""

import asyncio
import json
import random
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import base64

from agno.agent import Agent
from agno.models.google import Gemini
# OpenAI via requests - contorna problemas do SDK
try:
    import requests
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.utils.time_utils import get_period_of_day


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
                "max_completion_tokens": self.max_tokens  # o3-mini usa max_completion_tokens, sem temperature
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
from agno.knowledge import AgentKnowledge
from agno.tools import tool
from loguru import logger
from app.utils.logger import emoji_logger
from app.utils.optional_storage import OptionalStorage
from app.utils.agno_media_detection import agno_media_detector
from app.utils.retry_handler import async_retry, GEMINI_RETRY_CONFIG, OPENAI_RETRY_CONFIG

from app.config import settings
from app.integrations.supabase_client import supabase_client
from app.teams.sdr_team import SDRTeam

# Serviços REMOVIDOS - substituídos por funções simples inline
# from app.services.agno_context_agent import format_context_with_agno
# from app.services.document_processor_enhanced import process_document_enhanced
# KnowledgeService - Substitui KnowledgeAgent com implementação mais simples
from app.services.knowledge_service import knowledge_service


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
        
        # Armazenar instructions do agente principal
        self._agent_instructions = None
        
        self._initialize_models()
    
    def set_agent_instructions(self, instructions):
        """Define as instructions do agente principal para usar nos temp_agents"""
        self._agent_instructions = instructions
    
    @property
    def id(self):
        """Expõe o ID do modelo atual para compatibilidade com agno.agent.Agent"""
        if self.current_model:
            return self.current_model.id
        return "unknown_model"
    
    @property
    def provider(self):
        """Expõe o provider do modelo atual para compatibilidade com agno.agent.Agent"""
        if self.current_model and hasattr(self.current_model, 'provider'):
            return self.current_model.provider
        # Inferir provider do ID do modelo
        if self.current_model and hasattr(self.current_model, 'id'):
            model_id = self.current_model.id
            if 'gemini' in model_id.lower():
                return 'google'
            elif 'gpt' in model_id.lower() or 'o3' in model_id.lower():
                return 'openai'
        return "unknown"
    
    def __getattr__(self, name):
        """
        Delega qualquer atributo/método não encontrado para o modelo atual.
        Isso garante compatibilidade total com agno.agent.Agent.
        """
        if name.startswith('_'):  # Evitar recursão infinita com atributos privados
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        if self.current_model is None:
            raise AttributeError(f"No current model available to delegate '{name}'")
        
        # Tentar obter o atributo/método do modelo atual
        try:
            return getattr(self.current_model, name)
        except AttributeError:
            # Se o modelo atual não tem o atributo, retornar um valor padrão ou função vazia
            if name == 'get_instructions_for_model':
                # Retornar função vazia que retorna string vazia
                return lambda: ""
            raise AttributeError(f"'{self.__class__.__name__}' object and current model have no attribute '{name}'")
    
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
            emoji_logger.system_error("Model Init", f"Erro na inicialização de modelos: {e}")
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
    
    @async_retry(GEMINI_RETRY_CONFIG)
    async def _gemini_call_with_retry(self, message: str, **kwargs):
        """Chamada Gemini com retry automático via decorador"""
        if self.primary_model:
            # SOLUÇÃO DEFINITIVA: Usar arun() para async ou asyncio.to_thread para sync
            from agno.agent import Agent
            import asyncio
            
            # Usar instructions do agente principal se disponível, senão usar padrão
            instructions = self._agent_instructions or kwargs.pop('instructions', 'Você é Helen, uma vendedora especializada em energia solar da SolarPrime. Responda de forma natural, empática e focada em ajudar o cliente.')
            
            temp_agent = Agent(
                model=self.primary_model,
                markdown=True,
                show_tool_calls=False,
                instructions=instructions
            )
            
            # Verificar se tem arun (async) ou usar run em thread
            if hasattr(temp_agent, 'arun'):
                response = await temp_agent.arun(message, **kwargs)
            else:
                # Executar run() síncrono em thread para não bloquear
                response = await asyncio.to_thread(temp_agent.run, message, **kwargs)
            
            # CORREÇÃO: Extrair conteúdo do RunResponse se necessário
            if hasattr(response, 'content') and response.content is not None:
                return response.content
            elif hasattr(response, 'text') and response.text is not None:
                return response.text
            elif hasattr(response, 'message') and response.message is not None:
                return response.message
            elif isinstance(response, str):
                return response
            else:
                # Se for dict ou outro tipo, tentar extrair conteúdo
                if isinstance(response, dict):
                    return response.get('content') or response.get('text') or response.get('message') or str(response)
                return str(response)
            
        raise Exception("Modelo primário Gemini não disponível")
    
    @async_retry(OPENAI_RETRY_CONFIG)
    async def _openai_call_with_retry(self, message: str, **kwargs):
        """Chamada OpenAI com retry automático via decorador"""
        if self.fallback_model:
            # OpenAI wrapper tem run() implementado
            return self.fallback_model.run(message, **kwargs)
        raise Exception("Modelo fallback OpenAI não disponível")
    
    async def _retry_with_backoff(self, message: str, **kwargs):
        """
        Tenta executar o Gemini com retry e backoff
        Retorna a resposta ou None se todas as tentativas falharem
        """
        import asyncio
        from agno.agent import Agent
        
        last_error = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                emoji_logger.system_info(f"🔄 Retry Gemini - Tentativa {attempt + 1}/{self.max_retry_attempts}")
                
                # O Gemini no AGNO precisa ser usado através de um Agent
                # Usar instructions do agente principal se disponível, senão usar padrão
                instructions = self._agent_instructions or kwargs.pop('instructions', 'Você é Helen, uma vendedora especializada em energia solar da SolarPrime. Responda de forma natural, empática e focada em ajudar o cliente.')
                
                temp_agent = Agent(
                    model=self.primary_model,
                    markdown=True,
                    show_tool_calls=False,
                    instructions=instructions
                )
                
                # Usar arun se disponível, senão run em thread
                if hasattr(temp_agent, 'arun'):
                    response = await temp_agent.arun(message, **kwargs)
                else:
                    response = await asyncio.to_thread(temp_agent.run, message, **kwargs)
                
                if attempt > 0:
                    emoji_logger.system_ready(f"✅ Gemini recuperado após {attempt + 1} tentativa(s)")
                
                # CORREÇÃO: Extrair conteúdo do RunResponse se necessário
                if hasattr(response, 'content') and response.content is not None:
                    return response.content
                elif hasattr(response, 'text') and response.text is not None:
                    return response.text
                elif hasattr(response, 'message') and response.message is not None:
                    return response.message
                elif isinstance(response, str):
                    return response
                else:
                    # Se for dict ou outro tipo, tentar extrair conteúdo
                    if isinstance(response, dict):
                        return response.get('content') or response.get('text') or response.get('message') or str(response)
                    return str(response)
                
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
        # Se já estamos usando fallback, usa direto com retry
        if self.fallback_active and self.current_model == self.fallback_model:
            try:
                response = await self._openai_call_with_retry(message, **kwargs)
                emoji_logger.system_info("📍 Usando fallback OpenAI o3-mini com retry")
                return response
            except Exception as e:
                emoji_logger.system_error("Fallback OpenAI falhou após múltiplas tentativas", error=str(e))
                raise e
        
        # Tenta com modelo primário (Gemini) usando retry automático
        try:
            if self.primary_model:
                response = await self._gemini_call_with_retry(message, **kwargs)
                
                # Se estava usando fallback e Gemini funcionou, desativa fallback
                if self.fallback_active:
                    emoji_logger.system_ready("✅ Gemini recuperado, desativando fallback")
                    self.fallback_active = False
                    self.current_model = self.primary_model
                
                return response
                
        except Exception as e:
            emoji_logger.system_warning(f"⚠️ Gemini falhou após múltiplas tentativas: {e}")
            
            # Se temos fallback, ativa OpenAI com retry
            if self.fallback_model is not None:
                emoji_logger.system_warning("🔄 Ativando fallback OpenAI o3-mini com retry...")
                
                try:
                    self.current_model = self.fallback_model
                    self.fallback_active = True
                    
                    response = await self._openai_call_with_retry(message, **kwargs)
                    emoji_logger.system_ready("✅ Fallback OpenAI o3-mini ativado com sucesso")
                    return response
                        
                except Exception as fallback_error:
                    emoji_logger.system_error("Fallback OpenAI também falhou", error=str(fallback_error))
                    # Volta para modelo primário para próxima tentativa
                    self.current_model = self.primary_model
                    self.fallback_active = False
                    raise fallback_error
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
    
    # Alias para compatibilidade com AGNO Agent
    async def arun(self, message: str, **kwargs):
        """Alias para run() - mantém compatibilidade com AGNO Agent que espera arun()"""
        return await self.run(message, **kwargs)


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
    """Estados emocionais do AGENTIC SDR - Alinhados com banco de dados"""
    ENTUSIASMADA = "ENTUSIASMADA"
    CURIOSA = "CURIOSA"
    CONFIANTE = "CONFIANTE"
    DUVIDOSA = "DUVIDOSA"
    NEUTRA = "NEUTRA"


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
        
        # Cache removido - sempre buscar histórico atualizado do Supabase
        self.sentiment_analysis_enabled = settings.enable_sentiment_analysis
        self.emotional_triggers_enabled = settings.enable_emotional_triggers
        self.lead_scoring_enabled = settings.enable_lead_scoring
        self.emoji_usage_enabled = settings.enable_emoji_usage
        
        # REMOVIDO: Estado emocional como atributo de instância
        # Agora o estado é gerenciado por conversa no banco de dados
        
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
        
        # Memory v2 - SOLUÇÃO DEFINITIVA (conforme ANALISE_ERRO_AGENTMEMORY.md)
        # AgentMemory agora é apenas para memória de trabalho (RAM), sem db
        # O storage é passado diretamente para o Agent, não para AgentMemory
        try:
            # CORREÇÃO: AgentMemory sem parâmetro db (arquitetura nova do AGNO)
            self.memory = AgentMemory(
                create_user_memories=True,
                create_session_summary=True
            )
            emoji_logger.system_ready("Memory", status="configurada (in-memory)")
        except Exception as e:
            emoji_logger.system_info(f"Memory fallback: {str(e)[:100]}...")
            # Se AgentMemory falhar completamente, usar None
            # O Agent da AGNO aceita memory=None
            self.memory = None
            emoji_logger.system_info("💾 Memory: Desabilitado (Agent funcionará sem memória)")
        
        # Knowledge base SEM PostgreSQL - usando apenas dados locais
        # Sistema funciona perfeitamente sem vector database PostgreSQL
        try:
            # AgentKnowledge sem vector_db (usa conhecimento local)
            self.knowledge = AgentKnowledge(
                num_documents=10  # Busca em conhecimento local/memória
            )
            self.vector_db = None  # Não precisamos de PostgreSQL
            emoji_logger.system_ready("Knowledge", status="local ativo")
        except Exception as e:
            emoji_logger.system_info(f"Knowledge desabilitado: {str(e)[:40]}...")
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
            self.tools.append(self.analyze_energy_bill)
        
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
                        include_thoughts=False  # ✅ CORRIGIDO: Não vazar raciocínio interno para usuário
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
            emoji_logger.system_error("Model Config", f"Erro crítico na configuração de modelos: {e}")
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
            model=self.intelligent_model,  # CORREÇÃO: Passar o wrapper, não o modelo direto
            instructions=enhanced_prompt,
            tools=self.tools,
            storage=self.storage,  # CORREÇÃO: Passar storage diretamente para o Agent
            memory=self.memory,    # Passar a memória simples (ou None se falhou)
            knowledge=self.knowledge,
            show_tool_calls=False,
            markdown=True,
            debug_mode=settings.debug,
            # Context includes personality configurations
            context={
                "emotional_state": "ENTUSIASMADA",  # Estado padrão, será sobrescrito em process_message
                "cognitive_load": 0.0,
                "current_time": datetime.now().strftime("%H:%M"),
                "day_of_week": datetime.now().strftime("%A"),
                "period_of_day": get_period_of_day(settings.timezone)  # Manhã, Tarde ou Noite
            }
        )
        
        # Configurar as instructions no modelo wrapper para uso em temp_agents
        if hasattr(self.intelligent_model, 'set_agent_instructions'):
            self.intelligent_model.set_agent_instructions(enhanced_prompt)
    
    def _is_complex_message(self, message: str) -> bool:
        """
        Determina se a mensagem é complexa e requer reasoning (OTIMIZADO)
        
        Critérios mais restritivos para economizar tempo:
        - Mensagens muito curtas (< 15 chars) = simples
        - Saudações e respostas diretas = simples
        - Apenas perguntas ELABORADAS = complexa
        """
        message_lower = message.lower().strip()
        
        # Mensagens muito curtas são sempre simples - AUMENTADO DE 10 PARA 15
        if len(message_lower) < 15:
            return False
            
        # Respostas diretas que NÃO precisam reasoning - EXPANDIDO
        simple_responses = {
            'oi', 'olá', 'bom dia', 'boa tarde', 'boa noite',
            'tudo bem', 'tudo certo', 'sim', 'não', 'ok', 'certo', 
            'beleza', 'entendi', 'pode ser', 'claro', 'com certeza',
            'obrigado', 'obrigada', 'tchau', 'até mais', 'valeu',
            'ta bom', 'ta ok', 'legal', 'ótimo', 'perfeito',
            'isso', 'isso mesmo', 'exato', 'concordo'
        }
        
        # Se é uma resposta simples, não precisa reasoning
        if message_lower in simple_responses or any(
            message_lower.startswith(resp) and len(message_lower) < 25 
            for resp in simple_responses
        ):
            return False
        
        # SÓ ativar reasoning para questões REALMENTE complexas
        complex_indicators = [
            'como funciona', 'me explica', 'não entendi',
            'quanto custa', 'qual o valor', 'economia',
            'comparar', 'diferença', 'vantagem',
            'garantia', 'manutenção', 'instalação',
            'o que é', 'por que', 'quando'
        ]
        
        # Precisa ter pelo menos 2 indicadores OU pergunta muito elaborada
        indicator_count = sum(1 for ind in complex_indicators if ind in message_lower)
        has_multiple_questions = message.count('?') > 1
        is_long_question = '?' in message and len(message) > 50
        
        return indicator_count >= 2 or has_multiple_questions or is_long_question
    
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
        Busca as últimas 100 mensagens do Supabase (sempre atualizado)
        
        Args:
            identifier: Número do telefone ou conversation_id
            
        Returns:
            Lista com últimas 100 mensagens
        """
        
        # LOG CRÍTICO: Rastrear todas as chamadas
        emoji_logger.system_info(f"🔍 HISTÓRICO: Buscando mensagens para identifier={identifier}")
        
        # Validação de entrada
        if not identifier:
            emoji_logger.system_error("HISTÓRICO", "❌ Identifier vazio ou None!")
            return []
        
        try:
            # VALIDAÇÃO: Verificar se identifier é válido
            if not identifier:
                emoji_logger.system_warning("get_last_100_messages chamado com identifier None ou vazio")
                return []
                
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
            
            # GARANTIR que sempre tentamos buscar 100 mensagens
            query = supabase_client.client.table("messages")\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=True)\
                .limit(100)
            
            response = query.execute()  # Removido await - cliente síncrono
            messages = response.data if response.data else []
            
            # Log detalhado para debug
            emoji_logger.system_info(f"📊 QUERY EXECUTADA:")
            emoji_logger.system_info(f"  • Conversation ID: {conversation_id}")
            emoji_logger.system_info(f"  • Mensagens encontradas: {len(messages)}")
            emoji_logger.system_info(f"  • Limite solicitado: 100")
            
            # Log das primeiras e últimas mensagens para debug
            if messages:
                first_msg = messages[0]
                last_msg = messages[-1]
                emoji_logger.system_info(f"  • Primeira msg: {first_msg.get('created_at', 'N/A')} - {first_msg.get('sender', 'N/A')}")
                emoji_logger.system_info(f"  • Última msg: {last_msg.get('created_at', 'N/A')} - {last_msg.get('sender', 'N/A')}")
            
            # Se encontrou menos de 100 mensagens, informar
            if len(messages) < 100:
                emoji_logger.system_warning(f"Apenas {len(messages)} mensagens disponíveis (menos que o limite de 100)")
            
            # Reverter para ordem cronológica
            messages.reverse()
            
            # Log de sucesso com informação completa
            success_msg = f"Mensagens recuperadas: {len(messages)}"
            if len(messages) < 100:
                success_msg += f" (conversa tem apenas {len(messages)} mensagens no total)"
            else:
                success_msg += " (limite de 100 atingido)"
                
            emoji_logger.supabase_success(success_msg, execution_time=0.1)
            
            # Retornar mensagens diretamente (sem cache)
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
        
        # Fator 1: Complexidade da solicitação - CALENDÁRIO
        # ✅ CORRIGIDO: Keywords específicas para evitar falsos positivos
        calendar_keywords = [
            "agendar reunião", "marcar reunião", "marcar encontro", "marcar meeting",
            "horário para reunião", "disponibilidade para", "agenda disponível",
            "calendário livre", "encontro para", "meeting para", "apresentação comercial",
            "reagendar", "remarcar reunião", "cancelar reunião",
            "que dia pode ser", "qual horário", "quando podemos nos reunir",
            "semana que vem para reunião", "próxima semana reunião", 
            "amanhã para reunião", "hoje para reunião", "vamos marcar",
            # NOVO: Detecção específica da agenda do Leonardo
            "agenda do leonardo", "horários disponíveis", "leonardo está disponível",
            "leonardo pode", "disponibilidade do leonardo", "quando leonardo pode",
            "consultar agenda", "verificar agenda", "ver agenda", "checar agenda"
        ]
        
        # ✅ NOVO: Filtro de saudação para evitar falsos positivos
        greeting_indicators = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "tudo bem", "tchau", "obrigado"]
        is_simple_greeting = any(greeting in current_message.lower() for greeting in greeting_indicators) and len(current_message.split()) <= 5
        
        # ✅ CORRIGIDO: Indicadores negativos para agendamento
        negative_indicators = ["não", "nao", "sem interesse", "não quero", "já tenho", "não pedi"]
        has_negative_context = any(neg in current_message.lower() for neg in negative_indicators)
        
        # VERIFICAR SE É FOLLOW-UP/REENGAJAMENTO antes de detectar calendário
        followup_indicators = ["reengajamento", "follow-up", "não é agendamento", "parou de responder"]
        is_followup_message = any(indicator in current_message.lower() for indicator in followup_indicators)
        
        # ✅ NOVO: Detecção de alta confiança para agenda do Leonardo
        high_confidence_calendar = any(phrase in current_message.lower() for phrase in [
            "agenda do leonardo", "verificar agenda", "consultar agenda", 
            "horários disponíveis", "leonardo está disponível"
        ])
        
        # ✅ CORRIGIDO: Lógica mais inteligente para detectar agendamento REAL
        calendar_detected = any(word in current_message.lower() for word in calendar_keywords)
        is_real_calendar_request = calendar_detected and not is_simple_greeting and not has_negative_context and not is_followup_message
        
        # RETORNO IMEDIATO para alta confiança
        if high_confidence_calendar and not has_negative_context:
            logger.info("🚨 ALTA CONFIANÇA: Detecção de agenda do Leonardo - retornando imediatamente!")
            return True, "CalendarAgent", "Alta confiança: Solicitação explícita de verificação de agenda"
        
        if is_real_calendar_request:
            # ✅ CORRIGIDO: Score mais alto para garantir ativação
            decision_factors["complexity_score"] += 0.8  # Aumentado para 0.8
            decision_factors["recommended_agent"] = "CalendarAgent"
            decision_factors["reasoning"].append("🗓️ Solicitação de agendamento detectada - Ativando CalendarAgent")
            
            # Log detalhado para debug
            logger.info(f"📅 CALENDÁRIO DETECTADO - Score: {decision_factors['complexity_score']}")
            logger.info(f"📅 Mensagem: {current_message[:100]}...")
            logger.info(f"📅 Agent recomendado: CalendarAgent")
        elif is_followup_message:
            # É uma mensagem de follow-up, não de agendamento
            decision_factors["reasoning"].append("🔄 Mensagem de follow-up detectada - evitando CalendarAgent")
            logger.info(f"🔄 FOLLOW-UP DETECTADO - Evitando CalendarAgent")
            logger.info(f"🔄 Mensagem: {current_message[:100]}...")
        
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
        # REDUZIDO de 0.7 para 0.3 para ser mais sensível
        should_call = decision_factors["complexity_score"] >= 0.3
        
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
    
    def _get_media_type_from_mimetype(self, mimetype: str) -> str:
        """
        Mapeia mimetype para tipo de mídia
        SIMPLES E FUNCIONAL!
        """
        if not mimetype:
            return "unknown"
        
        mimetype_lower = mimetype.lower()
        
        # Mapeamento simples e direto
        if "image" in mimetype_lower:
            return "image"
        elif "audio" in mimetype_lower:
            return "audio"
        elif "video" in mimetype_lower:
            return "video"
        elif "pdf" in mimetype_lower:
            return "pdf"
        elif mimetype_lower in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return "document"
        elif "sticker" in mimetype_lower or "webp" in mimetype_lower:
            return "sticker"
        else:
            return "document"  # Default para documentos
    
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
        import asyncio
        start_time = time.time()
        
        # Configurar timeout de 30 segundos para todo o processamento
        MULTIMODAL_TIMEOUT = 30
        
        async def process_with_timeout():
            """Processa mídia com timeout"""
            # Usar nonlocal para acessar variáveis do escopo externo
            nonlocal media_data
            
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
                
                # Validar qualidade da imagem ANTES de enviar
                try:
                    import base64 as b64_module
                    from PIL import Image
                    from io import BytesIO
                    
                    # Decodificar imagem
                    img_bytes = b64_module.b64decode(media_data)
                    img = Image.open(BytesIO(img_bytes))
                    width, height = img.size
                    
                    emoji_logger.system_info(f"📐 IMAGEM - Dimensões: {width}x{height} pixels")
                    
                    # Validar tamanho mínimo (100x100)
                    if width < 100 or height < 100:
                        emoji_logger.system_error("Image Validation", f"❌ IMAGEM: Muito pequena ({width}x{height}). Mínimo: 100x100")
                        return {
                            "type": "image",
                            "error": f"Imagem muito pequena ({width}x{height} pixels). Envie uma imagem maior que 100x100.",
                            "status": "too_small",
                            "dimensions": {"width": width, "height": height}
                        }
                    
                    # Validar tamanho máximo (10MB)
                    if len(img_bytes) > 10 * 1024 * 1024:
                        emoji_logger.system_error("Image Validation", f"❌ IMAGEM: Muito grande ({len(img_bytes) / 1024 / 1024:.1f}MB). Máximo: 10MB")
                        return {
                            "type": "image",
                            "error": "Imagem muito grande. Por favor, envie uma imagem menor que 10MB.",
                            "status": "too_large",
                            "size_mb": len(img_bytes) / 1024 / 1024
                        }
                    
                    # Avisos sobre qualidade
                    if data_size < 50000:  # Menos de 50KB em base64
                        emoji_logger.system_warning("⚠️ IMAGEM: Possível thumbnail detectada (<50KB)")
                    elif estimated_mb > 2:
                        emoji_logger.system_warning(f"⚠️ IMAGEM: Tamanho grande ({estimated_mb:.2f} MB) - pode causar lentidão")
                    
                except Exception as val_error:
                    emoji_logger.system_error("Image Validation", f"❌ Erro ao validar imagem: {str(val_error)}")
                    # Continuar mesmo com erro de validação
                
                # Preparar prompt específico para análise (simplificado para evitar erros)
                analysis_prompt = f"""Analise esta imagem e extraia as informações visíveis.
{f'Contexto: {caption}' if caption else ''}

Retorne em formato estruturado:
- Tipo de documento
- Valores encontrados
- Datas
- Nomes ou empresas
- Outras informações relevantes"""
                
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
                        # Usar fallback suggestion
                        fallback_msg = detection_result.get('fallback_suggestion', 'Formato não suportado')
                        return {
                            "type": "image",
                            "error": f"Formato não suportado: {fallback_msg}",
                            "status": "unsupported_format",
                            "agno_detection": detection_result
                        }
                    else:
                        emoji_logger.system_info(f"✅ Formato detectado: {detection_result['format'].upper()}")
                        emoji_logger.system_info(f"  • Confiança: {detection_result.get('confidence', 'N/A')}")
                        emoji_logger.system_info(f"  • Tempo detecção: {detect_time:.2f}s")
                    
                    format_hint = detection_result.get('format', 'unknown')
                    
                    # Verificar se recommended_params existe antes de acessar
                    if 'recommended_params' in detection_result:
                        agno_params = detection_result['recommended_params']
                    else:
                        # Usar parâmetros padrão se não houver recomendação
                        logger.warning(f"⚠️ Sem recommended_params para formato: {format_hint}")
                        agno_params = {
                            'format': 'auto',
                            'detail': 'high'
                        }
                    
                    emoji_logger.agentic_thinking(f"AGNO detectou: {format_hint} (confiança: {detection_result.get('confidence', 'unknown')})")
                    
                    # 🔧 CORREÇÃO MULTIMODAL: Usar PIL + Gemini diretamente (sem AGNO)
                    # Esta correção resolve o erro 400 INVALID_ARGUMENT e a latência de 42s
                    emoji_logger.system_info("🔧 Usando PIL + Gemini direto (correção implementada)")
                    
                    try:
                        # Processamento direto com PIL + Gemini (sem AGNO Framework)
                        from io import BytesIO
                        from PIL import Image as PILImage
                        import google.generativeai as genai
                        
                        # Decodificar base64 para usar com PIL
                        img_bytes = base64.b64decode(media_data)
                        img = PILImage.open(BytesIO(img_bytes))
                        
                        # Configurar Gemini com modelo Vision correto
                        from app.config import settings
                        genai.configure(api_key=settings.google_api_key)
                        vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Modelo com capacidade vision
                        
                        # Prompt específico para análise de contas de energia
                        if "conta" in analysis_prompt.lower() or "energia" in analysis_prompt.lower():
                            enhanced_prompt = """Analise esta conta de energia elétrica e extraia as seguintes informações:
                            1. Valor total a pagar (em R$)
                            2. Consumo mensal em kWh
                            3. Nome completo do titular da conta
                            4. Endereço completo da instalação
                            5. Mês de referência da conta
                            6. Vencimento da fatura
                            
                            Responda em formato estruturado e claro. Se não conseguir identificar alguma informação, indique como "Não identificado"."""
                        else:
                            enhanced_prompt = analysis_prompt
                        
                        emoji_logger.system_info("📤 Enviando imagem para Gemini Vision com prompt otimizado...")
                        
                        # Enviar imagem com prompt otimizado ao Gemini
                        response = vision_model.generate_content([enhanced_prompt, img])
                        analysis_content = response.text if hasattr(response, 'text') else str(response)
                        
                        emoji_logger.system_info("✅ PIL + Gemini direto: Sucesso (latência otimizada)")
                            
                    except Exception as pil_gemini_error:
                        emoji_logger.system_error("PIL + Gemini direto falhou", f"Erro: {str(pil_gemini_error)}")
                        return {
                            "type": "image",
                            "error": f"Não foi possível processar a imagem: {str(pil_gemini_error)}",
                            "status": "error",
                            "suggestion": "Tente enviar a imagem em formato JPEG ou PNG"
                        }
                        
                    emoji_logger.agentic_multimodal("Análise de imagem concluída com sucesso")
                    
                    # Verificar se é conta de luz através da interpretação do Gemini
                    bill_keywords = ["conta", "energia", "kwh", "tarifa", "consumo", "fatura"]
                    is_bill = any(word in analysis_content.lower() for word in bill_keywords)
                    
                    if is_bill:
                        emoji_logger.agentic_multimodal("Conta de luz detectada", media_type="bill_image")
                        # Extrair valor da conta se possível
                        import re
                        
                        # Buscar padrão de valor monetário na análise
                        valor_match = re.search(r'R\$\s*(\d+[.,]\d{2})', analysis_content)
                        bill_amount = None
                        if valor_match:
                            # Converter vírgula para ponto e para float
                            bill_amount = float(valor_match.group(1).replace(',', '.'))
                            emoji_logger.system_info(f"💰 Valor da conta detectado: R$ {bill_amount:.2f}")
                        
                        return {
                            "type": "bill_image",
                            "needs_analysis": True,
                            "content": analysis_content,
                            "bill_amount": bill_amount,  # Adicionar valor extraído
                            "is_bill": True  # Garantir que é reconhecido como conta
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
                        "is_thumbnail": data_size < 50000
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
                        # SIMPLES: Apenas retornar a transcrição
                        # Não precisa processar com agente adicional
                        transcribed_text = result["text"]
                        
                        emoji_logger.agentic_multimodal(
                            f"Audio transcrito com sucesso: {len(transcribed_text)} caracteres",
                            media_type="audio",
                            duration=result.get("duration", 0)
                        )
                        
                        return {
                            "type": "audio",
                            "transcription": transcribed_text,
                            "duration": result.get("duration", 0),
                            "engine": result.get("engine", "Google Speech Recognition"),
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
                    
                    document_type = detection_result.get('format', 'unknown')
                    
                    # Verificar se recommended_params existe antes de acessar
                    if 'recommended_params' in detection_result:
                        agno_params = detection_result['recommended_params']
                    else:
                        # Usar parâmetros padrão se não houver recomendação
                        logger.warning(f"⚠️ Sem recommended_params para documento: {document_type}")
                        agno_params = {
                            'reader_class': 'PDFReader',
                            'ocr_enabled': True,
                            'max_pages': None
                        }
                    
                    is_pdf = document_type == 'pdf'
                    is_docx = document_type == 'docx'
                    
                    emoji_logger.agentic_thinking(f"AGNO detectou documento: {document_type} (confiança: {detection_result.get('confidence', 'unknown')})")
                    
                    # Determinar tipo e usar AGNO reader apropriado
                    extracted_text = ""
                    doc_metadata = {}
                    
                    if is_pdf or is_docx:
                        try:
                            # Usar processador centralizado de documentos
                            emoji_logger.agentic_thinking(f"Processando documento {document_type} com EnhancedDocumentProcessor...")
                            
                            # Processar documento usando função SIMPLES (substitui document_processor_enhanced.py)
                            result = await self._process_document_simple(
                                data=document_bytes,
                                filename=f"document.{document_type}"
                            )
                            
                            if result.get('status') == 'success':
                                extracted_text = result.get('content', '')
                                doc_metadata = {
                                    "reader": "enhanced_document_processor",
                                    "format": document_type,
                                    "size_bytes": original_size,
                                    "text_extracted": result.get('text_extracted', False),
                                    "images_processed": result.get('images_processed', 0),
                                    "ocr_content": result.get('ocr_content', False)
                                }
                                
                                if is_pdf:
                                    doc_metadata["pages"] = result.get('pages', 0)
                                elif is_docx:
                                    doc_metadata["sections"] = result.get('sections', 0)
                                
                                emoji_logger.agentic_thinking(f"Documento processado com sucesso: {len(extracted_text)} caracteres extraídos")
                            else:
                                raise Exception(f"Falha no processamento: {result.get('error', 'Unknown error')}")
                            
                        except Exception as doc_error:
                            emoji_logger.system_error("Document Processing", f"Erro ao processar documento: {str(doc_error)}")
                            # Não lançar exceção, retornar erro estruturado
                            return {
                                "type": "document",
                                "error": str(doc_error),
                                "status": "error",
                                "message": f"Erro ao processar documento: {str(doc_error)[:100]}"
                            }
                    
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
                        
                        # Criar contexto para análise do documento
                        doc_context = f"""O cliente enviou um {doc_type} com o seguinte conteúdo:
                        
                        {extracted_text[:3000]}...
                        
                        Documento completo: {result.get('pages', 'N/A')} página(s)
                        Tipo identificado: {doc_type}
                        
                        Por favor, analise o documento e:
                        1. Identifique as informações principais
                        2. Se for uma conta de luz, extraia valor e consumo
                        3. Se for outro documento, resuma os pontos importantes"""
                        
                        # Usar IntelligentModelFallback diretamente para evitar dependência do OpenAI
                        emoji_logger.agentic_thinking("Analisando documento com IntelligentModelFallback...")
                        try:
                            # Criar um agente temporário apenas com o modelo inteligente
                            from agno.agent import Agent as AgnoAgent
                            
                            temp_agent = AgnoAgent(
                                model=self.intelligent_model,  # Usa o wrapper com fallback
                                markdown=True,
                                show_tool_calls=False,
                                instructions="Você é um assistente especializado em análise de documentos. Extraia todas as informações relevantes de forma detalhada."
                            )
                            
                            # Processar documento
                            response = temp_agent.run(doc_context)
                            
                            # Extrair conteúdo da resposta
                            if hasattr(response, 'content'):
                                agent_response = response.content
                            elif isinstance(response, dict) and 'content' in response:
                                agent_response = response['content']
                            elif isinstance(response, str):
                                agent_response = response
                            else:
                                agent_response = str(response)
                            
                            emoji_logger.agentic_thinking(f"Documento analisado com sucesso: {len(str(agent_response))} caracteres")
                        except Exception as analysis_error:
                            emoji_logger.system_error("Document Analysis", f"Erro ao analisar: {str(analysis_error)}")
                            agent_response = "Não foi possível analisar o documento neste momento."
                        
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
            
        # Executar com timeout
        try:
            result = await asyncio.wait_for(
                process_with_timeout(),
                timeout=MULTIMODAL_TIMEOUT
            )
            
            # Métricas finais de sucesso
            total_time = time.time() - start_time
            emoji_logger.system_info("═" * 50)
            emoji_logger.system_info(f"✅ MULTIMODAL: Processamento concluído")
            emoji_logger.system_info(f"  • Tipo: {media_type}")
            emoji_logger.system_info(f"  • Status: {result.get('status', 'success')}")
            emoji_logger.system_info(f"  • Tempo total: {total_time:.2f}s")
            emoji_logger.system_info("═" * 50)
            
            return result
            
        except asyncio.TimeoutError:
            total_time = time.time() - start_time
            emoji_logger.system_error("Multimodal Timeout", f"❌ MULTIMODAL: Timeout após {MULTIMODAL_TIMEOUT}s")
            emoji_logger.system_info(f"  • Tipo: {media_type}")
            emoji_logger.system_info(f"  • Tempo decorrido: {total_time:.2f}s")
            
            return {
                "type": media_type,
                "error": f"Processamento excedeu o limite de {MULTIMODAL_TIMEOUT} segundos",
                "status": "timeout",
                "timeout_seconds": MULTIMODAL_TIMEOUT,
                "processing_time": total_time
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
        Busca na knowledge base usando KnowledgeService simplificado
        
        Args:
            query: Query de busca
            filters: Filtros opcionais (ignorado na versão simplificada)
            
        Returns:
            Documentos relevantes
        """
        try:
            # Verificar se knowledge base está habilitada
            if not self.knowledge_search_enabled:
                return []
                
            emoji_logger.team_knowledge(f"🔍 Buscando: {query[:50]}...")
            
            # Usar o novo KnowledgeService simplificado
            results = await knowledge_service.search_knowledge_base(query, max_results=5)
            
            # Converter para formato compatível
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.get("content", ""),
                    "title": doc.get("title", ""),
                    "category": doc.get("category", ""),
                    "metadata": {
                        "id": doc.get("id"),
                        "tags": doc.get("tags", ""),
                        "created_at": doc.get("created_at", "")
                    },
                    "score": 0.8  # Score fixo para versão simplificada
                })
            
            emoji_logger.team_knowledge(f"✅ Encontrados {len(formatted_results)} documentos")
            return formatted_results
            
        except Exception as e:
            emoji_logger.team_knowledge(f"❌ Erro na busca: {e}")
            return []
    
    def analyze_energy_bill(self, image_data: str, customer_name: str = "Cliente") -> Dict[str, Any]:
        """
        Analisa conta de energia via Vision AI - SUBSTITUI BillAnalyzerAgent (881 linhas → função simples)
        
        Args:
            image_data: Imagem em base64
            customer_name: Nome do cliente
            
        Returns:
            Dados extraídos e análise completa
        """
        try:
            # Prompt inteligente que substitui 881 linhas de código complexo!
            analysis_prompt = f"""
            Analise esta conta de energia elétrica e extraia TODOS os dados possíveis.

            EXTRAIR:
            1. Valor total a pagar (R$) - campo mais importante
            2. Consumo em kWh
            3. Nome do titular
            4. Endereço da instalação
            5. Número da instalação/UC
            6. Fornecedor (Celpe, Coelba, Cosern, etc)
            7. Mês de referência
            8. Histórico de consumo se visível

            CALCULAR:
            - Economia mensal com solar (20% do valor total)
            - Economia anual (economia mensal × 12)
            - Sistema solar recomendado em kWp (consumo ÷ 150)
            - Número de painéis necessários (kWp ÷ 0.55)
            - Investimento estimado (kWp × R$ 4.000)
            - Payback em anos (investimento ÷ economia anual)

            QUALIFICAR LEAD:
            - Se valor ≥ R$ 600: "LEAD_QUENTE" 
            - Se valor ≥ R$ 400: "IDEAL"
            - Se valor ≥ R$ 200: "QUALIFICADO"
            - Se valor < R$ 200: "BAIXO"

            RETORNAR JSON ESTRUTURADO com todos os campos calculados.
            """
            
            # Usar Vision AI do Gemini (modelo já tem capacidade multimodal)
            import base64
            image_bytes = base64.b64decode(image_data)
            
            # Usar Gemini diretamente via genai (não pelo AGNO)
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            
            # Preparar imagem para Gemini
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(image_bytes))
            
            # Usar modelo Gemini Flash para análise rápida
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([analysis_prompt, img])
            
            # Parse da resposta JSON
            import json
            import re
            from datetime import datetime
            
            # Extrair texto da resposta
            response_text = response.text if hasattr(response, 'text') else str(response)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    result = json.loads(json_str)
                except:
                    # Fallback: extrair manualmente via regex
                    result = self._extract_bill_data_fallback(response_text)
            else:
                result = self._extract_bill_data_fallback(response_text)
            
            # Normalizar campos e garantir dados mínimos
            normalized_result = {
                "success": True,
                "analysis_method": "vision_ai_prompt",
                "customer_name": customer_name,
                "analyzed_at": datetime.now().isoformat(),
                
                # Dados extraídos
                "valor_total": result.get("valor_total") or result.get("bill_value", 0),
                "consumo_kwh": result.get("consumo_kwh") or result.get("consumption_kwh", 0),
                "titular": result.get("titular") or result.get("customer_name", ""),
                "endereco": result.get("endereco") or result.get("address", ""),
                "instalacao": result.get("instalacao") or result.get("installation_number", ""),
                "fornecedor": result.get("fornecedor") or result.get("provider", ""),
                "mes_referencia": result.get("mes_referencia") or result.get("reference_month", ""),
                
                # Cálculos financeiros
                "economia_mensal": result.get("economia_mensal", 0),
                "economia_anual": result.get("economia_anual", 0),
                "sistema_kwp": result.get("sistema_kwp", 0),
                "num_paineis": result.get("num_paineis", 0),
                "investimento": result.get("investimento", 0),
                "payback_anos": result.get("payback_anos", 0),
                
                # Qualificação
                "qualificacao": result.get("qualificacao", "BAIXO"),
                "qualificado": result.get("valor_total", 0) >= 200
            }
            
            emoji_logger.team_knowledge(f"💡 Conta analisada via Vision AI: R$ {normalized_result.get('valor_total', 0)} - {normalized_result.get('qualificacao', 'N/A')}")
            return normalized_result
            
        except Exception as e:
            logger.error(f"Erro análise conta Vision AI: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_method": "vision_ai_prompt",
                "customer_name": customer_name
            }
    
    def _extract_bill_data_fallback(self, text: str) -> Dict[str, Any]:
        """Extração fallback se JSON parsing falhar - regex simples"""
        result = {}
        
        import re
        
        # Valor em R$ - múltiplos padrões
        for pattern in [r'R\$\s*([\d.,]+)', r'total[:\s]+R?\$?\s*([\d.,]+)', r'pagar[:\s]+R?\$?\s*([\d.,]+)']:
            value_match = re.search(pattern, text, re.IGNORECASE)
            if value_match:
                value_str = value_match.group(1).replace('.', '').replace(',', '.')
                try:
                    bill_value = float(value_str)
                    result['valor_total'] = bill_value
                    
                    # Cálculos básicos
                    result['economia_mensal'] = bill_value * 0.20
                    result['economia_anual'] = result['economia_mensal'] * 12
                    
                    # Qualificação
                    if bill_value >= 600:
                        result['qualificacao'] = 'LEAD_QUENTE'
                    elif bill_value >= 400:
                        result['qualificacao'] = 'IDEAL'
                    elif bill_value >= 200:
                        result['qualificacao'] = 'QUALIFICADO'
                    else:
                        result['qualificacao'] = 'BAIXO'
                    break
                except:
                    continue
        
        # Consumo kWh
        kwh_match = re.search(r'(\d+)\s*kWh', text, re.IGNORECASE)
        if kwh_match:
            consumption = int(kwh_match.group(1))
            result['consumo_kwh'] = consumption
            
            # Dimensionamento aproximado
            if consumption > 0:
                result['sistema_kwp'] = round(consumption / 150, 2)
                result['num_paineis'] = int(result['sistema_kwp'] / 0.55) + 1
                result['investimento'] = result['sistema_kwp'] * 4000
                
                if result.get('economia_anual', 0) > 0:
                    result['payback_anos'] = round(result['investimento'] / result['economia_anual'], 1)
        
        return result
    
    # Funções simples que substituem serviços complexos (456+404=860 linhas → ~50 linhas)
    
    def _format_context_simple(
        self,
        message_history: List[Dict[str, Any]] = None,
        multimodal_result: Dict[str, Any] = None,
        phone: str = None
    ) -> Dict[str, Any]:
        """
        Formatação SIMPLES de contexto - substitui agno_context_agent.py (456 linhas)
        MANTÉM TODAS as mensagens recuperadas (até 100) para preservar contexto completo
        """
        try:
            if not message_history:
                return {
                    'formatted_history': "",
                    'message_count': 0,
                    'context_quality': 'empty'
                }
            
            # Pegar TODAS as mensagens recuperadas (mantém as 100 mensagens originais!)
            recent_messages = message_history  # SEM REDUÇÃO - usa todas as mensagens que foram buscadas
            
            # Formato simples: "USER: mensagem" ou "ASSISTANT: mensagem"
            formatted_lines = []
            
            # CORREÇÃO CRÍTICA: Incluir análise multimodal PRIMEIRO no contexto
            if multimodal_result and not multimodal_result.get('error'):
                media_type = multimodal_result.get('type', 'unknown')
                content = multimodal_result.get('content', '')
                
                if content:
                    # Adicionar análise multimodal com destaque
                    formatted_lines.append("=== ANÁLISE MULTIMODAL RECEBIDA ===")
                    formatted_lines.append(f"TIPO: {media_type.upper()}")
                    formatted_lines.append(f"ANÁLISE: {content}")
                    
                    # Se for conta de luz, adicionar detalhes
                    if multimodal_result.get('is_bill'):
                        formatted_lines.append(f"CONTA DE LUZ DETECTADA - Valor: R$ {multimodal_result.get('bill_amount', 0):.2f}")
                    
                    formatted_lines.append("=== FIM DA ANÁLISE ===")
                    formatted_lines.append("")  # Linha em branco para separação
            
            # Adicionar histórico de mensagens
            for msg in recent_messages:
                role = msg.get('sender', 'user').upper()
                content = msg.get('content', '')
                if content:
                    formatted_lines.append(f"{role}: {content}")
            
            return {
                'formatted_history': '\n'.join(formatted_lines),
                'message_count': len(recent_messages),
                'context_quality': 'excellent' if len(recent_messages) >= 50 else 'good' if len(recent_messages) >= 10 else 'basic',
                'has_multimodal': bool(multimodal_result and not multimodal_result.get('error'))
            }
            
        except Exception as e:
            logger.error(f"Erro formatação contexto: {e}")
            return {
                'formatted_history': "",
                'message_count': 0,
                'context_quality': 'error'
            }
    
    async def _process_document_simple(self, data: bytes, filename: str = "document") -> Dict[str, Any]:
        """
        Processamento SIMPLES de documentos via Vision AI - substitui document_processor_enhanced.py (404 linhas)
        """
        try:
            import base64
            
            # Converter para base64
            document_b64 = base64.b64encode(data).decode()
            
            # Usar Vision AI diretamente (muito mais simples que OCR/PDF parsing)
            prompt = """
            Analise este documento e extraia:
            1. Tipo de documento
            2. Conteúdo principal (texto legível)
            3. Informações importantes (valores, datas, nomes)
            4. Se for conta de energia: valor total e consumo
            
            Retorne JSON estruturado com os dados extraídos.
            """
            
            # Usar Gemini diretamente para documentos também
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            
            # Para PDFs, tentar usar como imagem primeiro
            from PIL import Image
            from io import BytesIO
            
            try:
                # Tentar abrir como imagem (para PDFs simples)
                img = Image.open(BytesIO(data))
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([prompt, img])
                response_text = response.text if hasattr(response, 'text') else str(response)
            except:
                # Se falhar, usar apenas o texto do prompt
                # Por agora, retornar erro estruturado
                return {
                    "success": False,
                    "error": "PDF complexo requer processamento avançado",
                    "document_type": "pdf",
                    "content": "Não foi possível processar este PDF automaticamente. Por favor, envie uma imagem da conta."
                }
            
            # Parse simples da resposta
            import json
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])
                else:
                    result = {"text_content": response_text, "document_type": "unknown"}
            except:
                result = {"text_content": response_text, "document_type": "text"}
            
            result.update({
                "success": True,
                "processing_method": "vision_ai_simple",
                "filename": filename
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro processamento documento: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_method": "vision_ai_simple"
            }
    
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
            
            # Buscar documentos da tabela knowledge_base (usando import global)
            
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
    
    def _generate_simple_fallback_response(self, message: str) -> str:
        """Gera resposta simples de fallback quando agent.arun falha ou dá timeout"""
        
        emoji_logger.system_info("🔄 Gerando resposta de fallback...")
        
        # Respostas contextuais baseadas em palavras-chave
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
            return "Oi! Vi sua mensagem sobre energia solar. Você gostaria de saber quanto pode economizar na sua conta de luz?"
        
        elif any(word in message_lower for word in ['quanto', 'valor', 'preço', 'preco', 'custa']):
            return "Para calcular sua economia, preciso saber: qual o valor médio da sua conta de luz?"
        
        elif any(word in message_lower for word in ['economia', 'economizar', 'desconto']):
            return "Com energia solar você pode economizar até 95% na conta de luz! Qual o valor da sua conta atual?"
        
        elif any(word in message_lower for word in ['sim', 'quero', 'tenho interesse']):
            return "Ótimo! Para fazer uma proposta personalizada, me diz: quanto você paga de luz por mês?"
        
        elif any(word in message_lower for word in ['não', 'nao', 'depois', 'agora não']):
            return "Sem problemas! Quando quiser saber mais sobre energia solar, estarei aqui. Até mais!"
        
        else:
            # Resposta genérica
            return "Entendi! Para te ajudar melhor com energia solar, qual o valor da sua conta de luz?"
    
    def _extract_name(self, message: str) -> Optional[str]:
        """Extrai nome do lead da mensagem usando regex simples"""
        patterns = [
            r"meu nome é ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
            r"me chamo ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
            r"sou o?a? ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
            r"([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*), prazer"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_email(self, message: str) -> Optional[str]:
        """Extrai email do lead usando regex"""
        pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        match = re.search(pattern, message)
        
        if match:
            return match.group(0).lower()
        
        return None
    
    def _extract_document(self, message: str) -> Optional[str]:
        """Extrai CPF ou CNPJ da mensagem"""
        # Remove pontuação para facilitar
        clean_msg = re.sub(r'[.\-/]', '', message)
        
        # CPF: 11 dígitos
        cpf_pattern = r'\b\d{11}\b'
        cpf_match = re.search(cpf_pattern, clean_msg)
        if cpf_match:
            cpf = cpf_match.group(0)
            # Formata CPF: XXX.XXX.XXX-XX
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        # CNPJ: 14 dígitos
        cnpj_pattern = r'\b\d{14}\b'
        cnpj_match = re.search(cnpj_pattern, clean_msg)
        if cnpj_match:
            cnpj = cnpj_match.group(0)
            # Formata CNPJ: XX.XXX.XXX/XXXX-XX
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        
        return None
    
    def _extract_bill_value(self, message: str) -> Optional[float]:
        """Extrai valor da conta de luz da mensagem"""
        import re
        
        # Padrões para detectar valores em reais
        # Ex: R$ 4.000, R$4000, 4000 reais, 4.000,00
        patterns = [
            r'r\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # R$ 4.000,00
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*reais',  # 4.000 reais
            r'conta.*?(\d{1,3}(?:\.\d{3})*)',  # conta de 4.000
            r'valor.*?(\d{1,3}(?:\.\d{3})*)',  # valor 4.000
        ]
        
        message_lower = message.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, message_lower, re.IGNORECASE)
            if matches:
                for match in matches:
                    try:
                        # Remove pontos de milhar e substitui vírgula por ponto
                        value_str = match.replace('.', '').replace(',', '.')
                        value = float(value_str)
                        
                        # Se o valor parece ser da conta de luz (entre 100 e 50000)
                        if 100 <= value <= 50000:
                            return value
                    except ValueError:
                        continue
        
        return None
    
    def _calculate_qualification_score(self, lead_data: Dict) -> int:
        """Calcula score de qualificação baseado nos dados do lead"""
        score = 0
        
        # Score baseado no valor da conta (máximo 50 pontos)
        bill_value = lead_data.get('bill_value', 0) or 0
        if bill_value >= 8000:
            score += 50  # Conta muito alta
        elif bill_value >= 6000:
            score += 40  # Conta alta
        elif bill_value >= 4000:
            score += 30  # Conta qualificada
        elif bill_value >= 2000:
            score += 20  # Conta média
        elif bill_value >= 500:
            score += 10  # Conta baixa mas válida
        
        # Score baseado em tomada de decisão (20 pontos)
        if lead_data.get('is_decision_maker'):
            score += 20
        
        # Score baseado em interesse (15 pontos)
        if lead_data.get('has_interest'):
            score += 15
        
        # Score baseado em não ter sistema solar (10 pontos)
        if not lead_data.get('has_solar_system'):
            score += 10
        
        # Score baseado em não ter contrato ativo (5 pontos)  
        if not lead_data.get('has_active_contract'):
            score += 5
        
        # Garantir que o score não ultrapasse 100
        return min(score, 100)
    
    def _identify_stage(self, message: str, lead_data: Dict) -> str:
        """Identifica estágio atual baseado na conversa e dados do lead"""
        
        message_lower = message.lower()
        
        # Verificar se está qualificado
        if lead_data:
            # Corrigir comparação com None - garantir que bill_value é um número
            bill_value = lead_data.get('bill_value')
            if bill_value is None:
                bill_value = 0
            else:
                # Converter para float se for string
                try:
                    bill_value = float(bill_value) if bill_value else 0
                except (ValueError, TypeError):
                    bill_value = 0
            
            qualificado = all([
                bill_value > 4000,
                lead_data.get('is_decision_maker') == True,
                lead_data.get('has_solar_system') == False or lead_data.get('wants_new_solar_system') == True,
                lead_data.get('has_active_contract') == False
            ])
            
            if qualificado:
                return "QUALIFICADO"
        
        # Identificar por palavras-chave
        if any(word in message_lower for word in ["agendar", "reunião", "marcar", "disponibilidade", "horário"]):
            return "REUNIAO_AGENDADA"
        
        elif any(word in message_lower for word in ["quanto custa", "valor", "preço", "investimento", "orçamento"]):
            return "EM_NEGOCIACAO"
        
        elif any(phrase in message_lower for phrase in ["não tenho interesse", "não quero", "obrigado mas", "desisto"]):
            return "NAO_INTERESSADO"
        
        elif any(word in message_lower for word in ["conta de luz", "energia", "consumo", "kwh"]):
            return "EM_QUALIFICACAO"
        
        # Se não identificou, mantém o atual ou usa default
        return lead_data.get('current_stage', 'EM_QUALIFICACAO') if lead_data else "INITIAL_CONTACT"
    


    def _format_knowledge_results(self, results: List[Dict[str, Any]]) -> str:
        """Formata resultados da knowledge base de forma concisa"""
        if not results:
            return "Sem informações específicas"
        
        formatted = []
        for i, result in enumerate(results[:3], 1):  # Máximo 3 resultados
            question = result.get('question', 'Pergunta')
            answer = result.get('answer', 'Resposta')[:200]
            formatted.append(f"{i}. P: {question}\n   R: {answer}...")
        
        return "\n".join(formatted)

    def _is_first_contact(self, messages_history: List[Dict[str, Any]]) -> bool:
        """
        Detecta se é o primeiro contato com o lead de forma INTELIGENTE
        
        Returns:
            True se for primeira interação, False caso contrário
        """
        if not messages_history:
            return True
        
        # Contar mensagens do AGENTE (não do usuário)
        agent_messages = [
            msg for msg in messages_history 
            if msg.get('sender') == 'agent' or msg.get('role') == 'assistant'
        ]
        
        # Se o agente nunca respondeu, é primeira interação
        return len(agent_messages) == 0
    
    def _should_knowledge_search(self, message: str) -> bool:
        """
        SEMPRE retorna True - knowledge search é OBRIGATÓRIO
        """
        return True

    async def process_message(
        self,
        phone: str,
        message: str,
        lead_data: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        media: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
        current_emotional_state: Optional[str] = None
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
        
        # DEFENSIVE PROGRAMMING: Inicializar new_emotional_state com valor padrão seguro
        new_emotional_state = current_emotional_state or "ENTUSIASMADA"
        
        try:
            emoji_logger.agentic_thinking(f"Processando mensagem de {phone}: {message[:50]}...")
            
            if not self.is_initialized:
                await self.initialize()
            
            # EXTRAÇÃO DE DADOS E ATUALIZAÇÃO DE ESTÁGIO
            # Extrair informações básicas da mensagem
            nome_extraido = self._extract_name(message)
            email_extraido = self._extract_email(message)
            documento_extraido = self._extract_document(message)
            bill_value_extraido = self._extract_bill_value(message)
            
            # Identificar novo estágio
            novo_stage = self._identify_stage(message, lead_data or {})
            
            # Preparar dados para atualização
            update_data = {}
            if nome_extraido and (not lead_data or not lead_data.get('name')):
                update_data['name'] = nome_extraido
                emoji_logger.system_info(f"Nome extraído: {nome_extraido}")
            
            if email_extraido and (not lead_data or not lead_data.get('email')):
                update_data['email'] = email_extraido
                emoji_logger.system_info(f"Email extraído: {email_extraido}")
            
            if documento_extraido and (not lead_data or not lead_data.get('document')):
                update_data['document'] = documento_extraido
                emoji_logger.system_info(f"Documento extraído: {documento_extraido}")
            
            if bill_value_extraido and (not lead_data or not lead_data.get('bill_value')):
                update_data['bill_value'] = bill_value_extraido
                emoji_logger.system_info(f"💰 Valor da conta extraído: R$ {bill_value_extraido}")
            
            if lead_data and novo_stage != lead_data.get('current_stage'):
                update_data['current_stage'] = novo_stage
                emoji_logger.system_info(f"Novo estágio identificado: {novo_stage}")
                
                # CORREÇÃO ATÔMICA: Se o lead foi qualificado, calcular e salvar score junto
                if novo_stage == "QUALIFICADO" and not lead_data.get('qualification_status'):
                    # Calcular score baseado nos critérios
                    qualification_score = self._calculate_qualification_score(lead_data)
                    
                    update_data['qualification_status'] = 'QUALIFIED'
                    update_data['qualification_score'] = qualification_score
                    emoji_logger.system_success(f"🎯 Lead qualificado com score {qualification_score}")
                    
                    # Salvar também na tabela de qualificações
                    try:
                        await supabase_client.create_lead_qualification({
                            'lead_id': lead_data['id'],
                            'qualification_status': 'QUALIFIED',
                            'score': qualification_score,
                            'criteria': {
                                'bill_value': lead_data.get('bill_value', 0),
                                'is_decision_maker': lead_data.get('is_decision_maker', True),
                                'has_interest': True,
                                'stage_identified': novo_stage
                            },
                            'notes': 'Lead qualificado automaticamente pelo AgenticSDR'
                        })
                        emoji_logger.system_success("✅ Qualificação salva na tabela leads_qualifications")
                    except Exception as qual_error:
                        emoji_logger.system_error("AGENTIC SDR", f"Erro ao salvar qualificação: {qual_error}")
            
            # Atualizar no banco se houver mudanças
            if update_data and lead_data and lead_data.get('id'):
                try:
                    await supabase_client.update_lead(lead_data['id'], update_data)
                    emoji_logger.system_success(f"✅ Lead atualizado no Supabase: {update_data}")
                    
                    # Atualizar lead_data local para uso posterior
                    lead_data.update(update_data)
                except Exception as update_error:
                    emoji_logger.system_warning(f"Erro ao atualizar lead: {str(update_error)[:50]}")
            
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
            
            # 2. SEMPRE buscar histórico (OBRIGATÓRIO) e detectar gatilhos emocionais
            messages_history = []
            try:
                # MELHORIA HÍBRIDA: Histórico é SEMPRE consultado
                # VALIDAÇÃO CRÍTICA: Garantir que conversation_id é válido
                if not conversation_id:
                    emoji_logger.system_error("HISTÓRICO", f"❌ conversation_id é None/vazio! Lead: {lead_data}")
                    # Tentar buscar por phone como fallback
                    if phone:
                        emoji_logger.system_info(f"🔄 Tentando buscar histórico por phone: {phone}")
                        messages_history = await self.get_last_100_messages(phone)
                    else:
                        emoji_logger.system_error("HISTÓRICO", "❌ Nem conversation_id nem phone disponíveis!")
                        messages_history = []
                else:
                    # Buscar histórico de mensagens (será usado para contexto e análise emocional)
                    messages_history = await self.get_last_100_messages(conversation_id)
                
                emoji_logger.system_info(f"✅ HISTÓRICO FINAL: {len(messages_history)} mensagens carregadas")
                emotional_triggers = await self.detect_emotional_triggers(messages_history)
            except Exception as emo_error:
                emoji_logger.system_warning(f"Análise emocional falhou: {str(emo_error)[:50]}")
                emotional_triggers = {"dominant_emotion": "neutral", "enabled": False}
            
            # 3. Processar multimodal se necessário
            multimodal_result = None
            if media:
                # Mapear mimetype para type (O SIMPLES FUNCIONA!)
                media_type = self._get_media_type_from_mimetype(media.get("mimetype", ""))
                multimodal_result = await self.process_multimodal_content(
                    media_type,
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
                        emotional_triggers,
                        new_emotional_state
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
                    # Formatar contexto com função SIMPLES (substitui agno_context_agent.py)
                    context_result = self._format_context_simple(
                        message_history=messages_history or [],
                        multimodal_result=multimodal_result,
                        phone=phone
                    )
                    
                    # AGNO Framework já formatou multimodal + histórico no formatted_history
                    formatted_history = context_result.get('formatted_history', '')
                    
                    # MELHORIA HÍBRIDA: Context Pruning - limitar para evitar poluição
                    if len(messages_history) > 20:
                        emoji_logger.system_info(f"📊 Context Pruning: {len(messages_history)} → 20 mensagens")
                        # Pegar apenas as 20 mais recentes para o contexto
                        recent_messages = messages_history[-20:]
                        context_result = self._format_context_simple(
                            message_history=recent_messages,
                            multimodal_result=multimodal_result,
                            phone=phone
                        )
                        formatted_history = context_result.get('formatted_history', '')
                    
                    # DEBUG: Verificar se multimodal foi incluído no contexto
                    if context_result.get('has_multimodal'):
                        emoji_logger.system_info("✅ Análise multimodal incluída no contexto formatado")
                        emoji_logger.system_debug(f"Primeiras 500 chars do contexto: {formatted_history[:500]}...")
                    
                    
                    # MELHORIA HÍBRIDA: SEMPRE consultar knowledge base (OBRIGATÓRIO)
                    knowledge_results = []
                    try:
                        if message and len(message.strip()) > 2:  # Mensagem válida
                            emoji_logger.system_info("🔍 Consultando Knowledge Base (OBRIGATÓRIO)")
                            # MUDANÇA: Buscar TODO o conhecimento, não filtrar por mensagem
                            # O objetivo é enriquecer a resposta com TODAS as informações disponíveis
                            from app.services.knowledge_service import knowledge_service
                            kb_task = asyncio.create_task(knowledge_service.get_all_knowledge(limit=15))
                            knowledge_results = await asyncio.wait_for(kb_task, timeout=5.0)  # 5 segundos max
                            emoji_logger.system_info(f"✅ Knowledge Base: {len(knowledge_results)} resultados encontrados")
                    except asyncio.TimeoutError:
                        emoji_logger.system_warning("⏱️ Knowledge Base timeout (5s), continuando sem resultados")
                        knowledge_results = []
                    except Exception as kb_error:
                        emoji_logger.system_warning(f"Knowledge Base falhou: {str(kb_error)[:100]}")
                        knowledge_results = []
                    
                    # Detectar se é primeiro contato ANTES de construir o prompt
                    is_first_contact = self._is_first_contact(messages_history)
                    emoji_logger.system_info(f"🎯 Primeiro contato detectado: {is_first_contact}")
                    
                    # Preparar prompt com contexto completo AGNO-enhanced
                    contextual_prompt = f"""
                    🚨 ESTADO DA CONVERSA: {'PRIMEIRO CONTATO - APRESENTE-SE!' if is_first_contact else f'CONVERSA EM ANDAMENTO ({len(messages_history)} mensagens)'}
                    
                    📚 KNOWLEDGE BASE (CONSULTADA):
                    {self._format_knowledge_results(knowledge_results) if knowledge_results else 'Nenhum resultado específico'}
                    
                    CONTEXTO DO LEAD:
                    - Nome: {lead_data.get('name', 'Não informado') if lead_data else 'Não informado'}
                    - Telefone: {phone}
                    - Estágio: {lead_data.get('current_stage', 'INITIAL_CONTACT') if lead_data else 'INITIAL_CONTACT'}
                    - Status: {lead_data.get('qualification_status', 'PENDING') if lead_data else 'PENDING'}
                    
                    {formatted_history}
                    
                    MENSAGEM ATUAL DO CLIENTE: {message}
                    """
                    
                    # Se tem resultado multimodal, adicionar informações EXPLICITAMENTE
                    if multimodal_result and not multimodal_result.get('error'):
                        media_type = multimodal_result.get('type')
                        
                        if media_type == 'audio' and multimodal_result.get('transcription'):
                            contextual_prompt += f"""
                    
                    🎤 TRANSCRIÇÃO DO ÁUDIO RECEBIDO:
                    "{multimodal_result.get('transcription')}"
                    (Duração: {multimodal_result.get('duration', 0)}s)
                    
                    IMPORTANTE: Use a transcrição acima como o conteúdo real da mensagem do cliente, não a mensagem genérica.
                    """
                        
                        elif media_type in ['image', 'bill_image']:  # CORREÇÃO: Aceitar bill_image
                            contextual_prompt += f"""
                    
                    📸 IMAGEM RECEBIDA - ANÁLISE:
                    {multimodal_result.get('content', 'Análise não disponível')}
                    
                    """
                            # CORREÇÃO: Verificar tanto is_bill quanto type=='bill_image'
                            if multimodal_result.get('is_bill') or multimodal_result.get('type') == 'bill_image':
                                contextual_prompt += f"""
                    💡 CONTA DE LUZ DETECTADA:
                    - Valor mensal: R$ {multimodal_result.get('bill_amount', 0):.2f}
                    - Consumo: {multimodal_result.get('consumption', 'N/A')} kWh
                    - Concessionária: {multimodal_result.get('provider', 'N/A')}
                    """
                        
                        elif media_type == 'pdf':
                            contextual_prompt += f"""
                    
                    📄 DOCUMENTO PDF RECEBIDO:
                    Arquivo: {multimodal_result.get('filename', 'documento.pdf')}
                    
                    Conteúdo extraído:
                    {multimodal_result.get('content', 'Conteúdo não disponível')[:1000]}
                    """
                            if len(multimodal_result.get('content', '')) > 1000:
                                contextual_prompt += "\n[... documento truncado para contexto]"
                    
                    # VALIDAÇÃO DE CALENDÁRIO - CRÍTICO
                    calendar_keywords = [
                        "agenda", "horário", "disponibilidade", "marcar", "reunião",
                        "encontro", "meeting", "agendar", "leonardo está", "leonardo pode",
                        "quando pode", "que dia", "que hora", "horários disponíveis"
                    ]
                    
                    needs_calendar = any(keyword in message.lower() for keyword in calendar_keywords)
                    
                    if needs_calendar:
                        contextual_prompt += """
                    
                    🚨🚨🚨 ATENÇÃO CRÍTICA - CALENDÁRIO DETECTADO 🚨🚨🚨
                    
                    ⚠️ O LEAD ESTÁ PEDINDO INFORMAÇÕES DE AGENDA/HORÁRIOS!
                    
                    VOCÊ DEVE OBRIGATORIAMENTE:
                    1. DELEGAR para SDR_TEAM (CalendarAgent) IMEDIATAMENTE
                    2. NÃO INVENTAR horários disponíveis
                    3. NÃO DIZER que "consultou a agenda" sem consultar
                    
                    RESPONDA ALGO COMO:
                    "Vou verificar a agenda do Leonardo agora mesmo para te passar os melhores horários!"
                    
                    E ENTÃO DELEGUE A TAREFA!
                    """
                    
                    contextual_prompt += f"""
                    
                    Análise Contextual:
                    - Contexto Principal: {context_analysis.get('primary_context')}
                    - Engajamento: {context_analysis.get('lead_engagement_level')}
                    - Estágio: {context_analysis.get('decision_stage')}
                    - Ação Recomendada: {context_analysis.get('recommended_action')}
                    
                    Estado Emocional do Lead:
                    - Emoção Dominante: {emotional_triggers.get('dominant_emotion')}
                    - Urgência: {context_analysis.get('urgency_level')}
                    
                    IMPORTANTE: Se uma análise de imagem foi fornecida acima, USE ESSAS INFORMAÇÕES NA SUA RESPOSTA!
                    Por exemplo, se detectamos uma conta de luz com valor, MENCIONE O VALOR DETECTADO.
                    
                    Responda de forma natural, empática e personalizada, levando em conta todo o contexto e histórico da conversa.
                    
                    {'🚨 IMPORTANTE: Como é o PRIMEIRO CONTATO, APRESENTE-SE como Helen da SolarPrime!' if is_first_contact else '⚠️ NÃO se apresente novamente - vocês já se conhecem!'}
                    """
                    
                    # Usar reasoning APENAS para casos complexos
                    # Determinar se a mensagem atual é complexa
                    is_complex = self._is_complex_message(message)
                    
                    # Debug: Log do prompt sendo enviado
                    emoji_logger.system_info(f"📝 Prompt para o agente (primeiros 500 chars): {contextual_prompt[:500]}...")
                    emoji_logger.system_info(f"📏 Tamanho do prompt: {len(contextual_prompt)} caracteres")
                    
                    # Debug: Verificar se multimodal foi incluído
                    if multimodal_result and 'content' in multimodal_result:
                        emoji_logger.system_info(f"✅ Multimodal incluído no prompt: {multimodal_result.get('content', '')[:200]}...")
                    else:
                        emoji_logger.system_info("❌ Nenhum resultado multimodal incluído no prompt")
                    
                    # Debug adicional: verificar se multimodal_result foi incluído
                    if multimodal_result and not multimodal_result.get('error'):
                        emoji_logger.system_info(f"🖼️ Multimodal incluído no prompt: tipo={multimodal_result.get('type')}, tem conteúdo={bool(multimodal_result.get('content'))}")
                    
                    # Timeout para evitar travamento
                    AGENT_TIMEOUT = 45  # segundos
                    
                    if self.reasoning_enabled and is_complex:
                        emoji_logger.agentic_thinking(f"Mensagem complexa detectada, ativando reasoning mode")
                        # Usar reasoning model para perguntas complexas
                        try:
                            emoji_logger.system_info(f"🚀 Chamando agent.arun com timeout de {AGENT_TIMEOUT}s (modo complexo)...")
                            if hasattr(self, 'reasoning_model'):
                                result = await asyncio.wait_for(
                                    self.agent.arun(contextual_prompt),
                                    timeout=AGENT_TIMEOUT
                                )
                            else:
                                result = await asyncio.wait_for(
                                    self.agent.arun(contextual_prompt),
                                    timeout=AGENT_TIMEOUT
                                )
                            emoji_logger.system_info("✅ agent.arun completou com sucesso (modo complexo)")
                        except asyncio.TimeoutError:
                            emoji_logger.system_error("Agent Timeout", f"❌ Timeout em agent.arun após {AGENT_TIMEOUT}s (modo complexo)")
                            result = None
                        except Exception as e:
                            emoji_logger.system_error("Agent Error", f"❌ Erro em agent.arun (modo complexo): {str(e)}")
                            result = None
                    else:
                        # Mensagem simples - resposta direta sem reasoning
                        emoji_logger.agentic_thinking(f"Mensagem simples, resposta direta")
                        
                        # Debug: Log antes de chamar o agente
                        emoji_logger.system_info("🚀 Preparando para chamar agent.arun...")
                        emoji_logger.system_info(f"📝 Agent tem instructions? {bool(self.agent.instructions)}")
                        emoji_logger.system_info(f"📝 Agent tem memory? {bool(self.agent.memory)}")
                        emoji_logger.system_info(f"📝 Agent tem model? {bool(self.agent.model)}")
                        
                        try:
                            emoji_logger.system_info(f"🚀 Chamando agent.arun com timeout de {AGENT_TIMEOUT}s...")
                            
                            # PROTEÇÃO EXTRA: Verificar se agent está pronto
                            if not self.agent or not hasattr(self.agent, 'arun'):
                                emoji_logger.system_error("Agent State", "❌ Agent não está pronto ou não tem método arun")
                                result = self._generate_simple_fallback_response(message)
                            else:
                                # Criar task para poder cancelar se necessário
                                agent_task = asyncio.create_task(self.agent.arun(contextual_prompt))
                                
                                try:
                                    result = await asyncio.wait_for(agent_task, timeout=AGENT_TIMEOUT)
                                    emoji_logger.system_info("✅ agent.arun completou com sucesso")
                                except asyncio.TimeoutError:
                                    # Cancelar task se ainda estiver rodando
                                    agent_task.cancel()
                                    try:
                                        await agent_task
                                    except asyncio.CancelledError:
                                        pass
                                    raise
                        except asyncio.TimeoutError:
                            emoji_logger.system_error("Agent Timeout", f"❌ Timeout em agent.arun após {AGENT_TIMEOUT}s")
                            # Tentar gerar resposta de fallback
                            try:
                                emoji_logger.system_info("🔄 Tentando gerar resposta de fallback...")
                                result = self._generate_simple_fallback_response(message)
                            except Exception as fallback_error:
                                emoji_logger.system_error("Fallback Error", f"❌ Falha no fallback: {str(fallback_error)}")
                                result = None
                        except Exception as arun_error:
                            emoji_logger.system_error("Agent Error", f"❌ Erro em agent.arun: {str(arun_error)}")
                            import traceback
                            emoji_logger.system_error("Stack Trace", f"Stack trace: {traceback.format_exc()}")
                            result = None
                    
                    # Debug: Log do resultado recebido
                    emoji_logger.system_info(f"🔍 Tipo do result: {type(result)}")
                    emoji_logger.system_info(f"🔍 result tem content? {hasattr(result, 'content')}")
                    if hasattr(result, '__dict__'):
                        emoji_logger.system_info(f"🔍 Atributos do result: {list(result.__dict__.keys())}")
                    else:
                        emoji_logger.system_info(f"🔍 result como string: {str(result)[:200]}...")
                    
                    # Debug adicional para entender o resultado
                    if result:
                        emoji_logger.system_info(f"📋 Result não é None, tipo: {type(result).__name__}")
                    else:
                        emoji_logger.system_warning("⚠️ Result é None ou vazio!")
                    
                    # Extrair conteúdo da resposta - CORREÇÃO PARA AGNO RunResponse
                    raw_response = None
                    
                    # 1. Tentar content primeiro
                    if hasattr(result, 'content'):
                        emoji_logger.system_info(f"🔍 result.content existe: tipo={type(result.content).__name__}, valor={repr(result.content)[:100]}")
                        
                        # IMPORTANTE: Verificar se content é True (booleano) em vez de string
                        if result.content is True:
                            emoji_logger.system_warning("⚠️ result.content é True (booleano)! Verificando messages...")
                        elif result.content:
                            # Verificar se content é um objeto complexo
                            if hasattr(result.content, 'text'):
                                raw_response = result.content.text
                            elif hasattr(result.content, 'value'):
                                raw_response = result.content.value
                            elif isinstance(result.content, str):
                                raw_response = result.content
                            else:
                                raw_response = str(result.content)
                            emoji_logger.system_info(f"✅ Conteúdo extraído de result.content: tipo={type(raw_response).__name__}, tamanho={len(str(raw_response)) if raw_response else 0}")
                            
                            # 🚨 CORREÇÃO CRÍTICA: Se já extraímos content com sucesso, marcar para NÃO CONTINUAR!
                            content_extracted_successfully = True if (raw_response and raw_response != "" and str(raw_response) != "True") else False
                            if content_extracted_successfully:
                                emoji_logger.system_info("✅ Content extraído com sucesso - vamos pular outras tentativas")
                    
                    # 2. Se vazio ou content=True, verificar messages (AGNO padrão)
                    if (not raw_response or raw_response == "" or result.content is True) and hasattr(result, 'messages') and result.messages and not locals().get('content_extracted_successfully', False):
                        emoji_logger.system_info(f"🔍 Verificando {len(result.messages)} mensagens em result.messages")
                        for i, msg in enumerate(reversed(result.messages)):
                            emoji_logger.system_info(f"🔍 Mensagem {i}: tipo={type(msg).__name__}, tem role={hasattr(msg, 'role')}, tem content={hasattr(msg, 'content')}")
                            if hasattr(msg, 'role'):
                                emoji_logger.system_info(f"🔍 Mensagem {i} role: {msg.role}")
                            if hasattr(msg, 'content'):
                                emoji_logger.system_info(f"🔍 Mensagem {i} content tipo: {type(msg.content).__name__}, valor: {repr(msg.content)[:100] if msg.content else 'NONE/VAZIO'}")
                                if hasattr(msg.content, '__dict__'):
                                    emoji_logger.system_info(f"🔍 Mensagem {i} content atributos: {list(msg.content.__dict__.keys())}")
                            
                            if hasattr(msg, 'role') and msg.role == 'assistant' and hasattr(msg, 'content'):
                                # Garantir que msg.content seja convertido para string se necessário
                                if msg.content is not None:
                                    # Se for um objeto complexo, tentar extrair o texto
                                    if hasattr(msg.content, 'text'):
                                        raw_response = msg.content.text
                                    elif hasattr(msg.content, 'value'):
                                        raw_response = msg.content.value
                                    elif isinstance(msg.content, str):
                                        raw_response = msg.content
                                    else:
                                        # Converter para string se não for
                                        raw_response = str(msg.content)
                                    
                                    emoji_logger.system_info(f"✅ Conteúdo extraído de messages[{i}]: tipo={type(raw_response).__name__}, tamanho={len(str(raw_response)) if raw_response else 0}")
                                    if raw_response and str(raw_response).strip():  # Garantir que não está vazio
                                        break
                    # 3. Outros atributos - APENAS se ainda não extraímos nada
                    if (not raw_response or raw_response == "") and not locals().get('content_extracted_successfully', False):
                        if hasattr(result, 'text') and result.text:
                            raw_response = result.text
                        elif hasattr(result, 'message') and result.message:
                            raw_response = result.message
                        elif isinstance(result, dict):
                            raw_response = result.get('content') or result.get('text') or str(result)
                        else:
                            # 🚨 ÚLTIMO RECURSO: só usar str(result) se REALMENTE não temos nada
                            if not raw_response or raw_response == "":
                                raw_response = str(result)
                                emoji_logger.system_warning("⚠️ Usando str(result) como último recurso")
                            else:
                                emoji_logger.system_info("✅ Já temos raw_response, não vamos sobrescrever!")
                    
                    # Debug: Log do conteúdo extraído
                    emoji_logger.system_info(f"📄 raw_response tipo: {type(raw_response).__name__ if raw_response else 'None'}")
                    emoji_logger.system_info(f"📄 raw_response (primeiros 200 chars): {raw_response[:200] if raw_response else 'VAZIO'}...")
                    emoji_logger.system_info(f"📏 Tamanho raw_response: {len(raw_response) if raw_response else 0} caracteres")
                    
                    # Debug adicional para entender conteúdo vazio
                    if raw_response and len(str(raw_response)) == 0:
                        emoji_logger.system_warning(f"⚠️ raw_response existe mas está vazio! tipo={type(raw_response).__name__}, repr={repr(raw_response)}")
                    
                    # CORREÇÃO: Verificar se é None ou "None" ou lista vazia
                    if (raw_response is None or 
                        str(raw_response).strip().lower() == "none" or
                        (isinstance(raw_response, list) and len(raw_response) == 0) or
                        (isinstance(raw_response, str) and raw_response.strip() == "")):
                        emoji_logger.system_warning("⚠️ raw_response é None ou vazio! Usando fallback...")
                        raw_response = None  # Força None para cair no fallback
                    
                    # Verificar se resposta está vazia antes de processar
                    if not raw_response or str(raw_response).strip() == "":
                        emoji_logger.system_warning("⚠️ raw_response está vazio ANTES da verificação!")
                    
                    # ✅ CORREÇÃO: Verificar se a resposta está vazia antes de processar
                    if not raw_response or raw_response.strip() == "" or str(raw_response).strip().lower() == "none":
                        emoji_logger.system_warning("⚠️ Agent retornou resposta vazia! Usando fallback...")
                        
                        # Debug: Entender por que está vazio
                        if multimodal_result and 'content' in multimodal_result and not multimodal_result.get('error'):
                            emoji_logger.system_info("🔍 Tinha análise multimodal mas agente retornou vazio")
                            emoji_logger.system_info(f"🔍 Análise multimodal: {multimodal_result.get('content', '')[:100]}...")
                            
                            # Fallback especializado para quando há análise multimodal
                            if multimodal_result.get('is_bill'):
                                # É uma conta de luz
                                bill_amount = multimodal_result.get('bill_amount', 0)
                                if bill_amount > 0:
                                    raw_response = f"Perfeito! Vi aqui sua conta de luz no valor de R$ {bill_amount:.2f}. Com esse valor, consigo fazer uma análise bem precisa de quanto você pode economizar com energia solar! Esse valor está pesando no orçamento?"
                                else:
                                    raw_response = "Ótimo! Recebi a foto da sua conta de luz. Para fazer uma análise precisa da economia, você pode me dizer qual o valor médio que está pagando?"
                            elif multimodal_result.get('type') == 'image':
                                # Imagem genérica
                                raw_response = "Legal! Recebi sua imagem. Para eu fazer uma proposta personalizada de economia com energia solar, me conta: qual o valor médio da sua conta de luz?"
                            elif multimodal_result.get('type') == 'audio':
                                # Áudio transcrito
                                transcription = multimodal_result.get('transcription', '')
                                if transcription:
                                    raw_response = f"Entendi! Ouvi seu áudio dizendo: '{transcription[:100]}...'. Como posso ajudar você com energia solar?"
                                else:
                                    raw_response = "Recebi seu áudio! Para fazer uma análise completa, preciso saber: qual o valor da sua conta de luz?"
                            else:
                                # Fallback genérico com mídia
                                raw_response = "Obrigada por enviar! Para fazer uma proposta personalizada de economia, preciso saber o valor da sua conta de luz. Quanto você paga em média?"
                        else:
                            emoji_logger.system_info("🔍 Sem análise multimodal disponível")
                            # Fallback com base no estágio atual
                            current_stage = lead_data.get('current_stage', 'INITIAL_CONTACT') if lead_data else 'INITIAL_CONTACT'
                            if current_stage == 'INITIAL_CONTACT':
                                raw_response = "Oi! Tudo bem? Sou a Helen da SolarPrime! Antes de começarmos, como posso te chamar?"
                            else:
                                raw_response = "Oi! Desculpe, tive um probleminha aqui. Pode repetir sua última mensagem?"
                    
                    # ✅ CORREÇÃO: Verificar se já há tags antes de adicionar (evita duplicação)
                    if "<RESPOSTA_FINAL>" in raw_response:
                        # Resposta já tem tags - usar diretamente
                        response = raw_response
                        emoji_logger.system_debug("✅ Tags <RESPOSTA_FINAL> já presentes - usando resposta diretamente")
                    else:
                        # Resposta sem tags - adicionar tags para extração
                        response = f"<RESPOSTA_FINAL>{raw_response}</RESPOSTA_FINAL>"
                        emoji_logger.system_debug("➕ Adicionando tags <RESPOSTA_FINAL> à resposta")
                    
                    # 🚨 CORREÇÃO CRÍTICA: Verificar se response contém RunResponse serializado
                    if "RunResponse(" in str(response):
                        emoji_logger.system_error("🚨 ERRO CRÍTICO: response contém RunResponse serializado!")
                        emoji_logger.system_error(f"Tamanho do response: {len(str(response))} caracteres")
                        # Tentar extrair apenas o conteúdo de dentro do RunResponse
                        import re
                        match = re.search(r"RunResponse\(content='([^']+)'", str(response))
                        if match:
                            content_only = match.group(1)
                            response = f"<RESPOSTA_FINAL>{content_only}</RESPOSTA_FINAL>"
                            emoji_logger.system_info(f"✅ Extraído apenas conteúdo: {len(content_only)} caracteres")
                        else:
                            emoji_logger.system_error("❌ Não foi possível extrair conteúdo do RunResponse")
                            response = "<RESPOSTA_FINAL>Desculpe, tive um problema técnico. Pode repetir sua mensagem?</RESPOSTA_FINAL>"
                    
                    # 🚨 VALIDAÇÃO DE SEGURANÇA: Verificar se está pedindo dados proibidos
                    forbidden_terms = [
                        'cpf', 'c.p.f', 'cadastro de pessoa', 'documento',
                        'rg', 'r.g', 'identidade', 'cnh', 'c.n.h',
                        'carteira de motorista', 'carteira de identidade',
                        'dados bancários', 'conta bancária', 'senha',
                        'cartão de crédito', 'dados do cartão'
                    ]
                    
                    response_lower = response.lower()
                    
                    # CORREÇÃO: Usar regex para detectar palavras completas, não substrings
                    import re
                    contains_forbidden = False
                    for term in forbidden_terms:
                        # \b marca limites de palavra para evitar falsos positivos
                        pattern = r'\b' + re.escape(term) + r'\b'
                        if re.search(pattern, response_lower):
                            contains_forbidden = True
                            break
                    
                    if contains_forbidden:
                        emoji_logger.system_warning("🚨 ALERTA: Resposta contém solicitação de dados proibidos!")
                        emoji_logger.system_warning(f"Resposta original: {response}")
                        
                        # Substituir resposta por uma segura baseada no contexto
                        if multimodal_result and 'content' in multimodal_result:
                            # Se tem análise de imagem, focar nisso
                            analysis = multimodal_result.get('content', '')
                            if 'conta' in analysis.lower() and 'valor' in analysis.lower():
                                response = "<RESPOSTA_FINAL>Perfeito! Vi sua conta de luz aqui. Vamos calcular quanto você pode economizar com energia solar! Me conta, esse valor está pesando no seu bolso?</RESPOSTA_FINAL>"
                            else:
                                response = "<RESPOSTA_FINAL>Legal! Recebi sua imagem. Para fazer uma análise completa, preciso saber: qual o valor médio da sua conta de luz?</RESPOSTA_FINAL>"
                        else:
                            # Resposta genérica segura
                            response = "<RESPOSTA_FINAL>Ótimo! Para eu fazer uma proposta personalizada de economia, preciso apenas saber o valor da sua conta de luz. Quanto você está pagando em média?</RESPOSTA_FINAL>"
                        
                        emoji_logger.system_debug(f"✅ Resposta substituída por versão segura: {response}")
                    
                except Exception as agent_error:
                    emoji_logger.system_error("AGENTIC SDR", f"Erro ao gerar resposta: {agent_error}")
                    # Fallback para resposta padrão
                    response = None
            
            # Garantir que SEMPRE temos uma resposta
            if not response or response.strip() == "":
                emoji_logger.system_warning("Nenhuma resposta gerada, usando fallback")
                # Resposta fallback baseada no contexto
                if "oi" in message.lower() or "olá" in message.lower() or "ola" in message.lower():
                    if is_first_contact:
                        response = "<RESPOSTA_FINAL>Oi! Tudo bem? Sou a Helen da Solar Prime! Como posso ajudar você hoje?</RESPOSTA_FINAL>"
                    else:
                        response = "<RESPOSTA_FINAL>Oi! Tudo bem? Como posso ajudar você?</RESPOSTA_FINAL>"
                elif "bom dia" in message.lower():
                    if is_first_contact:
                        response = "<RESPOSTA_FINAL>Bom dia! Que legal você entrar em contato! Sou a Helen da Solar Prime. Em que posso ajudar?</RESPOSTA_FINAL>"
                    else:
                        response = "<RESPOSTA_FINAL>Bom dia! Em que posso ajudar?</RESPOSTA_FINAL>"
                elif "boa tarde" in message.lower():
                    if is_first_contact:
                        response = "<RESPOSTA_FINAL>Boa tarde! Obrigada por entrar em contato com a Solar Prime! Sou a Helen, como posso ajudar?</RESPOSTA_FINAL>"
                    else:
                        response = "<RESPOSTA_FINAL>Boa tarde! Como posso ajudar?</RESPOSTA_FINAL>"
                elif "boa noite" in message.lower():
                    if is_first_contact:
                        response = "<RESPOSTA_FINAL>Boa noite! Que bom falar com você! Sou a Helen da Solar Prime. Como posso ajudar?</RESPOSTA_FINAL>"
                    else:
                        response = "<RESPOSTA_FINAL>Boa noite! Como posso ajudar?</RESPOSTA_FINAL>"
                else:
                    response = "<RESPOSTA_FINAL>Olá! Sou a Helen da Solar Prime. Vi sua mensagem e adoraria ajudar! Você tem interesse em economizar na conta de luz com energia solar?</RESPOSTA_FINAL>"
            
            # 7. Atualizar estado emocional da Helen com análise completa
            try:
                # Recalcular com dados completos da conversa
                current_state = current_emotional_state or "ENTUSIASMADA"
                new_emotional_state = self._update_emotional_state(
                    emotional_triggers, 
                    context_analysis,
                    current_state
                )
                
                # Salva o novo estado no banco para a próxima interação (usando import global)
                if conversation_id:
                    await supabase_client.update_conversation_emotional_state(
                        conversation_id,
                        new_emotional_state
                    )
            except Exception as e:
                emoji_logger.system_error("AGENTIC SDR", f"Erro ao atualizar estado emocional: {str(e)}")
                new_emotional_state = current_emotional_state or "ENTUSIASMADA"
            
            # 8. Memória é gerenciada automaticamente pelo Agent no AGNO v1.7.6
            # O Agent salva automaticamente as interações quando configurado com memory
            # Não precisa chamar explicitamente memory.add()
            
            # 9. Aplicar simulação de digitação natural
            # Garantir que response tem um valor antes de aplicar simulação
            if response and str(response).strip() != "" and str(response).strip().lower() != "none":
                response = self._apply_typing_simulation(response)
            else:
                # Fallback final se ainda não houver resposta ou se for None
                emoji_logger.system_warning("⚠️ Response vazio ou None no final, usando fallback de emergência")
                
                # Verificar contexto para resposta apropriada
                if messages_history and len(messages_history) > 0:
                    # Já há conversa anterior
                    response = "<RESPOSTA_FINAL>Oi! Me desculpe, tive um pequeno problema aqui. Pode repetir sua última mensagem?</RESPOSTA_FINAL>"
                else:
                    # Primeira interação
                    response = "<RESPOSTA_FINAL>Oi! 😊 Sou a Helen da Solar Prime. Como posso ajudar você hoje?</RESPOSTA_FINAL>"
            
            # 10. Determinar se deve reagir ou responder citando
            result = {
                "text": response,
                "reaction": None,
                "reply_to": None
            }
            
            # Lógica mais natural: apenas ~10% de chance de reagir ou citar
            import random
            
            # Reações: apenas para mensagens muito específicas (10% de chance)
            message_lower = message.lower().strip()
            if random.random() < 0.1:  # 10% de chance
                # Reações para confirmações muito curtas
                if len(message_lower) < 10 and any(word in message_lower for word in ["ok", "blz", "👍"]):
                    result["reaction"] = "👍"
                # Reações para agradecimentos explícitos
                elif len(message_lower) < 20 and any(word in message_lower for word in ["obrigado", "obrigada", "valeu"]):
                    result["reaction"] = "❤️"
                # Reações para risadas
                elif any(indicator in message_lower for indicator in ["kkkkk", "hahaha", "😂😂", "🤣🤣"]):
                    result["reaction"] = "😂"
            
            # Reação especial para imagens/documentos recebidos
            if media and media.get("type") in ["image", "document", "pdf"]:
                result["reaction"] = "✅"  # Confirma recebimento de mídia
            
            # Citações: apenas em contextos muito específicos (10% de chance)
            if message_id and random.random() < 0.1:
                # Citar quando há múltiplas perguntas ou contexto importante
                question_count = message.count("?")
                if question_count > 1:  # Múltiplas perguntas
                    result["reply_to"] = message_id
                # Citar quando está respondendo a uma dúvida específica após outras mensagens
                elif conversation_id and len(messages_history or []) > 5 and "?" in message:
                    result["reply_to"] = message_id
            
            emoji_logger.agentic_response(f"Resposta gerada: {response[:100]}...")
            
            # Retornar estrutura enriquecida
            return result
            
        except Exception as e:
            emoji_logger.system_error("AGENTIC SDR", f"Erro crítico ao processar: {e}")
            # Resposta de emergência mais natural
            emergency_responses = [
                "<RESPOSTA_FINAL>Oi! Sou a Helen da Solar Prime! Como posso ajudar você hoje com energia solar?</RESPOSTA_FINAL>",
                "<RESPOSTA_FINAL>Olá! Que bom você entrar em contato! Sou a Helen, especialista em energia solar. Em que posso ajudar?</RESPOSTA_FINAL>",
                "<RESPOSTA_FINAL>Oi! Tudo bem? Sou a Helen da Solar Prime! Você tem interesse em economizar na conta de luz?</RESPOSTA_FINAL>"
            ]
            import random
            # Retornar estrutura consistente mesmo em erro
            return {
                "text": random.choice(emergency_responses),
                "reaction": None,
                "reply_to": None
            }
    
    async def _personalize_team_response(
        self,
        team_response: str,
        emotional_triggers: Dict[str, Any],
        emotional_state: str = "ENTUSIASMADA"
    ) -> str:
        """Personaliza resposta do Team com toque do AGENTIC SDR"""
        
        # Adicionar personalização baseada no estado emocional
        personalization_prompt = f"""
        Resposta técnica: {team_response}
        
        Emoção do lead: {emotional_triggers.get('dominant_emotion')}
        Seu estado emocional: {emotional_state}
        
        Reescreva mantendo a informação mas com seu toque pessoal,
        empatia e naturalidade. Mantenha breve e direto.
        """
        
        # Em AGNO v1.7.6, usar run()
        # Usar arun() para suporte assíncrono com timeout
        PERSONALIZATION_TIMEOUT = 15  # timeout menor para personalização
        
        try:
            if hasattr(self.agent, 'arun'):
                result = await asyncio.wait_for(
                    self.agent.arun(personalization_prompt),
                    timeout=PERSONALIZATION_TIMEOUT
                )
            else:
                # Fallback para run() se arun() não estiver disponível
                result = await asyncio.wait_for(
                    self.agent.run(personalization_prompt),
                    timeout=PERSONALIZATION_TIMEOUT
                )
        except asyncio.TimeoutError:
            emoji_logger.system_warning(f"Timeout na personalização após {PERSONALIZATION_TIMEOUT}s, usando resposta original")
            return team_response  # Retorna resposta original sem personalização
        except Exception as e:
            emoji_logger.system_error("Personalization", f"Erro na personalização: {str(e)}, usando resposta original")
            return team_response  # Retorna resposta original sem personalização
        
        # Extrair conteúdo da resposta com múltiplas tentativas
        raw_response = None
        
        # 1. Tentar content primeiro
        if hasattr(result, 'content') and result.content is not None and result.content is not True:
            # Verificar se content é um objeto complexo
            if hasattr(result.content, 'text'):
                raw_response = result.content.text
            elif hasattr(result.content, 'value'):
                raw_response = result.content.value
            elif isinstance(result.content, str):
                raw_response = result.content
            else:
                raw_response = str(result.content)
            emoji_logger.system_info(f"✅ Conteúdo personalizado extraído de result.content: tamanho={len(str(raw_response)) if raw_response else 0}")
        
        # 2. Se ainda não temos conteúdo, tentar outros atributos
        if not raw_response or raw_response == "":
            if hasattr(result, 'text') and result.text is not None:
                raw_response = result.text
            elif hasattr(result, 'message') and result.message is not None:
                raw_response = result.message
            elif isinstance(result, dict):
                raw_response = result.get('content') or result.get('text') or result.get('message')
                if not raw_response:
                    raw_response = str(result)
            else:
                raw_response = str(result)
        
        # ✅ CORREÇÃO: Verificar se já há tags antes de adicionar (evita duplicação)
        if "<RESPOSTA_FINAL>" in raw_response:
            # Resposta já tem tags - usar diretamente
            emoji_logger.system_debug("✅ Tags <RESPOSTA_FINAL> já presentes na personalização - usando diretamente")
            return raw_response
        else:
            # Resposta sem tags - adicionar tags para extração
            emoji_logger.system_debug("➕ Adicionando tags <RESPOSTA_FINAL> à personalização")
            return f"<RESPOSTA_FINAL>{raw_response}</RESPOSTA_FINAL>"
    
    def _update_emotional_state(
        self,
        emotional_triggers: Dict[str, Any],
        context_analysis: Dict[str, Any],
        current_state: str
    ) -> str:
        """Calcula novo estado emocional baseado na conversa - Alinhado com banco"""
        
        # Validar estado atual
        valid_states = [state.value for state in EmotionalState]
        if current_state not in valid_states:
            current_state = EmotionalState.NEUTRA.value
        
        # Lógica de transição de estados atualizada
        dominant_emotion = emotional_triggers.get("dominant_emotion")
        
        if dominant_emotion == "frustration" or dominant_emotion == "hesitation":
            # Usuário com dúvidas ou hesitação
            new_state = EmotionalState.DUVIDOSA.value
        
        elif dominant_emotion == "excitement" or dominant_emotion == "interest":
            # Usuário animado ou interessado
            new_state = EmotionalState.ENTUSIASMADA.value
        
        elif dominant_emotion == "curiosity" or emotional_triggers.get("questions_asked", 0) > 2:
            # Usuário fazendo muitas perguntas
            new_state = EmotionalState.CURIOSA.value
        
        elif context_analysis.get("decision_stage") == "decision" or \
             context_analysis.get("conversion_probability", 0) > 0.7:
            # Usuário próximo da decisão
            new_state = EmotionalState.CONFIANTE.value
        
        elif emotional_triggers.get("neutral_indicators", 0) > 2:
            # Conversa neutra/inicial
            new_state = EmotionalState.NEUTRA.value
        
        else:
            # Mantém o estado atual se válido
            new_state = current_state if current_state in valid_states else EmotionalState.NEUTRA.value
        
        emoji_logger.agentic_thinking(f"Estado emocional atualizado: {new_state}",
                                     emotional_state=new_state)
        
        return new_state
    
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
            "cognitive_load": self.cognitive_load,
            "is_initialized": self.is_initialized
        }


# Factory function - SEMPRE cria nova instância para isolamento total
async def create_agentic_sdr() -> AgenticSDR:
    """Cria e inicializa nova instância do AGENTIC SDR para cada requisição"""
    agent = AgenticSDR()
    await agent.initialize()
    return agent