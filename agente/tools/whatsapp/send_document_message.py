"""
SendDocumentMessageTool - Envia documento PDF via WhatsApp
Versão atualizada para novo Evolution API Service v2
"""

from typing import Dict, Any, Optional
from loguru import logger

from agente.services import get_evolution_service
from agente.tools.core.agno_async_executor import AGnOAsyncExecutor


async def _send_document_message_async(
    phone: str,
    document_url: str,
    caption: Optional[str] = None,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envia documento (PDF, DOC, etc) via WhatsApp
    
    Args:
        phone: Número de telefone do destinatário (formato: 5511999999999)
        document_url: URL do documento (pdf, doc, docx, xls, xlsx, etc)
        caption: Legenda/descrição opcional para acompanhar o documento
        filename: Nome customizado do arquivo (opcional - não usado no v2)
    
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
            phone=phone[:4] + "****",
            document_url=document_url,
            has_caption=bool(caption)
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
        
        # Detecta tipo do documento pela extensão
        document_type = "unknown"
        url_lower = document_url.lower()
        if '.pdf' in url_lower:
            document_type = "pdf"
        elif '.doc' in url_lower or '.docx' in url_lower:
            document_type = "doc"
        elif '.xls' in url_lower or '.xlsx' in url_lower:
            document_type = "xls"
        elif '.ppt' in url_lower or '.pptx' in url_lower:
            document_type = "ppt"
        elif '.txt' in url_lower:
            document_type = "txt"
        elif '.csv' in url_lower:
            document_type = "csv"
        
        # Obtém serviço Evolution API v2
        evolution = get_evolution_service()
        
        # Envia documento usando o novo método
        result = await evolution.send_document(
            phone=phone,
            document_url=document_url,
            caption=caption
        )
        
        if result:
            logger.success(
                "Documento enviado com sucesso",
                phone=phone,
                message_id=result.key.id,
                document_type=document_type
            )
            
            return {
                "success": True,
                "message_id": result.key.id,
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
                "error": "Falha ao enviar documento - verifique conexão da instância",
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


# Criar wrapper síncrono para AGnO Framework
send_doc = AGnOAsyncExecutor.wrap_async_tool(_send_document_message_async)
send_doc.__name__ = "send_doc"  # Nome curto para evitar truncamento AGnO

# Export da tool - mantém compatibilidade
SendDocumentMessageTool = send_doc
send_document_message = send_doc  # Alias para compatibilidade