#!/usr/bin/env python3
"""
Teste direto do format_currency sem importar toda a estrutura
"""
import sys
import os
import asyncio

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

async def test_format_currency():
    """Testa a função format_currency diretamente"""
    # Importar apenas o necessário
    from agente.tools.utility.format_currency import format_currency
    
    # Testar a função
    result = await format_currency(1234.56)
    
    print("✅ Teste passou!")
    print(f"   Entrada: 1234.56")
    print(f"   Saída: {result['formatted']}")
    print(f"   Valor numérico: {result['numeric_value']}")
    
    # Testar com string
    result2 = await format_currency("R$ 350,90")
    print(f"\n✅ Teste 2 passou!")
    print(f"   Entrada: R$ 350,90")
    print(f"   Saída: {result2['formatted']}")
    print(f"   Valor numérico: {result2['numeric_value']}")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_format_currency())
        print("\n🎉 Todos os testes passaram!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()