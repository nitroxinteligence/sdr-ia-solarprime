"""
Cliente simplificado para Evolution API v2
Arquitetura modular e sem complexidade desnecessária
"""
import httpx
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from app.config import settings

class SimpleEvolutionClient:
    """Cliente minimalista para Evolution API"""
    
    def __init__(self):
        self.base_url = settings.evolution_api_url.rstrip('/')
        self.instance = settings.evolution_instance_name
        self.api_key = settings.evolution_api_key
        
    async def check_api(self) -> bool:
        """Verifica se a API está acessível"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Evolution API v{data.get('version', '?')} está funcionando!")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Evolution API não está acessível em {self.base_url}: {e}")
            return False
    
    async def check_instance(self) -> Dict[str, Any]:
        """Verifica status da instância"""
        try:
            async with httpx.AsyncClient(
                timeout=10.0,
                headers={"apikey": self.api_key}
            ) as client:
                response = await client.get(
                    f"{self.base_url}/instance/connectionState/{self.instance}"
                )
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def send_text(self, phone: str, text: str) -> Dict[str, Any]:
        """Envia mensagem de texto simples"""
        try:
            # Formatar número (remove caracteres especiais)
            phone = ''.join(filter(str.isdigit, phone))
            if not phone.startswith('55'):
                phone = '55' + phone
                
            payload = {
                "number": phone,
                "text": text
            }
            
            async with httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "apikey": self.api_key,
                    "Content-Type": "application/json"
                }
            ) as client:
                response = await client.post(
                    f"{self.base_url}/message/sendText/{self.instance}",
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Mensagem enviada para {phone}")
                    return response.json()
                else:
                    error_msg = f"Erro {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    return {"error": error_msg}
                    
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return {"error": str(e)}
    
    async def send_typing(self, phone: str, duration: int = 3):
        """Simula digitação"""
        try:
            phone = ''.join(filter(str.isdigit, phone))
            if not phone.startswith('55'):
                phone = '55' + phone
                
            payload = {
                "number": phone,
                "delay": duration * 1000,
                "state": "composing"
            }
            
            async with httpx.AsyncClient(
                timeout=10.0,
                headers={
                    "apikey": self.api_key,
                    "Content-Type": "application/json"
                }
            ) as client:
                await client.post(
                    f"{self.base_url}/chat/updatePresence/{self.instance}",
                    json=payload
                )
                
                # Aguarda duração
                await asyncio.sleep(duration)
                
                # Para digitação
                payload["state"] = "paused"
                await client.post(
                    f"{self.base_url}/chat/updatePresence/{self.instance}",
                    json=payload
                )
                
        except Exception as e:
            # Não propaga erro de digitação
            logger.debug(f"Erro em digitação (não crítico): {e}")

# Cliente global simples
simple_evolution = SimpleEvolutionClient()