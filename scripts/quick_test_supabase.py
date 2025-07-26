#!/usr/bin/env python3
"""
Teste Rápido do Supabase
========================
Script simples para verificar se a integração está funcionando
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

# Carregar variáveis de ambiente
load_dotenv()


async def test_basic_connection():
    """Testa conexão básica"""
    print("1️⃣ Testando conexão com Supabase...")
    
    try:
        from services.database import db
        
        # Verificar se consegue conectar
        health = await db.health_check()
        
        if health:
            print("✅ Conexão estabelecida com sucesso!")
            return True
        else:
            print("❌ Falha na conexão")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def test_lead_operations():
    """Testa operações com leads"""
    print("\n2️⃣ Testando operações com leads...")
    
    try:
        from repositories.lead_repository import lead_repository
        
        # Criar lead de teste
        from models.lead import LeadCreate
        
        test_phone = "5511777777777"
        lead_data = LeadCreate(
            phone_number=test_phone,
            name="Teste Rápido"
        )
        lead = await lead_repository.create_or_update(lead_data)
        
        if lead:
            print(f"✅ Lead criado/atualizado: {lead.id}")
            
            # Buscar lead
            found = await lead_repository.get_by_phone(test_phone)
            if found:
                print(f"✅ Lead encontrado: {found.name}")
                
                # Deletar lead de teste
                deleted = await lead_repository.delete(lead.id)
                if deleted:
                    print("✅ Lead de teste removido")
                
                return True
        
        print("❌ Falha nas operações com leads")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def test_agent_integration():
    """Testa integração com o agente"""
    print("\n3️⃣ Testando integração com agente SDR...")
    
    try:
        from agents.sdr_agent import SDRAgent
        
        # Criar agente
        agent = SDRAgent()
        
        # Processar mensagem de teste
        response = await agent.process_message(
            "5511666666666",
            "Olá, quero saber sobre energia solar"
        )
        
        if response:
            print("✅ Agente processou mensagem com sucesso!")
            print(f"   Resposta: {response[:100]}...")
            return True
        
        print("❌ Falha no processamento do agente")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def main():
    """Executa todos os testes"""
    print("🚀 Teste Rápido - Integração Supabase + SDR Agent\n")
    
    results = []
    
    # Executar testes
    results.append(await test_basic_connection())
    results.append(await test_lead_operations())
    results.append(await test_agent_integration())
    
    # Resumo
    print("\n" + "=" * 50)
    total = len(results)
    passed = sum(results)
    
    if passed == total:
        print(f"✅ SUCESSO! Todos os {total} testes passaram!")
        print("🎉 A integração está funcionando perfeitamente!")
    else:
        print(f"❌ {total - passed} de {total} testes falharam")
        print("💡 Execute 'python scripts/verify_supabase_setup.py' para diagnóstico detalhado")


if __name__ == "__main__":
    asyncio.run(main())