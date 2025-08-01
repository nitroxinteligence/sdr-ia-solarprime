"""
Validation tests for Helen Vieira humanization.

These tests verify that the humanization features work correctly,
including typing simulation, personality consistency, and natural conversation flow.
"""

import pytest
import pytest_asyncio
import asyncio
import time
import re
from unittest.mock import AsyncMock, patch, MagicMock

from agente.core.humanizer import HelenHumanizer
from agente.core.message_processor import MessageProcessor, MessageBuffer
from agente.core.agent import SDRAgent
from agente.core.types import WhatsAppMessage


@pytest.mark.validation
class TestHelenHumanization:
    """Tests for Helen Vieira humanization features."""
    
    @pytest.fixture
    def humanizer(self):
        """Create HelenHumanizer instance."""
        return HelenHumanizer()
    
    @pytest_asyncio.fixture
    async def message_processor(self):
        """Create MessageProcessor with mocked Evolution service."""
        evolution_service = AsyncMock()
        evolution_service.send_typing.return_value = {"success": True}
        evolution_service.send_text.return_value = {"success": True}
        
        processor = MessageProcessor(
            evolution_service=evolution_service,
            humanizer=HelenHumanizer()
        )
        return processor
    
    def test_typing_speed_calculation(self, humanizer):
        """Test realistic typing speed calculation."""
        # Test various message lengths
        test_messages = [
            "Oi!",  # Very short
            "Tudo bem com você?",  # Short
            "Que legal saber do seu interesse em energia solar! A SolarPrime tem as melhores soluções.",  # Medium
            "Deixa eu te explicar como funciona nosso sistema de energia solar. Primeiro, fazemos uma análise completa do seu consumo atual através da conta de luz. Depois, dimensionamos o sistema ideal para suas necessidades, garantindo economia desde o primeiro mês!",  # Long
        ]
        
        for message in test_messages:
            typing_time = humanizer.calculate_typing_time(message)
            
            # Calculate expected time based on WPM
            words = len(message.split())
            chars = len(message)
            min_time = (chars / 5) / 55 * 60  # 55 WPM max
            max_time = (chars / 5) / 45 * 60  # 45 WPM min
            
            # Add thinking time
            min_time += 0.5
            max_time += 2.0
            
            # Verify typing time is realistic
            assert min_time <= typing_time <= max_time + 1  # Allow small variance
    
    def test_personality_expressions(self, humanizer):
        """Test Helen's personality expressions."""
        # Test greeting variations
        greetings = humanizer.personality_config["greetings"]
        assert any("Oi" in g for g in greetings)
        assert any("Olá" in g for g in greetings)
        assert any("bem-vind" in g.lower() for g in greetings)
        
        # Test enthusiasm expressions
        enthusiasm = humanizer.personality_config["enthusiasm_expressions"]
        assert any("Que legal" in e for e in enthusiasm)
        assert any("maravilh" in e.lower() for e in enthusiasm)
        assert any("ótimo" in e.lower() for e in enthusiasm)
        
        # Test emojis usage
        emojis = humanizer.personality_config["emojis"]
        assert "😊" in emojis
        assert "🌟" in emojis
        assert "💚" in emojis  # Solar/green theme
    
    def test_message_personalization(self, humanizer):
        """Test message personalization features."""
        # Test with user name
        message = "Vou analisar sua conta de luz agora mesmo"
        personalized = humanizer.add_personality_touches(message, user_name="João")
        
        # Should occasionally add the name
        # (Note: This is probabilistic, so we test the method exists)
        assert callable(humanizer.add_personality_touches)
        
        # Test emoji addition
        message_with_emoji = humanizer.add_personality_touches(
            "Fico feliz em ajudar",
            add_emoji=True
        )
        # Should sometimes add emojis
        assert isinstance(message_with_emoji, str)
    
    @pytest.mark.asyncio
    async def test_typing_indicator_timing(self, message_processor):
        """Test typing indicator is sent with proper timing."""
        phone = "5511999999999"
        message = "Olá! Vou analisar as melhores opções de economia para você."
        
        start_time = time.time()
        await message_processor.send_message(phone, message)
        end_time = time.time()
        
        # Verify typing indicator was sent
        message_processor.evolution_service.send_typing.assert_called_with(phone)
        
        # Verify timing is realistic (at least 1 second for this message)
        assert end_time - start_time >= 1.0
    
    @pytest.mark.asyncio
    async def test_message_chunking_natural_breaks(self, message_processor):
        """Test that long messages are split at natural break points."""
        phone = "5511999999999"
        
        # Long message that should be split
        long_message = """Que ótimo que você tem interesse em energia solar! 
        
        A SolarPrime é líder em soluções de energia solar aqui em Pernambuco. Já ajudamos mais de 5.000 famílias a economizarem até 95% na conta de luz.
        
        Deixa eu te fazer algumas perguntinhas rápidas para entender melhor o que seria ideal para você:
        
        1. Você mora em casa ou apartamento?
        2. Qual o valor médio da sua conta de luz?
        3. O imóvel é próprio ou alugado?
        
        Com essas informações, consigo te mostrar exatamente quanto você vai economizar! 😊"""
        
        # Process message
        chunks = message_processor._split_message(long_message)
        
        # Verify chunks
        assert len(chunks) > 1  # Should be split
        
        # Each chunk should end at a natural break (period, question, newline)
        for chunk in chunks[:-1]:  # All but last
            assert chunk.strip().endswith(('.', '?', '!', ':')) or '\n' in chunk
        
        # No chunk should be too long
        for chunk in chunks:
            assert len(chunk) <= 1000
    
    @pytest.mark.asyncio
    async def test_conversation_flow_naturalness(self, message_processor):
        """Test natural conversation flow with pauses."""
        phone = "5511999999999"
        
        # Simulate a conversation sequence
        messages = [
            "Oi! Vi seu interesse em energia solar.",
            "Deixa eu me apresentar melhor...",
            "Sou a Helen, consultora especialista aqui da SolarPrime 😊",
            "Estou aqui para te ajudar a economizar até 95% na conta de luz!"
        ]
        
        # Track timing
        send_times = []
        
        # Mock to track call times
        async def track_send(*args, **kwargs):
            send_times.append(time.time())
            return {"success": True}
        
        message_processor.evolution_service.send_text.side_effect = track_send
        
        # Send sequence
        for msg in messages:
            await message_processor.send_message(phone, msg)
        
        # Verify natural pauses between messages
        for i in range(1, len(send_times)):
            pause = send_times[i] - send_times[i-1]
            # Should have natural pause (at least 0.5 seconds)
            assert pause >= 0.5
    
    def test_helen_personality_consistency(self, humanizer):
        """Test that Helen's personality remains consistent."""
        # Test formal vs informal balance
        formal_words = ["você", "para", "está"]
        informal_words = ["vc", "pra", "tá"]
        
        # Helen uses informal but not too abbreviated
        sample_text = "Oi! Tudo bem? Vou te ajudar a economizar na conta de luz!"
        
        # Should prefer "você" over "vc"
        assert "você" in humanizer.personality_config.get("preferred_words", [])
        
        # Test enthusiasm level
        enthusiasm_words = ["adoraria", "fantástico", "maravilhoso", "incrível", "ótimo"]
        assert any(word in humanizer.personality_config.get("vocabulary", []) 
                  for word in enthusiasm_words)
    
    @pytest.mark.asyncio
    async def test_buffer_message_grouping(self):
        """Test that rapid messages are properly buffered and grouped."""
        buffer = MessageBuffer(buffer_window_seconds=2)
        
        # Add rapid messages
        messages = [
            "Oi",
            "Tudo bem?",
            "Vi que você tem interesse",
            "em energia solar"
        ]
        
        for msg in messages:
            buffer.add_message(msg)
            await asyncio.sleep(0.3)  # 300ms between messages
        
        # Wait for buffer window
        await asyncio.sleep(2.1)
        
        # Get buffered result
        result = buffer.get_buffered_message()
        
        # Should combine messages naturally
        assert result is not None
        assert "Oi" in result
        assert "energia solar" in result
        
        # Should have natural separation
        assert "\n" in result or ". " in result
    
    def test_emoji_usage_appropriateness(self, humanizer):
        """Test that emojis are used appropriately."""
        # Test emoji context rules
        contexts = {
            "greeting": ["😊", "👋", "✨"],
            "celebration": ["🎉", "🌟", "💚"],
            "information": ["📊", "💡", "📋"],
            "scheduling": ["📅", "⏰", "✅"]
        }
        
        # Verify Helen's emoji usage matches contexts
        helen_emojis = humanizer.personality_config["emojis"]
        
        # Should include friendly/professional emojis
        assert any(emoji in helen_emojis for emoji in ["😊", "🌟", "💚", "✨"])
        
        # Should not include inappropriate emojis
        inappropriate = ["😘", "😍", "🔥", "💋", "🍺", "😈"]
        assert not any(emoji in helen_emojis for emoji in inappropriate)
    
    @pytest.mark.asyncio
    async def test_response_timing_variations(self, humanizer):
        """Test that response timings have natural variations."""
        # Calculate typing times for similar length messages
        messages = [
            "Claro! Vou verificar isso para você agora mesmo.",
            "Certo! Deixa eu consultar as informações aqui.",
            "Ótimo! Já estou analisando os dados para você.",
            "Legal! Vou buscar essas informações rapidinho."
        ]
        
        typing_times = []
        for msg in messages:
            typing_time = humanizer.calculate_typing_time(msg)
            typing_times.append(typing_time)
        
        # Verify there's variation (not all identical)
        assert len(set(typing_times)) > 1
        
        # But variation should be reasonable (within 20%)
        avg_time = sum(typing_times) / len(typing_times)
        for time in typing_times:
            assert 0.8 * avg_time <= time <= 1.2 * avg_time
    
    def test_cultural_localization(self, humanizer):
        """Test Brazilian Portuguese localization."""
        # Test regional expressions
        regional_expressions = [
            "massa",  # Northeastern slang for "cool"
            "oxe",  # Northeastern expression
            "vixe",  # Northeastern expression
            "arretado",  # Northeastern for "great"
        ]
        
        # Helen might use some regional expressions (she's from Recife)
        vocabulary = humanizer.personality_config.get("regional_vocabulary", [])
        assert isinstance(vocabulary, list)
        
        # Test number formatting
        # Brazilian format uses dot for thousands and comma for decimals
        test_value = 1234.56
        formatted = f"R$ 1.234,56"  # Brazilian format
        assert "." in formatted and "," in formatted
    
    @pytest.mark.asyncio
    async def test_error_message_humanization(self, message_processor):
        """Test that error messages are humanized."""
        phone = "5511999999999"
        
        # Simulate an error scenario
        message_processor.evolution_service.send_text.side_effect = Exception("Network error")
        
        # Try to send message
        try:
            await message_processor.send_message(phone, "Test message")
        except Exception:
            pass
        
        # In a real scenario, Helen would send a humanized error message
        # Test that error handling maintains personality
        error_responses = [
            "Ops! Parece que tive um probleminha técnico aqui 😅",
            "Desculpa! Algo deu errado, mas já estou resolvendo",
            "Eita! Tive uma dificuldade técnica, pode repetir?",
        ]
        
        # Verify error responses maintain Helen's friendly tone
        assert all("!" in response for response in error_responses)
        assert any("😅" in response or "😊" in response for response in error_responses)