"""
Qualification Kommo Integration
===============================
Integração entre sistema de qualificação e Kommo CRM
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from services.kommo_service import kommo_service
from models.kommo_models import KommoLead, LeadStatus, SolutionType
from models.lead import Lead
from repositories.lead_repository import lead_repository
from config.config import get_config


class QualificationKommoIntegration:
    """Integra qualificação de leads com Kommo CRM"""
    
    def __init__(self):
        self.config = get_config()
        self.kommo = kommo_service
        
        # Mapeamento de estágios do agente para status Kommo
        self.stage_to_status_map = {
            "INITIAL_CONTACT": LeadStatus.NEW,
            "IDENTIFICATION": LeadStatus.IN_QUALIFICATION,
            "QUALIFICATION": LeadStatus.IN_QUALIFICATION,
            "ENERGY_BILL_ANALYSIS": LeadStatus.QUALIFIED,
            "SOLUTION_DISCOVERY": LeadStatus.QUALIFIED,
            "SCHEDULING": LeadStatus.MEETING_SCHEDULED,
            "FOLLOW_UP": LeadStatus.IN_QUALIFICATION
        }
        
        # Mapeamento de tipos de solução
        self.solution_type_map = {
            "usina_propria": SolutionType.OWN_PLANT,
            "usina_parceira": SolutionType.PARTNER_PLANT,
            "desconto_alto": SolutionType.DISCOUNT_HIGH,
            "desconto_baixo": SolutionType.DISCOUNT_LOW,
            "investimento": SolutionType.INVESTMENT
        }
        
        logger.info("Integração Qualificação-Kommo inicializada")
    
    async def sync_lead_to_kommo(
        self,
        lead: Lead,
        ai_notes: str = "",
        current_stage: str = "INITIAL_CONTACT"
    ) -> Optional[str]:
        """
        Sincroniza lead do banco local para Kommo
        
        Returns:
            kommo_lead_id se sucesso, None se falhar
        """
        try:
            if not self.kommo:
                logger.warning("Serviço Kommo não disponível")
                return None
            
            # Preparar dados do lead
            kommo_lead = self._prepare_kommo_lead(lead, ai_notes, current_stage)
            
            # Criar ou atualizar no Kommo
            result = await self.kommo.create_or_update_lead(kommo_lead)
            
            if result and "id" in result:
                kommo_lead_id = str(result["id"])
                
                # Atualizar lead local com ID do Kommo
                await lead_repository.update(lead.id, {"kommo_lead_id": kommo_lead_id})
                
                logger.info(f"Lead sincronizado com Kommo: {lead.name} (ID: {kommo_lead_id})")
                return kommo_lead_id
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar lead com Kommo: {str(e)}")
            return None
    
    async def update_lead_stage(
        self,
        lead: Lead,
        new_stage: str,
        notes: str = ""
    ) -> bool:
        """Atualiza estágio do lead no Kommo"""
        try:
            if not self.kommo or not lead.kommo_lead_id:
                return False
            
            # Mapear estágio para status Kommo
            kommo_status = self.stage_to_status_map.get(new_stage, LeadStatus.IN_QUALIFICATION)
            
            # Mover lead no pipeline
            success = await self.kommo.move_lead_stage(
                int(lead.kommo_lead_id),
                kommo_status
            )
            
            if success and notes:
                # Adicionar nota sobre mudança
                await self.kommo.add_note(
                    int(lead.kommo_lead_id),
                    f"Estágio atualizado: {new_stage}\n\n{notes}"
                )
            
            # Adicionar tags baseadas no estágio
            tags = self._get_stage_tags(new_stage)
            if tags:
                await self.kommo.add_tags_to_lead(int(lead.kommo_lead_id), tags)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estágio no Kommo: {str(e)}")
            return False
    
    async def schedule_meeting_kommo(
        self,
        lead: Lead,
        meeting_datetime: datetime,
        notes: str = ""
    ) -> bool:
        """Agenda reunião no Kommo"""
        try:
            if not self.kommo or not lead.kommo_lead_id:
                return False
            
            # Agendar reunião
            success = await self.kommo.schedule_meeting(
                int(lead.kommo_lead_id),
                meeting_datetime,
                notes
            )
            
            if success:
                # Atualizar tags
                await self.kommo.add_tags_to_lead(
                    int(lead.kommo_lead_id),
                    ["Reunião Agendada", "WhatsApp Agendamento"]
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao agendar reunião no Kommo: {str(e)}")
            return False
    
    async def update_qualification_score(
        self,
        lead: Lead,
        score: int,
        factors: Dict[str, Any]
    ) -> bool:
        """Atualiza score de qualificação no Kommo"""
        try:
            if not self.kommo or not lead.kommo_lead_id:
                return False
            
            # Preparar nota com fatores de qualificação
            factors_text = "\n".join([f"- {k}: {v}" for k, v in factors.items()])
            note = f"Score de Qualificação: {score}/100\n\nFatores:\n{factors_text}"
            
            # Adicionar nota
            await self.kommo.add_note(int(lead.kommo_lead_id), note)
            
            # Atualizar tags baseadas no score
            if score >= 80:
                tags = ["Lead Quente", "Alta Prioridade"]
            elif score >= 60:
                tags = ["Lead Morno", "Média Prioridade"]
            else:
                tags = ["Lead Frio", "Baixa Prioridade"]
            
            await self.kommo.add_tags_to_lead(int(lead.kommo_lead_id), tags)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar score no Kommo: {str(e)}")
            return False
    
    async def add_whatsapp_interaction(
        self,
        lead: Lead,
        message_type: str,
        content: str,
        response: str
    ) -> bool:
        """Adiciona interação do WhatsApp como nota no Kommo"""
        try:
            if not self.kommo or not lead.kommo_lead_id:
                return False
            
            # Formatar nota
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            note = f"WhatsApp - {timestamp}\n\n"
            note += f"Tipo: {message_type}\n"
            note += f"Cliente: {content[:200]}...\n" if len(content) > 200 else f"Cliente: {content}\n"
            note += f"\nIA: {response[:200]}..." if len(response) > 200 else f"\nIA: {response}"
            
            # Adicionar nota
            return await self.kommo.add_note(int(lead.kommo_lead_id), note)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar interação no Kommo: {str(e)}")
            return False
    
    async def mark_lead_lost(
        self,
        lead: Lead,
        reason: str
    ) -> bool:
        """Marca lead como perdido no Kommo"""
        try:
            if not self.kommo or not lead.kommo_lead_id:
                return False
            
            # Mover para estágio perdido
            success = await self.kommo.move_lead_stage(
                int(lead.kommo_lead_id),
                LeadStatus.LOST
            )
            
            if success:
                # Adicionar nota com motivo
                await self.kommo.add_note(
                    int(lead.kommo_lead_id),
                    f"Lead Perdido\n\nMotivo: {reason}"
                )
                
                # Adicionar tags
                await self.kommo.add_tags_to_lead(
                    int(lead.kommo_lead_id),
                    ["Lead Perdido", "Sem Interesse"]
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao marcar lead como perdido: {str(e)}")
            return False
    
    # Métodos auxiliares privados
    
    def _prepare_kommo_lead(
        self,
        lead: Lead,
        ai_notes: str,
        current_stage: str
    ) -> KommoLead:
        """Prepara dados do lead para envio ao Kommo"""
        # Determinar tipo de solução
        solution_type = None
        if hasattr(lead, 'solution_type') and lead.solution_type:
            solution_type = self.solution_type_map.get(lead.solution_type)
        
        # Preparar tags
        tags = ["WhatsApp Lead"]
        if lead.qualification_score and lead.qualification_score >= 70:
            tags.append("Lead Qualificado")
        
        # Criar objeto KommoLead
        return KommoLead(
            name=lead.name or "Não identificado",
            phone=lead.phone_number,
            whatsapp=lead.phone_number,
            email=lead.email,
            energy_bill_value=float(lead.bill_value) if lead.bill_value else 0.0,
            solution_type=solution_type,
            current_discount=getattr(lead, 'current_discount', None),
            competitor=getattr(lead, 'competitor', None),
            qualification_score=lead.qualification_score or 0,
            ai_notes=ai_notes or "Lead criado via WhatsApp",
            tags=tags
        )
    
    def _get_stage_tags(self, stage: str) -> List[str]:
        """Retorna tags baseadas no estágio"""
        tag_map = {
            "IDENTIFICATION": ["Em Identificação"],
            "QUALIFICATION": ["Em Qualificação"],
            "ENERGY_BILL_ANALYSIS": ["Conta Analisada", "Qualificado"],
            "SOLUTION_DISCOVERY": ["Solução Identificada"],
            "SCHEDULING": ["Agendamento em Progresso"],
            "FOLLOW_UP": ["Follow-up Necessário"]
        }
        
        return tag_map.get(stage, [])


# Instância global
qualification_kommo_integration = QualificationKommoIntegration()