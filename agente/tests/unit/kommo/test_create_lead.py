"""
Unit tests for Kommo create_lead tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agente.tools.kommo.create_lead import create_kommo_lead, CreateKommoLeadTool
from agente.services.kommo_service import KommoAPIError


@pytest.fixture
def mock_kommo_service():
    """Mock Kommo service for tests"""
    service = AsyncMock()
    service.get_lead_by_phone = AsyncMock()
    service.get_custom_fields = AsyncMock()
    service.create_lead = AsyncMock()
    service.add_tag = AsyncMock()
    service.update_lead_stage = AsyncMock()
    return service


@pytest.mark.asyncio
class TestCreateKommoLead:
    """Test cases for create_kommo_lead tool"""

    async def test_create_lead_success(self, mock_kommo_service):
        """Test successful lead creation"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None  # No existing lead
        mock_kommo_service.get_custom_fields.return_value = [
            {"id": "123", "code": "EMAIL", "name": "Email"}
        ]
        mock_kommo_service.create_lead.return_value = {
            "id": 12345,
            "name": "João Silva",
            "status_id": 1001,
            "pipeline_id": 2001,
            "created_at": "2024-01-10T10:00:00Z"
        }
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999",
                email="joao@example.com",
                tags=["Solar", "WhatsApp"]
            )
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == 12345
        assert result["lead"]["name"] == "João Silva"
        assert result["lead"]["phone"] == "5511999999999"
        assert result["lead"]["email"] == "joao@example.com"
        assert result["lead"]["tags"] == ["Solar", "WhatsApp"]
        
        # Verify calls
        mock_kommo_service.get_lead_by_phone.assert_called_once_with("5511999999999")
        mock_kommo_service.create_lead.assert_called_once()
        assert mock_kommo_service.add_tag.call_count == 2

    async def test_create_lead_already_exists(self, mock_kommo_service):
        """Test lead creation when lead already exists"""
        # Arrange
        existing_lead = {
            "id": 99999,
            "name": "João Silva",
            "phone": "5511999999999"
        }
        mock_kommo_service.get_lead_by_phone.return_value = existing_lead
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999"
            )
        
        # Assert
        assert result["success"] is False
        assert "já existe" in result["error"]
        assert result["lead_id"] == 99999
        assert result["already_exists"] is True
        
        # Verify no lead was created
        mock_kommo_service.create_lead.assert_not_called()

    async def test_create_lead_missing_required_fields(self):
        """Test lead creation with missing required fields"""
        # Test missing name
        result = await create_kommo_lead(
            name="",
            phone="5511999999999"
        )
        assert result["success"] is False
        assert "obrigatórios" in result["error"]
        
        # Test missing phone
        result = await create_kommo_lead(
            name="João Silva",
            phone=""
        )
        assert result["success"] is False
        assert "obrigatórios" in result["error"]

    async def test_create_lead_with_custom_fields(self, mock_kommo_service):
        """Test lead creation with custom fields"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        mock_kommo_service.create_lead.return_value = {
            "id": 12345,
            "name": "João Silva"
        }
        
        custom_fields = {
            "456": "Casa própria",
            "789": "R$ 500,00"
        }
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999",
                custom_fields=custom_fields
            )
        
        # Assert
        assert result["success"] is True
        
        # Verify custom fields were passed
        call_args = mock_kommo_service.create_lead.call_args
        assert call_args.kwargs["custom_fields"] == custom_fields

    async def test_create_lead_with_initial_stage(self, mock_kommo_service):
        """Test lead creation with initial stage different from default"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        mock_kommo_service.create_lead.return_value = {
            "id": 12345,
            "name": "João Silva"
        }
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999",
                initial_stage="QUALIFICADO"
            )
        
        # Assert
        assert result["success"] is True
        
        # Verify stage update was called
        mock_kommo_service.update_lead_stage.assert_called_once_with(
            12345, "qualificado"
        )

    async def test_create_lead_api_error(self, mock_kommo_service):
        """Test lead creation with API error"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        mock_kommo_service.create_lead.side_effect = KommoAPIError(
            status_code=400,
            message="Invalid data",
            response_data={"error": "Bad request"}
        )
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro da API do Kommo" in result["error"]
        assert result["lead_id"] is None

    async def test_create_lead_unexpected_error(self, mock_kommo_service):
        """Test lead creation with unexpected error"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.side_effect = Exception("Connection error")
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro inesperado" in result["error"]
        assert result["lead_id"] is None

    async def test_create_lead_tag_error_continues(self, mock_kommo_service):
        """Test that tag errors don't fail the entire operation"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        mock_kommo_service.create_lead.return_value = {
            "id": 12345,
            "name": "João Silva"
        }
        mock_kommo_service.add_tag.side_effect = Exception("Tag error")
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999",
                tags=["Solar"]
            )
        
        # Assert - Lead creation should still succeed
        assert result["success"] is True
        assert result["lead_id"] == 12345

    async def test_create_lead_invalid_stage(self, mock_kommo_service):
        """Test lead creation with invalid initial stage"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        mock_kommo_service.create_lead.return_value = {
            "id": 12345,
            "name": "João Silva"
        }
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999",
                initial_stage="INVALID_STAGE"
            )
        
        # Assert
        assert result["success"] is True  # Lead still created
        # Stage update should not be called for invalid stage
        mock_kommo_service.update_lead_stage.assert_not_called()

    async def test_create_lead_tool_instance(self):
        """Test that CreateKommoLeadTool is correctly exported"""
        assert CreateKommoLeadTool == create_kommo_lead
        assert callable(CreateKommoLeadTool)

    async def test_create_lead_with_qualification_score(self, mock_kommo_service):
        """Test creating a lead with different qualification scores"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        mock_kommo_service.create_lead.return_value = {
            "id": 12345,
            "name": "João Silva"
        }
        
        # High qualification score lead
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999",
                tags=["Alta Qualificação", "Urgente"],
                initial_stage="QUALIFICADO"
            )
        
        assert result["success"] is True
        mock_kommo_service.update_lead_stage.assert_called_with(12345, "qualificado")

    async def test_create_lead_rate_limit_handling(self, mock_kommo_service):
        """Test handling of API rate limits"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.return_value = None
        mock_kommo_service.create_lead.side_effect = KommoAPIError(
            status_code=429,
            message="Too Many Requests",
            response_data={"error": "Rate limit exceeded"}
        )
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999"
            )
        
        # Assert
        assert result["success"] is False
        assert "429" in result["error"] or "Rate limit" in result["error"]

    async def test_create_lead_authentication_error(self, mock_kommo_service):
        """Test handling of authentication errors"""
        # Arrange
        mock_kommo_service.get_lead_by_phone.side_effect = KommoAPIError(
            status_code=401,
            message="Unauthorized",
            response_data={"error": "Invalid token"}
        )
        
        with patch('agente.tools.kommo.create_lead.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await create_kommo_lead(
                name="João Silva",
                phone="5511999999999"
            )
        
        # Assert
        assert result["success"] is False
        assert "401" in result["error"] or "Unauthorized" in result["error"]