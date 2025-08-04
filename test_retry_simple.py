#!/usr/bin/env python3
"""
Teste simples do sistema de retry
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.retry_handler import async_retry, RetryConfig
from loguru import logger


# Simula uma API que falha aleatoriamente
class FakeAPI:
    def __init__(self):
        self.call_count = 0
    
    async def call(self, fail_times=2):
        """Simula chamada que falha as primeiras N vezes"""
        self.call_count += 1
        logger.info(f"Tentativa {self.call_count}")
        
        if self.call_count <= fail_times:
            raise Exception(f"500 INTERNAL - Erro simulado (tentativa {self.call_count})")
        
        return f"Sucesso na tentativa {self.call_count}!"


async def test_retry():
    """Testa o sistema de retry"""
    
    # Teste 1: Com retry padrão
    logger.info("=== Teste 1: Retry com erro 500 ===")
    api = FakeAPI()
    
    @async_retry(RetryConfig(max_attempts=5, initial_delay=0.5))
    async def call_with_retry():
        return await api.call(fail_times=3)
    
    try:
        result = await call_with_retry()
        logger.success(f"✅ {result}")
    except Exception as e:
        logger.error(f"❌ Falhou após todas tentativas: {e}")
    
    
    # Teste 2: Erro não recuperável
    logger.info("\n=== Teste 2: Erro não recuperável ===")
    
    @async_retry(RetryConfig(max_attempts=3))
    async def call_non_retryable():
        raise ValueError("Este erro não é recuperável")
    
    try:
        await call_non_retryable()
    except ValueError as e:
        logger.info(f"✅ Erro não recuperável detectado corretamente: {e}")
    
    
    # Teste 3: Sucesso na primeira tentativa
    logger.info("\n=== Teste 3: Sucesso imediato ===")
    api3 = FakeAPI()
    
    @async_retry()
    async def call_success():
        return await api3.call(fail_times=0)
    
    result = await call_success()
    logger.success(f"✅ {result}")
    
    
    logger.info("\n🏁 Todos os testes concluídos!")


if __name__ == "__main__":
    asyncio.run(test_retry())