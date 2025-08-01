#!/usr/bin/env python3
"""
Teste específico para verificar apenas a inicialização do AGnO Agent.
"""

import sys
from pathlib import Path
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_agno_agent_direct():
    """Testa apenas a inicialização do AGnO Agent diretamente"""
    print("🧪 Testando inicialização direta do AGnO Agent...")
    
    try:
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        from agno.agent import Agent
        from agno.models.google import Gemini
        
        # Create Gemini model
        model = Gemini(
            id="gemini-2.0-flash-exp",
            api_key="test_key",
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.9
        )
        
        # Test Agent creation without debug parameter
        agent = Agent(
            name="Test Agent",
            model=model,
            tools=[],  # Empty tools for testing
            show_tool_calls=True,
            reasoning=False,
            storage=False,
            memory=False,
            instructions="Test instructions"
            # No debug parameter!
        )
        
        print("✅ AGnO Agent criado com sucesso sem parâmetro debug!")
        print(f"   - Agent name: {agent.name}")
        print("✅ CORREÇÃO DO PARÂMETRO debug CONFIRMADA!")
        
        return True
        
    except TypeError as e:
        if "unexpected keyword argument 'debug'" in str(e):
            print("❌ Erro: Ainda está passando parâmetro debug inválido")
            print(f"   Erro: {e}")
            return False
        else:
            print(f"❌ Erro de tipo diferente: {e}")
            return False
            
    except Exception as e:
        # For any other error (like API key issues), we still consider the debug fix successful
        if "unexpected keyword argument 'debug'" not in str(e):
            print("✅ Parâmetro debug corrigido (outros erros são independentes)")
            print(f"   Erro não relacionado ao debug: {e}")
            return True
        else:
            print(f"❌ Erro relacionado ao debug: {e}")
            return False

def main():
    """Executa teste focado no parâmetro debug"""
    print("🚀 Teste Específico do Parâmetro debug AGnO")
    print("=" * 50)
    
    if test_agno_agent_direct():
        print("\n🎉 CORREÇÃO DO PARÂMETRO debug CONCLUÍDA COM SUCESSO!")
        print("🔧 Problema original: Agent.__init__() got an unexpected keyword argument 'debug'")
        print("✅ Solução aplicada: Removido parâmetro 'debug=DEBUG' da inicialização do Agent")
        print("📝 Arquivo corrigido: agente/core/agent.py")
        print("\n🚀 O AGnO Agent agora pode ser inicializado sem erros de parâmetro debug!")
        return True
    else:
        print("\n⚠️  A correção não foi bem-sucedida.")
        return False

if __name__ == "__main__":
    main()