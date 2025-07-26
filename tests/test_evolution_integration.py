"""
Evolution API Integration Tests
================================
Testes de integração com Evolution API
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import httpx

from services.evolution_api import EvolutionAPIClient
from services.whatsapp_service import WhatsAppService
from services.connection_monitor import ConnectionMonitor, ConnectionState


# Fixtures de dados comuns
@pytest.fixture
def sample_webhook_payloads():
    """Payloads de webhook de exemplo"""
    return {
        "text_message": {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {
                    "id": "MSG123",
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "conversation": "Olá, quero saber sobre energia solar"
                },
                "messageTimestamp": 1234567890,
                "pushName": "João Silva"
            }
        },
        "image_message": {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {
                    "id": "IMG123",
                    "remoteJid": "5511888888888@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "imageMessage": {
                        "caption": "Minha conta de luz",
                        "mimetype": "image/jpeg",
                        "url": "https://example.com/image.jpg"
                    }
                },
                "messageTimestamp": 1234567891,
                "pushName": "Maria Santos"
            }
        },
        "audio_message": {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {
                    "id": "AUD123",
                    "remoteJid": "5511777777777@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "audioMessage": {
                        "seconds": 10,
                        "mimetype": "audio/ogg"
                    }
                },
                "messageTimestamp": 1234567892,
                "pushName": "Pedro Costa"
            }
        },
        "poll_message": {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {
                    "id": "POLL123",
                    "remoteJid": "5511666666666@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "pollCreationMessage": {
                        "name": "Qual solução você prefere?",
                        "options": [
                            {"name": "Energia Solar Residencial"},
                            {"name": "Energia Solar Empresarial"},
                            {"name": "Fazenda Solar"}
                        ]
                    }
                },
                "messageTimestamp": 1234567893,
                "pushName": "Ana Oliveira"
            }
        },
        "connection_update": {
            "event": "CONNECTION_UPDATE",
            "data": {
                "state": "open",
                "instance": "solarprime"
            }
        }
    }


@pytest.fixture
def evolution_client():
    """Fixture para cliente Evolution API"""
    return EvolutionAPIClient()


@pytest.fixture
def whatsapp_service():
    """Fixture para serviço WhatsApp"""
    return WhatsAppService()


@pytest.fixture
def connection_monitor():
    """Fixture para monitor de conexão"""
    return ConnectionMonitor()


class TestEvolutionAPIClient:
    """Testes do cliente Evolution API"""
    
    @pytest.mark.asyncio
    async def test_check_connection_success(self, evolution_client):
        """Testa verificação de conexão bem-sucedida"""
        with patch.object(evolution_client.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"state": "open"}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            result = await evolution_client.check_connection()
            
            assert result["state"] == "open"
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_text_message(self, evolution_client):
        """Testa envio de mensagem de texto"""
        with patch.object(evolution_client.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "key": {
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": True,
                    "id": "TEST123"
                },
                "message": {"conversation": "Teste"},
                "status": "PENDING"
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            result = await evolution_client.send_text_message(
                phone="11999999999",
                message="Teste"
            )
            
            assert result["key"]["id"] == "TEST123"
            assert result["status"] == "PENDING"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_poll(self, evolution_client):
        """Testa envio de enquete"""
        with patch.object(evolution_client.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "key": {"id": "POLL123"},
                "status": "SENT"
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            result = await evolution_client.send_poll(
                phone="11999999999",
                question="Qual seu interesse?",
                options=["Solar", "Economia", "Sustentabilidade"]
            )
            
            assert result["key"]["id"] == "POLL123"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_format_phone_number(self, evolution_client):
        """Testa formatação de número de telefone"""
        # Testes de formatação
        assert evolution_client._format_phone_number("11999999999") == "5511999999999@s.whatsapp.net"
        assert evolution_client._format_phone_number("5511999999999") == "5511999999999@s.whatsapp.net"
        assert evolution_client._format_phone_number("+5511999999999") == "5511999999999@s.whatsapp.net"
        assert evolution_client._format_phone_number("(11) 99999-9999") == "5511999999999@s.whatsapp.net"
    
    @pytest.mark.asyncio
    async def test_create_webhook(self, evolution_client):
        """Testa configuração de webhook"""
        with patch.object(evolution_client.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "instance": "test",
                "webhook": {"url": "http://test.com/webhook"}
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            result = await evolution_client.create_webhook(
                webhook_url="http://test.com/webhook"
            )
            
            assert result["webhook"]["url"] == "http://test.com/webhook"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retry_on_network_error(self, evolution_client):
        """Testa retry em erro de rede"""
        with patch.object(evolution_client.client, 'get') as mock_get:
            # Simular falha na primeira tentativa, sucesso na segunda
            mock_get.side_effect = [
                httpx.RequestError("Network error"),
                MagicMock(
                    json=lambda: {"state": "open"},
                    raise_for_status=lambda: None
                )
            ]
            
            result = await evolution_client.check_connection()
            
            assert result["state"] == "open"
            assert mock_get.call_count == 2  # Deve ter tentado 2 vezes


class TestWhatsAppService:
    """Testes do serviço WhatsApp"""
    
    @pytest.mark.asyncio
    async def test_process_text_message(self, whatsapp_service):
        """Testa processamento de mensagem de texto"""
        webhook_payload = {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {
                    "id": "MSG123",
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "conversation": "Olá, quero saber sobre energia solar"
                },
                "messageTimestamp": 1234567890,
                "pushName": "João"
            }
        }
        
        with patch.object(whatsapp_service, '_process_message') as mock_process:
            mock_process.return_value = "Olá João! Fico feliz em ajudar..."
            
            result = await whatsapp_service.process_webhook(webhook_payload)
            
            assert result["status"] == "success"
            assert result["message_id"] == "MSG123"
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_poll_message(self, whatsapp_service):
        """Testa extração de mensagem de enquete"""
        data = {
            "key": {"id": "POLL123", "remoteJid": "5511999999999@s.whatsapp.net"},
            "message": {
                "pollCreationMessage": {
                    "name": "Qual seu interesse?",
                    "options": [
                        {"name": "Economia"},
                        {"name": "Sustentabilidade"},
                        {"name": "Tecnologia"}
                    ]
                }
            }
        }
        
        info = whatsapp_service._extract_message_info(data)
        
        assert info["type"] == "poll"
        assert info["content"] == "Qual seu interesse?"
        assert len(info["media_data"]["options"]) == 3
    
    @pytest.mark.asyncio
    async def test_handle_reaction_message(self, whatsapp_service):
        """Testa processamento de reação"""
        data = {
            "key": {"id": "REACT123", "remoteJid": "5511999999999@s.whatsapp.net"},
            "message": {
                "reactionMessage": {
                    "key": {"id": "MSG123"},
                    "text": "👍"
                }
            }
        }
        
        info = whatsapp_service._extract_message_info(data)
        
        assert info["type"] == "reaction"
        assert info["content"] == "👍"
        assert info["media_data"]["emoji"] == "👍"
    
    @pytest.mark.asyncio
    async def test_ignore_own_messages(self, whatsapp_service):
        """Testa ignorar mensagens próprias"""
        webhook_payload = {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {
                    "id": "MSG123",
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": True  # Mensagem própria
                },
                "message": {"conversation": "Teste"}
            }
        }
        
        result = await whatsapp_service.process_webhook(webhook_payload)
        
        assert result["status"] == "ignored"
        assert result["reason"] == "own_message"


class TestConnectionMonitor:
    """Testes do monitor de conexão"""
    
    @pytest.mark.asyncio
    async def test_map_connection_states(self, connection_monitor):
        """Testa mapeamento de estados"""
        # Estado conectado
        state = connection_monitor._map_connection_state({"state": "open"})
        assert state == ConnectionState.CONNECTED
        
        # Estado desconectado
        state = connection_monitor._map_connection_state({"state": "close"})
        assert state == ConnectionState.DISCONNECTED
        
        # Estado QR Code
        state = connection_monitor._map_connection_state({"state": "qr"})
        assert state == ConnectionState.QR_CODE
        
        # Estado erro
        state = connection_monitor._map_connection_state({"error": "Some error"})
        assert state == ConnectionState.ERROR
    
    @pytest.mark.asyncio
    async def test_state_change_callbacks(self, connection_monitor):
        """Testa callbacks de mudança de estado"""
        callback_called = False
        callback_data = None
        
        def on_disconnected(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        connection_monitor.add_callback("on_disconnected", on_disconnected)
        
        # Simular mudança para desconectado
        await connection_monitor._handle_state_change(
            ConnectionState.DISCONNECTED,
            {"state": "close"}
        )
        
        assert callback_called
        assert callback_data["state"] == "close"
    
    @pytest.mark.asyncio
    async def test_uptime_calculation(self, connection_monitor):
        """Testa cálculo de uptime"""
        # Adicionar histórico fictício
        now = datetime.now()
        connection_monitor.state_history = [
            {
                "state": "connected",
                "timestamp": now.isoformat(),
                "data": {}
            },
            {
                "state": "disconnected",
                "timestamp": (now.replace(hour=now.hour + 1)).isoformat(),
                "data": {}
            },
            {
                "state": "connected",
                "timestamp": (now.replace(hour=now.hour + 2)).isoformat(),
                "data": {}
            }
        ]
        
        stats = connection_monitor.get_uptime_stats()
        
        assert stats["total_time"] == 7200  # 2 horas em segundos
        assert stats["connected_time"] == 3600  # 1 hora conectado
        assert stats["uptime_percentage"] == 50.0  # 50% uptime


# Testes de integração completa
class TestFullIntegration:
    """Testes de integração completa do sistema"""
    
    @pytest.mark.asyncio
    async def test_webhook_to_response_flow(self):
        """Testa fluxo completo de webhook até resposta"""
        from services.whatsapp_service import whatsapp_service
        from services.redis_service import redis_service
        
        # Mock do agente
        with patch.object(whatsapp_service, 'agent') as mock_agent:
            mock_agent.process_message = AsyncMock(return_value=(
                "Olá! Sou a Luna, assistente virtual da SolarPrime. Como posso ajudar?",
                {"stage": "GREETING", "sentiment": "positivo"}
            ))
            
            # Mock do Redis
            with patch.object(redis_service, 'get_conversation_state') as mock_redis_get:
                mock_redis_get.return_value = None
                
                # Mock do Evolution client
                with patch('services.whatsapp_service.evolution_client') as mock_evolution:
                    mock_client = AsyncMock()
                    mock_client.mark_as_read = AsyncMock()
                    mock_client.send_typing = AsyncMock()
                    mock_client.send_text_message = AsyncMock(return_value={
                        "key": {"id": "RESP123"},
                        "status": "SENT"
                    })
                    mock_evolution.__aenter__.return_value = mock_client
                    
                    # Webhook payload de teste
                    webhook_payload = {
                        "event": "MESSAGES_UPSERT",
                        "data": {
                            "key": {
                                "id": "MSG123",
                                "remoteJid": "5511999999999@s.whatsapp.net",
                                "fromMe": False
                            },
                            "message": {
                                "conversation": "Olá, gostaria de saber sobre energia solar"
                            },
                            "messageTimestamp": 1234567890,
                            "pushName": "João Silva"
                        }
                    }
                    
                    # Processar webhook
                    result = await whatsapp_service.process_webhook(webhook_payload)
                    
                    # Verificar resultado
                    assert result["status"] == "success"
                    assert result["message_id"] == "MSG123"
                    assert result["response_sent"] == True
                    
                    # Verificar chamadas
                    mock_client.mark_as_read.assert_called_once()
                    mock_client.send_typing.assert_called_once()
                    mock_client.send_text_message.assert_called_once()
                    mock_agent.process_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connection_recovery(self):
        """Testa recuperação de conexão perdida"""
        from services.connection_monitor import ConnectionMonitor, ConnectionState
        
        monitor = ConnectionMonitor()
        
        # Mock do Evolution client
        with patch('services.connection_monitor.evolution_client') as mock_evolution:
            mock_client = AsyncMock()
            
            # Simular sequência: conectado -> desconectado -> reconectando -> conectado
            mock_client.check_connection = AsyncMock(side_effect=[
                {"state": "open"},  # Estado inicial conectado
                {"state": "close"},  # Desconexão
                {"state": "connecting"},  # Tentando reconectar
                {"state": "open"}  # Reconectado
            ])
            
            mock_client.restart_instance = AsyncMock(return_value=True)
            mock_evolution.__aenter__.return_value = mock_client
            
            # Mock do Redis
            with patch('services.connection_monitor.redis_service') as mock_redis:
                mock_redis.set = AsyncMock()
                
                # Callbacks para rastrear mudanças
                disconnection_detected = False
                reconnection_detected = False
                
                def on_disconnected(data):
                    nonlocal disconnection_detected
                    disconnection_detected = True
                
                def on_connected(data):
                    nonlocal reconnection_detected
                    reconnection_detected = True
                
                monitor.add_callback("on_disconnected", on_disconnected)
                monitor.add_callback("on_connected", on_connected)
                
                # Executar 4 verificações
                for _ in range(4):
                    await monitor._check_connection()
                
                # Verificar sequência de eventos
                assert disconnection_detected, "Desconexão não foi detectada"
                assert reconnection_detected, "Reconexão não foi detectada"
                assert monitor.last_state == ConnectionState.CONNECTED
                
                # Verificar tentativa de reconexão
                success = await monitor.force_reconnect()
                assert success == True
                mock_client.restart_instance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_media_processing_flow(self):
        """Testa processamento de mídia (imagem, áudio, documento)"""
        from services.whatsapp_service import whatsapp_service
        
        # Mock do download de mídia
        with patch('services.whatsapp_service.evolution_client') as mock_evolution:
            mock_client = AsyncMock()
            mock_client.download_media = AsyncMock(return_value=b"fake_image_data")
            mock_client.mark_as_read = AsyncMock()
            mock_client.send_typing = AsyncMock()
            mock_client.send_text_message = AsyncMock()
            mock_evolution.__aenter__.return_value = mock_client
            
            # Mock do agente para processar mídia
            with patch.object(whatsapp_service, 'agent') as mock_agent:
                mock_agent.process_message = AsyncMock(return_value=(
                    "Recebi sua conta de luz. Vejo que o valor está em R$ 450. Posso ajudar a reduzir!",
                    {"stage": "BILL_ANALYSIS", "bill_value": 450}
                ))
                
                # Mock do Redis
                with patch('services.whatsapp_service.redis_service') as mock_redis:
                    mock_redis.get_media = AsyncMock(return_value=None)
                    mock_redis.cache_media = AsyncMock()
                    mock_redis.get_conversation_state = AsyncMock(return_value=None)
                    
                    # Payload de imagem
                    image_payload = {
                        "event": "MESSAGES_UPSERT",
                        "data": {
                            "key": {
                                "id": "IMG123",
                                "remoteJid": "5511999999999@s.whatsapp.net",
                                "fromMe": False
                            },
                            "message": {
                                "imageMessage": {
                                    "caption": "Minha conta de luz",
                                    "mimetype": "image/jpeg"
                                }
                            },
                            "pushName": "Cliente Teste"
                        }
                    }
                    
                    # Processar
                    result = await whatsapp_service.process_webhook(image_payload)
                    
                    # Verificações
                    assert result["status"] == "success"
                    mock_client.download_media.assert_called_once_with("IMG123")
                    mock_redis.cache_media.assert_called_once()
                    mock_agent.process_message.assert_called_once()
                    
                    # Verificar que mídia foi processada
                    call_args = mock_agent.process_message.call_args[1]
                    assert call_args["media_type"] == "image"
                    assert call_args["media_data"] is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_scenarios(self):
        """Testa cenários de erro e recuperação"""
        from services.whatsapp_service import whatsapp_service
        
        # Cenário 1: Erro no agente
        with patch.object(whatsapp_service, 'agent') as mock_agent:
            mock_agent.process_message = AsyncMock(side_effect=Exception("Erro no processamento"))
            
            with patch('services.whatsapp_service.evolution_client') as mock_evolution:
                mock_client = AsyncMock()
                mock_client.mark_as_read = AsyncMock()
                mock_client.send_typing = AsyncMock()
                mock_client.send_text_message = AsyncMock()
                mock_evolution.__aenter__.return_value = mock_client
                
                with patch('services.whatsapp_service.redis_service'):
                    webhook_payload = {
                        "event": "MESSAGES_UPSERT",
                        "data": {
                            "key": {"id": "MSG123", "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": False},
                            "message": {"conversation": "Teste"},
                            "pushName": "Teste"
                        }
                    }
                    
                    result = await whatsapp_service.process_webhook(webhook_payload)
                    
                    # Deve ter enviado mensagem de erro
                    assert result["status"] == "success"
                    error_msg_call = mock_client.send_text_message.call_args[1]
                    assert "Desculpe" in error_msg_call["message"]
                    assert "problema" in error_msg_call["message"]
    
    @pytest.mark.asyncio
    async def test_poll_and_reaction_handling(self):
        """Testa processamento de enquetes e reações"""
        # Teste de enquete
        poll_client = EvolutionAPIClient()
        with patch.object(poll_client.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"key": {"id": "POLL123"}, "status": "SENT"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            result = await poll_client.send_poll(
                phone="11999999999",
                question="Qual seu interesse em energia solar?",
                options=["Economia", "Sustentabilidade", "Independência energética"],
                multiple_answers=True
            )
            
            assert result["key"]["id"] == "POLL123"
            call_args = mock_post.call_args[1]["json"]
            assert call_args["pollMessage"]["name"] == "Qual seu interesse em energia solar?"
            assert len(call_args["pollMessage"]["values"]) == 3
            assert call_args["pollMessage"]["selectableCount"] == 3
    
    @pytest.mark.asyncio
    async def test_webhook_configuration_on_startup(self):
        """Testa configuração automática de webhook na inicialização"""
        from api.main import lifespan
        from fastapi import FastAPI
        
        app = FastAPI()
        
        with patch('api.main.evolution_client') as mock_evolution:
            mock_client = AsyncMock()
            mock_client.check_connection = AsyncMock(return_value={"state": "open"})
            mock_client.get_webhook_info = AsyncMock(return_value=None)  # Sem webhook configurado
            mock_client.create_webhook = AsyncMock(return_value={"webhook": {"url": "http://test.com"}})
            mock_evolution.__aenter__.return_value = mock_client
            
            with patch('api.main.connection_monitor') as mock_monitor:
                mock_monitor.start = AsyncMock()
                
                # Simular startup
                async with lifespan(app):
                    pass
                
                # Verificar que webhook foi configurado
                mock_client.create_webhook.assert_called_once()
                webhook_call = mock_client.create_webhook.call_args[1]
                assert "/webhook/whatsapp" in webhook_call["webhook_url"]
                assert "MESSAGES_UPSERT" in webhook_call["events"]
                assert "CONNECTION_UPDATE" in webhook_call["events"]