#!/usr/bin/env python3
"""
Script para aplicar correção do campo phone_number com segurança
================================================
Aplica a correção do tamanho do campo phone_number com validações
e capacidade de rollback em caso de erro.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2 import sql
from loguru import logger
from dotenv import load_dotenv
from supabase import create_client

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

def parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL para componentes de conexão"""
    # Formato: postgresql://user:password@host:port/database
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:],  # Remove leading /
        'user': parsed.username,
        'password': parsed.password
    }

def check_current_field_size():
    """Verifica o tamanho atual do campo phone_number"""
    logger.info("🔍 Verificando tamanho atual do campo phone_number...")
    
    try:
        # Usar Supabase client para verificar
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Credenciais Supabase não encontradas")
            return None
            
        client = create_client(supabase_url, supabase_key)
        
        # Query para verificar estrutura
        query = """
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'leads' 
        AND column_name = 'phone_number'
        """
        
        # Executar via SQL direto se possível
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            conn_params = parse_database_url(database_url)
            
            with psycopg2.connect(**conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    result = cur.fetchone()
                    
                    if result:
                        col_name, data_type, max_length = result
                        logger.info(f"📊 Campo atual: {col_name} - {data_type}({max_length})")
                        return max_length
                    else:
                        logger.error("❌ Campo phone_number não encontrado")
                        return None
        else:
            logger.warning("⚠️ DATABASE_URL não configurado, verificação limitada")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar campo: {e}")
        return None

def apply_fix():
    """Aplica a correção do campo phone_number"""
    logger.info("🚀 Iniciando aplicação da correção...")
    
    # Verificar tamanho atual
    current_size = check_current_field_size()
    
    if current_size == 50:
        logger.success("✅ Campo já está com tamanho correto (50 caracteres)")
        return True
    elif current_size == 20:
        logger.info("📝 Campo está com 20 caracteres, aplicando correção...")
    else:
        logger.warning(f"⚠️ Tamanho inesperado: {current_size}")
    
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("❌ DATABASE_URL não configurado")
            return False
            
        conn_params = parse_database_url(database_url)
        
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                # Criar backup dos dados atuais
                logger.info("💾 Criando backup dos dados...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS leads_backup_phone_fix AS 
                    SELECT * FROM leads
                """)
                
                # Aplicar correção
                logger.info("🔧 Aplicando correção...")
                cur.execute("""
                    ALTER TABLE leads 
                    ALTER COLUMN phone_number TYPE VARCHAR(50)
                """)
                
                # Verificar se funcionou
                cur.execute("""
                    SELECT character_maximum_length 
                    FROM information_schema.columns
                    WHERE table_name = 'leads' 
                    AND column_name = 'phone_number'
                """)
                
                new_size = cur.fetchone()[0]
                
                if new_size == 50:
                    conn.commit()
                    logger.success("✅ Correção aplicada com sucesso!")
                    
                    # Verificar dados existentes
                    cur.execute("SELECT COUNT(*) FROM leads WHERE LENGTH(phone_number) > 20")
                    long_phones = cur.fetchone()[0]
                    
                    if long_phones > 0:
                        logger.info(f"📱 Encontrados {long_phones} registros com telefones > 20 caracteres")
                    
                    return True
                else:
                    conn.rollback()
                    logger.error(f"❌ Correção falhou, tamanho após alteração: {new_size}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar correção: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("🔧 CORREÇÃO DO CAMPO PHONE_NUMBER")
    logger.info("=" * 60)
    
    # Verificar ambiente
    env = os.getenv("ENVIRONMENT", "development")
    logger.info(f"🌍 Ambiente: {env}")
    
    if env == "production":
        logger.warning("⚠️ ATENÇÃO: Executando em PRODUÇÃO!")
        response = input("Deseja continuar? (sim/não): ")
        if response.lower() != "sim":
            logger.info("❌ Operação cancelada")
            return
    
    # Aplicar correção
    success = apply_fix()
    
    if success:
        logger.success("✅ Processo concluído com sucesso!")
        logger.info("📝 Próximos passos:")
        logger.info("1. Testar inserção de números longos do WhatsApp")
        logger.info("2. Verificar se aplicação está funcionando corretamente")
        logger.info("3. Remover tabela de backup após confirmação: DROP TABLE leads_backup_phone_fix")
    else:
        logger.error("❌ Processo falhou!")
        logger.info("💡 Verifique os logs e tente novamente")

if __name__ == "__main__":
    main()