#!/usr/bin/env python3
"""
Verificar parâmetros corretos do Team no AGNO v1.7.6
"""

import inspect
from agno.team import Team
from agno.agent import Agent

print("=" * 50)
print("AGNO Team Class Parameters Check")
print("=" * 50)

# Verificar parâmetros do Team
print("\n1. Team.__init__ signature:")
sig = inspect.signature(Team.__init__)
for param_name, param in sig.parameters.items():
    if param_name != 'self':
        default = param.default
        if default == inspect.Parameter.empty:
            default = "required"
        print(f"  - {param_name}: {default}")

print("\n2. Agent.__init__ signature:")
sig = inspect.signature(Agent.__init__)
for param_name, param in sig.parameters.items():
    if param_name != 'self':
        default = param.default
        if default == inspect.Parameter.empty:
            default = "required"
        print(f"  - {param_name}: {default}")

# Testar criação do Team
print("\n3. Testing Team creation...")
from agno.models.google import Gemini
from app.config import settings

try:
    # Criar modelo
    model = Gemini(
        id="gemini-2.0-flash-exp",
        api_key=settings.google_api_key or "test-key"
    )
    
    # Criar agente simples
    agent = Agent(
        name="Test Agent",
        model=model,
        instructions="Test instructions"  # NOT role
    )
    
    # Criar team
    team = Team(
        name="Test Team",
        members=[agent],
        mode="coordinate",
        model=model,
        description="Test description",  # NOT role
        instructions="Test team instructions",
        markdown=True
    )
    
    print("✅ Team created successfully!")
    print(f"   Team name: {team.name}")
    print(f"   Members: {len(team.members)}")
    
except Exception as e:
    print(f"❌ Error creating team: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)