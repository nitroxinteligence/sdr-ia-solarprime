"""
Currency Parser Utility
=======================
Utilitário para converter valores monetários brasileiros para float
"""

from typing import Union, Optional
from loguru import logger


def parse_brazilian_currency(value: Union[str, float, int]) -> Optional[float]:
    """
    Converte valor monetário brasileiro para float.
    
    Suporta formatos como:
    - "R$ 800"
    - "R$ 1.500,00"
    - "1500,00"
    - "1.500"
    - 800 (int)
    - 800.0 (float)
    
    Args:
        value: Valor monetário em diversos formatos
        
    Returns:
        float: Valor convertido ou None se não conseguir converter
    """
    if value is None:
        return None
        
    # Se já é float ou int, retornar direto
    if isinstance(value, (int, float)):
        return float(value)
    
    try:
        # Converter para string e limpar
        value_str = str(value).strip()
        
        # Remover símbolo de moeda e espaços
        cleaned = value_str.replace("R$", "").replace(" ", "").strip()
        
        # Se estiver vazio após limpeza
        if not cleaned:
            return None
        
        # Detectar formato brasileiro (vírgula como decimal)
        if "," in cleaned:
            # Se tem vírgula e ponto, assumir formato brasileiro (1.500,00)
            if "." in cleaned:
                # Remover pontos de milhar
                cleaned = cleaned.replace(".", "")
            # Trocar vírgula por ponto
            cleaned = cleaned.replace(",", ".")
        else:
            # Se só tem ponto, verificar se é separador de milhar
            if "." in cleaned and len(cleaned.split(".")[-1]) == 3:
                # É separador de milhar (ex: 1.500)
                cleaned = cleaned.replace(".", "")
        
        # Converter para float
        result = float(cleaned)
        
        # Validar resultado (não pode ser negativo para conta de luz)
        if result < 0:
            logger.warning(f"Valor negativo detectado: {result}")
            return None
            
        return result
        
    except (ValueError, AttributeError) as e:
        logger.debug(f"Erro ao converter valor monetário '{value}': {e}")
        return None


def format_brazilian_currency(value: float) -> str:
    """
    Formata float para moeda brasileira.
    
    Args:
        value: Valor numérico
        
    Returns:
        str: Valor formatado como "R$ 1.500,00"
    """
    try:
        # Formatar com 2 casas decimais
        formatted = f"{value:,.2f}"
        # Trocar separadores para formato brasileiro
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except Exception as e:
        logger.error(f"Erro ao formatar valor {value}: {e}")
        return f"R$ {value}"


# Testes básicos
if __name__ == "__main__":
    test_values = [
        "R$ 800",
        "R$ 1.500,00",
        "1500,00",
        "1.500",
        "800",
        800,
        800.0,
        "R$ 1.234,56",
        "R$ 1.234.567,89",
        None,
        "",
        "R$ ",
        "abc"
    ]
    
    print("Testando conversão de valores:")
    for val in test_values:
        result = parse_brazilian_currency(val)
        print(f"'{val}' -> {result}")
    
    print("\nTestando formatação:")
    test_numbers = [800, 1500, 1234.56, 1234567.89]
    for num in test_numbers:
        formatted = format_brazilian_currency(num)
        print(f"{num} -> {formatted}")