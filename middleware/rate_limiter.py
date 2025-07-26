"""
Rate Limiter Middleware
=======================
Middleware de rate limiting para proteção contra abuso
"""

import os
import time
import hashlib
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import asyncio
from collections import defaultdict
import ipaddress

from services.redis_enhanced import redis_enhanced


class RateLimiter:
    """Rate limiter com suporte a Redis e fallback em memória"""
    
    def __init__(self):
        self.redis = redis_enhanced
        self.memory_store = defaultdict(list)
        self._cleanup_task = None
        
        # Configurações
        self.default_limit = int(os.getenv("RATE_LIMIT_DEFAULT", "60"))
        self.default_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # segundos
        self.burst_limit = int(os.getenv("RATE_LIMIT_BURST", "10"))
        self.burst_window = int(os.getenv("RATE_LIMIT_BURST_WINDOW", "10"))
        
        # Limites por endpoint
        self.endpoint_limits = {
            "/webhook/whatsapp": {
                "limit": int(os.getenv("RATE_LIMIT_WEBHOOK", "300")),
                "window": 60,
                "burst_limit": 50,
                "burst_window": 10
            },
            "/api/send_message": {
                "limit": int(os.getenv("RATE_LIMIT_SEND_MESSAGE", "30")),
                "window": 60,
                "burst_limit": 5,
                "burst_window": 10
            },
            "/api/": {  # Todos os endpoints da API
                "limit": int(os.getenv("RATE_LIMIT_API", "120")),
                "window": 60,
                "burst_limit": 20,
                "burst_window": 10
            }
        }
        
        # IPs permitidos (whitelist)
        self.whitelisted_ips = set(
            os.getenv("RATE_LIMIT_WHITELIST_IPS", "").split(",")
        )
        
        # IPs bloqueados
        self.blacklisted_ips = set()
        
        # Configuração de bloqueio automático
        self.auto_block_threshold = int(os.getenv("RATE_LIMIT_AUTO_BLOCK_THRESHOLD", "5"))
        self.auto_block_duration = int(os.getenv("RATE_LIMIT_AUTO_BLOCK_DURATION", "3600"))
    
    async def start_cleanup_task(self):
        """Inicia task de limpeza de dados antigos"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Loop de limpeza de dados expirados"""
        while True:
            await asyncio.sleep(300)  # A cada 5 minutos
            await self._cleanup_memory_store()
    
    async def _cleanup_memory_store(self):
        """Limpa dados antigos do armazenamento em memória"""
        try:
            current_time = time.time()
            
            for key in list(self.memory_store.keys()):
                # Filtrar apenas timestamps recentes
                self.memory_store[key] = [
                    timestamp for timestamp in self.memory_store[key]
                    if current_time - timestamp < 3600  # Manter última hora
                ]
                
                # Remover chave se vazia
                if not self.memory_store[key]:
                    del self.memory_store[key]
                    
        except Exception as e:
            logger.error(f"Erro na limpeza do rate limiter: {e}")
    
    def _get_identifier(self, request: Request) -> str:
        """Obtém identificador único para o cliente"""
        # Prioridade: API Key > User ID > IP
        
        # Verificar API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Verificar token de autenticação
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token_hash = hashlib.md5(auth_header.encode()).hexdigest()[:8]
            return f"token:{token_hash}"
        
        # Usar IP
        client_ip = request.client.host
        return f"ip:{client_ip}"
    
    def _get_endpoint_config(self, path: str) -> Dict[str, int]:
        """Obtém configuração de rate limit para o endpoint"""
        # Verificar correspondência exata
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]
        
        # Verificar prefixos
        for endpoint, config in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return config
        
        # Retornar configuração padrão
        return {
            "limit": self.default_limit,
            "window": self.default_window,
            "burst_limit": self.burst_limit,
            "burst_window": self.burst_window
        }
    
    async def _check_redis_limit(
        self,
        identifier: str,
        limit: int,
        window: int
    ) -> tuple[bool, int, int]:
        """Verifica limite usando Redis"""
        try:
            key = f"rate_limit:{identifier}:{int(time.time() // window)}"
            
            # Incrementar contador
            current = await self.redis.increment_counter(key)
            
            # Definir expiração na primeira requisição
            if current == 1:
                await self.redis.client.expire(
                    self.redis._make_key(f"counter:{key}"),
                    window
                )
            
            remaining = max(0, limit - current)
            reset_time = int(time.time() // window + 1) * window
            
            return current <= limit, remaining, reset_time
            
        except Exception as e:
            logger.debug(f"Falha ao usar Redis para rate limiting: {e}")
            return None, None, None
    
    def _check_memory_limit(
        self,
        identifier: str,
        limit: int,
        window: int
    ) -> tuple[bool, int, int]:
        """Verifica limite usando memória"""
        current_time = time.time()
        window_start = current_time - window
        
        # Filtrar requisições dentro da janela
        self.memory_store[identifier] = [
            timestamp for timestamp in self.memory_store[identifier]
            if timestamp > window_start
        ]
        
        # Contar requisições
        current_count = len(self.memory_store[identifier])
        
        # Adicionar timestamp atual
        self.memory_store[identifier].append(current_time)
        
        remaining = max(0, limit - current_count - 1)
        reset_time = int(current_time + window)
        
        return current_count < limit, remaining, reset_time
    
    async def check_rate_limit(self, request: Request) -> tuple[bool, Dict[str, Any]]:
        """Verifica se a requisição está dentro do limite"""
        # Obter IP do cliente
        client_ip = request.client.host
        
        # Verificar blacklist
        if client_ip in self.blacklisted_ips:
            return False, {
                "reason": "IP blocked",
                "retry_after": self.auto_block_duration
            }
        
        # Verificar whitelist
        if client_ip in self.whitelisted_ips:
            return True, {}
        
        # Obter identificador e configuração
        identifier = self._get_identifier(request)
        config = self._get_endpoint_config(request.url.path)
        
        # Verificar burst limit primeiro
        burst_allowed, burst_remaining, burst_reset = await self._check_limit(
            f"{identifier}:burst",
            config["burst_limit"],
            config["burst_window"]
        )
        
        if not burst_allowed:
            return False, {
                "reason": "Burst limit exceeded",
                "limit": config["burst_limit"],
                "window": config["burst_window"],
                "remaining": burst_remaining,
                "reset": burst_reset,
                "retry_after": burst_reset - int(time.time())
            }
        
        # Verificar limite normal
        allowed, remaining, reset_time = await self._check_limit(
            identifier,
            config["limit"],
            config["window"]
        )
        
        if not allowed:
            # Incrementar contador de violações
            await self._increment_violation_counter(client_ip)
            
            return False, {
                "reason": "Rate limit exceeded",
                "limit": config["limit"],
                "window": config["window"],
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": reset_time - int(time.time())
            }
        
        return True, {
            "limit": config["limit"],
            "remaining": remaining,
            "reset": reset_time
        }
    
    async def _check_limit(
        self,
        identifier: str,
        limit: int,
        window: int
    ) -> tuple[bool, int, int]:
        """Verifica limite com fallback automático"""
        # Tentar Redis primeiro
        if self.redis.is_connected:
            result = await self._check_redis_limit(identifier, limit, window)
            if result[0] is not None:
                return result
        
        # Fallback para memória
        return self._check_memory_limit(identifier, limit, window)
    
    async def _increment_violation_counter(self, ip: str):
        """Incrementa contador de violações e bloqueia se necessário"""
        key = f"violations:{ip}"
        
        try:
            # Incrementar no Redis
            if self.redis.is_connected:
                violations = await self.redis.increment_counter(key)
                
                # Definir expiração
                if violations == 1:
                    await self.redis.client.expire(
                        self.redis._make_key(f"counter:{key}"),
                        3600  # 1 hora
                    )
            else:
                # Fallback em memória
                violations = self.memory_store[key][-1] if key in self.memory_store else 0
                violations += 1
                self.memory_store[key] = [violations]
            
            # Bloquear automaticamente se exceder threshold
            if violations >= self.auto_block_threshold:
                self.blacklisted_ips.add(ip)
                logger.warning(f"IP {ip} bloqueado automaticamente após {violations} violações")
                
                # Agendar desbloqueio
                asyncio.create_task(self._schedule_unblock(ip))
                
        except Exception as e:
            logger.error(f"Erro ao incrementar contador de violações: {e}")
    
    async def _schedule_unblock(self, ip: str):
        """Agenda desbloqueio de IP"""
        await asyncio.sleep(self.auto_block_duration)
        
        if ip in self.blacklisted_ips:
            self.blacklisted_ips.remove(ip)
            logger.info(f"IP {ip} desbloqueado automaticamente")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Middleware FastAPI para rate limiting"""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        
        # Endpoints excluídos
        self.excluded_paths = {
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Pular verificação para endpoints excluídos
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Verificar rate limit
        allowed, info = await self.rate_limiter.check_rate_limit(request)
        
        if not allowed:
            # Retornar erro 429
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": info.get("reason", "Rate limit exceeded"),
                    "retry_after": info.get("retry_after", 60)
                },
                headers={
                    "X-RateLimit-Limit": str(info.get("limit", "")),
                    "X-RateLimit-Remaining": str(info.get("remaining", 0)),
                    "X-RateLimit-Reset": str(info.get("reset", "")),
                    "Retry-After": str(info.get("retry_after", 60))
                }
            )
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", ""))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", ""))
        response.headers["X-RateLimit-Reset"] = str(info.get("reset", ""))
        
        return response


# Função helper para criar e configurar o rate limiter
async def setup_rate_limiter(app):
    """Configura rate limiter na aplicação"""
    rate_limiter = RateLimiter()
    
    # Iniciar task de limpeza
    await rate_limiter.start_cleanup_task()
    
    # Adicionar middleware
    app.add_middleware(RateLimiterMiddleware, rate_limiter=rate_limiter)
    
    logger.info("✅ Rate limiter configurado com sucesso")
    
    return rate_limiter