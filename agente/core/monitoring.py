"""
Monitoring and error tracking integration for SDR Agent.
Integrates Sentry for error tracking, performance monitoring, and custom event tracking.
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from loguru import logger
from typing import Optional, Dict, Any
import traceback

from agente.core.config import (
    SENTRY_DSN,
    SENTRY_TRACES_SAMPLE_RATE,
    SENTRY_PROFILES_SAMPLE_RATE,
    ENVIRONMENT,
    DEBUG
)


def setup_sentry() -> bool:
    """
    Initialize Sentry SDK with custom integrations for the SDR Agent.
    
    Returns:
        bool: True if Sentry was initialized successfully, False otherwise
    """
    if not SENTRY_DSN:
        logger.warning("Sentry DSN not configured, error tracking disabled")
        return False
    
    try:
        # Configure Sentry
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=ENVIRONMENT,
            debug=DEBUG,
            
            # Performance monitoring
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
            
            # Integrations
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint",
                    failed_request_status_codes={500, 503}
                ),
                RedisIntegration(),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=None,  # Capture all levels
                    event_level=None  # Don't create events from logs
                )
            ],
            
            # Event filtering
            before_send=before_send_filter,
            before_send_transaction=before_send_transaction_filter,
            
            # Other options
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send personally identifiable information
            request_bodies="medium",  # Include request bodies for debugging
            
            # Release tracking
            release=f"sdr-agent@2.0.0",
            
            # Custom tags
            tags={
                "agent": "helen-vieira",
                "framework": "agno",
                "company": "solarprime"
            }
        )
        
        logger.info("✅ Sentry initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def before_send_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter events before sending to Sentry.
    Removes sensitive data and adds custom context.
    
    Args:
        event: The event to be sent
        hint: Additional information about the event
        
    Returns:
        The filtered event or None to drop it
    """
    # Remove sensitive data from request
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        
        # List of sensitive fields to redact
        sensitive_fields = [
            "phone", "whatsapp", "telefone", "celular",
            "api_key", "token", "password", "secret",
            "cpf", "rg", "email"
        ]
        
        for field in sensitive_fields:
            if field in data:
                data[field] = "[REDACTED]"
    
    # Add custom context for SDR Agent
    if "contexts" not in event:
        event["contexts"] = {}
    
    # Add agent context
    event["contexts"]["agent"] = {
        "name": "Helen Vieira",
        "type": "SDR",
        "framework": "AGnO",
        "version": "2.0.0"
    }
    
    # Filter out health check errors
    if "transaction" in event and event["transaction"] == "/health":
        return None
    
    return event


