#!/usr/bin/env python3
"""
Check Follow-up Status
======================
Verifica o status do sistema de follow-up e mostra follow-ups pendentes
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logger.add("follow_up_check.log", rotation="1 MB")

async def check_follow_up_status():
    """Verifica status completo do sistema de follow-up"""
    
    logger.info("=== VERIFICAÇÃO DO SISTEMA DE FOLLOW-UP ===")
    
    # 1. Verificar configurações
    from config.agent_config import config as agent_config
    
    logger.info("\n📋 CONFIGURAÇÕES:")
    logger.info(f"  Follow-up habilitado: {agent_config.enable_follow_up}")
    logger.info(f"  Delay primeiro follow-up: {agent_config.follow_up_delay_minutes} minutos")
    logger.info(f"  Delay segundo follow-up: {agent_config.follow_up_second_delay_hours} horas")
    logger.info(f"  Follow-up inteligente: {agent_config.enable_intelligent_follow_up}")
    
    # 2. Verificar banco de dados
    from services.database import supabase_client
    
    try:
        # Contar follow-ups por status
        pending = supabase_client.table('follow_ups')\
            .select('*', count='exact')\
            .eq('status', 'pending')\
            .execute()
        
        executed = supabase_client.table('follow_ups')\
            .select('*', count='exact')\
            .eq('status', 'executed')\
            .execute()
        
        failed = supabase_client.table('follow_ups')\
            .select('*', count='exact')\
            .eq('status', 'failed')\
            .execute()
        
        logger.info("\n📊 ESTATÍSTICAS:")
        logger.info(f"  Follow-ups pendentes: {pending.count}")
        logger.info(f"  Follow-ups executados: {executed.count}")
        logger.info(f"  Follow-ups falhados: {failed.count}")
        
        # 3. Listar follow-ups pendentes que já deveriam ter sido executados
        overdue = supabase_client.table('follow_ups')\
            .select('*, leads!inner(*)')\
            .eq('status', 'pending')\
            .lte('scheduled_at', datetime.now().isoformat())\
            .order('scheduled_at')\
            .limit(10)\
            .execute()
        
        if overdue.data:
            logger.warning(f"\n⚠️ {len(overdue.data)} FOLLOW-UPS ATRASADOS:")
            for fu in overdue.data:
                scheduled = datetime.fromisoformat(fu['scheduled_at'].replace('Z', '+00:00'))
                delay = (datetime.now(scheduled.tzinfo) - scheduled).total_seconds() / 60
                
                lead = fu.get('leads', {})
                logger.warning(f"  - ID: {fu['id'][:8]}...")
                logger.warning(f"    Lead: {lead.get('name', 'N/A')} ({lead.get('phone_number', 'N/A')})")
                logger.warning(f"    Tipo: {fu['type']}")
                logger.warning(f"    Agendado para: {scheduled.strftime('%d/%m %H:%M')}")
                logger.warning(f"    Atraso: {delay:.0f} minutos")
                logger.warning("")
        else:
            logger.info("\n✅ Nenhum follow-up atrasado!")
        
        # 4. Verificar próximos follow-ups
        upcoming = supabase_client.table('follow_ups')\
            .select('*, leads!inner(*)')\
            .eq('status', 'pending')\
            .gt('scheduled_at', datetime.now().isoformat())\
            .order('scheduled_at')\
            .limit(5)\
            .execute()
        
        if upcoming.data:
            logger.info(f"\n📅 PRÓXIMOS {len(upcoming.data)} FOLLOW-UPS:")
            for fu in upcoming.data:
                scheduled = datetime.fromisoformat(fu['scheduled_at'].replace('Z', '+00:00'))
                time_until = (scheduled - datetime.now(scheduled.tzinfo)).total_seconds() / 60
                
                lead = fu.get('leads', {})
                logger.info(f"  - Lead: {lead.get('name', 'N/A')}")
                logger.info(f"    Tipo: {fu['type']}")
                logger.info(f"    Em: {time_until:.0f} minutos")
                logger.info("")
        
        # 5. Verificar última execução
        last_executed = supabase_client.table('follow_ups')\
            .select('*')\
            .eq('status', 'executed')\
            .order('executed_at', desc=True)\
            .limit(1)\
            .execute()
        
        if last_executed.data:
            last = last_executed.data[0]
            executed_at = datetime.fromisoformat(last['executed_at'].replace('Z', '+00:00'))
            logger.info(f"\n⏰ ÚLTIMA EXECUÇÃO:")
            logger.info(f"  Executado em: {executed_at.strftime('%d/%m/%Y %H:%M:%S')}")
            logger.info(f"  Há: {(datetime.now(executed_at.tzinfo) - executed_at).total_seconds() / 60:.0f} minutos")
        else:
            logger.warning("\n⚠️ Nenhum follow-up foi executado ainda!")
        
    except Exception as e:
        logger.error(f"Erro ao verificar banco de dados: {e}")
        return
    
    # 6. Verificar se o scheduler está configurado corretamente
    logger.info("\n🔧 VERIFICAÇÃO DO SISTEMA:")
    
    # Verificar qual main.py está sendo usado
    logger.info("  Para verificar qual main.py está em uso:")
    logger.info("  $ ps aux | grep uvicorn")
    logger.info("  ou")
    logger.info("  $ docker ps  # se usando Docker")
    
    # Sugestões
    logger.info("\n💡 SUGESTÕES:")
    if pending.count > 0 and not last_executed.data:
        logger.warning("  ⚠️ Há follow-ups pendentes mas nenhum foi executado!")
        logger.warning("  Verifique se o scheduler está rodando:")
        logger.warning("  1. Reinicie o servidor")
        logger.warning("  2. Verifique os logs por '✅ Follow-up scheduler iniciado'")
        logger.warning("  3. Verifique se ENABLE_FOLLOW_UP=true no .env")
    
    logger.info("\n=== FIM DA VERIFICAÇÃO ===")


async def test_create_follow_up():
    """Cria um follow-up de teste para verificar o sistema"""
    from services.follow_up_service import follow_up_service
    
    logger.info("\n🧪 CRIANDO FOLLOW-UP DE TESTE...")
    
    # Número de teste (você pode mudar)
    test_phone = "+5511999999999"
    
    result = await follow_up_service.create_follow_up_after_message(
        phone_number=test_phone,
        message_sent="Teste do sistema de follow-up",
        stage="INITIAL_CONTACT"
    )
    
    if result['status'] == 'success':
        logger.success(f"✅ Follow-up de teste criado!")
        logger.info(f"   ID: {result['follow_up_id']}")
        logger.info(f"   Agendado para: {result['scheduled_at']}")
        logger.info(f"   Em {result['minutes_until']} minutos")
        logger.info(f"\n⏳ Aguarde {result['minutes_until']} minutos e verifique se a mensagem foi enviada!")
    else:
        logger.error(f"❌ Erro ao criar follow-up de teste: {result}")


async def main():
    """Função principal"""
    import sys
    
    # Verificar status
    await check_follow_up_status()
    
    # Perguntar se quer criar um teste
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        await test_create_follow_up()


if __name__ == "__main__":
    asyncio.run(main())