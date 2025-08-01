"""
Tool para atualizar o estágio/status de leads no pipeline do Kommo CRM
"""

from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from ...services.kommo_service import get_kommo_service, KommoAPIError
from ...core.config import KOMMO_STAGES


@tool(show_result=True, stop_after_tool_call=True)
async def update_kommo_stage(
    lead_id: int,
    stage_name: str,
    add_note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Move um lead para um novo estágio no pipeline do Kommo CRM.
    
    Args:
        lead_id: ID do lead no Kommo
        stage_name: Nome do estágio (usar constantes de KOMMO_STAGES)
                   Valores válidos: NOVO_LEAD, EM_NEGOCIACAO, EM_QUALIFICACAO,
                   QUALIFICADO, REUNIAO_AGENDADA, NAO_INTERESSADO
        add_note: Nota opcional para adicionar ao mover o lead
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - lead_id: ID do lead
            - old_stage: estágio anterior
            - new_stage: novo estágio
            - pipeline_id: ID do pipeline
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Movendo lead {lead_id} para estágio '{stage_name}'")
        
        # Validar stage_name
        if stage_name not in KOMMO_STAGES:
            # Tentar encontrar pelo valor
            stage_key = None
            for key, value in KOMMO_STAGES.items():
                if value.lower() == stage_name.lower():
                    stage_key = key
                    break
            
            if not stage_key:
                return {
                    "success": False,
                    "error": f"Estágio inválido: '{stage_name}'. Use um dos valores: {', '.join(KOMMO_STAGES.keys())}",
                    "lead_id": lead_id,
                    "old_stage": None,
                    "new_stage": None,
                    "pipeline_id": None
                }
            
            stage_name = stage_key
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Buscar lead atual para obter estágio anterior
        try:
            current_lead = await kommo.get_lead(lead_id)
            old_status_id = current_lead.get('status_id')
            pipeline_id = current_lead.get('pipeline_id')
        except KommoAPIError as e:
            if e.status_code == 404:
                return {
                    "success": False,
                    "error": f"Lead {lead_id} não encontrado",
                    "lead_id": lead_id,
                    "old_stage": None,
                    "new_stage": None,
                    "pipeline_id": None
                }
            raise
        
        # Buscar informações dos pipelines para mapear IDs para nomes
        pipelines = await kommo.get_pipelines()
        
        # Encontrar nome do estágio anterior
        old_stage_name = None
        new_stage_id = None
        
        for pipeline in pipelines:
            if pipeline.get('id') == pipeline_id:
                statuses = pipeline.get('_embedded', {}).get('statuses', [])
                for status in statuses:
                    if status.get('id') == old_status_id:
                        old_stage_name = status.get('name')
                    # Encontrar ID do novo estágio
                    if status.get('name', '').lower() == KOMMO_STAGES[stage_name].lower():
                        new_stage_id = status.get('id')
        
        # Verificar se já está no estágio desejado
        if new_stage_id and new_stage_id == old_status_id:
            logger.info(f"Lead {lead_id} já está no estágio '{KOMMO_STAGES[stage_name]}'")
            return {
                "success": True,
                "lead_id": lead_id,
                "old_stage": old_stage_name,
                "new_stage": KOMMO_STAGES[stage_name],
                "pipeline_id": pipeline_id,
                "message": f"Lead já está no estágio '{KOMMO_STAGES[stage_name]}'"
            }
        
        # Mover lead para novo estágio
        mapped_stage_name = KOMMO_STAGES[stage_name]
        updated_lead = await kommo.update_lead_stage(lead_id, mapped_stage_name)
        
        # Adicionar nota se fornecida
        if add_note:
            try:
                note_text = f"Lead movido para estágio '{mapped_stage_name}'. {add_note}"
                await kommo.add_note(lead_id, note_text)
                logger.info(f"Nota adicionada ao lead {lead_id}")
            except Exception as e:
                logger.warning(f"Erro ao adicionar nota: {e}")
        
        # Log de ações especiais baseadas no estágio
        if stage_name == "QUALIFICADO":
            logger.success(f"Lead {lead_id} QUALIFICADO! Pronto para agendamento.")
        elif stage_name == "REUNIAO_AGENDADA":
            logger.success(f"Lead {lead_id} com REUNIÃO AGENDADA!")
        elif stage_name == "NAO_INTERESSADO":
            logger.warning(f"Lead {lead_id} marcado como NÃO INTERESSADO")
        
        logger.success(
            f"Lead {lead_id} movido de '{old_stage_name}' para '{mapped_stage_name}'"
        )
        
        return {
            "success": True,
            "lead_id": lead_id,
            "old_stage": old_stage_name,
            "new_stage": mapped_stage_name,
            "pipeline_id": pipeline_id,
            "message": f"Lead movido com sucesso para estágio '{mapped_stage_name}'"
        }
        
    except KommoAPIError as e:
        logger.error(f"Erro da API do Kommo ao mover lead: {e}")
        return {
            "success": False,
            "lead_id": lead_id,
            "old_stage": None,
            "new_stage": None,
            "pipeline_id": None,
            "error": f"Erro da API do Kommo: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao mover lead: {e}")
        return {
            "success": False,
            "lead_id": lead_id,
            "old_stage": None,
            "new_stage": None,
            "pipeline_id": None,
            "error": f"Erro inesperado: {str(e)}"
        }


@tool(show_result=True)
async def get_lead_stage(lead_id: int) -> Dict[str, Any]:
    """
    Obtém o estágio atual de um lead no pipeline.
    
    Args:
        lead_id: ID do lead no Kommo
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - lead_id: ID do lead
            - stage_name: nome do estágio atual
            - stage_id: ID do estágio atual
            - pipeline_id: ID do pipeline
            - pipeline_name: nome do pipeline
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Consultando estágio do lead {lead_id}")
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Buscar lead
        try:
            lead = await kommo.get_lead(lead_id)
        except KommoAPIError as e:
            if e.status_code == 404:
                return {
                    "success": False,
                    "error": f"Lead {lead_id} não encontrado",
                    "lead_id": lead_id,
                    "stage_name": None,
                    "stage_id": None,
                    "pipeline_id": None,
                    "pipeline_name": None
                }
            raise
        
        status_id = lead.get('status_id')
        pipeline_id = lead.get('pipeline_id')
        
        # Buscar informações dos pipelines
        pipelines = await kommo.get_pipelines()
        
        # Encontrar nome do estágio e pipeline
        stage_name = None
        pipeline_name = None
        
        for pipeline in pipelines:
            if pipeline.get('id') == pipeline_id:
                pipeline_name = pipeline.get('name')
                statuses = pipeline.get('_embedded', {}).get('statuses', [])
                for status in statuses:
                    if status.get('id') == status_id:
                        stage_name = status.get('name')
                        break
                break
        
        # Mapear para constante KOMMO_STAGES se possível
        stage_key = None
        for key, value in KOMMO_STAGES.items():
            if value.lower() == (stage_name or '').lower():
                stage_key = key
                break
        
        logger.info(f"Lead {lead_id} está no estágio '{stage_name}' (ID: {status_id})")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "stage_name": stage_name,
            "stage_key": stage_key,
            "stage_id": status_id,
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name
        }
        
    except Exception as e:
        logger.error(f"Erro ao consultar estágio do lead: {e}")
        return {
            "success": False,
            "lead_id": lead_id,
            "stage_name": None,
            "stage_id": None,
            "pipeline_id": None,
            "pipeline_name": None,
            "error": f"Erro ao consultar estágio: {str(e)}"
        }


# Exportar tools
UpdateKommoStageTool = update_kommo_stage
GetLeadStageTool = get_lead_stage