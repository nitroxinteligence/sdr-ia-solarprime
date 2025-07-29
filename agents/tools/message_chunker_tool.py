"""
Message Chunker Tool for AGnO
==============================
Tool para dividir mensagens em chunks menores, criando conversação mais natural
Baseado no padrão N8N para mensagens "picotadas"
"""

import re
import random
from typing import List, Dict, Any, Optional, Tuple
from agno.tools import tool
from loguru import logger
from utils.message_formatter import format_message_for_whatsapp, improve_chunk_splitting, should_use_natural_breaks


async def chunk_message_standalone(
    message: str,
    join_probability: float = 0.6,
    max_chunk_words: int = 30,
    min_chunk_words: int = 3,
    max_chars_per_chunk: int = 1200  # Deixar margem do limite de 1600 do WhatsApp
) -> Dict[str, Any]:
    """
    Versão standalone da função chunk_message para uso direto
    """
    if not message or not message.strip():
        return {
            "chunks": [],
            "delays": [],
            "total_reading_time": 0
        }
    
    try:
        # Primeiro, formatar a mensagem para WhatsApp
        message = format_message_for_whatsapp(message)
        
        # Verificar se deve usar quebras naturais
        use_natural, natural_chunks = should_use_natural_breaks(message)
        
        if use_natural and natural_chunks:
            # Usar as quebras naturais encontradas
            chunks = natural_chunks
        else:
            # Converter markdown headers para bold (já feito no formatter)
            # message = convert_markdown_headers(message)
            
            # Dividir em sentenças preservando casos especiais
            sentences = split_into_sentences(message)
            
            if not sentences:
                return {
                    "chunks": [message],
                    "delays": [calculate_typing_delay(message)],
                    "total_reading_time": calculate_reading_time(message)
                }
            
            # Aplicar lógica de junção probabilística
            chunks = apply_join_probability(sentences, join_probability)
            
            # Otimizar tamanhos dos chunks
            chunks = optimize_chunk_sizes(chunks, max_chunk_words, min_chunk_words, max_chars_per_chunk)
        
        # Melhorar divisão de chunks (evitar quebras em vírgulas)
        chunks = improve_chunk_splitting(chunks)
        
        # Limpar e validar chunks
        final_chunks = []
        delays = []
        
        for chunk in chunks:
            cleaned = chunk.strip()
            if cleaned:
                # Aplicar formatação final em cada chunk
                cleaned = format_message_for_whatsapp(cleaned)
                final_chunks.append(cleaned)
                # Calcular delay baseado no tamanho do chunk
                delay = calculate_typing_delay(cleaned)
                delays.append(delay)
        
        # Se não houver chunks válidos, retornar mensagem original
        if not final_chunks:
            return {
                "chunks": [message],
                "delays": [calculate_typing_delay(message)],
                "total_reading_time": calculate_reading_time(message)
            }
        
        # Calcular tempo total de leitura
        total_reading_time = sum(calculate_reading_time(chunk) for chunk in final_chunks)
        
        logger.info(f"Mensagem dividida em {len(final_chunks)} chunks, tempo total: {total_reading_time/1000:.1f}s")
        
        return {
            "chunks": final_chunks,
            "delays": delays,
            "total_reading_time": total_reading_time,
            "chunk_count": len(final_chunks)
        }
        
    except Exception as e:
        logger.error(f"Erro ao dividir mensagem em chunks: {e}")
        # Em caso de erro, retornar mensagem original
        return {
            "chunks": [message],
            "delays": [2000],  # Delay padrão de 2s
            "total_reading_time": calculate_reading_time(message)
        }


