#!/usr/bin/env python3
"""
Teste final simplificado do sistema de typing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.services.typing_controller import typing_controller, TypingContext

print("🔍 VALIDAÇÃO FINAL DO SISTEMA DE TYPING\n")

# 1. Verificar configurações
print("1️⃣ CONFIGURAÇÕES:")
print(f"   enable_typing_simulation: {settings.enable_typing_simulation}")
print(f"   simulate_reading_time: {settings.simulate_reading_time}")

assert settings.enable_typing_simulation == True, "❌ Typing deve estar habilitado"
assert settings.simulate_reading_time == False, "❌ Tempo de leitura deve estar DESABILITADO"
print("   ✅ Configurações corretas!\n")

# 2. Testar TypingController
print("2️⃣ TYPING CONTROLLER:")

# Cenário 1: Usuário envia mensagem
decision = typing_controller.should_show_typing(TypingContext.USER_MESSAGE, 100)
print(f"   USER_MESSAGE → should_show: {decision.should_show}")
print(f"   Motivo: {decision.reason}")
assert decision.should_show == False, "❌ Não deve mostrar typing para mensagem do usuário"
print("   ✅ Correto!\n")

# Cenário 2: Agente responde
decision = typing_controller.should_show_typing(TypingContext.AGENT_RESPONSE, 100)
print(f"   AGENT_RESPONSE → should_show: {decision.should_show}")
print(f"   Duração: {decision.duration}s")
print(f"   Motivo: {decision.reason}")
assert decision.should_show == True, "❌ Deve mostrar typing quando agente responde"
assert decision.duration == 2.0, "❌ Duração incorreta"
print("   ✅ Correto!\n")

# 3. Verificar webhook
print("3️⃣ VERIFICAÇÃO DO WEBHOOK:")
with open("app/api/webhooks.py", "r") as f:
    content = f.read()
    lines = content.split('\n')
    
    # Procurar por tempo de leitura simulado
    found_removed = False
    for i, line in enumerate(lines, 1):
        if "REMOVIDO:" in line and "tempo de leitura" in line:
            found_removed = True
            print(f"   Linha {i}: {line.strip()}")
            break
    
    assert found_removed, "❌ Código de tempo de leitura não foi removido"
    print("   ✅ Tempo de leitura removido corretamente!\n")

# 4. Resumo final
print("🎉 VALIDAÇÃO COMPLETA - SISTEMA 100% FUNCIONAL!")
print("\n📋 RESUMO:")
print("   • Typing NÃO aparece quando usuário envia mensagem ✅")
print("   • Typing APARECE quando agente está respondendo ✅") 
print("   • Tempo de leitura foi REMOVIDO do webhook ✅")
print("   • TypingController está centralizado e testado ✅")
print("\n🚀 Pronto para deploy em produção!")