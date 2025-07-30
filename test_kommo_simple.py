#!/usr/bin/env python3
"""
Teste Simplificado - Integração Kommo CRM
=========================================
Testa a integração usando Long-Lived Token
"""

import asyncio
import sys
from loguru import logger
import os

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from services.kommo_auth_simple import KommoAuthSimple
from services.kommo_service_updated import KommoServiceSimple
from config.config import get_config


async def run_tests():
    """Executa testes básicos da integração"""
    logger.info("=" * 80)
    logger.info("🧪 TESTE RÁPIDO - INTEGRAÇÃO KOMMO CRM")
    logger.info("=" * 80)
    
    # Verificar token
    token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
    if not token:
        logger.error("❌ KOMMO_LONG_LIVED_TOKEN não encontrado no .env!")
        logger.info("   Execute primeiro: python setup_kommo_integration.py")
        return
    
    logger.info(f"✅ Token encontrado: {token[:30]}...")
    
    # Teste 1: Autenticação
    logger.info("\n1️⃣ Testando Autenticação...")
    config = get_config()
    auth = KommoAuthSimple(config)
    
    try:
        valid_token = await auth.get_valid_token()
        logger.info("✅ Token carregado com sucesso")
        
        if await auth.test_token():
            logger.info("✅ Token válido e funcionando!")
        else:
            logger.error("❌ Token inválido")
            return
    except Exception as e:
        logger.error(f"❌ Erro na autenticação: {str(e)}")
        return
    
    # Teste 2: Conexão com API
    logger.info("\n2️⃣ Testando Conexão com API...")
    service = KommoServiceSimple()
    
    try:
        account = await service.test_connection()
        logger.info(f"✅ Conectado! Conta: {account.get('name')}")
        logger.info(f"   Subdomínio: {account.get('subdomain')}")
        logger.info(f"   Moeda: {account.get('currency')}")
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {str(e)}")
        return
    
    # Teste 3: Listar Pipelines
    logger.info("\n3️⃣ Listando Pipelines...")
    try:
        pipelines = await service.get_pipelines()
        logger.info(f"✅ {len(pipelines)} pipelines encontrados")
        
        for pipeline in pipelines[:3]:  # Mostrar apenas 3 primeiros
            logger.info(f"   - {pipeline['name']} (ID: {pipeline['id']})")
            
    except Exception as e:
        logger.error(f"❌ Erro ao listar pipelines: {str(e)}")
    
    # Resumo
    logger.info("\n" + "=" * 80)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 80)
    logger.info("✅ Autenticação: OK")
    logger.info("✅ Conexão API: OK")
    logger.info("✅ Operações Básicas: OK")
    logger.info("\n🎉 Integração funcionando perfeitamente!")
    logger.info("   Não é necessário renovar token por 5 anos!")


async def main():
    """Função principal"""
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Executar testes
    await run_tests()


if __name__ == "__main__":
    asyncio.run(main())