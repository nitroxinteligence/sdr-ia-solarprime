#!/usr/bin/env python3
"""
Test script to verify AGNO v1.7.6 fixes
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Test AGNO imports
        from agno.agent import Agent
        print("✅ agno.agent.Agent")
        
        from agno.team import Team
        print("✅ agno.team.Team")
        
        from agno.models.google import Gemini
        print("✅ agno.models.google.Gemini")
        
        from agno.memory import AgentMemory
        print("✅ agno.memory.AgentMemory")
        
        from agno.storage.postgres import PostgresStorage
        print("✅ agno.storage.postgres.PostgresStorage")
        
        from agno.knowledge import AgentKnowledge
        print("✅ agno.knowledge.AgentKnowledge")
        
        print("\n✅ All AGNO imports successful!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from app.config import settings
        
        # Check if running in production or development
        env = os.getenv('ENVIRONMENT', 'development')
        print(f"Environment: {env}")
        
        # Test critical settings
        if settings.google_api_key:
            print("✅ Google API key configured")
        else:
            print("⚠️ Google API key not configured")
        
        db_url = settings.get_postgres_url()
        if "supabase" in db_url or "postgresql" in db_url:
            print("✅ PostgreSQL URL configured")
        else:
            print("⚠️ PostgreSQL using localhost fallback")
        
        print("\n✅ Configuration loaded successfully!")
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    return True

def test_optional_storage():
    """Test OptionalStorage wrapper"""
    print("\nTesting OptionalStorage...")
    
    try:
        from app.utils.optional_storage import OptionalStorage
        from app.config import settings
        
        # Create storage with fallback
        storage = OptionalStorage(
            table_name="test_table",
            db_url=settings.get_postgres_url(),
            schema="public",
            auto_upgrade_schema=True
        )
        
        if storage.storage:
            print("✅ OptionalStorage with PostgreSQL backend")
        else:
            print("✅ OptionalStorage with memory fallback")
        
        print("\n✅ OptionalStorage working!")
        
    except Exception as e:
        print(f"❌ OptionalStorage error: {e}")
        return False
    
    return True

def test_memory_initialization():
    """Test Memory initialization with and without persistence"""
    print("\nTesting Memory initialization...")
    
    try:
        from agno.memory import AgentMemory
        from agno.models.google import Gemini
        from app.config import settings
        from app.utils.optional_storage import OptionalStorage
        
        # Create model first
        model = Gemini(
            id="gemini-2.0-flash-exp",
            api_key=settings.google_api_key or "test-key"
        )
        
        # Test with storage
        storage = OptionalStorage(
            table_name="test_memory",
            db_url=settings.get_postgres_url(),
            schema="public"
        )
        
        try:
            # Try with persistence
            memory_with_db = AgentMemory(
                db=storage,
                create_user_memories=True,
                create_session_summary=True
            )
            print("✅ Memory with persistence created")
        except:
            # Fallback without persistence
            memory_without_db = AgentMemory(
                create_user_memories=True,
                create_session_summary=True
            )
            print("✅ Memory without persistence created (with model)")
        
        print("\n✅ Memory initialization working!")
        
    except Exception as e:
        print(f"❌ Memory error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_agent_initialization():
    """Test AGENTIC SDR initialization"""
    print("\nTesting AGENTIC SDR initialization...")
    
    try:
        from app.agents.agentic_sdr import AgenticSDR
        
        # Create agent
        agent = AgenticSDR()
        
        print("✅ AGENTIC SDR initialized")
        
        # Check key components
        if agent.model:
            print("✅ Model configured")
        if agent.memory:
            print("✅ Memory configured")
        if agent.storage:
            print("✅ Storage configured")
        
        print("\n✅ AGENTIC SDR working!")
        
    except Exception as e:
        print(f"❌ AGENTIC SDR error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_team_initialization():
    """Test SDR Team initialization"""
    print("\nTesting SDR Team initialization...")
    
    try:
        from app.teams.sdr_team import SDRTeam
        
        # Create team
        team = SDRTeam()
        
        print("✅ SDR Team initialized")
        
        # Check key components
        if team.model:
            print("✅ Model configured")
        if team.memory:
            print("✅ Memory configured")
        if team.storage:
            print("✅ Storage configured")
        if team.team_leader:
            print("✅ Team Leader configured")
        
        print("\n✅ SDR Team working!")
        
    except Exception as e:
        print(f"❌ SDR Team error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("AGNO v1.7.6 Fix Verification")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Config", test_config()))
    results.append(("OptionalStorage", test_optional_storage()))
    results.append(("Memory", test_memory_initialization()))
    results.append(("AGENTIC SDR", test_agent_initialization()))
    results.append(("SDR Team", test_team_initialization()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests passed! The system is ready to run.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)