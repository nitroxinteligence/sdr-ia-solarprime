#!/usr/bin/env python3
"""
Script para corrigir configuração do Redirect URI do Kommo
"""

import os
import sys

print("="*60)
print("🔧 Correção de Configuração do Kommo OAuth2")
print("="*60)

print("\nO Kommo requer que o Redirect URI seja EXATAMENTE igual")
print("ao que está configurado na aplicação no site do Kommo.\n")

print("Escolha uma opção:")
print("1. Desenvolvimento Local (http://localhost:8000)")
print("2. Produção no EasyPanel")
print("3. Configuração personalizada")

choice = input("\nOpção (1/2/3): ").strip()

if choice == "1":
    redirect_uri = "http://localhost:8000/auth/kommo/callback"
    print(f"\n✅ Usando: {redirect_uri}")
elif choice == "2":
    subdomain = input("Digite o subdomínio do EasyPanel (ex: sdr-api): ").strip()
    domain = input("Digite o domínio do EasyPanel (ex: fzvgou.easypanel.host): ").strip()
    redirect_uri = f"https://{subdomain}.{domain}/auth/kommo/callback"
    print(f"\n✅ Usando: {redirect_uri}")
elif choice == "3":
    redirect_uri = input("Digite a URL completa do redirect (incluindo /auth/kommo/callback): ").strip()
    print(f"\n✅ Usando: {redirect_uri}")
else:
    print("❌ Opção inválida!")
    sys.exit(1)

print("\n📝 Atualizando .env...")

# Ler .env atual
env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Atualizar linha do KOMMO_REDIRECT_URI
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('KOMMO_REDIRECT_URI='):
            lines[i] = f'KOMMO_REDIRECT_URI={redirect_uri}\n'
            updated = True
            break
    
    # Se não encontrou, adicionar
    if not updated:
        # Procurar seção do Kommo
        for i, line in enumerate(lines):
            if '# Kommo CRM' in line:
                # Inserir após KOMMO_SUBDOMAIN
                for j in range(i, len(lines)):
                    if lines[j].startswith('KOMMO_SUBDOMAIN='):
                        lines.insert(j + 1, f'KOMMO_REDIRECT_URI={redirect_uri}\n')
                        updated = True
                        break
                break
        
        # Se ainda não adicionou, adicionar no final
        if not updated:
            lines.append(f'\nKOMMO_REDIRECT_URI={redirect_uri}\n')
    
    # Salvar
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ Arquivo .env atualizado!")
else:
    print("❌ Arquivo .env não encontrado!")
    sys.exit(1)

print("\n⚠️  IMPORTANTE:")
print("="*60)
print("1. No Kommo CRM, vá para:")
print("   Configurações → Integrações → API → Suas integrações")
print("")
print("2. Na sua aplicação OAuth2, adicione este Redirect URI:")
print(f"   {redirect_uri}")
print("")
print("3. O Kommo permite múltiplas URLs (uma por linha)")
print("")
print("4. Após adicionar no Kommo, reinicie o servidor:")
print("   Ctrl+C e execute novamente: uvicorn api.main:app --reload")
print("="*60)