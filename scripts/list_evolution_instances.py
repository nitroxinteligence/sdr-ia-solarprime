#!/usr/bin/env python3
"""
List Evolution API Instances
===========================
Script para listar todas as instâncias disponíveis na Evolution API
e ajudar a identificar o nome correto da instância.
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

console = Console()


async def list_instances():
    """Lista todas as instâncias da Evolution API"""
    
    # Configurações
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    
    if not base_url or not api_key:
        console.print("[red]❌ EVOLUTION_API_URL ou EVOLUTION_API_KEY não configurados no .env[/red]")
        return
    
    # Remover /manager se existir
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    console.print(Panel.fit(
        f"[bold blue]🔍 Listando Instâncias da Evolution API[/bold blue]\n"
        f"[dim]URL: {base_url}[/dim]",
        border_style="blue"
    ))
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Buscar todas as instâncias
            with console.status("[yellow]Conectando à Evolution API...[/yellow]"):
                response = await client.get(
                    f"{base_url}/instance/fetchInstances",
                    headers=headers
                )
            
            if response.status_code == 200:
                instances = response.json()
                
                if not instances:
                    console.print("[yellow]⚠️  Nenhuma instância encontrada[/yellow]")
                    console.print("\n[dim]Você precisa criar uma instância primeiro:[/dim]")
                    console.print("[green]1. Acesse o Evolution Manager[/green]")
                    console.print("[green]2. Crie uma nova instância[/green]")
                    console.print("[green]3. Conecte ao WhatsApp via QR Code[/green]")
                    return
                
                # Criar tabela
                table = Table(title=f"📱 Instâncias Encontradas ({len(instances)})")
                table.add_column("Nome da Instância", style="cyan", no_wrap=True)
                table.add_column("Status", style="green")
                table.add_column("ID", style="dim")
                table.add_column("Integração", style="yellow")
                table.add_column("Webhook", style="blue")
                
                # Adicionar instâncias à tabela
                for instance in instances:
                    inst_data = instance.get("instance", {})
                    
                    name = inst_data.get("instanceName", "N/A")
                    status = inst_data.get("status", "unknown")
                    instance_id = inst_data.get("instanceId", "N/A")
                    integration = inst_data.get("integration", "N/A")
                    
                    # Verificar webhook
                    webhook_info = instance.get("webhook", {})
                    webhook_enabled = "✅" if webhook_info.get("enabled") else "❌"
                    
                    # Cor do status
                    if status == "open":
                        status_display = "[green]🟢 Conectado[/green]"
                    elif status == "connecting":
                        status_display = "[yellow]🟡 Conectando[/yellow]"
                    elif status == "close":
                        status_display = "[red]🔴 Desconectado[/red]"
                    else:
                        status_display = f"[dim]{status}[/dim]"
                    
                    table.add_row(
                        name,
                        status_display,
                        instance_id[:8] + "...",
                        integration,
                        webhook_enabled
                    )
                
                console.print("\n")
                console.print(table)
                
                # Mostrar configuração recomendada
                connected_instances = [
                    i for i in instances 
                    if i.get("instance", {}).get("status") == "open"
                ]
                
                if connected_instances:
                    first_instance = connected_instances[0].get("instance", {})
                    instance_name = first_instance.get("instanceName", "")
                    
                    console.print("\n")
                    console.print(Panel(
                        f"[bold green]✅ Configuração Recomendada:[/bold green]\n\n"
                        f"[yellow]EVOLUTION_INSTANCE_NAME=[/yellow]{instance_name}\n\n"
                        f"[dim]Adicione esta linha ao seu arquivo .env[/dim]",
                        border_style="green"
                    ))
                    
                    # Verificar se é diferente do configurado
                    current_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
                    if current_name and current_name != instance_name:
                        console.print(
                            f"\n[red]⚠️  ATENÇÃO: O nome configurado '[yellow]{current_name}[/yellow]' "
                            f"é diferente do nome real '[green]{instance_name}[/green]'[/red]"
                        )
                else:
                    console.print("\n[yellow]⚠️  Nenhuma instância conectada ao WhatsApp[/yellow]")
                    console.print("[dim]Conecte uma instância ao WhatsApp primeiro[/dim]")
                
            else:
                console.print(f"[red]❌ Erro ao conectar: HTTP {response.status_code}[/red]")
                console.print(f"[dim]Resposta: {response.text}[/dim]")
                
        except httpx.ConnectError:
            console.print("[red]❌ Não foi possível conectar à Evolution API[/red]")
            console.print("[dim]Verifique se a URL está correta e a API está rodando[/dim]")
        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")


async def check_webhook_config(instance_name: str):
    """Verifica a configuração do webhook para uma instância específica"""
    
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{base_url}/webhook/find/{instance_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                webhook_config = response.json()
                
                console.print("\n")
                console.print(Panel(
                    f"[bold blue]🔗 Configuração do Webhook[/bold blue]\n\n"
                    f"[yellow]URL:[/yellow] {webhook_config.get('url', 'Não configurada')}\n"
                    f"[yellow]Ativo:[/yellow] {'✅ Sim' if webhook_config.get('enabled') else '❌ Não'}\n"
                    f"[yellow]Eventos:[/yellow] {len(webhook_config.get('events', []))} configurados",
                    border_style="blue"
                ))
                
        except Exception:
            # Webhook pode não estar configurado ainda
            pass


async def main():
    """Função principal"""
    
    console.print(Panel.fit(
        "[bold]🚀 SDR IA SolarPrime - Listar Instâncias Evolution API[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    # Listar instâncias
    await list_instances()
    
    # Se houver uma instância configurada, verificar webhook
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME")
    if instance_name:
        await check_webhook_config(instance_name)
    
    console.print("\n[dim]Script finalizado.[/dim]")


if __name__ == "__main__":
    asyncio.run(main())