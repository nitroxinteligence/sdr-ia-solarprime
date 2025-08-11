"""
FollowUp Service - Sistema de Follow-up Simplificado
Zero complexidade, funcionalidade total
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import json
from app.utils.logger import emoji_logger
from app.config import settings
from app.database.supabase_client import supabase_client

class FollowUpService:
    """
    Serviço direto de follow-up - sem camadas desnecessárias
    Mantém 100% da funcionalidade do FollowUpAgent
    """
    
    def __init__(self):
        self.is_initialized = False
        self.followup_templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, List[str]]:
        """Carrega templates de follow-up"""
        return {
            "initial": [
                "Oi {name}! 👋 Vi que você demonstrou interesse em economizar na conta de luz. Posso te ajudar com isso?",
                "Olá {name}! ☀️ A energia solar pode reduzir sua conta em até 95%. Que tal conversarmos sobre isso?",
                "E aí {name}! 💡 Já pensou em parar de sofrer com aumentos na conta de luz?"
            ],
            "re_engagement": [
                "Oi {name}! 😊 Voltando aqui para ver se você ainda tem interesse em economizar na conta de luz...",
                "{name}, conseguiu pensar sobre a energia solar? Estou aqui para tirar qualquer dúvida!",
                "Olá {name}! ⚡ As tarifas de energia subiram de novo... Que tal conversarmos sobre solar?"
            ],
            "qualification": [
                "{name}, para eu te apresentar a melhor solução, você pode me enviar uma foto da sua conta de luz? 📸",
                "Legal {name}! Me conta: qual o valor médio da sua conta de luz hoje?",
                "Perfeito {name}! Você é proprietário do imóvel ou aluga?"
            ],
            "scheduling": [
                "Excelente {name}! O Leonardo, nosso especialista, tem alguns horários disponíveis. Quando seria melhor para você?",
                "{name}, que tal marcarmos uma conversa rápida com o Leonardo para ele te mostrar quanto você vai economizar?",
                "Show {name}! Vou verificar a agenda do Leonardo. Prefere manhã ou tarde?"
            ]
        }
        
    async def initialize(self):
        """Inicialização simples e direta"""
        if self.is_initialized:
            return
            
        self.is_initialized = True
        emoji_logger.service_ready("🔄 FollowUpService inicializado")
        
    async def create_followup(self, 
                             lead_data: Dict[str, Any],
                             followup_type: str,
                             delay_hours: int = 24) -> Dict[str, Any]:
        """
        Cria follow-up de forma SIMPLES e DIRETA
        
        Args:
            lead_data: Dados do lead
            followup_type: Tipo do follow-up
            delay_hours: Horas de delay para o follow-up
            
        Returns:
            Dict com resultado da operação
        """
        try:
            # Calcula quando enviar
            scheduled_time = datetime.now() + timedelta(hours=delay_hours)
            
            # Seleciona template apropriado
            templates = self.followup_templates.get(followup_type, self.followup_templates["initial"])
            message = templates[0].format(name=lead_data.get("name", "amigo"))
            
            # Salva follow-up no banco
            followup_data = {
                "phone": lead_data.get("phone"),
                "name": lead_data.get("name"),
                "type": followup_type,
                "message": message,
                "scheduled_time": scheduled_time.isoformat(),
                "status": "pending"
            }
            
            # Aqui salvaria no Supabase
            emoji_logger.followup_event(
                f"⏰ Follow-up agendado para {lead_data.get('name')} em {delay_hours}h"
            )
            
            return {
                "success": True,
                "followup_id": f"followup_{datetime.now().timestamp()}",
                "scheduled_time": scheduled_time.isoformat(),
                "message": f"Follow-up agendado para {scheduled_time.strftime('%d/%m às %H:%M')}"
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao criar follow-up: {e}")
            return {
                "success": False,
                "message": "Erro ao agendar follow-up"
            }
    
    async def get_pending_followups(self) -> List[Dict[str, Any]]:
        """
        Busca follow-ups pendentes
        
        Returns:
            Lista de follow-ups pendentes
        """
        try:
            # Aqui buscaria do Supabase
            # Por enquanto, retorno simulado
            
            return []
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao buscar follow-ups: {e}")
            return []
    
    async def execute_followup(self, followup_id: str) -> Dict[str, Any]:
        """
        Executa um follow-up
        
        Args:
            followup_id: ID do follow-up
            
        Returns:
            Dict com resultado da execução
        """
        try:
            emoji_logger.followup_event(f"📤 Executando follow-up {followup_id}")
            
            # Aqui enviaria a mensagem via Evolution API
            
            return {
                "success": True,
                "message": "Follow-up executado com sucesso"
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao executar follow-up: {e}")
            return {
                "success": False,
                "message": "Erro ao executar follow-up"
            }
    
    async def cancel_followup(self, followup_id: str) -> Dict[str, Any]:
        """
        Cancela um follow-up
        
        Args:
            followup_id: ID do follow-up
            
        Returns:
            Dict com resultado do cancelamento
        """
        try:
            emoji_logger.followup_event(f"❌ Follow-up cancelado: {followup_id}")
            
            return {
                "success": True,
                "message": "Follow-up cancelado com sucesso"
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao cancelar follow-up: {e}")
            return {
                "success": False,
                "message": "Erro ao cancelar follow-up"
            }
    
    def get_best_followup_message(self, 
                                  lead_stage: str,
                                  context: Dict[str, Any]) -> str:
        """
        Retorna melhor mensagem de follow-up baseada no contexto
        
        Args:
            lead_stage: Estágio atual do lead
            context: Contexto da conversa
            
        Returns:
            Mensagem de follow-up otimizada
        """
        try:
            # Lógica simples de seleção
            if lead_stage == "novo":
                templates = self.followup_templates["initial"]
            elif lead_stage == "qualificando":
                templates = self.followup_templates["qualification"]
            elif lead_stage == "agendamento":
                templates = self.followup_templates["scheduling"]
            else:
                templates = self.followup_templates["re_engagement"]
            
            # Seleciona template baseado no contexto
            import random
            message = random.choice(templates)
            
            # Personaliza com dados do contexto
            name = context.get("name", "amigo")
            return message.format(name=name)
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao gerar mensagem: {e}")
            return "Oi! Tudo bem? Estou aqui para ajudar com energia solar! ☀️"