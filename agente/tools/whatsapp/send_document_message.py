"""
SendDocumentMessageTool - Envia documento PDF via WhatsApp usando Evolution API
"""

from typing import Dict, Any, Optional
from agno.tools import tool
from loguru import logger

from ...services import get_evolution_service
from ...core.types import MediaType


@tool(show_result=True)
async def send_document_message(
    phone: str,
    document_url: str,
    caption: Optional[str] = None,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envia documento (PDF, DOC, etc) via WhatsApp.
    
    Args:
        phone: Número de telefone do destinatário (formato: 5511999999999)
        document_url: URL do documento (pdf, doc, docx, xls, xlsx, etc)
        caption: Legenda/descrição opcional para acompanhar o documento
        filename: Nome customizado do arquivo (opcional)
    
    Returns:
        Dict com status do envio:
        - success: bool - Se o documento foi enviado com sucesso
        - message_id: str - ID da mensagem no WhatsApp (se sucesso)
        - error: str - Mensagem de erro (se falhou)
        - phone: str - Número formatado usado no envio
        - media_type: str - Tipo de mídia enviada (sempre "document")
        - has_caption: bool - Se incluiu caption
        - document_type: str - Tipo do documento detectado (pdf, doc, etc)
    
    Examples:
        >>> await send_document_message("5511999999999", "https://example.com/contract.pdf")
        {"success": True, "message_id": "3EB0C767D097E9ECFE90", "phone": "5511999999999", "media_type": "document", "has_caption": False, "document_type": "pdf"}
        
        >>> await send_document_message("5511999999999", "https://example.com/report.pdf", "Relatório mensal", "Relatorio_Janeiro_2024.pdf")
        {"success": True, "message_id": "3EB0C767D097E9ECFE91", "phone": "5511999999999", "media_type": "document", "has_caption": True, "document_type": "pdf"}
    """
    try:
        # Log da operação
        logger.info(
            "Enviando documento via WhatsApp",
            phone=phone,
            document_url=document_url,
            has_caption=bool(caption),
            custom_filename=filename
        )
        
        # Validação básica da URL
        if not document_url or not document_url.startswith(('http://', 'https://')):
            logger.error(
                "URL de documento inválida",
                document_url=document_url
            )
            return {
                "success": False,
                "error": "URL de documento inválida - deve começar com http:// ou https://",
                "phone": phone,
                "media_type": "document",
                "has_caption": bool(caption),
                "document_type": "unknown"
            }
        
        # Detecta tipo de documento
        document_type = "unknown"
        url_lower = document_url.lower()
        
        # Mapeamento de extensões
        doc_extensions = {
            '.pdf': 'pdf',
            '.doc': 'doc',
            '.docx': 'docx',
            '.xls': 'xls',
            '.xlsx': 'xlsx',
            '.ppt': 'ppt',
            '.pptx': 'pptx',
            '.txt': 'txt',
            '.csv': 'csv',
            '.zip': 'zip',
            '.rar': 'rar'
        }
        
        # Detecta extensão
        for ext, doc_type in doc_extensions.items():
            if ext in url_lower:
                document_type = doc_type
                break
        
        # Aviso se não detectou tipo
        if document_type == "unknown":
            logger.warning(
                "Tipo de documento não detectado",
                document_url=document_url
            )
        
        # Obtém serviço Evolution API
        evolution = get_evolution_service()
        
        # Prepara caption com filename se fornecido
        final_caption = caption
        if filename and caption:
            final_caption = f"{filename}\n\n{caption}"
        elif filename:
            final_caption = filename
        
        # Envia documento
        result = await evolution.send_media(
            phone=phone,
            media_url=document_url,
            media_type="document",
            caption=final_caption
        )
        
        if result:
            # Extrai informações relevantes
            message_id = result.get("key", {}).get("id", "")
            
            logger.success(
                "Documento enviado com sucesso",
                phone=phone,
                message_id=message_id,
                document_type=document_type,
                has_caption=bool(caption)
            )
            
            return {
                "success": True,
                "message_id": message_id,
                "phone": phone,
                "media_type": "document",
                "has_caption": bool(caption),
                "document_type": document_type
            }
        else:
            logger.error(
                "Falha ao enviar documento",
                phone=phone
            )
            
            return {
                "success": False,
                "error": "Falha ao enviar documento - resposta vazia da API",
                "phone": phone,
                "media_type": "document",
                "has_caption": bool(caption),
                "document_type": document_type
            }
            
    except Exception as e:
        logger.error(
            f"Erro ao enviar documento: {str(e)}",
            phone=phone,
            error_type=type(e).__name__
        )
        
        return {
            "success": False,
            "error": f"Erro ao enviar documento: {str(e)}",
            "phone": phone,
            "media_type": "document",
            "has_caption": bool(caption),
            "document_type": "unknown"
        }


# Export da tool
SendDocumentMessageTool = send_document_message