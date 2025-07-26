"""
Database Enhanced Service
=========================
Serviço de banco de dados com pool de conexões e otimizações
"""

import os
import asyncio
from typing import Optional, Dict, Any, List, Type, TypeVar
from contextlib import asynccontextmanager
from datetime import datetime
import asyncpg
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from loguru import logger
from dotenv import load_dotenv
import backoff

load_dotenv()

T = TypeVar('T')


class DatabasePool:
    """Pool de conexões PostgreSQL direto para operações de alta performance"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = os.getenv("DATABASE_URL")
        self._lock = asyncio.Lock()
        
        # Configurações do pool
        self.pool_config = {
            'min_size': int(os.getenv("DB_POOL_MIN_SIZE", "10")),
            'max_size': int(os.getenv("DB_POOL_MAX_SIZE", "50")),
            'max_queries': int(os.getenv("DB_POOL_MAX_QUERIES", "50000")),
            'max_inactive_connection_lifetime': float(os.getenv("DB_POOL_MAX_INACTIVE_LIFETIME", "300")),
            'command_timeout': float(os.getenv("DB_COMMAND_TIMEOUT", "10")),
        }
        
        self._health_check_task: Optional[asyncio.Task] = None
    
    @backoff.on_exception(
        backoff.expo,
        (asyncpg.PostgresError, OSError),
        max_tries=3,
        max_time=10
    )
    async def _create_pool(self) -> asyncpg.Pool:
        """Cria pool de conexões com retry"""
        if not self.database_url:
            raise ValueError("DATABASE_URL não configurado")
        
        logger.info(f"Criando pool de conexões PostgreSQL (min={self.pool_config['min_size']}, max={self.pool_config['max_size']})")
        
        return await asyncpg.create_pool(
            self.database_url,
            min_size=self.pool_config['min_size'],
            max_size=self.pool_config['max_size'],
            max_queries=self.pool_config['max_queries'],
            max_inactive_connection_lifetime=self.pool_config['max_inactive_connection_lifetime'],
            command_timeout=self.pool_config['command_timeout'],
            # Configurações de performance
            server_settings={
                'jit': 'off',  # Desabilitar JIT para queries simples
                'application_name': 'sdr_solarprime'
            }
        )
    
    async def initialize(self):
        """Inicializa o pool de conexões"""
        if self.pool is not None:
            return
        
        async with self._lock:
            if self.pool is not None:
                return
            
            try:
                self.pool = await self._create_pool()
                
                # Testar conexão
                async with self.pool.acquire() as conn:
                    version = await conn.fetchval('SELECT version()')
                    logger.success(f"✅ Pool PostgreSQL conectado: {version.split(',')[0]}")
                
                # Iniciar health check
                if not self._health_check_task:
                    self._health_check_task = asyncio.create_task(self._health_check_loop())
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar pool PostgreSQL: {e}")
                raise
    
    async def _health_check_loop(self):
        """Loop de verificação de saúde do pool"""
        while True:
            await asyncio.sleep(30)
            
            if not self.pool:
                continue
            
            try:
                async with self.pool.acquire() as conn:
                    await conn.fetchval('SELECT 1')
                
                logger.debug(f"Pool health check OK - Conexões: {self.pool.get_size()}/{self.pool_config['max_size']}")
                
            except Exception as e:
                logger.error(f"Pool health check falhou: {e}")
    
    async def close(self):
        """Fecha o pool de conexões"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Pool PostgreSQL fechado")
    
    @asynccontextmanager
    async def acquire(self):
        """Adquire uma conexão do pool"""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do pool"""
        if not self.pool:
            return {"status": "not_initialized"}
        
        return {
            "status": "active",
            "size": self.pool.get_size(),
            "max_size": self.pool_config['max_size'],
            "min_size": self.pool_config['min_size'],
            "free_connections": self.pool.get_idle_size(),
            "used_connections": self.pool.get_size() - self.pool.get_idle_size()
        }


class DatabaseEnhancedService:
    """Serviço de banco de dados otimizado com Supabase e pool nativo"""
    
    _instance: Optional['DatabaseEnhancedService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._supabase_client: Optional[Client] = None
            self._pool = DatabasePool()
            self._initialized = True
            self._init_lock = asyncio.Lock()
    
    async def initialize(self):
        """Inicializa serviços de banco de dados"""
        async with self._init_lock:
            # Inicializar Supabase
            if self._supabase_client is None:
                await self._initialize_supabase()
            
            # Inicializar pool PostgreSQL
            await self._pool.initialize()
    
    async def _initialize_supabase(self):
        """Inicializa cliente Supabase com configurações otimizadas"""
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not key:
                raise ValueError("Credenciais Supabase não encontradas")
            
            # Configurações otimizadas
            options = ClientOptions(
                auto_refresh_token=True,
                persist_session=True,
                local_storage={},  # Usar storage em memória
                flow_type="pkce"
            )
            
            self._supabase_client = create_client(url, key, options)
            logger.success("✅ Cliente Supabase inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Falha ao inicializar Supabase: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Retorna cliente Supabase (compatibilidade)"""
        if self._supabase_client is None:
            raise RuntimeError("DatabaseEnhancedService não foi inicializado. Chame initialize() primeiro.")
        return self._supabase_client
    
    @property
    def pool(self) -> DatabasePool:
        """Retorna pool de conexões PostgreSQL"""
        return self._pool
    
    # Métodos de tabela (compatibilidade com código existente)
    
    @property
    def leads(self):
        """Acesso à tabela leads via Supabase"""
        return self.client.table("leads")
    
    @property
    def conversations(self):
        """Acesso à tabela conversations via Supabase"""
        return self.client.table("conversations")
    
    @property
    def messages(self):
        """Acesso à tabela messages via Supabase"""
        return self.client.table("messages")
    
    @property
    def qualifications(self):
        """Acesso à tabela lead_qualifications via Supabase"""
        return self.client.table("lead_qualifications")
    
    @property
    def follow_ups(self):
        """Acesso à tabela follow_ups via Supabase"""
        return self.client.table("follow_ups")
    
    @property
    def analytics(self):
        """Acesso à tabela analytics via Supabase"""
        return self.client.table("analytics")
    
    # Métodos otimizados usando pool direto
    
    async def execute_query(
        self,
        query: str,
        *args,
        fetch_one: bool = False
    ) -> Any:
        """Executa query usando pool de conexões"""
        async with self._pool.acquire() as conn:
            if fetch_one:
                return await conn.fetchrow(query, *args)
            return await conn.fetch(query, *args)
    
    async def execute_many(
        self,
        query: str,
        args_list: List[tuple]
    ) -> None:
        """Executa múltiplas queries em batch"""
        async with self._pool.acquire() as conn:
            await conn.executemany(query, args_list)
    
    async def bulk_insert(
        self,
        table: str,
        records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Inserção em massa otimizada"""
        if not records:
            return []
        
        # Preparar colunas e valores
        columns = list(records[0].keys())
        values = []
        
        for record in records:
            values.append([record.get(col) for col in columns])
        
        # Query de inserção
        placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
        column_names = ', '.join(columns)
        
        query = f"""
            INSERT INTO {table} ({column_names})
            VALUES ({placeholders})
            RETURNING *
        """
        
        async with self._pool.acquire() as conn:
            # Usar prepared statement para melhor performance
            stmt = await conn.prepare(query)
            
            results = []
            for value_tuple in values:
                result = await stmt.fetchrow(*value_tuple)
                results.append(dict(result))
            
            return results
    
    async def find_by_id(
        self,
        table: str,
        id: Any,
        id_column: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """Busca otimizada por ID"""
        query = f"SELECT * FROM {table} WHERE {id_column} = $1"
        
        result = await self.execute_query(query, id, fetch_one=True)
        return dict(result) if result else None
    
    async def find_many(
        self,
        table: str,
        conditions: Dict[str, Any],
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Busca otimizada com condições"""
        # Construir WHERE clause
        where_parts = []
        values = []
        
        for i, (column, value) in enumerate(conditions.items(), 1):
            where_parts.append(f"{column} = ${i}")
            values.append(value)
        
        where_clause = " AND ".join(where_parts) if where_parts else "1=1"
        
        # Query completa
        query = f"""
            SELECT * FROM {table}
            WHERE {where_clause}
            {f'ORDER BY {order_by}' if order_by else ''}
            LIMIT ${len(values)+1} OFFSET ${len(values)+2}
        """
        
        values.extend([limit, offset])
        
        results = await self.execute_query(query, *values)
        return [dict(row) for row in results]
    
    async def count(
        self,
        table: str,
        conditions: Optional[Dict[str, Any]] = None
    ) -> int:
        """Contagem otimizada"""
        if conditions:
            where_parts = []
            values = []
            
            for i, (column, value) in enumerate(conditions.items(), 1):
                where_parts.append(f"{column} = ${i}")
                values.append(value)
            
            where_clause = " WHERE " + " AND ".join(where_parts)
            query = f"SELECT COUNT(*) FROM {table}{where_clause}"
            result = await self.execute_query(query, *values, fetch_one=True)
        else:
            query = f"SELECT COUNT(*) FROM {table}"
            result = await self.execute_query(query, fetch_one=True)
        
        return result['count']
    
    async def update_by_id(
        self,
        table: str,
        id: Any,
        updates: Dict[str, Any],
        id_column: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """Atualização otimizada por ID"""
        if not updates:
            return None
        
        # Construir SET clause
        set_parts = []
        values = []
        
        for i, (column, value) in enumerate(updates.items(), 1):
            set_parts.append(f"{column} = ${i}")
            values.append(value)
        
        # Adicionar updated_at se existir
        if "updated_at" not in updates:
            set_parts.append(f"updated_at = ${len(values)+1}")
            values.append(datetime.utcnow())
        
        values.append(id)
        
        query = f"""
            UPDATE {table}
            SET {', '.join(set_parts)}
            WHERE {id_column} = ${len(values)}
            RETURNING *
        """
        
        result = await self.execute_query(query, *values, fetch_one=True)
        return dict(result) if result else None
    
    async def delete_by_id(
        self,
        table: str,
        id: Any,
        id_column: str = "id"
    ) -> bool:
        """Deleção otimizada por ID"""
        query = f"DELETE FROM {table} WHERE {id_column} = $1 RETURNING {id_column}"
        
        result = await self.execute_query(query, id, fetch_one=True)
        return result is not None
    
    # Métodos utilitários
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do banco de dados"""
        health = {
            "supabase": False,
            "postgresql": False,
            "pool_stats": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Verificar Supabase
        try:
            result = self.leads.select("id").limit(1).execute()
            health["supabase"] = True
        except Exception as e:
            health["supabase_error"] = str(e)
        
        # Verificar PostgreSQL direto
        try:
            await self.execute_query("SELECT 1", fetch_one=True)
            health["postgresql"] = True
            health["pool_stats"] = await self._pool.get_pool_stats()
        except Exception as e:
            health["postgresql_error"] = str(e)
        
        health["healthy"] = health["supabase"] and health["postgresql"]
        
        return health
    
    async def close(self):
        """Fecha conexões"""
        await self._pool.close()
        logger.info("DatabaseEnhancedService fechado")
    
    def handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Trata erros de banco de dados (compatibilidade)"""
        logger.error(f"Database error in {operation}: {error}")
        
        error_message = str(error)
        
        if "duplicate key" in error_message:
            return {
                "error": "duplicate_entry",
                "message": "Registro já existe"
            }
        elif "foreign key" in error_message:
            return {
                "error": "invalid_reference",
                "message": "Referência inválida"
            }
        elif "not found" in error_message:
            return {
                "error": "not_found",
                "message": "Registro não encontrado"
            }
        else:
            return {
                "error": "database_error",
                "message": "Erro ao acessar banco de dados"
            }


# Instância global
db_enhanced = DatabaseEnhancedService()