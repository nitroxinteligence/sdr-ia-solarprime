#!/usr/bin/env python3
"""
Teste simples do Smart Message Splitter - sem dependências complexas
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

# Importar NLTK para divisão inteligente por frases
try:
    from nltk.tokenize import sent_tokenize
    import nltk
    # Verificar se os dados necessários estão disponíveis
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        # Tentar baixar os dados necessários
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

from typing import List

# Mock do logger
emoji_logger = MockEmojiLogger()

class MessageSplitter:
    """
    Splitter inteligente que preserva emojis, palavras e frases
    Usa regex module para suporte a grapheme clusters e NLTK para divisão por frases
    """
    
    def __init__(self, max_length: int = 150, add_indicators: bool = False, enable_smart_splitting: bool = True, smart_splitting_fallback: bool = True):
        """
        Inicializa o splitter
        
        Args:
            max_length: Tamanho máximo de cada chunk
            add_indicators: Se deve adicionar [1/3], [2/3] etc
            enable_smart_splitting: Se deve usar divisão inteligente por frases
            smart_splitting_fallback: Se deve fazer fallback para algoritmo atual quando NLTK falha
        """
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
        """
        Divide mensagem em chunks preservando palavras, emojis e frases
        
        Args:
            text: Texto para dividir
            
        Returns:
            Lista de chunks
        """
        if not text:
            return []
        
        # Se cabe, retorna direto
        if len(text) <= self.max_length:
            return [text.strip()]
        
        # Tentar divisão inteligente por frases primeiro
        if self.enable_smart_splitting and HAS_NLTK:
            try:
                chunks = self._split_by_sentences(text)
                emoji_logger.system_debug(
                    f"Mensagem dividida inteligentemente",
                    original_length=len(text),
                    chunks=len(chunks),
                    method="smart_splitting"
                )
                
                # Adiciona indicadores se configurado
                if self.add_indicators and len(chunks) > 1:
                    chunks = self._add_indicators(chunks)
                
                return chunks
            except Exception as e:
                emoji_logger.system_warning(
                    f"Divisão inteligente falhou: {e}. Usando algoritmo padrão"
                )
                if not self.smart_splitting_fallback:
                    raise
        
        # Fallback: Divide de forma simples
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
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Divide texto por frases usando NLTK para divisão inteligente
        
        Args:
            text: Texto para dividir
            
        Returns:
            Lista de chunks agrupando frases
        """
        try:
            # Tokenizar em frases usando NLTK
            sentences = sent_tokenize(text, language='portuguese')
            
            if not sentences:
                return [text.strip()]
            
            # Se só há uma frase mas é muito longa, forçar divisão
            if len(sentences) == 1 and len(sentences[0]) > self.max_length:
                return self._force_split_long_sentence(sentences[0])
            
            # Agrupar frases respeitando o limite de caracteres
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Teste se a frase cabe no chunk atual
                test_chunk = current_chunk + (" " if current_chunk else "") + sentence
                
                if len(test_chunk) <= self.max_length:
                    # Cabe no chunk atual
                    current_chunk = test_chunk
                else:
                    # Não cabe, finalizar chunk atual e começar novo
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # Se a frase sozinha é muito longa, dividir ela
                    if len(sentence) > self.max_length:
                        chunks.extend(self._force_split_long_sentence(sentence))
                        current_chunk = ""
                    else:
                        current_chunk = sentence
            
            # Adicionar último chunk se houver
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks if chunks else [text.strip()]
        
        except Exception as e:
            emoji_logger.system_warning(f"Erro na divisão por frases: {e}")
            raise
    
    def _force_split_long_sentence(self, sentence: str) -> List[str]:
        """
        Força divisão de frase muito longa usando algoritmo de fallback
        
        Args:
            sentence: Frase muito longa para dividir
            
        Returns:
            Lista de chunks da frase dividida
        """
        # Usar algoritmo simples para dividir frase longa
        return self._split_simple(sentence)
    
    def _split_simple(self, text: str) -> List[str]:
        """
        Divide de forma simples (fallback)
        
        Args:
            text: Texto para dividir
            
        Returns:
            Lista de chunks
        """
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
        """
        Adiciona indicadores [1/3], [2/3] etc
        
        Args:
            chunks: Lista de chunks
            
        Returns:
            Chunks com indicadores
        """
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

if __name__ == "__main__":
    print("🧪 TESTE SIMPLES DO SMART MESSAGE SPLITTER")
    print("=" * 50)
    print()
    
    print(f"NLTK disponível: {HAS_NLTK}")
    print(f"Regex disponível: {HAS_REGEX}")
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
        
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()