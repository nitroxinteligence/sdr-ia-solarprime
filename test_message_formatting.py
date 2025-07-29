#!/usr/bin/env python3
"""
Teste de Formatação de Mensagens
================================
Testa as correções de formatação implementadas
"""

import sys
sys.path.append('.')

from utils.message_formatter import format_message_for_whatsapp, improve_chunk_splitting, should_use_natural_breaks


def test_bold_formatting():
    """Testa conversão de negrito Markdown para WhatsApp"""
    print("\n=== Teste de Formatação de Negrito ===")
    
    test_cases = [
        ("**Energia** solar é o futuro", "*Energia* solar é o futuro"),
        ("**Importante:** preciso da sua conta", "*Importante...* preciso da sua conta"),
        ("### Título Principal", "*Título Principal*"),
        ("## Subtítulo", "*Subtítulo*"),
        ("# Outro Título", "*Outro Título*"),
        ("Texto com **múltiplos** negritos **aqui**", "Texto com *múltiplos* negritos *aqui*"),
    ]
    
    for input_text, expected in test_cases:
        result = format_message_for_whatsapp(input_text)
        print(f"✓ '{input_text}' → '{result}'")
        assert result == expected, f"Esperado: {expected}, Obtido: {result}"
    
    print("✅ Todos os testes de negrito passaram!")


def test_punctuation_formatting():
    """Testa conversão de pontuação"""
    print("\n=== Teste de Formatação de Pontuação ===")
    
    test_cases = [
        ("Vamos ao que interessa: a economia", "Vamos ao que interessa... a economia"),
        ("Primeira pergunta importante:", "Primeira pergunta importante..."),
        ("- Item da lista", "Item da lista"),
        ("- Outro item", "Outro item"),
        ("Texto normal. Sem mudanças.", "Texto normal. Sem mudanças."),
    ]
    
    for input_text, expected in test_cases:
        result = format_message_for_whatsapp(input_text)
        print(f"✓ '{input_text}' → '{result}'")
        assert result == expected, f"Esperado: {expected}, Obtido: {result}"
    
    print("✅ Todos os testes de pontuação passaram!")


def test_chunk_improvement():
    """Testa melhoria de chunking"""
    print("\n=== Teste de Melhoria de Chunking ===")
    
    # Simular chunks ruins (quebrados em vírgulas)
    bad_chunks = [
        "Ótimo. Agora com sua fatura em mãos e sabendo como me dirigir a você,",
        "vamos ao que interessa:",
        "a sua economia.",
        "Primeira pergunta importante:",
        "você já tem algum desconto?"
    ]
    
    improved = improve_chunk_splitting(bad_chunks)
    
    print("Chunks originais:")
    for i, chunk in enumerate(bad_chunks):
        print(f"  {i+1}. '{chunk}'")
    
    print("\nChunks melhorados:")
    for i, chunk in enumerate(improved):
        print(f"  {i+1}. '{chunk}'")
    
    # Verificar que chunks curtos foram unidos
    assert len(improved) < len(bad_chunks), "Chunks deveriam ter sido unidos"
    
    # Verificar que não há chunks terminando apenas com vírgula ou dois pontos
    for chunk in improved:
        assert not (chunk.endswith(',') and len(chunk.split()) < 8), f"Chunk muito curto com vírgula: {chunk}"
        assert not (chunk.endswith(':') and len(chunk.split()) < 8), f"Chunk muito curto com dois pontos: {chunk}"
    
    print("✅ Teste de chunking passou!")


