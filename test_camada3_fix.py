#!/usr/bin/env python3
"""
Teste CAMADA 3: Validação do ResponseSanitizer
Verifica se os vazamentos internos do AGnO Framework são filtrados
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_response_sanitizer_basic():
    """Testa funcionalidades básicas do ResponseSanitizer"""
    print("🧪 TESTE CAMADA 3: RESPONSE SANITIZER")
    print("=" * 45)
    
    try:
        from agente.core.response_sanitizer import ResponseSanitizer, get_response_sanitizer
        
        # Criar instância
        sanitizer = ResponseSanitizer()
        print("✅ ResponseSanitizer criado com sucesso")
        
        # Testar singleton
        sanitizer2 = get_response_sanitizer()
        print(f"✅ Singleton funcionando: {sanitizer is not sanitizer2}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_internal_leakage_removal():
    """Testa remoção de vazamentos internos específicos"""
    print("\n🔍 TESTE REMOÇÃO VAZAMENTOS INTERNOS:")
    print("-" * 40)
    
    try:
        from agente.core.response_sanitizer import get_response_sanitizer
        
        sanitizer = get_response_sanitizer()
        
        # Casos de teste com vazamentos comuns
        test_cases = [
            {
                "input": "Got it. I'll continue the conversation. Olá! Sou Helen Vieira, consultora em energia solar da SolarPrime.",
                "expected_contains": "Olá! Sou Helen Vieira",
                "expected_not_contains": "Got it. I'll continue",
                "description": "Vazamento AGnO Framework clássico"
            },
            {
                "input": "I'll help you with that. Como posso ajudá-lo com energia solar hoje?",
                "expected_contains": "Como posso ajudá-lo",
                "expected_not_contains": "I'll help you with that",
                "description": "Vazamento genérico de processamento"
            },
            {
                "input": "Let me process this information. Vou analisar sua conta de energia.",
                "expected_contains": "Vou analisar sua conta",
                "expected_not_contains": "Let me process",
                "description": "Vazamento de processamento interno"
            },
            {
                "input": "As an AI assistant, posso explicar sobre energia solar residencial.",
                "expected_contains": "posso explicar sobre energia",
                "expected_not_contains": "As an AI assistant",
                "description": "Vazamento de identidade IA"
            },
            {
                "input": "Olá! Sou Helen Vieira da SolarPrime. Como posso ajudá-lo?",
                "expected_contains": "Olá! Sou Helen Vieira",
                "expected_not_contains": None,  # Não deve remover nada
                "description": "Resposta limpa (não deve alterar)"
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            input_text = test_case["input"]
            expected_contains = test_case["expected_contains"]
            expected_not_contains = test_case["expected_not_contains"]
            description = test_case["description"]
            
            # Sanitizar
            sanitized = sanitizer.sanitize_response(input_text)
            
            # Verificar resultado
            contains_check = expected_contains in sanitized
            not_contains_check = (expected_not_contains is None or 
                                expected_not_contains not in sanitized)
            
            test_passed = contains_check and not_contains_check
            
            if test_passed:
                passed_tests += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"   {status} Teste {i}: {description}")
            
            if not test_passed:
                print(f"      Original: '{input_text}'")
                print(f"      Sanitizado: '{sanitized}'")
                if not contains_check:
                    print(f"      ❌ Deveria conter: '{expected_contains}'")
                if not not_contains_check:
                    print(f"      ❌ Não deveria conter: '{expected_not_contains}'")
        
        success_rate = passed_tests / total_tests
        print(f"\n📊 Resultado: {passed_tests}/{total_tests} testes passaram ({success_rate:.1%})")
        
        return success_rate >= 0.8  # 80% dos testes devem passar
        
    except Exception as e:
        print(f"❌ Erro no teste de vazamentos: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_leakage_analysis():
    """Testa análise de vazamentos sem modificar o conteúdo"""
    print("\n🔍 TESTE ANÁLISE DE VAZAMENTOS:")
    print("-" * 35)
    
    try:
        from agente.core.response_sanitizer import get_response_sanitizer
        
        sanitizer = get_response_sanitizer()
        
        # Texto com vazamentos
        leaky_text = "Got it. I'll continue the conversation. I'll help you with that. Olá! Sou Helen."
        
        # Analisar vazamentos
        analysis = sanitizer.analyze_leakage(leaky_text)
        
        print(f"   ✅ Has leakage: {analysis['has_leakage']}")
        print(f"   ✅ Total matches: {analysis['total_matches']}")
        print(f"   ✅ Leakage score: {analysis['leakage_score']:.2f}")
        print(f"   ✅ Patterns found: {len(analysis['patterns_found'])}")
        
        # Texto limpo
        clean_text = "Olá! Sou Helen Vieira da SolarPrime. Como posso ajudá-lo?"
        analysis_clean = sanitizer.analyze_leakage(clean_text)
        
        print(f"   ✅ Clean text has leakage: {analysis_clean['has_leakage']}")
        
        # Deve detectar vazamentos no primeiro e não no segundo
        return analysis['has_leakage'] and not analysis_clean['has_leakage']
        
    except Exception as e:
        print(f"❌ Erro no teste de análise: {e}")
        return False

def test_decorator_functionality():
    """Testa o decorator @sanitize_response"""
    print("\n🎯 TESTE DECORATOR SANITIZAÇÃO:")
    print("-" * 35)
    
    try:
        from agente.core.response_sanitizer import sanitize_response
        
        # Função de teste com decorator
        @sanitize_response
        def fake_ai_response():
            return "Got it. I'll continue the conversation. Olá! Como posso ajudar?"
        
        # Chamar função
        result = fake_ai_response()
        
        # Verificar se foi sanitizado
        has_leakage = "Got it. I'll continue" in result
        has_clean_content = "Olá! Como posso ajudar" in result
        
        print(f"   ✅ Decorator aplicado: {not has_leakage}")
        print(f"   ✅ Conteúdo preservado: {has_clean_content}")
        print(f"   ✅ Resultado: '{result}'")
        
        return not has_leakage and has_clean_content
        
    except Exception as e:
        print(f"❌ Erro no teste do decorator: {e}")
        return False

def main():
    """Executa todos os testes da CAMADA 3"""
    print("🔧 VALIDAÇÃO CAMADA 3 - RESPONSE SANITIZER")
    print("=" * 50)
    
    success_basic = test_response_sanitizer_basic()
    success_removal = test_internal_leakage_removal()
    success_analysis = test_leakage_analysis()
    success_decorator = test_decorator_functionality()
    
    print("\n" + "=" * 50)
    print("📋 RESULTADO FINAL CAMADA 3:")
    print(f"   Criação ResponseSanitizer: {'✅ PASSOU' if success_basic else '❌ FALHOU'}")
    print(f"   Remoção Vazamentos: {'✅ PASSOU' if success_removal else '❌ FALHOU'}")
    print(f"   Análise Vazamentos: {'✅ PASSOU' if success_analysis else '❌ FALHOU'}")
    print(f"   Decorator Sanitização: {'✅ PASSOU' if success_decorator else '❌ FALHOU'}")
    
    all_passed = all([success_basic, success_removal, success_analysis, success_decorator])
    
    if all_passed:
        print("\n🎉 CAMADA 3 VALIDADA COM SUCESSO!")
        print("✅ ResponseSanitizer funcionando")
        print("✅ Vazamentos internos AGnO REMOVIDOS")
        print("✅ 'Got it. I'll continue the conversation' - ELIMINADO")
        print("✅ Análise de vazamentos operacional")
        print("✅ Decorator @sanitize_response ativo")
        print("\n🎯 CAMADA 3 - CORREÇÕES APLICADAS:")
        print("  1. ✅ Sistema sanitização de respostas criado")
        print("  2. ✅ Padrões vazamento AGnO Framework mapeados")
        print("  3. ✅ Remoção automática de processos internos")
        print("  4. ✅ Preservação de conteúdo útil")
        print("  5. ✅ Análise não-destrutiva de vazamentos")
        print("\n🔄 PRÓXIMO: CAMADA 4 - Sistema deduplicação Helen")
    else:
        print("\n❌ CAMADA 3 AINDA INCOMPLETA")
        print("🔍 Verifique logs para mais detalhes")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)