"""
Intelligent Follow-up Workflow
==============================
Sistema de follow-up inteligente com contexto completo usando AGnO Framework
"""

from typing import Dict, Any, Optional, List, Iterator
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from agno.workflow import Workflow, RunResponse
from agno.agent import Agent, AgentMemory
from agno.models.google import Gemini
from agno.storage.agent.sqlite import SqliteAgentStorage

from services.database import supabase_client
from services.evolution_api import evolution_client
from repositories.lead_repository import lead_repository
from repositories.message_repository import message_repository
from repositories.conversation_repository import conversation_repository
from config.config import config
from config.agent_config import config as agent_config

# Executor para rodar funções assíncronas em threads separadas
executor = ThreadPoolExecutor(max_workers=1)


def run_async(coro):
    """Executa uma coroutine de forma síncrona"""
    loop = None
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    else:
        future = executor.submit(asyncio.run, coro)
        return future.result()


# Templates inteligentes baseados em padrões
INTELLIGENT_FOLLOW_UP_TEMPLATES = {
    "abandoned_quotation": {
        "pattern": "usuário pediu simulação mas não respondeu",
        "keywords": ["simulação", "calcular", "economia"],
        "template": """
        Crie um follow-up para {name} que pediu uma simulação de economia.
        Contexto: {context}
        
        Mencione:
        1. Que você já preparou os números que ele pediu
        2. Um benefício específico baseado no que ele mencionou
        3. Crie urgência suave mencionando promoção ou benefício temporal
        """
    },
    "objection_price": {
        "pattern": "usuário mencionou preço alto ou custo",
        "keywords": ["caro", "preço", "custo", "não tenho dinheiro"],
        "template": """
        Crie um follow-up para {name} que demonstrou preocupação com o investimento.
        Contexto: {context}
        
        Aborde:
        1. Uma forma de reduzir o investimento inicial
        2. Mencione o retorno sobre investimento
        3. Ofereça uma alternativa ou facilidade
        """
    },
    "technical_questions": {
        "pattern": "usuário fez perguntas técnicas",
        "keywords": ["como funciona", "instalação", "manutenção", "garantia"],
        "template": """
        Crie um follow-up para {name} que tem dúvidas técnicas.
        Contexto: {context}
        Perguntas não respondidas: {unanswered_questions}
        
        Responda:
        1. A principal dúvida técnica dele
        2. Ofereça material ou visita técnica
        3. Transmita confiança e expertise
        """
    },
    "high_engagement": {
        "pattern": "usuário muito engajado mas não avançou",
        "keywords": ["interesse", "legal", "quero"],
        "template": """
        Crie um follow-up para {name} que demonstrou alto interesse.
        Contexto: {context}
        Tópicos de interesse: {topics}
        
        Foque em:
        1. Relembrar o benefício que mais chamou atenção dele
        2. Criar um próximo passo concreto e fácil
        3. Demonstrar que você lembra da conversa específica
        """
    },
    "generic_reengagement": {
        "pattern": "reengajamento genérico",
        "keywords": [],
        "template": """
        Crie um follow-up de reengajamento para {name}.
        Contexto resumido: {context}
        Último tópico discutido: {last_topic}
        
        Seja:
        1. Breve e amigável
        2. Mencione algo específico da última conversa
        3. Ofereça um benefício novo ou informação relevante
        """
    }
}


