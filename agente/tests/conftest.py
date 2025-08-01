"""
Pytest configuration and fixtures for SDR Agent tests.
"""

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load test environment
load_dotenv(".env.test")

from agente.core.agent import SDRAgent
from agente.core.config import Config
from agente.core.context_manager import ContextManager
from agente.core.humanizer import HelenHumanizer
from agente.core.message_processor import MessageProcessor
from agente.core.qualification_flow import QualificationFlow
from agente.core.session_manager import SessionManager
from agente.core.types import (
    ConversationState,
    Lead,
    LeadInfo,
    Message,
    ProcessedMessage,
    WhatsAppMessage,
)
from agente.services.supabase_service import SupabaseService
from agente.services.evolution_service import EvolutionService
from agente.services.kommo_service import KommoService
from agente.services.calendar_service import CalendarService


# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    config = MagicMock(spec=Config)
    config.SUPABASE_URL = "https://test.supabase.co"
    config.SUPABASE_KEY = "test-key"
    config.EVOLUTION_API_URL = "http://localhost:8080"
    config.EVOLUTION_API_KEY = "test-api-key"
    config.EVOLUTION_INSTANCE = "test-instance"
    config.KOMMO_SUBDOMAIN = "test"
    config.KOMMO_LONG_LIVED_TOKEN = "test-token"
    config.GOOGLE_API_KEY = "test-google-key"
    config.WEBHOOK_URL = "http://localhost:8000"
    config.BUSINESS_HOURS = {"start": "09:00", "end": "18:00", "timezone": "America/Recife"}
    config.AI_RESPONSE_DELAY_SECONDS = 2
    return config


@pytest.fixture
def mock_lead():
    """Mock lead for tests."""
    return Lead(
        id="test-lead-id",
        phone="5511999999999",
        name="Test User",
        email="test@example.com",
        stage="IDENTIFICATION",
        score=0,
        info=LeadInfo(
            solution_type=None,
            energy_value=None,
            has_discount=None,
            roof_access=None,
            energy_provider=None,
            cnpj=None,
            monthly_consumption=None
        ),
        qualification_status="in_progress",
        kommo_lead_id=None,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )


@pytest.fixture
def mock_whatsapp_message():
    """Mock WhatsApp message for tests."""
    return WhatsAppMessage(
        instance_id="test-instance",
        phone="5511999999999",
        name="Test User",
        message="Olá, quero saber sobre energia solar",
        message_id="test-msg-id",
        timestamp="1234567890",
        media_url=None,
        media_type=None
    )


@pytest_asyncio.fixture
async def mock_supabase_service():
    """Mock Supabase service for tests."""
    service = AsyncMock(spec=SupabaseService)
    
    # Mock common methods
    service.get_lead.return_value = None
    service.create_lead.return_value = {"id": "test-lead-id"}
    service.update_lead.return_value = {"id": "test-lead-id"}
    service.get_conversation.return_value = None
    service.create_conversation.return_value = {"id": "test-conv-id"}
    service.create_message.return_value = {"id": "test-msg-id"}
    
    return service


@pytest_asyncio.fixture
async def mock_evolution_service():
    """Mock Evolution service for tests."""
    service = AsyncMock(spec=EvolutionService)
    
    # Mock common methods
    service.send_text.return_value = {"success": True}
    service.send_typing.return_value = {"success": True}
    service.send_media.return_value = {"success": True}
    service.download_media.return_value = b"test-media-content"
    
    return service


@pytest_asyncio.fixture
async def mock_kommo_service():
    """Mock Kommo service for tests."""
    service = AsyncMock(spec=KommoService)
    
    # Mock common methods
    service.create_lead.return_value = {"id": 12345}
    service.update_lead.return_value = {"id": 12345}
    service.add_note.return_value = {"id": 67890}
    service.get_calendar_link.return_value = "https://calendar.kommo.com/test"
    
    return service


@pytest_asyncio.fixture
async def mock_calendar_service():
    """Mock Calendar service for tests."""
    service = AsyncMock(spec=CalendarService)
    
    # Mock common methods
    service.check_availability.return_value = [
        {"date": "2024-01-10", "time": "10:00", "available": True},
        {"date": "2024-01-10", "time": "14:00", "available": True}
    ]
    service.create_event.return_value = {"id": "test-event-id"}
    
    return service


@pytest.fixture
def helen_humanizer():
    """Create HelenHumanizer instance for tests."""
    return HelenHumanizer()


@pytest.fixture
def context_manager():
    """Create ContextManager instance for tests."""
    return ContextManager()


