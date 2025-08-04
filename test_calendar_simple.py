#!/usr/bin/env python3
"""
Teste simplificado de agendamento REAL no Google Calendar
Sem Google Meet para evitar erros de conference_data
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_calendar import google_calendar_client
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)

async def test_simple_calendar():
    """Teste simples e direto de criação de evento"""
    
    print("\n" + "="*60)
    print("🧪 TESTE SIMPLES DE AGENDAMENTO NO GOOGLE CALENDAR")
    print("="*60)
    
    # Preparar dados do evento
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    print(f"\n📅 Criando evento para: {start_time.strftime('%d/%m/%Y %H:%M')}")
    
    try:
        # Criar evento SEM Google Meet (conference_data=False)
        result = await google_calendar_client.create_event(
            title="Teste Solar Prime - Reunião de Demonstração",
            start_time=start_time,
            end_time=end_time,
            description="Teste de agendamento via sistema SDR IA",
            location="A definir",  # Sem "Online" para evitar conference_data
            attendees=[],  # Sem attendees por enquanto
            reminder_minutes=30,
            conference_data=False  # IMPORTANTE: Desabilitar Google Meet
        )
        
        if result:
            print("\n✅ EVENTO CRIADO COM SUCESSO!")
            print(f"📍 Google Event ID: {result.get('google_event_id')}")
            print(f"🔗 Link do Calendar: {result.get('html_link')}")
            print(f"📅 Status: {result.get('status')}")
            
            # Aguardar um pouco
            await asyncio.sleep(2)
            
            # Verificar se o evento existe
            print("\n🔍 Verificando evento no Google Calendar...")
            event = await google_calendar_client.get_event(result.get('google_event_id'))
            
            if event:
                print("✅ Evento confirmado no Google Calendar!")
                print(f"   Título: {event.get('title')}")
                print(f"   Data/Hora início: {event.get('start')}")
                print(f"   Data/Hora fim: {event.get('end')}")
                
                # Limpar - deletar evento de teste
                print("\n🗑️ Removendo evento de teste...")
                deleted = await google_calendar_client.delete_event(result.get('google_event_id'))
                if deleted:
                    print("✅ Evento de teste removido com sucesso")
                
                return True
            else:
                print("❌ Evento não encontrado no Google Calendar")
                return False
        else:
            print("❌ Falha ao criar evento")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_google_meet():
    """Teste com Google Meet usando formato correto"""
    
    print("\n" + "="*60)
    print("🎥 TESTE COM GOOGLE MEET")
    print("="*60)
    
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    print(f"\n📅 Criando evento com Meet para: {start_time.strftime('%d/%m/%Y %H:%M')}")
    
    try:
        # Tentar criar com Google Meet usando o formato correto
        result = await google_calendar_client.create_event(
            title="Teste Solar Prime - Reunião com Google Meet",
            start_time=start_time,
            end_time=end_time,
            description="Teste com Google Meet",
            location="Online - Google Meet",
            attendees=[],
            reminder_minutes=30,
            conference_data=True  # Habilitar Meet
        )
        
        if result:
            print("\n✅ EVENTO COM MEET CRIADO!")
            print(f"📍 Event ID: {result.get('google_event_id')}")
            print(f"🎥 Google Meet Link: {result.get('hangout_link', 'Não gerado')}")
            print(f"📅 Conference Data: {result.get('conference_data')}")
            
            # Limpar
            await asyncio.sleep(2)
            await google_calendar_client.delete_event(result.get('google_event_id'))
            print("✅ Evento de teste removido")
            return True
        else:
            print("❌ Falha ao criar evento com Meet")
            return False
            
    except Exception as e:
        print(f"⚠️ Erro esperado com Google Meet: {e}")
        print("Nota: Google Meet pode requerer configuração adicional no Service Account")
        return False

async def test_availability_check():
    """Teste de verificação de disponibilidade"""
    
    print("\n" + "="*60)
    print("🔍 TESTE DE DISPONIBILIDADE")
    print("="*60)
    
    # Verificar próxima segunda-feira às 10h
    days_ahead = (7 - datetime.now().weekday()) % 7  # Dias até segunda
    if days_ahead == 0:
        days_ahead = 7  # Se hoje é segunda, pegar próxima
    
    next_monday = datetime.now() + timedelta(days=days_ahead)
    start_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    print(f"\n🔍 Verificando disponibilidade: {start_time.strftime('%d/%m/%Y %H:%M')}")
    
    try:
        result = await google_calendar_client.check_availability(
            start_time=start_time,
            end_time=end_time
        )
        
        if result is True:
            print("✅ Horário está DISPONÍVEL")
        elif isinstance(result, dict):
            print(f"❌ Horário OCUPADO: {result.get('conflicts', [])}")
        else:
            print(f"⚠️ Status desconhecido: {result}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def main():
    """Executa todos os testes"""
    
    print("\n" + "🚀"*30)
    print("TESTES DIRETOS DO GOOGLE CALENDAR API")
    print("🚀"*30)
    
    results = []
    
    # Teste 1: Evento simples
    results.append(("Evento Simples", await test_simple_calendar()))
    
    # Teste 2: Com Google Meet
    results.append(("Google Meet", await test_with_google_meet()))
    
    # Teste 3: Verificação de disponibilidade
    results.append(("Disponibilidade", await test_availability_check()))
    
    # Relatório
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\n📈 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"⚠️ {total - passed} testes falharam")

if __name__ == "__main__":
    asyncio.run(main())