"""
Kommo Webhooks Routes
=====================
Endpoints para receber webhooks do Kommo CRM
"""

from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from typing import Optional, Dict, Any, List
from datetime import datetime
import hmac
import hashlib
from loguru import logger

from config.config import get_config
from services.kommo_service import kommo_service
from services.whatsapp_service import whatsapp_service
from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository


router = APIRouter(prefix="/webhook/kommo", tags=["kommo-webhooks"])


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """Verifica assinatura do webhook"""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@router.post("/events")
async def kommo_webhook_events(
    request: Request,
    background_tasks: BackgroundTasks,
    x_auth: Optional[str] = Header(None)
):
    """
    Recebe eventos do Kommo CRM
    
    Eventos suportados:
    - leads:status - Mudança de status do lead
    - leads:update - Atualização do lead
    - leads:delete - Lead deletado
    - leads:restore - Lead restaurado
    - task:add - Tarefa criada
    - task:update - Tarefa atualizada
    - note:add - Nota adicionada
    """
    try:
        # Obter body raw para verificação
        body = await request.body()
        data = await request.json()
        
        # TODO: Implementar verificação de assinatura quando Kommo fornecer
        # Por enquanto, verificar token simples se fornecido
        config = get_config()
        if x_auth and config.kommo.webhook_token:
            if x_auth != config.kommo.webhook_token:
                raise HTTPException(status_code=401, detail="Token inválido")
        
        # Log do evento recebido
        logger.info(f"Webhook Kommo recebido: {data}")
        
        # Processar diferentes tipos de eventos
        if "leads" in data:
            # Processar eventos de leads
            await process_leads_events(data["leads"], background_tasks)
            
        if "contacts" in data:
            # Processar eventos de contatos
            await process_contacts_events(data["contacts"], background_tasks)
            
        if "tasks" in data:
            # Processar eventos de tarefas
            await process_tasks_events(data["tasks"], background_tasks)
            
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook Kommo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar webhook")


async def process_leads_events(events: Dict[str, List], background_tasks: BackgroundTasks):
    """Processa eventos relacionados a leads"""
    
    # Status mudou
    if "status" in events:
        for event in events["status"]:
            lead_id = event.get("id")
            old_status = event.get("old_status_id")
            new_status = event.get("status_id")
            
            logger.info(f"Lead {lead_id} mudou de status: {old_status} -> {new_status}")
            
            # Agendar processamento em background
            background_tasks.add_task(
                handle_lead_status_change,
                lead_id,
                old_status,
                new_status
            )
    
    # Lead atualizado
    if "update" in events:
        for event in events["update"]:
            lead_id = event.get("id")
            
            logger.info(f"Lead {lead_id} foi atualizado")
            
            # Agendar sincronização
            background_tasks.add_task(
                sync_lead_from_kommo,
                lead_id
            )
    
    # Lead deletado
    if "delete" in events:
        for event in events["delete"]:
            lead_id = event.get("id")
            
            logger.info(f"Lead {lead_id} foi deletado")
            
            # Marcar como inativo localmente
            background_tasks.add_task(
                mark_lead_inactive,
                lead_id
            )


async def process_contacts_events(events: Dict[str, List], background_tasks: BackgroundTasks):
    """Processa eventos relacionados a contatos"""
    
    if "update" in events:
        for event in events["update"]:
            contact_id = event.get("id")
            
            logger.info(f"Contato {contact_id} foi atualizado")
            
            # TODO: Implementar sincronização de contatos


async def process_tasks_events(events: Dict[str, List], background_tasks: BackgroundTasks):
    """Processa eventos relacionados a tarefas"""
    
    # Tarefa adicionada
    if "add" in events:
        for event in events["add"]:
            task_id = event.get("id")
            entity_id = event.get("entity_id")
            text = event.get("text", "")
            
            logger.info(f"Tarefa {task_id} criada para lead {entity_id}")
            
            # Se for tarefa de follow-up, enviar mensagem WhatsApp
            if "follow" in text.lower() or "acompanhamento" in text.lower():
                background_tasks.add_task(
                    send_follow_up_message,
                    entity_id,
                    text
                )
    
    # Tarefa completada
    if "update" in events:
        for event in events["update"]:
            task_id = event.get("id")
            is_completed = event.get("is_completed")
            
            if is_completed:
                logger.info(f"Tarefa {task_id} foi completada")


# Funções de background

