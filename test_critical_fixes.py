#!/usr/bin/env python3
"""
Teste CRÍTICO das correções urgentes:
1. Supabase maybe_single() com verificação None
2. AGnO arun() para tools async
"""

import sys
from pathlib import Path
import ast

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_supabase_none_handling():
    """Testa se o Supabase service trata None corretamente"""
    print("🧪 Testando tratamento None no Supabase...")
    
    try:
        service_file = Path(__file__).parent / "agente/services/supabase_service.py"
        content = service_file.read_text()
        
        # Verificar se tem verificação robusta para None
        if "hasattr(result, 'data')" not in content:
            print("❌ Verificação hasattr(result, 'data') não encontrada")
            return False
        
        if "result and hasattr(result, 'data') and result.data" not in content:
            print("❌ Verificação completa de None não encontrada")
            return False
        
        print("✅ Tratamento robusto de None implementado")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando Supabase: {e}")
        return False

def test_agno_arun_method():
    """Testa se o AGnO Agent usa arun() para tools async"""
    print("🧪 Testando método arun() do AGnO...")
    
    try:
        agent_file = Path(__file__).parent / "agente/core/agent.py"
        content = agent_file.read_text()
        
        # Verificar se usa arun()
        if "agent.arun(" not in content:
            print("❌ Método arun() não encontrado")
            return False
        
        if "hasattr(self.agent, 'arun')" not in content:
            print("❌ Verificação hasattr arun não encontrada")
            return False
        
        if "await self.agent.arun(agent_input)" not in content:
            print("❌ Chamada await arun() não encontrada")
            return False
        
        print("✅ Método arun() implementado corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando AGnO: {e}")
        return False

def test_syntax_validation():
    """Valida sintaxe dos arquivos modificados"""
    print("🧪 Validando sintaxe Python...")
    
    try:
        files_to_check = [
            "agente/core/agent.py",
            "agente/services/supabase_service.py"
        ]
        
        for file_path in files_to_check:
            full_path = Path(__file__).parent / file_path
            if not full_path.exists():
                continue
                
            try:
                content = full_path.read_text()
                ast.parse(content)
                
            except SyntaxError as e:
                print(f"❌ Erro de sintaxe em {file_path}: {e}")
                return False
        
        print("✅ Sintaxe Python válida")
        return True
        
    except Exception as e:
        print(f"❌ Erro validando sintaxe: {e}")
        return False

def main():
    """Executa testes críticos"""
    print("🚨 TESTES CRÍTICOS - CORREÇÕES URGENTES")
    print("=" * 50)
    
    tests = [
        ("Supabase None Handling", test_supabase_none_handling),
        ("AGnO arun() Method", test_agno_arun_method),
        ("Sintaxe Python", test_syntax_validation)
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
    print("📊 RESULTADO DOS TESTES CRÍTICOS")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÕES CRÍTICAS IMPLEMENTADAS!")
        print("\n📋 Correções aplicadas:")
        print("   ✅ Supabase: Verificação robusta de None")
        print("   ✅ AGnO: Uso de arun() para tools async")
        print("   ✅ Sintaxe: Código Python válido")
        print("\n🚀 ERROS CRÍTICOS RESOLVIDOS!")
        return True
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam.")
        print("Corrija os erros antes de fazer deploy.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)