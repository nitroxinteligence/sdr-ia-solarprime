"""
Unit tests for update_lead database tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID, uuid4

from agente.tools.database.update_lead import update_lead, UpdateLeadTool
from agente.core.types import Lead, LeadStage, PropertyType, UrgencyLevel


@pytest.fixture
def mock_lead_repository():
    """Mock lead repository for tests"""
    repository = AsyncMock()
    repository.get_lead_by_id = AsyncMock()
    repository.get_lead_by_phone = AsyncMock()
    repository.update_lead = AsyncMock()
    repository.update_qualification = AsyncMock()
    return repository


@pytest.fixture
def sample_lead():
    """Sample lead for testing"""
    lead_id = uuid4()
    return Lead(
        id=lead_id,
        phone_number="5511999999999",
        name="João Silva",
        email="joao@example.com",
        property_type=PropertyType.HOUSE,
        current_stage=LeadStage.QUALIFYING,
        qualification_score=50,
        interested=True,
        bill_value=300.0,
        consumption_kwh=250
    )


@pytest.mark.asyncio
class TestUpdateLead:
    """Test cases for update_lead tool"""

    async def test_update_lead_by_id_success(self, mock_lead_repository, sample_lead):
        """Test successful lead update by ID"""
        # Arrange
        lead_id = str(sample_lead.id)
        updated_lead = Lead(
            **sample_lead.dict(),
            name="João Silva Santos",
            email="joao.santos@example.com",
            qualification_score=85
        )
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = updated_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=lead_id,
                name="João Silva Santos",
                email="joao.santos@example.com",
                qualification_score=85
            )
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == lead_id
        assert result["updated_fields"] == ["name", "email", "qualification_score"]
        assert result["data"]["name"] == "João Silva Santos"
        assert result["data"]["qualification_score"] == 85
        
        # Verify repository calls
        mock_lead_repository.get_lead_by_id.assert_called_once_with(UUID(lead_id))
        mock_lead_repository.update_lead.assert_called_once()

    async def test_update_lead_by_phone_success(self, mock_lead_repository, sample_lead):
        """Test successful lead update by phone"""
        # Arrange
        phone = "5511999999999"
        updated_lead = Lead(**sample_lead.dict(), interested=False)
        
        mock_lead_repository.get_lead_by_phone.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = updated_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                phone=phone,
                interested=False
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["interested"] is False
        
        # Verify repository calls
        mock_lead_repository.get_lead_by_phone.assert_called_once_with(phone)

    async def test_update_lead_stage_transition(self, mock_lead_repository, sample_lead):
        """Test lead stage transition"""
        # Arrange
        updated_lead = Lead(**sample_lead.dict(), current_stage=LeadStage.QUALIFIED)
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = updated_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                stage="QUALIFIED"
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["stage"] == "QUALIFIED"
        
        # Verify stage was updated
        update_data = mock_lead_repository.update_lead.call_args[0][1]
        assert update_data["current_stage"] == LeadStage.QUALIFIED

    async def test_update_lead_property_type(self, mock_lead_repository, sample_lead):
        """Test updating property type"""
        # Arrange
        updated_lead = Lead(**sample_lead.dict(), property_type=PropertyType.COMMERCIAL)
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = updated_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                property_type="comercial"
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["property_type"] == "comercial"

    async def test_update_lead_with_qualification(self, mock_lead_repository, sample_lead):
        """Test updating lead with qualification data"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = sample_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                solutions_presented=["Solar residencial", "Financiamento"],
                urgency_level="alta",
                objections=["Preço alto"]
            )
        
        # Assert
        assert result["success"] is True
        assert result["qualification_updated"] is True
        
        # Verify qualification update was called
        mock_lead_repository.update_qualification.assert_called_once()
        qual_data = mock_lead_repository.update_qualification.call_args[0][1]
        assert qual_data["solutions_presented"] == ["Solar residencial", "Financiamento"]
        assert qual_data["urgency_level"] == UrgencyLevel.HIGH
        assert qual_data["objections"] == ["Preço alto"]

    async def test_update_lead_bill_value_and_consumption(self, mock_lead_repository, sample_lead):
        """Test updating bill value and consumption"""
        # Arrange
        updated_lead = Lead(**sample_lead.dict(), bill_value=750.0, consumption_kwh=600)
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = updated_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                bill_value=750.0,
                consumption_kwh=600
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["bill_value"] == 750.0
        assert result["data"]["consumption_kwh"] == 600

    async def test_update_lead_not_found(self, mock_lead_repository):
        """Test updating non-existent lead"""
        # Arrange
        lead_id = str(uuid4())
        mock_lead_repository.get_lead_by_id.return_value = None
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(lead_id=lead_id, name="New Name")
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Lead não encontrado"
        assert result["error_type"] == "not_found"

    async def test_update_lead_missing_parameters(self):
        """Test with no identification parameters"""
        # Act
        result = await update_lead(name="New Name")
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "É necessário fornecer lead_id ou phone"
        assert result["error_type"] == "validation"

    async def test_update_lead_invalid_stage(self, mock_lead_repository, sample_lead):
        """Test with invalid stage value"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = sample_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                stage="INVALID_STAGE"
            )
        
        # Assert
        assert result["success"] is True  # Should still succeed but ignore invalid stage
        # Invalid stage should not be in update data
        update_data = mock_lead_repository.update_lead.call_args[0][1]
        assert "current_stage" not in update_data

    async def test_update_lead_invalid_property_type(self, mock_lead_repository, sample_lead):
        """Test with invalid property type"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = sample_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                property_type="invalid_type"
            )
        
        # Assert
        assert result["success"] is True  # Should still succeed but ignore invalid type
        # Invalid property type should not be in update data
        update_data = mock_lead_repository.update_lead.call_args[0][1]
        assert "property_type" not in update_data

    async def test_update_lead_invalid_urgency_level(self, mock_lead_repository, sample_lead):
        """Test with invalid urgency level"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = sample_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                urgency_level="invalid_urgency"
            )
        
        # Assert
        assert result["success"] is True
        # Invalid urgency should not cause qualification update
        qual_data = mock_lead_repository.update_qualification.call_args
        if qual_data:
            assert "urgency_level" not in qual_data[0][1]

    async def test_update_lead_database_error(self, mock_lead_repository, sample_lead):
        """Test database error during update"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.side_effect = Exception("Database error")
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                name="New Name"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao atualizar lead" in result["error"]
        assert result["error_type"] == "database"

    async def test_update_lead_validation_error(self, mock_lead_repository, sample_lead):
        """Test validation error during update"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.side_effect = ValueError("Invalid data")
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                qualification_score=150  # Invalid score > 100
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro de validação" in result["error"]
        assert result["error_type"] == "validation"

    async def test_update_lead_partial_update(self, mock_lead_repository, sample_lead):
        """Test partial update with only some fields"""
        # Arrange
        updated_lead = Lead(**sample_lead.dict(), name="João Santos")
        
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = updated_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await update_lead(
                lead_id=str(sample_lead.id),
                name="João Santos"
            )
        
        # Assert
        assert result["success"] is True
        assert len(result["updated_fields"]) == 1
        assert "name" in result["updated_fields"]

    async def test_update_lead_tool_instance(self):
        """Test that UpdateLeadTool is correctly exported"""
        assert UpdateLeadTool == update_lead
        assert callable(UpdateLeadTool)

    async def test_update_lead_concurrent_updates(self, mock_lead_repository, sample_lead):
        """Test handling concurrent updates"""
        # Arrange
        import asyncio
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = sample_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act - Simulate concurrent updates
            tasks = [
                update_lead(lead_id=str(sample_lead.id), qualification_score=60),
                update_lead(lead_id=str(sample_lead.id), qualification_score=70),
                update_lead(lead_id=str(sample_lead.id), qualification_score=80)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assert - At least one should succeed
        successes = [r for r in results if isinstance(r, dict) and r.get("success")]
        assert len(successes) >= 1

    async def test_update_lead_data_type_conversion(self, mock_lead_repository, sample_lead):
        """Test automatic data type conversion"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.update_lead.return_value = sample_lead
        
        with patch('agente.tools.database.update_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act - Pass string values that should be converted
            result = await update_lead(
                lead_id=str(sample_lead.id),
                bill_value="850.50",  # String should be converted to float
                consumption_kwh="750",  # String should be converted to int
                qualification_score="95"  # String should be converted to int
            )
        
        # Assert
        assert result["success"] is True
        update_data = mock_lead_repository.update_lead.call_args[0][1]
        assert isinstance(update_data["bill_value"], float)
        assert update_data["bill_value"] == 850.5
        assert isinstance(update_data["consumption_kwh"], int)
        assert update_data["consumption_kwh"] == 750
        assert isinstance(update_data["qualification_score"], int)
        assert update_data["qualification_score"] == 95