"""
FollowUp Executor Service - Processamento de Follow-ups Agendados
Executa follow-ups e lembretes agendados no banco de dados
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from app.integrations.supabase_client import SupabaseClient
from app.integrations.evolution import evolution_client
from app.config import settings, FOLLOW_UP_TYPES
from app.utils.logger import emoji_logger

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
                "Oi {name}! 👋 Vi que nossa conversa ficou pela metade...",
                "Ainda posso te ajudar com a economia na conta de luz?",
                "Se preferir, podemos conversar em outro momento 😊"
            ],
            "DAILY_NURTURING": [
                "{name}, você sabia que clientes como você economizam em média R$ {savings} por ano? 💰",
                "A Solar Prime tem a solução perfeita para sua conta de R$ {bill_value} 🌞",
                "Vamos conversar sobre como reduzir sua conta de luz?"
            ],
            "MEETING_CONFIRMATION": [
                "Oi {name}! 📅 Passando para confirmar nossa reunião de amanhã às {time}",
                "Você confirma presença? É só responder SIM ou NÃO",
                "Vou te mostrar como economizar {percentage}% na conta de luz! 💡"
            ],
            "MEETING_REMINDER": [
                "{name}, nossa reunião é daqui a {hours} horas! ⏰",
                "Já preparei tudo para te mostrar a economia 📊",
                "Link da reunião: {meeting_link}"
            ],
            "ABANDONMENT_CHECK": [
                "{name}, há {days} dias você demonstrou interesse em economizar na conta de luz",
                "Ainda tem interesse? A Solar Prime continua com as melhores condições 🌟",
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
        
        # Iniciar loop principal
        asyncio.create_task(self._execution_loop())
        asyncio.create_task(self._meeting_reminder_loop())
        
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
            now = datetime.now()
            
            # Buscar follow-ups pendentes
            result = self.db.client.table('follow_ups').select("*").eq(
                'status', 'pending'
            ).lte(
                'scheduled_at', now.isoformat()
            ).order('scheduled_at').limit(10).execute()
            
            if not result.data:
                return
            
            logger.info(f"📋 {len(result.data)} follow-ups pendentes encontrados")
            
            for followup in result.data:
                await self._execute_followup(followup)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar follow-ups: {e}")
    
    async def process_meeting_reminders(self):
        """
        Processa lembretes de reunião (24h e 2h antes)
        """
        try:
            now = datetime.now()
            
            # Buscar reuniões nas próximas 24h
            tomorrow = now + timedelta(hours=24)
            two_hours = now + timedelta(hours=2)
            
            # Buscar eventos do calendário
            events_24h = self.db.client.table('calendar_events').select("*").eq(
                'status', 'confirmed'
            ).gte(
                'start_time', tomorrow.isoformat()
            ).lte(
                'start_time', (tomorrow + timedelta(minutes=30)).isoformat()
            ).eq(
                'reminder_24h_sent', False
            ).execute()
            
            events_2h = self.db.client.table('calendar_events').select("*").eq(
                'status', 'confirmed'
            ).gte(
                'start_time', two_hours.isoformat()
            ).lte(
                'start_time', (two_hours + timedelta(minutes=30)).isoformat()
            ).eq(
                'reminder_2h_sent', False
            ).execute()
            
            # Enviar lembretes de 24h
            for event in events_24h.data:
                await self._send_meeting_reminder(event, hours_before=24)
            
            # Enviar lembretes de 2h
            for event in events_2h.data:
                await self._send_meeting_reminder(event, hours_before=2)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar lembretes de reunião: {e}")
    
    async def _execute_followup(self, followup: Dict[str, Any]):
        """Executa um follow-up individual"""
        try:
            lead_id = followup.get('lead_id')
            followup_type = followup.get('type', 'CUSTOM')
            
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
            
            # Preparar mensagem baseada no template
            message = await self._prepare_followup_message(followup_type, lead, followup)
            
            if not message:
                await self._mark_followup_failed(followup['id'], "Falha ao preparar mensagem")
                return
            
            # Enviar mensagem via WhatsApp
            result = await self.evolution.send_text_message(
                phone=phone,
                message=message
            )
            
            if result:
                # Marcar como executado
                self.db.client.table('follow_ups').update({
                    'status': 'executed',
                    'executed_at': datetime.now().isoformat(),
                    'response': json.dumps({'evolution_result': result})
                }).eq('id', followup['id']).execute()
                
                emoji_logger.whatsapp_sent(f"Follow-up enviado para {lead.get('name')}")
                
                # Agendar próximo follow-up se necessário
                await self._schedule_next_followup(followup_type, lead, followup)
            else:
                await self._mark_followup_failed(followup['id'], "Falha no envio")
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar follow-up: {e}")
            await self._mark_followup_failed(followup.get('id'), str(e))
    
    async def _send_meeting_reminder(self, event: Dict[str, Any], hours_before: int):
        """Envia lembrete de reunião"""
        try:
            lead_id = event.get('lead_id')
            
            # Buscar dados do lead
            lead_result = self.db.client.table('leads').select("*").eq(
                'id', lead_id
            ).single().execute()
            
            if not lead_result.data:
                return
            
            lead = lead_result.data
            phone = lead.get('phone_number')
            
            if not phone:
                return
            
            # Preparar mensagem de lembrete
            start_time = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
            
            if hours_before == 24:
                message = f"""
