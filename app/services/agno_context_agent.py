#!/usr/bin/env python3
"""
AGNO ContextEnhancementAgent - Sub-agente modular para gerenciamento de contexto
Baseado nos padrões AGNO Framework para context management

FILOSOFIA: ZERO COMPLEXIDADE - O SIMPLES FUNCIONA
- Wrappeia o código existente de contexto sem breaking changes
- Melhora formatação de histórico de mensagens
- Adiciona metadata AGNO para context quality
- Decorator pattern para modularidade
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from app.utils.logger import emoji_logger


class AGNOContextManager:
    """
    Gerenciador de contexto baseado nos padrões AGNO Framework
    Melhora formatting, metadata e context quality
    """
    
    def __init__(self):
        """Initialize com configurações AGNO"""
        self.max_messages = 50  # AGNO standard for context window
        self.max_message_length = 200  # Truncate long messages for context efficiency
        self.context_quality_thresholds = {
            'excellent': 40,  # 40+ messages with rich content
            'good': 20,       # 20+ messages 
            'fair': 10,       # 10+ messages
            'poor': 5,        # 5+ messages
            'minimal': 1      # 1+ messages
        }
    
    def enhance_message_history(
        self, 
        messages: List[Dict[str, Any]], 
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhanced message history formatting com AGNO patterns
        
        Args:
            messages: Lista de mensagens brutas
            phone: Número do telefone (opcional)
            
        Returns:
            Dict com histórico formatado + AGNO metadata
        """
        try:
            if not messages:
                return {
                    'formatted_history': "",
                    'message_count': 0,
                    'context_quality': 'empty',
                    'agno_context_score': 0.0,
                    'truncated': False
                }
            
            # Truncar para últimas N mensagens (AGNO pattern)
            recent_messages = messages[-self.max_messages:] if len(messages) > self.max_messages else messages
            truncated = len(messages) > self.max_messages
            
            # Formatar mensagens com padrão AGNO
            formatted_lines = []
            content_richness_score = 0
            
            for msg in recent_messages:
                try:
                    # Determinar role/sender
                    role = self._determine_message_role(msg)
                    content = self._extract_message_content(msg)
                    timestamp = self._extract_timestamp(msg)
                    
                    if content:
                        # Truncar mensagem muito longa
                        if len(content) > self.max_message_length:
                            content = content[:self.max_message_length] + "..."
                        
                        # Formato AGNO: Role: Content [timestamp]
                        formatted_line = f"{role}: {content}"
                        if timestamp:
                            formatted_line += f" [{timestamp}]"
                        
                        formatted_lines.append(formatted_line)
                        
                        # Calcular richness score baseado no conteúdo
                        content_richness_score += self._calculate_content_richness(content)
                    
                except Exception as msg_error:
                    emoji_logger.system_warning(f"Erro ao formatar mensagem: {msg_error}")
                    continue
            
            # Combinar em histórico formatado
            formatted_history = "\n".join(formatted_lines)
            
            # Calcular quality score AGNO
            context_quality = self._calculate_context_quality(len(formatted_lines), content_richness_score)
            agno_score = self._calculate_agno_context_score(len(formatted_lines), content_richness_score, truncated)
            
            result = {
                'formatted_history': formatted_history,
                'message_count': len(formatted_lines),
                'original_count': len(messages),
                'context_quality': context_quality,
                'agno_context_score': agno_score,
                'truncated': truncated,
                'phone': phone,
                'processing_timestamp': datetime.now().isoformat(),
                'agno_pattern': 'ContextManager'
            }
            
            emoji_logger.system_info(
                f"AGNO Context enhanced: {len(formatted_lines)} mensagens, "
                f"quality={context_quality}, score={agno_score:.2f}"
            )
            
            return result
            
        except Exception as e:
            emoji_logger.system_error("AGNO Context Enhancement", str(e))
            return {
                'formatted_history': "",
                'message_count': 0,
                'context_quality': 'error',
                'agno_context_score': 0.0,
                'error': str(e)
            }
    
    def _determine_message_role(self, msg: Dict[str, Any]) -> str:
        """Determina role da mensagem com padrões AGNO"""
        # Tentar diferentes campos de role/sender
        role_fields = ['role', 'sender', 'from', 'author']
        
        for field in role_fields:
            if field in msg:
                role_value = msg[field].lower()
                if role_value in ['user', 'client', 'customer']:
                    return "Cliente"
                elif role_value in ['assistant', 'agent', 'bot', 'system']:
                    return "Assistente" 
                elif role_value in ['admin', 'operator']:
                    return "Operador"
        
        # Fallback baseado em conteúdo ou estrutura
        if msg.get('content', '').startswith('['):
            return "Sistema"
        
        return "Cliente"  # Default
    
    def _extract_message_content(self, msg: Dict[str, Any]) -> str:
        """Extrai conteúdo da mensagem com fallbacks"""
        content_fields = ['content', 'text', 'message', 'body']
        
        for field in content_fields:
            if field in msg and msg[field]:
                content = str(msg[field]).strip()
                if content:
                    return content
        
        return ""
    
    def _extract_timestamp(self, msg: Dict[str, Any]) -> Optional[str]:
        """Extrai timestamp formatado"""
        timestamp_fields = ['timestamp', 'created_at', 'sent_at', 'date']
        
        for field in timestamp_fields:
            if field in msg and msg[field]:
                try:
                    # Assumir ISO format ou timestamp
                    timestamp_str = str(msg[field])
                    if timestamp_str:
                        # Simplificar timestamp para contexto
                        if 'T' in timestamp_str:
                            date_part = timestamp_str.split('T')[0]
                            time_part = timestamp_str.split('T')[1][:5]  # HH:MM
                            return f"{date_part} {time_part}"
                        return timestamp_str[:16]  # Truncar se muito longo
                except Exception:
                    continue
        
        return None
    
    def _calculate_content_richness(self, content: str) -> float:
        """Calcula richness score do conteúdo"""
        if not content:
            return 0.0
        
        richness = 0.0
        
        # Comprimento do conteúdo
        richness += min(len(content) / 100, 1.0)  # Max 1.0 for length
        
        # Presença de questões (engagement)
        if '?' in content:
            richness += 0.3
        
        # Presença de números (dados específicos)
        if any(char.isdigit() for char in content):
            richness += 0.2
        
        # Conteúdo não é apenas saudações
        greeting_words = ['oi', 'olá', 'bom dia', 'boa tarde', 'boa noite', 'tchau']
        if not any(greeting.lower() in content.lower() for greeting in greeting_words):
            richness += 0.3
        
        # Presença de mídia
        if any(indicator in content for indicator in ['[Imagem', '[Documento', '[Áudio', '[Vídeo']):
            richness += 0.5
        
        return min(richness, 2.0)  # Cap at 2.0
    
    def _calculate_context_quality(self, message_count: int, total_richness: float) -> str:
        """Calcula quality level baseado nos thresholds"""
        avg_richness = total_richness / max(message_count, 1)
        adjusted_count = message_count * (1 + avg_richness / 2)  # Bonus for rich content
        
        for quality, threshold in self.context_quality_thresholds.items():
            if adjusted_count >= threshold:
                return quality
        
        return 'minimal'
    
    def _calculate_agno_context_score(
        self, 
        message_count: int, 
        total_richness: float, 
        truncated: bool
    ) -> float:
        """Calcula AGNO context score (0.0 - 1.0)"""
        if message_count == 0:
            return 0.0
        
        # Base score por quantidade de mensagens
        quantity_score = min(message_count / self.max_messages, 1.0)
        
        # Quality score por richness
        avg_richness = total_richness / message_count
        quality_score = min(avg_richness / 2.0, 1.0)
        
        # Penalty por truncation
        truncation_penalty = 0.1 if truncated else 0.0
        
        # Weighted average
        final_score = (quantity_score * 0.4 + quality_score * 0.6) - truncation_penalty
        
        return max(0.0, min(1.0, final_score))
    
    def enhance_multimodal_context_formatting(
        self, 
        multimodal_result: Optional[Dict[str, Any]], 
        message_history: str
    ) -> str:
        """
        Enhanced formatting para contexto multimodal (AGNO pattern)
        
        Args:
            multimodal_result: Resultado do processamento multimodal
            message_history: Histórico de mensagens formatado
            
        Returns:
            Contexto completo formatado para o agente
        """
        try:
            context_parts = []
            
            # Histórico de mensagens (se disponível)
            if message_history and message_history.strip():
                context_parts.append("=== HISTÓRICO DE CONVERSA ===")
                context_parts.append(message_history)
                context_parts.append("")  # Linha em branco
            
            # Conteúdo multimodal (se disponível)
            if multimodal_result and not multimodal_result.get('error'):
                media_type = multimodal_result.get('type', 'unknown')
                
                if media_type == 'document':
                    context_parts.append("=== DOCUMENTO RECEBIDO ===")
                    filename = multimodal_result.get('filename', 'documento')
                    context_parts.append(f"📄 Arquivo: {filename}")
                    
                    # Conteúdo do documento (truncado se muito longo)
                    content = multimodal_result.get('content', '')
                    if content:
                        if len(content) > 1500:  # AGNO context window management
                            content = content[:1500] + "...\n[Documento truncado para contexto]"
                        context_parts.append(f"Conteúdo:\n{content}")
                    
                    # Metadata AGNO se disponível
                    if multimodal_result.get('agno_metadata'):
                        agno_meta = multimodal_result['agno_metadata']
                        if agno_meta.get('pages'):
                            context_parts.append(f"📊 {agno_meta['pages']} páginas")
                        if agno_meta.get('images_processed', 0) > 0:
                            context_parts.append(f"🔍 {agno_meta['images_processed']} imagens processadas com OCR")
                    
                elif media_type == 'image':
                    context_parts.append("=== IMAGEM RECEBIDA ===")
                    caption = multimodal_result.get('caption', '')
                    if caption:
                        context_parts.append(f"💬 Legenda: {caption}")
                    
                    # AGNO metadata se disponível
                    if multimodal_result.get('agno_metadata'):
                        agno_meta = multimodal_result['agno_metadata']
                        confidence = agno_meta.get('combined_confidence', 'unknown')
                        context_parts.append(f"📊 Confiança: {confidence}")
                
                context_parts.append("")  # Linha em branco
            
            # Combinar contexto completo
            full_context = "\n".join(context_parts)
            
            if full_context.strip():
                return full_context
            else:
                return ""  # Contexto vazio
                
        except Exception as e:
            emoji_logger.system_error("AGNO Context Formatting", str(e))
            return message_history or ""  # Fallback para histórico básico


