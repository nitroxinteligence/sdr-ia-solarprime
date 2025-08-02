"""
Message Processor for SDR Agent.

This module handles message processing, media handling, buffering,
and intelligent response generation.
"""

import asyncio
import re
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from loguru import logger

from agente.types import WhatsAppMessage, Message, MediaType
# from agente.core.humanizer import HelenHumanizer  # ❌ REMOVIDO - Evolution API faz tudo
from agente.core.context_manager import ContextManager
from agente.core.qualification_flow import QualificationFlow
from agente.services import EvolutionAPIService
from agente.repositories import MessageRepository, LeadRepository


class MessageBuffer:
    """Handles message buffering for rapid consecutive messages."""
    
    def __init__(self, buffer_window_seconds: int = 3):
        """
        Initialize message buffer.
        
        Args:
            buffer_window_seconds: Time window to buffer messages
        """
        self.buffer: Dict[str, List[WhatsAppMessage]] = {}
        self.last_message_time: Dict[str, datetime] = {}
        self.buffer_window = timedelta(seconds=buffer_window_seconds)
        self.processing_locks: Dict[str, asyncio.Lock] = {}
    
    async def add_message(self, message: WhatsAppMessage) -> bool:
        """
        Add message to buffer.
        
        Args:
            message: Message to buffer
            
        Returns:
            True if should wait for more messages, False if ready to process
        """
        phone = message.phone
        current_time = datetime.now(timezone.utc)
        
        # Initialize buffer for new phone
        if phone not in self.buffer:
            self.buffer[phone] = []
            self.processing_locks[phone] = asyncio.Lock()
        
        # Add message to buffer
        self.buffer[phone].append(message)
        self.last_message_time[phone] = current_time
        
        # Check if we should wait for more messages
        if len(self.buffer[phone]) == 1:
            # First message, wait for potential follow-ups
            return True
        
        # If messages are coming rapidly, keep buffering
        time_since_last = current_time - self.last_message_time.get(phone, current_time)
        return time_since_last < self.buffer_window
    
    async def get_buffered_messages(self, phone: str) -> List[WhatsAppMessage]:
        """
        Get and clear buffered messages for a phone.
        
        Args:
            phone: Phone number
            
        Returns:
            List of buffered messages
        """
        async with self.processing_locks.get(phone, asyncio.Lock()):
            messages = self.buffer.get(phone, [])
            self.buffer[phone] = []
            return messages
    
    def should_process(self, phone: str) -> bool:
        """
        Check if buffer should be processed.
        
        Args:
            phone: Phone number
            
        Returns:
            True if ready to process
        """
        if phone not in self.last_message_time:
            return False
        
        time_since_last = datetime.now(timezone.utc) - self.last_message_time[phone]
        return time_since_last >= self.buffer_window and len(self.buffer.get(phone, [])) > 0


