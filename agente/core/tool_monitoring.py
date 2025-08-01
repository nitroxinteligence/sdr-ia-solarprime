"""
Tool monitoring decorator for Sentry integration.
Automatically tracks tool usage, performance, and errors.
"""

import functools
import time
from typing import Any, Callable, Dict, Optional
from loguru import logger

from agente.core.monitoring import (
    monitor_tool_usage,
    add_breadcrumb,
    capture_agent_error
)


def monitor_tool(tool_name: Optional[str] = None):
    """
    Decorator to monitor tool execution with Sentry.
    
    Args:
        tool_name: Optional tool name override. If not provided,
                  uses the function name.
    
    Usage:
        @monitor_tool("send_whatsapp_message")
        async def send_text_message(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Get tool name from parameter or function name
        name = tool_name or func.__name__
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            """Async wrapper for monitoring."""
            start_time = time.time()
            success = False
            error_msg = None
            
            # Add breadcrumb for tool execution
            add_breadcrumb(
                message=f"Executing tool: {name}",
                category="tool",
                level="info",
                data={
                    "tool_name": name,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            )
            
            try:
                # Execute the tool
                result = await func(*args, **kwargs)
                
                # Check if result indicates success
                if isinstance(result, dict):
                    success = result.get("success", True)
                    error_msg = result.get("error", None)
                else:
                    success = True
                
                return result
                
            except Exception as e:
                # Log and capture error
                logger.error(f"Error in tool {name}: {str(e)}")
                error_msg = str(e)
                
                # Capture to Sentry
                capture_agent_error(
                    e,
                    context={
                        "tool_name": name,
                        "args": str(args)[:200],  # Limit size
                        "kwargs": str(kwargs)[:200]
                    }
                )
                
                # Re-raise the exception
                raise
                
            finally:
                # Calculate execution time
                execution_time = (time.time() - start_time) * 1000  # milliseconds
                
                # Monitor tool usage
                monitor_tool_usage(
                    tool_name=name,
                    success=success,
                    duration_ms=int(execution_time),
                    error=error_msg
                )
                
                # Add completion breadcrumb
                add_breadcrumb(
                    message=f"Tool {name} completed",
                    category="tool",
                    level="info" if success else "error",
                    data={
                        "tool_name": name,
                        "success": success,
                        "duration_ms": execution_time,
                        "error": error_msg
                    }
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            """Sync wrapper for monitoring."""
            start_time = time.time()
            success = False
            error_msg = None
            
            # Add breadcrumb for tool execution
            add_breadcrumb(
                message=f"Executing tool: {name}",
                category="tool",
                level="info",
                data={
                    "tool_name": name,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            )
            
            try:
                # Execute the tool
                result = func(*args, **kwargs)
                
                # Check if result indicates success
                if isinstance(result, dict):
                    success = result.get("success", True)
                    error_msg = result.get("error", None)
                else:
                    success = True
                
                return result
                
            except Exception as e:
                # Log and capture error
                logger.error(f"Error in tool {name}: {str(e)}")
                error_msg = str(e)
                
                # Capture to Sentry
                capture_agent_error(
                    e,
                    context={
                        "tool_name": name,
                        "args": str(args)[:200],  # Limit size
                        "kwargs": str(kwargs)[:200]
                    }
                )
                
                # Re-raise the exception
                raise
                
            finally:
                # Calculate execution time
                execution_time = (time.time() - start_time) * 1000  # milliseconds
                
                # Monitor tool usage
                monitor_tool_usage(
                    tool_name=name,
                    success=success,
                    duration_ms=int(execution_time),
                    error=error_msg
                )
                
                # Add completion breadcrumb
                add_breadcrumb(
                    message=f"Tool {name} completed",
                    category="tool",
                    level="info" if success else "error",
                    data={
                        "tool_name": name,
                        "success": success,
                        "duration_ms": execution_time,
                        "error": error_msg
                    }
                )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# For backward compatibility and convenience
def track_tool_usage(tool_name: Optional[str] = None):
    """Alias for monitor_tool decorator."""
    return monitor_tool(tool_name)


# Import asyncio for checking if function is async
import asyncio