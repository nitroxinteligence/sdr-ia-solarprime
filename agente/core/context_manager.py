"""
Context Manager for SDR Agent conversations.

This module manages conversation context, tracks qualification progress,
and analyzes emotional states to provide intelligent conversation flow.
"""

import re
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime, timedelta
from loguru import logger

# Avoid circular imports
if TYPE_CHECKING:
    from agente.repositories import (
        MessageRepository,
        ConversationRepository,
        LeadRepository
    )
    from agente.types import Message, Lead, Conversation


class ContextManager:
    """Manages conversation context and qualification tracking for SDR Agent."""
    
    # Qualification stages
    STAGES = {
        "INITIAL_CONTACT": "Contato inicial",
        "IDENTIFICATION": "Identificação",
        "QUALIFICATION": "Qualificação",
        "DISCOVERY": "Descoberta",
        "PRESENTATION": "Apresentação",
        "OBJECTION_HANDLING": "Tratamento de objeções",
        "SCHEDULING": "Agendamento",
        "FOLLOW_UP": "Follow-up"
    }
    
    # Keywords for emotional state analysis
    POSITIVE_KEYWORDS = [
        "interessante", "legal", "ótimo", "bom", "quero", "sim", "claro",
        "perfeito", "maravilha", "top", "show", "bacana", "gostei",
        "adorei", "fantástico", "excelente", "com certeza", "vamos"
    ]
    
    NEGATIVE_KEYWORDS = [
        "não", "nunca", "ruim", "péssimo", "horrível", "caro", "difícil",
        "complicado", "dúvida", "problema", "chato", "desisti", "cansei",
        "sem tempo", "ocupado", "depois", "talvez", "acho que não"
    ]
    
    URGENCY_KEYWORDS = [
        "urgente", "rápido", "logo", "agora", "hoje", "amanhã", "preciso",
        "necessito", "correndo", "pressa", "quanto antes", "imediato"
    ]
    
    OBJECTION_PATTERNS = [
        r"muito caro",
        r"não tenho (dinheiro|grana|verba)",
        r"já tenho (energia solar|placa|sistema)",
        r"não (confio|acredito)",
        r"é golpe",
        r"não funciona",
        r"minha conta (é baixa|não compensa)",
        r"moro de aluguel",
        r"vou mudar",
        r"não sou (dono|proprietário)",
        r"preciso (pensar|conversar|analisar)"
    ]
    
    def __init__(
        self,
        message_repo: Optional["MessageRepository"] = None,
        conversation_repo: Optional["ConversationRepository"] = None,
        lead_repo: Optional["LeadRepository"] = None
    ):
        """Initialize ContextManager with repositories."""
        # Lazy import to avoid circular dependencies
        if message_repo is None:
            from agente.repositories import MessageRepository
            message_repo = MessageRepository()
        if conversation_repo is None:
            from agente.repositories import ConversationRepository
            conversation_repo = ConversationRepository()
        if lead_repo is None:
            from agente.repositories import LeadRepository
            lead_repo = LeadRepository()
            
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo
        self.lead_repo = lead_repo
        
        logger.info("ContextManager initialized")
    
    async def get_last_100_messages(self, phone: str) -> List["Message"]:
        """
        Get last 100 messages from a lead.
        
        Args:
            phone: Lead's phone number
            
        Returns:
            List of last 100 messages ordered by timestamp
        """
        try:
            # Get conversation
            conversation = await self.conversation_repo.get_by_phone(phone)
            if not conversation:
                return []
            
            # Get messages
            messages = await self.message_repo.get_conversation_messages(
                conversation_id=conversation.id,
                limit=100
            )
            
            # Sort by timestamp
            messages.sort(key=lambda m: m.timestamp)
            
            logger.debug(f"Retrieved {len(messages)} messages for {phone}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages for {phone}: {e}")
            return []
    
    async def get_lead_context(self, phone: str) -> Dict[str, Any]:
        """
        Get complete lead context including CRM data.
        
        Args:
            phone: Lead's phone number
            
        Returns:
            Dictionary with lead data, interactions, and CRM info
        """
        try:
            # Get lead
            lead = await self.lead_repo.get_by_phone(phone)
            if not lead:
                return {}
            
            # Build context
            context = {
                "id": lead.id,
                "phone": lead.phone,
                "name": lead.name,
                "email": lead.email,
                "stage": lead.stage,
                "status": lead.status,
                "score": lead.score,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at,
                "metadata": lead.metadata or {},
                "interactions": {
                    "total_messages": 0,
                    "last_interaction": None,
                    "first_interaction": lead.created_at
                }
            }
            
            # Add qualification data
            if lead.metadata:
                context["qualification"] = {
                    "valor_conta": lead.metadata.get("valor_conta"),
                    "tipo_imovel": lead.metadata.get("tipo_imovel"),
                    "e_decisor": lead.metadata.get("e_decisor"),
                    "tem_usina_propria": lead.metadata.get("tem_usina_propria"),
                    "tem_contrato_vigente": lead.metadata.get("tem_contrato_vigente"),
                    "solucao_interesse": lead.metadata.get("solucao_interesse")
                }
            
            # Add CRM data if available
            if lead.kommo_lead_id:
                context["crm"] = {
                    "kommo_lead_id": lead.kommo_lead_id,
                    "pipeline_status": lead.metadata.get("pipeline_status"),
                    "responsible_user": lead.metadata.get("responsible_user")
                }
            
            # Get interaction stats
            messages = await self.get_last_100_messages(phone)
            if messages:
                context["interactions"]["total_messages"] = len(messages)
                context["interactions"]["last_interaction"] = messages[-1].timestamp
            
            logger.debug(f"Built lead context for {phone}: {context}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting lead context for {phone}: {e}")
            return {}
    
    def detect_conversation_stage(
        self,
        messages: List["Message"],
        lead: "Lead"
    ) -> str:
        """
        Detect current conversation stage based on messages and lead data.
        
        Args:
            messages: List of conversation messages
            lead: "Lead" object
            
        Returns:
            Current stage name
        """
        try:
            # Check lead metadata for collected info
            metadata = lead.metadata or {}
            
            # If we have a meeting scheduled, we're in follow-up
            if metadata.get("meeting_scheduled"):
                return "FOLLOW_UP"
            
            # If we're handling objections
            if metadata.get("has_objections") and not metadata.get("objections_handled"):
                return "OBJECTION_HANDLING"
            
            # Check qualification criteria
            has_name = bool(lead.name)
            has_value = bool(metadata.get("valor_conta"))
            has_decisor_info = metadata.get("e_decisor") is not None
            has_solution_interest = bool(metadata.get("solucao_interesse"))
            has_availability = bool(metadata.get("disponibilidade_reuniao"))
            
            # Determine stage based on collected information
            if not has_name:
                return "INITIAL_CONTACT"
            
            if has_name and not has_value:
                return "IDENTIFICATION"
            
            if has_value and not has_decisor_info:
                return "QUALIFICATION"
            
            if has_decisor_info and not has_solution_interest:
                return "DISCOVERY"
            
            if has_solution_interest and not has_availability:
                return "PRESENTATION"
            
            if has_availability:
                return "SCHEDULING"
            
            # Default to qualification if we have some info
            return "QUALIFICATION"
            
        except Exception as e:
            logger.error(f"Error detecting conversation stage: {e}")
            return "INITIAL_CONTACT"
    
    def analyze_emotional_state(self, messages: List["Message"]) -> Dict[str, Any]:
        """
        Analyze lead's emotional state from recent messages.
        
        Args:
            messages: List of messages to analyze
            
        Returns:
            Dictionary with interest level, urgency, and sentiment
        """
        try:
            # Get last 10 lead messages
            lead_messages = [
                m for m in messages[-20:] 
                if m.direction == "incoming" and m.content
            ][-10:]
            
            if not lead_messages:
                return {
                    "interesse_level": 5,
                    "urgencia": "média",
                    "sentimento": "neutro"
                }
            
            # Analyze sentiment
            positive_count = 0
            negative_count = 0
            urgency_count = 0
            
            for msg in lead_messages:
                content_lower = msg.content.lower()
                
                # Count positive keywords
                for keyword in self.POSITIVE_KEYWORDS:
                    if keyword in content_lower:
                        positive_count += 1
                
                # Count negative keywords
                for keyword in self.NEGATIVE_KEYWORDS:
                    if keyword in content_lower:
                        negative_count += 1
                
                # Count urgency keywords
                for keyword in self.URGENCY_KEYWORDS:
                    if keyword in content_lower:
                        urgency_count += 1
            
            # Calculate scores
            total_keywords = positive_count + negative_count
            if total_keywords == 0:
                sentiment = "neutro"
                interest_level = 5
            else:
                positive_ratio = positive_count / total_keywords
                if positive_ratio > 0.7:
                    sentiment = "positivo"
                    interest_level = min(10, 7 + int(positive_ratio * 3))
                elif positive_ratio < 0.3:
                    sentiment = "negativo"
                    interest_level = max(1, 3 - int((1 - positive_ratio) * 2))
                else:
                    sentiment = "neutro"
                    interest_level = 5
            
            # Determine urgency
            if urgency_count >= 3:
                urgency = "alta"
            elif urgency_count >= 1:
                urgency = "média"
            else:
                urgency = "baixa"
            
            # Adjust interest based on response time
            if len(lead_messages) >= 2:
                avg_response_time = self._calculate_avg_response_time(messages)
                if avg_response_time < timedelta(minutes=5):
                    interest_level = min(10, interest_level + 1)
                elif avg_response_time > timedelta(hours=1):
                    interest_level = max(1, interest_level - 1)
            
            result = {
                "interesse_level": interest_level,
                "urgencia": urgency,
                "sentimento": sentiment,
                "details": {
                    "positive_keywords": positive_count,
                    "negative_keywords": negative_count,
                    "urgency_keywords": urgency_count,
                    "messages_analyzed": len(lead_messages)
                }
            }
            
            logger.debug(f"Emotional state analysis: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing emotional state: {e}")
            return {
                "interesse_level": 5,
                "urgencia": "média",
                "sentimento": "neutro"
            }
    
    def track_qualification_progress(self, lead: "Lead") -> Dict[str, Any]:
        """
        Track qualification progress and suggest next steps.
        
        Args:
            lead: "Lead" object to analyze
            
        Returns:
            Dictionary with progress and missing information
        """
        try:
            metadata = lead.metadata or {}
            
            # Define qualification criteria
            criteria = {
                "conta_acima_4000": {
                    "value": metadata.get("valor_conta", 0) >= 400,
                    "field": "valor_conta",
                    "question": "Qual o valor médio da sua conta de energia?"
                },
                "e_decisor": {
                    "value": metadata.get("e_decisor", False),
                    "field": "e_decisor",
                    "question": "Você é o responsável pelas decisões sobre energia na sua casa/empresa?"
                },
                "tem_usina_propria": {
                    "value": not metadata.get("tem_usina_propria", True),
                    "field": "tem_usina_propria",
                    "question": "Você já possui sistema de energia solar instalado?"
                },
                "tem_contrato_vigente": {
                    "value": not metadata.get("tem_contrato_vigente", True),
                    "field": "tem_contrato_vigente",
                    "question": "Você tem algum contrato de energia vigente com outra empresa?"
                },
                "demonstra_interesse": {
                    "value": metadata.get("demonstra_interesse", False),
                    "field": "demonstra_interesse",
                    "question": None  # This is inferred from behavior
                }
            }
            
            # Calculate progress
            completed = sum(1 for c in criteria.values() if c["value"])
            total = len(criteria)
            progress_percent = int((completed / total) * 100)
            
            # Find missing information
            missing = []
            next_question = None
            
            for key, criterion in criteria.items():
                if not criterion["value"] and criterion["question"]:
                    missing.append(key)
                    if not next_question:
                        next_question = criterion["question"]
            
            # Check if lead is qualified
            is_qualified = (
                criteria["conta_acima_4000"]["value"] and
                criteria["e_decisor"]["value"] and
                criteria["tem_usina_propria"]["value"] and
                criteria["tem_contrato_vigente"]["value"]
            )
            
            result = {
                "completed": progress_percent,
                "is_qualified": is_qualified,
                "criteria": {k: v["value"] for k, v in criteria.items()},
                "missing": missing,
                "next_question": next_question,
                "total_criteria": total,
                "completed_criteria": completed
            }
            
            logger.debug(f"Qualification progress for {lead.phone}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking qualification progress: {e}")
            return {
                "completed": 0,
                "is_qualified": False,
                "criteria": {},
                "missing": [],
                "next_question": None
            }
    
    def extract_key_information(self, messages: List["Message"]) -> Dict[str, Any]:
        """
        Extract key information from messages using patterns.
        
        Args:
            messages: List of messages to analyze
            
        Returns:
            Dictionary with extracted information
        """
        try:
            extracted = {
                "nome": None,
                "valor_conta": None,
                "tipo_imovel": None,
                "objecoes": [],
                "tem_interesse_real": False,
                "telefones_adicionais": [],
                "emails": []
            }
            
            # Analyze all messages
            for msg in messages:
                if msg.direction != "incoming" or not msg.content:
                    continue
                
                content = msg.content
                
                # Extract name (common patterns)
                name_patterns = [
                    r"(?:meu nome é|me chamo|sou o?a?)\s+([A-Za-zÀ-ÿ\s]+)",
                    r"^([A-Za-zÀ-ÿ]+)(?:\s+[A-Za-zÀ-ÿ]+)*$",  # Single line with just name
                ]
                for pattern in name_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match and not extracted["nome"]:
                        name = match.group(1).strip()
                        if len(name) > 2 and len(name) < 50:
                            extracted["nome"] = name
                
                # Extract value (conta de energia)
                value_patterns = [
                    r"(?:R\$|r\$|rs)\s*(\d+(?:[.,]\d+)?)",
                    r"(\d+(?:[.,]\d+)?)\s*(?:reais|real)",
                    r"(?:conta|valor|pago|gasto)\s*(?:é|de|em torno de|cerca de|aproximadamente)?\s*(\d+(?:[.,]\d+)?)",
                ]
                for pattern in value_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match and not extracted["valor_conta"]:
                        value_str = match.group(1).replace(",", ".")
                        try:
                            value = float(value_str)
                            if 50 <= value <= 50000:  # Reasonable range
                                extracted["valor_conta"] = value
                        except ValueError:
                            pass
                
                # Extract property type
                if "casa" in content.lower():
                    extracted["tipo_imovel"] = "casa"
                elif "apartamento" in content.lower() or "apto" in content.lower():
                    extracted["tipo_imovel"] = "apartamento"
                elif "empresa" in content.lower() or "comércio" in content.lower():
                    extracted["tipo_imovel"] = "comercial"
                elif "indústria" in content.lower() or "fábrica" in content.lower():
                    extracted["tipo_imovel"] = "industrial"
                
                # Extract objections
                for pattern in self.OBJECTION_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        objection = re.search(pattern, content, re.IGNORECASE).group(0)
                        if objection not in extracted["objecoes"]:
                            extracted["objecoes"].append(objection)
                
                # Check for real interest
                interest_patterns = [
                    r"(?:quero|preciso|tenho interesse|me interessa)",
                    r"(?:quanto|como|quando)\s+(?:custa|fica|sai|começa)",
                    r"(?:agendar|marcar|conversar|reunião)"
                ]
                for pattern in interest_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        extracted["tem_interesse_real"] = True
                
                # Extract additional phones
                phone_pattern = r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[-\s]?\d{4}"
                phones = re.findall(phone_pattern, content)
                for phone in phones:
                    clean_phone = re.sub(r"[^\d]", "", phone)
                    if len(clean_phone) >= 10 and clean_phone not in extracted["telefones_adicionais"]:
                        extracted["telefones_adicionais"].append(clean_phone)
                
                # Extract emails
                email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                emails = re.findall(email_pattern, content)
                for email in emails:
                    if email not in extracted["emails"]:
                        extracted["emails"].append(email)
            
            logger.debug(f"Extracted information: {extracted}")
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting key information: {e}")
            return {
                "nome": None,
                "valor_conta": None,
                "tipo_imovel": None,
                "objecoes": [],
                "tem_interesse_real": False
            }
    
    async def build_conversation_context(self, phone: str) -> Dict[str, Any]:
        """
        Build complete conversation context for the agent.
        
        Args:
            phone: Lead's phone number
            
        Returns:
            Complete context dictionary
        """
        try:
            # Get lead data
            lead = await self.lead_repo.get_by_phone(phone)
            if not lead:
                logger.warning(f"No lead found for {phone}")
                return {
                    "error": "Lead not found",
                    "phone": phone
                }
            
            # Get messages
            messages = await self.get_last_100_messages(phone)
            
            # Get lead context
            lead_context = await self.get_lead_context(phone)
            
            # Detect stage
            stage = self.detect_conversation_stage(messages, lead)
            
            # Analyze emotional state
            emotional_state = self.analyze_emotional_state(messages)
            
            # Track qualification
            qualification_progress = self.track_qualification_progress(lead)
            
            # Extract key information
            key_info = self.extract_key_information(messages)
            
            # Build complete context
            context = {
                "lead": lead_context,
                "stage": stage,
                "stage_name": self.STAGES.get(stage, stage),
                "messages": messages,
                "emotional_state": emotional_state,
                "qualification_progress": qualification_progress,
                "key_info": key_info,
                "should_use_reasoning": self.should_activate_reasoning({
                    "messages": messages,
                    "emotional_state": emotional_state,
                    "stage": stage,
                    "key_info": key_info
                }),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Built context for {phone}: "
                f"stage={stage}, "
                f"interest={emotional_state['interesse_level']}, "
                f"progress={qualification_progress['completed']}%"
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error building conversation context for {phone}: {e}")
            return {
                "error": str(e),
                "phone": phone
            }
    
    def should_activate_reasoning(self, context: Dict[str, Any]) -> bool:
        """
        Determine if reasoning mode should be activated.
        
        Args:
            context: Current conversation context
            
        Returns:
            True if reasoning should be activated
        """
        try:
            # Check for complex indicators
            indicators = []
            
            # Multiple questions in recent messages
            messages = context.get("messages", [])
            recent_lead_messages = [
                m for m in messages[-10:]
                if m.direction == "incoming" and m.content
            ]
            
            question_count = 0
            for msg in recent_lead_messages:
                if "?" in msg.content:
                    question_count += msg.content.count("?")
            
            if question_count >= 3:
                indicators.append("multiple_questions")
            
            # Technical objections
            key_info = context.get("key_info", {})
            objections = key_info.get("objecoes", [])
            technical_objections = [
                "não funciona", "não acredito", "é golpe",
                "como comprova", "garantia", "manutenção"
            ]
            
            for objection in objections:
                for tech_obj in technical_objections:
                    if tech_obj in objection.lower():
                        indicators.append("technical_objection")
                        break
            
            # Comparison requests
            comparison_keywords = [
                "comparar", "diferença", "melhor", "pior",
                "vantagem", "desvantagem", "versus", "ou"
            ]
            
            for msg in recent_lead_messages:
                content_lower = msg.content.lower()
                for keyword in comparison_keywords:
                    if keyword in content_lower:
                        indicators.append("comparison_request")
                        break
            
            # Low interest but still engaging
            emotional_state = context.get("emotional_state", {})
            if emotional_state.get("interesse_level", 5) <= 3 and len(recent_lead_messages) > 2:
                indicators.append("low_interest_engaged")
            
            # Complex stage
            stage = context.get("stage", "")
            if stage in ["OBJECTION_HANDLING", "DISCOVERY"]:
                indicators.append("complex_stage")
            
            # Decision: activate if 2+ indicators
            should_activate = len(indicators) >= 2
            
            if should_activate:
                logger.info(f"Reasoning activated due to: {indicators}")
            
            return should_activate
            
        except Exception as e:
            logger.error(f"Error checking reasoning activation: {e}")
            return False
    
    def _calculate_avg_response_time(self, messages: List["Message"]) -> timedelta:
        """Calculate average response time between messages."""
        try:
            response_times = []
            last_outgoing = None
            
            for msg in messages:
                if msg.direction == "outgoing":
                    last_outgoing = msg.timestamp
                elif msg.direction == "incoming" and last_outgoing:
                    response_time = msg.timestamp - last_outgoing
                    if timedelta(0) < response_time < timedelta(days=1):
                        response_times.append(response_time)
                    last_outgoing = None
            
            if response_times:
                avg_seconds = sum(rt.total_seconds() for rt in response_times) / len(response_times)
                return timedelta(seconds=avg_seconds)
            
            return timedelta(hours=1)  # Default
            
        except Exception as e:
            logger.error(f"Error calculating response time: {e}")
            return timedelta(hours=1)