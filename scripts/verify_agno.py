#!/usr/bin/env python3
"""
Verificação da Instalação do AGnO
=================================
Verifica se o AGnO está instalado corretamente
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔍 Verificando instalação do AGnO Framework...\n")

# Testa imports básicos
try:
    import agno
    print("✅ Módulo agno importado")
except ImportError as e:
    print(f"❌ Erro ao importar agno: {e}")
    sys.exit(1)

# Testa imports específicos
try:
    from agno.agent import Agent, AgentMemory, AgentSession
    print("✅ Classes Agent, AgentMemory, AgentSession importadas")
except ImportError as e:
    print(f"❌ Erro ao importar classes do agent: {e}")
    sys.exit(1)

try:
    from agno.models.google import Gemini
    print("✅ Modelo Gemini importado")
except ImportError as e:
    print(f"❌ Erro ao importar Gemini: {e}")
    sys.exit(1)

# Testa imports locais
try:
    from config.agent_config import config
    print("✅ Configurações carregadas")
    print(f"   - Agente: {config.personality.name}")
    print(f"   - Empresa: {config.personality.company}")
except Exception as e:
    print(f"❌ Erro ao carregar configurações: {e}")
    sys.exit(1)

try:
    from agents.sdr_agent import SDRAgent
    print("✅ Classe SDRAgent importada")
except ImportError as e:
    print(f"❌ Erro ao importar SDRAgent: {e}")
    sys.exit(1)

print("\n🎉 VERIFICAÇÃO COMPLETA!")
print("\nPróximos passos:")
print("1. Configure sua GEMINI_API_KEY no arquivo .env")
print("2. Execute: python scripts/test_agent.py")
print("\n💡 Para obter uma API key:")
print("   https://makersuite.google.com/app/apikey")