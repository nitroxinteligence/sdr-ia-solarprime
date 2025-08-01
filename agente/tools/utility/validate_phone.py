"""
Validate Phone Tool - Valida e formata número de telefone brasileiro
"""

from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from ...utils.validators import validate_phone_number
from ...utils.formatters import format_phone_number


@tool(show_result=True)
async def validate_phone(phone: str) -> Dict[str, Any]:
    """
    Valida e formata número de telefone brasileiro.
    
    Esta ferramenta valida números de telefone brasileiros, verificando:
    - DDD válido (11-99)
    - Quantidade correta de dígitos (10 ou 11)
    - Formatação para o padrão internacional (+55)
    
    Args:
        phone: Número de telefone em qualquer formato
        
    Returns:
        Dict contendo:
        - success: Se a validação foi bem sucedida
        - original: Número original fornecido
        - formatted: Número formatado (+5511999999999) se válido
        - is_mobile: Se é um celular (tem 9 dígitos após DDD)
        - ddd: Código de área extraído
        - error: Mensagem de erro se inválido
        
    Example:
        >>> await validate_phone("11 98765-4321")
        {
            "success": True,
            "original": "11 98765-4321",
            "formatted": "+5511987654321",
            "is_mobile": True,
            "ddd": "11"
        }
    """
    try:
        logger.info(f"Validando telefone: {phone}")
        
        # Validar o número
        is_valid, error_message = validate_phone_number(phone)
        
        if not is_valid:
            logger.warning(f"Telefone inválido: {phone} - {error_message}")
            return {
                "success": False,
                "original": phone,
                "error": error_message
            }
        
        # Formatar o número
        formatted = format_phone_number(phone)
        
        # Extrair informações adicionais
        # Remove o +55 para análise
        digits = formatted[3:]
        ddd = digits[:2]
        local_number = digits[2:]
        
        # Verifica se é celular (9 dígitos no número local)
        is_mobile = len(local_number) == 9
        
        logger.success(f"Telefone válido e formatado: {phone} -> {formatted}")
        
        return {
            "success": True,
            "original": phone,
            "formatted": formatted,
            "is_mobile": is_mobile,
            "ddd": ddd
        }
        
    except Exception as e:
        logger.error(f"Erro ao validar telefone {phone}: {str(e)}")
        return {
            "success": False,
            "original": phone,
            "error": f"Erro ao processar telefone: {str(e)}"
        }


# Exportar a tool
ValidatePhoneTool = validate_phone