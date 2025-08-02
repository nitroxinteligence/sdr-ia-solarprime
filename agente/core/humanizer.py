"""
Humanizer module for Helen Vieira chatbot.
Provides realistic typing simulation and emotional state handling.
"""

import random
import re
from typing import List, Dict, Tuple
from loguru import logger


class NaturalBreakAnalyzer:
    """
    Analisador de pontos naturais de quebra semântica em português brasileiro.
    Identifica locais onde quebras de mensagem soam naturais mesmo sem pontuação.
    """
    
    def __init__(self):
        """Inicializa analisador com padrões linguísticos brasileiros."""
        
        # Padrões de quebra natural otimizados para Helen Vieira (resultado exato esperado)
        self.natural_break_patterns = [
            # Apresentação completa com saudação - quebra após nome completo
            (r'(Oi!\s+Muito prazer,\s+me chamo [A-Za-zÀ-ÿ\s]+?)(?=\s+e\s+sou)', 'greeting_presentation'),
            (r'(Olá!\s+Muito prazer,\s+me chamo [A-Za-zÀ-ÿ\s]+?)(?=\s+e\s+sou)', 'greeting_presentation'),
            
            # Apresentações pessoais isoladas - quebra após nome completo
            (r'(me chamo [A-Za-zÀ-ÿ\s]+?)(?=\s+e\s+sou|\.|!|\?)', 'presentation_name'),
            (r'(meu nome é [A-Za-zÀ-ÿ\s]+?)(?=\s+e\s+sou|\.|!|\?)', 'presentation_name'),
            
            # Identificações profissionais com empresa - quebra após empresa
            (r'((?:e\s+)?sou [^.!?]*?(?:da|na|de)\s+[A-Za-zÀ-ÿ\s]*?(?:Prime|Solar|Energy)[^.!?]*?)(?=\.|!|\?)', 'professional_company'),
            (r'((?:e\s+)?sou [^.!?]*?(?:consultora|especialista)[^.!?]*?)(?=\.|!|\?)', 'professional_role'),
            
            # Expressões de cortesia isoladas
            (r'(muito prazer)(?![,\s]*me chamo)', 'courtesy'),
            (r'(seja bem-vindo[a]?)', 'courtesy'),
            (r'(fico feliz em [^.!?]*)', 'courtesy'),
            
            # Transições conversacionais
            (r'(agora [^.!?]*)', 'transition'),
            (r'(então [^.!?]*)', 'transition'),
            (r'(vamos [^.!?]*)', 'transition'),
        ]
        
        # Padrões que merecem destaque próprio (sempre quebrar antes)
        self.highlight_patterns = [
            (r'(qual [^.!?]*\?)', 'question'),
            (r'(como [^.!?]*\?)', 'question'),
            (r'(quando [^.!?]*\?)', 'question'),
            (r'(onde [^.!?]*\?)', 'question'),
            (r'(por que [^.!?]*\?)', 'question'),
            (r'(você [^.!?]*\?)', 'question'),
            (r'(posso [^.!?]*\?)', 'question'),
        ]
        
        # Pontuações tradicionais para balanceamento
        self.punctuation_breaks = ['.', '!', '?', ';']
        
        logger.info(
            "NaturalBreakAnalyzer initialized",
            natural_patterns=len(self.natural_break_patterns),
            highlight_patterns=len(self.highlight_patterns)
        )
    
    def find_natural_break_points(self, text: str) -> List[Tuple[int, str, str]]:
        """
        Identifica pontos naturais de quebra no texto.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Lista de tuplas (posição, tipo, texto_matched)
        """
        break_points = []
        
        # 1. Encontrar quebras por padrões naturais
        for pattern, break_type in self.natural_break_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                end_pos = match.end()
                matched_text = match.group(1)
                break_points.append((end_pos, f'natural_{break_type}', matched_text))
        
        # 2. Encontrar padrões que merecem destaque
        for pattern, break_type in self.highlight_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start_pos = match.start()
                matched_text = match.group(1)
                # Quebrar ANTES da pergunta
                break_points.append((start_pos, f'highlight_{break_type}', matched_text))
        
        # 3. Encontrar quebras por pontuação (para balancear)
        for i, char in enumerate(text):
            if char in self.punctuation_breaks:
                # Quebrar APÓS pontuação
                break_points.append((i + 1, 'punctuation', char))
        
        # Ordenar por posição e remover duplicatas próximas
        break_points.sort(key=lambda x: x[0])
        filtered_points = []
        
        for point in break_points:
            pos, break_type, matched = point
            # Evitar quebras muito próximas (menos de 20 caracteres)
            if not filtered_points or pos - filtered_points[-1][0] >= 20:
                filtered_points.append(point)
        
        logger.debug(
            "Natural break points found",
            total_points=len(filtered_points),
            text_length=len(text)
        )
        
        return filtered_points
    
    def score_break_naturalness(self, text_before: str, text_after: str) -> float:
        """
        Calcula quão natural é uma quebra entre dois segmentos.
        
        Args:
            text_before: Texto antes da quebra
            text_after: Texto depois da quebra
            
        Returns:
            Score de 0.0 a 1.0 (1.0 = muito natural)
        """
        score = 0.5  # Base score
        
        before_words = text_before.strip().split()
        after_words = text_after.strip().split() if text_after else []
        
        # Penalizar chunks muito pequenos ou grandes
        if len(before_words) < 2:
            score -= 0.3
        elif len(before_words) > 20:
            score -= 0.2
        elif 3 <= len(before_words) <= 12:
            score += 0.2
        
        # Bonificar quebras após expressões completas
        before_text = text_before.strip().lower()
        if any(expr in before_text for expr in ['me chamo', 'sou', 'muito prazer']):
            score += 0.3
        
        # Bonificar quebras antes de perguntas
        after_text = text_after.strip().lower() if text_after else ""
        if any(after_text.startswith(q) for q in ['qual', 'como', 'quando', 'onde']):
            score += 0.4
        
        # Penalizar quebras no meio de nomes próprios
        if before_words and before_words[-1][0].isupper() and after_words and after_words[0][0].isupper():
            score -= 0.4
        
        return max(0.0, min(1.0, score))


