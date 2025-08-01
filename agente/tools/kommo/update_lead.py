"""
Tool para atualizar dados de leads no Kommo CRM
"""

from typing import Dict, Optional, Any, List
from agno.tools import tool
from loguru import logger

from ...services.kommo_service import get_kommo_service, KommoAPIError


@tool(show_result=True)
async def update_kommo_lead(
    lead_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    price: Optional[int] = None,
    custom_fields: Optional[Dict[int, Any]] = None,
    tags_to_add: Optional[List[str]] = None,
    tags_to_remove: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Atualiza dados de um lead existente no Kommo CRM.
    
    Args:
        lead_id: ID do lead no Kommo
        name: Novo nome do lead (opcional)
        email: Novo email (opcional)
        phone: Novo telefone (opcional)
        price: Novo valor/preço do lead (opcional)
        custom_fields: Dicionário com campos customizados {field_id: value}
        tags_to_add: Lista de tags para adicionar
        tags_to_remove: Lista de tags para remover
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - lead: dados atualizados do lead
            - updated_fields: lista de campos que foram atualizados
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Atualizando lead {lead_id} no Kommo")
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Buscar lead atual para validação
        try:
            current_lead = await kommo.get_lead(lead_id)
        except KommoAPIError as e:
            if e.status_code == 404:
                return {
                    "success": False,
                    "error": f"Lead {lead_id} não encontrado",
                    "lead": None,
                    "updated_fields": []
                }
            raise
        
        # Preparar dados de atualização
        update_data = {}
        updated_fields = []
        
        # Atualizar nome se fornecido
        if name and name != current_lead.get('name'):
            update_data['name'] = name
            updated_fields.append('name')
        
        # Atualizar preço se fornecido
        if price is not None and price != current_lead.get('price'):
            update_data['price'] = price
            updated_fields.append('price')
        
        # Preparar campos customizados
        custom_fields_values = []
        
        # Buscar campos customizados disponíveis
        available_fields = await kommo.get_custom_fields()
        field_mapping = {
            field.get('code', field.get('name', '').lower()): field.get('id')
            for field in available_fields
        }
        
        # Atualizar telefone se fornecido
        if phone:
            phone_field_id = field_mapping.get('PHONE') or field_mapping.get('phone') or field_mapping.get('telefone')
            if phone_field_id:
                custom_fields_values.append({
                    "field_id": phone_field_id,
                    "values": [{"value": phone}]
                })
                updated_fields.append('phone')
        
        # Atualizar email se fornecido
        if email:
            email_field_id = field_mapping.get('EMAIL') or field_mapping.get('email')
            if email_field_id:
                custom_fields_values.append({
                    "field_id": email_field_id,
                    "values": [{"value": email}]
                })
                updated_fields.append('email')
        
        # Adicionar campos customizados extras
        if custom_fields:
            for field_id, value in custom_fields.items():
                custom_fields_values.append({
                    "field_id": field_id,
                    "values": [{"value": value}]
                })
                updated_fields.append(f'custom_field_{field_id}')
        
        # Adicionar campos customizados ao update_data se houver
        if custom_fields_values:
            update_data['custom_fields_values'] = custom_fields_values
        
        # Realizar atualização se houver campos para atualizar
        if update_data:
            lead = await kommo.update_lead(lead_id, **update_data)
            logger.info(f"Lead {lead_id} atualizado: {', '.join(updated_fields)}")
        else:
            lead = current_lead
            logger.info(f"Nenhum campo de dados para atualizar no lead {lead_id}")
        
        # Gerenciar tags
        tags_updated = False
        
        # Adicionar novas tags
        if tags_to_add:
            for tag in tags_to_add:
                try:
                    await kommo.add_tag(lead_id, tag)
                    logger.info(f"Tag '{tag}' adicionada ao lead {lead_id}")
                    tags_updated = True
                except Exception as e:
                    logger.warning(f"Erro ao adicionar tag '{tag}': {e}")
        
        # Remover tags (requer manipulação da lista completa)
        if tags_to_remove:
            current_tags = current_lead.get('_embedded', {}).get('tags', [])
            current_tag_names = [tag.get('name') for tag in current_tags]
            
            # Filtrar tags a manter
            new_tags = [tag for tag in current_tag_names if tag not in tags_to_remove]
            
            if len(new_tags) != len(current_tag_names):
                # Atualizar com nova lista de tags
                tag_data = {
                    "id": lead_id,
                    "_embedded": {
                        "tags": [{"name": name} for name in new_tags]
                    }
                }
                await kommo._make_request('PATCH', '/leads', json=[tag_data])
                logger.info(f"Tags removidas do lead {lead_id}: {', '.join(tags_to_remove)}")
                tags_updated = True
        
        if tags_updated:
            updated_fields.append('tags')
            # Recarregar lead para obter tags atualizadas
            lead = await kommo.get_lead(lead_id)
        
        # Preparar resposta
        processed_lead = {
            "id": lead.get("id"),
            "name": lead.get("name"),
            "price": lead.get("price", 0),
            "status_id": lead.get("status_id"),
            "pipeline_id": lead.get("pipeline_id"),
            "updated_at": lead.get("updated_at"),
            "tags": [tag.get("name") for tag in lead.get("_embedded", {}).get("tags", [])]
        }
        
        # Adicionar campos customizados à resposta
        for field in lead.get('custom_fields_values', []):
            values = field.get('values', [])
            if values and values[0].get('value'):
                field_code = field.get('field_code', f"field_{field.get('field_id')}")
                processed_lead[field_code.lower()] = values[0].get('value')
        
        logger.success(f"Lead {lead_id} atualizado com sucesso")
        
        return {
            "success": True,
            "lead": processed_lead,
            "updated_fields": updated_fields,
            "message": f"Lead atualizado com sucesso. Campos modificados: {', '.join(updated_fields) if updated_fields else 'nenhum'}"
        }
        
    except KommoAPIError as e:
        logger.error(f"Erro da API do Kommo ao atualizar lead: {e}")
        return {
            "success": False,
            "lead": None,
            "updated_fields": [],
            "error": f"Erro da API do Kommo: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar lead: {e}")
        return {
            "success": False,
            "lead": None,
            "updated_fields": [],
            "error": f"Erro inesperado: {str(e)}"
        }


# Exportar tool
UpdateKommoLeadTool = update_kommo_lead