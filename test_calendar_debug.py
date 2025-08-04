#!/usr/bin/env python3
"""
DEBUG - Verifica o que está sendo retornado do Google Calendar
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
logger.add(sys.stdout, level="DEBUG", format="<green>{time:HH:mm:ss}</green> | <cyan>{message}</cyan>")

async def debug_calendar():
    """Debug do Google Calendar"""
    
    logger.info("🔍 DEBUG DO GOOGLE CALENDAR")
    logger.info("=" * 60)
    
    try:
        # Criar cliente
        calendar_client = GoogleCalendarClient()
        
        # Buscar eventos dos próximos 7 dias
        time_min = datetime.now()
        time_max = time_min + timedelta(days=7)
        
        logger.info(f"📅 Buscando eventos de {time_min.strftime('%d/%m/%Y %H:%M')} até {time_max.strftime('%d/%m/%Y %H:%M')}")
        
        events = await calendar_client.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=50
        )
        
        logger.info(f"📊 Total de eventos encontrados: {len(events)}")
        
        if events:
            logger.info("\n🔴 EVENTOS ENCONTRADOS:")
            for i, event in enumerate(events, 1):
                logger.info(f"\n📌 Evento {i}:")
                logger.info(f"   ID: {event.get('id', 'N/A')}")
                logger.info(f"   Título: {event.get('summary', 'Sem título')}")
                logger.info(f"   Status: {event.get('status', 'N/A')}")
                
                # Processar horário de início
                start = event.get('start', {})
                if 'dateTime' in start:
                    logger.info(f"   Início (dateTime): {start['dateTime']}")
                elif 'date' in start:
                    logger.info(f"   Início (date): {start['date']} - DIA INTEIRO")
                else:
                    logger.info(f"   Início: {start}")
                
                # Processar horário de fim
                end = event.get('end', {})
                if 'dateTime' in end:
                    logger.info(f"   Fim (dateTime): {end['dateTime']}")
                elif 'date' in end:
                    logger.info(f"   Fim (date): {end['date']} - DIA INTEIRO")
                else:
                    logger.info(f"   Fim: {end}")
                
                # Outros detalhes
                logger.info(f"   Local: {event.get('location', 'N/A')}")
                desc = event.get('description', 'N/A')
                logger.info(f"   Descrição: {desc[:100] if desc and desc != 'N/A' else desc}...")
                
                # Verificar formatação para processar no CalendarAgent
                if 'dateTime' in start:
                    try:
                        # Tentar fazer parse do datetime
                        dt_str = start['dateTime']
                        if 'T' in dt_str:
                            # Remover timezone para teste
                            if '+' in dt_str:
                                dt_str = dt_str.split('+')[0]
                            elif 'Z' in dt_str:
                                dt_str = dt_str.replace('Z', '')
                            elif '-03:00' in dt_str or '-02:00' in dt_str:
                                dt_str = dt_str.split('-')[0]
                            
                            dt = datetime.fromisoformat(dt_str)
                            logger.success(f"   ✅ Parse OK: {dt.strftime('%d/%m/%Y %H:%M')}")
                        else:
                            logger.warning(f"   ⚠️ Formato inesperado: {dt_str}")
                    except Exception as e:
                        logger.error(f"   ❌ Erro no parse: {e}")
                
        else:
            logger.warning("⚠️ Nenhum evento encontrado no período!")
            logger.info("\nVerifique:")
            logger.info("1. Se o calendário está correto no .env")
            logger.info("2. Se há eventos no calendário")
            logger.info("3. Se as credenciais têm permissão de leitura")
        
        # Testar com um período maior
        logger.info("\n" + "=" * 60)
        logger.info("📅 Testando com período de 30 dias...")
        
        time_max_30 = time_min + timedelta(days=30)
        events_30 = await calendar_client.list_events(
            time_min=time_min,
            time_max=time_max_30,
            max_results=100
        )
        
        logger.info(f"📊 Total de eventos em 30 dias: {len(events_30)}")
        
        # Agrupar por dia
        events_by_day = {}
        for event in events_30:
            start = event.get('start', {})
            if 'dateTime' in start:
                dt_str = start['dateTime']
                # Extrair apenas a data
                if 'T' in dt_str:
                    date_part = dt_str.split('T')[0]
                    if date_part not in events_by_day:
                        events_by_day[date_part] = []
                    events_by_day[date_part].append(event.get('summary', 'Sem título'))
        
        if events_by_day:
            logger.info("\n📊 EVENTOS POR DIA:")
            for date_str in sorted(events_by_day.keys())[:10]:
                logger.info(f"   {date_str}: {len(events_by_day[date_str])} eventos - {', '.join(events_by_day[date_str][:3])}")
        
        # Salvar eventos para análise
        with open("calendar_events_debug.json", "w", encoding="utf-8") as f:
            json.dump(events_30, f, indent=2, ensure_ascii=False, default=str)
        logger.info("\n💾 Eventos salvos em calendar_events_debug.json para análise")
        
        return len(events) > 0
        
    except Exception as e:
        logger.error(f"❌ Erro no debug: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await debug_calendar()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.success("✅ Eventos encontrados - verificar processamento")
    else:
        logger.warning("⚠️ Problema na busca de eventos")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())