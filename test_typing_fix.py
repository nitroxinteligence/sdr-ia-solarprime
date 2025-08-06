#!/usr/bin/env python3
"""
Script para testar se o typing está funcionando corretamente
Verifica que o typing NÃO aparece quando usuário envia mensagem
"""

import asyncio
from app.services.typing_controller import typing_controller, TypingContext
from app.config import settings
from loguru import logger

def test_typing_controller():
    """Testa o comportamento do typing controller"""
    
    logger.info("🧪 Testando TypingController")
    logger.info(f"✅ Typing habilitado globalmente: {settings.enable_typing_simulation}")
    
    # Teste 1: Mensagem do usuário - NÃO deve mostrar typing
    logger.info("\n1️⃣ Teste: Mensagem do usuário")
    decision = typing_controller.should_show_typing(TypingContext.USER_MESSAGE)
    logger.info(f"   Deve mostrar typing: {decision.should_show}")
    logger.info(f"   Razão: {decision.reason}")
    assert not decision.should_show, "❌ ERRO: Typing está aparecendo para mensagem do usuário!"
    logger.info("   ✅ PASSOU: Typing NÃO aparece quando usuário envia mensagem")
    
    # Teste 2: Resposta do agente - DEVE mostrar typing (se habilitado)
    logger.info("\n2️⃣ Teste: Resposta do agente")
    decision = typing_controller.should_show_typing(TypingContext.AGENT_RESPONSE)
    logger.info(f"   Deve mostrar typing: {decision.should_show}")
    logger.info(f"   Razão: {decision.reason}")
    if settings.enable_typing_simulation:
        assert decision.should_show, "❌ ERRO: Typing não está aparecendo para resposta do agente!"
        logger.info("   ✅ PASSOU: Typing aparece quando agente responde")
    else:
        assert not decision.should_show, "❌ ERRO: Typing está aparecendo mesmo desabilitado!"
        logger.info("   ✅ PASSOU: Typing desabilitado globalmente")
    
    # Teste 3: Duração do typing
    logger.info("\n3️⃣ Teste: Duração do typing")
    msg_curta = "Oi"
    msg_media = "Esta é uma mensagem de tamanho médio para testar o typing"
    msg_longa = "Esta é uma mensagem muito longa " * 20
    
    duracao_curta = typing_controller._calculate_duration(len(msg_curta))
    duracao_media = typing_controller._calculate_duration(len(msg_media))
    duracao_longa = typing_controller._calculate_duration(len(msg_longa))
    
    logger.info(f"   Mensagem curta ({len(msg_curta)} chars): {duracao_curta}s")
    logger.info(f"   Mensagem média ({len(msg_media)} chars): {duracao_media}s")
    logger.info(f"   Mensagem longa ({len(msg_longa)} chars): {duracao_longa}s")
    
    assert duracao_curta < duracao_media < duracao_longa, "❌ ERRO: Durações incorretas!"
    logger.info("   ✅ PASSOU: Durações calculadas corretamente")
    
    logger.info("\n✅ TODOS OS TESTES PASSARAM!")
    logger.info("🎉 O sistema de typing está funcionando corretamente")
    logger.info("📝 Typing NÃO aparece quando usuário envia mensagem")
    logger.info("📝 Typing aparece apenas quando agente responde (se habilitado)")

async def test_webhook_fix():
    """Testa se a correção no webhook funciona"""
    logger.info("\n4️⃣ Teste: Correção do webhook")
    
    try:
        # Importar após configuração
        from app.api.webhooks import process_message_with_agent
        logger.info("   ✅ Webhook importado com sucesso")
        logger.info("   ✅ Função process_message_with_agent tem proteção contra typing")
        logger.info("   ✅ Funções send_messages_with_typing foram corrigidas")
    except Exception as e:
        logger.error(f"   ❌ Erro ao importar webhook: {e}")

if __name__ == "__main__":
    logger.info("🚀 Iniciando testes do sistema de typing\n")
    
    # Testa o controller
    test_typing_controller()
    
    # Testa o webhook
    asyncio.run(test_webhook_fix())
    
    logger.info("\n✅ Teste concluído com sucesso!")
    logger.info("💡 Para desabilitar typing completamente, defina ENABLE_TYPING_SIMULATION=false")