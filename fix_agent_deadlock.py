#!/usr/bin/env python3
"""
Fix para resolver o travamento do agente após agent.arun()

Problemas identificados:
1. Singleton do agente causando problemas de concorrência
2. Falta de timeout no agent.arun()
3. Possível deadlock em operações assíncronas

Soluções implementadas:
1. Remover singleton e criar nova instância por requisição
2. Adicionar timeout ao agent.arun()
3. Melhorar tratamento de erros e logging
"""

import asyncio
from typing import Optional, Dict, Any

# Patch 1: Modificar webhooks.py para remover singleton
WEBHOOKS_PATCH = '''
# REMOVIDO: Cache global do agente - causava deadlock
# _cached_agent = None
# _agent_lock = asyncio.Lock()

async def get_agentic_agent():
    """Cria NOVA instância do agente para cada requisição (evita deadlock)"""
    # SEMPRE criar nova instância - evita problemas de estado compartilhado
    emoji_logger.webhook_process("🚀 Criando nova instância do AgenticSDR...")
    agent = await create_agentic_sdr()
    emoji_logger.system_ready("✅ Nova instância do AgenticSDR criada!")
    return agent
'''

# Patch 2: Adicionar timeout ao agent.arun() no agentic_sdr.py
AGENTIC_SDR_PATCH = '''
# Adicionar timeout de 30 segundos para evitar travamento
AGENT_TIMEOUT = 30  # segundos

# No método process_message, substituir as chamadas agent.arun por:

try:
    # Adicionar timeout para evitar travamento
    emoji_logger.system_info(f"🚀 Chamando agent.arun com timeout de {AGENT_TIMEOUT}s...")
    
    result = await asyncio.wait_for(
        self.agent.arun(contextual_prompt),
        timeout=AGENT_TIMEOUT
    )
    
    emoji_logger.system_info("✅ agent.arun completou com sucesso")
    
except asyncio.TimeoutError:
    emoji_logger.system_error(f"❌ Timeout em agent.arun após {AGENT_TIMEOUT}s")
    # Tentar fallback com modelo mais simples
    try:
        emoji_logger.system_info("🔄 Tentando fallback com resposta simples...")
        result = self._generate_fallback_response(message, lead_data)
    except Exception as fallback_error:
        emoji_logger.system_error(f"❌ Falha no fallback: {str(fallback_error)}")
        result = None
        
except Exception as arun_error:
    emoji_logger.system_error(f"❌ Erro em agent.arun: {str(arun_error)}")
    # Log detalhado do erro
    import traceback
    emoji_logger.system_error(f"Stack trace: {traceback.format_exc()}")
    result = None
'''

# Patch 3: Adicionar método de fallback
FALLBACK_METHOD = '''
def _generate_fallback_response(self, message: str, lead_data: Dict[str, Any]) -> str:
    """Gera resposta simples de fallback quando agent.arun falha"""
    
    # Respostas contextuais baseadas em palavras-chave
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
        return "Oi! Vi sua mensagem sobre energia solar. Você gostaria de saber quanto pode economizar na sua conta de luz?"
    
    elif any(word in message_lower for word in ['quanto', 'valor', 'preço', 'preco', 'custa']):
        return "Para calcular sua economia, preciso saber: qual o valor médio da sua conta de luz?"
    
    elif any(word in message_lower for word in ['economia', 'economizar', 'desconto']):
        return "Com energia solar você pode economizar até 95% na conta de luz! Qual o valor da sua conta atual?"
    
    elif any(word in message_lower for word in ['sim', 'quero', 'tenho interesse']):
        return "Ótimo! Para fazer uma proposta personalizada, me diz: quanto você paga de luz por mês?"
    
    else:
        # Resposta genérica
        return "Entendi! Para te ajudar melhor com energia solar, qual o valor da sua conta de luz?"
'''

# Patch 4: Melhorar logging e debugging
DEBUG_PATCH = '''
# Adicionar mais logging detalhado antes de chamar agent.arun

# Log do estado do agente
emoji_logger.system_info("📊 Estado do agente antes de chamar arun:")
emoji_logger.system_info(f"  - Model: {type(self.agent.model).__name__ if self.agent.model else 'None'}")
emoji_logger.system_info(f"  - Memory: {type(self.agent.memory).__name__ if self.agent.memory else 'None'}")
emoji_logger.system_info(f"  - Storage: {type(self.agent.storage).__name__ if self.agent.storage else 'None'}")
emoji_logger.system_info(f"  - Tools: {len(self.agent.tools) if self.agent.tools else 0} ferramentas")
emoji_logger.system_info(f"  - Instructions length: {len(self.agent.instructions) if self.agent.instructions else 0}")

# Log do prompt
emoji_logger.system_info(f"📝 Prompt enviado (primeiros 200 chars): {contextual_prompt[:200]}...")
emoji_logger.system_info(f"📝 Prompt length: {len(contextual_prompt)}")
'''

# Script para aplicar os patches
def main():
    print("🔧 Fix para resolver travamento do agente")
    print("\n📋 Patches a serem aplicados:")
    print("\n1. REMOVER SINGLETON:")
    print("   - Modificar get_agentic_agent() em webhooks.py")
    print("   - Sempre criar nova instância ao invés de reutilizar")
    
    print("\n2. ADICIONAR TIMEOUT:")
    print("   - Adicionar asyncio.wait_for() com timeout de 30s")
    print("   - Implementar fallback quando timeout ocorrer")
    
    print("\n3. MELHORAR DEBUGGING:")
    print("   - Adicionar mais logs antes de chamar agent.arun()")
    print("   - Log detalhado do estado do agente")
    
    print("\n4. IMPLEMENTAR FALLBACK:")
    print("   - Respostas simples quando agent.arun falha")
    print("   - Baseado em palavras-chave da mensagem")
    
    print("\n⚠️  IMPORTANTE:")
    print("   - Fazer backup dos arquivos antes de aplicar")
    print("   - Testar em ambiente de desenvolvimento primeiro")
    print("   - Monitorar logs após aplicar as mudanças")
    
    print("\n📝 Arquivos a modificar:")
    print("   1. app/api/webhooks.py")
    print("   2. app/agents/agentic_sdr.py")

if __name__ == "__main__":
    main()