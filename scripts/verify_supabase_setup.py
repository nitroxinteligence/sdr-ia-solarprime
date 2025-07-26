#!/usr/bin/env python3
"""
Verificação e Configuração do Supabase
======================================
Script para verificar a configuração do Supabase e garantir
que a integração está funcionando corretamente.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client
from colorama import init, Fore, Style

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

# Inicializar colorama
init(autoreset=True)

# Carregar variáveis de ambiente
load_dotenv()


class SupabaseVerifier:
    """Verificador de configuração do Supabase"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client = None
        self.issues = []
        self.warnings = []
        
    def print_header(self, text: str):
        """Imprime cabeçalho formatado"""
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{text}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    
    def print_success(self, text: str):
        """Imprime mensagem de sucesso"""
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
    
    def print_error(self, text: str):
        """Imprime mensagem de erro"""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
        self.issues.append(text)
    
    def print_warning(self, text: str):
        """Imprime mensagem de aviso"""
        print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")
        self.warnings.append(text)
    
    def print_info(self, text: str):
        """Imprime informação"""
        print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")
    
    async def check_environment(self):
        """Verifica variáveis de ambiente"""
        self.print_header("1. Verificando Variáveis de Ambiente")
        
        # Verificar URL
        if self.url:
            self.print_success(f"SUPABASE_URL definida: {self.url[:30]}...")
        else:
            self.print_error("SUPABASE_URL não está definida no .env")
            return False
        
        # Verificar Anon Key
        if self.anon_key:
            self.print_success(f"SUPABASE_ANON_KEY definida: {self.anon_key[:20]}...")
        else:
            self.print_error("SUPABASE_ANON_KEY não está definida no .env")
            return False
        
        # Verificar Service Key
        if self.service_key:
            self.print_success(f"SUPABASE_SERVICE_KEY definida: {self.service_key[:20]}...")
            self.print_info("Service Key detectada - RLS será bypassado")
        else:
            self.print_warning("SUPABASE_SERVICE_KEY não definida - usando ANON_KEY")
            self.print_warning("Isso pode causar problemas com RLS (Row Level Security)")
        
        return True
    
    async def check_connection(self):
        """Verifica conexão com Supabase"""
        self.print_header("2. Testando Conexão com Supabase")
        
        try:
            # Tentar com Service Key primeiro, depois Anon Key
            key = self.service_key or self.anon_key
            self.client = create_client(self.url, key)
            
            # Fazer uma query simples para testar
            result = self.client.table("leads").select("id").limit(1).execute()
            
            self.print_success("Conexão com Supabase estabelecida com sucesso!")
            
            if self.service_key:
                self.print_info("Usando Service Key (RLS bypassado)")
            else:
                self.print_info("Usando Anon Key (RLS ativo)")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro ao conectar com Supabase: {e}")
            return False
    
    async def check_tables(self):
        """Verifica se as tabelas existem"""
        self.print_header("3. Verificando Tabelas no Banco de Dados")
        
        required_tables = [
            "leads",
            "conversations", 
            "messages",
            "lead_qualifications",
            "follow_ups",
            "analytics"
        ]
        
        tables_ok = True
        
        for table in required_tables:
            try:
                # Tentar fazer select em cada tabela
                result = self.client.table(table).select("id").limit(1).execute()
                self.print_success(f"Tabela '{table}' existe e está acessível")
                
            except Exception as e:
                error_msg = str(e)
                if "relation" in error_msg and "does not exist" in error_msg:
                    self.print_error(f"Tabela '{table}' não existe")
                    tables_ok = False
                elif "row-level security" in error_msg:
                    self.print_warning(f"Tabela '{table}' existe mas RLS está bloqueando acesso")
                else:
                    self.print_error(f"Erro ao acessar tabela '{table}': {e}")
                    tables_ok = False
        
        return tables_ok
    
    async def check_rls_status(self):
        """Verifica status do RLS"""
        self.print_header("4. Verificando Row Level Security (RLS)")
        
        if self.service_key:
            self.print_info("Usando Service Key - RLS é bypassado automaticamente")
            return True
        
        # Tentar criar um lead de teste
        try:
            test_data = {
                "phone_number": "5511999999999",
                "name": "Teste RLS"
            }
            
            result = self.client.table("leads").insert(test_data).execute()
            
            if result.data:
                # Conseguiu inserir - deletar o teste
                lead_id = result.data[0]["id"]
                self.client.table("leads").delete().eq("id", lead_id).execute()
                self.print_success("RLS permite operações CRUD")
                return True
                
        except Exception as e:
            error_msg = str(e)
            if "row-level security" in error_msg:
                self.print_error("RLS está bloqueando operações")
                self.print_info("Soluções possíveis:")
                self.print_info("1. Adicionar SUPABASE_SERVICE_KEY ao .env")
                self.print_info("2. Ou executar o script disable_rls_for_testing.sql (apenas desenvolvimento)")
                return False
            else:
                self.print_error(f"Erro ao testar RLS: {e}")
                return False
    
    async def test_crud_operations(self):
        """Testa operações CRUD"""
        self.print_header("5. Testando Operações CRUD")
        
        from repositories.lead_repository import lead_repository
        from models.lead import LeadCreate
        
        try:
            # CREATE
            self.print_info("Testando CREATE...")
            test_lead = await lead_repository.create({
                "phone_number": "5511888888888",
                "name": "Lead Teste CRUD"
            })
            
            if test_lead:
                self.print_success(f"CREATE funcionando - Lead ID: {test_lead.id}")
            else:
                self.print_error("CREATE falhou")
                return False
            
            # READ
            self.print_info("Testando READ...")
            read_lead = await lead_repository.get_by_id(test_lead.id)
            
            if read_lead:
                self.print_success("READ funcionando")
            else:
                self.print_error("READ falhou")
                return False
            
            # UPDATE
            self.print_info("Testando UPDATE...")
            updated_lead = await lead_repository.update(
                test_lead.id,
                {"name": "Lead Teste Atualizado"}
            )
            
            if updated_lead and updated_lead.name == "Lead Teste Atualizado":
                self.print_success("UPDATE funcionando")
            else:
                self.print_error("UPDATE falhou")
                return False
            
            # DELETE
            self.print_info("Testando DELETE...")
            deleted = await lead_repository.delete(test_lead.id)
            
            if deleted:
                self.print_success("DELETE funcionando")
            else:
                self.print_error("DELETE falhou")
                return False
            
            self.print_success("Todas operações CRUD funcionando corretamente!")
            return True
            
        except Exception as e:
            self.print_error(f"Erro durante testes CRUD: {e}")
            return False
    
    async def print_summary(self):
        """Imprime resumo da verificação"""
        self.print_header("RESUMO DA VERIFICAÇÃO")
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        if total_issues == 0:
            print(f"\n{Fore.GREEN}✅ SUCESSO! Supabase está configurado corretamente!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}A integração está 100% funcional com o AGnO Framework.{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.RED}❌ Foram encontrados {total_issues} problemas que precisam ser corrigidos:{Style.RESET_ALL}")
            for issue in self.issues:
                print(f"{Fore.RED}   • {issue}{Style.RESET_ALL}")
        
        if total_warnings > 0:
            print(f"\n{Fore.YELLOW}⚠️  {total_warnings} avisos encontrados:{Style.RESET_ALL}")
            for warning in self.warnings:
                print(f"{Fore.YELLOW}   • {warning}{Style.RESET_ALL}")
        
        # Instruções finais
        if total_issues > 0:
            self.print_header("PRÓXIMOS PASSOS")
            
            if "SUPABASE_SERVICE_KEY" in str(self.issues + self.warnings):
                print("\n1. Adicione a SUPABASE_SERVICE_KEY ao arquivo .env:")
                print(f"{Fore.CYAN}   SUPABASE_SERVICE_KEY=seu_service_key_aqui{Style.RESET_ALL}")
                print("   (Encontre no painel do Supabase: Settings > API > Service Role Key)")
            
            if "não existe" in str(self.issues):
                print("\n2. Execute o script SQL para criar as tabelas:")
                print(f"{Fore.CYAN}   scripts/create_supabase_tables.sql{Style.RESET_ALL}")
                print("   (Copie e cole no SQL Editor do Supabase)")
            
            if "row-level security" in str(self.issues + self.warnings):
                print("\n3. Para desenvolvimento, você pode desabilitar RLS temporariamente:")
                print(f"{Fore.CYAN}   scripts/disable_rls_for_testing.sql{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   ⚠️  NUNCA faça isso em produção!{Style.RESET_ALL}")
    
    async def run(self):
        """Executa todas as verificações"""
        print(f"{Fore.CYAN}🔍 Verificador de Configuração Supabase - SDR IA SolarPrime{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        
        # Executar verificações em ordem
        if not await self.check_environment():
            await self.print_summary()
            return
        
        if not await self.check_connection():
            await self.print_summary()
            return
        
        await self.check_tables()
        await self.check_rls_status()
        
        # Só testar CRUD se não houver problemas críticos
        if len(self.issues) == 0:
            await self.test_crud_operations()
        
        await self.print_summary()


async def main():
    """Função principal"""
    verifier = SupabaseVerifier()
    await verifier.run()


if __name__ == "__main__":
    asyncio.run(main())