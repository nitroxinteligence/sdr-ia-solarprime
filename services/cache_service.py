"""
Cache Service
=============
Serviço de cache agressivo para otimização de performance
"""

from typing import Any, Dict, Optional, Callable, TypeVar, cast
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from functools import wraps
import hashlib
import json

from services.redis_fallback import get_redis_fallback_service

T = TypeVar('T')


class AggressiveCache:
    """Cache em 2 níveis: memória (L1) e Redis (L2)"""
    
    def __init__(self):
        self.redis = get_redis_fallback_service()
        self.memory_cache: Dict[str, tuple[Any, datetime]] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'redis_hits': 0
        }
        
    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable,
        ttl: int = 3600,
        memory_ttl: int = 300  # 5 minutos em memória
    ) -> Any:
        """
        Cache em 2 níveis com computação lazy
        
        Args:
            key: Chave do cache
            compute_fn: Função para computar o valor se não estiver em cache
            ttl: TTL para Redis (padrão 1 hora)
            memory_ttl: TTL para cache em memória (padrão 5 minutos)
        """
        # L1: Cache em memória
        if key in self.memory_cache:
            value, expiry = self.memory_cache[key]
            if datetime.now() < expiry:
                self.cache_stats['hits'] += 1
                self.cache_stats['memory_hits'] += 1
                logger.debug(f"Cache L1 hit: {key}")
                return value
            else:
                # Expirado, remover
                del self.memory_cache[key]
                
        # L2: Redis
        value = await self.redis.get(key)
        if value is not None:
            self.cache_stats['hits'] += 1
            self.cache_stats['redis_hits'] += 1
            logger.debug(f"Cache L2 hit: {key}")
            
            # Adicionar ao cache L1
            self.memory_cache[key] = (value, datetime.now() + timedelta(seconds=memory_ttl))
            return value
            
        # Cache miss - computar valor
        self.cache_stats['misses'] += 1
        logger.debug(f"Cache miss: {key}")
        
        # Se compute_fn é assíncrona
        if asyncio.iscoroutinefunction(compute_fn):
            value = await compute_fn()
        else:
            value = compute_fn()
            
        # Salvar em ambos os níveis
        self.memory_cache[key] = (value, datetime.now() + timedelta(seconds=memory_ttl))
        await self.redis.set(key, value, ttl)
        
        return value
        
    async def invalidate(self, key: str):
        """Invalida cache em ambos os níveis"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        await self.redis.delete(key)
        
    async def invalidate_pattern(self, pattern: str):
        """Invalida todas as chaves que correspondem ao padrão"""
        # Invalidar memória
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
            
        # Redis não suporta invalidação por padrão facilmente
        # Por ora, apenas log
        logger.info(f"Invalidated {len(keys_to_delete)} keys matching pattern: {pattern}")
        
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            'total_requests': total,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': f"{hit_rate:.2f}%",
            'memory_hits': self.cache_stats['memory_hits'],
            'redis_hits': self.cache_stats['redis_hits'],
            'memory_cache_size': len(self.memory_cache)
        }
        
    def clear_memory_cache(self):
        """Limpa apenas o cache em memória"""
        self.memory_cache.clear()
        logger.info("Memory cache cleared")


# Instância global
cache_service = AggressiveCache()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator para cache automático de funções
    
    Args:
        ttl: Tempo de vida do cache em segundos
        key_prefix: Prefixo para a chave do cache
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # Gerar chave baseada na função e argumentos
            cache_key = _generate_cache_key(func.__name__, key_prefix, args, kwargs)
            
            # Tentar obter do cache ou computar
            result = await cache_service.get_or_compute(
                key=cache_key,
                compute_fn=lambda: func(*args, **kwargs),
                ttl=ttl
            )
            
            return cast(T, result)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # Para funções síncronas, usar run_until_complete
            cache_key = _generate_cache_key(func.__name__, key_prefix, args, kwargs)
            
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                cache_service.get_or_compute(
                    key=cache_key,
                    compute_fn=lambda: func(*args, **kwargs),
                    ttl=ttl
                )
            )
            
            return cast(T, result)
            
        # Retornar wrapper apropriado
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def _generate_cache_key(func_name: str, prefix: str, args: tuple, kwargs: dict) -> str:
    """Gera chave única para cache baseada nos argumentos"""
    # Criar representação dos argumentos
    key_parts = [prefix, func_name]
    
    # Adicionar args (pular 'self' se for método)
    start_idx = 1 if args and hasattr(args[0], '__class__') else 0
    for arg in args[start_idx:]:
        key_parts.append(str(arg))
        
    # Adicionar kwargs ordenados
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
        
    # Criar hash se a chave for muito longa
    key_str = ":".join(key_parts)
    if len(key_str) > 200:
        # Usar hash para chaves longas
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{func_name}:{key_hash}"
        
    return key_str


# Funções específicas para cache de leads e conversas
async def cache_lead_data(phone: str, data: Dict[str, Any], ttl: int = 1800):
    """Cache dados do lead por 30 minutos"""
    key = f"lead:{phone}"
    await cache_service.redis.set(key, data, ttl)
    cache_service.memory_cache[key] = (data, datetime.now() + timedelta(seconds=300))
    

async def get_cached_lead_data(phone: str) -> Optional[Dict[str, Any]]:
    """Obtém dados do lead do cache"""
    key = f"lead:{phone}"
    return await cache_service.get_or_compute(
        key=key,
        compute_fn=lambda: None,  # Não computar se não existir
        ttl=1800
    )
    

async def cache_conversation_messages(conversation_id: str, messages: list, ttl: int = 600):
    """Cache mensagens da conversa por 10 minutos"""
    key = f"conversation:{conversation_id}:messages"
    await cache_service.redis.set(key, messages, ttl)
    cache_service.memory_cache[key] = (messages, datetime.now() + timedelta(seconds=300))
    

async def invalidate_lead_cache(phone: str):
    """Invalida cache de um lead específico"""
    await cache_service.invalidate(f"lead:{phone}")
    await cache_service.invalidate_pattern(f"conversation:*{phone}*")