"""
Tool para processamento de documentos usando AGnO Framework
"""
from agno.tools import tool
from loguru import logger
from typing import Optional, Dict, Any, List
import os
from urllib.parse import urlparse

# Formatos de documento suportados
SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.doc', '.docx', '.txt', '.rtf']

@tool(show_result=True, stop_after_tool_call=False)
async def process_document(
    media_url: str,
    document_type: Optional[str] = None,
    extract_specific_data: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Processa documentos (principalmente PDFs de contas de luz) recebidos via WhatsApp.
    
    Args:
        media_url: URL do documento recebido
        document_type: Tipo do documento (ex: "conta_luz", "contrato", "proposta")
        extract_specific_data: Lista de dados específicos para extrair
        
    Returns:
        Dict com informações sobre o processamento do documento
    """
    try:
        logger.info(f"Processando documento: {media_url}")
        
        # Validar URL
        if not media_url or not media_url.startswith(('http://', 'https://')):
            raise ValueError("URL de documento inválida")
        
        # Extrair informações do arquivo
        parsed_url = urlparse(media_url)
        file_path = parsed_url.path
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Validar formato
        if file_extension not in SUPPORTED_DOCUMENT_FORMATS:
            logger.warning(f"Formato de documento não suportado: {file_extension}")
            return {
                "success": False,
                "error": f"Formato {file_extension} não suportado. Formatos aceitos: {', '.join(SUPPORTED_DOCUMENT_FORMATS)}"
            }
        
        # Determinar tipo de documento e dados para extrair
        if not document_type:
            # Tentar inferir pelo nome do arquivo
            file_name_lower = file_name.lower()
            if any(term in file_name_lower for term in ["conta", "fatura", "energia", "luz", "cpfl", "enel", "light"]):
                document_type = "conta_luz"
            elif any(term in file_name_lower for term in ["contrato", "acordo", "termo"]):
                document_type = "contrato"
            elif any(term in file_name_lower for term in ["proposta", "orçamento", "cotação"]):
                document_type = "proposta"
            else:
                document_type = "generic"
        
        # Definir campos para extração baseado no tipo
        extraction_fields = extract_specific_data or []
        analysis_priority = "normal"
        
        if document_type == "conta_luz":
            analysis_priority = "high"
            if not extraction_fields:
                extraction_fields = [
                    "numero_cliente",
                    "nome_titular",
                    "endereco_instalacao",
                    "mes_referencia",
                    "valor_total",
                    "consumo_kwh",
                    "consumo_medio_12_meses",
                    "bandeira_tarifaria",
                    "historico_consumo",
                    "desconto_aplicado",
                    "nome_concessionaria",
                    "tipo_tarifa",
                    "demanda_contratada"
                ]
        elif document_type == "contrato":
            extraction_fields = extraction_fields or [
                "numero_contrato",
                "partes_envolvidas",
                "valor_total",
                "prazo_vigencia",
                "clausulas_importantes"
            ]
        elif document_type == "proposta":
            extraction_fields = extraction_fields or [
                "numero_proposta",
                "valor_investimento",
                "economia_estimada",
                "payback",
                "garantias"
            ]
        
        # Preparar resposta estruturada
        result = {
            "success": True,
            "type": "document",
            "document_type": document_type,
            "format": file_extension.replace('.', ''),
            "file_name": file_name,
            "media_url": media_url,
            "ready_for_gemini": True,
            "extraction_fields": extraction_fields,
            "analysis_priority": analysis_priority,
            "metadata": {
                "supported_format": True,
                "is_pdf": file_extension == '.pdf',
                "processing_notes": f"Documento tipo '{document_type}' pronto para análise"
            }
        }
        
        logger.success(f"Documento processado com sucesso: {file_name} (tipo: {document_type})")
        
        # Instruções especiais para conta de luz
        if document_type == "conta_luz":
            result["special_instructions"] = {
                "ocr_quality": "high",
                "extract_tables": True,
                "identify_patterns": [
                    "Histórico de consumo dos últimos 12 meses",
                    "Composição da tarifa",
                    "Tributos aplicados",
                    "Bandeiras tarifárias"
                ],
                "validation_rules": {
                    "valor_total": "Deve ser numérico e maior que zero",
                    "consumo_kwh": "Deve ser inteiro positivo",
                    "mes_referencia": "Formato MM/AAAA",
                    "historico_consumo": "Array de 12 valores numéricos"
                },
                "data_enrichment": {
                    "calculate_average": True,
                    "identify_peak_months": True,
                    "check_discounts": True,
                    "estimate_solar_savings": True
                }
            }
            
            result["analysis_guidelines"] = [
                "Verificar se já possui desconto de outra empresa solar",
                "Calcular média de consumo anual",
                "Identificar sazonalidade no consumo",
                "Estimar potencial de economia com energia solar",
                "Verificar tipo de tarifa (convencional, branca, etc)"
            ]
        
        # Dicas para processamento de PDF
        if file_extension == '.pdf':
            result["pdf_processing_tips"] = {
                "multi_page": "Processar todas as páginas para histórico completo",
                "ocr_needed": "Alguns PDFs podem ser imagens escaneadas",
                "table_extraction": "Focar em tabelas para dados estruturados",
                "quality_check": "Verificar legibilidade antes de extrair dados"
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar documento: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "type": "document",
            "media_url": media_url
        }

# Exportar a tool
ProcessDocumentTool = process_document