"""
Configuração de logging estruturado com Loguru
"""

import sys
from pathlib import Path
from loguru import logger

from .config import LOG_LEVEL, DEBUG, BASE_DIR


# Remover handler padrão
logger.remove()

# Diretório de logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Formato de log para console
console_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Formato de log para arquivo
file_format = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message}"
)

# Handler para console
logger.add(
    sys.stdout,
    format=console_format,
    level=LOG_LEVEL,
    colorize=True,
    backtrace=DEBUG,
    diagnose=DEBUG
)

# Handler para arquivo de log principal
logger.add(
    LOG_DIR / "agente_{time:YYYY-MM-DD}.log",
    format=file_format,
    level=LOG_LEVEL,
    rotation="1 day",
    retention="30 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
    encoding="utf-8"
)

# Handler para erros
logger.add(
    LOG_DIR / "errors_{time:YYYY-MM-DD}.log",
    format=file_format,
    level="ERROR",
    rotation="1 day",
    retention="60 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
    encoding="utf-8"
)

# Handler específico para webhooks (debug)
if DEBUG:
    logger.add(
        LOG_DIR / "webhooks_{time:YYYY-MM-DD}.log",
        format=file_format,
        level="DEBUG",
        filter=lambda record: "webhook" in record["name"].lower(),
        rotation="1 day",
        retention="7 days",
        encoding="utf-8"
    )

# Handler específico para integrações
logger.add(
    LOG_DIR / "integrations_{time:YYYY-MM-DD}.log",
    format=file_format,
    level="INFO",
    filter=lambda record: any(
        service in record["name"].lower() 
        for service in ["kommo", "calendar", "evolution", "supabase"]
    ),
    rotation="1 day",
    retention="14 days",
    encoding="utf-8"
)


def setup_module_logger(module_name: str) -> logger:
    """
    Cria um logger contextualizado para um módulo específico
    
    Args:
        module_name: Nome do módulo
        
    Returns:
        Logger configurado para o módulo
    """
    return logger.bind(name=module_name)


# Funções auxiliares para logging estruturado
def log_api_request(service: str, endpoint: str, method: str, **kwargs):
    """Log de requisição para API externa"""
    logger.bind(
        service=service,
        endpoint=endpoint,
        method=method,
        **kwargs
    ).info(f"API Request: {method} {service} {endpoint}")


def log_api_response(service: str, endpoint: str, status: int, duration: float, **kwargs):
    """Log de resposta de API externa"""
    logger.bind(
        service=service,
        endpoint=endpoint,
        status=status,
        duration_ms=duration * 1000,
        **kwargs
    ).info(f"API Response: {service} {endpoint} - {status} ({duration:.2f}s)")


def log_webhook_received(event: str, instance: str, phone: str = None, **kwargs):
    """Log de webhook recebido"""
    logger.bind(
        event=event,
        instance=instance,
        phone=phone,
        **kwargs
    ).info(f"Webhook received: {event} from {instance}")


def log_agent_action(action: str, phone: str, success: bool, **kwargs):
    """Log de ação do agente"""
    level = "info" if success else "error"
    logger.bind(
        action=action,
        phone=phone,
        success=success,
        **kwargs
    ).log(level.upper(), f"Agent action: {action} for {phone} - {'Success' if success else 'Failed'}")


# Função para compatibilidade com código existente
def get_logger(name: str = None) -> logger:
    """
    Retorna um logger configurado para o módulo
    
    Args:
        name: Nome do módulo (opcional)
        
    Returns:
        Logger configurado
    """
    if name:
        return setup_module_logger(name)
    return logger


# Exportar logger configurado
__all__ = [
    'logger',
    'get_logger',
    'setup_module_logger',
    'log_api_request',
    'log_api_response', 
    'log_webhook_received',
    'log_agent_action'
]