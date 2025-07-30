"""
Testes Unitários - Kommo Auth Service
=====================================
Testes unitários para o serviço de autenticação OAuth2 do Kommo
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json

from services.kommo_auth import KommoAuth
from config.config import Config


class TestKommoAuthUnit:
    """Testes unitários do KommoAuth"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock de configuração"""
        config = Mock(spec=Config)
        config.kommo = Mock()
        config.kommo.client_id = "test_client_id"
        config.kommo.client_secret = "test_secret"
        config.kommo.subdomain = "testcompany"
        config.kommo.redirect_uri = "http://localhost:8000/callback"
        return config
    
    @pytest.fixture
    def kommo_auth(self, mock_config):
        """Instância do KommoAuth com mocks"""
        with patch('services.kommo_auth.redis_client') as mock_redis:
            auth = KommoAuth(mock_config)
            auth.redis_mock = mock_redis
            return auth
    
    def test_init(self, kommo_auth, mock_config):
        """Testa inicialização do serviço"""
        assert kommo_auth.client_id == "test_client_id"
        assert kommo_auth.client_secret == "test_secret"
        assert kommo_auth.subdomain == "testcompany"
        assert kommo_auth.base_url == "https://testcompany.kommo.com"
    
    def test_generate_state(self, kommo_auth):
        """Testa geração de state para CSRF"""
        state = kommo_auth.generate_state()
        
        assert isinstance(state, str)
        assert len(state) > 20  # Token deve ser longo o suficiente
        
        # Verifica se foi salvo no Redis
        kommo_auth.redis_mock.setex.assert_called_once()
        call_args = kommo_auth.redis_mock.setex.call_args[0]
        assert call_args[0].startswith("kommo:oauth:state:")
        assert call_args[1] == 600  # 10 minutos TTL
        assert call_args[2] == "1"
    
    def test_verify_state_valid(self, kommo_auth):
        """Testa verificação de state válido"""
        kommo_auth.redis_mock.exists.return_value = True
        
        result = kommo_auth.verify_state("valid_state")
        
        assert result == True
        kommo_auth.redis_mock.exists.assert_called_once()
        kommo_auth.redis_mock.delete.assert_called_once()  # State usado apenas uma vez
    
    def test_verify_state_invalid(self, kommo_auth):
        """Testa verificação de state inválido"""
        kommo_auth.redis_mock.exists.return_value = False
        
        result = kommo_auth.verify_state("invalid_state")
        
        assert result == False
        kommo_auth.redis_mock.exists.assert_called_once()
        kommo_auth.redis_mock.delete.assert_not_called()
    
    def test_get_auth_url(self, kommo_auth):
        """Testa geração de URL de autorização"""
        with patch.object(kommo_auth, 'generate_state', return_value='test_state'):
            url = kommo_auth.get_auth_url()
        
        assert "https://testcompany.kommo.com/oauth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=http://localhost:8000/callback" in url
        assert "response_type=code" in url
        assert "state=test_state" in url
        assert "mode=post_message" in url
    
    def test_get_auth_url_with_custom_state(self, kommo_auth):
        """Testa URL com state customizado"""
        url = kommo_auth.get_auth_url(state="custom_state")
        
        assert "state=custom_state" in url
    
    @pytest.mark.asyncio
    async def test_save_tokens(self, kommo_auth):
        """Testa salvamento de tokens"""
        tokens = {
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_in": 86400
        }
        
        await kommo_auth._save_tokens(tokens)
        
        # Verifica se adicionou expires_at
        saved_data = kommo_auth.redis_mock.setex.call_args[0][2]
        saved_tokens = json.loads(saved_data)
        assert "expires_at" in saved_tokens
        assert saved_tokens["expires_at"] > datetime.now().timestamp()
        
        # Verifica TTL (90 dias)
        assert kommo_auth.redis_mock.setex.call_args[0][1] == 90 * 24 * 60 * 60
    
    @pytest.mark.asyncio
    async def test_get_tokens_exists(self, kommo_auth):
        """Testa recuperação de tokens existentes"""
        mock_tokens = {
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_at": datetime.now().timestamp() + 3600
        }
        
        kommo_auth.redis_mock.get.return_value = json.dumps(mock_tokens)
        
        tokens = await kommo_auth._get_tokens()
        
        assert tokens == mock_tokens
        kommo_auth.redis_mock.get.assert_called_once_with("kommo:tokens")
    
    @pytest.mark.asyncio
    async def test_get_tokens_not_exists(self, kommo_auth):
        """Testa quando não há tokens salvos"""
        kommo_auth.redis_mock.get.return_value = None
        
        tokens = await kommo_auth._get_tokens()
        
        assert tokens is None
    
    @pytest.mark.asyncio
    async def test_get_valid_token_not_expired(self, kommo_auth):
        """Testa obtenção de token válido não expirado"""
        mock_tokens = {
            "access_token": "valid_token",
            "refresh_token": "refresh",
            "expires_at": datetime.now().timestamp() + 3600  # 1 hora no futuro
        }
        
        with patch.object(kommo_auth, '_get_tokens', AsyncMock(return_value=mock_tokens)):
            token = await kommo_auth.get_valid_token()
        
        assert token == "valid_token"
    
    @pytest.mark.asyncio
    async def test_get_valid_token_expired(self, kommo_auth):
        """Testa renovação automática de token expirado"""
        expired_tokens = {
            "access_token": "expired_token",
            "refresh_token": "refresh",
            "expires_at": datetime.now().timestamp() - 100  # Expirado
        }
        
        new_tokens = {
            "access_token": "new_token",
            "refresh_token": "new_refresh",
            "expires_in": 86400
        }
        
        with patch.object(kommo_auth, '_get_tokens', AsyncMock(return_value=expired_tokens)):
            with patch.object(kommo_auth, 'refresh_access_token', AsyncMock(return_value=new_tokens)):
                token = await kommo_auth.get_valid_token()
        
        assert token == "new_token"
        kommo_auth.refresh_access_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_valid_token_no_tokens(self, kommo_auth):
        """Testa erro quando não há tokens"""
        with patch.object(kommo_auth, '_get_tokens', AsyncMock(return_value=None)):
            
            with pytest.raises(Exception) as exc_info:
                await kommo_auth.get_valid_token()
            
            assert "Nenhum token encontrado" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_clear_tokens(self, kommo_auth):
        """Testa limpeza de tokens"""
        await kommo_auth._clear_tokens()
        
        kommo_auth.redis_mock.delete.assert_called_once_with("kommo:tokens")
    
    @pytest.mark.asyncio
    async def test_is_authenticated_true(self, kommo_auth):
        """Testa verificação de autenticação válida"""
        with patch.object(kommo_auth, 'get_valid_token', AsyncMock(return_value="valid_token")):
            result = await kommo_auth.is_authenticated()
        
        assert result == True
    
    @pytest.mark.asyncio
    async def test_is_authenticated_false(self, kommo_auth):
        """Testa verificação de autenticação inválida"""
        with patch.object(kommo_auth, 'get_valid_token', AsyncMock(side_effect=Exception("No token"))):
            result = await kommo_auth.is_authenticated()
        
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])