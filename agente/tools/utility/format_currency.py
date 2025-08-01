"""
Format Currency Tool - Formata valores monetários em Reais
"""

from typing import Dict, Any, Union, Optional
from decimal import Decimal, InvalidOperation
from agno.tools import tool
from loguru import logger

from ...utils.formatters import format_currency as format_currency_util
from ...utils.validators import validate_bill_value


@tool(show_result=True)
async def format_currency(
    value: Union[str, float, int],
    validate: bool = True,
    include_cents: bool = True
) -> Dict[str, Any]:
    """
    Formata valores monetários no padrão brasileiro (R$ 1.234,56).
    
    Esta ferramenta formata valores monetários para o padrão brasileiro,
    podendo também validar se o valor está dentro de limites aceitáveis
    para contas de energia.
    
    Args:
        value: Valor a ser formatado (string, float ou int)
        validate: Se deve validar o valor (útil para contas de energia)
        include_cents: Se deve incluir os centavos na formatação
        
    Returns:
        Dict contendo:
        - success: Se a formatação foi bem sucedida
        - original: Valor original fornecido
        - formatted: Valor formatado em Reais
        - numeric_value: Valor numérico (float)
        - is_valid_bill: Se é um valor válido para conta de luz (quando validate=True)
        - validation_message: Mensagem de validação se aplicável
        - error: Mensagem de erro se houver
        
    Example:
        >>> await format_currency("1234.56")
        {
            "success": True,
            "original": "1234.56",
            "formatted": "R$ 1.234,56",
            "numeric_value": 1234.56,
            "is_valid_bill": True
        }
        
        >>> await format_currency("350,90", validate=True)
        {
            "success": True,
            "original": "350,90",
            "formatted": "R$ 350,90",
            "numeric_value": 350.90,
            "is_valid_bill": True
        }
    """
    try:
        logger.info(f"Formatando valor monetário: {value}")
        
        # Converter para float
        numeric_value = None
        
        if isinstance(value, str):
            # Limpar a string
            clean_value = value.strip()
            
            # Remover R$ se existir
            clean_value = clean_value.replace('R$', '').strip()
            
            # Remover pontos de milhar e converter vírgula para ponto
            clean_value = clean_value.replace('.', '').replace(',', '.')
            
            try:
                numeric_value = float(clean_value)
            except ValueError:
                # Tentar extrair números do texto
                import re
                numbers = re.findall(r'[\d,\.]+', clean_value)
                if numbers:
                    # Pegar o primeiro número encontrado
                    first_number = numbers[0].replace('.', '').replace(',', '.')
                    numeric_value = float(first_number)
                else:
                    raise ValueError("Não foi possível extrair um valor numérico")
        else:
            numeric_value = float(value)
        
        # Validar se solicitado
        is_valid_bill = None
        validation_message = None
        
        if validate:
            is_valid, error_msg = validate_bill_value(numeric_value)
            is_valid_bill = is_valid
            if not is_valid:
                validation_message = error_msg
                logger.warning(f"Valor fora dos limites esperados: {numeric_value} - {error_msg}")
        
        # Formatar o valor
        if include_cents:
            formatted = format_currency_util(numeric_value)
        else:
            # Formatar sem centavos
            formatted = f"R$ {int(numeric_value):,}".replace(',', '.')
        
        logger.success(f"Valor formatado: {value} -> {formatted}")
        
        result = {
            "success": True,
            "original": str(value),
            "formatted": formatted,
            "numeric_value": numeric_value
        }
        
        if validate:
            result["is_valid_bill"] = is_valid_bill
            if validation_message:
                result["validation_message"] = validation_message
        
        return result
        
    except (ValueError, InvalidOperation) as e:
        logger.error(f"Erro ao converter valor {value}: {str(e)}")
        return {
            "success": False,
            "original": str(value),
            "error": f"Valor inválido: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro ao formatar valor {value}: {str(e)}")
        return {
            "success": False,
            "original": str(value),
            "error": f"Erro ao processar valor: {str(e)}"
        }


# Função auxiliar para extrair valor monetário de texto
@tool(show_result=True)
async def extract_currency_from_text(text: str) -> Dict[str, Any]:
    """
    Extrai e formata valores monetários de um texto.
    
    Útil para processar mensagens que contêm valores de conta de luz.
    
    Args:
        text: Texto contendo valores monetários
        
    Returns:
        Dict contendo:
        - success: Se encontrou valores
        - values: Lista de valores encontrados e formatados
        - count: Quantidade de valores encontrados
        
    Example:
        >>> await extract_currency_from_text("Minha conta veio R$ 450,00 esse mês")
        {
            "success": True,
            "values": [
                {
                    "original": "450,00",
                    "formatted": "R$ 450,00",
                    "numeric_value": 450.0
                }
            ],
            "count": 1
        }
    """
    try:
        import re
        
        logger.info(f"Extraindo valores monetários do texto: {text[:100]}...")
        
        # Padrões para encontrar valores monetários
        patterns = [
            r'R\$\s*[\d.,]+',  # R$ 123,45 ou R$ 123.45
            r'[\d.,]+\s*(?:reais|real)',  # 123,45 reais
            r'(?:valor|conta|total|pagamento)[\s:]*R?\$?\s*([\d.,]+)',  # valor: 123,45
            r'[\d]+[,.][\d]{2}(?!\d)',  # 123,45 (formato decimal brasileiro)
        ]
        
        found_values = []
        processed_spans = []  # Para evitar duplicatas
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                span = match.span()
                
                # Verificar se já processamos essa parte do texto
                overlap = False
                for start, end in processed_spans:
                    if (span[0] >= start and span[0] < end) or (span[1] > start and span[1] <= end):
                        overlap = True
                        break
                
                if not overlap:
                    matched_text = match.group()
                    
                    # Tentar formatar o valor
                    result = await format_currency(matched_text, validate=True)
                    
                    if result["success"]:
                        found_values.append({
                            "original": matched_text,
                            "formatted": result["formatted"],
                            "numeric_value": result["numeric_value"],
                            "is_valid_bill": result.get("is_valid_bill", True)
                        })
                        processed_spans.append(span)
        
        # Remover duplicatas baseadas no valor numérico
        unique_values = []
        seen_values = set()
        
        for value in found_values:
            if value["numeric_value"] not in seen_values:
                unique_values.append(value)
                seen_values.add(value["numeric_value"])
        
        logger.success(f"Encontrados {len(unique_values)} valores monetários no texto")
        
        return {
            "success": len(unique_values) > 0,
            "values": unique_values,
            "count": len(unique_values)
        }
        
    except Exception as e:
        logger.error(f"Erro ao extrair valores do texto: {str(e)}")
        return {
            "success": False,
            "values": [],
            "count": 0,
            "error": str(e)
        }


# Exportar as tools
FormatCurrencyTool = format_currency
ExtractCurrencyFromTextTool = extract_currency_from_text