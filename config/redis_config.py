"""
Redis Configuration
===================
Configurações centralizadas para o serviço Redis
"""

import os
from typing import Dict, Any

class RedisConfig:
    """Configurações do Redis com valores padrão inteligentes"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Retorna configuração completa do Redis"""
        
        # Detectar ambiente
        environment = os.getenv("ENVIRONMENT", "development")
        
        # Configurações base
        config = {
            # Conexão
            "url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            "prefix": os.getenv("REDIS_PREFIX", "sdr_solarprime"),
            
            # Timeouts e TTL
            "ttl_default": int(os.getenv("REDIS_TTL_SECONDS", "3600")),  # 1 hora
            "ttl_conversation": int(os.getenv("REDIS_TTL_CONVERSATION", "7200")),  # 2 horas
            "ttl_media": int(os.getenv("REDIS_TTL_MEDIA", "3600")),  # 1 hora
            "ttl_lead": int(os.getenv("REDIS_TTL_LEAD", "86400")),  # 24 horas
            
            # Pool de conexões
            "pool_max_connections": int(os.getenv("REDIS_POOL_MAX_CONNECTIONS", "50")),
            "pool_min_connections": int(os.getenv("REDIS_POOL_MIN_CONNECTIONS", "10")),
            
            # Retry e resiliência
            "max_retries": int(os.getenv("REDIS_MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("REDIS_RETRY_DELAY", "1.0")),
            "retry_backoff": float(os.getenv("REDIS_RETRY_BACKOFF", "2.0")),
            
            # Health check
            "health_check_interval": int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30")),
            "health_check_timeout": int(os.getenv("REDIS_HEALTH_CHECK_TIMEOUT", "5")),
            
            # Timeouts de operação
            "socket_timeout": int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
            "socket_connect_timeout": int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5")),
            "socket_keepalive": os.getenv("REDIS_SOCKET_KEEPALIVE", "true").lower() == "true",
            
            # Fallback
            "enable_fallback": os.getenv("REDIS_ENABLE_FALLBACK", "true").lower() == "true",
            "fallback_cleanup_interval": int(os.getenv("REDIS_FALLBACK_CLEANUP_INTERVAL", "300")),
            
            # Monitoramento
            "enable_metrics": os.getenv("REDIS_ENABLE_METRICS", "true").lower() == "true",
            "metrics_interval": int(os.getenv("REDIS_METRICS_INTERVAL", "60")),
        }
        
        # Ajustes por ambiente
        if environment == "production":
            config.update({
                "pool_max_connections": 100,
                "pool_min_connections": 20,
                "health_check_interval": 10,
                "max_retries": 5,
            })
        elif environment == "staging":
            config.update({
                "pool_max_connections": 50,
                "pool_min_connections": 10,
                "health_check_interval": 20,
            })
        
        return config
    
    @staticmethod
    def get_redis_url(
        host: str = None,
        port: int = None,
        password: str = None,
        username: str = "default",
        db: int = 0,
        ssl: bool = False
    ) -> str:
        """Constrói URL do Redis a partir de componentes"""
        
        # Usar valores do ambiente se não fornecidos
        host = host or os.getenv("REDIS_HOST", "localhost")
        port = port or int(os.getenv("REDIS_PORT", "6379"))
        password = password or os.getenv("REDIS_PASSWORD")
        username = username or os.getenv("REDIS_USERNAME", "default")
        db = db if db is not None else int(os.getenv("REDIS_DB", "0"))
        ssl = ssl or os.getenv("REDIS_SSL", "false").lower() == "true"
        
        # Construir URL
        protocol = "rediss" if ssl else "redis"
        
        if password:
            if username and username != "default":
                auth = f"{username}:{password}"
            else:
                auth = f":{password}"
            url = f"{protocol}://{auth}@{host}:{port}/{db}"
        else:
            url = f"{protocol}://{host}:{port}/{db}"
        
        return url
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """Valida configuração do Redis"""
        
        required_fields = ["url", "prefix", "ttl_default"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validar valores numéricos
        numeric_fields = [
            "ttl_default", "pool_max_connections", "max_retries",
            "health_check_interval", "socket_timeout"
        ]
        
        for field in numeric_fields:
            if field in config:
                try:
                    value = int(config[field])
                    if value <= 0:
                        return False
                except:
                    return False
        
        return True
    
    @staticmethod
    def get_cache_key_patterns() -> Dict[str, str]:
        """Retorna padrões de chaves do cache"""
        
        prefix = os.getenv("REDIS_PREFIX", "sdr_solarprime")
        
        return {
            "conversation": f"{prefix}:conversation:*",
            "lead": f"{prefix}:lead:*",
            "media": f"{prefix}:media:*",
            "counter": f"{prefix}:counter:*",
            "session": f"{prefix}:session:*",
            "analytics": f"{prefix}:analytics:*",
            "lock": f"{prefix}:lock:*",
        }
    
    @staticmethod
    def get_example_env() -> str:
        """Retorna exemplo de configuração .env"""
        
        return """
# Redis Configuration
# ===================

# Conexão básica
REDIS_URL=redis://localhost:6379/0
# Ou componentes separados:
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_PASSWORD=
# REDIS_USERNAME=default
# REDIS_DB=0
# REDIS_SSL=false

# Prefixo para chaves
REDIS_PREFIX=sdr_solarprime

# TTL (Time To Live) em segundos
REDIS_TTL_SECONDS=3600          # Padrão: 1 hora
REDIS_TTL_CONVERSATION=7200     # Conversas: 2 horas
REDIS_TTL_MEDIA=3600           # Mídia: 1 hora
REDIS_TTL_LEAD=86400           # Leads: 24 horas

# Pool de conexões
REDIS_POOL_MAX_CONNECTIONS=50
REDIS_POOL_MIN_CONNECTIONS=10

# Retry e resiliência
REDIS_MAX_RETRIES=3
REDIS_RETRY_DELAY=1.0
REDIS_RETRY_BACKOFF=2.0

# Health check
REDIS_HEALTH_CHECK_INTERVAL=30
REDIS_HEALTH_CHECK_TIMEOUT=5

# Timeouts de socket
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_SOCKET_KEEPALIVE=true

# Fallback
REDIS_ENABLE_FALLBACK=true
REDIS_FALLBACK_CLEANUP_INTERVAL=300

# Monitoramento
REDIS_ENABLE_METRICS=true
REDIS_METRICS_INTERVAL=60
"""


# Exportar configuração
redis_config = RedisConfig()