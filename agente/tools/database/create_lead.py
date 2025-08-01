"""
Tool para criar novo lead no banco de dados local
"""

from agno.tools import tool
from loguru import logger
from typing import Optional, Dict, Any
from uuid import UUID

from ...repositories import get_lead_repository
from ...core.types import Lead, LeadStage, PropertyType
from ...core.logger import setup_module_logger

logger = setup_module_logger(__name__)


@tool(show_result=True)
async def create_lead(
    phone: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    property_type: Optional[str] = None,
    address: Optional[str] = None,
    bill_value: Optional[float] = None,
    consumption_kwh: Optional[int] = None
) -> Dict[str, Any]:
    """
    Cria novo lead no banco de dados local
    
    Args:
        phone: Número de telefone do lead (obrigatório)
        name: Nome do lead
        email: Email do lead
        property_type: Tipo de propriedade (casa, apartamento, comercial, rural)
        address: Endereço da propriedade
        bill_value: Valor da conta de luz
        consumption_kwh: Consumo em kWh
    
    Returns:
        Dict com sucesso, lead_id e dados do lead criado
    """
    try:
        logger.info(f"Criando novo lead para telefone: {phone}")
        
        # Prepara kwargs adicionais
        kwargs = {}
        if email:
            kwargs["email"] = email
        if property_type:
            # Converte string para enum se necessário
            try:
                prop_type = PropertyType(property_type.lower())
                kwargs["property_type"] = prop_type
            except:
                logger.warning(f"Tipo de propriedade inválido: {property_type}")
        if address:
            kwargs["address"] = address
        if bill_value is not None:
            kwargs["bill_value"] = float(bill_value)
        if consumption_kwh is not None:
            kwargs["consumption_kwh"] = int(consumption_kwh)
        
        # Cria o lead usando o repository
        lead_repo = get_lead_repository()
        lead = await lead_repo.create_lead(
            phone=phone,
            name=name,
            **kwargs
        )
        
        logger.success(f"Lead criado com sucesso: ID={lead.id}, Phone={lead.phone_number}")
        
        return {
            "success": True,
            "lead_id": str(lead.id),
            "phone": lead.phone_number,
            "name": lead.name,
            "stage": lead.current_stage.value if hasattr(lead.current_stage, 'value') else lead.current_stage,
            "qualified": lead.qualification_score > 0,
            "data": {
                "email": lead.email,
                "property_type": lead.property_type.value if lead.property_type and hasattr(lead.property_type, 'value') else lead.property_type,
                "address": lead.address,
                "bill_value": lead.bill_value,
                "consumption_kwh": lead.consumption_kwh,
                "kommo_lead_id": lead.kommo_lead_id
            }
        }
        
    except ValueError as e:
        logger.error(f"Erro de validação ao criar lead: {e}")
        return {
            "success": False,
            "error": f"Erro de validação: {str(e)}",
            "error_type": "validation"
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao criar lead: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao criar lead: {str(e)}",
            "error_type": "database"
        }


# Exporta a tool
CreateLeadTool = create_lead