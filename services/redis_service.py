"""
Redis Service
=============
Serviço de cache para otimização de performance
"""

import os
import json
import asyncio
from typing import Optional, Any, Dict, List
from datetime import timedelta
import redis.asyncio as aioredis
from loguru import logger
import pickle

class RedisService:
    """Serviço de cache com Redis"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.prefix = os.getenv("REDIS_PREFIX", "sdr_solarprime")
        self.ttl_default = int(os.getenv("REDIS_TTL_SECONDS", "3600"))  # 1 hora
        self.client: Optional[aioredis.Redis] = None
        self._lock = asyncio.Lock()
        
    async def connect(self):
        """Conecta ao Redis"""
        if self.client is None:
            async with self._lock:
                if self.client is None:
                    try:
                        # Tentar usar URL primeiro
                        if self.redis_url and "REDIS_URL" in os.environ:
                            self.client = await aioredis.from_url(
                                self.redis_url,
                                encoding="utf-8",
                                decode_responses=False  # Para suportar dados binários
                            )
                        else:
                            # Usar variáveis individuais
                            host = os.getenv("REDIS_HOST", "localhost")
                            port = int(os.getenv("REDIS_PORT", "6379"))
                            password = os.getenv("REDIS_PASSWORD")
                            username = os.getenv("REDIS_USERNAME", "default")
                            
                            redis_url = f"redis://{username}:{password}@{host}:{port}/0" if password else f"redis://{host}:{port}/0"
                            
                            self.client = await aioredis.from_url(
                                redis_url,
                                encoding="utf-8",
                                decode_responses=False
                            )
                        
                        await self.client.ping()
                        logger.info("✅ Redis conectado com sucesso")
                    except Exception as e:
                        logger.error(f"❌ Erro ao conectar ao Redis: {e}")
                        logger.info("🔄 Usando fallback em memória para cache")
                        self.client = None
                        # Não lançar erro - usar fallback
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Redis desconectado")
    
    def _make_key(self, key: str) -> str:
        """Cria chave com prefixo"""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        await self.connect()
        
        try:
            full_key = self._make_key(key)
            value = await self.client.get(full_key)
            
            if value is None:
                return None
            
            # Tentar deserializar como JSON primeiro
            try:
                return json.loads(value)
            except:
                # Se falhar, tentar como pickle
                try:
                    return pickle.loads(value)
                except:
                    # Se falhar, retornar como string
                    return value.decode() if isinstance(value, bytes) else value
                    
        except Exception as e:
            logger.error(f"Erro ao obter do cache: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Define valor no cache"""
        await self.connect()
        
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.ttl_default
            
            # Serializar valor
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                serialized = str(value)
            else:
                # Para objetos complexos, usar pickle
                serialized = pickle.dumps(value)
            
            await self.client.setex(full_key, ttl, serialized)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar no cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        await self.connect()
        
        try:
            full_key = self._make_key(key)
            result = await self.client.delete(full_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        await self.connect()
        
        try:
            full_key = self._make_key(key)
            return await self.client.exists(full_key) > 0
            
        except Exception as e:
            logger.error(f"Erro ao verificar existência: {e}")
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Obtém múltiplos valores"""
        await self.connect()
        
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        
        return result
    
    async def set_many(
        self, 
        data: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> bool:
        """Define múltiplos valores"""
        await self.connect()
        
        try:
            for key, value in data.items():
                await self.set(key, value, ttl)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar múltiplos valores: {e}")
            return False
    
    # Cache específico para WhatsApp
    
    async def cache_conversation_state(
        self, 
        phone: str, 
        state: Dict[str, Any],
        ttl: int = 7200  # 2 horas
    ) -> bool:
        """Cacheia estado da conversa"""
        key = f"conversation:{phone}"
        return await self.set(key, state, ttl)
    
    async def get_conversation_state(self, phone: str) -> Optional[Dict[str, Any]]:
        """Obtém estado da conversa do cache"""
        key = f"conversation:{phone}"
        return await self.get(key)
    
    async def cache_lead_data(
        self, 
        phone: str, 
        data: Dict[str, Any],
        ttl: int = 86400  # 24 horas
    ) -> bool:
        """Cacheia dados do lead"""
        key = f"lead:{phone}"
        return await self.set(key, data, ttl)
    
    async def get_lead_data(self, phone: str) -> Optional[Dict[str, Any]]:
        """Obtém dados do lead do cache"""
        key = f"lead:{phone}"
        return await self.get(key)
    
    async def cache_media(
        self, 
        media_id: str, 
        data: bytes,
        ttl: int = 3600  # 1 hora
    ) -> bool:
        """Cacheia mídia baixada"""
        key = f"media:{media_id}"
        return await self.set(key, data, ttl)
    
    async def get_media(self, media_id: str) -> Optional[bytes]:
        """Obtém mídia do cache"""
        key = f"media:{media_id}"
        return await self.get(key)
    
    async def increment_counter(
        self, 
        key: str, 
        amount: int = 1
    ) -> int:
        """Incrementa contador"""
        await self.connect()
        
        try:
            full_key = self._make_key(f"counter:{key}")
            return await self.client.incrby(full_key, amount)
            
        except Exception as e:
            logger.error(f"Erro ao incrementar contador: {e}")
            return 0
    
    async def get_counter(self, key: str) -> int:
        """Obtém valor do contador"""
        await self.connect()
        
        try:
            full_key = self._make_key(f"counter:{key}")
            value = await self.client.get(full_key)
            return int(value) if value else 0
            
        except Exception as e:
            logger.error(f"Erro ao obter contador: {e}")
            return 0


# Instância global
redis_service = RedisService()