"""
FollowUp Executor Service - Processamento de Follow-ups Agendados
Executa follow-ups e lembretes agendados no banco de dados
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import json

from app.integrations.supabase_client import SupabaseClient
from app.integrations.evolution import evolution_client
from app.integrations.google_calendar import google_calendar_client
from app.config import settings, FOLLOW_UP_TYPES
from app.utils.logger import emoji_logger
from app.integrations.redis_client import redis_client

logger = logging.getLogger(__name__)

class FollowUpExecutorService:
    """
    Serviço executor de follow-ups
    Processa follow-ups agendados e envia mensagens personalizadas
    """
    
    def __init__(self):
        """Inicializa o executor de follow-ups"""
        self.db = SupabaseClient()
        self.evolution = evolution_client
        self.running = False
        self.check_interval = 60  # 1 minuto
        
        # Templates de mensagens por tipo
        self.templates = {
            "IMMEDIATE_REENGAGEMENT": [
                "Oi {name}! Vi que nossa conversa ficou pela metade...",
                "Ainda posso te ajudar com a economia na conta de luz?",
                "Se preferir, podemos conversar em outro momento"
            ],
            "DAILY_NURTURING": [
                "{name}, você sabia que clientes como você economizam em média R$ {savings} por ano?",
                "A Solar Prime tem a solução perfeita para sua conta de R$ {bill_value}",
                "Vamos conversar sobre como reduzir sua conta de luz?"
            ],
            "MEETING_CONFIRMATION": [
                "Oi {name}! Passando para confirmar nossa reunião de amanhã às {time}",
                "Você confirma presença? É só responder SIM ou NÃO",
                "Vou te mostrar como economizar {percentage}% na conta de luz!"
            ],
            "MEETING_REMINDER": [
                "{name}, nossa reunião é daqui a {hours} horas!",
                "Já preparei tudo para te mostrar a economia",
                "Link da reunião: {meeting_link}"
            ],
            "ABANDONMENT_CHECK": [
                "{name}, há {days} dias você demonstrou interesse em economizar na conta de luz",
                "Ainda tem interesse? A SolarPrime continua com as melhores condições",
                "Posso te ajudar com alguma dúvida?"
            ]
        }
        
    async def start(self):
        """Inicia o serviço executor"""
        if self.running:
            logger.warning("Executor de follow-ups já está rodando")
            return
            
        self.running = True
        emoji_logger.system_ready("FollowUp Executor")
        logger.info("🚀 DEBUG: FollowUp Executor iniciado com sucesso!")
        logger.info(f"⏰ DEBUG: Check interval: {self.check_interval}s")
        logger.info("📋 DEBUG: Templates de mensagens carregados:")
        for tipo, msgs in self.templates.items():
            logger.info(f"  - {tipo}: {len(msgs)} templates")
        
        # Iniciar loop principal
        asyncio.create_task(self._execution_loop())
        asyncio.create_task(self._meeting_reminder_loop())
        logger.info("🔄 DEBUG: Loops de execução iniciados (follow-ups e lembretes)")
        
    async def stop(self):
        """Para o serviço executor"""
        self.running = False
        logger.info("FollowUp Executor parado")
        
    async def _execution_loop(self):
        """Loop principal de execução de follow-ups"""
        while self.running:
            try:
                await self.process_pending_followups()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Erro no loop de follow-ups: {e}")
                await asyncio.sleep(60)
    
    async def _meeting_reminder_loop(self):
        """Loop específico para lembretes de reunião (24h e 2h antes)"""
        while self.running:
            try:
                await self.process_meeting_reminders()
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
            except Exception as e:
                logger.error(f"❌ Erro no loop de lembretes: {e}")
                await asyncio.sleep(60)
    
    async def process_pending_followups(self):
        """
        Processa follow-ups pendentes
        Busca follow-ups com scheduled_at <= agora e status = pending
        """
        try:
            now = datetime.now(timezone.utc)
            logger.info(f"🔍 DEBUG: Verificando follow-ups pendentes às {now.isoformat()}")
            
            # Buscar follow-ups pendentes
            result = self.db.client.table('follow_ups').select("*").eq(
                'status', 'pending'
            ).lte(
                'scheduled_at', now.isoformat()
            ).order('scheduled_at').limit(10).execute()
            
            # DEBUG: Log detalhado do resultado
            logger.info(f"📊 DEBUG: Query executada. Result data: {result.data is not None}, Count: {len(result.data) if result.data else 0}")
            
            if not result.data:
                logger.debug("🔍 DEBUG: Nenhum follow-up pendente encontrado no momento")
                # DEBUG: Verificar se existem follow-ups futuros
                future_result = self.db.client.table('follow_ups').select("scheduled_at, type, status").eq(
                    'status', 'pending'
                ).order('scheduled_at').limit(5).execute()
                
                if future_result.data:
                    logger.info(f"📅 DEBUG: Próximos follow-ups agendados:")
                    for f in future_result.data:
                        logger.info(f"  - {f['scheduled_at']} | {f['type']} | {f['status']}")
                else:
                    logger.info("📭 DEBUG: Nenhum follow-up agendado na tabela")
                return
            
            logger.info(f"📋 {len(result.data)} follow-ups pendentes encontrados")
            logger.info(f"📝 DEBUG: Detalhes dos follow-ups:")
            for idx, f in enumerate(result.data):
                logger.info(f"  {idx+1}. Lead: {f.get('lead_id')} | Type: {f.get('type')} | Scheduled: {f.get('scheduled_at')}")
            
            for followup in result.data:
                await self._execute_followup(followup)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar follow-ups: {e}")
    
    async def process_meeting_reminders(self):
        """
        Processa lembretes de reunião da tabela follow_ups
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Verificar se Google Calendar está habilitado
            if settings.disable_google_calendar:
                logger.debug("Google Calendar desabilitado nas configurações")
                return
            
            # Buscar lembretes de reunião pendentes na tabela follow_ups
            pending_reminders_result = self.db.client.table('follow_ups').select("*").eq(
                'type', 'MEETING_REMINDER'
            ).eq(
                'status', 'PENDING'
            ).lte(
                'scheduled_at', now.isoformat()
            ).execute()
            
            if not pending_reminders_result.data:
                logger.debug("Nenhum lembrete de reunião pendente")
                return
            
            # Processar cada lembrete
            for reminder in pending_reminders_result.data:
                try:
                    # Buscar dados do lead
                    lead_data = await self.db.get_lead_by_id(reminder['lead_id'])
                    if not lead_data:
                        logger.warning(f"Lead {reminder['lead_id']} não encontrado para lembrete")
                        continue
            
                    # Extrair metadata do lembrete
                    metadata = reminder.get('metadata', {})
                    hours_before = metadata.get('hours_before', 24)
                    google_event_id = metadata.get('google_event_id')
                    
                    # Buscar evento no Google Calendar se tiver ID
                    google_event = None
                    if google_event_id:
                        try:
                            google_event = await google_calendar_client.get_event(google_event_id)
                            if google_event and google_event.get('status') == 'cancelled':
                                # Reunião cancelada, marcar lembrete como cancelado
                                await self.db.client.table('follow_ups').update({
                                    'status': 'cancelled',
                                    'executed_at': now.isoformat(),
                                    'response': json.dumps({'reason': 'meeting_cancelled'})
                                }).eq('id', reminder['id']).execute()
                                continue
                        except Exception as cal_error:
                            logger.error(f"Erro ao buscar evento no Google Calendar: {cal_error}")
                    
                    # Buscar qualificação do lead
                    qualification_result = self.db.client.table('leads_qualifications').select("*").eq(
                        'lead_id', reminder['lead_id']
                    ).single().execute()
                    
                    qualification_id = qualification_result.data['id'] if qualification_result.data else None
                    
                    # Enviar lembrete personalizado
                    await self._send_meeting_reminder_v2(
                        lead_data=lead_data,
                        google_event=google_event or {'summary': reminder.get('message', 'Reunião')},
                        hours_before=hours_before,
                        qualification_id=qualification_id
                    )
                    
                    # Marcar lembrete como executado
                    await self.db.client.table('follow_ups').update({
                        'status': 'executed',
                        'executed_at': now.isoformat()
                    }).eq('id', reminder['id']).execute()
                    
                except Exception as reminder_error:
                    logger.error(f"Erro ao processar lembrete {reminder['id']}: {reminder_error}")
                    await self.db.client.table('follow_ups').update({
                        'status': 'failed',
                        'executed_at': now.isoformat(),
                        'error_reason': str(reminder_error)
                    }).eq('id', reminder['id']).execute()
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar lembretes de reunião: {e}")
    
    async def _execute_followup(self, followup: Dict[str, Any]):
        """Executa um follow-up individual"""
        try:
            lead_id = followup.get('lead_id')
            followup_type = followup.get('type', 'CUSTOM')
            
            logger.info(f"🎯 DEBUG: Iniciando execução de follow-up")
            logger.info(f"  - ID: {followup.get('id')}")
            logger.info(f"  - Lead ID: {lead_id}")
            logger.info(f"  - Type: {followup_type}")
            logger.info(f"  - Scheduled: {followup.get('scheduled_at')}")
            
            # 🔒 LOCK DISTRIBUÍDO POR LEAD - Previne envios duplicados
            lock_key = f"followup:{lead_id}"
            lock_acquired = await redis_client.acquire_lock(lock_key, ttl=60)
            
            if not lock_acquired:
                logger.info(f"🔒 Follow-up para lead {lead_id} já sendo processado por outro processo")
                return
                
            try:
                # Buscar dados do lead
                lead_result = self.db.client.table('leads').select("*").eq(
                    'id', lead_id
                ).single().execute()
                
                if not lead_result.data:
                    logger.error(f"Lead {lead_id} não encontrado")
                    await self._mark_followup_failed(followup['id'], "Lead não encontrado")
                    return
                
                lead = lead_result.data
                phone = lead.get('phone_number')
                
                if not phone:
                    await self._mark_followup_failed(followup['id'], "Telefone não encontrado")
                    return
                
                # NOVA VALIDAÇÃO: Para follow-ups de reengajamento, verificar se usuário realmente ficou inativo
                if followup_type == 'reengagement':
                    should_send = await self._validate_inactivity_followup(followup)
                    if not should_send:
                        # Usuário respondeu, cancelar este follow-up
                        self.db.client.table('follow_ups').update({
                            'status': 'cancelled',
                            'executed_at': datetime.now(timezone.utc).isoformat(),
                            'response': json.dumps({'reason': 'user_responded_before_followup'})
                        }).eq('id', followup['id']).execute()
                        
                        logger.info(f"📞 Follow-up cancelado - {lead.get('name')} respondeu antes do prazo")
                        return
                
                # Preparar mensagem baseada no template
                message = await self._prepare_followup_message(followup_type, lead, followup)
                
                if not message:
                    await self._mark_followup_failed(followup['id'], "Falha ao preparar mensagem")
                    return
                
                # SANITIZAÇÃO FINAL - Remove qualquer tag remanescente
                message = self._sanitize_final_message(message)
                
                logger.info(f"📤 DEBUG: Preparando envio via Evolution API")
                logger.info(f"  - Phone: {phone}")
                logger.info(f"  - Message length: {len(message)}")
                logger.info(f"  - Message preview: {message[:100]}...")
                
                # Enviar mensagem via WhatsApp
                result = await self.evolution.send_text_message(
                    phone=phone,
                    message=message
                )
                
                logger.info(f"📱 DEBUG: Resultado do envio Evolution: {result}")
            
                if result:
                    # Marcar como executado
                    update_result = self.db.client.table('follow_ups').update({
                        'status': 'executed',
                        'executed_at': datetime.now(timezone.utc).isoformat(),
                        'response': json.dumps({'evolution_result': result})
                    }).eq('id', followup['id']).execute()
                    
                    logger.info(f"✅ DEBUG: Follow-up marcado como executado no banco")
                    emoji_logger.whatsapp_sent(f"Follow-up enviado para {lead.get('name')}")
                    
                    # Agendar próximo follow-up se necessário
                    await self._schedule_next_followup(followup_type, lead, followup)
                else:
                    logger.error(f"❌ DEBUG: Falha no envio via Evolution. Result: {result}")
                    await self._mark_followup_failed(followup['id'], "Falha no envio")
                    
            finally:
                # 🔓 LIBERAR LOCK
                await redis_client.release_lock(lock_key)
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar follow-up: {e}")
            await self._mark_followup_failed(followup.get('id'), str(e))
            # Garantir liberação do lock mesmo em caso de erro
            await redis_client.release_lock(lock_key)
    
    async def _send_meeting_reminder_v2(self, lead_data: Dict[str, Any], google_event: Dict[str, Any], hours_before: int, qualification_id: str):
        """
        Envia lembrete de reunião PERSONALIZADO usando Helen + contexto completo
        
        Args:
            lead_data: Dados do lead (id, name, phone_number)
            google_event: Evento do Google Calendar
            hours_before: Horas antes da reunião (24 ou 2)
            qualification_id: ID do registro na tabela leads_qualifications
        """
        try:
            phone = lead_data.get('phone_number')
            
            if not phone:
                logger.warning(f"Lead {lead_data.get('id')} sem telefone para lembrete")
                return
            
            # Extrair informações do evento
            start_str = google_event.get('start', {}).get('dateTime', '')
            start_time = self._parse_datetime(start_str)
            
            # Local da reunião (online ou presencial)
            location = google_event.get('location', 'Online')
            
            # Link da reunião se houver
            meeting_link = ''
            if google_event.get('hangoutLink'):
                meeting_link = google_event['hangoutLink']
            elif 'meet.google.com' in google_event.get('description', ''):
                # Extrair link do Google Meet da descrição
                import re
                match = re.search(r'(https://meet\.google\.com/[\w-]+)', google_event.get('description', ''))
                if match:
                    meeting_link = match.group(1)
            
            # 🧠 GERAR MENSAGEM INTELIGENTE PERSONALIZADA (Helen + Contexto)
            logger.info(f"🧠 Gerando lembrete personalizado {hours_before}h para {lead_data.get('name')}")
            
            # Simular follow-up para reutilizar sistema inteligente
            fake_followup = {
                'type': f'MEETING_REMINDER_{hours_before}H',
                'metadata': {
                    'phone': phone,
                    'meeting_date': start_time.strftime('%d/%m/%Y'),
                    'meeting_time': start_time.strftime('%H:%M'),
                    'meeting_link': meeting_link,
                    'location': location,
                    'hours_before': hours_before,
                    'google_event_id': google_event.get('id')
                }
            }
            
            # Tentar mensagem inteligente primeiro
            intelligent_message = await self._generate_intelligent_meeting_reminder(lead_data, fake_followup, hours_before)
            
            if intelligent_message:
                message = intelligent_message
                logger.info(f"✅ Lembrete personalizado gerado por Helen")
            else:
                # Fallback para mensagem básica (mas melhor que padrão)
                if hours_before == 24:
                    message = f"Oi {lead_data.get('name', 'Cliente')}! Nossa reunião sobre energia solar está confirmada para amanhã ({start_time.strftime('%d/%m/%Y')}) às {start_time.strftime('%H:%M')}. Posso confirmar sua presença?"
                elif hours_before == 2:
                    message = f"{lead_data.get('name', 'Cliente')}, nossa reunião é daqui a 2 horas ({start_time.strftime('%H:%M')})! {f'🔗 {meeting_link}' if meeting_link else ''} Até já!"
                else:
                    return
                logger.info(f"⚠️ Usando mensagem de fallback para lembrete {hours_before}h")
            
            # Marcar como enviado ANTES de tentar enviar
            if hours_before == 24:
                self.db.client.table('leads_qualifications').update({
                    'reminder_24h_sent': True,
                    'reminder_24h_sent_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', qualification_id).execute()
            elif hours_before == 2:
                self.db.client.table('leads_qualifications').update({
                    'reminder_2h_sent': True,
                    'reminder_2h_sent_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', qualification_id).execute()
            
            # SANITIZAÇÃO FINAL - Remove qualquer tag remanescente
            message = self._sanitize_final_message(message)
            
            # Enviar via WhatsApp
            result = await self.evolution.send_text_message(
                phone=phone,
                message=message
            )
            
            if result:
                emoji_logger.whatsapp_sent(f"Lembrete personalizado {hours_before}h enviado para {lead_data.get('name')}")
            else:
                logger.error(f"Falha ao enviar lembrete {hours_before}h para {lead_data.get('name')}")
                # Não reverter marcação - evita reenvios múltiplos
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar lembrete personalizado: {e}")
    
    async def _prepare_followup_message(self, followup_type: str, lead: Dict, followup: Dict) -> Optional[str]:
        """Prepara mensagem personalizada - INTELIGENTE para reengajamento, template para outros"""
        try:
            # FOLLOW-UP INTELIGENTE: Para reengajamento, SEMPRE usar Helen completa com contexto
            if followup_type in ["reengagement", "IMMEDIATE_REENGAGEMENT", "ABANDONMENT_CHECK"]:
                return await self._generate_intelligent_message(followup_type, lead, followup)
            
            # TEMPLATES EXISTENTES: Para outros tipos (funcionam perfeitamente)
            templates = self.templates.get(followup_type, [])
            
            if not templates:
                # CORREÇÃO CRÍTICA: NUNCA usar campo 'message' diretamente pois pode conter texto técnico
                # Em vez disso, usar fallback inteligente
                if followup.get('message', '').strip():
                    # Se tem mensagem mas não é template conhecido, tentar IA também
                    intelligent_fallback = await self._generate_intelligent_message(followup_type, lead, followup)
                    if intelligent_fallback:
                        return intelligent_fallback
                    # Se IA falhar, usar template padrão seguro
                    return f"Oi {lead.get('name', 'Cliente')}! Vi que nossa conversa ficou pela metade... Posso continuar te ajudando?"
                return None
            
            # Selecionar template baseado no índice do follow-up
            attempt = followup.get('attempt', 0)
            template = templates[min(attempt, len(templates) - 1)]
            
            # Substituir variáveis
            bill_value = float(lead.get('bill_value', 0) or 0)
            savings_value = bill_value * 0.3  # 30% de economia
            
            # Calcular dias desde criação
            created_at = lead.get('created_at', datetime.now(timezone.utc).isoformat())
            if created_at:
                created_dt = self._parse_datetime(created_at)
                days_since = (datetime.now(timezone.utc) - created_dt).days
            else:
                days_since = 0
            
            message = template.format(
                name=lead.get('name', 'Cliente'),
                bill_value=f"{bill_value:.2f}",
                savings=f"{savings_value:.2f}",
                percentage=30,
                time=followup.get('metadata', {}).get('meeting_time', ''),
                meeting_link=followup.get('metadata', {}).get('meeting_link', ''),
                days=days_since,
                hours=followup.get('metadata', {}).get('hours_until', '')
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Erro ao preparar mensagem: {e}")
            return None
    
    async def _schedule_next_followup(self, followup_type: str, lead: Dict, current_followup: Dict):
        """Agenda próximo follow-up baseado na estratégia - FLUXO SEQUENCIAL"""
        try:
            from app.utils.time_utils import get_business_aware_datetime
            
            # NOVO FLUXO SEQUENCIAL - Só agenda próximo se usuário não respondeu
            if followup_type == "reengagement":
                # Agendar follow-up de 24h apenas se foi o primeiro (30min)
                metadata = current_followup.get('metadata', {})
                trigger = metadata.get('trigger', '')
                
                if trigger == "agent_response_30min":
                    # Este era o follow-up de 30min, agendar o de 24h
                    agent_response_timestamp = metadata.get('agent_response_timestamp')
                    phone = metadata.get('phone')
                    conversation_id = metadata.get('conversation_id')
                    
                    if agent_response_timestamp and phone and conversation_id:
                        next_time = get_business_aware_datetime(hours_from_now=24)
                        
                        followup_24h_data = {
                            'lead_id': lead['id'],
                            'scheduled_at': next_time.isoformat(),
                            'type': 'reengagement',
                            'follow_up_type': 'DAILY_NURTURING',
                            'message': '',  # Usar mensagem inteligente
                            'status': 'pending',
                            'priority': 'medium',
                            'metadata': {
                                'phone': phone,
                                'conversation_id': conversation_id,
                                'trigger': 'agent_response_24h',
                                'agent_response_timestamp': agent_response_timestamp,
                                'scheduled_reason': 'User inactivity check 24h after agent response',
                                'message_type': 'intelligent_reengagement'
                            }
                        }
                        
                        result = self.db.client.table('follow_ups').insert(followup_24h_data).execute()
                        
                        if result.data:
                            emoji_logger.system_info(f"📅 Follow-up sequencial de 24h agendado para {phone} às {next_time.strftime('%d/%m %H:%M')}")
                        else:
                            logger.error("Falha ao agendar follow-up sequencial de 24h")
                    
                elif trigger == "agent_response_24h":
                    # Este era o follow-up de 24h, pode continuar nurturing por mais alguns dias
                    attempt = current_followup.get('attempt', 0)
                    if attempt < 3:  # Máximo 3 tentativas adicionais após 24h
                        next_time = get_business_aware_datetime(hours_from_now=48)  # A cada 48h
                        
                        await self._create_followup(
                            lead_id=lead['id'],
                            followup_type="DAILY_NURTURING",
                            scheduled_at=next_time,
                            message="",
                            priority="low",
                            attempt=attempt + 1
                        )
                        emoji_logger.system_info(f"📅 Follow-up de nurturing adicional agendado (tentativa {attempt + 1})")
                    
        except Exception as e:
            logger.error(f"Erro ao agendar próximo follow-up: {e}")
    
    async def _create_followup(self, lead_id: int, followup_type: str, 
                              scheduled_at: datetime, message: str, 
                              priority: str = "medium", attempt: int = 0):
        """Cria novo follow-up no banco"""
        try:
            followup_data = {
                'lead_id': lead_id,
                'type': followup_type,
                'scheduled_at': scheduled_at.isoformat(),
                'status': 'pending',
                'priority': priority,
                'message': message,
                'attempt': attempt,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            self.db.client.table('follow_ups').insert(followup_data).execute()
            logger.info(f"📅 Novo follow-up agendado para {scheduled_at}")
            
        except Exception as e:
            logger.error(f"Erro ao criar follow-up: {e}")
    
    async def _mark_followup_failed(self, followup_id: int, reason: str):
        """Marca follow-up como falho"""
        try:
            self.db.client.table('follow_ups').update({
                'status': 'failed',
                'failed_at': datetime.now(timezone.utc).isoformat(),
                'error_reason': reason
            }).eq('id', followup_id).execute()
            
        except Exception as e:
            logger.error(f"Erro ao marcar follow-up como falho: {e}")
    
    async def _validate_inactivity_followup(self, followup: Dict[str, Any]) -> bool:
        """
        Valida se usuário realmente ficou inativo para follow-ups de reengajamento
        
        Returns:
            True: Deve enviar follow-up (usuário inativo)
            False: Cancelar follow-up (usuário respondeu)
        """
        try:
            metadata = followup.get('metadata', {})
            if not isinstance(metadata, dict):
                metadata = json.loads(metadata) if metadata else {}
            
            conversation_id = metadata.get('conversation_id')
            agent_response_timestamp = metadata.get('agent_response_timestamp')
            
            if not conversation_id or not agent_response_timestamp:
                logger.warning(f"Follow-up {followup['id']} sem metadados necessários para validação")
                return True  # Se não temos dados, enviar o follow-up mesmo assim
            
            # Converter timestamp para datetime (garantir timezone-aware)
            agent_response_time = self._parse_datetime(agent_response_timestamp)
            
            # Buscar última mensagem do usuário na conversa (sender='user')
            result = self.db.client.table('messages').select(
                "id, created_at, role"
            ).eq(
                'conversation_id', conversation_id
            ).eq(
                'role', 'user'
            ).order(
                'created_at', desc=True
            ).limit(1).execute()
            
            if not result.data:
                # Sem mensagens do usuário na conversa, enviar follow-up
                logger.info(f"🔍 Nenhuma mensagem do usuário encontrada na conversa {conversation_id}")
                return True
            
            last_user_message = result.data[0]
            last_user_message_time = self._parse_datetime(last_user_message['created_at'])
            
            # Verificar se usuário respondeu APÓS a resposta do agente que gerou este follow-up
            if last_user_message_time > agent_response_time:
                logger.info(f"🚫 Usuário respondeu às {last_user_message_time} após agente às {agent_response_time} - cancelando follow-up")
                return False
            
            # Usuário não respondeu desde a resposta do agente, enviar follow-up
            logger.info(f"✅ Usuário inativo desde {agent_response_time} - enviando follow-up de reengajamento")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar inatividade do follow-up: {e}")
            return True  # Em caso de erro, enviar o follow-up mesmo assim
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """
        Converte string para datetime garantindo timezone awareness
        Lida com diferentes formatos que podem vir do banco
        """
        try:
            # Tentar parse com fromisoformat
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            
            # Se o datetime é naive (sem timezone), assumir UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            return dt
        except Exception as e:
            logger.warning(f"Erro ao fazer parse de datetime '{datetime_str}': {e}")
            # Fallback: retornar datetime atual em UTC
            return datetime.now(timezone.utc)
    
    async def _generate_intelligent_message(self, followup_type: str, lead: Dict, followup: Dict) -> Optional[str]:
        """
        FOLLOW-UP INTELIGENTE: Helen analisa contexto completo e gera mensagem personalizada
        Usa prompt-agente.md + histórico + knowledge_base + AgenticSDR
        """
        try:
            logger.info(f"🧠 Gerando follow-up inteligente para {lead.get('name')}")
            
            # 1. VERIFICAR DISPONIBILIDADE DO PROMPT (AgenticSDR já carrega automaticamente)
            import os
            base_path = os.path.dirname(os.path.dirname(__file__))
            prompt_path = os.path.join(base_path, "prompts", "prompt-agente.md")
            
            prompt_available = os.path.exists(prompt_path)
            logger.info(f"📚 Prompt Helen disponível: {'✅' if prompt_available else '❌'}")
            
            # 2. RECUPERAR CONTEXTO DA CONVERSA
            metadata = followup.get('metadata', {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            conversation_id = metadata.get('conversation_id')
            phone = metadata.get('phone')
            
            conversation_history = ""
            if conversation_id:
                try:
                    # Buscar histórico completo da conversa
                    messages_result = self.db.client.table('messages').select(
                        "role, content, created_at"
                    ).eq(
                        'conversation_id', conversation_id
                    ).order('created_at', desc=False).execute()
                    
                    if messages_result.data:
                        conversation_history = "\n".join([
                            f"{msg['role'].upper()}: {msg['content']}"
                            for msg in messages_result.data
                        ])
                        logger.info(f"📚 Histórico recuperado: {len(messages_result.data)} mensagens")
                    else:
                        logger.info("📚 Nenhuma mensagem encontrada na conversa")
                except Exception as e:
                    logger.warning(f"Erro ao buscar histórico: {e}")
                    conversation_history = "Histórico não disponível"
            
            # 3. VERIFICAR KNOWLEDGE BASE (AgenticSDR pode acessar quando necessário)
            try:
                # Schema correto baseado no SQL: question, answer, category
                kb_result = self.db.client.table('knowledge_base').select("title").limit(1).execute()
                kb_available = len(kb_result.data) > 0
                logger.info(f"🧠 Knowledge base disponível: {'✅' if kb_available else '❌'}")
            except Exception as e:
                logger.warning(f"Knowledge base não acessível: {e}")
                kb_available = False
            
            # 4. CRIAR MENSAGEM DE CONTEXTO PARA FOLLOW-UP (EVITAR TRIGGER DE CALENDÁRIO)
            followup_trigger_message = f"""REENGAJAMENTO DE LEAD - NÃO É AGENDAMENTO:

⚠️ IMPORTANTE: Esta é uma mensagem de follow-up/reengajamento, NÃO é uma solicitação de agendamento.

Lead: {lead.get('name', 'Cliente')} - Conta: R${lead.get('bill_value', '0')} - Tel: {phone}
Status: Lead parou de responder após conversa ({followup_type})

Contexto da conversa anterior:
{conversation_history[-800:] if conversation_history else "Nenhum histórico disponível"}

OBJETIVO: Gerar mensagem empática de reengajamento para reativar conversa onde parou. NÃO mencionar agendamentos a menos que o histórico mostre interesse específico nisso."""
            
            # 5. CHAMAR AGENTIC SDR PARA GERAR MENSAGEM INTELIGENTE
            from app.agents.agentic_sdr import create_agentic_sdr
            
            sdr_agent = await create_agentic_sdr()
            
            # Chamar AgenticSDR com contexto da conversa
            response = await sdr_agent.process_message(
                phone=phone or lead.get('phone_number', ''),
                message=followup_trigger_message,
                lead_data=lead,
                conversation_id=conversation_id
            )
            
            if response:
                # Extrair resposta limpa
                if isinstance(response, dict):
                    intelligent_message = response.get("text", "")
                else:
                    intelligent_message = str(response)
                
                # Limpar resposta (remover tags se houver)
                intelligent_message = self._extract_final_response(intelligent_message)
                
                # Garantir linha única para WhatsApp
                intelligent_message = intelligent_message.replace('\n', ' ').replace('\r', ' ')
                intelligent_message = ' '.join(intelligent_message.split())
                
                logger.info(f"🧠✅ Follow-up inteligente gerado: {intelligent_message[:50]}...")
                return intelligent_message
            else:
                logger.warning("❌ AgenticSDR não gerou resposta, usando fallback")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar follow-up inteligente: {e}")
            # Fallback para template original em caso de erro
            return None
    
    async def _generate_intelligent_meeting_reminder(self, lead_data: Dict, fake_followup: Dict, hours_before: int) -> Optional[str]:
        """
        LEMBRETE INTELIGENTE: Helen recupera contexto da conversa e gera lembrete personalizado
        Usa prompt-agente.md + histórico da conversa + dados da reunião + AgenticSDR
        """
        try:
            logger.info(f"🧠 Gerando lembrete inteligente {hours_before}h para {lead_data.get('name')}")
            
            phone = lead_data.get('phone_number')
            metadata = fake_followup.get('metadata', {})
            
            # 1. BUSCAR HISTÓRICO DA CONVERSA (Lead pode ter conversation_id)
            conversation_history = ""
            conversation_id = None
            
            try:
                # Buscar conversas do lead pelo telefone
                conversations_result = self.db.client.table('conversations').select(
                    "id, created_at"
                ).eq('phone_number', phone).order('created_at', desc=True).limit(1).execute()
                
                if conversations_result.data:
                    conversation_id = conversations_result.data[0]['id']
                    logger.info(f"📚 Conversa encontrada: {conversation_id}")
                    
                    # Buscar mensagens da conversa
                    messages_result = self.db.client.table('messages').select(
                        "role, content, created_at"
                    ).eq(
                        'conversation_id', conversation_id
                    ).order('created_at', desc=False).execute()
                    
                    if messages_result.data:
                        conversation_history = "\n".join([
                            f"{msg['role'].upper()}: {msg['content']}"
                            for msg in messages_result.data
                        ])
                        logger.info(f"📚 Histórico recuperado: {len(messages_result.data)} mensagens")
                    else:
                        logger.info("📚 Nenhuma mensagem encontrada na conversa")
                else:
                    logger.info(f"📚 Nenhuma conversa encontrada para telefone {phone}")
            except Exception as e:
                logger.warning(f"Erro ao buscar histórico da conversa: {e}")
                conversation_history = "Histórico não disponível"
            
            # 2. CRIAR CONTEXTO ESPECÍFICO PARA LEMBRETE DE REUNIÃO
            meeting_context = f"""LEMBRETE DE REUNIÃO PERSONALIZADO - Helen Vieira:

⏰ TIPO: Lembrete de reunião {hours_before}h antes
📅 REUNIÃO: {metadata.get('meeting_date')} às {metadata.get('meeting_time')}
🔗 LINK: {metadata.get('meeting_link', 'A definir')}
📍 LOCAL: {metadata.get('location', 'Online')}

👤 LEAD: {lead_data.get('name', 'Cliente')} 
📞 TELEFONE: {phone}
💰 CONTA DE LUZ: R$ {lead_data.get('bill_value', '0')}

🗨️ CONTEXTO DA CONVERSA:
{conversation_history[-1000:] if conversation_history else "Primeira interação - ainda não temos histórico de conversa"}

🎯 OBJETIVO: Gerar lembrete caloroso e personalizado usando o contexto da conversa.
- Para 24h antes: Confirmar presença e criar expectativa positiva
- Para 2h antes: Lembrete amigável com link e motivação final
- Use o nome real do lead
- Seja empática e referente aos assuntos discutidos na conversa
- Mantenha o tom Helen Vieira (consultora especialista em energia solar)
- NÃO seja genérica, use detalhes específicos da conversa quando possível"""
            
            # 3. CHAMAR AGENTIC SDR COM CONTEXTO DE LEMBRETE
            from app.agents.agentic_sdr import create_agentic_sdr
            
            sdr_agent = await create_agentic_sdr()
            
            response = await sdr_agent.process_message(
                phone=phone,
                message=meeting_context,
                lead_data=lead_data,
                conversation_id=conversation_id
            )
            
            if response:
                # Extrair resposta limpa
                if isinstance(response, dict):
                    intelligent_reminder = response.get("text", "")
                else:
                    intelligent_reminder = str(response)
                
                # Limpar resposta (remover tags se houver)
                intelligent_reminder = self._extract_final_response(intelligent_reminder)
                
                # Garantir formatação adequada para WhatsApp (manter quebras de linha)
                intelligent_reminder = intelligent_reminder.strip()
                
                logger.info(f"🧠✅ Lembrete inteligente {hours_before}h gerado: {intelligent_reminder[:60]}...")
                return intelligent_reminder
            else:
                logger.warning("❌ AgenticSDR não gerou lembrete, usando fallback")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar lembrete inteligente: {e}")
            return None
    
    async def force_process(self) -> Dict[str, Any]:
        """
        Força processamento imediato de follow-ups
        Útil para testes
        """
        try:
            await self.process_pending_followups()
            await self.process_meeting_reminders()
            
            return {
                'success': True,
                'message': 'Processamento forçado concluído'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sanitize_final_message(self, text: str) -> str:
        """
        Sanitização final de mensagens - Remove qualquer tag remanescente
        
        Args:
            text: Texto a ser sanitizado
            
        Returns:
            Texto limpo sem tags
        """
        import re
        
        if not isinstance(text, str) or not text:
            return ""
        
        # Remove qualquer tag XML/HTML remanescente
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove quebras de linha múltiplas
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\r+', '', text)
        
        # Limpa espaços extras
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _extract_final_response(self, full_response: str) -> str:
        """
        Extrai apenas a resposta final das tags <RESPOSTA_FINAL>
        
        Args:
            full_response: Resposta completa do LLM incluindo raciocínio
            
        Returns:
            Apenas o conteúdo dentro das tags RESPOSTA_FINAL
        """
        import re
        
        try:
            if not full_response:
                return "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"
            
            # Busca o conteúdo entre as tags <RESPOSTA_FINAL> e </RESPOSTA_FINAL>
            pattern = r'<RESPOSTA_FINAL>(.*?)</RESPOSTA_FINAL>'
            match = re.search(pattern, full_response, re.DOTALL | re.IGNORECASE)
            
            if match:
                # Extrai e limpa o conteúdo
                final_response = match.group(1).strip()
                return final_response
            else:
                # ✅ RESPOSTA SEGURA: fallback que não vaza raciocínio
                logger.warning("🚨 TAGS <RESPOSTA_FINAL> não encontradas no follow-up")
                return "Olá! Como posso te ajudar hoje com sua energia solar?"
                
        except Exception as e:
            logger.error(f"🚨 ERRO ao extrair resposta final: {e}")
            # 🚨 RESPOSTA SEGURA: fallback de emergência
            return "Oi! Tive um probleminha técnico. Me dê só um momento que já te respondo!"

# Singleton
followup_executor_service = FollowUpExecutorService()