"""
Unit tests for the process_document tool.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from agente.tools.media.process_document import process_document, ProcessDocumentTool


class TestProcessDocument:
    """Test suite for process_document tool."""
    
    @pytest.mark.asyncio
    async def test_process_document_success_with_pdf(self):
        """Test successful PDF document processing."""
        result = await process_document(
            media_url="https://example.com/conta_luz.pdf",
            document_type="conta_luz",
            extract_specific_data=["valor_total", "consumo_kwh"]
        )
        
        assert result["success"] is True
        assert result["type"] == "document"
        assert result["document_type"] == "conta_luz"
        assert result["format"] == "pdf"
        assert result["file_name"] == "conta_luz.pdf"
        assert result["media_url"] == "https://example.com/conta_luz.pdf"
        assert result["ready_for_gemini"] is True
        assert "valor_total" in result["extraction_fields"]
        assert "consumo_kwh" in result["extraction_fields"]
        assert result["analysis_priority"] == "high"
        assert result["metadata"]["is_pdf"] is True
        
    @pytest.mark.asyncio
    async def test_process_document_with_supported_formats(self):
        """Test processing documents with all supported formats."""
        supported_formats = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        
        for fmt in supported_formats:
            result = await process_document(
                media_url=f"https://example.com/document{fmt}"
            )
            assert result["success"] is True
            assert result["format"] == fmt.replace('.', '')
            assert result["metadata"]["supported_format"] is True
            assert result["metadata"]["is_pdf"] == (fmt == '.pdf')
            
    @pytest.mark.asyncio
    async def test_process_document_with_unsupported_format(self):
        """Test processing document with unsupported format."""
        result = await process_document(
            media_url="https://example.com/image.jpg"
        )
        
        assert result["success"] is False
        assert "não suportado" in result["error"]
        assert ".jpg" in result["error"]
        
    @pytest.mark.asyncio
    async def test_process_document_type_inference_from_filename(self):
        """Test document type inference from filename."""
        # Test energy bill inference
        test_cases = [
            ("conta_energia.pdf", "conta_luz"),
            ("fatura_cpfl.pdf", "conta_luz"),
            ("luz_janeiro.pdf", "conta_luz"),
            ("contrato_solar.pdf", "contrato"),
            ("acordo_servico.pdf", "contrato"),
            ("proposta_comercial.pdf", "proposta"),
            ("orcamento_solar.pdf", "proposta"),
            ("documento_generico.pdf", "generic")
        ]
        
        for filename, expected_type in test_cases:
            result = await process_document(
                media_url=f"https://example.com/{filename}",
                document_type=None  # Let it infer
            )
            assert result["document_type"] == expected_type, f"Failed for {filename}"
            
    @pytest.mark.asyncio
    async def test_process_document_conta_luz_fields(self):
        """Test that conta_luz documents get proper extraction fields."""
        result = await process_document(
            media_url="https://example.com/conta.pdf",
            document_type="conta_luz"
        )
        
        expected_fields = [
            "numero_cliente", "nome_titular", "endereco_instalacao",
            "mes_referencia", "valor_total", "consumo_kwh",
            "consumo_medio_12_meses", "bandeira_tarifaria",
            "historico_consumo", "desconto_aplicado",
            "nome_concessionaria", "tipo_tarifa", "demanda_contratada"
        ]
        
        for field in expected_fields:
            assert field in result["extraction_fields"]
            
        assert "special_instructions" in result
        instructions = result["special_instructions"]
        assert instructions["ocr_quality"] == "high"
        assert instructions["extract_tables"] is True
        assert "validation_rules" in instructions
        assert "data_enrichment" in instructions
        
    @pytest.mark.asyncio
    async def test_process_document_contrato_fields(self):
        """Test that contrato documents get proper extraction fields."""
        result = await process_document(
            media_url="https://example.com/contrato.pdf",
            document_type="contrato"
        )
        
        expected_fields = [
            "numero_contrato", "partes_envolvidas",
            "valor_total", "prazo_vigencia", "clausulas_importantes"
        ]
        
        for field in expected_fields:
            assert field in result["extraction_fields"]
            
    @pytest.mark.asyncio
    async def test_process_document_proposta_fields(self):
        """Test that proposta documents get proper extraction fields."""
        result = await process_document(
            media_url="https://example.com/proposta.pdf",
            document_type="proposta"
        )
        
        expected_fields = [
            "numero_proposta", "valor_investimento",
            "economia_estimada", "payback", "garantias"
        ]
        
        for field in expected_fields:
            assert field in result["extraction_fields"]
            
    @pytest.mark.asyncio
    async def test_process_document_with_custom_extraction_fields(self):
        """Test providing custom extraction fields."""
        custom_fields = ["custom_field_1", "custom_field_2", "custom_field_3"]
        
        result = await process_document(
            media_url="https://example.com/document.pdf",
            document_type="generic",
            extract_specific_data=custom_fields
        )
        
        assert result["extraction_fields"] == custom_fields
        
    @pytest.mark.asyncio
    async def test_process_document_with_invalid_url(self):
        """Test processing with invalid URL."""
        # Test with empty URL
        result = await process_document(media_url="")
        assert result["success"] is False
        assert "URL de documento inválida" in result["error"]
        
        # Test with non-HTTP URL
        result = await process_document(media_url="ftp://example.com/doc.pdf")
        assert result["success"] is False
        assert "URL de documento inválida" in result["error"]
        
        # Test with None URL
        result = await process_document(media_url=None)
        assert result["success"] is False
        assert "URL de documento inválida" in result["error"]
        
    @pytest.mark.asyncio
    async def test_process_document_conta_luz_special_instructions(self):
        """Test special instructions for conta_luz documents."""
        result = await process_document(
            media_url="https://example.com/conta.pdf",
            document_type="conta_luz"
        )
        
        assert "special_instructions" in result
        instructions = result["special_instructions"]
        
        # Check OCR quality setting
        assert instructions["ocr_quality"] == "high"
        assert instructions["extract_tables"] is True
        
        # Check patterns to identify
        patterns = instructions["identify_patterns"]
        assert "Histórico de consumo dos últimos 12 meses" in patterns
        assert "Composição da tarifa" in patterns
        assert "Tributos aplicados" in patterns
        assert "Bandeiras tarifárias" in patterns
        
        # Check validation rules
        rules = instructions["validation_rules"]
        assert "valor_total" in rules
        assert "consumo_kwh" in rules
        assert "mes_referencia" in rules
        assert "historico_consumo" in rules
        
        # Check data enrichment settings
        enrichment = instructions["data_enrichment"]
        assert enrichment["calculate_average"] is True
        assert enrichment["identify_peak_months"] is True
        assert enrichment["check_discounts"] is True
        assert enrichment["estimate_solar_savings"] is True
        
    @pytest.mark.asyncio
    async def test_process_document_analysis_guidelines(self):
        """Test analysis guidelines for conta_luz documents."""
        result = await process_document(
            media_url="https://example.com/conta.pdf",
            document_type="conta_luz"
        )
        
        assert "analysis_guidelines" in result
        guidelines = result["analysis_guidelines"]
        
        expected_guidelines = [
            "Verificar se já possui desconto de outra empresa solar",
            "Calcular média de consumo anual",
            "Identificar sazonalidade no consumo",
            "Estimar potencial de economia com energia solar",
            "Verificar tipo de tarifa (convencional, branca, etc)"
        ]
        
        for guideline in expected_guidelines:
            assert guideline in guidelines
            
    @pytest.mark.asyncio
    async def test_process_document_pdf_processing_tips(self):
        """Test PDF processing tips are included for PDF files."""
        result = await process_document(
            media_url="https://example.com/document.pdf"
        )
        
        assert "pdf_processing_tips" in result
        tips = result["pdf_processing_tips"]
        
        assert tips["multi_page"] == "Processar todas as páginas para histórico completo"
        assert tips["ocr_needed"] == "Alguns PDFs podem ser imagens escaneadas"
        assert tips["table_extraction"] == "Focar em tabelas para dados estruturados"
        assert tips["quality_check"] == "Verificar legibilidade antes de extrair dados"
        
    @pytest.mark.asyncio
    async def test_process_document_non_pdf_no_tips(self):
        """Test that non-PDF documents don't get PDF tips."""
        result = await process_document(
            media_url="https://example.com/document.docx"
        )
        
        assert "pdf_processing_tips" not in result
        
    @pytest.mark.asyncio
    async def test_process_document_priority_levels(self):
        """Test different priority levels for document types."""
        # Conta luz should have high priority
        result = await process_document(
            media_url="https://example.com/conta.pdf",
            document_type="conta_luz"
        )
        assert result["analysis_priority"] == "high"
        
        # Other documents should have normal priority
        for doc_type in ["contrato", "proposta", "generic"]:
            result = await process_document(
                media_url="https://example.com/doc.pdf",
                document_type=doc_type
            )
            assert result["analysis_priority"] == "normal"
            
    @pytest.mark.asyncio
    async def test_process_document_with_exception_handling(self):
        """Test exception handling in process_document."""
        # Simulate an exception by mocking urlparse
        with patch('agente.tools.media.process_document.urlparse') as mock_urlparse:
            mock_urlparse.side_effect = Exception("Test exception")
            
            result = await process_document(
                media_url="https://example.com/test.pdf"
            )
            
            assert result["success"] is False
            assert "Test exception" in result["error"]
            assert result["type"] == "document"
            assert result["media_url"] == "https://example.com/test.pdf"
            
    @pytest.mark.asyncio
    async def test_process_document_tool_export(self):
        """Test that ProcessDocumentTool is properly exported."""
        assert ProcessDocumentTool is not None
        assert ProcessDocumentTool == process_document
        
    @pytest.mark.asyncio
    async def test_process_document_with_special_characters_in_url(self):
        """Test processing document with special characters in URL."""
        result = await process_document(
            media_url="https://example.com/conta%20de%20luz.pdf"
        )
        
        assert result["success"] is True
        assert result["file_name"] == "conta%20de%20luz.pdf"
        
    @pytest.mark.asyncio
    async def test_process_document_case_insensitive_filename_detection(self):
        """Test that filename detection is case insensitive."""
        result = await process_document(
            media_url="https://example.com/CONTA_LUZ.PDF",
            document_type=None
        )
        
        assert result["document_type"] == "conta_luz"
        
    @pytest.mark.asyncio
    async def test_process_document_multi_page_pdf_considerations(self):
        """Test that multi-page PDF considerations are included."""
        result = await process_document(
            media_url="https://example.com/conta_completa.pdf",
            document_type="conta_luz"
        )
        
        # Should have PDF tips for multi-page processing
        assert "pdf_processing_tips" in result
        assert "multi_page" in result["pdf_processing_tips"]
        
        # Should have extraction fields that may span multiple pages
        assert "historico_consumo" in result["extraction_fields"]
        
    @pytest.mark.asyncio
    async def test_process_document_validation_rules_format(self):
        """Test the format of validation rules for conta_luz."""
        result = await process_document(
            media_url="https://example.com/conta.pdf",
            document_type="conta_luz"
        )
        
        rules = result["special_instructions"]["validation_rules"]
        
        # Check specific validation rules
        assert rules["valor_total"] == "Deve ser numérico e maior que zero"
        assert rules["consumo_kwh"] == "Deve ser inteiro positivo"
        assert rules["mes_referencia"] == "Formato MM/AAAA"
        assert rules["historico_consumo"] == "Array de 12 valores numéricos"
        
    @pytest.mark.asyncio
    async def test_process_document_with_network_timeout_simulation(self):
        """Test handling of network timeout scenarios."""
        # This is a placeholder for actual network timeout testing
        # In real implementation, you might use httpx with timeout settings
        result = await process_document(
            media_url="https://example.com/large_document.pdf",
            document_type="conta_luz"
        )
        
        # Should still return a valid structure even if processing might timeout
        assert "success" in result
        assert "type" in result
        assert "media_url" in result