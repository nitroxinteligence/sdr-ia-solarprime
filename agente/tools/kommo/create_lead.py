"""
Tool para criar leads no Kommo CRM
"""

from typing import Dict, Optional, Any
from agno.tools import tool
from loguru import logger

from ...services.kommo_service import get_kommo_service, KommoAPIError
from ...core.config import KOMMO_STAGES


@tool(show_result=True, stop_after_tool_call=True)
async def create_kommo_lead(
    name: str,
    phone: str,
    email: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    tags: Optional[list[str]] = None,
    initial_stage: str = "NOVO_LEAD"
) -> Dict[str, Any]:
    """
    Cria um novo lead no Kommo CRM.
    
    Args:
        name: Nome do lead
        phone: Telefone do lead (obrigatório)
        email: Email do lead (opcional)
        custom_fields: Dicionário com campos customizados extras {field_id: value}
        tags: Lista de tags para adicionar ao lead
        initial_stage: Estágio inicial do pipeline (padrão: NOVO_LEAD)
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - lead_id: ID do lead criado
            - lead: dados completos do lead criado
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Criando novo lead no Kommo: {name} - {phone}")
        
        # Validar dados obrigatórios
        if not name or not phone:
            return {
                "success": False,
                "error": "Nome e telefone são obrigatórios",
                "lead_id": None,
                "lead": None
            }
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Verificar se lead já existe
        existing_lead = await kommo.get_lead_by_phone(phone)
        if existing_lead:
            logger.warning(f"Lead já existe com telefone {phone}: ID {existing_lead.get('id')}")
            return {
                "success": False,
                "error": f"Lead já existe com este telefone. ID: {existing_lead.get('id')}",
                "lead_id": existing_lead.get('id'),
                "lead": existing_lead,
                "already_exists": True
            }
        
        # Preparar campos customizados
        fields_to_create = custom_fields or {}
        
        # Adicionar email se fornecido
        if email:
            # Buscar ID do campo de email
            custom_fields_list = await kommo.get_custom_fields()
            email_field_id = None
            for field in custom_fields_list:
                if field.get('code') == 'EMAIL' or field.get('name', '').lower() == 'email':
                    email_field_id = field.get('id')
                    break
            
            if email_field_id:
                fields_to_create[email_field_id] = email
        
        # Criar o lead
        lead = await kommo.create_lead(
            name=name,
            phone=phone,
            custom_fields=fields_to_create
        )
        
        # Adicionar tags se fornecidas
        if tags and lead:
            lead_id = lead.get('id')
            for tag in tags:
                try:
                    await kommo.add_tag(lead_id, tag)
                    logger.info(f"Tag '{tag}' adicionada ao lead {lead_id}")
                except Exception as e:
                    logger.warning(f"Erro ao adicionar tag '{tag}': {e}")
        
        # Mover para estágio inicial se não for NOVO_LEAD
        if initial_stage != "NOVO_LEAD" and initial_stage in KOMMO_STAGES:
            try:
                lead_id = lead.get('id')
                stage_name = KOMMO_STAGES[initial_stage]
                await kommo.update_lead_stage(lead_id, stage_name)
                logger.info(f"Lead {lead_id} movido para estágio '{stage_name}'")
            except Exception as e:
                logger.warning(f"Erro ao mover lead para estágio inicial: {e}")
        
        logger.success(f"Lead criado com sucesso: ID {lead.get('id')} - {name}")
        
        return {
            "success": True,
            "lead_id": lead.get('id'),
            "lead": {
                "id": lead.get('id'),
                "name": lead.get('name'),
                "phone": phone,
                "email": email,
                "status_id": lead.get('status_id'),
                "pipeline_id": lead.get('pipeline_id'),
                "created_at": lead.get('created_at'),
                "tags": tags or []
            },
            "message": f"Lead '{name}' criado com sucesso no Kommo CRM"
        }
        
    except KommoAPIError as e:
        logger.error(f"Erro da API do Kommo ao criar lead: {e}")
        return {
            "success": False,
            "lead_id": None,
            "lead": None,
            "error": f"Erro da API do Kommo: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao criar lead: {e}")
        return {
            "success": False,
            "lead_id": None,
            "lead": None,
            "error": f"Erro inesperado: {str(e)}"
        }


# Exportar tool
CreateKommoLeadTool = create_kommo_lead