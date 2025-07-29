#!/usr/bin/env python3
"""
Test Connection String
======================
Verifica diferentes formas de conexão com o banco
"""

import os
import urllib.parse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Connection string original do .env
original_url = os.getenv("SUPABASE_DATABASE_URL")
print(f"Connection string original:\n{original_url}\n")

# Tentar diferentes abordagens
print("Testando diferentes formas de conexão...\n")

# 1. Tentar com a URL original
print("1. Teste com URL original:")
try:
    engine = create_engine(original_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✅ Conexão bem-sucedida!")
        print(f"   PostgreSQL: {version}\n")
except Exception as e:
    print(f"❌ Erro: {e}\n")

# 2. Tentar decodificar a senha
print("2. Teste decodificando a senha:")
try:
    # Extrair partes da URL
    import re
    match = re.match(r'postgresql://postgres:(.+)@(.+)', original_url)
    if match:
        encoded_password = match.group(1)
        host_and_rest = match.group(2)
        
        # Decodificar senha
        decoded_password = urllib.parse.unquote(encoded_password)
        print(f"   Senha encoded: {encoded_password}")
        print(f"   Senha decoded: {decoded_password}")
        
        # Recriar URL com senha decodificada e depois re-encodar
        new_encoded_password = urllib.parse.quote(decoded_password, safe='')
        new_url = f"postgresql://postgres:{new_encoded_password}@{host_and_rest}"
        
        engine = create_engine(new_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Conexão bem-sucedida com senha re-encoded!")
            print(f"   PostgreSQL: {version}\n")
    else:
        print("❌ Não foi possível extrair partes da URL\n")
except Exception as e:
    print(f"❌ Erro: {e}\n")

# 3. Tentar com psycopg2 diretamente
print("3. Teste com psycopg2 diretamente:")
try:
    import psycopg2
    from urllib.parse import urlparse
    
    # Parse da URL
    parsed = urlparse(original_url)
    
    # Decodificar senha
    password = urllib.parse.unquote(parsed.password)
    
    # Conectar
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],  # Remove a barra inicial
        user=parsed.username,
        password=password,
        sslmode='require'
    )
    
    cur = conn.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()[0]
    print(f"✅ Conexão bem-sucedida com psycopg2!")
    print(f"   PostgreSQL: {version}\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}\n")

print("\nRecomendação:")
print("Se algum teste funcionou, use esse método para criar a connection string.")
print("A senha pode precisar ser properly encoded para funcionar com SQLAlchemy.")