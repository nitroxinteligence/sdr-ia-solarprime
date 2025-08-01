#!/usr/bin/env python3
"""
Script para testar DIRETAMENTE os testes reais do Google Calendar
Executa validações sem depender do framework pytest.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# CARREGA O .ENV CORRETAMENTE
env_path = root_dir / '.env'
print(f"🔧 Carregando variáveis de ambiente de: {env_path}")
load_dotenv(env_path)

from agente.core.config import (
    GOOGLE_SERVICE_ACCOUNT_EMAIL,
    GOOGLE_PRIVATE_KEY,
    GOOGLE_PROJECT_ID,
    GOOGLE_CALENDAR_ID,
    DISABLE_GOOGLE_CALENDAR
)

def check_credentials():
    """Verifica se temos credenciais reais do Google Calendar."""
    print("🔍 VERIFICANDO CREDENCIAIS GOOGLE CALENDAR")
    print("=" * 50)
    
    required_vars = {
        'GOOGLE_SERVICE_ACCOUNT_EMAIL': GOOGLE_SERVICE_ACCOUNT_EMAIL,
        'GOOGLE_PRIVATE_KEY': GOOGLE_PRIVATE_KEY,
        'GOOGLE_PROJECT_ID': GOOGLE_PROJECT_ID,
        'GOOGLE_CALENDAR_ID': GOOGLE_CALENDAR_ID or 'primary'
    }
    
    print("📋 Status das variáveis:")
    for name, value in required_vars.items():
        if value and value.strip() and not value.startswith('test-'):
            status = "✅ REAL"
            print(f"   {name}: {status}")
        elif value and value.strip():
            status = "⚠️  TESTE/DUMMY"  
            print(f"   {name}: {status}")
        else:
            status = "❌ AUSENTE"
            print(f"   {name}: {status}")
    
    print(f"\n🔧 DISABLE_GOOGLE_CALENDAR: {DISABLE_GOOGLE_CALENDAR}")
    
    # Determina se temos credenciais reais
    has_real_creds = all(
        var and var.strip() and not var.startswith('test-') 
        for var in [GOOGLE_SERVICE_ACCOUNT_EMAIL, GOOGLE_PRIVATE_KEY, GOOGLE_PROJECT_ID]
    )
    
    print(f"\n📊 RESULTADO:")
    if has_real_creds and not DISABLE_GOOGLE_CALENDAR:
        print("   ✅ CREDENCIAIS REAIS DISPONÍVEIS - Testes reais podem executar")
        return True
    elif DISABLE_GOOGLE_CALENDAR:
        print("   ⚠️  GOOGLE CALENDAR DESABILITADO - Testes serão pulados")
        return False
    else:
        print("   ❌ CREDENCIAIS REAIS NÃO DISPONÍVEIS - Testes serão pulados")
        print("\n💡 Para executar testes reais, configure:")
        print("   - GOOGLE_SERVICE_ACCOUNT_EMAIL")
        print("   - GOOGLE_PRIVATE_KEY") 
        print("   - GOOGLE_PROJECT_ID")
        return False

def test_basic_google_auth():
    """Testa autenticação básica do Google Calendar (apenas se credenciais reais)."""
    print("\n🔐 TESTANDO AUTENTICAÇÃO GOOGLE CALENDAR")
    print("=" * 50)
    
    if not check_credentials():
        print("   ⏭️  PULANDO - Credenciais não disponíveis")
        return False
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        import httplib2
        import google_auth_httplib2
        
        print("📦 Importações realizadas com sucesso")
        
        # Cria credenciais
        service_account_info = {
            "type": "service_account", 
            "project_id": GOOGLE_PROJECT_ID,
            "private_key": GOOGLE_PRIVATE_KEY,
            "client_email": GOOGLE_SERVICE_ACCOUNT_EMAIL,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        print("✅ Credenciais criadas com sucesso")
        print(f"   📧 Service Account: {credentials.service_account_email}")
        
        # Cria serviço
        http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
        service = build('calendar', 'v3', http=http, cache_discovery=False)
        
        print("✅ Serviço Google Calendar criado")
        
        # Testa chamada real à API
        print("🔄 Fazendo chamada REAL à API...")
        calendar_info = service.calendars().get(calendarId=GOOGLE_CALENDAR_ID or 'primary').execute()
        
        print("✅ SUCESSO! Chamada real à API funcionou")
        print(f"   📅 Calendário: {calendar_info.get('summary', 'N/A')}")
        print(f"   🆔 ID: {calendar_info.get('id', 'N/A')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        print("   💡 Instale as dependências: pip install google-auth google-api-python-client")
        return False
    except Exception as e:
        print(f"❌ ERRO NA AUTENTICAÇÃO: {e}")
        print("   💡 Verifique se as credenciais estão corretas")
        return False

def main():
    """Função principal."""
    print("🚀 TESTE DIRETO DE INTEGRAÇÃO REAL - GOOGLE CALENDAR")
    print("=" * 60)
    print("Este script testa a integração real sem mocks ou frameworks")
    print()
    
    # Define environment para indicar que é teste
    os.environ['PYTEST_RUNNING'] = 'true'
    
    # Executa validações
    has_creds = check_credentials()
    
    if has_creds:
        success = test_basic_google_auth()
        if success:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("   Os testes reais estão prontos para execução")
        else:
            print("\n❌ FALHA NOS TESTES")
            print("   Verifique as credenciais e configurações")
    else:
        print("\n⚠️  TESTES NÃO EXECUTADOS")
        print("   Configure credenciais reais para executar testes reais")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()