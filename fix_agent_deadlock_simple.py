#!/usr/bin/env python3
"""
Correção SIMPLES para resolver travamento do agente

PROBLEMA: Agent trava após "Agent tem model? True" na linha 2925 de agentic_sdr.py
SOLUÇÃO: Adicionar proteção extra contra travamento no agent.arun()
"""

import os
import shutil
from datetime import datetime

def apply_fix():
    """Aplica correção simples no arquivo agentic_sdr.py"""
    
    file_path = "app/agents/agentic_sdr.py"
    backup_path = f"app/agents/agentic_sdr.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🔧 Aplicando correção simples para travamento do agente")
    print(f"📁 Arquivo: {file_path}")
    
    # Fazer backup
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
    else:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correção 1: Adicionar proteção extra no agent.arun
    old_code1 = """                        try:
                            emoji_logger.system_info(f"🚀 Chamando agent.arun com timeout de {AGENT_TIMEOUT}s...")
                            result = await asyncio.wait_for(
                                self.agent.arun(contextual_prompt),
                                timeout=AGENT_TIMEOUT
                            )
                            emoji_logger.system_info("✅ agent.arun completou com sucesso")"""
    
    new_code1 = """                        try:
                            emoji_logger.system_info(f"🚀 Chamando agent.arun com timeout de {AGENT_TIMEOUT}s...")
                            
                            # PROTEÇÃO EXTRA: Verificar se agent está pronto
                            if not self.agent or not hasattr(self.agent, 'arun'):
                                emoji_logger.system_error("❌ Agent não está pronto ou não tem método arun")
                                result = self._generate_simple_fallback_response(message)
                            else:
                                # Criar task para poder cancelar se necessário
                                agent_task = asyncio.create_task(self.agent.arun(contextual_prompt))
                                
                                try:
                                    result = await asyncio.wait_for(agent_task, timeout=AGENT_TIMEOUT)
                                    emoji_logger.system_info("✅ agent.arun completou com sucesso")
                                except asyncio.TimeoutError:
                                    # Cancelar task se ainda estiver rodando
                                    agent_task.cancel()
                                    try:
                                        await agent_task
                                    except asyncio.CancelledError:
                                        pass
                                    raise"""
    
    if old_code1 in content:
        content = content.replace(old_code1, new_code1)
        print("✅ Correção 1 aplicada: Proteção extra no agent.arun")
    else:
        print("⚠️  Correção 1: Código não encontrado exatamente como esperado")
    
    # Correção 2: Melhorar o método _generate_simple_fallback_response
    old_fallback = """    def _generate_simple_fallback_response(self, message: str) -> str:
        \"\"\"Gera resposta simples de fallback quando agent.arun falha ou dá timeout\"\"\"
        
        # Respostas contextuais baseadas em palavras-chave
        message_lower = message.lower()"""
    
    new_fallback = """    def _generate_simple_fallback_response(self, message: str) -> str:
        \"\"\"Gera resposta simples de fallback quando agent.arun falha ou dá timeout\"\"\"
        
        emoji_logger.system_info("🔄 Gerando resposta de fallback...")
        
        # Respostas contextuais baseadas em palavras-chave
        message_lower = message.lower()"""
    
    if old_fallback in content:
        content = content.replace(old_fallback, new_fallback)
        print("✅ Correção 2 aplicada: Melhor logging no fallback")
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Correções aplicadas com sucesso!")
    print(f"📝 Mudanças:")
    print(f"   1. Adicionada proteção extra antes de chamar agent.arun()")
    print(f"   2. Criação de task cancelável para evitar travamento")
    print(f"   3. Melhor tratamento de timeout com cancelamento adequado")
    print(f"   4. Fallback automático se agent não estiver pronto")
    
    return True

if __name__ == "__main__":
    if apply_fix():
        print("\n🚀 Próximos passos:")
        print("   1. Reinicie o servidor: docker-compose restart")
        print("   2. Execute o teste: python test_agent_fix.py")
        print("   3. Monitore os logs para verificar se o problema foi resolvido")
    else:
        print("\n❌ Falha ao aplicar correções")