class MessageProcessor:
    """Processes WhatsApp messages and generates appropriate responses."""
    
    # Message length limits
    MAX_MESSAGE_LENGTH = 4096  # WhatsApp limit
    CHUNK_SIZE = 1000  # Ideal chunk size for natural conversation
    
    # Media processing settings
    SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]
    SUPPORTED_DOCUMENT_FORMATS = [".pdf", ".doc", ".docx"]
    MAX_AUDIO_DURATION = 300  # 5 minutes
    
    def __init__(
        self,
        # humanizer: Optional[HelenHumanizer] = None,  # ❌ REMOVIDO - Evolution API faz tudo
        context_manager: Optional[ContextManager] = None,
        qualification_flow: Optional[QualificationFlow] = None,
        evolution_service: Optional[EvolutionAPIService] = None,
        message_repo: Optional[MessageRepository] = None,
        lead_repo: Optional[LeadRepository] = None
    ):
        """Initialize MessageProcessor with dependencies."""
        # self.humanizer = humanizer or HelenHumanizer()  # ❌ REMOVIDO - Evolution API faz tudo
        self.context_manager = context_manager or ContextManager()
        self.qualification_flow = qualification_flow or QualificationFlow()
        self.evolution_service = evolution_service or EvolutionAPIService()
        self.message_repo = message_repo or MessageRepository()
        self.lead_repo = lead_repo or LeadRepository()
        
        # Message buffer for handling rapid messages
        self.message_buffer = MessageBuffer()
        
        # Response cache to avoid duplicates
        self.response_cache: Dict[str, str] = {}
        self.cache_ttl = timedelta(minutes=5)
        
        logger.info("MessageProcessor initialized")
    
    async def process_incoming_message(
        self,
        whatsapp_msg: WhatsAppMessage
    ) -> Dict[str, Any]:
        """
        Process incoming WhatsApp message.
        
        Args:
            whatsapp_msg: WhatsApp message to process
            
        Returns:
            Processing result with response and metadata
        """
        try:
            # Check if message should be buffered
            should_buffer = await self.message_buffer.add_message(whatsapp_msg)
            
            if should_buffer:
                # Wait for buffer window
                await asyncio.sleep(self.message_buffer.buffer_window.total_seconds())
            
            # Get all buffered messages
            messages = await self.message_buffer.get_buffered_messages(whatsapp_msg.phone)
            if not messages:
                messages = [whatsapp_msg]
            
            # Process media if present
            media_content = None
            if messages[0].media_url:
                media_content = await self._process_media(messages[0])
            
            # Combine message texts
            combined_text = "\n".join([msg.message for msg in messages if msg.message])
            
            # Check for duplicate processing
            message_hash = self._generate_message_hash(whatsapp_msg.phone, combined_text)
            if message_hash in self.response_cache:
                logger.info(f"Duplicate message detected from {whatsapp_msg.phone}, skipping")
                return {
                    "success": True,
                    "duplicate": True,
                    "response": self.response_cache[message_hash]
                }
            
            # Build conversation context
            context = await self.context_manager.build_conversation_context(whatsapp_msg.phone)
            
            # Add current message info
            context["current_message"] = {
                "text": combined_text,
                "media_content": media_content,
                "message_count": len(messages),
                "has_media": bool(media_content)
            }
            
            # Detect message intent
            intent = self._detect_message_intent(combined_text, media_content)
            context["intent"] = intent
            
            # Process based on intent and context
            response = await self._generate_response(context)
            
            # Cache response
            self.response_cache[message_hash] = response
            self._cleanup_cache()
            
            # Save messages to database
            for msg in messages:
                await self._save_message(msg, "incoming")
            
            return {
                "success": True,
                "response": response,
                "context": context,
                "messages_processed": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error processing message from {whatsapp_msg.phone}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def chunk_message(self, text: str, max_length: int = CHUNK_SIZE) -> List[str]:
        """
        Split long message into natural chunks.
        
        Args:
            text: Text to chunk
            max_length: Maximum chunk length
            
        Returns:
            List of message chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If paragraph itself is too long, split by sentences
            if len(paragraph) > max_length:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= max_length:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
            else:
                # Try to add paragraph to current chunk
                if len(current_chunk) + len(paragraph) + 2 <= max_length:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def format_for_whatsapp(self, text: str) -> str:
        """
        Format text for WhatsApp display.
        
        Args:
            text: Text to format
            
        Returns:
            WhatsApp formatted text
        """
        # Convert markdown bold to WhatsApp bold
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
        text = re.sub(r'__(.*?)__', r'*\1*', text)
        
        # Convert markdown italic to WhatsApp italic
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'_\1_', text)
        
        # Format values and percentages in bold
        text = re.sub(r'R\$\s*[\d.,]+', lambda m: f'*{m.group()}*', text)
        text = re.sub(r'\d+%', lambda m: f'*{m.group()}*', text)
        
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Add emoji accents for key points
        text = re.sub(r'^-\s*', '• ', text, flags=re.MULTILINE)
        
        return text
    
    async def _process_media(self, message: WhatsAppMessage) -> Optional[Dict[str, Any]]:
        """Process media attachments."""
        try:
            if not message.media_url:
                return None
            
            media_type = message.media_type or self._detect_media_type(message.media_url)
            
            if media_type == MediaType.IMAGE:
                # For energy bills, extract data
                if "conta" in message.message.lower() or "fatura" in message.message.lower():
                    return {
                        "type": "energy_bill",
                        "url": message.media_url,
                        "requires_ocr": True
                    }
                else:
                    return {
                        "type": "image",
                        "url": message.media_url
                    }
            
            elif media_type == MediaType.DOCUMENT:
                return {
                    "type": "document",
                    "url": message.media_url,
                    "filename": message.media_url.split('/')[-1]
                }
            
            elif media_type == MediaType.AUDIO:
                return {
                    "type": "audio",
                    "url": message.media_url,
                    "duration": None,  # Would need to analyze
                    "requires_transcription": True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing media: {e}")
            return None
    
    def _detect_media_type(self, url: str) -> Optional[MediaType]:
        """Detect media type from URL."""
        url_lower = url.lower()
        
        if any(ext in url_lower for ext in self.SUPPORTED_IMAGE_FORMATS):
            return MediaType.IMAGE
        elif any(ext in url_lower for ext in self.SUPPORTED_DOCUMENT_FORMATS):
            return MediaType.DOCUMENT
        elif any(ext in url_lower for ext in [".mp3", ".ogg", ".wav", ".m4a"]):
            return MediaType.AUDIO
        
        return None
    
    def _detect_message_intent(self, text: str, media_content: Optional[Dict]) -> Dict[str, Any]:
        """
        Detect user intent from message.
        
        Args:
            text: Message text
            media_content: Media content if any
            
        Returns:
            Intent analysis
        """
        text_lower = text.lower()
        
        intent = {
            "type": "general",
            "confidence": 0.5,
            "entities": []
        }
        
        # Greeting patterns
        greeting_patterns = ["oi", "olá", "bom dia", "boa tarde", "boa noite", "opa", "e aí"]
        if any(pattern in text_lower for pattern in greeting_patterns):
            intent["type"] = "greeting"
            intent["confidence"] = 0.9
        
        # Question patterns
        elif "?" in text or any(q in text_lower for q in ["quanto", "como", "quando", "onde", "qual"]):
            intent["type"] = "question"
            intent["confidence"] = 0.8
            
            # Specific question types
            if "quanto" in text_lower and ("custa" in text_lower or "valor" in text_lower):
                intent["sub_type"] = "pricing"
            elif "como" in text_lower and "funciona" in text_lower:
                intent["sub_type"] = "how_it_works"
            elif "quando" in text_lower:
                intent["sub_type"] = "timing"
        
        # Energy bill value
        value_match = re.search(r'R\$\s*([\d.,]+)', text)
        if value_match:
            intent["type"] = "value_provided"
            intent["confidence"] = 0.95
            intent["entities"].append({
                "type": "monetary_value",
                "value": value_match.group(1)
            })
        
        # Contact info
        phone_pattern = r'(?:\+?55\s?)?\(?[1-9]{2}\)?\s?9?\d{4}[-\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            intent["entities"].append({
                "type": "phone",
                "value": phone_match.group()
            })
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        if email_match:
            intent["entities"].append({
                "type": "email",
                "value": email_match.group()
            })
        
        # Media intents
        if media_content:
            if media_content.get("type") == "energy_bill":
                intent["type"] = "energy_bill_provided"
                intent["confidence"] = 1.0
            elif media_content.get("type") == "audio":
                intent["type"] = "audio_message"
                intent["confidence"] = 0.9
        
        # Objections
        objection_keywords = ["caro", "não", "depois", "pensar", "dúvida", "receio", "medo"]
        if any(keyword in text_lower for keyword in objection_keywords):
            intent["type"] = "objection"
            intent["confidence"] = 0.7
        
        # Interest indicators
        interest_keywords = ["quero", "interesse", "sim", "vamos", "pode", "ótimo", "legal"]
        if any(keyword in text_lower for keyword in interest_keywords):
            intent["type"] = "interest"
            intent["confidence"] = 0.8
        
        return intent
    
    async def _generate_response(self, context: Dict[str, Any]) -> str:
        """
        Generate appropriate response based on context.
        
        This is a simplified version. In the full implementation,
        this would use the AGnO agent with all tools.
        """
        try:
            stage = context.get("stage", "INITIAL_CONTACT")
            intent = context.get("intent", {})
            current_message = context.get("current_message", {})
            
            # Get next question from qualification flow
            if "lead" in context and isinstance(context["lead"], dict) and "phone" in context["lead"]:
                # This is a placeholder - in real implementation, would get lead from DB
                next_question = self.qualification_flow.CRITERIA_QUESTIONS.get("name")
            else:
                next_question = None
            
            # Generate response based on stage and intent
            if stage == "INITIAL_CONTACT" and intent["type"] == "greeting":
                response = (
                    "Oii! Seja muito bem-vindo à Solar Prime! 😊\n\n"
                    "Meu nome é Helen Vieira, sou consultora especialista aqui da Solar Prime em Recife.\n\n"
                    "Antes de começarmos, como posso chamá-lo?"
                )
            
            elif intent["type"] == "value_provided":
                value = float(intent["entities"][0]["value"].replace(",", "."))
                if value >= 4000:
                    response = (
                        f"Nossa! *R$ {value:.2f}* por mês?! 😱\n\n"
                        "Isso é MUITO dinheiro! Com uma conta dessas, "
                        "posso te garantir uma economia de pelo menos *20%* todo mês!\n\n"
                        "Isso daria mais de *R$ {value * 0.2:.2f}* de economia mensal! "
                        "Você tem noção que em um ano isso são *R$ {value * 0.2 * 12:.2f}*?"
                    )
                else:
                    response = (
                        f"Entendi, *R$ {value:.2f}* mensais.\n\n"
                        "Para contas entre R$ 400 e R$ 4.000, temos uma solução residencial "
                        "com desconto de 12% a 15%! Ainda vale muito a pena!\n\n"
                        "Mas me conta, é para sua casa ou você tem uma empresa também?"
                    )
            
            elif intent["type"] == "objection":
                objection_response = self.qualification_flow.handle_objection(current_message["text"])
                response = objection_response or (
                    "Entendo perfeitamente sua preocupação!\n\n"
                    "Sabe, é super normal ter dúvidas. Por isso mesmo a Solar Prime tem "
                    "nota 9,64 no Reclame Aqui e já ajudou mais de 23 mil famílias!\n\n"
                    "Que tal conversarmos sem compromisso para eu esclarecer tudo?"
                )
            
            elif next_question:
                response = next_question
            
            else:
                response = (
                    "Que legal! Estou aqui para ajudar você a economizar até 95% "
                    "na sua conta de energia! ⚡\n\n"
                    "Me conta, qual o valor médio da sua conta de luz?"
                )
            
            return self.format_for_whatsapp(response)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Desculpe, tive um problema técnico. Pode repetir sua mensagem?"
    
    async def _save_message(self, whatsapp_msg: WhatsAppMessage, direction: str) -> None:
        """Save message to database."""
        try:
            # Get or create conversation
            # This is simplified - in real implementation would use repositories
            
            message = Message(
                conversation_id="temp-id",  # Would get from conversation repo
                sender_name=whatsapp_msg.name or whatsapp_msg.phone,
                sender_phone=whatsapp_msg.phone,
                content=whatsapp_msg.message,
                media_url=whatsapp_msg.media_url,
                media_type=whatsapp_msg.media_type,
                direction=direction,
                platform="whatsapp",
                external_id=whatsapp_msg.message_id,
                timestamp=datetime.now(timezone.utc)
            )
            
            # In real implementation, would save via repository
            logger.debug(f"Message saved: {message.external_id}")
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
    
    def _generate_message_hash(self, phone: str, text: str) -> str:
        """Generate hash for duplicate detection."""
        content = f"{phone}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        # This would be implemented with proper TTL checking
        if len(self.response_cache) > 1000:
            # Simple cleanup - in production would check timestamps
            self.response_cache.clear()
    
    async def send_response_with_humanization(
        self,
        phone: str,
        response: str,
        emotional_state: str = "neutral",
        is_first_message: bool = False
    ) -> Dict[str, Any]:
        """
        Send response with humanization effects.
        
        Args:
            phone: Recipient phone
            response: Response text
            emotional_state: Current emotional state
            is_first_message: Whether this is first message
            
        Returns:
            Send result
        """
        try:
            # Humanize the response
            chunks = self.humanizer.humanize_response(
                response,
                emotional_state,
                is_first_message
            )
            
            results = []
            
            for chunk_data in chunks:
                # Pre-pause
                if chunk_data.get("pre_pause", 0) > 0:
                    await asyncio.sleep(chunk_data["pre_pause"])
                
                # Show typing
                await self.evolution_service.send_typing(
                    phone=phone,
                    duration=int(chunk_data["typing_delay"] * 1000)  # Convert to ms
                )
                
                # Wait for typing duration
                await asyncio.sleep(chunk_data["typing_delay"])
                
                # Send chunk
                result = await self.evolution_service.send_text_message(
                    phone=phone,
                    message=chunk_data["text"]
                )
                results.append(result)
                
                # Post-pause
                if chunk_data.get("post_pause", 0) > 0:
                    await asyncio.sleep(chunk_data["post_pause"])
            
            return {
                "success": True,
                "chunks_sent": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending humanized response: {e}")
            return {
                "success": False,
                "error": str(e)
            }