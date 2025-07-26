#!/usr/bin/env python3
"""
Setup do Supabase
=================
Script interativo para configurar a integração com Supabase
"""

import os
import sys
from pathlib import Path
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)


def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def print_step(number: int, text: str):
    """Imprime passo numerado"""
    print(f"{Fore.YELLOW}Passo {number}:{Style.RESET_ALL} {text}")


def check_env_file():
    """Verifica e cria arquivo .env se necessário"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists():
        print(f"{Fore.YELLOW}Arquivo .env não encontrado.{Style.RESET_ALL}")
        
        if env_example_path.exists():
            print("Copiando .env.example para .env...")
            env_path.write_text(env_example_path.read_text())
            print(f"{Fore.GREEN}✅ Arquivo .env criado!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ .env.example também não encontrado!{Style.RESET_ALL}")
            return False
    
    return True


def update_env_variable(key: str, value: str):
    """Atualiza variável no arquivo .env"""
    env_path = Path(".env")
    
    if not env_path.exists():
        return False
    
    lines = env_path.read_text().splitlines()
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            updated = True
            break
    
    if not updated:
        lines.append(f"{key}={value}")
    
    env_path.write_text("\n".join(lines) + "\n")
    return True


def main():
    """Função principal"""
    print(f"{Fore.CYAN}🚀 Setup Supabase - SDR IA SolarPrime{Style.RESET_ALL}")
    print_header("Configuração Inicial do Supabase")
    
    # Verificar arquivo .env
    if not check_env_file():
        print(f"{Fore.RED}Crie o arquivo .env antes de continuar!{Style.RESET_ALL}")
        return
    
    print("Este script ajudará você a configurar a integração com Supabase.\n")
    
    # Passo 1: Credenciais
    print_step(1, "Configurar Credenciais do Supabase")
    print("\nVocê precisará das seguintes informações do seu projeto Supabase:")
    print("- URL do projeto")
    print("- Anon Key (pública)")
    print("- Service Key (privada - recomendada para backend)")
    print(f"\n{Fore.BLUE}Encontre em: Supabase Dashboard > Settings > API{Style.RESET_ALL}")
    
    configure = input("\nDeseja configurar as credenciais agora? (s/n): ").lower()
    
    if configure == 's':
        url = input("\nSUPABASE_URL: ").strip()
        if url:
            update_env_variable("SUPABASE_URL", url)
            print(f"{Fore.GREEN}✅ URL configurada!{Style.RESET_ALL}")
        
        anon_key = input("\nSUPABASE_ANON_KEY: ").strip()
        if anon_key:
            update_env_variable("SUPABASE_ANON_KEY", anon_key)
            print(f"{Fore.GREEN}✅ Anon Key configurada!{Style.RESET_ALL}")
        
        service_key = input("\nSUPABASE_SERVICE_KEY (opcional mas recomendada): ").strip()
        if service_key:
            update_env_variable("SUPABASE_SERVICE_KEY", service_key)
            print(f"{Fore.GREEN}✅ Service Key configurada!{Style.RESET_ALL}")
    
    # Passo 2: Criar tabelas
    print_step(2, "Criar Tabelas no Banco de Dados")
    print("\nPara criar as tabelas necessárias:")
    print(f"1. Abra o {Fore.CYAN}scripts/create_supabase_tables.sql{Style.RESET_ALL}")
    print("2. Copie todo o conteúdo")
    print("3. Cole no SQL Editor do Supabase")
    print("4. Execute o script")
    
    input("\nPressione ENTER quando as tabelas estiverem criadas...")
    
    # Passo 3: Configurar RLS
    print_step(3, "Configurar Row Level Security (RLS)")
    print("\nPara desenvolvimento, você tem duas opções:")
    print(f"1. {Fore.GREEN}Usar Service Key (recomendado){Style.RESET_ALL} - bypassa RLS automaticamente")
    print(f"2. {Fore.YELLOW}Desabilitar RLS temporariamente{Style.RESET_ALL} - execute scripts/disable_rls_for_testing.sql")
    print(f"\n{Fore.RED}⚠️  NUNCA desabilite RLS em produção!{Style.RESET_ALL}")
    
    # Passo 4: Instalar dependências
    print_step(4, "Instalar Dependências Python")
    print("\nExecute o seguinte comando:")
    print(f"{Fore.CYAN}pip install -r requirements.txt{Style.RESET_ALL}")
    
    install = input("\nDeseja instalar as dependências agora? (s/n): ").lower()
    if install == 's':
        os.system("pip install -r requirements.txt")
        print(f"{Fore.GREEN}✅ Dependências instaladas!{Style.RESET_ALL}")
    
    # Passo 5: Testar integração
    print_step(5, "Testar Integração")
    print("\nPara verificar se tudo está funcionando:")
    print(f"1. Teste rápido: {Fore.CYAN}python scripts/quick_test_supabase.py{Style.RESET_ALL}")
    print(f"2. Verificação completa: {Fore.CYAN}python scripts/verify_supabase_setup.py{Style.RESET_ALL}")
    
    # Resumo
    print_header("RESUMO")
    print("✅ Arquivo .env verificado")
    print("📋 Próximos passos:")
    print("   1. Configure as credenciais no .env (se ainda não fez)")
    print("   2. Execute o SQL para criar as tabelas")
    print("   3. Configure RLS conforme necessário")
    print("   4. Execute os scripts de teste")
    
    print(f"\n{Fore.GREEN}🎉 Setup concluído!{Style.RESET_ALL}")
    print(f"Execute {Fore.CYAN}python scripts/verify_supabase_setup.py{Style.RESET_ALL} para verificar a configuração.")


if __name__ == "__main__":
    main()