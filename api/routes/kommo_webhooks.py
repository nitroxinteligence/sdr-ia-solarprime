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
        # Verificar Content-Type
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            logger.warning(f"Webhook Kommo recebido com Content-Type inválido: {content_type}")
            # Tentar processar mesmo assim, mas com cuidado
        
        # Obter body raw para verificação
        body = await request.body()
        
        # Tentar decodificar JSON
        try:
            data = await request.json()
        except Exception as json_error:
            logger.error(f"Erro ao decodificar JSON do webhook Kommo: {json_error}")
            logger.debug(f"Body recebido: {body[:500] if body else 'vazio'}")
            
            # Tentar decodificar manualmente
            try:
                import json
                data = json.loads(body.decode('utf-8'))
            except:
                # Se ainda falhar, retornar erro
                return {
                    "status": "error",
                    "error": "Invalid JSON format",
                    "detail": "O webhook deve enviar dados em formato JSON válido"
                }
        
        # TODO: Implementar verificação de assinatura quando Kommo fornecer
        # Por enquanto, verificar token simples se fornecido
        config = get_config()
        if x_auth and config.kommo.webhook_token:
            if x_auth != config.kommo.webhook_token:
                raise HTTPException(status_code=401, detail="Token inválido")
        
        # Log do evento recebido
        logger.info(f"Webhook Kommo recebido - tipo de dados: {type(data)}")
        
        # Verificar se data é um dict válido
        if not isinstance(data, dict):
            logger.warning(f"Webhook Kommo recebeu dados que não são um dicionário: {type(data)}")
            return {
                "status": "error",
                "error": "Invalid data format",
                "detail": "Expected JSON object, got " + str(type(data).__name__)
            }
        
        # Log do conteúdo para debug
        logger.debug(f"Dados do webhook: {data}")
        
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
            
        # Se não encontrou nenhum evento conhecido, logar para debug
        if not any(key in data for key in ["leads", "contacts", "tasks"]):
            logger.warning(f"Webhook Kommo sem eventos conhecidos. Keys recebidas: {list(data.keys())}")
            
        return {"status": "ok", "processed": True}
        
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
            task_type = event.get("task_type", 0)
            
            logger.info(f"Tarefa {task_id} criada para lead {entity_id}")
            
            # Se for tarefa de follow-up, enviar mensagem WhatsApp
            if "follow" in text.lower() or "acompanhamento" in text.lower():
                background_tasks.add_task(
                    send_follow_up_message,
                    entity_id,
                    text
                )
    
    # Tarefa atualizada
    if "update" in events:
        for event in events["update"]:
            task_id = event.get("id")
            is_completed = event.get("is_completed")
            text = event.get("text", "")
            
            # Se for uma tarefa de reunião
            if "reunião" in text.lower() or "meeting" in text.lower():
                if is_completed:
                    logger.info(f"Reunião {task_id} foi completada")
                    # Atualizar status da reunião
                    background_tasks.add_task(
                        update_meeting_status,
                        event.get("entity_id"),
                        "completed"
                    )
    
    # Tarefa deletada
    if "delete" in events:
        for event in events["delete"]:
            task_id = event.get("id")
            text = event.get("text", "")
            
            # Se for uma tarefa de reunião sendo cancelada
            if "reunião" in text.lower() or "meeting" in text.lower():
                logger.info(f"Reunião {task_id} foi cancelada")
                background_tasks.add_task(
                    handle_meeting_cancellation,
                    event.get("entity_id"),
                    "Reunião cancelada pelo vendedor"
                )


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
            import random
            name = kommo_lead.get('name', '').split()[0] if kommo_lead.get('name') else ''
            messages = [
                f"Oi {name}! 👋 Tudo bem? Voltei pra ver se você ainda quer economizar naquela conta de luz... Que tal a gente conversar? 😊",
                f"E aí, {name}! Lembrei de você agora! ☀️ Ainda tá interessado em reduzir até 95% da conta de energia?",
                f"Olá {name}! Passando rapidinho pra saber se você ainda quer aquela economia que conversamos... Posso te ajudar? 💡"
            ]
            message = random.choice(messages)
            
            await whatsapp_service.send_text_message(whatsapp, message)
            logger.info(f"Follow-up enviado para {whatsapp}")
            
    except Exception as e:
        logger.error(f"Erro ao enviar follow-up: {str(e)}")


async def handle_meeting_cancellation(lead_id: int, reason: str = ""):
    """Processa cancelamento de reunião do Kommo"""
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
        if not lead or not lead.google_event_id:
            logger.warning(f"Lead local ou evento não encontrado para WhatsApp {whatsapp}")
            return
        
        # Cancelar evento no Google Calendar
        from services.google_calendar_service import get_google_calendar_service
        calendar_service = get_google_calendar_service()
        
        success = await calendar_service.cancel_event(lead.google_event_id)
        
        if success:
            # Atualizar lead local
            await lead_repository.update(lead.id, {
                "meeting_scheduled_at": None,
                "google_event_id": None,
                "meeting_status": "cancelled"
            })
            
            # Enviar mensagem WhatsApp informando cancelamento
            message = f"""😔 Olá {kommo_lead.get('name', '')}!

Infelizmente precisamos cancelar nossa reunião agendada.

{f'Motivo: {reason}' if reason else ''}

Por favor, entre em contato quando quiser reagendar. Estamos à disposição!

Atenciosamente,
Equipe SolarPrime"""
            
            await whatsapp_service.send_text_message(whatsapp, message)
            logger.info(f"Reunião cancelada e cliente notificado: {whatsapp}")
            
            # Atualizar campo no Kommo
            await kommo_service.update_lead_custom_field(
                lead_id=lead_id,
                field_name='meeting_status',
                value='cancelled'
            )
            
    except Exception as e:
        logger.error(f"Erro ao processar cancelamento de reunião: {str(e)}")


async def update_meeting_status(lead_id: int, status: str):
    """Atualiza status da reunião quando completada ou modificada"""
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
            # Buscar lead local
            lead = await lead_repository.get_by_phone(whatsapp)
            if lead:
                # Atualizar status
                await lead_repository.update(lead.id, {
                    "meeting_status": status
                })
                
                # Atualizar campo no Kommo
                await kommo_service.update_lead_custom_field(
                    lead_id=lead_id,
                    field_name='meeting_status',
                    value=status
                )
                
                # Se reunião foi completada, enviar mensagem de agradecimento
                if status == "completed":
                    message = f"""🎉 {kommo_lead.get('name', '')}, obrigado por participar da reunião!

Foi um prazer conversar com você sobre as soluções de energia solar da SolarPrime.

Em breve entraremos em contato com a proposta personalizada para você.

Qualquer dúvida, estou à disposição!

Atenciosamente,
Equipe SolarPrime"""
                    
                    await whatsapp_service.send_text_message(whatsapp, message)
                    
    except Exception as e:
        logger.error(f"Erro ao atualizar status da reunião: {str(e)}")


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