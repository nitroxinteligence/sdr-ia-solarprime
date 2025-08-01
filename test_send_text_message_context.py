#!/usr/bin/env python3
"""
Teste específico para validar que send_text_message consegue acessar phone do contexto
após correção contextvars
"""

import asyncio
from unittest.mock import Mock, patch
from agente.core.tool_context import set_tool_context
from agente.tools.whatsapp.send_text_message import _send_text_message_async

async def test_send_text_message_with_context():
    """Teste que simula exatamente o cenário do log de erro"""
    
    print("🧪 Testando send_text_message com contexto...")
    
    # Definir contexto exatamente como no agent.py
    test_phone = "558182986181"
    test_context = {
        "phone": test_phone,
        "conversation_id": "fecb7acc-5422-4d56-b204-9a029559b99f",
        "stage": "IDENTIFICATION"
    }
    
    # Definir contexto
    set_tool_context(test_phone, test_context)
    print(f"✅ Contexto definido para tools: phone={test_phone[:4]}****")
    
    # Mock do evolution service para evitar chamada real da API
    mock_evolution_result = {
        "key": {"id": "3EB0C767D097E9ECFE8A"},
        "status": "success"
    }
    
    with patch('agente.tools.whatsapp.send_text_message.get_evolution_service') as mock_get_service:
        # Configurar mock
        mock_service = Mock()
        mock_service.send_text_message = Mock(return_value=mock_evolution_result)
        mock_service._calculate_typing_delay = Mock(return_value=3)
        mock_get_service.return_value = mock_service
        
        # Chamar ferramenta SEM phone (deve obter do contexto)
        result = await _send_text_message_async("Olá! Como posso ajudar?")
        
        print(f"📞 Resultado: {result}")
        
        # Validar resultado
        if result["success"] and result["phone"] == test_phone:
            print("✅ SUCESSO: send_text_message conseguiu obter phone do contexto!")
            return True
        else:
            print("❌ FALHA: send_text_message não conseguiu obter phone do contexto!")
            print(f"   Success: {result.get('success')}")
            print(f"   Phone: {result.get('phone')}")
            print(f"   Error: {result.get('error')}")
            return False

async def test_send_text_message_without_context():
    """Teste para verificar comportamento quando não há contexto"""
    
    print("\n🧪 Testando send_text_message SEM contexto...")
    
    # Não definir contexto - simular situação de erro
    result = await _send_text_message_async("Teste sem contexto")
    
    print(f"📞 Resultado: {result}")
    
    # Deve falhar graciosamente
    if not result["success"] and "Número de telefone não disponível" in result["error"]:
        print("✅ SUCESSO: Falha graciosamente quando não há contexto!")
        return True
    else:
        print("❌ FALHA: Não tratou adequadamente a ausência de contexto!")
        return False

async def test_concurrent_send_messages():
    """Teste para verificar isolamento entre múltiplas mensagens concorrentes"""
    
    print("\n🧪 Testando múltiplas mensagens concorrentes...")
    
    async def send_message_with_context(phone: str, message: str, task_id: int):
        """Simular envio de mensagem com contexto específico"""
        context = {"phone": phone, "task_id": task_id}
        set_tool_context(phone, context)
        
        # Mock evolution service
        mock_result = {"key": {"id": f"MSG_{task_id}"}, "status": "success"}
        
        with patch('agente.tools.whatsapp.send_text_message.get_evolution_service') as mock_get_service:
            mock_service = Mock()
            mock_service.send_text_message = Mock(return_value=mock_result)
            mock_service._calculate_typing_delay = Mock(return_value=2)
            mock_get_service.return_value = mock_service
            
            result = await _send_text_message_async(message)
            
            print(f"Task {task_id}: Phone={result.get('phone')}, Success={result.get('success')}")
            
            return result["success"] and result["phone"] == phone
    
    # Executar múltiplas mensagens concorrentemente
    tasks = [
        send_message_with_context("558111111111", "Mensagem 1", 1),
        send_message_with_context("558222222222", "Mensagem 2", 2),
        send_message_with_context("558333333333", "Mensagem 3", 3)
    ]
    
    results = await asyncio.gather(*tasks)
    
    if all(results):
        print("✅ SUCESSO: Múltiplas mensagens isoladas corretamente!")
        return True
    else:
        print("❌ FALHA: Vazamento de contexto entre mensagens!")
        return False

async def main():
    """Executar todos os testes específicos da ferramenta"""
    print("🚀 Testando correção send_text_message após fix contextvars...\n")
    
    # Teste principal - com contexto
    result1 = await test_send_text_message_with_context()
    
    # Teste sem contexto
    result2 = await test_send_text_message_without_context()
    
    # Teste concorrência
    result3 = await test_concurrent_send_messages()
    
    print("\n📊 RESULTADO FINAL:")
    if result1 and result2 and result3:
        print("✅ TODOS OS TESTES PASSARAM - send_text_message corrigido!")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM - Problema ainda existe!")
        return False

if __name__ == "__main__":
    asyncio.run(main())