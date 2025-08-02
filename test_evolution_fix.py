#!/usr/bin/env python3
"""
Script de teste para verificar as correções no Evolution API Service
"""

import asyncio
import sys
import os

# Adiciona o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agente.services.evolution_service import get_evolution_service
from agente.core.logger import logger

async def test_evolution_fixes():
    """
    Testa as correções implementadas no Evolution API Service
    """
    
    logger.info("🧪 Iniciando teste das correções Evolution API")
    
    # Inicializa o serviço
    evolution_service = get_evolution_service()
    
    try:
        # 1. Testa verificação de status da instância
        logger.info("📡 Testando verificação de status da instância...")
        status = await evolution_service.get_instance_status()
        
        if status:
            instance_state = status.get("state", "unknown")
            logger.info(f"✅ Status da instância: {instance_state}")
            
            if instance_state != "open":
                logger.warning(f"⚠️  Instância não está conectada (estado: {instance_state})")
                logger.info("💡 Verifique se o WhatsApp está conectado na Evolution API")
                return False
        else:
            logger.error("❌ Não foi possível verificar o status da instância")
            return False
        
        # 2. Testa envio de mensagem simples
        logger.info("📱 Testando envio de mensagem simples...")
        
        # Use um número de teste válido aqui ou configure nas variáveis de ambiente
        test_phone = "5581999999999"  # Substitua por um número de teste
        test_message = "🧪 Teste das correções Evolution API - mensagem simples"
        
        result = await evolution_service.send_text_message(
            phone=test_phone,
            text=test_message,
            delay=2,
            enable_typing=True,
            chunk_manually=False
        )
        
        if result:
            message_id = result.get("key", {}).get("id", "unknown")
            status = result.get("status", "unknown")
            logger.info(f"✅ Mensagem enviada com sucesso (ID: {message_id}, Status: {status})")
        else:
            logger.error("❌ Falha no envio da mensagem")
            return False
        
        # 3. Testa envio de mensagem longa (chunking)
        logger.info("📱 Testando envio de mensagem longa com chunking...")
        
        long_message = """🧪 Teste de mensagem longa para verificar o chunking automático.
        
Esta mensagem foi dividida automaticamente para garantir que seja entregue corretamente pelo WhatsApp.

O sistema agora usa a estrutura oficial do Evolution API v2 e inclui:
- Verificação de conectividade da instância
- Tratamento de erro mais específico
- Estrutura de dados corrigida
- Chunking inteligente para mensagens longas
- Logs mais informativos

Teste concluído com sucesso! 🎉"""
        
        result = await evolution_service.send_text_message(
            phone=test_phone,
            text=long_message,
            delay=3,
            enable_typing=True,
            chunk_manually=True
        )
        
        if result:
            logger.info("✅ Mensagem longa enviada com sucesso (com chunking)")
        else:
            logger.error("❌ Falha no envio da mensagem longa")
            return False
        
        logger.info("🎉 Todos os testes passaram com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {str(e)}")
        return False
    
    finally:
        # Fecha o cliente HTTP
        await evolution_service.close()

async def main():
    """Função principal"""
    
    print("=" * 60)
    print("🚀 TESTE DAS CORREÇÕES EVOLUTION API SERVICE")
    print("=" * 60)
    
    # Executa os testes
    success = await test_evolution_fixes()
    
    print("=" * 60)
    if success:
        print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
        print("💡 As correções foram aplicadas e estão funcionando.")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("💡 Verifique os logs acima para mais detalhes.")
    print("=" * 60)

if __name__ == "__main__":
    # Executa o teste
    asyncio.run(main())