@pytest.fixture
def qualification_flow():
    """Create QualificationFlow instance for tests."""
    return QualificationFlow()


@pytest_asyncio.fixture
async def message_processor(
    mock_evolution_service,
    helen_humanizer
):
    """Create MessageProcessor instance for tests."""
    processor = MessageProcessor(
        evolution_service=mock_evolution_service,
        humanizer=helen_humanizer
    )
    return processor


@pytest_asyncio.fixture
async def session_manager():
    """Create SessionManager instance for tests."""
    manager = SessionManager()
    return manager


@pytest_asyncio.fixture
async def sdr_agent(
    mock_supabase_service,
    mock_evolution_service,
    mock_kommo_service,
    mock_calendar_service,
    context_manager,
    qualification_flow,
    message_processor,
    session_manager
):
    """Create SDRAgent instance with mocked dependencies."""
    with patch('agente.core.agent.SupabaseService', return_value=mock_supabase_service):
        with patch('agente.core.agent.EvolutionService', return_value=mock_evolution_service):
            with patch('agente.core.agent.KommoService', return_value=mock_kommo_service):
                with patch('agente.core.agent.CalendarService', return_value=mock_calendar_service):
                    agent = SDRAgent()
                    agent.supabase = mock_supabase_service
                    agent.evolution = mock_evolution_service
                    agent.kommo = mock_kommo_service
                    agent.calendar = mock_calendar_service
                    agent.context_manager = context_manager
                    agent.qualification_flow = qualification_flow
                    agent.message_processor = message_processor
                    agent.session_manager = session_manager
                    
                    # Mock AGnO agent
                    agent.agent = AsyncMock()
                    agent.agent.run.return_value = "Olá! Sou a Helen da SolarPrime. Como posso ajudar?"
                    
                    await agent.start()
                    yield agent
                    await agent.shutdown()


@pytest.fixture
def mock_conversation_state():
    """Mock conversation state for tests."""
    return ConversationState(
        stage="IDENTIFICATION",
        context={
            "awaiting_response": False,
            "last_question": None,
            "attempts": 0
        },
        lead_info=LeadInfo(),
        qualification_score=0,
        messages_count=1,
        last_interaction="2024-01-01T00:00:00Z"
    )


@pytest.fixture
def mock_processed_message():
    """Mock processed message for tests."""
    return ProcessedMessage(
        success=True,
        message="Mensagem processada com sucesso",
        error=None,
        metadata={
            "processing_time": 1.5,
            "tokens_used": 150
        }
    )


# Utility functions for tests

def create_mock_tool_response(success: bool = True, data: dict = None, error: str = None):
    """Create a mock tool response."""
    return {
        "success": success,
        "data": data or {},
        "error": error
    }


async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
    """Wait for a condition to be true."""
    start_time = asyncio.get_event_loop().time()
    while not condition_func():
        if asyncio.get_event_loop().time() - start_time > timeout:
            raise TimeoutError("Condition not met within timeout")
        await asyncio.sleep(interval)


def assert_message_sent(mock_evolution_service, phone: str, partial_message: str = None):
    """Assert that a message was sent via Evolution service."""
    calls = mock_evolution_service.send_text.call_args_list
    
    # Check if any call matches the phone
    for call in calls:
        args, kwargs = call
        if args[0] == phone:
            if partial_message:
                # Check if the message contains the partial text
                if partial_message in args[1]:
                    return True
            else:
                return True
    
    if partial_message:
        raise AssertionError(f"No message containing '{partial_message}' sent to {phone}")
    else:
        raise AssertionError(f"No message sent to {phone}")


def get_sent_messages(mock_evolution_service, phone: str = None):
    """Get all messages sent via Evolution service."""
    calls = mock_evolution_service.send_text.call_args_list
    messages = []
    
    for call in calls:
        args, kwargs = call
        if phone is None or args[0] == phone:
            messages.append({
                "phone": args[0],
                "message": args[1],
                "kwargs": kwargs
            })
    
    return messages


# Test environment setup

def setup_test_env():
    """Setup test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_KEY"] = "test-key"
    os.environ["EVOLUTION_API_URL"] = "http://localhost:8080"
    os.environ["EVOLUTION_API_KEY"] = "test-api-key"
    os.environ["EVOLUTION_INSTANCE"] = "test-instance"
    os.environ["KOMMO_SUBDOMAIN"] = "test"
    os.environ["KOMMO_LONG_LIVED_TOKEN"] = "test-token"
    os.environ["GOOGLE_API_KEY"] = "test-google-key"


# Call setup on import
setup_test_env()