#!/usr/bin/env python3
"""
Teste básico para validar as correções implementadas no sistema SDR Agent.
Este script testa as principais funcionalidades corrigidas.
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Testa se todos os imports críticos funcionam"""
    print("🧪 Testando imports...")
    
    try:
        # Test core types
        from agente.core.types import WhatsAppMessage, Lead, Conversation, Message, AgentResponse
        print("✅ Core types importados com sucesso")
        
        # Test repositories
        from agente.repositories.lead_repository import LeadRepository
        from agente.repositories.conversation_repository import ConversationRepository  
        from agente.repositories.message_repository import MessageRepository
        print("✅ Repositories importados com sucesso")
        
        # Test core components
        from agente.core.context_manager import ContextManager
        from agente.core.session_manager import SessionManager
        print("✅ Core components importados com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado nos imports: {e}")
        return False

def test_pydantic_models():
    """Testa se os modelos Pydantic estão funcionando"""
    print("🧪 Testando modelos Pydantic...")
    
    try:
        from agente.core.types import WhatsAppMessage, Lead, Conversation
        
        # Test WhatsAppMessage
        msg = WhatsAppMessage(
            instance_id="test_instance",
            phone="5511999999999",
            name="Test User",
            message="Olá, teste!",
            message_id="test_msg_123",
            timestamp="2025-01-01T12:00:00Z"
        )
        print(f"✅ WhatsAppMessage criada: {msg.phone}")
        
        # Test Lead
        lead = Lead(
            phone_number="5511999999999",
            name="Test Lead"
        )
        print(f"✅ Lead criado: {lead.name}")
        
        # Test Conversation
        import uuid
        conv = Conversation(
            lead_id=uuid.uuid4(),
            session_id="test_session",
            phone="5511999999999"
        )
        print(f"✅ Conversation criada: {conv.session_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos modelos Pydantic: {e}")
        return False

def test_repository_aliases():
    """Testa se os métodos alias dos repositories funcionam"""
    print("🧪 Testando métodos alias dos repositories...")
    
    try:
        from agente.repositories.lead_repository import LeadRepository
        from agente.repositories.conversation_repository import ConversationRepository
        
        # Test LeadRepository alias
        lead_repo = LeadRepository()
        if hasattr(lead_repo, 'get_by_phone'):
            print("✅ LeadRepository.get_by_phone() alias existe")
        else:
            print("❌ LeadRepository.get_by_phone() alias faltando")
            return False
        
        # Test ConversationRepository alias  
        conv_repo = ConversationRepository()
        if hasattr(conv_repo, 'get_or_create'):
            print("✅ ConversationRepository.get_or_create() alias existe")
        else:
            print("❌ ConversationRepository.get_or_create() alias faltando")
            return False
            
        if hasattr(conv_repo, 'update_last_message_at'):
            print("✅ ConversationRepository.update_last_message_at() método existe")
        else:
            print("❌ ConversationRepository.update_last_message_at() método faltando")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro testando repository aliases: {e}")
        return False

async def test_context_manager():
    """Testa se o ContextManager pode ser inicializado"""
    print("🧪 Testando ContextManager...")
    
    try:
        from agente.core.context_manager import ContextManager
        
        # Test initialization
        context_mgr = ContextManager()
        print("✅ ContextManager inicializado com sucesso")
        
        # Test if repositories are properly initialized
        if hasattr(context_mgr, 'lead_repo') and context_mgr.lead_repo:
            print("✅ LeadRepository inicializado no ContextManager")
        else:
            print("❌ LeadRepository não inicializado no ContextManager")
            return False
            
        if hasattr(context_mgr, 'conversation_repo') and context_mgr.conversation_repo:
            print("✅ ConversationRepository inicializado no ContextManager")
        else:
            print("❌ ConversationRepository não inicializado no ContextManager")  
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro testando ContextManager: {e}")
        return False

def test_agent_response_extraction():
    """Testa a função de extração de resposta do agente"""
    print("🧪 Testando extração de resposta do agente...")
    
    try:
        from agente.core.agent import SDRAgent
        
        # Create a mock agent without full initialization
        agent = object.__new__(SDRAgent)
        agent.name = "Test Agent"
        
        # Test different response types
        test_cases = [
            ("string response", "Olá! Como posso ajudar?"),
            ("boolean True", True),
            ("boolean False", False),
            ("dict response", {"content": "Resposta em dict"}),
            ("None response", None)
        ]
        
        for case_name, test_response in test_cases:
            try:
                result = agent._extract_response_text(test_response)
                print(f"✅ {case_name}: {result[:50]}...")
            except Exception as e:
                print(f"❌ {case_name} falhou: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro testando extração de resposta: {e}")
        return False

def test_configuration():
    """Testa se as configurações estão carregando"""
    print("🧪 Testando configurações...")
    
    try:
        from agente.core.config import GEMINI_API_KEY, EVOLUTION_API_URL, SUPABASE_URL
        
        # Check if critical configs are defined (not necessarily filled)
        if GEMINI_API_KEY is not None:
            print("✅ GEMINI_API_KEY configurado")
        else:
            print("⚠️  GEMINI_API_KEY não configurado")
            
        if EVOLUTION_API_URL is not None:
            print("✅ EVOLUTION_API_URL configurado")
        else:
            print("⚠️  EVOLUTION_API_URL não configurado")
            
        if SUPABASE_URL is not None:
            print("✅ SUPABASE_URL configurado")
        else:
            print("⚠️  SUPABASE_URL não configurado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro testando configurações: {e}")
        return False

async def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema SDR Agent...")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Modelos Pydantic", test_pydantic_models),  
        ("Repository Aliases", test_repository_aliases),
        ("ContextManager", test_context_manager),
        ("Agent Response Extraction", test_agent_response_extraction),
        ("Configurações", test_configuration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            if result:
                passed += 1
                print(f"✅ {test_name} PASSOU")
            else:
                failed += 1
                print(f"❌ {test_name} FALHOU")
                
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERRO: {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DOS TESTES")
    print("=" * 60)
    print(f"✅ Testes que passaram: {passed}")
    print(f"❌ Testes que falharam: {failed}")
    print(f"📈 Taxa de sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        return True
    else:
        print(f"\n⚠️  {failed} teste(s) falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    asyncio.run(run_all_tests())