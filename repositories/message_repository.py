"""
Message Repository
==================
Repositório para operações com mensagens
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from loguru import logger

from models.message import Message, MessageCreate
from repositories.base import BaseRepository
from services.database import db


class MessageRepository(BaseRepository[Message]):
    """Repositório de Mensagens"""
    
    def __init__(self):
        super().__init__(Message, "messages")
    
    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 100
    ) -> List[Message]:
        """Lista mensagens de uma conversa"""
        try:
            result = db.messages.select("*")\
                .eq("conversation_id", str(conversation_id))\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    async def get_last_messages(
        self,
        conversation_id: UUID,
        count: int = 10
    ) -> List[Message]:
        """Obtém últimas N mensagens"""
        try:
            result = db.messages.select("*")\
                .eq("conversation_id", str(conversation_id))\
                .order("created_at", desc=True)\
                .limit(count)\
                .execute()
            
            # Reverter ordem para cronológica
            messages = [Message(**item) for item in result.data]
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error getting last messages: {e}")
            return []
    
    async def save_user_message(
        self,
        conversation_id: UUID,
        content: str,
        whatsapp_message_id: Optional[str] = None,
        media_type: Optional[str] = None,
        media_url: Optional[str] = None,
        media_data: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Salva mensagem do usuário"""
        message_data = MessageCreate(
            conversation_id=conversation_id,
            whatsapp_message_id=whatsapp_message_id,
            role="user",
            content=content,
            media_type=media_type,
            media_url=media_url,
            media_data=media_data
        )
        
        return await self.create(message_data.dict())
    
    async def save_assistant_message(
        self,
        conversation_id: UUID,
        content: str
    ) -> Message:
        """Salva mensagem do assistente"""
        message_data = MessageCreate(
            conversation_id=conversation_id,
            role="assistant",
            content=content
        )
        
        return await self.create(message_data.dict())
    
    async def get_messages_with_media(
        self,
        conversation_id: UUID
    ) -> List[Message]:
        """Lista mensagens com mídia"""
        try:
            result = db.messages.select("*")\
                .eq("conversation_id", str(conversation_id))\
                .not_.is_("media_type", None)\
                .order("created_at", desc=False)\
                .execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting messages with media: {e}")
            return []
    
    async def search_messages(
        self,
        query: str,
        conversation_id: Optional[UUID] = None
    ) -> List[Message]:
        """Busca mensagens por conteúdo"""
        try:
            search_query = db.messages.select("*")\
                .ilike("content", f"%{query}%")
            
            if conversation_id:
                search_query = search_query.eq("conversation_id", str(conversation_id))
            
            result = search_query.limit(50).execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []
    
    async def get_recent_messages(
        self,
        hours: int = 24
    ) -> List[Message]:
        """Lista mensagens recentes"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            result = db.messages.select("*")\
                .gte("created_at", cutoff_time.isoformat())\
                .order("created_at", desc=True)\
                .execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    async def count_conversation_messages(
        self,
        conversation_id: UUID,
        role: Optional[str] = None
    ) -> int:
        """Conta mensagens de uma conversa"""
        filters = {"conversation_id": str(conversation_id)}
        
        if role:
            filters["role"] = role
        
        return await self.count(filters)
    
    async def get_conversation_context(
        self,
        conversation_id: UUID,
        max_messages: int = 20
    ) -> str:
        """Obtém contexto da conversa formatado"""
        messages = await self.get_last_messages(conversation_id, max_messages)
        
        context_parts = []
        for msg in messages:
            role_label = "Cliente" if msg.role == "user" else "Luna"
            context_parts.append(f"{role_label}: {msg.content}")
        
        return "\n".join(context_parts)


# Instância global
message_repository = MessageRepository()