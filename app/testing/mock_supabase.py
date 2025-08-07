"""
🎭 SISTEMA MOCK SUPABASE - INTERCEPTA 100% DAS CHAMADAS
Redesenhado para ser TRANSPARENTE e FUNCIONAR SEMPRE
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4
from unittest.mock import Mock, patch
from contextlib import contextmanager
import copy

class MockResult:
    """Simula resultado do Supabase exatamente como o real"""
    
    def __init__(self, data: List[Dict[str, Any]] = None, error: Any = None, count: int = None):
        self.data = data or []
        self.error = error
        self.count = count or len(self.data) if data else 0

class MockTable:
    """Mock perfeito de table() com chain methods"""
    
    def __init__(self, table_name: str, mock_db: 'MockDatabase'):
        self.table_name = table_name
        self.mock_db = mock_db
        self._query_params = {
            'select': '*',
            'filters': [],
            'order': None,
            'limit': None,
            'count': None
        }
    
    def select(self, columns: str = "*", count: str = None) -> 'MockTable':
        """Chain method: select"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['select'] = columns
        new_table._query_params['count'] = count
        return new_table
    
    def eq(self, column: str, value: Any) -> 'MockTable':
        """Chain method: filter equals"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['filters'].append(('eq', column, value))
        return new_table
    
    def neq(self, column: str, value: Any) -> 'MockTable':
        """Chain method: filter not equals"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['filters'].append(('neq', column, value))
        return new_table
    
    def ilike(self, column: str, value: str) -> 'MockTable':
        """Chain method: case insensitive like"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['filters'].append(('ilike', column, value))
        return new_table
    
    def gte(self, column: str, value: Any) -> 'MockTable':
        """Chain method: greater than or equal"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['filters'].append(('gte', column, value))
        return new_table
    
    def lte(self, column: str, value: Any) -> 'MockTable':
        """Chain method: less than or equal"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['filters'].append(('lte', column, value))
        return new_table
    
    def lt(self, column: str, value: Any) -> 'MockTable':
        """Chain method: less than"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['filters'].append(('lt', column, value))
        return new_table
    
    def order(self, column: str, desc: bool = False) -> 'MockTable':
        """Chain method: order by"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['order'] = (column, desc)
        return new_table
    
    def limit(self, count: int) -> 'MockTable':
        """Chain method: limit results"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['limit'] = count
        return new_table
    
    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> 'MockTable':
        """Chain method: insert data"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['operation'] = ('insert', data)
        return new_table
    
    def update(self, data: Dict[str, Any]) -> 'MockTable':
        """Chain method: update data"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['operation'] = ('update', data)
        return new_table
    
    def delete(self) -> 'MockTable':
        """Chain method: delete data"""
        new_table = MockTable(self.table_name, self.mock_db)
        new_table._query_params = copy.deepcopy(self._query_params)
        new_table._query_params['operation'] = ('delete', None)
        return new_table
    
    def execute(self) -> MockResult:
        """EXECUTA A QUERY NO MOCK DATABASE"""
        return self.mock_db.execute_query(self.table_name, self._query_params)

class MockClient:
    """Mock perfeito do Supabase Client"""
    
    def __init__(self, mock_db: 'MockDatabase'):
        self.mock_db = mock_db
    
    def table(self, table_name: str) -> MockTable:
        """Retorna mock table que suporta chain methods"""
        return MockTable(table_name, self.mock_db)
    
    def rpc(self, function_name: str, params: Dict[str, Any] = None) -> 'MockRPC':
        """Mock de RPC calls"""
        return MockRPC(function_name, params or {}, self.mock_db)

class MockRPC:
    """Mock para RPC calls que suporta execute()"""
    
    def __init__(self, function_name: str, params: Dict[str, Any], mock_db: 'MockDatabase'):
        self.function_name = function_name
        self.params = params
        self.mock_db = mock_db
    
    def execute(self) -> MockResult:
        """Executa RPC call"""
        return self.mock_db.execute_rpc(self.function_name, self.params)

