#!/usr/bin/env python3
"""
Teste Simples da Integração
===========================
Teste com números de telefone menores para verificar a integração
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from repositories.lead_repository import lead_repository
from models.lead import LeadCreate


async def test_simple():
    """Teste simples da integração"""
    
    print("🚀 Teste Simples - Integração Supabase + SDR Agent\n")
    
    # 1. Testar criação direta de lead (com número menor)
    print("1️⃣ Testando criação de lead...")
    try:
        lead_data = LeadCreate(
            phone_number="11999999999",  # 11 caracteres apenas
            name="Teste Integração"
        )
        lead = await lead_repository.create_or_update(lead_data)
        
        if lead:
            print(f"✅ Lead criado: {lead.id}")
            print(f"   Nome: {lead.name}")
            print(f"   Telefone: {lead.phone_number}")
        else:
            print("❌ Falha ao criar lead")
            
    except Exception as e:
        print(f"❌ Erro ao criar lead: {e}")
    
    # 2. Testar o agente (com número menor)
    print("\n2️⃣ Testando agente SDR...")
    try:
        agent = SDRAgent()
        
        # Usar número de telefone menor
        phone = "11888888888"  # 11 caracteres
        message = "Olá, quero saber sobre energia solar"
        
        response = await agent.process_message(message, phone)
        
        if isinstance(response, tuple):
            response_text = response[0]
            print(f"✅ Agente respondeu: {response_text[:100]}...")
        else:
            print(f"✅ Agente respondeu: {response[:100]}...")
            
        # Verificar se foi salvo no banco
        saved_lead = await lead_repository.get_by_phone(phone)
        if saved_lead:
            print(f"✅ Lead salvo no banco: {saved_lead.id}")
        else:
            print("⚠️  Lead não foi salvo no banco")
            
    except Exception as e:
        print(f"❌ Erro no agente: {e}")
    
    # 3. Verificar dados no banco
    print("\n3️⃣ Verificando dados salvos...")
    try:
        leads = await lead_repository.get_all(limit=5)
        print(f"✅ Total de leads no banco: {len(leads)}")
        
        if leads:
            print("\nÚltimos leads:")
            for lead in leads[:3]:
                print(f"   - {lead.name or 'Sem nome'} | {lead.phone_number}")
                
    except Exception as e:
        print(f"❌ Erro ao buscar leads: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Dica: Execute o script SQL 'fix_phone_field_with_views.sql'")
    print("   no Supabase para corrigir o limite do campo phone_number")
    print("=" * 50)


async def main():
    """Função principal"""
    await test_simple()


if __name__ == "__main__":
    asyncio.run(main())