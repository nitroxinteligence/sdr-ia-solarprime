"""
Follow-up Service
=================
Serviço para gerenciar criação de follow-ups automaticamente
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from loguru import logger

from services.database import supabase_client
from config.agent_config import config as agent_config
from repositories.lead_repository import lead_repository


class FollowUpService:
    """Serviço para gerenciar follow-ups"""
    
    def __init__(self):
        self.supabase = supabase_client
        self.enabled = agent_config.enable_follow_up
        
    async def create_follow_up_after_message(
        self,
        phone_number: str,
        lead_id: Optional[str] = None,
        message_sent: str = None,
        stage: str = None
    ) -> Dict[str, Any]:
        """
        Cria follow-up automático após enviar mensagem para lead
        
        Args:
            phone_number: Número do WhatsApp
            lead_id: ID do lead (opcional, busca pelo telefone se não fornecido)
            message_sent: Mensagem enviada (para contexto)
            stage: Estágio atual do lead
            
        Returns:
            Status da criação do follow-up
        """
        if not self.enabled:
            logger.debug("Sistema de follow-up desabilitado")
            return {"status": "disabled"}
            
        try:
            # Se não tem lead_id, buscar pelo telefone
            if not lead_id:
                lead = await lead_repository.get_by_phone(phone_number)
                if lead:
                    lead_id = str(lead.id)
                else:
                    logger.warning(f"Lead não encontrado para telefone {phone_number}")
                    return {"status": "error", "message": "Lead não encontrado"}
            
            # Verificar se lead já tem reunião agendada
            if stage == 'SCHEDULED':
                logger.info(f"Lead {lead_id} já tem reunião agendada, não criar follow-up")
                return {"status": "skipped", "reason": "already_scheduled"}
            
            # Cancelar follow-ups anteriores pendentes
            await self._cancel_pending_follow_ups(lead_id)
            
            # Calcular tempo do primeiro follow-up (30 minutos configurável)
            first_delay_minutes = agent_config.follow_up_delay_minutes
            scheduled_time = datetime.now() + timedelta(minutes=first_delay_minutes)
            
            # Criar novo follow-up
            follow_up_data = {
                'lead_id': lead_id,
                'type': 'reminder',  # Usar tipo existente por enquanto
                'scheduled_at': scheduled_time.isoformat(),
                'status': 'pending',
                'message': f"Follow-up automático para {phone_number}"  # Mensagem temporária
            }
            
            # Adicionar metadata apenas se o campo existir
            if hasattr(self, '_metadata_field_exists'):
                follow_up_data['metadata'] = {
                    'phone': phone_number,
                    'stage': stage,
                    'last_message': message_sent[:200] if message_sent else None,
                    'created_at': datetime.now().isoformat()
                }
            
            result = self.supabase.table('follow_ups').insert(follow_up_data).execute()
            
            logger.info(
                f"Follow-up criado para lead {lead_id} - "
                f"Tipo: first_contact - "
                f"Agendado para: {scheduled_time.strftime('%H:%M')} ({first_delay_minutes} minutos)"
            )
            
            return {
                "status": "success",
                "follow_up_id": result.data[0]['id'] if result.data else None,
                "scheduled_at": scheduled_time.isoformat(),
                "minutes_until": first_delay_minutes
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar follow-up: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    async def _cancel_pending_follow_ups(self, lead_id: str):
        """Cancela follow-ups pendentes de um lead"""
        try:
            # Buscar follow-ups pendentes
            result = self.supabase.table('follow_ups')\
                .update({'status': 'cancelled'})\
                .eq('lead_id', lead_id)\
                .eq('status', 'pending')\
                .execute()
                
            if result.data:
                logger.info(f"Cancelados {len(result.data)} follow-ups pendentes para lead {lead_id}")
                
        except Exception as e:
            logger.error(f"Erro ao cancelar follow-ups pendentes: {e}")
    
    async def check_follow_up_needed(self, phone_number: str) -> bool:
        """
        Verifica se é necessário criar follow-up para um número
        
        Returns:
            True se deve criar follow-up, False caso contrário
        """
        if not self.enabled:
            return False
            
        try:
            # Buscar lead
            lead = await lead_repository.get_by_phone(phone_number)
            if not lead:
                return False
                
            # Não criar se já tem reunião
            if lead.current_stage == 'SCHEDULED':
                return False
                
            # Não criar se não está interessado
            if not lead.interested:
                return False
                
            # Verificar se já tem follow-up pendente
            result = self.supabase.table('follow_ups')\
                .select('id')\
                .eq('lead_id', str(lead.id))\
                .eq('status', 'pending')\
                .execute()
                
            if result.data:
                logger.debug(f"Lead {lead.id} já tem follow-up pendente")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar necessidade de follow-up: {e}")
            return False
    
    async def get_pending_follow_ups(self, limit: int = 10) -> list:
        """Lista follow-ups pendentes"""
        try:
            now = datetime.now().isoformat()
            
            result = self.supabase.table('follow_ups')\
                .select('*, leads!inner(*)')\
                .eq('status', 'pending')\
                .lte('scheduled_at', now)\
                .order('scheduled_at')\
                .limit(limit)\
                .execute()
                
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Erro ao buscar follow-ups pendentes: {e}")
            return []
    
    async def mark_follow_up_executed(self, follow_up_id: str, result: Dict[str, Any]):
        """Marca follow-up como executado"""
        try:
            self.supabase.table('follow_ups')\
                .update({
                    'status': 'executed',
                    'executed_at': datetime.now().isoformat(),
                    'result': result
                })\
                .eq('id', follow_up_id)\
                .execute()
                
            logger.info(f"Follow-up {follow_up_id} marcado como executado")
            
        except Exception as e:
            logger.error(f"Erro ao marcar follow-up como executado: {e}")


# Instância global
follow_up_service = FollowUpService()