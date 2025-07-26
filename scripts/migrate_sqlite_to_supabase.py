#!/usr/bin/env python3
"""
Migrate SQLite to Supabase
==========================
Script para migrar dados do SQLite (AGnO) para Supabase
"""

import asyncio
import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from models.lead import LeadCreate
from models.conversation import ConversationCreate
from models.message import MessageCreate
from loguru import logger

load_dotenv()


class SQLiteToSupabaseMigrator:
    """Migrador de dados do SQLite para Supabase"""
    
    def __init__(self, sqlite_path: str = "data/agent_storage.db"):
        self.sqlite_path = sqlite_path
        self.phone_to_lead_id = {}  # Mapear telefone para lead_id
        self.session_to_conversation_id = {}  # Mapear session para conversation_id
        
    async def migrate(self):
        """Executa migração completa"""
        logger.info("🚀 Iniciando migração SQLite → Supabase")
        
        if not os.path.exists(self.sqlite_path):
            logger.error(f"Arquivo SQLite não encontrado: {self.sqlite_path}")
            return
        
        # Conectar ao SQLite
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # 1. Migrar sessões para leads e conversas
            await self._migrate_sessions(cursor)
            
            # 2. Migrar histórico de mensagens
            await self._migrate_messages(cursor)
            
            logger.info("✅ Migração concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante migração: {e}")
            raise
        finally:
            conn.close()
    
    async def _migrate_sessions(self, cursor):
        """Migra sessões do AGnO para leads e conversas"""
        logger.info("📋 Migrando sessões...")
        
        # Buscar todas as sessões
        cursor.execute("SELECT * FROM sdr_sessions ORDER BY created_at")
        sessions = cursor.fetchall()
        
        logger.info(f"Encontradas {len(sessions)} sessões")
        
        for session in sessions:
            try:
                # Extrair dados da sessão
                session_id = session["session_id"]
                user_id = session["user_id"]  # Geralmente o telefone
                created_at = session["created_at"]
                
                # Extrair dados do JSON
                session_data = {}
                if session["session_data"]:
                    try:
                        session_data = json.loads(session["session_data"])
                    except:
                        pass
                
                # Criar lead
                lead_info = session_data.get("lead_info", {})
                phone = user_id or lead_info.get("phone", "")
                
                if not phone:
                    logger.warning(f"Sessão {session_id} sem telefone, pulando...")
                    continue
                
                # Criar ou atualizar lead
                lead = await lead_repository.create_or_update(
                    LeadCreate(
                        phone_number=phone,
                        name=lead_info.get("name"),
                        email=lead_info.get("email")
                    )
                )
                
                # Atualizar com mais informações se disponíveis
                if lead_info:
                    update_data = {}
                    
                    if lead_info.get("property_type"):
                        update_data["property_type"] = lead_info["property_type"]
                    if lead_info.get("bill_value"):
                        try:
                            update_data["bill_value"] = float(lead_info["bill_value"])
                        except:
                            pass
                    if lead_info.get("consumption_kwh"):
                        try:
                            update_data["consumption_kwh"] = int(lead_info["consumption_kwh"])
                        except:
                            pass
                    if lead_info.get("address"):
                        update_data["address"] = lead_info["address"]
                    
                    # Estágio atual
                    current_stage = session_data.get("current_stage", "INITIAL_CONTACT")
                    update_data["current_stage"] = current_stage
                    
                    if update_data:
                        await lead_repository.update(lead.id, update_data)
                
                # Mapear para uso posterior
                self.phone_to_lead_id[phone] = lead.id
                
                # Criar conversa
                conversation = await conversation_repository.create(
                    ConversationCreate(
                        lead_id=lead.id,
                        session_id=session_id,
                        current_stage=session_data.get("current_stage", "INITIAL_CONTACT")
                    ).dict()
                )
                
                # Mapear para uso posterior
                self.session_to_conversation_id[session_id] = conversation.id
                
                logger.info(f"✅ Migrado lead {phone} com sessão {session_id}")
                
            except Exception as e:
                logger.error(f"Erro ao migrar sessão {session['session_id']}: {e}")
    
    async def _migrate_messages(self, cursor):
        """Migra histórico de mensagens"""
        logger.info("💬 Migrando mensagens...")
        
        message_count = 0
        
        for session_id, conversation_id in self.session_to_conversation_id.items():
            # Buscar dados da sessão
            cursor.execute(
                "SELECT session_data FROM sdr_sessions WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()
            
            if not result or not result["session_data"]:
                continue
            
            try:
                session_data = json.loads(result["session_data"])
                conversation_history = session_data.get("conversation_history", [])
                
                for msg in conversation_history:
                    # Criar mensagem
                    await message_repository.create(
                        MessageCreate(
                            conversation_id=conversation_id,
                            role=msg.get("role", "user"),
                            content=msg.get("content", ""),
                            created_at=msg.get("timestamp", datetime.now().isoformat())
                        ).dict()
                    )
                    message_count += 1
                
                # Atualizar contador de mensagens na conversa
                if conversation_history:
                    await conversation_repository.update(
                        conversation_id,
                        {"total_messages": len(conversation_history)}
                    )
                
            except Exception as e:
                logger.error(f"Erro ao migrar mensagens da sessão {session_id}: {e}")
        
        logger.info(f"✅ Migradas {message_count} mensagens")
    
    async def verify_migration(self):
        """Verifica resultado da migração"""
        logger.info("\n📊 Verificando migração...")
        
        # Contar registros
        lead_count = await lead_repository.count()
        conversation_count = await conversation_repository.count()
        message_count = await message_repository.count()
        
        logger.info(f"Leads: {lead_count}")
        logger.info(f"Conversas: {conversation_count}")
        logger.info(f"Mensagens: {message_count}")
        
        # Listar alguns leads
        leads = await lead_repository.get_all(limit=5)
        
        logger.info("\n📱 Primeiros 5 leads:")
        for lead in leads:
            logger.info(f"  - {lead.phone_number}: {lead.name or 'Sem nome'} ({lead.current_stage})")


async def main():
    """Função principal"""
    print("🔄 Migração SQLite → Supabase\n")
    
    # Verificar configurações
    if not os.getenv("SUPABASE_URL"):
        print("❌ SUPABASE_URL não configurada no .env")
        return
    
    if not os.getenv("SUPABASE_ANON_KEY"):
        print("❌ SUPABASE_ANON_KEY não configurada no .env")
        return
    
    # Perguntar confirmação
    print("⚠️  ATENÇÃO: Este script irá migrar dados do SQLite para o Supabase.")
    print("   Certifique-se que as tabelas foram criadas no Supabase primeiro!")
    print("   Execute o script create_supabase_tables.sql no Supabase SQL Editor.\n")
    
    confirm = input("Deseja continuar? (s/n): ").lower()
    
    if confirm != 's':
        print("Migração cancelada.")
        return
    
    # Executar migração
    migrator = SQLiteToSupabaseMigrator()
    await migrator.migrate()
    
    # Verificar resultado
    await migrator.verify_migration()
    
    print("\n✅ Migração concluída!")


if __name__ == "__main__":
    asyncio.run(main())