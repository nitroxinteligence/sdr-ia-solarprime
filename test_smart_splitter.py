#!/usr/bin/env python3
"""
Teste do Smart Message Splitter - Validação das melhorias implementadas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.message_splitter import MessageSplitter

def test_original_problem():
    """Testa o exemplo problemático original do usuário"""
    print("=== TESTE DO PROBLEMA ORIGINAL ===")
    
    # Texto que estava sendo dividido incorretamente
    original_text = """Oii! Seja muito bem-vindo à Solar Prime!
Meu nome é Helen Vieira
Sou consultora especialista aqui da Solar Prime em Recife
Antes de começarmos, como posso te chamar?."""
    
    print(f"Texto original ({len(original_text)} chars):")
    print(f'"{original_text}"')
    print()
    
    # Teste com Smart Splitting ativado
    print("--- Smart Splitting ATIVADO ---")
    smart_splitter = MessageSplitter(max_length=150, enable_smart_splitting=True)
    smart_chunks = smart_splitter.split_message(original_text)
    
    print(f"Dividido em {len(smart_chunks)} partes:")
    for i, chunk in enumerate(smart_chunks, 1):
        print(f"[{i}/{len(smart_chunks)}] ({len(chunk)} chars): \"{chunk}\"")
    print()
    
    # Teste com Smart Splitting desativado (algoritmo original)
    print("--- Smart Splitting DESATIVADO (Original) ---")
    original_splitter = MessageSplitter(max_length=150, enable_smart_splitting=False)
    original_chunks = original_splitter.split_message(original_text)
    
    print(f"Dividido em {len(original_chunks)} partes:")
    for i, chunk in enumerate(original_chunks, 1):
        print(f"[{i}/{len(original_chunks)}] ({len(chunk)} chars): \"{chunk}\"")
    print()
    
    return smart_chunks, original_chunks

def test_various_scenarios():
    """Testa diversos cenários para validar robustez"""
    print("=== TESTE DE CENÁRIOS DIVERSOS ===")
    
    scenarios = [
        ("Texto curto que cabe", "Oi! Tudo bem?"),
        ("Frase única longa", "Esta é uma frase muito longa que precisa ser dividida mas deveria manter sua integridade como uma unidade semântica completa e coerente."),
        ("Múltiplas frases", "Primeira frase. Segunda frase muito longa que pode precisar de divisão. Terceira frase curta. Quarta frase final."),
        ("Com quebras de linha", "Linha 1\nLinha 2\nLinha 3 mais longa\nLinha 4"),
        ("Com emojis", "Olá! 😊 Como você está hoje? 🌟 Espero que muito bem! 🎉"),
    ]
    
    splitter = MessageSplitter(max_length=80, enable_smart_splitting=True)
    
    for scenario_name, text in scenarios:
        print(f"--- {scenario_name.upper()} ---")
        print(f"Input ({len(text)} chars): \"{text}\"")
        
        chunks = splitter.split_message(text)
        print(f"Output ({len(chunks)} chunks):")
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}] ({len(chunk)} chars): \"{chunk}\"")
        print()

def test_fallback_behavior():
    """Testa comportamento de fallback quando NLTK não está disponível"""
    print("=== TESTE DE FALLBACK ===")
    
    # Simular falha do NLTK
    original_text = "Primeira frase. Segunda frase longa que precisa divisão. Terceira frase."
    
    print("Testando fallback quando smart splitting falha...")
    splitter = MessageSplitter(max_length=50, enable_smart_splitting=True, smart_splitting_fallback=True)
    
    # Forçar uso do fallback simulando erro
    chunks = splitter._split_with_regex(original_text)
    print(f"Fallback result ({len(chunks)} chunks):")
    for i, chunk in enumerate(chunks, 1):
        print(f"  [{i}] ({len(chunk)} chars): \"{chunk}\"")

if __name__ == "__main__":
    print("🧪 TESTE DO SMART MESSAGE SPLITTER")
    print("=" * 50)
    print()
    
    try:
        # Teste principal
        smart_chunks, original_chunks = test_original_problem()
        
        # Análise dos resultados
        print("=== ANÁLISE DOS RESULTADOS ===")
        print(f"Smart Splitting: {len(smart_chunks)} chunks")
        print(f"Original: {len(original_chunks)} chunks")
        
        if len(smart_chunks) <= len(original_chunks):
            print("✅ Smart splitting produz menos ou igual número de chunks")
        else:
            print("⚠️ Smart splitting produz mais chunks")
        
        # Verificar se preserva frases completas
        smart_text = " ".join(smart_chunks)
        original_problem_text = """Oii! Seja muito bem-vindo à Solar Prime!
Meu nome é Helen Vieira
Sou consultora especialista aqui da Solar Prime em Recife
Antes de começarmos, como posso te chamar?."""
        
        if smart_text.replace(" ", "").replace("\n", "") == original_problem_text.replace(" ", "").replace("\n", ""):
            print("✅ Conteúdo preservado integralmente")
        else:
            print("❌ Conteúdo não preservado")
        
        print()
        
        # Testes adicionais
        test_various_scenarios()
        test_fallback_behavior()
        
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()