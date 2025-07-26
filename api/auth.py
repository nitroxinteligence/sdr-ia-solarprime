"""
Authentication and Authorization
=================================
Módulo de autenticação para endpoints administrativos
"""

from fastapi import HTTPException, Header, status
import os
import logging

logger = logging.getLogger(__name__)


async def verify_admin_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> bool:
    """
    Verifica se a API key fornecida é válida para acesso administrativo
    
    Args:
        x_api_key: API key fornecida no header
        
    Returns:
        True se válida
        
    Raises:
        HTTPException: Se a API key for inválida
    """
    admin_api_key = os.getenv("ADMIN_API_KEY")
    
    if not admin_api_key:
        logger.error("ADMIN_API_KEY não configurada no ambiente")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Autenticação administrativa não configurada"
        )
    
    if x_api_key != admin_api_key:
        logger.warning(f"Tentativa de acesso admin com API key inválida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return True