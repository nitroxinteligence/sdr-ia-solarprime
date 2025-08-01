"""
Lead Repository
===============
Repositório para operações com leads
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from loguru import logger

from models.lead import Lead, LeadCreate, LeadUpdate
from repositories.base import BaseRepository
from services.database import db


class LeadRepository(BaseRepository[Lead]):
    """Repositório de Leads"""
    
    def __init__(self):
        super().__init__(Lead, "leads")
    
    async def get_by_phone(self, phone_number: str) -> Optional[Lead]:
        """Busca lead por telefone"""
        try:
            result = db.leads.select("*").eq("phone_number", phone_number).execute()
            
            if result.data and len(result.data) > 0:
                return Lead(**result.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting lead by phone: {e}")
            raise
    
    async def create_or_update(self, lead_data: LeadCreate) -> Lead:
        """Cria ou atualiza lead baseado no telefone"""
        try:
            # Log para debug
            logger.info(f"create_or_update - phone: '{lead_data.phone_number}' (tamanho: {len(lead_data.phone_number)})")
            
            # Verificar se já existe
            existing = await self.get_by_phone(lead_data.phone_number)
            
            if existing:
                # Atualizar apenas campos fornecidos
                update_data = lead_data.dict(exclude_unset=True)
                return await self.update(existing.id, update_data)
            else:
                # Criar novo
                return await self.create(lead_data.dict())
                
        except Exception as e:
            logger.error(f"Error in create_or_update lead: {e}")
            raise
    
    async def get_by_stage(self, stage: str, limit: int = 100) -> List[Lead]:
        """Lista leads por estágio"""
        return await self.get_all(
            filters={"current_stage": stage},
            limit=limit
        )
    
    async def get_qualified_leads(self, min_score: int = 70) -> List[Lead]:
        """Lista leads qualificados"""
        try:
            result = db.leads.select("*")\
                .gte("qualification_score", min_score)\
                .eq("interested", True)\
                .order("qualification_score", desc=True)\
                .execute()
            
            return [Lead(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting qualified leads: {e}")
            return []
    
    async def update_stage(self, lead_id: UUID, new_stage: str) -> Optional[Lead]:
        """Atualiza estágio do lead"""
        return await self.update(lead_id, {"current_stage": new_stage})
    
    async def update_qualification_score(self, lead_id: UUID, score: int) -> Optional[Lead]:
        """Atualiza score de qualificação"""
        return await self.update(lead_id, {"qualification_score": score})
    
    async def mark_as_not_interested(self, lead_id: UUID) -> Optional[Lead]:
        """Marca lead como não interessado"""
        return await self.update(lead_id, {"interested": False})
    
    async def update_lead(
        self,
        lead_id: UUID,
        **kwargs
    ) -> Optional[Lead]:
        """
        Atualiza lead com campos dinâmicos
        
        Args:
            lead_id: ID do lead
            **kwargs: Campos a atualizar (name, email, meeting_scheduled_at, etc)
            
        Returns:
            Lead atualizado ou None se falhar
        """
        try:
            # Filtrar campos None
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                logger.warning("Nenhum campo para atualizar")
                return await self.get(lead_id)
            
            # Atualizar campos especiais se necessário
            if 'meeting_scheduled_at' in update_data and isinstance(update_data['meeting_scheduled_at'], datetime):
                update_data['meeting_scheduled_at'] = update_data['meeting_scheduled_at'].isoformat()
            
            # Executar update
            return await self.update(lead_id, update_data)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar lead {lead_id}: {e}")
            return None
    
    async def get_lead_by_phone(self, phone_number: str) -> Optional[Lead]:
        """Alias para get_by_phone para compatibilidade"""
        return await self.get_by_phone(phone_number)
    
    async def get_leads_for_followup(self) -> List[Lead]:
        """Lista leads que precisam de follow-up"""
        try:
            # Leads interessados mas não agendados
            result = db.leads.select("*")\
                .eq("interested", True)\
                .neq("current_stage", "SCHEDULING")\
                .neq("current_stage", "SCHEDULED")\
                .order("updated_at", desc=False)\
                .execute()
            
            return [Lead(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting leads for followup: {e}")
            return []
    
    async def search(self, query: str) -> List[Lead]:
        """Busca leads por nome ou telefone"""
        try:
            # Busca por nome ou telefone
            result = db.leads.select("*")\
                .or_(f"name.ilike.%{query}%,phone_number.ilike.%{query}%")\
                .limit(50)\
                .execute()
            
            return [Lead(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error searching leads: {e}")
            return []
    
    async def delete_lead(self, lead_id: UUID) -> bool:
        """Deleta um lead e todas as suas relações"""
        try:
            # Deletar o lead (as relações em cascata devem estar configuradas no banco)
            response = await self.client.table("leads")\
                .delete()\
                .eq("id", str(lead_id))\
                .execute()
            
            logger.info(f"Lead {lead_id} deletado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar lead: {e}")
            return False


# Instância global
lead_repository = LeadRepository()