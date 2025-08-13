#\!/usr/bin/env python3
"""
Setup NLTK - Baixa recursos necessários para divisão inteligente
"""
import nltk
import os
import sys

def setup_nltk():
    """Configura NLTK com todos os recursos necessários"""
    
    print("🔧 Configurando NLTK para divisão inteligente de mensagens...")
    
    # Criar diretório de dados se não existir
    nltk_data_dir = os.path.expanduser('~/nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir, exist_ok=True)
        print(f"✅ Diretório criado: {nltk_data_dir}")
    
    # Adicionar ao path do NLTK
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.append(nltk_data_dir)
    
    # Lista de recursos necessários
    resources = [
        'punkt',        # Tokenizador de sentenças original
        'punkt_tab',    # Nova versão do tokenizador
    ]
    
    # Baixar recursos
    for resource in resources:
        try:
            # Verificar se já existe
            try:
                if resource == 'punkt_tab':
                    nltk.data.find('tokenizers/punkt_tab')
                else:
                    nltk.data.find(f'tokenizers/{resource}')
                print(f"✅ {resource} já instalado")
            except LookupError:
                # Baixar se não existir
                print(f"📥 Baixando {resource}...")
                nltk.download(resource, download_dir=nltk_data_dir, quiet=False)
                print(f"✅ {resource} instalado com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao instalar {resource}: {e}")
            # Continuar com próximo recurso
    
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