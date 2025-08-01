"""
Humanizer module for Helen Vieira chatbot.
Provides realistic typing simulation and emotional state handling.
"""

import random
import re
from typing import List, Dict
from loguru import logger


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
    
    def break_into_chunks(self, text: str) -> List[str]:
        """
        Break text into realistic typing chunks.
        
        Args:
            text: Text to break into chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        words = text.split()
        
        if not words:
            return [text]
        
        i = 0
        while i < len(words):
            # Determine chunk size with realistic distribution
            rand = random.random()
            if rand < 0.4:  # 40% very short (1-3 words)
                chunk_size = random.randint(1, 3)
            elif rand < 0.7:  # 30% short (4-7 words)
                chunk_size = random.randint(4, 7)
            else:  # 30% medium (8-12 words)
                chunk_size = random.randint(8, 12)
            
            # Don't break at commas or certain punctuation
            end_idx = min(i + chunk_size, len(words))
            chunk_words = words[i:end_idx]
            
            # Adjust chunk to not end with comma
            while end_idx > i + 1 and chunk_words[-1].endswith(','):
                end_idx -= 1
                chunk_words = words[i:end_idx]
            
            if chunk_words:
                chunks.append(' '.join(chunk_words))
                i = end_idx
            else:
                i += 1
        
        logger.debug(f"Broke text into {len(chunks)} chunks")
        return chunks
    
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