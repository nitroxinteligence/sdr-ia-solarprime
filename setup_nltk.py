#!/usr/bin/env python3
"""
Script de configuração do NLTK
Garante que os dados necessários estejam disponíveis
"""
import os
import sys

def setup_nltk():
    """Configura NLTK e baixa dados necessários"""
    try:
        import nltk
        
        # Configurar diretório de dados
        nltk_data_dir = os.path.expanduser('~/nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir, exist_ok=True)
        
        # Adicionar diretório aos caminhos do NLTK
        if nltk_data_dir not in nltk.data.path:
            nltk.data.path.append(nltk_data_dir)
        
        print("🔧 Configurando NLTK...")
        
        # Verificar e baixar punkt tokenizer
        try:
            nltk.data.find('tokenizers/punkt')
            print("✅ Punkt tokenizer já está instalado")
        except LookupError:
            print("📥 Baixando punkt tokenizer...")
            nltk.download('punkt', quiet=False, download_dir=nltk_data_dir)
            print("✅ Punkt tokenizer instalado com sucesso")
        
        # Testar tokenização em português
        from nltk.tokenize import sent_tokenize
        test_text = "Olá! Como você está? Eu estou bem."
        sentences = sent_tokenize(test_text, language='portuguese')
        print(f"✅ Teste de tokenização: {len(sentences)} frases detectadas")
        print(f"   Frases: {sentences}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro: NLTK não está instalado. Execute: pip install nltk")
        print(f"   Detalhes: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao configurar NLTK: {e}")
        return False

if __name__ == "__main__":
    success = setup_nltk()
    sys.exit(0 if success else 1)