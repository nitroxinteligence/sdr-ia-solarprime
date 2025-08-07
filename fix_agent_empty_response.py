#!/usr/bin/env python3
"""
Correção para problema de resposta vazia do agente AGNO

PROBLEMA: Agent.arun() retorna RunResponse mas código não extrai conteúdo corretamente
SOLUÇÃO: Adicionar debug e corrigir extração do conteúdo

ZERO COMPLEXIDADE - O SIMPLES FUNCIONA
"""

import os
from datetime import datetime

def fix_agent_empty_response():
    """Corrige problema de resposta vazia do agente"""
    
    file_path = "app/agents/agentic_sdr.py"
    
    print("🔧 CORREÇÃO - Resposta Vazia do Agente")
    print("=" * 60)
    
    # Backup
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(file_path):
        os.system(f"cp {file_path} {backup_path}")
        print(f"✅ Backup criado: {backup_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correção 1: Melhorar extração de conteúdo do RunResponse
    old_extraction = '''                    # Extrair conteúdo da resposta
                    if hasattr(result, 'content') and result.content is not None:
                        raw_response = result.content
                    elif hasattr(result, 'text') and result.text is not None:
                        raw_response = result.text
                    elif hasattr(result, 'message') and result.message is not None:
                        raw_response = result.message
                    elif isinstance(result, dict):
                        raw_response = result.get('content') or result.get('text') or result.get('message') or str(result)
                    else:
                        raw_response = str(result)'''
    
    new_extraction = '''                    # Extrair conteúdo da resposta - CORREÇÃO PARA AGNO RunResponse
                    if hasattr(result, 'content') and result.content is not None:
                        raw_response = result.content
                    elif hasattr(result, 'text') and result.text is not None:
                        raw_response = result.text
                    elif hasattr(result, 'message') and result.message is not None:
                        raw_response = result.message
                    elif hasattr(result, 'messages') and result.messages:
                        # NOVO: AGNO RunResponse pode ter messages ao invés de content
                        # Pegar última mensagem do assistant
                        for msg in reversed(result.messages):
                            if hasattr(msg, 'role') and msg.role == 'assistant' and hasattr(msg, 'content'):
                                raw_response = msg.content
                                emoji_logger.system_info(f"✅ Conteúdo extraído de result.messages")
                                break
                        else:
                            # Se não encontrou mensagem do assistant, pegar última mensagem
                            if result.messages:
                                last_msg = result.messages[-1]
                                raw_response = getattr(last_msg, 'content', str(last_msg))
                    elif isinstance(result, dict):
                        raw_response = result.get('content') or result.get('text') or result.get('message') or str(result)
                    else:
                        # Debug detalhado se nada funcionou
                        emoji_logger.system_error("Response Extraction", f"Tipo não reconhecido: {type(result)}")
                        if hasattr(result, '__dict__'):
                            emoji_logger.system_error("Response Extraction", f"Atributos: {list(result.__dict__.keys())}")
                        raw_response = str(result)'''
    
    content = content.replace(old_extraction, new_extraction)
    
    # Correção 2: Adicionar mais debug antes de chamar arun
    old_arun_call = '''                            else:
                                # Criar task para poder cancelar se necessário
                                agent_task = asyncio.create_task(self.agent.arun(contextual_prompt))'''
    
    new_arun_call = '''                            else:
                                # Debug: Verificar estado do agent antes de chamar
                                emoji_logger.system_info(f"📊 Agent state antes de arun:")
                                emoji_logger.system_info(f"  • Model: {type(self.agent.model).__name__ if self.agent.model else 'None'}")
                                emoji_logger.system_info(f"  • Memory: {type(self.agent.memory).__name__ if self.agent.memory else 'None'}")
                                emoji_logger.system_info(f"  • Instructions length: {len(self.agent.instructions) if self.agent.instructions else 0}")
                                
                                # Criar task para poder cancelar se necessário
                                agent_task = asyncio.create_task(self.agent.arun(contextual_prompt))'''
    
    content = content.replace(old_arun_call, new_arun_call)
    
    # Correção 3: Remover simulate_reading_time conforme análise
    # Procurar e remover bloco de simulação
    simulate_pattern = '''            # SIMULAÇÃO DE LEITURA: Enviar typing proporcional ao tamanho da mensagem
            if self.settings.simulate_reading_time:
                try:
                    # Calcular tempo de leitura (200 palavras por minuto)
                    words = len(message.split())
                    reading_time = max(2, min(words / 200 * 60, 8))  # Entre 2 e 8 segundos
                    
                    emoji_logger.system_info(f"📖 Simulando leitura por {reading_time:.1f}s ({words} palavras)")
                    
                    # Enviar typing com contexto "agent_response" para simular que está preparando resposta
                    await evolution_client.send_typing(
                        phone, 
                        duration_seconds=reading_time,
                        context="agent_response"  # Contexto que permite typing
                    )
                    
                    # Aguardar para simular leitura
                    await asyncio.sleep(reading_time)
                    
                except Exception as typing_error:
                    emoji_logger.system_warning(f"Erro na simulação de leitura: {typing_error}")
                    # Continua sem simulação'''
    
    if simulate_pattern in content:
        content = content.replace(simulate_pattern, 
            '''            # REMOVIDO: Simulação de leitura causava typing indevido
            # O typing agora é controlado apenas pelo TypingController''')
        print("✅ Removido bloco de simulate_reading_time")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Correções aplicadas em {file_path}")
    print("\n📋 Mudanças implementadas:")
    print("   1. Melhorada extração de conteúdo do RunResponse")
    print("   2. Adicionado suporte para result.messages")
    print("   3. Debug detalhado do estado do agent")
    print("   4. Removido simulate_reading_time que causava typing indevido")
    
    return True

if __name__ == "__main__":
    if fix_agent_empty_response():
        print("\n🚀 Próximos passos:")
        print("   1. Reinicie o servidor: docker-compose restart")
        print("   2. Monitore os logs para ver debug do agent")
        print("   3. Verifique se resposta está sendo extraída corretamente")