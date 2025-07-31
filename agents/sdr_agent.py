"""
Agente SDR Principal - SolarPrime
================================
Implementação do agente de vendas usando AGnO Framework
"""

import json
import asyncio
import os
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

# Nota: PDFs serão processados diretamente pelo Gemini 2.5 Pro que suporta PDFs nativamente
# PDFReader/PDFImageReader são para criar knowledge bases, não para processamento multimodal direto
logger.info("✅ Processamento de PDFs será feito nativamente pelo Gemini 2.5 Pro")

# Imports para retry e fallback
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

# Configurações locais
from config.agent_config import config, get_config
from config.prompts import PromptTemplates, get_example_response
from config.messages import (
    get_error_message, get_fallback_message, get_follow_up_message,
    IMAGE_ERRORS, PDF_ERRORS, AUDIO_ERRORS, personalize_message
)
from utils.helpers import calculate_typing_delay, format_phone_number
from utils.currency_parser import parse_brazilian_currency

# Importar repositórios Supabase
from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from models.lead import LeadCreate, LeadUpdate
from models.conversation import ConversationCreate

# Importar serviços de integração
from services.kommo_service import KommoService
from services.google_calendar_service import GoogleCalendarService
from models.kommo_models import KommoLead, LeadStatus, SolutionType
from services.evolution_api import evolution_client as evolution_api


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
        
        # Inicializar serviços de integração
        self.kommo_service = None
        self.calendar_service = None
        
        # Tentar inicializar Kommo Service
        try:
            if os.getenv("KOMMO_LONG_LIVED_TOKEN"):
                self.kommo_service = KommoService()
                logger.info("✅ KommoService inicializado com sucesso")
            else:
                logger.warning("⚠️ KOMMO_LONG_LIVED_TOKEN não configurado - Kommo desabilitado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar KommoService: {e}")
            
        # Tentar inicializar Google Calendar Service
        try:
            if os.getenv("DISABLE_GOOGLE_CALENDAR", "false").lower() == "true":
                logger.info("ℹ️ Google Calendar desabilitado via configuração")
                self.calendar_service = None
            else:
                # Verificar se está usando Service Account
                use_service_account = os.getenv('GOOGLE_USE_SERVICE_ACCOUNT', 'true').lower() == 'true'
                
                if use_service_account:
                    # Service Account: inicializar diretamente sem verificar credentials.json
                    logger.info("🔐 Usando Google Calendar com Service Account")
                    try:
                        self.calendar_service = GoogleCalendarService(self.config)
                        # Verificar se o serviço foi realmente inicializado
                        if hasattr(self.calendar_service, 'service') and self.calendar_service.service:
                            logger.info("✅ GoogleCalendarService inicializado com sucesso (Service Account)")
                        else:
                            logger.warning("⚠️ Google Calendar Service não pôde ser inicializado")
                            logger.info("💡 Verifique as variáveis de ambiente do Service Account")
                            self.calendar_service = None
                    except Exception as init_error:
                        logger.warning(f"⚠️ Erro ao inicializar Google Calendar com Service Account: {init_error}")
                        logger.info("💡 Verifique se todas as variáveis do Service Account estão configuradas:")
                        logger.info("   - GOOGLE_SERVICE_ACCOUNT_EMAIL")
                        logger.info("   - GOOGLE_PRIVATE_KEY")
                        logger.info("   - GOOGLE_PROJECT_ID")
                        logger.info("   - GOOGLE_CALENDAR_ID")
                        self.calendar_service = None
                else:
                    # OAuth: manter lógica original
                    logger.info("🔑 Usando Google Calendar com OAuth")
                    # Tentar criar arquivo de credenciais a partir de variáveis de ambiente
                    if self._create_google_credentials_from_env():
                        logger.info("✅ Arquivo de credenciais OAuth criado a partir de variáveis de ambiente")
                    
                    # Verificar se arquivo existe agora
                    credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "credentials/google_calendar_credentials.json")
                    if os.path.exists(credentials_path):
                        try:
                            self.calendar_service = GoogleCalendarService(self.config)
                            # Verificar se o serviço foi realmente inicializado
                            if hasattr(self.calendar_service, 'service') and self.calendar_service.service:
                                logger.info("✅ GoogleCalendarService inicializado com sucesso (OAuth)")
                            else:
                                logger.warning("⚠️ Google Calendar Service não pôde ser inicializado (possivelmente falta autenticação)")
                                logger.info("💡 Em produção, considere usar DISABLE_GOOGLE_CALENDAR=true ou configurar Service Account")
                                self.calendar_service = None
                        except Exception as init_error:
                            logger.warning(f"⚠️ Erro ao inicializar Google Calendar: {init_error}")
                            if "could not locate runnable browser" in str(init_error):
                                logger.info("💡 Ambiente sem interface gráfica detectado")
                                logger.info("📖 Use Service Account definindo GOOGLE_USE_SERVICE_ACCOUNT=true")
                            logger.info("💡 Para desabilitar, defina DISABLE_GOOGLE_CALENDAR=true")
                            self.calendar_service = None
                    else:
                        logger.warning("⚠️ Credenciais OAuth do Google Calendar não encontradas - Calendar desabilitado")
                        logger.info("💡 Para usar Service Account, defina GOOGLE_USE_SERVICE_ACCOUNT=true")
                        logger.info("💡 Para desabilitar este aviso, defina DISABLE_GOOGLE_CALENDAR=true")
                        self.calendar_service = None
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar GoogleCalendarService: {e}")
            if "could not locate runnable browser" in str(e):
                logger.info("💡 Ambiente headless detectado - veja GOOGLE_CALENDAR_HEADLESS_AUTH.md")
            self.calendar_service = None
        
        logger.info(f"SDR Agent '{self.config.personality.name}' inicializado com AGnO Framework")
    
    def _create_google_credentials_from_env(self) -> bool:
        """Cria arquivo de credenciais do Google Calendar a partir de variáveis de ambiente"""
        try:
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            project_id = os.getenv('GOOGLE_PROJECT_ID', 'solarprime-ia-sdr')
            
            if not client_id or not client_secret:
                return False
            
            credentials = {
                "installed": {
                    "client_id": client_id,
                    "project_id": project_id,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": client_secret,
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            # Criar diretório se não existir
            credentials_dir = os.path.dirname(os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "credentials/google_calendar_credentials.json"))
            if credentials_dir:
                os.makedirs(credentials_dir, exist_ok=True)
            
            # Salvar arquivo
            credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "credentials/google_calendar_credentials.json")
            with open(credentials_path, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            logger.info(f"✅ Arquivo de credenciais criado em: {credentials_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar arquivo de credenciais: {e}")
            return False
    
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
            analysis = await self._analyze_context(message, agent, session_state, phone_number)
            
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
            # Usar mensagem humanizada ao invés de erro técnico
            error_msg = get_error_message("ERRO_TECNICO")
            return error_msg, {"error": str(e), "humanized": True}
    
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
        # Usa o método run do AGnO com timeout de 60 segundos para Gemini
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    agent.run,
                    prompt,
                    **kwargs
                ),
                timeout=60.0  # 60 segundos de timeout para Gemini
            )
        except asyncio.TimeoutError:
            logger.error("⏱️ Timeout ao executar Gemini após 60 segundos")
            raise Exception("Timeout na resposta do Gemini. Por favor, tente novamente.")
        
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
        lead_name = lead_info.get('name', '')
        
        # Usar mensagens humanizadas com variações automáticas
        return get_fallback_message(stage, lead_name)
    
    async def _analyze_context(
        self, 
        message: str, 
        agent: Agent,
        session_state: Dict[str, Any],
        phone_number: str
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
                old_stage = session_state.get("current_stage", "INITIAL_CONTACT")
                
                if new_stage != old_stage:
                    logger.info(f"Mudança de estágio: {old_stage} -> {new_stage}")
                    session_state["current_stage"] = new_stage
                    
                    # Integração com Kommo quando estágio muda
                    if self.kommo_service:
                        asyncio.create_task(self._update_kommo_on_stage_change(
                            phone_number=phone_number,
                            old_stage=old_stage,
                            new_stage=new_stage,
                            session_state=session_state,
                            analysis=analysis
                        ))
                
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
            logger.info(f"🎯 Processamento de mídia iniciado - Tipo: {media_type}")
            logger.debug(f"Dados recebidos - Tipo: {type(media_data)}, É dict: {isinstance(media_data, dict)}")
            
            # Definir limite de tamanho (50MB)
            MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB em bytes
            
            # Verificar tamanho do arquivo
            file_size = 0
            if isinstance(media_data, dict):
                if 'content' in media_data and media_data['content']:
                    file_size = len(media_data['content'])
                elif 'base64' in media_data and media_data['base64']:
                    # Estimar tamanho do base64 (aproximadamente 3/4 do tamanho encodado)
                    file_size = int(len(media_data['base64']) * 0.75)
                elif 'filesize' in media_data:
                    file_size = int(media_data['filesize'])
                elif 'size' in media_data:
                    file_size = int(media_data['size'])
            
            if file_size > MAX_FILE_SIZE:
                logger.warning(f"⚠️ Arquivo muito grande: {file_size / (1024*1024):.1f}MB (limite: 50MB)")
                size_mb = file_size / (1024 * 1024)
                return {
                    "media_received": media_type,
                    "analysis_status": "file_too_large",
                    "file_size_mb": f"{size_mb:.1f}",
                    "user_message": f"Opa! Esse arquivo é muito grande ({size_mb:.1f}MB)! 📦 Preciso de arquivos menores que 50MB. Que tal enviar uma versão menor ou dividir em partes?",
                    "suggestion": "💡 Dica: Se for PDF, tente enviar só as páginas importantes. Se for imagem, reduza a qualidade ou tire uma foto mais leve!"
                }
            
            # Log detalhado do conteúdo recebido para debug
            if isinstance(media_data, dict):
                logger.info(f"📋 Dados disponíveis: {list(media_data.keys())}")
                if 'content' in media_data:
                    logger.info(f"✅ Conteúdo binário presente: {len(media_data['content']) if media_data['content'] else 0} bytes")
                if 'base64' in media_data:
                    logger.info(f"✅ Base64 presente: {len(media_data['base64']) if media_data['base64'] else 0} chars")
                if 'url' in media_data:
                    logger.info(f"🔗 URL presente: {media_data['url'][:50] if media_data['url'] else 'None'}...")
                    # Avisar sobre URLs do WhatsApp
                    if media_data.get('url') and ('whatsapp.net' in media_data['url'] or 'mmg.whatsapp.net' in media_data['url']):
                        logger.warning("⚠️ URL do WhatsApp detectada - usará conteúdo binário/base64 ao invés da URL")
            
            if media_type == "image":
                logger.info("🖼️ Iniciando processamento de imagem...")
                logger.debug(f"Dados da mídia recebidos: type={type(media_data)}, keys={media_data.keys() if isinstance(media_data, dict) else 'N/A'}")
                
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
                logger.info("📤 Enviando imagem para análise com Gemini Vision...")
                result = await self._analyze_image_with_gemini(
                    media_data, 
                    analysis_prompt
                )
                
                if result:
                    logger.success(f"✅ Análise concluída! Dados extraídos: {json.dumps(result, indent=2)}")
                    return result
                else:
                    logger.warning("❌ Não foi possível extrair dados da imagem")
                    import random
                    messages = [
                        "Parece que a imagem não veio completa... 🤔 Pode enviar de novo? Às vezes o WhatsApp corta a qualidade!",
                        "Opa, a foto tá meio embaçada aqui! 📸 Tenta tirar outra com mais luz? Prometo que consigo ler!",
                        "Xi, não consegui ler direito a imagem... Que tal mandar outra foto? Capricha na iluminação! 💡"
                    ]
                    return {
                        "media_received": "image",
                        "analysis_status": "failed",
                        "user_message": random.choice(messages),
                        "suggestion": "Dica: Coloca a conta numa superfície plana e tira a foto de cima, com boa luz! 😊"
                    }
                    
            elif media_type == "audio":
                logger.info("🎤 Iniciando processamento de áudio...")
                logger.debug(f"Dados do áudio recebidos: type={type(media_data)}, keys={media_data.keys() if isinstance(media_data, dict) else 'N/A'}")
                
                # Criar prompt para transcrição e análise
                audio_prompt = """Transcreva este áudio e analise o conteúdo para identificar:

1. Nome do cliente (se mencionado)
2. Valor da conta de luz (se mencionado) 
3. Interesse em economia/desconto
4. Dúvidas ou perguntas
5. Sentimento geral (positivo/negativo/neutro)

Retorne um JSON com essas informações."""
                
                # Processar áudio
                result = await self._analyze_audio_with_gemini(media_data, audio_prompt)
                
                if result:
                    logger.success(f"✅ Áudio processado! Transcrição: {result.get('transcription', 'N/A')[:100]}...")
                    return result
                else:
                    logger.warning("❌ Não foi possível processar o áudio")
                    import random
                    messages = [
                        "O áudio chegou meio cortado aqui... 🎤 Que tal me contar por mensagem mesmo? Prometo que respondo rapidinho! 💬",
                        "Ops, o áudio tá com um chiado! Pode escrever pra mim? Assim a gente conversa melhor! 😊",
                        "Ih, não consegui ouvir direito... 🙉 Manda por texto que eu te respondo na hora!"
                    ]
                    return {
                        "media_received": "audio",
                        "analysis_status": "failed",
                        "user_message": random.choice(messages),
                        "suggestion": "Prefiro conversar por mensagem mesmo, assim não perdemos nada! 📱"
                    }
                
            elif media_type == "document":
                # Verificar mimetype (sem underscore)
                mimetype = media_data.get('mimetype') or media_data.get('mime_type', '')
                filename = media_data.get('filename', '')
                
                logger.info(f"📄 Documento recebido - Tipo: {mimetype}, Nome: {filename}")
                logger.debug(f"Dados do documento: {list(media_data.keys()) if isinstance(media_data, dict) else 'N/A'}")
                
                if mimetype == 'application/pdf' or filename.lower().endswith('.pdf'):
                    logger.info("📑 Iniciando processamento de PDF...")
                    # Processar PDF com OCR se necessário
                    result = await self._process_pdf_with_ocr(media_data)
                    
                    if result:
                        logger.info(f"✅ PDF processado com sucesso. Status: {result.get('analysis_status', 'completed')}")
                    else:
                        logger.warning("⚠️ Processamento de PDF retornou resultado vazio")
                    
                    return result
                else:
                    logger.info(f"❌ Tipo de documento não suportado: {mimetype}")
                    return {
                        "media_received": "document",
                        "mimetype": mimetype,
                        "filename": filename,
                        "analysis_status": "unsupported_type",
                        "suggestion": "Pode mandar um PDF ou foto da conta de luz? Assim calculo sua economia! 📸"
                    }
            elif media_type == "buffered":
                # Tipo buffered pode conter diferentes tipos de mídia
                logger.info("Processando mídia do tipo buffered...")
                
                # Tentar extrair o tipo real da mídia
                if isinstance(media_data, dict):
                    actual_type = media_data.get('type', 'unknown')
                    logger.info(f"Tipo real da mídia buffered: {actual_type}")
                    
                    # Reprocessar com o tipo correto
                    if actual_type in ["image", "audio", "document"]:
                        return await self._process_media(actual_type, media_data)
                    else:
                        logger.warning(f"Tipo de mídia buffered não reconhecido: {actual_type}")
                        return {
                            "media_received": "buffered",
                            "actual_type": actual_type,
                            "analysis_pending": True
                        }
                else:
                    logger.warning("Dados de mídia buffered inválidos")
                    return None
            else:
                logger.warning(f"❌ Tipo de mídia não suportado: {media_type}")
                return {
                    "media_received": media_type,
                    "analysis_status": "unsupported_media_type",
                    "suggestion": "Manda uma imagem, PDF ou áudio que eu processo pra você! 😊"
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar mídia: {e}", exc_info=True)
            return {
                "media_received": media_type,
                "analysis_status": "error",
                "error": str(e),
                "suggestion": "Opa, deu um probleminha ao processar seu arquivo! 😅 Tenta mandar de novo?"
            }
    
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
            
            # Extrai email
            elif "@" in info and "." in info:
                import re
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                matches = re.findall(email_pattern, info)
                if matches:
                    lead_info["email"] = matches[0].lower()
                    logger.info(f"Email identificado: {matches[0]}")
        
        # Verifica também email na mensagem completa
        if "email" not in lead_info and message:
            import re
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            matches = re.findall(email_pattern, message)
            if matches:
                lead_info["email"] = matches[0].lower()
                logger.info(f"Email identificado na mensagem: {matches[0]}")
        
        # Adiciona timestamp
        lead_info["last_interaction"] = datetime.now().isoformat()
        
        # Atualiza no estado da sessão
        session_state["lead_info"] = lead_info
        
        # Se temos email e estamos em SCHEDULING, tentar criar reunião no Calendar
        if (lead_info.get("email") and 
            session_state.get("current_stage") == "SCHEDULING" and
            self.calendar_service):
            asyncio.create_task(self._try_schedule_meeting(lead_info, session_state, message))
    
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
            logger.info("🔍 Iniciando análise de imagem com Gemini...")
            
            # Criar imagem AGnO usando método auxiliar
            agno_image = self._create_agno_image(image_data)
            
            if not agno_image:
                logger.error("❌ Não foi possível criar objeto Image AGnO")
                return None
            
            logger.success("✅ Objeto Image AGnO criado com sucesso")
            
            # Executar análise usando o agente principal com prompt específico
            logger.info("📡 Enviando imagem para API do Gemini Vision...")
            
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
            
            # Executar análise com timeout de 60 segundos
            logger.info("🚀 Executando análise da imagem...")
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        vision_agent.run,
                        combined_prompt,
                        images=[agno_image]  # Passar objeto Image do AGnO
                    ),
                    timeout=60.0  # 60 segundos de timeout para análise de imagem
                )
            except asyncio.TimeoutError:
                logger.error("⏱️ Timeout ao analisar imagem com Gemini após 60 segundos")
                raise Exception("Timeout na análise da imagem. Por favor, tente novamente.")
            
            logger.info(f"📝 Resposta bruta do Gemini: {result[:200]}..." if result else "❌ Resposta vazia")
            
            # Parsear resultado JSON
            parsed_result = self._parse_vision_result(result)
            
            if parsed_result:
                logger.success("✅ Imagem analisada com sucesso pelo Gemini!")
                logger.info(f"📊 Dados estruturados extraídos: {list(parsed_result.keys())}")
                return parsed_result
            else:
                logger.warning("⚠️ Gemini não conseguiu extrair dados estruturados da imagem")
                return None
            
        except Exception as e:
            logger.error(f"Erro ao analisar imagem com Gemini: {e}")
            # Tentar fallback com OpenAI se disponível
            if self.fallback_model and self.config.enable_fallback:
                logger.info("Tentando análise de imagem com OpenAI GPT-4.1-nano...")
                return await self._analyze_image_with_openai(image_data, analysis_prompt)
            return None
    
    async def _analyze_audio_with_gemini(
        self,
        audio_data: Any,
        analysis_prompt: str
    ) -> Optional[Dict[str, Any]]:
        """Analisa áudio usando Gemini 2.5 Pro"""
        try:
            logger.info("🎵 Iniciando análise de áudio com Gemini...")
            
            # Criar objeto Audio do AGnO
            agno_audio = await self._create_agno_audio(audio_data)
            
            if not agno_audio:
                logger.error("❌ Não foi possível criar objeto Audio AGnO")
                return None
            
            logger.success("✅ Objeto Audio AGnO criado com sucesso")
            
            # Criar agente para análise de áudio
            audio_agent = Agent(
                name="Analisador de Áudio Gemini",
                description="Transcritor e analisador de áudio",
                instructions="Transcreva áudios e retorne análise estruturada em JSON.",
                model=self.model,  # Gemini 2.5 Pro
                reasoning=False
            )
            
            # Executar análise com timeout de 60 segundos
            logger.info("🚀 Executando análise do áudio...")
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        audio_agent.run,
                        analysis_prompt,
                        audio=[agno_audio]  # Passar objeto Audio
                    ),
                    timeout=60.0  # 60 segundos de timeout para análise de áudio
                )
            except asyncio.TimeoutError:
                logger.error("⏱️ Timeout ao analisar áudio com Gemini após 60 segundos")
                raise Exception("Timeout na análise do áudio. Por favor, tente novamente.")
            
            logger.info(f"📝 Resposta do Gemini: {result[:200]}..." if result else "❌ Resposta vazia")
            
            # Parsear resultado
            parsed_result = self._parse_audio_result(result)
            
            if parsed_result:
                logger.success("✅ Áudio analisado com sucesso!")
                return parsed_result
            else:
                logger.warning("⚠️ Não foi possível extrair dados do áudio")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao analisar áudio: {e}")
            # Tentar fallback com OpenAI se disponível
            if self.fallback_model and self.config.enable_fallback:
                logger.info("Tentando análise de áudio com OpenAI...")
                return await self._analyze_audio_with_openai(audio_data, analysis_prompt)
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
            logger.info("🏗️ Criando objeto Image do AGnO...")
            
            # Importar validador
            from utils.image_validator import ImageValidator
            
            # Se já é um objeto Image, retornar
            if isinstance(image_data, Image):
                logger.info("✅ Dados já são um objeto Image AGnO")
                return image_data
            
            # Validar dados da imagem primeiro
            if isinstance(image_data, dict):
                logger.info(f"📦 Processando dict com keys: {list(image_data.keys())}")
                
                # IMPORTANTE: Priorizar conteúdo binário/base64 sobre URL
                # URLs do WhatsApp exigem autenticação e não funcionam com APIs externas
                
                # 1. Tentar usar conteúdo binário direto primeiro
                if 'content' in image_data and image_data['content']:
                    logger.info("🔄 Usando conteúdo binário direto")
                    try:
                        content = image_data['content']
                        
                        # Validar que é bytes real e não string
                        if isinstance(content, str):
                            logger.warning("⚠️ Content é string, convertendo para bytes")
                            try:
                                # Tentar decodificar como base64 primeiro
                                content = base64.b64decode(content)
                                logger.info("✅ String era base64, decodificada com sucesso")
                            except:
                                # Se não for base64, tentar como bytes diretos
                                content = content.encode('latin-1')
                                logger.info("✅ String convertida para bytes (latin-1)")
                        
                        # Validar tamanho mínimo
                        if len(content) < 100:
                            logger.error(f"❌ Conteúdo muito pequeno: {len(content)} bytes")
                            return None
                        
                        logger.info(f"📦 Conteúdo binário válido: {len(content)} bytes")
                        
                        # Corrigir orientação se necessário
                        img_bytes = ImageValidator.fix_image_orientation(content)
                        return Image(content=img_bytes)
                    except Exception as e:
                        logger.error(f"Erro ao processar conteúdo binário: {e}")
                
                # 2. Tentar usar base64
                if 'base64' in image_data and image_data['base64']:
                    logger.info("🔄 Usando base64")
                    try:
                        img_bytes = base64.b64decode(image_data['base64'])
                        # Corrigir orientação se necessário
                        img_bytes = ImageValidator.fix_image_orientation(img_bytes)
                        return Image(content=img_bytes)
                    except Exception as e:
                        logger.error(f"Erro ao decodificar base64: {e}")
                
                # 3. Tentar ler de arquivo
                if 'path' in image_data and image_data['path']:
                    logger.info("🔄 Lendo de arquivo")
                    try:
                        with open(image_data['path'], 'rb') as f:
                            img_bytes = f.read()
                        # Corrigir orientação se necessário
                        img_bytes = ImageValidator.fix_image_orientation(img_bytes)
                        return Image(content=img_bytes)
                    except Exception as e:
                        logger.error(f"Erro ao ler arquivo de imagem: {e}")
                
                # 4. URL como última opção (provavelmente falhará com URLs do WhatsApp)
                if 'url' in image_data and image_data['url']:
                    logger.warning("⚠️ Tentando usar URL diretamente (pode falhar com URLs do WhatsApp)")
                    # Verificar se é URL do WhatsApp
                    if 'whatsapp.net' in image_data['url'] or 'mmg.whatsapp.net' in image_data['url']:
                        logger.error("❌ URLs do WhatsApp requerem autenticação e não funcionam diretamente com APIs de visão")
                        logger.info("💡 Use o conteúdo binário ou base64 ao invés da URL")
                        return None
                    return Image(url=image_data['url'])
                        
            elif isinstance(image_data, str):
                # String pode ser URL ou path
                if image_data.startswith('http'):
                    return Image(url=image_data)
                else:
                    # Validar se arquivo existe
                    import os
                    if os.path.exists(image_data):
                        try:
                            with open(image_data, 'rb') as f:
                                img_bytes = f.read()
                            img_bytes = ImageValidator.fix_image_orientation(img_bytes)
                            return Image(content=img_bytes)
                        except Exception as e:
                            logger.error(f"Erro ao ler arquivo: {e}")
                            return None
                    else:
                        logger.error(f"Arquivo não encontrado: {image_data}")
                        return None
            
            logger.error(f"Formato de imagem não reconhecido: {type(image_data)}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar Image AGnO: {e}")
            return None
    
    async def _create_agno_audio(self, audio_data: Any) -> Optional[Audio]:
        """Cria objeto Audio do AGnO a partir de diferentes formatos"""
        try:
            logger.info("🎵 Criando objeto Audio do AGnO...")
            
            # Se já é um objeto Audio, retornar
            if isinstance(audio_data, Audio):
                logger.info("✅ Dados já são um objeto Audio AGnO")
                return audio_data
            
            # Processar diferentes formatos
            if isinstance(audio_data, dict):
                logger.info(f"📦 Processando dict com keys: {list(audio_data.keys())}")
                
                # Verificar se é um objeto de metadados do WhatsApp
                if 'mediaKey' in audio_data or 'directPath' in audio_data:
                    logger.info("🔄 Detectado áudio do WhatsApp com metadados - baixando conteúdo via Evolution API...")
                    
                    # Usar Evolution API para baixar o áudio
                    try:
                        # Tentar baixar o áudio usando a mediaKey ou directPath
                        base64_content = None
                        
                        if audio_data.get('url'):
                            # Primeiro tentar a URL se disponível
                            logger.info(f"📥 Tentando baixar áudio via URL: {audio_data['url'][:50]}...")
                            base64_content = await evolution_api.get_media_base64(
                                url=audio_data['url'],
                                media_key=audio_data.get('mediaKey'),
                                direct_path=audio_data.get('directPath'),
                                mimetype=audio_data.get('mimetype', 'audio/ogg')
                            )
                        elif audio_data.get('mediaKey'):
                            # Tentar com mediaKey se URL não estiver disponível
                            logger.info("📥 Tentando baixar áudio via mediaKey...")
                            base64_content = await evolution_api.get_media_base64(
                                media_key=audio_data['mediaKey'],
                                direct_path=audio_data.get('directPath'),
                                mimetype=audio_data.get('mimetype', 'audio/ogg')
                            )
                        
                        if base64_content:
                            logger.success("✅ Áudio baixado com sucesso via Evolution API!")
                            audio_bytes = base64.b64decode(base64_content)
                            return Audio(content=audio_bytes)
                        else:
                            logger.error("❌ Não foi possível baixar o conteúdo do áudio")
                            return None
                            
                    except Exception as e:
                        logger.error(f"❌ Erro ao baixar áudio via Evolution API: {e}")
                        return None
                
                # Criar objeto Audio baseado no tipo
                elif 'url' in audio_data and audio_data['url']:
                    return Audio(url=audio_data['url'])
                elif 'base64' in audio_data:
                    try:
                        audio_bytes = base64.b64decode(audio_data['base64'])
                        return Audio(content=audio_bytes)
                    except Exception as e:
                        logger.error(f"Erro ao decodificar base64 do áudio: {e}")
                        return None
                elif 'path' in audio_data:
                    # Ler arquivo de áudio
                    try:
                        with open(audio_data['path'], 'rb') as f:
                            audio_bytes = f.read()
                        return Audio(content=audio_bytes)
                    except Exception as e:
                        logger.error(f"Erro ao ler arquivo de áudio: {e}")
                        return None
                        
            elif isinstance(audio_data, str):
                # String pode ser URL ou path
                if audio_data.startswith('http'):
                    return Audio(url=audio_data)
                else:
                    # Assumir que é um path
                    import os
                    if os.path.exists(audio_data):
                        with open(audio_data, 'rb') as f:
                            return Audio(content=f.read())
                    else:
                        logger.error(f"Arquivo de áudio não encontrado: {audio_data}")
                        return None
                        
            elif isinstance(audio_data, bytes):
                # Bytes diretos
                return Audio(content=audio_data)
            
            logger.error(f"Formato de áudio não suportado: {type(audio_data)}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar objeto Audio AGnO: {e}")
            return None
    
    def _parse_audio_result(self, result: Any) -> Optional[Dict[str, Any]]:
        """Parseia resultado da análise de áudio"""
        try:
            if not result:
                return None
            
            # Se já é um dict, retornar
            if isinstance(result, dict):
                return result
            
            # Converter para string se necessário
            result_str = str(result)
            
            # Tentar extrair JSON
            import re
            json_patterns = [
                r'\{[^{}]*\}',  # JSON simples
                r'\{.*?\}(?=\s*$)',  # JSON no final
                r'```json\s*(.*?)\s*```',  # JSON em markdown
                r'```\s*(.*?)\s*```',  # Código em markdown
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, result_str, re.DOTALL)
                if matches:
                    for match in matches:
                        try:
                            # Tentar parsear como JSON
                            parsed = json.loads(match)
                            # Adicionar transcrição se não existir
                            if 'transcription' not in parsed and result_str:
                                # Extrair texto antes do JSON como transcrição
                                text_before_json = result_str[:result_str.find(match)].strip()
                                if text_before_json:
                                    parsed['transcription'] = text_before_json
                            return parsed
                        except:
                            continue
            
            # Se não encontrou JSON, retornar como transcrição
            return {
                "transcription": result_str,
                "analysis_status": "partial",
                "_raw_response": result_str
            }
            
        except Exception as e:
            logger.error(f"Erro ao parsear resultado de áudio: {e}")
            return None
    
    async def _analyze_audio_with_openai(
        self,
        audio_data: Any,
        analysis_prompt: str
    ) -> Optional[Dict[str, Any]]:
        """Analisa áudio usando OpenAI como fallback"""
        try:
            # OpenAI atualmente não suporta áudio diretamente no GPT-4
            # Retornar mensagem apropriada
            logger.warning("OpenAI GPT-4.1-nano não suporta análise de áudio diretamente")
            return {
                "media_received": "audio",
                "analysis_status": "unsupported",
                "transcription": None,
                "user_message": "Poxa, ainda não consigo ouvir áudios! 🙉 Mas se você escrever, eu respondo super rápido! 💬",
                "_processed_by": "openai_fallback"
            }
            
        except Exception as e:
            logger.error(f"Erro no fallback de áudio: {e}")
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
        """Processa PDF usando capacidades nativas do Gemini 2.5 Pro"""
        try:
            logger.info("📄 Processamento de PDF iniciado - usando Gemini 2.5 Pro nativo")
            logger.debug(f"🔍 Dados recebidos para processamento: {list(pdf_data.keys())}")
            
            # Preparar conteúdo do PDF
            pdf_content = None
            temp_file_path = None
            
            try:
                # Primeiro tentar usar conteúdo binário se disponível
                if 'content' in pdf_data and pdf_data['content']:
                    logger.info("📦 Usando conteúdo binário direto do PDF")
                    pdf_content = pdf_data['content']
                    if isinstance(pdf_content, bytes):
                        logger.info(f"✅ Conteúdo binário recebido: {len(pdf_content)} bytes")
                    else:
                        logger.warning("⚠️ Conteúdo não é bytes, tentando converter...")
                        
                elif 'path' in pdf_data:
                    logger.info(f"📂 Processando PDF do caminho: {pdf_data['path']}")
                    if os.path.exists(pdf_data['path']):
                        with open(pdf_data['path'], 'rb') as f:
                            pdf_content = f.read()
                        logger.info(f"✅ PDF lido com sucesso: {len(pdf_content)} bytes")
                    else:
                        logger.error(f"❌ Arquivo PDF não encontrado: {pdf_data['path']}")
                        
                elif 'url' in pdf_data:
                    logger.info(f"🌐 Baixando PDF da URL: {pdf_data['url']}")
                    
                    # Se for URL do WhatsApp, tentar usar Evolution API
                    if 'whatsapp.net' in pdf_data['url']:
                        logger.info("📱 URL do WhatsApp detectada - usando Evolution API")
                        
                        if hasattr(evolution_api, 'get_media_base64'):
                            # Tentar obter mídia via Evolution API
                            media_data = await evolution_api.get_media_base64(
                                pdf_data.get('mediaKey', ''),
                                pdf_data.get('mimetype', 'application/pdf')
                            )
                            if media_data and 'base64' in media_data:
                                pdf_content = base64.b64decode(media_data['base64'])
                                logger.info(f"✅ PDF obtido via Evolution API: {len(pdf_content)} bytes")
                            else:
                                logger.warning("⚠️ Falha ao obter PDF via Evolution API")
                    
                    # Fallback: tentar download direto com aiohttp
                    if not pdf_content:
                        import aiohttp
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(pdf_data['url'], ssl=False) as response:
                                    pdf_content = await response.read()
                                    logger.info(f"✅ PDF baixado diretamente: {len(pdf_content)} bytes")
                        except Exception as e:
                            logger.error(f"❌ Erro ao baixar PDF: {e}")
                            
                elif 'base64' in pdf_data:
                    logger.info("🔐 Decodificando PDF de base64")
                    pdf_content = base64.b64decode(pdf_data['base64'])
                    
                if not pdf_content:
                    logger.error("❌ Não foi possível obter conteúdo do PDF")
                    raise ValueError("Conteúdo do PDF vazio")
                
                # Salvar temporariamente para processamento
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(pdf_content)
                    temp_file_path = tmp_file.name
                    logger.info(f"💾 PDF salvo temporariamente em: {temp_file_path}")
                
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

                logger.info("🤖 Criando agente para análise do PDF")
                
                # Criar agente temporário para análise
                vision_agent = Agent(
                    name="Analisador PDF Gemini",
                    description="Analisador de contas de luz em PDF",
                    instructions="Analise documentos e retorne APENAS JSON estruturado, sem texto adicional.",
                    model=self.model,  # Gemini 2.5 Pro
                    reasoning=False  # Desabilitar reasoning para resposta direta
                )
                
                # Processar PDF diretamente com Gemini
                # O Gemini 2.5 Pro suporta PDFs nativamente
                logger.info("🚀 Enviando PDF para análise com Gemini 2.5 Pro...")
                
                # Converter PDF em imagem se o processamento direto falhar
                try:
                    # Primeiro, tentar processar o PDF diretamente como arquivo
                    # Gemini pode processar PDFs, mas às vezes funciona melhor convertendo para imagem
                    result = await self._process_pdf_as_image_fallback(temp_file_path, analysis_prompt)
                    
                    if result:
                        logger.success("✅ PDF processado com sucesso!")
                        return result
                        
                except Exception as e:
                    logger.warning(f"⚠️ Processamento direto falhou: {e}")
                
            finally:
                # Limpar arquivo temporário
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.debug(f"🧹 Arquivo temporário removido: {temp_file_path}")
            
            # Se chegou aqui, o processamento falhou
            logger.warning("❌ Não foi possível processar o PDF")
            
            return {
                "media_received": "pdf",
                "analysis_status": "processing_failed",
                "suggestion": "Recebi o PDF! 📄 Mas tá um pouquinho pesado pra processar... Uma foto da conta funciona super bem também! Quer tentar? 📱",
                "fallback": "request_image",
                "_attempted_methods": ["gemini_native", "pdf_to_image_conversion"]
            }
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar PDF: {e}")
            return {
                "media_received": "pdf",
                "analysis_status": "error",
                "error": str(e),
                "suggestion": "Tive um probleminha ao abrir o PDF. 😅 Que tal enviar uma foto da conta? Assim consigo analisar na hora! 📱"
            }
    
    async def _process_pdf_as_image_fallback(self, pdf_path: str, analysis_prompt: str) -> Optional[Dict[str, Any]]:
        """Processa PDF convertendo para imagem como fallback"""
        try:
            logger.info("🔄 Tentando converter PDF para imagem...")
            
            # Tentar usar pdf2image se disponível
            try:
                from pdf2image import convert_from_path
                import tempfile
                import os
                
                # Converter primeira página para imagem
                logger.info("📸 Convertendo primeira página do PDF para imagem...")
                images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=200)
                
                if images:
                    # Salvar imagem temporariamente
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        images[0].save(tmp_file.name, 'JPEG', quality=95)
                        tmp_image_path = tmp_file.name
                        logger.info(f"✅ Imagem criada: {tmp_image_path}")
                    
                    # Processar como imagem
                    image_data = {'path': tmp_image_path}
                    result = await self._analyze_image_with_gemini(image_data, analysis_prompt)
                    
                    # Limpar arquivo temporário
                    os.unlink(tmp_image_path)
                    
                    if result:
                        logger.success("✅ PDF processado como imagem com sucesso!")
                        result['_processed_by'] = 'pdf2image_conversion'
                        result['_original_format'] = 'pdf'
                        return result
                        
            except ImportError:
                logger.warning("⚠️ pdf2image não está instalado")
                
                # Tentar alternativa com Pillow se disponível
                try:
                    from PIL import Image as PILImage
                    import fitz  # PyMuPDF
                    import tempfile
                    import os
                    
                    logger.info("📑 Tentando com PyMuPDF...")
                    
                    # Abrir PDF
                    pdf_document = fitz.open(pdf_path)
                    page = pdf_document[0]  # Primeira página
                    
                    # Renderizar página como imagem
                    mat = fitz.Matrix(2, 2)  # Zoom 2x para melhor qualidade
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Salvar como imagem
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        pix.save(tmp_file.name)
                        tmp_image_path = tmp_file.name
                        logger.info(f"✅ Imagem criada com PyMuPDF: {tmp_image_path}")
                    
                    pdf_document.close()
                    
                    # Processar como imagem
                    image_data = {'path': tmp_image_path}
                    result = await self._analyze_image_with_gemini(image_data, analysis_prompt)
                    
                    # Limpar arquivo temporário
                    os.unlink(tmp_image_path)
                    
                    if result:
                        logger.success("✅ PDF processado com PyMuPDF!")
                        result['_processed_by'] = 'pymupdf_conversion'
                        result['_original_format'] = 'pdf'
                        return result
                        
                except ImportError:
                    logger.warning("⚠️ PyMuPDF também não está disponível")
                    
        except Exception as e:
            logger.error(f"❌ Erro no fallback de conversão: {e}")
            
        return None
    
    
    def _get_fallback_response(self) -> str:
        """Resposta de fallback em caso de erro"""
        import random
        responses = [
            "Opa, acho que me confundi um pouquinho aqui 😅 Pode repetir? Prometo prestar mais atenção!",
            "Hmm, não entendi direito... 🤔 Pode me explicar de outro jeito? Às vezes sou meio lerda!",
            "Desculpa, tive uma pequena confusão aqui! Vamos tentar de novo? 💫",
            "Eita, me perdi! 😄 Pode repetir pra mim? Juro que agora vai!",
            "Xi, deu um branco aqui! 🙈 Me conta de novo que eu prometo caprichar na resposta!"
        ]
        return random.choice(responses)
    
    def _get_error_response(self) -> str:
        """Resposta de erro genérica"""
        import random
        responses = [
            "Opa! Precisei dar uma paradinha técnica aqui 🛠️ Mas já, já volto! Você pode tentar de novo em alguns segundinhos?",
            "Ih, o sistema deu uma travadinha... 😅 Que tal a gente tentar de novo daqui a pouquinho? Prometo que vai funcionar!",
            "Puxa, tô com uma lentidão aqui! 🐌 Me dá um minutinho que já volto turbinada pra te ajudar!",
            "Ops, preciso de um segundinho pra organizar as coisas aqui! ⏰ Tenta de novo rapidinho?",
            "Eita, deu uma engasgada no sistema! 🤖 Mas relaxa, daqui a pouco tá tudo funcionando de novo!"
        ]
        return random.choice(responses)
    
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
    
    async def _update_kommo_on_stage_change(
        self,
        phone_number: str,
        old_stage: str,
        new_stage: str,
        session_state: Dict[str, Any],
        analysis: Dict[str, Any]
    ):
        """Atualiza Kommo CRM quando o estágio do lead muda"""
        try:
            lead_info = session_state.get("lead_info", {})
            
            # Mapear estágios do bot para status do Kommo
            stage_to_status = {
                "INITIAL_CONTACT": LeadStatus.NEW,
                "IDENTIFICATION": LeadStatus.NEW,
                "DISCOVERY": LeadStatus.IN_QUALIFICATION,
                "QUALIFICATION": LeadStatus.QUALIFIED,
                "OBJECTION_HANDLING": LeadStatus.IN_QUALIFICATION,
                "SCHEDULING": LeadStatus.MEETING_SCHEDULED
            }
            
            # Preparar dados do lead
            kommo_lead = KommoLead(
                name=lead_info.get("name", f"Lead WhatsApp {phone_number[-4:]}"),
                phone=phone_number,
                whatsapp=phone_number,
                email=lead_info.get("email"),
                qualification_score=self._calculate_qualification_score(lead_info, session_state),
                ai_notes=f"Estágio: {new_stage}\n{analysis.get('summary', '')}",
                tags=["WhatsApp Lead", f"Estágio: {new_stage}", "WhatsApp AI"]
            )
            
            # Adicionar informações específicas por estágio
            if new_stage == "DISCOVERY" and lead_info.get("solution_type"):
                kommo_lead.solution_type = self._map_solution_type(lead_info["solution_type"])
                kommo_lead.tags.append(f"Solução: {lead_info['solution_type']}")
            
            # Sempre adicionar valor da conta se disponível
            if lead_info.get("bill_value"):
                kommo_lead.energy_bill_value = lead_info["bill_value"]
                kommo_lead.tags.append(f"Conta: R$ {lead_info['bill_value']}")
            
            # Verificar se já existe lead
            existing_lead = await self.kommo_service.find_lead_by_whatsapp(phone_number)
            
            if existing_lead:
                # Atualizar lead existente
                lead_id = existing_lead["id"]
                await self.kommo_service.update_lead(lead_id, kommo_lead)
                
                # Mover para novo estágio se necessário
                if new_stage != old_stage:
                    await self.kommo_service.move_lead_stage(
                        lead_id, 
                        stage_to_status.get(new_stage, LeadStatus.NEW)
                    )
                    
                logger.info(f"✅ Lead {lead_id} atualizado no Kommo - Estágio: {new_stage}")
            else:
                # Criar novo lead
                if new_stage in ["IDENTIFICATION", "DISCOVERY", "QUALIFICATION"]:
                    result = await self.kommo_service.create_lead(kommo_lead)
                    if result:
                        logger.info(f"✅ Novo lead criado no Kommo: {result.get('id')} - {kommo_lead.name}")
                        # Salvar ID do Kommo no session_state
                        session_state["kommo_lead_id"] = result.get("id")
                        
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar Kommo: {e}")
            # Não falhar a conversa por erro no Kommo
    
    def _map_solution_type(self, solution_type: str) -> SolutionType:
        """Mapeia tipo de solução do bot para enum do Kommo"""
        mapping = {
            "usina própria": SolutionType.USINA_PROPRIA,
            "usina parceira": SolutionType.USINA_PARCEIRA,
            "consórcio": SolutionType.CONSORCIO,
            "instalação residencial": SolutionType.INSTALACAO_RESIDENCIAL,
            "instalação comercial": SolutionType.INSTALACAO_COMERCIAL
        }
        return mapping.get(solution_type.lower(), SolutionType.USINA_PROPRIA)
    
    async def _get_available_meeting_times(self, date: datetime = None) -> List[Dict[str, Any]]:
        """Busca horários disponíveis no Google Calendar"""
        try:
            if not self.calendar_service:
                logger.warning("Google Calendar não disponível")
                return []
            
            # Se não foi fornecida data, usar próximo dia útil
            if not date:
                date = datetime.now()
                # Avançar para próximo dia útil se for fim de semana
                while date.weekday() >= 5:  # Sábado = 5, Domingo = 6
                    date += timedelta(days=1)
                # Se já passou das 17h, usar próximo dia útil
                if date.hour >= 17:
                    date += timedelta(days=1)
                    while date.weekday() >= 5:
                        date += timedelta(days=1)
            
            # Buscar horários disponíveis (9h às 18h)
            available_slots = await self.calendar_service.check_availability(
                date=date,
                duration_minutes=30,  # Reuniões de 30 minutos
                work_hours=(9, 18)    # Horário comercial
            )
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Erro ao buscar horários disponíveis: {e}")
            return []
    
    async def _suggest_available_times(self, date: datetime = None) -> str:
        """Formata e sugere horários disponíveis para o usuário"""
        try:
            available_slots = await self._get_available_meeting_times(date)
            
            if not available_slots:
                return "No momento não encontrei horários disponíveis. Que tal tentarmos outro dia?"
            
            # Formatar mensagem com horários disponíveis
            message = "🗓️ *Horários disponíveis para nossa reunião:*\n\n"
            
            # Agrupar por dia
            slots_by_day = {}
            for slot in available_slots[:10]:  # Limitar a 10 opções
                day = slot['datetime'][:10]
                if day not in slots_by_day:
                    slots_by_day[day] = []
                slots_by_day[day].append(slot)
            
            # Formatar por dia
            for day, day_slots in slots_by_day.items():
                date_obj = datetime.fromisoformat(day)
                day_name = date_obj.strftime('%A, %d/%m')
                message += f"*{day_name}:*\n"
                
                for slot in day_slots:
                    message += f"• {slot['start']} às {slot['end']}\n"
                
                message += "\n"
            
            message += "Por favor, escolha o horário que melhor se adequa à sua agenda! 😊"
            
            return message
            
        except Exception as e:
            logger.error(f"Erro ao sugerir horários: {e}")
            return "Desculpe, tive um problema ao buscar os horários. Vamos marcar manualmente?"
    
    async def _reschedule_meeting(self, event_id: str, new_datetime: datetime, session_state: Dict[str, Any]) -> bool:
        """Reagenda uma reunião existente"""
        try:
            if not self.calendar_service or not event_id:
                return False
            
            # Calcular novo fim
            new_end = new_datetime + timedelta(minutes=30)
            
            # Atualizar evento
            result = await self.calendar_service.update_event(
                event_id=event_id,
                updates={
                    'start_datetime': new_datetime,
                    'end_datetime': new_end
                }
            )
            
            if result:
                # Atualizar session_state
                session_state["meeting_datetime"] = new_datetime.isoformat()
                logger.info(f"✅ Reunião reagendada para {new_datetime}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao reagendar reunião: {e}")
            return False
    
    async def _try_schedule_meeting(self, lead_info: Dict[str, Any], session_state: Dict[str, Any], message: str):
        """Tenta agendar reunião no Google Calendar quando houver horário escolhido"""
        try:
            # Verificar se a mensagem contém informação de horário
            import re
            from datetime import datetime, timedelta
            
            # Padrões para detectar horários
            time_patterns = [
                r'(\d{1,2})(?:h|:)?(\d{2})?\s*(?:horas?)?',  # 15h, 15:30, 15h30
                r'às\s*(\d{1,2})(?:h|:)?(\d{2})?',           # às 15h, às 15:30
                r'(\d{1,2})\s*(?:da\s*)?(manhã|tarde|noite)'  # 9 da manhã, 3 da tarde
            ]
            
            # Padrões para detectar dias
            day_patterns = {
                'hoje': 0,
                'amanhã': 1,
                'depois de amanhã': 2,
                'segunda': 'monday',
                'terça': 'tuesday',
                'quarta': 'wednesday',
                'quinta': 'thursday',
                'sexta': 'friday'
            }
            
            # Tentar extrair horário
            meeting_time = None
            for pattern in time_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                    
                    # Ajustar para período do dia se necessário
                    if len(match.groups()) > 2 and match.group(3):
                        period = match.group(3)
                        if period == 'tarde' and hour < 12:
                            hour += 12
                        elif period == 'noite' and hour < 12:
                            hour += 12
                    
                    meeting_time = (hour, minute)
                    break
            
            if not meeting_time:
                logger.info("Horário não detectado na mensagem, aguardando escolha clara")
                return
            
            # Determinar dia
            meeting_date = datetime.now()
            for day_word, day_value in day_patterns.items():
                if day_word in message.lower():
                    if isinstance(day_value, int):
                        meeting_date += timedelta(days=day_value)
                    else:
                        # Calcular próximo dia da semana
                        days_ahead = 0
                        target_day = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].index(day_value)
                        current_day = meeting_date.weekday()
                        days_ahead = (target_day - current_day) % 7
                        if days_ahead == 0:
                            days_ahead = 7  # Próxima semana
                        meeting_date += timedelta(days=days_ahead)
                    break
            
            # Criar datetime completo
            hour, minute = meeting_time
            meeting_datetime = meeting_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Verificar se é horário comercial
            if not (9 <= hour <= 18):
                logger.warning(f"Horário fora do expediente: {hour}h")
                return
            
            # Criar reunião no Google Calendar
            event_data = {
                'summary': f'Apresentação SolarPrime - {lead_info.get("name", "Lead WhatsApp")}',
                'description': f"""
                Reunião de apresentação da solução SolarPrime
                
                Lead: {lead_info.get("name", "N/A")}
                Telefone: {lead_info.get("phone", "N/A")}
                Email: {lead_info.get("email", "N/A")}
                Valor da conta: {lead_info.get("bill_value", "N/A")}
                Tipo de solução: {lead_info.get("solution_type", "A definir")}
                
                Agendado via WhatsApp AI
                """,
                'start': meeting_datetime,
                'duration': 30,  # 30 minutos
                'attendees': [lead_info.get("email")],
                'location': 'Online - Link será enviado por WhatsApp'
            }
            
            # Criar evento no Google Calendar se disponível
            if self.calendar_service:
                # Calcular duração
                end_datetime = meeting_datetime + timedelta(minutes=event_data.get('duration', 30))
                
                # Chamar create_event com argumentos corretos
                result = await self.calendar_service.create_event(
                    title=event_data['title'],
                    start_datetime=event_data['start'],
                    end_datetime=end_datetime,
                    description=event_data.get('description'),
                    location=event_data.get('location'),
                    attendees=event_data.get('attendees', []),
                    lead_data=lead_info
                )
                
                if result and result.get('link'):
                    logger.info(f"✅ Reunião criada no Google Calendar: {result['link']}")
                    
                    # Salvar link no session_state
                    session_state["meeting_link"] = result['link']
                    session_state["meeting_datetime"] = meeting_datetime.isoformat()
                    session_state["meeting_event_id"] = result.get('id')  # Para futuro reagendamento
            else:
                logger.info("ℹ️ Google Calendar não disponível - reunião será gerenciada manualmente")
                # Salvar informações básicas da reunião
                session_state["meeting_datetime"] = meeting_datetime.isoformat()
                session_state["meeting_scheduled"] = True
                
                # Atualizar Kommo com link da reunião
                if self.kommo_service and session_state.get("kommo_lead_id") and result:
                    await self.kommo_service.add_note(
                        session_state["kommo_lead_id"],
                        f"Reunião agendada para {meeting_datetime.strftime('%d/%m/%Y às %H:%M')}\n"
                        f"Link do Calendar: {result.get('link', 'Link não disponível')}"
                    )
                    
                    # Adicionar link como campo customizado se disponível
                    if hasattr(self.kommo_service, 'update_custom_field') and result.get('link'):
                        await self.kommo_service.update_custom_field(
                            session_state["kommo_lead_id"],
                            "google_calendar_link",
                            result['link']
                        )
                
        except Exception as e:
            logger.error(f"❌ Erro ao agendar reunião no Calendar: {e}")
            # Não falhar a conversa por erro no Calendar


# Função helper para criar agente
def create_sdr_agent() -> SDRAgent:
    """Cria e retorna uma instância do agente SDR"""
    return SDRAgent()


# Exporta componentes
__all__ = ["SDRAgent", "create_sdr_agent"]