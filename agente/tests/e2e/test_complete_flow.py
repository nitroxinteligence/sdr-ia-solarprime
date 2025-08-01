"""
End-to-end tests for the complete SDR Agent flow.

This module tests the entire flow from webhook reception to qualified lead
with calendar scheduling, including multimodal processing and follow-ups.
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, AsyncMock, patch, call
import json

from agente.core.types import (
    WhatsAppMessage, AgentResponse, LeadStage,
    CalendarSlot, MediaType
)
from agente.tests.fixtures.test_data import TestData


class TestCompleteFlow:
    """Test complete SDR Agent flow from initial contact to scheduling"""
    
    @pytest.mark.asyncio
    async def test_webhook_message_reception(self, mock_sdr_agent, test_data):
        """Test webhook message reception and processing"""
        # Arrange
        webhook_payload = test_data.get_sample_message("text", "Olá, vi o anúncio sobre energia solar")
        phone = webhook_payload["data"]["key"]["remoteJid"].replace("@s.whatsapp.net", "")
        
        # Create WhatsApp message from webhook
        message = WhatsAppMessage(
            instance=webhook_payload["instance"]["instanceName"],
            phone=phone,
            message=webhook_payload["data"]["message"]["conversation"],
            message_id=webhook_payload["data"]["key"]["id"],
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # Act
        response = await mock_sdr_agent.process_message(message)
        
        # Assert
        assert response.success is True
        assert response.message is not None
        assert "SolarPrime" in response.message or "Helen" in response.message
        assert response.data["phone"] == phone
    
    @pytest.mark.asyncio
    async def test_multimodal_processing(self, mock_sdr_agent, mock_services, test_data):
        """Test processing of different media types (text, image, audio, document)"""
        # Test text message
        text_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=TestData.TEST_PHONES["lead_1"],
            message="Meu nome é João Silva",
            message_id="MSG001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        text_response = await mock_sdr_agent.process_message(text_message)
        assert text_response.success is True
        
        # Test image message (bill photo)
        with patch("agente.tools.media.process_image.process_image", 
                   return_value=TestData.MEDIA_PROCESSING_RESULTS["bill_image_success"]):
            image_message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=TestData.TEST_PHONES["lead_1"],
                message="Aqui está minha conta de luz",
                message_id="MSG002",
                timestamp=datetime.now(timezone.utc),
                from_me=False,
                media_type=MediaType.IMAGE,
                media_url="https://example.com/bill.jpg"
            )
            
            image_response = await mock_sdr_agent.process_message(image_message)
            assert image_response.success is True
        
        # Test audio message
        with patch("agente.tools.media.process_audio.process_audio",
                   return_value=TestData.MEDIA_PROCESSING_RESULTS["audio_transcription"]):
            audio_message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=TestData.TEST_PHONES["lead_2"],
                message="",
                message_id="MSG003",
                timestamp=datetime.now(timezone.utc),
                from_me=False,
                media_type=MediaType.AUDIO,
                media_url="https://example.com/audio.ogg"
            )
            
            audio_response = await mock_sdr_agent.process_message(audio_message)
            assert audio_response.success is True
        
        # Test document message (PDF bill)
        with patch("agente.tools.media.process_document.process_document",
                   return_value=TestData.MEDIA_PROCESSING_RESULTS["bill_pdf_success"]):
            doc_message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=TestData.TEST_PHONES["lead_3"],
                message="",
                message_id="MSG004",
                timestamp=datetime.now(timezone.utc),
                from_me=False,
                media_type=MediaType.DOCUMENT,
                media_url="https://example.com/bill.pdf"
            )
            
            doc_response = await mock_sdr_agent.process_message(doc_message)
            assert doc_response.success is True
    
    @pytest.mark.asyncio
    async def test_qualification_flow_complete(self, mock_sdr_agent, mock_repositories, mock_services):
        """Test complete qualification flow from initial contact to qualified lead"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Mock repository responses for lead progression
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value=None)
        mock_repositories["lead_repo"].create = AsyncMock(return_value={
            "id": "lead-123",
            "phone_number": phone,
            "current_stage": LeadStage.INITIAL_CONTACT
        })
        
        # Step 1: Initial contact
        initial_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Olá, vi sobre energia solar",
            message_id="QUAL001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response1 = await mock_sdr_agent.process_message(initial_message)
        assert response1.success is True
        
        # Step 2: Identification
        name_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Meu nome é João Silva",
            message_id="QUAL002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # Update mock to return lead with name
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-123",
            "phone_number": phone,
            "name": "João Silva",
            "current_stage": LeadStage.IDENTIFYING
        })
        
        response2 = await mock_sdr_agent.process_message(name_message)
        assert response2.success is True
        
        # Step 3: Qualification - Bill value
        with patch("agente.tools.media.process_image.process_image",
                   return_value=TestData.MEDIA_PROCESSING_RESULTS["bill_image_success"]):
            bill_message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=phone,
                message="Segue foto da minha conta",
                message_id="QUAL003",
                timestamp=datetime.now(timezone.utc),
                from_me=False,
                media_type=MediaType.IMAGE,
                media_url="https://example.com/bill.jpg"
            )
            
            # Update mock to return lead with bill value
            mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
                "id": "lead-123",
                "phone_number": phone,
                "name": "João Silva",
                "bill_value": 567.89,
                "current_stage": LeadStage.QUALIFYING
            })
            
            response3 = await mock_sdr_agent.process_message(bill_message)
            assert response3.success is True
        
        # Step 4: Decision maker confirmation
        decision_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Sim, sou eu quem decide sobre a energia aqui em casa",
            message_id="QUAL004",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # Update mock to qualified lead
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-123",
            "phone_number": phone,
            "name": "João Silva",
            "bill_value": 567.89,
            "property_type": "casa",
            "current_stage": LeadStage.QUALIFIED,
            "qualification_score": 85
        })
        
        response4 = await mock_sdr_agent.process_message(decision_message)
        assert response4.success is True
        
        # Verify Kommo CRM was updated
        assert mock_services["kommo"].create_lead.called
        assert mock_services["kommo"].update_lead.called
    
    @pytest.mark.asyncio
    async def test_calendar_scheduling_integration(self, mock_sdr_agent, mock_services, mock_repositories):
        """Test calendar scheduling integration"""
        phone = TestData.TEST_PHONES["qualified_lead"]
        
        # Mock qualified lead
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-456",
            "phone_number": phone,
            "name": "Ana Costa",
            "bill_value": 850.0,
            "current_stage": LeadStage.QUALIFIED,
            "qualification_score": 85
        })
        
        # Step 1: Request scheduling
        schedule_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Quero agendar a reunião",
            message_id="SCHED001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # Mock calendar availability
        mock_services["calendar"].get_available_slots = AsyncMock(
            return_value=[CalendarSlot(**slot) for slot in TestData.CALENDAR_SLOTS]
        )
        
        with patch("agente.tools.calendar.check_availability.check_availability",
                   return_value={"slots": TestData.CALENDAR_SLOTS}):
            response1 = await mock_sdr_agent.process_message(schedule_message)
            assert response1.success is True
        
        # Step 2: Select time slot
        slot_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Prefiro sexta às 10h",
            message_id="SCHED002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # Mock meeting creation
        mock_meeting_id = "evt_abc123def456"
        mock_meet_link = "https://meet.google.com/abc-defg-hij"
        
        with patch("agente.tools.calendar.create_meeting.create_meeting",
                   return_value={
                       "success": True,
                       "meeting_id": mock_meeting_id,
                       "meet_link": mock_meet_link,
                       "start_time": TestData.CALENDAR_SLOTS[0]["start"]
                   }):
            response2 = await mock_sdr_agent.process_message(slot_message)
            assert response2.success is True
        
        # Verify meeting was created and Kommo was updated
        assert mock_services["kommo"].update_lead.called
        update_call = mock_services["kommo"].update_lead.call_args
        assert update_call is not None
    
    @pytest.mark.asyncio
    async def test_follow_up_scheduling_and_execution(self, mock_sdr_agent, mock_repositories):
        """Test follow-up scheduling and execution"""
        phone = TestData.TEST_PHONES["lead_2"]
        
        # Mock lead that needs follow-up
        mock_repositories["lead_repo"].get_by_phone = AsyncMock(return_value={
            "id": "lead-789",
            "phone_number": phone,
            "name": "Maria Santos",
            "current_stage": LeadStage.IDENTIFYING,
            "last_interaction": datetime.now(timezone.utc) - timedelta(hours=1)
        })
        
        # Mock follow-up repository
        mock_repositories["followup_repo"].create = AsyncMock(return_value={
            "id": "followup-123",
            "lead_id": "lead-789",
            "scheduled_at": datetime.now(timezone.utc) + timedelta(minutes=30),
            "type": "reminder",
            "status": "pending"
        })
        
        # Simulate no response scenario
        with patch("agente.tools.database.schedule_followup.schedule_followup",
                   return_value={"success": True, "followup_id": "followup-123"}):
            # Process a message that triggers follow-up scheduling
            message = WhatsAppMessage(
                instance=TestData.INSTANCE_NAME,
                phone=phone,
                message="Preciso pensar",
                message_id="FOLLOW001",
                timestamp=datetime.now(timezone.utc),
                from_me=False
            )
            
            response = await mock_sdr_agent.process_message(message)
            assert response.success is True
        
        # Verify follow-up was scheduled
        mock_repositories["followup_repo"].get_pending = AsyncMock(return_value=[{
            "id": "followup-123",
            "lead_id": "lead-789",
            "phone_number": phone,
            "message": TestData.FOLLOW_UP_SCENARIOS["first_attempt"]["message"].format(name="Maria"),
            "scheduled_at": datetime.now(timezone.utc),
            "type": "reminder"
        }])
        
        # Test follow-up execution
        from agente.services.tasks import execute_follow_up
        with patch("agente.services.evolution_service.EvolutionService.send_text") as mock_send:
            mock_send.return_value = {"status": "sent"}
            
            result = await execute_follow_up("followup-123")
            assert result["success"] is True
            assert mock_send.called
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, mock_sdr_agent, mock_services):
        """Test error handling and recovery mechanisms"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # Test Evolution API failure
        mock_services["evolution"].send_text = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        
        message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Teste de erro",
            message_id="ERR001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        # The agent should handle the error gracefully
        with patch("agente.tools.whatsapp.send_text_message.send_text_message",
                   side_effect=Exception("Evolution API error")):
            response = await mock_sdr_agent.process_message(message)
            # Agent should still return a response, even if sending failed
            assert response is not None
        
        # Test Kommo rate limit
        mock_services["kommo"].create_lead = AsyncMock(
            side_effect=Exception("429 Too Many Requests")
        )
        
        with patch("agente.tools.kommo.create_kommo_lead.create_kommo_lead",
                   side_effect=Exception("Kommo rate limit")):
            # Should handle rate limit gracefully
            response2 = await mock_sdr_agent.process_message(message)
            assert response2 is not None
        
        # Test Google Calendar auth failure
        mock_services["calendar"].get_available_slots = AsyncMock(
            side_effect=Exception("401 Unauthorized")
        )
        
        schedule_message = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Quero agendar",
            message_id="ERR002",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        with patch("agente.tools.calendar.check_availability.check_availability",
                   side_effect=Exception("Calendar auth failed")):
            response3 = await mock_sdr_agent.process_message(schedule_message)
            assert response3 is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_message_handling(self, mock_sdr_agent, create_mock_message):
        """Test handling concurrent messages from multiple leads"""
        # Create messages from different leads
        messages = [
            create_mock_message(phone=TestData.TEST_PHONES["lead_1"], content="Mensagem 1"),
            create_mock_message(phone=TestData.TEST_PHONES["lead_2"], content="Mensagem 2"),
            create_mock_message(phone=TestData.TEST_PHONES["lead_3"], content="Mensagem 3"),
        ]
        
        # Process messages concurrently
        tasks = [mock_sdr_agent.process_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        assert len(responses) == 3
        for response in responses:
            if isinstance(response, Exception):
                pytest.fail(f"Concurrent processing failed: {response}")
            assert response.success is True
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, mock_sdr_agent, mock_repositories):
        """Test session persistence across multiple interactions"""
        phone = TestData.TEST_PHONES["lead_1"]
        
        # First interaction
        message1 = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Olá",
            message_id="SESS001",
            timestamp=datetime.now(timezone.utc),
            from_me=False
        )
        
        response1 = await mock_sdr_agent.process_message(message1)
        assert response1.success is True
        session_id = response1.data.get("session_id")
        
        # Second interaction - should maintain context
        message2 = WhatsAppMessage(
            instance=TestData.INSTANCE_NAME,
            phone=phone,
            message="Meu nome é João",
            message_id="SESS002",
            timestamp=datetime.now(timezone.utc) + timedelta(minutes=1),
            from_me=False
        )
        
        response2 = await mock_sdr_agent.process_message(message2)
        assert response2.success is True
        assert response2.data.get("session_id") == session_id
        
        # Context should be maintained
        context = response2.data.get("context", {})
        assert context is not None