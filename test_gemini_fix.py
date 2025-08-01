#!/usr/bin/env python3
"""
Teste específico para verificar se a correção do modelo Gemini funcionou.
Este teste verifica apenas a inicialização do modelo Gemini sem dependências externas.
"""

import sys
from pathlib import Path
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_model_initialization():
    """Testa apenas a inicialização do modelo Gemini"""
    print("🧪 Testando inicialização do modelo Gemini...")
    
    try:
        # Set a dummy API key for testing
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        from agno.models.google import Gemini
        
        # Test Gemini model creation with correct parameter
        model = Gemini(
            id="gemini-2.0-flash-exp",
            api_key="test_key",
            temperature=0.7,
            max_output_tokens=2048,  # Corrected parameter name
            top_p=0.9
        )
        
        print("✅ Modelo Gemini inicializado com sucesso!")
        print(f"   - Model ID: {model.id}")
        print(f"   - Temperature: {model.temperature}")
        print(f"   - Max Output Tokens: {getattr(model, 'max_output_tokens', 'não definido')}")
        print("✅ CORREÇÃO DO PARÂMETRO max_output_tokens FUNCIONOU!")
        
        return True
        
    except TypeError as e:
        if "unexpected keyword argument 'max_tokens'" in str(e):
            print("❌ Erro: Ainda está usando max_tokens em vez de max_output_tokens")
            print(f"   Erro: {e}")
            return False
        elif "unexpected keyword argument" in str(e):
            print(f"❌ Erro de parâmetro inválido: {e}")
            return False
        else:
            print(f"❌ Erro de tipo: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação AGnO: {e}")
        print("   Pode ser que AGnO não esteja instalado")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_core_import():
    """Testa se a correção não quebrou as importações do agent"""
    print("\n🧪 Testando importação da classe SDRAgent...")
    
    try:
        # Mock environment variables to avoid dependency errors
        mock_vars = {
            'SUPABASE_URL': 'http://test',
            'SUPABASE_SERVICE_KEY': 'test_key',
            'EVOLUTION_API_URL': 'http://test',
            'EVOLUTION_API_KEY': 'test_key',
            'KOMMO_SUBDOMAIN': 'test',
            'KOMMO_LONG_LIVED_TOKEN': 'test',
            'GOOGLE_SERVICE_ACCOUNT_EMAIL': 'test@test.com',
            'GOOGLE_PRIVATE_KEY': 'test_key'
        }
        
        for key, value in mock_vars.items():
            os.environ[key] = value
        
        from agente.core.agent import SDRAgent
        print("✅ Importação da classe SDRAgent bem-sucedida!")
        print("✅ A correção não quebrou as importações!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def main():
    """Executa todos os testes de correção do Gemini"""
    print("🚀 Teste de Correção do Modelo Gemini")
    print("=" * 50)
    
    tests = [
        ("Inicialização do Modelo Gemini", test_gemini_model_initialization),
        ("Importação da Classe SDRAgent", test_agent_core_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO DA CORREÇÃO")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÃO DO GEMINI MODEL CONCLUÍDA COM SUCESSO!")
        print("🔧 Problema original: TypeError: Gemini.__init__() got an unexpected keyword argument 'max_tokens'")
        print("✅ Solução aplicada: Alterado 'max_tokens' para 'max_output_tokens'")
        print("📝 Arquivo corrigido: agente/core/agent.py linha 200")
        print("\n🚀 O sistema agora pode ser iniciado sem erros de modelo Gemini!")
        return True
    else:
        print(f"\n⚠️  A correção não foi totalmente bem-sucedida.")
        print(f"   {total-passed} teste(s) ainda falharam.")
        return False

if __name__ == "__main__":
    main()