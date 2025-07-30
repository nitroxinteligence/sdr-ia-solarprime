"""
Kommo Follow-up Service
=======================
Serviço de follow-up automatizado integrado com Kommo CRM
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
from celery import Celery
from celery.schedules import crontab

from config.config import get_config
from config.messages import get_follow_up_message
from services.kommo_service import kommo_service
from services.qualification_kommo_integration import qualification_kommo_integration
from models.kommo_models import KommoTask, TaskType, LeadStatus
from repositories.lead_repository import lead_repository
from repositories.follow_up_repository import follow_up_repository
from services.tasks import celery_app


class KommoFollowUpService:
    """Gerencia follow-ups automatizados via Kommo"""
    
    def __init__(self):
        self.config = get_config()
        self.kommo = kommo_service
        
        # Configurações de follow-up
        self.follow_up_delays = {
            1: timedelta(minutes=30),    # 1º follow-up após 30 minutos
            2: timedelta(hours=24),      # 2º follow-up após 24 horas
            3: timedelta(hours=72),      # 3º follow-up após 72 horas
            4: timedelta(days=7)         # 4º follow-up após 7 dias
        }
        
        # Usar mensagens humanizadas centralizadas
        # Os templates agora vêm do módulo messages.py com múltiplas variações
        
        logger.info("Serviço de follow-up Kommo inicializado")
    
    async def schedule_follow_up(
        self,
        lead_id: str,
        follow_up_number: int = 1,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Agenda follow-up para um lead
        
        Args:
            lead_id: ID do lead no banco local
            follow_up_number: Número do follow-up (1-4)
            custom_message: Mensagem customizada (opcional)
        
        Returns:
            True se agendado com sucesso
        """
        try:
            # Buscar lead
            lead = await lead_repository.get(lead_id)
            if not lead:
                logger.error(f"Lead {lead_id} não encontrado")
                return False
            
            # Verificar se lead está interessado
            if not lead.interested:
                logger.info(f"Lead {lead_id} marcado como não interessado - skip follow-up")
                return False
            
            # Calcular horário do follow-up
            delay = self.follow_up_delays.get(follow_up_number, timedelta(hours=24))
            scheduled_time = datetime.now() + delay
            
            # Criar tarefa no Kommo se lead tem ID
            if lead.kommo_lead_id and self.kommo:
                task = KommoTask(
                    text=f"Follow-up WhatsApp #{follow_up_number} - Automático",
                    task_type=TaskType.CALL,
                    complete_till=scheduled_time,
                    entity_type="leads",
                    entity_id=int(lead.kommo_lead_id)
                )
                
                kommo_task = await self.kommo.create_task(task)
                
                if kommo_task:
                    logger.info(f"Tarefa criada no Kommo para follow-up #{follow_up_number}")
            
            # Agendar tarefa no Celery
            task_name = f"follow_up_{lead_id}_{follow_up_number}"
            
            send_follow_up_task.apply_async(
                args=[lead_id, follow_up_number, custom_message],
                eta=scheduled_time,
                task_id=task_name
            )
            
            # Registrar follow-up no banco
            await follow_up_repository.create({
                "lead_id": lead_id,
                "follow_up_number": follow_up_number,
                "scheduled_at": scheduled_time,
                "status": "scheduled",
                "message": custom_message or get_follow_up_message(self._get_interval_key(follow_up_number), lead.name or "")
            })
            
            logger.info(f"Follow-up #{follow_up_number} agendado para {scheduled_time}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar follow-up: {str(e)}")
            return False
    
    async def execute_follow_up(
        self,
        lead_id: str,
        follow_up_number: int,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Executa follow-up enviando mensagem via WhatsApp
        
        Returns:
            True se enviado com sucesso
        """
        try:
            # Buscar lead
            lead = await lead_repository.get(lead_id)
            if not lead:
                return False
            
            # Verificar se ainda está interessado
            if not lead.interested:
                logger.info(f"Lead {lead_id} não está mais interessado - cancelando follow-up")
                return False
            
            # Preparar mensagem
            if custom_message:
                message = custom_message
            else:
                # Usar mensagem humanizada com variação automática
                interval_key = self._get_interval_key(follow_up_number)
                message = get_follow_up_message(interval_key, lead.name or "")
            
            # Enviar via WhatsApp
            # Importação local para evitar circular import
            from services.whatsapp_service import whatsapp_service
            success = await whatsapp_service.send_text_message(
                lead.phone_number,
                message
            )
            
            if success:
                # Atualizar follow-up count no lead
                await lead_repository.update(lead.id, {
                    "follow_up_count": (lead.follow_up_count or 0) + 1,
                    "last_follow_up_at": datetime.now()
                })
                
                # Atualizar no Kommo
                if lead.kommo_lead_id and self.kommo:
                    # Adicionar nota sobre follow-up
                    await self.kommo.add_note(
                        int(lead.kommo_lead_id),
                        f"Follow-up #{follow_up_number} enviado via WhatsApp\n\nMensagem: {message}"
                    )
                    
                    # Adicionar tag
                    await self.kommo.add_tags_to_lead(
                        int(lead.kommo_lead_id),
                        [f"Follow-up {follow_up_number}"]
                    )
                
                # Marcar follow-up como enviado
                await follow_up_repository.update_status(lead_id, follow_up_number, "sent")
                
                # Agendar próximo follow-up se aplicável
                if follow_up_number < 4 and lead.interested:
                    await self.schedule_follow_up(lead_id, follow_up_number + 1)
                
                logger.info(f"Follow-up #{follow_up_number} enviado para {lead.phone_number}")
                return True
            else:
                logger.error(f"Falha ao enviar follow-up para {lead.phone_number}")
                # Marcar como falho
                await follow_up_repository.update_status(lead_id, follow_up_number, "failed")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao executar follow-up: {str(e)}")
            return False
    
    async def cancel_follow_ups(self, lead_id: str, reason: str = "Lead convertido") -> bool:
        """
        Cancela todos os follow-ups pendentes de um lead
        
        Args:
            lead_id: ID do lead
            reason: Motivo do cancelamento
        
        Returns:
            True se cancelado com sucesso
        """
        try:
            # Cancelar tarefas do Celery
            for i in range(1, 5):
                task_id = f"follow_up_{lead_id}_{i}"
                celery_app.control.revoke(task_id, terminate=True)
            
            # Atualizar status no banco
            await follow_up_repository.cancel_pending_follow_ups(lead_id, reason)
            
            # Adicionar nota no Kommo
            lead = await lead_repository.get(lead_id)
            if lead and lead.kommo_lead_id and self.kommo:
                await self.kommo.add_note(
                    int(lead.kommo_lead_id),
                    f"Follow-ups cancelados\n\nMotivo: {reason}"
                )
            
            logger.info(f"Follow-ups cancelados para lead {lead_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cancelar follow-ups: {str(e)}")
            return False
    
    async def process_kommo_task_trigger(self, kommo_task: Dict[str, Any]) -> bool:
        """
        Processa tarefa do Kommo para disparar follow-up
        
        Args:
            kommo_task: Dados da tarefa do Kommo
        
        Returns:
            True se processado com sucesso
        """
        try:
            # Extrair informações da tarefa
            lead_id = kommo_task.get("entity_id")
            task_text = kommo_task.get("text", "").lower()
            
            # Verificar se é tarefa de follow-up
            if "follow" not in task_text and "acompanhamento" not in task_text:
                return False
            
            # Buscar lead local pelo kommo_lead_id
            # TODO: Implementar busca por kommo_lead_id no repositório
            
            logger.info(f"Tarefa de follow-up processada do Kommo: {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar tarefa do Kommo: {str(e)}")
            return False
    
    def _get_interval_key(self, follow_up_number: int) -> str:
        """
        Mapeia número do follow-up para chave de intervalo
        
        Args:
            follow_up_number: Número do follow-up (1-4)
            
        Returns:
            Chave do intervalo para buscar mensagem
        """
        interval_map = {
            1: "30_minutos",
            2: "24_horas", 
            3: "48_horas",
            4: "7_dias"
        }
        return interval_map.get(follow_up_number, "24_horas")
    
    async def get_leads_for_follow_up(self) -> List[Dict[str, Any]]:
        """
        Obtém lista de leads que precisam de follow-up
        
        Returns:
            Lista de leads com informações de follow-up
        """
        try:
            # Buscar leads qualificados sem agendamento
            leads = await lead_repository.get_leads_for_followup()
            
            follow_up_list = []
            for lead in leads:
                # Verificar último follow-up
                last_follow_up = await follow_up_repository.get_last_follow_up(lead.id)
                
                # Calcular próximo follow-up
                if not last_follow_up:
                    next_number = 1
                    next_time = datetime.now() + self.follow_up_delays[1]
                else:
                    next_number = last_follow_up.follow_up_number + 1
                    if next_number <= 4:
                        next_time = last_follow_up.sent_at + self.follow_up_delays[next_number]
                    else:
                        continue  # Já fez todos os follow-ups
                
                # Verificar se é hora de fazer follow-up
                if datetime.now() >= next_time:
                    follow_up_list.append({
                        "lead": lead,
                        "follow_up_number": next_number,
                        "scheduled_time": next_time,
                        "overdue_hours": (datetime.now() - next_time).total_seconds() / 3600
                    })
            
            return follow_up_list
            
        except Exception as e:
            logger.error(f"Erro ao buscar leads para follow-up: {str(e)}")
            return []


# Tarefa Celery para follow-up
@celery_app.task(name="send_follow_up")
def send_follow_up_task(lead_id: str, follow_up_number: int, custom_message: Optional[str] = None):
    """Tarefa Celery para enviar follow-up"""
    import asyncio
    
    service = KommoFollowUpService()
    loop = asyncio.get_event_loop()
    
    result = loop.run_until_complete(
        service.execute_follow_up(lead_id, follow_up_number, custom_message)
    )
    
    return result


# Tarefa periódica para verificar follow-ups pendentes
@celery_app.task(name="check_pending_follow_ups")
def check_pending_follow_ups():
    """Verifica e agenda follow-ups pendentes"""
    import asyncio
    
    service = KommoFollowUpService()
    loop = asyncio.get_event_loop()
    
    leads = loop.run_until_complete(service.get_leads_for_follow_up())
    
    scheduled_count = 0
    for item in leads:
        lead = item["lead"]
        follow_up_number = item["follow_up_number"]
        
        success = loop.run_until_complete(
            service.schedule_follow_up(str(lead.id), follow_up_number)
        )
        
        if success:
            scheduled_count += 1
    
    logger.info(f"Follow-ups agendados: {scheduled_count}")
    return scheduled_count


# Configurar tarefa periódica no Celery beat
celery_app.conf.beat_schedule.update({
    'check-follow-ups': {
        'task': 'check_pending_follow_ups',
        'schedule': crontab(minute='*/30'),  # A cada 30 minutos
    }
})


# Instância global
kommo_follow_up_service = KommoFollowUpService()