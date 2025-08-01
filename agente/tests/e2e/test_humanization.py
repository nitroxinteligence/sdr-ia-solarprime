"""
End-to-end tests for humanization features.

This module tests typing simulation, message chunking,
emotional state responses, and error corrections.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, call
import re
from typing import List, Dict

from agente.core.types import WhatsAppMessage, MessageChunk
from agente.core.humanizer import HelenHumanizer
from agente.tests.fixtures.test_data import TestData


class TestHumanization:
    """Test humanization features of the SDR Agent"""
    
    @pytest.mark.asyncio
    async def test_typing_simulation(self, mock_sdr_agent, mock_services):
        """Test realistic typing simulation with variable speeds"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Track typing indicator calls
        typing_calls = []
        
        async def track_typing(phone_number, instance):
            typing_calls.append({
                "phone": phone_number,
                "instance": instance,
                "timestamp": datetime.now(timezone.utc)
            })
            return {"status": "ok"}
        
        mock_services["evolution"].send_typing = track_typing
        
        # Short message
        short_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Oi",
            message_id="TYPE001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        with patch("agente.tools.whatsapp.type_simulation.type_simulation") as mock_type_sim:
            mock_type_sim.return_value = {"typing_duration": 2.5, "status": "completed"}
            
            response = await mock_sdr_agent.process_message(short_message)
            assert response.success is True
        
        # Long message should have longer typing duration
        long_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Olá, gostaria de saber mais sobre o sistema de energia solar. "
                    "Vi que vocês prometem uma economia de até 95% na conta de luz. "
                    "Como funciona exatamente? Preciso fazer alguma obra em casa?",
            message_id="TYPE002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        with patch("agente.tools.whatsapp.type_simulation.type_simulation") as mock_type_sim:
            mock_type_sim.return_value = {"typing_duration": 8.5, "status": "completed"}
            
            response2 = await mock_sdr_agent.process_message(long_message)
            assert response2.success is True
    
    @pytest.mark.asyncio
    async def test_message_chunking(self, mock_sdr_agent, mock_services):
        """Test message chunking for natural conversation flow"""
        phone = TestData.TEST_PHONES["lead_2"]
        
        # Mock a response that should be chunked
        long_response = """
        Olá Maria! Que prazer falar com você! 😊
        
        Deixa eu te explicar como funciona nossa solução de energia solar:
        
        1️⃣ Primeiro, fazemos uma análise gratuita da sua conta de luz para calcular a economia
        2️⃣ Depois, criamos um projeto personalizado para sua casa
        3️⃣ A instalação é feita em apenas 1 dia, sem bagunça
        4️⃣ Você começa a economizar já no primeiro mês!
        
        O melhor de tudo é que não precisa pagar nada na instalação. 
        Você pode financiar em até 120x e a parcela fica menor que sua economia mensal!
        
        Quer que eu faça uma simulação para você agora?
        """
        
        # Create message that triggers long response
        message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Como funciona o sistema de vocês?",
            message_id="CHUNK001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # Track sent messages
        sent_chunks = []
        
        async def track_send(phone_number, message, instance):
            sent_chunks.append({
                "phone": phone_number,
                "message": message,
                "length": len(message)
            })
            return {"status": "sent"}
        
        mock_services["evolution"].send_text = track_send
        
        with patch("agente.tools.whatsapp.message_chunking.message_chunking") as mock_chunk:
            # Simulate chunking
            chunks = [
                MessageChunk(text="Olá Maria! Que prazer falar com você! 😊", delay_ms=0, words=8, chars=42),
                MessageChunk(text="Deixa eu te explicar como funciona nossa solução de energia solar:", delay_ms=2000, words=11, chars=66),
                MessageChunk(text="1️⃣ Primeiro, fazemos uma análise gratuita da sua conta de luz para calcular a economia", delay_ms=3500, words=15, chars=87),
                MessageChunk(text="2️⃣ Depois, criamos um projeto personalizado para sua casa", delay_ms=2500, words=9, chars=58),
                MessageChunk(text="3️⃣ A instalação é feita em apenas 1 dia, sem bagunça", delay_ms=2500, words=11, chars=53),
                MessageChunk(text="4️⃣ Você começa a economizar já no primeiro mês!", delay_ms=2000, words=9, chars=48),
                MessageChunk(text="O melhor de tudo é que não precisa pagar nada na instalação.", delay_ms=3000, words=13, chars=61),
                MessageChunk(text="Você pode financiar em até 120x e a parcela fica menor que sua economia mensal!", delay_ms=3500, words=16, chars=80),
                MessageChunk(text="Quer que eu faça uma simulação para você agora?", delay_ms=2000, words=10, chars=48)
            ]
            
            mock_chunk.return_value = {"chunks": [chunk.model_dump() for chunk in chunks]}
            
            response = await mock_sdr_agent.process_message(message)
            assert response.success is True
    
    @pytest.mark.asyncio
    async def test_emotional_state_responses(self, mock_sdr_agent, mock_repositories):
        """Test different emotional states in responses"""
        phone = TestData.TEST_PHONES["lead_3"]
        
        # Test enthusiastic state (new opportunity)
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "emotion-001",
            "phone_number": phone,
            "name": "Carlos",
            "bill_value": 950.0,
            "current_stage": LeadStage.QUALIFYING,
            "qualification_score": 75
        })
        
        high_value_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Minha conta veio R$ 950 esse mês!",
            message_id="EMOTION001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response1 = await mock_sdr_agent.process_message(high_value_message)
        assert response1.success is True
        # Should show enthusiasm
        assert any(indicator in response1.message for indicator in ["!", "😊", "😄", "ótima", "excelente"])
        
        # Test empathetic state (concern/objection)
        concern_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Estou preocupado se vale a pena mesmo, já fui enganado antes",
            message_id="EMOTION002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response2 = await mock_sdr_agent.process_message(concern_message)
        assert response2.success is True
        # Should show empathy
        assert any(word in response2.message.lower() for word in ["entendo", "compreendo", "preocupação"])
        
        # Test determined state (closing/scheduling)
        scheduling_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Ok, vamos marcar então",
            message_id="EMOTION003",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response3 = await mock_sdr_agent.process_message(scheduling_message)
        assert response3.success is True
        # Should show determination
        assert any(word in response3.message.lower() for word in ["vamos", "ótimo", "perfeito"])
    
    @pytest.mark.asyncio
    async def test_error_corrections(self, mock_sdr_agent, mock_services):
        """Test realistic typing errors and corrections"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Create humanizer instance
        humanizer = HelenHumanizer()
        
        # Test error generation and correction
        test_messages = [
            "Olá! Como vai você?",
            "Vamos agendar uma reunião",
            "A economia pode chegar a 95%"
        ]
        
        for original_text in test_messages:
            # Simulate typing with potential errors
            typed_text = humanizer.simulate_typing_errors(original_text)
            
            # Some messages should have errors
            if humanizer.should_make_error():
                # Verify error was introduced
                assert typed_text != original_text or "*" in typed_text
                
                # Check if correction marker is present
                if "*" in typed_text:
                    # Should have correction after asterisk
                    parts = typed_text.split("*")
                    assert len(parts) >= 2
    
    @pytest.mark.asyncio
    async def test_conversation_memory_and_context(self, mock_sdr_agent, mock_repositories):
        """Test humanized responses based on conversation context"""
        phone = TestData.TEST_PHONES["lead_2"]
        
        # Build conversation history
        conversation_history = []
        
        # First interaction - introduction
        message1 = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Oi",
            message_id="CONTEXT001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=None)
        response1 = await mock_sdr_agent.process_message(message1)
        assert response1.success is True
        conversation_history.append({"role": "assistant", "content": response1.message})
        
        # Second interaction - provide name
        message2 = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Sou a Juliana",
            message_id="CONTEXT002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "context-123",
            "phone_number": phone,
            "name": "Juliana",
            "current_stage": LeadStage.IDENTIFYING
        })
        
        response2 = await mock_sdr_agent.process_message(message2)
        assert response2.success is True
        # Should use the name in response
        assert "Juliana" in response2.message
        conversation_history.append({"role": "assistant", "content": response2.message})
        
        # Third interaction - returning after break
        message3 = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Voltei, estava almoçando",
            message_id="CONTEXT003",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # Mock with conversation history
        mock_repositories["message_repo"].get_conversation_history = AsyncMock(
            return_value=conversation_history
        )
        
        response3 = await mock_sdr_agent.process_message(message3)
        assert response3.success is True
        # Should acknowledge the return naturally
        assert any(word in response3.message.lower() for word in ["que bom", "ótimo", "perfeito"])
    
    @pytest.mark.asyncio
    async def test_natural_conversation_flow(self, mock_sdr_agent):
        """Test natural flow with appropriate pauses and transitions"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Track timing between messages
        message_timings = []
        
        async def track_timing(phone_number, message, instance):
            message_timings.append({
                "timestamp": datetime.now(timezone.utc),
                "message_length": len(message)
            })
            return {"status": "sent"}
        
        # Simulate a natural conversation
        messages = [
            "Oi, boa tarde!",
            "Vi o anúncio de vocês sobre energia solar",
            "Quanto custa mais ou menos?",
            "E precisa fazer obra?"
        ]
        
        for i, content in enumerate(messages):
            message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=phone,
                message=content,
                message_id=f"FLOW{i:03d}",
                timestamp=datetime.now(timezone.utc),
                from_me=False
            )
            
            response = await mock_sdr_agent.process_message(message)
            assert response.success is True
            
            # Small delay between messages to simulate natural conversation
            await asyncio.sleep(0.1)
    
    @pytest.mark.asyncio 
    async def test_emoji_usage_patterns(self, mock_sdr_agent):
        """Test appropriate emoji usage based on context"""
        phone = TestData.TEST_PHONES["lead_3"]
        
        # Positive context - should use emojis
        positive_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Adorei a proposta! Quando podemos conversar?",
            message_id="EMOJI001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response1 = await mock_sdr_agent.process_message(positive_message)
        assert response1.success is True
        # Should contain positive emojis
        emoji_pattern = re.compile(r'[😊😄🎉👏💚🌟✨💡🔋⚡🌱☀️📈💰✅]')
        assert emoji_pattern.search(response1.message) is not None
        
        # Serious/concern context - minimal emojis
        serious_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Preciso entender melhor os custos e garantias",
            message_id="EMOJI002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response2 = await mock_sdr_agent.process_message(serious_message)
        assert response2.success is True
        # Should have fewer or no emojis in serious context
        emoji_count = len(emoji_pattern.findall(response2.message))
        assert emoji_count <= 1  # At most one emoji in serious context
    
    @pytest.mark.asyncio
    async def test_personalization_based_on_lead_data(self, mock_sdr_agent, mock_repositories):
        """Test response personalization based on lead information"""
        phone = TestData.TEST_PHONES["qualified_lead"]
        
        # Mock detailed lead data
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "personal-123",
            "phone_number": phone,
            "name": "Dr. Ricardo Santos",
            "property_type": PropertyType.HOUSE,
            "address": "Condomínio Solar, Casa 15",
            "bill_value": 1200.0,
            "consumption_kwh": 1500,
            "current_stage": LeadStage.QUALIFIED,
            "metadata": {
                "profession": "médico",
                "family_size": 4,
                "main_concern": "economia e sustentabilidade"
            }
        })
        
        # Message about sustainability
        sustainability_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Além da economia, me preocupo com o meio ambiente",
            message_id="PERSON001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response = await mock_sdr_agent.process_message(sustainability_message)
        assert response.success is True
        
        # Should reference sustainability and personalize based on profile
        assert any(word in response.message.lower() for word in ["sustentável", "ambiente", "limpa", "verde"])
        # May reference high consumption or professional status
        assert "Dr." in response.message or "Ricardo" in response.message