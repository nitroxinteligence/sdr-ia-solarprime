#!/usr/bin/env python3
"""
Teste específico para verificar se a correção do parâmetro debug funcionou.
"""

import sys
from pathlib import Path
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_agno_agent_initialization():
    """Testa se o AGnO Agent inicializa sem erro de parâmetro debug"""
    print("🧪 Testando inicialização do AGnO Agent sem parâmetro debug...")
    
    try:
        # Set mock environment variables
        mock_vars = {
            'GEMINI_API_KEY': 'test_key',
            'SUPABASE_URL': 'http://test',
            'SUPABASE_SERVICE_KEY': 'test_key',
            'EVOLUTION_API_URL': 'http://test',
            'EVOLUTION_API_KEY': 'test_key',
            'KOMMO_SUBDOMAIN': 'test',
            'KOMMO_LONG_LIVED_TOKEN': 'test',
            'GOOGLE_SERVICE_ACCOUNT_EMAIL': 'test@test.com',
            'GOOGLE_PRIVATE_KEY': 'test_key',
            'DEBUG': 'True'
        }
        
        for key, value in mock_vars.items():
            os.environ[key] = value
        
        from agente.core.agent import SDRAgent
        
        print("✅ Importação bem-sucedida!")
        
        # Try to create agent
        agent = SDRAgent()
        print("✅ SDRAgent inicializado com sucesso!")
        print(f"   - Agent name: {agent.name}")
        print("✅ CORREÇÃO DO PARÂMETRO debug FUNCIONOU!")
        
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
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa teste da correção do parâmetro debug"""
    print("🚀 Teste de Correção do Parâmetro debug")
    print("=" * 50)
    
    if test_agno_agent_initialization():
        print("\n🎉 CORREÇÃO DO PARÂMETRO debug CONCLUÍDA COM SUCESSO!")
        print("🔧 Problema original: Agent.__init__() got an unexpected keyword argument 'debug'")
        print("✅ Solução aplicada: Removido parâmetro 'debug=DEBUG' da inicialização do Agent")
        print("📝 Arquivo corrigido: agente/core/agent.py linha 265")
        print("\n🚀 O sistema agora pode ser iniciado sem erros de parâmetro debug!")
        return True
    else:
        print("\n⚠️  A correção não foi bem-sucedida.")
        return False

if __name__ == "__main__":
    main()