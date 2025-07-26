#!/usr/bin/env python3
"""
Test Supabase Integration
=========================
Testa a integração completa com Supabase
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import create_sdr_agent
from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from services.database import db
from models.lead import LeadCreate

load_dotenv()


async def test_database_connection():
    """Testa conexão com Supabase"""
    print("1️⃣ Testando conexão com Supabase...")
    
    try:
        # Verificar health check
        is_connected = await db.health_check()
        
        if is_connected:
            print("✅ Conexão com Supabase estabelecida!")
            return True
        else:
            print("❌ Falha na conexão com Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False


async def test_crud_operations():
    """Testa operações CRUD básicas"""
    print("\n2️⃣ Testando operações CRUD...")
    
    try:
        # Criar lead de teste
        test_phone = f"5511{datetime.now().strftime('%H%M%S')}999"
        
        print(f"   Criando lead com telefone: {test_phone}")
        lead = await lead_repository.create_or_update(
            LeadCreate(
                phone_number=test_phone,
                name="Teste Supabase"
            )
        )
        print(f"   ✅ Lead criado: {lead.id}")
        
        # Buscar lead
        found_lead = await lead_repository.get_by_phone(test_phone)
        if found_lead:
            print(f"   ✅ Lead encontrado por telefone")
        
        # Atualizar lead
        updated_lead = await lead_repository.update(
            lead.id,
            {
                "email": "teste@supabase.com",
                "property_type": "casa",
                "bill_value": 450.00
            }
        )
        print(f"   ✅ Lead atualizado com sucesso")
        
        # Criar conversa
        conversation = await conversation_repository.create({
            "lead_id": str(lead.id),
            "session_id": f"test_{datetime.now().timestamp()}"
        })
        print(f"   ✅ Conversa criada: {conversation.id}")
        
        # Criar mensagens
        user_msg = await message_repository.save_user_message(
            conversation_id=conversation.id,
            content="Olá, quero saber sobre energia solar"
        )
        print(f"   ✅ Mensagem do usuário salva")
        
        assistant_msg = await message_repository.save_assistant_message(
            conversation_id=conversation.id,
            content="Olá! Fico feliz em ajudar com energia solar!"
        )
        print(f"   ✅ Mensagem do assistente salva")
        
        # Buscar mensagens
        messages = await message_repository.get_conversation_messages(conversation.id)
        print(f"   ✅ {len(messages)} mensagens encontradas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas operações CRUD: {e}")
        return False


async def test_agent_integration():
    """Testa integração do agente com Supabase"""
    print("\n3️⃣ Testando integração com agente SDR...")
    
    try:
        # Criar agente
        agent = create_sdr_agent()
        print("   ✅ Agente criado")
        
        # Processar mensagem de teste
        test_phone = f"5511{datetime.now().strftime('%H%M%S')}888"
        
        response, metadata = await agent.process_message(
            message="Oi, vi o anúncio sobre energia solar",
            phone_number=test_phone
        )
        
        print(f"   ✅ Mensagem processada")
        print(f"   📱 Telefone: {test_phone}")
        print(f"   💬 Resposta: {response[:100]}...")
        print(f"   📊 Estágio: {metadata.get('stage')}")
        
        # Verificar se foi salvo no banco
        lead = await lead_repository.get_by_phone(test_phone)
        if lead:
            print(f"   ✅ Lead salvo no Supabase: {lead.id}")
            
            # Buscar conversas
            conversations = await conversation_repository.get_lead_conversations(lead.id)
            print(f"   ✅ {len(conversations)} conversas encontradas")
            
            if conversations:
                # Buscar mensagens
                messages = await message_repository.get_conversation_messages(
                    conversations[0].id
                )
                print(f"   ✅ {len(messages)} mensagens salvas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração com agente: {e}")
        return False


async def test_analytics():
    """Testa funcionalidades de analytics"""
    print("\n4️⃣ Testando analytics e métricas...")
    
    try:
        # Buscar leads qualificados
        qualified_leads = await lead_repository.get_qualified_leads(min_score=50)
        print(f"   📊 {len(qualified_leads)} leads qualificados encontrados")
        
        # Buscar leads por estágio
        for stage in ["INITIAL_CONTACT", "QUALIFICATION", "SCHEDULING"]:
            leads = await lead_repository.get_by_stage(stage)
            print(f"   📊 {len(leads)} leads no estágio {stage}")
        
        # Contar mensagens recentes
        recent_messages = await message_repository.get_recent_messages(hours=24)
        print(f"   📊 {len(recent_messages)} mensagens nas últimas 24h")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro em analytics: {e}")
        return False


async def main():
    """Função principal"""
    print("🚀 Teste de Integração Supabase\n")
    
    # Verificar configurações
    configs = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
    }
    
    missing = [k for k, v in configs.items() if not v]
    
    if missing:
        print("❌ Configurações faltando:")
        for config in missing:
            print(f"   - {config}")
        print("\nConfigure as variáveis no arquivo .env")
        return
    
    print("✅ Todas as configurações encontradas!\n")
    
    # Executar testes
    tests = [
        ("Conexão com Banco", test_database_connection),
        ("Operações CRUD", test_crud_operations),
        ("Integração com Agente", test_agent_integration),
        ("Analytics e Métricas", test_analytics)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'='*50}")
        result = await test_func()
        results.append((name, result))
        
        if not result and name == "Conexão com Banco":
            print("\n⚠️ Sem conexão com banco, parando testes...")
            break
    
    # Resumo
    print(f"\n{'='*50}")
    print("📊 Resumo dos Testes:\n")
    
    for name, result in results:
        status = "✅ Passou" if result else "❌ Falhou"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! A integração com Supabase está funcionando!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")


if __name__ == "__main__":
    asyncio.run(main())