"""
Unit tests for Kommo update_lead tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agente.tools.kommo.update_lead import update_kommo_lead, UpdateKommoLeadTool
from agente.services.kommo_service import KommoAPIError


@pytest.fixture
def mock_kommo_service():
    """Mock Kommo service for tests"""
    service = AsyncMock()
    service.get_lead = AsyncMock()
    service.get_custom_fields = AsyncMock()
    service.update_lead = AsyncMock()
    service.add_tag = AsyncMock()
    service._make_request = AsyncMock()
    return service


@pytest.fixture
def mock_current_lead():
    """Mock current lead data"""
    return {
        "id": 12345,
        "name": "João Silva",
        "price": 1000,
        "status_id": 1001,
        "pipeline_id": 2001,
        "updated_at": "2024-01-10T10:00:00Z",
        "_embedded": {
            "tags": [
                {"id": 1, "name": "WhatsApp"},
                {"id": 2, "name": "Solar"}
            ]
        },
        "custom_fields_values": [
            {
                "field_id": "123",
                "field_code": "PHONE",
                "values": [{"value": "5511999999999"}]
            }
        ]
    }


@pytest.mark.asyncio
class TestUpdateKommoLead:
    """Test cases for update_kommo_lead tool"""

    async def test_update_lead_success(self, mock_kommo_service, mock_current_lead):
        """Test successful lead update with all fields"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = [
            {"id": "123", "code": "PHONE", "name": "Telefone"},
            {"id": "456", "code": "EMAIL", "name": "Email"}
        ]
        updated_lead = {**mock_current_lead, "name": "João Silva Updated", "price": 2000}
        mock_kommo_service.update_lead.return_value = updated_lead
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                name="João Silva Updated",
                email="joao.updated@example.com",
                phone="5511888888888",
                price=2000,
                tags_to_add=["Premium"]
            )
        
        # Assert
        assert result["success"] is True
        assert result["lead"]["id"] == 12345
        assert result["lead"]["name"] == "João Silva Updated"
        assert result["lead"]["price"] == 2000
        assert "name" in result["updated_fields"]
        assert "price" in result["updated_fields"]
        assert "email" in result["updated_fields"]
        assert "phone" in result["updated_fields"]
        
        # Verify calls
        mock_kommo_service.get_lead.assert_called_once_with(12345)
        mock_kommo_service.update_lead.assert_called_once()
        mock_kommo_service.add_tag.assert_called_once_with(12345, "Premium")

    async def test_update_lead_not_found(self, mock_kommo_service):
        """Test updating a lead that doesn't exist"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = KommoAPIError(
            status_code=404,
            message="Lead not found"
        )
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=99999,
                name="Non-existent Lead"
            )
        
        # Assert
        assert result["success"] is False
        assert "não encontrado" in result["error"]
        assert result["updated_fields"] == []

    async def test_update_lead_no_changes(self, mock_kommo_service, mock_current_lead):
        """Test update when no fields actually change"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = []
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                name="João Silva",  # Same as current
                price=1000  # Same as current
            )
        
        # Assert
        assert result["success"] is True
        assert result["updated_fields"] == []
        assert "Nenhum campo" in result["message"]
        
        # Should not call update if no changes
        mock_kommo_service.update_lead.assert_not_called()

    async def test_update_lead_custom_fields(self, mock_kommo_service, mock_current_lead):
        """Test updating custom fields"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = []
        mock_kommo_service.update_lead.return_value = mock_current_lead
        
        custom_fields = {
            789: "Casa própria",
            101112: "R$ 800,00"
        }
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                custom_fields=custom_fields
            )
        
        # Assert
        assert result["success"] is True
        assert "custom_field_789" in result["updated_fields"]
        assert "custom_field_101112" in result["updated_fields"]
        
        # Verify custom fields were passed correctly
        call_args = mock_kommo_service.update_lead.call_args
        custom_fields_values = call_args.kwargs["custom_fields_values"]
        assert len(custom_fields_values) == 2

    async def test_update_lead_remove_tags(self, mock_kommo_service, mock_current_lead):
        """Test removing tags from lead"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = []
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                tags_to_remove=["Solar"]
            )
        
        # Assert
        assert result["success"] is True
        assert "tags" in result["updated_fields"]
        
        # Verify tag removal API call
        mock_kommo_service._make_request.assert_called_once()
        call_args = mock_kommo_service._make_request.call_args
        assert call_args[0][0] == "PATCH"
        assert call_args[0][1] == "/leads"
        
        # Check remaining tags
        json_data = call_args.kwargs["json"][0]
        remaining_tags = [tag["name"] for tag in json_data["_embedded"]["tags"]]
        assert "WhatsApp" in remaining_tags
        assert "Solar" not in remaining_tags

    async def test_update_lead_api_error(self, mock_kommo_service, mock_current_lead):
        """Test handling of API errors during update"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = []
        mock_kommo_service.update_lead.side_effect = KommoAPIError(
            status_code=400,
            message="Invalid data"
        )
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                name="New Name"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro da API do Kommo" in result["error"]
        assert result["updated_fields"] == []

    async def test_update_lead_unexpected_error(self, mock_kommo_service):
        """Test handling of unexpected errors"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Connection error")
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                name="New Name"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro inesperado" in result["error"]
        assert result["updated_fields"] == []

    async def test_update_lead_pipeline_stage_change(self, mock_kommo_service, mock_current_lead):
        """Test updating lead through pipeline stages"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = []
        
        # Update to qualified stage (different status_id)
        updated_lead = {**mock_current_lead, "status_id": 2002}
        mock_kommo_service.update_lead.return_value = updated_lead
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                tags_to_add=["Qualificado"]
            )
        
        # Assert
        assert result["success"] is True
        assert result["lead"]["status_id"] == 2002

    async def test_update_lead_edge_cases(self, mock_kommo_service, mock_current_lead):
        """Test edge cases in lead updates"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = []
        mock_kommo_service.update_lead.return_value = mock_current_lead
        
        # Test with None values and empty strings
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                name=None,  # Should be ignored
                email="",  # Should be processed
                price=0,  # Zero price should be valid
                tags_to_add=[],  # Empty list should be handled
                tags_to_remove=None  # None should be handled
            )
        
        # Assert
        assert result["success"] is True
        # Only price and email should be in updated fields
        assert "price" in result["updated_fields"]
        assert "email" in result["updated_fields"]
        assert "name" not in result["updated_fields"]

    async def test_update_lead_rate_limit(self, mock_kommo_service, mock_current_lead):
        """Test handling of rate limit errors"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = []
        mock_kommo_service.update_lead.side_effect = KommoAPIError(
            status_code=429,
            message="Too Many Requests"
        )
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                name="New Name"
            )
        
        # Assert
        assert result["success"] is False
        assert "429" in result["error"] or "Too Many Requests" in result["error"]

    async def test_update_lead_tool_instance(self):
        """Test that UpdateKommoLeadTool is correctly exported"""
        assert UpdateKommoLeadTool == update_kommo_lead
        assert callable(UpdateKommoLeadTool)

    async def test_update_lead_data_integrity(self, mock_kommo_service, mock_current_lead):
        """Test data integrity during updates"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_current_lead
        mock_kommo_service.get_custom_fields.return_value = [
            {"id": "123", "code": "PHONE", "name": "Telefone"}
        ]
        
        # Test phone format preservation
        updated_lead = {**mock_current_lead}
        mock_kommo_service.update_lead.return_value = updated_lead
        
        with patch('agente.tools.kommo.update_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_lead(
                lead_id=12345,
                phone="+55 11 98888-8888"  # Different format
            )
        
        # Assert
        assert result["success"] is True
        assert "phone" in result["updated_fields"]
        
        # Verify phone was passed as-is
        call_args = mock_kommo_service.update_lead.call_args
        custom_fields = call_args.kwargs["custom_fields_values"]
        phone_field = next(f for f in custom_fields if f["field_id"] == "123")
        assert phone_field["values"][0]["value"] == "+55 11 98888-8888"