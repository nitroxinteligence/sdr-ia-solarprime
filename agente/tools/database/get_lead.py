"""
Tool para buscar lead por telefone ou ID
"""

from agno.tools import tool
from loguru import logger
from typing import Optional, Dict, Any
from uuid import UUID

from ...repositories import get_lead_repository
from ...core.logger import setup_module_logger
from ...utils.formatters import format_phone_number

logger = setup_module_logger(__name__)


@tool(show_result=True)
async def get_lead(
    lead_id: Optional[str] = None,
    phone: Optional[str] = None,
    include_qualification: bool = False,
    include_follow_ups: bool = False
) -> Dict[str, Any]:
    """
    Busca lead por telefone ou ID
    
    Args:
        lead_id: ID do lead (UUID)
        phone: Número de telefone
        include_qualification: Se deve incluir dados de qualificação
        include_follow_ups: Se deve incluir follow-ups agendados
    
    Returns:
        Dict com dados do lead ou erro se não encontrado
    """
    try:
        # Valida parâmetros
        if not lead_id and not phone:
            logger.error("Nem lead_id nem phone foram fornecidos")
            return {
                "success": False,
                "error": "É necessário fornecer lead_id ou phone",
                "error_type": "validation"
            }
        
        lead_repo = get_lead_repository()
        lead = None
        
        # Busca por ID
        if lead_id:
            logger.info(f"Buscando lead por ID: {lead_id}")
            try:
                lead = await lead_repo.get_lead_by_id(UUID(lead_id))
            except ValueError:
                logger.error(f"ID inválido: {lead_id}")
                return {
                    "success": False,
                    "error": "ID do lead inválido",
                    "error_type": "validation"
                }
        
        # Busca por telefone
        elif phone:
            logger.info(f"Buscando lead por telefone: {phone}")
            formatted_phone = format_phone_number(phone)
            lead = await lead_repo.get_lead_by_phone(formatted_phone)
        
        # Verifica se encontrou
        if not lead:
            logger.warning(f"Lead não encontrado")
            return {
                "success": False,
                "error": "Lead não encontrado",
                "error_type": "not_found",
                "searched_by": "id" if lead_id else "phone",
                "search_value": lead_id if lead_id else phone
            }
        
        # Prepara resposta
        result = {
            "success": True,
            "lead_id": str(lead.id),
            "data": {
                "name": lead.name,
                "phone": lead.phone_number,
                "email": lead.email,
                "document": lead.document,
                "property_type": lead.property_type.value if lead.property_type and hasattr(lead.property_type, 'value') else lead.property_type,
                "address": lead.address,
                "bill_value": lead.bill_value,
                "consumption_kwh": lead.consumption_kwh,
                "stage": lead.current_stage.value if hasattr(lead.current_stage, 'value') else lead.current_stage,
                "qualification_score": lead.qualification_score,
                "interested": lead.interested,
                "kommo_lead_id": lead.kommo_lead_id,
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
                "updated_at": lead.updated_at.isoformat() if lead.updated_at else None
            }
        }
        
        # Busca dados de qualificação se solicitado
        if include_qualification:
            try:
                qualification = await lead_repo.get_qualification(lead.id)
                if qualification:
                    result["qualification"] = {
                        "has_own_property": qualification.has_own_property,
                        "decision_maker": qualification.decision_maker,
                        "urgency_level": qualification.urgency_level.value if qualification.urgency_level and hasattr(qualification.urgency_level, 'value') else qualification.urgency_level,
                        "objections": qualification.objections,
                        "solutions_presented": qualification.solutions_presented,
                        "extracted_data": qualification.extracted_data,
                        "qualification_date": qualification.qualification_date.isoformat() if qualification.qualification_date else None
                    }
                else:
                    result["qualification"] = None
            except Exception as e:
                logger.warning(f"Erro ao buscar qualificação: {e}")
                result["qualification"] = None
        
        # Busca follow-ups se solicitado
        if include_follow_ups:
            try:
                from ...repositories import get_followup_repository
                followup_repo = get_followup_repository()
                follow_ups = await followup_repo.get_pending_follow_ups(lead.id)
                
                result["follow_ups"] = [
                    {
                        "id": str(fu.id),
                        "scheduled_at": fu.scheduled_at.isoformat(),
                        "type": fu.type.value if hasattr(fu.type, 'value') else fu.type,
                        "message": fu.message,
                        "attempt_number": fu.attempt_number,
                        "status": fu.status.value if hasattr(fu.status, 'value') else fu.status
                    }
                    for fu in follow_ups
                ]
            except Exception as e:
                logger.warning(f"Erro ao buscar follow-ups: {e}")
                result["follow_ups"] = []
        
        logger.success(f"Lead encontrado: ID={lead.id}, Nome={lead.name}")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar lead: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao buscar lead: {str(e)}",
            "error_type": "database"
        }


# Exporta a tool
GetLeadTool = get_lead