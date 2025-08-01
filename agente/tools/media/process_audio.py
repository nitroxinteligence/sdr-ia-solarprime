"""
Tool para processamento de áudio usando AGnO Framework
"""
from agno.tools import tool
from loguru import logger
from typing import Optional, Dict, Any
import os
from urllib.parse import urlparse

# Formatos de áudio suportados
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.opus', '.webm']

@tool(show_result=True)
async def process_audio(
    media_url: str,
    context: Optional[str] = None,
    language: str = "pt-BR"
) -> Dict[str, Any]:
    """
    Processa áudio recebido via WhatsApp e prepara para transcrição pelo Gemini 2.5 Pro.
    
    Args:
        media_url: URL do áudio recebido
        context: Contexto adicional sobre o áudio
        language: Idioma esperado do áudio (padrão: português brasileiro)
        
    Returns:
        Dict com informações sobre o processamento do áudio
    """
    try:
        logger.info(f"Processando áudio: {media_url}")
        
        # Validar URL
        if not media_url or not media_url.startswith(('http://', 'https://')):
            raise ValueError("URL de áudio inválida")
        
        # Extrair informações do arquivo
        parsed_url = urlparse(media_url)
        file_path = parsed_url.path
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Validar formato
        if file_extension not in SUPPORTED_AUDIO_FORMATS:
            logger.warning(f"Formato de áudio não suportado: {file_extension}")
            return {
                "success": False,
                "error": f"Formato {file_extension} não suportado. Formatos aceitos: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
            }
        
        # Determinar contexto do áudio
        audio_context = "general"
        transcription_hints = []
        
        if context:
            context_lower = context.lower()
            if any(term in context_lower for term in ["pergunta", "dúvida", "questão"]):
                audio_context = "question"
                transcription_hints = [
                    "Identificar pergunta principal",
                    "Detectar tom de voz e emoção",
                    "Capturar detalhes específicos mencionados"
                ]
            elif any(term in context_lower for term in ["resposta", "confirmação", "sim", "não"]):
                audio_context = "response"
                transcription_hints = [
                    "Identificar resposta clara",
                    "Detectar hesitação ou certeza",
                    "Capturar informações adicionais fornecidas"
                ]
            elif any(term in context_lower for term in ["endereço", "localização", "rua"]):
                audio_context = "location"
                transcription_hints = [
                    "Capturar endereço completo",
                    "Identificar pontos de referência",
                    "Detectar números e complementos"
                ]
        
        # Preparar resposta estruturada
        result = {
            "success": True,
            "type": "audio",
            "audio_context": audio_context,
            "format": file_extension.replace('.', ''),
            "file_name": file_name,
            "media_url": media_url,
            "ready_for_gemini": True,
            "context": context,
            "language": language,
            "transcription_hints": transcription_hints,
            "metadata": {
                "supported_format": True,
                "expected_language": language,
                "processing_notes": f"Áudio do tipo '{audio_context}' pronto para transcrição"
            }
        }
        
        logger.success(f"Áudio processado com sucesso: {file_name} (contexto: {audio_context})")
        
        # Adicionar instruções especiais baseadas no contexto
        if audio_context == "question":
            result["special_instructions"] = {
                "focus_on": "Entender a pergunta principal e preocupações do cliente",
                "sentiment_analysis": True,
                "extract_keywords": True,
                "response_priority": "high"
            }
        elif audio_context == "location":
            result["special_instructions"] = {
                "focus_on": "Capturar endereço completo e detalhes de localização",
                "normalize_address": True,
                "extract_landmarks": True,
                "validation_required": True
            }
        
        # Alertas sobre qualidade do áudio
        result["quality_notes"] = {
            "whatsapp_compression": "Áudio pode estar comprimido pelo WhatsApp",
            "background_noise": "Possível ruído de fundo em gravações móveis",
            "recommendation": "Usar modelo de transcrição robusto a ruídos"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar áudio: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "type": "audio",
            "media_url": media_url
        }

# Exportar a tool
ProcessAudioTool = process_audio