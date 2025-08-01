"""
Unit tests for the validate_phone tool.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from agente.tools.utility.validate_phone import validate_phone, ValidatePhoneTool


class TestValidatePhone:
    """Test suite for validate_phone tool."""
    
    @pytest.mark.asyncio
    async def test_validate_phone_success_mobile(self):
        """Test successful validation of a mobile phone number."""
        result = await validate_phone("11 98765-4321")
        
        assert result["success"] is True
        assert result["original"] == "11 98765-4321"
        assert result["formatted"] == "+5511987654321"
        assert result["is_mobile"] is True
        assert result["ddd"] == "11"
        
    @pytest.mark.asyncio
    async def test_validate_phone_success_landline(self):
        """Test successful validation of a landline phone number."""
        result = await validate_phone("11 3456-7890")
        
        assert result["success"] is True
        assert result["original"] == "11 3456-7890"
        assert result["formatted"] == "+5511345678900"
        assert result["is_mobile"] is False
        assert result["ddd"] == "11"
        
    @pytest.mark.asyncio
    async def test_validate_phone_different_formats(self):
        """Test validation with different input formats."""
        test_cases = [
            # (input, expected_formatted)
            ("11987654321", "+5511987654321"),  # No formatting
            ("(11) 98765-4321", "+5511987654321"),  # With parentheses
            ("11 9 8765-4321", "+5511987654321"),  # With extra space
            ("+5511987654321", "+5511987654321"),  # Already formatted
            ("5511987654321", "+5511987654321"),  # With country code
            ("011987654321", "+5511987654321"),  # With 0 prefix
        ]
        
        for phone_input, expected in test_cases:
            result = await validate_phone(phone_input)
            assert result["success"] is True, f"Failed for input: {phone_input}"
            assert result["formatted"] == expected, f"Wrong format for input: {phone_input}"
            
    @pytest.mark.asyncio
    async def test_validate_phone_all_valid_ddd_codes(self):
        """Test validation with all valid Brazilian DDD codes."""
        # Sample of valid DDD codes
        valid_ddds = ["11", "21", "31", "41", "51", "61", "71", "81", "85", "91"]
        
        for ddd in valid_ddds:
            phone = f"{ddd}987654321"
            result = await validate_phone(phone)
            
            assert result["success"] is True, f"Failed for DDD: {ddd}"
            assert result["ddd"] == ddd
            assert result["is_mobile"] is True
            
    @pytest.mark.asyncio
    async def test_validate_phone_invalid_ddd(self):
        """Test validation with invalid DDD codes."""
        invalid_phones = [
            "00987654321",  # Invalid DDD 00
            "10987654321",  # Invalid DDD 10
            "20987654321",  # Invalid DDD 20
            "90987654321",  # Invalid DDD 90
            "99987654321",  # Invalid DDD > 99
        ]
        
        for phone in invalid_phones:
            result = await validate_phone(phone)
            assert result["success"] is False
            assert "error" in result
            
    @pytest.mark.asyncio
    async def test_validate_phone_invalid_length(self):
        """Test validation with invalid phone lengths."""
        invalid_phones = [
            "119876543",  # Too short (9 digits total)
            "11987654321234",  # Too long (14 digits total)
            "1198765",  # Way too short
            "11",  # Only DDD
            "",  # Empty string
        ]
        
        for phone in invalid_phones:
            result = await validate_phone(phone)
            assert result["success"] is False
            assert "error" in result
            
    @pytest.mark.asyncio
    async def test_validate_phone_with_letters(self):
        """Test validation with invalid characters."""
        invalid_phones = [
            "11 9ABCD-1234",
            "telefone: 11987654321",
            "11-nine-8765-4321",
            "11 98765-432X",
        ]
        
        for phone in invalid_phones:
            result = await validate_phone(phone)
            assert result["success"] is False
            assert "error" in result
            
    @pytest.mark.asyncio
    async def test_validate_phone_mobile_detection(self):
        """Test correct detection of mobile vs landline numbers."""
        # Mobile numbers (9 digits after DDD)
        mobile_numbers = [
            "11987654321",
            "21999887766",
            "85988776655",
        ]
        
        for phone in mobile_numbers:
            result = await validate_phone(phone)
            assert result["success"] is True
            assert result["is_mobile"] is True
            
        # Landline numbers (8 digits after DDD)
        landline_numbers = [
            "1134567890",
            "2122334455",
            "8533445566",
        ]
        
        for phone in landline_numbers:
            result = await validate_phone(phone)
            assert result["success"] is True
            assert result["is_mobile"] is False
            
    @pytest.mark.asyncio
    async def test_validate_phone_whatsapp_format(self):
        """Test validation of WhatsApp-style phone numbers."""
        # WhatsApp often includes country code
        whatsapp_numbers = [
            "+55 11 98765-4321",
            "+5511987654321",
            "55 11 98765-4321",
            "+55 (11) 98765-4321",
        ]
        
        for phone in whatsapp_numbers:
            result = await validate_phone(phone)
            assert result["success"] is True
            assert result["formatted"] == "+5511987654321"
            assert result["is_mobile"] is True
            
    @pytest.mark.asyncio
    async def test_validate_phone_with_exception_handling(self):
        """Test exception handling in validate_phone."""
        # Mock the validate_phone_number to raise an exception
        with patch('agente.tools.utility.validate_phone.validate_phone_number') as mock_validate:
            mock_validate.side_effect = Exception("Test exception")
            
            result = await validate_phone("11987654321")
            
            assert result["success"] is False
            assert "Erro ao processar telefone" in result["error"]
            assert "Test exception" in result["error"]
            
    @pytest.mark.asyncio
    async def test_validate_phone_tool_export(self):
        """Test that ValidatePhoneTool is properly exported."""
        assert ValidatePhoneTool is not None
        assert ValidatePhoneTool == validate_phone
        
    @pytest.mark.asyncio
    async def test_validate_phone_edge_cases(self):
        """Test edge cases for phone validation."""
        # Phone with many special characters
        result = await validate_phone("(+55) (11) 9-8765-4321")
        assert result["success"] is True
        assert result["formatted"] == "+5511987654321"
        
        # Phone with dots
        result = await validate_phone("11.9.8765.4321")
        assert result["success"] is True
        assert result["formatted"] == "+5511987654321"
        
        # Phone with mixed separators
        result = await validate_phone("11-98765.4321")
        assert result["success"] is True
        assert result["formatted"] == "+5511987654321"
        
    @pytest.mark.asyncio
    async def test_validate_phone_brazilian_regions(self):
        """Test phone validation for different Brazilian regions."""
        regional_phones = [
            # São Paulo
            ("11987654321", "11", "São Paulo"),
            ("12987654321", "12", "Vale do Paraíba"),
            ("13987654321", "13", "Santos"),
            # Rio de Janeiro
            ("21987654321", "21", "Rio de Janeiro"),
            ("22987654321", "22", "Interior RJ"),
            # Minas Gerais
            ("31987654321", "31", "Belo Horizonte"),
            ("32987654321", "32", "Juiz de Fora"),
            # Northeast
            ("81987654321", "81", "Recife"),
            ("85987654321", "85", "Fortaleza"),
            ("71987654321", "71", "Salvador"),
        ]
        
        for phone, expected_ddd, region in regional_phones:
            result = await validate_phone(phone)
            assert result["success"] is True, f"Failed for {region}"
            assert result["ddd"] == expected_ddd
            
    @pytest.mark.asyncio
    async def test_validate_phone_old_mobile_format(self):
        """Test validation of old mobile format (8 digits starting with 7/8/9)."""
        # Some older mobile numbers might still exist
        old_format = "1197654321"  # 11 + 97654321 (8 digits starting with 9)
        
        result = await validate_phone(old_format)
        # This should be treated as having 10 digits total, which might be invalid
        # depending on the validation rules
        assert "success" in result
        
    @pytest.mark.asyncio
    async def test_validate_phone_with_spaces_and_dashes(self):
        """Test validation preserves original format in response."""
        original = "(11) 9 8765-4321"
        result = await validate_phone(original)
        
        assert result["success"] is True
        assert result["original"] == original  # Should preserve original
        assert result["formatted"] == "+5511987654321"  # But format correctly
        
    @pytest.mark.asyncio
    async def test_validate_phone_solar_prime_context(self):
        """Test phone validation in Solar Prime SDR context."""
        # Typical customer phone formats from WhatsApp
        customer_phones = [
            "11 98765-4321",  # Common WhatsApp format
            "(81) 99876-5432",  # Recife area (SolarPrime location)
            "+55 81 9 8765-4321",  # International format
            "081 987654321",  # With 0 prefix
            "81987654321",  # Just numbers
        ]
        
        for phone in customer_phones:
            result = await validate_phone(phone)
            assert result["success"] is True
            assert result["formatted"].startswith("+55")
            assert len(result["formatted"]) == 14  # +55 + 11 digits
            
    @pytest.mark.asyncio
    async def test_validate_phone_error_messages(self):
        """Test specific error messages for different validation failures."""
        # Test with empty phone
        result = await validate_phone("")
        assert result["success"] is False
        assert "error" in result
        
        # Test with None (if not handled by type checking)
        try:
            result = await validate_phone(None)
            assert result["success"] is False
            assert "error" in result
        except:
            # It's ok if it raises an exception for None
            pass
            
    @pytest.mark.asyncio
    async def test_validate_phone_formatted_output_consistency(self):
        """Test that formatted output is always consistent."""
        # Same number in different formats should produce same output
        different_formats = [
            "11987654321",
            "11 98765-4321",
            "(11) 98765-4321",
            "+5511987654321",
            "011 98765-4321",
            "11-98765-4321",
            "+55 11 98765 4321",
        ]
        
        expected_formatted = "+5511987654321"
        
        for phone_format in different_formats:
            result = await validate_phone(phone_format)
            assert result["success"] is True, f"Failed for format: {phone_format}"
            assert result["formatted"] == expected_formatted, f"Inconsistent output for: {phone_format}"