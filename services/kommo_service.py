"""
Kommo CRM Service (Mock)
========================
Mock do serviço Kommo para testes do sistema V2
"""

from typing import Dict, Any, Optional
from loguru import logger


class KommoService:
    """Mock do serviço Kommo CRM"""
    
    def __init__(self):
        logger.info("Kommo service initialized (mock)")
        
    async def create_lead(self, data: Dict[str, Any]) -> Optional[str]:
        """Mock: criar lead no CRM"""
        logger.info(f"Mock: Would create lead with data: {data}")
        return "mock-lead-123"
        
    async def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
        """Mock: atualizar lead no CRM"""
        logger.info(f"Mock: Would update lead {lead_id} with data: {data}")
        return True
        
    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Mock: buscar lead no CRM"""
        logger.info(f"Mock: Would get lead {lead_id}")
        return {
            "id": lead_id,
            "name": "Mock Lead",
            "status": "new"
        }
        
    async def schedule_meeting(self, lead_id: str, datetime_str: str) -> bool:
        """Mock: agendar reunião"""
        logger.info(f"Mock: Would schedule meeting for lead {lead_id} at {datetime_str}")
        return True


# Instância global
kommo_service = KommoService()