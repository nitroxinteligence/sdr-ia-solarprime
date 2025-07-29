#!/usr/bin/env python3
"""
Test Supabase Connection
========================
Script para testar e diagnosticar problemas de conexão com Supabase
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

def test_connection():
    """Testa conexão com Supabase"""
    
    print("🔍 Testando conexão com Supabase...\n")
    
    # Obter credenciais
    supabase_url = os.getenv("SUPABASE_URL", "")
    service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SERVICE_KEY: {service_key[:20]}...{service_key[-10:]}\n")
    
    # Extrair project ID
    if supabase_url:
        project_id = supabase_url.split("//")[1].split(".")[0]
        print(f"Project ID: {project_id}\n")
    else:
        print("❌ SUPABASE_URL não configurada!")
        return
    
    # Testar diferentes formatos de connection string
    connection_formats = [
        # Formato 1: Com project_id no user
        {
            "name": "Pooler com project_id no user",
            "url": f"postgresql://postgres.{project_id}:{service_key}@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
        },
        # Formato 2: Sem project_id no user
        {
            "name": "Pooler sem project_id no user",
            "url": f"postgresql://postgres:{service_key}@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
        },
        # Formato 3: Conexão direta
        {
            "name": "Conexão direta",
            "url": f"postgresql://postgres:{service_key}@db.{project_id}.supabase.co:5432/postgres?sslmode=require"
        },
        # Formato 4: Session pooler
        {
            "name": "Session pooler",
            "url": f"postgresql://postgres.{project_id}:{service_key}@aws-0-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
        }
    ]
    
    for conn_format in connection_formats:
        print(f"Testando: {conn_format['name']}")
        print(f"URL: {conn_format['url'][:80]}...\n")
        
        try:
            # Tentar conectar
            conn = psycopg2.connect(conn_format['url'])
            cur = conn.cursor()
            
            # Testar query simples
            cur.execute("SELECT version()")
            version = cur.fetchone()
            print(f"✅ SUCESSO! PostgreSQL: {version[0][:50]}...")
            
            # Verificar extensões
            cur.execute("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector')")
            extensions = cur.fetchall()
            print(f"Extensões instaladas: {[ext[0] for ext in extensions]}")
            
            # Verificar tabelas
            cur.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('knowledge_base', 'agent_sessions', 'embeddings')
            """)
            tables = cur.fetchall()
            print(f"Tabelas encontradas: {[table[0] for table in tables]}")
            
            cur.close()
            conn.close()
            
            print(f"\n🎉 Connection string correta:\n{conn_format['url']}\n")
            
            # Salvar a connection string correta
            return conn_format['url']
            
        except Exception as e:
            print(f"❌ Erro: {str(e)[:100]}...")
            print("-" * 50)
    
    print("\n💡 Nenhuma connection string funcionou!")
    print("\nPossíveis causas:")
    print("1. SERVICE_KEY incorreta ou expirada")
    print("2. Projeto na região errada (deve ser sa-east-1)")
    print("3. Pooler não configurado corretamente")
    print("\nVerifique no Dashboard do Supabase:")
    print("- Settings > Database > Connection string")
    print("- Selecione 'Connection pooling' e 'Transaction'")
    print("- Copie a connection string exata")

if __name__ == "__main__":
    test_connection()