def before_send_transaction_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter performance transactions before sending to Sentry.
    
    Args:
        event: The transaction event
        hint: Additional information
        
    Returns:
        The filtered event or None to drop it
    """
    # Skip health check transactions
    if event.get("transaction") in ["/health", "/", "/sessions"]:
        return None
    
    return event


def capture_agent_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: str = "error"
) -> Optional[str]:
    """
    Capture an error with agent-specific context.
    
    Args:
        error: The exception to capture
        context: Additional context about the error
        level: Error level (error, warning, info)
        
    Returns:
        The event ID if captured, None otherwise
    """
    if not SENTRY_DSN:
        return None
    
    try:
        # Add agent context
        with sentry_sdk.push_scope() as scope:
            # Set level
            scope.level = level
            
            # Add context
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            
            # Add error traceback
            scope.set_context("traceback", {
                "traceback": traceback.format_exc()
            })
            
            # Capture the error
            event_id = sentry_sdk.capture_exception(error)
            
            logger.debug(f"Error captured to Sentry: {event_id}")
            return event_id
            
    except Exception as e:
        logger.error(f"Failed to capture error to Sentry: {e}")
        return None


def capture_agent_event(
    message: str,
    category: str,
    data: Optional[Dict[str, Any]] = None,
    level: str = "info"
) -> Optional[str]:
    """
    Capture a custom event for the SDR Agent.
    
    Args:
        message: The event message
        category: Event category (qualification, tool_usage, etc.)
        data: Additional event data
        level: Event level
        
    Returns:
        The event ID if captured, None otherwise
    """
    if not SENTRY_DSN:
        return None
    
    try:
        with sentry_sdk.push_scope() as scope:
            # Set level
            scope.level = level
            
            # Add category tag
            scope.set_tag("event.category", category)
            
            # Add event data
            if data:
                scope.set_context("event_data", data)
            
            # Capture the message
            event_id = sentry_sdk.capture_message(message, level=level)
            
            return event_id
            
    except Exception as e:
        logger.error(f"Failed to capture event to Sentry: {e}")
        return None


def set_user_context(phone: str, name: Optional[str] = None):
    """
    Set user context for Sentry error tracking.
    
    Args:
        phone: User's phone number (will be hashed)
        name: User's name
    """
    if not SENTRY_DSN:
        return
    
    # Hash phone number for privacy
    import hashlib
    user_id = hashlib.sha256(phone.encode()).hexdigest()[:16]
    
    sentry_sdk.set_user({
        "id": user_id,
        "username": name or "Unknown"
    })


def add_breadcrumb(
    message: str,
    category: str,
    level: str = "info",
    data: Optional[Dict[str, Any]] = None
):
    """
    Add a breadcrumb for better error context.
    
    Args:
        message: Breadcrumb message
        category: Category (e.g., "agent", "tool", "qualification")
        level: Breadcrumb level
        data: Additional data
    """
    if not SENTRY_DSN:
        return
    
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


def monitor_qualification_stage(
    phone: str,
    stage: str,
    success: bool,
    duration_ms: Optional[int] = None
):
    """
    Monitor qualification stage transitions.
    
    Args:
        phone: User's phone number
        stage: Qualification stage
        success: Whether the transition was successful
        duration_ms: Duration of the stage in milliseconds
    """
    if not SENTRY_DSN:
        return
    
    try:
        with sentry_sdk.start_transaction(
            op="qualification.stage",
            name=f"Qualification Stage: {stage}"
        ) as transaction:
            transaction.set_tag("stage", stage)
            transaction.set_tag("success", str(success))
            
            if duration_ms:
                transaction.set_data("duration_ms", duration_ms)
            
            # Add breadcrumb
            add_breadcrumb(
                message=f"Qualification stage: {stage}",
                category="qualification",
                level="info" if success else "warning",
                data={
                    "phone": phone[:4] + "****",  # Partial phone for privacy
                    "stage": stage,
                    "success": success
                }
            )
            
    except Exception as e:
        logger.error(f"Failed to monitor qualification stage: {e}")


def monitor_tool_usage(
    tool_name: str,
    success: bool,
    duration_ms: Optional[int] = None,
    error: Optional[str] = None
):
    """
    Monitor tool usage and performance.
    
    Args:
        tool_name: Name of the tool used
        success: Whether the tool executed successfully
        duration_ms: Execution duration in milliseconds
        error: Error message if failed
    """
    if not SENTRY_DSN:
        return
    
    try:
        with sentry_sdk.start_transaction(
            op="tool.execution",
            name=f"Tool: {tool_name}"
        ) as transaction:
            transaction.set_tag("tool", tool_name)
            transaction.set_tag("success", str(success))
            
            if duration_ms:
                transaction.set_data("duration_ms", duration_ms)
            
            if error:
                transaction.set_data("error", error)
            
            # Add breadcrumb
            add_breadcrumb(
                message=f"Tool executed: {tool_name}",
                category="tool",
                level="info" if success else "error",
                data={
                    "tool": tool_name,
                    "success": success,
                    "error": error
                }
            )
            
    except Exception as e:
        logger.error(f"Failed to monitor tool usage: {e}")


class SentryContextManager:
    """
    Context manager for Sentry transactions and error handling.
    """
    
    def __init__(self, operation: str, name: str, **tags):
        self.operation = operation
        self.name = name
        self.tags = tags
        self.transaction = None
    
    def __enter__(self):
        if SENTRY_DSN:
            self.transaction = sentry_sdk.start_transaction(
                op=self.operation,
                name=self.name
            )
            for key, value in self.tags.items():
                self.transaction.set_tag(key, value)
            self.transaction.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            self.transaction.__exit__(exc_type, exc_val, exc_tb)
        
        # Capture exception if occurred
        if exc_val and SENTRY_DSN:
            capture_agent_error(
                exc_val,
                context={
                    "operation": self.operation,
                    "name": self.name,
                    "tags": self.tags
                }
            )
        
        return False  # Don't suppress exceptions