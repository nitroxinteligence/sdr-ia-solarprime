#!/usr/bin/env python3
"""
Script para atualizar constraint de media_type no banco de dados
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from services.database import db
from loguru import logger


async def update_media_type_constraint():
    """Atualiza a constraint media_type para incluir 'buffered' e 'text'"""
    
    try:
        logger.info("Iniciando atualização da constraint media_type...")
        
        # NOTA: O Supabase Python Client não suporta DDL (ALTER TABLE) diretamente
        # Você precisa executar estes comandos no Supabase Dashboard SQL Editor
        
        logger.warning("⚠️  ATENÇÃO: O Supabase Python Client não suporta comandos DDL (ALTER TABLE)")
        logger.warning("⚠️  Por favor, execute os seguintes comandos no Supabase Dashboard:")
        logger.warning("")
        logger.warning("1. Acesse seu projeto no Supabase Dashboard")
        logger.warning("2. Vá para SQL Editor")
        logger.warning("3. Execute os seguintes comandos:")
        logger.warning("")
        
        print("-- Remover constraint antiga")
        print("ALTER TABLE messages")
        print("DROP CONSTRAINT IF EXISTS messages_media_type_check;")
        print("")
        print("-- Adicionar nova constraint incluindo 'buffered' e 'text'")
        print("ALTER TABLE messages")
        print("ADD CONSTRAINT messages_media_type_check")
        print("CHECK (media_type IN ('image', 'audio', 'video', 'document', 'buffered', 'text'));")
        print("")
        print("-- Verificar se funcionou")
        print("SELECT")
        print("    conname AS constraint_name,")
        print("    pg_get_constraintdef(oid) AS constraint_definition")
        print("FROM pg_constraint")
        print("WHERE conrelid = 'messages'::regclass")
        print("AND conname = 'messages_media_type_check';")
        print("")
        
        logger.info("Após executar os comandos acima, pressione ENTER para testar...")
        input()
        
        # Testar se a constraint foi atualizada
        logger.info("Testando inserção com tipo 'text'...")
        
        # Primeiro, verificar se existe alguma conversa
        conversations = db.conversations.select("id").limit(1).execute()
        
        if not conversations.data:
            logger.warning("Nenhuma conversa encontrada. Criando conversa de teste...")
            
            # Criar lead de teste primeiro
            lead_result = db.leads.insert({
                "phone_number": "+5511999999999",
                "name": "Teste Constraint"
            }).execute()
            
            if lead_result.data:
                lead_id = lead_result.data[0]['id']
                
                # Criar conversa de teste
                conv_result = db.conversations.insert({
                    "lead_id": lead_id,
                    "session_id": "test_constraint_session"
                }).execute()
                
                if conv_result.data:
                    conversation_id = conv_result.data[0]['id']
                else:
                    logger.error("Erro ao criar conversa de teste")
                    return False
            else:
                logger.error("Erro ao criar lead de teste")
                return False
        else:
            conversation_id = conversations.data[0]['id']
        
        # Testar inserção com tipo 'text'
        try:
            test_result = db.messages.insert({
                "conversation_id": conversation_id,
                "role": "user",
                "content": "Teste de mensagem com tipo text",
                "media_type": "text"
            }).execute()
            
            if test_result.data:
                logger.success("✅ Teste com tipo 'text' bem-sucedido!")
                
                # Limpar mensagem de teste
                db.messages.delete().eq("id", test_result.data[0]['id']).execute()
        except Exception as e:
            logger.error(f"❌ Erro ao testar tipo 'text': {e}")
            return False
        
        # Testar inserção com tipo 'buffered'
        try:
            test_result = db.messages.insert({
                "conversation_id": conversation_id,
                "role": "user",
                "content": "Teste de mensagem bufferizada",
                "media_type": "buffered"
            }).execute()
            
            if test_result.data:
                logger.success("✅ Teste com tipo 'buffered' bem-sucedido!")
                
                # Limpar mensagem de teste
                db.messages.delete().eq("id", test_result.data[0]['id']).execute()
                
                logger.success("✅ Constraint atualizada com sucesso!")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao testar tipo 'buffered': {e}")
            logger.error("A constraint provavelmente não foi atualizada no banco de dados")
            logger.error("Por favor, execute os comandos SQL no Supabase Dashboard")
            return False
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return False


async def main():
    """Função principal"""
    success = await update_media_type_constraint()
    
    if not success:
        logger.error("❌ Falha ao atualizar constraint")
        logger.info("Por favor, execute os comandos SQL manualmente no Supabase Dashboard")
        sys.exit(1)
    else:
        logger.success("✅ Constraint atualizada e testada com sucesso!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())