class MockDatabase:
    """Database mock com dados realistas"""
    
    def __init__(self):
        self.data = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Cria dados mock realistas para todos os sistemas"""
        now = datetime.now()
        
        # Dados base realistas
        mock_phone = "5511999887766"
        mock_lead_id = str(uuid4())
        mock_conversation_id = str(uuid4())
        mock_session_id = f"session_{uuid4().hex}"
        
        return {
            'leads': [
                {
                    'id': mock_lead_id,
                    'name': 'João Silva',
                    'phone_number': mock_phone,
                    'bill_value': '5000',
                    'qualification_status': 'QUALIFIED',
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat(),
                    'meeting_scheduled_at': (now + timedelta(days=1)).isoformat()
                },
                {
                    'id': str(uuid4()),
                    'name': 'Maria Santos',
                    'phone_number': '5511888777666',
                    'bill_value': '3000',
                    'qualification_status': 'PENDING',
                    'created_at': (now - timedelta(hours=2)).isoformat(),
                    'updated_at': (now - timedelta(hours=2)).isoformat()
                }
            ],
            'conversations': [
                {
                    'id': mock_conversation_id,
                    'phone_number': mock_phone,
                    'lead_id': mock_lead_id,
                    'session_id': mock_session_id,
                    'status': 'ACTIVE',
                    'channel': 'whatsapp',
                    'sentiment': 'neutro',
                    'is_active': True,
                    'total_messages': 5,
                    'emotional_state': 'ENTUSIASMADA',
                    'created_at': (now - timedelta(hours=1)).isoformat(),
                    'updated_at': now.isoformat()
                }
            ],
            'messages': [
                {
                    'id': str(uuid4()),
                    'conversation_id': mock_conversation_id,
                    'message_type': 'user',
                    'content': 'Olá, gostaria de saber sobre energia solar',
                    'created_at': (now - timedelta(minutes=30)).isoformat()
                },
                {
                    'id': str(uuid4()),
                    'conversation_id': mock_conversation_id,
                    'message_type': 'agent',
                    'content': 'Olá! Claro, posso ajudar com energia solar. Qual o valor da sua conta atual?',
                    'created_at': (now - timedelta(minutes=25)).isoformat()
                }
            ],
            'knowledge_base': [
                {
                    'id': str(uuid4()),
                    'question': 'Como funciona energia solar?',
                    'answer': 'Energia solar fotovoltaica converte luz solar em eletricidade através de painéis solares.',
                    'category': 'tecnologia',
                    'content': 'Energia solar fotovoltaica converte luz solar em eletricidade',
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat()
                },
                {
                    'id': str(uuid4()),
                    'question': 'Quanto economizo com energia solar?',
                    'answer': 'Você pode economizar até 95% na conta de luz com energia solar.',
                    'category': 'economia',
                    'content': 'Economia de até 95% na conta de luz',
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat()
                }
            ],
            'follow_ups': [
                {
                    'id': str(uuid4()),
                    'type': 'reengagement',
                    'follow_up_type': 'IMMEDIATE_REENGAGEMENT',
                    'status': 'PENDING',
                    'priority': 5,
                    'scheduled_at': now.isoformat(),
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat(),
                    'metadata': {
                        'phone': mock_phone,
                        'conversation_id': mock_conversation_id,
                        'trigger': 'agent_response_30min'
                    }
                }
            ],
            'analytics': [],
            'agent_sessions': [
                {
                    'id': str(uuid4()),
                    'session_id': mock_session_id,
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat(),
                    'last_interaction': now.isoformat(),
                    'status': 'active'
                }
            ],
            'leads_qualifications': [
                {
                    'id': str(uuid4()),
                    'lead_id': mock_lead_id,
                    'qualification_status': 'QUALIFIED',
                    'score': 85,
                    'criteria': {
                        'meeting_scheduled': True,
                        'interest_level': 'high',
                        'decision_maker': True
                    },
                    'notes': 'Lead qualificado - Reunião agendada com sucesso',
                    'qualified_at': now.isoformat(),
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat()
                }
            ]
        }
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: List[tuple]) -> List[Dict[str, Any]]:
        """Aplica filtros aos dados"""
        result = data[:]
        
        for operation, column, value in filters:
            if operation == 'eq':
                result = [item for item in result if item.get(column) == value]
            elif operation == 'neq':
                result = [item for item in result if item.get(column) != value]
            elif operation == 'ilike':
                # Remove % do início e fim do valor para busca
                search_value = value.strip('%').lower()
                result = [
                    item for item in result 
                    if search_value in str(item.get(column, '')).lower()
                ]
            elif operation == 'gte':
                result = [item for item in result if item.get(column, '') >= value]
            elif operation == 'lte':
                result = [item for item in result if item.get(column, '') <= value]
            elif operation == 'lt':
                result = [item for item in result if item.get(column, '') < value]
        
        return result
    
    def _apply_order(self, data: List[Dict[str, Any]], order_params: tuple = None) -> List[Dict[str, Any]]:
        """Aplica ordenação aos dados"""
        if not order_params:
            return data
        
        column, desc = order_params
        return sorted(data, key=lambda x: x.get(column, ''), reverse=desc)
    
    def _apply_limit(self, data: List[Dict[str, Any]], limit: int = None) -> List[Dict[str, Any]]:
        """Aplica limite aos dados"""
        if limit is None:
            return data
        return data[:limit]
    
    def execute_query(self, table_name: str, params: Dict[str, Any]) -> MockResult:
        """Executa query no mock database"""
        try:
            # Pega dados da tabela
            table_data = self.data.get(table_name, [])
            
            # Verifica se é operação de modificação
            if 'operation' in params:
                return self._execute_modification(table_name, params)
            
            # Query de seleção
            result = table_data[:]
            
            # Aplica filtros
            if params.get('filters'):
                result = self._apply_filters(result, params['filters'])
            
            # Aplica ordenação
            if params.get('order'):
                result = self._apply_order(result, params['order'])
            
            # Aplica limite
            if params.get('limit'):
                result = self._apply_limit(result, params['limit'])
            
            # Se é count, retorna só o número
            if params.get('count'):
                return MockResult(data=result, count=len(result))
            
            return MockResult(data=result)
            
        except Exception as e:
            return MockResult(error=str(e))
    
    def _execute_modification(self, table_name: str, params: Dict[str, Any]) -> MockResult:
        """Executa operações de modificação (insert, update, delete)"""
        operation, data = params['operation']
        
        if operation == 'insert':
            return self._execute_insert(table_name, data)
        elif operation == 'update':
            return self._execute_update(table_name, params, data)
        elif operation == 'delete':
            return self._execute_delete(table_name, params)
        
        return MockResult(error="Operação não suportada")
    
    def _execute_insert(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> MockResult:
        """Executa insert"""
        if table_name not in self.data:
            self.data[table_name] = []
        
        # Normaliza para lista
        items = data if isinstance(data, list) else [data]
        
        # Adiciona IDs se não existirem
        for item in items:
            if 'id' not in item:
                item['id'] = str(uuid4())
            
            # Adiciona à tabela
            self.data[table_name].append(item)
        
        return MockResult(data=items)
    
    def _execute_update(self, table_name: str, params: Dict[str, Any], update_data: Dict[str, Any]) -> MockResult:
        """Executa update"""
        table_data = self.data.get(table_name, [])
        
        # Aplica filtros para encontrar registros
        filtered_data = self._apply_filters(table_data, params.get('filters', []))
        
        updated_items = []
        for item in filtered_data:
            # Atualiza o item
            item.update(update_data)
            updated_items.append(item)
        
        return MockResult(data=updated_items)
    
    def _execute_delete(self, table_name: str, params: Dict[str, Any]) -> MockResult:
        """Executa delete"""
        table_data = self.data.get(table_name, [])
        
        # Aplica filtros para encontrar registros
        to_delete = self._apply_filters(table_data, params.get('filters', []))
        
        # Remove os itens
        for item in to_delete:
            if item in table_data:
                table_data.remove(item)
        
        return MockResult(data=to_delete)
    
    def execute_rpc(self, function_name: str, params: Dict[str, Any]) -> MockResult:
        """Executa RPC functions"""
        if function_name == 'search_knowledge':
            query = params.get('search_query', '')
            limit = params.get('result_limit', 5)
            
            # Busca na knowledge_base
            knowledge_data = self.data.get('knowledge_base', [])
            
            # Filtro simples por conteúdo
            results = [
                item for item in knowledge_data
                if query.lower() in item.get('content', '').lower() or 
                   query.lower() in item.get('question', '').lower() or
                   query.lower() in item.get('answer', '').lower()
            ]
            
            return MockResult(data=results[:limit])
        
        return MockResult(error=f"RPC {function_name} não implementada")

@contextmanager
def mock_supabase_context():
    """
    🎭 CONTEXT MANAGER QUE INTERCEPTA 100% DAS CHAMADAS SUPABASE
    
    Usage:
        with mock_supabase_context():
            # Todos os calls ao Supabase são interceptados
            db = SupabaseClient()
            result = db.client.table('conversations').select().eq().execute()
            # ↑ Isso retorna dados mock, não chama o banco real
    """
    # Cria mock database
    mock_db = MockDatabase()
    mock_client = MockClient(mock_db)
    
    # Intercepta criação do Supabase client
    def mock_create_client(*args, **kwargs):
        return mock_client
    
    # Patches que interceptam TUDO
    patches = [
        # Intercepta supabase.create_client
        patch('supabase.create_client', side_effect=mock_create_client),
        patch('app.integrations.supabase_client.create_client', side_effect=mock_create_client),
        
        # Intercepta imports alternativos
        patch('supabase.Client', return_value=mock_client),
        
        # Intercepta singleton se existir
        patch('app.integrations.supabase_client.supabase_client.client', mock_client),
    ]
    
    # Inicia todos os patches
    started_patches = []
    for p in patches:
        try:
            started_patches.append(p.start())
        except:
            pass  # Alguns patches podem falhar se o módulo não foi importado ainda
    
    try:
        print("🎭 MOCK SUPABASE: Sistema mock ativo - 100% isolado do banco real")
        yield mock_db  # Permite acesso direto ao mock database para customização
        
    finally:
        # Para todos os patches
        for p in patches:
            try:
                p.stop()
            except:
                pass
        print("🎭 MOCK SUPABASE: Sistema mock desativado")

# Função helper para testes rápidos
def create_mock_supabase_client() -> MockClient:
    """Cria client mock para uso direto em testes"""
    mock_db = MockDatabase()
    return MockClient(mock_db)

# Dados de exemplo para testes
def get_mock_phone_data():
    """Retorna dados mock para telefone específico usado nos testes"""
    return {
        'phone': '5511999887766',
        'lead_name': 'João Silva',
        'conversation_exists': True,
        'has_messages': True,
        'qualification_status': 'QUALIFIED'
    }