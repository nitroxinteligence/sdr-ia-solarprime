"""
Unit tests for Kommo search_lead tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agente.tools.kommo.search_lead import (
    search_kommo_lead,
    search_lead_by_phone,
    SearchKommoLeadTool,
    SearchLeadByPhoneTool
)
from agente.services.kommo_service import KommoAPIError


@pytest.fixture
def mock_kommo_service():
    """Mock Kommo service for tests"""
    service = AsyncMock()
    service.search_leads = AsyncMock()
    service.get_lead_by_phone = AsyncMock()
    return service


@pytest.fixture
def mock_leads():
    """Mock leads data"""
    return [
        {
            "id": 12345,
            "name": "João Silva",
            "price": 1500,
            "status_id": 1001,
            "pipeline_id": 2001,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-10T15:00:00Z",
            "_embedded": {
                "tags": [
                    {"id": 1, "name": "Solar"},
                    {"id": 2, "name": "WhatsApp"}
                ]
            },
            "custom_fields_values": [
                {
                    "field_id": "123",
                    "field_code": "PHONE",
                    "field_name": "Telefone",
                    "values": [{"value": "5511999999999"}]
                },
                {
                    "field_id": "456",
                    "field_code": "EMAIL",
                    "field_name": "Email",
                    "values": [{"value": "joao@example.com"}]
                }
            ]
        },
        {
            "id": 67890,
            "name": "Maria Santos",
            "price": 2000,
            "status_id": 1002,
            "pipeline_id": 2001,
            "created_at": "2024-01-05T14:00:00Z",
            "updated_at": "2024-01-12T10:00:00Z",
            "_embedded": {
                "tags": [
                    {"id": 3, "name": "Premium"}
                ]
            },
            "custom_fields_values": [
                {
                    "field_id": "123",
                    "field_code": "PHONE",
                    "values": [{"value": "5511888888888"}]
                },
                {
                    "field_id": "789",
                    "field_name": "Endereço",
                    "values": [{"value": "Rua Solar, 123"}]
                }
            ]
        }
    ]


@pytest.mark.asyncio
class TestSearchKommoLead:
    """Test cases for search_kommo_lead tool"""

    async def test_search_lead_success(self, mock_kommo_service, mock_leads):
        """Test successful lead search"""
        # Arrange
        mock_kommo_service.search_leads.return_value = mock_leads
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(
                query="João",
                limit=50
            )
        
        # Assert
        assert result["success"] is True
        assert result["count"] == 2
        assert result["query"] == "João"
        assert len(result["leads"]) == 2
        
        # Check first lead
        lead1 = result["leads"][0]
        assert lead1["id"] == 12345
        assert lead1["name"] == "João Silva"
        assert lead1["price"] == 1500
        assert lead1["phone"] == "5511999999999"
        assert lead1["email"] == "joao@example.com"
        assert "Solar" in lead1["tags"]
        assert "WhatsApp" in lead1["tags"]
        
        # Check second lead
        lead2 = result["leads"][1]
        assert lead2["id"] == 67890
        assert lead2["name"] == "Maria Santos"
        assert lead2["phone"] == "5511888888888"
        assert "email" not in lead2  # No email field
        assert lead2["Endereço"] == "Rua Solar, 123"  # Custom field
        
        # Verify service call
        mock_kommo_service.search_leads.assert_called_once_with("João", limit=50)

    async def test_search_lead_no_results(self, mock_kommo_service):
        """Test search with no results"""
        # Arrange
        mock_kommo_service.search_leads.return_value = []
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(
                query="NonExistent"
            )
        
        # Assert
        assert result["success"] is True
        assert result["count"] == 0
        assert result["leads"] == []
        assert result["query"] == "NonExistent"

    async def test_search_lead_by_phone_number(self, mock_kommo_service, mock_leads):
        """Test searching by phone number"""
        # Arrange
        mock_kommo_service.search_leads.return_value = [mock_leads[0]]
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(
                query="5511999999999"
            )
        
        # Assert
        assert result["success"] is True
        assert result["count"] == 1
        assert result["leads"][0]["phone"] == "5511999999999"

    async def test_search_lead_by_email(self, mock_kommo_service, mock_leads):
        """Test searching by email"""
        # Arrange
        mock_kommo_service.search_leads.return_value = [mock_leads[0]]
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(
                query="joao@example.com"
            )
        
        # Assert
        assert result["success"] is True
        assert result["count"] == 1
        assert result["leads"][0]["email"] == "joao@example.com"

    async def test_search_lead_with_limit(self, mock_kommo_service, mock_leads):
        """Test search with custom limit"""
        # Arrange
        mock_kommo_service.search_leads.return_value = mock_leads[:1]
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(
                query="test",
                limit=1
            )
        
        # Assert
        assert result["success"] is True
        assert result["count"] == 1
        mock_kommo_service.search_leads.assert_called_once_with("test", limit=1)

    async def test_search_lead_api_error(self, mock_kommo_service):
        """Test API error during search"""
        # Arrange
        mock_kommo_service.search_leads.side_effect = KommoAPIError(
            status_code=400,
            message="Invalid query"
        )
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(
                query="test"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro da API do Kommo" in result["error"]
        assert result["count"] == 0
        assert result["leads"] == []

    async def test_search_lead_unexpected_error(self, mock_kommo_service):
        """Test unexpected error during search"""
        # Arrange
        mock_kommo_service.search_leads.side_effect = Exception("Connection error")
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(
                query="test"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro inesperado" in result["error"]
        assert result["count"] == 0

    async def test_search_lead_custom_fields_handling(self, mock_kommo_service):
        """Test handling of various custom field structures"""
        # Arrange
        leads_with_custom_fields = [
            {
                "id": 11111,
                "name": "Test Lead",
                "custom_fields_values": [
                    {
                        "field_id": "999",
                        "field_name": "Campo Customizado",
                        "values": [{"value": "Valor Custom"}]
                    },
                    {
                        "field_id": "888",
                        # No field_name
                        "values": [{"value": "Sem Nome"}]
                    },
                    {
                        "field_id": "777",
                        "field_name": "Campo Vazio",
                        "values": []  # Empty values
                    },
                    {
                        "field_id": "666",
                        "field_name": "Campo Null",
                        "values": [{"value": None}]  # Null value
                    }
                ]
            }
        ]
        mock_kommo_service.search_leads.return_value = leads_with_custom_fields
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(query="test")
        
        # Assert
        assert result["success"] is True
        lead = result["leads"][0]
        assert lead["Campo Customizado"] == "Valor Custom"
        assert lead["custom_999"] == "Sem Nome"  # Fallback field name
        assert "Campo Vazio" not in lead  # Empty values ignored
        assert "Campo Null" not in lead  # Null values ignored


@pytest.mark.asyncio
class TestSearchLeadByPhone:
    """Test cases for search_lead_by_phone tool"""

    async def test_search_by_phone_found(self, mock_kommo_service, mock_leads):
        """Test successful phone search"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = mock_leads[0]
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_lead_by_phone(
                phone="5511999999999"
            )
        
        # Assert
        assert result["success"] is True
        assert result["found"] is True
        assert result["phone"] == "5511999999999"
        assert result["lead"]["id"] == 12345
        assert result["lead"]["name"] == "João Silva"
        assert result["lead"]["PHONE"] == "5511999999999"
        assert result["lead"]["EMAIL"] == "joao@example.com"
        
        # Verify service call
        mock_kommo_service.get_lead_by_phone.assert_called_once_with("5511999999999")

    async def test_search_by_phone_not_found(self, mock_kommo_service):
        """Test phone search with no results"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_lead_by_phone(
                phone="5511777777777"
            )
        
        # Assert
        assert result["success"] is True
        assert result["found"] is False
        assert result["lead"] is None
        assert result["phone"] == "5511777777777"
        assert "Nenhum lead encontrado" in result["message"]

    async def test_search_by_phone_various_formats(self, mock_kommo_service, mock_leads):
        """Test searching with different phone formats"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = mock_leads[0]
        
        phone_formats = [
            "5511999999999",
            "+5511999999999",
            "11999999999",
            "(11) 99999-9999",
            "+55 11 99999-9999"
        ]
        
        for phone_format in phone_formats:
            with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
                # Act
                result = await search_lead_by_phone(phone=phone_format)
            
            # Assert
            assert result["success"] is True
            assert result["found"] is True
            assert result["phone"] == phone_format
            
            # Verify service was called with exact format
            mock_kommo_service.get_lead_by_phone.assert_called_with(phone_format)

    async def test_search_by_phone_error(self, mock_kommo_service):
        """Test error handling during phone search"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.side_effect = Exception("API Error")
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_lead_by_phone(
                phone="5511999999999"
            )
        
        # Assert
        assert result["success"] is False
        assert result["found"] is False
        assert result["lead"] is None
        assert "Erro ao buscar lead" in result["error"]

    async def test_search_by_phone_custom_fields(self, mock_kommo_service):
        """Test phone search with various custom field structures"""
        # Arrange
        lead_with_many_fields = {
            "id": 12345,
            "name": "Test Lead",
            "custom_fields_values": [
                {"field_id": "123", "field_code": "PHONE", "values": [{"value": "5511999999999"}]},
                {"field_id": "456", "field_code": "EMAIL", "values": [{"value": "test@example.com"}]},
                {"field_id": "789", "field_code": "ADDRESS", "values": [{"value": "Rua Test, 123"}]},
                {"field_id": "101", "values": [{"value": "No field code"}]},  # No field_code
                {"field_id": "102", "field_code": "EMPTY", "values": []},  # Empty values
            ]
        }
        mock_kommo_service.get_lead_by_phone.return_value = lead_with_many_fields
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_lead_by_phone(phone="5511999999999")
        
        # Assert
        assert result["success"] is True
        assert result["found"] is True
        lead = result["lead"]
        assert lead["PHONE"] == "5511999999999"
        assert lead["EMAIL"] == "test@example.com"
        assert lead["ADDRESS"] == "Rua Test, 123"
        assert lead["field_101"] == "No field code"
        assert "EMPTY" not in lead  # Empty values ignored

    async def test_tool_instances(self):
        """Test that all tool instances are correctly exported"""
        assert SearchKommoLeadTool == search_kommo_lead
        assert SearchLeadByPhoneTool == search_lead_by_phone
        assert callable(SearchKommoLeadTool)
        assert callable(SearchLeadByPhoneTool)

    async def test_search_lead_rate_limit_handling(self, mock_kommo_service):
        """Test handling of rate limit errors"""
        # Arrange
        mock_kommo_service.search_leads.side_effect = KommoAPIError(
            status_code=429,
            message="Too Many Requests"
        )
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(query="test")
        
        # Assert
        assert result["success"] is False
        assert "429" in result["error"] or "Too Many Requests" in result["error"]

    async def test_search_lead_authentication_error(self, mock_kommo_service):
        """Test handling of authentication errors"""
        # Arrange
        mock_kommo_service.search_leads.side_effect = KommoAPIError(
            status_code=401,
            message="Unauthorized"
        )
        
        with patch('agente.tools.kommo.search_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await search_kommo_lead(query="test")
        
        # Assert
        assert result["success"] is False
        assert "401" in result["error"] or "Unauthorized" in result["error"]