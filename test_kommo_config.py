"""
Script para testar configuração do Kommo
"""

import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print("="*60)
print("Configuração Atual do Kommo:")
print("="*60)
print(f"CLIENT_ID: {os.getenv('KOMMO_CLIENT_ID', 'NÃO CONFIGURADO')}")
print(f"CLIENT_SECRET: {'****' + os.getenv('KOMMO_CLIENT_SECRET', '')[-4:] if os.getenv('KOMMO_CLIENT_SECRET') else 'NÃO CONFIGURADO'}")
print(f"SUBDOMAIN: {os.getenv('KOMMO_SUBDOMAIN', 'NÃO CONFIGURADO')}")
print(f"REDIRECT_URI: {os.getenv('KOMMO_REDIRECT_URI', 'NÃO CONFIGURADO')}")
print("="*60)

# Verificar se está usando localhost ou produção
redirect_uri = os.getenv('KOMMO_REDIRECT_URI', '')
if 'localhost' in redirect_uri:
    print("\n⚠️  ATENÇÃO: Redirect URI está configurado para DESENVOLVIMENTO (localhost)")
    print("   Para funcionar, você precisa:")
    print("   1. Adicionar esta URL no Kommo CRM")
    print("   2. Acessar via http://localhost:8000/auth/kommo/login")
elif 'easypanel.host' in redirect_uri:
    print("\n⚠️  ATENÇÃO: Redirect URI está configurado para PRODUÇÃO (EasyPanel)")
    print("   Para funcionar, você precisa:")
    print("   1. Adicionar esta URL no Kommo CRM")
    print(f"   2. Acessar via {redirect_uri.replace('/auth/kommo/callback', '/auth/kommo/login')}")

print("\n💡 DICA: No Kommo CRM, você pode adicionar múltiplas URLs de redirect")
print("   separadas por vírgula ou em linhas diferentes.")
print("="*60)