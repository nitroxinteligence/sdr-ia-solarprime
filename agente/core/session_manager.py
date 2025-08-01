"""
Session Manager for SDR Agent.

This module manages conversation sessions, handles timeouts,
and maintains session state across multiple interactions.
"""

import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone, timedelta
from enum import Enum
from loguru import logger

from agente.types import Conversation, Lead
from agente.repositories import (
    ConversationRepository,
    LeadRepository,
    MessageRepository,
    FollowUpRepository
)
from agente.core.context_manager import ContextManager
from agente.core.qualification_flow import QualificationStage


class SessionState(Enum):
    """Possible session states."""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionManager:
    """Manages conversation sessions for the SDR Agent."""
    
    # Session configuration
    DEFAULT_SESSION_TIMEOUT = timedelta(minutes=30)
    IDLE_WARNING_TIME = timedelta(minutes=20)
    MAX_SESSION_DURATION = timedelta(hours=2)
    
    # Follow-up timing
    FIRST_FOLLOWUP_DELAY = timedelta(minutes=30)
    SECOND_FOLLOWUP_DELAY = timedelta(hours=24)
    THIRD_FOLLOWUP_DELAY = timedelta(days=3)
    
    # Session limits
    MAX_MESSAGES_PER_SESSION = 100
    MAX_CONCURRENT_SESSIONS = 50
    
    def __init__(
        self,
        conversation_repo: Optional[ConversationRepository] = None,
        lead_repo: Optional[LeadRepository] = None,
        message_repo: Optional[MessageRepository] = None,
        followup_repo: Optional[FollowUpRepository] = None,
        context_manager: Optional[ContextManager] = None
    ):
        """Initialize SessionManager with repositories."""
        self.conversation_repo = conversation_repo or ConversationRepository()
        self.lead_repo = lead_repo or LeadRepository()
        self.message_repo = message_repo or MessageRepository()
        self.followup_repo = followup_repo or FollowUpRepository()
        self.context_manager = context_manager or ContextManager()
        
        # Active sessions cache
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Session cleanup task
        self.cleanup_task = None
        
        logger.info("SessionManager initialized")
    
    async def start(self):
        """Start session manager and cleanup task."""
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        logger.info("SessionManager started with cleanup task")
    
    async def stop(self):
        """Stop session manager and cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("SessionManager stopped")
    
    async def get_or_create_session(self, phone: str) -> Dict[str, Any]:
        """
        Get existing session or create new one.
        
        Args:
            phone: Phone number
            
        Returns:
            Session data dictionary
        """
        try:
            # Check active sessions cache
            if phone in self.active_sessions:
                session = self.active_sessions[phone]
                
                # Check if session is still valid
                if self._is_session_valid(session):
                    session["last_activity"] = datetime.now(timezone.utc)
                    logger.debug(f"Returning cached session for {phone}")
                    return session
                else:
                    # Session expired, remove from cache
                    del self.active_sessions[phone]
            
            # Get or create conversation
            conversation = await self.conversation_repo.get_or_create(phone)
            
            # Get lead data
            lead = await self.lead_repo.get_by_phone(phone)
            
            # Check if we should resume previous session
            if conversation and self._should_resume_session(conversation):
                session = await self._resume_session(conversation, lead)
            else:
                session = await self._create_new_session(phone, lead)
            
            # Cache session
            self.active_sessions[phone] = session
            
            logger.info(
                f"Session for {phone}: "
                f"id={session['conversation_id']}, "
                f"state={session['state']}, "
                f"message_count={session['message_count']}"
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting/creating session for {phone}: {e}")
            # Return basic session on error
            return {
                "phone": phone,
                "conversation_id": None,
                "state": SessionState.ACTIVE.value,
                "created_at": datetime.now(timezone.utc),
                "last_activity": datetime.now(timezone.utc),
                "message_count": 0,
                "error": str(e)
            }
    
    async def update_session(self, phone: str, data: Dict[str, Any]) -> None:
        """
        Update session data.
        
        Args:
            phone: Phone number
            data: Data to update
        """
        try:
            session = await self.get_or_create_session(phone)
            
            # Update session data
            session.update(data)
            session["last_activity"] = datetime.now(timezone.utc)
            
            # Update message count if message was added
            if "message_added" in data:
                session["message_count"] = session.get("message_count", 0) + 1
            
            # Check session limits
            if session["message_count"] >= self.MAX_MESSAGES_PER_SESSION:
                logger.warning(f"Session {phone} reached message limit")
                session["state"] = SessionState.COMPLETED.value
            
            # Update conversation in database
            if session.get("conversation_id"):
                await self.conversation_repo.update_last_message_at(
                    session["conversation_id"],
                    session["last_activity"]
                )
            
            logger.debug(f"Updated session for {phone}: {data}")
            
        except Exception as e:
            logger.error(f"Error updating session for {phone}: {e}")
    
    async def end_session(
        self,
        phone: str,
        reason: str = "completed"
    ) -> None:
        """
        End a session.
        
        Args:
            phone: Phone number
            reason: Reason for ending session
        """
        try:
            session = self.active_sessions.get(phone)
            if not session:
                return
            
            # Update session state
            if reason == "completed":
                session["state"] = SessionState.COMPLETED.value
            elif reason == "timeout":
                session["state"] = SessionState.EXPIRED.value
            elif reason == "abandoned":
                session["state"] = SessionState.ABANDONED.value
            
            session["ended_at"] = datetime.now(timezone.utc)
            
            # Get conversation and lead
            conversation = await self.conversation_repo.get_by_id(
                session["conversation_id"]
            )
            lead = await self.lead_repo.get_by_phone(phone)
            
            # Schedule follow-ups if needed
            if lead and session["state"] != SessionState.COMPLETED.value:
                await self._schedule_session_followups(lead, conversation, reason)
            
            # Remove from active sessions
            del self.active_sessions[phone]
            
            logger.info(
                f"Ended session for {phone}: "
                f"reason={reason}, "
                f"duration={(session['ended_at'] - session['created_at']).total_seconds()}s"
            )
            
        except Exception as e:
            logger.error(f"Error ending session for {phone}: {e}")
    
    def get_session_stats(self, phone: str) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Args:
            phone: Phone number
            
        Returns:
            Session statistics
        """
        session = self.active_sessions.get(phone, {})
        
        if not session:
            return {"active": False}
        
        now = datetime.now(timezone.utc)
        duration = now - session.get("created_at", now)
        idle_time = now - session.get("last_activity", now)
        
        return {
            "active": True,
            "state": session.get("state", SessionState.ACTIVE.value),
            "duration_seconds": duration.total_seconds(),
            "idle_seconds": idle_time.total_seconds(),
            "message_count": session.get("message_count", 0),
            "is_idle": idle_time > self.IDLE_WARNING_TIME,
            "is_expired": not self._is_session_valid(session)
        }
    
    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(self.active_sessions)
    
    async def broadcast_to_active_sessions(
        self,
        message: str,
        filter_func: Optional[callable] = None
    ) -> int:
        """
        Broadcast message to active sessions.
        
        Args:
            message: Message to broadcast
            filter_func: Optional filter function
            
        Returns:
            Number of sessions broadcasted to
        """
        count = 0
        
        for _, session in self.active_sessions.items():
            if filter_func and not filter_func(session):
                continue
            
            # This would send the message via WhatsApp service
            # For now, just count
            # TODO: Implement actual message sending using 'message' parameter
            count += 1
        
        logger.info(f"Broadcasted to {count} active sessions")
        return count
    
    def _is_session_valid(self, session: Dict[str, Any]) -> bool:
        """Check if session is still valid."""
        now = datetime.now(timezone.utc)
        
        # Check if session expired
        last_activity = session.get("last_activity", now)
        if now - last_activity > self.DEFAULT_SESSION_TIMEOUT:
            return False
        
        # Check if session exceeded max duration
        created_at = session.get("created_at", now)
        if now - created_at > self.MAX_SESSION_DURATION:
            return False
        
        # Check session state
        state = session.get("state", SessionState.ACTIVE.value)
        if state in [SessionState.EXPIRED.value, SessionState.COMPLETED.value]:
            return False
        
        return True
    
    def _should_resume_session(self, conversation: Conversation) -> bool:
        """Check if should resume previous session."""
        if not conversation.last_message_at:
            return False
        
        time_since_last = datetime.now(timezone.utc) - conversation.last_message_at
        
        # Resume if last message was within session timeout
        return time_since_last < self.DEFAULT_SESSION_TIMEOUT
    
    async def _create_new_session(
        self,
        phone: str,
        lead: Optional[Lead]
    ) -> Dict[str, Any]:
        """Create new session."""
        # Create new conversation
        conversation = await self.conversation_repo.create(
            phone=phone,
            lead_id=lead.id if lead else None,
            platform="whatsapp",
            metadata={
                "session_started": datetime.now(timezone.utc).isoformat(),
                "initial_stage": QualificationStage.INITIAL_CONTACT.value
            }
        )
        
        session = {
            "phone": phone,
            "conversation_id": conversation.id,
            "lead_id": lead.id if lead else None,
            "state": SessionState.ACTIVE.value,
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "message_count": 0,
            "context": {
                "stage": QualificationStage.INITIAL_CONTACT.value,
                "is_new_lead": lead is None,
                "qualification_score": 0
            }
        }
        
        logger.info(f"Created new session for {phone}")
        return session
    
    async def _resume_session(
        self,
        conversation: Conversation,
        lead: Optional[Lead]
    ) -> Dict[str, Any]:
        """Resume existing session."""
        # Get message count
        messages = await self.message_repo.get_conversation_messages(
            conversation_id=conversation.id,
            limit=1
        )
        message_count = len(messages)
        
        # Get current context
        context = await self.context_manager.build_conversation_context(
            conversation.phone
        )
        
        session = {
            "phone": conversation.phone,
            "conversation_id": conversation.id,
            "lead_id": lead.id if lead else None,
            "state": SessionState.ACTIVE.value,
            "created_at": conversation.created_at,
            "last_activity": datetime.now(timezone.utc),
            "resumed_at": datetime.now(timezone.utc),
            "message_count": message_count,
            "context": {
                "stage": context.get("stage", QualificationStage.INITIAL_CONTACT.value),
                "qualification_progress": context.get("qualification_progress", {}),
                "emotional_state": context.get("emotional_state", {})
            }
        }
        
        logger.info(f"Resumed session for {conversation.phone}")
        return session
    
    async def _schedule_session_followups(
        self,
        lead: Lead,
        conversation: Optional[Conversation],
        reason: str
    ) -> None:
        """Schedule follow-ups for ended session."""
        try:
            # Determine follow-up message based on reason
            if reason == "timeout":
                message = (
                    f"Oi {lead.name or 'amigo(a)'}! Vi que você precisou sair... "
                    "Fico à disposição para continuar nossa conversa quando quiser! "
                    "Tem alguma dúvida sobre energia solar que posso esclarecer?"
                )
                delay = self.FIRST_FOLLOWUP_DELAY
            elif reason == "abandoned":
                message = (
                    f"Olá {lead.name or 'amigo(a)'}! "
                    "Percebi que não conseguimos concluir nossa conversa... "
                    "Que tal retormarmos? Tenho ótimas notícias sobre economia "
                    "na conta de luz!"
                )
                delay = self.SECOND_FOLLOWUP_DELAY
            else:
                return  # No follow-up for other reasons
            
            # Schedule follow-up
            await self.followup_repo.schedule(
                lead_id=lead.id,
                scheduled_for=datetime.now(timezone.utc) + delay,
                message=message,
                attempt_number=1,
                metadata={
                    "session_end_reason": reason,
                    "conversation_id": conversation.id if conversation else None
                }
            )
            
            logger.info(
                f"Scheduled follow-up for {lead.phone} "
                f"in {delay.total_seconds()/60:.0f} minutes"
            )
            
        except Exception as e:
            logger.error(f"Error scheduling session follow-ups: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                expired_phones = []
                
                for phone, session in self.active_sessions.items():
                    if not self._is_session_valid(session):
                        expired_phones.append(phone)
                
                # End expired sessions
                for phone in expired_phones:
                    await self.end_session(phone, "timeout")
                
                if expired_phones:
                    logger.info(f"Cleaned up {len(expired_phones)} expired sessions")
                
            except asyncio.CancelledError:
                logger.info("Session cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
    
    async def get_session_history(
        self,
        phone: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get session history for a phone number.
        
        Args:
            phone: Phone number
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            # Get lead
            lead = await self.lead_repo.get_by_phone(phone)
            if not lead:
                return []
            
            # Get conversations
            # Note: This assumes conversation repo has a method to get by lead
            # In real implementation, would need to add this method
            conversations = []  # Placeholder
            
            history = []
            for conv in conversations[:limit]:
                # Get message count
                messages = await self.message_repo.get_conversation_messages(
                    conversation_id=conv.id,
                    limit=1
                )
                
                history.append({
                    "conversation_id": conv.id,
                    "started_at": conv.created_at,
                    "last_message_at": conv.last_message_at,
                    "message_count": len(messages),
                    "metadata": conv.metadata
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting session history for {phone}: {e}")
            return []