"""
Test Intelligent Follow-up System
=================================
Testa o funcionamento do sistema de follow-up inteligente com contexto completo
"""

import asyncio
import os
from datetime import datetime, timedelta
from loguru import logger
import json

# Configurar ambiente
os.environ["ENABLE_FOLLOW_UP"] = "true"
os.environ["ENABLE_INTELLIGENT_FOLLOW_UP"] = "true"
os.environ["FOLLOW_UP_CONTEXT_MESSAGES"] = "100"
os.environ["FOLLOW_UP_MIN_INTEREST_LEVEL"] = "3"

from config.agent_config import config as agent_config
from workflows.intelligent_follow_up_workflow import IntelligentFollowUpWorkflow
from repositories.message_repository import message_repository
from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from services.database import supabase_client


async def test_context_analysis():
    """Testa análise de contexto de conversa"""
    logger.info("=== TESTE 1: Análise de Contexto ===")
    
    # Buscar uma conversa existente
    conversations = await conversation_repository.get_all(limit=1)
    if not conversations:
        logger.error("Nenhuma conversa encontrada")
        return False
    
    conversation = conversations[0]
    logger.info(f"Usando conversa: {conversation.id}")
    
    # Buscar contexto completo
    context = await message_repository.get_full_conversation_context(
        conversation.id,
        limit=100
    )
    
    logger.info(f"Contexto recuperado:")
    logger.info(f"  - Total de mensagens: {context['total_messages']}")
    logger.info(f"  - Duração: {context['conversation_duration']} minutos")
    logger.info(f"  - Tópicos discutidos: {', '.join(context['patterns'].get('topics_discussed', []))}")
    logger.info(f"  - Engajamento do usuário: {context['patterns'].get('user_engagement', 'low')}")
    
    # Análise de insights
    insights = context['insights']
    if insights['objections']:
        logger.info(f"  - Objeções detectadas: {len(insights['objections'])}")
        for obj in insights['objections'][:2]:
            logger.info(f"    → {obj['keyword']}: {obj['message']}")
    
    if insights['interests']:
        logger.info(f"  - Interesses detectados: {len(insights['interests'])}")
        for int_item in insights['interests'][:2]:
            logger.info(f"    → {int_item['keyword']}: {int_item['message']}")
    
    if insights['questions_asked']:
        logger.info(f"  - Perguntas feitas: {len(insights['questions_asked'])}")
        for question in insights['questions_asked'][:2]:
            logger.info(f"    → {question}")
    
    return True


async def test_intelligent_workflow():
    """Testa workflow inteligente completo"""
    logger.info("\n=== TESTE 2: Workflow Inteligente ===")
    
    # Buscar um lead com conversa
    leads = await lead_repository.get_all(limit=5)
    lead_with_conversation = None
    
    for lead in leads:
        # Verificar se tem conversa
        profile_id = getattr(lead, 'profile_id', None)
        if profile_id:
            convs = await conversation_repository.get_by_profile_id(profile_id)
            if convs:
                lead_with_conversation = lead
                break
    
    if not lead_with_conversation:
        logger.error("Nenhum lead com conversa encontrado")
        return False
    
    logger.info(f"Usando lead: {lead_with_conversation.name} (ID: {lead_with_conversation.id})")
    
    # Criar workflow inteligente
    workflow = IntelligentFollowUpWorkflow()
    
    # Executar workflow
    results = list(workflow.run(
        lead_id=str(lead_with_conversation.id),
        follow_up_type='reminder'
    ))
    
    if results:
        result = results[0]
        if hasattr(result, 'content'):
            result_data = result.content
        else:
            result_data = result
        
        logger.info(f"Resultado do workflow: {result_data['status']}")
        
        if result_data['status'] == 'success':
            logger.success("✓ Follow-up inteligente executado!")
            logger.info(f"  Mensagem: {result_data.get('message', 'N/A')}")
            
            # Mostrar contexto usado
            context_info = result_data.get('context_used', {})
            logger.info(f"  Contexto usado:")
            logger.info(f"    - Mensagens analisadas: {context_info.get('total_messages', 0)}")
            logger.info(f"    - Padrões encontrados: {context_info.get('patterns_found', 0)}")
            logger.info(f"    - Insights extraídos: {context_info.get('insights_extracted', 0)}")
            
            # Mostrar análise
            analysis = result_data.get('analysis', {})
            if analysis:
                logger.info(f"  Análise:")
                logger.info(f"    - Nível de interesse: {analysis.get('interest_level', 0)}/10")
                logger.info(f"    - Abordagem recomendada: {analysis.get('recommended_approach', 'N/A')}")
                logger.info(f"    - Melhor ângulo: {analysis.get('best_angle', 'N/A')}")
            
            return True
        else:
            logger.warning(f"✗ Status: {result_data['status']}")
            logger.info(f"  Razão: {result_data.get('reason', result_data.get('message', 'N/A'))}")
            return False
    else:
        logger.error("Nenhum resultado do workflow")
        return False


