"""
Supabase Storage for AGnO Framework
====================================
Implementação customizada de storage para persistir sessões do agente no Supabase
"""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from loguru import logger
# AGnO não tem uma classe base AgentStorage genérica, vamos implementar nossa própria
# seguindo o padrão dos storages existentes (SqliteStorage, PostgresStorage)
from services.database import supabase_client


class SupabaseAgentStorage:
    """Storage implementation using Supabase for AGnO agents
    
    Implementação customizada seguindo o padrão do AGnO
    (SqliteStorage, PostgresStorage)
    """
    
    def __init__(self, table_name: str = "agent_sessions"):
        """
        Initialize Supabase storage
        
        Args:
            table_name: Nome da tabela no Supabase para armazenar sessões
        """
        self.client = supabase_client
        self.table_name = table_name
        
    async def save(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Save session data to Supabase
        
        Args:
            session_id: Unique session identifier
            data: Session data to save
        """
        try:
            # Extrair phone_number do session_id (formato: whatsapp_5511999999999)
            phone_number = session_id.replace("whatsapp_", "") if session_id.startswith("whatsapp_") else session_id
            
            # Preparar dados para salvar
            session_data = {
                'session_id': session_id,
                'phone_number': phone_number,
                'state': json.dumps(data),
                'last_interaction': datetime.now().isoformat()
            }
            
            # Upsert (insert ou update)
            result = self.client.table(self.table_name).upsert(
                session_data,
                on_conflict='session_id'
            ).execute()
            
            logger.debug(f"Session {session_id} saved to Supabase")
            
        except Exception as e:
            logger.error(f"Error saving session to Supabase: {e}")
            raise
            
    async def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data from Supabase
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data or None if not found
        """
        try:
            result = self.client.table(self.table_name)\
                .select('state')\
                .eq('session_id', session_id)\
                .single()\
                .execute()
                
            if result.data:
                return json.loads(result.data['state'])
                
            logger.debug(f"No session found for {session_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading session from Supabase: {e}")
            return None
            
    async def delete(self, session_id: str) -> None:
        """
        Delete session data from Supabase
        
        Args:
            session_id: Unique session identifier
        """
        try:
            self.client.table(self.table_name)\
                .delete()\
                .eq('session_id', session_id)\
                .execute()
                
            logger.debug(f"Session {session_id} deleted from Supabase")
            
        except Exception as e:
            logger.error(f"Error deleting session from Supabase: {e}")
            raise
            
    async def exists(self, session_id: str) -> bool:
        """
        Check if session exists in Supabase
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        try:
            result = self.client.table(self.table_name)\
                .select('id')\
                .eq('session_id', session_id)\
                .execute()
                
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error checking session existence: {e}")
            return False
            
    async def list_sessions(self, phone_number: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all sessions or sessions for a specific phone number
        
        Args:
            phone_number: Optional phone number to filter sessions
            
        Returns:
            List of session metadata
        """
        try:
            query = self.client.table(self.table_name).select('session_id, phone_number, created_at, last_interaction')
            
            if phone_number:
                query = query.eq('phone_number', phone_number)
                
            result = query.order('last_interaction', desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []
            
    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Remove sessions older than specified days
        
        Args:
            days: Number of days to keep sessions
            
        Returns:
            Number of sessions deleted
        """
        try:
            cutoff_date = datetime.now()
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            result = self.client.table(self.table_name)\
                .delete()\
                .lt('last_interaction', cutoff_date.isoformat())\
                .execute()
                
            count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {count} old sessions")
            
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0
            
    def sync_save(self, session_id: str, data: Dict[str, Any]) -> None:
        """Synchronous save - converts async to sync for AGnO compatibility"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.run_until_complete(self.save(session_id, data))
        
    def sync_load(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Synchronous load - converts async to sync for AGnO compatibility"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self.load(session_id))
        
    def sync_delete(self, session_id: str) -> None:
        """Synchronous delete - converts async to sync for AGnO compatibility"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.run_until_complete(self.delete(session_id))
        
    def sync_exists(self, session_id: str) -> bool:
        """Synchronous exists - converts async to sync for AGnO compatibility"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self.exists(session_id))