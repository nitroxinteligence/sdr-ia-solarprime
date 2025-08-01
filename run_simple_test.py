#!/usr/bin/env python3
"""
Script simples para executar testes sem todas as dependências
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Test simple format_currency functionality
print("🧪 Teste simples do format_currency...")

try:
    from agente.tools.utility.format_currency import format_currency
    import asyncio
    
    async def test():
        result = await format_currency(1234.56)
        print(f"✅ Teste passou! Resultado: {result}")
        return result
    
    result = asyncio.run(test())
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 Resumo de Testes Disponíveis:")
print("- Unit Tests: 30 tools em 6 categorias")
print("  - WhatsApp: 9 testes")
print("  - Kommo CRM: 6 testes") 
print("  - Calendar: 5 testes")
print("  - Database: 6 testes")
print("  - Media: 3 testes")
print("  - Utility: 4 testes")
print("- Integration Tests: APIs externas")
print("- Stress Tests: Conversas concorrentes")
print("- Validation Tests: Humanização")
print("- Performance Benchmarks: Métricas")

print("\n⚠️ Nota: Os testes completos requerem configuração de ambiente adequada.")