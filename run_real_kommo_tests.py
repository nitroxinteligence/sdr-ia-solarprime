#!/usr/bin/env python3
"""
Executar TESTES REAIS do Kommo CRM diretamente com Python
Baseado no sucesso dos testes do Google Calendar
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Setup do ambiente
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Carrega .env
env_path = root_dir / '.env'
load_dotenv(env_path)
os.environ['PYTEST_RUNNING'] = 'true'

print("🚀 EXECUTANDO TESTES REAIS DO KOMMO CRM")
print("=" * 60)

# Importa a classe de teste
from agente.tests.real_integration.test_kommo_crm_real import TestKommoCRMReal

def run_kommo_tests():
    """Executa testes do Kommo CRM."""
    print("\n💼 TESTES KOMMO CRM REAL")
    print("=" * 40)
    
    test_class = TestKommoCRMReal()
    test_class.test_prefix = "[TEST-CRM]"
    test_class.created_leads = []
    
    # Configura URLs e headers
    kommo_subdomain = os.getenv('KOMMO_SUBDOMAIN')
    test_class.base_url = f"https://{kommo_subdomain}.kommo.com/api/v4"
    test_class.headers = {
        'Authorization': f"Bearer {os.getenv('KOMMO_LONG_LIVED_TOKEN')}",
        'Content-Type': 'application/json'
    }
    
    tests_run = 0
    tests_passed = 0
    
    # Lista de métodos de teste
    test_methods = [
        'test_environment_validation_kommo',
        'test_kommo_authentication_real',
        'test_get_pipelines_real',
        'test_create_lead_real',
        'test_complete_lead_cycle_real',
        'test_search_leads_real',
        'test_rate_limiting_kommo'
    ]
    
    for test_name in test_methods:
        print(f"\n🧪 Executando: {test_name}")
        print("-" * 50)
        
        try:
            test_method = getattr(test_class, test_name)
            test_method()
            print(f"✅ PASSOU: {test_name}")
            tests_passed += 1
        except Exception as e:
            print(f"❌ FALHOU: {test_name}")
            print(f"   Erro: {str(e)}")
        
        tests_run += 1
    
    # Cleanup de leads criados
    if hasattr(test_class, 'created_leads') and test_class.created_leads:
        print(f"\n🗑️ LIMPEZA DE {len(test_class.created_leads)} LEADS DE TESTE")
        try:
            import requests
            
            for lead_id in test_class.created_leads:
                try:
                    delete_url = f"{test_class.base_url}/leads/{lead_id}"
                    response = requests.delete(delete_url, headers=test_class.headers)
                    if response.status_code in [200, 204, 404]:
                        print(f"   ✅ Lead {lead_id} removido/arquivado")
                    else:
                        print(f"   ⚠️ Lead {lead_id}: status {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Erro ao remover lead {lead_id}: {e}")
        except Exception as e:
            print(f"   ❌ Erro geral na limpeza: {e}")
    
    print(f"\n📊 RESULTADOS KOMMO CRM: {tests_passed}/{tests_run} testes passaram")
    return tests_passed, tests_run

def main():
    """Função principal."""
    print("Carregando configurações...")
    
    # Verifica se as credenciais estão disponíveis
    required_vars = [
        'KOMMO_SUBDOMAIN',
        'KOMMO_LONG_LIVED_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ ERRO: Variáveis faltando: {', '.join(missing_vars)}")
        return
    
    print("✅ Credenciais carregadas com sucesso")
    print(f"   🏢 Subdomain: {os.getenv('KOMMO_SUBDOMAIN')}")
    print(f"   🔗 Pipeline ID: {os.getenv('KOMMO_PIPELINE_ID', 'N/A')}")
    
    # Executa os testes
    kommo_passed, kommo_run = run_kommo_tests()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("🏆 RESULTADO FINAL DOS TESTES REAIS KOMMO CRM")
    print("=" * 60)
    print(f"📊 Total de testes: {kommo_run}")
    print(f"✅ Testes passaram: {kommo_passed}")
    print(f"❌ Testes falharam: {kommo_run - kommo_passed}")
    print(f"📈 Taxa de sucesso: {(kommo_passed/kommo_run)*100:.1f}%")
    
    if kommo_passed == kommo_run:
        print("\n🎉 TODOS OS TESTES REAIS DO KOMMO PASSARAM!")
        print("   A integração com Kommo CRM está funcionando perfeitamente!")
    else:
        print(f"\n⚠️ {kommo_run - kommo_passed} teste(s) falharam")
        print("   Verifique os logs acima para detalhes")
    
    print("=" * 60)

if __name__ == "__main__":
    main()