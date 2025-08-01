"""
Integration tests for Kommo CRM API.

These tests verify the actual integration with Kommo API endpoints.
They should be run against a test account or with proper mocking.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import httpx
from datetime import datetime, timezone

from agente.services.kommo_service import KommoService
from agente.core.config import KOMMO_SUBDOMAIN, KOMMO_LONG_LIVED_TOKEN


@pytest.mark.integration
class TestKommoAPIIntegration:
    """Integration tests for Kommo CRM API service."""
    
    @pytest_asyncio.fixture
    async def kommo_service(self):
        """Create Kommo service instance."""
        service = KommoService()
        return service
    
    @pytest_asyncio.fixture
    async def mock_httpx_client(self):
        """Mock httpx client for controlled testing."""
        client = AsyncMock(spec=httpx.AsyncClient)
        return client
    
    @pytest.mark.asyncio
    async def test_create_lead_integration(self, kommo_service, mock_httpx_client):
        """Test creating a lead through Kommo API."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "leads": [{
                    "id": 12345,
                    "name": "João Silva - Solar Residencial",
                    "status_id": 123,
                    "pipeline_id": 456,
                    "created_at": int(datetime.now(timezone.utc).timestamp()),
                    "custom_fields_values": []
                }]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.create_lead(
                name="João Silva",
                phone="5511999999999",
                email="joao@example.com",
                solution_type="residencial",
                energy_value=450.0
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        
        assert call_args[1]["method"] == "POST"
        assert f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/leads" in call_args[1]["url"]
        assert call_args[1]["headers"]["Authorization"] == f"Bearer {KOMMO_LONG_LIVED_TOKEN}"
        
        # Verify request body
        request_data = call_args[1]["json"][0]
        assert request_data["name"] == "João Silva - Solar Residencial"
        assert any(cf["field_id"] for cf in request_data["custom_fields_values"])
        
        # Verify result
        assert result["id"] == 12345
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_update_lead_integration(self, kommo_service, mock_httpx_client):
        """Test updating a lead through Kommo API."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "leads": [{
                    "id": 12345,
                    "name": "João Silva - Solar Residencial",
                    "status_id": 456,
                    "updated_at": int(datetime.now(timezone.utc).timestamp())
                }]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.update_lead(
                lead_id=12345,
                status_id=456,
                custom_fields={"qualification_score": 85}
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        
        assert call_args[1]["method"] == "PATCH"
        assert f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/leads" in call_args[1]["url"]
        
        # Verify result
        assert result["id"] == 12345
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_add_note_integration(self, kommo_service, mock_httpx_client):
        """Test adding a note to a lead."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "notes": [{
                    "id": 67890,
                    "entity_id": 12345,
                    "note_type": "common",
                    "params": {
                        "text": "Lead qualificado - Score: 85/100"
                    }
                }]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.add_note(
                lead_id=12345,
                text="Lead qualificado - Score: 85/100"
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        
        assert call_args[1]["method"] == "POST"
        assert f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/leads/notes" in call_args[1]["url"]
        
        # Verify request body
        request_data = call_args[1]["json"][0]
        assert request_data["entity_id"] == 12345
        assert request_data["params"]["text"] == "Lead qualificado - Score: 85/100"
        
        # Verify result
        assert result["id"] == 67890
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_get_pipelines_integration(self, kommo_service, mock_httpx_client):
        """Test getting pipelines from Kommo."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "pipelines": [
                    {
                        "id": 456,
                        "name": "Pipeline Solar",
                        "_embedded": {
                            "statuses": [
                                {"id": 123, "name": "Novo Lead", "sort": 10},
                                {"id": 456, "name": "Qualificado", "sort": 20},
                                {"id": 789, "name": "Reunião Agendada", "sort": 30}
                            ]
                        }
                    }
                ]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.get_pipelines()
        
        # Verify API call
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        
        assert call_args[1]["method"] == "GET"
        assert f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/leads/pipelines" in call_args[1]["url"]
        
        # Verify result
        assert len(result) == 1
        assert result[0]["id"] == 456
        assert len(result[0]["statuses"]) == 3
    
    @pytest.mark.asyncio
    async def test_create_task_integration(self, kommo_service, mock_httpx_client):
        """Test creating a task in Kommo."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "tasks": [{
                    "id": 111222,
                    "entity_id": 12345,
                    "entity_type": "leads",
                    "text": "Fazer follow-up com o lead",
                    "complete_till": int(datetime.now(timezone.utc).timestamp()) + 86400
                }]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.create_task(
                lead_id=12345,
                text="Fazer follow-up com o lead",
                complete_till=int(datetime.now(timezone.utc).timestamp()) + 86400
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        
        assert call_args[1]["method"] == "POST"
        assert f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/tasks" in call_args[1]["url"]
        
        # Verify result
        assert result["id"] == 111222
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_search_lead_integration(self, kommo_service, mock_httpx_client):
        """Test searching for leads in Kommo."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "leads": [
                    {
                        "id": 12345,
                        "name": "João Silva - Solar Residencial",
                        "custom_fields_values": [
                            {
                                "field_id": 123456,
                                "field_name": "Telefone",
                                "values": [{"value": "5511999999999"}]
                            }
                        ]
                    }
                ]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.search_lead(
                query="5511999999999"
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        
        assert call_args[1]["method"] == "GET"
        assert "query=5511999999999" in call_args[1]["url"]
        
        # Verify result
        assert len(result) == 1
        assert result[0]["id"] == 12345
    
    @pytest.mark.asyncio
    async def test_api_rate_limit_handling(self, kommo_service, mock_httpx_client):
        """Test handling of API rate limits."""
        # Mock 429 response
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": "Too Many Requests"}
        mock_httpx_client.request.return_value = mock_response
        
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.create_lead(
                name="Test Lead",
                phone="5511999999999"
            )
        
        assert result["success"] is False
        assert "rate limit" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_api_authentication_error(self, kommo_service, mock_httpx_client):
        """Test handling of authentication errors."""
        # Mock 401 response
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_httpx_client.request.return_value = mock_response
        
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.create_lead(
                name="Test Lead",
                phone="5511999999999"
            )
        
        assert result["success"] is False
        assert "authentication" in result["error"].lower() or "unauthorized" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_custom_fields_mapping(self, kommo_service, mock_httpx_client):
        """Test custom fields mapping for Solar Prime."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "leads": [{
                    "id": 12345,
                    "custom_fields_values": [
                        {
                            "field_id": 123456,
                            "field_name": "Valor da Conta",
                            "values": [{"value": "450.00"}]
                        },
                        {
                            "field_id": 123457,
                            "field_name": "Tipo de Solução",
                            "values": [{"value": "residencial"}]
                        }
                    ]
                }]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Test creating lead with custom fields
        with patch.object(kommo_service, '_client', mock_httpx_client):
            result = await kommo_service.create_lead(
                name="Test Lead",
                phone="5511999999999",
                energy_value=450.0,
                solution_type="residencial"
            )
        
        # Verify custom fields were included
        call_args = mock_httpx_client.request.call_args
        request_data = call_args[1]["json"][0]
        
        # Should have custom fields for energy value and solution type
        custom_fields = request_data.get("custom_fields_values", [])
        assert len(custom_fields) >= 2
    
    @pytest.mark.asyncio
    async def test_webhook_integration(self, kommo_service, mock_httpx_client):
        """Test Kommo webhook handling."""
        webhook_data = {
            "leads": {
                "update": [{
                    "id": 12345,
                    "status_id": 789,
                    "pipeline_id": 456,
                    "updated_at": int(datetime.now(timezone.utc).timestamp()),
                    "custom_fields": [
                        {
                            "id": 123456,
                            "name": "Qualification Score",
                            "values": [{"value": "95"}]
                        }
                    ]
                }]
            }
        }
        
        # Verify webhook structure
        assert "leads" in webhook_data
        assert "update" in webhook_data["leads"]
        assert webhook_data["leads"]["update"][0]["status_id"] == 789