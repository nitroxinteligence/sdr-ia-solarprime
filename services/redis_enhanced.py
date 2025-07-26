"""
Redis Enhanced Service
======================
Serviço de cache Redis com melhorias de resiliência e fallback inteligente
"""

import os
import asyncio
from typing import Optional, Any, Dict, List
from datetime import timedelta
import redis.asyncio as aioredis
from loguru import logger
import pickle
import json
import backoff

class RedisEnhancedService:
    """Serviço Redis melhorado com resiliência e fallback inteligente"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.prefix = os.getenv("REDIS_PREFIX", "sdr_solarprime")
        self.ttl_default = int(os.getenv("REDIS_TTL_SECONDS", "3600"))
        
        # Configurações de retry
        self.max_retries = int(os.getenv("REDIS_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("REDIS_RETRY_DELAY", "1.0"))
        
        # Estado da conexão
        self.client: Optional[aioredis.Redis] = None
        self._lock = asyncio.Lock()
        self._is_connected = False
        self._last_error: Optional[Exception] = None
        self._health_check_task: Optional[asyncio.Task] = None
        self._connection_attempts = 0
        
        # Configurações de pool
        self.pool_config = {
            'max_connections': int(os.getenv("REDIS_POOL_MAX_CONNECTIONS", "50")),
            'health_check_interval': int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30")),
            'retry_on_timeout': True,
            'socket_keepalive': True,
            'socket_keepalive_options': {
                1: 1,  # TCP_KEEPIDLE
                2: 3,  # TCP_KEEPINTVL  
                3: 5,  # TCP_KEEPCNT
            }
        }
    
    @backoff.on_exception(
        backoff.expo,
        (aioredis.ConnectionError, aioredis.TimeoutError),
        max_tries=3,
        max_time=10
    )
    async def _create_connection(self) -> aioredis.Redis:
        """Cria conexão com Redis com retry automático"""
        logger.debug(f"Tentando conectar ao Redis: {self.redis_url}")
        
        # Criar pool de conexões
        pool = aioredis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=self.pool_config['max_connections'],
            decode_responses=False,
            retry_on_timeout=self.pool_config['retry_on_timeout'],
            health_check_interval=self.pool_config['health_check_interval'],
            socket_keepalive=self.pool_config['socket_keepalive'],
            socket_keepalive_options=self.pool_config['socket_keepalive_options']
        )
        
        client = aioredis.Redis(connection_pool=pool)
        
        # Testar conexão
        await client.ping()
        
        return client
    
    async def connect(self) -> bool:
        """Conecta ao Redis com tratamento melhorado de erros"""
        if self._is_connected and self.client:
            return True
            
        async with self._lock:
            if self._is_connected and self.client:
                return True
                
            try:
                self._connection_attempts += 1
                
                # Tentar criar conexão
                self.client = await self._create_connection()
                
                self._is_connected = True
                self._last_error = None
                self._connection_attempts = 0
                
                logger.success(f"✅ Redis conectado com sucesso (tentativa {self._connection_attempts})")
                
                # Iniciar health check
                if not self._health_check_task:
                    self._health_check_task = asyncio.create_task(self._health_check_loop())
                
                return True
                
            except Exception as e:
                self._is_connected = False
                self._last_error = e
                self.client = None
                
                logger.warning(
                    f"⚠️ Falha ao conectar ao Redis (tentativa {self._connection_attempts}): {e}\n"
                    f"Usando fallback em memória"
                )
                
                return False
    
    async def _health_check_loop(self):
        """Loop de verificação de saúde da conexão"""
        while True:
            await asyncio.sleep(self.pool_config['health_check_interval'])
            
            if not self._is_connected or not self.client:
                continue
                
            try:
                # Verificar conexão
                await self.client.ping()
                logger.debug("Redis health check: OK")
                
            except Exception as e:
                logger.error(f"Redis health check falhou: {e}")
                self._is_connected = False
                
                # Tentar reconectar
                await self.connect()
    
    async def disconnect(self):
        """Desconecta do Redis com limpeza adequada"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        
        if self.client:
            await self.client.close()
            await self.client.connection_pool.disconnect()
            self.client = None
            self._is_connected = False
            logger.info("Redis desconectado")
    
    def _make_key(self, key: str) -> str:
        """Cria chave com prefixo"""
        return f"{self.prefix}:{key}"
    
    async def _ensure_connected(self) -> bool:
        """Garante que está conectado antes de operações"""
        if not self._is_connected:
            return await self.connect()
        return True
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache com resiliência"""
        if not await self._ensure_connected():
            return None
            
        try:
            full_key = self._make_key(key)
            value = await self.client.get(full_key)
            
            if value is None:
                return None
            
            # Deserializar valor
            try:
                return json.loads(value)
            except:
                try:
                    return pickle.loads(value)
                except:
                    return value.decode() if isinstance(value, bytes) else value
                    
        except aioredis.ConnectionError:
            self._is_connected = False
            logger.error("Conexão perdida durante GET")
            return None
        except Exception as e:
            logger.error(f"Erro ao obter do cache: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Define valor no cache com resiliência"""
        if not await self._ensure_connected():
            return False
            
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.ttl_default
            
            # Serializar valor
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                serialized = str(value)
            else:
                serialized = pickle.dumps(value)
            
            await self.client.setex(full_key, ttl, serialized)
            return True
            
        except aioredis.ConnectionError:
            self._is_connected = False
            logger.error("Conexão perdida durante SET")
            return False
        except Exception as e:
            logger.error(f"Erro ao salvar no cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache com resiliência"""
        if not await self._ensure_connected():
            return False
            
        try:
            full_key = self._make_key(key)
            result = await self.client.delete(full_key)
            return result > 0
            
        except aioredis.ConnectionError:
            self._is_connected = False
            logger.error("Conexão perdida durante DELETE")
            return False
        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe com resiliência"""
        if not await self._ensure_connected():
            return False
            
        try:
            full_key = self._make_key(key)
            return await self.client.exists(full_key) > 0
            
        except aioredis.ConnectionError:
            self._is_connected = False
            logger.error("Conexão perdida durante EXISTS")
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar existência: {e}")
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Obtém múltiplos valores com resiliência"""
        if not await self._ensure_connected():
            return {}
            
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
        """Define múltiplos valores com resiliência"""
        if not await self._ensure_connected():
            return False
            
        success = True
        for key, value in data.items():
            if not await self.set(key, value, ttl):
                success = False
        
        return success
    
    # Métodos específicos para WhatsApp
    
    async def cache_conversation_state(
        self, 
        phone: str, 
        state: Dict[str, Any],
        ttl: int = 7200
    ) -> bool:
        """Cacheia estado da conversa com resiliência"""
        key = f"conversation:{phone}"
        return await self.set(key, state, ttl)
    
    async def get_conversation_state(self, phone: str) -> Optional[Dict[str, Any]]:
        """Obtém estado da conversa do cache com resiliência"""
        key = f"conversation:{phone}"
        return await self.get(key)
    
    async def cache_lead_data(
        self, 
        phone: str, 
        data: Dict[str, Any],
        ttl: int = 86400
    ) -> bool:
        """Cacheia dados do lead com resiliência"""
        key = f"lead:{phone}"
        return await self.set(key, data, ttl)
    
    async def get_lead_data(self, phone: str) -> Optional[Dict[str, Any]]:
        """Obtém dados do lead do cache com resiliência"""
        key = f"lead:{phone}"
        return await self.get(key)
    
    async def cache_media(
        self, 
        media_id: str, 
        data: bytes,
        ttl: int = 3600
    ) -> bool:
        """Cacheia mídia baixada com resiliência"""
        key = f"media:{media_id}"
        return await self.set(key, data, ttl)
    
    async def get_media(self, media_id: str) -> Optional[bytes]:
        """Obtém mídia do cache com resiliência"""
        key = f"media:{media_id}"
        return await self.get(key)
    
    async def increment_counter(
        self, 
        key: str, 
        amount: int = 1
    ) -> int:
        """Incrementa contador com resiliência"""
        if not await self._ensure_connected():
            return 0
            
        try:
            full_key = self._make_key(f"counter:{key}")
            return await self.client.incrby(full_key, amount)
            
        except aioredis.ConnectionError:
            self._is_connected = False
            logger.error("Conexão perdida durante INCREMENT")
            return 0
        except Exception as e:
            logger.error(f"Erro ao incrementar contador: {e}")
            return 0
    
    async def get_counter(self, key: str) -> int:
        """Obtém valor do contador com resiliência"""
        if not await self._ensure_connected():
            return 0
            
        try:
            full_key = self._make_key(f"counter:{key}")
            value = await self.client.get(full_key)
            return int(value) if value else 0
            
        except aioredis.ConnectionError:
            self._is_connected = False
            logger.error("Conexão perdida durante GET_COUNTER")
            return 0
        except Exception as e:
            logger.error(f"Erro ao obter contador: {e}")
            return 0
    
    # Métodos de monitoramento
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do Redis"""
        if not await self._ensure_connected():
            return {
                "connected": False,
                "error": str(self._last_error) if self._last_error else "Not connected"
            }
            
        try:
            info = await self.client.info()
            return {
                "connected": True,
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands": info.get("total_commands_processed"),
                "uptime_days": info.get("uptime_in_days")
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    @property
    def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self._is_connected
    
    @property
    def connection_info(self) -> Dict[str, Any]:
        """Informações sobre a conexão"""
        return {
            "url": self.redis_url,
            "connected": self._is_connected,
            "attempts": self._connection_attempts,
            "last_error": str(self._last_error) if self._last_error else None,
            "pool_max_connections": self.pool_config['max_connections']
        }


# Instância global
redis_enhanced = RedisEnhancedService()