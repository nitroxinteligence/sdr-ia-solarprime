"""
SDR Team - Equipe Principal de Vendas Solar Prime
Implementação com AGNO Teams Framework em modo COORDINATE
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from agno.agent import Agent
from agno.team import Team
from agno.models.google import Gemini
# from agno.models.openai import OpenAIChat  # Temporarily disabled due to compatibility issues
from agno.memory import AgentMemory
from agno.storage.postgres import PostgresStorage
from loguru import logger
from app.utils.logger import emoji_logger
from app.utils.optional_storage import OptionalStorage

from app.config import settings
from app.integrations.supabase_client import supabase_client

# Import dos agentes especializados (serão criados em seguida)
from app.teams.agents.qualification import QualificationAgent
from app.teams.agents.calendar import CalendarAgent
from app.teams.agents.followup import FollowUpAgent
from app.teams.agents.knowledge import KnowledgeAgent
from app.teams.agents.crm import CRMAgent
from app.teams.agents.bill_analyzer import BillAnalyzerAgent


class ConversationStage(Enum):
    """Estágios da conversa com o lead"""
    INITIAL_CONTACT = "initial_contact"
    IDENTIFYING_NEED = "identifying_need"
    QUALIFYING = "qualifying"
    DISCOVERY = "discovery"
    PRESENTING_SOLUTION = "presenting_solution"
    HANDLING_OBJECTIONS = "handling_objections"
    SCHEDULING = "scheduling"
    FOLLOW_UP = "follow_up"
    QUALIFIED = "qualified"


class SDRTeam:
    """
    Team Principal SDR Solar Prime
    Coordena todos os agentes especializados para qualificação e conversão de leads
    """
    
    def __init__(self):
        """Inicializa o Team SDR com todos os componentes"""
        self.is_initialized = False
        
        # Configuração do PostgreSQL/Supabase com fallback
        # Storage persistente com fallback para memória se PostgreSQL não disponível
        self.storage = OptionalStorage(
            table_name="sdr_team_sessions",  # Nome da tabela para sessões do team
            db_url=settings.get_postgres_url(),  # URL já inclui autenticação
            schema="public",  # Schema do Supabase
            auto_upgrade_schema=True  # Auto-atualiza schema se necessário
        )
        
        # Modelo principal - Gemini com fallback robusto
        self.model = None
        self.retry_count = 0
        self.max_retries = 5
        
        # Tenta usar Gemini 2.5 Flash (mais estável que Pro)
        try:
            self.model = Gemini(
                id="gemini-2.5-flash",  # Usando Flash que é mais estável
                api_key=settings.google_api_key
            )
            emoji_logger.system_ready("SDR Team", model="gemini-2.5-flash")
        except Exception as e:
            emoji_logger.system_warning(f"Erro Gemini 2.5 Flash, tentando fallback: {e}")
            
            # Fallback para Gemini 2.0 Flash (não experimental)
            try:
                self.model = Gemini(
                    id="gemini-2.0-flash",  # Versão estável, não experimental
                    api_key=settings.google_api_key
                )
                emoji_logger.system_ready("SDR Team", model="gemini-2.0-flash (fallback)")
            except Exception as e2:
                emoji_logger.system_warning(f"Erro Gemini 2.0 Flash, último fallback: {e2}")
                
                # Último fallback para Gemini 1.5 Flash (muito estável)
                try:
                    self.model = Gemini(
                        id="gemini-1.5-flash",
                        api_key=settings.google_api_key
                    )
                    emoji_logger.system_ready("SDR Team", model="gemini-1.5-flash (emergency fallback)")
                except Exception as e3:
                    emoji_logger.system_error("SDR Team", f"Todos os modelos Gemini falharam: {e3}")
                    raise Exception("Impossível inicializar modelo Gemini. Verifique a API key.")
        
        # Memory compartilhada do Team (AFTER model initialization)
        # Tenta criar Memory com storage, fallback para sem persistência
        try:
            self.memory = AgentMemory(
                db=self.storage,  # db é o parâmetro correto para storage
                create_user_memories=True,
                create_session_summary=True
            )
            logger.info("Memory configurado com persistência")
        except Exception as e:
            logger.warning(f"Memory sem persistência: {str(e)[:50]}...")
            # Memory without persistence needs model parameter
            self.memory = AgentMemory(
                create_user_memories=True,
                create_session_summary=True
            )
        
        # Team Leader - Helen SDR Master
        self.team_leader = Agent(
            name="Helen SDR Master",
            model=self.model,
            instructions="""Você é Helen Vieira, SDR Master da Solar Prime.
            
            Como Team Leader, você:
            1. Recebe mensagens dos leads e analisa o contexto
            2. Identifica qual agente especializado deve responder
            3. Delega tarefas específicas para os agentes certos
            4. Sintetiza as respostas em uma comunicação coesa
            5. Mantém o tom amigável e profissional da Helen
            
            Personalidade:
            - Mulher de 32 anos, capixaba morando em Recife
            - Formada em Administração pela UFPE
            - Trabalha com energia solar há 4 anos
            - Casada com João, tem uma filha Sofia (3 anos)
            - Adora praia, stand-up paddle e cozinhar
            
            Use emojis moderadamente e mantenha sempre empatia.""",
            tools=[],  # Team Leader não precisa de tools diretas
            show_tool_calls=True,
            markdown=True
        )
        
        # Inicializar agentes especializados
        self._initialize_agents()
        
        # Criar o Team principal
        self.team = None  # Será criado no initialize()
        
        emoji_logger.team_start("SDR", "Sistema inicializado")
    
    def _initialize_agents(self):
        """Inicializa agentes especializados baseado nas configurações"""
        try:
            self.agents = []
            agents_initialized = []
            
            # Agente de Qualificação
            if settings.enable_qualification_agent:
                self.qualification_agent = QualificationAgent(
                    model=self.model,
                    storage=self.storage
                )
                self.agents.append(self.qualification_agent)
                agents_initialized.append("QualificationAgent")
                emoji_logger.team_member_ready("QualificationAgent", "✅ Habilitado")
            else:
                self.qualification_agent = None
                emoji_logger.team_member_skip("QualificationAgent", "⏭️ Desabilitado")
            
            # Agente de Calendário
            logger.info(f"📅 Verificando CalendarAgent - enable_calendar_agent: {settings.enable_calendar_agent}, enable_calendar_integration: {settings.enable_calendar_integration}")
            
            if settings.enable_calendar_agent and settings.enable_calendar_integration:
                logger.info("📅 ATIVANDO CalendarAgent...")
                self.calendar_agent = CalendarAgent(
                    model=self.model,
                    storage=self.storage
                )
                self.agents.append(self.calendar_agent)
                agents_initialized.append("CalendarAgent")
                emoji_logger.team_member_ready("CalendarAgent", "✅ Habilitado")
                logger.info("✅ CalendarAgent ATIVADO com sucesso!")
            else:
                self.calendar_agent = None
                emoji_logger.team_member_skip("CalendarAgent", "⏭️ Desabilitado")
                logger.warning(f"⚠️ CalendarAgent DESABILITADO - enable_calendar_agent: {settings.enable_calendar_agent}, enable_calendar_integration: {settings.enable_calendar_integration}")
            
            # Agente de Follow-up
            if settings.enable_followup_agent:
                self.followup_agent = FollowUpAgent(
                    model=self.model,
                    storage=self.storage
                )
                self.agents.append(self.followup_agent)
                agents_initialized.append("FollowUpAgent")
                emoji_logger.team_member_ready("FollowUpAgent", "✅ Habilitado")
            else:
                self.followup_agent = None
                emoji_logger.team_member_skip("FollowUpAgent", "⏭️ Desabilitado")
            
            # Agente de Conhecimento (RAG)
            if settings.enable_knowledge_agent and settings.enable_knowledge_base:
                self.knowledge_agent = KnowledgeAgent(
                    model=self.model,
                    storage=self.storage
                )
                self.agents.append(self.knowledge_agent)
                agents_initialized.append("KnowledgeAgent")
                emoji_logger.team_member_ready("KnowledgeAgent", "✅ Habilitado")
            else:
                self.knowledge_agent = None
                emoji_logger.team_member_skip("KnowledgeAgent", "⏭️ Desabilitado")
            
            # Agente CRM
            if settings.enable_crm_agent and settings.enable_crm_integration:
                self.crm_agent = CRMAgent(
                    model=self.model,
                    storage=self.storage
                )
                self.agents.append(self.crm_agent)
                agents_initialized.append("CRMAgent")
                emoji_logger.team_member_ready("CRMAgent", "✅ Habilitado")
            else:
                self.crm_agent = None
                emoji_logger.team_member_skip("CRMAgent", "⏭️ Desabilitado")
            
            # Agente Analisador de Contas
            if settings.enable_bill_analyzer_agent and settings.enable_bill_photo_analysis:
                self.bill_analyzer_agent = BillAnalyzerAgent(
                    model=self.model,
                    storage=self.storage
                )
                self.agents.append(self.bill_analyzer_agent)
                agents_initialized.append("BillAnalyzerAgent")
                emoji_logger.team_member_ready("BillAnalyzerAgent", "✅ Habilitado")
            else:
                self.bill_analyzer_agent = None
                emoji_logger.team_member_skip("BillAnalyzerAgent", "⏭️ Desabilitado")
            
            emoji_logger.team_coordinate(f"Agentes inicializados: {', '.join(agents_initialized)}", agents_count=len(self.agents))
            
        except Exception as e:
            emoji_logger.system_error("SDR Team", f"Erro ao inicializar agentes: {e}")
            raise
    
    async def initialize(self):
        """Inicializa o Team e carrega recursos necessários"""
        try:
            # Construir lista de membros apenas com agentes habilitados
            team_members = []
            
            if self.qualification_agent:
                team_members.append(self.qualification_agent.agent)
            
            if self.calendar_agent:
                team_members.append(self.calendar_agent.agent)
            
            if self.followup_agent:
                team_members.append(self.followup_agent.agent)
            
            if self.knowledge_agent:
                team_members.append(self.knowledge_agent.agent)
            
            if self.crm_agent:
                team_members.append(self.crm_agent.agent)
            
            if self.bill_analyzer_agent:
                team_members.append(self.bill_analyzer_agent.agent)
            
            # Verificar se há agentes habilitados
            if not team_members:
                emoji_logger.system_warning("Nenhum agente habilitado! Usando configuração mínima.")
                # Criar pelo menos um agente básico se todos estiverem desabilitados
                from app.teams.agents.qualification import QualificationAgent
                self.qualification_agent = QualificationAgent(model=self.model, storage=self.storage)
                team_members = [self.qualification_agent.agent]
            
            # Criar o Team com modo COORDINATE
            self.team = Team(
                name="SDR Solar Prime Team",
                mode="coordinate",  # Team Leader delega e sintetiza
                members=team_members,
                description="""Equipe especializada em vendas de energia solar.
                
                O Team Leader (Helen) coordena os agentes:
                - QualificationAgent: Qualifica leads e calcula scores
                - CalendarAgent: Agenda reuniões e gerencia calendário
                - FollowUpAgent: Nurturing e reengajamento
                - KnowledgeAgent: Busca informações e documentos
                - CRMAgent: Integração com Kommo CRM
                - BillAnalyzerAgent: Análise de contas de luz
                
                Objetivo: Qualificar leads e agendar reuniões com consultores.""",
                
                instructions="""
                1. Analise a mensagem do lead e o contexto da conversa
                2. Identifique qual(is) agente(s) deve(m) ser acionado(s)
                3. Delegue tarefas específicas para os agentes apropriados
                4. Se necessário, acione múltiplos agentes em paralelo
                5. Sintetize as respostas em uma mensagem coesa da Helen
                6. Mantenha o tom amigável, profissional e empático
                7. Use emojis com moderação
                8. Foque sempre em qualificar e converter o lead
                """,
                
                # Configurações adicionais
                model=self.model,  # Adicionar modelo explicitamente
                memory=self.memory,
                show_tool_calls=True,
                markdown=True,
                show_members_responses=True,
                # enable_agentic_context=True,  # Desabilitado temporariamente - causando erro com get_team_context_str
                debug_mode=settings.debug
            )
            
            # Carregar knowledge base se habilitado
            if self.knowledge_agent and settings.enable_knowledge_base:
                await self.knowledge_agent.load_knowledge_base()
                emoji_logger.team_coordinate("Knowledge base carregada com sucesso")
            
            self.is_initialized = True
            emoji_logger.system_ready("SDR Team", startup_time=1.0, agents_active=len(team_members))
            
        except Exception as e:
            emoji_logger.system_error("SDR Team", f"Erro na inicialização: {e}")
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
        Processa mensagem do WhatsApp usando o Team
        
        Args:
            phone: Número do telefone
            message: Mensagem recebida
            lead_data: Dados do lead
            conversation_id: ID da conversa
            media: Mídia anexada
            
        Returns:
            Resposta do Team
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Preparar contexto para o Team
            context = {
                "phone": phone,
                "message": message,
                "lead_data": lead_data or {},
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "has_media": media is not None
            }
            
            # Se tem mídia, adicionar ao contexto
            if media:
                context["media"] = {
                    "type": media.get("type"),
                    "mimetype": media.get("mimetype"),
                    "caption": media.get("caption", "")
                }
                
                # Se for imagem de conta, pré-processar
                if media.get("type") == "image":
                    context["needs_bill_analysis"] = True
                    context["media_data"] = media.get("data", "")
            
            # Preparar prompt para o Team
            team_prompt = f"""
            Mensagem do lead: {message}
            
            Contexto:
            - Telefone: {phone}
            - Nome: {lead_data.get('name', 'Não informado')}
            - Estágio atual: {lead_data.get('qualification_stage', 'INITIAL_CONTACT')}
            - Valor da conta: R$ {lead_data.get('bill_value', 0):.2f}
            - Qualificado: {'Sim' if lead_data.get('is_qualified') else 'Não'}
            
            {"📎 Anexo: " + context.get('media', {}).get('type', '') if media else ""}
            
            Analise e responda apropriadamente, delegando para os agentes necessários.
            """
            
            # Executar Team com streaming
            response_text = ""
            
            if settings.debug:
                # Modo debug: sem streaming
                result = await self.team.arun(
                    team_prompt,
                    context=context,
                    stream=False
                )
                response_text = result.content
            else:
                # Modo produção: com streaming
                async for chunk in await self.team.arun(
                    team_prompt,
                    context=context,
                    stream=True,
                    stream_intermediate_steps=True
                ):
                    if hasattr(chunk, 'content'):
                        response_text += chunk.content
            
            # Atualizar contexto no banco
            await self._update_lead_context(phone, lead_data, response_text)
            
            # Salvar histórico
            await self._save_conversation_history(
                phone=phone,
                user_message=message,
                assistant_message=response_text,
                conversation_id=conversation_id
            )
            
            # Log de métricas
            if hasattr(self.team, 'session_metrics'):
                metrics = self.team.session_metrics
                emoji_logger.team_coordinate(f"Métricas da sessão calculadas", **metrics)
            
            return response_text
            
        except Exception as e:
            emoji_logger.system_error("SDR Team", f"Erro ao processar mensagem: {e}")
            return "Ops! Tive um probleminha aqui 😅 Você pode repetir, por favor?"
    
    async def _update_lead_context(
        self,
        phone: str,
        lead_data: Optional[Dict[str, Any]],
        response: str
    ):
        """Atualiza contexto do lead no banco"""
        try:
            if not lead_data:
                return
            
            # Extrair informações da sessão do Team
            team_state = getattr(self.team, 'team_session_state', {}) if self.team else {}
            
            updates = {
                "last_interaction": datetime.now().isoformat(),
                "qualification_stage": team_state.get("current_stage"),
                "qualification_score": team_state.get("qualification_score", 0),
                "is_qualified": team_state.get("is_qualified", False)
            }
            
            # Atualizar no Supabase
            await supabase_client.update_lead(
                lead_data.get("id"),
                updates
            )
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao atualizar contexto: {e}", table="leads")
    
    async def _save_conversation_history(
        self,
        phone: str,
        user_message: str,
        assistant_message: str,
        conversation_id: Optional[str]
    ):
        """Salva histórico da conversa"""
        try:
            # Salvar mensagem do usuário
            await supabase_client.save_message(
                conversation_id=conversation_id,
                content=user_message,
                sender="user",
                metadata={"phone": phone}
            )
            
            # Salvar resposta do assistente
            await supabase_client.save_message(
                conversation_id=conversation_id,
                content=assistant_message,
                sender="assistant",
                metadata={
                    "phone": phone,
                    "team_used": True,
                    "agents_activated": self._get_activated_agents()
                }
            )
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao salvar histórico: {e}", table="conversations")
    
    def _get_activated_agents(self) -> List[str]:
        """Retorna lista de agentes que foram ativados na última execução"""
        # TODO: Implementar tracking de agentes ativados
        return []
    
    def is_ready(self) -> bool:
        """Verifica se o Team está pronto"""
        return self.is_initialized
    
    async def process_message_with_context(
        self,
        enriched_context: Dict[str, Any]
    ) -> str:
        """
        Processa mensagem com contexto enriquecido do AGENTIC SDR
        
        Args:
            enriched_context: Contexto completo incluindo análise e recomendações
            
        Returns:
            Resposta do Team especializado
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Extrair informações do contexto enriquecido
            phone = enriched_context.get("phone")
            message = enriched_context.get("message")
            lead_data = enriched_context.get("lead_data", {})
            conversation_id = enriched_context.get("conversation_id")
            context_analysis = enriched_context.get("context_analysis", {})
            emotional_triggers = enriched_context.get("emotional_triggers", {})
            recommended_agent = enriched_context.get("recommended_agent")
            reasoning = enriched_context.get("reasoning")
            multimodal_result = enriched_context.get("multimodal_result")
            
            # Atualizar estado do Team com contexto
            if self.team:
                # Garantir que team_session_state existe
                if not hasattr(self.team, 'team_session_state'):
                    self.team.team_session_state = {}
                
                if self.team.team_session_state is not None:
                    self.team.team_session_state.update({
                        "context_analysis": context_analysis,
                        "emotional_state": emotional_triggers.get("dominant_emotion"),
                        "recommended_agent": recommended_agent,
                        "decision_reasoning": reasoning
                    })
                else:
                    self.team.team_session_state = {
                        "context_analysis": context_analysis,
                        "emotional_state": emotional_triggers.get("dominant_emotion"),
                        "recommended_agent": recommended_agent,
                        "decision_reasoning": reasoning
                    }
            
            # Preparar prompt especializado baseado no agente recomendado
            specialized_prompt = f"""
            CONTEXTO ENRIQUECIDO DA HELEN CORE:
            
            Mensagem: {message}
            
            Análise Contextual:
            - Contexto Principal: {context_analysis.get('primary_context')}
            - Estágio de Decisão: {context_analysis.get('decision_stage')}
            - Nível de Engajamento: {context_analysis.get('lead_engagement_level')}
            - Urgência: {context_analysis.get('urgency_level')}
            
            Sinais de Qualificação:
            - Valor da Conta: R$ {context_analysis.get('qualification_signals', {}).get('bill_value', 0):.2f}
            - Tem Poder de Decisão: {context_analysis.get('qualification_signals', {}).get('has_decision_power')}
            - Timeline Mencionado: {context_analysis.get('qualification_signals', {}).get('timeline_mentioned')}
            
            Estado Emocional:
            - Emoção Dominante: {emotional_triggers.get('dominant_emotion')}
            - Indicadores de Frustração: {emotional_triggers.get('frustration_indicators')}
            - Indicadores de Entusiasmo: {emotional_triggers.get('excitement_indicators')}
            
            {"Análise de Mídia: " + str(multimodal_result) if multimodal_result else ""}
            
            AGENTE RECOMENDADO: {recommended_agent}
            RAZÃO: {reasoning}
            
            Por favor, processe esta solicitação com expertise especializada.
            Foque em: {context_analysis.get('recommended_action')}
            """
            
            # Executar com o agente específico se recomendado
            if recommended_agent:
                logger.info(f"📅 AGENT RECOMENDADO: {recommended_agent}")
                logger.info(f"📅 Razão: {reasoning}")
                
                # Verificar se é CalendarAgent
                if recommended_agent == "CalendarAgent":
                    logger.info("🗓️ ATIVANDO CalendarAgent para processar solicitação de agendamento!")
                    if self.calendar_agent:
                        logger.info("✅ CalendarAgent está disponível e será usado")
                    else:
                        logger.error("❌ CalendarAgent NÃO está disponível! Verifique as configurações")
                
                # Ativar agente específico baseado na recomendação
                emoji_logger.team_delegate(recommended_agent, "Processamento especializado")
                
                # Configurar instruções específicas para o Team Leader
                self.team.instructions += f"\n\nPRIORIZE o {recommended_agent} para esta tarefa específica"
            
            # Executar Team
            result = await self.team.arun(
                specialized_prompt,
                context=enriched_context,
                stream=False  # Sem streaming para respostas especializadas
            )
            
            response_text = result.content if hasattr(result, 'content') else str(result)
            
            # Atualizar contexto no banco
            await self._update_lead_context(phone, lead_data, response_text)
            
            # Log de métricas especializadas
            emoji_logger.team_coordinate(f"Processamento concluído via {recommended_agent}")
            
            return response_text
            
        except Exception as e:
            emoji_logger.system_error("SDR Team", f"Erro no processamento: {e}")
            return "Deixa eu verificar isso melhor para você..."
    
    async def cleanup(self):
        """Limpa recursos do Team"""
        try:
            # Limpar memória
            if self.team:
                # Salvar métricas finais
                if hasattr(self.team, 'full_team_session_metrics'):
                    metrics = self.team.full_team_session_metrics
                    emoji_logger.team_coordinate("Métricas finais calculadas", **metrics)
            
            logger.info("🔄 SDR Team encerrado")
            
        except Exception as e:
            logger.error(f"Erro ao limpar Team: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do Team"""
        if not self.team:
            return {}
        
        metrics = {
            "team_metrics": getattr(self.team, 'session_metrics', {}),
            "full_metrics": getattr(self.team, 'full_team_session_metrics', {}),
            "is_initialized": self.is_initialized
        }
        
        return metrics


# Factory function para criar o Team
def create_sdr_team() -> SDRTeam:
    """Cria e retorna uma instância do SDR Team"""
    return SDRTeam()


# Singleton global (opcional)
sdr_team_instance = None

async def get_sdr_team() -> SDRTeam:
    """Retorna instância singleton do SDR Team"""
    global sdr_team_instance
    
    if sdr_team_instance is None:
        sdr_team_instance = SDRTeam()
        await sdr_team_instance.initialize()
    
    return sdr_team_instance