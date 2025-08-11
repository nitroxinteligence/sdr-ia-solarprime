"""
Sistema de Retry Robusto para APIs Externas
Implementa retry com backoff exponencial para lidar com erros temporários
"""
import asyncio
import random
from typing import Any, Callable, Optional, TypeVar, Union
from functools import wraps
from loguru import logger

T = TypeVar('T')

class RetryConfig:
    """Configuração para política de retry"""
    def __init__(
        self,
        max_attempts: int = 5,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calcula o delay para a próxima tentativa com backoff exponencial"""
    delay = min(
        config.initial_delay * (config.exponential_base ** (attempt - 1)),
        config.max_delay
    )
    
    if config.jitter:
        # Adiciona jitter para evitar thundering herd
        delay = delay * (0.5 + random.random())
    
    return delay


def is_retryable_error(error: Exception) -> bool:
    """Determina se o erro é recuperável e deve ser tentado novamente"""
    # Erros HTTP recuperáveis
    retryable_status_codes = {429, 500, 502, 503, 504}
    
    # Verifica se é um erro HTTP com status code
    if hasattr(error, 'status_code'):
        return error.status_code in retryable_status_codes
    
    # Verifica se é um erro de timeout ou rede
    error_message = str(error).lower()
    retryable_patterns = [
        'timeout', 'timed out',
        'connection', 'network',
        'temporarily unavailable',
        'internal error',
        '500', '502', '503', '504',
        'rate limit', 'too many requests'
    ]
    
    return any(pattern in error_message for pattern in retryable_patterns)


def async_retry(config: Optional[RetryConfig] = None):
    """
    Decorador para adicionar retry automático a funções assíncronas
    
    Uso:
        @async_retry()
        async def minha_funcao():
            # código que pode falhar
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    # Tenta executar a função
                    result = await func(*args, **kwargs)
                    
                    # Sucesso - retorna o resultado
                    if attempt > 1:
                        logger.info(
                            f"✅ {func.__name__} succeeded after {attempt} attempts"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Verifica se o erro é recuperável
                    if not is_retryable_error(e):
                        logger.error(
                            f"❌ {func.__name__} failed with non-retryable error: {e}"
                        )
                        raise
                    
                    # Se for a última tentativa, falha definitivamente
                    if attempt >= config.max_attempts:
                        logger.error(
                            f"❌ {func.__name__} failed after {attempt} attempts. "
                            f"Last error: {e}"
                        )
                        raise
                    
                    # Calcula o delay para a próxima tentativa
                    delay = calculate_delay(attempt, config)
                    
                    logger.warning(
                        f"⚠️ {func.__name__} failed (attempt {attempt}/{config.max_attempts}). "
                        f"Retrying in {delay:.1f}s. Error: {e}"
                    )
                    
                    # Aguarda antes de tentar novamente
                    await asyncio.sleep(delay)
            
            # Não deveria chegar aqui, mas por segurança
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError(f"{func.__name__} failed without exception")
        
        return wrapper
    
    return decorator


def sync_retry(config: Optional[RetryConfig] = None):
    """
    Decorador para adicionar retry automático a funções síncronas
    
    Uso:
        @sync_retry()
        def minha_funcao():
            # código que pode falhar
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    # Tenta executar a função
                    result = func(*args, **kwargs)
                    
                    # Sucesso - retorna o resultado
                    if attempt > 1:
                        logger.info(
                            f"✅ {func.__name__} succeeded after {attempt} attempts"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Verifica se o erro é recuperável
                    if not is_retryable_error(e):
                        logger.error(
                            f"❌ {func.__name__} failed with non-retryable error: {e}"
                        )
                        raise
                    
                    # Se for a última tentativa, falha definitivamente
                    if attempt >= config.max_attempts:
                        logger.error(
                            f"❌ {func.__name__} failed after {attempt} attempts. "
                            f"Last error: {e}"
                        )
                        raise
                    
                    # Calcula o delay para a próxima tentativa
                    delay = calculate_delay(attempt, config)
                    
                    logger.warning(
                        f"⚠️ {func.__name__} failed (attempt {attempt}/{config.max_attempts}). "
                        f"Retrying in {delay:.1f}s. Error: {e}"
                    )
                    
                    # Aguarda antes de tentar novamente
                    import time
                    time.sleep(delay)
            
            # Não deveria chegar aqui, mas por segurança
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError(f"{func.__name__} failed without exception")
        
        return wrapper
    
    return decorator


# Configurações pré-definidas para diferentes cenários
GEMINI_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay=2.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True
)

OPENAI_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True
)

API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=0.5,
    max_delay=5.0,
    exponential_base=2.0,
    jitter=True
)