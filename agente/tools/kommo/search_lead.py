"""
Tool para buscar leads no Kommo CRM
"""

from typing import Dict, Any
from agno.tools import tool
from loguru import logger

from ...services.kommo_service import get_kommo_service, KommoAPIError


@tool(show_result=True)
async def search_kommo_lead(query: str, limit: int = 50) -> Dict[str, Any]:
    """
    Busca leads no Kommo CRM por telefone, email ou nome.
    
    Args:
        query: Termo de busca (telefone, email ou nome)
        limit: Número máximo de resultados (padrão: 50)
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - count: número de leads encontrados
            - leads: lista de leads encontrados
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Buscando leads no Kommo com query: {query}")
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Buscar leads
        leads = await kommo.search_leads(query, limit=limit)
        
        # Processar resultados
        processed_leads = []
        for lead in leads:
            processed_lead = {
                "id": lead.get("id"),
                "name": lead.get("name"),
                "price": lead.get("price", 0),
                "status_id": lead.get("status_id"),
                "pipeline_id": lead.get("pipeline_id"),
                "created_at": lead.get("created_at"),
                "updated_at": lead.get("updated_at"),
                "tags": [tag.get("name") for tag in lead.get("_embedded", {}).get("tags", [])]
            }
            
            # Extrair campos customizados relevantes
            custom_fields = lead.get("custom_fields_values", [])
            for field in custom_fields:
                field_id = field.get("field_id")
                values = field.get("values", [])
                if values and values[0].get("value"):
                    # Mapear campos conhecidos
                    if field.get("field_code") == "PHONE":
                        processed_lead["phone"] = values[0].get("value")
                    elif field.get("field_code") == "EMAIL":
                        processed_lead["email"] = values[0].get("value")
                    else:
                        # Adicionar outros campos customizados
                        field_name = field.get("field_name", f"custom_{field_id}")
                        processed_lead[field_name] = values[0].get("value")
            
            processed_leads.append(processed_lead)
        
        logger.success(f"Encontrados {len(leads)} leads para query '{query}'")
        
        return {
            "success": True,
            "count": len(leads),
            "leads": processed_leads,
            "query": query
        }
        
    except KommoAPIError as e:
        logger.error(f"Erro da API do Kommo ao buscar leads: {e}")
        return {
            "success": False,
            "count": 0,
            "leads": [],
            "error": f"Erro da API do Kommo: {str(e)}",
            "query": query
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar leads: {e}")
        return {
            "success": False,
            "count": 0,
            "leads": [],
            "error": f"Erro inesperado: {str(e)}",
            "query": query
        }


@tool(show_result=True)
async def search_lead_by_phone(phone: str) -> Dict[str, Any]:
    """
    Busca um lead específico pelo número de telefone.
    
    Args:
        phone: Número de telefone para buscar
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - found: bool indicando se o lead foi encontrado
            - lead: dados do lead (se encontrado)
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Buscando lead por telefone: {phone}")
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Buscar lead pelo telefone
        lead = await kommo.get_lead_by_phone(phone)
        
        if lead:
            # Processar lead encontrado
            processed_lead = {
                "id": lead.get("id"),
                "name": lead.get("name"),
                "price": lead.get("price", 0),
                "status_id": lead.get("status_id"),
                "pipeline_id": lead.get("pipeline_id"),
                "created_at": lead.get("created_at"),
                "updated_at": lead.get("updated_at"),
                "tags": [tag.get("name") for tag in lead.get("_embedded", {}).get("tags", [])]
            }
            
            # Extrair campos customizados
            custom_fields = lead.get("custom_fields_values", [])
            for field in custom_fields:
                values = field.get("values", [])
                if values and values[0].get("value"):
                    field_name = field.get("field_code", f"field_{field.get('field_id')}")
                    processed_lead[field_name] = values[0].get("value")
            
            logger.success(f"Lead encontrado para telefone {phone}: ID {lead.get('id')}")
            
            return {
                "success": True,
                "found": True,
                "lead": processed_lead,
                "phone": phone
            }
        else:
            logger.info(f"Nenhum lead encontrado para telefone {phone}")
            
            return {
                "success": True,
                "found": False,
                "lead": None,
                "phone": phone,
                "message": f"Nenhum lead encontrado com o telefone {phone}"
            }
            
    except Exception as e:
        logger.error(f"Erro ao buscar lead por telefone: {e}")
        return {
            "success": False,
            "found": False,
            "lead": None,
            "error": f"Erro ao buscar lead: {str(e)}",
            "phone": phone
        }


# Exportar tools
SearchKommoLeadTool = search_kommo_lead
SearchLeadByPhoneTool = search_lead_by_phone