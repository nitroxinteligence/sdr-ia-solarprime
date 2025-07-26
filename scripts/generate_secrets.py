#!/usr/bin/env python3
"""
Script para gerar chaves secretas seguras para o arquivo .env
"""
import secrets
import string
import sys

def generate_secret_key(length=32):
    """Gera uma chave secreta segura"""
    return secrets.token_urlsafe(length)

def generate_password(length=16):
    """Gera uma senha forte"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Gerador de Chaves Secretas - SDR SolarPrime")
    print("=" * 50)
    print()
    
    # Gerar SECRET_KEY
    secret_key = generate_secret_key(32)
    print(f"SECRET_KEY={secret_key}")
    print()
    
    # Gerar JWT_SECRET_KEY
    jwt_secret = generate_secret_key(32)
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    
    # Gerar REDIS_PASSWORD
    redis_password = generate_password(20)
    print(f"REDIS_PASSWORD={redis_password}")
    print()
    
    # Gerar KOMMO_WEBHOOK_TOKEN
    webhook_token = generate_secret_key(24)
    print(f"KOMMO_WEBHOOK_TOKEN={webhook_token}")
    print()
    
    print("=" * 50)
    print("✅ Copie as chaves acima para seu arquivo .env")
    print("⚠️  IMPORTANTE: Mantenha essas chaves seguras!")
    print()
    
    # Gerar Redis URLs com a senha
    print("URLs do Redis com a senha gerada:")
    print(f"REDIS_URL=redis://:{redis_password}@localhost:6379/0")
    print(f"CELERY_BROKER_URL=redis://:{redis_password}@localhost:6379/1")
    print(f"CELERY_RESULT_BACKEND=redis://:{redis_password}@localhost:6379/2")

if __name__ == "__main__":
    main()