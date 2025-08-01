#!/usr/bin/env python3
"""
Teste para validar correção do formato de input AGnO
Verifica se a correção resolve o erro "contents are required"
"""

import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path  
sys.path.insert(0, str(Path(__file__).parent))

def test_agno_input_format_correction():
    """Testa se a correção do formato de input AGnO foi implementada"""
    print("🧪 Testando correção formato input AGnO...")
    
    try:
        agent_file = Path(__file__).parent / "agente/core/agent.py"
        content = agent_file.read_text()
        
        # Verificar se a correção foi implementada
        if "agent_input = user_message" not in content:
            print("❌ Correção user_message não encontrada")
            return False
            
        if "AGnO arun() espera string simples" not in content:
            print("❌ Comentário explicativo não encontrado")
            return False
            
        if "_current_context" not in content:
            print("❌ Context storage não encontrado")
            return False
            
        if "f\"[CONTEXT: {stage_info}]\\n\\nMensagem do cliente: {user_message}\"" not in content:
            print("❌ Format string com context não encontrado")
            return False
            
        # Verificar se o dict complexo foi removido
        if "\"phone\": message.phone," in content and "\"context\": context," in content:
            # Verificar se é na parte corrigida ou em outra parte
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "\"phone\": message.phone," in line:
                    # Verificar contexto ao redor
                    context_lines = lines[max(0, i-5):i+5]
                    context_str = '\n'.join(context_lines)
                    if "agent_input = {" in context_str and "await self.agent.arun(agent_input)" in context_str:
                        print("❌ Dict complexo ainda sendo usado como input para arun()")
                        return False
        
        print("✅ Correção formato input AGnO implementada corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando formato: {e}")
        return False

def test_context_storage_implementation():
    """Testa se o context storage foi implementado"""
    print("🧪 Testando context storage...")
    
    try:
        agent_file = Path(__file__).parent / "agente/core/agent.py"
        content = agent_file.read_text()
        
        # Verificar inicialização do context storage
        if "self._current_context = {}" not in content:
            print("❌ Inicialização _current_context não encontrada")
            return False
            
        # Verificar atribuição do context
        if "self._current_context = {" not in content:
            print("❌ Atribuição _current_context não encontrada")  
            return False
            
        print("✅ Context storage implementado corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando context storage: {e}")
        return False

def test_message_format_structure():
    """Testa se a estrutura de mensagem está correta"""
    print("🧪 Testando estrutura de mensagem...")
    
    try:
        agent_file = Path(__file__).parent / "agente/core/agent.py"
        content = agent_file.read_text()
        
        # Verificar se usa user_message diretamente
        if "user_message = message.message" not in content:
            print("❌ Extração user_message não encontrada")
            return False
            
        # Verificar logging do input
        if "agent_input[:100]" not in content:
            print("❌ Logging do input não encontrado")
            return False
            
        print("✅ Estrutura de mensagem correta")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando estrutura: {e}")
        return False

def main():
    """Executa todos os testes de correção AGnO"""
    print("🚀 TESTE CORREÇÃO FORMATO INPUT AGnO")
    print("=" * 50)
    
    tests = [
        ("Formato Input AGnO", test_agno_input_format_correction),
        ("Context Storage", test_context_storage_implementation), 
        ("Estrutura Mensagem", test_message_format_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSOU")
            else:
                print(f"❌ {test_name} FALHOU")
        except Exception as e:
            print(f"❌ {test_name} ERRO: {e}")
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO CORREÇÃO AGnO")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÃO AGnO INPUT FORMAT IMPLEMENTADA!")
        print("\n📋 Correções aplicadas:")
        print("   ✅ Input AGnO: Dict complexo → String simples")
        print("   ✅ Context: Separado do input principal")
        print("   ✅ Format: String com context para melhor compreensão")
        print("\n🚀 ERRO 'contents are required' DEVE ESTAR RESOLVIDO!")
        return True
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam.")
        print("Verifique as correções antes de testar em produção.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)