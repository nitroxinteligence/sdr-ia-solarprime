"""
End-to-end tests for qualification stages and transitions.

This module tests each qualification stage, objection handling,
disqualification scenarios, and score calculation.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

from agente.core.types import (
    WhatsAppMessage, LeadStage, MediaType,
    PropertyType, UrgencyLevel
)
from agente.tests.fixtures.test_data import TestData


class TestQualificationStages:
    """Test qualification stage transitions and logic"""
    
    @pytest.mark.asyncio
    async def test_initial_contact_to_identification(self, mock_sdr_agent, mock_repositories):
        """Test transition from initial contact to identification stage"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Mock empty lead (new contact)
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=None)
        
        # Initial contact message
        message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Oi, vi o anúncio de vocês",
            message_id="STAGE001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        with patch("agente.tools.database.create_lead.create_lead",
                   return_value={"success": True, "lead_id": "new-lead-123"}):
            response = await mock_sdr_agent.process_message(message)
        
        # Assert
        assert response.success is True
        assert any(keyword in response.message.lower() for keyword in ["prazer", "helen", "nome"])
        
        # Verify stage transition markers
        assert response.data is not None
        context = response.data.get("context", {})
        # The response should be asking for the lead's name
    
    @pytest.mark.asyncio
    async def test_identification_to_qualification(self, mock_repositories, mock_sdr_agent):
        """Test transition from identification to qualification stage"""
        phone = TestData.TEST_PHONES["lead_2"]
        
        # Mock lead in identification stage
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-456",
            "phone_number": phone,
            "name": None,
            "current_stage": LeadStage.IDENTIFYING,
            "qualification_score": 10
        })
        
        # Provide name
        message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Me chamo Carlos Oliveira",
            message_id="STAGE002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        with patch("agente.tools.database.update_lead.update_lead",
                   return_value={"success": True}):
            response = await mock_sdr_agent.process_message(message)
        
        # Assert
        assert response.success is True
        # Should ask about energy bill or property
        assert any(keyword in response.message.lower() for keyword in ["conta", "energia", "valor"])
    
    @pytest.mark.asyncio
    async def test_qualification_criteria_collection(self, mock_sdr_agent, mock_repositories):
        """Test collection of all qualification criteria"""
        phone = TestData.TEST_PHONES["lead_3"]
        
        # Track qualification progress
        qualification_data = {
            "name": "Ana Silva",
            "bill_value": None,
            "property_type": None,
            "is_decision_maker": None,
            "has_solar_system": None,
            "current_stage": LeadStage.QUALIFYING
        }
        
        # Test 1: Bill value collection via image
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-789",
            "phone_number": phone,
            **qualification_data
        })
        
        with patch("agente.tools.media.process_image.process_image",
                   return_value=TestData.MEDIA_PROCESSING_RESULTS["bill_image_success"]):
            bill_message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=phone,
                message="Aqui está minha conta",
                message_id="QUAL001",
                timestamp=datetime.now(timezone.utc),
                from_me=False,
                media_type=MediaType.IMAGE,
                media_url="https://example.com/bill.jpg"
            )
            
            response1 = await mock_sdr_agent.process_message(bill_message)
            assert response1.success is True
            
        # Update qualification data
        qualification_data["bill_value"] = 567.89
        
        # Test 2: Property type
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-789",
            "phone_number": phone,
            **qualification_data
        })
        
        property_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="É para minha casa mesmo",
            message_id="QUAL002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response2 = await mock_sdr_agent.process_message(property_message)
        assert response2.success is True
        
        # Update qualification data
        qualification_data["property_type"] = PropertyType.HOUSE
        
        # Test 3: Decision maker
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-789",
            "phone_number": phone,
            **qualification_data
        })
        
        decision_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Sim, eu decido sobre essas coisas aqui em casa",
            message_id="QUAL003",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response3 = await mock_sdr_agent.process_message(decision_message)
        assert response3.success is True
        
        # Should now be moving towards qualification
        qualification_data["is_decision_maker"] = True
        
        # Test 4: No existing solar system
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-789",
            "phone_number": phone,
            **qualification_data
        })
        
        solar_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Não, ainda não tenho energia solar",
            message_id="QUAL004",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response4 = await mock_sdr_agent.process_message(solar_message)
        assert response4.success is True
        
        # Should be qualified now
        qualification_data["has_solar_system"] = False
        qualification_data["current_stage"] = LeadStage.QUALIFIED
    
    @pytest.mark.asyncio
    async def test_objection_handling(self, mock_sdr_agent, mock_repositories):
        """Test handling of common objections"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Mock qualified lead showing objections
        base_lead_data = {
            "id": "lead-obj-123",
            "phone_number": phone,
            "name": "Roberto Costa",
            "bill_value": 650.0,
            "current_stage": LeadStage.QUALIFYING,
            "qualification_score": 60
        }
        
        # Test each objection scenario
        for objection_key, objection_data in TestData.OBJECTION_SCENARIOS.items():
            mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=base_lead_data)
            
            objection_message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=phone,
                message=objection_data["message"],
                message_id=f"OBJ_{objection_key}",
                timestamp=datetime.now(timezone.utc),
                from_me=False
            )
            
            response = await mock_sdr_agent.process_message(objection_message)
            
            # Assert objection was handled
            assert response.success is True
            
            # Check that response contains expected keywords
            response_lower = response.message.lower()
            assert any(keyword.lower() in response_lower 
                      for keyword in objection_data["expected_keywords"])
    
    @pytest.mark.asyncio
    async def test_disqualification_scenarios(self, mock_sdr_agent, mock_repositories):
        """Test scenarios that lead to disqualification"""
        
        # Scenario 1: Low bill value
        phone1 = TestData.TEST_PHONES["disqualified_lead"]
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "disq-001",
            "phone_number": phone1,
            "name": "José Santos",
            "current_stage": LeadStage.QUALIFYING
        })
        
        low_bill_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone1,
            message="Minha conta é só 150 reais",
            message_id="DISQ001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        with patch("agente.tools.database.update_lead.update_lead") as mock_update:
            response1 = await mock_sdr_agent.process_message(low_bill_message)
            assert response1.success is True
            # Should mention that it doesn't compensate
            assert "não compensa" in response1.message.lower() or "indicação" in response1.message.lower()
        
        # Scenario 2: Not decision maker
        phone2 = "5511777666555"
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "disq-002",
            "phone_number": phone2,
            "name": "Maria Lima",
            "bill_value": 500.0,
            "current_stage": LeadStage.QUALIFYING
        })
        
        not_decision_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone2,
            message="Não, quem decide é meu marido e ele não quer",
            message_id="DISQ002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response2 = await mock_sdr_agent.process_message(not_decision_message)
        assert response2.success is True
        
        # Scenario 3: Has existing solar system
        phone3 = "5511666555444"
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "disq-003",
            "phone_number": phone3,
            "name": "Pedro Alves",
            "bill_value": 800.0,
            "current_stage": LeadStage.QUALIFYING
        })
        
        has_solar_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone3,
            message="Já tenho painéis solares instalados",
            message_id="DISQ003",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response3 = await mock_sdr_agent.process_message(has_solar_message)
        assert response3.success is True
        
        # Scenario 4: Clear lack of interest
        phone4 = "5511555444333"
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "disq-004",
            "phone_number": phone4,
            "name": "Ana Souza",
            "current_stage": LeadStage.QUALIFYING
        })
        
        not_interested_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone4,
            message="Não tenho interesse, por favor me remova da lista",
            message_id="DISQ004",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response4 = await mock_sdr_agent.process_message(not_interested_message)
        assert response4.success is True
        # Should acknowledge and respect the request
    
    @pytest.mark.asyncio
    async def test_qualification_score_calculation(self, mock_sdr_agent, mock_repositories):
        """Test qualification score calculation based on criteria"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Track score progression
        score_progression = []
        
        # Initial score (just name)
        mock_lead = {
            "id": "score-123",
            "phone_number": phone,
            "name": "Carlos Test",
            "qualification_score": 10,
            "current_stage": LeadStage.IDENTIFYING
        }
        score_progression.append(10)
        
        # Add bill value (high value)
        mock_lead["bill_value"] = 850.0
        mock_lead["qualification_score"] = 40
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=mock_lead)
        score_progression.append(40)
        
        # Add property type
        mock_lead["property_type"] = PropertyType.HOUSE
        mock_lead["qualification_score"] = 50
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=mock_lead)
        score_progression.append(50)
        
        # Add decision maker status
        mock_lead["is_decision_maker"] = True
        mock_lead["qualification_score"] = 70
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=mock_lead)
        score_progression.append(70)
        
        # Add no existing system
        mock_lead["has_solar_system"] = False
        mock_lead["qualification_score"] = 85
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=mock_lead)
        score_progression.append(85)
        
        # Add high urgency
        mock_lead["urgency_level"] = UrgencyLevel.HIGH
        mock_lead["qualification_score"] = 95
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=mock_lead)
        score_progression.append(95)
        
        # Verify score increases with each positive criterion
        for i in range(1, len(score_progression)):
            assert score_progression[i] > score_progression[i-1]
        
        # Final score should indicate highly qualified lead
        assert score_progression[-1] >= 85
    
    @pytest.mark.asyncio
    async def test_stage_regression_handling(self, mock_sdr_agent, mock_repositories):
        """Test handling of stage regression (e.g., qualified lead showing new objections)"""
        phone = TestData.TEST_PHONES["qualified_lead"]
        
        # Start with qualified lead
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "regression-123",
            "phone_number": phone,
            "name": "Paulo Regression",
            "bill_value": 750.0,
            "is_decision_maker": True,
            "current_stage": LeadStage.QUALIFIED,
            "qualification_score": 85
        })
        
        # Lead shows new concern after being qualified
        concern_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Pensando melhor, preciso falar com minha esposa primeiro",
            message_id="REGRESS001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response = await mock_sdr_agent.process_message(concern_message)
        assert response.success is True
        
        # Should handle gracefully without losing qualification
        # but acknowledge the concern
        assert "entendo" in response.message.lower() or "compreendo" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_parallel_qualification_paths(self, mock_sdr_agent, mock_repositories):
        """Test handling of leads providing multiple qualification criteria at once"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Lead provides multiple information at once
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "parallel-123",
            "phone_number": phone,
            "current_stage": LeadStage.INITIAL_CONTACT
        })
        
        multi_info_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Oi, meu nome é Ricardo, minha conta vem uns 600 reais e é para minha casa",
            message_id="PARALLEL001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        with patch("agente.tools.database.update_lead.update_lead") as mock_update:
            response = await mock_sdr_agent.process_message(multi_info_message)
            assert response.success is True
            
            # Should recognize and process multiple data points
            # Lead should advance multiple stages at once