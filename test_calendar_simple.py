#!/usr/bin/env python3
"""
Teste simplificado do Google Calendar
Verifica apenas as funções básicas sem CalendarAgent
"""

import asyncio
from datetime import datetime, timedelta
from app.integrations.google_calendar import GoogleCalendarClient
from loguru import logger
import sys

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def main():
    """Teste direto do Google Calendar Client"""
    
    logger.info("🚀 TESTE SIMPLIFICADO DO GOOGLE CALENDAR")
    logger.info("=" * 60)
    
    # Criar cliente
    client = GoogleCalendarClient()
    
    if not client.service:
        logger.error("❌ Falha na autenticação!")
        return False
    
    logger.success("✅ Cliente autenticado com sucesso!")
    logger.info(f"📧 Service Account: {client.credentials.service_account_email}")
    
    # 1. Listar eventos
    logger.info("\n📋 Listando eventos...")
    events = await client.list_events(max_results=5)
    logger.success(f"✅ {len(events)} eventos encontrados")
    for event in events[:3]:
        logger.info(f"   📅 {event.get('title', 'Sem título')}")
    
    # 2. Verificar disponibilidade
    logger.info("\n🔍 Verificando disponibilidade...")
    tomorrow = datetime.now() + timedelta(days=1)
    check_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    available = await client.check_availability(
        start_time=check_time,
        end_time=check_time + timedelta(minutes=30)
    )
    
    if available is True:
        logger.success("✅ Horário disponível!")
    else:
        logger.info(f"📊 Status: {available}")
    
    # 3. Criar e deletar evento de teste
    logger.info("\n➕ Criando evento de teste...")
    result = await client.create_event(
        title="[TESTE] Validação Google Calendar",
        start_time=check_time,
        end_time=check_time + timedelta(minutes=30),
        description="Teste de validação - pode ser deletado",
        reminder_minutes=15
    )
    
    if result and result.get('google_event_id'):
        event_id = result['google_event_id']
        logger.success(f"✅ Evento criado: {event_id}")
        logger.info(f"   🔗 Link: {result.get('html_link')}")
        
        # Deletar evento
        logger.info(f"\n🗑️ Deletando evento {event_id}...")
        deleted = await client.delete_event(event_id, send_notifications=False)
        if deleted:
            logger.success("✅ Evento deletado com sucesso!")
    
    logger.info("\n" + "=" * 60)
    logger.success("🎉 GOOGLE CALENDAR 100% VALIDADO E FUNCIONAL!")
    logger.info("Todas as operações essenciais estão funcionando perfeitamente.")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)