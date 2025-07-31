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
    
    async def create_or_resume(self, lead_id: UUID, session_id: str) -> Optional[Conversation]:
        """Cria nova conversa ou retoma a existente"""
        try:
            # Verificar se já existe conversa ativa
            active = await self.get_active_by_lead(lead_id)
            
            if active:
                # Atualizar session_id se mudou
                if active.session_id != session_id:
                    updated = await self.update(
                        active.id,
                        {"session_id": session_id}
                    )
                    return updated if updated else active
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
            
            # Garantir que o ID seja gerado se não existir
            if 'id' not in data_dict:
                from uuid import uuid4
                data_dict['id'] = str(uuid4())
            
            created = await self.create(data_dict)
            if not created:
                logger.error(f"Failed to create conversation for lead {lead_id}")
                return None
                
            logger.info(f"Created new conversation {created.id} for lead {lead_id}")
            return created
            
        except Exception as e:
            logger.error(f"Error in create_or_resume conversation: {e}", exc_info=True)
            # Tentar buscar conversa existente em caso de erro na criação
            try:
                existing = await self.get_active_by_lead(lead_id)
                if existing:
                    logger.info(f"Returning existing conversation {existing.id} after create error")
                    return existing
            except:
                pass
            return None
    
    async def reset_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Reseta uma conversa para o estado inicial"""
        try:
            return await self.update(
                conversation_id,
                {
                    "current_stage": "INITIAL_CONTACT",
                    "sentiment": "neutro",
                    "total_messages": 0,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")
            return None
    
    async def get_conversation_by_phone(self, phone: str) -> Optional[Conversation]:
        """Busca conversa ativa por número de telefone"""
        try:
            # Primeiro buscar o lead pelo telefone
            from repositories.lead_repository import lead_repository
            lead = await lead_repository.get_lead_by_phone(phone)
            
            if not lead:
                return None
            
            # Buscar conversa ativa do lead
            return await self.get_active_by_lead(lead.id)
            
        except Exception as e:
            logger.error(f"Error getting conversation by phone: {e}")
            return None


# Instância global
conversation_repository = ConversationRepository()