# Instância global do context manager AGNO
agno_context_manager = AGNOContextManager()


def agno_context_enhancer(func: Callable) -> Callable:
    """
    Decorator AGNO para enhanced context management
    Wrappeia método existente + adiciona AGNO context capabilities
    
    ZERO COMPLEXIDADE: Mantém código existente funcionando
    """
    def wrapper(*args, **kwargs):
        # Chama método original (mantém funcionalidade existente)
        original_result = func(*args, **kwargs)
        
        # Se é lista de mensagens, aplicar AGNO enhancements
        if isinstance(original_result, list):
            try:
                # Determinar phone se disponível nos args
                phone = None
                if args and isinstance(args[0], str):
                    phone = args[0]  # Provavelmente phone number
                
                # Aplicar AGNO context enhancement
                agno_context = agno_context_manager.enhance_message_history(original_result, phone)
                
                # Adicionar metadata AGNO à lista original
                if hasattr(original_result, 'agno_metadata'):
                    original_result.agno_metadata = agno_context
                else:
                    # Se não pode adicionar atributo, criar wrapper dict
                    enhanced_result = {
                        'messages': original_result,
                        'agno_metadata': agno_context,
                        'enhanced_with_agno': True
                    }
                    
                    emoji_logger.system_info(
                        f"AGNO Context enhanced: {agno_context['message_count']} mensagens, "
                        f"quality={agno_context['context_quality']}"
                    )
                    
                    return enhanced_result
                
            except Exception as e:
                emoji_logger.system_warning(f"AGNO context enhancement failed (non-critical): {e}")
                # Não falha - apenas não adiciona enhancements
        
        return original_result
    
    return wrapper


def format_context_with_agno(
    message_history: List[Dict[str, Any]], 
    multimodal_result: Optional[Dict[str, Any]] = None,
    phone: Optional[str] = None
) -> str:
    """
    Interface pública para formatação de contexto AGNO
    
    Args:
        message_history: Lista de mensagens
        multimodal_result: Resultado multimodal (opcional)
        phone: Número do telefone (opcional)
        
    Returns:
        Contexto formatado para o agente
    """
    try:
        # Enhanced message history
        agno_context = agno_context_manager.enhance_message_history(message_history, phone)
        formatted_history = agno_context['formatted_history']
        
        # Enhanced multimodal context
        full_context = agno_context_manager.enhance_multimodal_context_formatting(
            multimodal_result, 
            formatted_history
        )
        
        return full_context
        
    except Exception as e:
        emoji_logger.system_error("AGNO Context Formatting", str(e))
        return ""  # Fallback vazio