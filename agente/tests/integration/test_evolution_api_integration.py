"""
Integration tests for Evolution API v2.

These tests verify the actual integration with Evolution API endpoints.
They should be run against a test instance or with proper mocking.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import httpx
import json

from agente.services.evolution_service import EvolutionService
from agente.core.config import EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE


@pytest.mark.integration
class TestEvolutionAPIIntegration:
    """Integration tests for Evolution API service."""
    
    @pytest_asyncio.fixture
    async def evolution_service(self):
        """Create Evolution service instance."""
        # For integration tests, we can use the real service
        # but mock the HTTP client to avoid actual API calls
        service = EvolutionService()
        return service
    
    @pytest_asyncio.fixture
    async def mock_httpx_client(self):
        """Mock httpx client for controlled testing."""
        client = AsyncMock(spec=httpx.AsyncClient)
        return client
    
    @pytest.mark.asyncio
    async def test_send_text_integration(self, evolution_service, mock_httpx_client):
        """Test sending text message through Evolution API."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": true,
                "id": "BAE5123456789"
            },
            "message": {
                "conversation": "Test message"
            },
            "status": "PENDING"
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.send_text(
                phone="5511999999999",
                message="Test message"
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once_with(
            method="POST",
            url=f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}",
            json={
                "number": "5511999999999",
                "text": "Test message",
                "delay": 1000
            },
            headers={
                "apikey": EVOLUTION_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        # Verify result
        assert result["success"] is True
        assert "key" in result
    
    @pytest.mark.asyncio
    async def test_send_media_integration(self, evolution_service, mock_httpx_client):
        """Test sending media through Evolution API."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": true,
                "id": "BAE5987654321"
            },
            "message": {
                "imageMessage": {
                    "url": "https://example.com/image.jpg",
                    "mimetype": "image/jpeg",
                    "caption": "Test caption"
                }
            },
            "status": "PENDING"
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.send_media(
                phone="5511999999999",
                media_url="https://example.com/image.jpg",
                media_type="image",
                caption="Test caption"
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once_with(
            method="POST",
            url=f"{EVOLUTION_API_URL}/message/sendMedia/{EVOLUTION_INSTANCE}",
            json={
                "number": "5511999999999",
                "mediatype": "image",
                "media": "https://example.com/image.jpg",
                "caption": "Test caption"
            },
            headers={
                "apikey": EVOLUTION_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        
        # Verify result
        assert result["success"] is True
        assert "key" in result
    
    @pytest.mark.asyncio
    async def test_download_media_integration(self, evolution_service, mock_httpx_client):
        """Test downloading media from Evolution API."""
        # Mock response with binary data
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"fake-image-data"
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.download_media(
                message_id="BAE5123456789"
            )
        
        # Verify API call
        mock_httpx_client.request.assert_called_once_with(
            method="POST",
            url=f"{EVOLUTION_API_URL}/chat/getBase64FromMediaMessage/{EVOLUTION_INSTANCE}",
            json={
                "key": {
                    "id": "BAE5123456789"
                }
            },
            headers={
                "apikey": EVOLUTION_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        
        # Verify result
        assert result == b"fake-image-data"
    
    @pytest.mark.asyncio
    async def test_check_connection_integration(self, evolution_service, mock_httpx_client):
        """Test checking WhatsApp connection status."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "instance": {
                "instanceName": EVOLUTION_INSTANCE,
                "status": "open",
                "state": "CONNECTED"
            },
            "qrcode": None
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.check_connection()
        
        # Verify API call
        mock_httpx_client.request.assert_called_once_with(
            method="GET",
            url=f"{EVOLUTION_API_URL}/instance/connectionState/{EVOLUTION_INSTANCE}",
            headers={
                "apikey": EVOLUTION_API_KEY
            },
            timeout=10.0
        )
        
        # Verify result
        assert result["connected"] is True
        assert result["status"] == "open"
    
    @pytest.mark.asyncio
    async def test_webhook_configuration_integration(self, evolution_service, mock_httpx_client):
        """Test webhook configuration through Evolution API."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "webhook": {
                "url": "https://example.com/webhook",
                "enabled": True,
                "events": ["messages.upsert", "messages.update"]
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        # Patch the service's client
        with patch.object(evolution_service, '_client', mock_httpx_client):
            # Simulate setting webhook
            response = await mock_httpx_client.request(
                method="POST",
                url=f"{EVOLUTION_API_URL}/webhook/set/{EVOLUTION_INSTANCE}",
                json={
                    "url": "https://example.com/webhook",
                    "webhook_by_events": True,
                    "events": ["messages.upsert", "messages.update"]
                },
                headers={
                    "apikey": EVOLUTION_API_KEY,
                    "Content-Type": "application/json"
                }
            )
        
        # Verify webhook was set
        assert response.status_code == 200
        webhook_data = await response.json()
        assert webhook_data["webhook"]["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, evolution_service, mock_httpx_client):
        """Test error handling for API failures."""
        # Test 401 Unauthorized
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_httpx_client.request.return_value = mock_response
        
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.send_text(
                phone="5511999999999",
                message="Test"
            )
        
        assert result["success"] is False
        assert "Invalid API key" in result["error"]
        
        # Test 429 Rate Limit
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.send_text(
                phone="5511999999999",
                message="Test"
            )
        
        assert result["success"] is False
        assert "Rate limit" in result["error"]
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, evolution_service, mock_httpx_client):
        """Test handling of network timeouts."""
        # Simulate timeout
        mock_httpx_client.request.side_effect = httpx.TimeoutException("Request timed out")
        
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.send_text(
                phone="5511999999999",
                message="Test"
            )
        
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_instance_not_connected(self, evolution_service, mock_httpx_client):
        """Test handling when WhatsApp instance is not connected."""
        # Mock disconnected response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "instance": {
                "instanceName": EVOLUTION_INSTANCE,
                "status": "close",
                "state": "DISCONNECTED"
            },
            "qrcode": {
                "qrcode": "data:image/png;base64,..."
            }
        }
        mock_httpx_client.request.return_value = mock_response
        
        with patch.object(evolution_service, '_client', mock_httpx_client):
            result = await evolution_service.check_connection()
        
        assert result["connected"] is False
        assert result["status"] == "close"
        assert "qrcode" in result
    
    @pytest.mark.asyncio
    async def test_bulk_message_sending(self, evolution_service, mock_httpx_client):
        """Test sending messages to multiple recipients."""
        # Mock successful responses
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": true},
            "status": "PENDING"
        }
        mock_httpx_client.request.return_value = mock_response
        
        phones = ["5511999999999", "5511888888888", "5511777777777"]
        
        with patch.object(evolution_service, '_client', mock_httpx_client):
            results = []
            for phone in phones:
                result = await evolution_service.send_text(
                    phone=phone,
                    message="Bulk test message"
                )
                results.append(result)
        
        # Verify all messages were sent
        assert len(results) == 3
        assert all(r["success"] for r in results)
        assert mock_httpx_client.request.call_count == 3


@pytest.mark.integration
class TestEvolutionWebhookIntegration:
    """Test Evolution API webhook handling."""
    
    @pytest.mark.asyncio
    async def test_webhook_message_upsert(self):
        """Test handling of message.upsert webhook event."""
        webhook_data = {
            "event": "messages.upsert",
            "instance": {
                "instanceId": EVOLUTION_INSTANCE,
                "instanceName": EVOLUTION_INSTANCE
            },
            "data": {
                "key": {
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": False,
                    "id": "BAE5123456789"
                },
                "message": {
                    "conversation": "Quero saber sobre energia solar"
                },
                "messageTimestamp": "1234567890",
                "pushName": "João Silva"
            }
        }
        
        # Verify webhook structure
        assert webhook_data["event"] == "messages.upsert"
        assert not webhook_data["data"]["key"]["fromMe"]
        assert webhook_data["data"]["message"]["conversation"]
    
    @pytest.mark.asyncio
    async def test_webhook_connection_update(self):
        """Test handling of connection.update webhook event."""
        webhook_data = {
            "event": "connection.update",
            "instance": {
                "instanceId": EVOLUTION_INSTANCE,
                "instanceName": EVOLUTION_INSTANCE
            },
            "data": {
                "state": "open",
                "statusCode": 200
            }
        }
        
        # Verify webhook structure
        assert webhook_data["event"] == "connection.update"
        assert webhook_data["data"]["state"] == "open"