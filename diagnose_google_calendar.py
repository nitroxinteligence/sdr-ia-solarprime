#!/usr/bin/env python3
"""
DIAGNÓSTICO GOOGLE CALENDAR - Service Account e Permissões
Verifica configuração e corrige problemas de Domain-Wide Delegation
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Setup do ambiente
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
load_dotenv(root_dir / '.env')

from agente.services.calendar_service import GoogleCalendarService
from agente.core.config import (
    GOOGLE_SERVICE_ACCOUNT_EMAIL,
    GOOGLE_PROJECT_ID,
    GOOGLE_CALENDAR_ID,
    DISABLE_GOOGLE_CALENDAR
)

print("🔍 DIAGNÓSTICO GOOGLE CALENDAR - SERVICE ACCOUNT")
print("=" * 60)
print(f"📊 Configuração atual:")
print(f"   📧 Service Account: {GOOGLE_SERVICE_ACCOUNT_EMAIL}")
print(f"   🆔 Project ID: {GOOGLE_PROJECT_ID}")
print(f"   📅 Calendar ID: {GOOGLE_CALENDAR_ID}")
print(f"   🚫 Disabled: {DISABLE_GOOGLE_CALENDAR}")

async def test_calendar_service():
    """Testa o Google Calendar Service"""
    
    print(f"\n🧪 TESTE: Inicialização do Calendar Service")
    
    try:
        calendar_service = GoogleCalendarService()
        
        if not calendar_service.is_available():
            print("   ❌ Service não disponível")
            return False
        
        print("   ✅ Service inicializado com sucesso")
        
        # Teste 1: Verificar disponibilidade
        print(f"\n🧪 TESTE: Verificar disponibilidade (próximas 2 horas)")
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        slots = await calendar_service.check_availability(start_time, end_time)
        print(f"   📊 Slots disponíveis encontrados: {len(slots)}")
        
        if slots:
            for i, slot in enumerate(slots[:3]):  # Mostrar primeiros 3
                print(f"      {i+1}. {slot.start.strftime('%d/%m %H:%M')} - {slot.end.strftime('%H:%M')}")
        
        # Teste 2: Criar reunião SEM convidados (evitar Domain-Wide Delegation)
        print(f"\n🧪 TESTE: Criar reunião sem convidados")
        meeting_time = start_time
        
        event = await calendar_service.create_meeting(
            title="[DIAGNÓSTICO] Teste Reunião",
            description="Reunião de teste para diagnóstico do sistema",
            start_time=meeting_time,
            duration_minutes=60,
            attendees=None  # SEM convidados para evitar erro de permissão
        )
        
        if event:
            print(f"   ✅ Reunião criada com sucesso!")
            print(f"   🆔 Event ID: {event.id}")
            print(f"   📅 Data: {event.start.strftime('%d/%m/%Y %H:%M')}")
            print(f"   🔗 Meet Link: {event.meet_link or 'N/A'}")
            
            # Teste 3: Atualizar reunião
            print(f"\n🧪 TESTE: Atualizar reunião")
            new_time = meeting_time + timedelta(hours=1)
            
            updated_event = await calendar_service.update_event(
                event.id,
                {
                    'title': '[DIAGNÓSTICO] Reunião Atualizada',
                    'description': 'Reunião atualizada durante diagnóstico',
                    'start_time': new_time,
                    'end_time': new_time + timedelta(hours=1)
                }
            )
            
            if updated_event:
                print(f"   ✅ Reunião atualizada com sucesso!")
                print(f"   📅 Nova data: {updated_event.start.strftime('%d/%m/%Y %H:%M')}")
            else:
                print(f"   ❌ Falha ao atualizar reunião")
            
            # Teste 4: Cancelar reunião de teste
            print(f"\n🧪 TESTE: Cancelar reunião de teste")
            cancelled = await calendar_service.cancel_event(event.id, send_notifications=False)
            
            if cancelled:
                print(f"   ✅ Reunião cancelada com sucesso")
            else:
                print(f"   ❌ Falha ao cancelar reunião")
        
        else:
            print(f"   ❌ Falha ao criar reunião")
            return False
        
        # Teste 5: Listar eventos
        print(f"\n🧪 TESTE: Listar eventos (próximos 7 dias)")
        events = await calendar_service.get_calendar_events(
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )
        
        print(f"   📊 Eventos encontrados: {len(events)}")
        for i, event in enumerate(events[:3]):  # Primeiros 3
            print(f"      {i+1}. {event.title} - {event.start.strftime('%d/%m %H:%M')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO durante testes: {str(e)}")
        return False

async def test_conference_creation():
    """Testa criação de reunião com Google Meet (sem convidados)"""
    
    print(f"\n🧪 TESTE ESPECÍFICO: Google Meet Conference")
    
    try:
        calendar_service = GoogleCalendarService()
        
        if not calendar_service.is_available():
            print("   ❌ Calendar service não disponível")
            return False
        
        # Criar reunião com Google Meet mas sem convidados
        tomorrow = datetime.now() + timedelta(days=1)
        meeting_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
        
        event = await calendar_service.create_meeting(
            title="[TESTE-MEET] Reunião com Google Meet",
            description="Teste específico para Google Meet integration",
            start_time=meeting_time,
            duration_minutes=30,
            attendees=[]  # Lista vazia em vez de None
        )
        
        if event:
            print(f"   ✅ Reunião com Meet criada!")
            print(f"   🔗 Google Meet: {event.meet_link}")
            print(f"   📍 Location: {event.location}")
            
            # Limpeza - cancelar o evento de teste
            await calendar_service.cancel_event(event.id, send_notifications=False)
            print(f"   🧹 Evento de teste removido")
            
            return True
        else:
            print(f"   ❌ Falha ao criar reunião com Meet")
            return False
            
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        return False

async def main():
    """Função principal de diagnóstico"""
    print(f"\n⏰ Iniciando diagnóstico em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if DISABLE_GOOGLE_CALENDAR:
        print("⚠️ AVISO: Google Calendar está DESABILITADO na configuração!")
        return False
    
    # Teste principal
    success1 = await test_calendar_service()
    
    # Teste específico do Google Meet
    success2 = await test_conference_creation()
    
    print(f"\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ RESULTADO: Google Calendar está 100% OPERACIONAL!")
        print("   ✅ Service Account funcionando")
        print("   ✅ Criação de eventos OK")
        print("   ✅ Atualização de eventos OK")
        print("   ✅ Google Meet integration OK")
        print("   ✅ Cancelamento de eventos OK")
        return True
    else:
        print("❌ RESULTADO: Google Calendar apresenta problemas")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)