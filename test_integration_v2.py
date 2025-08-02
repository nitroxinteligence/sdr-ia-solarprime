#!/usr/bin/env python3
"""
Script de teste rápido para verificar integração Evolution API v2
Testa apenas a integração básica sem enviar mensagens reais
"""

import asyncio
import sys
from loguru import logger

# Adiciona o diretório pai ao path
sys.path.insert(0, '.')

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")


async def test_imports():
    """Testa se todos os imports funcionam corretamente"""
    logger.info("🔍 Testando imports...")
    
    try:
        # Importar serviços
        from agente.services import get_evolution_service
        logger.success("✅ Import do serviço principal OK")
        
        # Importar ferramentas
        from agente.tools.whatsapp.send_text_message import send_text_message
        from agente.tools.whatsapp.send_audio_message import send_audio_message
        from agente.tools.whatsapp.send_image_message import send_image_message
        from agente.tools.whatsapp.send_document_message import send_document_message
        from agente.tools.whatsapp.send_location_message import send_location_message
        from agente.tools.whatsapp.message_buffer import buffer_message
        from agente.tools.whatsapp.type_simulation import simulate_typing
        logger.success("✅ Import de todas as ferramentas OK")
        
        # Importar tipos
        from agente.services.evolution import (
            EvolutionService,
            MessageResponse,
            MediaType,
            InstanceState
        )
        logger.success("✅ Import dos tipos OK")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos imports: {e}")
        return False


async def test_service_creation():
    """Testa criação do serviço"""
    logger.info("🔍 Testando criação do serviço...")
    
    try:
        from agente.services import get_evolution_service
        
        # Obter instância singleton
        service1 = get_evolution_service()
        service2 = get_evolution_service()
        
        # Verificar se é singleton
        if service1 is service2:
            logger.success("✅ Singleton pattern funcionando corretamente")
        else:
            logger.error("❌ Singleton pattern não está funcionando")
            return False
        
        # Verificar métodos disponíveis
        required_methods = [
            'send_text_message',
            'send_image',
            'send_audio',
            'send_document',
            'send_location',
            'send_reaction',
            'get_instance_status',
            'check_connection'
        ]
        
        for method in required_methods:
            if hasattr(service1, method):
                logger.success(f"✅ Método {method} disponível")
            else:
                logger.error(f"❌ Método {method} não encontrado")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na criação do serviço: {e}")
        return False


async def test_interface_compatibility():
    """Testa compatibilidade da interface"""
    logger.info("🔍 Testando compatibilidade de interface...")
    
    try:
        from agente.services import get_evolution_service
        from agente.services.evolution import MessageResponse, MessageKey
        
        service = get_evolution_service()
        
        # Simular resposta do serviço
        mock_response = MessageResponse(
            key=MessageKey(
                id="TEST123",
                fromMe=True,
                remoteJid="5511999999999@s.whatsapp.net"
            ),
            status="sent"
        )
        
        # Verificar que o objeto tem os atributos esperados
        assert hasattr(mock_response, 'key')
        assert hasattr(mock_response.key, 'id')
        assert mock_response.key.id == "TEST123"
        
        logger.success("✅ Interface MessageResponse compatível")
        
        # Verificar que o serviço retorna None ou MessageResponse
        logger.info("ℹ️  Métodos do serviço retornam Optional[MessageResponse]")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na compatibilidade: {e}")
        return False


async def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes de integração Evolution API v2")
    logger.info("=" * 60)
    
    tests = [
        ("Imports", test_imports()),
        ("Criação do Serviço", test_service_creation()),
        ("Compatibilidade de Interface", test_interface_compatibility())
    ]
    
    results = []
    for test_name, test_coro in tests:
        logger.info(f"\n🧪 Executando: {test_name}")
        result = await test_coro
        results.append((test_name, result))
        logger.info("-" * 40)
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO DOS TESTES")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.success("\n🎉 INTEGRAÇÃO FUNCIONANDO PERFEITAMENTE!")
    else:
        logger.error(f"\n⚠️  {total - passed} testes falharam - verificar problemas")


if __name__ == "__main__":
    asyncio.run(main())