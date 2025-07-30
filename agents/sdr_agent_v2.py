"""
SDR Agent V2 - 100% AGnO Framework
===================================
Agente de vendas otimizado com AGnO Framework puro
Performance target: <30s response time
"""

from typing import Dict, Any, Optional, Tuple, List
import asyncio
from datetime import datetime
from loguru import logger
from agno.agent import Agent, AgentMemory
from agno.models.google import Gemini
from agno.tools import tool
from agno.media import Image, Audio

from config.config import Config
from config.prompts import PromptTemplates, get_example_response, get_objection_handler
from agents.storage.supabase_storage import SupabaseAgentStorage
from agents.knowledge.solarprime_knowledge_simple import SolarPrimeKnowledgeSimple as SolarPrimeKnowledge
from agents.tools.message_buffer_tool import process_buffered_messages, analyze_message_pattern
from agents.tools.google_calendar_tools import calendar_tools
from services.database import supabase_client
from services.kommo_service import kommo_service
from services.qualification_kommo_integration import qualification_kommo_integration
from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from utils.helpers import format_phone_number
from services.analytics_service import analytics_service


class SDRAgentV2:
    """Agente de vendas v2 com AGnO Framework"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Modelo otimizado para velocidade
        self.model = Gemini(
            id=config.gemini.model,  # gemini-2.5-pro
            api_key=config.gemini.api_key,
            temperature=0.7
        )
        
        # Storage no Supabase
        self.storage = SupabaseAgentStorage()
        
        # Knowledge Base
        self.knowledge = SolarPrimeKnowledge()
        
        # Cache de agentes por telefone
        self.agents: Dict[str, Agent] = {}
        
        # Memory configuration usando prompts centralizados
        self.memory_config = AgentMemory(
            role=PromptTemplates.SYSTEM_PROMPT,
            instructions=""  # As instruções agora vêm do SYSTEM_PROMPT e dos stage prompts
        )
        
        logger.info("SDR Agent V2 inicializado com AGnO Framework")
        
    async def initialize(self):
        """Inicializa knowledge base e outros recursos async"""
        await self.knowledge.load_from_supabase()
        logger.info("Knowledge base carregada")
        
    def _get_or_create_agent(self, phone_number: str) -> Agent:
        """Obtém ou cria um agente para o número"""
        if phone_number not in self.agents:
            self.agents[phone_number] = self._create_agent(phone_number)
        return self.agents[phone_number]
        
    def _create_agent(self, phone_number: str) -> Agent:
        """Cria agente otimizado com AGnO"""
        # Determinar estágio inicial
        initial_stage = "INITIAL_CONTACT"
        
        return Agent(
            name="Leonardo",  # Padronizando com o nome do prompts.py
            model=self.model,
            # Reasoning otimizado
            reasoning=True,
            reasoning_min_steps=1,  # Mínimo para velocidade
            reasoning_max_steps=3,  # Máximo 3 para garantir <30s
            # Memory e Storage
            memory=self.memory_config,
            storage=self.storage,
            session_id=f"whatsapp_{phone_number}",
            # Knowledge
            knowledge=self.knowledge,
            search_knowledge=True,
            add_references=False,  # Desabilitar referências para velocidade
            # Tools customizados
            tools=[
                self.analyze_bill_tool,
                self.calculate_savings_tool,
                process_buffered_messages,  # Tool para processar mensagens bufferizadas
                analyze_message_pattern,    # Tool para analisar padrões
                *calendar_tools            # Tools do Google Calendar
            ],
            # Instructions dinâmicas baseadas no estágio
            instructions=self._get_stage_instructions(initial_stage),
            # Performance
            markdown=False,
            debug_mode=self.config.debug
        )
        
    def _get_stage_instructions(self, stage: str = "INITIAL_CONTACT") -> str:
        """Retorna instruções dinâmicas baseadas no estágio atual"""
        return PromptTemplates.get_stage_prompt(stage)
        
    @tool
    async def analyze_bill_tool(self, image_data: bytes) -> Dict[str, Any]:
        """Analisa conta de luz e extrai informações"""
        return {
            "instruction": "Analise esta conta de energia e extraia: valor total, consumo kWh, nome do titular",
            "format": "json"
        }
        
    @tool
    async def calculate_savings_tool(self, bill_value: float) -> Dict[str, Any]:
        """Calcula economia com energia solar"""
        monthly_savings = bill_value * 0.95
        annual_savings = monthly_savings * 12
        payback_months = 12000 / monthly_savings if monthly_savings > 0 else 0
        
        return {
            "economia_mensal": f"R$ {monthly_savings:.2f}",
            "economia_anual": f"R$ {annual_savings:.2f}",
            "retorno_investimento": f"{int(payback_months)} meses",
            "percentual_economia": "95%"
        }
        
        
    async def process_message(
        self,
        message: str,
        phone_number: str,
        media_type: Optional[str] = None,
        media_data: Optional[Any] = None,
        message_id: Optional[str] = None,
        media_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Processa mensagem com AGnO Framework
        
        Returns:
            Tuple[response_text, metadata]
        """
        start_time = datetime.now()
        phone = format_phone_number(phone_number)
        
        # Log detalhado de entrada
        logger.info(f"📥 V2 - Processando mensagem: phone={phone}, media_type={media_type}")
        if media_data:
            logger.debug(f"📦 V2 - Media data keys: {media_data.keys() if isinstance(media_data, dict) else type(media_data)}")
        
        try:
            # Obter agente
            agent = self._get_or_create_agent(phone)
            
            # Preparar contexto em paralelo para performance
            context_tasks = [
                self._load_lead_context(phone),
                self._load_conversation_context(phone),
                self._prepare_knowledge_context(message)
            ]
            
            lead_context, conv_context, knowledge_context = await asyncio.gather(*context_tasks)
            
            # Atualizar estado do agente
            current_state = agent.session_state or {}
            
            # Determinar estágio com consideração especial para análise de conta
            if media_type == 'image' and media_info and media_info.get('bill_value'):
                stage = 'ENERGY_BILL_ANALYSIS'
            else:
                stage = self._determine_stage(lead_context)
            
            current_state.update({
                'lead_info': lead_context,
                'current_stage': stage,
                'last_messages': conv_context,
                'relevant_knowledge': knowledge_context,
                'media_info': media_info if media_info else {}
            })
            agent.session_state = current_state
            
            # Atualizar instruções do agente baseado no estágio
            agent.instructions = self._get_stage_instructions(stage)
            
            # Preparar inputs multimodais
            context_parts = [
                f"Cliente: {lead_context.get('name', 'Ainda não identificado')}",
                f"Estágio: {current_state['current_stage']}"
            ]
            
            # Adicionar dados da conta se disponível
            if media_info and media_info.get('bill_value'):
                context_parts.append("\n📊 DADOS DA CONTA JÁ EXTRAÍDOS:")
                context_parts.append(f"- Valor: {media_info['bill_value']}")
                if media_info.get('consumption'):
                    context_parts.append(f"- Consumo: {media_info['consumption']}")
                if media_info.get('customer_name'):
                    context_parts.append(f"- Titular: {media_info['customer_name']}")
                context_parts.append("\n⚡ RESPONDA IMEDIATAMENTE com estes dados!")
            
            inputs = {
                'message': message,
                'context': "\n".join(context_parts)
            }
            
            # Adicionar mídia se houver
            if media_type == 'image' and media_data:
                logger.info("🖼️ Processando imagem no V2...")
                # Criar objeto Image corretamente
                image_obj = self._create_image_object(media_data)
                if image_obj:
                    inputs['images'] = [image_obj]
                    logger.info("✅ V2 - Imagem adicionada ao input")
            elif media_type == 'audio' and media_data:
                logger.info("🎤 Processando áudio no V2...")
                inputs['audio'] = [Audio(data=media_data)]
            elif media_type == 'buffered' and media_data:
                # Extrair tipo real de buffered
                logger.info("📦 Processando mídia buffered no V2...")
                if isinstance(media_data, dict):
                    actual_type = media_data.get('type', 'unknown')
                    logger.info(f"Tipo real da mídia: {actual_type}")
                    
                    # Reprocessar com tipo correto
                    if actual_type == 'image':
                        image_obj = self._create_image_object(media_data.get('media_data', media_data))
                        if image_obj:
                            inputs['images'] = [image_obj]
                    elif actual_type == 'audio':
                        inputs['audio'] = [Audio(data=media_data)]
                    else:
                        logger.warning(f"Tipo de mídia buffered não suportado: {actual_type}")
                
            # Executar agente com timeout
            response = await asyncio.wait_for(
                agent.arun(**inputs),
                timeout=25.0  # 25s timeout, deixando margem para 30s total
            )
            
            # Extrair resposta
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Calcular tempo de resposta
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Salvar análise e estado
            await self._save_interaction(
                phone, message, response_text, current_state, response_time
            )
            
            # Preparar metadata
            metadata = {
                'stage': current_state['current_stage'],
                'response_time': response_time,
                'lead_score': self._calculate_lead_score(lead_context, current_state),
                'lead_id': lead_context.get('lead_id'),  # Adicionar lead_id para follow-up
                'should_react': media_type in ['image', 'document'],
                'reaction_emoji': '👍' if media_type in ['image', 'document'] else None,
                'reasoning_enabled': True
            }
            
            # Log performance
            if response_time > 30:
                logger.warning(f"Response time exceeded 30s: {response_time:.2f}s")
            else:
                logger.info(f"Response delivered in {response_time:.2f}s")
                
            return response_text, metadata
            
        except asyncio.TimeoutError:
            logger.error("Timeout ao processar mensagem (>25s)")
            import random
            timeout_responses = [
                "Opa, deu uma lentidão aqui! 🐌 Pode repetir? Prometo caprichar na resposta!",
                "Xi, travei um pouquinho! 😅 Me conta de novo?",
                "Eita, me perdi! Pode repetir pra mim? Agora vai! 💪"
            ]
            return random.choice(timeout_responses), {
                'error': 'timeout',
                'response_time': 30.0
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            import random
            error_responses = [
                "Ops, tive um probleminha técnico aqui! 🔧 Já já volto!",
                "Ih, deu uma travadinha no sistema! 😅 Me dá um segundinho?",
                "Eita, bugou aqui! 🐛 Mas relaxa que já vou resolver!"
            ]
            return random.choice(error_responses), {
                'error': str(e),
                'response_time': (datetime.now() - start_time).total_seconds()
            }
            
    async def _load_lead_context(self, phone: str) -> Dict[str, Any]:
        """Carrega contexto do lead com cache"""
        # TODO: Implementar cache Redis aqui
        # Por enquanto, vamos apenas buscar ou criar o lead diretamente
        lead = await lead_repository.get_by_phone(phone)
        
        if not lead:
            # Criar lead básico se não existir
            from models.lead import LeadCreate
            lead_data = LeadCreate(phone_number=phone)
            lead = await lead_repository.create_or_update(lead_data)
        
        context = {
            'phone': phone,
            'profile_id': str(lead.id),
            'created_at': lead.created_at.isoformat()
        }
        
        if lead:
            context.update({
                'lead_id': str(lead.id),
                'name': lead.name,
                'email': lead.email,
                'property_type': lead.property_type,
                'bill_value': lead.bill_value,
                'consumption_kwh': lead.consumption_kwh,
                'current_stage': lead.current_stage,
                'qualification_score': lead.qualification_score
            })
            
        return context
        
    async def _load_conversation_context(self, phone: str) -> List[Dict[str, Any]]:
        """Carrega últimas mensagens da conversa"""
        # Primeiro precisamos do lead
        lead = await lead_repository.get_by_phone(phone)
        if not lead:
            return []
            
        # Criar ou retomar conversa
        conversation = await conversation_repository.create_or_resume(
            lead_id=lead.id,
            session_id=f"whatsapp_{phone}"
        )
        
        # Carregar apenas últimas 10 mensagens para performance
        messages = await message_repository.get_conversation_messages(
            conversation_id=conversation.id,
            limit=10
        )
        
        return [
            {
                'role': msg.sender_type,
                'content': msg.content,
                'timestamp': msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
    async def _prepare_knowledge_context(self, message: str) -> str:
        """Prepara contexto relevante da base de conhecimento"""
        # Buscar conhecimento relevante de forma assíncrona
        relevant_knowledge = await self.knowledge.get_relevant_knowledge(message, max_results=2)
        return relevant_knowledge
        
    def _determine_stage(self, lead_context: Dict[str, Any]) -> str:
        """Determina estágio atual do lead"""
        if not lead_context.get('name'):
            return 'IDENTIFICATION'
        elif not lead_context.get('property_type'):
            return 'DISCOVERY'
        elif not lead_context.get('bill_value'):
            return 'QUALIFICATION'
        else:
            return 'SCHEDULING'
            
    def _create_image_object(self, image_data: Any) -> Optional[Image]:
        """Cria objeto Image do AGnO a partir de diferentes formatos"""
        try:
            import base64
            
            # Se já é um objeto Image, retornar
            if isinstance(image_data, Image):
                return image_data
            
            # Processar diferentes formatos
            if isinstance(image_data, dict):
                # Tentar diferentes campos
                if 'url' in image_data:
                    return Image(url=image_data['url'])
                elif 'base64' in image_data:
                    # Decodificar base64
                    img_bytes = base64.b64decode(image_data['base64'])
                    return Image(content=img_bytes)
                elif 'path' in image_data:
                    # Ler arquivo
                    with open(image_data['path'], 'rb') as f:
                        return Image(content=f.read())
                elif 'data' in image_data:
                    # Campo 'data' pode ser bytes ou base64
                    if isinstance(image_data['data'], str):
                        # Assumir base64
                        img_bytes = base64.b64decode(image_data['data'])
                        return Image(content=img_bytes)
                    else:
                        return Image(content=image_data['data'])
            elif isinstance(image_data, str):
                # String pode ser URL ou base64
                if image_data.startswith('http'):
                    return Image(url=image_data)
                else:
                    # Tentar decodificar como base64
                    img_bytes = base64.b64decode(image_data)
                    return Image(content=img_bytes)
            elif isinstance(image_data, bytes):
                # Bytes diretos
                return Image(content=image_data)
            
            logger.error(f"Formato de imagem não suportado no V2: {type(image_data)}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar objeto Image no V2: {e}")
            return None
    
    def _calculate_lead_score(self, lead_context: Dict[str, Any], session_state: Dict[str, Any]) -> int:
        """Calcula score de qualificação do lead"""
        score = 0
        
        # Informações básicas (30 pontos)
        if lead_context.get('name'):
            score += 10
        if lead_context.get('phone'):
            score += 10
        if lead_context.get('property_type'):
            score += 10
            
        # Informações de consumo (40 pontos)
        if lead_context.get('bill_value'):
            score += 20
            # Bonus por conta alta
            try:
                bill_value = float(lead_context['bill_value'])
                if bill_value > 500:
                    score += 15
                elif bill_value > 300:
                    score += 5
            except (ValueError, TypeError):
                pass
                
        if lead_context.get('consumption_kwh'):
            score += 10
            
        # Engajamento (30 pontos)
        stage = session_state.get('current_stage', '')
        if stage == 'QUALIFICATION':
            score += 10
        elif stage == 'SCHEDULING':
            score += 30
            
        return min(score, 100)
        
    async def _save_interaction(
        self,
        phone: str,
        message: str,
        response: str,
        session_state: Dict[str, Any],
        response_time: float
    ):
        """Salva interação e atualiza estado"""
        try:
            # Salvar mensagens
            lead = await lead_repository.get_by_phone(phone)
            if not lead:
                return
                
            conversation = await conversation_repository.create_or_resume(
                lead_id=lead.id,
                session_id=f"whatsapp_{phone}"
            )
            
            # Mensagem do usuário
            await message_repository.create_message(
                conversation_id=conversation.id,
                sender_type='user',
                content=message
            )
            
            # Resposta do agente
            await message_repository.create_message(
                conversation_id=conversation.id,
                sender_type='assistant',
                content=response,
                metadata={
                    'response_time': response_time,
                    'stage': session_state.get('current_stage'),
                    'reasoning_enabled': True
                }
            )
            
            # Atualizar lead se houver novas informações
            lead_info = session_state.get('lead_info', {})
            if lead_info.get('lead_id'):
                await lead_repository.update_lead(
                    lead_id=lead_info['lead_id'],
                    current_stage=session_state.get('current_stage'),
                    qualification_score=self._calculate_lead_score(lead_info, session_state)
                )
                
                # Sincronizar com Kommo CRM
                if kommo_service and qualification_kommo_integration:
                    try:
                        # Criar/atualizar lead no Kommo
                        ai_notes = f"Estágio: {session_state.get('current_stage')}\n"
                        ai_notes += f"Score: {self._calculate_lead_score(lead_info, session_state)}\n"
                        ai_notes += f"Última mensagem: {message[:100]}..."
                        
                        kommo_lead_id = await qualification_kommo_integration.sync_lead_to_kommo(
                            lead,
                            ai_notes=ai_notes,
                            current_stage=session_state.get('current_stage')
                        )
                        
                        # Se moveu para agendamento, notificar Kommo
                        if session_state.get('current_stage') == 'SCHEDULING':
                            await qualification_kommo_integration.update_lead_stage(
                                lead,
                                'SCHEDULING',
                                notes="Cliente iniciou processo de agendamento via WhatsApp"
                            )
                        
                        # Adicionar interação como nota no Kommo
                        await qualification_kommo_integration.add_whatsapp_interaction(
                            lead,
                            message_type="text",
                            content=message,
                            response=response
                        )
                        
                        logger.info(f"Lead sincronizado com Kommo: {kommo_lead_id}")
                        
                    except Exception as e:
                        logger.error(f"Erro ao sincronizar com Kommo: {e}")
                        # Não falhar a operação principal se Kommo falhar
                
            # Analytics
            await analytics_service.track_event(
                event_type='message_processed',
                event_data={
                    'stage': session_state.get('current_stage'),
                    'response_time': response_time,
                    'lead_score': self._calculate_lead_score(lead_info, session_state)
                },
                session_id=phone
            )
            
        except Exception as e:
            logger.error(f"Erro ao salvar interação: {e}")
            
    async def handle_greeting(self, phone_number: str) -> Tuple[str, Dict[str, Any]]:
        """Mensagem de boas-vindas otimizada"""
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        greetings = []
        
        if hour < 12:
            greetings = [
                "Bom dia! ☀️ Eu sou a Luna da SolarPrime. Vim te ajudar a economizar até 95% na conta de luz! Como posso te chamar?",
                "Oi, bom dia! 😊 Sou a Luna, especialista em economia solar. Vamos reduzir essa conta de luz? Qual seu nome?"
            ]
        elif hour < 18:
            greetings = [
                "Boa tarde! 😊 Eu sou a Luna da SolarPrime. Que tal economizar até 95% na energia? Como posso te chamar?",
                "Oi, boa tarde! ☀️ Sou a Luna e vim te mostrar como economizar muito na conta de luz! Qual seu nome?"
            ]
        else:
            greetings = [
                "Boa noite! 🌙 Eu sou a Luna da SolarPrime. Ainda dá tempo de começar a economizar na energia! Como posso te chamar?",
                "Oi, boa noite! 😊 Sou a Luna e posso te ajudar a reduzir até 95% da conta de luz! Qual seu nome?"
            ]
        
        return random.choice(greetings), {
            'stage': 'IDENTIFICATION',
            'is_greeting': True,
            'typing_delay': 1.0  # Reduzido de calculate_typing_delay
        }
    
    async def process_buffered_messages(
        self,
        messages: List[Dict[str, Any]],
        phone_number: str,
        consolidated_content: str,
        media_items: List[Dict[str, Any]]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Processa múltiplas mensagens bufferizadas
        
        Args:
            messages: Lista de mensagens originais
            phone_number: Número do telefone
            consolidated_content: Conteúdo consolidado das mensagens
            media_items: Lista de itens de mídia
            
        Returns:
            Tuple[response_text, metadata]
        """
        start_time = datetime.now()
        phone = format_phone_number(phone_number)
        
        try:
            # Obter agente
            agent = self._get_or_create_agent(phone)
            
            # Usar a tool process_buffered_messages do agente
            buffer_analysis = await agent.arun(
                f"process_buffered_messages com estas mensagens: {messages}"
            )
            
            # Preparar contexto em paralelo
            context_tasks = [
                self._load_lead_context(phone),
                self._load_conversation_context(phone),
                self._prepare_knowledge_context(consolidated_content)
            ]
            
            lead_context, conv_context, knowledge_context = await asyncio.gather(*context_tasks)
            
            # Atualizar estado do agente com informações do buffer
            current_state = agent.session_state or {}
            current_state.update({
                'lead_info': lead_context,
                'current_stage': self._determine_stage(lead_context),
                'last_messages': conv_context,
                'relevant_knowledge': knowledge_context,
                'buffer_info': {
                    'message_count': len(messages),
                    'consolidated_content': consolidated_content,
                    'has_media': len(media_items) > 0,
                    'media_items': media_items
                }
            })
            agent.session_state = current_state
            
            # Preparar contexto especial para mensagens bufferizadas
            buffer_context = f"""
            O cliente enviou {len(messages)} mensagens rapidamente:
            
            Conteúdo consolidado: {consolidated_content}
            
            Cliente: {lead_context.get('name', 'Ainda não identificado')}
            Estágio: {current_state['current_stage']}
            """
            
            # Preparar inputs
            inputs = {
                'message': consolidated_content,
                'context': buffer_context
            }
            
            # Adicionar mídia se houver
            if media_items:
                # Processar apenas o primeiro item de mídia por enquanto
                first_media = media_items[0]
                if first_media['type'] == 'image':
                    # TODO: Baixar e processar imagem
                    inputs['images'] = [Image(data=None, description=f"Imagem enviada: {first_media.get('content', '')}")]
            
            # Executar agente com timeout
            response = await asyncio.wait_for(
                agent.arun(**inputs),
                timeout=25.0
            )
            
            # Extrair resposta
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Calcular tempo de resposta
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Salvar análise
            await self._save_interaction(
                phone, consolidated_content, response_text, current_state, response_time
            )
            
            # Preparar metadata
            metadata = {
                'stage': current_state['current_stage'],
                'response_time': response_time,
                'lead_score': self._calculate_lead_score(lead_context, current_state),
                'lead_id': lead_context.get('lead_id'),  # Adicionar lead_id para follow-up
                'buffered_messages': len(messages),
                'has_media': len(media_items) > 0,
                'media_count': len(media_items),
                'reasoning_enabled': True,
                'buffer_analysis': {
                    'fragmented': len(messages) > 3,
                    'urgent': any('urgente' in msg.get('content', '').lower() for msg in messages),
                    'has_questions': '?' in consolidated_content
                }
            }
            
            # Log performance
            logger.info(f"Buffered response ({len(messages)} msgs) delivered in {response_time:.2f}s")
            
            return response_text, metadata
            
        except asyncio.TimeoutError:
            logger.error("Timeout ao processar mensagens bufferizadas")
            import random
            timeout_msgs = [
                "Opa, recebi várias mensagens de uma vez! 😅 Me conta resumidinho: o que você precisa saber sobre energia solar?",
                "Eita, chegou tudo junto! 📱 Vamos com calma... Como posso te ajudar a economizar na conta de luz?",
                "Xi, recebi um montão de mensagens! 😄 Me diz: você quer saber sobre economia na energia?"
            ]
            return random.choice(timeout_msgs), {
                'error': 'timeout',
                'response_time': 30.0,
                'buffered_messages': len(messages)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagens bufferizadas: {e}", exc_info=True)
            import random
            error_msgs = [
                "Ops, me atrapalhei com tantas mensagens! 🤭 Pode me dizer o principal que você quer saber?",
                "Ih, bugou com várias mensagens! 😅 Vamos recomeçar: como posso ajudar com energia solar?",
                "Eita, me perdi nas mensagens! 🙈 Me conta de novo, mas resumidinho?"
            ]
            return random.choice(error_msgs), {
                'error': str(e),
                'response_time': (datetime.now() - start_time).total_seconds(),
                'buffered_messages': len(messages)
            }