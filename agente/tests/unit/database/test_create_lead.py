"""
Unit tests for create_lead database tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID, uuid4

from agente.tools.database.create_lead import create_lead, CreateLeadTool
from agente.core.types import Lead, LeadStage, PropertyType


@pytest.fixture
def mock_lead_repository():
    """Mock lead repository for tests"""
    repository = AsyncMock()
    repository.create_lead = AsyncMock()
    repository.get_lead_by_phone = AsyncMock()
    return repository


@pytest.fixture
def sample_lead():
    """Sample lead for testing"""
    return Lead(
        id=uuid4(),
        phone_number="5511999999999",
        name="João Silva",
        email="joao@example.com",
        property_type=PropertyType.HOUSE,
        address="Rua Solar, 123",
        bill_value=500.0,
        consumption_kwh=450,
        current_stage=LeadStage.INITIAL_CONTACT,
        qualification_score=0,
        interested=True,
        kommo_lead_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.mark.asyncio
class TestCreateLead:
    """Test cases for create_lead tool"""

    async def test_create_lead_success_minimal(self, mock_lead_repository):
        """Test successful lead creation with minimal data"""
        # Arrange
        phone = "5511999999999"
        new_lead = Lead(
            id=uuid4(),
            phone_number=phone,
            name=None,
            current_stage=LeadStage.INITIAL_CONTACT,
            qualification_score=0,
            interested=True
        )
        
        mock_lead_repository.create_lead.return_value = new_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(phone=phone)
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == str(new_lead.id)
        assert result["phone"] == phone
        assert result["name"] is None
        assert result["stage"] == "INITIAL_CONTACT"
        assert result["qualified"] is False
        
        # Verify repository call
        mock_lead_repository.create_lead.assert_called_once_with(
            phone=phone,
            name=None
        )

    async def test_create_lead_success_full_data(self, mock_lead_repository, sample_lead):
        """Test successful lead creation with all data"""
        # Arrange
        mock_lead_repository.create_lead.return_value = sample_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(
                phone="5511999999999",
                name="João Silva",
                email="joao@example.com",
                property_type="casa",
                address="Rua Solar, 123",
                bill_value=500.0,
                consumption_kwh=450
            )
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == str(sample_lead.id)
        assert result["phone"] == "5511999999999"
        assert result["name"] == "João Silva"
        assert result["data"]["email"] == "joao@example.com"
        assert result["data"]["property_type"] == "casa"
        assert result["data"]["address"] == "Rua Solar, 123"
        assert result["data"]["bill_value"] == 500.0
        assert result["data"]["consumption_kwh"] == 450
        
        # Verify repository call
        call_args = mock_lead_repository.create_lead.call_args
        assert call_args.kwargs["email"] == "joao@example.com"
        assert call_args.kwargs["property_type"] == PropertyType.HOUSE
        assert call_args.kwargs["address"] == "Rua Solar, 123"
        assert call_args.kwargs["bill_value"] == 500.0
        assert call_args.kwargs["consumption_kwh"] == 450

    async def test_create_lead_with_property_type_enum(self, mock_lead_repository):
        """Test lead creation with different property types"""
        # Arrange
        property_types = [
            ("casa", PropertyType.HOUSE),
            ("apartamento", PropertyType.APARTMENT),
            ("comercial", PropertyType.COMMERCIAL),
            ("rural", PropertyType.RURAL)
        ]
        
        for input_type, expected_enum in property_types:
            new_lead = Lead(
                id=uuid4(),
                phone_number="5511999999999",
                property_type=expected_enum,
                current_stage=LeadStage.INITIAL_CONTACT
            )
            
            mock_lead_repository.create_lead.return_value = new_lead
            
            with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
                # Act
                result = await create_lead(
                    phone="5511999999999",
                    property_type=input_type
                )
            
            # Assert
            assert result["success"] is True
            assert result["data"]["property_type"] == input_type
            
            # Verify enum conversion
            call_args = mock_lead_repository.create_lead.call_args
            assert call_args.kwargs["property_type"] == expected_enum

    async def test_create_lead_invalid_property_type(self, mock_lead_repository):
        """Test lead creation with invalid property type"""
        # Arrange
        new_lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            property_type=None,  # Invalid type ignored
            current_stage=LeadStage.INITIAL_CONTACT
        )
        
        mock_lead_repository.create_lead.return_value = new_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(
                phone="5511999999999",
                property_type="invalid_type"
            )
        
        # Assert
        assert result["success"] is True
        # Invalid property type should be ignored
        call_args = mock_lead_repository.create_lead.call_args
        assert "property_type" not in call_args.kwargs

    async def test_create_lead_missing_phone(self):
        """Test lead creation without required phone number"""
        # Act
        result = await create_lead(
            name="João Silva",
            email="joao@example.com"
        )
        
        # Assert - Should fail due to missing phone
        assert result["success"] is False
        assert "Erro de validação" in result["error"]
        assert result["error_type"] == "validation"

    async def test_create_lead_data_type_conversion(self, mock_lead_repository):
        """Test automatic data type conversion"""
        # Arrange
        new_lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            bill_value=850.5,
            consumption_kwh=750,
            current_stage=LeadStage.INITIAL_CONTACT
        )
        
        mock_lead_repository.create_lead.return_value = new_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act - Pass string values that should be converted
            result = await create_lead(
                phone="5511999999999",
                bill_value="850.50",  # String should be converted to float
                consumption_kwh="750"  # String should be converted to int
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["bill_value"] == 850.5
        assert result["data"]["consumption_kwh"] == 750
        
        # Verify conversion in repository call
        call_args = mock_lead_repository.create_lead.call_args
        assert isinstance(call_args.kwargs["bill_value"], float)
        assert call_args.kwargs["bill_value"] == 850.5
        assert isinstance(call_args.kwargs["consumption_kwh"], int)
        assert call_args.kwargs["consumption_kwh"] == 750

    async def test_create_lead_database_error(self, mock_lead_repository):
        """Test database error during lead creation"""
        # Arrange
        mock_lead_repository.create_lead.side_effect = Exception("Database connection failed")
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(phone="5511999999999")
        
        # Assert
        assert result["success"] is False
        assert "Erro ao criar lead" in result["error"]
        assert result["error_type"] == "database"

    async def test_create_lead_validation_error(self, mock_lead_repository):
        """Test validation error during lead creation"""
        # Arrange
        mock_lead_repository.create_lead.side_effect = ValueError("Invalid phone format")
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(phone="invalid_phone")
        
        # Assert
        assert result["success"] is False
        assert "Erro de validação" in result["error"]
        assert result["error_type"] == "validation"

    async def test_create_lead_with_kommo_integration(self, mock_lead_repository):
        """Test lead creation with Kommo CRM ID"""
        # Arrange
        lead_with_kommo = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            name="João Silva",
            current_stage=LeadStage.INITIAL_CONTACT,
            kommo_lead_id="12345"
        )
        
        mock_lead_repository.create_lead.return_value = lead_with_kommo
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(
                phone="5511999999999",
                name="João Silva"
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["kommo_lead_id"] == "12345"

    async def test_create_lead_with_special_characters(self, mock_lead_repository):
        """Test lead creation with special characters in name"""
        # Arrange
        special_lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            name="José D'Ávila Júnior",
            email="jose.davila@example.com",
            current_stage=LeadStage.INITIAL_CONTACT
        )
        
        mock_lead_repository.create_lead.return_value = special_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(
                phone="5511999999999",
                name="José D'Ávila Júnior",
                email="jose.davila@example.com"
            )
        
        # Assert
        assert result["success"] is True
        assert result["name"] == "José D'Ávila Júnior"

    async def test_create_lead_tool_instance(self):
        """Test that CreateLeadTool is correctly exported"""
        assert CreateLeadTool == create_lead
        assert callable(CreateLeadTool)

    async def test_create_lead_concurrent_creation(self, mock_lead_repository):
        """Test handling concurrent lead creation"""
        # Arrange
        import asyncio
        phone = "5511999999999"
        
        # Simulate different leads being created
        leads = [
            Lead(
                id=uuid4(),
                phone_number=phone,
                name=f"Lead {i}",
                current_stage=LeadStage.INITIAL_CONTACT
            )
            for i in range(3)
        ]
        
        mock_lead_repository.create_lead.side_effect = leads
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act - Simulate concurrent creation
            tasks = [
                create_lead(phone=phone, name=f"Lead {i}")
                for i in range(3)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assert - All should succeed with different IDs
        for i, result in enumerate(results):
            if isinstance(result, dict):
                assert result.get("success") is True
                assert result.get("name") == f"Lead {i}"

    async def test_create_lead_empty_optional_fields(self, mock_lead_repository):
        """Test lead creation with empty optional fields"""
        # Arrange
        new_lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            name="João Silva",
            email=None,
            property_type=None,
            address=None,
            bill_value=None,
            consumption_kwh=None,
            current_stage=LeadStage.INITIAL_CONTACT
        )
        
        mock_lead_repository.create_lead.return_value = new_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(
                phone="5511999999999",
                name="João Silva",
                email="",  # Empty string
                address=""  # Empty string
            )
        
        # Assert
        assert result["success"] is True
        # Empty strings should not be passed to repository
        call_args = mock_lead_repository.create_lead.call_args
        assert "email" not in call_args.kwargs or call_args.kwargs["email"] == ""
        assert "address" not in call_args.kwargs or call_args.kwargs["address"] == ""

    async def test_create_lead_qualification_score_initial(self, mock_lead_repository):
        """Test that new leads start with zero qualification score"""
        # Arrange
        new_lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            current_stage=LeadStage.INITIAL_CONTACT,
            qualification_score=0
        )
        
        mock_lead_repository.create_lead.return_value = new_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(phone="5511999999999")
        
        # Assert
        assert result["success"] is True
        assert result["qualified"] is False  # Score is 0

    async def test_create_lead_solar_specific_fields(self, mock_lead_repository):
        """Test lead creation with solar-specific data"""
        # Arrange
        solar_lead = Lead(
            id=uuid4(),
            phone_number="5511999999999",
            name="João Silva",
            property_type=PropertyType.HOUSE,
            bill_value=750.0,
            consumption_kwh=600,
            current_stage=LeadStage.INITIAL_CONTACT
        )
        
        mock_lead_repository.create_lead.return_value = solar_lead
        
        with patch('agente.tools.database.create_lead.get_lead_repository', return_value=mock_lead_repository):
            # Act
            result = await create_lead(
                phone="5511999999999",
                name="João Silva",
                property_type="casa",
                bill_value=750.0,
                consumption_kwh=600
            )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["bill_value"] == 750.0
        assert result["data"]["consumption_kwh"] == 600
        # These values are important for solar panel sizing calculations