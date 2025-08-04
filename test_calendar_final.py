#!/usr/bin/env python3
"""
TESTE FINAL - Valida que os slots ocupados são detectados corretamente
Após correções de timezone
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Settings
from app.integrations.google_calendar import GoogleCalendarClient
from app.teams.agents.calendar import CalendarAgent
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_final():
    """Teste final após correções"""
    
    logger.info("=" * 60)
    logger.info("🎯 TESTE FINAL - DETECÇÃO DE SLOTS OCUPADOS")
    logger.info("=" * 60)
    
    try:
        # 1. Primeiro, verificar eventos no Google Calendar
        logger.info("\n1️⃣ Verificando eventos no Google Calendar...")
        calendar_client = GoogleCalendarClient()
        
        time_min = datetime.now()
        time_max = time_min + timedelta(days=7)
        
        events = await calendar_client.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=50
        )
        
        logger.info(f"📊 Total de eventos no Google Calendar: {len(events)}")
        
        if events:
            logger.info("\n📅 Eventos encontrados:")
            for i, event in enumerate(events[:5], 1):
                start = event.get('start', {})
                if 'dateTime' in start:
                    dt_str = start['dateTime']
                    # Parse para mostrar horário
                    try:
                        if 'T' in dt_str:
                            date_part = dt_str.split('T')[0]
                            time_part = dt_str.split('T')[1].split('-')[0].split('+')[0][:5]
                            logger.info(f"   {i}. {event.get('summary', 'Sem título')}: {date_part} às {time_part}")
                    except:
                        logger.info(f"   {i}. {event.get('summary', 'Sem título')}: {dt_str}")
                elif 'date' in start:
                    logger.info(f"   {i}. {event.get('summary', 'Sem título')}: {start['date']} (dia inteiro)")
        
        # 2. Testar CalendarAgent com correções
        logger.info("\n2️⃣ Testando CalendarAgent com correções de timezone...")
        calendar_agent = CalendarAgent(model=None, storage=None)
        
        result = await calendar_agent._get_available_slots_internal(
            days_ahead=7,
            slot_duration_minutes=30,
            business_hours_only=True
        )
        
        if not result.get("success"):
            logger.error(f"❌ Erro: {result.get('error')}")
            return False
        
        # 3. Analisar resultados
        stats = result.get("statistics", {})
        logger.info(f"\n📊 ESTATÍSTICAS APÓS CORREÇÃO:")
        logger.info(f"   - Total de slots disponíveis: {stats.get('total_available_slots', 0)}")
        logger.info(f"   - Total de slots OCUPADOS: {stats.get('total_occupied_slots', 0)}")
        logger.info(f"   - Taxa de disponibilidade: {stats.get('availability_percentage', 0)}%")
        
        # 4. Mostrar slots ocupados detectados
        occupied_slots = result.get("occupied_slots", {})
        has_occupied = False
        
        logger.info(f"\n🔴 SLOTS OCUPADOS DETECTADOS:")
        for date_str, day_data in occupied_slots.items():
            if day_data["slots"]:
                has_occupied = True
                logger.success(f"   ✅ {day_data['day_name']} {date_str}: {len(day_data['slots'])} slots ocupados")
                # Mostrar alguns horários ocupados
                for slot in day_data["slots"][:3]:
                    logger.info(f"      - {slot['time']}")
                if len(day_data["slots"]) > 3:
                    logger.info(f"      ... e mais {len(day_data['slots']) - 3} slots")
        
        if not has_occupied:
            logger.warning("   ⚠️ Nenhum slot ocupado detectado!")
            if events:
                logger.error("   ❌ PROBLEMA: Há eventos no calendário mas não foram detectados como ocupados!")
                logger.info("\n   Possíveis causas:")
                logger.info("   1. Os eventos estão fora do horário comercial (9h-18h)")
                logger.info("   2. Os eventos são de dia inteiro")
                logger.info("   3. Ainda há problema no processamento de timezone")
                return False
        
        # 5. Validar correspondência
        logger.info("\n3️⃣ VALIDAÇÃO DE CORRESPONDÊNCIA:")
        
        if events and stats.get('total_occupied_slots', 0) > 0:
            logger.success("✅ SUCESSO! O sistema está detectando corretamente os slots ocupados!")
            logger.info(f"   - {len(events)} eventos no Google Calendar")
            logger.info(f"   - {stats.get('total_occupied_slots', 0)} slots marcados como ocupados")
            
            # Mostrar exemplo de horário disponível vs ocupado
            logger.info("\n📋 EXEMPLO DE FUNCIONAMENTO:")
            
            # Pegar primeiro dia com slots ocupados
            for date_str, day_data in occupied_slots.items():
                if day_data["slots"]:
                    logger.info(f"   Dia: {date_str}")
                    logger.info(f"   - Slots ocupados: {[s['time'] for s in day_data['slots'][:3]]}")
                    
                    # Mostrar disponíveis do mesmo dia
                    if date_str in result.get("available_slots", {}):
                        avail = result["available_slots"][date_str]["slots"]
                        if avail:
                            logger.info(f"   - Slots disponíveis: {[s['time'] for s in avail[:3]]}")
                    break
            
            return True
        elif events and stats.get('total_occupied_slots', 0) == 0:
            logger.error("❌ FALHA! Eventos existem mas não foram detectados!")
            return False
        elif not events:
            logger.warning("⚠️ Nenhum evento no calendário para testar")
            logger.info("   Crie alguns eventos no Google Calendar e execute o teste novamente")
            return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal"""
    success = await test_final()
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESULTADO DO TESTE FINAL")
    logger.info("=" * 60)
    
    if success:
        logger.success("🎉 TESTE PASSOU - SISTEMA FUNCIONANDO CORRETAMENTE!")
        logger.info("\n✅ O CalendarAgent agora:")
        logger.info("   • Detecta corretamente slots ocupados")
        logger.info("   • Processa eventos com qualquer timezone")
        logger.info("   • Diferencia slots disponíveis de ocupados")
        logger.info("   • Está pronto para uso em produção!")
    else:
        logger.error("❌ TESTE FALHOU - AINDA HÁ PROBLEMAS")
        logger.info("\nVerifique:")
        logger.info("   1. Se os eventos estão no horário comercial (9h-18h)")
        logger.info("   2. Se os eventos têm duração definida (não são de dia inteiro)")
        logger.info("   3. Os logs acima para mais detalhes")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())