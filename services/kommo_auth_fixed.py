"""
Kommo CRM OAuth2 Authentication Service (Fixed)
===============================================
Versão corrigida sem dependência de Redis síncrono
"""

import httpx
from typing import Optional, Dict
from datetime import datetime, timedelta
import json
from loguru import logger
from config.config import Config
import secrets
import os

# Usar dicionário em memória como fallback
MEMORY_CACHE = {}


class KommoAuthFixed:
    """Gerenciador de autenticação OAuth2 do Kommo (versão corrigida)"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client_id = config.kommo.client_id
        self.client_secret = config.kommo.client_secret
        self.redirect_uri = config.kommo.redirect_uri
        self.subdomain = config.kommo.subdomain
        self.base_url = f"https://{self.subdomain}.kommo.com"
        
        # Usar arquivo local para tokens em desenvolvimento
        self.token_file = ".kommo_tokens.json"
        
        logger.info(f"KommoAuth inicializado para subdomain: {self.subdomain}")
        logger.info(f"Redirect URI: {self.redirect_uri}")
        
    def generate_state(self) -> str:
        """Gera state único para CSRF protection"""
        state = secrets.token_urlsafe(32)
        # Salva state em memória
        MEMORY_CACHE[f"state:{state}"] = {
            "value": "1",
            "expires": datetime.now() + timedelta(minutes=10)
        }
        return state
        
    def verify_state(self, state: str) -> bool:
        """Verifica se state é válido"""
        key = f"state:{state}"
        if key in MEMORY_CACHE:
            data = MEMORY_CACHE[key]
            if datetime.now() < data["expires"]:
                # Remove após uso
                del MEMORY_CACHE[key]
                return True
        return False
        
    def get_auth_url(self, state: Optional[str] = None) -> str:
        """Gera URL de autorização OAuth2"""
        if not state:
            state = self.generate_state()
            
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state
        }
        
        # Construir query string manualmente para evitar problemas de encoding
        query_parts = []
        for k, v in params.items():
            query_parts.append(f"{k}={v}")
        
        query = "&".join(query_parts)
        auth_url = f"{self.base_url}/oauth/authorize?{query}"
        
        logger.info(f"URL de autorização gerada: {auth_url}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """Troca código de autorização por tokens"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri
                }
                
                logger.info(f"Trocando código por token no endpoint: {self.base_url}/oauth/access_token")
                
                response = await client.post(
                    f"{self.base_url}/oauth/access_token",
                    json=data
                )
                
                if response.status_code == 200:
                    tokens = response.json()
                    await self._save_tokens(tokens)
                    logger.info("Tokens obtidos e salvos com sucesso")
                    return tokens
                else:
                    error_msg = f"Erro ao trocar código: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            logger.error("Timeout ao trocar código por token")
            raise Exception("Timeout na autenticação OAuth2")
        except Exception as e:
            logger.error(f"Erro na troca de código: {str(e)}")
            raise
    
    async def refresh_access_token(self) -> Dict:
        """Renova access token usando refresh token"""
        try:
            refresh_token = await self._get_refresh_token()
            
            if not refresh_token:
                raise Exception("Refresh token não encontrado. Faça login novamente.")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                }
                
                logger.info("Renovando access token...")
                
                response = await client.post(
                    f"{self.base_url}/oauth/access_token",
                    json=data
                )
                
                if response.status_code == 200:
                    tokens = response.json()
                    await self._save_tokens(tokens)
                    logger.info("Access token renovado com sucesso")
                    return tokens
                else:
                    error_msg = f"Erro ao renovar token: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    # Se falhar ao renovar, limpa tokens inválidos
                    await self._clear_tokens()
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"Erro ao renovar token: {str(e)}")
            raise
    
    async def get_valid_token(self) -> str:
        """Retorna um access token válido"""
        try:
            token_data = await self._get_tokens()
            
            if not token_data:
                raise Exception("Nenhum token encontrado. Faça autenticação OAuth2 primeiro.")
            
            # Verifica se token está expirado
            expires_at = token_data.get("expires_at", 0)
            current_time = datetime.now().timestamp()
            
            # Renova se faltam menos de 5 minutos para expirar
            if current_time >= expires_at - 300:
                logger.info("Token próximo de expirar, renovando...")
                token_data = await self.refresh_access_token()
            
            return token_data["access_token"]
            
        except Exception as e:
            logger.error(f"Erro ao obter token válido: {str(e)}")
            raise
    
    async def _save_tokens(self, tokens: Dict):
        """Salva tokens em arquivo local"""
        try:
            # Adiciona timestamp de expiração
            tokens["expires_at"] = datetime.now().timestamp() + tokens.get("expires_in", 86400)
            
            # Salva em arquivo
            with open(self.token_file, "w") as f:
                json.dump(tokens, f)
            
            logger.info(f"Tokens salvos em {self.token_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar tokens: {str(e)}")
            raise
        
    async def _get_tokens(self) -> Optional[Dict]:
        """Recupera tokens do arquivo"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, "r") as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar tokens: {str(e)}")
            return None
            
    async def _get_refresh_token(self) -> Optional[str]:
        """Recupera refresh token"""
        token_data = await self._get_tokens()
        return token_data.get("refresh_token") if token_data else None
        
    async def _clear_tokens(self):
        """Limpa tokens"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                logger.info("Tokens removidos")
        except Exception as e:
            logger.error(f"Erro ao limpar tokens: {str(e)}")
            
    async def is_authenticated(self) -> bool:
        """Verifica se está autenticado"""
        try:
            await self.get_valid_token()
            return True
        except:
            return False
            
    async def get_account_info(self) -> Optional[Dict]:
        """Obtém informações da conta autenticada"""
        try:
            token = await self.get_valid_token()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    f"{self.base_url}/api/v4/account",
                    headers=headers,
                    params={"with": "users"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao obter info da conta: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao obter informações da conta: {str(e)}")
            return None