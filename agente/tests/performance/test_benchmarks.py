"""
Performance benchmark tests for the SDR Agent.

These tests measure and validate performance metrics including:
- Response time
- Throughput
- Resource usage
- API call efficiency
"""

import pytest
import pytest_asyncio
import asyncio
import time
import statistics
from unittest.mock import AsyncMock, patch
import psutil
import gc

from agente.core.agent import SDRAgent
from agente.core.types import WhatsAppMessage
from agente.core.humanizer import HelenHumanizer
from agente.core.message_processor import MessageProcessor


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest_asyncio.fixture
    async def agent_for_benchmarks(self):
        """Create agent with controlled mocks for benchmarking."""
        agent = SDRAgent()
        
        # Mock external services with minimal latency
        agent.supabase = AsyncMock()
        agent.evolution = AsyncMock()
        agent.kommo = AsyncMock()
        agent.calendar = AsyncMock()
        agent.agent = AsyncMock()
        
        # Configure consistent mock responses
        agent.supabase.get_lead.return_value = None
        agent.supabase.create_lead.return_value = {"id": "test-lead"}
        agent.supabase.create_conversation.return_value = {"id": "test-conv"}
        agent.supabase.create_message.return_value = {"id": "test-msg"}
        
        # Simulate realistic API latencies
        async def mock_api_call(*args, **kwargs):
            await asyncio.sleep(0.05)  # 50ms latency
            return {"success": True}
        
        agent.evolution.send_text.side_effect = mock_api_call
        agent.evolution.send_typing.side_effect = mock_api_call
        
        # Simulate AI response time
        async def mock_ai_response(*args, **kwargs):
            await asyncio.sleep(0.2)  # 200ms AI processing
            return "Olá! Sou a Helen da SolarPrime."
        
        agent.agent.run.side_effect = mock_ai_response
        
        await agent.start()
        yield agent
        await agent.shutdown()
    
    def create_test_message(self, phone: str = "5511999999999") -> WhatsAppMessage:
        """Create a test WhatsApp message."""
        return WhatsAppMessage(
            instance_id="test",
            phone=phone,
            name="Test User",
            message="Quero saber sobre energia solar",
            message_id=f"msg-{time.time()}",
            timestamp=str(int(time.time())),
            media_url=None,
            media_type=None
        )
    
    @pytest.mark.asyncio
    async def test_single_message_response_time(self, agent_for_benchmarks):
        """Benchmark single message processing time."""
        message = self.create_test_message()
        
        # Measure processing time
        start_time = time.perf_counter()
        result = await agent_for_benchmarks.process_message(message)
        end_time = time.perf_counter()
        
        processing_time = end_time - start_time
        
        # Verify success
        assert result.success
        
        # Performance assertions
        assert processing_time < 3.0  # Should process in under 3 seconds
        
        # Log performance metrics
        print(f"\nSingle message processing time: {processing_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_throughput_messages_per_second(self, agent_for_benchmarks):
        """Benchmark message throughput."""
        num_messages = 50
        messages = [
            self.create_test_message(phone=f"5511{90000000 + i}")
            for i in range(num_messages)
        ]
        
        # Process messages and measure throughput
        start_time = time.perf_counter()
        
        tasks = [agent_for_benchmarks.process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Calculate metrics
        successful = sum(1 for r in results if hasattr(r, 'success') and r.success)
        throughput = successful / total_time
        
        # Performance assertions
        assert successful >= num_messages * 0.95  # 95% success rate
        assert throughput >= 5  # At least 5 messages per second
        
        print(f"\nThroughput: {throughput:.2f} messages/second")
        print(f"Total time for {num_messages} messages: {total_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_response_time_percentiles(self, agent_for_benchmarks):
        """Measure response time percentiles."""
        num_samples = 20
        response_times = []
        
        for i in range(num_samples):
            message = self.create_test_message(phone=f"5511{90000000 + i}")
            
            start_time = time.perf_counter()
            result = await agent_for_benchmarks.process_message(message)
            end_time = time.perf_counter()
            
            if result.success:
                response_times.append(end_time - start_time)
        
        # Calculate percentiles
        response_times.sort()
        p50 = statistics.median(response_times)
        p95 = response_times[int(len(response_times) * 0.95)]
        p99 = response_times[int(len(response_times) * 0.99)]
        
        # Performance assertions
        assert p50 < 2.0  # Median under 2 seconds
        assert p95 < 3.0  # 95th percentile under 3 seconds
        assert p99 < 5.0  # 99th percentile under 5 seconds
        
        print(f"\nResponse time percentiles:")
        print(f"  P50: {p50:.3f}s")
        print(f"  P95: {p95:.3f}s")
        print(f"  P99: {p99:.3f}s")
    
    @pytest.mark.asyncio
    async def test_memory_usage_per_session(self, agent_for_benchmarks):
        """Benchmark memory usage per session."""
        # Force garbage collection and get baseline
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create 100 sessions
        num_sessions = 100
        messages = [
            self.create_test_message(phone=f"5511{90000000 + i}")
            for i in range(num_sessions)
        ]
        
        # Process all messages to create sessions
        tasks = [agent_for_benchmarks.process_message(msg) for msg in messages]
        await asyncio.gather(*tasks)
        
        # Measure memory after sessions
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory
        memory_per_session = memory_increase / num_sessions
        
        # Performance assertions
        assert memory_per_session < 1.0  # Less than 1MB per session
        
        print(f"\nMemory usage:")
        print(f"  Baseline: {baseline_memory:.2f} MB")
        print(f"  Final: {final_memory:.2f} MB")
        print(f"  Per session: {memory_per_session:.3f} MB")
    
    @pytest.mark.asyncio
    async def test_api_call_efficiency(self, agent_for_benchmarks):
        """Benchmark API call efficiency."""
        # Track API calls
        api_calls = {
            "supabase": 0,
            "evolution": 0,
            "kommo": 0,
            "calendar": 0
        }
        
        # Wrap methods to count calls
        original_methods = {}
        
        for service_name, service in [
            ("supabase", agent_for_benchmarks.supabase),
            ("evolution", agent_for_benchmarks.evolution),
            ("kommo", agent_for_benchmarks.kommo),
            ("calendar", agent_for_benchmarks.calendar)
        ]:
            for method_name in dir(service):
                if not method_name.startswith("_"):
                    method = getattr(service, method_name)
                    if hasattr(method, '__call__'):
                        async def counting_wrapper(*args, **kwargs):
                            api_calls[service_name] += 1
                            return await method(*args, **kwargs)
                        
                        setattr(service, method_name, counting_wrapper)
        
        # Process 10 messages from same user (conversation flow)
        phone = "5511999999999"
        for i in range(10):
            message = self.create_test_message(phone=phone)
            message.message = f"Mensagem {i}"
            await agent_for_benchmarks.process_message(message)
        
        # Verify API efficiency
        # Should reuse session and not create multiple leads
        assert api_calls["supabase"] < 30  # Reasonable number of DB calls
        assert api_calls["evolution"] >= 10  # At least one per message
        
        print(f"\nAPI call efficiency for 10 messages:")
        for service, count in api_calls.items():
            print(f"  {service}: {count} calls")
    
    @pytest.mark.asyncio
    async def test_humanization_overhead(self):
        """Benchmark humanization processing overhead."""
        humanizer = HelenHumanizer()
        
        test_messages = [
            "Oi!",
            "Como posso ajudar você hoje?",
            "Vou analisar sua conta de luz para encontrar a melhor solução de economia para você!",
            "A SolarPrime oferece várias opções de financiamento. Temos planos que cabem no seu bolso, com parcelas menores que sua economia mensal. Assim você já sai ganhando desde o primeiro mês!"
        ]
        
        typing_times = []
        
        for message in test_messages * 10:  # Test each message 10 times
            start_time = time.perf_counter()
            typing_time = humanizer.calculate_typing_time(message)
            personalized = humanizer.add_personality_touches(message)
            end_time = time.perf_counter()
            
            processing_time = end_time - start_time
            typing_times.append(processing_time)
        
        # Calculate metrics
        avg_overhead = statistics.mean(typing_times)
        max_overhead = max(typing_times)
        
        # Performance assertions
        assert avg_overhead < 0.001  # Less than 1ms average
        assert max_overhead < 0.01   # Less than 10ms max
        
        print(f"\nHumanization overhead:")
        print(f"  Average: {avg_overhead*1000:.3f}ms")
        print(f"  Maximum: {max_overhead*1000:.3f}ms")
    
    @pytest.mark.asyncio
    async def test_concurrent_session_scaling(self, agent_for_benchmarks):
        """Benchmark performance with increasing concurrent sessions."""
        session_counts = [10, 25, 50, 100]
        results = []
        
        for count in session_counts:
            # Create messages for different users
            messages = [
                self.create_test_message(phone=f"5511{90000000 + i}")
                for i in range(count)
            ]
            
            # Measure processing time
            start_time = time.perf_counter()
            tasks = [agent_for_benchmarks.process_message(msg) for msg in messages]
            await asyncio.gather(*tasks)
            end_time = time.perf_counter()
            
            total_time = end_time - start_time
            avg_time = total_time / count
            
            results.append({
                "sessions": count,
                "total_time": total_time,
                "avg_time_per_message": avg_time
            })
            
            # Clear sessions for next test
            agent_for_benchmarks.session_manager.active_sessions.clear()
        
        # Verify scaling
        # Average time shouldn't increase dramatically with more sessions
        base_avg = results[0]["avg_time_per_message"]
        for result in results:
            # Allow up to 50% increase in average time
            assert result["avg_time_per_message"] < base_avg * 1.5
        
        print(f"\nConcurrent session scaling:")
        for result in results:
            print(f"  {result['sessions']} sessions: "
                  f"{result['total_time']:.2f}s total, "
                  f"{result['avg_time_per_message']:.3f}s per message")
    
    @pytest.mark.asyncio
    async def test_message_buffering_performance(self, agent_for_benchmarks):
        """Benchmark message buffering efficiency."""
        phone = "5511999999999"
        
        # Send rapid burst of messages
        num_messages = 20
        send_times = []
        
        for i in range(num_messages):
            message = self.create_test_message(phone=phone)
            message.message = f"Mensagem rápida {i}"
            
            start_time = time.perf_counter()
            await agent_for_benchmarks.process_message(message)
            end_time = time.perf_counter()
            
            send_times.append(end_time - start_time)
            await asyncio.sleep(0.1)  # 100ms between messages
        
        # Analyze buffering efficiency
        # Later messages should process faster due to buffering
        first_half_avg = statistics.mean(send_times[:10])
        second_half_avg = statistics.mean(send_times[10:])
        
        # Second half should be at least 20% faster due to buffering
        improvement = (first_half_avg - second_half_avg) / first_half_avg
        assert improvement > 0.2
        
        print(f"\nMessage buffering performance:")
        print(f"  First half average: {first_half_avg:.3f}s")
        print(f"  Second half average: {second_half_avg:.3f}s")
        print(f"  Improvement: {improvement*100:.1f}%")
    
    @pytest.mark.asyncio
    async def test_qualification_flow_performance(self, agent_for_benchmarks):
        """Benchmark complete qualification flow performance."""
        phone = "5511999999999"
        
        # Simulate complete qualification conversation
        conversation_flow = [
            "Oi, quero saber sobre energia solar",
            "Meu nome é João Silva",
            "Moro em casa própria",
            "Minha conta vem uns R$ 450",
            "Não tenho desconto nenhum",
            "Sim, quero agendar uma visita",
            "Pode ser amanhã às 14h"
        ]
        
        start_time = time.perf_counter()
        
        for message_text in conversation_flow:
            message = self.create_test_message(phone=phone)
            message.message = message_text
            result = await agent_for_benchmarks.process_message(message)
            assert result.success
            await asyncio.sleep(0.5)  # Simulate user typing
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Complete qualification should be efficient
        assert total_time < 30  # Under 30 seconds for full flow
        
        print(f"\nQualification flow performance:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average per interaction: {total_time/len(conversation_flow):.2f}s")