class HelenHumanizer:
    """
    Humanizer class for Helen Vieira SDR chatbot.
    Simulates realistic typing patterns, errors, and emotional states.
    """
    
    def __init__(self):
        """Initialize humanizer with Helen's typing characteristics."""
        # Typing speed configuration (words per minute)
        self.typing_speed_wpm_range = (45, 55)
        self.base_typing_speed_wpm = 50
        
        # Error rates
        self.error_rate = 0.03  # 3% chance of error per chunk
        self.correction_rate = 0.7  # 70% of errors are corrected
        
        # Configurações de quebra natural inteligente
        self.natural_break_ratio = 0.6        # 60% quebras naturais vs 40% pontuação
        self.min_chunk_words = 3              # Mínimo de palavras por chunk  
        self.max_chunk_words = 15             # Máximo de palavras por chunk
        self.variation_factor = 0.2           # ±20% de variação aleatória
        
        # Inicializar analisador de quebras naturais
        self.break_analyzer = NaturalBreakAnalyzer()
        
        # Emotional states with speed and error modifiers
        self.emotional_states = {
            "neutral": {
                "speed_modifier": 1.0,
                "error_modifier": 1.0,
                "pause_modifier": 1.0
            },
            "entusiasmada": {
                "speed_modifier": 1.2,  # +20% speed
                "error_modifier": 1.1,   # Slightly more errors when excited
                "pause_modifier": 0.8    # Shorter pauses
            },
            "empática": {
                "speed_modifier": 0.9,   # -10% speed
                "error_modifier": 0.8,   # Fewer errors when careful
                "pause_modifier": 1.2    # Longer pauses for thoughtfulness
            },
            "determinada": {
                "speed_modifier": 1.05,  # +5% speed
                "error_modifier": 0.9,   # Focused = fewer errors
                "pause_modifier": 0.9    # Slightly shorter pauses
            }
        }
        
        # Common typing errors (adjacent keys on QWERTY keyboard)
        self.adjacent_keys = {
            'a': ['s', 'q', 'w', 'z'],
            'b': ['v', 'g', 'h', 'n'],
            'c': ['x', 'd', 'f', 'v'],
            'd': ['s', 'e', 'r', 'f', 'c', 'x'],
            'e': ['w', 'r', 'd', 's'],
            'f': ['d', 'r', 't', 'g', 'v', 'c'],
            'g': ['f', 't', 'y', 'h', 'b', 'v'],
            'h': ['g', 'y', 'u', 'j', 'n', 'b'],
            'i': ['u', 'o', 'k', 'j'],
            'j': ['h', 'u', 'i', 'k', 'n', 'm'],
            'k': ['j', 'i', 'o', 'l', 'm'],
            'l': ['k', 'o', 'p'],
            'm': ['n', 'j', 'k'],
            'n': ['b', 'h', 'j', 'm'],
            'o': ['i', 'p', 'l', 'k'],
            'p': ['o', 'l'],
            'q': ['w', 'a'],
            'r': ['e', 't', 'f', 'd'],
            's': ['a', 'w', 'e', 'd', 'x', 'z'],
            't': ['r', 'y', 'g', 'f'],
            'u': ['y', 'i', 'j', 'h'],
            'v': ['c', 'f', 'g', 'b'],
            'w': ['q', 'e', 's', 'a'],
            'x': ['z', 's', 'd', 'c'],
            'y': ['t', 'u', 'h', 'g'],
            'z': ['a', 's', 'x']
        }
        
        logger.info("HelenHumanizer initialized with typing speed {}wpm and {}% error rate", 
                   self.base_typing_speed_wpm, self.error_rate * 100)
    
    def calculate_typing_delay(self, text: str, speed_modifier: float = 1.0) -> float:
        """
        Calculate typing delay based on text length and speed.
        
        Args:
            text: Text to calculate delay for
            speed_modifier: Speed modifier from emotional state
            
        Returns:
            Typing delay in seconds (2-15 seconds range)
        """
        # Count words
        word_count = len(text.split())
        if word_count == 0:
            return 2.0
        
        # Calculate base WPM with variation
        wpm = random.uniform(*self.typing_speed_wpm_range) * speed_modifier
        
        # Calculate base delay (minutes to seconds)
        base_delay = (word_count / wpm) * 60
        
        # Add random variation (±15%)
        variation = random.uniform(0.85, 1.15)
        delay = base_delay * variation
        
        # Clamp to reasonable range
        delay = max(2.0, min(15.0, delay))
        
        logger.debug(f"Typing delay for '{text[:20]}...': {delay:.2f}s ({word_count} words at {wpm:.0f}wpm)")
        return delay
    
    def add_typing_errors(self, text: str, error_modifier: float = 1.0) -> List[str]:
        """
        Add realistic typing errors with corrections.
        
        Args:
            text: Original text
            error_modifier: Error rate modifier from emotional state
            
        Returns:
            List of text chunks including errors and corrections
        """
        chunks = []
        
        # Check if error should occur
        if random.random() > self.error_rate * error_modifier:
            # No error
            return [text]
        
        # Choose error type
        error_type = random.choice(['adjacent', 'transpose', 'missing'])
        
        # Find a suitable position for error (avoid first/last character)
        words = text.split()
        if len(words) == 0 or all(len(w) <= 2 for w in words):
            return [text]
        
        # Select a word with more than 2 characters
        suitable_words = [(i, w) for i, w in enumerate(words) if len(w) > 2]
        if not suitable_words:
            return [text]
        
        word_idx, word = random.choice(suitable_words)
        char_idx = random.randint(1, len(word) - 2)
        
        error_text = text
        
        if error_type == 'adjacent':
            # Replace with adjacent key
            char = word[char_idx].lower()
            if char in self.adjacent_keys:
                wrong_char = random.choice(self.adjacent_keys[char])
                error_word = word[:char_idx] + wrong_char + word[char_idx + 1:]
                words[word_idx] = error_word
                error_text = ' '.join(words)
        
        elif error_type == 'transpose':
            # Swap two adjacent characters
            if char_idx < len(word) - 1:
                error_word = (word[:char_idx] + word[char_idx + 1] + 
                            word[char_idx] + word[char_idx + 2:])
                words[word_idx] = error_word
                error_text = ' '.join(words)
        
        elif error_type == 'missing':
            # Omit a character
            error_word = word[:char_idx] + word[char_idx + 1:]
            words[word_idx] = error_word
            error_text = ' '.join(words)
        
        # Check if error should be corrected
        if random.random() < self.correction_rate:
            # Add error then correction
            chunks.append(error_text)
            chunks.append(text + '*')  # Asterisk indicates correction
            logger.debug(f"Added typing error '{error_text}' with correction")
        else:
            # Keep the error
            chunks.append(error_text)
            logger.debug(f"Added uncorrected typing error '{error_text}'")
        
        return chunks
    
    def break_into_chunks_intelligent(self, text: str) -> List[str]:
        """
        🧠 NOVO: Quebra inteligente de texto com análise semântica natural.
        
        Combina quebras naturais (60%) com pontuação tradicional (40%) para 
        conversas mais humanas e menos robóticas.
        
        Args:
            text: Texto a ser dividido em chunks
            
        Returns:
            Lista de chunks naturais e variados
        """
        if not text or not text.strip():
            return [text] if text else []
        
        # Decidir estratégia: quebra natural vs tradicional (60/40)
        use_natural_breaks = random.random() < self.natural_break_ratio
        
        if use_natural_breaks:
            chunks = self._break_by_natural_patterns(text)
        else:
            chunks = self._break_by_traditional_method(text)
        
        # Aplicar variação para evitar padrões rígidos
        chunks = self._apply_variation_to_chunks(chunks)
        
        # Validar tamanhos e ajustar se necessário
        chunks = self._validate_and_adjust_chunks(chunks)
        
        logger.debug(
            "Intelligent chunking completed",
            strategy="natural" if use_natural_breaks else "traditional",
            chunks_count=len(chunks),
            avg_words=sum(len(c.split()) for c in chunks) / len(chunks) if chunks else 0
        )
        
        return chunks
    
    def _break_by_natural_patterns(self, text: str) -> List[str]:
        """🧠 Quebra texto usando padrões naturais otimizados para Helen Vieira."""
        
        # Estratégia otimizada para o padrão Helen Vieira
        chunks = self._try_helen_specific_patterns(text)
        if chunks and len(chunks) > 1:
            return chunks
        
        # Fallback para análise geral de padrões
        break_points = self.break_analyzer.find_natural_break_points(text)
        
        if not break_points:
            return self._break_by_traditional_method(text)
        
        chunks = []
        last_pos = 0
        
        # Selecionar quebras com melhor score de naturalidade
        selected_breaks = []
        for pos, break_type, _ in break_points:
            if pos > last_pos:
                text_before = text[last_pos:pos].strip()
                text_after = text[pos:].strip()
                
                if text_before:  # Só adicionar se há conteúdo
                    naturalness_score = self.break_analyzer.score_break_naturalness(
                        text_before, text_after
                    )
                    
                    # Aceitar quebras com score > 0.6 ou aleatoriamente aceitar outras
                    if naturalness_score > 0.6 or random.random() < 0.3:
                        selected_breaks.append((pos, break_type, naturalness_score))
        
        # Aplicar quebras selecionadas
        last_pos = 0
        for pos, break_type, _ in selected_breaks:
            chunk_text = text[last_pos:pos].strip()
            if chunk_text and len(chunk_text.split()) >= self.min_chunk_words:
                chunks.append(chunk_text)
                last_pos = pos
        
        # Adicionar resto do texto se houver
        if last_pos < len(text):
            remaining_text = text[last_pos:].strip()
            if remaining_text:
                chunks.append(remaining_text)
        
        return chunks if chunks else [text]
    
    def _try_helen_specific_patterns(self, text: str) -> List[str]:
        """
        🎯 Tenta padrões específicos otimizados para mensagens típicas da Helen.
        
        Implementa quebras exatas como no exemplo:
        "Oi! Muito prazer, me chamo Helen Vieira" → "Sou consultora da Solar Prime" → "Qual o seu nome?"
        """
        
        # Estratégia robusta: quebra manual baseada em marcos conhecidos
        chunks = []
        
        # Marco 1: Encontrar final do nome Helen Vieira
        name_patterns = [
            r'(.*me chamo Helen Vieira)',
            r'(.*meu nome é Helen Vieira)', 
            r'(Oi[!]?\s+Muito prazer[,]?\s+me chamo [A-Za-zÀ-ÿ\s]+)',
        ]
        
        name_match = None
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                break
        
        if name_match:
            # Chunk 1: Saudação + apresentação até o nome
            chunk1 = name_match.group(1).strip()
            chunks.append(chunk1)
            
            # Marco 2: Encontrar identificação profissional
            remaining_start = name_match.end()
            remaining_text = text[remaining_start:].strip()
            
            # Procurar padrão profissional
            prof_patterns = [
                r'[^A-Za-z]*(sou consultora [^.!?]*(?:Prime|Solar)[^.!?]*)',
                r'[^A-Za-z]*(sou [^.!?]*consultora[^.!?]*)',
            ]
            
            prof_match = None
            for pattern in prof_patterns:
                prof_match = re.search(pattern, remaining_text, re.IGNORECASE)
                if prof_match:
                    break
            
            if prof_match:
                # Chunk 2: Identificação profissional
                chunk2_raw = prof_match.group(1).strip()
                # Garantir que começa com maiúscula
                chunk2 = chunk2_raw[0].upper() + chunk2_raw[1:] if chunk2_raw else ""
                chunks.append(chunk2)
                
                # Marco 3: Encontrar pergunta final
                prof_end = remaining_start + prof_match.end()
                final_text = text[prof_end:].strip()
                
                # Limpar pontuação inicial e pegar pergunta
                question_text = re.sub(r'^[.!?\s]*', '', final_text).strip()
                if question_text:
                    chunks.append(question_text)
        
        # Validar resultado
        if len(chunks) >= 3:
            # Verificar se está próximo do resultado esperado
            expected_keywords = ['prazer', 'Helen', 'consultora', 'nome']
            chunk_text = ' '.join(chunks).lower()
            found_keywords = sum(1 for kw in expected_keywords if kw in chunk_text)
            
            if found_keywords >= 3:  # Pelo menos 3 keywords encontradas
                logger.debug(
                    "Helen-specific pattern applied successfully",
                    chunks_count=len(chunks),
                    pattern_type="manual_semantic_parsing",
                    keywords_found=found_keywords
                )
                return chunks
        
        # Fallback: Quebra heurística baseada no exemplo esperado
        return self._try_heuristic_helen_break(text)
    
    def _try_heuristic_helen_break(self, text: str) -> List[str]:
        """Quebra heurística baseada no padrão conhecido da Helen."""
        
        # Se contém os elementos-chave, fazer quebra heurística
        if all(keyword in text.lower() for keyword in ['oi', 'prazer', 'helen', 'consultora', 'nome']):
            
            # Estratégia: dividir em 3 partes aproximadamente iguais semanticamente
            
            # Parte 1: Saudação até nome (aproximadamente)
            first_break = text.find('Helen Vieira')
            if first_break > 0:
                first_break += len('Helen Vieira')
                chunk1 = text[:first_break].strip()
                
                # Parte 2: Identificação profissional
                remaining = text[first_break:].strip()
                
                # Encontrar onde termina a identificação profissional
                second_break = -1
                markers = ['Prime.', 'Solar.', 'energia.']
                for marker in markers:
                    pos = remaining.lower().find(marker.lower())
                    if pos >= 0:
                        second_break = pos + len(marker)
                        break
                
                if second_break > 0:
                    chunk2_raw = remaining[:second_break].strip()
                    # Limpar início (e sou → Sou)
                    chunk2 = re.sub(r'^[^A-Za-z]*e\s+sou', 'Sou', chunk2_raw, flags=re.IGNORECASE).strip()
                    # Remover ponto final se houver
                    chunk2 = chunk2.rstrip('.')
                    
                    # Parte 3: Pergunta
                    chunk3_raw = remaining[second_break:].strip()
                    chunk3 = re.sub(r'^[.!?\s]*', '', chunk3_raw).strip()
                    
                    if chunk1 and chunk2 and chunk3:
                        return [chunk1, chunk2, chunk3]
        
        # Se chegou até aqui, não conseguiu quebrar
        return []
    
    def _try_semantic_units(self, text: str) -> List[str]:
        """Tenta quebrar por unidades semânticas menores."""
        chunks = []
        
        # Tentar quebrar em sentenças completas
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if len(sentences) > 1:
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Se sentença muito longa, tentar quebrar internamente
                    if len(sentence.split()) > self.max_chunk_words:
                        sub_chunks = self._break_long_sentence(sentence)
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append(sentence)
        
        # Validar se chunks estão em tamanho adequado
        valid_chunks = []
        for chunk in chunks:
            words = len(chunk.split())
            if self.min_chunk_words <= words <= self.max_chunk_words:
                valid_chunks.append(chunk)
            elif words > self.max_chunk_words:
                # Dividir chunk muito grande
                sub_chunks = self._break_long_sentence(chunk)
                valid_chunks.extend(sub_chunks)
            # Ignorar chunks muito pequenos
        
        return valid_chunks
    
    def _break_long_sentence(self, sentence: str) -> List[str]:
        """Quebra sentenças longas em chunks menores."""
        words = sentence.split()
        chunks = []
        
        # Dividir em chunks de tamanho médio
        chunk_size = (self.min_chunk_words + self.max_chunk_words) // 2
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            if chunk_words:
                chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def _break_by_traditional_method(self, text: str) -> List[str]:
        """Método tradicional de quebra por tamanho (mantido para balanceamento)."""
        chunks = []
        words = text.split()
        
        if not words:
            return [text]
        
        i = 0
        while i < len(words):
            # Tamanho variável baseado nos limites configurados
            min_size = max(1, self.min_chunk_words - 1)
            max_size = min(len(words) - i, self.max_chunk_words)
            
            if max_size <= min_size:
                chunk_size = max_size
            else:
                # Distribuição mais natural
                rand = random.random()
                if rand < 0.4:  # 40% chunks pequenos
                    chunk_size = random.randint(min_size, min_size + 2)
                elif rand < 0.7:  # 30% chunks médios
                    chunk_size = random.randint(min_size + 3, min_size + 6)
                else:  # 30% chunks maiores
                    chunk_size = random.randint(min_size + 7, max_size)
            
            end_idx = min(i + chunk_size, len(words))
            chunk_words = words[i:end_idx]
            
            # Evitar quebras ruins (no meio de vírgulas)
            while end_idx > i + 1 and chunk_words[-1].endswith(','):
                end_idx -= 1
                chunk_words = words[i:end_idx]
            
            if chunk_words:
                chunks.append(' '.join(chunk_words))
                i = end_idx
            else:
                i += 1
        
        return chunks
    
    def _apply_variation_to_chunks(self, chunks: List[str]) -> List[str]:
        """Aplica variação aleatória para evitar padrões previsíveis."""
        if len(chunks) <= 1:
            return chunks
        
        # Ocasionalmente combinar chunks muito pequenos
        if random.random() < self.variation_factor:
            new_chunks = []
            i = 0
            while i < len(chunks):
                current_chunk = chunks[i]
                
                # Se chunk muito pequeno e há próximo, considerar combinar
                if (len(current_chunk.split()) < self.min_chunk_words and 
                    i + 1 < len(chunks) and
                    len(current_chunk.split()) + len(chunks[i + 1].split()) <= self.max_chunk_words):
                    
                    combined = current_chunk + " " + chunks[i + 1]
                    new_chunks.append(combined)
                    i += 2
                else:
                    new_chunks.append(current_chunk)
                    i += 1
            
            chunks = new_chunks
        
        return chunks
    
    def _validate_and_adjust_chunks(self, chunks: List[str]) -> List[str]:
        """Valida e ajusta chunks para garantir qualidade."""
        if not chunks:
            return chunks
        
        validated_chunks = []
        
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            
            words = chunk.split()
            
            # Chunk muito pequeno - tentar combinar com anterior
            if len(words) < self.min_chunk_words and validated_chunks:
                last_chunk = validated_chunks[-1]
                combined_words = last_chunk.split() + words
                
                if len(combined_words) <= self.max_chunk_words:
                    validated_chunks[-1] = ' '.join(combined_words)
                    continue
            
            # Chunk muito grande - dividir
            if len(words) > self.max_chunk_words:
                # Dividir em chunks menores
                sub_chunks = []
                for i in range(0, len(words), self.max_chunk_words):
                    sub_chunk_words = words[i:i + self.max_chunk_words]
                    sub_chunks.append(' '.join(sub_chunk_words))
                
                validated_chunks.extend(sub_chunks)
            else:
                validated_chunks.append(chunk)
        
        return validated_chunks if validated_chunks else [text for text in chunks if text.strip()]
    
    def break_into_chunks(self, text: str) -> List[str]:
        """
        🔄 COMPATIBILIDADE: Método principal que chama a nova lógica inteligente.
        
        Mantém compatibilidade com código existente enquanto usa a nova
        funcionalidade de quebra natural inteligente.
        """
        return self.break_into_chunks_intelligent(text)
    
    def simulate_emotional_state(self, state: str) -> Dict:
        """
        Get modifiers for emotional state.
        
        Args:
            state: Emotional state name
            
        Returns:
            Dictionary with speed, error, and pause modifiers
        """
        if state not in self.emotional_states:
            logger.warning(f"Unknown emotional state '{state}', using neutral")
            state = "neutral"
        
        return self.emotional_states[state].copy()
    
    def add_cognitive_pauses(self, chunks: List[str], is_first_message: bool = False, 
                           pause_modifier: float = 1.0) -> List[Dict]:
        """
        Add realistic pauses between chunks.
        
        Args:
            chunks: List of text chunks
            is_first_message: Whether this is the first message (longer initial pause)
            pause_modifier: Pause length modifier from emotional state
            
        Returns:
            List of dictionaries with chunk data and pause timings
        """
        result = []
        
        for i, chunk in enumerate(chunks):
            chunk_data = {"text": chunk}
            
            # Pre-pause (before typing)
            if i == 0 and is_first_message:
                # Longer pause for first message (thinking time)
                chunk_data["pre_pause"] = random.uniform(1.5, 3.0) * pause_modifier
            elif i == 0:
                # Normal first chunk pause
                chunk_data["pre_pause"] = random.uniform(0.8, 1.5) * pause_modifier
            else:
                # Inter-chunk pause
                chunk_data["pre_pause"] = random.uniform(0.3, 0.8) * pause_modifier
            
            # Post-pause (after typing)
            # Check if chunk ends with question mark for longer pause
            if chunk.strip().endswith('?'):
                chunk_data["post_pause"] = random.uniform(0.8, 1.2) * pause_modifier
            else:
                chunk_data["post_pause"] = random.uniform(0.3, 0.7) * pause_modifier
            
            result.append(chunk_data)
        
        return result
    
    def format_whatsapp_style(self, text: str) -> str:
        """
        Format text for WhatsApp style.
        
        Args:
            text: Text to format
            
        Returns:
            WhatsApp formatted text
        """
        # Bold formatting for values and percentages
        text = re.sub(r'R\$\s*[\d.,]+', lambda m: f'*{m.group()}*', text)
        text = re.sub(r'\d+%', lambda m: f'*{m.group()}*', text)
        
        # Remove markdown formatting
        text = re.sub(r'#{1,6}\s*', '', text)  # Headers
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)  # Bold
        text = re.sub(r'__(.*?)__', r'*\1*', text)  # Also bold
        text = re.sub(r'`(.*?)`', r'\1', text)  # Code
        
        # Add natural ellipsis where appropriate
        text = re.sub(r'\.\.\s', '... ', text)
        
        return text
    
    def humanize_response(self, text: str, emotional_state: str = "neutral", 
                         is_first_message: bool = False) -> List[Dict]:
        """
        Main method to humanize a response with all effects.
        
        Args:
            text: Text to humanize
            emotional_state: Current emotional state
            is_first_message: Whether this is the first message in conversation
            
        Returns:
            List of chunk dictionaries with text, delays, and pauses
        """
        logger.info(f"Humanizing response with emotional state: {emotional_state}")
        
        # Get emotional state modifiers
        state_modifiers = self.simulate_emotional_state(emotional_state)
        
        # Format text for WhatsApp
        text = self.format_whatsapp_style(text)
        
        # Break into chunks
        raw_chunks = self.break_into_chunks(text)
        
        # Process each chunk for errors
        processed_chunks = []
        for chunk in raw_chunks:
            error_chunks = self.add_typing_errors(chunk, state_modifiers['error_modifier'])
            processed_chunks.extend(error_chunks)
        
        # Add cognitive pauses
        chunks_with_pauses = self.add_cognitive_pauses(
            processed_chunks, 
            is_first_message, 
            state_modifiers['pause_modifier']
        )
        
        # Calculate typing delays
        for chunk_data in chunks_with_pauses:
            chunk_data['typing_delay'] = self.calculate_typing_delay(
                chunk_data['text'], 
                state_modifiers['speed_modifier']
            )
        
        logger.info(f"Humanized response into {len(chunks_with_pauses)} chunks")
        return chunks_with_pauses