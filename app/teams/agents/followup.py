"""
FollowUpAgent - Agente Especializado em Follow-up e Nurturing
Responsável por reengajamento, nutrição de leads e campanhas de follow-up
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from agno.agent import Agent
from agno.tools import tool
from loguru import logger

from app.integrations.supabase_client import supabase_client
from app.integrations.evolution import evolution_client
from app.config import settings


class FollowUpType(Enum):
    """Tipos de follow-up"""
    IMMEDIATE_REENGAGEMENT = "immediate_reengagement"  # Reengajamento imediato
    DAILY_NURTURING = "daily_nurturing"                # Nutrição diária
    MEETING_CONFIRMATION = "meeting_confirmation"       # Confirmação de reunião
    MEETING_REMINDER = "meeting_reminder"               # Lembrete de reunião
    ABANDONMENT_CHECK = "abandonment_check"             # Verificação de abandono
    VALUE_CONTENT = "value_content"                     # Conteúdo de valor
    OBJECTION_HANDLING = "objection_handling"           # Tratamento de objeção
    SPECIAL_OFFER = "special_offer"                     # Oferta especial


class FollowUpStrategy(Enum):
    """Estratégias de follow-up baseadas em temperatura do lead"""
    AGGRESSIVE = "aggressive"    # Para leads quentes (HOT)
    MODERATE = "moderate"        # Para leads mornos (WARM)
    GENTLE = "gentle"            # Para leads frios (COLD)
    EDUCATIONAL = "educational"  # Para leads não qualificados


class FollowUpAgent:
    """
    Agente especializado em follow-up e nurturing de leads
    Gerencia campanhas de reengajamento e nutrição
    """
    
    def __init__(self, model, storage):
        """
        Inicializa o agente de follow-up
        
        Args:
            model: Modelo LLM a ser usado
            storage: Storage para persistência
        """
        self.model = model
        self.storage = storage
        self.evolution = evolution_client
        
        # Configurações de follow-up
        self.followup_config = {
            "max_attempts": 3,
            "retry_intervals": {
                "immediate": timedelta(hours=2),
                "daily": timedelta(days=1),
                "weekly": timedelta(days=7)
            },
            "business_hours": {
                "start": 9,
                "end": 20
            },
            "optimal_times": {
                "morning": (9, 11),
                "lunch": (12, 14),
                "afternoon": (15, 17),
                "evening": (18, 20)
            }
        }
        
        # Carregar prompt master do arquivo
        self.prompt_master = self._load_prompt_master()
        
        # Configuração de mensagens de follow-up
        # As mensagens serão geradas dinamicamente usando o prompt master
        
        # Tools do agente
        self.tools = [
            self.schedule_followup,
            self.send_followup_message,
            self.create_nurturing_campaign,
            self.check_followup_status,
            self.cancel_followup,
            self.get_best_followup_time,
            self.track_engagement,
            self.personalize_message
        ]
        
        # Criar o agente
        self.agent = Agent(
            name="Follow-up Specialist",
            model=self.model,
            instructions="""Você é um especialista em follow-up e nurturing de leads.
            
            Suas responsabilidades:
            1. Reengajar leads que abandonaram a conversa
            2. Nutrir leads com conteúdo relevante
            3. Confirmar e lembrar reuniões agendadas
            4. Personalizar mensagens baseadas no perfil do lead
            5. Otimizar timing de envio para máximo engajamento
            
            Estratégias:
            - HOT leads: Follow-up agressivo, criar urgência
            - WARM leads: Nutrição moderada, construir confiança
            - COLD leads: Educação gentil, plantar sementes
            
            Princípios:
            - Nunca ser invasivo ou spam
            - Sempre agregar valor na mensagem
            - Personalização é fundamental
            - Respeitar horário comercial
            - Máximo 3 tentativas por ciclo
            
            Diretrizes:
            - Analise o histórico de interações do lead
            - Escolha a estratégia apropriada baseada na temperatura
            - Personalize a mensagem com dados específicos
            - Respeite limites de tentativas e horários
            - Rastreie engajamento e ajuste estratégia
            - Sempre ofereça valor, não apenas venda""",
            
            tools=self.tools
        )
        
        logger.info("✅ FollowUpAgent inicializado")
    
    @tool
    async def schedule_followup(
        self,
        lead_id: str,
        followup_type: str,
        delay_hours: int,
        message: Optional[str] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Agenda um follow-up para o lead
        
        Args:
            lead_id: ID do lead
            followup_type: Tipo de follow-up
            delay_hours: Horas até o follow-up
            message: Mensagem personalizada (opcional)
            priority: Prioridade (low/normal/high/urgent)
            
        Returns:
            Detalhes do follow-up agendado
        """
        try:
            # Calcular horário do follow-up
            scheduled_at = datetime.now() + timedelta(hours=delay_hours)
            
            # Ajustar para horário comercial se necessário
            scheduled_at = self._adjust_to_business_hours(scheduled_at)
            
            # Buscar dados do lead
            lead = await supabase_client.get_lead(lead_id)
            if not lead:
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }
            
            # Preparar mensagem se não foi fornecida
            if not message:
                message = await self._generate_followup_message(
                    lead, followup_type
                )
            
            # Salvar follow-up no banco
            followup_data = {
                "lead_id": lead_id,
                "type": followup_type,
                "scheduled_at": scheduled_at.isoformat(),
                "message": message,
                "priority": priority,
                "status": "pending",
                "attempts": 0,
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase_client.client.table("follow_ups")\
                .insert(followup_data)\
                .execute()
            
            if result.data:
                logger.info(f"📅 Follow-up agendado para {lead.get('name')} em {scheduled_at}")
                
                return {
                    "success": True,
                    "followup_id": result.data[0]["id"],
                    "scheduled_at": scheduled_at.isoformat(),
                    "type": followup_type,
                    "message": f"Follow-up agendado para {scheduled_at.strftime('%d/%m às %H:%M')}"
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao salvar follow-up"
                }
                
        except Exception as e:
            logger.error(f"Erro ao agendar follow-up: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def send_followup_message(
        self,
        lead_id: str,
        message: str,
        followup_type: str,
        track_response: bool = True
    ) -> Dict[str, Any]:
        """
        Envia mensagem de follow-up imediatamente
        
        Args:
            lead_id: ID do lead
            message: Mensagem a enviar
            followup_type: Tipo de follow-up
            track_response: Se deve rastrear resposta
            
        Returns:
            Status do envio
        """
        try:
            # Buscar dados do lead
            lead = await supabase_client.get_lead(lead_id)
            if not lead:
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }
            
            # Enviar via Evolution API
            sent = await self.evolution.send_text(
                number=lead.get("phone"),
                text=message
            )
            
            if sent:
                # Registrar envio
                supabase_client.client.table("messages").insert({
                    "lead_id": lead_id,
                    "sender": "assistant",
                    "content": message,
                    "message_type": "followup",
                    "metadata": {
                        "followup_type": followup_type,
                        "track_response": track_response
                    },
                    "created_at": datetime.now().isoformat()
                }).execute()
                
                # Atualizar último contato
                await supabase_client.update_lead(lead_id, {
                    "last_followup_at": datetime.now().isoformat(),
                    "last_followup_type": followup_type
                })
                
                logger.info(f"📤 Follow-up enviado para {lead.get('name')}")
                
                return {
                    "success": True,
                    "message_sent": message,
                    "sent_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao enviar mensagem"
                }
                
        except Exception as e:
            logger.error(f"Erro ao enviar follow-up: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def create_nurturing_campaign(
        self,
        lead_id: str,
        campaign_type: str = "standard",
        duration_days: int = 7,
        messages_per_day: int = 1
    ) -> Dict[str, Any]:
        """
        Cria campanha de nurturing para o lead
        
        Args:
            lead_id: ID do lead
            campaign_type: Tipo de campanha (standard/aggressive/gentle)
            duration_days: Duração em dias
            messages_per_day: Mensagens por dia
            
        Returns:
            Detalhes da campanha criada
        """
        try:
            # Buscar dados e classificação do lead
            lead = await supabase_client.get_lead(lead_id)
            if not lead:
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }
            
            # Determinar estratégia baseada na classificação
            classification = lead.get("classification", "cold")
            strategy = self._get_strategy_for_classification(classification)
            
            # Gerar sequência de follow-ups
            followups = []
            current_date = datetime.now()
            
            for day in range(duration_days):
                for msg_num in range(messages_per_day):
                    # Calcular horário otimizado
                    scheduled_time = current_date + timedelta(
                        days=day,
                        hours=self._get_optimal_hour(msg_num)
                    )
                    
                    # Escolher tipo de follow-up variado
                    followup_types = [
                        FollowUpType.DAILY_NURTURING,
                        FollowUpType.VALUE_CONTENT,
                        FollowUpType.SPECIAL_OFFER
                    ]
                    followup_type = followup_types[day % len(followup_types)]
                    
                    followups.append({
                        "lead_id": lead_id,
                        "type": followup_type.value,
                        "scheduled_at": scheduled_time.isoformat(),
                        "campaign_id": f"campaign_{lead_id}_{datetime.now().timestamp()}",
                        "status": "pending",
                        "priority": "normal" if strategy == "gentle" else "high"
                    })
            
            # Salvar todos os follow-ups
            for followup in followups:
                supabase_client.client.table("follow_ups")\
                    .insert(followup)\
                    .execute()
            
            logger.info(f"🎯 Campanha de nurturing criada: {len(followups)} mensagens")
            
            return {
                "success": True,
                "campaign_id": followups[0]["campaign_id"],
                "total_messages": len(followups),
                "duration_days": duration_days,
                "strategy": strategy,
                "start_date": current_date.isoformat(),
                "end_date": (current_date + timedelta(days=duration_days)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar campanha: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def check_followup_status(
        self,
        lead_id: str,
        include_history: bool = False
    ) -> Dict[str, Any]:
        """
        Verifica status de follow-ups do lead
        
        Args:
            lead_id: ID do lead
            include_history: Se deve incluir histórico
            
        Returns:
            Status dos follow-ups
        """
        try:
            # Buscar follow-ups pendentes
            pending = supabase_client.client.table("follow_ups")\
                .select("*")\
                .eq("lead_id", lead_id)\
                .eq("status", "pending")\
                .order("scheduled_at")\
                .execute()
            
            result = {
                "lead_id": lead_id,
                "pending_count": len(pending.data) if pending.data else 0,
                "pending_followups": []
            }
            
            if pending.data:
                for f in pending.data[:5]:  # Máximo 5
                    result["pending_followups"].append({
                        "id": f["id"],
                        "type": f["type"],
                        "scheduled_at": f["scheduled_at"],
                        "priority": f.get("priority", "normal")
                    })
                
                # Próximo follow-up
                next_followup = pending.data[0]
                result["next_followup"] = {
                    "type": next_followup["type"],
                    "scheduled_at": next_followup["scheduled_at"],
                    "in_hours": self._hours_until(next_followup["scheduled_at"])
                }
            
            # Incluir histórico se solicitado
            if include_history:
                completed = supabase_client.client.table("follow_ups")\
                    .select("*")\
                    .eq("lead_id", lead_id)\
                    .eq("status", "completed")\
                    .order("completed_at", desc=True)\
                    .limit(10)\
                    .execute()
                
                result["history"] = []
                if completed.data:
                    for f in completed.data:
                        result["history"].append({
                            "type": f["type"],
                            "sent_at": f.get("completed_at"),
                            "response_received": f.get("response_received", False)
                        })
                
                result["total_sent"] = len(completed.data) if completed.data else 0
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}")
            return {
                "lead_id": lead_id,
                "error": str(e)
            }
    
    @tool
    async def cancel_followup(
        self,
        followup_id: Optional[str] = None,
        lead_id: Optional[str] = None,
        cancel_all: bool = False
    ) -> Dict[str, Any]:
        """
        Cancela follow-up(s)
        
        Args:
            followup_id: ID específico do follow-up
            lead_id: ID do lead (para cancelar todos)
            cancel_all: Se deve cancelar todos do lead
            
        Returns:
            Status do cancelamento
        """
        try:
            if followup_id:
                # Cancelar específico
                result = supabase_client.client.table("follow_ups")\
                    .update({"status": "cancelled"})\
                    .eq("id", followup_id)\
                    .execute()
                
                return {
                    "success": True,
                    "cancelled_count": 1,
                    "message": "Follow-up cancelado"
                }
            
            elif lead_id and cancel_all:
                # Cancelar todos do lead
                result = supabase_client.client.table("follow_ups")\
                    .update({"status": "cancelled"})\
                    .eq("lead_id", lead_id)\
                    .eq("status", "pending")\
                    .execute()
                
                count = len(result.data) if result.data else 0
                
                return {
                    "success": True,
                    "cancelled_count": count,
                    "message": f"{count} follow-ups cancelados"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Especifique followup_id ou lead_id com cancel_all"
                }
                
        except Exception as e:
            logger.error(f"Erro ao cancelar follow-up: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def get_best_followup_time(
        self,
        lead_id: str,
        preferred_period: Optional[str] = None  # morning/lunch/afternoon/evening
    ) -> Dict[str, Any]:
        """
        Determina melhor horário para follow-up
        
        Args:
            lead_id: ID do lead
            preferred_period: Período preferido (opcional)
            
        Returns:
            Melhor horário para contato
        """
        try:
            # Analisar histórico de interações
            messages = supabase_client.client.table("messages")\
                .select("created_at, sender")\
                .eq("lead_id", lead_id)\
                .eq("sender", "user")\
                .order("created_at", desc=True)\
                .limit(20)\
                .execute()
            
            # Calcular horários de maior engajamento
            engagement_hours = {}
            if messages.data:
                for msg in messages.data:
                    hour = datetime.fromisoformat(msg["created_at"]).hour
                    engagement_hours[hour] = engagement_hours.get(hour, 0) + 1
            
            # Determinar melhor horário
            if engagement_hours:
                # Hora com mais engajamento
                best_hour = max(engagement_hours, key=engagement_hours.get)
            else:
                # Usar período preferido ou padrão
                if preferred_period:
                    period_hours = self.followup_config["optimal_times"].get(
                        preferred_period, (10, 11)
                    )
                    best_hour = period_hours[0]
                else:
                    best_hour = 10  # Padrão: 10h da manhã
            
            # Criar timestamp para próximo horário disponível
            now = datetime.now()
            next_time = now.replace(hour=best_hour, minute=0, second=0)
            
            if next_time <= now:
                next_time += timedelta(days=1)
            
            # Ajustar para dia útil
            while next_time.weekday() >= 5:  # Sábado ou Domingo
                next_time += timedelta(days=1)
            
            return {
                "best_time": next_time.isoformat(),
                "best_hour": best_hour,
                "period": self._get_period_name(best_hour),
                "confidence": "high" if engagement_hours else "medium",
                "based_on": f"{len(messages.data)} interações" if messages.data else "padrão"
            }
            
        except Exception as e:
            logger.error(f"Erro ao determinar melhor horário: {e}")
            return {
                "best_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                "error": str(e)
            }
    
    @tool
    async def track_engagement(
        self,
        lead_id: str,
        followup_id: str,
        response_received: bool,
        response_time_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Rastreia engajamento com follow-up
        
        Args:
            lead_id: ID do lead
            followup_id: ID do follow-up
            response_received: Se houve resposta
            response_time_minutes: Tempo até resposta (opcional)
            
        Returns:
            Métricas de engajamento
        """
        try:
            # Atualizar follow-up
            update_data = {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "response_received": response_received
            }
            
            if response_time_minutes:
                update_data["response_time_minutes"] = response_time_minutes
            
            supabase_client.client.table("follow_ups")\
                .update(update_data)\
                .eq("id", followup_id)\
                .execute()
            
            # Calcular métricas de engajamento
            all_followups = supabase_client.client.table("follow_ups")\
                .select("*")\
                .eq("lead_id", lead_id)\
                .eq("status", "completed")\
                .execute()
            
            if all_followups.data:
                total = len(all_followups.data)
                responded = len([f for f in all_followups.data if f.get("response_received")])
                response_rate = (responded / total) * 100
                
                # Calcular tempo médio de resposta
                response_times = [
                    f.get("response_time_minutes", 0) 
                    for f in all_followups.data 
                    if f.get("response_time_minutes")
                ]
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            else:
                response_rate = 0
                avg_response_time = 0
            
            # Atualizar métricas do lead
            await supabase_client.update_lead(lead_id, {
                "engagement_rate": response_rate,
                "avg_response_time_minutes": avg_response_time,
                "last_engagement": datetime.now().isoformat() if response_received else None
            })
            
            return {
                "success": True,
                "lead_id": lead_id,
                "response_rate": f"{response_rate:.1f}%",
                "avg_response_time": f"{avg_response_time:.0f} minutos",
                "total_followups": total if all_followups.data else 1,
                "total_responses": responded if all_followups.data else (1 if response_received else 0)
            }
            
        except Exception as e:
            logger.error(f"Erro ao rastrear engajamento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def personalize_message(
        self,
        lead_id: str,
        template_type: str,
        include_data: bool = True
    ) -> str:
        """
        Personaliza mensagem para o lead
        
        Args:
            lead_id: ID do lead
            template_type: Tipo de template
            include_data: Se deve incluir dados específicos
            
        Returns:
            Mensagem personalizada
        """
        try:
            # Buscar dados do lead
            lead = await supabase_client.get_lead(lead_id)
            if not lead:
                return "Olá! Como posso ajudar você hoje?"
            
            # Preparar dados para personalização
            lead_name = lead.get("name", "").split()[0] if lead.get("name") else "você"
            bill_value = lead.get('bill_value', 0)
            
            # Gerar mensagem baseada no tipo de follow-up usando o padrão do prompt master
            # As mensagens seguem o padrão definido no ESTÁGIO 7 do prompt-agente.md
            if template_type.upper() == "IMMEDIATE_REENGAGEMENT":
                # Follow-up após 30-60 minutos
                message = f"Olá, {lead_name}! Vi que nossa conversa ficou pela metade. Posso continuar te ajudando com a economia na conta de luz?"
                
            elif template_type.upper() == "DAILY_NURTURING":
                # Follow-up diário
                savings = bill_value * 0.2
                message = f"{lead_name}, se ainda tiver interesse em economizar R${savings:.2f} por mês na conta de luz, estarei aqui. Nossa solução realmente pode fazer a diferença."
                
            elif template_type.upper() == "MEETING_CONFIRMATION":
                # Confirmação de reunião - buscar dados da reunião
                meetings = supabase_client.client.table("calendar_events")\
                    .select("*")\
                    .eq("lead_id", lead_id)\
                    .eq("status", "scheduled")\
                    .order("start_time")\
                    .limit(1)\
                    .execute()
                
                if meetings.data:
                    meeting = meetings.data[0]
                    start_time = datetime.fromisoformat(meeting["start_time"])
                    day = start_time.strftime("%d/%m")
                    time = start_time.strftime("%H:%M")
                    message = f"Oi {lead_name}! 📅 Passando para confirmar nossa reunião {day} às {time}. Você confirma presença?"
                else:
                    message = f"Oi {lead_name}! Passando para confirmar nossa reunião. Você confirma presença?"
                    
            elif template_type.upper() == "MEETING_REMINDER":
                # Lembrete de reunião
                meetings = supabase_client.client.table("calendar_events")\
                    .select("*")\
                    .eq("lead_id", lead_id)\
                    .eq("status", "scheduled")\
                    .order("start_time")\
                    .limit(1)\
                    .execute()
                
                if meetings.data:
                    meeting = meetings.data[0]
                    start_time = datetime.fromisoformat(meeting["start_time"])
                    time = start_time.strftime("%H:%M")
                    message = f"{lead_name}, nossa reunião está chegando! Te vejo às {time}. Preparei uma apresentação especial sobre como economizar na sua conta de luz."
                else:
                    message = f"{lead_name}, nossa reunião está chegando! Preparei uma apresentação especial sobre como economizar na sua conta de luz."
                    
            elif template_type.upper() == "VALUE_CONTENT":
                # Conteúdo de valor
                yearly_savings = bill_value * 0.2 * 12
                message = f"{lead_name}, acabei de calcular: você pode economizar R${yearly_savings:.2f} por ano com nossa solução! Vamos conversar sobre isso?"
                
            else:
                # Mensagem genérica de follow-up
                message = f"Olá {lead_name}! Temos novidades sobre economia de energia solar para você. Posso te mostrar como economizar até 20% na conta de luz?"
            
            return message
            
        except Exception as e:
            logger.error(f"Erro ao personalizar mensagem: {e}")
            return "Olá! Temos novidades sobre economia de energia solar para você!"
    
    # Métodos auxiliares privados
    
    def _load_prompt_master(self) -> str:
        """Carrega o prompt master do arquivo"""
        try:
            import os
            prompt_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'prompts',
                'prompt-agente.md'
            )
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Erro ao carregar prompt master: {e}")
            return ""
    
    def _adjust_to_business_hours(self, dt: datetime) -> datetime:
        """Ajusta datetime para horário comercial"""
        hour = dt.hour
        
        # Se antes do horário comercial
        if hour < self.followup_config["business_hours"]["start"]:
            dt = dt.replace(hour=self.followup_config["business_hours"]["start"], minute=0)
        
        # Se depois do horário comercial
        elif hour >= self.followup_config["business_hours"]["end"]:
            # Próximo dia útil às 9h
            dt = dt + timedelta(days=1)
            dt = dt.replace(hour=self.followup_config["business_hours"]["start"], minute=0)
        
        # Ajustar para dia útil
        while dt.weekday() >= 5:  # Sábado ou Domingo
            dt += timedelta(days=1)
        
        return dt
    
    async def _generate_followup_message(
        self,
        lead: Dict[str, Any],
        followup_type: str
    ) -> str:
        """Gera mensagem de follow-up personalizada"""
        return await self.personalize_message(
            lead["id"],
            followup_type,
            include_data=True
        )
    
    def _get_strategy_for_classification(self, classification: str) -> str:
        """Retorna estratégia baseada na classificação"""
        strategies = {
            "hot": FollowUpStrategy.AGGRESSIVE.value,
            "warm": FollowUpStrategy.MODERATE.value,
            "cold": FollowUpStrategy.GENTLE.value,
            "unqualified": FollowUpStrategy.EDUCATIONAL.value
        }
        return strategies.get(classification, FollowUpStrategy.GENTLE.value)
    
    def _get_optimal_hour(self, message_number: int) -> int:
        """Retorna hora otimizada para envio"""
        hours = [10, 14, 16]  # Manhã, tarde, fim de tarde
        return hours[message_number % len(hours)]
    
    def _hours_until(self, scheduled_time_str: str) -> float:
        """Calcula horas até o horário agendado"""
        scheduled = datetime.fromisoformat(scheduled_time_str)
        delta = scheduled - datetime.now()
        return delta.total_seconds() / 3600
    
    def _get_period_name(self, hour: int) -> str:
        """Retorna nome do período do dia"""
        if hour < 12:
            return "morning"
        elif hour < 14:
            return "lunch"
        elif hour < 18:
            return "afternoon"
        else:
            return "evening"
    
    @tool
    async def analyze_engagement(
        self,
        lead_id: int
    ) -> Dict[str, Any]:
        """
        Analisa engajamento do lead
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Análise de engajamento
        """
        try:
            # Buscar histórico de follow-ups
            followups = supabase_client.client.table("follow_ups")\
                .select("*")\
                .eq("lead_id", lead_id)\
                .order("created_at", desc=True)\
                .execute()
            
            # Buscar conversas
            conversations = supabase_client.client.table("conversations")\
                .select("*")\
                .eq("lead_id", lead_id)\
                .order("timestamp", desc=True)\
                .execute()
            
            # Calcular métricas
            total_followups = len(followups.data)
            completed_followups = len([f for f in followups.data if f["status"] == "completed"])
            total_messages = len(conversations.data)
            response_rate = (total_messages / max(total_followups, 1)) * 100 if total_followups > 0 else 0
            
            # Determinar nível de engajamento
            if response_rate > 75:
                engagement_level = "HIGH"
            elif response_rate > 40:
                engagement_level = "MEDIUM"
            else:
                engagement_level = "LOW"
            
            return {
                "success": True,
                "lead_id": lead_id,
                "engagement_level": engagement_level,
                "metrics": {
                    "total_followups": total_followups,
                    "completed_followups": completed_followups,
                    "response_rate": response_rate,
                    "total_messages": total_messages
                },
                "recommendation": self._get_engagement_recommendation(engagement_level)
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar engajamento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def get_followup_strategy(
        self,
        lead_id: int
    ) -> Dict[str, Any]:
        """
        Obtém estratégia de follow-up recomendada
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Estratégia recomendada
        """
        try:
            # Buscar lead
            lead = supabase_client.client.table("leads")\
                .select("*")\
                .eq("id", lead_id)\
                .single()\
                .execute()
            
            if not lead.data:
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }
            
            # Analisar engajamento
            engagement = await self.analyze_engagement(lead_id)
            
            # Determinar estratégia baseada no perfil
            classification = lead.data.get("qualification_status", "pending")
            engagement_level = engagement.get("engagement_level", "LOW")
            
            if classification == "hot" or engagement_level == "HIGH":
                strategy = FollowUpStrategy.AGGRESSIVE.value
                interval_hours = 2
                max_attempts = 7
            elif classification == "warm" or engagement_level == "MEDIUM":
                strategy = FollowUpStrategy.MODERATE.value
                interval_hours = 24
                max_attempts = 5
            else:
                strategy = FollowUpStrategy.GENTLE.value
                interval_hours = 48
                max_attempts = 3
            
            return {
                "success": True,
                "lead_id": lead_id,
                "strategy": strategy,
                "interval_hours": interval_hours,
                "max_attempts": max_attempts,
                "classification": classification,
                "engagement_level": engagement_level,
                "next_actions": self._get_strategy_actions(strategy)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estratégia: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def list_pending_followups(
        self,
        lead_id: Optional[int] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Lista follow-ups pendentes
        
        Args:
            lead_id: ID do lead (opcional)
            limit: Limite de resultados
            
        Returns:
            Lista de follow-ups pendentes
        """
        try:
            query = supabase_client.client.table("follow_ups")\
                .select("*, leads(*)")\
                .eq("status", "pending")\
                .order("scheduled_at")\
                .limit(limit)
            
            if lead_id:
                query = query.eq("lead_id", lead_id)
            
            followups = query.execute()
            
            formatted = []
            for f in followups.data:
                scheduled = datetime.fromisoformat(f["scheduled_at"])
                formatted.append({
                    "id": f["id"],
                    "lead_name": f["leads"]["name"] if f.get("leads") else "N/A",
                    "type": f["follow_up_type"],
                    "scheduled": scheduled.strftime("%d/%m/%Y %H:%M"),
                    "priority": f.get("priority", "normal"),
                    "message": f.get("message", "")[:100]
                })
            
            return {
                "success": True,
                "count": len(formatted),
                "followups": formatted
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar follow-ups: {e}")
            return {
                "success": False,
                "error": str(e),
                "followups": []
            }
    
    @tool
    async def execute_immediate_followup(
        self,
        lead_id: int,
        message: str
    ) -> Dict[str, Any]:
        """
        Executa follow-up imediato
        
        Args:
            lead_id: ID do lead
            message: Mensagem a enviar
            
        Returns:
            Status da execução
        """
        try:
            # Buscar lead
            lead = supabase_client.client.table("leads")\
                .select("*")\
                .eq("id", lead_id)\
                .single()\
                .execute()
            
            if not lead.data:
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }
            
            # Enviar mensagem via Evolution API
            from app.integrations.evolution import evolution_client
            
            result = await evolution_client.send_text_message(
                to=lead.data["phone_number"],
                message=message
            )
            
            # Registrar follow-up
            supabase_client.client.table("follow_ups").insert({
                "lead_id": lead_id,
                "type": "custom",
                "follow_up_type": "IMMEDIATE_REENGAGEMENT",
                "message": message,
                "scheduled_at": datetime.now().isoformat(),
                "executed_at": datetime.now().isoformat(),
                "status": "completed" if result else "failed",
                "priority": "high"
            }).execute()
            
            return {
                "success": result,
                "lead_id": lead_id,
                "message_sent": message,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar follow-up imediato: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def update_followup_status(
        self,
        followup_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Atualiza status de follow-up
        
        Args:
            followup_id: ID do follow-up
            status: Novo status (pending, executing, completed, failed, cancelled)
            notes: Notas adicionais (opcional)
            
        Returns:
            Status da atualização
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if status == "completed":
                update_data["executed_at"] = datetime.now().isoformat()
            
            if notes:
                update_data["notes"] = notes
            
            result = supabase_client.client.table("follow_ups")\
                .update(update_data)\
                .eq("id", followup_id)\
                .execute()
            
            if result.data:
                return {
                    "success": True,
                    "followup_id": followup_id,
                    "new_status": status,
                    "updated_at": update_data["updated_at"]
                }
            else:
                return {
                    "success": False,
                    "error": "Follow-up não encontrado"
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_engagement_recommendation(self, level: str) -> str:
        """Retorna recomendação baseada no nível de engajamento"""
        recommendations = {
            "HIGH": "Continue com abordagem atual. Lead altamente engajado.",
            "MEDIUM": "Aumente frequência de contato. Oportunidade de conversão.",
            "LOW": "Mude estratégia. Considere conteúdo educacional."
        }
        return recommendations.get(level, "Analisar caso individualmente")
    
    def _get_strategy_actions(self, strategy: str) -> List[str]:
        """Retorna ações recomendadas para estratégia"""
        actions = {
            "aggressive": [
                "Follow-up em 2 horas",
                "Ligação telefônica em 24h",
                "Oferta especial em 48h"
            ],
            "moderate": [
                "Follow-up diário",
                "Conteúdo educacional",
                "Agendamento de reunião"
            ],
            "gentle": [
                "Follow-up a cada 2 dias",
                "Conteúdo informativo",
                "Manter relacionamento"
            ]
        }
        return actions.get(strategy, ["Avaliar individualmente"])