#!/usr/bin/env python3
"""
Teste de Estrutura - Sem API Key
================================
Testa a estrutura do agente sem fazer chamadas à API
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.agent_config import config
from config.prompts import PromptTemplates

print("🏗️ Teste de Estrutura do SDR SolarPrime\n")

# Testa configurações
print("📋 Configurações:")
print(f"   Agente: {config.personality.name}")
print(f"   Empresa: {config.personality.company}")
print(f"   Modelo: {config.gemini.model}")
print(f"   Personalidade: {config.personality.voice_tone}")
print(f"   Características: {', '.join(config.personality.traits[:3])}...")

# Testa prompts
print("\n📝 Sistema de Prompts:")
system_prompt = PromptTemplates.format_system_prompt()
print(f"   System Prompt: {len(system_prompt)} caracteres")
print(f"   Estágios definidos: {len(PromptTemplates.STAGE_PROMPTS)}")

# Testa estágios
print("\n🎯 Estágios de Vendas:")
for stage, description in config.sales_stages.stages.items():
    print(f"   - {stage}: {description}")

# Testa soluções
print("\n☀️ Soluções Oferecidas:")
for solution_id, solution in config.solutions.solutions.items():
    print(f"   - {solution['name']}: {solution['benefits']}")

# Mensagens padrão
print("\n💬 Mensagens Padrão Configuradas:")
for msg_type in config.default_messages.keys():
    print(f"   - {msg_type}")

print("\n✅ ESTRUTURA VALIDADA COM SUCESSO!")
print("\n🚀 Próximo passo:")
print("   1. Configure sua GEMINI_API_KEY no arquivo .env")
print("   2. Execute: python scripts/test_agent.py")
print("\n📖 Documentação completa em: docs/AGNO_FRAMEWORK_GUIDE.md")