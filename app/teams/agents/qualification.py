"""
QualificationAgent - Agente Especializado em Qualificação de Leads
Responsável por avaliar e pontuar leads baseado em critérios específicos
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from agno import Agent
from agno.tools import tool
from loguru import logger

from app.integrations.supabase_client import supabase_client


class QualificationStage(Enum):
    """Estágios de qualificação do lead"""
    INITIAL_CONTACT = "initial_contact"
    IDENTIFYING_NEED = "identifying_need"
    QUALIFYING = "qualifying"
    DISCOVERY = "discovery"
    PRESENTING_SOLUTION = "presenting_solution"
    HANDLING_OBJECTIONS = "handling_objections"
    SCHEDULING = "scheduling"
    QUALIFIED = "qualified"
    NOT_QUALIFIED = "not_qualified"


class LeadClassification(Enum):
    """Classificação de temperatura do lead"""
    HOT = "hot"        # Score >= 70
    WARM = "warm"      # Score 40-69
    COLD = "cold"      # Score 20-39
    UNQUALIFIED = "unqualified"  # Score < 20


class QualificationAgent:
    """
    Agente especializado em qualificação de leads
    Avalia potencial, calcula scores e determina próximos passos
    """
    
    def __init__(self, model, storage):
        """
        Inicializa o agente de qualificação
        
        Args:
            model: Modelo LLM a ser usado
            storage: Storage para persistência
        """
        self.model = model
        self.storage = storage
        
        # Critérios de qualificação
        self.qualification_criteria = {
            "bill_value": {
                "weight": 0.35,
                "thresholds": {
                    "high": 6000,    # > R$ 6.000
                    "medium": 4000,   # R$ 4.000 - 6.000
                    "low": 2000       # R$ 2.000 - 4.000
                }
            },
            "decision_power": {
                "weight": 0.25,
                "required": True
            },
            "timeline": {
                "weight": 0.15,
                "options": ["immediate", "30_days", "60_days", "future"]
            },
            "engagement": {
                "weight": 0.15,
                "min_messages": 3
            },
            "objections": {
                "weight": 0.10,
                "max_count": 2
            }
        }
        
        # Tools do agente
        self.tools = [
            self.calculate_qualification_score,
            self.check_qualification_criteria,
            self.classify_lead_temperature,
            self.determine_next_action,
            self.save_qualification_data
        ]
        
        # Criar o agente
        self.agent = Agent(
            name="Qualification Specialist",
            model=self.model,
            role="""Você é um especialista em qualificação de leads para energia solar.
            
            Suas responsabilidades:
            1. Avaliar o potencial do lead baseado em critérios objetivos
            2. Calcular score de qualificação (0-100)
            3. Classificar temperatura (Hot/Warm/Cold/Unqualified)
            4. Identificar objeções e barreiras
            5. Recomendar próximas ações
            
            Critérios principais:
            - Valor da conta de luz (mínimo R$ 2.000)
            - Poder de decisão
            - Timeline de implementação
            - Nível de engajamento
            
            Seja objetivo e baseie-se em dados concretos.""",
            
            tools=self.tools,
            instructions=[
                "Analise todos os dados disponíveis do lead",
                "Calcule o score baseado nos critérios estabelecidos",
                "Identifique pontos fortes e fracos",
                "Sugira ações específicas para avançar o lead",
                "Documente objeções encontradas"
            ]
        )
        
        logger.info("✅ QualificationAgent inicializado")
    
    @tool
    async def calculate_qualification_score(
        self,
        lead_id: str,
        bill_value: float,
        has_decision_power: bool,
        timeline: str,
        message_count: int,
        objection_count: int
    ) -> Dict[str, Any]:
        """
        Calcula score de qualificação do lead
        
        Args:
            lead_id: ID do lead
            bill_value: Valor da conta de luz
            has_decision_power: Se tem poder de decisão
            timeline: Timeline de implementação
            message_count: Número de mensagens trocadas
            objection_count: Número de objeções apresentadas
            
        Returns:
            Score e breakdown da pontuação
        """
        score = 0
        breakdown = {}
        
        # 1. Valor da conta (35% do score)
        bill_score = 0
        if bill_value >= self.qualification_criteria["bill_value"]["thresholds"]["high"]:
            bill_score = 35
        elif bill_value >= self.qualification_criteria["bill_value"]["thresholds"]["medium"]:
            bill_score = 25
        elif bill_value >= self.qualification_criteria["bill_value"]["thresholds"]["low"]:
            bill_score = 15
        else:
            bill_score = 5
        
        score += bill_score
        breakdown["bill_value"] = bill_score
        
        # 2. Poder de decisão (25% do score)
        decision_score = 25 if has_decision_power else 0
        score += decision_score
        breakdown["decision_power"] = decision_score
        
        # 3. Timeline (15% do score)
        timeline_scores = {
            "immediate": 15,
            "30_days": 12,
            "60_days": 8,
            "future": 3
        }
        timeline_score = timeline_scores.get(timeline, 0)
        score += timeline_score
        breakdown["timeline"] = timeline_score
        
        # 4. Engajamento (15% do score)
        engagement_score = min(15, (message_count / 10) * 15)
        score += engagement_score
        breakdown["engagement"] = engagement_score
        
        # 5. Objeções (10% do score - inverso)
        objection_score = max(0, 10 - (objection_count * 3))
        score += objection_score
        breakdown["objections"] = objection_score
        
        # Arredondar score
        final_score = round(score)
        
        logger.info(f"📊 Lead {lead_id} - Score: {final_score} | Breakdown: {breakdown}")
        
        return {
            "lead_id": lead_id,
            "score": final_score,
            "breakdown": breakdown,
            "qualified": final_score >= 40,
            "calculated_at": datetime.now().isoformat()
        }
    
    @tool
    async def check_qualification_criteria(
        self,
        lead_id: str,
        criteria: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Verifica critérios específicos de qualificação
        
        Args:
            lead_id: ID do lead
            criteria: Dicionário com critérios a verificar
            
        Returns:
            Status de cada critério
        """
        results = {}
        
        # Verificar valor mínimo da conta
        if "bill_value" in criteria:
            min_value = self.qualification_criteria["bill_value"]["thresholds"]["low"]
            results["min_bill_value"] = criteria["bill_value"] >= min_value
        
        # Verificar poder de decisão
        if "has_decision_power" in criteria:
            results["has_decision_power"] = criteria["has_decision_power"] == True
        
        # Verificar timeline aceitável
        if "timeline" in criteria:
            acceptable_timelines = ["immediate", "30_days", "60_days"]
            results["acceptable_timeline"] = criteria["timeline"] in acceptable_timelines
        
        # Verificar engajamento mínimo
        if "message_count" in criteria:
            min_messages = self.qualification_criteria["engagement"]["min_messages"]
            results["minimum_engagement"] = criteria["message_count"] >= min_messages
        
        # Verificar se há muitas objeções
        if "objection_count" in criteria:
            max_objections = self.qualification_criteria["objections"]["max_count"]
            results["acceptable_objections"] = criteria["objection_count"] <= max_objections
        
        # Determinar se está qualificado
        results["is_qualified"] = all([
            results.get("min_bill_value", False),
            results.get("has_decision_power", False),
            results.get("acceptable_timeline", True),
            results.get("minimum_engagement", True),
            results.get("acceptable_objections", True)
        ])
        
        logger.info(f"✅ Lead {lead_id} - Critérios: {results}")
        
        return results
    
    @tool
    async def classify_lead_temperature(
        self,
        score: int,
        engagement_level: str,
        has_urgency: bool
    ) -> Dict[str, Any]:
        """
        Classifica a temperatura do lead
        
        Args:
            score: Score de qualificação
            engagement_level: Nível de engajamento (high/medium/low)
            has_urgency: Se tem urgência
            
        Returns:
            Classificação e recomendações
        """
        # Classificação base pelo score
        if score >= 70:
            classification = LeadClassification.HOT.value
            priority = "urgent"
            recommendation = "Agendar reunião imediatamente. Lead altamente qualificado."
        elif score >= 40:
            classification = LeadClassification.WARM.value
            priority = "high"
            recommendation = "Nutrir com conteúdo relevante e agendar follow-up em 24h."
        elif score >= 20:
            classification = LeadClassification.COLD.value
            priority = "normal"
            recommendation = "Educar sobre benefícios. Follow-up em 3 dias."
        else:
            classification = LeadClassification.UNQUALIFIED.value
            priority = "low"
            recommendation = "Marcar como não qualificado ou adicionar à lista de nutrição de longo prazo."
        
        # Ajustes baseados em outros fatores
        if has_urgency and classification == LeadClassification.WARM.value:
            classification = LeadClassification.HOT.value
            priority = "urgent"
            recommendation = "Lead morno com urgência - tratar como HOT."
        
        if engagement_level == "low" and classification == LeadClassification.HOT.value:
            classification = LeadClassification.WARM.value
            priority = "high"
            recommendation = "Score alto mas baixo engajamento - aumentar interação."
        
        return {
            "classification": classification,
            "priority": priority,
            "recommendation": recommendation,
            "factors": {
                "score": score,
                "engagement": engagement_level,
                "urgency": has_urgency
            }
        }
    
    @tool
    async def determine_next_action(
        self,
        lead_id: str,
        current_stage: str,
        score: int,
        objections: List[str]
    ) -> Dict[str, Any]:
        """
        Determina próxima ação baseada no status atual
        
        Args:
            lead_id: ID do lead
            current_stage: Estágio atual
            score: Score de qualificação
            objections: Lista de objeções identificadas
            
        Returns:
            Próxima ação recomendada
        """
        next_actions = []
        
        # Mapear estágio atual para próximo
        stage_progression = {
            QualificationStage.INITIAL_CONTACT.value: QualificationStage.IDENTIFYING_NEED.value,
            QualificationStage.IDENTIFYING_NEED.value: QualificationStage.QUALIFYING.value,
            QualificationStage.QUALIFYING.value: QualificationStage.DISCOVERY.value,
            QualificationStage.DISCOVERY.value: QualificationStage.PRESENTING_SOLUTION.value,
            QualificationStage.PRESENTING_SOLUTION.value: QualificationStage.HANDLING_OBJECTIONS.value,
            QualificationStage.HANDLING_OBJECTIONS.value: QualificationStage.SCHEDULING.value,
            QualificationStage.SCHEDULING.value: QualificationStage.QUALIFIED.value
        }
        
        # Se score alto, acelerar processo
        if score >= 70:
            if current_stage in [
                QualificationStage.INITIAL_CONTACT.value,
                QualificationStage.IDENTIFYING_NEED.value
            ]:
                next_stage = QualificationStage.PRESENTING_SOLUTION.value
                next_actions.append({
                    "action": "present_solution",
                    "priority": "high",
                    "message": "Lead quente - apresentar solução imediatamente"
                })
            else:
                next_stage = QualificationStage.SCHEDULING.value
                next_actions.append({
                    "action": "schedule_meeting",
                    "priority": "urgent",
                    "message": "Agendar reunião com consultor"
                })
        
        # Se tem objeções, tratar primeiro
        elif objections and len(objections) > 0:
            next_stage = QualificationStage.HANDLING_OBJECTIONS.value
            for objection in objections[:2]:  # Máximo 2 objeções por vez
                next_actions.append({
                    "action": "handle_objection",
                    "priority": "high",
                    "objection": objection,
                    "message": f"Tratar objeção: {objection}"
                })
        
        # Progressão normal
        else:
            next_stage = stage_progression.get(
                current_stage,
                QualificationStage.QUALIFYING.value
            )
            
            action_map = {
                QualificationStage.IDENTIFYING_NEED.value: "identify_need",
                QualificationStage.QUALIFYING.value: "qualify_lead",
                QualificationStage.DISCOVERY.value: "discover_details",
                QualificationStage.PRESENTING_SOLUTION.value: "present_solution",
                QualificationStage.SCHEDULING.value: "schedule_meeting"
            }
            
            next_actions.append({
                "action": action_map.get(next_stage, "continue_conversation"),
                "priority": "normal",
                "message": f"Avançar para: {next_stage}"
            })
        
        # Se score muito baixo, considerar desqualificar
        if score < 20:
            next_actions.append({
                "action": "consider_disqualification",
                "priority": "low",
                "message": "Score muito baixo - avaliar desqualificação"
            })
        
        return {
            "lead_id": lead_id,
            "current_stage": current_stage,
            "next_stage": next_stage,
            "next_actions": next_actions,
            "score": score,
            "has_objections": len(objections) > 0
        }
    
    @tool
    async def save_qualification_data(
        self,
        lead_id: str,
        qualification_data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Salva dados de qualificação no banco
        
        Args:
            lead_id: ID do lead
            qualification_data: Dados de qualificação
            
        Returns:
            Status da operação
        """
        try:
            # Preparar dados para salvar
            data = {
                "lead_id": lead_id,
                "score": qualification_data.get("score", 0),
                "classification": qualification_data.get("classification", "cold"),
                "is_qualified": qualification_data.get("is_qualified", False),
                "stage": qualification_data.get("stage", "initial_contact"),
                "has_decision_power": qualification_data.get("has_decision_power", False),
                "bill_value": qualification_data.get("bill_value", 0),
                "timeline": qualification_data.get("timeline", "not_defined"),
                "objections": qualification_data.get("objections", []),
                "breakdown": qualification_data.get("breakdown", {}),
                "next_actions": qualification_data.get("next_actions", []),
                "qualified_at": datetime.now().isoformat() if qualification_data.get("is_qualified") else None,
                "updated_at": datetime.now().isoformat()
            }
            
            # Verificar se já existe
            existing = await supabase_client.client.table("leads_qualifications")\
                .select("*")\
                .eq("lead_id", lead_id)\
                .execute()
            
            if existing.data:
                # Atualizar existente
                result = await supabase_client.client.table("leads_qualifications")\
                    .update(data)\
                    .eq("lead_id", lead_id)\
                    .execute()
            else:
                # Inserir novo
                result = await supabase_client.client.table("leads_qualifications")\
                    .insert(data)\
                    .execute()
            
            # Atualizar lead principal
            await supabase_client.update_lead(lead_id, {
                "qualification_score": data["score"],
                "qualification_stage": data["stage"],
                "is_qualified": data["is_qualified"],
                "classification": data["classification"]
            })
            
            logger.info(f"✅ Qualificação salva para lead {lead_id}")
            
            return {
                "success": True,
                "lead_id": lead_id,
                "saved": True
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar qualificação: {e}")
            return {
                "success": False,
                "lead_id": lead_id,
                "error": str(e)
            }