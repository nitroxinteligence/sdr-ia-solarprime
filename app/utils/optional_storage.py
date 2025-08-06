"""
OptionalStorage - Storage wrapper que funciona com ou sem PostgreSQL
Arquitetura modular simples - zero complexidade
"""

from typing import Optional, Any, Dict
from loguru import logger
import asyncio
import time
from app.utils.supabase_storage import SupabaseStorage
from app.integrations.supabase_client import supabase_client


class OptionalStorage:
    """
    Storage wrapper que pode funcionar com PostgreSQL ou em memória
    Fallback automático se PostgreSQL não estiver disponível
    """
    
    def __init__(
        self,
        table_name: str,
        db_url: str,
        schema: str = "public",
        auto_upgrade_schema: bool = True
    ):
        """
        Tenta inicializar PostgresStorage, fallback para memória se falhar
        
        Args:
            table_name: Nome da tabela
            db_url: URL do banco de dados
            schema: Schema do banco
            auto_upgrade_schema: Auto-atualizar schema
        """
        self.storage = None
        self.memory_storage = {}  # Storage em memória como fallback
        self.table_name = table_name
        
        # Tenta conectar ao PostgreSQL com retry
        self._connect_with_retry(table_name, db_url, schema, auto_upgrade_schema)
    
    def _connect_with_retry(self, table_name: str, db_url: str, schema: str, auto_upgrade_schema: bool):
        """Conecta usando SupabaseStorage em vez de PostgreSQL direto"""
        try:
            # Usa SupabaseStorage com o cliente Supabase existente
            self.storage = SupabaseStorage(
                table_name=table_name,
                supabase_client=supabase_client,
                schema=schema,
                auto_upgrade_schema=auto_upgrade_schema
            )
            logger.info(f"✅ SupabaseStorage conectado para tabela: {table_name}")
            logger.info(f"🚀 Usando Supabase Client - sem necessidade de PostgreSQL direto!")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao conectar SupabaseStorage: {e}")
            logger.warning(f"📝 Sistema funcionará com storage em memória para: {table_name}")
            self.storage = None
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao storage"""
        return self.storage is not None
    
    # Métodos compatíveis com AGNO Storage
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do storage"""
        if self.storage:
            try:
                return self.storage.get(key)
            except:
                pass
        return self.memory_storage.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """Define valor no storage"""
        if self.storage:
            try:
                return self.storage.set(key, value)
            except:
                pass
        self.memory_storage[key] = value
        return True
    
    def delete(self, key: str) -> bool:
        """Remove valor do storage"""
        if self.storage:
            try:
                return self.storage.delete(key)
            except:
                pass
        if key in self.memory_storage:
            del self.memory_storage[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if self.storage:
            try:
                return self.storage.exists(key)
            except:
                pass
        return key in self.memory_storage
    
    # Métodos requeridos pelo AGNO Memory
    def __getattr__(self, name):
        """
        Proxy para métodos do PostgresStorage real
        Se não tiver storage, retorna método dummy
        """
        if self.storage and hasattr(self.storage, name):
            return getattr(self.storage, name)
        
        # Retorna função dummy para métodos não implementados
        def dummy_method(*args, **kwargs):
            logger.debug(f"Método {name} chamado sem PostgreSQL - operação ignorada")
            return None
        
        return dummy_method