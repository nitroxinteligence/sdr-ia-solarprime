"""
Módulo de Conversões Seguras
Fornece funções utilitárias para conversões de tipo seguras e validadas
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Converte valor para int de forma segura
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se a conversão falhar
        
    Returns:
        int: Valor convertido ou default
    """
    if value is None:
        return default
    
    # Se já for int, retorna direto
    if isinstance(value, int):
        return value
    
    # Se for float, converte para int
    if isinstance(value, float):
        return int(value)
    
    # Se for string, tenta converter
    if isinstance(value, str):
        # Remove espaços e verifica casos especiais
        value = value.strip()
        
        # Casos especiais de strings vazias ou "None"
        if not value or value.lower() in ['none', 'null', 'nan']:
            return default
        
        # Remove símbolos comuns
        value = value.replace(',', '').replace('.', '')
        
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Não foi possível converter '{value}' para int. Usando valor padrão {default}")
            return default
    
    # Para qualquer outro tipo, retorna default
    return default


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Converte valor para float de forma segura
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se a conversão falhar
        
    Returns:
        float: Valor convertido ou default
    """
    if value is None:
        return default
    
    # Se já for float, retorna direto
    if isinstance(value, (int, float)):
        return float(value)
    
    # Se for string, tenta converter
    if isinstance(value, str):
        # Remove espaços e verifica casos especiais
        value = value.strip()
        
        # Casos especiais de strings vazias ou "None"
        if not value or value.lower() in ['none', 'null', 'nan']:
            return default
        
        # Tenta converter removendo símbolos de moeda comuns
        value = value.replace('R$', '').replace('$', '').replace(',', '.')
        
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Não foi possível converter '{value}' para float. Usando valor padrão {default}")
            return default
    
    # Para qualquer outro tipo, retorna default
    return default


def safe_datetime_conversion(
    value: Any, 
    default: Optional[datetime] = None,
    formats: Optional[list] = None
) -> Optional[datetime]:
    """
    Converte valor para datetime de forma segura
    
    Args:
        value: Valor a ser convertido (string ISO format ou datetime)
        default: Valor padrão se a conversão falhar
        formats: Lista de formatos para tentar (além do ISO format)
        
    Returns:
        datetime: Valor convertido ou default
    """
    if value is None:
        return default
    
    # Se já for datetime, retorna direto
    if isinstance(value, datetime):
        return value
    
    # Se for string, tenta converter
    if isinstance(value, str):
        value = value.strip()
        
        if not value:
            return default
        
        # Primeiro tenta ISO format
        try:
            # Remove timezone indicators para simplificar
            cleaned_value = value.replace('Z', '+00:00')
            return datetime.fromisoformat(cleaned_value)
        except (ValueError, TypeError):
            pass
        
        # Tenta formatos customizados se fornecidos
        if formats:
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except (ValueError, TypeError):
                    continue
        
        # Formatos comuns brasileiros
        common_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
            '%Y-%m-%d',
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        
        logger.warning(f"Não foi possível converter '{value}' para datetime")
        return default
    
    return default


def safe_json_loads(
    value: Union[str, bytes], 
    default: Any = None,
    strict: bool = False
) -> Any:
    """
    Faz parse de JSON de forma segura
    
    Args:
        value: String ou bytes contendo JSON
        default: Valor padrão se o parse falhar
        strict: Se True, controle rigoroso de formato
        
    Returns:
        Any: Objeto parseado ou default
    """
    if not value:
        return default
    
    try:
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        
        return json.loads(value, strict=strict)
    except json.JSONDecodeError as e:
        logger.warning(f"Erro ao fazer parse de JSON: {e}")
        return default
    except Exception as e:
        logger.error(f"Erro inesperado ao fazer parse de JSON: {e}")
        return default


def safe_json_dumps(
    obj: Any, 
    default: str = "{}",
    **kwargs
) -> str:
    """
    Serializa objeto para JSON de forma segura
    
    Args:
        obj: Objeto a ser serializado
        default: String padrão se a serialização falhar
        **kwargs: Argumentos adicionais para json.dumps
        
    Returns:
        str: JSON string ou default
    """
    try:
        # Define defaults sensatos
        kwargs.setdefault('ensure_ascii', False)
        kwargs.setdefault('default', str)  # Converte objetos não serializáveis para string
        
        return json.dumps(obj, **kwargs)
    except Exception as e:
        logger.warning(f"Erro ao serializar objeto para JSON: {e}")
        return default


def safe_dict_get(
    dictionary: dict,
    key: str,
    default: Any = None,
    expected_type: Optional[type] = None
) -> Any:
    """
    Obtém valor de dicionário com validação de tipo opcional
    
    Args:
        dictionary: Dicionário fonte
        key: Chave a buscar
        default: Valor padrão
        expected_type: Tipo esperado (opcional)
        
    Returns:
        Any: Valor encontrado ou default
    """
    if not isinstance(dictionary, dict):
        return default
    
    value = dictionary.get(key, default)
    
    # Se não há tipo esperado, retorna o valor
    if expected_type is None:
        return value
    
    # Valida o tipo
    if value is not None and not isinstance(value, expected_type):
        logger.warning(
            f"Tipo inesperado para '{key}': esperado {expected_type.__name__}, "
            f"recebido {type(value).__name__}"
        )
        return default
    
    return value