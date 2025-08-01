"""
Unit tests for message_chunking tool
"""

import pytest
from unittest.mock import patch
from agente.tools.whatsapp.message_chunking import chunk_message


@pytest.mark.asyncio
async def test_chunk_message_short_text():
    """Test chunking with text shorter than max_chars"""
    # Arrange
    text = "This is a short message."
    max_chars = 100
    
    # Act
    result = await chunk_message(text, max_chars=max_chars)
    
    # Assert
    assert result["success"] is True
    assert result["total_chunks"] == 1
    assert result["chunks"][0]["text"] == text
    assert result["chunks"][0]["words"] == 5
    assert result["chunks"][0]["chars"] == len(text)
    assert 900 <= result["chunks"][0]["delay_ms"] <= 1100  # Around min_delay with variation


@pytest.mark.asyncio
async def test_chunk_message_long_text_with_sentences():
    """Test chunking long text respecting sentence boundaries"""
    # Arrange
    text = ("This is the first sentence. " * 20 + 
            "This is the second part. " * 20 + 
            "And this is the final part.")
    max_chars = 200
    
    # Act
    result = await chunk_message(text, max_chars=max_chars, prefer_sentences=True)
    
    # Assert
    assert result["success"] is True
    assert result["total_chunks"] > 1
    assert result["total_chars"] == len(text.strip())
    
    # Check that chunks end with sentence endings when possible
    for i, chunk in enumerate(result["chunks"][:-1]):  # All but last chunk
        chunk_text = chunk["text"]
        # Should end with sentence punctuation or be at word boundary
        assert (chunk_text.endswith('.') or 
                chunk_text.endswith('!') or 
                chunk_text.endswith('?') or
                not chunk_text[-1].isalnum())


@pytest.mark.asyncio
async def test_chunk_message_without_sentence_preference():
    """Test chunking without preferring sentence boundaries"""
    # Arrange
    text = "This is a very long sentence without any punctuation " * 10
    max_chars = 50
    
    # Act
    result = await chunk_message(text, max_chars=max_chars, prefer_sentences=False)
    
    # Assert
    assert result["success"] is True
    assert result["total_chunks"] > 1
    
    # Check chunk sizes are close to max_chars
    for chunk in result["chunks"]:
        assert chunk["chars"] <= max_chars


@pytest.mark.asyncio
async def test_chunk_message_custom_delays():
    """Test chunking with custom delay settings"""
    # Arrange
    text = "Short chunk. " * 10
    max_chars = 50
    min_delay = 2000
    max_delay = 5000
    
    # Act
    result = await chunk_message(
        text, 
        max_chars=max_chars,
        min_delay_ms=min_delay,
        max_delay_ms=max_delay
    )
    
    # Assert
    assert result["success"] is True
    
    # Check delays are within custom range
    for chunk in result["chunks"]:
        # Account for ±10% variation
        assert min_delay * 0.9 <= chunk["delay_ms"] <= max_delay * 1.1


@pytest.mark.asyncio
async def test_chunk_message_empty_text():
    """Test chunking with empty text"""
    # Arrange
    text = ""
    
    # Act
    result = await chunk_message(text)
    
    # Assert
    assert result["success"] is False
    assert "Texto vazio" in result["error"]
    assert result["total_chunks"] == 0
    assert result["chunks"] == []


@pytest.mark.asyncio
async def test_chunk_message_whitespace_only():
    """Test chunking with whitespace-only text"""
    # Arrange
    text = "   \n\n\t   "
    
    # Act
    result = await chunk_message(text)
    
    # Assert
    assert result["success"] is False
    assert "Texto vazio" in result["error"]


@pytest.mark.asyncio
async def test_chunk_message_small_max_chars():
    """Test chunking with very small max_chars (should be adjusted to minimum)"""
    # Arrange
    text = "This is a test message with several words in it."
    max_chars = 10  # Too small, should be adjusted to 50
    
    # Act
    result = await chunk_message(text, max_chars=max_chars)
    
    # Assert
    assert result["success"] is True
    # Check that chunks respect the adjusted minimum of 50 chars
    for chunk in result["chunks"][:-1]:  # All but potentially the last chunk
        assert chunk["chars"] <= 50


@pytest.mark.asyncio
async def test_chunk_message_multiple_paragraphs():
    """Test chunking text with multiple paragraphs"""
    # Arrange
    text = """First paragraph with some content here.

Second paragraph with more content.

Third paragraph that is much longer and contains multiple sentences. It should be handled properly by the chunking algorithm. The algorithm should respect paragraph boundaries when possible."""
    
    max_chars = 100
    
    # Act
    result = await chunk_message(text, max_chars=max_chars)
    
    # Assert
    assert result["success"] is True
    assert result["total_chunks"] >= 2
    # Original structure should be preserved (normalized to double line breaks)
    combined = "\n\n".join(chunk["text"] for chunk in result["chunks"])
    # Normalize the original text the same way
    normalized_text = text.strip()
    assert combined == normalized_text.replace('\n\n\n', '\n\n')


