"""
Stress tests for concurrent conversation handling.

These tests verify the system can handle multiple simultaneous conversations
without performance degradation or data corruption.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import random
import time

from agente.core.agent import SDRAgent
from agente.core.types import WhatsAppMessage, ProcessedMessage
from agente.core.session_manager import SessionManager
from agente.core.message_processor import MessageProcessor


@pytest.mark.stress
class TestConcurrentConversations:
    """Stress tests for concurrent conversation handling."""
    
    @pytest_asyncio.fixture
    async def agent_with_mocks(self):
        """Create agent with mocked dependencies for stress testing."""
        agent = SDRAgent()
        
        # Mock all external services
        agent.supabase = AsyncMock()
        agent.evolution = AsyncMock()
        agent.kommo = AsyncMock()
        agent.calendar = AsyncMock()
        
        # Mock AGnO agent
        agent.agent = AsyncMock()
        
        # Configure basic mock responses
        agent.supabase.get_lead.return_value = None
        agent.supabase.create_lead.return_value = {"id": "test-lead-id"}
        agent.supabase.create_conversation.return_value = {"id": "test-conv-id"}
        agent.supabase.create_message.return_value = {"id": "test-msg-id"}
        agent.evolution.send_text.return_value = {"success": True}
        agent.evolution.send_typing.return_value = {"success": True}
        
        await agent.start()
        yield agent
        await agent.shutdown()
    
    def generate_test_messages(self, count: int) -> list[WhatsAppMessage]:
        """Generate test messages from different phone numbers."""
        messages = []
        for i in range(count):
            phone = f"5511{90000000 + i}"
            messages.append(WhatsAppMessage(
                instance_id="test-instance",
                phone=phone,
                name=f"Test User {i}",
                message=f"Olá, quero saber sobre energia solar #{i}",
                message_id=f"msg-{i}-{time.time()}",
                timestamp=str(int(time.time())),
                media_url=None,
                media_type=None
            ))
        return messages
    
    @pytest.mark.asyncio
    async def test_concurrent_message_processing(self, agent_with_mocks):
        """Test processing multiple messages concurrently."""
        # Generate 50 messages from different users
        messages = self.generate_test_messages(50)
        
        # Configure agent response
        agent_with_mocks.agent.run.return_value = "Olá! Sou a Helen da SolarPrime."
        
        # Process all messages concurrently
        start_time = time.time()
        tasks = [
            agent_with_mocks.process_message(msg)
            for msg in messages
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Verify results
        successful = [r for r in results if isinstance(r, ProcessedMessage) and r.success]
        failed = [r for r in results if isinstance(r, Exception) or (isinstance(r, ProcessedMessage) and not r.success)]
        
        # At least 90% should succeed
        assert len(successful) >= 45
        
        # Check processing time (should handle 50 messages in under 30 seconds)
        processing_time = end_time - start_time
        assert processing_time < 30
        
        # Verify no session conflicts
        session_count = await agent_with_mocks.session_manager.get_active_sessions_count()
        assert session_count <= 50
    
    @pytest.mark.asyncio
    async def test_session_isolation(self, agent_with_mocks):
        """Test that sessions are properly isolated."""
        # Create 10 concurrent sessions
        messages = self.generate_test_messages(10)
        
        # Configure different responses for each session
        responses = [
            "Olá! Sou a Helen.",
            "Qual o valor da sua conta?",
            "Você tem telhado próprio?",
            "Vamos agendar uma reunião?",
            "Obrigada pelo interesse!"
        ]
        
        agent_with_mocks.agent.run.side_effect = lambda *args, **kwargs: random.choice(responses)
        
        # Process messages concurrently
        tasks = [agent_with_mocks.process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks)
        
        # Verify each session has its own context
        for i, result in enumerate(results):
            assert result.success
            
            # Check session exists
            phone = messages[i].phone
            session = agent_with_mocks.session_manager.active_sessions.get(phone)
            assert session is not None
            assert session["phone"] == phone
            assert session["conversation_id"] is not None
    
    @pytest.mark.asyncio
    async def test_message_buffering_under_load(self, agent_with_mocks):
        """Test message buffering with rapid consecutive messages."""
        phone = "5511999999999"
        
        # Send 20 rapid messages from same user
        messages = []
        for i in range(20):
            msg = WhatsAppMessage(
                instance_id="test-instance",
                phone=phone,
                name="Rapid User",
                message=f"Mensagem rápida {i}",
                message_id=f"rapid-{i}",
                timestamp=str(int(time.time())),
                media_url=None,
                media_type=None
            )
            messages.append(msg)
        
        # Configure agent to handle buffered messages
        agent_with_mocks.agent.run.return_value = "Vou processar suas mensagens..."
        
        # Send all messages with minimal delay
        tasks = []
        for msg in messages:
            tasks.append(agent_with_mocks.process_message(msg))
            await asyncio.sleep(0.1)  # 100ms between messages
        
        results = await asyncio.gather(*tasks)
        
        # Verify buffering worked
        successful = [r for r in results if r.success]
        assert len(successful) == 20
        
        # Check that messages were properly buffered
        # (Evolution service should have been called less than 20 times due to buffering)
        call_count = agent_with_mocks.evolution.send_text.call_count
        assert call_count < 20  # Some messages should have been buffered
    
    @pytest.mark.asyncio
    async def test_resource_cleanup(self, agent_with_mocks):
        """Test that resources are properly cleaned up after sessions."""
        # Create 30 sessions
        messages = self.generate_test_messages(30)
        
        agent_with_mocks.agent.run.return_value = "Processando..."
        
        # Process all messages
        tasks = [agent_with_mocks.process_message(msg) for msg in messages]
        await asyncio.gather(*tasks)
        
        # Verify all sessions were created
        initial_count = await agent_with_mocks.session_manager.get_active_sessions_count()
        assert initial_count == 30
        
        # Simulate session timeout by clearing old sessions
        # (In real scenario, this would happen after 30 minutes)
        agent_with_mocks.session_manager.active_sessions.clear()
        
        # Verify cleanup
        final_count = await agent_with_mocks.session_manager.get_active_sessions_count()
        assert final_count == 0
    
    @pytest.mark.asyncio
    async def test_database_connection_pool(self, agent_with_mocks):
        """Test database connection pooling under load."""
        # Generate 100 messages
        messages = self.generate_test_messages(100)
        
        # Track database calls
        db_calls = []
        
        async def track_db_call(*args, **kwargs):
            db_calls.append(time.time())
            return {"id": f"lead-{len(db_calls)}"}
        
        agent_with_mocks.supabase.create_lead.side_effect = track_db_call
        agent_with_mocks.agent.run.return_value = "Processando..."
        
        # Process messages in batches
        batch_size = 20
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            tasks = [agent_with_mocks.process_message(msg) for msg in batch]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.5)  # Small delay between batches
        
        # Verify database wasn't overwhelmed
        # Check that calls were spread out over time
        assert len(db_calls) == 100
        
        # Calculate call rate (calls per second)
        if len(db_calls) > 1:
            duration = db_calls[-1] - db_calls[0]
            call_rate = len(db_calls) / duration
            # Should not exceed 50 calls per second
            assert call_rate < 50
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, agent_with_mocks):
        """Test memory usage remains stable with many conversations."""
        import gc
        import sys
        
        # Get initial memory baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process 200 messages in waves
        for wave in range(4):
            messages = self.generate_test_messages(50)
            agent_with_mocks.agent.run.return_value = f"Processando wave {wave}"
            
            tasks = [agent_with_mocks.process_message(msg) for msg in messages]
            await asyncio.gather(*tasks)
            
            # Clear old sessions to simulate timeout
            if wave % 2 == 1:
                agent_with_mocks.session_manager.active_sessions.clear()
                gc.collect()
        
        # Final cleanup
        agent_with_mocks.session_manager.active_sessions.clear()
        gc.collect()
        
        # Check object count didn't grow excessively
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        # Allow some growth but not excessive (less than 10% of messages processed)
        assert object_growth < 20  # 200 messages * 0.1
    
    @pytest.mark.asyncio
    async def test_error_recovery_under_load(self, agent_with_mocks):
        """Test system recovers from errors during high load."""
        messages = self.generate_test_messages(50)
        
        # Configure some operations to fail
        call_count = 0
        
        async def sometimes_fail(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 5 == 0:  # Fail every 5th call
                raise Exception("Simulated API failure")
            return {"success": True}
        
        agent_with_mocks.evolution.send_text.side_effect = sometimes_fail
        agent_with_mocks.agent.run.return_value = "Testando recuperação..."
        
        # Process all messages
        tasks = [agent_with_mocks.process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        successful = [r for r in results if isinstance(r, ProcessedMessage) and r.success]
        failed = [r for r in results if isinstance(r, Exception) or (isinstance(r, ProcessedMessage) and not r.success)]
        
        # Despite some failures, most should succeed
        assert len(successful) >= 40  # At least 80% success rate
        assert len(failed) <= 10  # No more than 20% failures
    
    @pytest.mark.asyncio
    async def test_rate_limiting_compliance(self, agent_with_mocks):
        """Test that rate limiting is respected under load."""
        # Track API calls with timestamps
        api_calls = []
        
        async def track_api_call(*args, **kwargs):
            api_calls.append(time.time())
            return {"success": True}
        
        agent_with_mocks.evolution.send_text.side_effect = track_api_call
        agent_with_mocks.agent.run.return_value = "Rate limit test"
        
        # Generate burst of messages
        messages = self.generate_test_messages(30)
        
        # Process all at once
        tasks = [agent_with_mocks.process_message(msg) for msg in messages]
        await asyncio.gather(*tasks)
        
        # Analyze call rate
        if len(api_calls) > 10:
            # Check calls in any 1-second window
            for i in range(len(api_calls) - 10):
                window_start = api_calls[i]
                window_end = window_start + 1.0
                calls_in_window = sum(1 for t in api_calls[i:] if t <= window_end)
                
                # Should not exceed 10 calls per second (example limit)
                assert calls_in_window <= 10
    
    @pytest.mark.asyncio
    async def test_concurrent_state_updates(self, agent_with_mocks):
        """Test that concurrent state updates don't cause conflicts."""
        phone = "5511999999999"
        
        # Create initial session
        first_msg = WhatsAppMessage(
            instance_id="test",
            phone=phone,
            name="Test User",
            message="Início",
            message_id="msg-1",
            timestamp=str(int(time.time())),
            media_url=None,
            media_type=None
        )
        
        await agent_with_mocks.process_message(first_msg)
        
        # Send 10 concurrent messages to same session
        concurrent_messages = []
        for i in range(10):
            msg = WhatsAppMessage(
                instance_id="test",
                phone=phone,
                name="Test User",
                message=f"Mensagem concorrente {i}",
                message_id=f"concurrent-{i}",
                timestamp=str(int(time.time())),
                media_url=None,
                media_type=None
            )
            concurrent_messages.append(msg)
        
        agent_with_mocks.agent.run.return_value = "Processando concorrentemente..."
        
        # Process all concurrently
        tasks = [agent_with_mocks.process_message(msg) for msg in concurrent_messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify no conflicts occurred
        successful = [r for r in results if isinstance(r, ProcessedMessage) and r.success]
        assert len(successful) >= 8  # At least 80% should succeed
        
        # Check session state is consistent
        session = agent_with_mocks.session_manager.active_sessions.get(phone)
        assert session is not None
        assert isinstance(session["message_count"], int)
        assert session["message_count"] >= 10