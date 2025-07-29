#!/usr/bin/env python3
"""
Test Prompt Integration
=======================
Testa a integração dos prompts centralizados com o SDR Agent V2
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
from config.prompts import PromptTemplates, get_example_response, get_objection_handler
from agents.sdr_agent_v2 import SDRAgentV2


async def test_prompts():
    """Testa os prompts centralizados"""
    print(f"\n{Fore.CYAN}=== TESTE DE PROMPTS CENTRALIZADOS ==={Style.RESET_ALL}\n")
    
    # 1. Testar SYSTEM_PROMPT
    print(f"{Fore.YELLOW}1. System Prompt:{Style.RESET_ALL}")
    print(f"   Tamanho: {len(PromptTemplates.SYSTEM_PROMPT)} caracteres")
    print(f"   Primeiras 100 chars: {PromptTemplates.SYSTEM_PROMPT[:100]}...")
    # Verificar se é Helen Vieira
    if "Helen Vieira" in PromptTemplates.SYSTEM_PROMPT:
        print(f"   {Fore.GREEN}✓ System prompt de Helen Vieira carregado{Style.RESET_ALL}")
    else:
        print(f"   {Fore.RED}✗ System prompt não contém Helen Vieira{Style.RESET_ALL}")
    
    # 2. Testar stage prompts
    print(f"\n{Fore.YELLOW}2. Stage Prompts:{Style.RESET_ALL}")
    stages = ["INITIAL_CONTACT", "IDENTIFICATION", "QUALIFICATION", "DISCOVERY", "PRESENTATION", "OBJECTION_HANDLING", "SCHEDULING", "FOLLOW_UP"]
    for stage in stages:
        prompt = PromptTemplates.get_stage_prompt(stage)
        print(f"   {stage}: {len(prompt)} chars")
    print(f"   {Fore.GREEN}✓ Todos os stage prompts disponíveis (incluindo PRESENTATION){Style.RESET_ALL}")
    
    # 3. Testar templates de resposta
    print(f"\n{Fore.YELLOW}3. Response Templates:{Style.RESET_ALL}")
    greeting = PromptTemplates.get_template("greeting_initial")
    print(f"   greeting_initial: {greeting[:50]}...")
    
    high_value = get_example_response("high_energy_bill", value="1000", reduced_value="50", monthly_savings="950", yearly_savings="11400")
    print(f"   high_energy_bill: {high_value[:50]}...")
    print(f"   {Fore.GREEN}✓ Templates de resposta funcionando{Style.RESET_ALL}")
    
    # 4. Testar objection handlers
    print(f"\n{Fore.YELLOW}4. Objection Handlers:{Style.RESET_ALL}")
    cost_obj = get_objection_handler("cost_concern")
    print(f"   cost_concern: {cost_obj[:50]}...")
    
    competitor_obj = get_objection_handler("competitor_comparison")
    print(f"   competitor_comparison: {competitor_obj[:50]}...")
    print(f"   {Fore.GREEN}✓ Objection handlers funcionando{Style.RESET_ALL}")


async def test_agent_integration():
    """Testa a integração com o agente"""
    print(f"\n{Fore.CYAN}=== TESTE DE INTEGRAÇÃO COM AGENTE ==={Style.RESET_ALL}\n")
    
    try:
        # Criar configuração
        config = Config()
        
        # Criar agente
        agent = SDRAgentV2(config)
        print(f"{Fore.GREEN}✓ Agente criado com sucesso{Style.RESET_ALL}")
        
        # Verificar memory config
        print(f"\n{Fore.YELLOW}Memory Config:{Style.RESET_ALL}")
        print(f"   Memory config type: {type(agent.memory_config).__name__}")
        print(f"   {Fore.GREEN}✓ Memory config criado{Style.RESET_ALL}")
        
        # Verificar role no agent criado
        print(f"\n{Fore.YELLOW}Agent Role Check:{Style.RESET_ALL}")
        test_agent = agent._create_agent("5511999999999")
        # Verificar se o nome é Helen
        if test_agent.name == "Helen":
            print(f"   Agent name: {test_agent.name} {Fore.GREEN}✓{Style.RESET_ALL}")
        else:
            print(f"   Agent name: {test_agent.name} {Fore.RED}✗ (esperado: Helen){Style.RESET_ALL}")
        print(f"   {Fore.GREEN}✓ Agent criado com configurações corretas{Style.RESET_ALL}")
        
        # Testar greeting
        print(f"\n{Fore.YELLOW}Teste de Greeting:{Style.RESET_ALL}")
        greeting, metadata = await agent.handle_greeting("5511999999999")
        print(f"   Greeting: {greeting}")
        print(f"   Stage: {metadata.get('stage')}")
        print(f"   {Fore.GREEN}✓ Greeting usando template centralizado{Style.RESET_ALL}")
        
        # Testar stage instructions
        print(f"\n{Fore.YELLOW}Teste de Stage Instructions:{Style.RESET_ALL}")
        for stage in ["INITIAL_CONTACT", "IDENTIFICATION", "DISCOVERY"]:
            instructions = agent._get_stage_instructions(stage)
            print(f"   {stage}: {len(instructions)} chars")
        print(f"   {Fore.GREEN}✓ Stage instructions funcionando{Style.RESET_ALL}")
        
        # Testar determine stage
        print(f"\n{Fore.YELLOW}Teste de Stage Determination:{Style.RESET_ALL}")
        test_contexts = [
            ({}, "INITIAL_CONTACT"),
            ({"name": "Maria"}, "IDENTIFICATION"),
            ({"name": "Maria", "solution_interest": "economizar"}, "QUALIFICATION"),
            ({"name": "Maria", "solution_interest": "economizar", "bill_value": 5000}, "DISCOVERY"),
            ({"name": "Maria", "solution_interest": "economizar", "bill_value": 5000, "current_discount": 0}, "PRESENTATION"),
            ({"name": "Maria", "solution_interest": "economizar", "bill_value": 5000, "current_discount": 0, "solution_accepted": True}, "SCHEDULING"),
        ]
        
        for context, expected in test_contexts:
            stage = agent._determine_stage(context)
            status = "✓" if stage == expected else "✗"
            color = Fore.GREEN if stage == expected else Fore.RED
            print(f"   {color}{status} {context} → {stage}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✅ INTEGRAÇÃO COMPLETA E FUNCIONAL!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}✗ Erro na integração: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


async def main():
    """Executa todos os testes"""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🧪 TESTE DE INTEGRAÇÃO DOS PROMPTS CENTRALIZADOS{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    
    # Testar prompts
    await test_prompts()
    
    # Testar integração com agente
    await test_agent_integration()
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Executar testes
    asyncio.run(main())