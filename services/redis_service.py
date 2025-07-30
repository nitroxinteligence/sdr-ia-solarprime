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

# Importar configuração centralizada
try:
    from core.environment import env_config
except ImportError:
    env_config = None

class RedisService:
    """Serviço de cache com Redis"""
    
    def __init__(self):
        # Obter ambiente
        environment = os.getenv("ENVIRONMENT", "development")
        
        # Usar configuração centralizada se disponível
        if env_config:
            self.redis_url = env_config.redis_url
        else:
            # Fallback para configuração manual
            if environment == "production":
                # Em produção, usar nome do serviço Docker
                self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
            else:
                # Em desenvolvimento, usar localhost
                self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Lista de URLs Redis para fallback (útil em produção)
        self.redis_urls = []
        if environment == "production":
            # Adicionar múltiplos hosts Redis para fallback
            fallback_hosts = os.getenv("REDIS_FALLBACK_HOSTS", "").split(",")
            if fallback_hosts and fallback_hosts[0]:
                self.redis_urls.extend([f"redis://{host.strip()}/0" for host in fallback_hosts])
            
            # Adicionar URL principal e possíveis variações
            self.redis_urls.extend([
                self.redis_url,
                "redis://redis:6379/0",
                "redis://localhost:6379/0",
                "redis://127.0.0.1:6379/0"
            ])
        else:
            self.redis_urls = [self.redis_url]
        
        self.prefix = os.getenv("REDIS_PREFIX", "sdr_solarprime")
        self.ttl_default = int(os.getenv("REDIS_TTL_SECONDS", "3600"))  # 1 hora
        self.client: Optional[aioredis.Redis] = None
        self._lock = asyncio.Lock()
        self._memory_cache: Dict[str, Any] = {}  # Cache em memória como fallback
        self._cache_lock = asyncio.Lock()  # Lock específico para operações no cache em memória
        
    async def connect(self):
        """Conecta ao Redis tentando múltiplos hosts em caso de falha"""
        if self.client is None:
            async with self._lock:
                if self.client is None:
                    connection_timeout = int(os.getenv("REDIS_CONNECTION_TIMEOUT", "5"))
                    
                    # Tentar conectar a cada URL Redis disponível
                    for redis_url in self.redis_urls:
                        try:
                            logger.info(f"🔄 Tentando conectar ao Redis: {redis_url}")
                            
                            # Criar cliente com timeout
                            test_client = await aioredis.from_url(
                                redis_url,
                                encoding="utf-8",
                                decode_responses=False,
                                socket_connect_timeout=connection_timeout,
                                socket_timeout=connection_timeout,
                                retry_on_timeout=True,
                                health_check_interval=30
                            )
                            
                            # Testar conexão com timeout
                            await asyncio.wait_for(test_client.ping(), timeout=3.0)
                            
                            # Se chegou aqui, a conexão funcionou
                            self.client = test_client
                            logger.success(f"✅ Redis conectado com sucesso em {redis_url}")
                            return
                            
                        except asyncio.TimeoutError:
                            logger.warning(f"⏱️ Timeout ao conectar ao Redis em {redis_url}")
                            continue
                        except Exception as e:
                            logger.warning(f"❌ Falha ao conectar em {redis_url}: {type(e).__name__}: {str(e)}")
                            continue
                    
                    # Se chegou aqui, nenhuma conexão funcionou
                    if env_config and env_config.is_development:
                        logger.info("ℹ️ Redis não disponível em desenvolvimento")
                        logger.debug("💡 Para desenvolvimento com cache, inicie o Redis localmente")
                    else:
                        logger.error("❌ Não foi possível conectar a nenhum servidor Redis")
                        logger.info(f"📍 URLs tentadas: {', '.join(self.redis_urls)}")
                    
                    logger.info("🔄 Usando fallback em memória para cache")
                    self.client = None
    
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
        
        # Se não há cliente (Redis não disponível), usar cache em memória
        if self.client is None:
            async with self._cache_lock:
                full_key = self._make_key(key)
                cache_entry = self._memory_cache.get(full_key)
                if cache_entry:
                    # Verificar se expirou
                    import time
                    if cache_entry['expire_at'] > time.time():
                        return cache_entry['value']
                    else:
                        # Remover entrada expirada
                        del self._memory_cache[full_key]
                return None
        
        try:
            full_key = self._make_key(key)
            value = await self.client.get(full_key)
            
            if value is None:
                return None
            
            # Tentar deserializar como JSON primeiro
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Se falhar, tentar como pickle
                try:
                    return pickle.loads(value)
                except (pickle.UnpicklingError, TypeError):
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
        
        # Se não há cliente (Redis não disponível), usar cache em memória
        if self.client is None:
            async with self._cache_lock:
                import time
                full_key = self._make_key(key)
                ttl = ttl or self.ttl_default
                self._memory_cache[full_key] = {
                    'value': value,
                    'expire_at': time.time() + ttl
                }
                # Limitar tamanho do cache em memória
                if len(self._memory_cache) > 1000:
                    # Remover entradas expiradas
                    current_time = time.time()
                    expired_keys = [k for k, v in self._memory_cache.items() if v['expire_at'] <= current_time]
                    for k in expired_keys:
                        del self._memory_cache[k]
                    # Se ainda estiver muito grande, remover as mais antigas
                    if len(self._memory_cache) > 1000:
                        sorted_keys = sorted(self._memory_cache.keys(), key=lambda k: self._memory_cache[k]['expire_at'])
                        for k in sorted_keys[:len(sorted_keys) - 900]:
                            del self._memory_cache[k]
                return True
        
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
        
        # Se não há cliente (Redis não disponível), usar cache em memória
        if self.client is None:
            async with self._cache_lock:
                full_key = self._make_key(key)
                if full_key in self._memory_cache:
                    del self._memory_cache[full_key]
                    return True
                return False
        
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
        
        # Se não há cliente (Redis não disponível), usar cache em memória
        if self.client is None:
            async with self._cache_lock:
                full_key = self._make_key(key)
                cache_entry = self._memory_cache.get(full_key)
                if cache_entry:
                    import time
                    if cache_entry['expire_at'] > time.time():
                        return True
                    else:
                        del self._memory_cache[full_key]
                return False
        
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