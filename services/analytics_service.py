"""
Analytics Service
=================
Serviço para coletar e analisar métricas do sistema
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from loguru import logger
from collections import defaultdict

from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from services.database import db


class AnalyticsService:
    """Serviço de analytics e métricas"""
    
    async def track_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        lead_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ):
        """Registra evento de analytics"""
        try:
            await db.analytics.insert({
                "lead_id": str(lead_id) if lead_id else None,
                "event_type": event_type,
                "event_data": event_data,
                "session_id": session_id
            }).execute()
            
            logger.debug(f"Analytics event tracked: {event_type}")
            
        except Exception as e:
            logger.error(f"Error tracking analytics event: {e}")
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Obtém métricas para dashboard"""
        try:
            # Métricas gerais
            total_leads = await lead_repository.count()
            active_conversations = await conversation_repository.count({"is_active": True})
            total_messages = await message_repository.count()
            
            # Leads por estágio
            stage_distribution = {}
            stages = ["INITIAL_CONTACT", "DISCOVERY", "QUALIFICATION", "OBJECTION_HANDLING", "SCHEDULING"]
            
            for stage in stages:
                count = await lead_repository.count({"current_stage": stage})
                stage_distribution[stage] = count
            
            # Taxa de conversão
            qualified_count = await lead_repository.count({"current_stage": "QUALIFICATION"})
            scheduled_count = await lead_repository.count({"current_stage": "SCHEDULING"})
            
            conversion_rate = 0
            if total_leads > 0:
                conversion_rate = (scheduled_count / total_leads) * 100
            
            # Leads interessados vs não interessados
            interested_count = await lead_repository.count({"interested": True})
            not_interested_count = await lead_repository.count({"interested": False})
            
            return {
                "overview": {
                    "total_leads": total_leads,
                    "active_conversations": active_conversations,
                    "total_messages": total_messages,
                    "conversion_rate": round(conversion_rate, 2)
                },
                "stage_distribution": stage_distribution,
                "interest_distribution": {
                    "interested": interested_count,
                    "not_interested": not_interested_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            return {}
    
    async def get_lead_analytics(self, lead_id: UUID) -> Dict[str, Any]:
        """Obtém analytics de um lead específico"""
        try:
            # Buscar lead
            lead = await lead_repository.get_by_id(lead_id)
            if not lead:
                return {"error": "Lead not found"}
            
            # Conversas do lead
            conversations = await conversation_repository.get_lead_conversations(lead_id)
            
            # Calcular métricas
            total_conversations = len(conversations)
            total_messages = 0
            avg_messages_per_conversation = 0
            
            if conversations:
                for conv in conversations:
                    messages = await message_repository.count_conversation_messages(conv.id)
                    total_messages += messages
                
                avg_messages_per_conversation = total_messages / total_conversations
            
            # Tempo médio de resposta
            # TODO: Implementar cálculo real baseado em timestamps
            avg_response_time = "2.5 minutos"
            
            return {
                "lead": {
                    "id": str(lead.id),
                    "phone": lead.phone_number,
                    "name": lead.name,
                    "stage": lead.current_stage,
                    "score": lead.qualification_score
                },
                "metrics": {
                    "total_conversations": total_conversations,
                    "total_messages": total_messages,
                    "avg_messages_per_conversation": round(avg_messages_per_conversation, 1),
                    "avg_response_time": avg_response_time
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting lead analytics: {e}")
            return {"error": str(e)}
    
    async def get_conversion_funnel(self) -> Dict[str, Any]:
        """Obtém dados do funil de conversão"""
        try:
            stages = [
                "INITIAL_CONTACT",
                "IDENTIFICATION", 
                "DISCOVERY",
                "QUALIFICATION",
                "OBJECTION_HANDLING",
                "SCHEDULING"
            ]
            
            funnel_data = []
            previous_count = await lead_repository.count()
            
            for stage in stages:
                count = await lead_repository.count({"current_stage": stage})
                
                # Calcular taxa de conversão para próximo estágio
                conversion_rate = 0
                if previous_count > 0:
                    conversion_rate = (count / previous_count) * 100
                
                funnel_data.append({
                    "stage": stage,
                    "count": count,
                    "conversion_rate": round(conversion_rate, 2)
                })
                
                # Considerar apenas leads que passaram deste estágio
                # Para simplificar, usar o count atual
                if count > 0:
                    previous_count = count
            
            return {
                "funnel": funnel_data,
                "total_leads": await lead_repository.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting conversion funnel: {e}")
            return {"funnel": [], "total_leads": 0}
    
    async def get_time_based_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Obtém métricas baseadas em tempo"""
        try:
            # Data de corte
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Mensagens por dia
            messages_by_day = defaultdict(int)
            recent_messages = await message_repository.get_recent_messages(hours=days * 24)
            
            for msg in recent_messages:
                day = msg.created_at.strftime("%Y-%m-%d")
                messages_by_day[day] += 1
            
            # Leads por dia
            # TODO: Implementar query por data no repositório
            
            return {
                "messages_by_day": dict(messages_by_day),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting time based metrics: {e}")
            return {}
    
    async def generate_weekly_report(self) -> str:
        """Gera relatório semanal"""
        try:
            # Obter métricas
            metrics = await self.get_dashboard_metrics()
            funnel = await self.get_conversion_funnel()
            
            # Formatar relatório
            report = f"""
📊 **RELATÓRIO SEMANAL - SDR IA SolarPrime**
📅 {datetime.now().strftime('%d/%m/%Y')}

**RESUMO GERAL**
• Total de Leads: {metrics['overview']['total_leads']}
• Conversas Ativas: {metrics['overview']['active_conversations']}
• Total de Mensagens: {metrics['overview']['total_messages']}
• Taxa de Conversão: {metrics['overview']['conversion_rate']}%

**DISTRIBUIÇÃO POR ESTÁGIO**
"""
            
            for stage, count in metrics['stage_distribution'].items():
                report += f"• {stage}: {count} leads\n"
            
            report += f"""
**INTERESSE**
• Interessados: {metrics['interest_distribution']['interested']}
• Não Interessados: {metrics['interest_distribution']['not_interested']}

**TOP PERFORMERS**
🏆 Leads com maior engajamento serão listados aqui

_Relatório gerado automaticamente pelo SDR IA SolarPrime_
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return "Erro ao gerar relatório"


# Instância global
analytics_service = AnalyticsService()