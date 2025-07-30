"""
Kommo CRM Simple Authentication
================================
Autenticação simplificada usando Long-Lived Token
"""

import os
from typing import Optional, Dict
from loguru import logger
from config.config import Config


class KommoAuthSimple:
    """Gerenciador simplificado de autenticação do Kommo usando Long-Lived Token"""
    
    def __init__(self, config: Config):
        self.config = config
        self.subdomain = config.kommo.subdomain
        self.base_url = f"https://{self.subdomain}.kommo.com"
        
        # Tentar obter token do ambiente primeiro
        self.long_lived_token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
        
        if self.long_lived_token:
            logger.info(f"✅ KommoAuthSimple inicializado com Long-Lived Token")
        else:
            logger.warning("⚠️  Long-Lived Token não encontrado no .env")
            
    async def get_valid_token(self) -> str:
        """Retorna o Long-Lived Token"""
        if not self.long_lived_token:
            raise Exception(
                "Long-Lived Token não configurado!\n"
                "1. Acesse https://leonardofvieira00.kommo.com/settings/integrations/\n"
                "2. Crie uma integração privada\n"
                "3. Gere um Long-Lived Token\n"
                "4. Adicione KOMMO_LONG_LIVED_TOKEN no .env"
            )
        
        return self.long_lived_token
    
    async def set_token(self, token: str) -> None:
        """Define o Long-Lived Token manualmente"""
        self.long_lived_token = token
        logger.info("✅ Long-Lived Token configurado manualmente")
    
    async def test_token(self) -> bool:
        """Testa se o token é válido"""
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.long_lived_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/account",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Token válido! Conta: {data.get('name', 'N/A')}")
                    return True
                else:
                    logger.error(f"❌ Token inválido! Status: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao testar token: {str(e)}")
            return False
    
    # Métodos de compatibilidade com a interface antiga
    async def refresh_access_token(self) -> Dict:
        """Long-Lived Tokens não precisam ser renovados"""
        logger.info("Long-Lived Token não precisa renovação")
        return {"access_token": self.long_lived_token}
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """Não usado com Long-Lived Token"""
        raise NotImplementedError("Use Long-Lived Token ao invés de OAuth2")