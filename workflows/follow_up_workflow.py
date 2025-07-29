"""
Follow-up Workflow
==================
Sistema de follow-up automático usando AGnO Workflows
"""

from typing import Dict, Any, Optional, List, Iterator
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from agno.workflow import Workflow, RunResponse
from agno.agent import Agent, AgentMemory
from agno.models.google import Gemini

from services.database import supabase_client
from services.evolution_api import evolution_client
from repositories.lead_repository import lead_repository
from config.config import config
from config.agent_config import config as agent_config

# Executor para rodar funções assíncronas em threads separadas
executor = ThreadPoolExecutor(max_workers=1)


def run_async(coro):
    """Executa uma coroutine de forma síncrona"""
    loop = None
    try:
        # Tentar pegar o loop existente
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Se não houver loop, criar um novo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    else:
        # Se já existe um loop rodando, usar thread separada
        future = executor.submit(asyncio.run, coro)
        return future.result()


class FollowUpWorkflow(Workflow):
    """Workflow de follow-up automático com AGnO"""
    
    def __init__(self):
        super().__init__(
            name="follow_up_workflow",
            description="Sistema automatizado de follow-up para leads"
        )
        
        # Modelo rápido para follow-ups
        self.model = Gemini(
            id="gemini-2.5-flash",  # Modelo mais rápido para follow-ups simples
            api_key=config.gemini.api_key,
            temperature=0.7
        )
        
        # Agente especializado em follow-up
        self.follow_up_agent = Agent(
            name="FollowUpLuna",
            model=self.model,
            reasoning=False,  # Sem reasoning para velocidade
            memory=AgentMemory(
                role="Você é Luna da SolarPrime, fazendo follow-up com leads interessados.",
                instructions="""Regras para follow-up:
                1. Seja MUITO breve (máximo 2 frases)
                2. Seja amigável e não invasiva
                3. Foque em reengajar o lead
                4. Sempre ofereça valor (dica, informação, benefício)"""
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
        Executa workflow de follow-up
        
        Args:
            lead_id: ID do lead
            follow_up_type: Tipo de follow-up (first_contact, reminder, reengagement, etc.)
            custom_message: Mensagem customizada opcional
            
        Returns:
            Status da execução
        """
        start_time = datetime.now()
        
        try:
            # Buscar dados do lead
            lead_data = run_async(self._get_lead_data(lead_id))
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
                
            # Gerar mensagem personalizada
            if custom_message:
                message = custom_message
            else:
                message = run_async(self._generate_follow_up_message(lead_data, follow_up_type))
                
            # Enviar mensagem via WhatsApp
            send_result = run_async(self._send_whatsapp_message(lead_data['phone'], message))
            
            if send_result['success']:
                # Registrar follow-up enviado
                run_async(self._record_follow_up(lead_id, follow_up_type, message))
                
                # Agendar próximo follow-up se necessário
                next_follow_up = run_async(self._schedule_next_follow_up(lead_id, follow_up_type))
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                yield RunResponse(
                    content={
                        'status': 'success',
                        'message': message,
                        'sent_at': datetime.now().isoformat(),
                        'next_follow_up': next_follow_up,
                        'execution_time': execution_time
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
            logger.error(f"Erro no workflow de follow-up: {e}", exc_info=True)
            yield RunResponse(
                content={
                    'status': 'error',
                    'message': str(e)
                }
            )
            
    async def _get_lead_data(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca dados completos do lead"""
        try:
            # Buscar do Supabase
            result = self.supabase.table('leads')\
                .select('*')\
                .eq('id', lead_id)\
                .single()\
                .execute()
                
            if result.data:
                lead = result.data
                # Buscar profile separadamente se necessário
                profile_result = self.supabase.table('profiles')\
                    .select('phone')\
                    .eq('id', lead.get('profile_id'))\
                    .single()\
                    .execute()
                    
                phone_number = lead.get('phone_number') or (profile_result.data.get('phone') if profile_result.data else None)
                
                return {
                    'id': lead['id'],
                    'name': lead['name'] or 'Cliente',
                    'phone': phone_number,
                    'stage': lead['current_stage'],
                    'qualification_score': lead['qualification_score'],
                    'last_interaction': lead['updated_at'],
                    'property_type': lead.get('property_type'),
                    'bill_value': lead.get('bill_value')
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do lead: {e}")
            return None
            
    def _should_send_follow_up(self, lead_data: Dict[str, Any], follow_up_type: str) -> bool:
        """Verifica se deve enviar follow-up"""
        # Não fazer follow-up se já agendou reunião
        if lead_data['stage'] == 'SCHEDULED':
            lead_data['skip_reason'] = 'Lead já tem reunião agendada'
            return False
            
        # Verificar tempo desde última interação
        last_interaction = datetime.fromisoformat(lead_data['last_interaction'].replace('Z', '+00:00'))
        hours_since_last = (datetime.now(last_interaction.tzinfo) - last_interaction).total_seconds() / 3600
        minutes_since_last = hours_since_last * 60
        
        # Usar configurações do config
        first_delay_minutes = agent_config.follow_up_delay_minutes  # 30 minutos
        second_delay_hours = agent_config.follow_up_second_delay_hours  # 24 horas
        
        # Regras por tipo de follow-up usando configurações
        # Para reminder (primeiro follow-up) - usar minutos
        if follow_up_type == 'reminder' and minutes_since_last < first_delay_minutes:
            lead_data['skip_reason'] = f'Muito cedo para primeiro follow-up (aguardar {first_delay_minutes} minutos)'
            return False
            
        # Para check_in (segundo follow-up) - usar horas
        if follow_up_type == 'check_in' and hours_since_last < second_delay_hours:
            lead_data['skip_reason'] = f'Muito cedo para segundo follow-up (aguardar {second_delay_hours} horas)'
            return False
            
        if follow_up_type == 'reengagement' and hours_since_last < 72:
            lead_data['skip_reason'] = 'Muito cedo para reengajamento'
            return False
            
        return True
        
    async def _generate_follow_up_message(self, lead_data: Dict[str, Any], follow_up_type: str) -> str:
        """Gera mensagem de follow-up personalizada"""
        # Contexto para o agente
        context = f"""
        Lead: {lead_data['name']}
        Estágio: {lead_data['stage']}
        Score: {lead_data['qualification_score']}
        Tipo de follow-up: {follow_up_type}
        """
        
        # Prompts específicos por tipo
        prompts = {
            'reminder': f"Crie um follow-up amigável para {lead_data['name']} que demonstrou interesse inicial. Mencione economia de energia.",
            'check_in': f"Lembre {lead_data['name']} sobre a oportunidade de economizar na conta de luz. Seja gentil e não invasiva.",
            'reengagement': f"Reengaje {lead_data['name']} que parou de responder. Ofereça uma informação nova ou benefício.",
            'nurture': f"Envie uma mensagem educativa para {lead_data['name']} sobre benefícios da energia solar."
        }
        
        prompt = prompts.get(follow_up_type, prompts['reminder'])
        
        # Gerar mensagem com o agente
        response = await self.follow_up_agent.arun(prompt + "\n\nContexto: " + context)
        
        # Extrair apenas o texto da resposta
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
            
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
            
    async def _record_follow_up(self, lead_id: str, follow_up_type: str, message: str):
        """Registra follow-up enviado"""
        try:
            self.supabase.table('follow_ups').insert({
                'lead_id': lead_id,
                'type': follow_up_type,
                'message': message,
                'status': 'executed',
                'executed_at': datetime.now().isoformat(),
                'scheduled_at': datetime.now().isoformat()
            }).execute()
            
        except Exception as e:
            logger.error(f"Erro ao registrar follow-up: {e}")
            
    async def _schedule_next_follow_up(self, lead_id: str, current_type: str) -> Optional[Dict[str, Any]]:
        """Agenda próximo follow-up baseado no tipo atual"""
        # Usar configurações do config
        second_delay_hours = agent_config.follow_up_second_delay_hours  # 24 horas configuráveis
        
        # Sequência de follow-ups com tempos configuráveis
        sequence = {
            'reminder': ('check_in', second_delay_hours),      # Segundo follow-up em 24h (configurável)
            'check_in': ('reengagement', 48),                  # Reengajamento em 48h
            'reengagement': ('nurture', 72),                   # Nutrição em 72h
        }
        
        if current_type in sequence:
            next_type, hours = sequence[current_type]
            scheduled_time = datetime.now() + timedelta(hours=hours)
            
            try:
                result = self.supabase.table('follow_ups').insert({
                    'lead_id': lead_id,
                    'type': next_type,
                    'scheduled_at': scheduled_time.isoformat(),
                    'status': 'pending'
                }).execute()
                
                return {
                    'type': next_type,
                    'scheduled_at': scheduled_time.isoformat(),
                    'hours_until': hours
                }
                
            except Exception as e:
                logger.error(f"Erro ao agendar próximo follow-up: {e}")
                
        return None


class FollowUpScheduler:
    """Agendador de follow-ups que roda periodicamente"""
    
    def __init__(self):
        self.workflow = FollowUpWorkflow()
        self.supabase = supabase_client
        self.running = False
        
    async def start(self):
        """Inicia o agendador"""
        self.running = True
        logger.info("Follow-up scheduler iniciado")
        
        while self.running:
            try:
                # Processar follow-ups pendentes
                await self._process_pending_follow_ups()
                
                # Aguardar 5 minutos antes da próxima verificação
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Erro no scheduler de follow-up: {e}")
                await asyncio.sleep(60)  # Aguardar 1 minuto em caso de erro
                
    async def stop(self):
        """Para o agendador"""
        self.running = False
        logger.info("Follow-up scheduler parado")
        
    async def _process_pending_follow_ups(self):
        """Processa todos os follow-ups pendentes"""
        try:
            # Buscar follow-ups pendentes que já passaram do horário
            result = self.supabase.table('follow_ups')\
                .select('*')\
                .eq('status', 'pending')\
                .lte('scheduled_at', datetime.now().isoformat())\
                .execute()
                
            if result.data:
                logger.info(f"Processando {len(result.data)} follow-ups pendentes")
                
                for follow_up in result.data:
                    # Executar workflow
                    workflow_result = await self.workflow.run(
                        lead_id=follow_up['lead_id'],
                        follow_up_type=follow_up['type'],
                        custom_message=follow_up.get('message')
                    )
                    
                    # Atualizar status
                    if workflow_result['status'] == 'success':
                        self.supabase.table('follow_ups')\
                            .update({
                                'status': 'executed',
                                'executed_at': datetime.now().isoformat(),
                                'result': workflow_result
                            })\
                            .eq('id', follow_up['id'])\
                            .execute()
                    else:
                        # Marcar como falha mas não retentar infinitamente
                        self.supabase.table('follow_ups')\
                            .update({
                                'status': 'failed',
                                'result': workflow_result
                            })\
                            .eq('id', follow_up['id'])\
                            .execute()
                            
                    # Pequeno delay entre execuções
                    await asyncio.sleep(2)
                    
        except Exception as e:
            logger.error(f"Erro ao processar follow-ups pendentes: {e}")


# Instância global do scheduler
follow_up_scheduler = FollowUpScheduler()