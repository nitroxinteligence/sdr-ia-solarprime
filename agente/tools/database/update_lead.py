"""
Tool para atualizar dados do lead existente
"""

from agno.tools import tool
from loguru import logger
from typing import Optional, Dict, Any, List
from uuid import UUID

from ...repositories import get_lead_repository
from ...core.types import LeadStage, PropertyType, UrgencyLevel
from ...core.logger import setup_module_logger

logger = setup_module_logger(__name__)


@tool(show_result=True)
async def update_lead(
    lead_id: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    property_type: Optional[str] = None,
    address: Optional[str] = None,
    bill_value: Optional[float] = None,
    consumption_kwh: Optional[int] = None,
    stage: Optional[str] = None,
    qualification_score: Optional[int] = None,
    interested: Optional[bool] = None,
    solutions_presented: Optional[List[str]] = None,
    urgency_level: Optional[str] = None,
    objections: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Atualiza dados do lead (qualificação, solução, status)
    
    Args:
        lead_id: ID do lead (UUID)
        phone: Número de telefone (usado se lead_id não fornecido)
        name: Nome do lead
        email: Email do lead
        property_type: Tipo de propriedade (casa, apartamento, comercial, rural)
        address: Endereço da propriedade
        bill_value: Valor da conta de luz
        consumption_kwh: Consumo em kWh
        stage: Estágio atual do lead (INITIAL_CONTACT, IDENTIFYING, QUALIFYING, etc.)
        qualification_score: Score de qualificação (0-100)
        interested: Se o lead está interessado
        solutions_presented: Lista de soluções apresentadas
        urgency_level: Nível de urgência (alta, media, baixa)
        objections: Lista de objeções do lead
    
    Returns:
        Dict com sucesso e dados atualizados do lead
    """
    try:
        lead_repo = get_lead_repository()
        
        # Busca o lead
        if lead_id:
            logger.info(f"Buscando lead por ID: {lead_id}")
            lead = await lead_repo.get_lead_by_id(UUID(lead_id))
        elif phone:
            logger.info(f"Buscando lead por telefone: {phone}")
            lead = await lead_repo.get_lead_by_phone(phone)
        else:
            logger.error("Nem lead_id nem phone foram fornecidos")
            return {
                "success": False,
                "error": "É necessário fornecer lead_id ou phone",
                "error_type": "validation"
            }
        
        if not lead:
            logger.warning(f"Lead não encontrado")
            return {
                "success": False,
                "error": "Lead não encontrado",
                "error_type": "not_found"
            }
        
        # Prepara dados para atualização
        update_data = {}
        
        # Dados básicos
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if address is not None:
            update_data["address"] = address
        if bill_value is not None:
            update_data["bill_value"] = float(bill_value)
        if consumption_kwh is not None:
            update_data["consumption_kwh"] = int(consumption_kwh)
        if interested is not None:
            update_data["interested"] = bool(interested)
        if qualification_score is not None:
            update_data["qualification_score"] = int(qualification_score)
            
        # Tipo de propriedade
        if property_type is not None:
            try:
                prop_type = PropertyType(property_type.lower())
                update_data["property_type"] = prop_type
            except:
                logger.warning(f"Tipo de propriedade inválido: {property_type}")
        
        # Estágio do lead
        if stage is not None:
            try:
                lead_stage = LeadStage(stage)
                update_data["current_stage"] = lead_stage
            except:
                logger.warning(f"Estágio inválido: {stage}")
        
        # Atualiza o lead
        updated_lead = await lead_repo.update_lead(lead.id, update_data)
        
        # Atualiza qualificação se houver dados de qualificação
        qualification_updated = False
        if any([solutions_presented, urgency_level, objections]):
            qual_data = {}
            
            if solutions_presented:
                qual_data["solutions_presented"] = solutions_presented
            if urgency_level:
                try:
                    qual_data["urgency_level"] = UrgencyLevel(urgency_level.lower())
                except:
                    logger.warning(f"Nível de urgência inválido: {urgency_level}")
            if objections:
                qual_data["objections"] = objections
                
            if qual_data:
                await lead_repo.update_qualification(lead.id, qual_data)
                qualification_updated = True
        
        logger.success(f"Lead atualizado com sucesso: ID={lead.id}")
        
        return {
            "success": True,
            "lead_id": str(updated_lead.id),
            "updated_fields": list(update_data.keys()),
            "qualification_updated": qualification_updated,
            "data": {
                "name": updated_lead.name,
                "phone": updated_lead.phone_number,
                "stage": updated_lead.current_stage.value if hasattr(updated_lead.current_stage, 'value') else updated_lead.current_stage,
                "qualification_score": updated_lead.qualification_score,
                "interested": updated_lead.interested,
                "property_type": updated_lead.property_type.value if updated_lead.property_type and hasattr(updated_lead.property_type, 'value') else updated_lead.property_type,
                "bill_value": updated_lead.bill_value,
                "consumption_kwh": updated_lead.consumption_kwh
            }
        }
        
    except ValueError as e:
        logger.error(f"Erro de validação ao atualizar lead: {e}")
        return {
            "success": False,
            "error": f"Erro de validação: {str(e)}",
            "error_type": "validation"
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar lead: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao atualizar lead: {str(e)}",
            "error_type": "database"
        }


# Exporta a tool
UpdateLeadTool = update_lead