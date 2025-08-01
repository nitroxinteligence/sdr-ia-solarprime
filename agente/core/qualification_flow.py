"""
Qualification Flow for SDR Agent.

This module manages the lead qualification process, ensuring all criteria
are met according to Solar Prime requirements.
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
from loguru import logger

from agente.types import Lead
from agente.repositories import LeadRepository, MessageRepository


class QualificationStage(Enum):
    """Lead qualification stages."""
    INITIAL_CONTACT = "initial_contact"
    IDENTIFICATION = "identification"
    QUALIFICATION = "qualification"
    DISCOVERY = "discovery"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    SCHEDULING = "scheduling"
    FOLLOW_UP = "follow_up"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"


class QualificationCriteria(Enum):
    """Qualification criteria for leads."""
    HIGH_VALUE_ACCOUNT = "conta_acima_4000"  # R$ 4000+ for 20% discount
    DECISION_MAKER = "e_decisor"  # Decision maker will be present
    NO_EXISTING_SYSTEM = "sem_usina_propria"  # No existing solar system
    NO_ACTIVE_CONTRACT = "sem_contrato_vigente"  # No active energy contract
    DEMONSTRATES_INTEREST = "demonstra_interesse"  # Shows real interest


class QualificationFlow:
    """Manages lead qualification flow and criteria validation."""
    
    # Minimum account value for 20% discount
    MIN_COMMERCIAL_VALUE = 4000.0
    MIN_RESIDENTIAL_VALUE = 400.0
    
    # Stage progression requirements
    STAGE_REQUIREMENTS = {
        QualificationStage.IDENTIFICATION: ["name"],
        QualificationStage.QUALIFICATION: ["name", "valor_conta"],
        QualificationStage.DISCOVERY: ["name", "valor_conta", "e_decisor"],
        QualificationStage.PRESENTATION: ["name", "valor_conta", "e_decisor", "solucao_interesse"],
        QualificationStage.SCHEDULING: ["name", "valor_conta", "e_decisor", "solucao_interesse", "disponibilidade_reuniao"],
        QualificationStage.QUALIFIED: ["name", "valor_conta", "e_decisor", "solucao_interesse", "meeting_scheduled"]
    }
    
    # Questions for each missing criteria
    CRITERIA_QUESTIONS = {
        "name": "Antes de começarmos, como posso chamá-lo?",
        "valor_conta": "Qual o valor médio da sua conta de energia?",
        "e_decisor": "Você é o responsável pelas decisões sobre energia na sua casa/empresa?",
        "tem_usina_propria": "Você já possui sistema de energia solar instalado?",
        "tem_contrato_vigente": "Você tem algum contrato de energia vigente com outra empresa?",
        "tipo_imovel": "É para sua casa ou empresa?",
        "disponibilidade_reuniao": "Qual o melhor dia e horário para nossa reunião online?"
    }
    
    # Objection responses
    OBJECTION_RESPONSES = {
        "muito_caro": "Entendo sua preocupação! Mas veja só: nossa solução substitui sua conta atual. Você paga o mesmo ou menos, mas com energia limpa e garantida por 25 anos!",
        "nao_confio": "Super compreensível! Por isso a Solar Prime tem nota 9,64 no Reclame Aqui e mais de 23 mil clientes satisfeitos. Posso te enviar alguns depoimentos?",
        "conta_baixa": "Com conta abaixo de R$400 realmente não compensa. Mas você conhece alguém com conta alta que poderia se beneficiar? Temos um programa de indicação!",
        "moro_aluguel": "Ótima notícia! Temos a solução de assinatura que não precisa de instalação! Você economiza 12-20% sem fazer nenhuma obra!",
        "preciso_pensar": "Claro! É uma decisão importante. Que tal agendarmos uma conversa sem compromisso para eu tirar todas suas dúvidas?"
    }
    
    def __init__(
        self,
        lead_repo: Optional[LeadRepository] = None,
        message_repo: Optional[MessageRepository] = None
    ):
        """Initialize QualificationFlow with repositories."""
        self.lead_repo = lead_repo or LeadRepository()
        self.message_repo = message_repo or MessageRepository()
        logger.info("QualificationFlow initialized")
    
    def get_current_stage(self, lead: Lead) -> QualificationStage:
        """
        Determine current qualification stage based on lead data.
        
        Args:
            lead: Lead object to analyze
            
        Returns:
            Current qualification stage
        """
        try:
            metadata = lead.metadata or {}
            
            # Check if already qualified or disqualified
            if lead.status == "qualified":
                return QualificationStage.QUALIFIED
            elif lead.status == "disqualified":
                return QualificationStage.DISQUALIFIED
            
            # Check stage based on collected data
            if metadata.get("meeting_scheduled"):
                return QualificationStage.FOLLOW_UP
            
            if metadata.get("disponibilidade_reuniao"):
                return QualificationStage.SCHEDULING
            
            if metadata.get("has_objections") and not metadata.get("objections_handled"):
                return QualificationStage.OBJECTION_HANDLING
            
            if metadata.get("solucao_interesse"):
                return QualificationStage.PRESENTATION
            
            if metadata.get("e_decisor") is not None:
                return QualificationStage.DISCOVERY
            
            if metadata.get("valor_conta"):
                return QualificationStage.QUALIFICATION
            
            if lead.name:
                return QualificationStage.IDENTIFICATION
            
            return QualificationStage.INITIAL_CONTACT
            
        except Exception as e:
            logger.error(f"Error determining stage: {e}")
            return QualificationStage.INITIAL_CONTACT
    
    def check_qualification_criteria(self, lead: Lead) -> Dict[str, Any]:
        """
        Check if lead meets all qualification criteria.
        
        Args:
            lead: Lead to evaluate
            
        Returns:
            Dictionary with criteria status and details
        """
        try:
            metadata = lead.metadata or {}
            
            criteria_status = {
                QualificationCriteria.HIGH_VALUE_ACCOUNT: {
                    "met": False,
                    "value": metadata.get("valor_conta", 0),
                    "required": self.MIN_COMMERCIAL_VALUE,
                    "reason": None
                },
                QualificationCriteria.DECISION_MAKER: {
                    "met": False,
                    "value": metadata.get("e_decisor"),
                    "required": True,
                    "reason": None
                },
                QualificationCriteria.NO_EXISTING_SYSTEM: {
                    "met": True,  # Default to true unless stated otherwise
                    "value": not metadata.get("tem_usina_propria", False),
                    "required": True,
                    "reason": None
                },
                QualificationCriteria.NO_ACTIVE_CONTRACT: {
                    "met": True,  # Default to true unless stated otherwise
                    "value": not metadata.get("tem_contrato_vigente", False),
                    "required": True,
                    "reason": None
                },
                QualificationCriteria.DEMONSTRATES_INTEREST: {
                    "met": False,
                    "value": metadata.get("demonstra_interesse", False),
                    "required": True,
                    "reason": None
                }
            }
            
            # Check high value account
            valor_conta = metadata.get("valor_conta", 0)
            if valor_conta >= self.MIN_COMMERCIAL_VALUE:
                criteria_status[QualificationCriteria.HIGH_VALUE_ACCOUNT]["met"] = True
                criteria_status[QualificationCriteria.HIGH_VALUE_ACCOUNT]["discount"] = "20%"
            elif valor_conta >= self.MIN_RESIDENTIAL_VALUE:
                criteria_status[QualificationCriteria.HIGH_VALUE_ACCOUNT]["met"] = True
                criteria_status[QualificationCriteria.HIGH_VALUE_ACCOUNT]["discount"] = "12-15%"
                criteria_status[QualificationCriteria.HIGH_VALUE_ACCOUNT]["reason"] = "residential_value"
            else:
                criteria_status[QualificationCriteria.HIGH_VALUE_ACCOUNT]["reason"] = "below_minimum"
            
            # Check decision maker
            if metadata.get("e_decisor") == True:
                criteria_status[QualificationCriteria.DECISION_MAKER]["met"] = True
            elif metadata.get("e_decisor") == False:
                criteria_status[QualificationCriteria.DECISION_MAKER]["reason"] = "not_decision_maker"
            else:
                criteria_status[QualificationCriteria.DECISION_MAKER]["reason"] = "unknown"
            
            # Check existing system
            if metadata.get("tem_usina_propria") == True:
                criteria_status[QualificationCriteria.NO_EXISTING_SYSTEM]["met"] = False
                criteria_status[QualificationCriteria.NO_EXISTING_SYSTEM]["reason"] = "has_system"
            
            # Check active contract
            if metadata.get("tem_contrato_vigente") == True:
                criteria_status[QualificationCriteria.NO_ACTIVE_CONTRACT]["met"] = False
                criteria_status[QualificationCriteria.NO_ACTIVE_CONTRACT]["reason"] = "has_contract"
                criteria_status[QualificationCriteria.NO_ACTIVE_CONTRACT]["contract_end"] = metadata.get("contrato_termino")
            
            # Check interest (inferred from engagement)
            engagement_indicators = [
                metadata.get("messages_count", 0) > 5,
                metadata.get("asked_questions", False),
                metadata.get("provided_documents", False),
                metadata.get("showed_excitement", False),
                metadata.get("disponibilidade_reuniao") is not None
            ]
            
            if sum(engagement_indicators) >= 2:
                criteria_status[QualificationCriteria.DEMONSTRATES_INTEREST]["met"] = True
                criteria_status[QualificationCriteria.DEMONSTRATES_INTEREST]["indicators"] = engagement_indicators
            
            # Overall qualification
            all_criteria_met = all(
                status["met"] for status in criteria_status.values()
            )
            
            # Check for hard disqualifiers
            disqualification_reasons = []
            if valor_conta < self.MIN_RESIDENTIAL_VALUE:
                disqualification_reasons.append("account_too_low")
            if metadata.get("e_decisor") == False and not metadata.get("pode_trazer_decisor"):
                disqualification_reasons.append("no_decision_maker")
            
            return {
                "qualified": all_criteria_met and not disqualification_reasons,
                "criteria": criteria_status,
                "disqualification_reasons": disqualification_reasons,
                "recommendation": self._get_qualification_recommendation(criteria_status, disqualification_reasons)
            }
            
        except Exception as e:
            logger.error(f"Error checking qualification criteria: {e}")
            return {
                "qualified": False,
                "criteria": {},
                "disqualification_reasons": ["error"],
                "recommendation": "continue_qualification"
            }
    
    def get_next_question(self, lead: Lead) -> Optional[str]:
        """
        Get the next question to ask based on missing information.
        
        Args:
            lead: Current lead
            
        Returns:
            Next question to ask, or None if all info collected
        """
        try:
            metadata = lead.metadata or {}
            stage = self.get_current_stage(lead)
            
            # Priority order for questions
            priority_fields = [
                ("name", lead.name),
                ("valor_conta", metadata.get("valor_conta")),
                ("tipo_imovel", metadata.get("tipo_imovel")),
                ("e_decisor", metadata.get("e_decisor")),
                ("tem_usina_propria", metadata.get("tem_usina_propria")),
                ("tem_contrato_vigente", metadata.get("tem_contrato_vigente"))
            ]
            
            # Find first missing field
            for field, value in priority_fields:
                if value is None or (field == "name" and not value):
                    return self.CRITERIA_QUESTIONS.get(field)
            
            # If in scheduling stage, ask for availability
            if stage == QualificationStage.PRESENTATION and not metadata.get("disponibilidade_reuniao"):
                return self.CRITERIA_QUESTIONS["disponibilidade_reuniao"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting next question: {e}")
            return None
    
    def handle_objection(self, objection_text: str) -> Optional[str]:
        """
        Get appropriate response for common objections.
        
        Args:
            objection_text: Text containing the objection
            
        Returns:
            Appropriate response or None
        """
        try:
            objection_lower = objection_text.lower()
            
            # Check for common objection patterns
            for pattern, response in self.OBJECTION_RESPONSES.items():
                if pattern.replace("_", " ") in objection_lower:
                    return response
            
            # Generic objection handling
            if any(word in objection_lower for word in ["não", "nunca", "depois", "talvez"]):
                return "Entendo perfeitamente! Que tal conversarmos sem compromisso para eu esclarecer suas dúvidas? Garanto que vale a pena conhecer!"
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling objection: {e}")
            return None
    
    def calculate_savings_estimate(self, valor_conta: float, solution_type: str = "commercial") -> Dict[str, Any]:
        """
        Calculate estimated savings based on account value.
        
        Args:
            valor_conta: Monthly energy bill value
            solution_type: Type of solution (commercial/residential)
            
        Returns:
            Dictionary with savings calculations
        """
        try:
            if solution_type == "commercial" and valor_conta >= self.MIN_COMMERCIAL_VALUE:
                discount_rate = 0.20  # 20% discount
                discount_label = "20%"
            elif valor_conta >= self.MIN_RESIDENTIAL_VALUE:
                discount_rate = 0.13  # Average 13% for residential
                discount_label = "12-15%"
            else:
                return {
                    "eligible": False,
                    "reason": "below_minimum_value"
                }
            
            monthly_savings = valor_conta * discount_rate
            annual_savings = monthly_savings * 12
            savings_25_years = annual_savings * 25
            
            return {
                "eligible": True,
                "discount_rate": discount_label,
                "current_bill": valor_conta,
                "new_bill": valor_conta - monthly_savings,
                "monthly_savings": monthly_savings,
                "annual_savings": annual_savings,
                "total_savings_25_years": savings_25_years,
                "co2_reduction_tons": annual_savings * 0.0008,  # Approximate CO2 calculation
                "trees_equivalent": int(annual_savings * 0.06)  # Trees planted equivalent
            }
            
        except Exception as e:
            logger.error(f"Error calculating savings: {e}")
            return {"eligible": False, "reason": "calculation_error"}
    
    def get_stage_transition_message(self, from_stage: QualificationStage, to_stage: QualificationStage) -> Optional[str]:
        """
        Get appropriate message for stage transitions.
        
        Args:
            from_stage: Current stage
            to_stage: Target stage
            
        Returns:
            Transition message or None
        """
        transitions = {
            (QualificationStage.INITIAL_CONTACT, QualificationStage.IDENTIFICATION): 
                "Prazer em conhecê-lo! Agora preciso entender melhor sua situação...",
            
            (QualificationStage.IDENTIFICATION, QualificationStage.QUALIFICATION):
                "Perfeito! Agora vamos falar sobre sua conta de energia...",
            
            (QualificationStage.QUALIFICATION, QualificationStage.DISCOVERY):
                "Excelente! Com esse valor, temos ótimas opções para você!",
            
            (QualificationStage.DISCOVERY, QualificationStage.PRESENTATION):
                "Maravilha! Deixa eu te mostrar como podemos te ajudar...",
            
            (QualificationStage.PRESENTATION, QualificationStage.SCHEDULING):
                "Que bom que gostou! Vamos agendar uma reunião para detalhar tudo?",
            
            (QualificationStage.SCHEDULING, QualificationStage.QUALIFIED):
                "Perfeito! Reunião agendada! Vou enviar todos os detalhes por aqui!"
        }
        
        return transitions.get((from_stage, to_stage))
    
    async def update_lead_qualification(self, lead: Lead, new_data: Dict[str, Any]) -> Lead:
        """
        Update lead with new qualification data.
        
        Args:
            lead: Lead to update
            new_data: New qualification data
            
        Returns:
            Updated lead
        """
        try:
            # Update metadata
            if not lead.metadata:
                lead.metadata = {}
            
            lead.metadata.update(new_data)
            
            # Update stage
            new_stage = self.get_current_stage(lead)
            lead.stage = new_stage.value
            
            # Check qualification
            qualification_result = self.check_qualification_criteria(lead)
            
            if qualification_result["qualified"]:
                lead.status = "qualified"
                lead.score = 10
            elif qualification_result["disqualification_reasons"]:
                lead.status = "disqualified"
                lead.score = 0
            else:
                # Calculate score based on progress
                criteria_met = sum(
                    1 for status in qualification_result["criteria"].values() 
                    if status["met"]
                )
                total_criteria = len(qualification_result["criteria"])
                lead.score = int((criteria_met / total_criteria) * 10)
            
            lead.updated_at = datetime.now(timezone.utc)
            
            # Save to database
            await self.lead_repo.update(lead)
            
            logger.info(
                f"Updated lead {lead.phone} qualification: "
                f"stage={new_stage.value}, score={lead.score}, status={lead.status}"
            )
            
            return lead
            
        except Exception as e:
            logger.error(f"Error updating lead qualification: {e}")
            return lead
    
    def _get_qualification_recommendation(
        self, 
        criteria_status: Dict[QualificationCriteria, Dict],
        disqualification_reasons: List[str]
    ) -> str:
        """Get recommendation based on qualification status."""
        if disqualification_reasons:
            if "account_too_low" in disqualification_reasons:
                return "offer_referral_program"
            elif "no_decision_maker" in disqualification_reasons:
                return "request_decision_maker"
            else:
                return "disqualify_politely"
        
        # Count met criteria
        met_count = sum(1 for status in criteria_status.values() if status["met"])
        total_count = len(criteria_status)
        
        if met_count == total_count:
            return "proceed_to_scheduling"
        elif met_count >= 3:
            return "continue_qualification"
        else:
            return "gather_more_info"
    
    def extract_value_from_text(self, text: str) -> Optional[float]:
        """
        Extract monetary value from text.
        
        Args:
            text: Text containing value
            
        Returns:
            Extracted value or None
        """
        try:
            # Patterns to match values
            patterns = [
                r"R\$\s*([0-9]+(?:[.,][0-9]+)?)",
                r"([0-9]+(?:[.,][0-9]+)?)\s*(?:reais|real)",
                r"([0-9]+(?:[.,][0-9]+)?)\s*(?:$|R\$)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value_str = match.group(1).replace(",", ".")
                    value = float(value_str)
                    # Sanity check
                    if 50 <= value <= 50000:
                        return value
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting value: {e}")
            return None
    
    def is_business_hours(self) -> bool:
        """Check if current time is within business hours (8AM-6PM Brazil time)."""
        from zoneinfo import ZoneInfo
        
        brazil_tz = ZoneInfo("America/Sao_Paulo")
        current_time = datetime.now(brazil_tz)
        
        # Monday-Friday, 8AM-6PM
        if current_time.weekday() >= 5:  # Weekend
            return False
        
        return 8 <= current_time.hour < 18