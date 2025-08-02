"""
Cliente HTTP base para Evolution API v2
Gerencia conexões e requisições HTTP de forma simples e eficiente
"""

import httpx
from typing import Optional, Dict, Any
from loguru import logger

from agente.core.config import (
    EVOLUTION_API_URL,
    EVOLUTION_API_KEY,
    EVOLUTION_INSTANCE_NAME
)


class EvolutionClient:
    """
    Cliente HTTP simplificado para Evolution API
    
    Características:
    - Sem filas ou processamento assíncrono complexo
    - Sem reconexão automática (responsabilidade do usuário)
    - Timeouts configuráveis
    - Logging estruturado
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        instance: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Inicializa cliente HTTP
        
        Args:
            base_url: URL base da API (usa config se não fornecido)
            api_key: Chave da API (usa config se não fornecido)
            instance: Nome da instância (usa config se não fornecido)
            timeout: Timeout padrão em segundos
        """
        self.base_url = base_url or EVOLUTION_API_URL
        self.instance = instance or EVOLUTION_INSTANCE_NAME
        self.timeout = timeout
        
        # Headers padrão
        self.headers = {
            'apikey': api_key or EVOLUTION_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Cliente HTTP (criado sob demanda)
        self._client: Optional[httpx.AsyncClient] = None
        
        logger.info(
            "Evolution API Client initialized",
            instance=self.instance,
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    async def _ensure_client(self):
        """Garante que o cliente HTTP existe"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers
            )
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Faz uma requisição HTTP
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API (sem base_url)
            data: Dados JSON para enviar
            params: Query parameters
            timeout: Timeout customizado
            
        Returns:
            Resposta da API ou None em caso de erro
        """
        # Garante cliente existe
        await self._ensure_client()
        
        # Monta URL completa
        url = f"{self.base_url}{endpoint}"
        
        # Timeout customizado ou padrão
        request_timeout = timeout or self.timeout
        
        try:
            logger.debug(
                f"Making {method} request",
                endpoint=endpoint,
                has_data=bool(data),
                has_params=bool(params)
            )
            
            # Faz requisição
            response = await self._client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=request_timeout
            )
            
            # Verifica status
            response.raise_for_status()
            
            # Retorna JSON se houver
            if response.text:
                result = response.json()
                logger.debug(f"Request successful", status=response.status_code)
                return result
            else:
                return {}
                
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code}",
                endpoint=endpoint,
                status=e.response.status_code,
                detail=e.response.text[:200] if e.response.text else None
            )
            return None
            
        except httpx.TimeoutException:
            logger.error(
                f"Request timeout",
                endpoint=endpoint,
                timeout=request_timeout
            )
            return None
            
        except Exception as e:
            logger.error(
                f"Unexpected error: {type(e).__name__}",
                endpoint=endpoint,
                error=str(e)
            )
            return None
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Faz requisição GET"""
        return await self.request("GET", endpoint, params=params, timeout=timeout)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Faz requisição POST"""
        return await self.request("POST", endpoint, data=data, timeout=timeout)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Faz requisição PUT"""
        return await self.request("PUT", endpoint, data=data, timeout=timeout)
    
    async def delete(
        self,
        endpoint: str,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Faz requisição DELETE"""
        return await self.request("DELETE", endpoint, timeout=timeout)
    
    async def close(self):
        """Fecha o cliente HTTP"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.debug("HTTP client closed")
    
    async def __aenter__(self):
        """Context manager entrada"""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager saída"""
        await self.close()
    
    # Métodos de conveniência para endpoints comuns
    
    def instance_endpoint(self, path: str) -> str:
        """Monta endpoint com instância"""
        return f"{path}/{self.instance}"
    
    async def check_connection(self) -> bool:
        """
        Verifica se a instância está conectada
        
        Returns:
            True se conectada, False caso contrário
        """
        try:
            response = await self.get(
                self.instance_endpoint("/instance/connectionState")
            )
            
            if response:
                state = response.get("state", "close")
                return state == "open"
            return False
            
        except Exception as e:
            logger.error(f"Error checking connection: {e}")
            return False