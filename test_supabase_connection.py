#!/usr/bin/env python3
"""
Test Supabase Connection Options
================================
Testa diferentes opções de conexão com Supabase
"""

import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("🔍 Testando opções de conexão com Supabase\n")

# 1. Testar API REST do Supabase
print("1. Testando API REST do Supabase:")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if supabase_url and supabase_key:
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/knowledge_base",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}"
            },
            params={"limit": 1}
        )
        
        if response.status_code == 200:
            print("✅ API REST funcionando!")
            print(f"   Status: {response.status_code}")
            print(f"   Registros: {len(response.json())}\n")
        else:
            print(f"❌ API retornou erro: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...\n")
    except Exception as e:
        print(f"❌ Erro na API REST: {e}\n")
else:
    print("❌ SUPABASE_URL ou SUPABASE_ANON_KEY não encontrados\n")

# 2. Verificar alternativas de conexão
print("2. Alternativas de conexão para PgVector:\n")

print("📌 Opção A - Usar Supabase Client (Recomendado):")
print("   - Use o supabase_client para todas as operações")
print("   - Implemente busca vetorial via RPC functions")
print("   - Não precisa de conexão direta ao PostgreSQL")

print("\n📌 Opção B - Connection Pooler:")
print("   - Use o pooler ao invés da conexão direta")
print("   - URL format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres")
print("   - Mais estável mas pode ter limitações")

print("\n📌 Opção C - Conexão via Proxy/Tunnel:")
print("   - Configure um túnel SSH ou proxy local")
print("   - Útil para desenvolvimento local")

print("\n📌 Opção D - Use apenas o Supabase Client:")
print("   - Evite conexão direta ao PostgreSQL")
print("   - Use RPC functions para operações complexas")
print("   - Mais simples e confiável")

# 3. Testar se tabelas existem via API
print("\n3. Verificando tabelas via API REST:")
tables_to_check = ["knowledge_base", "agent_sessions", "profiles", "embeddings"]

for table in tables_to_check:
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/{table}",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}"
            },
            params={"limit": 0, "count": "exact"}
        )
        
        if response.status_code == 200:
            count = response.headers.get('content-range', '').split('/')[-1]
            print(f"✅ Tabela '{table}' existe - Registros: {count}")
        else:
            print(f"❌ Tabela '{table}' - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar '{table}': {e}")

print("\n💡 RECOMENDAÇÃO:")
print("Para evitar problemas de conexão, considere usar o Supabase Client")
print("ao invés de conexão direta com PostgreSQL para o PgVector.")
print("\nO AGnO Framework pode funcionar com um adapter customizado")
print("que use o Supabase Client internamente.")