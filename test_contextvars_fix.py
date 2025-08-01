#!/usr/bin/env python3
"""
Teste para validar a correção do contexto usando contextvars em ambiente async/await
"""

import asyncio
from agente.core.tool_context import set_tool_context, get_current_phone, get_current_context

async def test_async_context():
    """Teste que simula o cenário real do problema"""
    
    # Definir contexto (como feito no agent.py)
    test_phone = "558182986181"
    test_context = {
        "phone": test_phone,
        "conversation_id": "fecb7acc-5422-4d56-b204-9a029559b99f",
        "stage": "IDENTIFICATION"
    }
    
    print("🧪 Iniciando teste de contexto async...")
    
    # Definir contexto
    set_tool_context(test_phone, test_context)
    print(f"✅ Contexto definido: {test_phone[:4]}****")
    
    # Simular operação assíncrona (como o AGnO faz)
    await asyncio.sleep(0.1)
    
    # Tentar recuperar contexto (como a ferramenta send_text_message faz)
    recovered_phone = get_current_phone()
    recovered_context = get_current_context()
    
    print(f"📞 Phone recuperado: {recovered_phone}")
    print(f"📋 Context recuperado: {recovered_context is not None}")
    
    # Validar resultado
    if recovered_phone == test_phone:
        print("✅ SUCESSO: Contexto preservado em ambiente async!")
        return True
    else:
        print("❌ FALHA: Contexto perdido em ambiente async!")
        return False

async def test_concurrent_contexts():
    """Teste para verificar isolamento entre tasks concorrentes"""
    
    async def task_with_context(phone: str, task_id: int):
        """Task individual com seu próprio contexto"""
        context = {"phone": phone, "task_id": task_id}
        set_tool_context(phone, context)
        
        # Simular operação assíncrona
        await asyncio.sleep(0.2)
        
        # Recuperar contexto
        recovered_phone = get_current_phone()
        recovered_context = get_current_context()
        
        print(f"Task {task_id}: Phone={recovered_phone}, Context={recovered_context}")
        
        return recovered_phone == phone and recovered_context["task_id"] == task_id
    
    print("\n🧪 Testando isolamento entre tasks concorrentes...")
    
    # Executar múltiplas tasks concorrentemente
    tasks = [
        task_with_context("558111111111", 1),
        task_with_context("558222222222", 2),
        task_with_context("558333333333", 3)
    ]
    
    results = await asyncio.gather(*tasks)
    
    if all(results):
        print("✅ SUCESSO: Contextos isolados corretamente!")
        return True
    else:
        print("❌ FALHA: Vazamento de contexto entre tasks!")
        return False

async def main():
    """Executar todos os testes"""
    print("🚀 Testando correção contextvars para problema async/await...\n")
    
    # Teste básico
    result1 = await test_async_context()
    
    # Teste de concorrência
    result2 = await test_concurrent_contexts()
    
    print("\n📊 RESULTADO FINAL:")
    if result1 and result2:
        print("✅ TODOS OS TESTES PASSARAM - Correção funcionando!")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM - Precisa investigar mais!")
        return False

if __name__ == "__main__":
    asyncio.run(main())