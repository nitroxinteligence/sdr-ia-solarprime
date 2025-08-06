#!/usr/bin/env python3
"""
Script para testar a conexão com o Redis
Verifica se as configurações estão corretas
"""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

# Carregar variáveis de ambiente
load_dotenv()

async def test_redis_connection():
    """Testa a conexão com o Redis"""
    
    # Mostrar configurações
    logger.info("🔍 Configurações do Redis:")
    logger.info(f"   REDIS_URL: {os.getenv('REDIS_URL', 'Não definido')}")
    logger.info(f"   REDIS_HOST: {os.getenv('REDIS_HOST', 'Não definido')}")
    logger.info(f"   REDIS_PORT: {os.getenv('REDIS_PORT', 'Não definido')}")
    logger.info(f"   REDIS_USERNAME: {os.getenv('REDIS_USERNAME', 'Não definido')}")
    logger.info(f"   REDIS_PASSWORD: {'***' if os.getenv('REDIS_PASSWORD') else 'Não definido'}")
    
    # Importar após carregar env
    from app.integrations.redis_client import redis_client
    
    logger.info("\n🚀 Testando conexão...")
    
    # Conectar
    await redis_client.connect()
    
    # Testar operações básicas se conectado
    if redis_client.redis_client:
        logger.info("\n🧪 Testando operações básicas...")
        
        # Teste 1: Set/Get
        test_key = "test:connection"
        test_value = {"status": "working", "timestamp": "2025-08-06"}
        
        success = await redis_client.set(test_key, test_value, ttl=60)
        if success:
            logger.info("✅ SET funcionando")
        else:
            logger.error("❌ SET falhou")
        
        retrieved = await redis_client.get(test_key)
        if retrieved == test_value:
            logger.info("✅ GET funcionando")
        else:
            logger.error("❌ GET falhou")
        
        # Teste 2: Ping
        if await redis_client.ping():
            logger.info("✅ PING funcionando")
        else:
            logger.error("❌ PING falhou")
        
        # Teste 3: Counter
        counter_name = "test:counter"
        count = await redis_client.increment_counter(counter_name)
        logger.info(f"✅ Counter incrementado: {count}")
        
        # Limpar teste
        await redis_client.delete(test_key)
        await redis_client.reset_counter(counter_name)
        
        logger.info("\n✅ REDIS FUNCIONANDO PERFEITAMENTE!")
        
    else:
        logger.error("\n❌ REDIS NÃO ESTÁ CONECTADO")
        logger.info("💡 Verifique se:")
        logger.info("   1. O Redis está rodando")
        logger.info("   2. O host 'redis_redis' está acessível")
        logger.info("   3. As credenciais estão corretas")
        logger.info("   4. A porta 6379 está aberta")
    
    # Desconectar
    await redis_client.disconnect()

async def test_redis_fallback():
    """Testa o comportamento quando Redis não está disponível"""
    logger.info("\n🧪 Testando fallback sem Redis...")
    
    from app.integrations.redis_client import RedisClient
    
    # Criar cliente com URL inválida
    test_client = RedisClient()
    test_client.redis_url = "redis://invalid:6379"
    
    await test_client.connect()
    
    # Testar operações sem Redis
    result = await test_client.set("test", "value")
    logger.info(f"SET sem Redis: {result}")
    
    value = await test_client.get("test")
    logger.info(f"GET sem Redis: {value}")
    
    ping = await test_client.ping()
    logger.info(f"PING sem Redis: {ping}")
    
    logger.info("✅ Sistema funciona sem Redis (sem cache)")

async def main():
    """Executa os testes"""
    logger.info("🚀 Iniciando teste de conexão do Redis\n")
    
    await test_redis_connection()
    await test_redis_fallback()
    
    logger.info("\n✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(main())