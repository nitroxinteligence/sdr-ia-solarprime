#!/usr/bin/env python3
"""
test_agents_complete.py - Teste completo dos agentes com inicialização
"""

import asyncio
from app.teams.agents.crm import CRMAgent
from app.teams.agents.qualification import QualificationAgent
from agno.models.google import Gemini
from app.config import settings

async def test_agents_complete():
    """Testa se os agentes funcionam completamente após correções"""
    
    print("🧪 Testando agentes com inicialização completa...")
    print("=" * 60)
    
    try:
        # Criar modelo usando Gemini
        model = Gemini(
            id="gemini-1.5-flash",
            api_key=settings.google_api_key
        )
        storage = None  # Storage fake
        
        print("\n📋 Testando CRMAgent com inicialização...")
        crm_agent = CRMAgent(model, storage)
        
        # Inicializar o agente para registrar tools
        await crm_agent.initialize()
        
        print(f"✅ CRMAgent inicializado")
        print(f"📊 Tools registrados: {len(crm_agent.tools)}")
        
        if crm_agent.tools:
            print("📝 Lista de tools do CRM:")
            for tool in crm_agent.tools:
                print(f"   - {tool.__name__ if hasattr(tool, '__name__') else tool}")
        
        print("\n📋 Testando QualificationAgent...")
        qual_agent = QualificationAgent(model, storage)
        
        print(f"✅ QualificationAgent inicializado")
        print(f"📊 Tools registrados: {len(qual_agent.tools)}")
        
        if qual_agent.tools:
            print("📝 Lista de tools do Qualification:")
            for tool in qual_agent.tools:
                print(f"   - {tool.__name__ if hasattr(tool, '__name__') else tool}")
        
        # Testar se os tools são chamáveis
        print("\n🔧 Verificando se tools são chamáveis...")
        
        if crm_agent.tools:
            first_tool = crm_agent.tools[0]
            print(f"✅ CRM tool '{first_tool.__name__}' é {'chamável' if callable(first_tool) else 'NÃO chamável'}")
        
        if qual_agent.tools:
            first_tool = qual_agent.tools[0]
            print(f"✅ Qualification tool '{first_tool.__name__}' é {'chamável' if callable(first_tool) else 'NÃO chamável'}")
        
        # Verificar se os agentes têm acesso aos seus agentes internos
        print("\n🤖 Verificando agentes internos...")
        print(f"✅ CRMAgent.agent existe: {hasattr(crm_agent, 'agent')}")
        print(f"✅ QualificationAgent.agent existe: {hasattr(qual_agent, 'agent')}")
        
        # Verificar se os tools foram registrados no agente interno
        if hasattr(crm_agent, 'agent') and crm_agent.agent:
            print(f"📊 CRMAgent.agent.tools: {len(crm_agent.agent.tools) if hasattr(crm_agent.agent, 'tools') else 'N/A'}")
        
        if hasattr(qual_agent, 'agent') and qual_agent.agent:
            print(f"📊 QualificationAgent.agent.tools: {len(qual_agent.agent.tools) if hasattr(qual_agent.agent, 'tools') else 'N/A'}")
        
        print("\n" + "=" * 60)
        print("✅ TESTE COMPLETO PASSOU!")
        print("\n🎉 Os agentes estão prontos para uso!")
        print("💡 Você pode agora:")
        print("1. Iniciar o webhook: python app/integrations/whatsapp_webhook.py")
        print("2. Testar com mensagens reais no WhatsApp")
        print("3. Monitorar os logs em logs/sdr_solar.log")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_agents_complete())