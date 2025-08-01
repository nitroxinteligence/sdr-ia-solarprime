"""
Unit tests for the format_currency and extract_currency_from_text tools.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
from decimal import Decimal

from agente.tools.utility.format_currency import (
    format_currency, 
    extract_currency_from_text,
    FormatCurrencyTool,
    ExtractCurrencyFromTextTool
)


class TestFormatCurrency:
    """Test suite for format_currency tool."""
    
    @pytest.mark.asyncio
    async def test_format_currency_with_float(self):
        """Test formatting a float value."""
        result = await format_currency(1234.56)
        
        assert result["success"] is True
        assert result["original"] == "1234.56"
        assert result["formatted"] == "R$ 1.234,56"
        assert result["numeric_value"] == 1234.56
        
    @pytest.mark.asyncio
    async def test_format_currency_with_integer(self):
        """Test formatting an integer value."""
        result = await format_currency(1500)
        
        assert result["success"] is True
        assert result["original"] == "1500"
        assert result["formatted"] == "R$ 1.500,00"
        assert result["numeric_value"] == 1500.0
        
    @pytest.mark.asyncio
    async def test_format_currency_with_string_dot_separator(self):
        """Test formatting a string with dot as decimal separator."""
        result = await format_currency("350.90")
        
        assert result["success"] is True
        assert result["original"] == "350.90"
        assert result["formatted"] == "R$ 350,90"
        assert result["numeric_value"] == 350.90
        
    @pytest.mark.asyncio
    async def test_format_currency_with_string_comma_separator(self):
        """Test formatting a string with comma as decimal separator."""
        result = await format_currency("350,90")
        
        assert result["success"] is True
        assert result["original"] == "350,90"
        assert result["formatted"] == "R$ 350,90"
        assert result["numeric_value"] == 350.90
        
    @pytest.mark.asyncio
    async def test_format_currency_with_thousand_separator(self):
        """Test formatting a string with thousand separator."""
        result = await format_currency("1.234,56")
        
        assert result["success"] is True
        assert result["original"] == "1.234,56"
        assert result["formatted"] == "R$ 1.234,56"
        assert result["numeric_value"] == 1234.56
        
    @pytest.mark.asyncio
    async def test_format_currency_with_r_symbol(self):
        """Test formatting a string that already contains R$ symbol."""
        result = await format_currency("R$ 450,00")
        
        assert result["success"] is True
        assert result["original"] == "R$ 450,00"
        assert result["formatted"] == "R$ 450,00"
        assert result["numeric_value"] == 450.0
        
    @pytest.mark.asyncio
    async def test_format_currency_with_validation(self):
        """Test formatting with bill validation enabled."""
        # Valid bill amount
        result = await format_currency("350.00", validate=True)
        
        assert result["success"] is True
        assert result["is_valid_bill"] is True
        assert "validation_message" not in result
        
        # Invalid bill amount (too low)
        result = await format_currency("10.00", validate=True)
        
        assert result["success"] is True
        assert result["is_valid_bill"] is False
        assert "validation_message" in result
        
    @pytest.mark.asyncio
    async def test_format_currency_without_cents(self):
        """Test formatting without including cents."""
        result = await format_currency(1234.56, include_cents=False)
        
        assert result["success"] is True
        assert result["formatted"] == "R$ 1.234"
        assert result["numeric_value"] == 1234.56
        
    @pytest.mark.asyncio
    async def test_format_currency_with_text_containing_number(self):
        """Test extracting and formatting number from text."""
        result = await format_currency("O valor é 450,00 reais")
        
        assert result["success"] is True
        assert result["formatted"] == "R$ 450,00"
        assert result["numeric_value"] == 450.0
        
    @pytest.mark.asyncio
    async def test_format_currency_with_invalid_value(self):
        """Test formatting with invalid values."""
        # Test with text without numbers
        result = await format_currency("sem números aqui")
        
        assert result["success"] is False
        assert "Não foi possível extrair um valor numérico" in result["error"]
        
        # Test with empty string
        result = await format_currency("")
        
        assert result["success"] is False
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_format_currency_with_exception_handling(self):
        """Test exception handling in format_currency."""
        # Test with None value causing exception
        with patch('agente.tools.utility.format_currency.float') as mock_float:
            mock_float.side_effect = Exception("Test exception")
            
            result = await format_currency("test")
            
            assert result["success"] is False
            assert "error" in result
            
    @pytest.mark.asyncio
    async def test_format_currency_tool_export(self):
        """Test that FormatCurrencyTool is properly exported."""
        assert FormatCurrencyTool is not None
        assert FormatCurrencyTool == format_currency
        
    @pytest.mark.asyncio
    async def test_format_currency_with_large_values(self):
        """Test formatting large monetary values."""
        result = await format_currency(1234567.89)
        
        assert result["success"] is True
        assert result["formatted"] == "R$ 1.234.567,89"
        assert result["numeric_value"] == 1234567.89
        
    @pytest.mark.asyncio
    async def test_format_currency_with_zero(self):
        """Test formatting zero value."""
        result = await format_currency(0)
        
        assert result["success"] is True
        assert result["formatted"] == "R$ 0,00"
        assert result["numeric_value"] == 0.0
        
    @pytest.mark.asyncio
    async def test_format_currency_with_negative_value(self):
        """Test formatting negative values."""
        result = await format_currency(-100.50)
        
        assert result["success"] is True
        assert result["formatted"] == "R$ -100,50"
        assert result["numeric_value"] == -100.50


class TestExtractCurrencyFromText:
    """Test suite for extract_currency_from_text tool."""
    
    @pytest.mark.asyncio
    async def test_extract_currency_simple_case(self):
        """Test extracting currency from simple text."""
        result = await extract_currency_from_text("Minha conta veio R$ 450,00 esse mês")
        
        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["values"]) == 1
        assert result["values"][0]["original"] == "R$ 450,00"
        assert result["values"][0]["formatted"] == "R$ 450,00"
        assert result["values"][0]["numeric_value"] == 450.0
        
    @pytest.mark.asyncio
    async def test_extract_currency_multiple_values(self):
        """Test extracting multiple currency values from text."""
        text = "A conta antiga era R$ 350,00 mas agora está R$ 425,50"
        result = await extract_currency_from_text(text)
        
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["values"]) == 2
        assert result["values"][0]["numeric_value"] == 350.0
        assert result["values"][1]["numeric_value"] == 425.50
        
    @pytest.mark.asyncio
    async def test_extract_currency_with_word_reais(self):
        """Test extracting values with 'reais' word."""
        result = await extract_currency_from_text("Pago 320 reais de luz")
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["values"][0]["numeric_value"] == 320.0
        
    @pytest.mark.asyncio
    async def test_extract_currency_with_context_keywords(self):
        """Test extracting values with context keywords."""
        text = "O valor da conta é 485,90 e o total do mês foi 485,90"
        result = await extract_currency_from_text(text)
        
        assert result["success"] is True
        # Should remove duplicates
        assert result["count"] == 1
        assert result["values"][0]["numeric_value"] == 485.90
        
    @pytest.mark.asyncio
    async def test_extract_currency_no_values(self):
        """Test extracting from text without currency values."""
        result = await extract_currency_from_text("Não tenho valores monetários aqui")
        
        assert result["success"] is False
        assert result["count"] == 0
        assert len(result["values"]) == 0
        
    @pytest.mark.asyncio
    async def test_extract_currency_with_decimal_formats(self):
        """Test extracting different decimal formats."""
        text = "Valores: 123,45 e 678.90 e R$901,23"
        result = await extract_currency_from_text(text)
        
        assert result["success"] is True
        assert result["count"] >= 2  # At least 2 unique values
        
    @pytest.mark.asyncio
    async def test_extract_currency_bill_validation(self):
        """Test that extracted values are validated as bills."""
        result = await extract_currency_from_text("Conta de R$ 350,00")
        
        assert result["success"] is True
        assert result["values"][0]["is_valid_bill"] is True
        
    @pytest.mark.asyncio
    async def test_extract_currency_with_exception_handling(self):
        """Test exception handling in extract_currency_from_text."""
        with patch('agente.tools.utility.format_currency.re.finditer') as mock_finditer:
            mock_finditer.side_effect = Exception("Test exception")
            
            result = await extract_currency_from_text("test text")
            
            assert result["success"] is False
            assert "error" in result
            assert result["count"] == 0
            
    @pytest.mark.asyncio
    async def test_extract_currency_tool_export(self):
        """Test that ExtractCurrencyFromTextTool is properly exported."""
        assert ExtractCurrencyFromTextTool is not None
        assert ExtractCurrencyFromTextTool == extract_currency_from_text
        
    @pytest.mark.asyncio
    async def test_extract_currency_with_special_patterns(self):
        """Test extracting currency with special patterns."""
        # Test with colon separator
        result = await extract_currency_from_text("Valor: R$ 450,00")
        assert result["success"] is True
        assert result["values"][0]["numeric_value"] == 450.0
        
        # Test with 'total' keyword
        result = await extract_currency_from_text("Total 350,00")
        assert result["success"] is True
        assert result["values"][0]["numeric_value"] == 350.0
        
        # Test with 'pagamento' keyword
        result = await extract_currency_from_text("Pagamento de 280,50")
        assert result["success"] is True
        assert result["values"][0]["numeric_value"] == 280.50
        
    @pytest.mark.asyncio
    async def test_extract_currency_overlapping_patterns(self):
        """Test that overlapping patterns don't create duplicates."""
        text = "R$ 450,00 reais"  # Both patterns match the same value
        result = await extract_currency_from_text(text)
        
        assert result["success"] is True
        assert result["count"] == 1  # Should not duplicate
        
    @pytest.mark.asyncio
    async def test_extract_currency_long_text(self):
        """Test extracting from long text (simulating real message)."""
        text = """
        Olá, recebi minha conta de luz esse mês e o valor está R$ 456,78.
        No mês passado eu paguei 398,50 reais. Acho que está muito alto.
        Vi que o consumo foi de 450 kWh. Será que vale a pena instalar
        energia solar? O investimento seria de uns 15000 reais?
        """
        result = await extract_currency_from_text(text)
        
        assert result["success"] is True
        assert result["count"] >= 3  # Should find at least 3 values
        
        # Check if values were found
        numeric_values = [v["numeric_value"] for v in result["values"]]
        assert 456.78 in numeric_values
        assert 398.50 in numeric_values
        assert 15000.0 in numeric_values
        
    @pytest.mark.asyncio
    async def test_format_currency_typical_energy_bill_values(self):
        """Test formatting typical energy bill values for Solar Prime context."""
        typical_values = [
            ("R$ 250,00", 250.0),
            ("R$ 350,50", 350.50),
            ("R$ 1.234,56", 1234.56),
            ("450", 450.0),
            ("R$ 2.500,00", 2500.0)
        ]
        
        for original, expected_numeric in typical_values:
            result = await format_currency(original, validate=True)
            
            assert result["success"] is True
            assert result["numeric_value"] == expected_numeric
            assert result["is_valid_bill"] is True  # All should be valid bill amounts
            
    @pytest.mark.asyncio
    async def test_extract_currency_from_whatsapp_message(self):
        """Test extracting currency from typical WhatsApp message formats."""
        messages = [
            "minha conta veio 380 esse mes",
            "to pagando R$450,00 de luz",
            "a fatura chegou no valor de 523,45",
            "conta de energia: R$ 678,90"
        ]
        
        for msg in messages:
            result = await extract_currency_from_text(msg)
            assert result["success"] is True
            assert result["count"] > 0
            
    @pytest.mark.asyncio
    async def test_format_currency_edge_cases(self):
        """Test edge cases for currency formatting."""
        # Very small value
        result = await format_currency(0.01)
        assert result["success"] is True
        assert result["formatted"] == "R$ 0,01"
        
        # Value with many decimal places
        result = await format_currency(123.456789)
        assert result["success"] is True
        # Should handle rounding appropriately
        
        # String with spaces
        result = await format_currency(" 350,00 ")
        assert result["success"] is True
        assert result["numeric_value"] == 350.0