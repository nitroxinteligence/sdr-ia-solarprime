"""
Agente SDR Principal - SolarPrime
================================
Implementação do agente de vendas usando AGnO Framework
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger
import base64
from uuid import UUID

# AGnO Framework - API Correta
from agno.agent import Agent, AgentMemory
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage

# Importar módulos multimodais do AGnO - Documentação oficial
from agno.media import Image, Audio, Video
AGNO_MEDIA_AVAILABLE = True

# Tentar importar módulos de leitura de documentos do AGnO
try:
    from agno.document_reader import PDFReader, PDFImageReader
    AGNO_READERS_AVAILABLE = True
    logger.info("Módulos PDFReader e PDFImageReader do AGnO disponíveis")
except ImportError:
    logger.warning("Módulos PDFReader/PDFImageReader não disponíveis - PDFs serão tratados como imagens")
    AGNO_READERS_AVAILABLE = False
    PDFReader = None
    PDFImageReader = None

# Imports para retry e fallback
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

# Configurações locais
from config.agent_config import config, get_config
from config.prompts import PromptTemplates, get_example_response
from utils.helpers import calculate_typing_delay, format_phone_number
from utils.currency_parser import parse_brazilian_currency

# Importar repositórios Supabase
from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from models.lead import LeadCreate, LeadUpdate
from models.conversation import ConversationCreate


class SDRAgent:
    """Agente SDR principal para vendas de energia solar usando AGnO Framework"""
    
    def __init__(self):
        """Inicializa o agente SDR com AGnO"""
        self.config = get_config()
        self.agents: Dict[str, Agent] = {}  # Um agente por telefone
        
        # Configuração do modelo Gemini (principal)
        self.model = Gemini(
            id=self.config.gemini.model,
            api_key=self.config.gemini.api_key
        )
        
        # Configuração do modelo OpenAI (fallback)
        self.fallback_model = None
        if self.config.enable_fallback and self.config.openai.api_key:
            try:
                self.fallback_model = OpenAIChat(
                    id=self.config.openai.model,
                    api_key=self.config.openai.api_key
                )
                logger.info(f"Modelo de fallback OpenAI configurado: {self.config.openai.model}")
            except Exception as e:
                logger.warning(f"Erro ao configurar modelo de fallback OpenAI: {e}")
        
        # Configuração do storage para persistência
        self.storage = SqliteAgentStorage(
            table_name="sdr_sessions",
            db_file="data/agent_storage.db"
        )
        
        # Configuração de memória
        self.memory_config = AgentMemory(
            role="Você é Luna, uma consultora especializada em energia solar.",
            instructions="Mantenha o contexto das conversas e lembre-se de informações importantes dos leads."
        )
        
        # Cache de respostas (simples em memória por enquanto)
        self._response_cache: Dict[str, Tuple[str, datetime]] = {}
        
        logger.info(f"SDR Agent '{self.config.personality.name}' inicializado com AGnO Framework")
    
    def _get_or_create_agent(self, phone_number: str) -> Agent:
        """Obtém ou cria um agente para o número de telefone"""
        if phone_number not in self.agents:
            # Cria um agente único para este telefone com session_id próprio
            self.agents[phone_number] = Agent(
                name=self.config.personality.name,
                description=f"Consultora de energia solar da {self.config.personality.company}",
                instructions=PromptTemplates.format_system_prompt(),
                model=self.model,
                reasoning=True,  # Habilita chain of thought
                reasoning_min_steps=2,  # Mínimo 2 passos de raciocínio para vendas
                reasoning_max_steps=5,  # Máximo 5 passos para não demorar
                reasoning_model=None,  # Usa o mesmo modelo (Gemini 2.5 Pro)
                memory=self.memory_config,
                session_id=f"sdr_{phone_number}",  # ID único por lead
                storage=self.storage,
                session_state={
                    "lead_info": {"phone": format_phone_number(phone_number)},
                    "current_stage": "INITIAL_CONTACT",
                    "conversation_history": []
                },
                # Configurações adicionais para vendas
                debug_mode=config.debug  # Ativa debug do reasoning se configurado
            )
            logger.info(f"Novo agente criado para telefone: {phone_number}")
        return self.agents[phone_number]
    
    def _get_session_state(self, agent: Agent) -> Dict[str, Any]:
        """Obtém o estado da sessão do agente"""
        if agent.session_state is None:
            agent.session_state = {
                "lead_info": {},
                "current_stage": "INITIAL_CONTACT",
                "conversation_history": []
            }
        return agent.session_state
    
    def _update_session_state(self, agent: Agent, updates: Dict[str, Any]):
        """Atualiza o estado da sessão do agente"""
        state = self._get_session_state(agent)
        state.update(updates)
        agent.session_state = state
    
    async def process_message(
        self, 
        message: str,
        phone_number: str,
        media_type: Optional[str] = None,
        media_data: Optional[Any] = None,
        message_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Processa mensagem recebida e gera resposta usando AGnO
        
        Args:
            message: Mensagem de texto do usuário
            phone_number: Número de telefone do lead
            media_type: Tipo de mídia (image, document, audio)
            media_data: Dados da mídia se houver
            
        Returns:
            Tuple com (resposta, metadados)
        """
        try:
            # Log para debug
            logger.info(f"Processando mensagem para telefone: '{phone_number}' (tamanho: {len(phone_number)})")
            
            # Criar ou atualizar lead no Supabase
            lead = await lead_repository.create_or_update(
                LeadCreate(phone_number=phone_number)
            )
            
            # Criar ou retomar conversa
            # Usar hash do phone_number + data para manter o session_id único mas menor
            import hashlib
            date_str = datetime.now().strftime('%Y%m%d')
            session_hash = hashlib.md5(f"{phone_number}_{date_str}".encode()).hexdigest()[:16]
            session_id = f"s_{session_hash}"
            
            conversation = await conversation_repository.create_or_resume(
                lead_id=lead.id,
                session_id=session_id
            )
            
            # Buscar histórico completo de mensagens do Supabase
            messages_history = await message_repository.get_conversation_messages(
                conversation_id=conversation.id,
                limit=50  # Últimas 50 mensagens para contexto completo
            )
            
            # Obter contexto formatado da conversa
            conversation_context = await message_repository.get_conversation_context(
                conversation_id=conversation.id,
                max_messages=20  # Últimas 20 mensagens formatadas
            )
            
            # Obtém ou cria agente específico para este telefone
            agent = self._get_or_create_agent(phone_number)
            
            # Obtém estado atual da sessão
            session_state = self._get_session_state(agent)
            
            # Adicionar IDs do Supabase ao estado da sessão
            session_state["lead_id"] = str(lead.id)
            session_state["conversation_id"] = str(conversation.id)
            
            # Adiciona mensagem ao histórico
            session_state["conversation_history"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Salvar mensagem do usuário no Supabase
            await message_repository.save_user_message(
                conversation_id=conversation.id,
                content=message,
                media_type=media_type,
                media_url=media_data.get("url") if isinstance(media_data, dict) else None
            )
            
            # Analisa contexto e determina estágio
            analysis = await self._analyze_context(message, agent, session_state)
            
            # Atualiza informações do lead
            self._update_lead_info(analysis, agent, session_state)
            
            # Processa mídia se houver
            media_info = None
            processed_images = None
            
            if media_type and media_data:
                # Para imagens, criar objeto Image AGnO primeiro
                if media_type == "image":
                    # Criar imagem AGnO que será usada tanto para análise quanto para o prompt
                    agno_image = self._create_agno_image(media_data)
                    if agno_image:
                        processed_images = [agno_image]
                        
                        # Analisar a imagem para extrair dados
                        media_info = await self._process_media(media_type, media_data)
                        
                        if media_info:
                            # Atualizar lead_info com dados extraídos da conta
                            if 'bill_value' in media_info:
                                session_state["lead_info"]["bill_value"] = media_info['bill_value']
                            if 'customer_name' in media_info:
                                session_state["lead_info"]["customer_name"] = media_info['customer_name']
                            if 'address' in media_info:
                                session_state["lead_info"]["address"] = media_info['address']
                            if 'consumption_kwh' in media_info:
                                session_state["lead_info"]["consumption_kwh"] = media_info['consumption_kwh']
                else:
                    # Para outros tipos de mídia
                    media_info = await self._process_media(media_type, media_data)
            
            # Prepara contexto adicional para o agente
            context_prompt = self._build_context_prompt(
                message, 
                analysis, 
                session_state, 
                media_info,
                conversation_context=conversation_context  # Passar contexto do Supabase
            )
            
            # Executa o agente AGnO para gerar resposta
            # Se houver imagem processada, passar junto
            if processed_images:
                response = await self._run_agent(context_prompt, agent, images=processed_images)
            else:
                response = await self._run_agent(context_prompt, agent)
            
            # Adiciona resposta ao histórico
            session_state["conversation_history"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Salvar resposta do assistente no Supabase
            await message_repository.save_assistant_message(
                conversation_id=UUID(session_state["conversation_id"]),
                content=response
            )
            
            # Atualizar conversa no Supabase
            await conversation_repository.update_stage_and_sentiment(
                conversation_id=UUID(session_state["conversation_id"]),
                stage=session_state["current_stage"],
                sentiment=analysis.get("sentiment", "neutro")
            )
            
            # Incrementar contador de mensagens
            await conversation_repository.increment_message_count(
                UUID(session_state["conversation_id"])
            )
            
            # Atualizar lead no Supabase se houver novas informações
            lead_updates = {}
            lead_info = session_state.get("lead_info", {})
            
            if lead_info.get("name"):
                lead_updates["name"] = lead_info["name"]
            if lead_info.get("email"):
                lead_updates["email"] = lead_info["email"]
            if lead_info.get("property_type"):
                lead_updates["property_type"] = lead_info["property_type"]
            if lead_info.get("bill_value"):
                parsed_value = parse_brazilian_currency(lead_info["bill_value"])
                if parsed_value is not None:
                    lead_updates["bill_value"] = parsed_value
                else:
                    logger.warning(f"Não foi possível converter bill_value: '{lead_info.get('bill_value')}'")
            if lead_info.get("consumption_kwh"):
                try:
                    lead_updates["consumption_kwh"] = int(lead_info["consumption_kwh"])
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao converter consumption_kwh para int: {e}")
            if lead_info.get("address"):
                lead_updates["address"] = lead_info["address"]
            
            # Atualizar stage do lead
            lead_updates["current_stage"] = session_state["current_stage"]
            
            # Calcular score de qualificação baseado nas informações coletadas
            qualification_score = self._calculate_qualification_score(lead_info, session_state)
            if qualification_score:
                lead_updates["qualification_score"] = qualification_score
            
            if lead_updates:
                await lead_repository.update(
                    UUID(session_state["lead_id"]),
                    lead_updates
                )
            
            # Atualiza estado da sessão
            self._update_session_state(agent, session_state)
            
            # Determinar se deve reagir e qual emoji usar
            should_react, reaction_emoji = self._should_react_to_message(
                message, 
                analysis, 
                session_state,
                media_type
            )
            
            # Prepara metadados
            metadata = {
                "stage": session_state["current_stage"],
                "sentiment": analysis.get("sentiment", "neutro"),
                "lead_info": session_state["lead_info"],
                "typing_delay": calculate_typing_delay(response),
                "should_schedule": session_state["current_stage"] == "SCHEDULING",
                "session_id": agent.session_id if hasattr(agent, 'session_id') else None,
                "reasoning_enabled": True,
                "model": self.config.gemini.model,
                "should_react": should_react,
                "reaction_emoji": reaction_emoji,
                "message_id": message_id
            }
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return self._get_error_response(), {"error": str(e)}
    
    async def _run_agent(
        self, 
        prompt: str, 
        agent: Agent,
        images: Optional[List] = None,
        documents: Optional[List] = None,
        audio: Optional[List] = None
    ) -> str:
        """Executa o agente AGnO com suporte multimodal e fallback"""
        # Verificar cache primeiro
        cache_key = self._get_cache_key(prompt, agent.session_state)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            logger.info("Resposta encontrada no cache")
            return cached_response
        
        # Preparar kwargs para mídias
        kwargs = self._prepare_media_kwargs(images, audio)
        
        # Tentar com Gemini primeiro
        try:
            response = await self._run_agent_with_retry(
                agent, prompt, self.model, **kwargs
            )
            # Salvar no cache
            self._cache_response(cache_key, response)
            return response
        except Exception as gemini_error:
            logger.error(f"Gemini falhou após todas tentativas: {gemini_error}")
            
            # Tentar fallback com OpenAI
            if self.fallback_model and self.config.enable_fallback:
                logger.warning("Ativando fallback para OpenAI gpt-4o-mini...")
                try:
                    # Criar agente temporário com OpenAI
                    fallback_agent = self._create_fallback_agent(agent.session_id)
                    response = await self._run_agent_with_retry(
                        fallback_agent, prompt, self.fallback_model, **kwargs
                    )
                    # Salvar no cache
                    self._cache_response(cache_key, response)
                    return response
                except Exception as openai_error:
                    logger.error(f"OpenAI também falhou: {openai_error}")
            
            # Se tudo falhar, usar resposta de fallback contextual
            return self._get_contextual_fallback_response(agent.session_state)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, Exception)),
        before_sleep=lambda retry_state: logger.warning(
            f"Tentativa {retry_state.attempt_number}/3, aguardando {retry_state.next_action.sleep} segundos..."
        )
    )
    async def _run_agent_with_retry(
        self, 
        agent: Agent,
        prompt: str,
        model: Any,
        **kwargs
    ) -> str:
        """Executa agente com retry logic"""
        # Usa o método run do AGnO
        response = await asyncio.to_thread(
            agent.run,
            prompt,
            **kwargs
        )
        
        # Log do reasoning em modo debug
        if self.config.debug and hasattr(response, 'reasoning'):
            logger.debug("=== REASONING STEPS ===")
            if isinstance(response.reasoning, list):
                for i, step in enumerate(response.reasoning, 1):
                    logger.debug(f"Step {i}: {step}")
            else:
                logger.debug(f"Reasoning: {response.reasoning}")
            logger.debug("=== END REASONING ===")
        
        # Extrai o conteúdo da resposta
        if hasattr(response, 'content'):
            return response.content
        elif hasattr(response, 'messages') and response.messages:
            # Se retornar uma lista de mensagens, pega a última
            return response.messages[-1].content
        else:
            return str(response)
    
    def _prepare_media_kwargs(self, images: Optional[List], audio: Optional[List]) -> Dict[str, Any]:
        """Prepara kwargs com mídias convertidas para formato AGnO"""
        kwargs = {}
        
        if images:
            agno_images = []
            for img in images:
                if isinstance(img, Image):
                    agno_images.append(img)
                elif isinstance(img, dict):
                    if 'url' in img:
                        agno_images.append(Image(url=img['url']))
                    elif 'path' in img:
                        agno_images.append(Image(filepath=img['path']))
                    elif 'base64' in img:
                        import base64 as b64
                        img_bytes = b64.b64decode(img['base64'])
                        agno_images.append(Image(content=img_bytes))
                elif isinstance(img, str):
                    if img.startswith('http'):
                        agno_images.append(Image(url=img))
                    else:
                        agno_images.append(Image(filepath=img))
            
            if agno_images:
                kwargs['images'] = agno_images
                logger.debug(f"Preparou {len(agno_images)} imagem(ns)")
        
        if audio:
            agno_audio = []
            for aud in audio:
                if isinstance(aud, Audio):
                    agno_audio.append(aud)
                elif isinstance(aud, dict):
                    if 'content' in aud:
                        agno_audio.append(Audio(content=aud['content'], format=aud.get('format', 'wav')))
                    elif 'path' in aud:
                        with open(aud['path'], 'rb') as f:
                            agno_audio.append(Audio(content=f.read(), format=aud.get('format', 'wav')))
            
            if agno_audio:
                kwargs['audio'] = agno_audio
                logger.debug(f"Preparou {len(agno_audio)} áudio(s)")
        
        return kwargs
    
    def _get_cache_key(self, prompt: str, session_state: Dict[str, Any]) -> str:
        """Gera chave única para cache baseada no prompt e contexto"""
        import hashlib
        stage = session_state.get('current_stage', 'INITIAL_CONTACT')
        content = f"{prompt}:{stage}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Busca resposta no cache se ainda válida"""
        if cache_key in self._response_cache:
            response, timestamp = self._response_cache[cache_key]
            # Verificar se ainda está dentro do TTL
            if datetime.now() - timestamp < timedelta(minutes=self.config.response_cache_ttl):
                return response
            else:
                # Limpar entrada expirada
                del self._response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Armazena resposta no cache"""
        self._response_cache[cache_key] = (response, datetime.now())
        # Limpar cache antigo se ficar muito grande
        if len(self._response_cache) > 100:
            # Remover 20% das entradas mais antigas
            sorted_keys = sorted(
                self._response_cache.keys(),
                key=lambda k: self._response_cache[k][1]
            )
            for key in sorted_keys[:20]:
                del self._response_cache[key]
    
    def _create_fallback_agent(self, session_id: str) -> Agent:
        """Cria agente temporário com modelo de fallback"""
        return Agent(
            name=self.config.personality.name,
            description=f"Consultora de energia solar da {self.config.personality.company}",
            instructions=PromptTemplates.format_system_prompt(),
            model=self.fallback_model,
            reasoning=True,
            reasoning_min_steps=1,  # Reduzido para velocidade
            reasoning_max_steps=2,  # Máximo 2 para garantir resposta rápida
            memory=self.memory_config,
            storage=self.storage,
            session_id=session_id,
            search_knowledge=False,  # Desabilitar para velocidade
            debug_mode=self.config.debug
        )
    
    def _get_contextual_fallback_response(self, session_state: Dict[str, Any]) -> str:
        """Resposta de fallback baseada no contexto da conversa"""
        stage = session_state.get('current_stage', 'INITIAL_CONTACT')
        lead_info = session_state.get('lead_info', {})
        
        fallback_responses = {
            'INITIAL_CONTACT': "Oi! 😊 Sou a Luna da SolarPrime. Estamos com alta demanda, mas quero muito te ajudar a economizar na conta de luz! Como posso te chamar?",
            'IDENTIFICATION': f"Desculpe a demora{' ' + lead_info.get('name', '') if lead_info.get('name') else ''}! Para continuar nossa conversa sobre economia solar, qual seu nome completo?",
            'DISCOVERY': "Ops, tive uma instabilidade! 😅 Me conta, você mora em casa ou apartamento? Isso ajuda a calcular sua economia!",
            'QUALIFICATION': "Perdão pelo atraso! Para calcular sua economia exata, preciso saber: qual o valor médio da sua conta de luz?",
            'SCHEDULING': "Desculpe a demora! Nossos consultores têm horários disponíveis:\n📅 Amanhã: 10h, 14h ou 16h\n📅 Quinta: 9h, 11h ou 15h\n\nQual horário fica melhor pra você?",
            'OBJECTION_HANDLING': "Entendo sua preocupação! 🤝 A energia solar realmente é um investimento que se paga. Que tal conversarmos melhor sobre isso?",
            'NURTURING': "Oi! Voltei para saber se você ainda tem interesse em economizar até 95% na conta de luz. Posso te ajudar?"
        }
        
        return fallback_responses.get(stage, self._get_fallback_response())
    
    async def _analyze_context(
        self, 
        message: str, 
        agent: Agent,
        session_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisa o contexto da conversa usando AGnO"""
        try:
            # Prepara histórico resumido
            history_summary = self._get_conversation_summary(session_state)
            
            # Prepara prompt de análise com contexto completo
            analysis_prompt = f"""Você é um analisador de contexto para vendas de energia solar.

CONTEXTO DA CONVERSA:
{history_summary}

INFORMAÇÕES JÁ COLETADAS:
{json.dumps(session_state.get("lead_info", {}), indent=2, ensure_ascii=False)}

ESTÁGIO ATUAL: {session_state.get("current_stage", "INITIAL_CONTACT")}

NOVA MENSAGEM DO LEAD: {message}

SE a conversa indica que perguntamos o nome e o lead respondeu com uma única palavra ou nome próprio, considere isso como o nome do lead.

Analise e determine:
1. Em qual estágio a conversa deve estar agora
2. O sentimento do lead em relação à proposta
3. A intenção principal da mensagem
4. Próxima ação recomendada
5. Informações importantes a extrair (IMPORTANTE: Se o lead disse seu nome, inclua "nome: [nome_mencionado]")

IMPORTANTE: Responda APENAS com um JSON válido, sem texto adicional.

{{
    "stage": "IDENTIFICATION ou DISCOVERY ou QUALIFICATION ou OBJECTION_HANDLING ou SCHEDULING ou FOLLOW_UP",
    "sentiment": "positivo ou neutro ou negativo",
    "intent": "descrição clara da intenção",
    "next_action": "próxima ação específica",
    "key_info": ["lista de informações extraídas", "Se o lead mencionou nome, adicione: nome: [nome_dito]"]
}}"""
            
            # Cria um agente temporário para análise
            analysis_agent = Agent(
                name="Analisador",
                description="Analisador de contexto de vendas",
                instructions="Você analisa conversas e retorna APENAS JSON válido, sem texto adicional.",
                model=self.model
            )
            
            # Executa análise
            result = await asyncio.to_thread(
                analysis_agent.run,
                analysis_prompt
            )
            
            # Parse do resultado
            try:
                if hasattr(result, 'content'):
                    content = result.content
                else:
                    content = str(result)
                
                # Remove possíveis marcadores de código
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Parse JSON
                analysis = json.loads(content)
                
                # Atualiza estágio se mudou
                new_stage = analysis.get("stage", session_state.get("current_stage"))
                if new_stage != session_state.get("current_stage"):
                    logger.info(f"Mudança de estágio: {session_state.get('current_stage')} -> {new_stage}")
                    session_state["current_stage"] = new_stage
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.warning(f"Falha ao parsear análise: {e}, conteúdo: {content[:200]}")
                return {
                    "stage": session_state.get("current_stage", "INITIAL_CONTACT"),
                    "sentiment": "neutro",
                    "intent": "continuação de conversa",
                    "next_action": "responder naturalmente",
                    "key_info": []
                }
                
        except Exception as e:
            logger.error(f"Erro na análise de contexto: {e}")
            return {
                "stage": session_state.get("current_stage", "INITIAL_CONTACT"),
                "sentiment": "neutro",
                "intent": "erro na análise",
                "next_action": "continuar conversa",
                "key_info": []
            }
    
    def _get_conversation_summary(self, session_state: Dict[str, Any]) -> str:
        """Cria um resumo do histórico da conversa"""
        history = session_state.get("conversation_history", [])
        if not history:
            return "Primeira interação com o lead."
        
        # Pega últimas 6 mensagens (3 trocas)
        recent = history[-6:]
        summary = []
        
        for msg in recent:
            role = "Lead" if msg["role"] == "user" else "Luna"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary.append(f"{role}: {content}")
        
        return "\n".join(summary)
    
    def _build_context_prompt(
        self, 
        message: str, 
        analysis: Dict[str, Any], 
        session_state: Dict[str, Any],
        media_info: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[str] = None
    ) -> str:
        """Constrói o prompt com contexto para o agente"""
        # Obtém instruções específicas do estágio
        stage_instructions = PromptTemplates.get_stage_prompt(session_state["current_stage"])
        
        # Informações do lead
        lead_info = session_state.get("lead_info", {})
        lead_name = lead_info.get("name", "")
        
        # Monta contexto
        context_parts = [
            f"CONTEXTO IMPORTANTE:",
            f"- Você já está em conversa com este lead",
            f"- Estágio atual: {session_state['current_stage']}",
            f"- Sentimento detectado: {analysis.get('sentiment', 'neutro')}",
        ]
        
        if lead_name:
            context_parts.append(f"- Nome do lead: {lead_name}")
        
        # Se houver análise de mídia, adicionar contexto especial
        if media_info and 'bill_value' in media_info:
            context_parts.append("\n🎯 DADOS EXTRAÍDOS DA CONTA DE LUZ:")
            context_parts.append(f"- Valor da conta: {media_info.get('bill_value', 'Não identificado')}")
            
            if media_info.get('consumption_kwh'):
                context_parts.append(f"- Consumo: {media_info['consumption_kwh']} kWh")
            if media_info.get('customer_name'):
                context_parts.append(f"- Titular: {media_info['customer_name']}")
            if media_info.get('address'):
                context_parts.append(f"- Endereço: {media_info['address']}")
            if media_info.get('reference_period'):
                context_parts.append(f"- Período: {media_info['reference_period']}")
            
            # Instruções especiais para conta de luz
            context_parts.append("\n📌 INSTRUÇÕES ESPECIAIS PARA ANÁLISE DE CONTA:")
            context_parts.append("- RESPONDA IMEDIATAMENTE com os dados extraídos da conta")
            context_parts.append("- NÃO diga que vai analisar ou retornar depois - A ANÁLISE JÁ FOI FEITA")
            context_parts.append("- Confirme o valor extraído: 'Vi aqui na sua conta que o valor é R$ X, está correto?'")
            context_parts.append("- Calcule e mencione a economia estimada de 95% AGORA")
            context_parts.append("- Seja específico com os números NESTA MENSAGEM")
            context_parts.append("- Use os dados para personalizar sua abordagem IMEDIATAMENTE")
            context_parts.append("- NUNCA prometa retornar com números - você JÁ TEM os números")
            
            # Se o valor for alto, adicionar contexto de urgência
            try:
                bill_value = media_info.get('bill_value')
                if bill_value and isinstance(bill_value, str):
                    valor_str = bill_value.replace('R$', '').replace('.', '').replace(',', '.').strip()
                    if valor_str:
                        valor = float(valor_str)
                        if valor > 500:
                            context_parts.append(f"\n⚡ ALERTA: Conta alta! Enfatize a economia potencial de R$ {valor * 0.95:.2f}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Erro ao converter valor da conta: {bill_value if 'bill_value' in locals() else 'None'} - {e}")
        
        # Adiciona informações conhecidas
        if lead_info:
            context_parts.append("\nINFORMAÇÕES JÁ COLETADAS:")
            for key, value in lead_info.items():
                if key not in ['phone', 'last_interaction'] and value:
                    # Formatar nome da chave de forma mais amigável
                    friendly_key = key.replace('_', ' ').title()
                    context_parts.append(f"- {friendly_key}: {value}")
        
        # Adiciona histórico completo do Supabase se disponível
        if conversation_context:
            context_parts.append(f"\nHISTÓRICO COMPLETO DA CONVERSA:\n{conversation_context}")
        else:
            # Fallback para histórico da sessão se não tiver contexto do Supabase
            history_summary = self._get_conversation_summary(session_state)
            if history_summary != "Primeira interação com o lead.":
                context_parts.append(f"\nHISTÓRICO RECENTE:\n{history_summary}")
        
        # Adiciona mensagem atual
        context_parts.append(f"\nNOVA MENSAGEM DO LEAD: {message}")
        
        # Adiciona instruções do estágio
        context_parts.append(f"\nINSTRUÇÕES PARA ESTE ESTÁGIO:\n{stage_instructions}")
        
        # Adiciona orientações específicas
        context_parts.append("\nORIENTAÇÕES:")
        context_parts.append("- NÃO se apresente novamente se já conversaram antes")
        context_parts.append("- Continue a conversa naturalmente do ponto onde parou")
        context_parts.append("- Use o nome do lead se já souber")
        context_parts.append("- Seja natural e evite repetições")
        
        # Se houver análise de conta, adicionar orientação extra
        if media_info and 'bill_value' in media_info:
            context_parts.append("\n⚠️ IMPORTANTE - ANÁLISE DE CONTA JÁ CONCLUÍDA:")
            context_parts.append("- A análise da conta JÁ FOI FEITA - os dados estão acima")
            context_parts.append("- RESPONDA AGORA com os valores encontrados")
            context_parts.append("- NÃO prometa analisar ou retornar depois")
            context_parts.append("- Exemplo: 'Analisei sua conta e vi que você paga R$ [VALOR]. Com nossa solução...'")
            context_parts.append("- Demonstre que analisou a conta detalhadamente")
            context_parts.append("- Seja consultivo e mostre expertise")
        
        # Adiciona exemplos se relevante
        if self._should_use_example(analysis):
            example = self._get_relevant_example(analysis)
            if example:
                context_parts.append(f"\nExemplo de resposta apropriada:\n{example}")
        
        return "\n".join(context_parts)
    
    async def _process_media(
        self, 
        media_type: str, 
        media_data: Any
    ) -> Optional[Dict[str, Any]]:
        """Processa mídia usando capacidades do Gemini 2.5 Pro"""
        try:
            if media_type == "image":
                logger.info("Processando imagem de conta de luz...")
                
                # Criar prompt específico para análise de conta de luz
                analysis_prompt = """Analise esta conta de energia elétrica e extraia IMEDIATAMENTE as seguintes informações:

1. Valor total da fatura (em R$)
2. Consumo em kWh
3. Mês/Ano de referência
4. Nome do titular da conta
5. Endereço completo
6. CPF ou CNPJ
7. Nome da distribuidora de energia
8. Histórico de consumo (se disponível)

IMPORTANTE: Retorne APENAS um JSON válido com essas informações, sem texto adicional.
Formato esperado:
{
    "bill_value": "valor em reais",
    "consumption_kwh": "consumo em kWh",
    "reference_period": "mês/ano",
    "customer_name": "nome do titular",
    "address": "endereço completo",
    "document": "CPF ou CNPJ",
    "distributor": "nome da distribuidora",
    "consumption_history": []
}

Se alguma informação não estiver disponível, use null."""
                
                # Processar imagem com Gemini Vision
                result = await self._analyze_image_with_gemini(
                    media_data, 
                    analysis_prompt
                )
                
                if result:
                    logger.info(f"Dados extraídos da conta: {json.dumps(result, indent=2)}")
                    return result
                else:
                    logger.warning("Não foi possível extrair dados da imagem")
                    return {
                        "media_received": "image",
                        "analysis_status": "failed"
                    }
                    
            elif media_type == "audio":
                logger.info("Processamento de áudio ainda não implementado")
                return {
                    "media_received": "audio",
                    "analysis_pending": True
                }
                
            elif media_type == "document":
                if media_data.get('mime_type') == 'application/pdf':
                    logger.info("Processando documento PDF...")
                    # Processar PDF com OCR se necessário
                    result = await self._process_pdf_with_ocr(media_data)
                    return result
                else:
                    logger.info("Tipo de documento não suportado")
                    return {
                        "media_received": "document",
                        "analysis_pending": True
                    }
            else:
                logger.warning(f"Tipo de mídia não suportado: {media_type}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao processar mídia: {e}")
            return None
    
    def _update_lead_info(self, analysis: Dict[str, Any], agent: Agent, session_state: Dict[str, Any]):
        """Atualiza informações do lead baseado na análise"""
        lead_info = session_state.get("lead_info", {})
        
        # Extrai informações chave
        key_info = analysis.get("key_info", [])
        
        # Lista de palavras comuns que NÃO são nomes
        palavras_comuns = [
            "oi", "olá", "ola", "sim", "não", "nao", "ok", "okay", "blz", "beleza",
            "voltei", "volto", "aqui", "ali", "tudo", "bem", "bom", "boa", "dia", 
            "tarde", "noite", "obrigado", "obrigada", "valeu", "vlw", "pra", "para",
            "com", "sem", "mais", "menos", "muito", "pouco", "agora", "depois",
            "antes", "sempre", "nunca", "talvez", "quero", "queria", "pode", "posso"
        ]
        
        # Verifica se estamos esperando o nome (após pergunta específica)
        conversation_history = session_state.get("conversation_history", [])
        esperando_nome = False
        
        # Verifica se a última mensagem do assistente perguntou o nome
        if len(conversation_history) >= 2:
            ultima_msg_assistente = conversation_history[-2] if conversation_history[-1]["role"] == "user" else None
            if ultima_msg_assistente and ultima_msg_assistente["role"] == "assistant":
                msg_content = ultima_msg_assistente["content"].lower()
                if any(frase in msg_content for frase in ["como posso te chamar", "qual é o seu nome", "me diz seu nome", "como você se chama"]):
                    esperando_nome = True
        
        # Verifica se a mensagem é simplesmente um nome (resposta à pergunta sobre nome)
        message = conversation_history[-1].get("content", "") if conversation_history else ""
        if message and esperando_nome and session_state.get("current_stage") == "IDENTIFICATION":
            # Remove pontuação e espaços extras
            possible_name = message.strip().strip(".,!?").title()
            
            # Verifica se é uma palavra válida para nome
            if (possible_name and 
                len(possible_name) > 2 and 
                possible_name[0].isupper() and
                possible_name.lower() not in palavras_comuns and
                not any(char.isdigit() for char in possible_name)):
                
                lead_info["name"] = possible_name
                logger.info(f"Nome identificado pela resposta direta: {possible_name}")
        
        for info in key_info:
            info_lower = info.lower()
            
            # Extrai nome apenas com validação rigorosa
            if "nome:" in info_lower:
                # Extrai o nome após "nome:"
                name = info.split(":")[-1].strip().strip(".,!?")
                if (name and 
                    len(name) > 2 and 
                    name.lower() not in ["o lead", "do lead", "usuário"] and
                    name.lower() not in palavras_comuns and
                    not any(char.isdigit() for char in name)):
                    lead_info["name"] = name.title()
                    logger.info(f"Nome identificado: {name}")
            elif any(word in info_lower for word in ["chamo", "sou o", "sou a", "meu nome"]):
                # Tenta extrair o nome de outras formas
                words = info.split()
                for i, word in enumerate(words):
                    if word.lower() in ["chamo", "sou", "nome"] and i + 1 < len(words):
                        name = words[i + 1].strip(".,!?")
                        if (name and 
                            len(name) > 2 and
                            name.lower() not in palavras_comuns and
                            not any(char.isdigit() for char in name)):
                            lead_info["name"] = name.title()
                            logger.info(f"Nome identificado: {name}")
                            break
            
            # Extrai tipo de imóvel
            elif any(word in info_lower for word in ["casa", "apartamento", "residência", "comercial", "empresa"]):
                if "casa" in info_lower:
                    lead_info["property_type"] = "casa"
                elif "apartamento" in info_lower or "ap" in info_lower.split():
                    lead_info["property_type"] = "apartamento"
                elif "empresa" in info_lower or "comercial" in info_lower:
                    lead_info["property_type"] = "comercial"
                else:
                    lead_info["property_type"] = info
            
            # Extrai valor da conta
            elif "r$" in info_lower or any(char.isdigit() for char in info):
                import re
                # Extrai valores monetários
                money_pattern = r'R\$?\s*(\d+(?:\.\d{3})*(?:,\d{2})?)'
                matches = re.findall(money_pattern, info, re.IGNORECASE)
                if matches:
                    lead_info["bill_value"] = f"R$ {matches[0]}"
                else:
                    # Tenta extrair apenas números
                    numbers = re.findall(r'\d+', info)
                    if numbers:
                        lead_info["bill_value"] = f"R$ {numbers[0]}"
        
        # Adiciona timestamp
        lead_info["last_interaction"] = datetime.now().isoformat()
        
        # Atualiza no estado da sessão
        session_state["lead_info"] = lead_info
    
    def _should_use_example(self, analysis: Dict[str, Any]) -> bool:
        """Determina se deve usar resposta de exemplo"""
        intent = analysis.get("intent", "").lower()
        triggers = ["custo", "preço", "valor", "funciona", "manutenção", "caro"]
        return any(trigger in intent for trigger in triggers)
    
    def _get_relevant_example(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Obtém exemplo relevante baseado na análise"""
        intent = analysis.get("intent", "").lower()
        
        if "caro" in intent or "custo" in intent:
            return get_example_response("cost_concern")
        elif "funciona" in intent:
            return get_example_response("how_it_works")
        elif "manutenção" in intent:
            return get_example_response("maintenance_concern")
        
        return None
    
    async def _analyze_image_with_gemini(
        self, 
        image_data: Any, 
        analysis_prompt: str
    ) -> Optional[Dict[str, Any]]:
        """Analisa imagem usando Gemini 2.5 Pro Vision"""
        try:
            # Criar imagem AGnO usando método auxiliar
            agno_image = self._create_agno_image(image_data)
            
            if not agno_image:
                logger.error("Não foi possível criar objeto Image AGnO")
                return None
            
            # Executar análise usando o agente principal com prompt específico
            logger.info("Enviando imagem para análise com Gemini Vision...")
            
            # Criar prompt combinado para análise
            combined_prompt = f"""Você é um assistente especializado em análise de contas de energia.
            
{analysis_prompt}

IMPORTANTE: Retorne APENAS um JSON válido, sem texto adicional antes ou depois."""
            
            # Criar agente temporário para análise de visão
            vision_agent = Agent(
                name="Analisador Vision Gemini",
                description="Analisador de imagens de contas de luz",
                instructions="Analise imagens e retorne APENAS JSON estruturado, sem texto adicional.",
                model=self.model,  # Gemini 2.5 Pro
                reasoning=False  # Desabilitar reasoning para resposta direta
            )
            
            # Executar análise
            result = await asyncio.to_thread(
                vision_agent.run,
                combined_prompt,
                images=[agno_image]  # Passar objeto Image do AGnO
            )
            
            # Parsear resultado JSON
            parsed_result = self._parse_vision_result(result)
            
            if parsed_result:
                logger.info("Imagem analisada com sucesso pelo Gemini")
                return parsed_result
            else:
                logger.warning("Gemini não conseguiu extrair dados estruturados da imagem")
                return None
            
        except Exception as e:
            logger.error(f"Erro ao analisar imagem com Gemini: {e}")
            # Tentar fallback com OpenAI se disponível
            if self.fallback_model and self.config.enable_fallback:
                logger.info("Tentando análise de imagem com OpenAI GPT-4.1-nano...")
                return await self._analyze_image_with_openai(image_data, analysis_prompt)
            return None
    
    async def _analyze_image_with_openai(
        self, 
        image_data: Any, 
        analysis_prompt: str
    ) -> Optional[Dict[str, Any]]:
        """Analisa imagem usando OpenAI GPT-4.1-nano Vision como fallback"""
        try:
            # Criar agente temporário com OpenAI para análise
            openai_agent = Agent(
                name="Analisador Vision OpenAI",
                description="Analisador de imagens de contas de luz usando OpenAI",
                instructions="Analise imagens e retorne APENAS JSON estruturado, sem texto adicional.",
                model=self.fallback_model,  # OpenAI GPT-4.1-nano
                reasoning=False  # Desabilitar reasoning para resposta direta
            )
            
            # Criar imagem AGnO usando método auxiliar
            agno_image = self._create_agno_image(image_data)
            
            if not agno_image:
                logger.error("Não foi possível criar objeto Image AGnO para OpenAI")
                return None
            
            # Executar análise
            logger.info("Enviando imagem para análise com OpenAI Vision...")
            result = await asyncio.to_thread(
                openai_agent.run,
                analysis_prompt,
                images=[agno_image]
            )
            
            # Parsear resultado
            parsed_result = self._parse_vision_result(result)
            
            if parsed_result:
                logger.info("Imagem analisada com sucesso pelo OpenAI")
                # Adicionar flag indicando que foi processado por fallback
                parsed_result['_processed_by'] = 'openai_fallback'
                return parsed_result
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao analisar imagem com OpenAI: {e}")
            return None
    
    def _create_agno_image(self, image_data: Any) -> Optional[Image]:
        """Cria objeto Image do AGnO a partir de diferentes formatos"""
        try:
            if isinstance(image_data, dict):
                if 'url' in image_data:
                    return Image(url=image_data['url'])
                elif 'base64' in image_data:
                    try:
                        img_bytes = base64.b64decode(image_data['base64'])
                        return Image(content=img_bytes)
                    except Exception as e:
                        logger.error(f"Erro ao decodificar base64: {e}")
                        return None
                elif 'path' in image_data:
                    return Image(filepath=image_data['path'])
            elif isinstance(image_data, str):
                if image_data.startswith('http'):
                    return Image(url=image_data)
                else:
                    return Image(filepath=image_data)
            
            logger.error(f"Formato de imagem não reconhecido: {type(image_data)}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar Image AGnO: {e}")
            return None
    
    def _parse_vision_result(self, result: Any) -> Optional[Dict[str, Any]]:
        """Parseia resultado da análise de visão"""
        try:
            # Extrair conteúdo da resposta
            if hasattr(result, 'content'):
                content = result.content
            elif hasattr(result, 'messages') and result.messages:
                content = result.messages[-1].content
            else:
                content = str(result)
            
            # Limpar e parsear JSON
            content = content.strip()
            
            # Remover marcadores de código se existirem
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parsear JSON
            parsed = json.loads(content)
            
            # Normalizar valores monetários se existirem
            if 'bill_value' in parsed and parsed['bill_value']:
                # Garantir formato correto do valor
                value = parsed['bill_value']
                if not value.startswith('R$'):
                    value = f"R$ {value}"
                parsed['bill_value'] = value
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da análise de visão: {e}")
            logger.debug(f"Conteúdo recebido: {content[:500] if 'content' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao parsear resultado: {e}")
            return None
    
    async def _process_pdf_with_ocr(self, pdf_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa PDF com OCR se necessário"""
        try:
            logger.info("Processamento de PDF iniciado")
            
            # Verificar se temos os módulos PDF do AGnO disponíveis
            if AGNO_READERS_AVAILABLE and PDFImageReader:
                logger.info("Usando PDFImageReader do AGnO para processar PDF com OCR")
                
                try:
                    # Criar PDFImageReader baseado no tipo de dados
                    pdf_reader = None
                    
                    if 'url' in pdf_data:
                        pdf_reader = PDFImageReader(pdf=pdf_data['url'])
                    elif 'path' in pdf_data:
                        pdf_reader = PDFImageReader(pdf=pdf_data['path'])
                    elif 'content' in pdf_data:
                        # Se for conteúdo binário, criar objeto IO
                        import io
                        pdf_io = io.BytesIO(pdf_data['content'])
                        pdf_reader = PDFImageReader(pdf=pdf_io)
                    elif 'base64' in pdf_data:
                        # Decodificar base64 e criar objeto IO
                        import io
                        pdf_bytes = base64.b64decode(pdf_data['base64'])
                        pdf_io = io.BytesIO(pdf_bytes)
                        pdf_reader = PDFImageReader(pdf=pdf_io)
                    
                    if pdf_reader:
                        # Extrair texto e realizar OCR
                        logger.info("Extraindo texto e realizando OCR no PDF...")
                        
                        # O PDFImageReader deve retornar o conteúdo extraído
                        # Tentamos diferentes métodos possíveis do AGnO
                        extracted_content = None
                        
                        # Tentar método extract() primeiro
                        if hasattr(pdf_reader, 'extract'):
                            extracted_content = pdf_reader.extract()
                        # Tentar método read() 
                        elif hasattr(pdf_reader, 'read'):
                            extracted_content = pdf_reader.read()
                        # Tentar método get_text()
                        elif hasattr(pdf_reader, 'get_text'):
                            extracted_content = pdf_reader.get_text()
                        # Tentar conversão para string
                        else:
                            extracted_content = str(pdf_reader)
                        
                        if extracted_content:
                            # Analisar o conteúdo extraído
                            logger.info("Conteúdo extraído do PDF, analisando...")
                            result = await self._analyze_pdf_content(extracted_content)
                            
                            if result:
                                logger.info("PDF processado com sucesso via PDFImageReader")
                                result['_processed_by'] = 'agno_pdf_reader'
                                return result
                        else:
                            logger.warning("PDFImageReader não conseguiu extrair conteúdo")
                    
                except Exception as e:
                    logger.error(f"Erro ao usar PDFImageReader: {e}")
                    # Continuar para fallback
            
            # Fallback: tentar processar PDF como imagem
            logger.info("Tentando processar PDF como imagem (fallback)")
            
            # Se temos URL ou path, podemos tentar converter primeira página para imagem
            if 'url' in pdf_data or 'path' in pdf_data:
                # Criar dados de imagem para análise
                image_data = {
                    'url': pdf_data.get('url'),
                    'path': pdf_data.get('path')
                }
                
                # Remover None values
                image_data = {k: v for k, v in image_data.items() if v is not None}
                
                # Usar o mesmo prompt de análise de conta
                analysis_prompt = """Analise esta conta de energia elétrica e extraia IMEDIATAMENTE as seguintes informações:

1. Valor total da fatura (em R$)
2. Consumo em kWh
3. Mês/Ano de referência
4. Nome do titular da conta
5. Endereço completo
6. CPF ou CNPJ
7. Nome da distribuidora de energia
8. Histórico de consumo (se disponível)

IMPORTANTE: Retorne APENAS um JSON válido com essas informações, sem texto adicional.
Formato esperado:
{
    "bill_value": "valor em reais",
    "consumption_kwh": "consumo em kWh",
    "reference_period": "mês/ano",
    "customer_name": "nome do titular",
    "address": "endereço completo",
    "document": "CPF ou CNPJ",
    "distributor": "nome da distribuidora",
    "consumption_history": []
}

Se alguma informação não estiver disponível, use null."""
                
                # Tentar análise como imagem
                result = await self._analyze_image_with_gemini(image_data, analysis_prompt)
                
                if result:
                    logger.info("PDF processado como imagem com sucesso")
                    result['_processed_by'] = 'pdf_as_image'
                    result['_original_format'] = 'pdf'
                    return result
            
            # Se nada funcionou, retornar sugestão
            logger.warning("Não foi possível processar o PDF. Sugerindo alternativas.")
            
            return {
                "media_received": "pdf",
                "analysis_status": "fallback_failed",
                "suggestion": "Por favor, envie uma foto/screenshot da conta de luz para melhor análise.",
                "fallback": "convert_to_image",
                "_attempted_methods": ["agno_pdf_reader", "pdf_as_image"]
            }
                
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {e}")
            return {
                "media_received": "pdf",
                "analysis_status": "error",
                "error": str(e),
                "suggestion": "Ocorreu um erro ao processar o PDF. Por favor, tente enviar uma foto da conta."
            }
    
    async def _analyze_pdf_content(self, content: str) -> Dict[str, Any]:
        """Analisa conteúdo extraído de PDF"""
        # Usar o mesmo prompt de análise de conta
        prompt = f"""Analise o texto extraído desta conta de energia e retorne um JSON com:
        - bill_value
        - consumption_kwh
        - reference_period
        - customer_name
        - address
        - document
        - distributor
        
        Texto extraído:
        {content[:2000]}  # Limitar para não exceder contexto
        
        Retorne APENAS o JSON, sem explicações."""
        
        # Criar agente temporário
        analyzer = Agent(
            name="Analisador PDF",
            model=self.model,
            instructions="Extraia informações e retorne JSON"
        )
        
        result = await asyncio.to_thread(analyzer.run, prompt)
        return self._parse_vision_result(result)
    
    def _get_fallback_response(self) -> str:
        """Resposta de fallback em caso de erro"""
        return """Desculpe, tive um pequeno problema técnico. 😅

Mas estou aqui para ajudar você com energia solar! Pode repetir sua pergunta?"""
    
    def _get_error_response(self) -> str:
        """Resposta de erro genérica"""
        return """Ops! Parece que estamos com uma instabilidade temporária. 

Por favor, tente novamente em alguns instantes. Nossa equipe já foi notificada!"""
    
    def _should_react_to_message(
        self, 
        message: str,
        analysis: Dict[str, Any],
        session_state: Dict[str, Any],
        media_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Determina se deve reagir à mensagem e qual emoji usar
        
        Returns:
            Tuple[bool, Optional[str]]: (deve_reagir, emoji)
        """
        message_lower = message.lower()
        
        # Reagir apenas a conta de luz/documento com joinha
        if media_type in ["image", "document"]:
            return True, "👍"
            
        # Reagir a agradecimentos com coração
        if any(word in message_lower for word in ["obrigado", "obrigada", "agradeço", "valeu", "thanks"]):
            return True, "❤️"
                
        # Não reagir em outros casos
        return False, None
    
    def _calculate_qualification_score(self, lead_info: Dict[str, Any], session_state: Dict[str, Any]) -> Optional[int]:
        """Calcula score de qualificação do lead baseado nas informações coletadas"""
        score = 0
        
        # Informações básicas (20 pontos)
        if lead_info.get("name"):
            score += 10
        if lead_info.get("email"):
            score += 10
        
        # Informações da propriedade (30 pontos)
        if lead_info.get("property_type"):
            score += 15
        if lead_info.get("address"):
            score += 15
        
        # Informações de consumo (30 pontos)
        if lead_info.get("bill_value"):
            score += 15
            # Bonus por conta alta
            bill_value = parse_brazilian_currency(lead_info["bill_value"])
            if bill_value is not None:
                if bill_value > 500:
                    score += 10
                elif bill_value > 300:
                    score += 5
            else:
                logger.debug(f"Não foi possível processar valor da conta para lead score: '{lead_info.get('bill_value')}'")
        
        if lead_info.get("consumption_kwh"):
            score += 10
        
        # Progressão no funil (20 pontos)
        stage = session_state.get("current_stage", "")
        if stage == "QUALIFICATION":
            score += 10
        elif stage == "OBJECTION_HANDLING":
            score += 15
        elif stage == "SCHEDULING":
            score += 20
        
        return min(score, 100)  # Máximo 100 pontos
    
    async def start_conversation(self, phone_number: str) -> Tuple[str, Dict[str, Any]]:
        """Inicia uma nova conversa"""
        # Obtém ou cria agente para este telefone
        agent = self._get_or_create_agent(phone_number)
        
        # Reseta o estado da sessão
        session_state = {
            "lead_info": {"phone": format_phone_number(phone_number)},
            "current_stage": "INITIAL_CONTACT",
            "conversation_history": []
        }
        self._update_session_state(agent, session_state)
        
        # Gera mensagem de boas-vindas usando o agente
        greeting_prompt = f"""Inicie uma conversa como {self.config.personality.name}, consultora de energia solar.
        
        Use a mensagem de saudação padrão adaptando para um tom natural e amigável.
        Mencione a economia de até 95% na conta de luz e pergunte sobre o interesse.
        Use no máximo 1-2 emojis apropriados."""
        
        greeting = await self._run_agent(greeting_prompt, agent)
        
        # Adiciona ao histórico
        session_state["conversation_history"].append({
            "role": "assistant",
            "content": greeting,
            "timestamp": datetime.now().isoformat()
        })
        
        metadata = {
            "stage": session_state["current_stage"],
            "typing_delay": calculate_typing_delay(greeting),
            "is_new_conversation": True
        }
        
        return greeting, metadata
    
    async def handle_no_interest(self, phone_number: str) -> Tuple[str, Dict[str, Any]]:
        """Trata casos de não interesse"""
        agent = self._get_or_create_agent(phone_number)
        session_state = self._get_session_state(agent)
        
        # Usa o agente para gerar despedida apropriada
        farewell_prompt = """O lead não tem interesse em energia solar.
        Agradeça educadamente, deixe a porta aberta para o futuro e deseje um bom dia.
        Seja breve e profissional."""
        
        farewell = await self._run_agent(farewell_prompt, agent)
        
        # Marca lead como não interessado
        session_state["lead_info"]["interested"] = False
        session_state["lead_info"]["closed_at"] = datetime.now().isoformat()
        session_state["current_stage"] = "CLOSED"
        
        metadata = {
            "stage": "CLOSED",
            "lead_qualified": False,
            "reason": "no_interest"
        }
        
        return farewell, metadata
    
    def get_conversation_summary(self, phone_number: str) -> Dict[str, Any]:
        """Obtém resumo da conversa para relatórios"""
        if phone_number in self.agents:
            agent = self.agents[phone_number]
            session_state = self._get_session_state(agent)
            
            return {
                "phone": phone_number,
                "lead_info": session_state.get("lead_info", {}),
                "current_stage": session_state.get("current_stage", "UNKNOWN"),
                "conversation_count": len(session_state.get("conversation_history", [])),
                "session_active": True,
                "last_interaction": session_state.get("lead_info", {}).get("last_interaction")
            }
        else:
            return {
                "phone": phone_number,
                "session_active": False
            }


# Função helper para criar agente
def create_sdr_agent() -> SDRAgent:
    """Cria e retorna uma instância do agente SDR"""
    return SDRAgent()


# Exporta componentes
__all__ = ["SDRAgent", "create_sdr_agent"]