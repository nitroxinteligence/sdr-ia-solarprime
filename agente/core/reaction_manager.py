"""
Reaction Manager - Gerencia reações automáticas e espontâneas
Integrado com o sistema de processamento de mensagens
"""

import asyncio
import random
from typing import Optional, Dict, Any, List
from datetime import datetime

from agente.core.logger import logger, setup_module_logger
from agente.tools.whatsapp.send_reaction import send_reaction
from agente.core.types import WhatsAppMessage

# Logger específico para o módulo
module_logger = setup_module_logger("reaction_manager")


class ReactionManager:
    """
    Gerenciador de reações automáticas e espontâneas
    
    Funcionalidades:
    - Reações automáticas a mídia (✅ 👍🏻)
    - Reações espontâneas baseadas em probabilidade (❤️)
    - Contexto inteligente baseado na conversa
    - Integração com Evolution API via send_reaction tool
    """
    
    def __init__(self):
        """Inicializa o gerenciador de reações"""
        # send_reaction é uma função, não precisa de instanciação
        
        # Configurações de probabilidade
        self.spontaneous_probability = 0.15  # 15% chance de reação espontânea
        self.media_reaction_probability = 0.80  # 80% chance de reagir a mídia
        
        # Patterns que aumentam probabilidade de reação espontânea
        self.high_engagement_patterns = [
            # Mensagens positivas
            "obrigad", "grato", "muito bom", "excelente", "perfeito",
            "adorei", "amei", "fantástico", "incrível", "maravilhoso",
            
            # Confirmações e interesse
            "sim", "claro", "certeza", "com certeza", "vamos em frente",
            "quero sim", "tenho interesse", "me interessei",
            
            # Energia solar específico
            "economia", "conta de luz", "energia solar", "painéis",
            "sustentável", "meio ambiente", "financiamento",
            
            # Urgência e disposição
            "urgente", "rápido", "quanto antes", "hoje mesmo",
            "estou disponível", "pode ligar"
        ]
        
        # Patterns que diminuem probabilidade de reação
        self.low_engagement_patterns = [
            "não", "não tenho", "não posso", "não quero",
            "depois", "mais tarde", "ocupado", "sem tempo",
            "não interessado", "desculpa", "perdão"
        ]
        
        module_logger.info("ReactionManager initialized")
    
    def analyze_message_context(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """
        Analisa o contexto da mensagem para determinar tipo de reação
        
        Args:
            message: Mensagem do WhatsApp
            
        Returns:
            Contexto analisado com recomendações
        """
        message_text = message.message.lower()
        
        # Análise de engajamento
        high_engagement_score = sum(
            1 for pattern in self.high_engagement_patterns
            if pattern in message_text
        )
        
        low_engagement_score = sum(
            1 for pattern in self.low_engagement_patterns
            if pattern in message_text
        )
        
        # Calcular score final
        engagement_score = high_engagement_score - low_engagement_score
        
        # Determinar probabilidade ajustada
        base_probability = self.spontaneous_probability
        if engagement_score > 0:
            # Aumenta probabilidade para mensagens positivas
            adjusted_probability = min(base_probability * (1 + engagement_score * 0.5), 0.4)
        elif engagement_score < 0:
            # Diminui probabilidade para mensagens negativas
            adjusted_probability = max(base_probability * (1 + engagement_score * 0.3), 0.05)
        else:
            adjusted_probability = base_probability
        
        # Análise de contexto semântico
        context_type = "general"
        if any(word in message_text for word in ["energia", "solar", "painel", "economia"]):
            context_type = "energy_related"
        elif any(word in message_text for word in ["obrigad", "grato", "valeu"]):
            context_type = "appreciation"
        elif any(word in message_text for word in ["sim", "perfeito", "ótimo", "excelente"]):
            context_type = "confirmation"
        
        return {
            "engagement_score": engagement_score,
            "adjusted_probability": adjusted_probability,
            "context_type": context_type,
            "high_engagement_count": high_engagement_score,
            "low_engagement_count": low_engagement_score,
            "should_prioritize_reaction": engagement_score > 1
        }
    
    async def process_spontaneous_reaction(
        self, 
        message: WhatsAppMessage,
        context_analysis: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Processa reação espontânea baseada em probabilidade e contexto
        
        Args:
            message: Mensagem recebida
            context_analysis: Análise de contexto (opcional)
            
        Returns:
            Resultado da reação enviada ou None se não reagiu
        """
        try:
            # Analisar contexto se não foi fornecido
            if not context_analysis:
                context_analysis = self.analyze_message_context(message)
            
            adjusted_probability = context_analysis["adjusted_probability"]
            
            # Verificar se deve reagir
            if random.random() > adjusted_probability:
                module_logger.debug(
                    "Skipping spontaneous reaction based on probability",
                    phone=message.phone[:4] + "****",
                    probability=adjusted_probability,
                    engagement_score=context_analysis["engagement_score"]
                )
                return None
            
            module_logger.info(
                "Sending spontaneous reaction",
                phone=message.phone[:4] + "****",
                probability=adjusted_probability,
                engagement_score=context_analysis["engagement_score"],
                context_type=context_analysis["context_type"]
            )
            
            # Enviar reação espontânea
            result = await send_reaction(
                phone=message.phone,
                message_key=message.message_id,
                context=message.message,
                force_send=True  # Já passou pela verificação de probabilidade
            )
            
            return result
            
        except Exception as e:
            module_logger.error(
                f"Error processing spontaneous reaction: {str(e)}",
                phone=message.phone[:4] + "****"
            )
            return None
    
    async def process_media_reaction(
        self, 
        message: WhatsAppMessage
    ) -> Optional[Dict[str, Any]]:
        """
        Processa reação automática a mídia recebida
        
        Args:
            message: Mensagem com mídia
            
        Returns:
            Resultado da reação enviada ou None se não reagiu
        """
        try:
            if not message.media_type:
                return None
            
            module_logger.info(
                "Processing media reaction",
                phone=message.phone[:4] + "****",
                media_type=message.media_type,
                has_caption=bool(message.message)
            )
            
            # Determinar contexto baseado no tipo de mídia e caption
            context = message.message if message.message else f"media_{message.media_type}"
            
            # Enviar reação à mídia
            result = await send_reaction(
                phone=message.phone,
                message_key=message.message_id,
                context=context,
                media_type=message.media_type,
                force_send=False  # Usar probabilidade configurada
            )
            
            return result
            
        except Exception as e:
            module_logger.error(
                f"Error processing media reaction: {str(e)}",
                phone=message.phone[:4] + "****",
                media_type=message.media_type
            )
            return None
    
    async def process_message_reactions(
        self, 
        message: WhatsAppMessage
    ) -> Dict[str, Any]:
        """
        Processa todas as reações possíveis para uma mensagem
        
        Args:
            message: Mensagem do WhatsApp
            
        Returns:
            Resultado consolidado de todas as reações
        """
        results = {
            "spontaneous_reaction": None,
            "media_reaction": None,
            "total_reactions_sent": 0
        }
        
        try:
            # Analisar contexto uma vez
            context_analysis = self.analyze_message_context(message)
            
            # Lista de tarefas assíncronas
            tasks = []
            
            # Reação a mídia (se aplicável)
            if message.media_type:
                tasks.append(self.process_media_reaction(message))
            
            # Reação espontânea (sempre verificar)
            tasks.append(self.process_spontaneous_reaction(message, context_analysis))
            
            # Executar reações em paralelo
            if tasks:
                task_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Processar resultados
                if message.media_type and len(task_results) >= 1:
                    media_result = task_results[0]
                    if isinstance(media_result, dict) and media_result.get("success"):
                        results["media_reaction"] = media_result
                        if not media_result.get("skipped"):
                            results["total_reactions_sent"] += 1
                
                # Resultado da reação espontânea
                spontaneous_idx = 1 if message.media_type else 0
                if len(task_results) > spontaneous_idx:
                    spontaneous_result = task_results[spontaneous_idx]
                    if isinstance(spontaneous_result, dict) and spontaneous_result.get("success"):
                        results["spontaneous_reaction"] = spontaneous_result
                        if not spontaneous_result.get("skipped"):
                            results["total_reactions_sent"] += 1
            
            # Log resultado consolidado
            if results["total_reactions_sent"] > 0:
                module_logger.info(
                    "Reactions processed successfully",
                    phone=message.phone[:4] + "****",
                    total_sent=results["total_reactions_sent"],
                    has_media_reaction=bool(results["media_reaction"]),
                    has_spontaneous_reaction=bool(results["spontaneous_reaction"])
                )
            
            return results
            
        except Exception as e:
            module_logger.error(
                f"Error processing message reactions: {str(e)}",
                phone=message.phone[:4] + "****"
            )
            return results


# Singleton instance
_reaction_manager: Optional[ReactionManager] = None


def get_reaction_manager() -> ReactionManager:
    """
    Retorna instância singleton do Reaction Manager
    
    Returns:
        Instância do gerenciador
    """
    global _reaction_manager
    if _reaction_manager is None:
        _reaction_manager = ReactionManager()
    return _reaction_manager