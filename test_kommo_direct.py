#!/usr/bin/env python3
"""
Teste direto da API Kommo para verificar credenciais
"""

import requests
import os
from dotenv import load_dotenv
import base64

load_dotenv()

print("="*60)
print("🔍 Testando credenciais Kommo diretamente")
print("="*60)

client_id = os.getenv("KOMMO_CLIENT_ID")
client_secret = os.getenv("KOMMO_CLIENT_SECRET")
subdomain = os.getenv("KOMMO_SUBDOMAIN")

# Teste 1: Verificar se o subdomínio existe
print(f"\n1️⃣ Verificando subdomínio: {subdomain}")
try:
    response = requests.get(f"https://{subdomain}.kommo.com/api/v4/account", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   ✅ Subdomínio existe (requer autenticação)")
    elif response.status_code == 404:
        print("   ❌ Subdomínio não encontrado!")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Tentar diferentes formatos de redirect URI
print("\n2️⃣ Testando URLs de autorização com diferentes redirect_uris:")

test_redirects = [
    "http://localhost:8000/auth/kommo/callback",
    "https://localhost:8000/auth/kommo/callback",
    "http://127.0.0.1:8000/auth/kommo/callback",
    "http://localhost/auth/kommo/callback",
]

for redirect in test_redirects:
    auth_url = (
        f"https://{subdomain}.kommo.com/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect}&"
        f"response_type=code&"
        f"state=test123"
    )
    print(f"\n   Testando: {redirect}")
    print(f"   URL: {auth_url[:100]}...")
    
    # Fazer uma requisição HEAD para ver se a URL é válida
    try:
        response = requests.head(auth_url, allow_redirects=False, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   Redirecionamento para: {response.headers.get('Location', 'N/A')}")
    except Exception as e:
        print(f"   Erro: {e}")

# Teste 3: Verificar se as credenciais estão no formato correto
print("\n3️⃣ Verificando formato das credenciais:")
print(f"   Client ID: {client_id}")
print(f"   - Formato UUID: {'Sim' if len(client_id) == 36 and client_id.count('-') == 4 else 'Não'}")
print(f"   Client Secret: {'*' * 50}{client_secret[-10:]}")
print(f"   - Comprimento: {len(client_secret)} caracteres")

print("\n💡 SOLUÇÃO ALTERNATIVA:")
print("="*60)
print("Se localhost não funciona, você pode:")
print("")
print("1. Usar ngrok para criar um túnel público:")
print("   - Instale: brew install ngrok")
print("   - Execute: ngrok http 8000")
print("   - Use a URL do ngrok como redirect_uri")
print("")
print("2. Ou usar 127.0.0.1 em vez de localhost")
print("")
print("3. Ou adicionar no /etc/hosts:")
print("   127.0.0.1 local.test")
print("   E usar http://local.test:8000/auth/kommo/callback")
print("="*60)