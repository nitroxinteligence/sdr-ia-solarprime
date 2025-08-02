#!/usr/bin/env python3
"""
Test script para validar o novo Evolution API Service v2
Testa todas as funcionalidades principais do serviço refatorado
"""

import asyncio
import sys
from datetime import datetime
from loguru import logger

# Adiciona o diretório pai ao path para importar o módulo
sys.path.insert(0, '.')

from agente.services import get_evolution_service
from agente.services.evolution import EvolutionService


# Configurar logger para o teste
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")


async def test_connection(service: EvolutionService) -> bool:
    """Testa conexão com a instância"""
    logger.info("🔍 Testando conexão com instância WhatsApp...")
    
    try:
        # Verifica status
        status = await service.get_instance_status()
        
        if status:
            state = status.get("state", "unknown")
            logger.info(f"📊 Status da instância: {state}")
            
            if state == "open":
                logger.success("✅ Instância conectada e pronta!")
                return True
            else:
                logger.warning(f"⚠️  Instância não está conectada: {state}")
                
                # Tenta conectar
                logger.info("🔄 Tentando conectar instância...")
                connected = await service.connect_instance()
                
                if connected:
                    logger.success("✅ Instância conectada com sucesso!")
                    return True
                else:
                    logger.error("❌ Falha ao conectar instância")
                    return False
        else:
            logger.error("❌ Não foi possível obter status da instância")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão: {e}")
        return False


async def test_text_message(service: EvolutionService, phone: str) -> bool:
    """Testa envio de mensagem de texto"""
    logger.info("📝 Testando envio de mensagem de texto...")
    
    try:
        # Mensagem simples
        result = await service.send_text_message(
            phone=phone,
            text=f"🧪 Teste Evolution API v2\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n✨ Novo serviço funcionando!"
        )
        
        if result:
            logger.success(f"✅ Mensagem enviada! ID: {result.key.id}")
            
            # Testa mensagem longa (chunking)
            logger.info("📝 Testando mensagem longa (chunking)...")
            long_text = """
🧪 TESTE DE MENSAGEM LONGA - Evolution API v2

Esta é uma mensagem muito longa para testar o sistema de chunking automático do novo serviço.

📋 Funcionalidades testadas:
1. Divisão automática de mensagens longas
2. Quebra em pontos naturais (sentenças)
3. Delay progressivo entre chunks
4. Manutenção da ordem das mensagens

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Esta mensagem deve ser dividida em múltiplos chunks de forma inteligente, preservando a legibilidade e mantendo o contexto.

✅ Fim do teste de mensagem longa!
"""
            
            result_long = await service.send_text_message(
                phone=phone,
                text=long_text
            )
            
            if result_long:
                logger.success(f"✅ Mensagem longa enviada em chunks!")
                return True
            else:
                logger.error("❌ Falha ao enviar mensagem longa")
                return False
        else:
            logger.error("❌ Falha ao enviar mensagem de texto")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar mensagem: {e}")
        return False


async def test_media(service: EvolutionService, phone: str) -> bool:
    """Testa envio de mídia"""
    logger.info("🖼️ Testando envio de mídia...")
    
    # URLs de exemplo (substitua por URLs válidas)
    test_media = {
        "image": "https://via.placeholder.com/300x200/007bff/ffffff?text=Evolution+API+v2",
        "document": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    }
    
    try:
        # Testa imagem
        logger.info("🖼️ Enviando imagem de teste...")
        result = await service.send_image(
            phone=phone,
            image_url=test_media["image"],
            caption="🖼️ Imagem de teste - Evolution API v2"
        )
        
        if result:
            logger.success(f"✅ Imagem enviada! ID: {result.key.id}")
        else:
            logger.warning("⚠️  Falha ao enviar imagem (verifique a URL)")
        
        # Testa documento
        logger.info("📄 Enviando documento de teste...")
        result = await service.send_document(
            phone=phone,
            document_url=test_media["document"],
            caption="📄 Documento de teste - Evolution API v2"
        )
        
        if result:
            logger.success(f"✅ Documento enviado! ID: {result.key.id}")
            return True
        else:
            logger.warning("⚠️  Falha ao enviar documento (verifique a URL)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar mídia: {e}")
        return False


async def test_location(service: EvolutionService, phone: str) -> bool:
    """Testa envio de localização"""
    logger.info("📍 Testando envio de localização...")
    
    try:
        # Coordenadas da Praia de Boa Viagem, Recife
        result = await service.send_location(
            phone=phone,
            latitude=-8.126371,
            longitude=-34.904990,
            name="🏖️ Praia de Boa Viagem - Teste Evolution API v2"
        )
        
        if result:
            logger.success(f"✅ Localização enviada! ID: {result.key.id}")
            return True
        else:
            logger.error("❌ Falha ao enviar localização")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar localização: {e}")
        return False


async def test_webhook(service: EvolutionService) -> bool:
    """Testa configuração de webhook"""
    logger.info("🔗 Testando configuração de webhook...")
    
    try:
        # URL de exemplo (substitua por sua URL de webhook)
        webhook_url = "https://webhook.site/test-evolution-v2"
        
        result = await service.set_webhook(
            url=webhook_url,
            events=["messages.upsert", "connection.update"]
        )
        
        if result:
            logger.success(f"✅ Webhook configurado: {webhook_url}")
            return True
        else:
            logger.error("❌ Falha ao configurar webhook")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar webhook: {e}")
        return False


async def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes do Evolution API Service v2")
    logger.info("=" * 60)
    
    # Solicita número de telefone para teste
    phone = input("📱 Digite o número de telefone para teste (formato: 5511999999999): ").strip()
    
    if not phone or len(phone) < 10:
        logger.error("❌ Número de telefone inválido!")
        return
    
    # Obtém serviço
    service = get_evolution_service()
    
    # Contadores
    total_tests = 0
    passed_tests = 0
    
    # Executa testes
    tests = [
        ("Conexão", test_connection(service)),
        ("Mensagem de Texto", test_text_message(service, phone)),
        ("Mídia", test_media(service, phone)),
        ("Localização", test_location(service, phone)),
        ("Webhook", test_webhook(service))
    ]
    
    logger.info("=" * 60)
    
    for test_name, test_coro in tests:
        total_tests += 1
        logger.info(f"🧪 Executando teste: {test_name}")
        
        try:
            result = await test_coro
            if result:
                passed_tests += 1
                logger.success(f"✅ {test_name}: PASSOU")
            else:
                logger.error(f"❌ {test_name}: FALHOU")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERRO - {e}")
        
        logger.info("-" * 40)
    
    # Resumo
    logger.info("=" * 60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info(f"Total de testes: {total_tests}")
    logger.info(f"Testes aprovados: {passed_tests}")
    logger.info(f"Testes falhados: {total_tests - passed_tests}")
    logger.info(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.success("🎉 TODOS OS TESTES PASSARAM!")
    else:
        logger.warning(f"⚠️  {total_tests - passed_tests} testes falharam")
    
    # Fecha conexões
    await service.close()
    logger.info("🔚 Testes finalizados")


if __name__ == "__main__":
    asyncio.run(main())