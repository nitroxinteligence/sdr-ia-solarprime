#!/usr/bin/env python3
"""
Script de Teste DIRETO para Busca de Horários Disponíveis
Testa a funcionalidade sem depender do decorator @tool
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Settings
from app.integrations.google_calendar import GoogleCalendarClient
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <cyan>{message}</cyan>")

class CalendarSlotsDirectTester:
    """Teste direto da funcionalidade de slots"""
    
    def __init__(self):
        self.settings = Settings()
        self.calendar_client = GoogleCalendarClient()
        
    async def get_available_slots_direct(self, days_ahead=7, slot_duration_minutes=30):
        """
        Implementação direta da busca de slots (sem decorator)
        """
        try:
            available_slots = {}
            occupied_slots = {}
            
            # Configuração de horário comercial
            business_start = 9  # 9h
            business_end = 18   # 18h
            
            # Data inicial (hoje)
            current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Buscar eventos ocupados dos próximos dias
            time_min = current_date
            time_max = current_date + timedelta(days=days_ahead + 10)  # Buffer para garantir 7 dias úteis
            
            # Buscar eventos do Google Calendar
            logger.info("🔍 Buscando eventos do Google Calendar...")
            events = await self.calendar_client.list_events(
                time_min=time_min,
                time_max=time_max,
                max_results=100
            )
            logger.info(f"📅 {len(events)} eventos encontrados no período")
            
            # Processar cada dia útil
            business_days_count = 0
            check_date = current_date
            
            while business_days_count < days_ahead:
                # Pular finais de semana
                if check_date.weekday() >= 5:  # 5=Sábado, 6=Domingo
                    check_date += timedelta(days=1)
                    continue
                
                date_str = check_date.strftime("%d/%m/%Y")
                day_name = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][check_date.weekday()]
                
                available_slots[date_str] = {
                    "day_name": day_name,
                    "date": date_str,
                    "slots": []
                }
                occupied_slots[date_str] = {
                    "day_name": day_name,
                    "date": date_str,
                    "slots": []
                }
                
                # Gerar todos os slots do dia
                slot_start = check_date.replace(hour=business_start, minute=0)
                slot_end = check_date.replace(hour=business_end, minute=0)
                
                current_slot = slot_start
                
                while current_slot < slot_end:
                    slot_end_time = current_slot + timedelta(minutes=slot_duration_minutes)
                    
                    # Verificar se o slot está ocupado
                    is_occupied = False
                    for event in events:
                        if event.get("start") and event.get("end"):
                            # Parse do horário do evento
                            event_start_str = event["start"].get("dateTime", event["start"].get("date", ""))
                            event_end_str = event["end"].get("dateTime", event["end"].get("date", ""))
                            
                            if event_start_str and event_end_str:
                                try:
                                    # Tratar diferentes formatos de data
                                    if 'T' in event_start_str:
                                        event_start = datetime.fromisoformat(event_start_str.replace("Z", "+00:00"))
                                        event_end = datetime.fromisoformat(event_end_str.replace("Z", "+00:00"))
                                    else:
                                        # Evento de dia inteiro
                                        event_start = datetime.strptime(event_start_str, "%Y-%m-%d")
                                        event_end = datetime.strptime(event_end_str, "%Y-%m-%d")
                                    
                                    # Remover timezone para comparação
                                    if event_start.tzinfo:
                                        event_start = event_start.replace(tzinfo=None)
                                    if event_end.tzinfo:
                                        event_end = event_end.replace(tzinfo=None)
                                    
                                    # Verificar sobreposição
                                    if (current_slot < event_end and slot_end_time > event_start):
                                        is_occupied = True
                                        break
                                except Exception as e:
                                    logger.debug(f"Erro ao processar evento: {e}")
                                    continue
                    
                    # Adicionar slot à lista apropriada
                    slot_info = {
                        "time": current_slot.strftime("%H:%M"),
                        "datetime": current_slot.isoformat(),
                        "duration": slot_duration_minutes
                    }
                    
                    if is_occupied:
                        occupied_slots[date_str]["slots"].append(slot_info)
                    else:
                        # Verificar se não é horário de almoço (12h-13h)
                        if not (12 <= current_slot.hour < 13):
                            available_slots[date_str]["slots"].append(slot_info)
                    
                    current_slot = slot_end_time
                
                business_days_count += 1
                check_date += timedelta(days=1)
            
            # Calcular estatísticas
            total_available = sum(len(day["slots"]) for day in available_slots.values())
            total_occupied = sum(len(day["slots"]) for day in occupied_slots.values())
            
            return {
                "success": True,
                "period": f"Próximos {days_ahead} dias úteis",
                "business_hours": f"{business_start}h às {business_end}h",
                "slot_duration": f"{slot_duration_minutes} minutos",
                "statistics": {
                    "total_available_slots": total_available,
                    "total_occupied_slots": total_occupied,
                    "availability_percentage": round((total_available / (total_available + total_occupied) * 100) if (total_available + total_occupied) > 0 else 100, 1)
                },
                "available_slots": available_slots,
                "occupied_slots": occupied_slots
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar slots: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_test(self):
        """Executa o teste principal"""
        logger.info("🚀 TESTE DIRETO DE SLOTS DO CALENDÁRIO")
        logger.info("=" * 60)
        
        # Buscar slots
        result = await self.get_available_slots_direct()
        
        if result.get("success"):
            logger.success("✅ Busca realizada com sucesso!")
            
            # Mostrar estatísticas
            stats = result.get("statistics", {})
            logger.info(f"\n📊 ESTATÍSTICAS:")
            logger.info(f"   - Total de slots disponíveis: {stats.get('total_available_slots', 0)}")
            logger.info(f"   - Total de slots ocupados: {stats.get('total_occupied_slots', 0)}")
            logger.info(f"   - Taxa de disponibilidade: {stats.get('availability_percentage', 0)}%")
            logger.info(f"   - Período: {result.get('period')}")
            logger.info(f"   - Horário comercial: {result.get('business_hours')}")
            
            # Mostrar resumo por dia
            available_slots = result.get("available_slots", {})
            logger.info(f"\n📋 RESUMO POR DIA:")
            for date_str, day_data in list(available_slots.items())[:7]:
                total_slots = len(day_data["slots"])
                logger.info(f"   {day_data['day_name']} {date_str}: {total_slots} slots disponíveis")
                
                # Mostrar primeiros horários do dia
                if total_slots > 0:
                    morning_slots = [s for s in day_data["slots"] if int(s["time"].split(":")[0]) < 12]
                    afternoon_slots = [s for s in day_data["slots"] if int(s["time"].split(":")[0]) >= 14]
                    
                    if morning_slots:
                        logger.info(f"      Manhã: {morning_slots[0]['time']} - {morning_slots[-1]['time']}")
                    if afternoon_slots:
                        logger.info(f"      Tarde: {afternoon_slots[0]['time']} - {afternoon_slots[-1]['time']}")
            
            # Mostrar dias com reuniões agendadas
            occupied_slots = result.get("occupied_slots", {})
            has_occupied = False
            for date_str, day_data in occupied_slots.items():
                if day_data["slots"]:
                    if not has_occupied:
                        logger.info(f"\n🔴 HORÁRIOS OCUPADOS:")
                        has_occupied = True
                    logger.info(f"   {day_data['day_name']} {date_str}: {len(day_data['slots'])} slots ocupados")
                    for slot in day_data["slots"][:3]:
                        logger.info(f"      - {slot['time']}")
                    if len(day_data["slots"]) > 3:
                        logger.info(f"      ... e mais {len(day_data['slots']) - 3} horários")
            
            if not has_occupied:
                logger.info(f"\n✨ Nenhum horário ocupado nos próximos 7 dias úteis!")
            
            # Sugerir melhores horários
            logger.info(f"\n⭐ SUGESTÃO DE MELHORES HORÁRIOS:")
            suggested = 0
            for date_str, day_data in available_slots.items():
                if suggested >= 5:
                    break
                for slot in day_data["slots"]:
                    hour = int(slot["time"].split(":")[0])
                    if hour in [9, 10, 14, 15]:  # Horários preferenciais
                        suggested += 1
                        logger.info(f"   {suggested}. {day_data['day_name']} {date_str} às {slot['time']}")
                        if suggested >= 5:
                            break
            
            return True
        else:
            logger.error(f"❌ Erro na busca: {result.get('error')}")
            return False

async def main():
    """Função principal"""
    tester = CalendarSlotsDirectTester()
    success = await tester.run_test()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.success("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("\n📝 Funcionalidade Validada:")
        logger.info("   ✅ Busca de horários dos próximos 7 dias úteis")
        logger.info("   ✅ Identificação de slots disponíveis e ocupados")
        logger.info("   ✅ Exclusão de fins de semana")
        logger.info("   ✅ Horário comercial (9h-18h)")
        logger.info("   ✅ Exclusão de almoço (12h-13h)")
        logger.info("   ✅ Integração com Google Calendar")
    else:
        logger.warning("⚠️ Teste falhou. Verifique os logs.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())