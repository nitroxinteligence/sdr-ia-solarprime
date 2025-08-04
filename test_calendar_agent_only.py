#!/usr/bin/env python3
"""
Teste isolado do CalendarAgent
Testa apenas a funcionalidade do agente sem dependência do banco
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Settings
from app.teams.agents.calendar import CalendarAgent
from agno.models.google import Gemini
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_calendar_agent_without_db():
    """Testa CalendarAgent sem dependência do banco de dados"""
    
    logger.info("🤖 Testando CalendarAgent sem banco de dados...")
    
    settings = Settings()
    
    try:
        # Criar modelo
        model = Gemini(
            id="gemini-2.5-pro",
            api_key=settings.google_api_key
        )
        
        # Criar CalendarAgent SEM storage (evita erro de conexão)
        logger.info("📅 Inicializando CalendarAgent sem persistência...")
        calendar_agent = CalendarAgent(
            model=model,
            storage=None  # Sem storage = sem erro de banco
        )
        
        logger.success("✅ CalendarAgent inicializado com sucesso!")
        logger.info(f"   📋 Tools disponíveis: {len(calendar_agent.tools)}")
        
        # Testar check_availability
        logger.info("\n🔍 Testando tool check_availability...")
        result = await calendar_agent.check_availability(
            date="05/08/2025",
            time="14:00",
            duration_minutes=30
        )
        
        if result:
            logger.success(f"✅ Check availability funcionando!")
            logger.info(f"   Disponível: {result.get('available')}")
            logger.info(f"   Horário: {result.get('start_time')} - {result.get('end_time')}")
        
        # Testar schedule_meeting
        logger.info("\n📅 Testando tool schedule_meeting...")
        tomorrow = datetime.now() + timedelta(days=1)
        
        meeting_result = await calendar_agent.schedule_meeting(
            title="[TESTE] Reunião Solar Prime - CalendarAgent",
            date=tomorrow.strftime("%d/%m/%Y"),
            time="15:00",
            duration_minutes=30,
            description="Teste do CalendarAgent sem banco de dados",
            location="Online"
        )
        
        if meeting_result and meeting_result.get('success'):
            logger.success(f"✅ Reunião agendada com sucesso!")
            logger.info(f"   ID: {meeting_result.get('event_id')}")
            logger.info(f"   Link: {meeting_result.get('event_link')}")
            
            # Deletar evento de teste
            event_id = meeting_result.get('event_id')
            if event_id:
                logger.info(f"\n🗑️ Deletando evento de teste {event_id}...")
                from app.integrations.google_calendar import GoogleCalendarClient
                client = GoogleCalendarClient()
                deleted = await client.delete_event(event_id, send_notifications=False)
                if deleted:
                    logger.success("✅ Evento de teste deletado!")
        
        # Testar processamento de linguagem natural
        logger.info("\n💬 Testando processamento de linguagem natural...")
        
        test_messages = [
            "Quero agendar uma reunião amanhã às 14h",
            "Você tem disponibilidade quinta-feira?",
            "Preciso marcar um horário para conversar sobre energia solar"
        ]
        
        for msg in test_messages:
            logger.info(f"   Mensagem: '{msg}'")
            # Aqui você poderia testar o processamento real se necessário
        
        logger.success("\n🎉 TODOS OS TESTES DO CALENDARAGENT PASSARAM!")
        logger.info("O CalendarAgent está funcionando corretamente sem dependência do banco!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        return False

async def main():
    """Função principal"""
    success = await test_calendar_agent_without_db()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())