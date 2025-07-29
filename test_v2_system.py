#!/usr/bin/env python3
"""
Test V2 System Complete
=======================
Script para testar completamente o sistema V2 com todas as integrações
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
import traceback

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Inicializar colorama
init()

# Importações do projeto
from config.config import Config
from services.redis_service import redis_service
from services.database import supabase_client
from agents.sdr_agent_v2 import SDRAgentV2
from agents.storage.supabase_storage import SupabaseAgentStorage
from agents.knowledge.solarprime_knowledge import SolarPrimeKnowledge
from services.message_buffer_service import message_buffer_service


class SystemTester:
    """Classe para testar o sistema completo"""
    
    def __init__(self):
        self.config = Config()
        self.results = {
            "redis": False,
            "supabase": False,
            "pgvector": False,
            "openai": False,
            "gemini": False,
            "agent": False,
            "buffer": False,
            "knowledge": False
        }
    
    async def test_redis_connection(self):
        """Testa conexão com Redis"""
        print(f"\n{Fore.YELLOW}1. Testando Redis...{Style.RESET_ALL}")
        
        try:
            await redis_service.connect()
            if redis_service.client:
                # Teste de escrita/leitura
                await redis_service.client.set("test_key", "test_value", ex=10)
                value = await redis_service.client.get("test_key")
                
                if value and value.decode() == "test_value":
                    print(f"{Fore.GREEN}✓ Redis conectado e funcionando!{Style.RESET_ALL}")
                    self.results["redis"] = True
                else:
                    print(f"{Fore.RED}✗ Redis conectado mas teste falhou{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Redis não conectou{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Erro no Redis: {e}{Style.RESET_ALL}")
    
    async def test_supabase_connection(self):
        """Testa conexão com Supabase"""
        print(f"\n{Fore.YELLOW}2. Testando Supabase...{Style.RESET_ALL}")
        
        try:
            # Teste simples de query
            result = supabase_client.table("profiles").select("*").limit(1).execute()
            print(f"{Fore.GREEN}✓ Supabase conectado!{Style.RESET_ALL}")
            self.results["supabase"] = True
        except Exception as e:
            print(f"{Fore.RED}✗ Erro no Supabase: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Verifique SUPABASE_URL e SUPABASE_ANON_KEY no .env{Style.RESET_ALL}")
    
    async def test_pgvector_connection(self):
        """Testa conexão PgVector"""
        print(f"\n{Fore.YELLOW}3. Testando PgVector (Supabase Database)...{Style.RESET_ALL}")
        
        try:
            # Testar através do storage adapter
            storage = SupabaseAgentStorage()
            
            # Verificar se tabelas existem
            test_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('knowledge_base', 'agent_sessions', 'embeddings')
            ORDER BY table_name;
            """
            
            # Como o Supabase client não tem acesso direto ao SQL, vamos testar via API
            # Tentar buscar da knowledge_base
            result = supabase_client.table("knowledge_base").select("*").limit(1).execute()
            print(f"{Fore.GREEN}✓ PgVector/Supabase Database conectado!{Style.RESET_ALL}")
            print(f"  - Tabela knowledge_base acessível")
            self.results["pgvector"] = True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Erro no PgVector: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Verifique SUPABASE_DATABASE_URL no .env{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Execute o script SQL: scripts/supabase_complete_setup.sql{Style.RESET_ALL}")
    
    async def test_openai_connection(self):
        """Testa API da OpenAI"""
        print(f"\n{Fore.YELLOW}4. Testando OpenAI API...{Style.RESET_ALL}")
        
        try:
            from openai import OpenAI
            
            # Criar cliente
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Teste simples de embedding
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input="Teste de conexão"
            )
            
            if response and response.data:
                print(f"{Fore.GREEN}✓ OpenAI API funcionando!{Style.RESET_ALL}")
                print(f"  - Modelo: text-embedding-ada-002")
                print(f"  - Dimensões: {len(response.data[0].embedding)}")
                self.results["openai"] = True
            else:
                print(f"{Fore.RED}✗ OpenAI API respondeu mas sem dados{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}✗ Erro na OpenAI API: {e}{Style.RESET_ALL}")
            if "invalid" in str(e).lower() or "incorrect" in str(e).lower():
                print(f"{Fore.YELLOW}  API key inválida ou sem créditos{Style.RESET_ALL}")
            elif "rate" in str(e).lower():
                print(f"{Fore.YELLOW}  Rate limit atingido{Style.RESET_ALL}")
    
    async def test_gemini_connection(self):
        """Testa API do Gemini"""
        print(f"\n{Fore.YELLOW}5. Testando Google Gemini...{Style.RESET_ALL}")
        
        try:
            import google.generativeai as genai
            
            # Configurar API
            genai.configure(api_key=self.config.gemini.api_key)
            
            # Criar modelo
            model = genai.GenerativeModel(self.config.gemini.model)
            
            # Teste simples
            response = model.generate_content("Olá, este é um teste. Responda apenas com a palavra OK.")
            
            if response and response.text and "OK" in response.text.upper():
                print(f"{Fore.GREEN}✓ Google Gemini funcionando!{Style.RESET_ALL}")
                print(f"  - Modelo: {self.config.gemini.model}")
                self.results["gemini"] = True
            else:
                print(f"{Fore.RED}✗ Gemini respondeu mas resposta inesperada{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}✗ Erro no Gemini: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Verifique GEMINI_API_KEY no .env{Style.RESET_ALL}")
    
    async def test_agent_initialization(self):
        """Testa inicialização do agente"""
        print(f"\n{Fore.YELLOW}6. Testando SDR Agent V2...{Style.RESET_ALL}")
        
        try:
            agent = SDRAgentV2(self.config)
            await agent.initialize()
            
            # Teste simples de mensagem
            response, metadata = await agent.handle_greeting("5511999999999")
            
            if response and ("Helen" in response or "Solar Prime" in response):
                print(f"{Fore.GREEN}✓ SDR Agent V2 inicializado!{Style.RESET_ALL}")
                print(f"  - Resposta: {response[:50]}...")
                self.results["agent"] = True
            else:
                print(f"{Fore.RED}✗ Agente inicializado mas resposta inesperada{Style.RESET_ALL}")
                print(f"  - Resposta recebida: {response[:100]}...")
                
        except Exception as e:
            print(f"{Fore.RED}✗ Erro no Agent: {e}{Style.RESET_ALL}")
            traceback.print_exc()
    
    async def test_buffer_system(self):
        """Testa sistema de buffer"""
        print(f"\n{Fore.YELLOW}7. Testando Message Buffer...{Style.RESET_ALL}")
        
        try:
            if not message_buffer_service.enabled:
                print(f"{Fore.YELLOW}⚠ Buffer desabilitado no .env{Style.RESET_ALL}")
                return
            
            # Teste simples
            test_phone = "5511999999999"
            test_callback_called = False
            
            async def test_callback(messages):
                nonlocal test_callback_called
                test_callback_called = True
            
            # Adicionar mensagem
            added = await message_buffer_service.add_message(
                phone=test_phone,
                message_data={
                    "id": "test_msg",
                    "content": "Teste de buffer",
                    "type": "text",
                    "timestamp": datetime.now().isoformat()
                },
                process_callback=test_callback
            )
            
            if added:
                # Limpar buffer
                await message_buffer_service.clear_buffer(test_phone)
                print(f"{Fore.GREEN}✓ Message Buffer funcionando!{Style.RESET_ALL}")
                print(f"  - Timeout: {message_buffer_service.timeout_seconds}s")
                self.results["buffer"] = True
            else:
                print(f"{Fore.RED}✗ Buffer não aceitou mensagem{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}✗ Erro no Buffer: {e}{Style.RESET_ALL}")
    
    async def test_knowledge_base(self):
        """Testa base de conhecimento"""
        print(f"\n{Fore.YELLOW}8. Testando Knowledge Base...{Style.RESET_ALL}")
        
        try:
            # Importar a versão simplificada
            from agents.knowledge.solarprime_knowledge_simple import SolarPrimeKnowledgeSimple
            
            knowledge = SolarPrimeKnowledgeSimple()
            await knowledge.load_from_supabase()
            
            # Verificar se carregou dados
            if knowledge.initialized:
                print(f"{Fore.GREEN}✓ Knowledge Base carregada!{Style.RESET_ALL}")
                
                # Teste de busca
                results = await knowledge.get_relevant_knowledge("energia solar", max_results=1)
                if results:
                    print(f"  - Documentos encontrados")
                    print(f"  - Total de itens: {len(knowledge.knowledge_items)}")
                self.results["knowledge"] = True
            else:
                print(f"{Fore.RED}✗ Knowledge Base não inicializou{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}✗ Erro na Knowledge Base: {e}{Style.RESET_ALL}")
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}RESUMO DOS TESTES{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        total = len(self.results)
        passed = sum(1 for v in self.results.values() if v)
        
        for component, status in self.results.items():
            icon = "✓" if status else "✗"
            color = Fore.GREEN if status else Fore.RED
            print(f"{color}{icon} {component.upper()}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Total: {passed}/{total} componentes funcionando{Style.RESET_ALL}")
        
        if passed == total:
            print(f"\n{Fore.GREEN}🎉 SISTEMA V2 TOTALMENTE FUNCIONAL!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️  Alguns componentes precisam de atenção{Style.RESET_ALL}")
        
        # Recomendações
        if not self.results["redis"]:
            print(f"\n{Fore.YELLOW}→ Redis: Execute 'redis-server' para iniciar{Style.RESET_ALL}")
        
        if not self.results["supabase"] or not self.results["pgvector"]:
            print(f"\n{Fore.YELLOW}→ Supabase: Verifique as credenciais no .env{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}→ Execute: psql $SUPABASE_DATABASE_URL < scripts/supabase_complete_setup.sql{Style.RESET_ALL}")
        
        if not self.results["openai"]:
            print(f"\n{Fore.YELLOW}→ OpenAI: Verifique se a API key tem créditos{Style.RESET_ALL}")
        
        if not self.results["gemini"]:
            print(f"\n{Fore.YELLOW}→ Gemini: Verifique a API key no .env{Style.RESET_ALL}")


async def main():
    """Executa todos os testes"""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🧪 TESTE COMPLETO DO SISTEMA V2{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    
    tester = SystemTester()
    
    # Executar testes
    await tester.test_redis_connection()
    await tester.test_supabase_connection()
    await tester.test_pgvector_connection()
    await tester.test_openai_connection()
    await tester.test_gemini_connection()
    await tester.test_agent_initialization()
    await tester.test_buffer_system()
    await tester.test_knowledge_base()
    
    # Resumo
    tester.print_summary()
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Executar testes
    asyncio.run(main())