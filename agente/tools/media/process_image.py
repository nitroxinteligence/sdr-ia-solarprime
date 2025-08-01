"""
Tool para processamento de imagens usando AGnO Framework
"""
from agno.tools import tool
from loguru import logger
from typing import Optional, Dict, Any
import os
from urllib.parse import urlparse

# Formatos de imagem suportados
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']

@tool(show_result=True)
async def process_image(
    media_url: str, 
    context: Optional[str] = None,
    extract_text: bool = True
) -> Dict[str, Any]:
    """
    Processa imagem recebida via WhatsApp e prepara para análise pelo Gemini 2.5 Pro.
    
    Args:
        media_url: URL da imagem recebida
        context: Contexto adicional sobre a imagem (ex: "conta de luz", "foto do local")
        extract_text: Se deve tentar extrair texto (OCR) da imagem
        
    Returns:
        Dict com informações sobre o processamento da imagem
    """
    try:
        logger.info(f"Processando imagem: {media_url}")
        
        # Validar URL
        if not media_url or not media_url.startswith(('http://', 'https://')):
            raise ValueError("URL inválida fornecida")
        
        # Extrair informações do arquivo
        parsed_url = urlparse(media_url)
        file_path = parsed_url.path
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Validar formato
        if file_extension not in SUPPORTED_IMAGE_FORMATS:
            logger.warning(f"Formato de imagem não suportado: {file_extension}")
            return {
                "success": False,
                "error": f"Formato {file_extension} não suportado. Formatos aceitos: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
            }
        
        # Determinar tipo de imagem baseado no contexto
        image_type = "generic"
        analysis_hints = []
        
        if context:
            context_lower = context.lower()
            if any(term in context_lower for term in ["conta", "luz", "energia", "fatura"]):
                image_type = "conta_energia"
                analysis_hints = [
                    "Extrair valor da conta",
                    "Identificar empresa/concessionária",
                    "Verificar mês de referência",
                    "Identificar consumo em kWh",
                    "Verificar se já tem desconto"
                ]
            elif any(term in context_lower for term in ["telhado", "casa", "local", "instalação"]):
                image_type = "local_instalacao"
                analysis_hints = [
                    "Avaliar espaço disponível",
                    "Verificar orientação do telhado",
                    "Identificar possíveis obstáculos",
                    "Avaliar condição estrutural"
                ]
            elif any(term in context_lower for term in ["documento", "identidade", "cpf", "rg"]):
                image_type = "documento"
                analysis_hints = [
                    "Extrair informações pessoais com cuidado",
                    "Manter privacidade dos dados",
                    "Validar apenas informações necessárias"
                ]
        
        # Preparar resposta estruturada
        result = {
            "success": True,
            "type": "image",
            "image_type": image_type,
            "format": file_extension.replace('.', ''),
            "file_name": file_name,
            "media_url": media_url,
            "ready_for_gemini": True,
            "context": context,
            "analysis_hints": analysis_hints,
            "metadata": {
                "supported_format": True,
                "extract_text_requested": extract_text,
                "processing_notes": f"Imagem do tipo '{image_type}' pronta para análise multimodal"
            }
        }
        
        logger.success(f"Imagem processada com sucesso: {file_name} (tipo: {image_type})")
        
        # Se for conta de energia, adicionar instruções específicas
        if image_type == "conta_energia":
            result["special_instructions"] = {
                "ocr_focus_areas": [
                    "Valor total a pagar",
                    "Consumo em kWh",
                    "Nome da concessionária",
                    "Período de referência",
                    "Descontos aplicados"
                ],
                "validation_required": True,
                "data_extraction_priority": "high"
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "type": "image",
            "media_url": media_url
        }

# Exportar a tool
ProcessImageTool = process_image