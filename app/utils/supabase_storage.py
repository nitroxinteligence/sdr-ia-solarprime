"""
SupabaseStorage - Adapter que implementa interface do AGNO Storage usando Supabase
Elimina a necessidade de conexão direta com PostgreSQL
"""

from typing import Optional, Any, Dict
from loguru import logger
import json
import asyncio
from datetime import datetime


class SupabaseStorage:
    """
    Storage adapter que usa Supabase Client em vez de PostgreSQL direto
    Implementa a mesma interface que PostgresStorage do AGNO
    """
    
    def __init__(
        self,
        table_name: str,
        supabase_client: Any,
        schema: str = "public",
        auto_upgrade_schema: bool = True
    ):
        """
        Inicializa o storage usando Supabase Client
        
        Args:
            table_name: Nome da tabela (usado como prefixo nas chaves)
            supabase_client: Instância do SupabaseClient
            schema: Schema do banco (mantido por compatibilidade)
            auto_upgrade_schema: Auto-atualizar schema (mantido por compatibilidade)
        """
        self.table_name = table_name
        self.supabase_client = supabase_client
        self.session_prefix = f"{table_name}:"
        
        # Inicializado com sucesso (sem logs repetitivos)
    
    def _get_session_id(self, key: str) -> str:
        """Gera ID único para a sessão baseado na chave"""
        return f"{self.session_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do storage"""
        try:
            # Usa coroutine em thread separada se necessário
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Se já está em um loop, cria task
                future = asyncio.ensure_future(
                    self.supabase_client.get_agent_session(self._get_session_id(key))
                )
                session = asyncio.run_coroutine_threadsafe(future, loop).result()
            else:
                # Se não há loop rodando, executa diretamente
                session = asyncio.run(
                    self.supabase_client.get_agent_session(self._get_session_id(key))
                )
            
            if session and 'data' in session:
                # Desserializa o JSON armazenado
                return json.loads(session['data'])
            
            return None
            
        except Exception as e:
            logger.debug(f"Erro ao buscar {key}: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """Define valor no storage"""
        try:
            session_data = {
                'session_id': self._get_session_id(key),
                'agent_type': self.table_name,
                'data': json.dumps(value, default=str),  # Serializa para JSON
                'metadata': {
                    'key': key,
                    'table_name': self.table_name,
                    'updated_at': datetime.now().isoformat()
                }
            }
            
            # Usa coroutine em thread separada se necessário
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.ensure_future(
                    self.supabase_client.save_agent_session(session_data)
                )
                result = asyncio.run_coroutine_threadsafe(future, loop).result()
            else:
                result = asyncio.run(
                    self.supabase_client.save_agent_session(session_data)
                )
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Erro ao salvar {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do storage"""
        try:
            session_id = self._get_session_id(key)
            
            # Deleta usando Supabase Client
            result = self.supabase_client.client.table('agent_sessions').delete().eq(
                'session_id', session_id
            ).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.debug(f"Erro ao deletar {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        return self.get(key) is not None
    
    def list_keys(self, prefix: Optional[str] = None) -> list:
        """Lista todas as chaves (com prefixo opcional)"""
        try:
            # Busca todas as sessões deste tipo
            result = self.supabase_client.client.table('agent_sessions').select(
                "session_id"
            ).ilike('session_id', f'{self.session_prefix}%').execute()
            
            keys = []
            for item in result.data:
                session_id = item['session_id']
                # Remove o prefixo para retornar apenas a chave
                key = session_id.replace(self.session_prefix, '', 1)
                
                if prefix is None or key.startswith(prefix):
                    keys.append(key)
            
            return keys
            
        except Exception as e:
            logger.error(f"Erro ao listar chaves: {e}")
            return []
    
    def clear(self) -> bool:
        """Limpa todo o storage desta tabela"""
        try:
            # Deleta todas as sessões com este prefixo
            result = self.supabase_client.client.table('agent_sessions').delete().ilike(
                'session_id', f'{self.session_prefix}%'
            ).execute()
            
            logger.info(f"🗑️ {len(result.data)} sessões removidas de {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar storage: {e}")
            return False
    
    # Métodos adicionais para compatibilidade com AGNO
    def __getattr__(self, name):
        """
        Proxy para métodos não implementados
        Retorna função dummy para manter compatibilidade
        """
        def dummy_method(*args, **kwargs):
            logger.debug(f"Método {name} chamado em SupabaseStorage - não implementado")
            return None
        
        return dummy_method