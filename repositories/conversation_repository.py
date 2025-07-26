"""
Conversation Repository
=======================
Repositório para operações com conversas
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from loguru import logger

from models.conversation import Conversation, ConversationCreate, ConversationUpdate
from repositories.base import BaseRepository
from services.database import db


class ConversationRepository(BaseRepository[Conversation]):
    """Repositório de Conversas"""
    
    def __init__(self):
        super().__init__(Conversation, "conversations")
    
    async def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Busca conversa por session_id"""
        try:
            result = db.conversations.select("*").eq("session_id", session_id).execute()
            
            if result.data and len(result.data) > 0:
                return Conversation(**result.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation by session_id: {e}")
            raise
    
    async def get_active_by_lead(self, lead_id: UUID) -> Optional[Conversation]:
        """Busca conversa ativa do lead"""
        try:
            result = db.conversations.select("*")\
                .eq("lead_id", str(lead_id))\
                .eq("is_active", True)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return Conversation(**result.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting active conversation: {e}")
            return None
    
    async def get_lead_conversations(self, lead_id: UUID) -> List[Conversation]:
        """Lista todas as conversas de um lead"""
        return await self.get_all(
            filters={"lead_id": str(lead_id)}
        )
    
    async def increment_message_count(self, conversation_id: UUID) -> Optional[Conversation]:
        """Incrementa contador de mensagens"""
        try:
            # Buscar conversa atual
            conversation = await self.get_by_id(conversation_id)
            if not conversation:
                return None
            
            # Incrementar contador
            new_count = conversation.total_messages + 1
            
            return await self.update(
                conversation_id,
                {"total_messages": new_count}
            )
            
        except Exception as e:
            logger.error(f"Error incrementing message count: {e}")
            return None
    
    async def end_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Finaliza uma conversa"""
        return await self.update(
            conversation_id,
            {
                "is_active": False,
                "ended_at": datetime.utcnow().isoformat()
            }
        )
    
    async def update_stage_and_sentiment(
        self,
        conversation_id: UUID,
        stage: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> Optional[Conversation]:
        """Atualiza estágio e sentimento da conversa"""
        update_data = {}
        
        if stage:
            update_data["current_stage"] = stage
        
        if sentiment:
            update_data["sentiment"] = sentiment
        
        if update_data:
            return await self.update(conversation_id, update_data)
        
        return None
    
    async def get_active_conversations(self) -> List[Conversation]:
        """Lista conversas ativas"""
        return await self.get_all(
            filters={"is_active": True}
        )
    
    async def get_conversations_by_stage(self, stage: str) -> List[Conversation]:
        """Lista conversas por estágio"""
        return await self.get_all(
            filters={"current_stage": stage}
        )
    
    async def create_or_resume(self, lead_id: UUID, session_id: str) -> Conversation:
        """Cria nova conversa ou retoma a existente"""
        try:
            # Verificar se já existe conversa ativa
            active = await self.get_active_by_lead(lead_id)
            
            if active:
                # Atualizar session_id se mudou
                if active.session_id != session_id:
                    return await self.update(
                        active.id,
                        {"session_id": session_id}
                    )
                return active
            
            # Criar nova conversa
            conversation_data = ConversationCreate(
                lead_id=lead_id,
                session_id=session_id,
                current_stage="INITIAL_CONTACT"
            )
            
            # Converter UUID para string no dict
            data_dict = conversation_data.dict()
            data_dict['lead_id'] = str(data_dict['lead_id'])
            
            return await self.create(data_dict)
            
        except Exception as e:
            logger.error(f"Error in create_or_resume conversation: {e}")
            raise


# Instância global
conversation_repository = ConversationRepository()