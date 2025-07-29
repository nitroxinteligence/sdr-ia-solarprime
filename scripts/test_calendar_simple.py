#!/usr/bin/env python3
"""
Simple Calendar Test
====================
Teste simplificado do Google Calendar sem usar as tools do AGnO
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from services.google_calendar_service import get_google_calendar_service
from repositories.lead_repository import lead_repository
from models.lead import LeadCreate


async def test_calendar_direct():
    """Testa o Google Calendar diretamente"""
    
    print("\n🔧 TESTE DIRETO DO GOOGLE CALENDAR SERVICE\n")
    print("="*60)
    
    # 1. Criar lead de teste
    print("\n1️⃣ Criando lead de teste...")
    try:
        test_phone = "+5511777777777"
        lead_data = LeadCreate(
            phone_number=test_phone,
            name="Teste Calendar Direct",
            email="teste@example.com"
        )
        lead = await lead_repository.create_or_update(lead_data)
        print(f"✅ Lead criado: {lead.name}")
    except Exception as e:
        print(f"❌ Erro ao criar lead: {e}")
        return
    
    # 2. Obter serviço do Calendar
    print("\n2️⃣ Inicializando Google Calendar Service...")
    try:
        calendar_service = get_google_calendar_service()
        print("✅ Serviço inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar serviço: {e}")
        return
    
    # 3. Testar listagem de eventos
    print("\n3️⃣ Listando eventos...")
    try:
        events = await calendar_service.list_events()
        print(f"✅ Encontrados {len(events)} eventos")
        for event in events[:3]:
            print(f"   - {event['summary']} em {event['start']}")
    except Exception as e:
        print(f"❌ Erro ao listar eventos: {e}")
    
    # 4. Testar criação de evento
    print("\n4️⃣ Criando evento de teste...")
    try:
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_14h = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        lead_data = {
            'id': str(lead.id),
            'name': lead.name,
            'phone': lead.phone_number,
            'email': lead.email,
            'bill_value': 500.00,
            'consumption_kwh': 300,
            'solution_interest': 'Energia Solar Residencial'
        }
        
        event = await calendar_service.create_event(
            title=f"☀️ Reunião SolarPrime - {lead.name}",
            start_datetime=tomorrow_14h,
            description="Reunião de apresentação da SolarPrime",
            location="SolarPrime - Av. Boa Viagem, 3344",
            lead_data=lead_data
        )
        
        if event:
            print("✅ Evento criado com sucesso!")
            print(f"   ID: {event['id']}")
            print(f"   Link: {event['link']}")
            return event['id']
        else:
            print("❌ Falha ao criar evento")
            
    except Exception as e:
        print(f"❌ Erro ao criar evento: {e}")
    
    # 5. Testar verificação de disponibilidade
    print("\n5️⃣ Verificando disponibilidade...")
    try:
        slots = await calendar_service.check_availability(
            date=tomorrow,
            duration_minutes=60
        )
        print(f"✅ Encontrados {len(slots)} horários disponíveis")
        for slot in slots[:5]:
            print(f"   - {slot['start']} até {slot['end']}")
    except Exception as e:
        print(f"❌ Erro ao verificar disponibilidade: {e}")
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO!")


async def test_calendar_tools_raw():
    """Testa as calendar tools sem decorador"""
    
    print("\n🔧 TESTE DAS FUNÇÕES DO CALENDAR (SEM DECORADOR)\n")
    print("="*60)
    
    # Importar as funções internas (sem decorador)
    from agents.tools.google_calendar_tools import (
        lead_repository,
        google_calendar_config,
        get_google_calendar_service,
        _is_business_hours
    )
    
    # 1. Criar lead
    print("\n1️⃣ Criando lead...")
    test_phone = "+5511666666666"
    try:
        lead_data = LeadCreate(
            phone_number=test_phone,
            name="Ana Teste Raw",
            email="ana@example.com"
        )
        lead = await lead_repository.create_or_update(lead_data)
        print(f"✅ Lead criado: {lead.name}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # 2. Testar agendamento manual
    print("\n2️⃣ Agendando reunião manualmente...")
    try:
        # Data e hora
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%d/%m/%Y")
        time_str = "15:00"
        
        # Converter para datetime
        day, month, year = date_str.split('/')
        hour, minute = time_str.split(':')
        meeting_datetime = datetime(
            int(year), int(month), int(day),
            int(hour), int(minute)
        )
        
        # Verificar horário comercial
        if _is_business_hours(meeting_datetime):
            print("✅ Horário comercial válido")
        else:
            print("❌ Fora do horário comercial")
            return
        
        # Criar evento
        calendar_service = get_google_calendar_service()
        
        lead_data = {
            'id': str(lead.id),
            'name': lead.name,
            'phone': lead.phone_number,
            'email': lead.email,
            'bill_value': 600.00,
            'consumption_kwh': 350,
            'solution_interest': 'Solar Residencial'
        }
        
        event = await calendar_service.create_event(
            title=f"☀️ Reunião SolarPrime - {lead.name}",
            start_datetime=meeting_datetime,
            description="Apresentação das soluções SolarPrime",
            location=google_calendar_config.meeting_location,
            lead_data=lead_data
        )
        
        if event:
            print("✅ Reunião agendada com sucesso!")
            print(f"   Data: {date_str} às {time_str}")
            print(f"   Link: {event['link']}")
            
            # Atualizar lead
            await lead_repository.update_lead(
                lead_id=lead.id,
                meeting_scheduled_at=meeting_datetime,
                current_stage='MEETING_SCHEDULED',
                google_event_id=event['id']
            )
            print("✅ Lead atualizado no banco")
        
    except Exception as e:
        print(f"❌ Erro ao agendar: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ TESTE RAW CONCLUÍDO!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste simplificado do Calendar")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Testar funções raw (sem decorador)"
    )
    
    args = parser.parse_args()
    
    if args.raw:
        asyncio.run(test_calendar_tools_raw())
    else:
        asyncio.run(test_calendar_direct())