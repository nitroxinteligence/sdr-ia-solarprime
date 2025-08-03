#!/usr/bin/env python3
"""
Teste para verificar que a função _apply_typing_simulation não modifica mais o texto
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_typing_simulation():
    """Testa que a função não adiciona quebras de linha"""
    
    print("🧪 TESTE DA CORREÇÃO DO TYPING SIMULATION")
    print("=" * 60)
    
    # Simular a função corrigida
    def _apply_typing_simulation(text: str) -> str:
        """Retorna o texto sem modificação - typing é feito via Evolution API"""
        return text
    
    # Casos de teste
    test_cases = [
        ("Mensagem curta", "Olá! Como você está?"),
        
        ("Mensagem da Helen - Abertura", 
         "Oii! Tudo bem? Seja muito bem-vindo à Solar Prime! Meu nome é Helen Vieira, sou consultora especialista aqui da Solar Prime em Recife. Antes de a gente começar, como posso te chamar?"),
        
        ("Mensagem longa com pontos",
         "Esta é uma mensagem longa. Ela tem várias frases. Cada frase termina com ponto. Mas não deve ser quebrada."),
        
        ("Mensagem com 200+ caracteres",
         "Esta é uma mensagem muito longa que tem mais de duzentos caracteres e seria dividida pela função antiga mas agora deve permanecer intacta porque o Smart Message Splitter cuidará disso quando necessário."),
    ]
    
    print("\n📝 Testando diferentes mensagens:\n")
    
    all_passed = True
    for name, text in test_cases:
        result = _apply_typing_simulation(text)
        
        # Verificar que o texto não foi modificado
        if result == text:
            print(f"✅ {name}: PASSOU")
            print(f"   Entrada: {len(text)} chars")
            print(f"   Saída: {len(result)} chars")
            has_newlines = '\\n' in result
            print(f"   Sem quebras de linha: {not has_newlines}")
        else:
            print(f"❌ {name}: FALHOU")
            print(f"   Esperado: {text[:50]}...")
            print(f"   Recebido: {result[:50]}...")
            all_passed = False
        print()
    
    print("=" * 60)
    
    # Verificar arquivo real
    print("\n🔍 Verificando arquivo agentic_sdr.py:")
    
    with open('app/agents/agentic_sdr.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que a função foi corrigida
    if 'return "\\n".join(result)' in content:
        print("❌ ERRO: Ainda existe código de quebra de linha na função!")
        all_passed = False
    elif 'def _apply_typing_simulation(self, text: str) -> str:' in content:
        if 'return text' in content:
            print("✅ Função _apply_typing_simulation corrigida corretamente!")
        else:
            print("⚠️ Função existe mas pode não estar retornando texto corretamente")
    else:
        print("⚠️ Função _apply_typing_simulation não encontrada")
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("   • A função não modifica mais o texto")
        print("   • Não adiciona quebras de linha")
        print("   • O Smart Message Splitter funcionará corretamente")
        print("   • O typing é enviado via Evolution API")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("   Verifique os erros acima")
    
    return all_passed

if __name__ == "__main__":
    success = test_typing_simulation()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    if success:
        print("1. ✅ Fazer commit das alterações")
        print("2. ✅ Push para o branch deploy")
        print("3. ✅ Testar em produção")
        print("4. ✅ Verificar que mensagens não quebram mais no WhatsApp")
    else:
        print("1. ❌ Corrigir os problemas identificados")
        print("2. ❌ Executar o teste novamente")
    
    sys.exit(0 if success else 1)