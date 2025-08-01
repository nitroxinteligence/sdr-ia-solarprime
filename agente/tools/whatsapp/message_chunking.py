"""
MessageChunkingTool - Divide mensagens grandes em chunks para envio natural
"""

import re
from typing import Dict, Any, List
from agno.tools import tool
from loguru import logger

from ...core.types import MessageChunk


@tool(show_result=True)
async def chunk_message(
    text: str,
    max_chars: int = 1000,
    prefer_sentences: bool = True,
    min_delay_ms: int = 1000,
    max_delay_ms: int = 3000
) -> Dict[str, Any]:
    """
    Divide mensagens grandes em chunks menores para envio mais natural.
    
    Esta ferramenta quebra textos longos em partes menores, respeitando
    pontuação e estrutura das frases quando possível, e calcula delays
    apropriados entre cada chunk para simular digitação humana.
    
    Args:
        text: Texto a ser dividido em chunks
        max_chars: Número máximo de caracteres por chunk (padrão: 1000)
        prefer_sentences: Se deve preferir quebrar em fim de frases (padrão: True)
        min_delay_ms: Delay mínimo entre chunks em milissegundos (padrão: 1000)
        max_delay_ms: Delay máximo entre chunks em milissegundos (padrão: 3000)
    
    Returns:
        Dict com chunks processados:
        - success: bool - Se o chunking foi realizado com sucesso
        - chunks: List[Dict] - Lista de chunks com texto e delay
        - total_chunks: int - Número total de chunks criados
        - total_chars: int - Total de caracteres no texto original
        - average_chunk_size: float - Tamanho médio dos chunks
        - total_delay_ms: int - Delay total entre todos os chunks
        - error: str - Mensagem de erro (se falhou)
    
    Examples:
        >>> await chunk_message("Texto muito longo..." * 100)
        {"success": True, "chunks": [...], "total_chunks": 3, "total_chars": 2000, "average_chunk_size": 666.7, "total_delay_ms": 6500}
        
        >>> await chunk_message("Frase curta.", max_chars=50)
        {"success": True, "chunks": [{"text": "Frase curta.", "delay_ms": 1000, "words": 2, "chars": 12}], "total_chunks": 1, ...}
    """
    try:
        logger.info(
            "Iniciando divisão de mensagem em chunks",
            text_length=len(text),
            max_chars=max_chars,
            prefer_sentences=prefer_sentences
        )
        
        # Validações
        if not text:
            return {
                "success": False,
                "error": "Texto vazio fornecido",
                "chunks": [],
                "total_chunks": 0,
                "total_chars": 0,
                "average_chunk_size": 0,
                "total_delay_ms": 0
            }
        
        if max_chars < 50:
            logger.warning(
                "max_chars muito pequeno, ajustando para 50",
                original_max_chars=max_chars
            )
            max_chars = 50
        
        # Remove espaços extras e normaliza quebras de linha
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        chunks = []
        current_position = 0
        text_length = len(text)
        
        while current_position < text_length:
            # Determina fim do chunk
            chunk_end = min(current_position + max_chars, text_length)
            
            # Se preferir sentenças e não é o último chunk
            if prefer_sentences and chunk_end < text_length:
                # Procura por pontuação de fim de frase
                sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
                
                # Busca a última pontuação antes do limite
                best_break = -1
                for ending in sentence_endings:
                    pos = text.rfind(ending, current_position, chunk_end)
                    if pos > best_break:
                        best_break = pos + len(ending) - 1  # Inclui a pontuação
                
                # Se encontrou uma boa quebra e não está muito próxima do início
                if best_break > current_position + max_chars * 0.3:
                    chunk_end = best_break + 1
                else:
                    # Tenta quebrar em espaço se não encontrou pontuação
                    space_pos = text.rfind(' ', current_position, chunk_end)
                    if space_pos > current_position:
                        chunk_end = space_pos
            
            # Extrai o chunk
            chunk_text = text[current_position:chunk_end].strip()
            
            if chunk_text:  # Apenas adiciona chunks não vazios
                # Conta palavras
                words_count = len(chunk_text.split())
                
                # Calcula delay baseado no tamanho do chunk
                # Mais palavras = mais tempo para "digitar"
                delay_factor = min(words_count / 50, 1.0)  # Normaliza até 50 palavras
                delay_ms = int(min_delay_ms + (max_delay_ms - min_delay_ms) * delay_factor)
                
                # Adiciona pequena variação aleatória (±10%)
                import random
                variation = int(delay_ms * 0.1)
                delay_ms += random.randint(-variation, variation)
                
                chunk_data = MessageChunk(
                    text=chunk_text,
                    delay_ms=delay_ms,
                    words=words_count,
                    chars=len(chunk_text)
                )
                
                chunks.append(chunk_data.dict())
                
                logger.debug(
                    f"Chunk {len(chunks)} criado",
                    chars=len(chunk_text),
                    words=words_count,
                    delay_ms=delay_ms
                )
            
            current_position = chunk_end
        
        # Calcula estatísticas
        total_chunks = len(chunks)
        total_chars = sum(chunk["chars"] for chunk in chunks)
        average_chunk_size = total_chars / total_chunks if total_chunks > 0 else 0
        total_delay_ms = sum(chunk["delay_ms"] for chunk in chunks)
        
        logger.success(
            "Mensagem dividida em chunks com sucesso",
            total_chunks=total_chunks,
            average_size=average_chunk_size,
            total_delay_seconds=total_delay_ms / 1000
        )
        
        return {
            "success": True,
            "chunks": chunks,
            "total_chunks": total_chunks,
            "total_chars": total_chars,
            "average_chunk_size": round(average_chunk_size, 1),
            "total_delay_ms": total_delay_ms
        }
        
    except Exception as e:
        logger.error(
            f"Erro ao dividir mensagem em chunks: {str(e)}",
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro no chunking: {str(e)}",
            "chunks": [],
            "total_chunks": 0,
            "total_chars": len(text) if text else 0,
            "average_chunk_size": 0,
            "total_delay_ms": 0
        }


# Export da tool
MessageChunkingTool = chunk_message

# Alias para compatibilidade
message_chunking = chunk_message

# Alias para type_simulation (compatibilidade com imports antigos)
from .type_simulation import simulate_typing
type_simulation = simulate_typing  # Alias para compatibilidade