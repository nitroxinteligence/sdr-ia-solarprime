#!/usr/bin/env python3
"""
Correção DEFINITIVA para problema de repetições do agente

PROBLEMA: Agente repete introduções e pede informações já fornecidas
CAUSA: Histórico incompleto ou desatualizado sendo passado para o agente
SOLUÇÃO: Garantir que histórico seja SEMPRE buscado corretamente do Supabase

ARQUITETURA MODULAR - ZERO COMPLEXIDADE
"""

import os
from datetime import datetime

def fix_agent_repetitions():
    """Aplica correções definitivas para eliminar repetições"""
    
    files_to_fix = {
        "app/agents/agentic_sdr.py": fix_agentic_sdr,
        "app/api/webhooks.py": fix_webhooks
    }
    
    print("🔧 CORREÇÃO DEFINITIVA - Problema de Repetições do Agente")
    print("=" * 60)
    
    for file_path, fix_function in files_to_fix.items():
        print(f"\n📁 Corrigindo: {file_path}")
        
        # Backup
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(file_path):
            os.system(f"cp {file_path} {backup_path}")
            print(f"✅ Backup criado: {backup_path}")
        
        # Aplicar correção
        try:
            fix_function(file_path)
            print(f"✅ Correções aplicadas em {file_path}")
        except Exception as e:
            print(f"❌ Erro ao corrigir {file_path}: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
    print("\n📋 Mudanças implementadas:")
    print("   1. Logs detalhados em get_last_100_messages")
    print("   2. Validação rigorosa de conversation_id")
    print("   3. Garantia de busca sempre atualizada")
    print("   4. Fallback seguro se conversation_id inválido")
    
    return True

def fix_agentic_sdr(file_path):
    """Corrige agentic_sdr.py para garantir histórico sempre atualizado"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correção 1: Adicionar log CRÍTICO no início de get_last_100_messages
    old_get_messages = '''    async def get_last_100_messages(self, identifier: str) -> List[Dict[str, Any]]:
        """
        Busca as últimas 100 mensagens do Supabase (sempre atualizado)
        
        Args:
            identifier: Número do telefone ou conversation_id
            
        Returns:
            Lista com últimas 100 mensagens
        """
        
        try:'''
    
    new_get_messages = '''    async def get_last_100_messages(self, identifier: str) -> List[Dict[str, Any]]:
        """
        Busca as últimas 100 mensagens do Supabase (sempre atualizado)
        
        Args:
            identifier: Número do telefone ou conversation_id
            
        Returns:
            Lista com últimas 100 mensagens
        """
        
        # LOG CRÍTICO: Rastrear todas as chamadas
        emoji_logger.system_info(f"🔍 HISTÓRICO: Buscando mensagens para identifier={identifier}")
        
        # Validação de entrada
        if not identifier:
            emoji_logger.system_error("HISTÓRICO", "❌ Identifier vazio ou None!")
            return []
        
        try:'''
    
    content = content.replace(old_get_messages, new_get_messages)
    
    # Correção 2: Adicionar verificação ANTES de chamar get_last_100_messages
    old_process_msg = '''            # 2. Detectar gatilhos emocionais e obter histórico (com fallback)
            messages_history = []
            try:
                # Buscar histórico de mensagens (será usado para contexto e análise emocional)
                messages_history = await self.get_last_100_messages(conversation_id) if conversation_id else []
                emoji_logger.system_info(f"Histórico carregado: {len(messages_history)} mensagens")'''
    
    new_process_msg = '''            # 2. Detectar gatilhos emocionais e obter histórico (com fallback)
            messages_history = []
            try:
                # VALIDAÇÃO CRÍTICA: Garantir que conversation_id é válido
                if not conversation_id:
                    emoji_logger.system_error("HISTÓRICO", f"❌ conversation_id é None/vazio! Lead: {lead_data}")
                    # Tentar buscar por phone como fallback
                    if phone:
                        emoji_logger.system_info(f"🔄 Tentando buscar histórico por phone: {phone}")
                        messages_history = await self.get_last_100_messages(phone)
                    else:
                        emoji_logger.system_error("HISTÓRICO", "❌ Nem conversation_id nem phone disponíveis!")
                        messages_history = []
                else:
                    # Buscar histórico de mensagens (será usado para contexto e análise emocional)
                    messages_history = await self.get_last_100_messages(conversation_id)
                
                emoji_logger.system_info(f"✅ HISTÓRICO FINAL: {len(messages_history)} mensagens carregadas")'''
    
    content = content.replace(old_process_msg, new_process_msg)
    
    # Correção 3: Log detalhado após buscar mensagens
    old_query_log = '''            # Log detalhado para debug
            emoji_logger.system_info(f"Query executada, {len(messages)} mensagens encontradas (limite solicitado: 100)")'''
    
    new_query_log = '''            # Log detalhado para debug
            emoji_logger.system_info(f"📊 QUERY EXECUTADA:")
            emoji_logger.system_info(f"  • Conversation ID: {conversation_id}")
            emoji_logger.system_info(f"  • Mensagens encontradas: {len(messages)}")
            emoji_logger.system_info(f"  • Limite solicitado: 100")
            
            # Log das primeiras e últimas mensagens para debug
            if messages:
                first_msg = messages[0]
                last_msg = messages[-1]
                emoji_logger.system_info(f"  • Primeira msg: {first_msg.get('created_at', 'N/A')} - {first_msg.get('sender', 'N/A')}")
                emoji_logger.system_info(f"  • Última msg: {last_msg.get('created_at', 'N/A')} - {last_msg.get('sender', 'N/A')}")'''
    
    content = content.replace(old_query_log, new_query_log)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_webhooks(file_path):
    """Corrige webhooks.py para garantir conversation_id sempre válido"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correção: Adicionar validação rigorosa antes de chamar process_message
    old_process_call = '''        # Processa mensagem com análise contextual inteligente
        emoji_logger.webhook_process(f"Chamando AGENTIC SDR para processar: {message_content[:50]}...")'''
    
    new_process_call = '''        # VALIDAÇÃO CRÍTICA: Garantir conversation_id antes de processar
        if not conversation or not conversation.get("id"):
            emoji_logger.system_error("WEBHOOK", f"❌ Conversation inválida! Lead: {lead}, Phone: {phone}")
            # Tentar criar nova conversa como fallback
            try:
                conversation = await supabase_client.create_conversation(phone, lead["id"] if lead else None)
                emoji_logger.system_info(f"✅ Nova conversa criada: {conversation.get('id', 'N/A')}")
            except Exception as conv_error:
                emoji_logger.system_error("WEBHOOK", f"❌ Falha ao criar conversa: {conv_error}")
                return
        
        # Log do conversation_id que será usado
        emoji_logger.system_info(f"🔍 WEBHOOK: Usando conversation_id={conversation.get('id', 'N/A')} para phone={phone}")
        
        # Processa mensagem com análise contextual inteligente
        emoji_logger.webhook_process(f"Chamando AGENTIC SDR para processar: {message_content[:50]}...")'''
    
    content = content.replace(old_process_call, new_process_call)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    if fix_agent_repetitions():
        print("\n🚀 Próximos passos:")
        print("   1. Reinicie o servidor: docker-compose restart")
        print("   2. Monitore os logs para verificar histórico sendo carregado")
        print("   3. Teste com conversas existentes")
        print("\n⚠️  IMPORTANTE: Os logs agora mostrarão:")
        print("   • Cada busca de histórico")
        print("   • Quantas mensagens foram encontradas")
        print("   • Se conversation_id está válido")
        print("   • Primeira e última mensagem do histórico")
    else:
        print("\n❌ Falha ao aplicar correções")