📅 *Lembrete de Reunião - Amanhã*

Oi {lead.get('name', 'Cliente')}! 

Nossa reunião sobre economia de energia solar está confirmada para amanhã:

🗓️ Data: {start_time.strftime('%d/%m/%Y')}
⏰ Horário: {start_time.strftime('%H:%M')}
📍 Local: {event.get('location', 'Online')}

Vou te mostrar como economizar até 30% na conta de luz! 💡

Confirma presença? Responda com SIM ou NÃO
                """.strip()
                
                # Marcar lembrete de 24h como enviado
                self.db.client.table('calendar_events').update({
                    'reminder_24h_sent': True,
                    'reminder_24h_sent_at': datetime.now().isoformat()
                }).eq('id', event['id']).execute()
                
            elif hours_before == 2:
                message = f"""
⏰ *Reunião em 2 horas!*

{lead.get('name', 'Cliente')}, nossa reunião é às {start_time.strftime('%H:%M')}!

Já preparei sua proposta personalizada de economia 📊

{f"🔗 Link: {event.get('meeting_link')}" if event.get('meeting_link') else ""}

Até daqui a pouco! 😊
                """.strip()
                
                # Marcar lembrete de 2h como enviado
                self.db.client.table('calendar_events').update({
                    'reminder_2h_sent': True,
                    'reminder_2h_sent_at': datetime.now().isoformat()
                }).eq('id', event['id']).execute()
            else:
                return
            
            # Enviar via WhatsApp
            await self.evolution.send_text_message(
                phone=phone,
                message=message
            )
            
            emoji_logger.whatsapp_sent(f"Lembrete {hours_before}h enviado para {lead.get('name')}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar lembrete de reunião: {e}")
    
    async def _prepare_followup_message(self, followup_type: str, lead: Dict, followup: Dict) -> Optional[str]:
        """Prepara mensagem personalizada baseada no template"""
        try:
            templates = self.templates.get(followup_type, [])
            
            if not templates:
                # Usar mensagem customizada se houver
                return followup.get('message', '')
            
            # Selecionar template baseado no índice do follow-up
            attempt = followup.get('attempt', 0)
            template = templates[min(attempt, len(templates) - 1)]
            
            # Substituir variáveis
            bill_value = float(lead.get('bill_value', 0) or 0)
            savings_value = bill_value * 0.3  # 30% de economia
            
            # Calcular dias desde criação
            created_at = lead.get('created_at', datetime.now().isoformat())
            if created_at:
                days_since = (datetime.now() - datetime.fromisoformat(created_at)).days
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
        """Agenda próximo follow-up baseado na estratégia"""
        try:
            # Lógica de follow-up baseada no tipo
            if followup_type == "IMMEDIATE_REENGAGEMENT":
                # Se não houve resposta, agendar daily nurturing em 24h
                if not lead.get('last_response_at'):
                    next_time = datetime.now() + timedelta(hours=24)
                    await self._create_followup(
                        lead_id=lead['id'],
                        followup_type="DAILY_NURTURING",
                        scheduled_at=next_time,
                        message="",
                        priority="medium"
                    )
                    
            elif followup_type == "DAILY_NURTURING":
                # Continuar nurturing por 7 dias
                attempt = current_followup.get('attempt', 0)
                if attempt < 7:
                    next_time = datetime.now() + timedelta(hours=24)
                    await self._create_followup(
                        lead_id=lead['id'],
                        followup_type="DAILY_NURTURING",
                        scheduled_at=next_time,
                        message="",
                        priority="low",
                        attempt=attempt + 1
                    )
                    
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
                'created_at': datetime.now().isoformat()
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
                'failed_at': datetime.now().isoformat(),
                'error_reason': reason
            }).eq('id', followup_id).execute()
            
        except Exception as e:
            logger.error(f"Erro ao marcar follow-up como falho: {e}")
    
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

# Singleton
followup_executor_service = FollowUpExecutorService()