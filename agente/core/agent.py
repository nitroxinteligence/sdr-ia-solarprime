"""
Agente SDR Principal - Helen Vieira (SolarPrime)
Implementação modular usando AGnO Framework
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import Toolkit
from loguru import logger

from agente.core.config import (
    GEMINI_API_KEY,
    AGENTE_DIR,
    DEBUG
)
from agente.core.types import (
    WhatsAppMessage,
    AgentResponse,
    Lead
)
from agente.core.monitoring import (
    capture_agent_error,
    capture_agent_event,
    monitor_qualification_stage,
    monitor_tool_usage,
    add_breadcrumb,
    SentryContextManager
)

# Import all core components
from agente.core.humanizer import HelenHumanizer
from agente.core.context_manager import ContextManager
from agente.core.qualification_flow import QualificationFlow
from agente.core.message_processor import MessageProcessor
from agente.core.session_manager import SessionManager

# Import all tools
from agente.tools.whatsapp import (
    send_text_message,
    send_audio_message,
    send_image_message,
    send_document_message,
    send_location_message,
    type_simulation,
    message_chunking,
    message_buffer
)
from agente.tools.kommo import (
    search_kommo_lead,
    create_kommo_lead,
    update_kommo_lead,
    update_kommo_stage,
    add_kommo_note,
    schedule_kommo_activity
)
from agente.tools.calendar import (
    check_availability,
    create_meeting,
    update_meeting,
    cancel_meeting,
    send_calendar_invite
)
from agente.tools.database import (
    create_lead,
    update_lead,
    get_lead,
    save_message,
    update_conversation,
    schedule_followup
)
from agente.tools.media import (
    process_image,
    process_audio,
    process_document
)
from agente.tools.utility import (
    validate_phone,
    format_currency
)


class SDRAgent:
    """
    Agente SDR inteligente para qualificação e agendamento de leads
    via WhatsApp usando AGnO Framework
    """
    
    def __init__(self):
        """Inicializa o agente SDR com todas as configurações"""
        self.name = "Helen Vieira - SDR SolarPrime"
        self.agent = None
        self.toolkit = None
        
        # Initialize core components
        self.humanizer = HelenHumanizer()
        self.context_manager = ContextManager()
        self.qualification_flow = QualificationFlow()
        self.message_processor = MessageProcessor(
            humanizer=self.humanizer,
            context_manager=self.context_manager,
            qualification_flow=self.qualification_flow
        )
        self.session_manager = SessionManager(
            context_manager=self.context_manager
        )
        
        self._initialize_agent()
        
    def _load_system_prompt(self) -> str:
        """Carrega o prompt do sistema do arquivo"""
        prompt_file = AGENTE_DIR / "prompts" / "system_prompt.md"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logger.warning("Arquivo de prompt não encontrado, usando prompt básico")
            return self._get_basic_prompt()
    
    def _get_basic_prompt(self) -> str:
        """Retorna um prompt básico caso o arquivo não seja encontrado"""
        return """
        Você é Helen Vieira, consultora de energia solar da SolarPrime Boa Viagem.
        
        Sua missão é qualificar leads e agendar reuniões para apresentação da solução
        de energia solar que pode gerar até 95% de economia na conta de luz.
        
        Seja sempre cordial, profissional e focada em entender as necessidades do cliente.
        """
    
    def _get_tool_instructions(self) -> str:
        """Retorna as instruções de uso das tools"""
        return """
        
        ## INSTRUÇÕES PARA USO DE TOOLS
        
        ### Início da Conversa:
        1. Quando receber uma nova mensagem, use 'get_lead' para verificar se já existe
        2. Se não existir, use 'create_lead' para criar o registro
        3. Use 'create_kommo_lead' no Kommo para inserir como "NOVO LEAD"
        4. Use o contexto fornecido para entender o histórico
        
        ### Durante a Qualificação:
        1. Use 'update_lead' sempre que obtiver novas informações
        2. Atualize o stage no Kommo com 'update_kommo_stage' conforme progressão:
           - Início: "novo lead"
           - Em atendimento: "em negociação"
           - Interesse demonstrado: "em qualificação"
           - Dados completos: "qualificado"
        
        ### Processamento de Mídia:
        1. Para imagens de conta de luz: use 'process_image'
        2. Para outros documentos: use 'process_document'
        3. Para áudios: use 'process_audio'
        4. Sempre salve dados extraídos com 'update_lead'
        
        ### Agendamento de Reuniões:
        1. Quando lead aceitar agendar, use 'check_availability'
        2. Apresente até 3 opções de horários disponíveis
        3. Após confirmação, use 'create_meeting'
        4. Atualize Kommo para "reunião agendada" com 'update_kommo_stage'
        5. Adicione nota no Kommo com detalhes usando 'add_kommo_note'
        
        ### Envio de Mensagens:
        1. Para mensagens normais, use 'send_text_message'
        2. Para mensagens longas, use 'message_chunking' primeiro
        3. Para simular digitação, use 'type_simulation'
        4. Para áudios, use 'send_audio_message'
        
        ### Follow-ups:
        1. Se lead não responder, agende follow-up com 'schedule_followup'
        2. Primeira tentativa: 30 minutos
        3. Segunda tentativa: 24 horas
        4. Após 2 falhas: marcar como "não interessado" no Kommo
        
        ### Importante:
        - Sempre mantenha o contexto usando o histórico fornecido
        - Atualize o Kommo em tempo real conforme progressão
        - Use reasoning=True apenas para situações complexas
        - Personalize follow-ups baseado no contexto da conversa
        - Siga SEMPRE a personalidade e estilo de Helen Vieira conforme o system prompt
        """
    
    def _initialize_agent(self):
        """Inicializa o agente AGnO com todas as configurações"""
        try:
            # Configurar modelo Gemini
            model = Gemini(
                id="gemini-2.0-flash-exp",
                api_key=GEMINI_API_KEY
            )
            
            # Criar toolkit com todas as tools
            self.toolkit = Toolkit(
                show_tool_results=True,
                tools_to_stop_on=["create_meeting", "create_lead"],
                tools=[
                    # WhatsApp Tools
                    send_text_message,
                    send_audio_message,
                    send_image_message,
                    send_document_message,
                    send_location_message,
                    type_simulation,
                    message_chunking,
                    message_buffer,
                    
                    # Kommo Tools
                    search_kommo_lead,
                    create_kommo_lead,
                    update_kommo_lead,
                    update_kommo_stage,
                    add_kommo_note,
                    schedule_kommo_activity,
                    
                    # Calendar Tools
                    check_availability,
                    create_meeting,
                    update_meeting,
                    cancel_meeting,
                    send_calendar_invite,
                    
                    # Database Tools
                    create_lead,
                    update_lead,
                    get_lead,
                    save_message,
                    update_conversation,
                    schedule_followup,
                    
                    # Media Tools
                    process_image,
                    process_audio,
                    process_document,
                    
                    # Utility Tools
                    validate_phone,
                    format_currency
                ]
            )
            
            # Carregar prompts
            system_prompt = self._load_system_prompt()
            tool_instructions = self._get_tool_instructions()
            
            # Criar agente
            self.agent = Agent(
                name=self.name,
                model=model,
                toolkit=self.toolkit,
                reasoning=False,  # Ativar apenas quando necessário
                storage=False,    # Não usar storage do AGnO
                memory=False,     # Não usar memory do AGnO
                instructions=system_prompt + tool_instructions,
                debug=DEBUG,
                log_level="INFO" if DEBUG else "WARNING"
            )
            
            logger.info(f"✅ Agente {self.name} inicializado com sucesso com {len(self.toolkit.tools)} tools")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar agente: {str(e)}")
            raise
    
    async def process_message(self, message: WhatsAppMessage) -> AgentResponse:
        """
        Processa uma mensagem recebida do WhatsApp
        
        Args:
            message: Mensagem do WhatsApp para processar
            
        Returns:
            AgentResponse com o resultado do processamento
        """
        # Use Sentry context manager for monitoring
        with SentryContextManager(
            "agent.process_message",
            f"Process message from {message.phone[:4]}****",
            phone=message.phone[:4] + "****",
            has_media=bool(message.media_url)
        ):
            try:
                logger.info(f"📱 Processando mensagem de {message.phone}: {message.message[:50]}...")
                
                # Add breadcrumb for message processing
                add_breadcrumb(
                    message="Starting message processing",
                    category="agent",
                    level="info",
                    data={
                        "phone": message.phone[:4] + "****",
                        "message_length": len(message.message),
                        "has_media": bool(message.media_url)
                    }
                )
                
                # Get or create session
                session = await self.session_manager.get_or_create_session(message.phone)
                
                # Build conversation context
                context = await self.context_manager.build_conversation_context(message.phone)
                
                # Add current message to context
                context["current_message"] = message.model_dump()
                context["session"] = session
                
                # Monitor qualification stage if available
                if "qualification_stage" in context.get("lead", {}):
                    current_stage = context["lead"]["qualification_stage"]
                    add_breadcrumb(
                        message=f"Lead in qualification stage: {current_stage}",
                        category="qualification",
                        level="info"
                    )
                
                # Determine if should use reasoning
                use_reasoning = self.should_use_reasoning(context)
                
                # Update agent reasoning mode if needed
                if use_reasoning != self.agent.reasoning:
                    self.agent.reasoning = use_reasoning
                    logger.info(f"Reasoning mode {'ativado' if use_reasoning else 'desativado'} para {message.phone}")
                
                # Process with agent
                agent_input = {
                    "phone": message.phone,
                    "message": message.message,
                    "media_url": message.media_url,
                    "media_type": message.media_type,
                    "context": context,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Run agent with full context
                import time
                start_time = time.time()
                response = await self.agent.run(agent_input)
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Add breadcrumb for agent execution
                add_breadcrumb(
                    message="Agent execution completed",
                    category="agent",
                    level="info",
                    data={
                        "execution_time_ms": execution_time,
                        "reasoning_enabled": use_reasoning
                    }
                )
                
                # Update session
                await self.session_manager.update_session(message.phone, {
                    "message_added": True,
                    "last_response": response
                })
                
                # Extract response text from agent response
                response_text = self._extract_response_text(response)
                
                # Monitor qualification stage transition if changed
                if "qualification_stage" in context.get("lead", {}):
                    new_context = await self.context_manager.build_conversation_context(message.phone)
                    if new_context.get("lead", {}).get("qualification_stage") != current_stage:
                        new_stage = new_context["lead"]["qualification_stage"]
                        monitor_qualification_stage(
                            phone=message.phone,
                            stage=new_stage,
                            success=True,
                            duration_ms=int(execution_time)
                        )
                
                # Capture successful processing event
                capture_agent_event(
                    "Message processed successfully",
                    "agent.process",
                    {
                        "phone": message.phone[:4] + "****",
                        "execution_time_ms": execution_time,
                        "response_length": len(response_text),
                        "reasoning_enabled": use_reasoning
                    }
                )
                
                return AgentResponse(
                    success=True,
                    message=response_text,
                    data={
                        "phone": message.phone,
                        "session_id": session.get("conversation_id"),
                        "context": context
                    }
                )
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar mensagem: {str(e)}")
                
                # Capture error with context
                capture_agent_error(
                    e,
                    context={
                        "phone": message.phone[:4] + "****",
                        "message_id": message.message_id,
                        "message_preview": message.message[:50],
                        "has_media": bool(message.media_url),
                        "media_type": message.media_type
                    }
                )
                
                return AgentResponse(
                    success=False,
                    error=str(e)
                )
    
    async def process_with_context(
        self, 
        message: WhatsAppMessage,
        lead: Optional[Lead] = None,  # Kept for backward compatibility
        history: Optional[List[Dict]] = None  # Kept for backward compatibility
    ) -> AgentResponse:
        """
        Processa mensagem com contexto completo
        
        Args:
            message: Mensagem para processar
            lead: Dados do lead (se existir)
            history: Histórico de conversas
            
        Returns:
            AgentResponse com o resultado
        """
        try:
            # This method is now redundant as process_message handles context
            # But keeping it for backward compatibility
            return await self.process_message(message)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar com contexto: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e)
            )
    
    def should_use_reasoning(self, context: Dict[str, Any]) -> bool:
        """
        Determina se deve ativar reasoning para o contexto atual
        
        Args:
            context: Contexto da conversa
            
        Returns:
            True se deve usar reasoning
        """
        # Check if context manager already determined reasoning should be used
        if context.get("should_use_reasoning", False):
            return True
        
        # Additional complex indicators
        complex_indicators = [
            "análise de proposta",
            "comparação com concorrentes", 
            "cálculo de economia",
            "objeções técnicas",
            "múltiplas perguntas",
            "solicitação de garantias",
            "dúvidas complexas",
            "questionamento técnico"
        ]
        
        message_text = context.get("current_message", {}).get("message", "").lower()
        
        # Check for complex indicators in message
        if any(indicator in message_text for indicator in complex_indicators):
            return True
        
        # Check qualification progress
        qual_progress = context.get("qualification_progress", {})
        if qual_progress.get("completed", 0) > 70 and not qual_progress.get("is_qualified"):
            return True  # Complex qualification scenario
        
        # Check emotional state
        emotional_state = context.get("emotional_state", {})
        if emotional_state.get("interesse_level", 5) <= 3:
            return True  # Low interest requires careful handling
        
        return False
    
    def _extract_response_text(self, agent_response: Any) -> str:
        """
        Extrai o texto de resposta do resultado do agente
        
        Args:
            agent_response: Resposta do agente AGnO
            
        Returns:
            Texto da resposta
        """
        try:
            # AGnO agent response structure may vary
            # This is a generic extraction method
            
            if isinstance(agent_response, str):
                return agent_response
            
            if isinstance(agent_response, dict):
                # Try common response fields
                for field in ["response", "message", "text", "content"]:
                    if field in agent_response:
                        return str(agent_response[field])
            
            # Fallback to string representation
            return str(agent_response)
            
        except Exception as e:
            logger.error(f"Erro ao extrair resposta: {e}")
            return "Desculpe, tive um problema ao processar sua mensagem. Pode repetir?"
    
    async def start(self):
        """Inicia o agente e componentes necessários"""
        logger.info(f"🚀 Iniciando agente {self.name}")
        await self.session_manager.start()
    
    async def shutdown(self):
        """Desliga o agente de forma segura"""
        logger.info(f"🔌 Desligando agente {self.name}")
        await self.session_manager.stop()
        # Cleanup adicional se necessário