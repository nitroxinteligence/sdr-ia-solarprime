#!/usr/bin/env python3
"""
Verifica compatibilidade do Client ID
"""
import os
from dotenv import load_dotenv
import base64
import json

load_dotenv()

token = os.getenv('KOMMO_LONG_LIVED_TOKEN')
client_id = os.getenv('KOMMO_CLIENT_ID')
client_secret = os.getenv('KOMMO_CLIENT_SECRET')

# Decodificar token para ver o client_id
parts = token.split('.')
payload = parts[1]
padding = 4 - len(payload) % 4
if padding != 4:
    payload += '=' * padding
decoded = base64.urlsafe_b64decode(payload)
token_data = json.loads(decoded)

print('🔍 ANÁLISE DE COMPATIBILIDADE:')
print('='*60)
print(f'Client ID no .env:   {client_id}')
print(f'Client ID no token:  {token_data.get("aud")}')
print('')

if client_id != token_data.get('aud'):
    print('❌ INCOMPATIBILIDADE DETECTADA!')
    print('')
    print('🔧 CORREÇÃO NECESSÁRIA:')
    print(f'1. O token foi gerado para um Client ID diferente')
    print(f'2. Atualize KOMMO_CLIENT_ID no .env para: {token_data.get("aud")}')
    print('')
    print('OU')
    print('')
    print('Gere um novo token para o Client ID correto:')
    print(f'   Client ID esperado: {client_id}')
else:
    print('✅ Client IDs correspondem')

print('')
print('📊 Informações adicionais do token:')
print(f'   Account ID: {token_data.get("account_id")}')
print(f'   User ID: {token_data.get("sub")}')
print(f'   API Domain: {token_data.get("api_domain")}')
print(f'   Escopos: {", ".join(token_data.get("scopes", []))}')