"""
Cache Utilities
===============
Utilitários de cache para o sistema
"""

from services.redis_service import RedisService
from loguru import logger

# Criar instância do Redis
redis_service = RedisService()

# Cliente Redis para uso direto
redis_client = None

async def get_redis_client():
    """Obtém cliente Redis conectado"""
    global redis_client
    if not redis_client:
        await redis_service.connect()
        redis_client = redis_service.client
    return redis_client

# Wrapper simplificado para compatibilidade
class RedisClient:
    """Wrapper para cliente Redis com interface simplificada"""
    
    def __init__(self):
        self._service = redis_service
    
    async def _ensure_connected(self):
        """Garante que está conectado"""
        if not self._service.client:
            await self._service.connect()
    
    def setex(self, key: str, seconds: int, value: str):
        """Set com expiração (síncrono para compatibilidade)"""
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Se já estiver em contexto async, agenda para execução
            asyncio.create_task(self._async_setex(key, seconds, value))
        else:
            # Se não, executa síncronamente
            loop.run_until_complete(self._async_setex(key, seconds, value))
    
    async def _async_setex(self, key: str, seconds: int, value: str):
        """Set com expiração assíncrono"""
        await self._ensure_connected()
        await self._service.client.setex(key, seconds, value)
    
    def get(self, key: str) -> str:
        """Get síncrono para compatibilidade"""
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Em contexto async, retorna None por segurança
            logger.warning(f"Tentativa de get síncrono em contexto async para key: {key}")
            return None
        else:
            return loop.run_until_complete(self._async_get(key))
    
    async def _async_get(self, key: str) -> str:
        """Get assíncrono"""
        await self._ensure_connected()
        value = await self._service.client.get(key)
        return value.decode() if value else None
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe (síncrono)"""
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return False
        else:
            return loop.run_until_complete(self._async_exists(key))
    
    async def _async_exists(self, key: str) -> bool:
        """Verifica se chave existe (assíncrono)"""
        await self._ensure_connected()
        return await self._service.client.exists(key) > 0
    
    def delete(self, key: str):
        """Delete síncrono para compatibilidade"""
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self._async_delete(key))
        else:
            loop.run_until_complete(self._async_delete(key))
    
    async def _async_delete(self, key: str):
        """Delete assíncrono"""
        await self._ensure_connected()
        await self._service.client.delete(key)

# Instância global para compatibilidade
redis_client = RedisClient()

# Exportar ambos
__all__ = ['redis_service', 'redis_client', 'get_redis_client']