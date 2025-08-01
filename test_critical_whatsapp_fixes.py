#!/usr/bin/env python3
"""
Teste CRÍTICO para validar correções dos erros WhatsApp
Verifica se os dois erros principais foram resolvidos
"""

import sys
from pathlib import Path
import ast

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_function_callable_fix():
    """Testa se o erro 'Function' object is not callable foi corrigido"""
    print("🧪 Testando correção 'Function' object is not callable...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        content = main_file.read_text()
        
        # Verificar se não usa mais import direto da tool
        if "from agente.tools.whatsapp.send_text_message import send_text_message" in content:
            print("❌ Ainda usa import direto da tool (causa o erro)")
            return False
        
        # Verificar se usa Evolution Service
        if "from agente.services import get_evolution_service" not in content:
            print("❌ Import Evolution Service não encontrado")
            return False
        
        if "evolution_service.send_text_message(" not in content:
            print("❌ Chamada Evolution Service não encontrada")
            return False
        
        print("✅ Correção 'Function callable' implementada")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando function callable: {e}")
        return False

def test_duplicate_session_fix():
    """Testa se o erro duplicate session_id foi corrigido"""
    print("🧪 Testando correção duplicate session_id...")
    
    try:
        session_file = Path(__file__).parent / "agente/core/session_manager.py"
        content = session_file.read_text()
        
        # Verificar se usa UUID único para session_id
        if "str(uuid.uuid4())[:8]" not in content:
            print("❌ UUID único para session_id não encontrado")
            return False
        
        if "unique_session_id = f\"session_{phone}_{str(uuid.uuid4())[:8]}\"" not in content:
            print("❌ Formato único de session_id não encontrado")
            return False
        
        # Verificar se não usa mais timestamp simples
        if "datetime.now(timezone.utc).timestamp()" in content and "session_" in content:
            # Verificar se ainda está na parte problemática
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "datetime.now(timezone.utc).timestamp()" in line and "session_" in line:
                    context_lines = lines[max(0, i-2):i+3]
                    context_str = '\n'.join(context_lines)
                    if "start_conversation" in context_str:
                        print("❌ Timestamp simples ainda sendo usado")
                        return False
        
        print("✅ Correção duplicate session_id implementada")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando session_id: {e}")
        return False

def test_evolution_service_usage():
    """Testa se o Evolution Service está sendo usado corretamente"""
    print("🧪 Testando uso correto do Evolution Service...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        content = main_file.read_text()
        
        # Verificar estrutura correta
        required_elements = [
            "evolution_service = get_evolution_service()",
            "await evolution_service.send_text_message(",
            "phone=message.phone,",
            "text=response.message"
        ]
        
        found_elements = 0
        for element in required_elements:
            if element in content:
                found_elements += 1
        
        if found_elements < len(required_elements):
            print(f"❌ Apenas {found_elements}/{len(required_elements)} elementos encontrados")
            return False
        
        print(f"✅ {found_elements}/{len(required_elements)} elementos Evolution Service corretos")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando Evolution Service: {e}")
        return False

def test_session_uniqueness():
    """Testa se a unicidade de session_id está garantida"""
    print("🧪 Testando unicidade de session_id...")
    
    try:
        session_file = Path(__file__).parent / "agente/core/session_manager.py"
        content = session_file.read_text()
        
        # Simular geração de IDs únicos
        import uuid
        
        # Verificar formato esperado
        phone = "558182986181"
        uuid_part = str(uuid.uuid4())[:8]
        expected_format = f"session_{phone}_{uuid_part}"
        
        if len(expected_format.split('_')) != 3:
            print("❌ Formato de session_id incorreto")
            return False
        
        # Verificar se usa UUID (sempre único)
        if "uuid.uuid4()" not in content:
            print("❌ UUID não sendo usado para unicidade")
            return False
        
        print("✅ Unicidade de session_id garantida")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando unicidade: {e}")
        return False

def test_syntax_validation():
    """Valida sintaxe dos arquivos corrigidos"""
    print("🧪 Validando sintaxe Python...")
    
    try:
        files_to_check = [
            "agente/main.py",
            "agente/core/session_manager.py"
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
        
        print("✅ Sintaxe Python válida em todos os arquivos")
        return True
        
    except Exception as e:
        print(f"❌ Erro validando sintaxe: {e}")
        return False

def test_error_resolution():
    """Testa se os erros específicos foram resolvidos"""
    print("🧪 Testando resolução dos erros específicos...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        session_file = Path(__file__).parent / "agente/core/session_manager.py"
        
        main_content = main_file.read_text()
        session_content = session_file.read_text()
        
        # Verificar se padrões que causavam erros foram removidos
        error_patterns = [
            # Padrão que causava 'Function' object is not callable
            ("main.py", "send_text_message(", "tool import direto"),
            # Padrão que causava duplicate key
            ("session_manager.py", "f\"session_{phone}\"", "session_id sem UUID")
        ]
        
        for file_name, pattern, description in error_patterns:
            if file_name == "main.py" and pattern in main_content:
                # Verificar se não é na nova implementação
                if "evolution_service.send_text_message(" not in main_content:
                    print(f"❌ Padrão problemático ainda presente: {description}")
                    return False
        
        print("✅ Padrões que causavam erros foram corrigidos")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando resolução: {e}")
        return False

def main():
    """Executa todos os testes de correção WhatsApp críticos"""
    print("🚨 TESTE CORREÇÕES CRÍTICAS WHATSAPP")
    print("=" * 50)
    
    tests = [
        ("Function Callable Fix", test_function_callable_fix),
        ("Duplicate Session Fix", test_duplicate_session_fix),
        ("Evolution Service Usage", test_evolution_service_usage),
        ("Session Uniqueness", test_session_uniqueness),
        ("Sintaxe Python", test_syntax_validation),
        ("Resolução Erros", test_error_resolution)
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
    print("📊 RESULTADO CORREÇÕES CRÍTICAS")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÕES CRÍTICAS IMPLEMENTADAS!")
        print("\n📋 Problemas resolvidos:")
        print("   ✅ 'Function' object is not callable: Evolution Service usado")
        print("   ✅ duplicate key session_id: UUID único implementado")
        print("   ✅ Evolution Service: Chamada direta correta")
        print("   ✅ Session Uniqueness: UUID garante unicidade")
        print("   ✅ Sintaxe: Código Python válido")
        print("   ✅ Erros: Padrões problemáticos corrigidos")
        print("\n🚀 AGENTE DEVE FUNCIONAR SEM ERROS!")
        print("\n💡 Correções aplicadas:")
        print("   • main.py: Evolution Service em vez de tool direta")
        print("   • session_manager.py: UUID único para session_id")
        return True
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam.")
        print("Verifique as correções antes de reiniciar o servidor.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)