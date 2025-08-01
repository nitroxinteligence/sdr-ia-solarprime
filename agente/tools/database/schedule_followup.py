"""
Tool para agendar follow-up inteligente
"""

from loguru import logger
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from ...repositories import get_followup_repository, get_lead_repository
from ...core.types import FollowUpType, LeadStage
from ...core.logger import setup_module_logger

logger = setup_module_logger(__name__)

# Configurações padrão de follow-up
DEFAULT_FIRST_FOLLOW_UP_MINUTES = 30
DEFAULT_SECOND_FOLLOW_UP_HOURS = 24


# CRÍTICO: AGnO Framework bug com @tool decorator em async functions
# Removendo @tool decorator conforme documentação oficial AGnO
# Issue #2296: https://github.com/agno-agi/agno/issues/2296
async def schedule_followup(
    lead_id: Optional[str] = None,
    phone: Optional[str] = None,
    follow_up_type: Optional[str] = None,
    custom_message: Optional[str] = None,
    minutes_from_now: Optional[int] = None,
    hours_from_now: Optional[int] = None,
    scheduled_at: Optional[str] = None,
    attempt_number: int = 1,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Agenda follow-up inteligente
    
    Args:
        lead_id: ID do lead (UUID)
        phone: Número de telefone (usado se lead_id não fornecido)
        follow_up_type: Tipo do follow-up (reminder, check_in, reengagement, nurture, hot_lead_rescue)
        custom_message: Mensagem personalizada (se não fornecida, gera automaticamente)
        minutes_from_now: Agendar para X minutos a partir de agora
        hours_from_now: Agendar para X horas a partir de agora
        scheduled_at: Data/hora específica (ISO format)
        attempt_number: Número da tentativa (1 ou 2)
        context: Contexto adicional para personalização da mensagem
    
    Returns:
        Dict com sucesso e dados do follow-up agendado
    """
    try:
        # Busca o lead
        lead_repo = get_lead_repository()
        lead = None
        
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
        
        # Verifica se o lead está interessado
        if not lead.interested:
            logger.warning(f"Lead não está interessado, não agendando follow-up")
            return {
                "success": False,
                "error": "Lead marcado como não interessado",
                "error_type": "business_rule",
                "lead_stage": lead.current_stage.value if hasattr(lead.current_stage, 'value') else lead.current_stage
            }
        
        # Define tipo de follow-up
        if follow_up_type:
            try:
                followup_type_enum = FollowUpType(follow_up_type.lower())
            except ValueError:
                logger.warning(f"Tipo de follow-up inválido: {follow_up_type}, usando REMINDER")
                followup_type_enum = FollowUpType.REMINDER
        else:
            # Define tipo baseado no contexto
            if attempt_number == 1:
                followup_type_enum = FollowUpType.REMINDER
            elif lead.current_stage == LeadStage.SCHEDULING:
                followup_type_enum = FollowUpType.HOT_LEAD_RESCUE
            else:
                followup_type_enum = FollowUpType.CHECK_IN
        
        # Calcula horário do follow-up
        if scheduled_at:
            try:
                schedule_time = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            except:
                logger.error(f"Data/hora inválida: {scheduled_at}")
                return {
                    "success": False,
                    "error": "Data/hora inválida. Use formato ISO",
                    "error_type": "validation"
                }
        elif minutes_from_now:
            schedule_time = datetime.now() + timedelta(minutes=minutes_from_now)
        elif hours_from_now:
            schedule_time = datetime.now() + timedelta(hours=hours_from_now)
        else:
            # Usa tempos padrão baseado na tentativa
            if attempt_number == 1:
                schedule_time = datetime.now() + timedelta(minutes=DEFAULT_FIRST_FOLLOW_UP_MINUTES)
            else:
                schedule_time = datetime.now() + timedelta(hours=DEFAULT_SECOND_FOLLOW_UP_HOURS)
        
        # Prepara contexto para mensagem
        message_context = {
            "name": lead.name or "",
            "last_stage": lead.current_stage.value if hasattr(lead.current_stage, 'value') else lead.current_stage,
            "property_type": lead.property_type.value if lead.property_type and hasattr(lead.property_type, 'value') else lead.property_type,
            "attempt_number": attempt_number
        }
        
        # Adiciona contexto extra se fornecido
        if context:
            message_context.update(context)
        
        # Agenda o follow-up
        followup_repo = get_followup_repository()
        follow_up = await followup_repo.schedule_follow_up(
            lead_id=lead.id,
            follow_up_type=followup_type_enum,
            scheduled_at=schedule_time,
            message=custom_message,
            context=message_context,
            attempt_number=attempt_number
        )
        
        if not follow_up:
            logger.error("Falha ao agendar follow-up")
            return {
                "success": False,
                "error": "Falha ao agendar follow-up",
                "error_type": "database"
            }
        
        # Verifica se é o segundo follow-up (última tentativa)
        if attempt_number >= 2:
            logger.info(f"Segundo follow-up agendado. Se não houver resposta, lead será marcado como NOT_INTERESTED")
        
        logger.success(f"Follow-up agendado com sucesso: ID={follow_up.id}")
        
        return {
            "success": True,
            "follow_up_id": str(follow_up.id),
            "lead_id": str(lead.id),
            "data": {
                "type": follow_up.type.value if hasattr(follow_up.type, 'value') else follow_up.type,
                "scheduled_at": follow_up.scheduled_at.isoformat(),
                "scheduled_in_minutes": round((follow_up.scheduled_at - datetime.now()).total_seconds() / 60, 1),
                "message": follow_up.message[:100] + "..." if len(follow_up.message) > 100 else follow_up.message,
                "attempt_number": follow_up.attempt_number,
                "status": follow_up.status.value if hasattr(follow_up.status, 'value') else follow_up.status,
                "is_final_attempt": attempt_number >= 2,
                "lead_info": {
                    "name": lead.name,
                    "phone": lead.phone_number,
                    "stage": lead.current_stage.value if hasattr(lead.current_stage, 'value') else lead.current_stage
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Erro inesperado ao agendar follow-up: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao agendar follow-up: {str(e)}",
            "error_type": "database"
        }


# Exporta a tool
ScheduleFollowUpTool = schedule_followup