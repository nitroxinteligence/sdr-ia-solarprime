"""
Unit tests for Kommo update_stage tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agente.tools.kommo.update_stage import (
    update_kommo_stage,
    get_lead_stage,
    UpdateKommoStageTool,
    GetLeadStageTool
)
from agente.services.kommo_service import KommoAPIError
from agente.core.config import KOMMO_STAGES


@pytest.fixture
def mock_kommo_service():
    """Mock Kommo service for tests"""
    service = AsyncMock()
    service.get_lead = AsyncMock()
    service.get_pipelines = AsyncMock()
    service.update_lead_stage = AsyncMock()
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


@pytest.fixture
def mock_pipelines():
    """Mock pipelines data"""
    return [
        {
            "id": 2001,
            "name": "Pipeline Principal",
            "_embedded": {
                "statuses": [
                    {"id": 1001, "name": "novo lead"},
                    {"id": 1002, "name": "em negociação"},
                    {"id": 1003, "name": "em qualificação"},
                    {"id": 1004, "name": "qualificado"},
                    {"id": 1005, "name": "reunião agendada"},
                    {"id": 1006, "name": "não interessado"}
                ]
            }
        }
    ]


@pytest.mark.asyncio
class TestUpdateKommoStage:
    """Test cases for update_kommo_stage tool"""

    async def test_update_stage_success(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test successful stage update"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        updated_lead = {**mock_lead, "status_id": 1004}
        mock_kommo_service.update_lead_stage.return_value = updated_lead
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="QUALIFICADO",
                add_note="Lead qualificado com sucesso"
            )
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == 12345
        assert result["old_stage"] == "novo lead"
        assert result["new_stage"] == "qualificado"
        assert result["pipeline_id"] == 2001
        
        # Verify calls
        mock_kommo_service.update_lead_stage.assert_called_once_with(12345, "qualificado")
        mock_kommo_service.add_note.assert_called_once()
        note_text = mock_kommo_service.add_note.call_args[0][1]
        assert "Lead movido para estágio 'qualificado'" in note_text
        assert "Lead qualificado com sucesso" in note_text

    async def test_update_stage_by_value(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test updating stage using value instead of key"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        mock_kommo_service.update_lead_stage.return_value = mock_lead
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="em negociação"  # Using value instead of key
            )
        
        # Assert
        assert result["success"] is True
        mock_kommo_service.update_lead_stage.assert_called_once_with(12345, "em negociação")

    async def test_update_stage_invalid_stage(self):
        """Test updating with invalid stage name"""
        # Act
        result = await update_kommo_stage(
            lead_id=12345,
            stage_name="INVALID_STAGE"
        )
        
        # Assert
        assert result["success"] is False
        assert "Estágio inválido" in result["error"]
        assert "NOVO_LEAD" in result["error"]  # Should list valid options

    async def test_update_stage_lead_not_found(self, mock_kommo_service):
        """Test updating stage when lead doesn't exist"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = KommoAPIError(
            status_code=404,
            message="Lead not found"
        )
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=99999,
                stage_name="QUALIFICADO"
            )
        
        # Assert
        assert result["success"] is False
        assert "não encontrado" in result["error"]
        assert result["lead_id"] == 99999

    async def test_update_stage_already_in_stage(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test updating when lead is already in target stage"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="NOVO_LEAD"  # Same as current stage
            )
        
        # Assert
        assert result["success"] is True
        assert "já está no estágio" in result["message"]
        # Should not call update
        mock_kommo_service.update_lead_stage.assert_not_called()

    async def test_update_stage_special_stages(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test special stage logging"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        mock_kommo_service.update_lead_stage.return_value = mock_lead
        
        # Test QUALIFICADO stage
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="QUALIFICADO"
            )
        
        assert result["success"] is True
        
        # Test REUNIAO_AGENDADA stage
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="REUNIAO_AGENDADA"
            )
        
        assert result["success"] is True
        
        # Test NAO_INTERESSADO stage
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="NAO_INTERESSADO"
            )
        
        assert result["success"] is True

    async def test_update_stage_note_error_continues(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test that note errors don't fail the stage update"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        mock_kommo_service.update_lead_stage.return_value = mock_lead
        mock_kommo_service.add_note.side_effect = Exception("Note error")
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="QUALIFICADO",
                add_note="Test note"
            )
        
        # Assert - Stage update should still succeed
        assert result["success"] is True
        assert result["new_stage"] == "qualificado"

    async def test_update_stage_api_error(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test API error during stage update"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        mock_kommo_service.update_lead_stage.side_effect = KommoAPIError(
            status_code=400,
            message="Invalid stage"
        )
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="QUALIFICADO"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro da API do Kommo" in result["error"]

    async def test_update_stage_unexpected_error(self, mock_kommo_service):
        """Test unexpected error handling"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Connection error")
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="QUALIFICADO"
            )
        
        # Assert
        assert result["success"] is False
        assert "Erro inesperado" in result["error"]


@pytest.mark.asyncio
class TestGetLeadStage:
    """Test cases for get_lead_stage tool"""

    async def test_get_stage_success(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test successful stage retrieval"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await get_lead_stage(lead_id=12345)
        
        # Assert
        assert result["success"] is True
        assert result["lead_id"] == 12345
        assert result["stage_name"] == "novo lead"
        assert result["stage_key"] == "NOVO_LEAD"
        assert result["stage_id"] == 1001
        assert result["pipeline_id"] == 2001
        assert result["pipeline_name"] == "Pipeline Principal"

    async def test_get_stage_lead_not_found(self, mock_kommo_service):
        """Test getting stage when lead doesn't exist"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = KommoAPIError(
            status_code=404,
            message="Lead not found"
        )
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await get_lead_stage(lead_id=99999)
        
        # Assert
        assert result["success"] is False
        assert "não encontrado" in result["error"]
        assert result["stage_name"] is None

    async def test_get_stage_unknown_stage(self, mock_kommo_service, mock_lead):
        """Test getting stage when stage is not in KOMMO_STAGES"""
        # Arrange
        mock_lead_custom = {**mock_lead, "status_id": 9999}
        mock_kommo_service.get_lead.return_value = mock_lead_custom
        mock_pipelines_custom = [
            {
                "id": 2001,
                "name": "Pipeline Principal",
                "_embedded": {
                    "statuses": [
                        {"id": 9999, "name": "estágio customizado"}
                    ]
                }
            }
        ]
        mock_kommo_service.get_pipelines.return_value = mock_pipelines_custom
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await get_lead_stage(lead_id=12345)
        
        # Assert
        assert result["success"] is True
        assert result["stage_name"] == "estágio customizado"
        assert result["stage_key"] is None  # Not mapped to KOMMO_STAGES

    async def test_get_stage_pipeline_not_found(self, mock_kommo_service, mock_lead):
        """Test getting stage when pipeline is not found"""
        # Arrange
        mock_lead_invalid = {**mock_lead, "pipeline_id": 9999}
        mock_kommo_service.get_lead.return_value = mock_lead_invalid
        mock_kommo_service.get_pipelines.return_value = []
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await get_lead_stage(lead_id=12345)
        
        # Assert
        assert result["success"] is True
        assert result["stage_name"] is None
        assert result["pipeline_name"] is None

    async def test_get_stage_error_handling(self, mock_kommo_service):
        """Test error handling in get_lead_stage"""
        # Arrange
        mock_kommo_service.get_lead.side_effect = Exception("Connection error")
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await get_lead_stage(lead_id=12345)
        
        # Assert
        assert result["success"] is False
        assert "Erro ao consultar estágio" in result["error"]

    async def test_tool_instances(self):
        """Test that all tool instances are correctly exported"""
        assert UpdateKommoStageTool == update_kommo_stage
        assert GetLeadStageTool == get_lead_stage
        assert callable(UpdateKommoStageTool)
        assert callable(GetLeadStageTool)

    async def test_update_stage_pipeline_transitions(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test various pipeline stage transitions"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        
        # Test progression through pipeline
        stages_progression = [
            ("NOVO_LEAD", "EM_NEGOCIACAO"),
            ("EM_NEGOCIACAO", "EM_QUALIFICACAO"),
            ("EM_QUALIFICACAO", "QUALIFICADO"),
            ("QUALIFICADO", "REUNIAO_AGENDADA")
        ]
        
        for current_stage, next_stage in stages_progression:
            with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
                mock_kommo_service.update_lead_stage.return_value = mock_lead
                
                result = await update_kommo_stage(
                    lead_id=12345,
                    stage_name=next_stage
                )
                
                assert result["success"] is True
                assert result["new_stage"] == KOMMO_STAGES[next_stage]

    async def test_update_stage_rate_limit_handling(self, mock_kommo_service, mock_lead, mock_pipelines):
        """Test handling of rate limit errors"""
        # Arrange
        mock_kommo_service.get_lead.return_value = mock_lead
        mock_kommo_service.get_pipelines.return_value = mock_pipelines
        mock_kommo_service.update_lead_stage.side_effect = KommoAPIError(
            status_code=429,
            message="Too Many Requests"
        )
        
        with patch('agente.tools.kommo.update_stage.get_kommo_service', return_value=mock_kommo_service):
            # Act
            result = await update_kommo_stage(
                lead_id=12345,
                stage_name="QUALIFICADO"
            )
        
        # Assert
        assert result["success"] is False
        assert "429" in result["error"] or "Too Many Requests" in result["error"]