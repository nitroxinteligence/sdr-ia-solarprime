"""
Unit tests for lead qualification score calculation functionality.

This tests the scoring logic that would be used in a calculate_score tool.
The scoring is based on qualification criteria and lead attributes.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from agente.core.types import Lead, LeadInfo


class TestCalculateScore:
    """Test suite for lead qualification score calculation."""
    
    def calculate_score(self, lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate lead qualification score based on various criteria.
        
        This simulates what a calculate_score tool would do.
        """
        score = 0
        max_score = 100
        breakdown = {}
        
        # Energy value score (0-30 points)
        energy_value = lead_info.get("energy_value", 0)
        if energy_value >= 500:
            value_score = 30
        elif energy_value >= 350:
            value_score = 20
        elif energy_value >= 200:
            value_score = 10
        else:
            value_score = 0
        score += value_score
        breakdown["energy_value"] = value_score
        
        # Solution type score (0-20 points)
        solution_type = lead_info.get("solution_type")
        solution_scores = {
            "residential": 20,
            "commercial": 20,
            "industrial": 15,
            "rural": 10,
            "other": 5
        }
        solution_score = solution_scores.get(solution_type, 0)
        score += solution_score
        breakdown["solution_type"] = solution_score
        
        # Decision maker score (0-20 points)
        is_decision_maker = lead_info.get("is_decision_maker", False)
        can_bring_decision_maker = lead_info.get("can_bring_decision_maker", False)
        if is_decision_maker:
            decision_score = 20
        elif can_bring_decision_maker:
            decision_score = 10
        else:
            decision_score = 0
        score += decision_score
        breakdown["decision_maker"] = decision_score
        
        # Roof access score (0-10 points)
        roof_access = lead_info.get("roof_access", False)
        roof_score = 10 if roof_access else 0
        score += roof_score
        breakdown["roof_access"] = roof_score
        
        # Interest level score (0-20 points)
        interest_indicators = {
            "asked_questions": lead_info.get("asked_questions", False),
            "provided_documents": lead_info.get("provided_documents", False),
            "showed_excitement": lead_info.get("showed_excitement", False),
            "messages_count": lead_info.get("messages_count", 0) > 5,
            "response_time": lead_info.get("avg_response_time", 300) < 180  # Less than 3 minutes
        }
        interest_score = sum(4 for indicator in interest_indicators.values() if indicator)
        score += interest_score
        breakdown["interest_level"] = interest_score
        
        # Disqualifiers check
        disqualifiers = []
        if lead_info.get("has_solar_system", False):
            disqualifiers.append("already_has_system")
            score = 0
        if lead_info.get("has_active_contract", False):
            disqualifiers.append("active_contract")
            score = max(score - 50, 0)
        if energy_value < 100:
            disqualifiers.append("value_too_low")
            score = 0
            
        # Calculate qualification status
        if score >= 70:
            status = "highly_qualified"
        elif score >= 50:
            status = "qualified"
        elif score >= 30:
            status = "partially_qualified"
        else:
            status = "not_qualified"
            
        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "status": status,
            "breakdown": breakdown,
            "disqualifiers": disqualifiers,
            "recommendation": self._get_recommendation(score, status, disqualifiers)
        }
        
    def _get_recommendation(self, score: int, status: str, disqualifiers: list) -> str:
        """Get recommendation based on score and status."""
        if disqualifiers:
            if "already_has_system" in disqualifiers:
                return "Lead já possui sistema solar. Verificar possibilidade de expansão."
            elif "active_contract" in disqualifiers:
                return "Lead possui contrato ativo. Agendar follow-up para quando terminar."
            elif "value_too_low" in disqualifiers:
                return "Valor da conta muito baixo. Não é viável economicamente."
                
        if status == "highly_qualified":
            return "Lead altamente qualificado. Priorizar agendamento imediato."
        elif status == "qualified":
            return "Lead qualificado. Agendar reunião nos próximos dias."
        elif status == "partially_qualified":
            return "Lead parcialmente qualificado. Necessita mais informações."
        else:
            return "Lead não qualificado no momento. Manter em base para futuro."
    
    @pytest.mark.asyncio
    async def test_calculate_score_highly_qualified_lead(self):
        """Test scoring for a highly qualified lead."""
        lead_info = {
            "energy_value": 600,
            "solution_type": "residential",
            "is_decision_maker": True,
            "roof_access": True,
            "asked_questions": True,
            "provided_documents": True,
            "showed_excitement": True,
            "messages_count": 10,
            "avg_response_time": 120
        }
        
        result = self.calculate_score(lead_info)
        
        assert result["score"] >= 70
        assert result["status"] == "highly_qualified"
        assert result["percentage"] >= 70
        assert len(result["disqualifiers"]) == 0
        assert "altamente qualificado" in result["recommendation"]
        
    @pytest.mark.asyncio
    async def test_calculate_score_energy_value_tiers(self):
        """Test different energy value scoring tiers."""
        # High value
        result = self.calculate_score({"energy_value": 1000})
        assert result["breakdown"]["energy_value"] == 30
        
        # Medium value
        result = self.calculate_score({"energy_value": 400})
        assert result["breakdown"]["energy_value"] == 20
        
        # Low value
        result = self.calculate_score({"energy_value": 250})
        assert result["breakdown"]["energy_value"] == 10
        
        # Very low value
        result = self.calculate_score({"energy_value": 150})
        assert result["breakdown"]["energy_value"] == 0
        
    @pytest.mark.asyncio
    async def test_calculate_score_solution_types(self):
        """Test scoring for different solution types."""
        solution_types = [
            ("residential", 20),
            ("commercial", 20),
            ("industrial", 15),
            ("rural", 10),
            ("other", 5),
            ("unknown", 0)
        ]
        
        for solution_type, expected_score in solution_types:
            result = self.calculate_score({"solution_type": solution_type})
            assert result["breakdown"]["solution_type"] == expected_score
            
    @pytest.mark.asyncio
    async def test_calculate_score_decision_maker_scenarios(self):
        """Test scoring for decision maker scenarios."""
        # Is decision maker
        result = self.calculate_score({"is_decision_maker": True})
        assert result["breakdown"]["decision_maker"] == 20
        
        # Can bring decision maker
        result = self.calculate_score({
            "is_decision_maker": False,
            "can_bring_decision_maker": True
        })
        assert result["breakdown"]["decision_maker"] == 10
        
        # Neither
        result = self.calculate_score({
            "is_decision_maker": False,
            "can_bring_decision_maker": False
        })
        assert result["breakdown"]["decision_maker"] == 0
        
    @pytest.mark.asyncio
    async def test_calculate_score_interest_indicators(self):
        """Test scoring based on interest indicators."""
        # No interest indicators
        result = self.calculate_score({})
        assert result["breakdown"]["interest_level"] == 0
        
        # Some interest indicators
        result = self.calculate_score({
            "asked_questions": True,
            "messages_count": 8
        })
        assert result["breakdown"]["interest_level"] == 8  # 2 indicators * 4 points
        
        # All interest indicators
        result = self.calculate_score({
            "asked_questions": True,
            "provided_documents": True,
            "showed_excitement": True,
            "messages_count": 10,
            "avg_response_time": 60
        })
        assert result["breakdown"]["interest_level"] == 20  # 5 indicators * 4 points
        
    @pytest.mark.asyncio
    async def test_calculate_score_with_disqualifiers(self):
        """Test scoring with disqualifying factors."""
        # Already has system
        result = self.calculate_score({
            "energy_value": 500,
            "has_solar_system": True
        })
        assert result["score"] == 0
        assert "already_has_system" in result["disqualifiers"]
        assert "já possui sistema solar" in result["recommendation"]
        
        # Has active contract
        result = self.calculate_score({
            "energy_value": 500,
            "solution_type": "residential",
            "has_active_contract": True
        })
        assert result["score"] < 50  # Score reduced but not zero
        assert "active_contract" in result["disqualifiers"]
        assert "contrato ativo" in result["recommendation"]
        
        # Value too low
        result = self.calculate_score({
            "energy_value": 50
        })
        assert result["score"] == 0
        assert "value_too_low" in result["disqualifiers"]
        assert "muito baixo" in result["recommendation"]
        
    @pytest.mark.asyncio
    async def test_calculate_score_qualification_statuses(self):
        """Test different qualification status thresholds."""
        # Highly qualified (>= 70)
        result = self.calculate_score({
            "energy_value": 600,
            "solution_type": "commercial",
            "is_decision_maker": True,
            "roof_access": True,
            "asked_questions": True,
            "showed_excitement": True
        })
        assert result["status"] == "highly_qualified"
        
        # Qualified (50-69)
        result = self.calculate_score({
            "energy_value": 400,
            "solution_type": "residential",
            "can_bring_decision_maker": True
        })
        assert result["status"] == "qualified"
        
        # Partially qualified (30-49)
        result = self.calculate_score({
            "energy_value": 250,
            "solution_type": "rural"
        })
        assert result["status"] == "partially_qualified"
        
        # Not qualified (< 30)
        result = self.calculate_score({
            "energy_value": 150
        })
        assert result["status"] == "not_qualified"
        
    @pytest.mark.asyncio
    async def test_calculate_score_edge_cases(self):
        """Test edge cases in score calculation."""
        # Empty lead info
        result = self.calculate_score({})
        assert result["score"] == 0
        assert result["status"] == "not_qualified"
        
        # Maximum possible score
        result = self.calculate_score({
            "energy_value": 1000,
            "solution_type": "commercial",
            "is_decision_maker": True,
            "roof_access": True,
            "asked_questions": True,
            "provided_documents": True,
            "showed_excitement": True,
            "messages_count": 20,
            "avg_response_time": 30
        })
        assert result["score"] == 100
        assert result["percentage"] == 100.0
        
    @pytest.mark.asyncio
    async def test_calculate_score_percentage_calculation(self):
        """Test percentage calculation accuracy."""
        test_cases = [
            ({"energy_value": 500}, 30),  # 30/100 = 30%
            ({"energy_value": 500, "solution_type": "residential"}, 50),  # 50/100 = 50%
        ]
        
        for lead_info, expected_score in test_cases:
            result = self.calculate_score(lead_info)
            assert result["score"] == expected_score
            assert result["percentage"] == (expected_score / 100) * 100
            
    @pytest.mark.asyncio
    async def test_calculate_score_solar_prime_context(self):
        """Test scoring in Solar Prime business context."""
        # Typical qualified Solar Prime lead
        solar_prime_lead = {
            "energy_value": 450,  # R$ 450 energy bill
            "solution_type": "residential",
            "is_decision_maker": True,
            "roof_access": True,
            "asked_questions": True,
            "messages_count": 7,
            "provider": "CPFL",
            "location": "Campinas-SP"
        }
        
        result = self.calculate_score(solar_prime_lead)
        
        assert result["score"] >= 50
        assert result["status"] in ["qualified", "highly_qualified"]
        assert len(result["disqualifiers"]) == 0
        
    @pytest.mark.asyncio
    async def test_calculate_score_breakdown_completeness(self):
        """Test that breakdown includes all scoring categories."""
        result = self.calculate_score({
            "energy_value": 300,
            "solution_type": "residential"
        })
        
        expected_categories = [
            "energy_value",
            "solution_type",
            "decision_maker",
            "roof_access",
            "interest_level"
        ]
        
        for category in expected_categories:
            assert category in result["breakdown"]
            assert isinstance(result["breakdown"][category], (int, float))
            
    @pytest.mark.asyncio
    async def test_calculate_score_response_time_scoring(self):
        """Test interest scoring based on response time."""
        # Fast response (< 3 minutes)
        result = self.calculate_score({
            "avg_response_time": 120  # 2 minutes
        })
        assert result["breakdown"]["interest_level"] >= 4
        
        # Slow response
        result = self.calculate_score({
            "avg_response_time": 600  # 10 minutes
        })
        assert result["breakdown"]["interest_level"] == 0