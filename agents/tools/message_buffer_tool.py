"""
Message Buffer Tool for AGnO
============================
Tool customizada para processar múltiplas mensagens como contexto único
"""

from typing import List, Dict, Any
from datetime import datetime
from agno.tools import tool
from loguru import logger


@tool
async def process_buffered_messages(
    agent,
    messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Processa múltiplas mensagens consecutivas como um contexto único
    
    Esta tool é usada quando o usuário envia várias mensagens rapidamente
    e queremos entender o contexto completo antes de responder.
    
    Args:
        agent: Instância do agente AGnO
        messages: Lista de mensagens no formato:
            [{
                "content": "texto da mensagem",
                "type": "text|image|audio|document",
                "timestamp": "2024-01-01T10:00:00",
                "media_data": {...} (opcional)
            }]
    
    Returns:
        Dict com o contexto consolidado e análise
    """
    
    if not messages:
        return {
            "error": "Nenhuma mensagem para processar",
            "consolidated_content": "",
            "message_count": 0
        }
    
    try:
        # Estatísticas das mensagens
        message_count = len(messages)
        text_messages = []
        media_messages = []
        
        # Separar mensagens por tipo
        for msg in messages:
            msg_type = msg.get("type", "text")
            
            if msg_type == "text":
                content = msg.get("content", "").strip()
                if content:
                    text_messages.append(content)
            else:
                media_messages.append({
                    "type": msg_type,
                    "content": msg.get("content", ""),
                    "media_data": msg.get("media_data", {})
                })
        
        # Consolidar mensagens de texto
        # Usar ". " para separar frases se não terminarem com pontuação
        consolidated_parts = []
        for text in text_messages:
            if text:
                # Adicionar ponto se não tiver pontuação no final
                if text[-1] not in ".!?":
                    text += "."
                consolidated_parts.append(text)
        
        consolidated_content = " ".join(consolidated_parts)
        
        # Análise temporal
        timestamps = []
        for msg in messages:
            if "timestamp" in msg:
                try:
                    ts = datetime.fromisoformat(msg["timestamp"])
                    timestamps.append(ts)
                except:
                    pass
        
        # Calcular intervalo de tempo
        time_span_seconds = 0
        if len(timestamps) >= 2:
            timestamps.sort()
            time_span_seconds = (timestamps[-1] - timestamps[0]).total_seconds()
        
        # Detectar intenção principal
        # Palavras-chave para diferentes intenções
        keywords_interesse = ["quero", "gostaria", "preciso", "interesse", "saber", "informação"]
        keywords_duvida = ["?", "como", "quanto", "qual", "quando", "onde", "porque"]
        keywords_urgencia = ["urgente", "rápido", "agora", "hoje", "já", "imediato"]
        
        consolidated_lower = consolidated_content.lower()
        
        detected_intents = []
        if any(kw in consolidated_lower for kw in keywords_interesse):
            detected_intents.append("interesse")
        if any(kw in consolidated_lower for kw in keywords_duvida):
            detected_intents.append("dúvida")
        if any(kw in consolidated_lower for kw in keywords_urgencia):
            detected_intents.append("urgência")
        
        # Atualizar contexto do agente
        if hasattr(agent, 'session_state') and agent.session_state:
            agent.session_state['last_buffered_messages'] = {
                'count': message_count,
                'consolidated': consolidated_content,
                'has_media': len(media_messages) > 0,
                'time_span': time_span_seconds,
                'detected_intents': detected_intents
            }
        
        logger.info(f"Processadas {message_count} mensagens - Tempo: {time_span_seconds:.1f}s - Intenções: {detected_intents}")
        
        return {
            "consolidated_content": consolidated_content,
            "message_count": message_count,
            "text_count": len(text_messages),
            "media_count": len(media_messages),
            "media_types": list(set(m["type"] for m in media_messages)),
            "time_span_seconds": time_span_seconds,
            "detected_intents": detected_intents,
            "requires_immediate_response": "urgência" in detected_intents,
            "media_messages": media_messages,
            "analysis": {
                "is_fragmented": message_count > 3,
                "has_questions": "dúvida" in detected_intents,
                "shows_interest": "interesse" in detected_intents,
                "message_velocity": message_count / max(time_span_seconds, 1) if time_span_seconds > 0 else message_count
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagens bufferizadas: {e}", exc_info=True)
        return {
            "error": str(e),
            "consolidated_content": " ".join(msg.get("content", "") for msg in messages if msg.get("type") == "text"),
            "message_count": len(messages)
        }


@tool
async def analyze_message_pattern(
    agent,
    phone: str,
    time_window_minutes: int = 5
) -> Dict[str, Any]:
    """
    Analisa o padrão de mensagens de um usuário
    
    Útil para entender o comportamento do usuário e ajustar
    a estratégia de resposta.
    
    Args:
        agent: Instância do agente AGnO
        phone: Número de telefone do usuário
        time_window_minutes: Janela de tempo para análise
        
    Returns:
        Dict com análise do padrão de mensagens
    """
    
    try:
        # Obter histórico do session_state
        if not hasattr(agent, 'session_state') or not agent.session_state:
            return {
                "error": "Session state não disponível",
                "has_pattern": False
            }
        
        # Obter informações de mensagens bufferizadas anteriores
        buffered_info = agent.session_state.get('last_buffered_messages', {})
        
        # Análise básica
        analysis = {
            "phone": phone,
            "has_buffered_messages": bool(buffered_info),
            "average_messages_per_burst": buffered_info.get('count', 0),
            "tends_to_fragment": buffered_info.get('count', 0) > 2,
            "uses_media": buffered_info.get('has_media', False),
            "common_intents": buffered_info.get('detected_intents', []),
            "recommendation": ""
        }
        
        # Recomendações baseadas no padrão
        if analysis["tends_to_fragment"]:
            analysis["recommendation"] = "Aguardar usuário terminar antes de responder"
        elif analysis["uses_media"]:
            analysis["recommendation"] = "Preparar para análise de mídia"
        else:
            analysis["recommendation"] = "Responder normalmente"
        
        return analysis
        
    except Exception as e:
        logger.error(f"Erro ao analisar padrão de mensagens: {e}")
        return {
            "error": str(e),
            "has_pattern": False
        }