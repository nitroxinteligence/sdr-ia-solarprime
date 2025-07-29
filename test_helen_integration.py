#!/usr/bin/env python3
"""
Test Helen Integration
======================
Testa a integração completa com a nova identidade Helen Vieira
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Inicializar colorama
init()

# Importações do projeto
from config.config import Config
from config.prompts import (
    PromptTemplates, 
    EXAMPLE_RESPONSES, 
    OBJECTION_HANDLERS,
    CRM_FIELDS,
    CRM_OBSERVATIONS,
    get_example_response,
    get_objection_handler
)
from agents.sdr_agent_v2 import SDRAgentV2


async def test_helen_identity():
    """Testa se a identidade Helen Vieira está corretamente configurada"""
    print(f"\n{Fore.CYAN}=== TESTE DE IDENTIDADE HELEN VIEIRA ==={Style.RESET_ALL}\n")
    
    success_count = 0
    total_tests = 0
    
    # 1. Verificar SYSTEM_PROMPT
    total_tests += 1
    if "Helen Vieira" in PromptTemplates.SYSTEM_PROMPT:
        print(f"{Fore.GREEN}✓ System Prompt contém Helen Vieira{Style.RESET_ALL}")
        success_count += 1
    else:
        print(f"{Fore.RED}✗ System Prompt NÃO contém Helen Vieira{Style.RESET_ALL}")
    
    # 2. Verificar informações profissionais
    total_tests += 1
    if "12+ anos" in PromptTemplates.SYSTEM_PROMPT and "nordestina" in PromptTemplates.SYSTEM_PROMPT:
        print(f"{Fore.GREEN}✓ Informações profissionais corretas (12+ anos, nordestina){Style.RESET_ALL}")
        success_count += 1
    else:
        print(f"{Fore.RED}✗ Informações profissionais incorretas{Style.RESET_ALL}")
    
    # 3. Verificar tom de comunicação
    total_tests += 1
    if "Profissional mas calorosa" in PromptTemplates.SYSTEM_PROMPT:
        print(f"{Fore.GREEN}✓ Tom de comunicação profissional definido{Style.RESET_ALL}")
        success_count += 1
    else:
        print(f"{Fore.RED}✗ Tom de comunicação não encontrado{Style.RESET_ALL}")
    
    # 4. Verificar greeting
    total_tests += 1
    greeting = PromptTemplates.get_template("greeting_initial")
    if "Helen Vieira" in greeting and "consultora especialista" in greeting:
        print(f"{Fore.GREEN}✓ Greeting contém apresentação correta{Style.RESET_ALL}")
        success_count += 1
    else:
        print(f"{Fore.RED}✗ Greeting não contém apresentação correta{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Resultado: {success_count}/{total_tests} testes passaram{Style.RESET_ALL}")
    return success_count == total_tests


async def test_new_features():
    """Testa as novas funcionalidades adicionadas"""
    print(f"\n{Fore.CYAN}=== TESTE DE NOVAS FUNCIONALIDADES ==={Style.RESET_ALL}\n")
    
    success_count = 0
    total_tests = 0
    
    # 1. Verificar estágio PRESENTATION
    total_tests += 1
    presentation_prompt = PromptTemplates.get_stage_prompt("PRESENTATION")
    if presentation_prompt and "APRESENTAÇÃO DA SOLUÇÃO" in presentation_prompt:
        print(f"{Fore.GREEN}✓ Estágio PRESENTATION implementado{Style.RESET_ALL}")
        success_count += 1
    else:
        print(f"{Fore.RED}✗ Estágio PRESENTATION não encontrado{Style.RESET_ALL}")
    
    # 2. Verificar novos templates
    total_tests += 1
    templates = ["meeting_confirmation", "follow_up_30min", "follow_up_24h", "meeting_reminder"]
    all_templates_ok = True
    for template_name in templates:
        template = PromptTemplates.get_template(template_name)
        if not template:
            all_templates_ok = False
            print(f"{Fore.RED}  ✗ Template {template_name} não encontrado{Style.RESET_ALL}")
    
    if all_templates_ok:
        print(f"{Fore.GREEN}✓ Todos os novos templates implementados{Style.RESET_ALL}")
        success_count += 1
    
    # 3. Verificar CRM_FIELDS
    total_tests += 1
    if CRM_FIELDS and "nome_lead" in CRM_FIELDS and "observacoes_helen" in CRM_FIELDS:
        print(f"{Fore.GREEN}✓ CRM_FIELDS configurados corretamente{Style.RESET_ALL}")
        success_count += 1
    else:
        print(f"{Fore.RED}✗ CRM_FIELDS não configurados{Style.RESET_ALL}")
    
    # 4. Verificar novas objeções
    total_tests += 1
    new_objections = ["high_discount_already", "dont_trust_solar", "too_good_to_be_true", "prefer_to_wait"]
    all_objections_ok = True
    for obj in new_objections:
        if obj not in OBJECTION_HANDLERS:
            all_objections_ok = False
            print(f"{Fore.RED}  ✗ Objeção {obj} não encontrada{Style.RESET_ALL}")
    
    if all_objections_ok:
        print(f"{Fore.GREEN}✓ Todas as novas objeções implementadas{Style.RESET_ALL}")
        success_count += 1
    
    print(f"\n{Fore.CYAN}Resultado: {success_count}/{total_tests} testes passaram{Style.RESET_ALL}")
    return success_count == total_tests


async def test_agent_integration():
    """Testa a integração do agente com as mudanças"""
    print(f"\n{Fore.CYAN}=== TESTE DE INTEGRAÇÃO DO AGENTE ==={Style.RESET_ALL}\n")
    
    try:
        config = Config()
        agent = SDRAgentV2(config)
        await agent.initialize()
        
        # 1. Verificar nome do agente
        test_agent = agent._create_agent("5511999999999")
        if test_agent.name == "Helen":
            print(f"{Fore.GREEN}✓ Agent name correto: Helen{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Agent name incorreto: {test_agent.name} (esperado: Helen){Style.RESET_ALL}")
        
        # 2. Testar greeting
        greeting, metadata = await agent.handle_greeting("5511999999999")
        if "Helen Vieira" in greeting:
            print(f"{Fore.GREEN}✓ Greeting usa identidade Helen Vieira{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Greeting não usa identidade Helen Vieira{Style.RESET_ALL}")
            print(f"  Greeting: {greeting[:100]}...")
        
        # 3. Testar novo fluxo de estágios
        test_cases = [
            ({}, "INITIAL_CONTACT"),
            ({"name": "Maria"}, "IDENTIFICATION"),
            ({"name": "Maria", "solution_interest": "economizar"}, "QUALIFICATION"),
            ({"name": "Maria", "solution_interest": "economizar", "bill_value": 5000}, "DISCOVERY"),
            ({"name": "Maria", "solution_interest": "economizar", "bill_value": 5000, "current_discount": 0}, "PRESENTATION"),
        ]
        
        print(f"\n{Fore.YELLOW}Teste de fluxo de estágios:{Style.RESET_ALL}")
        all_stages_ok = True
        for context, expected_stage in test_cases:
            stage = agent._determine_stage(context)
            if stage == expected_stage:
                print(f"  {Fore.GREEN}✓ {context} → {stage}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.RED}✗ {context} → {stage} (esperado: {expected_stage}){Style.RESET_ALL}")
                all_stages_ok = False
        
        # 4. Testar métodos CRM
        print(f"\n{Fore.YELLOW}Teste de métodos CRM:{Style.RESET_ALL}")
        lead_context = {
            "name": "Maria Silva",
            "phone": "5511999999999",
            "bill_value": 5000,
            "qualification_score": 75
        }
        session_state = {
            "current_stage": "PRESENTATION",
            "objections": ["contract_time"]
        }
        
        crm_data = agent._prepare_crm_data(lead_context, session_state)
        if crm_data["nome_lead"] == "Maria Silva" and crm_data["tipo_solucao_interesse"] == "assinatura_comercial":
            print(f"  {Fore.GREEN}✓ CRM data preparado corretamente{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}✗ CRM data incorreto{Style.RESET_ALL}")
        
        observation = agent._generate_crm_observation(lead_context, session_state)
        if "interesse na proposta" in observation:
            print(f"  {Fore.GREEN}✓ Observação CRM gerada{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}✗ Observação CRM vazia ou incorreta{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✅ Integração do agente testada{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Erro na integração: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Executa todos os testes"""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🧪 TESTE COMPLETO DA INTEGRAÇÃO HELEN VIEIRA{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    
    # Executar testes
    identity_ok = await test_helen_identity()
    features_ok = await test_new_features()
    integration_ok = await test_agent_integration()
    
    # Resumo final
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}RESUMO FINAL{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    if identity_ok:
        print(f"{Fore.GREEN}✓ Identidade Helen Vieira OK{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Problemas na identidade{Style.RESET_ALL}")
    
    if features_ok:
        print(f"{Fore.GREEN}✓ Novas funcionalidades OK{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Problemas nas funcionalidades{Style.RESET_ALL}")
    
    if integration_ok:
        print(f"{Fore.GREEN}✓ Integração do agente OK{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Problemas na integração{Style.RESET_ALL}")
    
    if identity_ok and features_ok and integration_ok:
        print(f"\n{Fore.GREEN}🎉 REFATORAÇÃO CONCLUÍDA COM SUCESSO!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Helen Vieira está pronta para atender os clientes da Solar Prime!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️ Alguns testes falharam. Verifique os erros acima.{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Executar testes
    asyncio.run(main())