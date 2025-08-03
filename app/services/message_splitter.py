"""
Message Splitter Service - Quebra mensagens preservando emojis e palavras
"""
try:
    import regex
    HAS_REGEX = True
except ImportError:
    import re as regex
    HAS_REGEX = False
    
from typing import List, Optional
from app.utils.logger import emoji_logger

class MessageSplitter:
    """
    Splitter simples que preserva emojis e palavras inteiras
    Usa regex module para suporte a grapheme clusters
    """
    
    def __init__(self, max_length: int = 150, add_indicators: bool = False):
        """
        Inicializa o splitter
        
        Args:
            max_length: Tamanho máximo de cada chunk
            add_indicators: Se deve adicionar [1/3], [2/3] etc
        """
        self.max_length = max_length
        self.add_indicators = add_indicators
        
        if not HAS_REGEX:
            emoji_logger.system_warning(
                "Módulo 'regex' não instalado. Usando 're' padrão (pode quebrar emojis)"
            )
        
        emoji_logger.system_info(f"Message Splitter inicializado (max={max_length} chars)")
    
    def split_message(self, text: str) -> List[str]:
        """
        Divide mensagem em chunks preservando palavras e emojis
        
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
        
        # Divide preservando emojis
        if HAS_REGEX:
            chunks = self._split_with_regex(text)
        else:
            chunks = self._split_simple(text)
        
        # Adiciona indicadores se configurado
        if self.add_indicators and len(chunks) > 1:
            chunks = self._add_indicators(chunks)
        
        emoji_logger.system_debug(
            f"Mensagem dividida",
            original_length=len(text),
            chunks=len(chunks)
        )
        
        return chunks
    
    def _split_with_regex(self, text: str) -> List[str]:
        """
        Divide usando regex module (preserva emojis)
        
        Args:
            text: Texto para dividir
            
        Returns:
            Lista de chunks
        """
        chunks = []
        
        # Extrai grapheme clusters (caracteres completos incluindo emojis)
        graphemes = regex.findall(r'\X', text)
        
        while graphemes:
            # Determina tamanho máximo do chunk
            chunk_size = min(self.max_length, len(graphemes))
            
            # Constrói chunk respeitando o limite de caracteres
            chunk_text = ""
            chunk_count = 0
            
            for i, grapheme in enumerate(graphemes[:chunk_size]):
                test_chunk = chunk_text + grapheme
                # Verifica se adicionar este grapheme excede o limite
                if len(test_chunk) > self.max_length:
                    break
                chunk_text = test_chunk
                chunk_count = i + 1
            
            # Se não é o último chunk e terminou no meio de palavra, volta até espaço
            if len(graphemes) > chunk_count and chunk_text:
                # Procura último espaço no chunk
                last_space = -1
                current_text = ""
                for i, grapheme in enumerate(graphemes[:chunk_count]):
                    current_text += grapheme
                    if grapheme.isspace():
                        last_space = i + 1
                
                # Se encontrou espaço, corta ali
                if last_space > 0:
                    chunk_text = ''.join(graphemes[:last_space]).rstrip()
                    chunk_count = last_space
            
            # Adiciona chunk se não vazio
            chunk_text = chunk_text.strip()
            if chunk_text:
                chunks.append(chunk_text)
            
            # Remove graphemes processados
            graphemes = graphemes[chunk_count:]
            # Pula espaços iniciais do próximo chunk
            while graphemes and graphemes[0].isspace():
                graphemes.pop(0)
        
        return chunks
    
    def _split_simple(self, text: str) -> List[str]:
        """
        Divide de forma simples (fallback sem regex module)
        
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

# Instância global
message_splitter: Optional[MessageSplitter] = None

def get_message_splitter() -> MessageSplitter:
    """Retorna instância global do splitter"""
    global message_splitter
    if not message_splitter:
        message_splitter = MessageSplitter()
    return message_splitter

def set_message_splitter(splitter: MessageSplitter) -> None:
    """Define instância global do splitter"""
    global message_splitter
    message_splitter = splitter