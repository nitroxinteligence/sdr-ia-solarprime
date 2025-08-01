"""
Unit tests for the process_audio tool.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from agente.tools.media.process_audio import process_audio, ProcessAudioTool


class TestProcessAudio:
    """Test suite for process_audio tool."""
    
    @pytest.mark.asyncio
    async def test_process_audio_success_with_valid_url(self):
        """Test successful audio processing with a valid URL."""
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="pergunta sobre energia solar",
            language="pt-BR"
        )
        
        assert result["success"] is True
        assert result["type"] == "audio"
        assert result["audio_context"] == "question"
        assert result["format"] == "mp3"
        assert result["file_name"] == "audio.mp3"
        assert result["media_url"] == "https://example.com/audio.mp3"
        assert result["ready_for_gemini"] is True
        assert result["language"] == "pt-BR"
        assert len(result["transcription_hints"]) > 0
        assert "special_instructions" in result
        
    @pytest.mark.asyncio
    async def test_process_audio_with_different_contexts(self):
        """Test audio processing with different context types."""
        # Test question context
        result = await process_audio(
            media_url="https://example.com/audio.opus",
            context="tenho uma dúvida sobre o sistema"
        )
        assert result["audio_context"] == "question"
        assert "Identificar pergunta principal" in result["transcription_hints"]
        assert result["special_instructions"]["focus_on"] == "Entender a pergunta principal e preocupações do cliente"
        assert result["special_instructions"]["sentiment_analysis"] is True
        
        # Test response context
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="sim, confirmo o endereço"
        )
        assert result["audio_context"] == "response"
        assert "Identificar resposta clara" in result["transcription_hints"]
        
        # Test location context
        result = await process_audio(
            media_url="https://example.com/audio.wav",
            context="meu endereço é rua das flores"
        )
        assert result["audio_context"] == "location"
        assert "Capturar endereço completo" in result["transcription_hints"]
        assert result["special_instructions"]["normalize_address"] is True
        
        # Test generic context
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="informação geral"
        )
        assert result["audio_context"] == "general"
        assert len(result["transcription_hints"]) == 0
        
    @pytest.mark.asyncio
    async def test_process_audio_with_supported_formats(self):
        """Test processing audio with all supported formats."""
        supported_formats = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.opus', '.webm']
        
        for fmt in supported_formats:
            result = await process_audio(
                media_url=f"https://example.com/audio{fmt}"
            )
            assert result["success"] is True
            assert result["format"] == fmt.replace('.', '')
            assert result["metadata"]["supported_format"] is True
            
    @pytest.mark.asyncio
    async def test_process_audio_with_unsupported_format(self):
        """Test processing audio with unsupported format."""
        result = await process_audio(
            media_url="https://example.com/audio.flac"
        )
        
        assert result["success"] is False
        assert "não suportado" in result["error"]
        assert ".flac" in result["error"]
        
    @pytest.mark.asyncio
    async def test_process_audio_with_invalid_url(self):
        """Test processing with invalid URL."""
        # Test with empty URL
        result = await process_audio(media_url="")
        assert result["success"] is False
        assert "URL de áudio inválida" in result["error"]
        
        # Test with non-HTTP URL
        result = await process_audio(media_url="ftp://example.com/audio.mp3")
        assert result["success"] is False
        assert "URL de áudio inválida" in result["error"]
        
        # Test with None URL
        result = await process_audio(media_url=None)
        assert result["success"] is False
        assert "URL de áudio inválida" in result["error"]
        
    @pytest.mark.asyncio
    async def test_process_audio_without_context(self):
        """Test processing audio without context."""
        result = await process_audio(
            media_url="https://example.com/audio.mp3"
        )
        
        assert result["success"] is True
        assert result["audio_context"] == "general"
        assert result["context"] is None
        assert len(result["transcription_hints"]) == 0
        
    @pytest.mark.asyncio
    async def test_process_audio_language_parameter(self):
        """Test language parameter handling."""
        # Test with default language
        result = await process_audio(
            media_url="https://example.com/audio.mp3"
        )
        assert result["language"] == "pt-BR"
        assert result["metadata"]["expected_language"] == "pt-BR"
        
        # Test with custom language
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            language="en-US"
        )
        assert result["language"] == "en-US"
        assert result["metadata"]["expected_language"] == "en-US"
        
    @pytest.mark.asyncio
    async def test_process_audio_special_instructions_for_question(self):
        """Test special instructions are added for question context."""
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="qual é o preço da instalação?"
        )
        
        assert "special_instructions" in result
        instructions = result["special_instructions"]
        
        assert instructions["focus_on"] == "Entender a pergunta principal e preocupações do cliente"
        assert instructions["sentiment_analysis"] is True
        assert instructions["extract_keywords"] is True
        assert instructions["response_priority"] == "high"
        
    @pytest.mark.asyncio
    async def test_process_audio_special_instructions_for_location(self):
        """Test special instructions are added for location context."""
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="o endereço é avenida principal número 123"
        )
        
        assert "special_instructions" in result
        instructions = result["special_instructions"]
        
        assert instructions["focus_on"] == "Capturar endereço completo e detalhes de localização"
        assert instructions["normalize_address"] is True
        assert instructions["extract_landmarks"] is True
        assert instructions["validation_required"] is True
        
    @pytest.mark.asyncio
    async def test_process_audio_quality_notes(self):
        """Test quality notes are included."""
        result = await process_audio(
            media_url="https://example.com/audio.opus"
        )
        
        assert "quality_notes" in result
        notes = result["quality_notes"]
        
        assert notes["whatsapp_compression"] == "Áudio pode estar comprimido pelo WhatsApp"
        assert notes["background_noise"] == "Possível ruído de fundo em gravações móveis"
        assert notes["recommendation"] == "Usar modelo de transcrição robusto a ruídos"
        
    @pytest.mark.asyncio
    async def test_process_audio_metadata_fields(self):
        """Test all metadata fields are present."""
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="test",
            language="es-ES"
        )
        
        assert result["success"] is True
        metadata = result["metadata"]
        assert metadata["supported_format"] is True
        assert metadata["expected_language"] == "es-ES"
        assert "processing_notes" in metadata
        
    @pytest.mark.asyncio
    async def test_process_audio_with_exception_handling(self):
        """Test exception handling in process_audio."""
        # Simulate an exception by mocking urlparse
        with patch('agente.tools.media.process_audio.urlparse') as mock_urlparse:
            mock_urlparse.side_effect = Exception("Test exception")
            
            result = await process_audio(
                media_url="https://example.com/test.mp3"
            )
            
            assert result["success"] is False
            assert "Test exception" in result["error"]
            assert result["type"] == "audio"
            assert result["media_url"] == "https://example.com/test.mp3"
            
    @pytest.mark.asyncio
    async def test_process_audio_tool_export(self):
        """Test that ProcessAudioTool is properly exported."""
        assert ProcessAudioTool is not None
        assert ProcessAudioTool == process_audio
        
    @pytest.mark.asyncio
    async def test_process_audio_with_special_characters_in_url(self):
        """Test processing audio with special characters in URL."""
        result = await process_audio(
            media_url="https://example.com/audio%20file.mp3"
        )
        
        assert result["success"] is True
        assert result["file_name"] == "audio%20file.mp3"
        
    @pytest.mark.asyncio
    async def test_process_audio_case_insensitive_context(self):
        """Test that context matching is case insensitive."""
        result = await process_audio(
            media_url="https://example.com/test.mp3",
            context="PERGUNTA SOBRE O SISTEMA"
        )
        
        assert result["audio_context"] == "question"
        
    @pytest.mark.asyncio
    async def test_process_audio_multiple_context_keywords(self):
        """Test detection when multiple context keywords are present."""
        result = await process_audio(
            media_url="https://example.com/test.mp3",
            context="tenho uma questão e dúvida sobre o sistema"
        )
        
        assert result["audio_context"] == "question"
        assert len(result["transcription_hints"]) > 0
        
    @pytest.mark.asyncio
    async def test_process_audio_whatsapp_specific_formats(self):
        """Test WhatsApp-specific audio formats like opus."""
        # Opus is commonly used by WhatsApp
        result = await process_audio(
            media_url="https://example.com/PTT-20240115-WA0001.opus"
        )
        
        assert result["success"] is True
        assert result["format"] == "opus"
        assert result["ready_for_gemini"] is True
        
    @pytest.mark.asyncio
    async def test_process_audio_transcription_hints_content(self):
        """Test specific transcription hints for different contexts."""
        # Question context
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="pergunta"
        )
        hints = result["transcription_hints"]
        assert "Identificar pergunta principal" in hints
        assert "Detectar tom de voz e emoção" in hints
        assert "Capturar detalhes específicos mencionados" in hints
        
        # Response context
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="resposta"
        )
        hints = result["transcription_hints"]
        assert "Identificar resposta clara" in hints
        assert "Detectar hesitação ou certeza" in hints
        assert "Capturar informações adicionais fornecidas" in hints
        
        # Location context
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="endereço"
        )
        hints = result["transcription_hints"]
        assert "Capturar endereço completo" in hints
        assert "Identificar pontos de referência" in hints
        assert "Detectar números e complementos" in hints
        
    @pytest.mark.asyncio
    async def test_process_audio_with_webm_format(self):
        """Test processing WebM audio format (common in web browsers)."""
        result = await process_audio(
            media_url="https://example.com/voice_recording.webm"
        )
        
        assert result["success"] is True
        assert result["format"] == "webm"
        assert result["ready_for_gemini"] is True
        
    @pytest.mark.asyncio
    async def test_process_audio_processing_notes(self):
        """Test processing notes content for different contexts."""
        # General context
        result = await process_audio(
            media_url="https://example.com/audio.mp3"
        )
        assert "Áudio do tipo 'general' pronto para transcrição" in result["metadata"]["processing_notes"]
        
        # Question context
        result = await process_audio(
            media_url="https://example.com/audio.mp3",
            context="pergunta"
        )
        assert "Áudio do tipo 'question' pronto para transcrição" in result["metadata"]["processing_notes"]
        
    @pytest.mark.asyncio
    async def test_process_audio_with_corrupted_file_simulation(self):
        """Test handling of potentially corrupted audio files."""
        # This simulates the tool's response to a corrupted file
        # In real implementation, the AI service would handle this
        result = await process_audio(
            media_url="https://example.com/corrupted.mp3"
        )
        
        # The tool should still process the metadata even if the file might be corrupted
        assert "success" in result
        assert "type" in result
        assert "media_url" in result
        assert result["ready_for_gemini"] is True  # Let Gemini handle the actual validation
        
    @pytest.mark.asyncio
    async def test_process_audio_with_very_long_filename(self):
        """Test processing audio with very long filename."""
        long_filename = "audio_message_from_whatsapp_user_12345678901234567890_timestamp_20240115_120000.opus"
        result = await process_audio(
            media_url=f"https://example.com/{long_filename}"
        )
        
        assert result["success"] is True
        assert result["file_name"] == long_filename