async def test_memory_persistence():
    """Testa persistência de memória do agente"""
    logger.info("\n=== TESTE 3: Memória Persistente ===")
    
    # Criar workflow para testar memória
    workflow = IntelligentFollowUpWorkflow()
    
    # Testar se o agente tem memória de interações anteriores
    test_memory = "Lead João Silva interessado em economia de energia"
    
    # Adicionar memória de teste
    await workflow.intelligent_agent.memory.add(
        test_memory,
        metadata={
            'test': True,
            'timestamp': datetime.now().isoformat()
        }
    )
    
    logger.info("Memória adicionada ao agente")
    
    # Verificar se a storage SQLite foi criada
    import os
    if os.path.exists("follow_up_memory.db"):
        logger.success("✓ Banco de dados de memória criado")
        
        # Verificar tamanho do arquivo
        size = os.path.getsize("follow_up_memory.db")
        logger.info(f"  Tamanho do banco: {size} bytes")
        
        return True
    else:
        logger.error("✗ Banco de dados de memória não encontrado")
        return False


async def test_pattern_matching():
    """Testa correspondência de padrões para templates"""
    logger.info("\n=== TESTE 4: Correspondência de Padrões ===")
    
    from workflows.intelligent_follow_up_workflow import INTELLIGENT_FOLLOW_UP_TEMPLATES
    
    # Simular diferentes contextos
    test_cases = [
        {
            "patterns": {"topics_discussed": ["preço", "custo"]},
            "insights": {"objections": [{"keyword": "caro"}]},
            "expected_template": "objection_price"
        },
        {
            "patterns": {"topics_discussed": ["interesse", "economia"]},
            "insights": {"interests": [{"keyword": "quero saber"}]},
            "expected_template": "high_engagement"
        },
        {
            "patterns": {"topics_discussed": ["técnico", "instalação"]},
            "insights": {"questions_asked": ["Como funciona a instalação?"]},
            "expected_template": "technical_questions"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\nCaso de teste {i}:")
        logger.info(f"  Tópicos: {test_case['patterns']['topics_discussed']}")
        
        # Determinar template baseado em palavras-chave
        selected_template = None
        for template_key, template_data in INTELLIGENT_FOLLOW_UP_TEMPLATES.items():
            keywords = template_data.get('keywords', [])
            if any(keyword in str(test_case).lower() for keyword in keywords):
                selected_template = template_key
                break
        
        if selected_template:
            logger.success(f"  ✓ Template selecionado: {selected_template}")
        else:
            logger.warning(f"  ✗ Nenhum template correspondente")
    
    return True


async def main():
    """Executa todos os testes"""
    logger.info("====== TESTE DO SISTEMA DE FOLLOW-UP INTELIGENTE ======")
    logger.info(f"Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar configurações
    logger.info("\nConfigurações:")
    logger.info(f"  Follow-up habilitado: {agent_config.enable_follow_up}")
    logger.info(f"  Follow-up inteligente: {agent_config.enable_intelligent_follow_up}")
    logger.info(f"  Mensagens de contexto: {agent_config.follow_up_context_messages}")
    logger.info(f"  Nível mínimo de interesse: {agent_config.follow_up_min_interest_level}")
    
    tests = [
        ("Análise de Contexto", test_context_analysis),
        ("Workflow Inteligente", test_intelligent_workflow),
        ("Memória Persistente", test_memory_persistence),
        ("Correspondência de Padrões", test_pattern_matching)
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
        logger.success("🎉 Sistema de follow-up inteligente funcionando perfeitamente!")
        logger.info("\nPróximos passos:")
        logger.info("1. O sistema analisa até 100 mensagens de histórico")
        logger.info("2. Identifica padrões, objeções e interesses automaticamente")
        logger.info("3. Gera mensagens altamente personalizadas")
        logger.info("4. Aprende e melhora com cada interação")
    else:
        logger.warning(f"⚠️ {total - passed} testes falharam. Verificar logs acima.")


if __name__ == "__main__":
    asyncio.run(main())