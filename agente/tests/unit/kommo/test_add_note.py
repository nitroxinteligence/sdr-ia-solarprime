"""
Unit tests for Kommo add_note tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from freezegun import freeze_time

from agente.tools.kommo.add_note import (
    add_kommo_note,
    add_qualification_note,
    add_interaction_log,
    AddKommoNoteTool,
    AddQualificationNoteTool,
    AddInteractionLogTool
)
from agente.services.kommo_service import KommoAPIError


@pytest.fixture
def mock_kommo_service():
    """Mock Kommo service for tests"""
    service = AsyncMock()
    service.get_lead = AsyncMock()
    service.add_note = AsyncMock()
    return service


@pytest.fixture
def mock_lead():
    """Mock lead data"""
    return {
        "id": 12345,
        "name": "João Silva",
        "status_id": 1001,
        "pipeline_id": 2001
    }


@pytest.mark.asyncio
class TestAddKommoNote:
    """Test cases for add_kommo_note tool"""

    @freeze_time("2024-01-10 14:30:00")
    async def test_add_note_success(self, mock_kommo_service, mock_lead):
        """Test successful note addition"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {
            "id": 67890,
            "created_at": "2024-01-10T14:30:00Z"
        }
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_kommo_note(
                lead_id=12345,
                text="Conversa inicial sobre energia solar"
            )
        
        # Assert
        assert result["success"] is True
        assert result["note_id"] == 67890
        assert result["lead_id"] == 12345
        assert result["lead_name"] == "João Silva"
        assert result["text"] == "Conversa inicial sobre energia solar"
        
        # Verify note was added with timestamp
        mock_kommo_service.add_note.assert_called_once()
        call_args = mock_kommo_service.add_note.call_args
        assert call_args[0][0] == 12345
        assert "[10/01/2024 14:30]" in call_args[0][1]
        assert "Conversa inicial sobre energia solar" in call_args[0][1]

    async def test_add_note_empty_text(self):
        """Test adding note with empty text"""
        # Act
        result = await add_kommo_note(
            lead_id=12345,
            text=""
        )
        
        # Assert
        assert result["success"] is False
        assert "vazio" in result["error"]
        assert result["note_id"] is None

    async def test_add_note_lead_not_found(self, mock_kommo_service):
        """Test adding note when lead doesn't exist"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = KommoAPIError(
            status_code=404,
            message="Lead not found"
        )
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_kommo_note(
                lead_id=99999,
                text="Test note"
            )
        
        # Assert
        assert result["success"] is False
        assert "não encontrado" in result["error"]
        assert result["note_id"] is None

    async def test_add_note_api_error(self, mock_kommo_service, mock_lead):
        """Test API error during note addition"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.side_effect = KommoAPIError(
            status_code=400,
            message="Invalid request"
        )
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_kommo_note(
                lead_id=12345,
                text="Test note"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro da API do Kommo" in result["error"]

    async def test_add_note_unexpected_error(self, mock_kommo_service):
        """Test unexpected error handling"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Connection error")
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_kommo_note(
                lead_id=12345,
                text="Test note"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro inesperado" in result["error"]


@pytest.mark.asyncio
class TestAddQualificationNote:
    """Test cases for add_qualification_note tool"""

    @freeze_time("2024-01-10 14:30:00")
    async def test_add_qualification_note_complete(self, mock_kommo_service, mock_lead):
        """Test adding complete qualification note"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {
            "id": 67890,
            "created_at": "2024-01-10T14:30:00Z"
        }
        
        qualification_data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "phone": "5511999999999",
            "property_type": "Casa",
            "address": "Rua Solar, 123",
            "bill_value": 500.50,
            "consumption_kwh": 400,
            "urgency": "alta",
            "decision_maker": True,
            "has_discount": False,
            "interested": True,
            "objections": ["Preço", "Prazo de instalação"]
        }
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_qualification_note(
                lead_id=12345,
                qualification_data=qualification_data,
                score=85
            )
        
        # Assert
        assert result["success"] is True
        assert result["qualification_score"] == 85
        
        # Verify note content
        call_args = mock_kommo_service.add_note.call_args
        note_text = call_args[0][1]
        
        # Check formatting
        assert "📋 QUALIFICAÇÃO DO LEAD" in note_text
        assert "🟢 Score: 85/100" in note_text  # High score emoji
        assert "👤 Nome: João Silva" in note_text
        assert "💰 Valor da Conta: R$ 500,50" in note_text
        assert "⚡ Consumo (kWh): 400 kWh/mês" in note_text
        assert "🚨 Urgência: ALTA" in note_text
        assert "✅ Tomador de Decisão: Sim" in note_text
        assert "💳 Possui Desconto: Não" in note_text
        assert "❌ Objeções: Preço, Prazo de instalação" in note_text

    async def test_add_qualification_note_medium_score(self, mock_kommo_service, mock_lead):
        """Test qualification note with medium score"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {"id": 67890}
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_qualification_note(
                lead_id=12345,
                qualification_data={"name": "Test"},
                score=55
            )
        
        # Assert
        assert result["success"] is True
        
        # Check medium score emoji
        call_args = mock_kommo_service.add_note.call_args
        note_text = call_args[0][1]
        assert "🟡 Score: 55/100" in note_text

    async def test_add_qualification_note_low_score(self, mock_kommo_service, mock_lead):
        """Test qualification note with low score"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {"id": 67890}
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_qualification_note(
                lead_id=12345,
                qualification_data={"name": "Test"},
                score=25
            )
        
        # Assert
        assert result["success"] is True
        
        # Check low score emoji
        call_args = mock_kommo_service.add_note.call_args
        note_text = call_args[0][1]
        assert "🔴 Score: 25/100" in note_text

    async def test_add_qualification_note_partial_data(self, mock_kommo_service, mock_lead):
        """Test qualification note with partial data"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {"id": 67890}
        
        qualification_data = {
            "name": "João Silva",
            "phone": "5511999999999",
            "interested": True,
            "objections": []  # Empty list
        }
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_qualification_note(
                lead_id=12345,
                qualification_data=qualification_data
            )
        
        # Assert
        assert result["success"] is True
        
        # Verify only included fields are in note
        call_args = mock_kommo_service.add_note.call_args
        note_text = call_args[0][1]
        assert "👤 Nome: João Silva" in note_text
        assert "📱 Telefone: 5511999999999" in note_text
        assert "💚 Interesse: Sim" in note_text
        assert "❌ Objeções: Nenhuma" in note_text
        
        # Fields not included shouldn't appear
        assert "📧 Email:" not in note_text
        assert "🏠 Tipo de Imóvel:" not in note_text

    async def test_add_qualification_note_error(self, mock_kommo_service):
        """Test error handling in qualification note"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Test error")
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_qualification_note(
                lead_id=12345,
                qualification_data={"name": "Test"}
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao adicionar nota de qualificação" in result["error"]


@pytest.mark.asyncio
class TestAddInteractionLog:
    """Test cases for add_interaction_log tool"""

    async def test_add_interaction_log_call(self, mock_kommo_service, mock_lead):
        """Test adding call interaction log"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {"id": 67890}
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_interaction_log(
                lead_id=12345,
                interaction_type="call",
                details="Ligação inicial, cliente interessado em saber mais",
                sentiment="positive"
            )
        
        # Assert
        assert result["success"] is True
        assert result["interaction_type"] == "call"
        assert result["sentiment"] == "positive"
        
        # Verify note format
        call_args = mock_kommo_service.add_note.call_args
        note_text = call_args[0][1]
        assert "📞 CALL 😊" in note_text
        assert "Ligação inicial, cliente interessado" in note_text

    async def test_add_interaction_log_types(self, mock_kommo_service, mock_lead):
        """Test different interaction types"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {"id": 67890}
        
        interaction_types = {
            "message": "💬",
            "whatsapp": "📱",
            "meeting": "🤝",
            "email": "📧",
            "task": "📋",
            "custom": "📝"  # Default emoji for unknown types
        }
        
        for interaction_type, expected_emoji in interaction_types.items():
            with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
                # Act
                result = await add_interaction_log(
                    lead_id=12345,
                    interaction_type=interaction_type,
                    details="Test interaction"
                )
            
            # Assert
            assert result["success"] is True
            
            # Verify emoji
            call_args = mock_kommo_service.add_note.call_args
            note_text = call_args[0][1]
            assert expected_emoji in note_text

    async def test_add_interaction_log_sentiments(self, mock_kommo_service, mock_lead):
        """Test different sentiment values"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {"id": 67890}
        
        sentiments = {
            "positive": "😊",
            "neutral": "😐",
            "negative": "😟"
        }
        
        for sentiment, expected_emoji in sentiments.items():
            with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
                # Act
                result = await add_interaction_log(
                    lead_id=12345,
                    interaction_type="message",
                    details="Test",
                    sentiment=sentiment
                )
            
            # Assert
            assert result["success"] is True
            
            # Verify sentiment emoji
            call_args = mock_kommo_service.add_note.call_args
            note_text = call_args[0][1]
            assert expected_emoji in note_text

    async def test_add_interaction_log_no_sentiment(self, mock_kommo_service, mock_lead):
        """Test interaction log without sentiment"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.add_note.return_value = {"id": 67890}
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_interaction_log(
                lead_id=12345,
                interaction_type="email",
                details="Email enviado com proposta"
            )
        
        # Assert
        assert result["success"] is True
        
        # Verify no sentiment emoji
        call_args = mock_kommo_service.add_note.call_args
        note_text = call_args[0][1]
        assert "📧 EMAIL" in note_text
        assert "😊" not in note_text
        assert "😐" not in note_text
        assert "😟" not in note_text

    async def test_add_interaction_log_error(self, mock_kommo_service):
        """Test error handling in interaction log"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Test error")
        
        with patch('agente.tools.kommo.add_note.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await add_interaction_log(
                lead_id=12345,
                interaction_type="call",
                details="Test"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro ao adicionar log de interação" in result["error"]

    async def test_tool_instances(self):
        """Test that all tool instances are correctly exported"""
        assert AddKommoNoteTool == add_kommo_note
        assert AddQualificationNoteTool == add_qualification_note
        assert AddInteractionLogTool == add_interaction_log
        assert callable(AddKommoNoteTool)
        assert callable(AddQualificationNoteTool)
        assert callable(AddInteractionLogTool)