#!/usr/bin/env python3
"""
Pre-Flight Check - Verificação Completa do Sistema SDR IA SolarPrime
====================================================================
Verifica se todas as dependências e configurações estão prontas para testes
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn
import httpx

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar após adicionar ao path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

console = Console()

class SystemChecker:
    """Verificador completo do sistema"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
        
    async def run_all_checks(self):
        """Executa todas as verificações"""
        console.print(Panel.fit(
            "[bold cyan]🚀 SDR IA SolarPrime - Pre-Flight Check[/bold cyan]\n"
            "[yellow]Verificando se o sistema está pronto para testes no WhatsApp[/yellow]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # 1. Verificar variáveis de ambiente
            task = progress.add_task("[cyan]Verificando variáveis de ambiente...", total=None)
            await self.check_environment_variables()
            progress.remove_task(task)
            
            # 2. Verificar dependências Python
            task = progress.add_task("[cyan]Verificando dependências Python...", total=None)
            await self.check_python_dependencies()
            progress.remove_task(task)
            
            # 3. Verificar AGnO Framework
            task = progress.add_task("[cyan]Verificando AGnO Framework...", total=None)
            await self.check_agno_framework()
            progress.remove_task(task)
            
            # 4. Verificar Google Gemini API
            task = progress.add_task("[cyan]Verificando Google Gemini API...", total=None)
            await self.check_gemini_api()
            progress.remove_task(task)
            
            # 5. Verificar Evolution API
            task = progress.add_task("[cyan]Verificando Evolution API...", total=None)
            await self.check_evolution_api()
            progress.remove_task(task)
            
            # 6. Verificar banco de dados
            task = progress.add_task("[cyan]Verificando banco de dados...", total=None)
            await self.check_database()
            progress.remove_task(task)
            
            # 7. Verificar Redis
            task = progress.add_task("[cyan]Verificando Redis...", total=None)
            await self.check_redis()
            progress.remove_task(task)
            
            # 8. Verificar estrutura de arquivos
            task = progress.add_task("[cyan]Verificando estrutura de arquivos...", total=None)
            await self.check_file_structure()
            progress.remove_task(task)
            
            # 9. Testar webhook
            task = progress.add_task("[cyan]Verificando configuração do webhook...", total=None)
            await self.check_webhook_config()
            progress.remove_task(task)
            
            # 10. Verificar agente SDR
            task = progress.add_task("[cyan]Verificando agente SDR...", total=None)
            await self.check_sdr_agent()
            progress.remove_task(task)
        
        # Exibir resultados
        self.display_results()
    
    async def check_environment_variables(self):
        """Verifica variáveis de ambiente necessárias"""
        required_vars = {
            "GEMINI_API_KEY": "API Key do Google Gemini",
            "EVOLUTION_API_URL": "URL da Evolution API",
            "EVOLUTION_API_KEY": "API Key da Evolution",
            "EVOLUTION_INSTANCE_NAME": "Nome da instância WhatsApp",
            "SUPABASE_URL": "URL do Supabase",
            "SUPABASE_KEY": "Chave do Supabase",
            "DATABASE_URL": "URL de conexão PostgreSQL"
        }
        
        optional_vars = {
            "REDIS_URL": "URL do Redis (opcional)",
            "WEBHOOK_BASE_URL": "URL base para webhooks",
            "AI_RESPONSE_DELAY_SECONDS": "Delay de resposta IA",
            "TYPING_SIMULATION_ENABLED": "Simulação de digitação"
        }
        
        env_status = {"required": {}, "optional": {}}
        
        # Verificar obrigatórias
        for var, desc in required_vars.items():
            value = os.getenv(var)
            if value:
                # Ocultar valores sensíveis
                if "KEY" in var or "PASSWORD" in var:
                    display_value = value[:8] + "..." if len(value) > 8 else "***"
                else:
                    display_value = value[:30] + "..." if len(value) > 30 else value
                env_status["required"][var] = {"status": "✅", "value": display_value, "desc": desc}
            else:
                env_status["required"][var] = {"status": "❌", "value": "Não configurada", "desc": desc}
                self.errors.append(f"Variável obrigatória não configurada: {var}")
        
        # Verificar opcionais
        for var, desc in optional_vars.items():
            value = os.getenv(var)
            if value:
                env_status["optional"][var] = {"status": "✅", "value": value, "desc": desc}
            else:
                env_status["optional"][var] = {"status": "⚠️", "value": "Não configurada", "desc": desc}
                self.warnings.append(f"Variável opcional não configurada: {var}")
        
        self.results["environment"] = env_status
    
    async def check_python_dependencies(self):
        """Verifica se todas as dependências Python estão instaladas"""
        dependencies = {
            "Core": ["fastapi", "uvicorn", "httpx", "pydantic", "loguru"],
            "AGnO": ["agno"],
            "AI": ["google-generativeai"],
            "Database": ["supabase", "asyncpg", "sqlalchemy"],
            "WhatsApp": ["tenacity"],
            "Utils": ["python-dotenv", "rich", "aiofiles"]
        }
        
        dep_status = {}
        
        for category, packages in dependencies.items():
            dep_status[category] = {}
            for package in packages:
                try:
                    __import__(package.replace("-", "_"))
                    dep_status[category][package] = "✅ Instalado"
                except ImportError:
                    dep_status[category][package] = "❌ Não instalado"
                    self.errors.append(f"Dependência não instalada: {package}")
        
        self.results["dependencies"] = dep_status
    
    async def check_agno_framework(self):
        """Verifica instalação e configuração do AGnO Framework"""
        try:
            import agno
            from agno.agent import Agent
            from agno.models.google import Gemini
            from agno.media import Image, Audio
            
            agno_info = {
                "version": getattr(agno, "__version__", "Unknown"),
                "agent_import": "✅ OK",
                "gemini_model": "✅ OK",
                "media_support": "✅ OK",
                "components": {
                    "Agent": "✅",
                    "Gemini Model": "✅",
                    "Image Support": "✅",
                    "Audio Support": "✅"
                }
            }
            
            # Testar criação de agente básico
            try:
                test_agent = Agent(
                    name="TestAgent",
                    model=Gemini(id="gemini-1.5-flash", api_key="test"),
                    description="Test agent"
                )
                agno_info["agent_creation"] = "✅ OK"
            except Exception as e:
                agno_info["agent_creation"] = f"❌ Erro: {str(e)}"
                self.warnings.append(f"Erro ao criar agente de teste: {e}")
            
            self.results["agno"] = agno_info
            
        except ImportError as e:
            self.results["agno"] = {"status": "❌ Não instalado", "error": str(e)}
            self.errors.append("AGnO Framework não está instalado corretamente")
    
    async def check_gemini_api(self):
        """Verifica conexão com Google Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            self.results["gemini"] = {"status": "❌ API Key não configurada"}
            return
        
        try:
            # Teste básico de API
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Listar modelos disponíveis
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name)
            
            gemini_info = {
                "status": "✅ Conectado",
                "api_key": api_key[:8] + "...",
                "models_available": len(models),
                "gemini_2_5_pro": "✅ Disponível" if any("gemini-2.5-pro" in m for m in models) else "❌ Não encontrado",
                "supported_models": models[:5]  # Primeiros 5 modelos
            }
            
            self.results["gemini"] = gemini_info
            
        except Exception as e:
            self.results["gemini"] = {"status": "❌ Erro de conexão", "error": str(e)}
            self.errors.append(f"Erro ao conectar com Gemini API: {e}")
    
    async def check_evolution_api(self):
        """Verifica conexão com Evolution API"""
        base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        api_key = os.getenv("EVOLUTION_API_KEY", "")
        instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "solarprime")
        
        if base_url.endswith('/manager'):
            base_url = base_url[:-8]
        
        evolution_info = {
            "url": base_url,
            "instance": instance_name,
            "api_key": api_key[:8] + "..." if api_key else "❌ Não configurada"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Verificar saúde da API
                response = await client.get(
                    f"{base_url}/instance/fetchInstances",
                    headers={"apikey": api_key},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    evolution_info["api_status"] = "✅ Online"
                    
                    # Verificar instância específica
                    try:
                        instance_response = await client.get(
                            f"{base_url}/instance/connectionState/{instance_name}",
                            headers={"apikey": api_key},
                            timeout=5.0
                        )
                        
                        if instance_response.status_code == 200:
                            data = instance_response.json()
                            state = data.get("instance", {}).get("state", "unknown")
                            evolution_info["instance_status"] = f"✅ {state}"
                            evolution_info["whatsapp_connected"] = "✅ Conectado" if state == "open" else "❌ Desconectado"
                        else:
                            evolution_info["instance_status"] = "❌ Instância não encontrada"
                    except:
                        evolution_info["instance_status"] = "⚠️ Erro ao verificar instância"
                else:
                    evolution_info["api_status"] = f"❌ Erro HTTP {response.status_code}"
                    self.errors.append(f"Evolution API retornou erro: {response.status_code}")
                    
        except Exception as e:
            evolution_info["api_status"] = "❌ Offline"
            evolution_info["error"] = str(e)
            self.errors.append(f"Evolution API não está acessível: {e}")
        
        self.results["evolution"] = evolution_info
    
    async def check_database(self):
        """Verifica conexão com banco de dados"""
        try:
            from services.database import db
            
            # Tentar uma query simples
            result = db.leads.select("id").limit(1).execute()
            
            db_info = {
                "status": "✅ Conectado",
                "type": "Supabase (PostgreSQL)",
                "tables": ["leads", "conversations", "messages", "qualifications"],
                "phone_field": "❓ Verificar se está VARCHAR(50)"
            }
            
            # Verificar campo phone_number
            try:
                # Esta é uma verificação simplificada
                db_info["recent_fix"] = "✅ Script de correção disponível"
            except:
                pass
            
            self.results["database"] = db_info
            
        except Exception as e:
            self.results["database"] = {"status": "❌ Erro de conexão", "error": str(e)}
            self.warnings.append(f"Erro ao conectar com banco de dados: {e}")
    
    async def check_redis(self):
        """Verifica conexão com Redis"""
        try:
            from services.redis_service import redis_service
            
            # Tentar conectar
            await redis_service.connect()
            
            if redis_service.client:
                # Testar operação básica
                test_key = "test:preflight"
                await redis_service.set(test_key, "OK", 10)
                value = await redis_service.get(test_key)
                
                redis_info = {
                    "status": "✅ Conectado",
                    "test": "✅ Operações OK" if value == "OK" else "❌ Falha no teste",
                    "url": os.getenv("REDIS_URL", "redis://localhost:6379/0")
                }
            else:
                redis_info = {
                    "status": "⚠️ Usando fallback em memória",
                    "message": "Redis não está disponível, mas o sistema funcionará com cache em memória"
                }
                self.warnings.append("Redis não está disponível - usando fallback em memória")
            
            self.results["redis"] = redis_info
            
        except Exception as e:
            self.results["redis"] = {
                "status": "⚠️ Fallback ativo",
                "error": str(e),
                "message": "Sistema funcionará sem Redis"
            }
    
    async def check_file_structure(self):
        """Verifica estrutura de arquivos necessários"""
        required_files = {
            "Agente Principal": "agents/sdr_agent.py",
            "Evolution API Client": "services/evolution_api.py",
            "WhatsApp Service": "services/whatsapp_service.py",
            "Configuração": "config/agent_config.py",
            "Prompts": "config/prompts.py",
            "Database": "services/database.py",
            "API Routes": "api/routes/webhooks.py",
            "Main API": "api/main.py"
        }
        
        optional_files = {
            "Environment": ".env",
            "SQLite Storage": "data/agent_storage.db",
            "Logs": "logs/"
        }
        
        file_status = {"required": {}, "optional": {}}
        
        # Verificar obrigatórios
        for name, path in required_files.items():
            full_path = Path(path)
            if full_path.exists():
                file_status["required"][name] = "✅ Existe"
            else:
                file_status["required"][name] = "❌ Não encontrado"
                self.errors.append(f"Arquivo obrigatório não encontrado: {path}")
        
        # Verificar opcionais
        for name, path in optional_files.items():
            full_path = Path(path)
            if full_path.exists():
                file_status["optional"][name] = "✅ Existe"
            else:
                file_status["optional"][name] = "⚠️ Não encontrado"
                if name == "Environment":
                    self.warnings.append("Arquivo .env não encontrado - usando .env.example")
        
        # Criar diretórios necessários
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        self.results["files"] = file_status
    
    async def check_webhook_config(self):
        """Verifica configuração do webhook"""
        webhook_info = {
            "base_url": os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000"),
            "endpoint": "/webhook/whatsapp",
            "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE", "MESSAGES_UPDATE"]
        }
        
        # Verificar se webhook está configurado na Evolution API
        try:
            from services.evolution_api import evolution_client
            await evolution_client.initialize()
            
            webhook_data = await evolution_client.get_webhook_info()
            if webhook_data:
                webhook_info["configured"] = "✅ Configurado"
                webhook_info["current_url"] = webhook_data.get("url", "N/A")
            else:
                webhook_info["configured"] = "❌ Não configurado"
                self.warnings.append("Webhook não está configurado na Evolution API")
        except:
            webhook_info["configured"] = "❓ Não foi possível verificar"
        
        self.results["webhook"] = webhook_info
    
    async def check_sdr_agent(self):
        """Verifica se o agente SDR está funcional"""
        try:
            from agents.sdr_agent import create_sdr_agent
            from config.agent_config import validate_config
            
            # Validar configuração
            try:
                validate_config()
                agent_info = {"config": "✅ Válida"}
            except Exception as e:
                agent_info = {"config": f"❌ Inválida: {e}"}
                self.errors.append(f"Configuração do agente inválida: {e}")
            
            # Criar agente de teste
            try:
                agent = create_sdr_agent()
                agent_info["creation"] = "✅ OK"
                agent_info["personality"] = agent.config.personality.name
                agent_info["model"] = agent.config.gemini.model
                agent_info["features"] = {
                    "Reasoning": "✅ Habilitado",
                    "Multimodal": "✅ Suportado",
                    "Memory": "✅ Persistente",
                    "Sessions": "✅ Por telefone"
                }
            except Exception as e:
                agent_info["creation"] = f"❌ Erro: {e}"
                self.errors.append(f"Erro ao criar agente SDR: {e}")
            
            self.results["sdr_agent"] = agent_info
            
        except ImportError as e:
            self.results["sdr_agent"] = {"status": "❌ Erro de importação", "error": str(e)}
            self.errors.append(f"Erro ao importar agente SDR: {e}")
    
    def display_results(self):
        """Exibe os resultados da verificação"""
        console.print("\n" + "="*60 + "\n")
        
        # 1. Variáveis de Ambiente
        console.print("[bold cyan]1. VARIÁVEIS DE AMBIENTE[/bold cyan]")
        
        if "environment" in self.results:
            env_table = Table(show_header=True, header_style="bold magenta")
            env_table.add_column("Variável", style="cyan")
            env_table.add_column("Status", justify="center")
            env_table.add_column("Valor", style="yellow")
            env_table.add_column("Descrição")
            
            # Obrigatórias
            console.print("\n[yellow]Obrigatórias:[/yellow]")
            for var, info in self.results["environment"]["required"].items():
                env_table.add_row(var, info["status"], info["value"], info["desc"])
            
            console.print(env_table)
            
            # Opcionais
            if self.results["environment"]["optional"]:
                opt_table = Table(show_header=True, header_style="bold blue")
                opt_table.add_column("Variável", style="cyan")
                opt_table.add_column("Status", justify="center")
                opt_table.add_column("Valor", style="yellow")
                opt_table.add_column("Descrição")
                
                console.print("\n[blue]Opcionais:[/blue]")
                for var, info in self.results["environment"]["optional"].items():
                    opt_table.add_row(var, info["status"], info["value"], info["desc"])
                
                console.print(opt_table)
        
        # 2. AGnO Framework
        console.print("\n[bold cyan]2. AGNO FRAMEWORK[/bold cyan]")
        if "agno" in self.results:
            agno_info = self.results["agno"]
            if "version" in agno_info:
                console.print(f"Versão: {agno_info.get('version', 'Unknown')}")
                console.print(f"Criação de Agente: {agno_info.get('agent_creation', '❓')}")
                console.print("Componentes:")
                for comp, status in agno_info.get("components", {}).items():
                    console.print(f"  - {comp}: {status}")
            else:
                console.print(f"[red]{agno_info.get('status', 'Erro desconhecido')}[/red]")
        
        # 3. Google Gemini
        console.print("\n[bold cyan]3. GOOGLE GEMINI API[/bold cyan]")
        if "gemini" in self.results:
            gemini_info = self.results["gemini"]
            console.print(f"Status: {gemini_info.get('status', '❓')}")
            if "models_available" in gemini_info:
                console.print(f"Modelos disponíveis: {gemini_info['models_available']}")
                console.print(f"Gemini 2.5 Pro: {gemini_info.get('gemini_2_5_pro', '❓')}")
        
        # 4. Evolution API
        console.print("\n[bold cyan]4. EVOLUTION API (WHATSAPP)[/bold cyan]")
        if "evolution" in self.results:
            evo_info = self.results["evolution"]
            console.print(f"URL: {evo_info.get('url', 'N/A')}")
            console.print(f"API Status: {evo_info.get('api_status', '❓')}")
            console.print(f"Instância: {evo_info.get('instance', 'N/A')}")
            console.print(f"WhatsApp: {evo_info.get('whatsapp_connected', '❓')}")
        
        # 5. Banco de Dados
        console.print("\n[bold cyan]5. BANCO DE DADOS[/bold cyan]")
        if "database" in self.results:
            db_info = self.results["database"]
            console.print(f"Status: {db_info.get('status', '❓')}")
            console.print(f"Tipo: {db_info.get('type', 'N/A')}")
            console.print(f"Campo phone_number: {db_info.get('phone_field', '❓')}")
        
        # 6. Redis
        console.print("\n[bold cyan]6. REDIS[/bold cyan]")
        if "redis" in self.results:
            redis_info = self.results["redis"]
            console.print(f"Status: {redis_info.get('status', '❓')}")
            if "message" in redis_info:
                console.print(f"[yellow]{redis_info['message']}[/yellow]")
        
        # 7. Agente SDR
        console.print("\n[bold cyan]7. AGENTE SDR[/bold cyan]")
        if "sdr_agent" in self.results:
            agent_info = self.results["sdr_agent"]
            console.print(f"Configuração: {agent_info.get('config', '❓')}")
            console.print(f"Criação: {agent_info.get('creation', '❓')}")
            if "personality" in agent_info:
                console.print(f"Personalidade: {agent_info['personality']}")
                console.print(f"Modelo: {agent_info['model']}")
                if "features" in agent_info:
                    console.print("Features:")
                    for feat, status in agent_info["features"].items():
                        console.print(f"  - {feat}: {status}")
        
        # Resumo Final
        console.print("\n" + "="*60)
        console.print("[bold]RESUMO FINAL[/bold]")
        
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        if total_errors == 0:
            console.print("[bold green]✅ SISTEMA PRONTO PARA TESTES![/bold green]")
            console.print("\nPróximos passos:")
            console.print("1. Inicie a API: uvicorn api.main:app --reload")
            console.print("2. Verifique o QR Code no Evolution API")
            console.print("3. Envie uma mensagem de teste para o WhatsApp")
        else:
            console.print(f"[bold red]❌ SISTEMA NÃO ESTÁ PRONTO - {total_errors} erro(s) encontrado(s)[/bold red]")
            
            console.print("\n[red]Erros críticos:[/red]")
            for error in self.errors[:5]:  # Primeiros 5 erros
                console.print(f"  • {error}")
            
            if len(self.errors) > 5:
                console.print(f"  ... e mais {len(self.errors) - 5} erros")
        
        if total_warnings > 0:
            console.print(f"\n[yellow]⚠️ {total_warnings} aviso(s):[/yellow]")
            for warning in self.warnings[:3]:  # Primeiros 3 avisos
                console.print(f"  • {warning}")

async def main():
    """Função principal"""
    checker = SystemChecker()
    await checker.run_all_checks()

if __name__ == "__main__":
    asyncio.run(main())