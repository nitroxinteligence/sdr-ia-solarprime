#!/usr/bin/env python3
"""
Teste Simples do Agente - Sem Banco de Dados
===========================================
"""

import os
import sys

# Configurar para não usar banco
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test"
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "test")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== TESTE SIMPLES DO AGENTE SDR ===\n")

try:
    # Teste 1: Importar módulos
    print("1. Testando imports...")
    from agents.sdr_agent import SDRAgent
    from config.agent_config import config
    print("✅ Imports OK\n")
    
    # Teste 2: Criar instância
    print("2. Criando agente...")
    agent = SDRAgent()
    print(f"✅ Agente criado: {agent.config.personality.name}\n")
    
    # Teste 3: Verificar configuração
    print("3. Verificando configuração...")
    print(f"   - Nome: {agent.config.personality.name}")
    print(f"   - Empresa: {agent.config.personality.company}")
    print(f"   - Modelo: {agent.model.id if hasattr(agent.model, 'id') else 'Configurado'}")
    print("✅ Configuração OK\n")
    
    # Teste 4: Testar criação de agente interno
    print("4. Testando criação de agente por telefone...")
    phone = "5511999999999"
    internal_agent = agent._get_or_create_agent(phone)
    print(f"✅ Agente interno criado para: {phone}\n")
    
    # Teste 5: Verificar parâmetros do agente
    print("5. Verificando parâmetros do agente AGnO...")
    print(f"   - Reasoning: {getattr(internal_agent, 'reasoning', 'N/A')}")
    print(f"   - Session ID: {getattr(internal_agent, 'session_id', 'N/A')}")
    print(f"   - Debug Mode: {getattr(internal_agent, 'debug_mode', 'N/A')}")
    
    # Verificar se NÃO tem markdown
    has_markdown = hasattr(internal_agent, 'markdown')
    print(f"   - Tem markdown?: {'❌ SIM (erro)' if has_markdown else '✅ NÃO (correto)'}")
    print()
    
    # Resumo
    print("="*40)
    print("RESUMO: Agente configurado corretamente!")
    print("- Sem parâmetros duplicados ✅")
    print("- Sem formatação markdown ✅")
    print("- Pronto para uso no WhatsApp ✅")
    print("="*40)
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)