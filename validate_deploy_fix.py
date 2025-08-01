#!/usr/bin/env python3
"""
VALIDAÇÃO DE CORREÇÃO DE DEPLOY - SDR IA SolarPrime
Verifica se as correções de importação resolveram o problema de deploy
"""

import sys
import traceback
from pathlib import Path

print("🔧 VALIDAÇÃO DE CORREÇÃO DE DEPLOY - SDR IA SOLARPRIME")
print("=" * 60)

def test_import(module_name, description):
    """Testa importação de um módulo"""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except Exception as e:
        print(f"❌ {description}: FALHA - {str(e)}")
        traceback.print_exc()
        return False

def test_config_imports():
    """Testa importações específicas do config"""
    try:
        from agente.core.config import PORT, HOST, DEBUG, LOG_LEVEL, ENVIRONMENT, API_PORT
        print(f"✅ Config imports: OK")
        print(f"   📊 PORT: {PORT}")
        print(f"   🌐 HOST: {HOST}")
        print(f"   🔧 API_PORT: {API_PORT}")
        print(f"   🐛 DEBUG: {DEBUG}")
        print(f"   📝 LOG_LEVEL: {LOG_LEVEL}")
        print(f"   🌍 ENVIRONMENT: {ENVIRONMENT}")
        return True
    except Exception as e:
        print(f"❌ Config imports: FALHA - {str(e)}")
        traceback.print_exc()
        return False

def test_fastapi_apps():
    """Testa carregamento das aplicações FastAPI"""
    apps_tested = []
    
    # Teste agente.main:app
    try:
        from agente.main import app as agente_app
        print(f"✅ agente.main:app: OK (FastAPI {type(agente_app).__name__})")
        print(f"   📋 Title: {agente_app.title}")
        apps_tested.append(("agente.main:app", True))
    except Exception as e:
        print(f"❌ agente.main:app: FALHA - {str(e)}")
        apps_tested.append(("agente.main:app", False))
    
    # Teste api.main:app (se existir)
    try:
        from api.main import app as api_app
        print(f"✅ api.main:app: OK (FastAPI {type(api_app).__name__})")
        apps_tested.append(("api.main:app", True))
    except Exception as e:
        print(f"❌ api.main:app: FALHA - {str(e)}")
        apps_tested.append(("api.main:app", False))
    
    return apps_tested

def main():
    """Executa todos os testes de validação"""
    print("🧪 EXECUTANDO TESTES DE VALIDAÇÃO\n")
    
    results = []
    
    # 1. Teste de importações básicas
    print("1️⃣ TESTE DE IMPORTAÇÕES BÁSICAS")
    print("-" * 40)
    results.append(test_import("agente.core.config", "Core config"))
    results.append(test_import("agente.main", "Main module"))
    results.append(test_import("agente.core.agent", "SDR Agent"))
    print()
    
    # 2. Teste de importações específicas do config
    print("2️⃣ TESTE DE IMPORTAÇÕES ESPECÍFICAS DO CONFIG")
    print("-" * 40)
    results.append(test_config_imports())
    print()
    
    # 3. Teste de aplicações FastAPI
    print("3️⃣ TESTE DE APLICAÇÕES FASTAPI")
    print("-" * 40)
    apps_results = test_fastapi_apps()
    results.extend([result[1] for result in apps_results])
    print()
    
    # 4. Relatório final
    print("📊 RELATÓRIO FINAL")
    print("=" * 40)
    
    successful_tests = sum(results)
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Testes bem-sucedidos: {successful_tests}/{total_tests}")
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"\n🎉 VALIDAÇÃO: APROVADA!")
        print(f"✅ O problema de deploy foi corrigido com sucesso!")
        print(f"✅ Sistema pronto para deploy no EasyPanel!")
        
        print(f"\n📋 INSTRUÇÕES PARA DEPLOY:")
        print(f"1. Use comando: uvicorn agente.main:app --host 0.0.0.0 --port 8000")
        print(f"2. Ou configure no EasyPanel: agente.main:app")
        print(f"3. Certifique-se de que as variáveis de ambiente estão configuradas")
        
        return True
    else:
        print(f"\n❌ VALIDAÇÃO: REPROVADA!")
        print(f"⚠️ Ainda existem problemas que precisam ser resolvidos")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)