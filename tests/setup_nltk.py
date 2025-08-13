#\!/usr/bin/env python3
"""
Setup NLTK - Baixa recursos necessários para divisão inteligente
"""
import nltk
import os
import sys

def setup_nltk():
    """Configura NLTK com recursos necessários"""
    
    print("🔧 Configurando NLTK para divisão inteligente de mensagens...")
    
    # Baixar apenas punkt padrão (mais estável)
    try:
        # Verificar se punkt já existe
        try:
            nltk.data.find('tokenizers/punkt')
            print("✅ punkt já instalado")
        except LookupError:
            # Baixar se não existir
            print("📥 Baixando punkt...")
            nltk.download('punkt', quiet=False)
            print("✅ punkt instalado com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao instalar punkt: {e}")
        return False
    
    # Verificar instalação
    print("\n🔍 Verificando instalação...")
    try:
        from nltk.tokenize import sent_tokenize
        # Testar tokenização em português
        test_text = "Olá\! Como vai? Estou testando o NLTK."
        sentences = sent_tokenize(test_text, language='portuguese')
        print(f"✅ NLTK funcionando\! Teste: {len(sentences)} sentenças detectadas")
        print(f"   Sentenças: {sentences}")
        return True
    except Exception as e:
        print(f"❌ Erro ao testar NLTK: {e}")
        return False

if __name__ == "__main__":
    success = setup_nltk()
    if success:
        print("\n✅ NLTK configurado com sucesso\!")
        print("💡 O Message Splitter agora pode usar divisão inteligente por sentenças")
        sys.exit(0)
    else:
        print("\n⚠️ NLTK configurado parcialmente")
        print("💡 O Message Splitter funcionará com algoritmo de fallback")
        sys.exit(1)