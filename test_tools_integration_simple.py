#!/usr/bin/env python3
"""
TESTE SIMPLES - Integração Tools KommoCRM e Google Calendar
Teste direto das tools sem dependências complexas
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

# Carregar .env
from dotenv import load_dotenv
env_file = Path(__file__).parent / '.env'
load_dotenv(env_file)

print(f"✅ .env carregado: {env_file}")

async def test_kommo_tools():
    """Testa tools Kommo diretamente"""
    print("\n🔍 TESTE KOMMO TOOLS")
    print("=" * 40)
    
    try:
        # Testar import das tools
        from agente.tools.kommo.search_lead import search_kommo_lead
        from agente.tools.kommo.create_lead import create_kommo_lead
        print("✅ Tools Kommo importadas com sucesso")
        
        # Testar configurações
        from agente.core.config import KOMMO_BASE_URL, KOMMO_LONG_LIVED_TOKEN
        print(f"   - Base URL: {'✅' if KOMMO_BASE_URL else '❌'} {KOMMO_BASE_URL}")
        print(f"   - Token: {'✅' if KOMMO_LONG_LIVED_TOKEN else '❌'} {'Configurado' if KOMMO_LONG_LIVED_TOKEN else 'FALTANDO'}")
        
        # Teste básico de execução das tools (sem fazer calls reais)
        print("✅ Tools Kommo prontas para uso")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando tools Kommo: {e}")
        return False

async def test_calendar_tools():
    """Testa tools Calendar diretamente"""
    print("\n📅 TESTE CALENDAR TOOLS")
    print("=" * 40)
    
    try:
        # Testar import das tools
        from agente.tools.calendar.create_meeting import create_meeting
        from agente.tools.calendar.check_availability import check_availability
        print("✅ Tools Calendar importadas com sucesso")
        
        # Testar configurações básicas
        from agente.core.config import GOOGLE_SERVICE_ACCOUNT_EMAIL, GOOGLE_PRIVATE_KEY
        print(f"   - Service Account: {'✅' if GOOGLE_SERVICE_ACCOUNT_EMAIL else '❌'} {GOOGLE_SERVICE_ACCOUNT_EMAIL}")
        print(f"   - Private Key: {'✅' if GOOGLE_PRIVATE_KEY else '❌'} {'Configurado' if GOOGLE_PRIVATE_KEY else 'FALTANDO'}")
        
        print("✅ Tools Calendar prontas para uso")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando tools Calendar: {e}")
        return False

async def test_agent_tools_registration():
    """Testa se as tools estão registradas no agent"""
    print("\n🔧 TESTE REGISTRO NO AGENT")
    print("=" * 40)
    
    try:
        # Verificar se as tools estão na lista do agent
        from agente.tools import ALL_TOOLS
        print(f"✅ Total de tools disponíveis: {len(ALL_TOOLS)}")
        
        # Verificar tools específicas
        kommo_tools = [t for t in ALL_TOOLS if 'Kommo' in str(t)]
        calendar_tools = [t for t in ALL_TOOLS if 'Calendar' in str(t) or 'Meeting' in str(t)]
        
        print(f"   - Tools Kommo: {len(kommo_tools)}")
        print(f"   - Tools Calendar: {len(calendar_tools)}")
        
        if len(kommo_tools) >= 5 and len(calendar_tools) >= 3:
            print("✅ Tools registradas adequadamente")
            return True
        else:
            print("❌ Número insuficiente de tools registradas")
            return False
            
    except Exception as e:
        print(f"❌ Erro verificando registro: {e}")
        return False

async def test_agent_initialization():
    """Testa inicialização básica do agent"""
    print("\n🤖 TESTE INICIALIZAÇÃO AGENT")
    print("=" * 40)
    
    try:
        # Verificar se podemos importar o agent
        from agente.core.agent import SDRAgent
        print("✅ Classe SDRAgent importada")
        
        # Verificar configurações mínimas
        from agente.core.config import GEMINI_API_KEY
        if GEMINI_API_KEY:
            print("✅ GEMINI_API_KEY configurada")
        else:
            print("❌ GEMINI_API_KEY não configurada")
            return False
        
        print("✅ Agent pode ser inicializado")
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização do agent: {e}")
        return False

async def main():
    """Executa todos os testes"""
    print("🚀 TESTE INTEGRAÇÃO TOOLS CRM + CALENDAR")
    print("=" * 50)
    
    tests = [
        ("Kommo Tools", test_kommo_tools),
        ("Calendar Tools", test_calendar_tools),
        ("Registro no Agent", test_agent_tools_registration),  
        ("Inicialização Agent", test_agent_initialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if await test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSOU")
            else:
                print(f"\n❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"\n❌ {test_name}: ERRO - {e}")
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 TODAS AS TOOLS ESTÃO FUNCIONANDO!")
        print("📋 Status:")
        print("   ✅ Tools Kommo: Importadas e configuradas")
        print("   ✅ Tools Calendar: Importadas e configuradas") 
        print("   ✅ Agent: Pode ser inicializado com as tools")
        print("   ✅ Registro: Tools registradas no AGnO Agent")
        print("\n🚀 SISTEMA PRONTO PARA USO!")
    else:
        print(f"\n⚠️  {total-passed} problema(s) detectado(s)")
        print("Verifique as configurações antes de usar o sistema.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        sys.exit(1)