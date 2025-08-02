"""
SendLocationMessageTool - Envia localização via WhatsApp
Versão atualizada para novo Evolution API Service v2
"""

from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from agente.services import get_evolution_service


@tool(show_result=True)
async def send_location_message(
    phone: str,
    latitude: float,
    longitude: float,
    name: Optional[str] = None,
    address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envia localização geográfica via WhatsApp
    
    Args:
        phone: Número de telefone do destinatário (formato: 5511999999999)
        latitude: Latitude da localização (-90 a 90)
        longitude: Longitude da localização (-180 a 180)
        name: Nome do local (opcional, ex: "Escritório SolarPrime")
        address: Endereço completo (opcional - não usado no v2)
    
    Returns:
        Dict com status do envio:
        - success: bool - Se a localização foi enviada com sucesso
        - message_id: str - ID da mensagem no WhatsApp (se sucesso)
        - error: str - Mensagem de erro (se falhou)
        - phone: str - Número formatado usado no envio
        - location: dict - Coordenadas enviadas (lat, lng)
        - has_name: bool - Se incluiu nome do local
    
    Examples:
        >>> await send_location_message("5511999999999", -8.1127, -34.8963)
        {"success": True, "message_id": "3EB0C767D097E9ECFE92", "phone": "5511999999999", "location": {"lat": -8.1127, "lng": -34.8963}, "has_name": False}
        
        >>> await send_location_message("5511999999999", -8.1127, -34.8963, "SolarPrime Boa Viagem", "Av. Conselheiro Aguiar, 3456")
        {"success": True, "message_id": "3EB0C767D097E9ECFE93", "phone": "5511999999999", "location": {"lat": -8.1127, "lng": -34.8963}, "has_name": True}
    """
    try:
        # Log da operação
        logger.info(
            "Enviando localização via WhatsApp",
            phone=phone[:4] + "****",
            latitude=latitude,
            longitude=longitude,
            has_name=bool(name)
        )
        
        # Validação de coordenadas
        if not (-90 <= latitude <= 90):
            logger.error(
                "Latitude inválida",
                latitude=latitude
            )
            return {
                "success": False,
                "error": f"Latitude inválida: {latitude}. Deve estar entre -90 e 90",
                "phone": phone,
                "location": {"lat": latitude, "lng": longitude},
                "has_name": bool(name)
            }
        
        if not (-180 <= longitude <= 180):
            logger.error(
                "Longitude inválida",
                longitude=longitude
            )
            return {
                "success": False,
                "error": f"Longitude inválida: {longitude}. Deve estar entre -180 e 180",
                "phone": phone,
                "location": {"lat": latitude, "lng": longitude},
                "has_name": bool(name)
            }
        
        # Combina nome e endereço se ambos fornecidos
        location_name = name
        if name and address:
            location_name = f"{name} - {address}"
        elif address:
            location_name = address
        
        # Obtém serviço Evolution API v2
        evolution = get_evolution_service()
        
        # Envia localização
        result = await evolution.send_location(
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            name=location_name
        )
        
        if result:
            logger.success(
                "Localização enviada com sucesso",
                phone=phone,
                message_id=result.key.id,
                location={"lat": latitude, "lng": longitude}
            )
            
            return {
                "success": True,
                "message_id": result.key.id,
                "phone": phone,
                "location": {"lat": latitude, "lng": longitude},
                "has_name": bool(name)
            }
        else:
            logger.error(
                "Falha ao enviar localização",
                phone=phone
            )
            
            return {
                "success": False,
                "error": "Falha ao enviar localização - verifique conexão da instância",
                "phone": phone,
                "location": {"lat": latitude, "lng": longitude},
                "has_name": bool(name)
            }
            
    except Exception as e:
        logger.error(
            f"Erro ao enviar localização: {str(e)}",
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro ao enviar localização: {str(e)}",
            "phone": phone,
            "location": {"lat": latitude, "lng": longitude},
            "has_name": bool(name)
        }


# Export da tool
SendLocationMessageTool = send_location_message