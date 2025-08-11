"""
Typing Controller - Módulo de controle centralizado de typing
Arquitetura modular com ZERO complexidade
"""

from enum import Enum
from typing import Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class TypingContext(Enum):
    """Contextos onde typing pode ou não aparecer"""
    USER_MESSAGE = "user_message"        # Usuário enviou mensagem - NUNCA mostrar typing
    AGENT_RESPONSE = "agent_response"    # Agente respondendo - SEMPRE mostrar typing
    SYSTEM_MESSAGE = "system_message"    # Sistema enviando - NUNCA mostrar typing
    MEDIA_UPLOAD = "media_upload"        # Upload de mídia - NUNCA mostrar typing


@dataclass
class TypingDecision:
    """Resultado da decisão sobre typing"""
    should_show: bool
    duration: Optional[float] = None
    reason: str = ""


class TypingController:
    """
    Controlador centralizado de typing
    ÚNICA fonte de verdade sobre quando mostrar "digitando..."
    """
    
    def __init__(self, enable_typing: bool = True):
        """
        Args:
            enable_typing: Se False, NUNCA mostra typing em nenhum contexto
        """
        self.enable_typing = enable_typing
        logger.info(f"TypingController inicializado: enable_typing={enable_typing}")
    
    def should_show_typing(self, context: TypingContext, message_length: int = 0) -> TypingDecision:
        """
        Decisão centralizada sobre mostrar typing
        
        Args:
            context: Contexto da operação
            message_length: Tamanho da mensagem (para calcular duração)
            
        Returns:
            TypingDecision com a decisão e motivo
        """
        # Se typing está globalmente desabilitado, NUNCA mostrar
        if not self.enable_typing:
            return TypingDecision(
                should_show=False,
                reason="Typing globalmente desabilitado"
            )
        
        # Decisão baseada APENAS no contexto
        if context == TypingContext.AGENT_RESPONSE:
            # ÚNICO caso onde mostramos typing
            duration = self._calculate_duration(message_length)
            return TypingDecision(
                should_show=True,
                duration=duration,
                reason=f"Agente respondendo - mostrar typing por {duration:.1f}s"
            )
        
        # TODOS os outros casos: NÃO mostrar
        reasons = {
            TypingContext.USER_MESSAGE: "Usuário enviou mensagem - não mostrar typing",
            TypingContext.SYSTEM_MESSAGE: "Mensagem do sistema - não mostrar typing",
            TypingContext.MEDIA_UPLOAD: "Upload de mídia - não mostrar typing"
        }
        
        return TypingDecision(
            should_show=False,
            reason=reasons.get(context, "Contexto não requer typing")
        )
    
    def _calculate_duration(self, message_length: int) -> float:
        """
        Calcula duração do typing baseado no tamanho da mensagem
        Simula velocidade humana realástica
        
        Args:
            message_length: Número de caracteres
            
        Returns:
            Duração em segundos
        """
        if message_length == 0:
            return 2.0  # Padrão para mensagens vazias
        
        # Cálculo mais realista baseado no tamanho
        if message_length < 50:
            # Mensagens curtas: 1-2 segundos
            return 1.5
        elif message_length < 150:
            # Mensagens médias: 2-4 segundos
            return 3.0
        elif message_length < 300:
            # Mensagens longas: 4-6 segundos
            return 5.0
        elif message_length < 500:
            # Mensagens muito longas: 6-8 segundos
            return 7.0
        else:
            # Mensagens enormes: 8-10 segundos
            return 9.0


# Singleton global com configuração do sistema
from app.config import settings
typing_controller = TypingController(enable_typing=settings.enable_typing_simulation)


# Funções de conveniência para uso direto
def should_show_typing_for_user_message() -> bool:
    """Quando usuário envia mensagem - SEMPRE retorna False"""
    decision = typing_controller.should_show_typing(TypingContext.USER_MESSAGE)
    logger.debug(f"Typing para mensagem do usuário: {decision.reason}")
    return decision.should_show


def should_show_typing_for_agent_response(message_length: int) -> TypingDecision:
    """Quando agente responde - retorna True com duração calculada"""
    decision = typing_controller.should_show_typing(
        TypingContext.AGENT_RESPONSE,
        message_length
    )
    logger.debug(f"Typing para resposta do agente: {decision.reason}")
    return decision