"""
Unit tests for the process_image tool.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from agente.tools.media.process_image import process_image, ProcessImageTool


class TestProcessImage:
    """Test suite for process_image tool."""
    
    @pytest.mark.asyncio
    async def test_process_image_success_with_valid_url(self):
        """Test successful image processing with a valid URL."""
        result = await process_image(
            media_url="https://example.com/image.jpg",
            context="conta de luz",
            extract_text=True
        )
        
        assert result["success"] is True
        assert result["type"] == "image"
        assert result["image_type"] == "conta_energia"
        assert result["format"] == "jpg"
        assert result["file_name"] == "image.jpg"
        assert result["media_url"] == "https://example.com/image.jpg"
        assert result["ready_for_gemini"] is True
        assert len(result["analysis_hints"]) > 0
        assert "special_instructions" in result
        
    @pytest.mark.asyncio
    async def test_process_image_with_different_contexts(self):
        """Test image processing with different context types."""
        # Test energy bill context
        result = await process_image(
            media_url="https://example.com/conta.pdf.jpg",
            context="fatura de energia"
        )
        assert result["image_type"] == "conta_energia"
        assert "Extrair valor da conta" in result["analysis_hints"]
        
        # Test installation location context
        result = await process_image(
            media_url="https://example.com/telhado.png",
            context="foto do telhado da casa"
        )
        assert result["image_type"] == "local_instalacao"
        assert "Avaliar espaço disponível" in result["analysis_hints"]
        
        # Test document context
        result = await process_image(
            media_url="https://example.com/documento.jpg",
            context="documento de identidade"
        )
        assert result["image_type"] == "documento"
        assert "Extrair informações pessoais com cuidado" in result["analysis_hints"]
        
        # Test generic context
        result = await process_image(
            media_url="https://example.com/other.jpg",
            context="outra coisa"
        )
        assert result["image_type"] == "generic"
        assert len(result["analysis_hints"]) == 0
        
    @pytest.mark.asyncio
    async def test_process_image_with_supported_formats(self):
        """Test processing images with all supported formats."""
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
        
        for fmt in supported_formats:
            result = await process_image(
                media_url=f"https://example.com/test{fmt}"
            )
            assert result["success"] is True
            assert result["format"] == fmt.replace('.', '')
            assert result["metadata"]["supported_format"] is True
            
    @pytest.mark.asyncio
    async def test_process_image_with_unsupported_format(self):
        """Test processing image with unsupported format."""
        result = await process_image(
            media_url="https://example.com/document.pdf"
        )
        
        assert result["success"] is False
        assert "não suportado" in result["error"]
        assert ".pdf" in result["error"]
        
    @pytest.mark.asyncio
    async def test_process_image_with_invalid_url(self):
        """Test processing with invalid URL."""
        # Test with empty URL
        result = await process_image(media_url="")
        assert result["success"] is False
        assert "URL inválida" in result["error"]
        
        # Test with non-HTTP URL
        result = await process_image(media_url="ftp://example.com/image.jpg")
        assert result["success"] is False
        assert "URL inválida" in result["error"]
        
        # Test with None URL
        result = await process_image(media_url=None)
        assert result["success"] is False
        assert "URL inválida" in result["error"]
        
    @pytest.mark.asyncio
    async def test_process_image_without_context(self):
        """Test processing image without context."""
        result = await process_image(
            media_url="https://example.com/random.jpg"
        )
        
        assert result["success"] is True
        assert result["image_type"] == "generic"
        assert result["context"] is None
        assert len(result["analysis_hints"]) == 0
        
    @pytest.mark.asyncio
    async def test_process_image_with_filename_inference(self):
        """Test context inference from filename."""
        # Test energy bill filename
        result = await process_image(
            media_url="https://example.com/conta_luz_janeiro.jpg",
            context=None
        )
        assert result["image_type"] == "conta_energia"
        
        # Test with energy provider name
        result = await process_image(
            media_url="https://example.com/fatura_cpfl.png",
            context=None
        )
        assert result["image_type"] == "conta_energia"
        
    @pytest.mark.asyncio
    async def test_process_image_special_instructions_for_energy_bill(self):
        """Test special instructions are added for energy bills."""
        result = await process_image(
            media_url="https://example.com/conta.jpg",
            context="conta de luz"
        )
        
        assert "special_instructions" in result
        instructions = result["special_instructions"]
        
        assert "ocr_focus_areas" in instructions
        assert "Valor total a pagar" in instructions["ocr_focus_areas"]
        assert "Consumo em kWh" in instructions["ocr_focus_areas"]
        assert instructions["validation_required"] is True
        assert instructions["data_extraction_priority"] == "high"
        
    @pytest.mark.asyncio
    async def test_process_image_metadata_fields(self):
        """Test all metadata fields are present."""
        result = await process_image(
            media_url="https://example.com/test.png",
            context="test",
            extract_text=False
        )
        
        assert result["success"] is True
        metadata = result["metadata"]
        assert metadata["supported_format"] is True
        assert metadata["extract_text_requested"] is False
        assert "processing_notes" in metadata
        
    @pytest.mark.asyncio
    async def test_process_image_with_exception_handling(self):
        """Test exception handling in process_image."""
        # Simulate an exception by mocking urlparse
        with patch('agente.tools.media.process_image.urlparse') as mock_urlparse:
            mock_urlparse.side_effect = Exception("Test exception")
            
            result = await process_image(
                media_url="https://example.com/test.jpg"
            )
            
            assert result["success"] is False
            assert "Test exception" in result["error"]
            assert result["type"] == "image"
            assert result["media_url"] == "https://example.com/test.jpg"
            
    @pytest.mark.asyncio
    async def test_process_image_tool_export(self):
        """Test that ProcessImageTool is properly exported."""
        assert ProcessImageTool is not None
        assert ProcessImageTool == process_image
        
    @pytest.mark.asyncio
    async def test_process_image_with_special_characters_in_url(self):
        """Test processing image with special characters in URL."""
        result = await process_image(
            media_url="https://example.com/image%20with%20spaces.jpg"
        )
        
        assert result["success"] is True
        assert result["file_name"] == "image%20with%20spaces.jpg"
        
    @pytest.mark.asyncio
    async def test_process_image_case_insensitive_context(self):
        """Test that context matching is case insensitive."""
        result = await process_image(
            media_url="https://example.com/test.jpg",
            context="CONTA DE LUZ"
        )
        
        assert result["image_type"] == "conta_energia"
        
    @pytest.mark.asyncio
    async def test_process_image_multiple_context_keywords(self):
        """Test detection when multiple context keywords are present."""
        result = await process_image(
            media_url="https://example.com/test.jpg",
            context="fatura de energia do mês passado"
        )
        
        assert result["image_type"] == "conta_energia"
        assert "fatura" in result["context"].lower()
        assert "energia" in result["context"].lower()