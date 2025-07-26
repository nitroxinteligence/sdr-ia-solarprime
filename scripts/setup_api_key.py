#!/usr/bin/env python3
"""
Script de Configuração da API Key
=================================
Ajuda a configurar a API key do Gemini
"""

import os
import sys
from pathlib import Path

# Cores para terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def main():
    print(f"{BLUE}🔑 Configuração da API Key do Gemini{RESET}\n")
    
    # Verifica se .env existe
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print(f"{RED}❌ Arquivo .env não encontrado!{RESET}")
        return
    
    # Lê o arquivo .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Verifica se precisa configurar
    if "YOUR_GEMINI_API_KEY_HERE" in content:
        print(f"{YELLOW}⚠️  API Key ainda não configurada!{RESET}\n")
        print("Para obter sua API key do Gemini:")
        print(f"1. Acesse: {BLUE}https://makersuite.google.com/app/apikey{RESET}")
        print("2. Faça login com sua conta Google")
        print("3. Clique em 'Create API Key'")
        print("4. Copie a API key gerada\n")
        
        api_key = input("Cole sua API key aqui (ou pressione Enter para pular): ").strip()
        
        if api_key and api_key != "":
            # Substitui no arquivo
            new_content = content.replace("YOUR_GEMINI_API_KEY_HERE", api_key)
            
            with open(env_path, 'w') as f:
                f.write(new_content)
            
            print(f"\n{GREEN}✅ API Key configurada com sucesso!{RESET}")
            print("Agora você pode testar o agente com:")
            print(f"{BLUE}python scripts/test_agent.py{RESET}")
        else:
            print(f"\n{YELLOW}ℹ️  Configuração pulada.{RESET}")
            print("Você pode editar manualmente o arquivo .env")
    else:
        print(f"{GREEN}✅ API Key já está configurada!{RESET}")
        
        # Verifica se é válida verificando o comprimento típico
        import re
        match = re.search(r'GEMINI_API_KEY="([^"]+)"', content)
        if match:
            key = match.group(1)
            if len(key) > 20 and not key.startswith("YOUR_"):
                print("A API key parece estar válida.")
            else:
                print(f"{YELLOW}⚠️  A API key pode estar inválida.{RESET}")

if __name__ == "__main__":
    main()