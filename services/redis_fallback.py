"""
Redis Fallback Service
======================
Serviço de cache em memória para quando Redis não está disponível
"""

import asyncio
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
from loguru import logger
import json

class InMemoryCache:
    """Cache em memória como fallback"""
    
    def __init__(self):
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()
        logger.warning("⚠️ Usando cache em memória (Redis não disponível)")
        
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        async with self._lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if datetime.now() < expiry:
                    return value
                else:
                    # Expirado, remover
                    del self.cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Define valor no cache"""
        async with self._lock:
            expiry = datetime.now() + timedelta(seconds=ttl)
            self.cache[key] = (value, expiry)
            return True
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        value = await self.get(key)
        return value is not None
    
    async def cleanup_expired(self):
        """Remove itens expirados"""
        async with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if now >= expiry
            ]
            for key in expired_keys:
                del self.cache[key]


class RedisFallbackService:
    """Serviço que tenta usar Redis, mas cai para memória se não disponível"""
    
    def __init__(self):
        self.redis_service = None
        self.fallback_cache = InMemoryCache()
        self.use_fallback = False
        self.prefix = "sdr_solarprime"
        self.ttl_default = 3600
        self._cleanup_task = None
        self._connection_lock = asyncio.Lock()
    
    async def _cleanup_loop(self):
        """Loop de limpeza de cache expirado"""
        while True:
            await asyncio.sleep(300)  # A cada 5 minutos
            if self.use_fallback:
                await self.fallback_cache.cleanup_expired()
    
    async def _ensure_cleanup_task(self):
        """Garante que a task de limpeza está rodando"""
        if self._cleanup_task is None or self._cleanup_task.done():
            try:
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            except RuntimeError:
                # Se não há loop rodando, ignorar por enquanto
                pass
    
    async def _try_redis_connection(self):
        """Tenta conectar ao Redis"""
        # Garantir que cleanup está rodando
        try:
            await self._ensure_cleanup_task()
        except Exception as e:
            logger.warning(f"Erro ao garantir task de limpeza: {e}")
        
        # Usar lock para evitar múltiplas tentativas simultâneas de conexão
        async with self._connection_lock:
            if not self.use_fallback and self.redis_service is not None:
                return  # Já está usando Redis
                
            try:
                from services.redis_service import redis_service
                await redis_service.connect()
                self.redis_service = redis_service
                self.use_fallback = False
                logger.info("✅ Conectado ao Redis")
            except Exception as e:
                self.use_fallback = True
                # logger.debug(f"Redis indisponível, usando cache em memória: {e}")
    
    def _make_key(self, key: str) -> str:
        """Cria chave com prefixo"""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        await self._try_redis_connection()
        
        full_key = self._make_key(key)
        
        if self.use_fallback:
            return await self.fallback_cache.get(full_key)
        else:
            return await self.redis_service.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        await self._try_redis_connection()
        
        ttl = ttl or self.ttl_default
        full_key = self._make_key(key)
        
        if self.use_fallback:
            return await self.fallback_cache.set(full_key, value, ttl)
        else:
            return await self.redis_service.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        await self._try_redis_connection()
        
        full_key = self._make_key(key)
        
        if self.use_fallback:
            return await self.fallback_cache.delete(full_key)
        else:
            return await self.redis_service.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        await self._try_redis_connection()
        
        full_key = self._make_key(key)
        
        if self.use_fallback:
            return await self.fallback_cache.exists(full_key)
        else:
            return await self.redis_service.exists(key)
    
    # Métodos específicos do WhatsApp
    
    async def cache_conversation_state(
        self, 
        phone: str, 
        state: Dict[str, Any],
        ttl: int = 7200
    ) -> bool:
        """Cacheia estado da conversa"""
        key = f"conversation:{phone}"
        return await self.set(key, state, ttl)
    
    async def get_conversation_state(self, phone: str) -> Optional[Dict[str, Any]]:
        """Obtém estado da conversa do cache"""
        key = f"conversation:{phone}"
        return await self.get(key)
    
    async def cache_media(
        self, 
        media_id: str, 
        data: bytes,
        ttl: int = 3600
    ) -> bool:
        """Cacheia mídia baixada"""
        key = f"media:{media_id}"
        return await self.set(key, data, ttl)
    
    async def get_media(self, media_id: str) -> Optional[bytes]:
        """Obtém mídia do cache"""
        key = f"media:{media_id}"
        return await self.get(key)
    
    async def clear_conversation_state(self, phone: str) -> bool:
        """Limpa todo o estado de conversa do cache"""
        keys_to_delete = [
            f"{self.prefix}:conversation:{phone}",
            f"{self.prefix}:reasoning:{phone}",
            f"{self.prefix}:lead:{phone}",
            f"{self.prefix}:stage:{phone}",
            f"{self.prefix}:context:{phone}"
        ]
        
        success = True
        for key in keys_to_delete:
            if not await self.delete(key):
                success = False
        
        logger.info(f"Cache limpo para {phone}: {'sucesso' if success else 'parcial'}")
        return success


# Instância global será criada sob demanda
redis_fallback_service = None

def get_redis_fallback_service():
    """Obtém instância do serviço com fallback"""
    global redis_fallback_service
    if redis_fallback_service is None:
        redis_fallback_service = RedisFallbackService()
    return redis_fallback_service