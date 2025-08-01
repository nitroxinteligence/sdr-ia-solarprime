"""
Unit tests for get_lead database tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID, uuid4

from agente.tools.database.get_lead import get_lead, GetLeadTool
from agente.core.types import Lead, LeadStage, PropertyType, LeadQualification, UrgencyLevel, FollowUp, FollowUpType, FollowUpStatus


@pytest.fixture
def mock_lead_repository():
    """Mock lead repository for tests"""
    repository = AsyncMock()
    repository.get_lead_by_id = AsyncMock()
    repository.get_lead_by_phone = AsyncMock()
    repository.get_qualification = AsyncMock()
    return repository


@pytest.fixture
def mock_followup_repository():
    """Mock followup repository for tests"""
    repository = AsyncMock()
    repository.get_pending_follow_ups = AsyncMock()
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
        document="12345678900",
        property_type=PropertyType.HOUSE,
        address="Rua Solar, 123",
        bill_value=500.0,
        consumption_kwh=450,
        current_stage=LeadStage.QUALIFYING,
        qualification_score=75,
        interested=True,
        kommo_lead_id="12345",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def sample_qualification():
    """Sample qualification for testing"""
    return LeadQualification(
        id=uuid4(),
        lead_id=uuid4(),
        has_own_property=True,
        decision_maker=True,
        urgency_level=UrgencyLevel.HIGH,
        objections=["Preço alto", "Precisa consultar cônjuge"],
        solutions_presented=["Solar residencial", "Financiamento"],
        extracted_data={"bill_analysis": {"average": 500}},
        qualification_date=datetime.now()
    )


@pytest.fixture
def sample_follow_ups():
    """Sample follow-ups for testing"""
    return [
        FollowUp(
            id=uuid4(),
            lead_id=uuid4(),
            scheduled_at=datetime.now(),
            type=FollowUpType.REMINDER,
            message="Olá João, tudo bem? Vamos continuar nossa conversa?",
            status=FollowUpStatus.PENDING,
            attempt_number=1
        ),
        FollowUp(
            id=uuid4(),
            lead_id=uuid4(),
            scheduled_at=datetime.now(),
            type=FollowUpType.CHECK_IN,
            message="João, ainda tem interesse em economizar na conta de luz?",
            status=FollowUpStatus.PENDING,
            attempt_number=2
        )
    ]


@pytest.mark.asyncio
class TestGetLead:
    """Test cases for get_lead tool"""

    async def test_get_lead_by_id_success(self, mock_lead_repository, sample_lead):
        """Test successful lead retrieval by ID"""
        # Arrange
        lead_id = str(sample_lead.id)
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await get_lead(lead_id=lead_id)
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == lead_id
        assert result["data"]["name"] == "João Silva"
        assert result["data"]["phone"] == "5511999999999"
        assert result["data"]["email"] == "joao@example.com"
        assert result["data"]["property_type"] == "casa"
        assert result["data"]["stage"] == "QUALIFYING"
        assert result["data"]["qualification_score"] == 75
        assert result["data"]["interested"] is True
        
        # Verify repository calls
        mock_lead_repository.get_lead_by_id.assert_called_once_with(UUID(lead_id))

    async def test_get_lead_by_phone_success(self, mock_lead_repository, sample_lead):
        """Test successful lead retrieval by phone"""
        # Arrange
        phone = "5511999999999"
        mock_lead_repository.get_lead_by_phone.return_value = sample_lead
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.get_lead.format_phone_number', return_value=phone):
                # Act
                result = await get_lead(phone=phone)
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == str(sample_lead.id)
        assert result["data"]["phone"] == phone
        
        # Verify repository calls
        mock_lead_repository.get_lead_by_phone.assert_called_once_with(phone)

    async def test_get_lead_with_qualification(self, mock_lead_repository, sample_lead, sample_qualification):
        """Test lead retrieval with qualification data"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.get_qualification.return_value = sample_qualification
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await get_lead(lead_id=str(sample_lead.id), include_qualification=True)
        
        # Assert
        assert result["success"] is True
        assert "qualification" in result
        assert result["qualification"]["has_own_property"] is True
        assert result["qualification"]["decision_maker"] is True
        assert result["qualification"]["urgency_level"] == "alta"
        assert len(result["qualification"]["objections"]) == 2
        assert len(result["qualification"]["solutions_presented"]) == 2

    async def test_get_lead_with_follow_ups(self, mock_lead_repository, mock_followup_repository, sample_lead, sample_follow_ups):
        """Test lead retrieval with follow-up data"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.get_pending_follow_ups.return_value = sample_follow_ups
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.get_lead.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await get_lead(lead_id=str(sample_lead.id), include_follow_ups=True)
        
        # Assert
        assert result["success"] is True
        assert "follow_ups" in result
        assert len(result["follow_ups"]) == 2
        assert result["follow_ups"][0]["type"] == "reminder"
        assert result["follow_ups"][0]["attempt_number"] == 1
        assert result["follow_ups"][1]["type"] == "check_in"
        assert result["follow_ups"][1]["attempt_number"] == 2

    async def test_get_lead_not_found_by_id(self, mock_lead_repository):
        """Test lead not found by ID"""
        # Arrange
        lead_id = str(uuid4())
        mock_lead_repository.get_lead_by_id.return_value = None
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await get_lead(lead_id=lead_id)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Lead não encontrado"
        assert result["error_type"] == "not_found"
        assert result["searched_by"] == "id"
        assert result["search_value"] == lead_id

    async def test_get_lead_not_found_by_phone(self, mock_lead_repository):
        """Test lead not found by phone"""
        # Arrange
        phone = "5511999999999"
        mock_lead_repository.get_lead_by_phone.return_value = None
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.get_lead.format_phone_number', return_value=phone):
                # Act
                result = await get_lead(phone=phone)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Lead não encontrado"
        assert result["error_type"] == "not_found"
        assert result["searched_by"] == "phone"
        assert result["search_value"] == phone

    async def test_get_lead_invalid_id(self, mock_lead_repository):
        """Test with invalid UUID format"""
        # Arrange
        invalid_id = "not-a-uuid"
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await get_lead(lead_id=invalid_id)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "ID do lead inválido"
        assert result["error_type"] == "validation"
        
        # Verify repository was not called
        mock_lead_repository.get_lead_by_id.assert_not_called()

    async def test_get_lead_missing_parameters(self):
        """Test with no parameters provided"""
        # Act
        result = await get_lead()
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "É necessário fornecer lead_id ou phone"
        assert result["error_type"] == "validation"

    async def test_get_lead_database_error(self, mock_lead_repository):
        """Test database connection failure"""
        # Arrange
        mock_lead_repository.get_lead_by_id.side_effect = Exception("Database connection failed")
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await get_lead(lead_id=str(uuid4()))
        
        # Assert
        assert result["success"] is False
        assert "Erro ao buscar lead" in result["error"]
        assert result["error_type"] == "database"

    async def test_get_lead_qualification_error_continues(self, mock_lead_repository, sample_lead):
        """Test that qualification errors don't fail the entire operation"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_lead_repository.get_qualification.side_effect = Exception("Qualification error")
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await get_lead(lead_id=str(sample_lead.id), include_qualification=True)
        
        # Assert
        assert result["success"] is True
        assert result["qualification"] is None

    async def test_get_lead_followup_error_continues(self, mock_lead_repository, mock_followup_repository, sample_lead):
        """Test that follow-up errors don't fail the entire operation"""
        # Arrange
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        mock_followup_repository.get_pending_follow_ups.side_effect = Exception("Follow-up error")
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.get_lead.get_followup_repository', return_value=mock_followup_repository):
                # Act
                result = await get_lead(lead_id=str(sample_lead.id), include_follow_ups=True)
        
        # Assert
        assert result["success"] is True
        assert result["follow_ups"] == []

    async def test_get_lead_tool_instance(self):
        """Test that GetLeadTool is correctly exported"""
        assert GetLeadTool == get_lead
        assert callable(GetLeadTool)

    async def test_get_lead_phone_formatting(self, mock_lead_repository):
        """Test phone number formatting"""
        # Arrange
        raw_phone = "11 9 9999-9999"
        formatted_phone = "5511999999999"
        mock_lead_repository.get_lead_by_phone.return_value = None
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            with patch('agente.tools.database.get_lead.format_phone_number', return_value=formatted_phone) as mock_format:
                # Act
                result = await get_lead(phone=raw_phone)
        
        # Assert
        mock_format.assert_called_once_with(raw_phone)
        mock_lead_repository.get_lead_by_phone.assert_called_once_with(formatted_phone)

    async def test_get_lead_with_null_optional_fields(self, mock_lead_repository):
        """Test handling of null optional fields"""
        # Arrange
        lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            name=None,  # null name
            email=None,  # null email
            property_type=None,  # null property type
            current_stage=LeadStage.INITIAL_CONTACT,
            qualification_score=0,
            interested=True
        )
        mock_lead_repository.get_lead_by_id.return_value = lead
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await get_lead(lead_id=str(lead.id))
        
        # Assert
        assert result["success"] is True
        assert result["data"]["name"] is None
        assert result["data"]["email"] is None
        assert result["data"]["property_type"] is None

    async def test_get_lead_concurrent_access(self, mock_lead_repository, sample_lead):
        """Test concurrent access handling"""
        # Arrange
        import asyncio
        mock_lead_repository.get_lead_by_id.return_value = sample_lead
        
        with patch('agente.tools.database.get_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act - Simulate concurrent access
            tasks = [
                get_lead(lead_id=str(sample_lead.id)),
                get_lead(lead_id=str(sample_lead.id)),
                get_lead(lead_id=str(sample_lead.id))
            ]
            results = await asyncio.gather(*tasks)
        
        # Assert - All should succeed
        for result in results:
            assert result["success"] is True
            assert result["lead_id"] == str(sample_lead.id)