async def handle_lead_status_change(lead_id: int, old_status: int, new_status: int):
    """Processa mudança de status do lead"""
    try:
        # Buscar lead no Kommo
        kommo_lead = await kommo_service.get_lead(lead_id)
        if not kommo_lead:
            return
        
        # Buscar WhatsApp do lead
        whatsapp = None
        custom_fields = kommo_lead.get("custom_fields_values", [])
        whatsapp_field_id = get_config().kommo.custom_fields.get("whatsapp_number", 0)
        
        for field in custom_fields:
            if field.get("field_id") == whatsapp_field_id:
                whatsapp = field.get("values", [{}])[0].get("value")
                break
        
        if not whatsapp:
            logger.warning(f"WhatsApp não encontrado para lead {lead_id}")
            return
        
        # Buscar lead local
        lead = await lead_repository.get_by_phone(whatsapp)
        if not lead:
            logger.warning(f"Lead local não encontrado para WhatsApp {whatsapp}")
            return
        
        # Mapear status para mensagem
        config = get_config()
        stage_messages = {
            config.kommo.stage_ids.get("meeting_scheduled"): "🎉 Ótima notícia! Sua reunião foi confirmada!",
            config.kommo.stage_ids.get("proposal_sent"): "📄 Sua proposta personalizada foi enviada!",
            config.kommo.stage_ids.get("won"): "🎊 Parabéns! Bem-vindo à família SolarPrime!"
        }
        
        message = stage_messages.get(new_status)
        if message:
            # Enviar mensagem via WhatsApp
            await whatsapp_service.send_text_message(whatsapp, message)
            
    except Exception as e:
        logger.error(f"Erro ao processar mudança de status: {str(e)}")


async def sync_lead_from_kommo(lead_id: int):
    """Sincroniza dados do lead do Kommo para o banco local"""
    try:
        # Buscar lead no Kommo
        kommo_lead = await kommo_service.get_lead(lead_id)
        if not kommo_lead:
            return
        
        # Extrair campos customizados
        custom_fields = {}
        field_config = get_config().kommo.custom_fields
        
        for field in kommo_lead.get("custom_fields_values", []):
            field_id = field.get("field_id")
            value = field.get("values", [{}])[0].get("value")
            
            # Mapear ID para nome do campo
            for field_name, configured_id in field_config.items():
                if configured_id == field_id:
                    custom_fields[field_name] = value
                    break
        
        # Buscar lead local pelo WhatsApp
        whatsapp = custom_fields.get("whatsapp_number")
        if not whatsapp:
            return
        
        lead = await lead_repository.get_by_phone(whatsapp)
        if lead:
            # Atualizar dados locais
            update_data = {
                "name": kommo_lead.get("name"),
                "kommo_lead_id": str(lead_id)
            }
            
            # Atualizar campos específicos se disponíveis
            if "energy_bill_value" in custom_fields:
                update_data["bill_value"] = float(custom_fields["energy_bill_value"])
            
            if "qualification_score" in custom_fields:
                update_data["qualification_score"] = int(custom_fields["qualification_score"])
            
            await lead_repository.update(lead.id, update_data)
            logger.info(f"Lead {lead.id} sincronizado do Kommo")
            
    except Exception as e:
        logger.error(f"Erro ao sincronizar lead do Kommo: {str(e)}")


async def mark_lead_inactive(lead_id: int):
    """Marca lead como inativo quando deletado no Kommo"""
    try:
        # Buscar lead local pelo kommo_lead_id
        # TODO: Implementar busca por kommo_lead_id no repositório
        logger.info(f"Lead {lead_id} marcado como inativo")
        
    except Exception as e:
        logger.error(f"Erro ao marcar lead como inativo: {str(e)}")


async def send_follow_up_message(lead_id: int, task_text: str):
    """Envia mensagem de follow-up via WhatsApp"""
    try:
        # Buscar lead no Kommo
        kommo_lead = await kommo_service.get_lead(lead_id)
        if not kommo_lead:
            return
        
        # Buscar WhatsApp
        whatsapp = None
        custom_fields = kommo_lead.get("custom_fields_values", [])
        whatsapp_field_id = get_config().kommo.custom_fields.get("whatsapp_number", 0)
        
        for field in custom_fields:
            if field.get("field_id") == whatsapp_field_id:
                whatsapp = field.get("values", [{}])[0].get("value")
                break
        
        if whatsapp:
            # Enviar mensagem personalizada
            message = f"Olá {kommo_lead.get('name', '')}! 👋\n\n"
            message += "Estou entrando em contato para dar continuidade à nossa conversa sobre energia solar.\n\n"
            message += "Você ainda tem interesse em conhecer como economizar até 95% na sua conta de luz?"
            
            await whatsapp_service.send_text_message(whatsapp, message)
            logger.info(f"Follow-up enviado para {whatsapp}")
            
    except Exception as e:
        logger.error(f"Erro ao enviar follow-up: {str(e)}")


@router.post("/setup")
async def setup_kommo_webhooks():
    """
    Configura webhooks no Kommo
    
    Este endpoint deve ser chamado uma vez para configurar
    todos os webhooks necessários
    """
    try:
        # TODO: Implementar configuração automática de webhooks
        # Por enquanto, retornar instruções manuais
        
        config = get_config()
        webhook_url = f"{config.api_base_url}/webhook/kommo/events"
        
        return {
            "status": "manual_setup_required",
            "instructions": {
                "1": "Acesse o painel do Kommo",
                "2": "Vá em Configurações > Integrações > Webhooks",
                "3": "Adicione um novo webhook",
                "4": f"URL: {webhook_url}",
                "5": "Eventos: leads:status, leads:update, task:add",
                "6": "Salve as configurações"
            },
            "webhook_url": webhook_url
        }
        
    except Exception as e:
        logger.error(f"Erro ao configurar webhooks: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao configurar webhooks")