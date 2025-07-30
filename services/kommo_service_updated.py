"""
Kommo CRM Service - Versão Atualizada com Long-Lived Token
==========================================================
Integração simplificada com Kommo CRM
"""

import httpx
import os
from typing import Optional, Dict, Any
from loguru import logger

from config.config import get_config
from services.kommo_auth_simple import KommoAuthSimple


class KommoServiceSimple:
    """Serviço simplificado de integração com Kommo CRM"""
    
    def __init__(self):
        self.config = get_config()
        self.auth = KommoAuthSimple(self.config)
        self.base_url = f"https://{self.config.kommo.subdomain}.kommo.com/api/v4"
        
        # Token direto do ambiente
        self.token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
        
        if self.token:
            logger.info(f"✅ KommoService inicializado com Long-Lived Token")
        else:
            logger.warning("⚠️  Long-Lived Token não encontrado!")
            
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Faz requisição para API do Kommo"""
        try:
            # Usar token diretamente
            if not self.token:
                self.token = await self.auth.get_valid_token()
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=data,
                    params=params
                )
                
                response.raise_for_status()
                return response.json() if response.text else {}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            raise
    
    # Métodos simplificados de exemplo
    
    async def test_connection(self) -> Dict:
        """Testa conexão com Kommo"""
        try:
            response = await self._make_request("GET", "/account")
            logger.info(f"✅ Conectado ao Kommo! Conta: {response.get('name')}")
            return response
        except Exception as e:
            logger.error(f"❌ Falha na conexão: {str(e)}")
            raise
    
    async def create_lead(self, lead_data: Dict) -> Dict:
        """Cria um lead no Kommo"""
        try:
            # Preparar dados do lead
            payload = [{
                "name": lead_data.get("name"),
                "price": lead_data.get("price", 0),
                "pipeline_id": self.config.kommo.pipeline_id,
                "custom_fields_values": [
                    {
                        "field_id": self.config.kommo.custom_fields.get("whatsapp_number"),
                        "values": [{"value": lead_data.get("whatsapp")}]
                    }
                ]
            }]
            
            response = await self._make_request("POST", "/leads", payload)
            
            if "_embedded" in response and "leads" in response["_embedded"]:
                lead = response["_embedded"]["leads"][0]
                logger.info(f"✅ Lead criado: {lead['id']} - {lead_data['name']}")
                return lead
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar lead: {str(e)}")
            raise
    
    async def get_pipelines(self) -> list:
        """Lista todos os pipelines"""
        try:
            response = await self._make_request("GET", "/leads/pipelines")
            pipelines = response.get("_embedded", {}).get("pipelines", [])
            
            for pipeline in pipelines:
                logger.info(f"Pipeline: {pipeline['name']} (ID: {pipeline['id']})")
                
            return pipelines
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar pipelines: {str(e)}")
            return []