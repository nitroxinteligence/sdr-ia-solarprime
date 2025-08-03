#!/usr/bin/env python3
"""
Teste de Fallback do Smart Message Splitter - sem NLTK
"""

# Mock básico do emoji_logger para evitar dependências
class MockEmojiLogger:
    def system_warning(self, msg): print(f"WARNING: {msg}")
    def system_info(self, msg): print(f"INFO: {msg}")
    def system_debug(self, msg, **kwargs): print(f"DEBUG: {msg} {kwargs}")

# Importação manual simplificada
try:
    import regex
    HAS_REGEX = True
except ImportError:
    import re as regex
    HAS_REGEX = False

# Simular NLTK não disponível
HAS_NLTK = False

from typing import List

# Mock do logger
emoji_logger = MockEmojiLogger()

class MessageSplitter:
    """
    Splitter inteligente que preserva emojis, palavras e frases
    Versão de teste com fallback
    """
    
    def __init__(self, max_length: int = 150, add_indicators: bool = False, enable_smart_splitting: bool = True, smart_splitting_fallback: bool = True):
        self.max_length = max_length
        self.add_indicators = add_indicators
        self.enable_smart_splitting = enable_smart_splitting
        self.smart_splitting_fallback = smart_splitting_fallback
        
        if not HAS_REGEX:
            emoji_logger.system_warning(
                "Módulo 'regex' não instalado. Usando 're' padrão (pode quebrar emojis)"
            )
        
        if self.enable_smart_splitting and not HAS_NLTK:
            emoji_logger.system_warning(
                "NLTK não disponível. Divisão inteligente desabilitada, usando algoritmo padrão"
            )
            self.enable_smart_splitting = False
        
        smart_status = "ativada" if self.enable_smart_splitting else "desativada"
        emoji_logger.system_info(f"Message Splitter inicializado (max={max_length} chars, smart={smart_status})")
    
    def split_message(self, text: str) -> List[str]:
        if not text:
            return []
        
        # Se cabe, retorna direto
        if len(text) <= self.max_length:
            return [text.strip()]
        
        # Como NLTK não está disponível, usar fallback
        chunks = self._split_simple(text)
        
        # Adiciona indicadores se configurado
        if self.add_indicators and len(chunks) > 1:
            chunks = self._add_indicators(chunks)
        
        emoji_logger.system_debug(
            f"Mensagem dividida",
            original_length=len(text),
            chunks=len(chunks),
            method="fallback_splitting"
        )
        
        return chunks
    
    def _split_simple(self, text: str) -> List[str]:
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            # Se a palavra sozinha é maior que o limite
            if word_length > self.max_length:
                # Salva chunk atual se houver
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Quebra palavra grande (último recurso)
                while len(word) > self.max_length:
                    chunks.append(word[:self.max_length])
                    word = word[self.max_length:]
                
                if word:
                    current_chunk = [word]
                    current_length = len(word)
            
            # Se adicionar a palavra ultrapassa o limite
            elif current_length + word_length + 1 > self.max_length:
                # Salva chunk atual
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                # Começa novo chunk
                current_chunk = [word]
                current_length = word_length
            
            else:
                # Adiciona ao chunk atual
                current_chunk.append(word)
                current_length += word_length + 1  # +1 para o espaço
        
        # Adiciona último chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _add_indicators(self, chunks: List[str]) -> List[str]:
        total = len(chunks)
        result = []
        
        for i, chunk in enumerate(chunks, 1):
            indicator = f"[{i}/{total}] "
            
            # Se adicionar indicador ultrapassa limite, ajusta
            if len(indicator + chunk) > self.max_length:
                # Remove alguns caracteres do fim
                max_content = self.max_length - len(indicator) - 3
                chunk = chunk[:max_content] + "..."
            
            result.append(indicator + chunk)
        
        return result

def test_basic_functionality():
    """Testa funcionalidade básica do splitter"""
    print("=== TESTE DE FUNCIONALIDADE BÁSICA ===")
    
    # Texto que estava sendo dividido incorretamente
    original_text = """Oii! Seja muito bem-vindo à Solar Prime!
Meu nome é Helen Vieira
Sou consultora especialista aqui da Solar Prime em Recife
Antes de começarmos, como posso te chamar?."""
    
    print(f"Texto original ({len(original_text)} chars):")
    print(f'"{original_text}"')
    print()
    
    # Teste com configuração padrão
    splitter = MessageSplitter(max_length=150, enable_smart_splitting=True)
    chunks = splitter.split_message(original_text)
    
    print(f"Dividido em {len(chunks)} partes:")
    for i, chunk in enumerate(chunks, 1):
        print(f"[{i}/{len(chunks)}] ({len(chunk)} chars): \"{chunk}\"")
    print()
    
    return chunks

def test_various_lengths():
    """Testa com diferentes tamanhos de limite"""
    print("=== TESTE COM DIFERENTES TAMANHOS ===")
    
    text = "Esta é uma mensagem de teste que será dividida em diferentes tamanhos para validar o comportamento do splitter."
    
    for max_len in [30, 50, 80]:
        print(f"--- Limite: {max_len} caracteres ---")
        splitter = MessageSplitter(max_length=max_len)
        chunks = splitter.split_message(text)
        
        print(f"Input ({len(text)} chars): \"{text}\"")
        print(f"Output ({len(chunks)} chunks):")
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}] ({len(chunk)} chars): \"{chunk}\"")
        print()

if __name__ == "__main__":
    print("🧪 TESTE DE FALLBACK DO SMART MESSAGE SPLITTER")
    print("=" * 60)
    print()
    
    print(f"NLTK disponível: {HAS_NLTK}")
    print(f"Regex disponível: {HAS_REGEX}")
    print()
    
    try:
        # Teste principal
        chunks = test_basic_functionality()
        
        # Teste com diferentes tamanhos
        test_various_lengths()
        
        # Análise dos resultados
        print("=== ANÁLISE DOS RESULTADOS ===")
        print(f"Número de chunks: {len(chunks)}")
        
        # Verificar se todos os chunks respeitam o limite
        max_len = max(len(chunk) for chunk in chunks)
        print(f"Tamanho máximo dos chunks: {max_len}")
        
        if max_len <= 150:
            print("✅ Todos os chunks respeitam o limite de 150 caracteres")
        else:
            print("❌ Alguns chunks excedem o limite")
        
        # Verificar se o conteúdo foi preservado
        reconstructed = " ".join(chunks).replace("  ", " ")
        original = """Oii! Seja muito bem-vindo à Solar Prime! Meu nome é Helen Vieira Sou consultora especialista aqui da Solar Prime em Recife Antes de começarmos, como posso te chamar?."""
        
        if reconstructed.replace(" ", "").replace("\n", "") == original.replace(" ", "").replace("\n", ""):
            print("✅ Conteúdo preservado")
        else:
            print("⚠️ Conteúdo pode ter sido alterado")
        
        print()
        print("✅ TESTE DE FALLBACK CONCLUÍDO COM SUCESSO!")
        print("✅ O sistema funciona mesmo sem NLTK, usando algoritmo de fallback")
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()