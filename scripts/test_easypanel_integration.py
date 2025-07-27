#!/usr/bin/env python3
"""
Test EasyPanel Integration
=========================
Script completo para testar a integração do SDR IA com Evolution API no EasyPanel.
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
import json

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

console = Console()


class EasyPanelTester:
    """Classe para testar integração no EasyPanel"""
    
    def __init__(self):
        self.evolution_url = os.getenv("EVOLUTION_API_URL", "")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
        self.webhook_base_url = os.getenv("WEBHOOK_BASE_URL", "")
        
        # Remover /manager se existir
        if self.evolution_url.endswith('/manager'):
            self.evolution_url = self.evolution_url[:-8]
        
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        self.test_results = []
    
    def add_result(self, test_name: str, success: bool, details: str = ""):
        """Adiciona resultado de teste"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_local_api(self):
        """Testa se a API local está rodando"""
        console.print("\n[bold]1️⃣ Testando API Local[/bold]")
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:8000/")
                
                if response.status_code == 200:
                    data = response.json()
                    console.print(f"[green]✅ API rodando: {data.get('status')}[/green]")
                    console.print(f"[dim]Versão: {data.get('version')} | Agent: {data.get('agent')}[/dim]")
                    self.add_result("API Local", True, "Rodando normalmente")
                else:
                    console.print(f"[red]❌ API com problema: HTTP {response.status_code}[/red]")
                    self.add_result("API Local", False, f"HTTP {response.status_code}")
        except Exception as e:
            console.print(f"[red]❌ API não está rodando: {e}[/red]")
            self.add_result("API Local", False, "Não está rodando")
            console.print("[yellow]💡 Execute: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000[/yellow]")
    
    async def test_evolution_connection(self):
        """Testa conexão com Evolution API"""
        console.print("\n[bold]2️⃣ Testando Conexão com Evolution API[/bold]")
        console.print(f"[dim]URL: {self.evolution_url}[/dim]")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.evolution_url}/instance/fetchInstances",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    console.print("[green]✅ Conectado à Evolution API[/green]")
                    self.add_result("Evolution API", True, "Conectado")
                    return True
                else:
                    console.print(f"[red]❌ Erro na Evolution API: HTTP {response.status_code}[/red]")
                    self.add_result("Evolution API", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            console.print(f"[red]❌ Não foi possível conectar: {e}[/red]")
            self.add_result("Evolution API", False, str(e))
            return False
    
    async def test_instance_exists(self):
        """Verifica se a instância existe"""
        console.print("\n[bold]3️⃣ Verificando Instância[/bold]")
        console.print(f"[dim]Nome: {self.instance_name}[/dim]")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.evolution_url}/instance/fetchInstances",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    instances = response.json()
                    
                    # Procurar instância
                    instance_found = False
                    instance_status = None
                    
                    for inst in instances:
                        inst_data = inst.get("instance", {})
                        if inst_data.get("instanceName") == self.instance_name:
                            instance_found = True
                            instance_status = inst_data.get("status")
                            break
                    
                    if instance_found:
                        if instance_status == "open":
                            console.print(f"[green]✅ Instância '{self.instance_name}' conectada ao WhatsApp[/green]")
                            self.add_result("Instância WhatsApp", True, "Conectada")
                        else:
                            console.print(f"[yellow]⚠️  Instância encontrada mas não conectada: {instance_status}[/yellow]")
                            self.add_result("Instância WhatsApp", False, f"Status: {instance_status}")
                    else:
                        console.print(f"[red]❌ Instância '{self.instance_name}' não encontrada[/red]")
                        console.print("\n[yellow]Instâncias disponíveis:[/yellow]")
                        for inst in instances:
                            name = inst.get("instance", {}).get("instanceName", "N/A")
                            console.print(f"  - {name}")
                        self.add_result("Instância WhatsApp", False, "Não encontrada")
        except Exception as e:
            console.print(f"[red]❌ Erro ao verificar instância: {e}[/red]")
            self.add_result("Instância WhatsApp", False, str(e))
    
    async def test_webhook_config(self):
        """Testa configuração do webhook"""
        console.print("\n[bold]4️⃣ Verificando Webhook[/bold]")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.evolution_url}/webhook/find/{self.instance_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    config = response.json()
                    webhook_url = config.get("url", "")
                    enabled = config.get("enabled", False)
                    
                    console.print(f"[dim]URL Configurada: {webhook_url}[/dim]")
                    console.print(f"[dim]Status: {'Ativo' if enabled else 'Inativo'}[/dim]")
                    
                    # Verificar se está usando comunicação interna
                    if webhook_url and "sdr-ia" in webhook_url and ":8000" in webhook_url:
                        console.print("[green]✅ Webhook configurado para comunicação interna[/green]")
                        self.add_result("Webhook Config", True, "Comunicação interna")
                    elif webhook_url:
                        console.print("[yellow]⚠️  Webhook configurado mas não para comunicação interna[/yellow]")
                        self.add_result("Webhook Config", False, "Não usa comunicação interna")
                    else:
                        console.print("[red]❌ Webhook não configurado[/red]")
                        self.add_result("Webhook Config", False, "Não configurado")
                else:
                    console.print("[red]❌ Webhook não encontrado[/red]")
                    self.add_result("Webhook Config", False, "Não encontrado")
        except Exception as e:
            console.print(f"[red]❌ Erro ao verificar webhook: {e}[/red]")
            self.add_result("Webhook Config", False, str(e))
    
    async def test_webhook_endpoint(self):
        """Testa endpoint do webhook localmente"""
        console.print("\n[bold]5️⃣ Testando Endpoint do Webhook[/bold]")
        
        test_payload = {
            "event": "TEST_EVENT",
            "instance": self.instance_name,
            "data": {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    "http://localhost:8000/webhook/whatsapp",
                    json=test_payload
                )
                
                if response.status_code == 200:
                    console.print("[green]✅ Webhook endpoint respondendo[/green]")
                    self.add_result("Webhook Endpoint", True, "Respondendo")
                else:
                    console.print(f"[red]❌ Webhook retornou: HTTP {response.status_code}[/red]")
                    self.add_result("Webhook Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            console.print(f"[red]❌ Erro ao testar webhook: {e}[/red]")
            self.add_result("Webhook Endpoint", False, str(e))
    
    async def simulate_whatsapp_message(self):
        """Simula uma mensagem do WhatsApp"""
        console.print("\n[bold]6️⃣ Simulando Mensagem do WhatsApp[/bold]")
        
        message_payload = {
            "event": "MESSAGES_UPSERT",
            "instance": self.instance_name,
            "data": {
                "key": {
                    "id": f"TEST_{int(datetime.now().timestamp())}",
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "conversation": "Olá! Quero saber sobre energia solar"
                },
                "messageTimestamp": int(datetime.now().timestamp()),
                "pushName": "Cliente Teste EasyPanel"
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "http://localhost:8000/webhook/whatsapp",
                    json=message_payload
                )
                
                if response.status_code == 200:
                    console.print("[green]✅ Mensagem simulada processada[/green]")
                    self.add_result("Simulação WhatsApp", True, "Processada")
                    console.print("[dim]Verifique os logs para ver o processamento[/dim]")
                else:
                    console.print(f"[red]❌ Erro ao processar: HTTP {response.status_code}[/red]")
                    self.add_result("Simulação WhatsApp", False, f"HTTP {response.status_code}")
        except Exception as e:
            console.print(f"[red]❌ Erro na simulação: {e}[/red]")
            self.add_result("Simulação WhatsApp", False, str(e))
    
    def show_results(self):
        """Mostra resumo dos testes"""
        console.print("\n")
        
        # Criar tabela de resultados
        table = Table(title="📊 Resumo dos Testes")
        table.add_column("Teste", style="cyan")
        table.add_column("Resultado", style="green")
        table.add_column("Detalhes", style="dim")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        
        for result in self.test_results:
            status = "[green]✅ Passou[/green]" if result["success"] else "[red]❌ Falhou[/red]"
            table.add_row(result["test"], status, result["details"])
        
        console.print(table)
        
        # Mostrar estatísticas
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        console.print(f"\n[bold]📈 Taxa de Sucesso: {success_rate:.0f}% ({passed_tests}/{total_tests})[/bold]")
        
        # Recomendações baseadas nos resultados
        if success_rate < 100:
            console.print("\n[yellow]💡 Recomendações:[/yellow]")
            
            for result in self.test_results:
                if not result["success"]:
                    if result["test"] == "API Local":
                        console.print("• Inicie a API: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
                    elif result["test"] == "Evolution API":
                        console.print("• Verifique se a Evolution API está rodando no EasyPanel")
                        console.print("• Confirme a URL e API Key no .env")
                    elif result["test"] == "Instância WhatsApp":
                        console.print("• Execute: python scripts/list_evolution_instances.py")
                        console.print("• Verifique o nome correto da instância")
                    elif result["test"] == "Webhook Config":
                        console.print("• Execute: python scripts/configure_webhook_easypanel.py")
                        console.print("• Configure o webhook para comunicação interna")
        else:
            console.print("\n[green]🎉 Todos os testes passaram! Sistema pronto para deploy![/green]")
            
            # Instruções finais
            console.print("\n")
            console.print(Panel(
                "[bold green]🚀 Próximos Passos para Deploy no EasyPanel:[/bold green]\n\n"
                "1. Faça commit das alterações\n"
                "2. No EasyPanel, crie o serviço 'sdr-ia'\n"
                "3. Configure as variáveis de ambiente do .env.easypanel\n"
                "4. Faça o deploy usando o Dockerfile\n"
                "5. Aguarde o build e inicialização\n"
                "6. Teste enviando mensagem no WhatsApp!",
                border_style="green"
            ))


async def main():
    """Função principal"""
    
    console.print(Panel.fit(
        "[bold]🧪 SDR IA SolarPrime - Teste de Integração EasyPanel[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    # Criar testador
    tester = EasyPanelTester()
    
    # Executar testes
    await tester.test_local_api()
    
    # Só continuar se API local estiver rodando
    if any(r["test"] == "API Local" and r["success"] for r in tester.test_results):
        if await tester.test_evolution_connection():
            await tester.test_instance_exists()
            await tester.test_webhook_config()
        
        await tester.test_webhook_endpoint()
        await tester.simulate_whatsapp_message()
    
    # Mostrar resultados
    tester.show_results()


if __name__ == "__main__":
    asyncio.run(main())