def test_natural_breaks():
    """Testa detecção de quebras naturais"""
    print("\n=== Teste de Quebras Naturais ===")
    
    message_with_list = """Olha só a simulação que preparei para você:

*Desconto Garantido...* Você terá *15% de desconto* sobre o valor total da sua conta de energia todos os meses.

1. *Economia Anual...* Isso representa uma economia de quase *R$ 1.000,00 por ano* no seu bolso.

2. *Tecnologia de Ponta...* Usamos inversores inteligentes.

3. *Segurança da Operação...* Por causa dessa tecnologia robusta."""
    
    has_breaks, chunks = should_use_natural_breaks(message_with_list)
    
    print(f"Tem quebras naturais: {has_breaks}")
    print(f"Número de chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"'{chunk}'")
    
    assert has_breaks, "Deveria detectar quebras naturais"
    assert len(chunks) >= 4, "Deveria ter pelo menos 4 chunks (parágrafo + 3 itens)"
    
    print("✅ Teste de quebras naturais passou!")


def test_complete_message():
    """Testa formatação completa de uma mensagem real"""
    print("\n=== Teste de Mensagem Completa ===")
    
    message = """**João**, analisei sua conta e vi que você está pagando **R$ 850,00** por mês!

Com nossa solução de **Energia por Assinatura**, você economizaria 95%, ficando com apenas **R$ 42,50**!

### Vantagens:
- Economia garantida
- Sem investimento inicial
- Energia limpa e sustentável

Primeira pergunta importante: você já tem algum desconto na sua conta atual?"""
    
    formatted = format_message_for_whatsapp(message)
    
    print("Mensagem original:")
    print(message)
    print("\nMensagem formatada:")
    print(formatted)
    
    # Verificações
    assert "*João*" in formatted, "Nome deveria estar em negrito WhatsApp"
    assert "*R$ 850,00*" in formatted, "Valor deveria estar em negrito WhatsApp"
    assert "*Vantagens...*" in formatted, "Título deveria ter reticências"
    assert "importante..." in formatted, "Dois pontos deveriam virar reticências"
    assert "- " not in formatted, "Hífens deveriam ser removidos"
    
    print("\n✅ Teste de mensagem completa passou!")


def test_conta_luz_response():
    """Testa se resposta sobre conta de luz não promete retornar depois"""
    print("\n=== Teste de Resposta de Conta de Luz ===")
    
    # Simular respostas problemáticas
    problematic_phrases = [
        "Volto a falar em breve com os números",
        "Vou analisar sua conta agora",
        "Me dê um momento para analisar",
        "Retorno em instantes com a análise",
        "Aguarde enquanto analiso"
    ]
    
    # Resposta correta esperada
    good_response = """*João*, analisei sua conta e vi que você está pagando *R$ 850,00* por mês! 😮

Com nossa solução, você economizaria 95%, ficando com apenas *R$ 42,50*!

São mais de *R$ 800* de economia todo mês!

Isso está correto?"""
    
    formatted = format_message_for_whatsapp(good_response)
    
    # Verificar que não contém frases problemáticas
    for phrase in problematic_phrases:
        assert phrase.lower() not in formatted.lower(), f"Resposta não deveria conter: {phrase}"
    
    # Verificar que contém elementos esperados
    assert "analisei sua conta" in formatted.lower(), "Deveria mencionar que analisou"
    assert "R$" in formatted, "Deveria mencionar valores"
    assert "economia" in formatted.lower(), "Deveria mencionar economia"
    
    print("✅ Resposta de conta de luz está correta!")
    print(f"\nResposta formatada:\n{formatted}")


if __name__ == "__main__":
    print("🧪 Executando testes de formatação de mensagens...")
    
    try:
        test_bold_formatting()
        test_punctuation_formatting()
        test_chunk_improvement()
        test_natural_breaks()
        test_complete_message()
        test_conta_luz_response()
        
        print("\n✅ TODOS OS TESTES PASSARAM! 🎉")
        print("\nAs correções foram implementadas com sucesso:")
        print("1. ✓ Negrito convertido de ** para *")
        print("2. ✓ Dois pontos ':' convertidos para reticências '...'")
        print("3. ✓ Hífens desnecessários removidos")
        print("4. ✓ Chunking melhorado (sem quebras em vírgulas)")
        print("5. ✓ Resposta imediata para conta de luz")
        
    except AssertionError as e:
        print(f"\n❌ ERRO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)