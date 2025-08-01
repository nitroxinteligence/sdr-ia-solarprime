#!/usr/bin/env python3
"""
Teste para validar que a solução simples está funcionando
"""

import asyncio
from unittest.mock import Mock, patch
from agente.core.tool_context import set_tool_context, get_current_phone
from agente.tools.whatsapp.send_text_message import _send_text_message_async

async def test_simple_context_solution():
    """Teste da solução simples sem complexidade"""
    
    print("🧪 Testando solução SIMPLES de contexto...")
    
    # Definir contexto
    test_phone = "558182986181"
    test_context = {
        "phone": test_phone,
        "conversation_id": "test-conversation",
        "stage": "IDENTIFICATION"
    }
    
    set_tool_context(test_phone, test_context)
    print(f"✅ Contexto definido: {test_phone[:4]}****")
    
    # Verificar se phone é obtido corretamente
    recovered_phone = get_current_phone()
    print(f"📞 Phone recuperado: {recovered_phone}")
    
    if recovered_phone == test_phone:
        print("✅ SUCESSO: Contexto funcionando!")
        
        # Testar ferramenta com mock simples
        mock_evolution_result = {
            "key": {"id": "TEST_MESSAGE_ID"},
            "status": "success"
        }
        
        with patch('agente.tools.whatsapp.send_text_message.get_evolution_service') as mock_get_service:
            # Configurar mock
            mock_service = Mock()
            mock_service.send_text_message = Mock(return_value=mock_evolution_result)
            mock_service._calculate_typing_delay = Mock(return_value=3)
            mock_get_service.return_value = mock_service
            
            # Chamar ferramenta SEM phone (deve obter do contexto)
            result = await _send_text_message_async("Teste de mensagem simples")
            
            print(f"📤 Resultado da ferramenta: {result}")
            
            if result["success"] and result["phone"] == test_phone:
                print("✅ SUCESSO TOTAL: Ferramenta funcionando com contexto simples!")
                return True
            else:
                print("❌ FALHA: Ferramenta não funcionou")
                return False
    else:
        print("❌ FALHA: Contexto não funcionou")
        return False

async def main():
    """Executar teste"""
    print("🚀 Testando correção SIMPLES após reversão...\n")
    
    result = await test_simple_context_solution()
    
    print("\n📊 RESULTADO:")
    if result:
        print("✅ SOLUÇÃO SIMPLES FUNCIONANDO!")
    else:
        print("❌ AINDA HÁ PROBLEMAS")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())