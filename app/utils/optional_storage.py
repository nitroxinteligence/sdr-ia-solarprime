"""
OptionalStorage - Storage wrapper que funciona com ou sem PostgreSQL
Arquitetura modular simples - zero complexidade
"""

from typing import Optional, Any, Dict
from loguru import logger
from agno.storage.postgres import PostgresStorage
import asyncio
import time


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
        """Tenta conectar ao PostgreSQL com retry e backoff exponencial"""
        max_retries = 5
        retry_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                logger.info(f"📡 Tentando conectar ao PostgreSQL (tentativa {attempt + 1}/{max_retries})...")
                
                self.storage = PostgresStorage(
                    table_name=table_name,
                    db_url=db_url,
                    schema=schema,
                    auto_upgrade_schema=auto_upgrade_schema
                )
                
                logger.info(f"✅ PostgresStorage conectado para tabela: {table_name}")
                return  # Sucesso!
                
            except Exception as e:
                error_msg = str(e)[:200]
                
                # Se for erro de IPv6, mostra mensagem específica
                if "2a05:d016" in error_msg or "IPv6" in error_msg.lower():
                    logger.warning(f"⚠️ Erro de conexão IPv6 detectado. Usando pooler na porta 6543 deve resolver.")
                
                logger.warning(f"⚠️ PostgreSQL não disponível (tentativa {attempt + 1}/{max_retries}): {error_msg}...")
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Backoff exponencial
                    logger.info(f"⏳ Aguardando {wait_time:.1f}s antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Falha ao conectar ao PostgreSQL após {max_retries} tentativas.")
                    logger.warning(f"📝 Sistema funcionará com storage em memória para: {table_name}")
                    self.storage = None
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao PostgreSQL"""
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