#!/usr/bin/env python3
"""
Teste simples do fluxo básico - Calendar + Meet
Sem dependência do SDR Team completo
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_calendar import google_calendar_client
from app.integrations.google_meet_handler import google_meet_handler

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)

async def main():
    """Teste direto do fluxo Calendar + Meet"""
    
    print("\n" + "="*60)
    print("🚀 TESTE SIMPLES - CALENDAR + GOOGLE MEET")
    print("="*60)
    
    # 1. Status do sistema
    meet_status = google_meet_handler.get_status()
    print(f"\n📊 Status:")
    print(f"  • Calendar: ✅ Ativo")
    print(f"  • Meet: {'✅ Automático' if meet_status['can_create_meet'] else '⚠️ Manual'}")
    
    created_events = []
    
    try:
        # 2. Criar evento com Meet
        print(f"\n📅 Criando evento com Google Meet...")
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
        
        event = await google_calendar_client.create_event(
            title="Reunião Solar Prime - João Silva",
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            description="Apresentação de soluções em energia solar",
            location="Online",
            reminder_minutes=30,
            conference_data=True  # Solicita Meet
        )
        
        if event and event.get('google_event_id'):
            created_events.append(event['google_event_id'])
            print(f"✅ Evento criado!")
            print(f"   ID: {event['google_event_id']}")
            print(f"   Link: {event.get('html_link')}")
            
            if event.get('has_meet'):
                print(f"   🎥 Meet: {event.get('meet_link')}")
            elif event.get('meet_setup_required'):
                print(f"   ⚠️ Meet requer configuração manual")
                print(f"   📝 Instruções no evento")
        else:
            print("❌ Falha ao criar evento")
            
        # 3. Verificar disponibilidade
        print(f"\n🔍 Verificando disponibilidade...")
        availability = await google_calendar_client.check_availability(
            start_time=start_time,
            end_time=start_time + timedelta(hours=1)
        )
        
        if availability == True:
            print(f"✅ Horário disponível")
        else:
            print(f"⚠️ Horário ocupado")
            
        # 4. Listar eventos
        print(f"\n📋 Listando eventos...")
        events = await google_calendar_client.list_events(
            time_min=tomorrow.replace(hour=0, minute=0),
            time_max=tomorrow.replace(hour=23, minute=59),
            max_results=5
        )
        
        if events:
            print(f"📅 {len(events)} evento(s) encontrado(s):")
            for evt in events[:3]:
                print(f"  • {evt['title']}")
                if evt.get('hangout_link'):
                    print(f"    🎥 Meet ativo")
                    
        # 5. Atualizar evento
        if created_events:
            print(f"\n🔄 Atualizando evento...")
            new_time = tomorrow.replace(hour=16, minute=0)
            
            result = await google_calendar_client.update_event(
                event_id=created_events[0],
                updates={
                    "title": "Reunião Solar Prime - REAGENDADA",
                    "start_time": new_time,
                    "end_time": new_time + timedelta(hours=1)
                }
            )
            
            if result:
                print(f"✅ Evento atualizado!")
            else:
                print(f"❌ Falha ao atualizar")
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Limpeza
        print(f"\n🧹 Limpando...")
        for event_id in created_events:
            try:
                await google_calendar_client.delete_event(event_id)
                print(f"  ✅ Removido: {event_id[:10]}...")
            except:
                pass
                
    print(f"\n✅ Teste concluído!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())