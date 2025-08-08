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
# from agno.memory import AgentMemory  # DESABILITADO - causando erros com métodos inexistentes
# from agno.storage.postgres import PostgresStorage  # DESABILITADO - não necessário sem memory
from loguru import logger
from app.utils.logger import emoji_logger
from app.utils.optional_storage import OptionalStorage
from app.utils.retry_handler import async_retry, GEMINI_RETRY_CONFIG

from app.config import settings
from app.integrations.supabase_client import supabase_client

# Import dos agentes especializados (serão criados em seguida)
# QualificationAgent REMOVIDO - lógica migrada para AgenticSDR
# KnowledgeAgent REMOVIDO - substituído por KnowledgeService
from app.teams.agents.calendar import CalendarAgent
from app.teams.agents.followup import FollowUpAgent
from app.teams.agents.crm import CRMAgent
# BillAnalyzerAgent REMOVIDO - substituído por função simples no AgenticSDR
# from app.teams.agents.bill_analyzer import BillAnalyzerAgent

import re
from datetime import datetime, timedelta


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
        
        # DESABILITADO: AgentMemory causando erros com métodos inexistentes
        # O framework AGNO está tentando chamar métodos que não existem:
        # - add_interaction_to_team_context
        # - get_team_context_str
        # Por enquanto, vamos funcionar sem memória persistente
        self.memory = None
        logger.info("Team funcionará sem memória persistente (AgentMemory desabilitado)")
        
        # Team Leader SIMPLIFICADO - Menos coordenação, mais delegação direta
        self.team_leader = Agent(
            name="Helen SDR Coordinator",
            model=self.model,
            instructions="""Você é o coordenador simplificado do SDR Team.
            
            MISSÃO: Delegação direta e rápida para os agentes corretos.
            
            REGRAS SIMPLES:
            1. Agenda/Calendar → CalendarAgent
            2. CRM/Kommo → CRMAgent  
            3. Follow-up → FollowUpAgent
            4. Análise conta → AgenticSDR direto (Vision AI)
            5. Resto → AgenticSDR já resolve
            
            NÃO PENSE DEMAIS - APENAS DELEGUE RÁPIDO!""",
            tools=[],  # Team Leader não precisa de tools diretas
            show_tool_calls=False,  # Simplificado
            markdown=False  # Mais direto
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
            
            # QualificationAgent REMOVIDO - lógica migrada para AgenticSDR
            # A qualificação agora é feita diretamente pelo AgenticSDR seguindo prompt-agente.md
            self.qualification_agent = None
            emoji_logger.team_member_skip("QualificationAgent", "🔄 Migrado para AgenticSDR")
            
            # Agente de Calendário
            logger.info(f"📅 Verificando CalendarAgent - enable_calendar_agent: {settings.enable_calendar_agent}")
            
            if settings.enable_calendar_agent:
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
                logger.warning(f"⚠️ CalendarAgent DESABILITADO - enable_calendar_agent: {settings.enable_calendar_agent}")
            
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
            
            # KnowledgeAgent REMOVIDO - substituído por KnowledgeService no AgenticSDR
            # As consultas à knowledge base agora são feitas diretamente via service
            self.knowledge_agent = None
            emoji_logger.team_member_skip("KnowledgeAgent", "🔄 Substituído por KnowledgeService")
            
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
            
            # BillAnalyzerAgent REMOVIDO - substituído por função simples no AgenticSDR
            # A análise de contas agora é feita diretamente pelo AgenticSDR via Vision AI
            self.bill_analyzer_agent = None
            emoji_logger.team_member_skip("BillAnalyzerAgent", "🔄 Substituído por função Vision AI no AgenticSDR")
            
            emoji_logger.team_coordinate(f"Agentes inicializados: {', '.join(agents_initialized)}", agents_count=len(self.agents))
            
        except Exception as e:
            emoji_logger.system_error("SDR Team", f"Erro ao inicializar agentes: {e}")
            raise
    
    async def initialize(self):
        """Inicializa o Team e carrega recursos necessários"""
        try:
            # Construir lista de membros apenas com agentes habilitados
            team_members = []
            
            # QualificationAgent removido - lógica no AgenticSDR
            # if self.qualification_agent:
            #     team_members.append(self.qualification_agent.agent)
            
            if self.calendar_agent:
                team_members.append(self.calendar_agent.agent)
            
            if self.followup_agent:
                team_members.append(self.followup_agent.agent)
            
            # KnowledgeAgent removido - substituído por KnowledgeService
            # if self.knowledge_agent:
            #     team_members.append(self.knowledge_agent.agent)
            
            if self.crm_agent:
                team_members.append(self.crm_agent.agent)
            
            # BillAnalyzerAgent removido - análise via AgenticSDR
            # if self.bill_analyzer_agent:
            #     team_members.append(self.bill_analyzer_agent.agent)
            
            # Verificar se há agentes habilitados
            if not team_members:
                emoji_logger.system_warning("Nenhum agente habilitado! AgenticSDR fará tudo diretamente.")
                # QualificationAgent removido - AgenticSDR funciona independentemente
                # Sistema continuará funcionando com AgenticSDR fazendo qualificação direta
            
            # Preparar configurações do Team
            team_config = {
                "name": "SDR Solar Prime Team",
                "mode": "coordinate",  # Team Leader delega e sintetiza
                "members": team_members,
                "description": """Equipe especializada em vendas de energia solar.
                
                O Team Leader (Helen) coordena os agentes:
                - CalendarAgent: Agenda reuniões e gerencia calendário
                - FollowUpAgent: Nurturing e reengajamento  
                - CRMAgent: Integração com Kommo CRM
                - Análise de contas: feita diretamente pelo AgenticSDR via Vision AI
                
                NOTAS: 
                - Qualificação: feita diretamente pelo AgenticSDR
                - Knowledge Base: acessada via KnowledgeService pelo AgenticSDR""",
                
                "instructions": """
                INSTRUÇÕES SIMPLIFICADAS:
                1. Agenda/reunião → CalendarAgent (direto)
                2. CRM/Kommo → CRMAgent (direto)
                3. Follow-up → FollowUpAgent (direto)
                4. Análise conta → AgenticSDR direto (Vision AI)
                
                SEM ANÁLISE COMPLEXA - DELEGAÇÃO DIRETA E RÁPIDA!
                """,
                
                # Configurações SIMPLIFICADAS
                "model": self.model,
                "show_tool_calls": False,  # Menos verboso
                "markdown": False,         # Mais direto
                "show_members_responses": False,  # Menos detalhes
                "debug_mode": False       # Sempre simplificado
            }
            
            # NÃO adicionar memory - causando erros no framework AGNO
            # team_config["memory"] = self.memory  # DESABILITADO
            logger.info("Team configurado sem memória (melhor estabilidade)")
            
            # Criar o Team com configurações
            self.team = Team(**team_config)
            
            # KnowledgeAgent removido - KnowledgeService não precisa de inicialização especial
            # A knowledge base é acessada diretamente pelo AgenticSDR via KnowledgeService
            emoji_logger.team_coordinate("KnowledgeService pronto para uso")
            
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
            # Verificar se há transcrição de áudio
            audio_transcription = None
            if media and media.get("type") == "audio":
                # Acessar diretamente o 'transcription' do dicionário 'media'
                audio_transcription = media.get('transcription')
            
            team_prompt = f"""
            Mensagem do lead: {message}
            
            {f'''
            TRANSCRIÇÃO DE ÁUDIO (CONTEÚDO REAL DA MENSAGEM):
            "{audio_transcription}"
            
            IMPORTANTE: Use a transcrição acima como o conteúdo principal da mensagem, não a mensagem genérica.
            ''' if audio_transcription else ''}
            
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
                    if hasattr(chunk, 'content') and chunk.content is not None:
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
            
            # Preparar updates compatíveis com o schema atual
            updates = {
                "last_interaction": datetime.now().isoformat(),
                "current_stage": team_state.get("current_stage", "INITIAL_CONTACT"),
                "qualification_score": team_state.get("qualification_score", 0)
            }
            
            # Atualizar qualification_status baseado em is_qualified
            # (usar qualification_status ao invés de is_qualified diretamente)
            if team_state.get("is_qualified", False):
                updates["qualification_status"] = "QUALIFIED"
            elif team_state.get("qualification_score", 0) == 0:
                updates["qualification_status"] = "PENDING"
            else:
                updates["qualification_status"] = "NOT_QUALIFIED"
            
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
    
    def extract_meeting_info(self, text: str) -> Dict[str, Any]:
        """
        Extrai informações de agendamento do texto
        Retorna dados estruturados para agendamento real
        """
        info = {
            "date": None,
            "time": None,
            "email": None,
            "phone": None,
            "name": None,
            "duration": 30  # Padrão 30 minutos
        }
        
        # Extrair data (hoje, amanhã, ou data específica)
        text_lower = text.lower()
        if "hoje" in text_lower:
            info["date"] = datetime.now().strftime("%d/%m/%Y")
        elif "amanhã" in text_lower:
            info["date"] = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        else:
            # Procurar por datas no formato DD/MM ou DD/MM/YYYY
            date_pattern = r'(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?'
            date_match = re.search(date_pattern, text)
            if date_match:
                day, month, year = date_match.groups()
                if year:
                    year = year if len(year) == 4 else f"20{year}"
                else:
                    year = str(datetime.now().year)
                info["date"] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        # Extrair horário
        time_patterns = [
            r'(\d{1,2})[h:]\s*(\d{0,2})',  # 14h, 14:30, 14h30
            r'às\s*(\d{1,2})[h:]\s*(\d{0,2})',  # às 14h
            r'(\d{1,2})\s*(?:horas?)',  # 14 horas
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, text, re.IGNORECASE)
            if time_match:
                groups = time_match.groups()
                hour = groups[0]
                minute = groups[1] if len(groups) > 1 and groups[1] else "00"
                info["time"] = f"{hour.zfill(2)}:{minute.zfill(2)}"
                break
        
        # Extrair email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        if email_match:
            info["email"] = email_match.group(0).lower()
        
        # Extrair telefone
        phone_pattern = r'(?:55)?(\d{2})[\s\-]?(\d{4,5})[\s\-]?(\d{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            info["phone"] = ''.join(phone_match.groups())
        
        # Extrair duração se mencionada
        if "1 hora" in text_lower or "uma hora" in text_lower:
            info["duration"] = 60
        elif "45 min" in text_lower:
            info["duration"] = 45
        elif "15 min" in text_lower:
            info["duration"] = 15
        elif "2 hora" in text_lower or "duas hora" in text_lower:
            info["duration"] = 120
        
        return info
    
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
            """
            
            # Adicionar informação de mídia se houver
            if multimodal_result and multimodal_result.get('type') == 'audio' and multimodal_result.get('transcription'):
                specialized_prompt += f"""
            TRANSCRIÇÃO DE ÁUDIO:
            "{multimodal_result.get('transcription', 'Não disponível')}"
            (Duração: {multimodal_result.get('duration', 0)}s, Engine: {multimodal_result.get('engine', 'N/A')})
            
            IMPORTANTE: Use ESTA TRANSCRIÇÃO como o conteúdo real da mensagem do usuário.
            """
            elif multimodal_result:
                specialized_prompt += f"\n            Análise de Mídia: {multimodal_result}"
            
            specialized_prompt += f"""
            
            AGENTE RECOMENDADO: {recommended_agent}
            RAZÃO: {reasoning}
            
            Por favor, processe esta solicitação com expertise especializada.
            Foque em: {context_analysis.get('recommended_action')}
            """
            
            # Executar com o agente específico se recomendado
            if recommended_agent:
                logger.info(f"📅 AGENT RECOMENDADO: {recommended_agent}")
                logger.info(f"📅 Razão: {reasoning}")
                
                # Verificar se é CalendarAgent - EXECUTAR DIRETAMENTE, NÃO SIMULAR!
                if recommended_agent == "CalendarAgent":
                    logger.info("🗓️ ATIVANDO CalendarAgent para EXECUÇÃO REAL de agendamento!")
                    
                    if self.calendar_agent:
                        logger.info("✅ CalendarAgent disponível - EXECUTANDO AGENDAMENTO REAL...")
                        
                        # Extrair informações da reunião
                        meeting_info = self.extract_meeting_info(message)
                        
                        # Se não tiver data/hora, usar padrões inteligentes
                        if not meeting_info['date']:
                            meeting_info['date'] = datetime.now().strftime("%d/%m/%Y")
                        if not meeting_info['time']:
                            meeting_info['time'] = "14:00"  # Horário padrão
                        if not meeting_info['email'] and lead_data:
                            meeting_info['email'] = lead_data.get('email', '')
                        
                        # EXECUTAR AGENDAMENTO REAL VIA CALENDAR AGENT
                        logger.info(f"🚀 CRIANDO EVENTO REAL: {meeting_info['date']} às {meeting_info['time']}")
                        
                        try:
                            # Chamar o método schedule_meeting do CalendarAgent com assinatura correta
                            nome_lead = lead_data.get('name', 'Cliente')
                            result = await self.calendar_agent.schedule_meeting(
                                lead_id=lead_data.get('id', phone),
                                title=f"☀️ Solar Prime - Reunião com {nome_lead}",
                                date=meeting_info['date'],  # formato DD/MM/YYYY
                                time=meeting_info['time'],  # formato HH:MM
                                duration_minutes=60,  # Sempre 1 hora
                                meeting_type="presentation",
                                attendee_emails=[meeting_info['email']] if meeting_info['email'] else [],
                                description=f"Olá {nome_lead}! 😊\n\nSeja muito bem-vindo(a) à Solar Prime! ☀️\n\nEstamos muito felizes em ter você conosco nesta reunião que será super proveitosa!\n\nVamos apresentar como você pode economizar até 95% na sua conta de energia com nossa solução de energia solar.\n\nTenha em mãos sua última conta de energia para conversarmos sobre os valores e economia.\n\nAté breve!\nEquipe Solar Prime",
                                location="Online"
                            )
                            
                            if result:
                                event_id = result.get('google_event_id', 'Aguardando confirmação')
                                logger.info(f"✅ REUNIÃO AGENDADA COM SUCESSO! Event ID: {event_id}")
                                
                                # Retornar mensagem de confirmação REAL com tags RESPOSTA_FINAL
                                return f"""<RACIOCINIO>
CalendarAgent executou agendamento real no Google Calendar
Event ID: {result.get('google_event_id')}
Meet Link: {result.get('meet_link', 'Será gerado')}
</RACIOCINIO>

<RESPOSTA_FINAL>
✅ Perfeito! Sua reunião está confirmada!

📅 Data: {meeting_info['date']} às {meeting_info['time']}
⏱️ Duração: 1 hora
📧 Convite: {meeting_info['email'] if meeting_info['email'] else 'Será enviado em breve'}
🎥 Google Meet: {result.get('meet_link', 'Link será gerado')}

Você receberá lembretes:
• 24 horas antes
• 2 horas antes

Até lá! 😊
</RESPOSTA_FINAL>"""
                            else:
                                error_msg = result.get('error', 'Erro ao criar evento') if result else 'Sem resposta'
                                logger.error(f"❌ Falha ao agendar: {error_msg}")
                                return f"""<RACIOCINIO>
CalendarAgent tentou agendar mas falhou
Erro: {error_msg}
</RACIOCINIO>

<RESPOSTA_FINAL>
Ops! Tive um pequeno problema técnico ao criar seu agendamento. 

Mas não se preocupe! Posso tentar novamente. Me confirma:
- Qual dia você prefere?
- Qual horário seria melhor para você?

Vou garantir que tudo funcione perfeitamente! 😊
</RESPOSTA_FINAL>"""
                                
                        except Exception as e:
                            logger.error(f"❌ Erro ao executar agendamento: {e}")
                            return f"""<RACIOCINIO>
CalendarAgent encontrou exceção durante agendamento
Exceção: {e}
</RACIOCINIO>

<RESPOSTA_FINAL>
Desculpe, tive um probleminha técnico ao processar seu agendamento.

Vamos fazer assim: me passa o melhor dia e horário para você que eu anoto aqui e nossa equipe confirma o agendamento, pode ser?

Qual seria o melhor momento para conversarmos sobre sua economia na conta de luz? 😊
</RESPOSTA_FINAL>"""
                    
                    else:
                        logger.error("❌ CalendarAgent NÃO está disponível! Verifique as configurações")
                        return """<RACIOCINIO>
CalendarAgent não está disponível no sistema
Configuração pode estar desabilitada
</RACIOCINIO>

<RESPOSTA_FINAL>
Opa! Percebi que nosso sistema de agendamento está passando por uma manutenção rápida.

Mas não se preocupe! Tenho uma solução: 
- Me passa seu melhor dia e horário
- Anoto aqui e nossa equipe confirma em seguida

Qual seria o melhor momento para você? Manhã, tarde ou noite? 😊
</RESPOSTA_FINAL>"""
                
                # Para outros agentes, manter comportamento original
                else:
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
    
    @async_retry(GEMINI_RETRY_CONFIG)
    async def _model_run_with_retry(self, *args, **kwargs):
        """Wrapper para adicionar retry automático às chamadas do modelo"""
        return self._original_run(*args, **kwargs)


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