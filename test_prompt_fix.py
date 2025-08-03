#!/usr/bin/env python3
"""
Teste para verificar que o prompt não adiciona quebras de linha desnecessárias
"""

import re

def test_prompt_formatting():
    """Verifica se o prompt está configurado corretamente"""
    
    # Ler o arquivo do prompt
    with open('app/prompts/prompt-agente.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Verificando prompt para problemas de formatação...")
    print("=" * 60)
    
    issues_found = []
    
    # Verificar se há instruções para quebrar mensagens
    problematic_patterns = [
        (r"quebra.*mensagens", "Instrução para quebrar mensagens"),
        (r"quebra.*pensamentos", "Instrução para quebrar pensamentos"),
        (r"média.*3-7.*palavras", "Instrução para usar poucas palavras"),
        (r"message_chunks.*shorter", "Configuração para mensagens curtas"),
        (r"\[pausa.*\]", "Pausas entre mensagens"),
        (r'\"[^\"]+\"\n\[pausa', "Mensagens com pausas"),
    ]
    
    for pattern, description in problematic_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues_found.append((description, len(matches)))
    
    # Verificar se há instruções corretas
    good_patterns = [
        (r"NUNCA.*quebr.*mensagens.*desnecessariamente", "Instrução para NÃO quebrar"),
        (r"mensagens.*fluidas.*completas", "Instrução para mensagens completas"),
        (r"consolidar.*pensamentos", "Instrução para consolidar"),
        (r"frases.*completas.*coesas", "Instrução para frases coesas"),
        (r"NÃO.*adicionar.*quebras.*linha", "Instrução contra quebras de linha"),
    ]
    
    good_found = []
    for pattern, description in good_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            good_found.append(description)
    
    # Relatório
    print("✅ INSTRUÇÕES CORRETAS ENCONTRADAS:")
    for instruction in good_found:
        print(f"  • {instruction}")
    
    if issues_found:
        print("\n⚠️ POSSÍVEIS PROBLEMAS ENCONTRADOS:")
        for issue, count in issues_found:
            print(f"  • {issue}: {count} ocorrência(s)")
    else:
        print("\n✅ Nenhum problema de formatação encontrado!")
    
    print("\n" + "=" * 60)
    
    # Verificar exemplos específicos
    print("\n📝 VERIFICANDO EXEMPLOS NO PROMPT:")
    
    # Procurar por exemplos com mensagens consolidadas
    if '"Oii! Seja muito bem-vindo à Solar Prime! Meu nome é Helen Vieira.' in content:
        print("✅ Exemplo de abertura consolidada encontrado")
    else:
        print("⚠️ Exemplo de abertura pode estar quebrado")
    
    # Verificar se há exemplo incorreto marcado
    if 'Exemplo INCORRETO:' in content:
        print("✅ Exemplo de formatação incorreta está marcado")
    
    # Verificar regra crítica no início
    if 'REGRA CRÍTICA DE FORMATAÇÃO' in content:
        print("✅ Seção de regra crítica de formatação presente")
    
    print("\n" + "=" * 60)
    print("📊 RESUMO:")
    
    if not issues_found and good_found:
        print("✅ Prompt está corretamente configurado para NÃO quebrar mensagens!")
        print("   O Message Splitter cuidará da divisão quando necessário.")
        return True
    else:
        print("⚠️ Ainda existem instruções que podem causar quebra de mensagens.")
        print("   Revise o prompt para remover todas as referências a quebra de texto.")
        return False

if __name__ == "__main__":
    print("\n🧪 TESTE DO PROMPT PARA CORREÇÃO DE QUEBRA DE MENSAGENS")
    print("=" * 60)
    
    success = test_prompt_formatting()
    
    if success:
        print("\n✅ TESTE PASSOU! O prompt está configurado corretamente.")
        print("   As mensagens serão enviadas de forma consolidada.")
        print("   O Smart Message Splitter dividirá apenas quando necessário.")
    else:
        print("\n❌ TESTE FALHOU! Ainda há problemas no prompt.")
        print("   Corrija as instruções problemáticas identificadas acima.")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Fazer commit das alterações")
    print("2. Fazer push para o branch deploy")
    print("3. Testar em produção com uma conversa real")
    print("4. Verificar que as mensagens aparecem consolidadas no WhatsApp")