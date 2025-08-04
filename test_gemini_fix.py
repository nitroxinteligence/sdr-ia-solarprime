#!/usr/bin/env python3
"""
Script de teste para verificar se o erro do Gemini foi corrigido
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_gemini():
    """Teste básico do Gemini com retry"""
    try:
        from app.agents.agentic_sdr import IntelligentModelFallback
        from app.config import settings
        from app.utils.logger import emoji_logger
        
        print("=" * 50)
        print("🧪 TESTE DE CORREÇÃO DO GEMINI")
        print("=" * 50)
        
        # Criar instância do modelo com retry
        print("\n1. Criando instância do IntelligentModelFallback...")
        model_manager = IntelligentModelFallback(settings)
        
        # Teste de mensagem simples
        print("\n2. Enviando mensagem de teste...")
        test_message = "Olá! Responda apenas: 'Sistema funcionando corretamente'"
        
        try:
            response = await model_manager.run(test_message)
            print(f"\n✅ SUCESSO! Resposta recebida:")
            print(f"   {response}")
            print("\n🎉 O erro foi corrigido com sucesso!")
            
        except Exception as e:
            print(f"\n❌ ERRO ao executar modelo:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensagem: {str(e)}")
            
            # Verificar se é o erro de 'str' object has no attribute 'role'
            if "'str' object has no attribute 'role'" in str(e):
                print("\n⚠️ O erro original ainda persiste!")
                print("   O modelo ainda espera um objeto Message ao invés de string")
            else:
                print(f"\n⚠️ Erro diferente encontrado: {e}")
        
        print("\n" + "=" * 50)
        print("📊 INFORMAÇÕES DO MODELO:")
        print("=" * 50)
        
        model_info = model_manager.get_current_model_info()
        print(f"Modelo atual: {model_info['current_model']}")
        print(f"Fallback ativo: {model_info['fallback_active']}")
        print(f"Tem fallback: {model_info['has_fallback']}")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("   Verifique se o ambiente está configurado corretamente")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Iniciando teste do Gemini com correção...")
    asyncio.run(test_gemini())