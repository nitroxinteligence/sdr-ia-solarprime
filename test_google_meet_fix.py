#!/usr/bin/env python3
"""
Teste para descobrir o formato correto do Google Meet
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config import settings

async def test_meet_formats():
    """Testa diferentes formatos de conference data"""
    
    print("\n" + "="*60)
    print("🔬 DESCOBRINDO FORMATO CORRETO DO GOOGLE MEET")
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
    
    service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
    
    # Preparar evento base
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    base_event = {
        'summary': 'Teste Google Meet - Formato Discovery',
        'description': 'Testando diferentes formatos de conference data',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': settings.timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': settings.timezone,
        }
    }
    
    # Formato 1: Com hangoutsMeet (documentação oficial)
    print("\n📝 Testando Formato 1: hangoutsMeet")
    test_event1 = base_event.copy()
    test_event1['conferenceData'] = {
        'createRequest': {
            'requestId': 'test-meet-001',
            'conferenceSolutionKey': {
                'type': 'hangoutsMeet'
            }
        }
    }
    
    try:
        result1 = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=test_event1,
            conferenceDataVersion=1
        ).execute()
        
        if result1.get('hangoutLink') or result1.get('conferenceData'):
            print("✅ FORMATO 1 FUNCIONOU!")
            print(f"   Meet Link: {result1.get('hangoutLink')}")
            print(f"   Conference ID: {result1.get('conferenceData', {}).get('conferenceId')}")
            
            # Limpar
            service.events().delete(
                calendarId=settings.google_calendar_id or 'primary',
                eventId=result1['id']
            ).execute()
            return True
    except Exception as e:
        print(f"❌ Formato 1 falhou: {e}")
    
    # Formato 2: Apenas com requestId (simplificado)
    print("\n📝 Testando Formato 2: Apenas requestId")
    test_event2 = base_event.copy()
    test_event2['conferenceData'] = {
        'createRequest': {
            'requestId': 'test-meet-002'
        }
    }
    
    try:
        result2 = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=test_event2,
            conferenceDataVersion=1
        ).execute()
        
        if result2.get('hangoutLink') or result2.get('conferenceData'):
            print("✅ FORMATO 2 FUNCIONOU!")
            print(f"   Meet Link: {result2.get('hangoutLink')}")
            
            # Limpar
            service.events().delete(
                calendarId=settings.google_calendar_id or 'primary',
                eventId=result2['id']
            ).execute()
            return True
    except Exception as e:
        print(f"❌ Formato 2 falhou: {e}")
    
    # Formato 3: Com tipo eventHangout
    print("\n📝 Testando Formato 3: eventHangout")
    test_event3 = base_event.copy()
    test_event3['conferenceData'] = {
        'createRequest': {
            'requestId': 'test-meet-003',
            'conferenceSolutionKey': {
                'type': 'eventHangout'
            }
        }
    }
    
    try:
        result3 = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=test_event3,
            conferenceDataVersion=1
        ).execute()
        
        if result3.get('hangoutLink'):
            print("✅ FORMATO 3 FUNCIONOU!")
            print(f"   Meet Link: {result3.get('hangoutLink')}")
            
            # Limpar
            service.events().delete(
                calendarId=settings.google_calendar_id or 'primary',
                eventId=result3['id']
            ).execute()
            return True
    except Exception as e:
        print(f"❌ Formato 3 falhou: {e}")
    
    # Formato 4: Sem conferenceSolutionKey
    print("\n📝 Testando Formato 4: Sem conferenceSolutionKey")
    test_event4 = base_event.copy()
    import uuid
    test_event4['conferenceData'] = {
        'createRequest': {
            'requestId': str(uuid.uuid4()),
            'conferenceSolutionKey': {
                'type': 'hangoutsMeet'
            },
            'status': {
                'statusCode': 'success'
            }
        }
    }
    
    try:
        result4 = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=test_event4,
            conferenceDataVersion=1
        ).execute()
        
        if result4.get('hangoutLink'):
            print("✅ FORMATO 4 FUNCIONOU!")
            print(f"   Meet Link: {result4.get('hangoutLink')}")
            
            # Limpar
            service.events().delete(
                calendarId=settings.google_calendar_id or 'primary',
                eventId=result4['id']
            ).execute()
            return True
    except Exception as e:
        print(f"❌ Formato 4 falhou: {e}")
    
    print("\n❌ Nenhum formato funcionou diretamente")
    print("🔍 Tentando alternativa: Criar evento e adicionar Meet depois...")
    
    # Alternativa: Criar evento sem Meet e tentar adicionar depois
    simple_event = base_event.copy()
    simple_event['summary'] = 'Teste Alternativo - Adicionar Meet Depois'
    
    try:
        # Criar evento simples
        result = service.events().insert(
            calendarId=settings.google_calendar_id or 'primary',
            body=simple_event
        ).execute()
        
        event_id = result['id']
        print(f"📅 Evento criado: {event_id}")
        
        # Tentar fazer PATCH para adicionar Meet
        patch_body = {
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }
        
        patched = service.events().patch(
            calendarId=settings.google_calendar_id or 'primary',
            eventId=event_id,
            body=patch_body,
            conferenceDataVersion=1
        ).execute()
        
        if patched.get('hangoutLink'):
            print("✅ ALTERNATIVA FUNCIONOU! Meet adicionado via PATCH")
            print(f"   Meet Link: {patched.get('hangoutLink')}")
            
        # Limpar
        service.events().delete(
            calendarId=settings.google_calendar_id or 'primary',
            eventId=event_id
        ).execute()
        
    except Exception as e:
        print(f"❌ Alternativa também falhou: {e}")
    
    return False

if __name__ == "__main__":
    result = asyncio.run(test_meet_formats())
    
    if result:
        print("\n🎉 SOLUÇÃO ENCONTRADA!")
    else:
        print("\n⚠️ Google Meet pode requerer configuração adicional na conta")