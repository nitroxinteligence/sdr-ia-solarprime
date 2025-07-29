#!/usr/bin/env python3
"""
Run Buffer Tests
================
Script para executar todos os testes do sistema de buffer
"""

import asyncio
import sys
import os
from pathlib import Path
from colorama import init, Fore, Style

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Inicializar colorama
init()


async def main():
    """Executa os testes"""
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🚀 EXECUTANDO TESTES DO SISTEMA DE BUFFER{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    # Verificar se Redis está rodando
    print(f"{Fore.YELLOW}Verificando pré-requisitos...{Style.RESET_ALL}")
    
    try:
        from services.redis_service import redis_service
        await redis_service.connect()
        
        if redis_service.client:
            print(f"{Fore.GREEN}✓ Redis conectado{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Redis não está rodando!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Por favor, inicie o Redis com: redis-server{Style.RESET_ALL}")
            return
    except Exception as e:
        print(f"{Fore.RED}✗ Erro ao verificar Redis: {e}{Style.RESET_ALL}")
        return
    
    # Menu de testes
    print(f"\n{Fore.CYAN}Escolha o teste a executar:{Style.RESET_ALL}")
    print(f"1. Teste básico do buffer (simulação de mensagens)")
    print(f"2. Teste de integração com SDR Agent V2")
    print(f"3. Executar todos os testes")
    print(f"0. Sair")
    
    choice = input(f"\n{Fore.YELLOW}Digite sua escolha: {Style.RESET_ALL}")
    
    if choice == "1":
        print(f"\n{Fore.GREEN}Executando teste básico do buffer...{Style.RESET_ALL}")
        from tests.test_message_buffer import run_all_tests
        await run_all_tests()
        
    elif choice == "2":
        print(f"\n{Fore.GREEN}Executando teste de integração...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Este teste requer API keys configuradas no .env{Style.RESET_ALL}")
        
        # Verificar se as APIs estão configuradas
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not gemini_key or gemini_key.startswith("your-"):
            print(f"{Fore.RED}✗ GEMINI_API_KEY não configurada no .env{Style.RESET_ALL}")
            return
            
        from tests.test_buffer_integration import run_integration_tests
        await run_integration_tests()
        
    elif choice == "3":
        print(f"\n{Fore.GREEN}Executando todos os testes...{Style.RESET_ALL}")
        
        # Teste básico
        print(f"\n{Fore.CYAN}[1/2] Teste básico do buffer{Style.RESET_ALL}")
        from tests.test_message_buffer import run_all_tests
        await run_all_tests()
        
        # Verificar APIs antes do teste de integração
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_key and not gemini_key.startswith("your-"):
            print(f"\n{Fore.CYAN}[2/2] Teste de integração{Style.RESET_ALL}")
            from tests.test_buffer_integration import run_integration_tests
            await run_integration_tests()
        else:
            print(f"\n{Fore.YELLOW}[2/2] Teste de integração pulado (API key não configurada){Style.RESET_ALL}")
            
    elif choice == "0":
        print(f"\n{Fore.YELLOW}Saindo...{Style.RESET_ALL}")
        return
        
    else:
        print(f"\n{Fore.RED}Opção inválida!{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✅ Testes concluídos!{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}Logs salvos em: tests/logs/{Style.RESET_ALL}")


if __name__ == "__main__":
    # Criar diretório de logs se não existir
    os.makedirs("tests/logs", exist_ok=True)
    
    # Executar
    asyncio.run(main())