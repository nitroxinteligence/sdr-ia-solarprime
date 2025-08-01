"""
ResponseSanitizer - Filtro para vazamentos internos do AGnO Framework
CAMADA 3: Remove processos internos que vazam para respostas do usuário

PROBLEMA: AGnO Framework RunResponse vaza conteúdo interno como:
- "Got it. I'll continue the conversation"
- "I'll help you with that"
- "Let me process this information"
- Outros vazamentos de processamento interno

SOLUÇÃO: Sistema de sanitização que filtra conteúdo interno do AGnO
"""

import re
from typing import List, Optional, Dict, Any
from loguru import logger

class ResponseSanitizer:
    """
    Sanitizador de respostas para remover vazamentos internos do AGnO Framework
    
    Remove frases de processamento interno que não devem aparecer para o usuário final
    """
    
    # Padrões de vazamento interno do AGnO Framework
    INTERNAL_LEAKAGE_PATTERNS = [
        # Frases diretas de processamento (início de frase)
        r"^Got it\.?\s*I'll continue the conversation\.?\s*",
        r"^I'll help you with that\.?\s*",
        r"^Let me process this information\.?\s*",
        r"^I understand\.?\s*Let me assist you\.?\s*",
        r"^I'll take care of that\.?\s*",
        r"^Let me handle this\.?\s*",
        
        # Padrões de processamento interno AGnO
        r"^Processing\.\.\.\s*",
        r"^Analyzing request\.\.\.\s*",
        r"^Working on it\.\.\.\s*",
        r"^Please wait while I\.\.\.\s*",
        
        # Vazamentos de RunResponse (início)
        r"^RunResponse:\s*",
        r"^Content:\s*",
        r"^Status:\s*",
        
        # Frases genéricas de IA que vazam do processamento (início)
        r"^As an AI assistant,?\s*",
        r"^I'm here to help\.?\s*",
        r"^How can I assist you\?\s*",
        r"^What can I do for you\?\s*",
        
        # Vazamentos específicos do contexto Helen Vieira (início)
        r"^I'm Helen Vieira\.?\s*Let me help you\.?\s*",
        r"^This is Helen\.?\s*How can I help\?\s*",
        
        # Vazamentos de debug/log (linhas completas)
        r"^\[DEBUG\].*$",
        r"^\[INFO\].*$", 
        r"^\[ERROR\].*$",
        r"^Logger:.*$",
        
        # Frases de processamento no meio do texto (mais cuidadosas)
        r"\s+Got it\.?\s+I'll continue the conversation\.?\s+",
        r"\s+I'll help you with that\.?\s+",
    ]
    
    # Frases que devem ser removidas completamente
    COMPLETE_REMOVAL_PATTERNS = [
        r"^\s*$",  # Linhas vazias
        r"^\s*\.\.\.\s*$",  # Apenas pontos
        r"^\s*\-+\s*$",  # Apenas hífens
        r"^\s*=+\s*$",  # Apenas igual
    ]
    
    # Padrões de limpeza de formatação
    FORMATTING_CLEANUP = [
        r"\n\s*\n\s*\n",  # Múltiplas quebras de linha → dupla
        r"\s{3,}",  # Múltiplos espaços → espaço único
        r"^\s+",  # Espaços no início
        r"\s+$",  # Espaços no final
    ]
    
    def __init__(self):
        """Inicializa o sanitizador compilando os padrões regex"""
        self.internal_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                                 for pattern in self.INTERNAL_LEAKAGE_PATTERNS]
        self.removal_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                               for pattern in self.COMPLETE_REMOVAL_PATTERNS]
        self.formatting_patterns = [re.compile(pattern, re.MULTILINE) 
                                  for pattern in self.FORMATTING_CLEANUP]
        
        logger.info("ResponseSanitizer inicializado com {} padrões de vazamento", 
                   len(self.internal_patterns))
    
    def sanitize_response(self, response: str) -> str:
        """
        Sanitiza uma resposta removendo vazamentos internos do AGnO Framework
        
        Args:
            response: Resposta original que pode conter vazamentos
            
        Returns:
            Resposta sanitizada sem vazamentos internos
        """
        if not response or not isinstance(response, str):
            return response or ""
        
        original_response = response
        sanitized = response
        
        # 1. Remove vazamentos internos
        removed_patterns = []
        for pattern in self.internal_patterns:
            matches = pattern.findall(sanitized)
            if matches:
                sanitized = pattern.sub("", sanitized)
                removed_patterns.extend(matches)
        
        # 2. Remove linhas que devem ser completamente removidas
        for pattern in self.removal_patterns:
            sanitized = pattern.sub("", sanitized)
        
        # 3. Limpeza de formatação
        for pattern in self.formatting_patterns:
            if pattern.pattern == r"\n\s*\n\s*\n":
                sanitized = pattern.sub("\n\n", sanitized)
            elif pattern.pattern == r"\s{3,}":
                sanitized = pattern.sub(" ", sanitized)
            else:
                sanitized = pattern.sub("", sanitized)
        
        # 4. Limpeza final
        sanitized = sanitized.strip()
        
        # Log se algo foi removido
        if sanitized != original_response:
            removed_count = len(removed_patterns)
            original_len = len(original_response)
            sanitized_len = len(sanitized)
            reduction = original_len - sanitized_len
            
            logger.info(
                "ResponseSanitizer: Vazamentos removidos",
                patterns_removed=removed_count,
                chars_reduced=reduction,
                original_length=original_len,
                sanitized_length=sanitized_len
            )
            
            if removed_patterns:
                logger.debug("Padrões removidos: {}", removed_patterns[:3])  # Primeiros 3
        
        return sanitized
    
    def sanitize_agno_run_response(self, run_response: Any) -> Any:
        """
        Sanitiza especificamente um AGnO RunResponse object
        
        Args:
            run_response: Objeto RunResponse do AGnO Framework
            
        Returns: 
            RunResponse sanitizado
        """
        try:
            # Se tem atributo content (string)
            if hasattr(run_response, 'content') and isinstance(run_response.content, str):
                original_content = run_response.content
                sanitized_content = self.sanitize_response(original_content)
                
                if sanitized_content != original_content:
                    run_response.content = sanitized_content
                    logger.info("AGnO RunResponse.content sanitizado")
            
            # Se é uma lista de mensagens
            if hasattr(run_response, 'messages') and isinstance(run_response.messages, list):
                for message in run_response.messages:
                    if hasattr(message, 'content') and isinstance(message.content, str):
                        original_content = message.content
                        sanitized_content = self.sanitize_response(original_content)
                        
                        if sanitized_content != original_content:
                            message.content = sanitized_content
                            logger.info("AGnO Message.content sanitizado")
            
            # Se é um dict
            if isinstance(run_response, dict):
                if 'content' in run_response and isinstance(run_response['content'], str):
                    run_response['content'] = self.sanitize_response(run_response['content'])
                
                if 'messages' in run_response and isinstance(run_response['messages'], list):
                    for message in run_response['messages']:
                        if isinstance(message, dict) and 'content' in message:
                            message['content'] = self.sanitize_response(message['content'])
            
            return run_response
            
        except Exception as e:
            logger.error(f"Erro ao sanitizar AGnO RunResponse: {e}")
            return run_response
    
    def analyze_leakage(self, response: str) -> Dict[str, Any]:
        """
        Analisa vazamentos em uma resposta sem modificá-la
        
        Args:
            response: Resposta a ser analisada
            
        Returns:
            Dict com análise de vazamentos detectados
        """
        if not response:
            return {"has_leakage": False, "patterns_found": [], "leakage_score": 0}
        
        patterns_found = []
        total_matches = 0
        
        for i, pattern in enumerate(self.internal_patterns):
            matches = pattern.findall(response)
            if matches:
                patterns_found.append({
                    "pattern_index": i,
                    "pattern": self.INTERNAL_LEAKAGE_PATTERNS[i],
                    "matches": matches,
                    "count": len(matches)
                })
                total_matches += len(matches)
        
        # Score de vazamento (0-1, onde 1 = muito vazamento)
        leakage_score = min(total_matches / 5.0, 1.0)  # Max score em 5+ vazamentos
        
        return {
            "has_leakage": total_matches > 0,
            "patterns_found": patterns_found,
            "total_matches": total_matches,
            "leakage_score": leakage_score,
            "response_length": len(response)
        }


# Singleton global para uso em todo o sistema
_response_sanitizer = None

def get_response_sanitizer() -> ResponseSanitizer:
    """Retorna instância singleton do ResponseSanitizer"""
    global _response_sanitizer
    if _response_sanitizer is None:
        _response_sanitizer = ResponseSanitizer()
    return _response_sanitizer


# Decorator convenience para sanitizar respostas de funções
def sanitize_response(func):
    """
    Decorator que sanitiza automaticamente o retorno de uma função
    
    Usage:
        @sanitize_response
        def my_ai_function():
            return "Got it. I'll help you with that. Here's your answer..."
            # Retorna: "Here's your answer..."
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        if isinstance(result, str):
            sanitizer = get_response_sanitizer()
            return sanitizer.sanitize_response(result)
        
        return result
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Export principal
__all__ = ['ResponseSanitizer', 'get_response_sanitizer', 'sanitize_response']