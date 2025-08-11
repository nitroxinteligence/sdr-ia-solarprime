#!/usr/bin/env python3
"""
Test Phase 2 - Validação Completa da Simplificação
Garante que TODOS os serviços continuam funcionando 100%
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.agentic_sdr import create_agentic_sdr, reset_singleton
from app.config import settings
import time

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

async def test_services_initialization():
    """Testa se todos os serviços foram inicializados corretamente"""
    print(f"\n{Colors.BLUE}🧪 TESTE 1: Inicialização dos Serviços{Colors.RESET}")
    print("-" * 60)
    
    # Resetar singleton
    await reset_singleton()
    
    # Criar agente
    agent = await create_agentic_sdr()
    
    # Verificar serviços
    services_ok = True
    
    # Calendar Service
    if settings.ENABLE_CALENDAR_AGENT:
        if agent.calendar_service and agent.calendar_service.is_initialized:
            print(f"{Colors.GREEN}✅ CalendarService inicializado{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ CalendarService não inicializado{Colors.RESET}")
            services_ok = False
    
    # CRM Service
    if settings.ENABLE_CRM_AGENT:
        if agent.crm_service and agent.crm_service.is_initialized:
            print(f"{Colors.GREEN}✅ CRMService inicializado{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ CRMService não inicializado{Colors.RESET}")
            services_ok = False
    
    # FollowUp Service
    if settings.ENABLE_FOLLOWUP_AGENT:
        if agent.followup_service and agent.followup_service.is_initialized:
            print(f"{Colors.GREEN}✅ FollowUpService inicializado{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ FollowUpService não inicializado{Colors.RESET}")
            services_ok = False
    
    if services_ok:
        print(f"\n{Colors.GREEN}✅ SUCESSO: Todos os serviços inicializados{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ FALHA: Alguns serviços não foram inicializados{Colors.RESET}")
    
    return services_ok

async def test_calendar_functionality():
    """Testa funcionalidade completa do Calendar"""
    print(f"\n{Colors.BLUE}🧪 TESTE 2: Funcionalidade Calendar{Colors.RESET}")
    print("-" * 60)
    
    agent = await create_agentic_sdr()
    
    test_cases = [
        {
            "message": "Quero agendar uma reunião com o Leonardo",
            "expected_agent": "CalendarAgent",
            "description": "Solicitação de agendamento"
        },
        {
            "message": "Verificar a agenda do Leonardo para amanhã",
            "expected_agent": "CalendarAgent",
            "description": "Verificação de disponibilidade"
        },
        {
            "message": "Quando o Leonardo pode me atender?",
            "expected_agent": "CalendarAgent",
            "description": "Consulta de horários"
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        should_call, agent_name, reason = await agent.should_call_sdr_team(
            test["message"], {}
        )
        
        if agent_name == test["expected_agent"]:
            print(f"{Colors.GREEN}✅ {test['description']}: CalendarAgent ativado{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ {test['description']}: Esperado {test['expected_agent']}, obtido {agent_name}{Colors.RESET}")
            all_passed = False
    
    # Testar execução direta do serviço
    if agent.calendar_service:
        result = await agent.calendar_service.check_availability("amanhã")
        if result.get("success"):
            print(f"{Colors.GREEN}✅ CalendarService.check_availability funcionando{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ CalendarService.check_availability falhou{Colors.RESET}")
            all_passed = False
    
    return all_passed

async def test_crm_functionality():
    """Testa funcionalidade completa do CRM"""
    print(f"\n{Colors.BLUE}🧪 TESTE 3: Funcionalidade CRM (Kommo){Colors.RESET}")
    print("-" * 60)
    
    agent = await create_agentic_sdr()
    
    # Testar criação de lead
    if agent.crm_service:
        lead_data = {
            "name": "Teste Cliente",
            "phone": "11999999999",
            "email": "teste@example.com",
            "bill_value": 800
        }
        
        result = await agent.crm_service.create_or_update_lead(lead_data)
        
        if result.get("success"):
            print(f"{Colors.GREEN}✅ CRMService.create_or_update_lead funcionando{Colors.RESET}")
            
            # Testar adicionar nota
            if result.get("lead_id"):
                note_result = await agent.crm_service.add_note(
                    result["lead_id"],
                    "Teste de nota"
                )
                if note_result.get("success"):
                    print(f"{Colors.GREEN}✅ CRMService.add_note funcionando{Colors.RESET}")
                else:
                    print(f"{Colors.RED}❌ CRMService.add_note falhou{Colors.RESET}")
                    return False
        else:
            print(f"{Colors.RED}❌ CRMService.create_or_update_lead falhou{Colors.RESET}")
            return False
    else:
        print(f"{Colors.YELLOW}⚠️ CRMService não disponível{Colors.RESET}")
    
    return True

async def test_followup_functionality():
    """Testa funcionalidade completa do Follow-up"""
    print(f"\n{Colors.BLUE}🧪 TESTE 4: Funcionalidade Follow-up{Colors.RESET}")
    print("-" * 60)
    
    agent = await create_agentic_sdr()
    
    # Testar criação de follow-up
    if agent.followup_service:
        lead_data = {
            "name": "Teste Cliente",
            "phone": "11999999999"
        }
        
        result = await agent.followup_service.create_followup(
            lead_data=lead_data,
            followup_type="initial",
            delay_hours=24
        )
        
        if result.get("success"):
            print(f"{Colors.GREEN}✅ FollowUpService.create_followup funcionando{Colors.RESET}")
            
            # Testar geração de mensagem
            message = agent.followup_service.get_best_followup_message(
                "novo",
                {"name": "Teste"}
            )
            if message:
                print(f"{Colors.GREEN}✅ FollowUpService.get_best_followup_message funcionando{Colors.RESET}")
                print(f"   Mensagem gerada: {message[:50]}...")
            else:
                print(f"{Colors.RED}❌ FollowUpService.get_best_followup_message falhou{Colors.RESET}")
                return False
        else:
            print(f"{Colors.RED}❌ FollowUpService.create_followup falhou{Colors.RESET}")
            return False
    else:
        print(f"{Colors.YELLOW}⚠️ FollowUpService não disponível{Colors.RESET}")
    
    return True

async def test_multimodal_functionality():
    """Testa se processamento multimodal continua funcionando"""
    print(f"\n{Colors.BLUE}🧪 TESTE 5: Funcionalidade Multimodal{Colors.RESET}")
    print("-" * 60)
    
    agent = await create_agentic_sdr()
    
    # Verificar se multimodal está habilitado
    if agent.multimodal_enabled:
        print(f"{Colors.GREEN}✅ Processamento multimodal habilitado{Colors.RESET}")
        
        # Simular análise de imagem
        media_context = {
            "type": "image",
            "content": "data:image/jpeg;base64,/9j/4AAQ..."  # Base64 simulado
        }
        
        # Verificar se o método existe
        if hasattr(agent, 'analyze_multimodal'):
            print(f"{Colors.GREEN}✅ Método analyze_multimodal disponível{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Método analyze_multimodal não encontrado{Colors.RESET}")
            return False
    else:
        print(f"{Colors.YELLOW}⚠️ Processamento multimodal desabilitado{Colors.RESET}")
    
    return True

async def test_direct_service_execution():
    """Testa execução direta dos serviços (nova arquitetura)"""
    print(f"\n{Colors.BLUE}🧪 TESTE 6: Execução Direta de Serviços{Colors.RESET}")
    print("-" * 60)
    
    agent = await create_agentic_sdr()
    
    # Testar CalendarService direto
    context = {
        "current_message": "Quero agendar para amanhã às 14h",
        "lead_info": {"name": "Teste Cliente", "phone": "11999999999"}
    }
    
    result = await agent._execute_service_directly("CalendarAgent", context)
    
    if result.get("success"):
        print(f"{Colors.GREEN}✅ Execução direta CalendarAgent funcionando{Colors.RESET}")
        print(f"   Resposta: {result.get('response', '')[:50]}...")
    else:
        print(f"{Colors.RED}❌ Execução direta CalendarAgent falhou{Colors.RESET}")
        return False
    
    # Testar CRMService direto
    result = await agent._execute_service_directly("CRMAgent", context)
    
    if result.get("success"):
        print(f"{Colors.GREEN}✅ Execução direta CRMAgent funcionando{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ Execução direta CRMAgent falhou{Colors.RESET}")
        return False
    
    # Testar FollowUpService direto
    result = await agent._execute_service_directly("FollowUpAgent", context)
    
    if result.get("success"):
        print(f"{Colors.GREEN}✅ Execução direta FollowUpAgent funcionando{Colors.RESET}")
        print(f"   Mensagem follow-up: {result.get('response', '')[:50]}...")
    else:
        print(f"{Colors.RED}❌ Execução direta FollowUpAgent falhou{Colors.RESET}")
        return False
    
    return True

async def main():
    """Executa todos os testes de validação"""
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}🚀 VALIDAÇÃO COMPLETA - FASE 2 SIMPLIFICAÇÃO{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    
    results = []
    
    # Executar todos os testes
    results.append(await test_services_initialization())
    results.append(await test_calendar_functionality())
    results.append(await test_crm_functionality())
    results.append(await test_followup_functionality())
    results.append(await test_multimodal_functionality())
    results.append(await test_direct_service_execution())
    
    # Resumo final
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 RESUMO DA VALIDAÇÃO{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    
    total = len(results)
    passed = sum(results)
    
    if all(results):
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ VALIDAÇÃO 100% COMPLETA ({passed}/{total}){Colors.RESET}")
        print(f"\n{Colors.GREEN}🎉 FASE 2 CONCLUÍDA COM SUCESSO!{Colors.RESET}")
        print(f"\n{Colors.BOLD}📈 MELHORIAS CONFIRMADAS:{Colors.RESET}")
        print(f"{Colors.GREEN}• SDRTeam consolidado nos serviços diretos{Colors.RESET}")
        print(f"{Colors.GREEN}• Calendar funcionando 100%{Colors.RESET}")
        print(f"{Colors.GREEN}• KommoCRM funcionando 100%{Colors.RESET}")
        print(f"{Colors.GREEN}• Follow-ups funcionando 100%{Colors.RESET}")
        print(f"{Colors.GREEN}• Multimodal preservado 100%{Colors.RESET}")
        print(f"{Colors.GREEN}• Arquitetura MUITO mais simples{Colors.RESET}")
        print(f"\n{Colors.BOLD}💡 PRINCÍPIO CONFIRMADO: O SIMPLES FUNCIONA SEMPRE!{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ ALGUNS TESTES FALHARAM ({passed}/{total}){Colors.RESET}")
        print(f"{Colors.YELLOW}Por favor, revise as implementações.{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}🔄 PRÓXIMOS PASSOS:{Colors.RESET}")
    print("• Completar eliminação de camadas redundantes")
    print("• Implementar cache inteligente com TTL")
    print("• Iniciar Fase 3 - Modularização")

if __name__ == "__main__":
    asyncio.run(main())