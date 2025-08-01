"""
TypeSimulationTool - Simula digitação humana no WhatsApp
"""

import asyncio
import random
from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from ...services import get_evolution_service
from ...core.config import AI_TYPING_DELAY_MAX


# CRÍTICO: AGnO Framework bug com @tool decorator em async functions
# Removendo @tool decorator conforme documentação oficial AGnO
# Issue #2296: https://github.com/agno-agi/agno/issues/2296
async def simulate_typing(
    text: str,
    phone: Optional[str] = None,
    send_after: bool = True,
    custom_delay: Optional[float] = None
) -> Dict[str, Any]:
    """
    Simula digitação humana no WhatsApp antes de enviar mensagem.
    
    Esta ferramenta calcula um delay proporcional ao tamanho do texto,
    simulando o tempo que uma pessoa levaria para digitar, criando
    uma experiência mais natural na conversa.
    
    Args:
        text: Texto base para calcular tempo de digitação
        phone: Número de telefone do destinatário (opcional, obtido do contexto se não fornecido)
        send_after: Se deve enviar a mensagem após simular digitação (padrão: True)
        custom_delay: Tempo customizado em segundos (opcional, calculado se não fornecido)
    
    Returns:
        Dict com resultado da simulação:
        - success: bool - Se a simulação foi executada com sucesso
        - typing_duration: float - Duração da simulação em segundos
        - words_count: int - Número de palavras no texto
        - chars_count: int - Número de caracteres no texto
        - message_sent: bool - Se a mensagem foi enviada após simulação
        - message_id: str - ID da mensagem enviada (se send_after=True)
        - error: str - Mensagem de erro (se falhou)
    
    Examples:
        >>> await simulate_typing("5511999999999", "Olá! Como posso ajudar você hoje?")
        {"success": True, "typing_duration": 3.2, "words_count": 6, "chars_count": 34, "message_sent": True, "message_id": "3EB0C767D097E9ECFE94"}
        
        >>> await simulate_typing("5511999999999", "Mensagem longa...", send_after=False)
        {"success": True, "typing_duration": 5.7, "words_count": 2, "chars_count": 16, "message_sent": False}
    """
    try:
        # Obter phone do contexto se não fornecido
        if phone is None:
            from ...core.tool_context import get_current_phone
            phone = get_current_phone()
            
            if phone is None:
                logger.error("Phone não fornecido e não encontrado no contexto")
                return {
                    "success": False,
                    "error": "Número de telefone não disponível - forneça phone ou configure contexto",
                    "typing_duration": 0,
                    "words_count": len(text.split()),
                    "chars_count": len(text),
                    "message_sent": False,
                    "message_id": None
                }
        
        # Análise do texto
        words_count = len(text.split())
        chars_count = len(text)
        
        logger.info(
            "Iniciando simulação de digitação",
            phone=phone[:4] + "****",
            words_count=words_count,
            chars_count=chars_count,
            send_after=send_after
        )
        
        # Calcula tempo de digitação
        if custom_delay is not None:
            typing_duration = custom_delay
        else:
            # Obtém serviço para usar o cálculo padrão
            evolution = get_evolution_service()
            typing_duration = evolution._calculate_typing_delay(text)
        
        # Garante limites razoáveis
        typing_duration = max(1.0, min(typing_duration, AI_TYPING_DELAY_MAX))
        
        logger.debug(
            "Tempo de digitação calculado",
            duration=typing_duration,
            words_per_second=words_count / typing_duration if typing_duration > 0 else 0
        )
        
        # Simula digitação com pequenas variações
        start_time = asyncio.get_event_loop().time()
        
        # Divide em pequenos intervalos para parecer mais natural
        intervals = int(typing_duration * 4)  # 4 checagens por segundo
        interval_duration = typing_duration / intervals
        
        for i in range(intervals):
            # Adiciona pequena variação aleatória
            variation = interval_duration * 0.1
            actual_interval = interval_duration + random.uniform(-variation, variation)
            await asyncio.sleep(actual_interval)
            
            # Log de progresso a cada 25%
            progress = (i + 1) / intervals * 100
            if progress in [25, 50, 75]:
                logger.debug(f"Simulação de digitação: {progress:.0f}% completa")
        
        # Tempo real decorrido
        actual_duration = asyncio.get_event_loop().time() - start_time
        
        logger.info(
            "Simulação de digitação concluída",
            planned_duration=typing_duration,
            actual_duration=actual_duration,
            difference=abs(actual_duration - typing_duration)
        )
        
        # Resultado base
        result = {
            "success": True,
            "typing_duration": round(actual_duration, 2),
            "words_count": words_count,
            "chars_count": chars_count,
            "message_sent": False
        }
        
        # Envia mensagem se solicitado
        if send_after:
            logger.info("Enviando mensagem após simulação de digitação")
            
            evolution = get_evolution_service()
            send_result = await evolution.send_text_message(
                phone=phone,
                text=text,
                delay=0  # Sem delay adicional, já simulamos
            )
            
            if send_result:
                result["message_sent"] = True
                result["message_id"] = send_result.get("key", {}).get("id", "")
                
                logger.success(
                    "Mensagem enviada após simulação",
                    message_id=result["message_id"]
                )
            else:
                result["message_sent"] = False
                result["error"] = "Simulação OK, mas falha ao enviar mensagem"
                
                logger.warning(
                    "Simulação concluída, mas falha ao enviar mensagem",
                    phone=phone
                )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Erro na simulação de digitação: {str(e)}",
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro na simulação: {str(e)}",
            "typing_duration": 0,
            "words_count": len(text.split()) if text else 0,
            "chars_count": len(text) if text else 0,
            "message_sent": False
        }


# Export da tool
TypeSimulationTool = simulate_typing
type_simulation = simulate_typing  # Alias para compatibilidade