class IntelligentFollowUpWorkflow(Workflow):
    """Workflow de follow-up inteligente com contexto completo"""
    
    def __init__(self):
        super().__init__(
            name="intelligent_follow_up_workflow",
            description="Sistema inteligente de follow-up com análise profunda de contexto"
        )
        
        # Storage persistente para memórias
        self.storage = SqliteAgentStorage(
            table_name="follow_up_memories",
            db_file="follow_up_memory.db"
        )
        
        # Modelo principal para análise e geração
        self.model = Gemini(
            id="gemini-2.0-flash-exp",  # Modelo rápido e eficiente
            api_key=config.gemini.api_key,
            temperature=0.7
        )
        
        # Agente com memória completa
        self.intelligent_agent = Agent(
            name="IntelligentFollowUpLuna",
            model=self.model,
            reasoning=True,  # Ativar reasoning para análise profunda
            memory=AgentMemory(
                role="Você é Luna da SolarPrime, especialista em follow-ups personalizados.",
                instructions="""
                Você tem acesso ao histórico COMPLETO das conversas e deve usar isso para criar
                follow-ups altamente personalizados. 
                
                Regras importantes:
                1. SEMPRE mencione algo específico da conversa anterior
                2. Seja MUITO breve (máximo 3 frases)
                3. Use linguagem natural e amigável
                4. Crie urgência suave quando apropriado
                5. Sempre ofereça valor (dica, benefício, informação nova)
                6. Use emojis com moderação (máximo 1-2)
                7. NUNCA seja genérico - cada mensagem deve ser única
                """
            ),
            storage=self.storage,
            user_id="system",
            add_history_to_messages=True,
            num_history_responses=10,  # Últimas 10 interações do agente
            enable_agentic_memory=True,  # Memórias persistentes
            markdown=False
        )
        
        # Agente analisador de contexto
        self.context_analyzer = Agent(
            name="ContextAnalyzer",
            model=self.model,
            reasoning=True,
            memory=AgentMemory(
                role="Analisador especializado em conversas de vendas",
                instructions="""
                Analise conversas e identifique:
                1. Padrões de comportamento
                2. Objeções não resolvidas
                3. Pontos de interesse principal
                4. Melhor abordagem para follow-up
                5. Nível de interesse (0-10)
                """
            ),
            markdown=False
        )
        
        self.supabase = supabase_client
        
    def run(
        self,
        lead_id: str,
        follow_up_type: str,
        custom_message: Optional[str] = None
    ) -> Iterator[RunResponse]:
        """
        Executa workflow de follow-up inteligente
        
        Args:
            lead_id: ID do lead
            follow_up_type: Tipo de follow-up
            custom_message: Mensagem customizada opcional
            
        Returns:
            Iterator com status da execução
        """
        start_time = datetime.now()
        
        try:
            # Buscar dados do lead
            lead_data = run_async(self._get_enhanced_lead_data(lead_id))
            if not lead_data:
                yield RunResponse(
                    content={
                        'status': 'error',
                        'message': 'Lead não encontrado'
                    }
                )
                return
            
            # Verificar se deve fazer follow-up
            if not self._should_send_follow_up(lead_data, follow_up_type):
                yield RunResponse(
                    content={
                        'status': 'skipped',
                        'message': 'Follow-up não necessário',
                        'reason': lead_data.get('skip_reason')
                    }
                )
                return
            
            # Buscar contexto completo da conversa
            context = run_async(self._get_full_conversation_context(lead_data))
            
            # Analisar contexto para determinar melhor abordagem
            analysis = run_async(self._analyze_conversation_context(context))
            
            # Gerar mensagem personalizada
            if custom_message:
                message = custom_message
            else:
                message = run_async(self._generate_intelligent_message(
                    lead_data, 
                    follow_up_type, 
                    context, 
                    analysis
                ))
            
            # Enviar mensagem via WhatsApp
            send_result = run_async(self._send_whatsapp_message(
                lead_data['phone'], 
                message
            ))
            
            if send_result['success']:
                # Registrar follow-up enviado
                run_async(self._record_follow_up(
                    lead_id, 
                    follow_up_type, 
                    message,
                    analysis
                ))
                
                # Salvar memória da interação
                run_async(self._save_interaction_memory(lead_data, message, analysis))
                
                # Agendar próximo follow-up se necessário
                next_follow_up = run_async(self._schedule_intelligent_next_follow_up(
                    lead_id, 
                    follow_up_type,
                    analysis
                ))
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                yield RunResponse(
                    content={
                        'status': 'success',
                        'message': message,
                        'sent_at': datetime.now().isoformat(),
                        'next_follow_up': next_follow_up,
                        'execution_time': execution_time,
                        'analysis': analysis,
                        'context_used': {
                            'total_messages': context.get('total_messages', 0),
                            'patterns_found': len(context.get('patterns', {}).get('topics_discussed', [])),
                            'insights_extracted': len(context.get('insights', {}).get('objections', []))
                        }
                    }
                )
            else:
                yield RunResponse(
                    content={
                        'status': 'error',
                        'message': 'Erro ao enviar mensagem',
                        'error': send_result.get('error')
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro no workflow de follow-up inteligente: {e}", exc_info=True)
            yield RunResponse(
                content={
                    'status': 'error',
                    'message': str(e)
                }
            )
    
    async def _get_enhanced_lead_data(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca dados aprimorados do lead incluindo conversa"""
        try:
            # Buscar dados básicos do lead
            result = self.supabase.table('leads')\
                .select('*')\
                .eq('id', lead_id)\
                .single()\
                .execute()
            
            if not result.data:
                return None
            
            lead = result.data
            
            # Buscar telefone
            phone_number = lead.get('phone_number')
            
            if not phone_number and lead.get('profile_id'):
                profile_result = self.supabase.table('profiles')\
                    .select('phone')\
                    .eq('id', lead.get('profile_id'))\
                    .single()\
                    .execute()
                
                if profile_result.data:
                    phone_number = profile_result.data.get('phone')
            
            if not phone_number:
                logger.warning(f"Lead {lead_id} sem número de telefone")
                return None
            
            # Buscar ID da conversa
            conversation_id = None
            if lead.get('profile_id'):
                conv_result = self.supabase.table('conversations')\
                    .select('id')\
                    .eq('profile_id', lead.get('profile_id'))\
                    .order('created_at', desc=True)\
                    .limit(1)\
                    .execute()
                
                if conv_result.data:
                    conversation_id = conv_result.data[0]['id']
            
            return {
                'id': lead['id'],
                'name': lead['name'] or 'Cliente',
                'phone': phone_number,
                'stage': lead['current_stage'],
                'qualification_score': lead['qualification_score'],
                'last_interaction': lead['updated_at'],
                'property_type': lead.get('property_type'),
                'bill_value': lead.get('bill_value'),
                'conversation_id': conversation_id,
                'profile_id': lead.get('profile_id')
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do lead: {e}")
            return None
    
    async def _get_full_conversation_context(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Busca contexto completo da conversa"""
        if not lead_data.get('conversation_id'):
            return {
                'messages': [],
                'patterns': {},
                'insights': {},
                'summary': 'Sem histórico de conversa'
            }
        
        # Usar o novo método do message_repository
        context = await message_repository.get_full_conversation_context(
            lead_data['conversation_id'],
            limit=100,  # Últimas 100 mensagens
            include_media=True
        )
        
        return context
    
    async def _analyze_conversation_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa contexto da conversa com IA"""
        if not context.get('messages'):
            return {
                'recommended_approach': 'generic_reengagement',
                'interest_level': 5,
                'key_points': [],
                'best_time': 'now'
            }
        
        # Preparar contexto para análise
        conversation_text = "\n".join([
            f"{'Cliente' if msg.role == 'user' else 'Luna'}: {msg.content}"
            for msg in context['messages'][-20:]  # Últimas 20 para análise
            if msg.content
        ])
        
        analysis_prompt = f"""
        Analise esta conversa de vendas de energia solar:
        
        {conversation_text}
        
        Padrões identificados: {context['patterns']}
        Insights extraídos: {context['insights']}
        
        Responda em formato JSON:
        {{
            "interest_level": 0-10,
            "recommended_approach": "tipo de abordagem",
            "key_points": ["pontos importantes"],
            "unresolved_objections": ["objeções"],
            "best_angle": "melhor ângulo de abordagem",
            "urgency_level": "low/medium/high",
            "personalization_tips": ["dicas de personalização"]
        }}
        """
        
        response = await self.context_analyzer.arun(analysis_prompt)
        
        try:
            # Extrair JSON da resposta
            import json
            analysis = json.loads(response.content)
        except:
            # Fallback se não conseguir parsear
            analysis = {
                'recommended_approach': 'high_engagement',
                'interest_level': 7,
                'key_points': ['interesse demonstrado'],
                'best_angle': 'benefícios econômicos'
            }
        
        return analysis
    
    async def _generate_intelligent_message(
        self,
        lead_data: Dict[str, Any],
        follow_up_type: str,
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Gera mensagem de follow-up altamente personalizada"""
        
        # Selecionar template baseado na análise
        template_key = analysis.get('recommended_approach', 'generic_reengagement')
        template = INTELLIGENT_FOLLOW_UP_TEMPLATES.get(
            template_key,
            INTELLIGENT_FOLLOW_UP_TEMPLATES['generic_reengagement']
        )
        
        # Preparar contexto rico
        last_messages = context['messages'][-5:] if context.get('messages') else []
        recent_context = "\n".join([
            f"{'Cliente' if msg.role == 'user' else 'Luna'}: {msg.content[:100]}"
            for msg in last_messages
            if msg.content
        ])
        
        # Criar prompt personalizado
        personalized_prompt = template['template'].format(
            name=lead_data['name'],
            context=recent_context,
            topics=", ".join(context['patterns'].get('topics_discussed', [])),
            unanswered_questions="; ".join(context['insights'].get('questions_asked', [])[:3]),
            last_topic=context['patterns'].get('topics_discussed', ['energia solar'])[0] if context['patterns'].get('topics_discussed') else 'energia solar'
        )
        
        # Adicionar instruções extras baseadas na análise
        personalized_prompt += f"""
        
        Instruções adicionais baseadas na análise:
        - Nível de interesse: {analysis.get('interest_level', 5)}/10
        - Melhor ângulo: {analysis.get('best_angle', 'benefícios')}
        - Urgência: {analysis.get('urgency_level', 'medium')}
        - Personalização: {'; '.join(analysis.get('personalization_tips', [])[:2])}
        
        LEMBRE-SE: Máximo 3 frases, seja específico sobre a conversa anterior!
        """
        
        # Gerar mensagem com o agente inteligente
        response = await self.intelligent_agent.arun(personalized_prompt)
        
        # Extrair apenas o texto da resposta
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
    
    def _should_send_follow_up(self, lead_data: Dict[str, Any], follow_up_type: str) -> bool:
        """Verifica se deve enviar follow-up com regras inteligentes"""
        # Não fazer follow-up se já agendou reunião
        if lead_data['stage'] == 'SCHEDULED':
            lead_data['skip_reason'] = 'Lead já tem reunião agendada'
            return False
        
        # Verificar tempo desde última interação
        last_interaction = datetime.fromisoformat(lead_data['last_interaction'].replace('Z', '+00:00'))
        hours_since_last = (datetime.now(last_interaction.tzinfo) - last_interaction).total_seconds() / 3600
        minutes_since_last = hours_since_last * 60
        
        # Usar configurações
        first_delay_minutes = agent_config.follow_up_delay_minutes
        second_delay_hours = agent_config.follow_up_second_delay_hours
        
        # Regras por tipo de follow-up
        if follow_up_type == 'reminder' and minutes_since_last < first_delay_minutes:
            lead_data['skip_reason'] = f'Muito cedo para primeiro follow-up (aguardar {first_delay_minutes} minutos)'
            return False
        
        if follow_up_type == 'check_in' and hours_since_last < second_delay_hours:
            lead_data['skip_reason'] = f'Muito cedo para segundo follow-up (aguardar {second_delay_hours} horas)'
            return False
        
        if follow_up_type == 'reengagement' and hours_since_last < 72:
            lead_data['skip_reason'] = 'Muito cedo para reengajamento'
            return False
        
        return True
    
    async def _send_whatsapp_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Envia mensagem via WhatsApp"""
        try:
            result = await evolution_client.send_text_message(
                phone=phone,
                message=message
            )
            
            return {
                'success': True,
                'message_id': result.get('key', {}).get('id')
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _record_follow_up(
        self,
        lead_id: str,
        follow_up_type: str,
        message: str,
        analysis: Dict[str, Any]
    ):
        """Registra follow-up enviado com análise"""
        try:
            self.supabase.table('follow_ups').insert({
                'lead_id': lead_id,
                'type': follow_up_type,
                'message': message,
                'status': 'executed',
                'executed_at': datetime.now().isoformat(),
                'scheduled_at': datetime.now().isoformat(),
                'metadata': {
                    'analysis': analysis,
                    'interest_level': analysis.get('interest_level', 0),
                    'approach_used': analysis.get('recommended_approach', 'generic')
                }
            }).execute()
            
        except Exception as e:
            logger.error(f"Erro ao registrar follow-up: {e}")
    
    async def _save_interaction_memory(
        self,
        lead_data: Dict[str, Any],
        message: str,
        analysis: Dict[str, Any]
    ):
        """Salva memória da interação para aprendizado"""
        try:
            # Salvar memória no agente
            memory_content = f"""
            Lead: {lead_data['name']}
            Stage: {lead_data['stage']}
            Interest Level: {analysis.get('interest_level', 0)}/10
            Approach Used: {analysis.get('recommended_approach', 'generic')}
            Message Sent: {message}
            Key Points: {', '.join(analysis.get('key_points', []))}
            """
            
            # O agente salvará automaticamente na storage SQLite
            await self.intelligent_agent.memory.add(
                memory_content,
                metadata={
                    'lead_id': lead_data['id'],
                    'timestamp': datetime.now().isoformat(),
                    'type': 'follow_up_sent'
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
    
    async def _schedule_intelligent_next_follow_up(
        self,
        lead_id: str,
        current_type: str,
        analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Agenda próximo follow-up baseado em análise"""
        
        # Ajustar timing baseado no nível de interesse
        interest_level = analysis.get('interest_level', 5)
        
        # Se interesse alto, follow-ups mais frequentes
        if interest_level >= 8:
            hour_multiplier = 0.5  # Metade do tempo
        elif interest_level >= 6:
            hour_multiplier = 0.75
        else:
            hour_multiplier = 1.0
        
        # Sequência inteligente de follow-ups
        sequence = {
            'reminder': ('check_in', int(24 * hour_multiplier)),
            'check_in': ('reengagement', int(48 * hour_multiplier)),
            'reengagement': ('nurture', int(72 * hour_multiplier)),
        }
        
        if current_type in sequence:
            next_type, hours = sequence[current_type]
            scheduled_time = datetime.now() + timedelta(hours=hours)
            
            try:
                result = self.supabase.table('follow_ups').insert({
                    'lead_id': lead_id,
                    'type': next_type,
                    'scheduled_at': scheduled_time.isoformat(),
                    'status': 'pending',
                    'metadata': {
                        'previous_interest_level': interest_level,
                        'scheduling_reason': f'Based on interest level {interest_level}/10'
                    }
                }).execute()
                
                return {
                    'type': next_type,
                    'scheduled_at': scheduled_time.isoformat(),
                    'hours_until': hours,
                    'reason': f'Agendado baseado no interesse ({interest_level}/10)'
                }
                
            except Exception as e:
                logger.error(f"Erro ao agendar próximo follow-up: {e}")
                
        return None


# Exportar classe para uso
__all__ = ['IntelligentFollowUpWorkflow']