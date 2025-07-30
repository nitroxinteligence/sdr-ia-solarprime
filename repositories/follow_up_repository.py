"""
Follow-up Repository
====================
Repositório para gerenciar follow-ups de leads
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from loguru import logger

from models.base import BaseDBModel
from repositories.base import BaseRepository
from services.database import db


class FollowUp(BaseDBModel):
    """Modelo de Follow-up"""
    lead_id: UUID
    follow_up_number: int
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    status: str = "scheduled"  # scheduled, sent, failed, cancelled
    message: str
    response: Optional[str] = None
    cancel_reason: Optional[str] = None


class FollowUpRepository(BaseRepository[FollowUp]):
    """Repositório de Follow-ups"""
    
    def __init__(self):
        super().__init__(FollowUp, "follow_ups")
    
    async def create(self, follow_up_data: Dict[str, Any]) -> FollowUp:
        """Cria novo follow-up"""
        try:
            result = await self.client.table(self.table_name)\
                .insert(follow_up_data)\
                .execute()
            
            if result.data:
                return FollowUp(**result.data[0])
            
            raise Exception("Falha ao criar follow-up")
            
        except Exception as e:
            logger.error(f"Erro ao criar follow-up: {e}")
            raise
    
    async def get_by_lead_and_number(
        self,
        lead_id: UUID,
        follow_up_number: int
    ) -> Optional[FollowUp]:
        """Busca follow-up específico"""
        try:
            result = await self.client.table(self.table_name)\
                .select("*")\
                .eq("lead_id", str(lead_id))\
                .eq("follow_up_number", follow_up_number)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return FollowUp(**result.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar follow-up: {e}")
            return None
    
    async def get_last_follow_up(self, lead_id: UUID) -> Optional[FollowUp]:
        """Busca último follow-up de um lead"""
        try:
            result = await self.client.table(self.table_name)\
                .select("*")\
                .eq("lead_id", str(lead_id))\
                .order("follow_up_number", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return FollowUp(**result.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar último follow-up: {e}")
            return None
    
    async def update_status(
        self,
        lead_id: str,
        follow_up_number: int,
        status: str,
        response: Optional[str] = None
    ) -> bool:
        """Atualiza status do follow-up"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if status == "sent":
                update_data["sent_at"] = datetime.now().isoformat()
            
            if response:
                update_data["response"] = response
            
            result = await self.client.table(self.table_name)\
                .update(update_data)\
                .eq("lead_id", lead_id)\
                .eq("follow_up_number", follow_up_number)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do follow-up: {e}")
            return False
    
    async def cancel_pending_follow_ups(
        self,
        lead_id: str,
        reason: str
    ) -> int:
        """Cancela todos os follow-ups pendentes de um lead"""
        try:
            update_data = {
                "status": "cancelled",
                "cancel_reason": reason,
                "updated_at": datetime.now().isoformat()
            }
            
            result = await self.client.table(self.table_name)\
                .update(update_data)\
                .eq("lead_id", lead_id)\
                .eq("status", "scheduled")\
                .execute()
            
            cancelled_count = len(result.data)
            logger.info(f"Cancelados {cancelled_count} follow-ups para lead {lead_id}")
            
            return cancelled_count
            
        except Exception as e:
            logger.error(f"Erro ao cancelar follow-ups: {e}")
            return 0
    
    async def get_pending_follow_ups(
        self,
        limit: int = 100
    ) -> List[FollowUp]:
        """Lista follow-ups pendentes"""
        try:
            result = await self.client.table(self.table_name)\
                .select("*")\
                .eq("status", "scheduled")\
                .lte("scheduled_at", datetime.now().isoformat())\
                .order("scheduled_at")\
                .limit(limit)\
                .execute()
            
            return [FollowUp(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Erro ao buscar follow-ups pendentes: {e}")
            return []
    
    async def get_follow_up_stats(self, days: int = 30) -> Dict[str, Any]:
        """Obtém estatísticas de follow-ups"""
        try:
            since_date = datetime.now().replace(hour=0, minute=0, second=0)
            since_date = since_date.replace(day=since_date.day - days)
            
            # Total de follow-ups
            total_result = await self.client.table(self.table_name)\
                .select("id", count="exact")\
                .gte("created_at", since_date.isoformat())\
                .execute()
            
            # Follow-ups enviados
            sent_result = await self.client.table(self.table_name)\
                .select("id", count="exact")\
                .eq("status", "sent")\
                .gte("created_at", since_date.isoformat())\
                .execute()
            
            # Follow-ups com resposta
            response_result = await self.client.table(self.table_name)\
                .select("id", count="exact")\
                .neq("response", None)\
                .gte("created_at", since_date.isoformat())\
                .execute()
            
            return {
                "total": total_result.count or 0,
                "sent": sent_result.count or 0,
                "with_response": response_result.count or 0,
                "response_rate": (response_result.count / sent_result.count * 100) if sent_result.count > 0 else 0,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                "total": 0,
                "sent": 0,
                "with_response": 0,
                "response_rate": 0,
                "period_days": days
            }


# Instância global
follow_up_repository = FollowUpRepository()