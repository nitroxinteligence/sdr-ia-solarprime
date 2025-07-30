#!/usr/bin/env python3
"""
Debug do problema de autenticação Kommo
"""

import os
import urllib.parse
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print("="*80)
print("🔍 DEBUG - Autenticação Kommo OAuth2")
print("="*80)

# Verificar configurações
client_id = os.getenv("KOMMO_CLIENT_ID")
client_secret = os.getenv("KOMMO_CLIENT_SECRET")
subdomain = os.getenv("KOMMO_SUBDOMAIN")
redirect_uri = os.getenv("KOMMO_REDIRECT_URI")

print("\n📋 Configurações carregadas do .env:")
print(f"CLIENT_ID: {client_id}")
print(f"CLIENT_SECRET: {'*' * 40}{client_secret[-10:]}")
print(f"SUBDOMAIN: {subdomain}")
print(f"REDIRECT_URI: {redirect_uri}")

# Construir URL manualmente
base_url = f"https://{subdomain}.kommo.com"
auth_endpoint = f"{base_url}/oauth/authorize"

# Parâmetros
params = {
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "state": "test_state_123"
}

# Construir query string
query_string = urllib.parse.urlencode(params)
full_url = f"{auth_endpoint}?{query_string}"

print("\n🔗 URL de autorização construída:")
print(full_url)

# URL alternativa com encoding manual
manual_url = (
    f"{auth_endpoint}?"
    f"client_id={client_id}&"
    f"redirect_uri={urllib.parse.quote(redirect_uri, safe='')}&"
    f"response_type=code&"
    f"state=test_state_123"
)

print("\n🔗 URL com encoding manual:")
print(manual_url)

print("\n📝 Instruções:")
print("="*80)
print("1. Copie uma das URLs acima e cole no navegador")
print("2. Se aparecer 'Nothing here', o problema é no Kommo")
print("3. Verifique no Kommo CRM:")
print("   - A integração está ATIVA?")
print("   - O redirect_uri está EXATAMENTE como acima?")
print("   - Não há espaços extras ou caracteres invisíveis?")
print("\n4. No Kommo, o redirect URI deve ser:")
print(f"   {redirect_uri}")
print("\n5. Tente também com HTTPS no localhost:")
print("   https://localhost:8000/auth/kommo/callback")
print("="*80)

# Verificar se há problemas conhecidos
print("\n⚠️  Possíveis problemas:")
if ' ' in redirect_uri:
    print("❌ Espaços encontrados no redirect_uri!")
if not redirect_uri.startswith(('http://', 'https://')):
    print("❌ Redirect URI não começa com http:// ou https://")
if subdomain != subdomain.lower():
    print("❌ Subdomain contém maiúsculas - pode causar problemas")

# Testar conexão básica
print("\n🌐 Testando conexão com Kommo...")
import requests

try:
    response = requests.get(f"https://{subdomain}.kommo.com", timeout=5)
    if response.status_code == 200:
        print("✅ Domínio Kommo acessível")
    else:
        print(f"⚠️  Status code: {response.status_code}")
except Exception as e:
    print(f"❌ Erro ao acessar Kommo: {e}")

print("\n💡 DICA IMPORTANTE:")
print("="*80)
print("Se nada funcionar, tente criar a URL de autorização manualmente:")
print(f"\nhttps://{subdomain}.kommo.com/oauth/authorize?client_id={client_id}&redirect_uri=http://localhost:8000/auth/kommo/callback&response_type=code&state=123")
print("\nE veja se o Kommo aceita.")
print("="*80)