@pytest.mark.asyncio
async def test_chunk_message_delay_calculation():
    """Test that delay calculation is proportional to chunk size"""
    # Arrange
    text = "Short. " * 5 + "This is a much longer chunk with many more words in it. " * 10
    max_chars = 100
    
    # Mock random to get predictable results
    with patch('agente.tools.whatsapp.message_chunking.random.randint', return_value=0):
        # Act
        result = await chunk_message(text, max_chars=max_chars)
    
    # Assert
    assert result["success"] is True
    assert len(result["chunks"]) >= 2
    
    # Find short and long chunks
    short_chunk = min(result["chunks"], key=lambda c: c["words"])
    long_chunk = max(result["chunks"], key=lambda c: c["words"])
    
    # Longer chunk should have longer delay
    assert long_chunk["delay_ms"] > short_chunk["delay_ms"]


@pytest.mark.asyncio
async def test_chunk_message_statistics():
    """Test that statistics are calculated correctly"""
    # Arrange
    text = "Test message. " * 50
    max_chars = 100
    
    # Act
    result = await chunk_message(text, max_chars=max_chars)
    
    # Assert
    assert result["success"] is True
    
    # Verify statistics
    total_chars_sum = sum(chunk["chars"] for chunk in result["chunks"])
    assert result["total_chars"] == total_chars_sum
    
    average = total_chars_sum / len(result["chunks"])
    assert abs(result["average_chunk_size"] - average) < 0.1
    
    total_delay_sum = sum(chunk["delay_ms"] for chunk in result["chunks"])
    assert result["total_delay_ms"] == total_delay_sum


@pytest.mark.asyncio
async def test_chunk_message_exception_handling():
    """Test exception handling in chunk_message"""
    # Arrange
    text = "Test message"
    
    # Mock re.sub to raise an exception
    with patch('re.sub', side_effect=Exception("Regex error")):
        # Act
        result = await chunk_message(text)
    
    # Assert
    assert result["success"] is False
    assert "Regex error" in result["error"]
    assert result["chunks"] == []


@pytest.mark.asyncio
async def test_chunk_message_exact_boundary():
    """Test chunking when text length is exactly max_chars"""
    # Arrange
    text = "X" * 100
    max_chars = 100
    
    # Act
    result = await chunk_message(text, max_chars=max_chars)
    
    # Assert
    assert result["success"] is True
    assert result["total_chunks"] == 1
    assert result["chunks"][0]["chars"] == 100


@pytest.mark.asyncio
async def test_chunk_message_punctuation_variations():
    """Test chunking with various punctuation marks"""
    # Arrange
    text = ("What is this? " * 10 + 
            "This is amazing! " * 10 + 
            "Really... " * 10 +
            "End.")
    max_chars = 100
    
    # Act
    result = await chunk_message(text, max_chars=max_chars, prefer_sentences=True)
    
    # Assert
    assert result["success"] is True
    
    # Check that chunks properly handle different punctuation
    for chunk in result["chunks"]:
        assert len(chunk["text"]) > 0
        assert chunk["text"] == chunk["text"].strip()


@pytest.mark.asyncio
async def test_chunk_message_word_boundary_fallback():
    """Test fallback to word boundaries when no sentence endings found"""
    # Arrange
    # Long text without punctuation
    text = "very long text without any punctuation just continuous words " * 20
    max_chars = 150
    
    # Act
    result = await chunk_message(text, max_chars=max_chars, prefer_sentences=True)
    
    # Assert
    assert result["success"] is True
    assert result["total_chunks"] > 1
    
    # Check chunks don't break in middle of words
    for chunk in result["chunks"]:
        # Should not end with partial word (unless it's the last chunk)
        if chunk != result["chunks"][-1]:
            assert chunk["text"][-1] == ' ' or chunk["text"][-1] in '.!?'


@pytest.mark.asyncio
async def test_chunk_message_unicode_handling():
    """Test chunking with unicode characters and emojis"""
    # Arrange
    text = "Hello 👋 This is a test with émojis 😊 and spëcial characters! " * 5
    max_chars = 100
    
    # Act
    result = await chunk_message(text, max_chars=max_chars)
    
    # Assert
    assert result["success"] is True
    assert result["total_chunks"] >= 1
    
    # Verify unicode is preserved
    combined = " ".join(chunk["text"] for chunk in result["chunks"])
    assert "👋" in combined
    assert "😊" in combined
    assert "ë" in combined


@pytest.mark.asyncio
async def test_chunk_message_total_delay_calculation():
    """Test total delay calculation across all chunks"""
    # Arrange
    text = "Test sentence. " * 30
    max_chars = 100
    min_delay = 1000
    max_delay = 3000
    
    # Act
    result = await chunk_message(
        text,
        max_chars=max_chars,
        min_delay_ms=min_delay,
        max_delay_ms=max_delay
    )
    
    # Assert
    assert result["success"] is True
    
    # Total delay should be sum of all chunk delays
    calculated_total = sum(chunk["delay_ms"] for chunk in result["chunks"])
    assert result["total_delay_ms"] == calculated_total
    
    # Total delay should be reasonable for the number of chunks
    expected_min_total = len(result["chunks"]) * min_delay * 0.9  # Account for variation
    expected_max_total = len(result["chunks"]) * max_delay * 1.1  # Account for variation
    assert expected_min_total <= result["total_delay_ms"] <= expected_max_total