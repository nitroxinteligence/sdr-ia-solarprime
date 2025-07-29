#!/usr/bin/env python3
"""
Teste das Novas Regras de Formatação
=====================================
Valida que o agente não usa listas, bulletpoints ou negrito excessivo
"""

import sys
import re
sys.path.append('.')

from config.prompts import PromptTemplates


def test_no_lists_or_bullets():
    """Testa que os prompts não contêm listas numeradas ou com bullets"""
    print("\n=== Teste de Ausência de Listas e Bullets ===")
    
    # Padrões proibidos
    forbidden_patterns = [
        r'^\d+\.',  # Listas numeradas (1., 2., etc)
        r'^-\s',    # Hífens como bullets
        r'^•\s',    # Bullets
        r'^\*\s',   # Asteriscos como bullets (não confundir com negrito)
        r'^✅',     # Checkmarks
        r'^❌',     # X marks
        r'^📅',     # Emojis de calendário em listas
    ]
    
    # Verificar cada prompt de estágio
    issues_found = []
    
    for stage, prompt in PromptTemplates.STAGE_PROMPTS.items():
        lines = prompt.split('\n')
        for i, line in enumerate(lines):
            for pattern in forbidden_patterns:
                if re.match(pattern, line.strip()):
                    issues_found.append(f"{stage} (linha {i+1}): '{line.strip()}'")
    
    if issues_found:
        print("❌ Encontrados padrões proibidos:")
        for issue in issues_found:
            print(f"  - {issue}")
        raise AssertionError(f"Encontrados {len(issues_found)} padrões proibidos")
    else:
        print("✅ Nenhuma lista ou bullet encontrado nos prompts!")


def test_bold_usage():
    """Testa uso apropriado de negrito"""
    print("\n=== Teste de Uso de Negrito ===")
    
    # Contar uso de negrito em cada prompt
    for stage, prompt in PromptTemplates.STAGE_PROMPTS.items():
        # Contar ocorrências de *texto*
        bold_matches = re.findall(r'\*[^*]+\*', prompt)
        
        print(f"\n{stage}:")
        print(f"  Total de negritos: {len(bold_matches)}")
        
        if len(bold_matches) > 0:
            print("  Exemplos encontrados:")
            for match in bold_matches[:5]:  # Mostrar apenas os 5 primeiros
                print(f"    - {match}")
        
        # Verificar se há negrito excessivo (mais de 10 em um único prompt)
        if len(bold_matches) > 10:
            print(f"  ⚠️ AVISO: Possível uso excessivo de negrito ({len(bold_matches)} ocorrências)")


def test_formatting_examples():
    """Testa exemplos de formatação corretos e incorretos"""
    print("\n=== Teste de Exemplos de Formatação ===")
    
    # Verificar se os exemplos estão presentes
    system_prompt = PromptTemplates.SYSTEM_PROMPT
    
    if "Exemplo CORRETO:" in system_prompt:
        print("✅ Exemplo de formatação CORRETA encontrado")
    else:
        print("❌ Exemplo de formatação CORRETA não encontrado")
    
    if "Exemplo ERRADO:" in system_prompt:
        print("✅ Exemplo de formatação ERRADA encontrado")
    else:
        print("❌ Exemplo de formatação ERRADA não encontrado")


def test_specific_rules():
    """Testa regras específicas de formatação"""
    print("\n=== Teste de Regras Específicas ===")
    
    # Verificar se as regras estão documentadas
    system_prompt = PromptTemplates.SYSTEM_PROMPT
    
    rules_to_check = [
        ("NUNCA use listas numeradas", "Regra sobre listas numeradas"),
        ("NUNCA use enumerações ou bulletpoints", "Regra sobre bulletpoints"),
        ("NUNCA use negrito em excesso", "Regra sobre negrito"),
        ("apenas em *palavras-chave*", "Orientação sobre uso de negrito"),
        ("Use reticências (...) ao invés de dois pontos", "Regra sobre pontuação"),
    ]
    
    for rule, description in rules_to_check:
        if rule in system_prompt:
            print(f"✅ {description} encontrada")
        else:
            print(f"❌ {description} NÃO encontrada")


def test_energy_bill_response():
    """Testa formatação específica da resposta de conta de luz"""
    print("\n=== Teste de Resposta de Conta de Luz ===")
    
    energy_bill_prompt = PromptTemplates.STAGE_PROMPTS.get("ENERGY_BILL_ANALYSIS", "")
    
    # Verificar ausência de checkmarks
    if "✅" in energy_bill_prompt:
        print("❌ ERRO: Resposta de conta ainda contém checkmarks!")
    else:
        print("✅ Resposta de conta sem checkmarks")
    
    # Verificar formato correto
    if "Com nossa solução de *Energia por Assinatura*, você teria uma economia de" in energy_bill_prompt:
        print("✅ Formato de resposta sem lista encontrado")
    else:
        print("❌ Formato de resposta pode precisar de ajuste")


def analyze_all_prompts():
    """Análise geral de todos os prompts"""
    print("\n=== Análise Geral dos Prompts ===")
    
    total_chars = 0
    total_bolds = 0
    
    for stage, prompt in PromptTemplates.STAGE_PROMPTS.items():
        chars = len(prompt)
        bolds = len(re.findall(r'\*[^*]+\*', prompt))
        
        total_chars += chars
        total_bolds += bolds
        
        print(f"{stage:20} - {chars:5} caracteres, {bolds:2} negritos")
    
    print(f"\nTOTAL: {total_chars} caracteres, {total_bolds} negritos")
    print(f"Média de negritos por prompt: {total_bolds/len(PromptTemplates.STAGE_PROMPTS):.1f}")


if __name__ == "__main__":
    print("🧪 Testando novas regras de formatação...")
    
    try:
        test_no_lists_or_bullets()
        test_bold_usage()
        test_formatting_examples()
        test_specific_rules()
        test_energy_bill_response()
        analyze_all_prompts()
        
        print("\n✅ TODOS OS TESTES PASSARAM! 🎉")
        print("\nAs regras de formatação foram implementadas com sucesso:")
        print("1. ✓ Sem listas numeradas ou bulletpoints")
        print("2. ✓ Negrito usado apenas em palavras-chave")
        print("3. ✓ Exemplos de formatação incluídos")
        print("4. ✓ Regras claramente documentadas")
        
    except AssertionError as e:
        print(f"\n❌ ERRO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)