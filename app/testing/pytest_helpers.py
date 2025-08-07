"""
🧪 PYTEST HELPERS - Fixtures para usar sistema mock
Facilita uso do sistema mock em testes pytest
"""
import pytest
from .mock_supabase import mock_supabase_context

@pytest.fixture
def mock_supabase():
    """
    Fixture pytest para sistema mock Supabase
    
    Usage:
        def test_my_function(mock_supabase):
            # Testa função que usa Supabase
            db = SupabaseClient()
            result = db.get_conversation_by_phone("5511999887766")
            assert result is not None
    """
    with mock_supabase_context() as mock_db:
        yield mock_db

@pytest.fixture
def mock_supabase_with_custom_data():
    """
    Fixture com dados customizáveis
    
    Usage:
        def test_custom_data(mock_supabase_with_custom_data):
            mock_db = mock_supabase_with_custom_data
            
            # Adiciona dados específicos
            mock_db.data['leads'].append({
                'id': 'test-lead-123',
                'name': 'Lead Teste',
                'phone_number': '5511111111111'
            })
            
            # Testa com dados customizados
            db = SupabaseClient()
            result = db.get_lead_by_phone("5511111111111")
            assert result['name'] == 'Lead Teste'
    """
    with mock_supabase_context() as mock_db:
        # Limpa dados padrão se necessário
        yield mock_db

# Decorator para tests que precisam de mock automático
def with_mock_supabase(func):
    """
    Decorator que automaticamente ativa mock
    
    Usage:
        @with_mock_supabase
        async def test_my_feature():
            db = SupabaseClient()  # Automaticamente usa mock
            result = await db.get_conversation_by_phone("123")
            assert result is not None
    """
    def wrapper(*args, **kwargs):
        with mock_supabase_context():
            return func(*args, **kwargs)
    return wrapper

# Classe para testes que herdam setup automático
class MockSupabaseTestCase:
    """
    Classe base para testes que precisam de mock automático
    
    Usage:
        class TestMyService(MockSupabaseTestCase):
            async def test_service_method(self):
                # Mock já está ativo
                db = SupabaseClient()
                result = await db.get_lead_by_phone("123")
                assert result is not None
    """
    
    def setup_method(self):
        """Setup automático do mock"""
        self._mock_context = mock_supabase_context()
        self.mock_db = self._mock_context.__enter__()
    
    def teardown_method(self):
        """Cleanup automático do mock"""
        if hasattr(self, '_mock_context'):
            self._mock_context.__exit__(None, None, None)

# Utilitários para assertions específicas
class MockAssertions:
    """Assertions específicas para testes com mock"""
    
    @staticmethod
    def assert_conversation_exists(phone: str, mock_db):
        """Verifica se conversa existe no mock"""
        conversations = mock_db.data.get('conversations', [])
        conv = next((c for c in conversations if c['phone_number'] == phone), None)
        assert conv is not None, f"Conversa não encontrada para {phone}"
        return conv
    
    @staticmethod
    def assert_lead_exists(phone: str, mock_db):
        """Verifica se lead existe no mock"""
        leads = mock_db.data.get('leads', [])
        lead = next((l for l in leads if l['phone_number'] == phone), None)
        assert lead is not None, f"Lead não encontrado para {phone}"
        return lead
    
    @staticmethod
    def assert_knowledge_not_empty(mock_db):
        """Verifica se knowledge base não está vazia"""
        knowledge = mock_db.data.get('knowledge_base', [])
        assert len(knowledge) > 0, "Knowledge base está vazia"
        return knowledge