@tool
async def chunk_message(
    agent,
    message: str,
    join_probability: float = 0.6,
    max_chunk_words: int = 30,
    min_chunk_words: int = 3,
    max_chars_per_chunk: int = 1200  # Deixar margem do limite de 1600 do WhatsApp
) -> Dict[str, Any]:
    """
    Divide uma mensagem em chunks menores para envio sequencial
    
    Esta tool cria uma conversação mais natural dividindo mensagens longas
    em pedaços menores, simulando como uma pessoa real digitaria.
    
    Args:
        agent: Instância do agente AGnO
        message: Mensagem completa para dividir
        join_probability: Probabilidade de juntar sentenças adjacentes (0.0-1.0)
        max_chunk_words: Número máximo de palavras por chunk
        min_chunk_words: Número mínimo de palavras por chunk
        max_chars_per_chunk: Número máximo de caracteres por chunk (WhatsApp: 1600)
        
    Returns:
        Dict contendo:
            - chunks: Lista de chunks de mensagem
            - delays: Lista de delays em ms para cada chunk
            - total_reading_time: Tempo total estimado de leitura
    """
    
    # Usar a versão standalone
    return await chunk_message_standalone(
        message=message,
        join_probability=join_probability,
        max_chunk_words=max_chunk_words,
        min_chunk_words=min_chunk_words,
        max_chars_per_chunk=max_chars_per_chunk
    )


