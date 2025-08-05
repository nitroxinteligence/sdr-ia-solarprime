"""
Testes abrangentes para o sistema de typing do AgenticSDR
Validação completa das mudanças implementadas
"""
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.evolution import EvolutionAPIClient
from app.api.webhooks import process_message_with_agent


class TestTypingDuration:
    """Testes unitários para o cálculo de duração do typing"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.client = EvolutionAPIClient()
    
    def test_duration_for_very_short_messages(self):
        """Testa duração para mensagens muito curtas (<50 chars)"""
        # Mensagem de 30 caracteres
        duration = self.client._calculate_humanized_typing_duration(30)
        # Deve retornar ~2s com variação de ±15%
        assert 1.7 <= duration <= 2.3
        
    def test_duration_for_short_messages(self):
        """Testa duração para mensagens curtas (50-150 chars)"""
        # Mensagem de 100 caracteres
        duration = self.client._calculate_humanized_typing_duration(100)
        # Deve retornar ~3s com variação de ±15%
        assert 2.55 <= duration <= 3.45
        
    def test_duration_for_medium_messages(self):
        """Testa duração para mensagens médias (150-250 chars)"""
        # Mensagem de 200 caracteres
        duration = self.client._calculate_humanized_typing_duration(200)
        # Deve retornar ~5s com variação de ±15%
        assert 4.25 <= duration <= 5.75
        
    def test_duration_for_long_messages(self):
        """Testa duração para mensagens longas (250-500 chars)"""
        # Mensagem de 400 caracteres
        duration = self.client._calculate_humanized_typing_duration(400)
        # Deve retornar ~8s com variação de ±15%
        assert 6.8 <= duration <= 9.2
        
    def test_duration_for_very_long_messages(self):
        """Testa duração para mensagens muito longas (>500 chars)"""
        # Mensagem de 700 caracteres
        duration = self.client._calculate_humanized_typing_duration(700)
        # Deve retornar ~12s com variação de ±15%
        assert 10.2 <= duration <= 13.8
        
    def test_duration_limits(self):
        """Testa os limites mínimo e máximo da duração"""
        # Teste com mensagem extremamente curta
        duration_min = self.client._calculate_humanized_typing_duration(1)
        assert duration_min >= 1.0
        
        # Teste com mensagem extremamente longa
        duration_max = self.client._calculate_humanized_typing_duration(10000)
        assert duration_max <= 15.0
        
    def test_duration_randomness(self):
        """Testa se há variação aleatória nas durações"""
        durations = []
        for _ in range(10):
            duration = self.client._calculate_humanized_typing_duration(200)
            durations.append(duration)
        
        # Deve haver alguma variação
        assert len(set(durations)) > 1
        # Mas todas dentro do range esperado
        assert all(4.25 <= d <= 5.75 for d in durations)


class TestTypingIntegration:
    """Testes de integração para o fluxo completo de typing"""
    
    @pytest.mark.asyncio
    async def test_send_typing_uses_calculated_duration(self):
        """Testa se send_typing usa a duração calculada corretamente"""
        client = EvolutionAPIClient()
        
        # Mock do método _make_request
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True}
            
            # Mock do sleep para não esperar
            with patch('asyncio.sleep', new_callable=AsyncMock):
                # Enviar typing para mensagem de 200 caracteres
                await client.send_typing("5511999999999", message_length=200)
                
                # Verificar se foi chamado duas vezes (composing e paused)
                assert mock_request.call_count == 2
                
                # Verificar primeira chamada (composing)
                first_call = mock_request.call_args_list[0]
                payload = first_call[1]['json']
                
                # A duração deve estar no range esperado (5s ±15% convertido para ms)
                assert 4250 <= payload['delay'] <= 5750
                assert payload['state'] == 'composing'
                
                # Verificar segunda chamada (paused)
                second_call = mock_request.call_args_list[1]
                payload = second_call[1]['json']
                assert payload['state'] == 'paused'
            
    @pytest.mark.asyncio
    async def test_send_typing_with_custom_duration(self):
        """Testa se send_typing aceita duração personalizada"""
        client = EvolutionAPIClient()
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True}
            
            # Mock do sleep para não esperar
            with patch('asyncio.sleep', new_callable=AsyncMock):
                # Enviar typing com duração específica
                await client.send_typing("5511999999999", duration_seconds=7.5)
                
                # Verificar primeira chamada (composing)
                first_call = mock_request.call_args_list[0]
                payload = first_call[1]['json']
                assert payload['delay'] == 7500  # 7.5s em ms
            
    @pytest.mark.asyncio
    async def test_send_text_message_triggers_typing(self):
        """Testa se send_text_message aciona o typing antes de enviar"""
        client = EvolutionAPIClient()
        
        # Mock dos métodos
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            # Criar um objeto mock que simula a resposta do httpx
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json = Mock(return_value={"key": {"id": "123"}})
            mock_request.return_value = mock_response
            
            with patch.object(client, 'send_typing', new_callable=AsyncMock) as mock_typing:
                # Enviar mensagem com typing habilitado
                message = "Esta é uma mensagem de teste com 100 caracteres aproximadamente para validar typing"
                await client.send_text_message("5511999999999", message, simulate_typing=True)
                
                # Verificar se typing foi chamado com o tamanho correto
                mock_typing.assert_called_once_with("5511999999999", len(message))
                
    @pytest.mark.asyncio
    async def test_webhook_no_premature_typing(self):
        """Testa que o webhook NÃO envia typing antes do processamento"""
        # Mock das dependências
        with patch('app.api.webhooks.emoji_logger') as mock_logger:
            with patch('app.api.webhooks.evolution_client') as mock_evolution:
                with patch('app.api.webhooks.get_agentic_sdr') as mock_get_agentic:
                    with patch('app.api.webhooks.supabase_client') as mock_supabase:
                        
                        # Configurar mocks
                        mock_evolution.send_typing = AsyncMock()
                        mock_evolution.send_text_message = AsyncMock(return_value={"success": True})
                        
                        mock_agentic = AsyncMock()
                        mock_get_agentic.return_value = mock_agentic
                        mock_agentic.process_message = AsyncMock(return_value="Resposta do agente")
                        
                        mock_supabase.get_or_create_lead = AsyncMock(return_value={
                            "id": "123",
                            "phone": "5511999999999"
                        })
                        mock_supabase.get_or_create_conversation = AsyncMock(return_value={
                            "id": "456"
                        })
                        
                        # Executar o processo
                        await process_message_with_agent(
                            phone="5511999999999",
                            message_content="Olá, teste",
                            lead={"id": "123", "phone": "5511999999999"},
                            conversation={"id": "456"},
                            agentic=mock_agentic,
                            evolution_client=mock_evolution,
                            supabase=mock_supabase,
                            media_data=None
                        )
                        
                        # Verificar que typing NÃO foi chamado durante o processamento
                        # O único typing deve ser do send_text_message
                        typing_calls = [call for call in mock_evolution.method_calls 
                                      if 'send_typing' in str(call)]
                        
                        # Não deve haver chamadas diretas de send_typing
                        # (apenas dentro de send_text_message)
                        assert len(typing_calls) == 0


class TestProductionScenarios:
    """Testes de cenários de produção"""
    
    @pytest.mark.asyncio
    async def test_complete_message_flow(self):
        """Testa o fluxo completo de uma mensagem"""
        client = EvolutionAPIClient()
        
        # Lista para rastrear as chamadas
        api_calls = []
        
        async def mock_make_request(method, endpoint, **kwargs):
            api_calls.append({
                'method': method,
                'endpoint': endpoint,
                'payload': kwargs.get('json', {})
            })
            # Retornar resposta mock apropriada
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json = Mock(return_value={"key": {"id": "123"}})
            return mock_response
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            # Mock do sleep para não esperar
            with patch('asyncio.sleep', new_callable=AsyncMock):
                # Simular envio de mensagem
                await client.send_text_message(
                    "5511999999999",
                    "Olá! Esta é uma resposta do agente com aproximadamente 100 caracteres de texto.",
                    simulate_typing=True
                )
                
                # Deve haver 3 chamadas: typing composing + typing paused + mensagem
                assert len(api_calls) == 3
                
                # Primeira chamada deve ser typing composing
                typing_call = api_calls[0]
                assert 'updatePresence' in typing_call['endpoint']
                assert typing_call['payload']['state'] == 'composing'
                # Duração deve estar no range para ~80 chars (3s ±15%)
                assert 2550 <= typing_call['payload']['delay'] <= 3450
                
                # Segunda chamada deve ser typing paused
                typing_paused = api_calls[1]
                assert 'updatePresence' in typing_paused['endpoint']
                assert typing_paused['payload']['state'] == 'paused'
                
                # Terceira chamada deve ser a mensagem
                message_call = api_calls[2]
                assert 'sendText' in message_call['endpoint']
            
    @pytest.mark.asyncio
    async def test_message_splitting_with_typing(self):
        """Testa o comportamento com mensagens divididas"""
        client = EvolutionAPIClient()
        
        api_calls = []
        
        async def mock_make_request(method, endpoint, **kwargs):
            api_calls.append({
                'method': method,
                'endpoint': endpoint,
                'payload': kwargs.get('json', {})
            })
            # Retornar resposta mock apropriada
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json = Mock(return_value={"key": {"id": "123"}})
            return mock_response
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            # Mock do sleep para não esperar
            with patch('asyncio.sleep', new_callable=AsyncMock):
                # Simular envio de duas partes de mensagem
                chunk1 = "Primeira parte da mensagem com 50 caracteres..."
                chunk2 = "Segunda parte da mensagem que também tem um tamanho considerável para teste"
                
                # Enviar primeira parte
                await client.send_text_message("5511999999999", chunk1, simulate_typing=True)
                
                # Enviar segunda parte
                await client.send_text_message("5511999999999", chunk2, simulate_typing=True)
                
                # Deve haver 6 chamadas: (typing composing + typing paused + msg) * 2
                assert len(api_calls) == 6
                
                # Verificar padrão para primeira mensagem
                assert 'updatePresence' in api_calls[0]['endpoint']
                assert api_calls[0]['payload']['state'] == 'composing'
                assert 'updatePresence' in api_calls[1]['endpoint']
                assert api_calls[1]['payload']['state'] == 'paused'
                assert 'sendText' in api_calls[2]['endpoint']
                
                # Verificar padrão para segunda mensagem
                assert 'updatePresence' in api_calls[3]['endpoint']
                assert api_calls[3]['payload']['state'] == 'composing'
                assert 'updatePresence' in api_calls[4]['endpoint']
                assert api_calls[4]['payload']['state'] == 'paused'
                assert 'sendText' in api_calls[5]['endpoint']
                
                # Verificar que as durações são diferentes (baseadas no tamanho)
                typing1_delay = api_calls[0]['payload']['delay']
                typing2_delay = api_calls[3]['payload']['delay']
                
                # Segunda mensagem é maior, deve ter typing mais longo
                assert typing2_delay > typing1_delay


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])