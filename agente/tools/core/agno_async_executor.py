"""
AGnO Framework Async Tools Executor
Wrapper síncrono para resolver RuntimeWarning crítico em agno/models/base.py:467

PROBLEMA: AGnO Framework Issue #2296 + bug interno base.py:467
SOLUÇÃO: Wrapper síncrono que executa async functions internally
STATUS: CAMADA 1 - Correção Crítica RuntimeWarning
"""

import asyncio
import functools
from typing import Any, Callable, Dict, Optional
from loguru import logger

class AGnOAsyncExecutor:
    """
    Wrapper executor para async tools do AGnO Framework
    
    Resolve o bug crítico RuntimeWarning: coroutine 'X' was never awaited
    que persiste mesmo após remoção dos @tool decorators (Issue #2296)
    """
    
    @staticmethod
    def wrap_async_tool(async_func: Callable) -> Callable:
        """
        Cria wrapper síncrono para async function que resolve RuntimeWarning
        
        Args:
            async_func: Função async original
            
        Returns:
            Função síncrona que executa async_func sem RuntimeWarning
        """
        @functools.wraps(async_func)
        def sync_wrapper(*args, **kwargs) -> Any:
            """
            Wrapper síncrono que executa async function corretamente
            Resolve bug AGnO Framework base.py:467
            """
            try:
                # Obter ou criar event loop
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Se loop está rodando, criar nova task
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, async_func(*args, **kwargs))
                            return future.result()
                    else:
                        # Loop não está rodando, usar run_until_complete
                        return loop.run_until_complete(async_func(*args, **kwargs))
                except RuntimeError:
                    # Não há loop ativo, criar novo
                    return asyncio.run(async_func(*args, **kwargs))
                    
            except Exception as e:
                logger.error(f"Erro no AGnOAsyncExecutor para {async_func.__name__}: {e}")
                # Retornar resposta de erro padronizada
                return {
                    "success": False,
                    "error": f"Erro ao executar {async_func.__name__}: {str(e)}",
                    "error_type": "async_execution"
                }
        
        # Preservar metadados da função original
        sync_wrapper.__name__ = async_func.__name__
        sync_wrapper.__doc__ = async_func.__doc__
        sync_wrapper.__annotations__ = async_func.__annotations__
        
        return sync_wrapper
    
    @staticmethod
    def create_sync_tool(async_func: Callable, tool_name: Optional[str] = None) -> Callable:
        """
        Cria tool síncrona com nome personalizado para AGnO Framework
        
        Args:
            async_func: Função async original
            tool_name: Nome da tool (se None, usa nome da função)
            
        Returns:
            Tool síncrona pronta para AGnO Framework
        """
        wrapped_func = AGnOAsyncExecutor.wrap_async_tool(async_func)
        
        if tool_name:
            wrapped_func.__name__ = tool_name
        
        # Log da criação da tool
        logger.info(f"AGnOAsyncExecutor: Tool síncrona criada - {wrapped_func.__name__}")
        
        return wrapped_func


# Decorator convenience para facilitar uso
def agno_sync_tool(tool_name: Optional[str] = None):
    """
    Decorator para converter async function em sync tool para AGnO
    
    Usage:
        @agno_sync_tool("send_msg")  # Nome curto para evitar truncamento
        async def send_text_message(...):
            ...
    """
    def decorator(async_func: Callable) -> Callable:
        return AGnOAsyncExecutor.create_sync_tool(async_func, tool_name)
    
    return decorator


# Export principal
__all__ = ['AGnOAsyncExecutor', 'agno_sync_tool']