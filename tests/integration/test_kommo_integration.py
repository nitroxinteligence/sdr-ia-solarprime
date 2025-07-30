"""
Testes de Integração Kommo CRM
===============================
Testes para validar a integração completa com Kommo CRM
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import httpx

from services.kommo_service import KommoService
from services.kommo_auth import KommoAuth
from services.qualification_kommo_integration import QualificationKommoIntegration
from services.kommo_follow_up_service import KommoFollowUpService
from models.kommo_models import KommoLead, LeadStatus, SolutionType, KommoTask, TaskType
from models.lead import Lead, LeadCreate
from config.config import Config


@pytest.fixture
def mock_config():
    """Mock de configuração para testes"""
    config = Mock(spec=Config)
    config.kommo = Mock()
    config.kommo.client_id = "test_client_id"
    config.kommo.client_secret = "test_client_secret"
    config.kommo.subdomain = "test"
    config.kommo.redirect_uri = "http://localhost:8000/auth/kommo/callback"
    config.kommo.pipeline_id = 12345
    config.kommo.stage_ids = {
        "new": 1,
        "in_qualification": 2,
        "qualified": 3,
        "meeting_scheduled": 4
    }
    config.kommo.custom_fields = {
        "whatsapp_number": 101,
        "energy_bill_value": 102,
        "qualification_score": 103
    }
    config.kommo.responsible_users = {
        "default": 1001,
        "high_value": 1002
    }
    return config


@pytest.fixture
def mock_redis():
    """Mock do Redis para testes"""
    with patch('services.kommo_auth.redis_client') as mock:
        mock.setex = Mock()
        mock.get = Mock(return_value=None)
        mock.exists = Mock(return_value=False)
        mock.delete = Mock()
        yield mock


class TestKommoAuth:
    """Testes do serviço de autenticação OAuth2"""
    
    @pytest.mark.asyncio
    async def test_generate_auth_url(self, mock_config):
        """Testa geração de URL de autorização"""
        auth = KommoAuth(mock_config)
        
        url = auth.get_auth_url()
        
        assert "https://test.kommo.com/oauth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "response_type=code" in url
        assert "state=" in url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self, mock_config, mock_redis):
        """Testa troca de código por token"""
        auth = KommoAuth(mock_config)
        
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 86400
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            tokens = await auth.exchange_code_for_token("test_code")
            
            assert tokens["access_token"] == "test_access_token"
            assert tokens["refresh_token"] == "test_refresh_token"
            assert mock_redis.setex.called
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, mock_config, mock_redis):
        """Testa renovação de token"""
        auth = KommoAuth(mock_config)
        
        # Mock do token existente
        import json
        mock_redis.get.return_value = json.dumps({
            "refresh_token": "old_refresh_token",
            "access_token": "old_access_token",
            "expires_at": datetime.now().timestamp() - 3600  # Expirado
        })
        
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 86400
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            tokens = await auth.refresh_access_token()
            
            assert tokens["access_token"] == "new_access_token"


class TestKommoService:
    """Testes do serviço principal Kommo"""
    
    @pytest.fixture
    def kommo_service(self, mock_config):
        """Fixture do serviço Kommo"""
        with patch('services.kommo_service.KommoAuth') as mock_auth:
            mock_auth.return_value.get_valid_token = AsyncMock(return_value="test_token")
            service = KommoService()
            service.config = mock_config
            return service
    
    @pytest.mark.asyncio
    async def test_create_lead(self, kommo_service):
        """Testa criação de lead"""
        lead_data = KommoLead(
            name="João Silva",
            phone="+5511999999999",
            whatsapp="+5511999999999",
            email="joao@email.com",
            energy_bill_value=450.00,
            solution_type=SolutionType.OWN_PLANT,
            qualification_score=85,
            ai_notes="Lead qualificado via WhatsApp",
            tags=["WhatsApp Lead", "Lead Quente"]
        )
        
        # Mock da resposta HTTP
        mock_response = {
            "_embedded": {
                "leads": [{
                    "id": 123456,
                    "name": "João Silva",
                    "status_id": 1
                }]
            }
        }
        
        with patch.object(kommo_service, '_make_request', AsyncMock(return_value=mock_response)):
            with patch.object(kommo_service, 'create_contact', AsyncMock(return_value={"id": 789})):
                with patch.object(kommo_service, 'link_contact_to_lead', AsyncMock(return_value=True)):
                    with patch.object(kommo_service, 'add_note', AsyncMock(return_value=True)):
                        
                        result = await kommo_service.create_lead(lead_data)
                        
                        assert result["id"] == 123456
                        assert result["name"] == "João Silva"
    
    @pytest.mark.asyncio
    async def test_update_lead(self, kommo_service):
        """Testa atualização de lead"""
        lead_data = KommoLead(
            name="João Silva",
            phone="+5511999999999",
            whatsapp="+5511999999999",
            energy_bill_value=550.00,
            qualification_score=90,
            ai_notes="Score atualizado"
        )
        
        mock_response = {"id": 123456, "updated": True}
        
        with patch.object(kommo_service, '_make_request', AsyncMock(return_value=mock_response)):
            with patch.object(kommo_service, 'add_note', AsyncMock(return_value=True)):
                
                result = await kommo_service.update_lead(123456, lead_data)
                
                assert result["id"] == 123456
                assert result["updated"] == True
    
    @pytest.mark.asyncio
    async def test_move_lead_stage(self, kommo_service):
        """Testa movimentação de lead no pipeline"""
        with patch.object(kommo_service, '_make_request', AsyncMock(return_value={})):
            with patch.object(kommo_service, 'add_tags_to_lead', AsyncMock(return_value=True)):
                
                result = await kommo_service.move_lead_stage(123456, LeadStatus.QUALIFIED)
                
                assert result == True
    
    @pytest.mark.asyncio
    async def test_find_lead_by_whatsapp(self, kommo_service):
        """Testa busca de lead por WhatsApp"""
        mock_response = {
            "_embedded": {
                "leads": [{
                    "id": 123456,
                    "name": "João Silva",
                    "custom_fields_values": [
                        {
                            "field_id": 101,
                            "values": [{"value": "+5511999999999"}]
                        }
                    ]
                }]
            }
        }
        
        with patch.object(kommo_service, '_make_request', AsyncMock(return_value=mock_response)):
            result = await kommo_service.find_lead_by_whatsapp("+5511999999999")
            
            assert result["id"] == 123456
            assert result["name"] == "João Silva"
    
    @pytest.mark.asyncio
    async def test_create_task(self, kommo_service):
        """Testa criação de tarefa"""
        task = KommoTask(
            text="Follow-up WhatsApp",
            task_type=TaskType.CALL,
            complete_till=datetime.now() + timedelta(hours=1),
            entity_type="leads",
            entity_id=123456
        )
        
        mock_response = {
            "_embedded": {
                "tasks": [{
                    "id": 789,
                    "text": "Follow-up WhatsApp"
                }]
            }
        }
        
        with patch.object(kommo_service, '_make_request', AsyncMock(return_value=mock_response)):
            result = await kommo_service.create_task(task)
            
            assert result["id"] == 789
            assert result["text"] == "Follow-up WhatsApp"


class TestQualificationIntegration:
    """Testes da integração de qualificação"""
    
    @pytest.fixture
    def qualification_integration(self, mock_config):
        """Fixture da integração de qualificação"""
        with patch('services.qualification_kommo_integration.kommo_service') as mock_service:
            integration = QualificationKommoIntegration()
            integration.config = mock_config
            integration.kommo = mock_service
            return integration
    
    @pytest.mark.asyncio
    async def test_sync_lead_to_kommo(self, qualification_integration):
        """Testa sincronização de lead para Kommo"""
        # Mock do lead local
        lead = Mock(spec=Lead)
        lead.id = "local-lead-id"
        lead.name = "João Silva"
        lead.phone_number = "+5511999999999"
        lead.email = "joao@email.com"
        lead.bill_value = 450.00
        lead.qualification_score = 85
        lead.kommo_lead_id = None
        
        # Mock do resultado do Kommo
        qualification_integration.kommo.create_or_update_lead = AsyncMock(
            return_value={"id": 123456}
        )
        
        # Mock do repositório
        with patch('services.qualification_kommo_integration.lead_repository') as mock_repo:
            mock_repo.update = AsyncMock()
            
            result = await qualification_integration.sync_lead_to_kommo(
                lead,
                ai_notes="Lead qualificado",
                current_stage="QUALIFICATION"
            )
            
            assert result == "123456"
            assert qualification_integration.kommo.create_or_update_lead.called
            assert mock_repo.update.called
    
    @pytest.mark.asyncio
    async def test_update_lead_stage(self, qualification_integration):
        """Testa atualização de estágio"""
        lead = Mock(spec=Lead)
        lead.kommo_lead_id = "123456"
        
        qualification_integration.kommo.move_lead_stage = AsyncMock(return_value=True)
        qualification_integration.kommo.add_note = AsyncMock(return_value=True)
        qualification_integration.kommo.add_tags_to_lead = AsyncMock(return_value=True)
        
        result = await qualification_integration.update_lead_stage(
            lead,
            "SCHEDULING",
            notes="Iniciou agendamento"
        )
        
        assert result == True
        assert qualification_integration.kommo.move_lead_stage.called
        assert qualification_integration.kommo.add_note.called


class TestKommoFollowUpService:
    """Testes do serviço de follow-up"""
    
    @pytest.fixture
    def follow_up_service(self, mock_config):
        """Fixture do serviço de follow-up"""
        with patch('services.kommo_follow_up_service.kommo_service') as mock_kommo:
            service = KommoFollowUpService()
            service.config = mock_config
            service.kommo = mock_kommo
            return service
    
    @pytest.mark.asyncio
    async def test_schedule_follow_up(self, follow_up_service):
        """Testa agendamento de follow-up"""
        # Mock do lead
        lead = Mock(spec=Lead)
        lead.id = "lead-id"
        lead.name = "João Silva"
        lead.phone_number = "+5511999999999"
        lead.interested = True
        lead.kommo_lead_id = "123456"
        
        # Mock do repositório
        with patch('services.kommo_follow_up_service.lead_repository') as mock_repo:
            mock_repo.get = AsyncMock(return_value=lead)
            
            # Mock do Kommo
            follow_up_service.kommo.create_task = AsyncMock(return_value={"id": 789})
            
            # Mock do Celery
            with patch('services.kommo_follow_up_service.send_follow_up_task') as mock_task:
                mock_task.apply_async = Mock()
                
                # Mock do repositório de follow-up
                with patch('services.kommo_follow_up_service.follow_up_repository') as mock_follow_repo:
                    mock_follow_repo.create = AsyncMock()
                    
                    result = await follow_up_service.schedule_follow_up("lead-id", 1)
                    
                    assert result == True
                    assert follow_up_service.kommo.create_task.called
                    assert mock_task.apply_async.called
                    assert mock_follow_repo.create.called
    
    @pytest.mark.asyncio
    async def test_execute_follow_up(self, follow_up_service):
        """Testa execução de follow-up"""
        # Mock do lead
        lead = Mock(spec=Lead)
        lead.id = "lead-id"
        lead.name = "João Silva"
        lead.phone_number = "+5511999999999"
        lead.interested = True
        lead.kommo_lead_id = "123456"
        lead.follow_up_count = 0
        
        # Mock dos repositórios
        with patch('services.kommo_follow_up_service.lead_repository') as mock_repo:
            mock_repo.get = AsyncMock(return_value=lead)
            mock_repo.update = AsyncMock()
            
            # Mock do WhatsApp
            with patch('services.kommo_follow_up_service.whatsapp_service') as mock_whatsapp:
                mock_whatsapp.send_text_message = AsyncMock(return_value=True)
                
                # Mock do Kommo
                follow_up_service.kommo.add_note = AsyncMock()
                follow_up_service.kommo.add_tags_to_lead = AsyncMock()
                
                # Mock do repositório de follow-up
                with patch('services.kommo_follow_up_service.follow_up_repository') as mock_follow_repo:
                    mock_follow_repo.update_status = AsyncMock()
                    
                    # Mock do schedule_follow_up para próximo follow-up
                    follow_up_service.schedule_follow_up = AsyncMock(return_value=True)
                    
                    result = await follow_up_service.execute_follow_up("lead-id", 1)
                    
                    assert result == True
                    assert mock_whatsapp.send_text_message.called
                    assert mock_repo.update.called
                    assert follow_up_service.kommo.add_note.called
                    assert follow_up_service.schedule_follow_up.called


@pytest.mark.integration
class TestKommoIntegrationFlow:
    """Testes de fluxo completo de integração"""
    
    @pytest.mark.asyncio
    async def test_complete_lead_flow(self):
        """Testa fluxo completo desde criação até agendamento"""
        # Este teste seria executado apenas com ambiente de teste real
        # configurado com credenciais de teste do Kommo
        
        # 1. Criar lead via WhatsApp
        # 2. Sincronizar com Kommo
        # 3. Atualizar qualificação
        # 4. Mover pelos estágios
        # 5. Agendar follow-up
        # 6. Executar follow-up
        
        pytest.skip("Teste de integração requer ambiente configurado")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])