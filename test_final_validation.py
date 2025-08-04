#!/usr/bin/env python3
"""
Teste Final de Validação - Verifica se a solução está funcionando
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)

async def test_calendar():
    """Testa Calendar básico"""
    from app.integrations.google_calendar import google_calendar_client
    
    print("\n📅 Testando Calendar...")
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    event = await google_calendar_client.create_event(
        title="Teste Final - Validação",
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        description="Teste de validação final",
        conference_data=True
    )
    
    if event and event.get('google_event_id'):
        print(f"✅ Calendar funcionando!")
        await google_calendar_client.delete_event(event['google_event_id'])
        return True
    else:
        print(f"❌ Calendar com problema")
        return False

async def test_agents():
    """Testa se os agents inicializam corretamente"""
    try:
        print("\n🤖 Testando Agents...")
        
        # Testar CRM Agent
        from app.teams.agents.crm import CRMAgent
        from agno.models import Model
        
        model = Model(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
        crm = CRMAgent(model=model, storage=None)
        print(f"  ✅ CRM Agent: {len(crm.tools)} tools registrados")
        
        # Testar Qualification Agent
        from app.teams.agents.qualification import QualificationAgent
        qual = QualificationAgent(model=model, storage=None)
        print(f"  ✅ Qualification Agent: {len(qual.tools)} tools registrados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos agents: {e}")
        return False

async def test_sdr_team():
    """Testa inicialização do SDR Team"""
    try:
        print("\n👥 Testando SDR Team...")
        from app.teams.sdr_team import SDRTeam
        
        team = SDRTeam()
        print(f"  ✅ SDR Team inicializado")
        
        # Testar processamento básico
        response = await team.process_message(
            message="Olá, quero saber sobre energia solar",
            phone="+5511999999999",
            lead_data={
                "id": "test-final",
                "name": "Teste Final",
                "phone": "+5511999999999"
            }
        )
        
        if response:
            print(f"  ✅ Processamento funcionando")
            return True
        else:
            print(f"  ⚠️ Sem resposta do processamento")
            return False
            
    except Exception as e:
        print(f"❌ Erro no SDR Team: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Executa todos os testes de validação"""
    print("="*60)
    print("🚀 TESTE FINAL DE VALIDAÇÃO")
    print("="*60)
    
    results = {
        "Calendar": await test_calendar(),
        "Agents": await test_agents(),
        "SDR Team": await test_sdr_team()
    }
    
    print("\n" + "="*60)
    print("📊 RESULTADOS FINAIS")
    print("="*60)
    
    for component, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {component}: {'OK' if status else 'FALHOU'}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTaxa de sucesso: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 SISTEMA 100% OPERACIONAL!")
        print("✅ Pronto para produção!")
    elif passed >= total * 0.7:
        print("\n⚠️ Sistema parcialmente operacional")
        print("Verifique os componentes que falharam")
    else:
        print("\n❌ Sistema com problemas críticos")
        print("Necessário revisar a implementação")

if __name__ == "__main__":
    asyncio.run(main())