"""
Test Follow-up System
====================
Testa o funcionamento completo do sistema de follow-up
"""

import asyncio
import os
from datetime import datetime, timedelta
from loguru import logger

# Configurar ambiente
os.environ["ENABLE_FOLLOW_UP"] = "true"
os.environ["FOLLOW_UP_DELAY_MINUTES"] = "30"
os.environ["FOLLOW_UP_SECOND_DELAY_HOURS"] = "24"

from config.agent_config import config as agent_config
from services.follow_up_service import follow_up_service
from workflows.follow_up_workflow import FollowUpWorkflow
from services.database import supabase_client
from repositories.lead_repository import lead_repository


async def test_follow_up_creation():
    """Testa criação de follow-up"""
    logger.info("=== TESTE 1: Criação de Follow-up ===")
    
    # Verificar configuração
    logger.info(f"Follow-up habilitado: {agent_config.enable_follow_up}")
    logger.info(f"Delay primeiro follow-up: {agent_config.follow_up_delay_minutes} minutos")
    logger.info(f"Delay segundo follow-up: {agent_config.follow_up_second_delay_hours} horas")
    
    # Buscar um lead de teste
    leads = await lead_repository.get_all(limit=1)
    if not leads:
        logger.error("Nenhum lead encontrado no banco. Criar um lead primeiro.")
        return False
        
    lead = leads[0]
    logger.info(f"Usando lead: {lead.name} ({lead.phone_number})")
    
    # Criar follow-up
    result = await follow_up_service.create_follow_up_after_message(
        phone_number=lead.phone_number,
        lead_id=str(lead.id),
        message_sent="Olá! Sou a Luna da SolarPrime. Como posso ajudar com energia solar?",
        stage="INITIAL_CONTACT"
    )
    
    logger.info(f"Resultado da criação: {result}")
    
    if result['status'] == 'success':
        logger.success(f"✓ Follow-up criado com sucesso! ID: {result['follow_up_id']}")
        logger.info(f"  Agendado para: {result['scheduled_at']}")
        logger.info(f"  Minutos até execução: {result['minutes_until']}")
        return True
    else:
        logger.error(f"✗ Erro ao criar follow-up: {result}")
        return False


async def test_follow_up_execution():
    """Testa execução de follow-up"""
    logger.info("\n=== TESTE 2: Execução de Follow-up ===")
    
    # Buscar um lead existente
    leads = await lead_repository.get_all(limit=1)
    if not leads:
        logger.error("Nenhum lead encontrado")
        return False
        
    lead = leads[0]
    
    # Usar o ID correto do lead
    lead_id = str(lead.id) if lead.id else None
    if not lead_id:
        logger.error("Lead sem ID válido")
        return False
        
    logger.info(f"Usando lead para teste: {lead.name} (ID: {lead_id})")
    
    # Criar follow-up com tempo passado (para execução imediata)
    scheduled_time = datetime.now() - timedelta(minutes=5)  # 5 minutos atrás
    
    follow_up_data = {
        'lead_id': lead_id,  # Usar o lead_id correto
        'type': 'reminder',  # Usar tipo existente
        'scheduled_at': scheduled_time.isoformat(),
        'status': 'pending',
        'message': 'Teste de follow-up automático'
    }
    
    result = supabase_client.table('follow_ups').insert(follow_up_data).execute()
    
    if result.data:
        follow_up_id = result.data[0]['id']
        logger.info(f"Follow-up de teste criado: {follow_up_id}")
        
        # Executar workflow
        workflow = FollowUpWorkflow()
        
        # Como run retorna um Iterator, precisamos consumir os resultados
        exec_results = list(workflow.run(
            lead_id=follow_up_data['lead_id'],  # Usar o ID correto
            follow_up_type='reminder'  # Usar tipo existente
        ))
        
        if exec_results:
            exec_result = exec_results[0]  # Pegar o primeiro resultado
            logger.info(f"Resultado da execução: {exec_result}")
            
            # Extrair content do RunResponse
            if hasattr(exec_result, 'content'):
                result_data = exec_result.content
            else:
                result_data = exec_result
        else:
            logger.error("Nenhum resultado retornado do workflow")
            return False
            
        if result_data.get('status') == 'success':
            logger.success("✓ Follow-up executado com sucesso!")
            logger.info(f"  Mensagem enviada: {result_data.get('message', 'N/A')}")
            logger.info(f"  Tempo de execução: {result_data.get('execution_time', 'N/A')}s")
            return True
        else:
            logger.error(f"✗ Erro na execução: {result_data}")
            return False
    else:
        logger.error("Erro ao criar follow-up de teste")
        return False


async def test_follow_up_scheduler():
    """Testa agendador de follow-ups"""
    logger.info("\n=== TESTE 3: Agendador de Follow-ups ===")
    
    # Listar follow-ups pendentes
    pending = await follow_up_service.get_pending_follow_ups()
    logger.info(f"Follow-ups pendentes: {len(pending)}")
    
    for fu in pending:
        logger.info(f"  - {fu['type']} para lead {fu['leads']['name']} agendado para {fu['scheduled_at']}")
    
    return True


async def test_follow_up_types():
    """Testa diferentes tipos de follow-up"""
    logger.info("\n=== TESTE 4: Tipos de Follow-up ===")
    
    workflow = FollowUpWorkflow()
    
    # Testar geração de mensagens para diferentes tipos
    test_lead_data = {
        'name': 'Teste Silva',
        'stage': 'DISCOVERY',
        'qualification_score': 70
    }
    
    for follow_up_type in ['reminder', 'check_in', 'reengagement', 'nurture']:
        logger.info(f"\nTestando tipo: {follow_up_type}")
        
        try:
            message = await workflow._generate_follow_up_message(test_lead_data, follow_up_type)
            logger.success(f"✓ Mensagem gerada: {message[:100]}...")
        except Exception as e:
            logger.error(f"✗ Erro ao gerar mensagem: {e}")
    
    return True


async def main():
    """Executa todos os testes"""
    logger.info("====== TESTE DO SISTEMA DE FOLLOW-UP ======")
    logger.info(f"Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Criação de Follow-up", test_follow_up_creation),
        ("Execução de Follow-up", test_follow_up_execution),
        ("Agendador", test_follow_up_scheduler),
        ("Tipos de Follow-up", test_follow_up_types)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Erro no teste {test_name}: {e}", exc_info=True)
            results.append((test_name, False))
    
    # Resumo
    logger.info("\n====== RESUMO DOS TESTES ======")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSOU" if success else "✗ FALHOU"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.success("🎉 Todos os testes passaram! Sistema de follow-up funcionando corretamente.")
    else:
        logger.warning(f"⚠️ {total - passed} testes falharam. Verificar logs acima.")


if __name__ == "__main__":
    asyncio.run(main())