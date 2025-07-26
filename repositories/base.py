"""
Base Repository
===============
Repositório base com operações CRUD comuns
"""

from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from uuid import UUID
from loguru import logger
from pydantic import BaseModel

from services.database import db

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    """Repositório base com operações CRUD"""
    
    def __init__(self, model: Type[T], table_name: str):
        self.model = model
        self.table_name = table_name
        self.table = getattr(db, table_name)
    
    async def create(self, data: Dict[str, Any]) -> Optional[T]:
        """Cria novo registro"""
        try:
            result = self.table.insert(data).execute()
            
            if result.data:
                logger.info(f"Created {self.table_name} record: {result.data[0].get('id')}")
                return self.model(**result.data[0])
            
            return None
            
        except Exception as e:
            error_info = db.handle_error(e, f"create_{self.table_name}")
            logger.error(f"Error creating {self.table_name}: {error_info}")
            raise
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Busca por ID"""
        try:
            result = self.table.select("*").eq("id", str(id)).execute()
            
            if result.data and len(result.data) > 0:
                return self.model(**result.data[0])
            
            return None
            
        except Exception as e:
            error_info = db.handle_error(e, f"get_{self.table_name}")
            logger.error(f"Error getting {self.table_name}: {error_info}")
            raise
    
    async def get_all(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """Lista registros com filtros opcionais"""
        try:
            query = self.table.select("*")
            
            # Aplicar filtros
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)
            
            # Aplicar paginação
            query = query.limit(limit).offset(offset)
            
            # Ordenar por created_at desc
            query = query.order("created_at", desc=True)
            
            result = query.execute()
            
            return [self.model(**item) for item in result.data]
            
        except Exception as e:
            error_info = db.handle_error(e, f"list_{self.table_name}")
            logger.error(f"Error listing {self.table_name}: {error_info}")
            return []
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """Atualiza registro"""
        try:
            # Remover campos None
            update_data = {k: v for k, v in data.items() if v is not None}
            
            # Adicionar updated_at
            from datetime import datetime
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.table.update(update_data).eq("id", str(id)).execute()
            
            if result.data:
                logger.info(f"Updated {self.table_name} record: {id}")
                return self.model(**result.data[0])
            
            return None
            
        except Exception as e:
            error_info = db.handle_error(e, f"update_{self.table_name}")
            logger.error(f"Error updating {self.table_name}: {error_info}")
            raise
    
    async def delete(self, id: UUID) -> bool:
        """Deleta registro"""
        try:
            result = self.table.delete().eq("id", str(id)).execute()
            
            if result.data:
                logger.info(f"Deleted {self.table_name} record: {id}")
                return True
            
            return False
            
        except Exception as e:
            error_info = db.handle_error(e, f"delete_{self.table_name}")
            logger.error(f"Error deleting {self.table_name}: {error_info}")
            return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Conta registros"""
        try:
            query = self.table.select("id", count="exact")
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)
            
            result = query.execute()
            
            return result.count or 0
            
        except Exception as e:
            error_info = db.handle_error(e, f"count_{self.table_name}")
            logger.error(f"Error counting {self.table_name}: {error_info}")
            return 0