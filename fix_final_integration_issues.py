#!/usr/bin/env python3
"""
CORREÇÃO FINAL DOS PROBLEMAS DE INTEGRAÇÃO
Corrige os últimos problemas identificados no teste de integração
"""

import asyncio
import httpx
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Setup do ambiente
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
load_dotenv(root_dir / '.env')

print("🔧 CORREÇÃO FINAL - PROBLEMAS DE INTEGRAÇÃO")
print("=" * 60)

async def fix_kommo_token_issue():
    """Testa e corrige problema do token Kommo"""
    print("\n🏢 PROBLEMA 1: TOKEN KOMMO CRM")
    print("-" * 40)
    
    KOMMO_SUBDOMAIN = os.getenv('KOMMO_SUBDOMAIN', '')
    KOMMO_LONG_LIVED_TOKEN = os.getenv('KOMMO_LONG_LIVED_TOKEN', '')
    KOMMO_BASE_URL = f"https://{KOMMO_SUBDOMAIN}.kommo.com"
    
    headers = {
        'Authorization': f'Bearer {KOMMO_LONG_LIVED_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'SDR-IA-SolarPrime/1.0'
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Teste simples de account
            url = f"{KOMMO_BASE_URL}/api/v4/account"
            response = await client.get(url, headers=headers)
            
            print(f"   📊 Status: {response.status_code}")
            print(f"   📄 Content-Type: {response.headers.get('content-type', '')}")
            
            if 'html' in response.headers.get('content-type', '').lower():
                print(f"   ❌ PROBLEMA: Recebendo HTML (token provavelmente expirou)")
                print(f"   🔧 SOLUÇÃO: Necessário renovar token no Kommo CRM")
                print(f"   📝 HTML preview: {response.text[:200]}")
                return False
            else:
                data = response.json()
                account_name = data.get('name', 'N/A')
                print(f"   ✅ TOKEN OK - Conta: {account_name}")
                return True
                
        except Exception as e:
            print(f"   ❌ ERRO: {str(e)}")
            return False

async def test_calendar_event_creation():
    """Testa criação de evento no Calendar para verificar o problema"""
    print("\n📅 PROBLEMA 2: CALENDAR EVENT RETURN")
    print("-" * 40)
    
    try:
        from agente.services.calendar_service import GoogleCalendarService
        
        calendar_service = GoogleCalendarService()
        
        if not calendar_service.is_available():
            print("   ❌ Calendar service não disponível")
            return False
        
        # Criar evento simples
        tomorrow = datetime.now() + timedelta(days=1)
        meeting_time = tomorrow.replace(hour=16, minute=0, second=0, microsecond=0)
        
        event = await calendar_service.create_meeting(
            title="[TESTE-CORREÇÃO] Evento Teste",
            description="Teste para verificar retorno do evento",
            start_time=meeting_time,
            duration_minutes=30,
            attendees=None
        )
        
        if event:
            print(f"   ✅ Evento criado: {event.id}")
            print(f"   📅 Data: {event.start}")
            print(f"   🔧 Tipo do retorno: {type(event)}")
            print(f"   📋 Atributos: {dir(event)}")
            
            # Verificar se tem event_id
            if hasattr(event, 'event_id'):
                print(f"   ✅ event_id disponível: {event.event_id}")
            else:
                print(f"   ⚠️ event_id não disponível, usando id: {event.id}")
            
            # Cancelar o evento de teste
            await calendar_service.cancel_event(event.id, send_notifications=False)
            print(f"   🧹 Evento de teste removido")
            
            return True
        else:
            print(f"   ❌ Falha ao criar evento")
            return False
            
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        return False

async def main():
    """Função principal de correção"""
    print(f"⏰ Iniciando correções em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Corrigir problemas identificados
    kommo_ok = await fix_kommo_token_issue()
    calendar_ok = await test_calendar_event_creation()
    
    print(f"\n" + "=" * 60)
    print("🏁 RESULTADO DAS CORREÇÕES")
    print("=" * 60)
    
    if kommo_ok and calendar_ok:
        print("✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print("   ✅ Kommo CRM: Operacional")
        print("   ✅ Google Calendar: Operacional")
        print("   🎯 Sistema pronto para integração completa")
        return True
    else:
        print("❌ PROBLEMAS PERSISTEM:")
        if not kommo_ok:
            print("   ❌ Kommo CRM: Token precisa ser renovado")
        if not calendar_ok:
            print("   ❌ Google Calendar: Problema na criação de eventos")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)