def convert_markdown_headers(text: str) -> str:
    """Converte headers markdown para texto em bold
    NOTA: Esta função está mantida por compatibilidade mas a conversão
    agora é feita em format_message_for_whatsapp()
    """
    # Converter ### Header para *Header* (WhatsApp format)
    text = re.sub(r'^###\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)
    return text


def split_into_sentences(text: str) -> List[str]:
    """
    Divide texto em sentenças considerando casos especiais
    """
    # Proteger casos especiais temporariamente
    protections = []
    
    # Proteger URLs
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    for i, url in enumerate(urls):
        placeholder = f"__URL_{i}__"
        text = text.replace(url, placeholder)
        protections.append((placeholder, url))
    
    # Proteger abreviações comuns
    abbreviations = [
        "Dr.", "Sr.", "Sra.", "Ltd.", "Inc.", "vs.", "etc.", "Jr.", 
        "Ph.D.", "M.D.", "B.A.", "M.A.", "B.S.", "M.S.",
        "i.e.", "e.g.", "a.m.", "p.m.", "A.M.", "P.M.",
        "Jan.", "Feb.", "Mar.", "Apr.", "Jun.", "Jul.", 
        "Aug.", "Sep.", "Sept.", "Oct.", "Nov.", "Dec."
    ]
    
    for abbr in abbreviations:
        if abbr in text:
            placeholder = f"__{abbr.replace('.', '_')}__"
            text = text.replace(abbr, placeholder)
            protections.append((placeholder, abbr))
    
    # Proteger números decimais
    decimal_pattern = r'\d+\.\d+'
    decimals = re.findall(decimal_pattern, text)
    for i, decimal in enumerate(decimals):
        placeholder = f"__DECIMAL_{i}__"
        text = text.replace(decimal, placeholder)
        protections.append((placeholder, decimal))
    
    # Padrão principal para dividir sentenças
    # Divide em: . ! ? ... 
    # Mas preserva casos como emojis seguidos de pontuação
    sentence_endings = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\s*\n|(?<=\.\.\.)\s+'
    
    # Dividir preservando enumerações
    # Não dividir após números seguidos de ponto (1. 2. etc)
    text = re.sub(r'(\d+)\.\s+', r'\1__ENUM__ ', text)
    
    # Realizar divisão
    sentences = re.split(sentence_endings, text)
    
    # Restaurar enumerações
    sentences = [s.replace('__ENUM__', '.') for s in sentences]
    
    # Restaurar proteções
    final_sentences = []
    for sentence in sentences:
        for placeholder, original in protections:
            sentence = sentence.replace(placeholder, original)
        final_sentences.append(sentence)
    
    # Tratar casos especiais de emojis e pontuação
    processed_sentences = []
    for sentence in final_sentences:
        # Se a sentença termina com emoji + pontuação, preservar
        if re.search(r'[😀-🙏]+[.!?]$', sentence):
            processed_sentences.append(sentence)
        # Se é uma linha com apenas emojis, preservar
        elif re.match(r'^[😀-🙏\s]+$', sentence):
            processed_sentences.append(sentence)
        else:
            processed_sentences.append(sentence)
    
    return [s.strip() for s in processed_sentences if s.strip()]


def apply_join_probability(sentences: List[str], join_probability: float) -> List[str]:
    """
    Aplica probabilidade de juntar sentenças adjacentes
    """
    if len(sentences) <= 1:
        return sentences
    
    chunks = []
    current_chunk = sentences[0]
    
    for i in range(1, len(sentences)):
        # Decidir se deve juntar com a sentença anterior
        should_join = random.random() < join_probability
        
        # Regras adicionais para forçar ou evitar junção
        prev_sentence = sentences[i-1].strip()
        curr_sentence = sentences[i].strip()
        
        # Sempre juntar se a sentença anterior é muito curta
        if len(prev_sentence.split()) < 3:
            should_join = True
        
        # Nunca juntar se resultar em chunk muito longo
        combined_length = len((current_chunk + " " + curr_sentence).split())
        if combined_length > 40:
            should_join = False
        
        # Sempre separar itens de lista
        if re.match(r'^\d+\.', curr_sentence) or curr_sentence.startswith('•'):
            should_join = False
        
        # Sempre separar perguntas
        if prev_sentence.endswith('?'):
            should_join = False
        
        if should_join:
            current_chunk += " " + curr_sentence
        else:
            chunks.append(current_chunk)
            current_chunk = curr_sentence
    
    # Adicionar último chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def optimize_chunk_sizes(chunks: List[str], max_words: int, min_words: int, max_chars: int) -> List[str]:
    """
    Otimiza o tamanho dos chunks para ficar dentro dos limites
    """
    optimized = []
    
    for chunk in chunks:
        # Verificar limite de caracteres primeiro (mais importante para WhatsApp)
        if len(chunk) > max_chars:
            # Dividir por caracteres mantendo palavras inteiras
            sub_chunks = []
            current_sub = ""
            
            words = chunk.split()
            for word in words:
                test_text = current_sub + " " + word if current_sub else word
                
                if len(test_text) > max_chars:
                    # Adicionar chunk atual e começar novo
                    if current_sub:
                        sub_chunks.append(current_sub)
                    current_sub = word
                else:
                    current_sub = test_text
            
            if current_sub:
                sub_chunks.append(current_sub)
            
            optimized.extend(sub_chunks)
            continue
        
        words = chunk.split()
        word_count = len(words)
        
        # Se o chunk é muito grande em palavras, dividir
        if word_count > max_words:
            # Tentar dividir em pontos naturais
            sub_chunks = []
            current_sub = []
            
            for word in words:
                current_sub.append(word)
                
                # Verificar se chegou em um ponto natural de divisão
                current_text = " ".join(current_sub)
                # Remover vírgula da lista de pontos de quebra
                if (len(current_sub) >= max_words // 2 and 
                    any(current_text.endswith(p) for p in ['.', '!', '?'])):
                    sub_chunks.append(current_text)
                    current_sub = []
                elif len(current_sub) >= max_words:
                    # Forçar divisão se muito longo
                    sub_chunks.append(current_text)
                    current_sub = []
            
            # Adicionar resto
            if current_sub:
                sub_chunks.append(" ".join(current_sub))
            
            optimized.extend(sub_chunks)
        
        # Se o chunk é muito pequeno, tentar juntar com próximo
        elif word_count < min_words and optimized:
            # Juntar com o chunk anterior se possível
            last_chunk = optimized[-1]
            combined = last_chunk + " " + chunk
            # Verificar limites de palavras e caracteres
            if len(combined.split()) <= max_words and len(combined) <= max_chars:
                optimized[-1] = combined
            else:
                optimized.append(chunk)
        else:
            optimized.append(chunk)
    
    return optimized


def calculate_typing_delay(text: str, words_per_minute: int = 150) -> int:
    """
    Calcula o delay de digitação baseado no tamanho do texto
    
    Args:
        text: Texto para calcular delay
        words_per_minute: Velocidade de digitação simulada (padrão: 150 wpm)
        
    Returns:
        Delay em milissegundos
    """
    # Contar palavras
    word_count = len(text.split())
    
    # Calcular tempo base (convertendo para ms)
    base_delay = (word_count / words_per_minute) * 60 * 1000
    
    # Adicionar variação aleatória (±20%)
    variation = random.uniform(0.8, 1.2)
    delay = int(base_delay * variation)
    
    # Limites: mínimo 1s, máximo 3s para WhatsApp
    delay = max(1000, min(3000, delay))
    
    # Se houver pontuação especial, adicionar pequena pausa
    if any(char in text for char in ['?', '!', '...', ':']):
        delay += 300
    
    return delay


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calcula o tempo estimado de leitura
    
    Args:
        text: Texto para calcular tempo de leitura
        words_per_minute: Velocidade média de leitura (padrão: 200 wpm)
        
    Returns:
        Tempo de leitura em milissegundos
    """
    word_count = len(text.split())
    # Tempo em ms
    reading_time = (word_count / words_per_minute) * 60 * 1000
    
    # Adicionar tempo extra para processar informações complexas
    if any(term in text.lower() for term in ['r$', '%', 'kwh', 'economia']):
        reading_time *= 1.2  # 20% mais tempo para números
    
    return int(reading_time)


@tool
async def analyze_message_for_chunking(
    agent,
    message: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analisa uma mensagem para determinar a melhor estratégia de chunking
    
    Args:
        agent: Instância do agente AGnO
        message: Mensagem a ser analisada
        context: Contexto da conversa (estágio, tipo de resposta, etc)
        
    Returns:
        Configurações recomendadas para chunking
    """
    
    try:
        word_count = len(message.split())
        has_list = bool(re.search(r'^\d+\.|\n•|\n-', message, re.MULTILINE))
        has_questions = message.count('?') > 0
        has_technical_info = any(term in message.lower() for term in 
                                ['kwh', 'r$', '%', 'economia', 'valor', 'conta'])
        
        # Análise do estágio da conversa
        stage = context.get('stage', 'INITIAL_CONTACT')
        
        # Configurações baseadas na análise
        config = {
            'should_chunk': word_count > 20,  # Dividir se tiver mais de 20 palavras
            'join_probability': 0.6,  # Padrão
            'max_chunk_words': 30,
            'min_chunk_words': 3,
            'chunk_delay_ms': 1500,  # Delay entre chunks
            'typing_simulation': True,
            'reasoning': ""
        }
        
        # Ajustes baseados no tipo de conteúdo
        if stage == 'INITIAL_CONTACT':
            # Mensagens iniciais devem ser mais "picotadas" para parecer natural
            config['join_probability'] = 0.4
            config['max_chunk_words'] = 20
            config['reasoning'] = "Contato inicial - mensagens mais curtas e naturais"
        
        elif has_list:
            # Listas devem ter items separados
            config['join_probability'] = 0.2
            config['reasoning'] = "Conteúdo com lista - manter items separados"
        
        elif has_technical_info:
            # Informações técnicas podem ser um pouco mais longas
            config['join_probability'] = 0.7
            config['max_chunk_words'] = 35
            config['reasoning'] = "Informações técnicas - chunks um pouco maiores"
        
        elif has_questions:
            # Perguntas devem ficar separadas
            config['join_probability'] = 0.3
            config['reasoning'] = "Perguntas detectadas - manter separadas"
        
        # Casos especiais onde não devemos dividir
        if word_count < 15:
            config['should_chunk'] = False
            config['reasoning'] = "Mensagem muito curta - enviar inteira"
        
        return config
        
    except Exception as e:
        logger.error(f"Erro ao analisar mensagem para chunking: {e}")
        return {
            'should_chunk': False,
            'reasoning': f"Erro na análise: {e}"
        }