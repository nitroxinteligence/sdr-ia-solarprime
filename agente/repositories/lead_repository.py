"""
Repository para gerenciamento de leads
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from loguru import logger

from ..core.types import Lead, LeadStage, LeadQualification, PropertyType, UrgencyLevel
from ..core.logger import setup_module_logger
from ..services import get_supabase_service, get_kommo_service
from ..utils.validators import validate_phone_number, validate_qualification_score
from ..utils.formatters import format_phone_number

logger = setup_module_logger(__name__)

# Singleton instance
_lead_repository_instance = None


class LeadRepository:
    """Repository para operações com leads"""
    
    def __init__(self):
        """Inicializa o repository com as dependências necessárias"""
        self.supabase = get_supabase_service()
        self.kommo = get_kommo_service()
        logger.info("LeadRepository inicializado")
    
    async def create_lead(
        self, 
        phone: str, 
        name: Optional[str] = None,
        **kwargs
    ) -> Lead:
        """
        Cria um novo lead com validação e profile associado
        
        Args:
            phone: Número de telefone do lead
            name: Nome do lead (opcional)
            **kwargs: Campos adicionais do lead
            
        Returns:
            Lead criado
            
        Raises:
            ValueError: Se o telefone for inválido
            Exception: Se houver erro ao criar o lead
        """
        # Valida telefone
        is_valid, error_msg = validate_phone_number(phone)
        if not is_valid:
            logger.error(f"Telefone inválido: {phone} - {error_msg}")
            raise ValueError(f"Telefone inválido: {error_msg}")
        
        # Formata telefone
        formatted_phone = format_phone_number(phone)
        
        # Verifica se lead já existe
        existing_lead = await self.get_lead_by_phone(formatted_phone)
        if existing_lead:
            logger.info(f"Lead já existe para telefone {formatted_phone}")
            return existing_lead
        
        try:
            # Cria profile primeiro
            profile_data = {
                "phone_number": formatted_phone,
                "name": name,
                "created_at": datetime.now()
            }
            
            profile_result = await self.supabase.create_profile(profile_data)
            if not profile_result or "error" in profile_result:
                raise Exception(f"Erro ao criar profile: {profile_result.get('error', 'Unknown error')}")
            
            profile_id = profile_result["data"]["id"]
            logger.info(f"Profile criado com ID: {profile_id}")
            
            # Cria lead
            lead_data = {
                "profile_id": profile_id,
                "phone_number": formatted_phone,
                "name": name,
                "current_stage": LeadStage.INITIAL_CONTACT.value,
                "qualification_score": 0,
                "interested": True,
                "created_at": datetime.now(),
                **kwargs
            }
            
            # Remove campos que não devem ir direto para o banco
            lead_data.pop("email", None)
            lead_data.pop("document", None)
            lead_data.pop("property_type", None)
            lead_data.pop("address", None)
            lead_data.pop("bill_value", None)
            lead_data.pop("consumption_kwh", None)
            
            result = await self.supabase.create_lead(lead_data)
            if not result or "error" in result:
                # Rollback: deleta profile se lead falhar
                await self.supabase.delete_profile(profile_id)
                raise Exception(f"Erro ao criar lead: {result.get('error', 'Unknown error')}")
            
            # Converte para modelo Lead
            lead = Lead(**result["data"])
            logger.info(f"Lead criado com sucesso: {lead.id}")
            
            # Sincroniza com Kommo
            await self.sync_with_kommo(lead)
            
            return lead
            
        except Exception as e:
            logger.error(f"Erro ao criar lead: {e}")
            raise
    
    async def get_lead_by_phone(self, phone: str) -> Optional[Lead]:
        """
        Busca lead por telefone com dados de qualificação
        
        Args:
            phone: Número de telefone
            
        Returns:
            Lead encontrado ou None
        """
        try:
            # Formata telefone
            formatted_phone = format_phone_number(phone)
            
            # Busca lead
            result = await self.supabase.get_lead_by_phone(formatted_phone)
            if not result or "error" in result or not result.get("data"):
                return None
            
            lead_data = result["data"]
            
            # Busca dados de qualificação se existir
            if lead_data.get("id"):
                qual_result = await self.supabase.get_lead_qualification(lead_data["id"])
                if qual_result and "data" in qual_result and qual_result["data"]:
                    # Adiciona dados de qualificação ao lead
                    qualification = qual_result["data"]
                    lead_data.update({
                        "has_own_property": qualification.get("has_own_property"),
                        "decision_maker": qualification.get("decision_maker"),
                        "urgency_level": qualification.get("urgency_level"),
                        "objections": qualification.get("objections", []),
                        "extracted_data": qualification.get("extracted_data", {})
                    })
            
            # Converte para modelo Lead
            lead = Lead(**lead_data)
            logger.debug(f"Lead encontrado: {lead.id}")
            
            return lead
            
        except Exception as e:
            logger.error(f"Erro ao buscar lead por telefone {phone}: {e}")
            return None
    
    async def update_lead_stage(
        self, 
        phone: str, 
        stage: LeadStage
    ) -> Lead:
        """
        Atualiza o estágio do lead com validação de transições
        
        Args:
            phone: Número de telefone do lead
            stage: Novo estágio
            
        Returns:
            Lead atualizado
            
        Raises:
            ValueError: Se a transição for inválida
            Exception: Se o lead não for encontrado
        """
        # Busca lead atual
        lead = await self.get_lead_by_phone(phone)
        if not lead:
            raise Exception(f"Lead não encontrado para telefone {phone}")
        
        # Valida transição de stage
        current_stage = LeadStage(lead.current_stage)
        if not self._is_valid_stage_transition(current_stage, stage):
            logger.warning(
                f"Transição inválida de {current_stage.value} para {stage.value}"
            )
            raise ValueError(
                f"Transição inválida de {current_stage.value} para {stage.value}"
            )
        
        try:
            # Atualiza stage
            update_data = {
                "current_stage": stage.value,
                "updated_at": datetime.now()
            }
            
            # Se mudando para NOT_INTERESTED ou LOST, marca como não interessado
            if stage in [LeadStage.NOT_INTERESTED, LeadStage.LOST]:
                update_data["interested"] = False
            
            result = await self.supabase.update_lead(lead.id, update_data)
            if not result or "error" in result:
                raise Exception(f"Erro ao atualizar stage: {result.get('error', 'Unknown error')}")
            
            # Atualiza objeto lead
            lead.current_stage = stage
            lead.updated_at = datetime.now()
            if stage in [LeadStage.NOT_INTERESTED, LeadStage.LOST]:
                lead.interested = False
            
            logger.info(f"Lead {lead.id} atualizado para stage {stage.value}")
            
            # Sincroniza com Kommo ao mudar stage
            await self.sync_with_kommo(lead)
            
            return lead
            
        except Exception as e:
            logger.error(f"Erro ao atualizar stage do lead: {e}")
            raise
    
    async def qualify_lead(
        self, 
        phone: str, 
        qualification_data: Dict[str, Any]
    ) -> Lead:
        """
        Atualiza dados de qualificação e recalcula score
        
        Args:
            phone: Número de telefone do lead
            qualification_data: Dados de qualificação
            
        Returns:
            Lead atualizado com novo score
        """
        # Busca lead
        lead = await self.get_lead_by_phone(phone)
        if not lead:
            raise Exception(f"Lead não encontrado para telefone {phone}")
        
        try:
            # Prepara dados de qualificação
            qual_data = {
                "lead_id": lead.id,
                "has_own_property": qualification_data.get("has_own_property"),
                "decision_maker": qualification_data.get("decision_maker"),
                "urgency_level": qualification_data.get("urgency_level"),
                "objections": qualification_data.get("objections", []),
                "solutions_presented": qualification_data.get("solutions_presented", []),
                "extracted_data": qualification_data.get("extracted_data", {}),
                "qualification_date": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Cria ou atualiza qualificação
            qual_result = await self.supabase.get_lead_qualification(lead.id)
            if qual_result and "data" in qual_result and qual_result["data"]:
                # Atualiza existente
                result = await self.supabase.update_lead_qualification(
                    qual_result["data"]["id"], 
                    qual_data
                )
            else:
                # Cria nova
                result = await self.supabase.create_lead_qualification(qual_data)
            
            if not result or "error" in result:
                raise Exception(f"Erro ao salvar qualificação: {result.get('error', 'Unknown error')}")
            
            # Atualiza lead com dados de qualificação
            lead_update = {
                "property_type": qualification_data.get("property_type"),
                "address": qualification_data.get("address"),
                "bill_value": qualification_data.get("bill_value"),
                "consumption_kwh": qualification_data.get("consumption_kwh"),
                "email": qualification_data.get("email"),
                "document": qualification_data.get("document"),
                "updated_at": datetime.now()
            }
            
            # Remove campos None
            lead_update = {k: v for k, v in lead_update.items() if v is not None}
            
            # Calcula novo score
            score = await self.calculate_qualification_score(lead)
            lead_update["qualification_score"] = score
            
            # Atualiza lead
            await self.supabase.update_lead(lead.id, lead_update)
            
            # Atualiza objeto lead
            for key, value in lead_update.items():
                if hasattr(lead, key):
                    setattr(lead, key, value)
            
            logger.info(f"Lead {lead.id} qualificado com score {score}")
            
            # Se score alto, marca como qualificado
            if score >= 70 and lead.current_stage == LeadStage.QUALIFYING:
                await self.update_lead_stage(phone, LeadStage.QUALIFIED)
            
            # Sincroniza com Kommo
            await self.sync_with_kommo(lead)
            
            return lead
            
        except Exception as e:
            logger.error(f"Erro ao qualificar lead: {e}")
            raise
    
    async def get_leads_by_stage(
        self, 
        stage: LeadStage, 
        limit: int = 100
    ) -> List[Lead]:
        """
        Busca leads por estágio
        
        Args:
            stage: Estágio para filtrar
            limit: Limite de resultados
            
        Returns:
            Lista de leads no estágio especificado
        """
        try:
            result = await self.supabase.get_leads_by_stage(stage.value, limit)
            if not result or "error" in result:
                logger.error(f"Erro ao buscar leads por stage: {result.get('error', 'Unknown error')}")
                return []
            
            leads = []
            for lead_data in result.get("data", []):
                try:
                    lead = Lead(**lead_data)
                    leads.append(lead)
                except Exception as e:
                    logger.warning(f"Erro ao converter lead {lead_data.get('id')}: {e}")
            
            logger.info(f"Encontrados {len(leads)} leads no stage {stage.value}")
            return leads
            
        except Exception as e:
            logger.error(f"Erro ao buscar leads por stage: {e}")
            return []
    
    async def mark_as_lost(self, phone: str, reason: str) -> Lead:
        """
        Marca lead como perdido com motivo
        
        Args:
            phone: Número de telefone do lead
            reason: Motivo da perda
            
        Returns:
            Lead atualizado
        """
        # Busca lead
        lead = await self.get_lead_by_phone(phone)
        if not lead:
            raise Exception(f"Lead não encontrado para telefone {phone}")
        
        try:
            # Atualiza para LOST
            lead = await self.update_lead_stage(phone, LeadStage.LOST)
            
            # Salva motivo nos dados extras
            update_data = {
                "lost_reason": reason,
                "lost_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            await self.supabase.update_lead(lead.id, update_data)
            
            logger.info(f"Lead {lead.id} marcado como perdido: {reason}")
            
            # Atualiza no Kommo
            if lead.kommo_lead_id:
                await self.kommo.update_lead_stage(
                    lead.kommo_lead_id,
                    self.kommo.STAGE_LOST,
                    note=f"Motivo: {reason}"
                )
            
            return lead
            
        except Exception as e:
            logger.error(f"Erro ao marcar lead como perdido: {e}")
            raise
    
    async def sync_with_kommo(self, lead: Lead) -> bool:
        """
        Sincroniza lead com Kommo CRM
        
        Args:
            lead: Lead para sincronizar
            
        Returns:
            True se sincronizado com sucesso
        """
        try:
            # Mapeia stage para Kommo
            stage_mapping = {
                LeadStage.INITIAL_CONTACT: self.kommo.STAGE_INCOMING_LEAD,
                LeadStage.IDENTIFYING: self.kommo.STAGE_INCOMING_LEAD,
                LeadStage.QUALIFYING: self.kommo.STAGE_FIRST_CONTACT,
                LeadStage.QUALIFIED: self.kommo.STAGE_FIRST_CONTACT,
                LeadStage.SCHEDULING: self.kommo.STAGE_DISCUSSION,
                LeadStage.SCHEDULED: self.kommo.STAGE_DECISION,
                LeadStage.NOT_INTERESTED: self.kommo.STAGE_LOST,
                LeadStage.LOST: self.kommo.STAGE_LOST
            }
            
            kommo_stage = stage_mapping.get(
                LeadStage(lead.current_stage), 
                self.kommo.STAGE_INCOMING_LEAD
            )
            
            # Prepara dados customizados
            custom_fields = {}
            if lead.property_type:
                custom_fields["property_type"] = lead.property_type
            if lead.bill_value:
                custom_fields["bill_value"] = str(lead.bill_value)
            if lead.consumption_kwh:
                custom_fields["consumption_kwh"] = str(lead.consumption_kwh)
            if lead.address:
                custom_fields["address"] = lead.address
            
            # Cria ou atualiza no Kommo
            if lead.kommo_lead_id:
                # Atualiza existente
                success = await self.kommo.update_lead_stage(
                    lead.kommo_lead_id,
                    kommo_stage
                )
                
                if custom_fields:
                    await self.kommo.update_lead(
                        lead.kommo_lead_id,
                        custom_fields=custom_fields
                    )
            else:
                # Cria novo
                kommo_lead = await self.kommo.create_lead(
                    name=lead.name or lead.phone_number,
                    phone=lead.phone_number,
                    stage_id=kommo_stage,
                    custom_fields=custom_fields,
                    tags=["WhatsApp", "SDR Bot"]
                )
                
                if kommo_lead and kommo_lead.id:
                    # Salva ID do Kommo no lead
                    await self.supabase.update_lead(
                        lead.id,
                        {"kommo_lead_id": str(kommo_lead.id)}
                    )
                    lead.kommo_lead_id = str(kommo_lead.id)
                    success = True
                else:
                    success = False
            
            if success:
                logger.info(f"Lead {lead.id} sincronizado com Kommo")
            else:
                logger.warning(f"Falha ao sincronizar lead {lead.id} com Kommo")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar com Kommo: {e}")
            return False
    
    async def calculate_qualification_score(self, lead: Lead) -> int:
        """
        Calcula score de qualificação do lead
        
        Pontuação:
        - Propriedade própria: +30
        - Decisor: +20
        - Urgência alta: +30
        - Sem objeções: +20
        
        Args:
            lead: Lead para calcular score
            
        Returns:
            Score de 0 a 100
        """
        score = 0
        
        try:
            # Busca dados de qualificação
            qual_result = await self.supabase.get_lead_qualification(lead.id)
            if not qual_result or "error" in qual_result or not qual_result.get("data"):
                return 0
            
            qualification = qual_result["data"]
            
            # Propriedade própria (+30)
            if qualification.get("has_own_property") is True:
                score += 30
                logger.debug(f"Lead {lead.id}: +30 por propriedade própria")
            
            # Decisor (+20)
            if qualification.get("decision_maker") is True:
                score += 20
                logger.debug(f"Lead {lead.id}: +20 por ser decisor")
            
            # Urgência alta (+30)
            if qualification.get("urgency_level") == UrgencyLevel.HIGH.value:
                score += 30
                logger.debug(f"Lead {lead.id}: +30 por urgência alta")
            elif qualification.get("urgency_level") == UrgencyLevel.MEDIUM.value:
                score += 15
                logger.debug(f"Lead {lead.id}: +15 por urgência média")
            
            # Sem objeções (+20)
            objections = qualification.get("objections", [])
            if not objections or len(objections) == 0:
                score += 20
                logger.debug(f"Lead {lead.id}: +20 por não ter objeções")
            elif len(objections) == 1:
                score += 10
                logger.debug(f"Lead {lead.id}: +10 por ter apenas 1 objeção")
            
            # Valida score
            is_valid, error_msg = validate_qualification_score(score)
            if not is_valid:
                logger.warning(f"Score inválido calculado: {score} - {error_msg}")
                score = max(0, min(100, score))
            
            logger.info(f"Score calculado para lead {lead.id}: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Erro ao calcular score: {e}")
            return 0
    
    def _is_valid_stage_transition(
        self, 
        current: LeadStage, 
        new: LeadStage
    ) -> bool:
        """
        Valida se a transição de estágio é permitida
        
        Args:
            current: Estágio atual
            new: Novo estágio
            
        Returns:
            True se a transição é válida
        """
        # Não pode voltar de SCHEDULED para QUALIFYING
        if current == LeadStage.SCHEDULED and new in [
            LeadStage.QUALIFYING,
            LeadStage.IDENTIFYING,
            LeadStage.INITIAL_CONTACT
        ]:
            return False
        
        # Não pode voltar de LOST ou NOT_INTERESTED
        if current in [LeadStage.LOST, LeadStage.NOT_INTERESTED]:
            return False
        
        # Outras transições são permitidas
        return True


def get_lead_repository() -> LeadRepository:
    """
    Retorna instância singleton do LeadRepository
    
    Returns:
        Instância do LeadRepository
    """
    global _lead_repository_instance
    
    if _lead_repository_instance is None:
        _lead_repository_instance = LeadRepository()
    
    return _lead_repository_instance