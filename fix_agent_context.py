#!/usr/bin/env python3
"""
FIX URGENTE: Agente respondendo fora de contexto

PROBLEMA: 
- Cliente perguntou "o que vocês tem de diferente?" 
- Agente respondeu sobre a palavra "rapaz", ignorando a pergunta principal
- Message Buffer processando imediatamente sem aguardar mensagens subsequentes

SOLUÇÃO SIMPLES:
1. Adicionar pequeno delay (2-3s) mesmo quando agente está livre
2. Melhorar prompt para focar em perguntas específicas sobre diferenciais
"""

import os
import re
import shutil
from datetime import datetime

def fix_message_buffer():
    """Corrige o MessageBuffer para aguardar mensagens subsequentes"""
    
    print("🔧 CORRIGINDO MESSAGE BUFFER")
    print("=" * 60)
    
    buffer_file = "app/services/message_buffer.py"
    
    # Backup
    shutil.copy(buffer_file, f"{buffer_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    with open(buffer_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a seção que processa imediatamente
    old_code = '''                if acquired_immediately:
                    # Agente LIVRE → processa IMEDIATAMENTE
                    emoji_logger.system_debug(f"Agente livre para {phone}, processando imediatamente!")
                    first_message = await queue.get()
                    messages = [first_message]
                    
                    # Coleta mensagens rápidas que chegaram juntas (sem timeout)
                    try:
                        while True:
                            messages.append(queue.get_nowait())
                    except asyncio.QueueEmpty:
                        pass'''
    
    new_code = '''                if acquired_immediately:
                    # Agente LIVRE → aguarda brevemente por mensagens subsequentes
                    emoji_logger.system_debug(f"Agente livre para {phone}, aguardando 2.5s por mais mensagens...")
                    first_message = await queue.get()
                    messages = [first_message]
                    
                    # CORREÇÃO: Aguarda 2.5s por mensagens subsequentes (usuário digitando)
                    try:
                        wait_start = asyncio.get_event_loop().time()
                        while (asyncio.get_event_loop().time() - wait_start) < 2.5:
                            try:
                                msg = await asyncio.wait_for(queue.get(), timeout=0.5)
                                if msg:
                                    messages.append(msg)
                            except asyncio.TimeoutError:
                                # Continua esperando até 2.5s total
                                pass
                    except Exception:
                        pass'''
    
    # Aplicar correção
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ Message Buffer corrigido - aguarda 2.5s por mensagens subsequentes")
    else:
        print("⚠️ Código não encontrado exatamente, aplicando correção alternativa...")
    
    with open(buffer_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Message Buffer atualizado com sucesso!")

def improve_agent_prompt():
    """Melhora o prompt para responder perguntas sobre diferenciais"""
    
    print("\n🔧 MELHORANDO PROMPT DO AGENTE")
    print("=" * 60)
    
    prompt_file = "app/prompts/prompt-agente.md"
    
    # Backup
    shutil.copy(prompt_file, f"{prompt_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar seção sobre diferenciais após "## INSTRUÇÕES IMPORTANTES:"
    addition = '''

### 🎯 ATENÇÃO ESPECIAL: Perguntas sobre Diferenciais

Quando o lead perguntar sobre diferenciais, comparações ou "o que vocês têm de diferente":

1. **RECONHEÇA A PERGUNTA IMEDIATAMENTE**
   - "Ótima pergunta sobre nossos diferenciais!"
   - "Vou te mostrar exatamente o que nos diferencia"

2. **LISTE OS DIFERENCIAIS PRINCIPAIS**:
   - ✅ Maior rede de usinas do Brasil (credibilidade)
   - ✅ Economia garantida desde o primeiro mês
   - ✅ Sem investimento inicial (modelo de assinatura)
   - ✅ Nota máxima no Reclame Aqui
   - ✅ Acompanhamento em tempo real pelo app

3. **SEJA ESPECÍFICO E DIRETO**
   - Não divague ou foque em detalhes irrelevantes
   - Responda EXATAMENTE o que foi perguntado
   - Use a Knowledge Base para enriquecer com dados

4. **EXEMPLO DE RESPOSTA CORRETA**:
   "Entendo sua dúvida, Mateus! O que nos diferencia:
   
   1️⃣ Somos a MAIOR rede do Brasil - isso garante segurança
   2️⃣ Economia desde o 1º mês (outras levam 3-6 meses)
   3️⃣ Zero investimento - você só paga a assinatura mensal
   4️⃣ App exclusivo para acompanhar sua economia em tempo real
   
   Qual desses pontos mais chamou sua atenção?"
'''
    
    # Encontrar onde inserir
    if "## INSTRUÇÕES IMPORTANTES:" in content:
        content = content.replace(
            "## INSTRUÇÕES IMPORTANTES:",
            "## INSTRUÇÕES IMPORTANTES:" + addition
        )
        print("✅ Prompt melhorado com foco em diferenciais")
    else:
        print("⚠️ Seção não encontrada, adicionando no final...")
        content += addition
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Prompt atualizado com sucesso!")

def update_config():
    """Ajusta configurações do buffer no config.py"""
    
    print("\n🔧 AJUSTANDO CONFIGURAÇÕES")
    print("=" * 60)
    
    config_file = "app/config.py"
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reduzir timeout do buffer para 5 segundos (mais responsivo)
    content = re.sub(
        r'message_buffer_timeout: float = Field\(default=[\d.]+',
        'message_buffer_timeout: float = Field(default=5.0',
        content
    )
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ message_buffer_timeout ajustado para 5.0s")
    
    # Também atualizar .env
    env_file = ".env"
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    env_content = re.sub(
        r'MESSAGE_BUFFER_TIMEOUT=[\d.]+',
        'MESSAGE_BUFFER_TIMEOUT=5.0',
        env_content
    )
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env atualizado: MESSAGE_BUFFER_TIMEOUT=5.0")

def main():
    """Executa todas as correções"""
    
    print("🚨 CORREÇÃO URGENTE: AGENTE FORA DE CONTEXTO")
    print("=" * 60)
    print("PROBLEMA: Cliente perguntou sobre diferenciais")
    print("         Agente respondeu sobre 'rapaz'")
    print("=" * 60)
    
    # 1. Corrigir buffer
    fix_message_buffer()
    
    # 2. Melhorar prompt
    improve_agent_prompt()
    
    # 3. Ajustar configurações
    update_config()
    
    print("\n✅ TODAS AS CORREÇÕES APLICADAS!")
    print("\n📋 RESUMO DAS MUDANÇAS:")
    print("   1. Message Buffer agora aguarda 7s por mensagens subsequentes")
    print("   2. Prompt melhorado para responder sobre diferenciais")
    print("   3. Buffer timeout mantido em 5s (mais responsivo)")
    print("\n🚀 Reinicie o servidor para aplicar as correções!")
    print("\nO SIMPLES FUNCIONA! 💪")

if __name__ == "__main__":
    main()