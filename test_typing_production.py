#!/usr/bin/env python3
"""
TESTE DE PRODUÇÃO - Sistema de Typing
Validação dos pontos críticos para deploy
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n🚀 TESTE DE PRODUÇÃO - SISTEMA DE TYPING\n")

# 1. CONFIGURAÇÕES CRÍTICAS
print("1️⃣ CONFIGURAÇÕES CRÍTICAS:")
from app.config import settings

configs_ok = True
if settings.enable_typing_simulation:
    print("   ✅ enable_typing_simulation = True")
else:
    print("   ❌ enable_typing_simulation = False (ERRO!)")
    configs_ok = False

if not settings.simulate_reading_time:
    print("   ✅ simulate_reading_time = False")
else:
    print("   ❌ simulate_reading_time = True (ERRO!)")
    configs_ok = False

print(f"   {'✅' if configs_ok else '❌'} Configurações {'OK' if configs_ok else 'COM PROBLEMA'}\n")

# 2. TYPING CONTROLLER
print("2️⃣ TYPING CONTROLLER:")
from app.services.typing_controller import typing_controller, TypingContext

# Teste crítico 1: Usuário envia mensagem
user_decision = typing_controller.should_show_typing(TypingContext.USER_MESSAGE, 100)
user_ok = not user_decision.should_show
print(f"   {'✅' if user_ok else '❌'} Usuário envia mensagem → typing = {user_decision.should_show}")

# Teste crítico 2: Agente responde
agent_decision = typing_controller.should_show_typing(TypingContext.AGENT_RESPONSE, 100)
agent_ok = agent_decision.should_show
print(f"   {'✅' if agent_ok else '❌'} Agente responde → typing = {agent_decision.should_show}")

controller_ok = user_ok and agent_ok
print(f"   {'✅' if controller_ok else '❌'} Controller {'OK' if controller_ok else 'COM PROBLEMA'}\n")

# 3. WEBHOOK
print("3️⃣ WEBHOOK:")
with open("app/api/webhooks.py", "r") as f:
    webhook_content = f.read()

webhook_ok = True
if "simulate_reading_time" in webhook_content and "REMOVIDO" not in webhook_content:
    print("   ❌ Webhook ainda tem código de simulate_reading_time ativo")
    webhook_ok = False
else:
    print("   ✅ Webhook sem simulate_reading_time ativo")

print(f"   {'✅' if webhook_ok else '❌'} Webhook {'OK' if webhook_ok else 'COM PROBLEMA'}\n")

# 4. RESULTADO FINAL
all_ok = configs_ok and controller_ok and webhook_ok

print("="*50)
if all_ok:
    print("✅ SISTEMA APROVADO PARA PRODUÇÃO!")
    print("\nRESUMO:")
    print("• Typing NÃO aparece quando usuário envia mensagem ✅")
    print("• Typing APARECE quando agente responde ✅")
    print("• Configurações corretas ✅")
    print("• Webhook corrigido ✅")
    print("\n🚀 Deploy autorizado!")
else:
    print("❌ SISTEMA NÃO ESTÁ PRONTO PARA PRODUÇÃO")
    print("\nPROBLEMAS ENCONTRADOS:")
    if not configs_ok:
        print("• Configurações incorretas")
    if not controller_ok:
        print("• TypingController com problema")
    if not webhook_ok:
        print("• Webhook precisa correção")
    print("\n⚠️  Corrija os problemas antes do deploy!")

print("="*50)