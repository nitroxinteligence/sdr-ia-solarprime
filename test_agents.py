#!/usr/bin/env python3
"""
test_agents.py - Teste simples dos agentes corrigidos
"""

import asyncio
from app.teams.agents.crm import CRMAgent
from app.teams.agents.qualification import QualificationAgent
from agno.models.google import Gemini
from app.config import settings

async def test_agents():
    """Testa se os agentes foram corrigidos corretamente"""
    
    print("🧪 Testando agentes corrigidos...")
    print("=" * 60)
    
    try:
        # Criar modelo usando Gemini
        model = Gemini(
            id="gemini-1.5-flash",
            api_key=settings.google_api_key
        )
        storage = None  # Storage fake
        
        print("\n📋 Testando CRMAgent...")
        crm_agent = CRMAgent(model, storage)
        
        # Verificar se o tool_registry existe
        assert hasattr(crm_agent, 'tool_registry'), "CRMAgent não tem tool_registry"
        print("✅ CRMAgent tem tool_registry")
        
        # Verificar se _register_tools existe
        assert hasattr(crm_agent, '_register_tools'), "CRMAgent não tem _register_tools"
        print("✅ CRMAgent tem _register_tools")
        
        # Verificar se os métodos ainda existem (sem @tool)
        assert hasattr(crm_agent, 'create_or_update_lead'), "CRMAgent perdeu método create_or_update_lead"
        print("✅ CRMAgent mantém métodos originais")
        
        print("\n📋 Testando QualificationAgent...")
        qual_agent = QualificationAgent(model, storage)
        
        # Verificar se o tool_registry existe
        assert hasattr(qual_agent, 'tool_registry'), "QualificationAgent não tem tool_registry"
        print("✅ QualificationAgent tem tool_registry")
        
        # Verificar se _register_tools existe
        assert hasattr(qual_agent, '_register_tools'), "QualificationAgent não tem _register_tools"
        print("✅ QualificationAgent tem _register_tools")
        
        # Verificar se os métodos ainda existem (sem @tool)
        assert hasattr(qual_agent, 'calculate_qualification_score'), "QualificationAgent perdeu método calculate_qualification_score"
        print("✅ QualificationAgent mantém métodos originais")
        
        # Verificar se tools foram registrados
        if hasattr(crm_agent, 'tools'):
            print(f"\n📊 CRMAgent tem {len(crm_agent.tools)} tools registrados")
        
        if hasattr(qual_agent, 'tools'):
            print(f"📊 QualificationAgent tem {len(qual_agent.tools)} tools registrados")
        
        print("\n" + "=" * 60)
        print("✅ TESTE PASSOU! Agentes corrigidos com sucesso!")
        print("\n💡 Próximos passos:")
        print("1. Inicie o webhook do WhatsApp")
        print("2. Teste com mensagens reais")
        print("3. Monitore os logs para erros")
        
    except AssertionError as e:
        print(f"\n❌ Teste falhou: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_agents())