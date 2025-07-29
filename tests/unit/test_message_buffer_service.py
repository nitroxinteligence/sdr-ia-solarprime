"""
Testes unitários para o MessageBufferService
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from services.message_buffer_service import MessageBufferService


@pytest.fixture
def buffer_service():
    """Fixture para criar instância do MessageBufferService"""
    with patch.dict('os.environ', {
        'MESSAGE_BUFFER_ENABLED': 'true',
        'MESSAGE_BUFFER_TIMEOUT': '1.0',  # 1 segundo para testes rápidos
        'MESSAGE_BUFFER_MAX_MESSAGES': '5'
    }):
        service = MessageBufferService()
        yield service
        # Limpar timers ativos após o teste
        for timer in service._active_timers.values():
            timer.cancel()


@pytest.mark.asyncio
async def test_buffer_accumulates_messages(buffer_service):
    """Testa se o buffer acumula mensagens corretamente"""
    phone = "5511999999999@s.whatsapp.net"
    messages_received = []
    
    async def mock_callback(messages):
        messages_received.extend(messages)
    
    # Adicionar 3 mensagens rapidamente
    for i in range(3):
        message = {
            "id": f"msg_{i}",
            "content": f"Mensagem {i}",
            "type": "text"
        }
        result = await buffer_service.add_message(phone, message, mock_callback)
        assert result is True
        await asyncio.sleep(0.1)  # Pequeno delay entre mensagens
    
    # Verificar que as mensagens estão no buffer
    status = await buffer_service.get_buffer_status(phone)
    assert status["buffer_size"] == 3
    assert status["has_active_timer"] is True
    assert status["is_processing"] is False
    
    # Aguardar o timer expirar
    await asyncio.sleep(1.5)
    
    # Verificar que todas as mensagens foram processadas juntas
    assert len(messages_received) == 3
    assert messages_received[0]["content"] == "Mensagem 0"
    assert messages_received[1]["content"] == "Mensagem 1"
    assert messages_received[2]["content"] == "Mensagem 2"


@pytest.mark.asyncio
async def test_timer_reset_on_new_message(buffer_service):
    """Testa se o timer é resetado quando nova mensagem chega"""
    phone = "5511999999999@s.whatsapp.net"
    callback_called = False
    
    async def mock_callback(messages):
        nonlocal callback_called
        callback_called = True
    
    # Adicionar primeira mensagem
    message1 = {"id": "msg_1", "content": "Primeira", "type": "text"}
    await buffer_service.add_message(phone, message1, mock_callback)
    
    # Aguardar 0.7 segundos (menos que o timeout)
    await asyncio.sleep(0.7)
    
    # Adicionar segunda mensagem (deve resetar o timer)
    message2 = {"id": "msg_2", "content": "Segunda", "type": "text"}
    await buffer_service.add_message(phone, message2, mock_callback)
    
    # Aguardar mais 0.5 segundos (total 1.2s desde a primeira, mas 0.5s desde a segunda)
    await asyncio.sleep(0.5)
    
    # Callback não deve ter sido chamado ainda
    assert callback_called is False
    
    # Aguardar mais tempo para o timer expirar
    await asyncio.sleep(0.7)
    
    # Agora o callback deve ter sido chamado
    assert callback_called is True


@pytest.mark.asyncio
async def test_no_duplicate_processing(buffer_service):
    """Testa que o buffer não processa mensagens duplicadamente"""
    phone = "5511999999999@s.whatsapp.net"
    process_count = 0
    
    async def mock_callback(messages):
        nonlocal process_count
        process_count += 1
        await asyncio.sleep(0.5)  # Simular processamento demorado
    
    # Adicionar mensagem
    message = {"id": "msg_1", "content": "Test", "type": "text"}
    await buffer_service.add_message(phone, message, mock_callback)
    
    # Forçar processamento múltiplas vezes
    await buffer_service.force_process(phone)
    await buffer_service.force_process(phone)  # Segunda tentativa deve ser ignorada
    
    # Aguardar processamento
    await asyncio.sleep(1.0)
    
    # Deve ter processado apenas uma vez
    assert process_count == 1


@pytest.mark.asyncio
async def test_max_messages_triggers_immediate_processing(buffer_service):
    """Testa se exceder o limite de mensagens dispara processamento imediato"""
    phone = "5511999999999@s.whatsapp.net"
    messages_received = []
    
    async def mock_callback(messages):
        messages_received.extend(messages)
    
    # Adicionar mensagens até o limite (5)
    for i in range(5):
        message = {
            "id": f"msg_{i}",
            "content": f"Mensagem {i}",
            "type": "text"
        }
        result = await buffer_service.add_message(phone, message, mock_callback)
        assert result is True
    
    # Aguardar um pouco para processamento assíncrono
    await asyncio.sleep(0.2)
    
    # Deve ter processado imediatamente ao atingir o limite
    assert len(messages_received) == 5


@pytest.mark.asyncio
async def test_concurrent_messages_different_phones(buffer_service):
    """Testa processamento concorrente para telefones diferentes"""
    phone1 = "5511111111111@s.whatsapp.net"
    phone2 = "5522222222222@s.whatsapp.net"
    
    results = {phone1: [], phone2: []}
    
    async def create_callback(phone):
        async def callback(messages):
            results[phone].extend(messages)
        return callback
    
    # Adicionar mensagens para ambos os telefones
    msg1 = {"id": "msg_1", "content": "Phone 1", "type": "text"}
    msg2 = {"id": "msg_2", "content": "Phone 2", "type": "text"}
    
    await buffer_service.add_message(phone1, msg1, await create_callback(phone1))
    await buffer_service.add_message(phone2, msg2, await create_callback(phone2))
    
    # Aguardar processamento
    await asyncio.sleep(1.5)
    
    # Ambos devem ter sido processados independentemente
    assert len(results[phone1]) == 1
    assert len(results[phone2]) == 1
    assert results[phone1][0]["content"] == "Phone 1"
    assert results[phone2][0]["content"] == "Phone 2"


@pytest.mark.asyncio
async def test_clear_buffer(buffer_service):
    """Testa limpeza do buffer sem processar"""
    phone = "5511999999999@s.whatsapp.net"
    callback_called = False
    
    async def mock_callback(messages):
        nonlocal callback_called
        callback_called = True
    
    # Adicionar mensagem
    message = {"id": "msg_1", "content": "Test", "type": "text"}
    await buffer_service.add_message(phone, message, mock_callback)
    
    # Limpar buffer
    result = await buffer_service.clear_buffer(phone)
    assert result is True
    
    # Aguardar mais que o timeout
    await asyncio.sleep(1.5)
    
    # Callback não deve ter sido chamado
    assert callback_called is False
    
    # Buffer deve estar vazio
    status = await buffer_service.get_buffer_status(phone)
    assert status["buffer_size"] == 0


@pytest.mark.asyncio
async def test_processing_flag_prevents_new_messages(buffer_service):
    """Testa que flag de processamento previne adição de novas mensagens"""
    phone = "5511999999999@s.whatsapp.net"
    
    # Marcar como processando manualmente
    buffer_service._processing[phone] = True
    
    # Tentar adicionar mensagem
    message = {"id": "msg_1", "content": "Test", "type": "text"}
    result = await buffer_service.add_message(phone, message, AsyncMock())
    
    # Deve retornar False (não adicionado)
    assert result is False