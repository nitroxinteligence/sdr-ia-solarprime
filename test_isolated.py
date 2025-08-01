#!/usr/bin/env python3
"""
Teste isolado sem importar nenhuma estrutura do agente
"""
import asyncio

async def format_currency(value: float | str, validate: bool = True, include_cents: bool = True) -> dict:
    """
    Formata um valor monetário no padrão brasileiro
    
    Args:
        value: Valor para formatar (pode ser float, int ou string)
        validate: Se True, valida se é um valor de conta válido
        include_cents: Se True, inclui centavos na formatação
        
    Returns:
        Dict com valor formatado e informações adicionais
    """
    try:
        # Remove R$ e espaços se existir
        if isinstance(value, str):
            value = value.replace("R$", "").replace("reais", "").strip()
            # Substitui vírgula por ponto para conversão
            value = value.replace(".", "").replace(",", ".")
        
        # Converte para float
        numeric_value = float(value)
        
        # Formata para real brasileiro
        if include_cents:
            formatted = f"R$ {numeric_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            formatted = f"R$ {int(numeric_value):,}".replace(",", ".")
        
        result = {
            "success": True,
            "original": str(value),
            "formatted": formatted,
            "numeric_value": numeric_value
        }
        
        # Validação de conta de energia
        if validate:
            if numeric_value < 50:
                result["is_valid_bill"] = False
                result["validation_message"] = "Valor muito baixo para conta de energia"
            elif numeric_value > 10000:
                result["is_valid_bill"] = False
                result["validation_message"] = "Valor muito alto para conta residencial"
            else:
                result["is_valid_bill"] = True
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original": str(value)
        }

async def test():
    print("🧪 Teste isolado do format_currency\n")
    
    # Teste 1: Float
    result = await format_currency(1234.56)
    print(f"Teste 1 - Float: {result['formatted']}")
    assert result['formatted'] == "R$ 1.234,56"
    
    # Teste 2: String com vírgula
    result = await format_currency("350,90")
    print(f"Teste 2 - String com vírgula: {result['formatted']}")
    assert result['formatted'] == "R$ 350,90"
    
    # Teste 3: String com R$
    result = await format_currency("R$ 450,00")
    print(f"Teste 3 - String com R$: {result['formatted']}")
    assert result['formatted'] == "R$ 450,00"
    
    # Teste 4: Validação
    result = await format_currency(350.00, validate=True)
    print(f"Teste 4 - Validação: {result['is_valid_bill']} - {result['formatted']}")
    assert result['is_valid_bill'] == True
    
    print("\n✅ Todos os testes passaram!")

if __name__ == "__main__":
    asyncio.run(test())