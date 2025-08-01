"""
Repository para gerenciamento de follow-ups inteligentes
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from loguru import logger

from ..core.types import FollowUp, FollowUpType, FollowUpStatus, LeadStage
from ..core.logger import setup_module_logger
from ..services import get_supabase_service, get_evolution_service
from ..utils.formatters import format_phone_number, format_datetime
from ..utils.validators import validate_business_hours

# Singleton instance
_followup_repository_instance = None

logger = setup_module_logger(__name__)

# Configurações de follow-up
FIRST_FOLLOW_UP_MINUTES = 30
SECOND_FOLLOW_UP_HOURS = 24
MAX_ATTEMPTS = 2

# Horário comercial
BUSINESS_START_HOUR = 8
BUSINESS_END_HOUR = 18
BUSINESS_DAYS = [0, 1, 2, 3, 4, 5]  # Segunda a Sábado (0=Segunda, 6=Domingo)


class FollowUpRepository:
    """Repository para gerenciar follow-ups de leads"""
    
    def __init__(self):
        """Inicializa o repository com as dependências necessárias"""
        self.supabase = get_supabase_service()
        self.evolution = get_evolution_service()
        logger.info("FollowUpRepository iniciado")
    
    def _generate_follow_up_message(self, context: Dict[str, Any]) -> str:
        """
        Gera mensagem personalizada de follow-up baseada no contexto
        
        Args:
            context: Contexto do lead incluindo nome, estágio, etc.
            
        Returns:
            Mensagem personalizada
        """
        name = context.get("name", "")
        last_stage = context.get("last_stage", "")
        last_topic = context.get("last_topic", "")
        property_type = context.get("property_type", "")
        
        # Mensagens personalizadas por contexto
        if "scheduling" in last_stage.lower() or last_stage == LeadStage.SCHEDULING.value:
            return f"Oi {name}! 👋 Vi que você estava escolhendo um horário para nossa reunião. Ainda posso ajudar você a agendar? 😊"
        
        elif "bill" in last_topic.lower() or "conta" in last_topic.lower():
            return f"Oi {name}! 📄 Você conseguiu encontrar sua conta de luz? Posso ajudar a analisar o potencial de economia! 💡"
        
        elif property_type and "casa" in property_type.lower():
            return f"Oi {name}! 🏠 Ainda estou por aqui para ajudar você a economizar até 95% na conta de luz da sua casa! ⚡"
        
        elif property_type and "empresa" in property_type.lower():
            return f"Oi {name}! 🏢 Que tal reduzir os custos de energia da sua empresa em até 95%? Ainda posso ajudar! 💰"
        
        else:
            # Mensagem genérica
            return f"Oi {name}! 😊 Tudo bem? Ainda estou por aqui para ajudar você a economizar até 95% na conta de luz! ⚡ Vamos conversar?"
    
    def _calculate_next_follow_up_time(self, attempt_number: int, last_interaction: datetime) -> datetime:
        """
        Calcula o próximo horário de follow-up respeitando horário comercial
        
        Args:
            attempt_number: Número da tentativa (1 ou 2)
            last_interaction: Última interação com o lead
            
        Returns:
            Datetime do próximo follow-up
        """
        now = datetime.now()
        
        if attempt_number == 1:
            # Primeira tentativa: 30 minutos após
            next_time = last_interaction + timedelta(minutes=FIRST_FOLLOW_UP_MINUTES)
        else:
            # Segunda tentativa: 24 horas após a primeira
            next_time = now + timedelta(hours=SECOND_FOLLOW_UP_HOURS)
        
        # Se caiu fora do horário comercial, ajusta
        next_time = self._adjust_to_business_hours(next_time)
        
        # Se o tempo calculado já passou, agenda para próximo horário disponível
        if next_time <= now:
            next_time = self._adjust_to_business_hours(now + timedelta(minutes=5))
        
        return next_time
    
    def _adjust_to_business_hours(self, dt: datetime) -> datetime:
        """
        Ajusta datetime para o próximo horário comercial disponível
        
        Args:
            dt: Datetime para ajustar
            
        Returns:
            Datetime ajustado para horário comercial
        """
        # Se é domingo, move para segunda
        if dt.weekday() == 6:
            dt = dt.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
            dt += timedelta(days=1)
        
        # Se é sábado após 13h, move para segunda
        elif dt.weekday() == 5 and dt.hour >= 13:
            dt = dt.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
            dt += timedelta(days=2)
        
        # Se está antes do horário comercial
        elif dt.hour < BUSINESS_START_HOUR:
            dt = dt.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
        
        # Se está após horário comercial
        elif dt.hour >= BUSINESS_END_HOUR:
            # Move para próximo dia útil
            dt = dt.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
            dt += timedelta(days=1)
            # Recursão para garantir que caiu em dia útil
            dt = self._adjust_to_business_hours(dt)
        
        return dt
    
    async def schedule_smart_follow_up(
        self, 
        lead_id: UUID, 
        phone: str, 
        context: Dict[str, Any]
    ) -> FollowUp:
        """
        Agenda follow-up inteligente com mensagem contextualizada
        
        Args:
            lead_id: ID do lead
            phone: Telefone do lead
            context: Contexto incluindo nome, estágio, etc.
            
        Returns:
            FollowUp criado
        """
        try:
            # Formata telefone
            phone = format_phone_number(phone)
            
            # Verifica tentativas anteriores
            existing = await self._get_lead_follow_up_count(lead_id)
            attempt_number = existing + 1
            
            if attempt_number > MAX_ATTEMPTS:
                logger.warning(f"Lead {lead_id} já atingiu máximo de tentativas")
                raise ValueError("Máximo de tentativas de follow-up atingido")
            
            # Calcula próximo horário
            last_interaction = context.get("last_interaction", datetime.now())
            scheduled_at = self._calculate_next_follow_up_time(attempt_number, last_interaction)
            
            # Gera mensagem personalizada
            message = self._generate_follow_up_message(context)
            
            # Determina tipo de follow-up
            follow_up_type = FollowUpType.REMINDER
            if attempt_number == 2:
                follow_up_type = FollowUpType.REENGAGEMENT
            elif context.get("last_stage") == LeadStage.SCHEDULING.value:
                follow_up_type = FollowUpType.HOT_LEAD_RESCUE
            
            # Cria follow-up no banco
            follow_up_data = {
                "lead_id": str(lead_id),
                "scheduled_at": scheduled_at.isoformat(),
                "type": follow_up_type.value,
                "message": message,
                "status": FollowUpStatus.PENDING.value,
                "attempt_number": attempt_number,
                "created_at": datetime.now().isoformat()
            }
            
            result = await self.supabase.table("follow_ups").insert(follow_up_data).execute()
            
            if result.data:
                follow_up = FollowUp(**result.data[0])
                logger.info(
                    f"Follow-up agendado para lead {lead_id}",
                    extra={
                        "lead_id": str(lead_id),
                        "scheduled_at": scheduled_at.isoformat(),
                        "attempt": attempt_number,
                        "type": follow_up_type.value
                    }
                )
                return follow_up
            else:
                raise Exception("Falha ao criar follow-up no banco")
                
        except Exception as e:
            logger.error(f"Erro ao agendar follow-up: {str(e)}")
            raise
    
    async def get_due_follow_ups(self, limit: int = 50) -> List[FollowUp]:
        """
        Busca follow-ups vencidos que precisam ser executados
        
        Args:
            limit: Limite de registros
            
        Returns:
            Lista de follow-ups pendentes
        """
        try:
            now = datetime.now()
            
            # Busca follow-ups pendentes com scheduled_at <= agora
            result = await self.supabase.table("follow_ups") \
                .select("*") \
                .eq("status", FollowUpStatus.PENDING.value) \
                .lte("scheduled_at", now.isoformat()) \
                .order("scheduled_at") \
                .limit(limit) \
                .execute()
            
            follow_ups = [FollowUp(**data) for data in result.data] if result.data else []
            
            if follow_ups:
                logger.info(f"Encontrados {len(follow_ups)} follow-ups vencidos")
            
            return follow_ups
            
        except Exception as e:
            logger.error(f"Erro ao buscar follow-ups vencidos: {str(e)}")
            return []
    
    async def execute_follow_up(self, follow_up_id: UUID) -> Dict[str, Any]:
        """
        Executa follow-up enviando mensagem via WhatsApp
        
        Args:
            follow_up_id: ID do follow-up
            
        Returns:
            Resultado da execução
        """
        try:
            # Busca follow-up com dados do lead
            result = await self.supabase.table("follow_ups") \
                .select("*, leads(phone_number, name)") \
                .eq("id", str(follow_up_id)) \
                .single() \
                .execute()
            
            if not result.data:
                raise ValueError("Follow-up não encontrado")
            
            follow_up_data = result.data
            lead_data = follow_up_data.get("leads", {})
            
            if not lead_data or not lead_data.get("phone_number"):
                raise ValueError("Dados do lead não encontrados")
            
            phone = format_phone_number(lead_data["phone_number"])
            message = follow_up_data["message"]
            
            logger.info(
                f"Executando follow-up {follow_up_id}",
                extra={
                    "follow_up_id": str(follow_up_id),
                    "phone": phone,
                    "attempt": follow_up_data["attempt_number"]
                }
            )
            
            # Envia mensagem via Evolution API
            send_result = await self.evolution.send_text(
                to=phone,
                text=message,
                instance="primary"  # Ajustar conforme configuração
            )
            
            # Atualiza status do follow-up
            success = send_result.get("success", False)
            execution_result = {
                "success": success,
                "message_id": send_result.get("id"),
                "error": send_result.get("error"),
                "executed_at": datetime.now().isoformat()
            }
            
            await self.mark_follow_up_executed(
                follow_up_id=follow_up_id,
                success=success,
                result=execution_result
            )
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Erro ao executar follow-up {follow_up_id}: {str(e)}")
            
            # Marca como falha
            await self.mark_follow_up_executed(
                follow_up_id=follow_up_id,
                success=False,
                result={"error": str(e), "executed_at": datetime.now().isoformat()}
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def mark_follow_up_executed(
        self, 
        follow_up_id: UUID, 
        success: bool, 
        result: Dict[str, Any]
    ) -> FollowUp:
        """
        Marca follow-up como executado
        
        Args:
            follow_up_id: ID do follow-up
            success: Se foi executado com sucesso
            result: Resultado da execução
            
        Returns:
            FollowUp atualizado
        """
        try:
            status = FollowUpStatus.EXECUTED if success else FollowUpStatus.FAILED
            
            update_data = {
                "status": status.value,
                "executed_at": datetime.now().isoformat(),
                "result": result,
                "updated_at": datetime.now().isoformat()
            }
            
            result = await self.supabase.table("follow_ups") \
                .update(update_data) \
                .eq("id", str(follow_up_id)) \
                .execute()
            
            if result.data:
                follow_up = FollowUp(**result.data[0])
                logger.info(
                    f"Follow-up {follow_up_id} marcado como {status.value}",
                    extra={"follow_up_id": str(follow_up_id), "status": status.value}
                )
                return follow_up
            else:
                raise Exception("Falha ao atualizar follow-up")
                
        except Exception as e:
            logger.error(f"Erro ao marcar follow-up como executado: {str(e)}")
            raise
    
    async def cancel_lead_follow_ups(self, lead_id: UUID, reason: str) -> int:
        """
        Cancela todos os follow-ups pendentes de um lead
        
        Args:
            lead_id: ID do lead
            reason: Motivo do cancelamento
            
        Returns:
            Quantidade de follow-ups cancelados
        """
        try:
            # Busca follow-ups pendentes
            result = await self.supabase.table("follow_ups") \
                .select("id") \
                .eq("lead_id", str(lead_id)) \
                .eq("status", FollowUpStatus.PENDING.value) \
                .execute()
            
            if not result.data:
                return 0
            
            follow_up_ids = [item["id"] for item in result.data]
            
            # Atualiza para cancelado
            update_data = {
                "status": FollowUpStatus.CANCELLED.value,
                "result": {"reason": reason, "cancelled_at": datetime.now().isoformat()},
                "updated_at": datetime.now().isoformat()
            }
            
            await self.supabase.table("follow_ups") \
                .update(update_data) \
                .in_("id", follow_up_ids) \
                .execute()
            
            cancelled_count = len(follow_up_ids)
            logger.info(
                f"Cancelados {cancelled_count} follow-ups do lead {lead_id}",
                extra={
                    "lead_id": str(lead_id),
                    "cancelled_count": cancelled_count,
                    "reason": reason
                }
            )
            
            return cancelled_count
            
        except Exception as e:
            logger.error(f"Erro ao cancelar follow-ups: {str(e)}")
            return 0
    
    async def reschedule_follow_up(self, follow_up_id: UUID, new_time: datetime) -> FollowUp:
        """
        Reagenda um follow-up para novo horário
        
        Args:
            follow_up_id: ID do follow-up
            new_time: Novo horário
            
        Returns:
            FollowUp atualizado
        """
        try:
            # Ajusta para horário comercial
            new_time = self._adjust_to_business_hours(new_time)
            
            # Valida horário comercial
            is_valid, error = validate_business_hours(new_time)
            if not is_valid:
                raise ValueError(f"Horário inválido: {error}")
            
            # Atualiza follow-up
            update_data = {
                "scheduled_at": new_time.isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = await self.supabase.table("follow_ups") \
                .update(update_data) \
                .eq("id", str(follow_up_id)) \
                .eq("status", FollowUpStatus.PENDING.value) \
                .execute()
            
            if result.data:
                follow_up = FollowUp(**result.data[0])
                logger.info(
                    f"Follow-up {follow_up_id} reagendado",
                    extra={
                        "follow_up_id": str(follow_up_id),
                        "new_time": new_time.isoformat()
                    }
                )
                return follow_up
            else:
                raise Exception("Follow-up não encontrado ou já executado")
                
        except Exception as e:
            logger.error(f"Erro ao reagendar follow-up: {str(e)}")
            raise
    
    async def get_follow_up_history(self, lead_id: UUID) -> List[FollowUp]:
        """
        Busca histórico completo de follow-ups de um lead
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Lista de follow-ups ordenados por data
        """
        try:
            result = await self.supabase.table("follow_ups") \
                .select("*") \
                .eq("lead_id", str(lead_id)) \
                .order("created_at", desc=True) \
                .execute()
            
            follow_ups = [FollowUp(**data) for data in result.data] if result.data else []
            
            logger.debug(
                f"Histórico de follow-ups do lead {lead_id}: {len(follow_ups)} registros"
            )
            
            return follow_ups
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico de follow-ups: {str(e)}")
            return []
    
    async def should_give_up(self, lead_id: UUID) -> bool:
        """
        Verifica se deve desistir do lead após múltiplas tentativas
        
        Args:
            lead_id: ID do lead
            
        Returns:
            True se deve marcar como NOT_INTERESTED
        """
        try:
            # Busca follow-ups executados ou falhados
            result = await self.supabase.table("follow_ups") \
                .select("status, attempt_number") \
                .eq("lead_id", str(lead_id)) \
                .in_("status", [FollowUpStatus.EXECUTED.value, FollowUpStatus.FAILED.value]) \
                .execute()
            
            if not result.data:
                return False
            
            # Conta tentativas
            attempts = len(result.data)
            max_attempt = max(item["attempt_number"] for item in result.data)
            
            # Desiste após MAX_ATTEMPTS tentativas
            should_give_up = attempts >= MAX_ATTEMPTS or max_attempt >= MAX_ATTEMPTS
            
            if should_give_up:
                logger.info(
                    f"Lead {lead_id} deve ser marcado como NOT_INTERESTED",
                    extra={
                        "lead_id": str(lead_id),
                        "attempts": attempts,
                        "max_attempt": max_attempt
                    }
                )
            
            return should_give_up
            
        except Exception as e:
            logger.error(f"Erro ao verificar se deve desistir do lead: {str(e)}")
            return False
    
    async def _get_lead_follow_up_count(self, lead_id: UUID) -> int:
        """
        Conta quantos follow-ups já foram criados para o lead
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Quantidade de follow-ups
        """
        try:
            result = await self.supabase.table("follow_ups") \
                .select("id", count="exact") \
                .eq("lead_id", str(lead_id)) \
                .execute()
            
            return result.count if result.count else 0
            
        except Exception as e:
            logger.error(f"Erro ao contar follow-ups do lead: {str(e)}")
            return 0
    
    async def get_pending_follow_ups_count(self) -> int:
        """
        Conta total de follow-ups pendentes no sistema
        
        Returns:
            Quantidade de follow-ups pendentes
        """
        try:
            result = await self.supabase.table("follow_ups") \
                .select("id", count="exact") \
                .eq("status", FollowUpStatus.PENDING.value) \
                .execute()
            
            return result.count if result.count else 0
            
        except Exception as e:
            logger.error(f"Erro ao contar follow-ups pendentes: {str(e)}")
            return 0
    
    async def get_follow_up_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Retorna estatísticas de follow-ups dos últimos dias
        
        Args:
            days: Quantidade de dias para análise
            
        Returns:
            Dicionário com estatísticas
        """
        try:
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Busca todos os follow-ups do período
            result = await self.supabase.table("follow_ups") \
                .select("status, type, attempt_number") \
                .gte("created_at", since_date) \
                .execute()
            
            if not result.data:
                return {
                    "total": 0,
                    "pending": 0,
                    "executed": 0,
                    "failed": 0,
                    "cancelled": 0,
                    "success_rate": 0.0
                }
            
            # Calcula estatísticas
            stats = {
                "total": len(result.data),
                "pending": sum(1 for f in result.data if f["status"] == FollowUpStatus.PENDING.value),
                "executed": sum(1 for f in result.data if f["status"] == FollowUpStatus.EXECUTED.value),
                "failed": sum(1 for f in result.data if f["status"] == FollowUpStatus.FAILED.value),
                "cancelled": sum(1 for f in result.data if f["status"] == FollowUpStatus.CANCELLED.value),
            }
            
            # Taxa de sucesso
            total_attempts = stats["executed"] + stats["failed"]
            stats["success_rate"] = (
                (stats["executed"] / total_attempts * 100) if total_attempts > 0 else 0.0
            )
            
            # Por tipo
            stats["by_type"] = {}
            for follow_up_type in FollowUpType:
                count = sum(1 for f in result.data if f["type"] == follow_up_type.value)
                if count > 0:
                    stats["by_type"][follow_up_type.value] = count
            
            # Por tentativa
            stats["by_attempt"] = {}
            for i in range(1, MAX_ATTEMPTS + 1):
                count = sum(1 for f in result.data if f["attempt_number"] == i)
                if count > 0:
                    stats["by_attempt"][f"attempt_{i}"] = count
            
            logger.info(f"Estatísticas de follow-ups calculadas para {days} dias")
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas de follow-ups: {str(e)}")
            return {}

def get_followup_repository() -> FollowUpRepository:
    """
    Retorna instância singleton do FollowUpRepository
    
    Returns:
        Instância do FollowUpRepository
    """
    global _followup_repository_instance
    
    if _followup_repository_instance is None:
        _followup_repository_instance = FollowUpRepository()
    
    return _followup_repository_instance