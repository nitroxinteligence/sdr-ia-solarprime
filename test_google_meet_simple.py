#!/usr/bin/env python3
"""
Teste simples do Google Meet via Calendar API
Usando conferenceData com Service Account
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid
from google.oauth2 import service_account
from googleapiclient.discovery import build

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)

async def test_meet_via_calendar():
    """Testa criação de Meet diretamente via Calendar API"""
    
    print("\n" + "="*60)
    print("🔬 TESTE GOOGLE MEET VIA CALENDAR API")
    print("="*60)
    
    # Autenticar
    service_account_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'credentials',
        'google_service_account.json'
    )
    
    # Se não tiver arquivo, usar env
    if not os.path.exists(service_account_file):
        credentials_info = {
            "type": "service_account",
            "project_id": settings.google_project_id,
            "private_key_id": settings.google_private_key_id,
            "private_key": settings.google_private_key,
            "client_email": settings.google_service_account_email,
            "client_id": settings.google_client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.google_service_account_email}"
        }
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
    else:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
    
    # Verificar se temos um usuário para impersonar
    if hasattr(settings, 'google_workspace_user_email') and settings.google_workspace_user_email:
        print(f"📧 Usando Domain-Wide Delegation com: {settings.google_workspace_user_email}")
        credentials = credentials.with_subject(settings.google_workspace_user_email)
    else:
        print("⚠️ Sem Domain-Wide Delegation configurado")
        print("📝 Service Account: " + credentials.service_account_email)
    
    service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
    
    # Preparar evento
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    # Formato 1: Com requestId único
    print("\n📝 Teste 1: Com requestId único")
    event1 = {
        'summary': 'Teste Meet Solar Prime - Método 1',
        'description': 'Testando criação de Google Meet',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': settings.timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': settings.timezone,
        },
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                }
            }
        }
    }
    
    try:
        result1 = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=event1,
            conferenceDataVersion=1
        ).execute()
        
        if result1.get('hangoutLink'):
            print("✅ SUCESSO! Google Meet criado!")
            print(f"🔗 Meet Link: {result1.get('hangoutLink')}")
            print(f"📅 Event ID: {result1.get('id')}")
            
            # Limpar
            service.events().delete(
                calendarId=settings.google_calendar_id or 'primary',
                eventId=result1['id']
            ).execute()
            print("✅ Evento de teste removido")
            return True
        else:
            print("⚠️ Evento criado mas sem Meet link")
            if result1.get('conferenceData'):
                print(f"Conference Data: {result1.get('conferenceData')}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Formato 2: Sem type (usar default)
    print("\n📝 Teste 2: Sem especificar type")
    event2 = {
        'summary': 'Teste Meet Solar Prime - Método 2',
        'description': 'Testando criação de Google Meet',
        'start': {
            'dateTime': (start_time + timedelta(hours=1)).isoformat(),
            'timeZone': settings.timezone,
        },
        'end': {
            'dateTime': (end_time + timedelta(hours=1)).isoformat(),
            'timeZone': settings.timezone,
        },
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4())
            }
        }
    }
    
    try:
        result2 = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=event2,
            conferenceDataVersion=1
        ).execute()
        
        if result2.get('hangoutLink'):
            print("✅ SUCESSO! Google Meet criado!")
            print(f"🔗 Meet Link: {result2.get('hangoutLink')}")
            print(f"📅 Event ID: {result2.get('id')}")
            
            # Limpar
            service.events().delete(
                calendarId=settings.google_calendar_id or 'primary',
                eventId=result2['id']
            ).execute()
            print("✅ Evento de teste removido")
            return True
        else:
            print("⚠️ Evento criado mas sem Meet link")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Formato 3: Com eventNamedHangout (deprecated mas pode funcionar)
    print("\n📝 Teste 3: Com eventNamedHangout")
    event3 = {
        'summary': 'Teste Meet Solar Prime - Método 3',
        'description': 'Testando criação de Google Meet',
        'start': {
            'dateTime': (start_time + timedelta(hours=2)).isoformat(),
            'timeZone': settings.timezone,
        },
        'end': {
            'dateTime': (end_time + timedelta(hours=2)).isoformat(),
            'timeZone': settings.timezone,
        },
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {
                    'type': 'eventNamedHangout'
                }
            }
        }
    }
    
    try:
        result3 = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=event3,
            conferenceDataVersion=1
        ).execute()
        
        if result3.get('hangoutLink'):
            print("✅ SUCESSO! Google Meet criado!")
            print(f"🔗 Meet Link: {result3.get('hangoutLink')}")
            print(f"📅 Event ID: {result3.get('id')}")
            
            # Limpar
            service.events().delete(
                calendarId=settings.google_calendar_id or 'primary',
                eventId=result3['id']
            ).execute()
            print("✅ Evento de teste removido")
            return True
        else:
            print("⚠️ Evento criado mas sem Meet link")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "="*60)
    print("📊 RESULTADOS:")
    print("="*60)
    print("\n❌ Nenhum método funcionou diretamente")
    print("\n💡 Conclusões:")
    print("  1. Service Account precisa de Domain-Wide Delegation para criar Meet")
    print("  2. Ou usar OAuth com conta de usuário real")
    print("  3. Ou usar Google Meet REST API v2 (mais complexo)")
    print("\n📝 Solução recomendada:")
    print("  - Configure Domain-Wide Delegation no Google Workspace")
    print("  - Ou use OAuth ao invés de Service Account")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_meet_via_calendar())