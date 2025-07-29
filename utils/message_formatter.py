"""
Message Formatter Utility
========================
Utilitário para formatar mensagens para o WhatsApp
"""

import re
from typing import List, Tuple

def format_message_for_whatsapp(message: str) -> str:
    """
    Formata uma mensagem para o WhatsApp
    
    Args:
        message: Mensagem original
        
    Returns:
        Mensagem formatada para WhatsApp
    """
    # 1. Converter markdown bold (**text**) para WhatsApp bold (*text*)
    # Primeiro, processar casos especiais como **texto:**
    message = re.sub(r'\*\*([^*]+):\*\*', r'*\1...*', message)
    
    # Depois, converter o restante dos bold normais
    message = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', message)
    
    # 2. Converter dois pontos ":" em final de frase para reticências "..."
    # Apenas quando seguido de espaço ou nova linha
    message = re.sub(r':(\s|$)', r'...\1', message)
    
    # 3. Remover hífens desnecessários no início de linhas
    message = re.sub(r'^-\s+', '', message, flags=re.MULTILINE)
    message = re.sub(r'\n-\s+', '\n', message)
    
    # 4. Converter markdown headers (###) para bold
    message = re.sub(r'^###\s+(.+)$', r'*\1*', message, flags=re.MULTILINE)
    message = re.sub(r'^##\s+(.+)$', r'*\1*', message, flags=re.MULTILINE)
    message = re.sub(r'^#\s+(.+)$', r'*\1*', message, flags=re.MULTILINE)
    
    # 5. Limpar espaços extras
    message = re.sub(r'\n{3,}', '\n\n', message)  # Máximo 2 quebras de linha
    message = re.sub(r' {2,}', ' ', message)  # Remover espaços múltiplos
    
    return message.strip()


def improve_chunk_splitting(chunks: List[str]) -> List[str]:
    """
    Melhora a divisão de chunks evitando quebras em vírgulas
    
    Args:
        chunks: Lista de chunks originais
        
    Returns:
        Lista de chunks melhorados
    """
    if not chunks:
        return chunks
        
    improved_chunks = []
    buffer = ""
    
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        
        # Se o buffer tem conteúdo, tentar juntar
        if buffer:
            # Juntar se o total não for muito longo
            combined = buffer + " " + chunk
            if len(combined.split()) <= 40:  # Limite de palavras
                buffer = combined
                # Se é o último chunk ou o próximo é um ponto final, adicionar
                if i == len(chunks) - 1 or chunk.endswith(('.', '!', '?')):
                    improved_chunks.append(buffer)
                    buffer = ""
            else:
                # Buffer muito longo, adicionar e começar novo
                improved_chunks.append(buffer)
                buffer = chunk
        else:
            # Verificar se deve iniciar buffer
            if (len(chunk.split()) < 8 and  # Chunk muito curto
                (chunk.endswith(',') or chunk.endswith(':')) and  # Termina com vírgula ou dois pontos
                i < len(chunks) - 1):  # Não é o último
                buffer = chunk
            else:
                # Chunk normal, adicionar diretamente
                improved_chunks.append(chunk)
    
    # Adicionar buffer restante
    if buffer:
        improved_chunks.append(buffer)
    
    # Terceira passada: juntar chunks muito curtos consecutivos
    final_chunks = []
    i = 0
    
    while i < len(improved_chunks):
        chunk = improved_chunks[i]
        
        # Se é muito curto e não é o último
        if len(chunk.split()) < 5 and i < len(improved_chunks) - 1:
            # Verificar se pode juntar com o próximo
            next_chunk = improved_chunks[i + 1]
            combined = chunk + " " + next_chunk
            
            # Se não fica muito longo, juntar
            if len(combined.split()) <= 35:
                final_chunks.append(combined)
                i += 2  # Pular o próximo
                continue
        
        final_chunks.append(chunk)
        i += 1
    
    return final_chunks


def should_use_natural_breaks(message: str) -> Tuple[bool, List[str]]:
    """
    Verifica se a mensagem tem quebras naturais e retorna os chunks
    
    Args:
        message: Mensagem a verificar
        
    Returns:
        Tuple (deve_usar_quebras_naturais, lista_de_chunks)
    """
    # Padrões que indicam quebras naturais
    natural_patterns = [
        r'\n\n',  # Parágrafos
        r'\n\d+\.',  # Listas numeradas
        r'\n[•\-]',  # Listas com bullets
        r'\n\*[^*]+\*',  # Títulos em negrito
    ]
    
    # Verificar se tem padrões naturais
    has_natural_breaks = any(re.search(pattern, message) for pattern in natural_patterns)
    
    if not has_natural_breaks:
        return False, []
    
    # Dividir por parágrafos primeiro
    paragraphs = message.split('\n\n')
    chunks = []
    
    for para in paragraphs:
        # Se o parágrafo é uma lista
        if re.search(r'^\d+\.|\n\d+\.|^[•\-]|\n[•\-]', para):
            # Dividir por itens
            items = re.split(r'\n(?=\d+\.)|(?=^[•\-])', para)
            chunks.extend([item.strip() for item in items if item.strip()])
        else:
            # Adicionar parágrafo inteiro se não for muito longo
            if len(para.split()) <= 50:
                chunks.append(para.strip())
            else:
                # Dividir parágrafo longo em sentenças
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current_chunk = ""
                
                for sentence in sentences:
                    if len((current_chunk + " " + sentence).split()) <= 30:
                        current_chunk = (current_chunk + " " + sentence).strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence
                
                if current_chunk:
                    chunks.append(current_chunk)
    
    return True, [chunk for chunk in chunks if chunk]