#!/usr/bin/env python3
"""
Setup Evolution API for EasyPanel
=================================
Script completo para configurar a Evolution API para funcionar com EasyPanel.
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from datetime import datetime
import json

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

console = Console()


async def find_instance_name(instances: list) -> str:
    """Extrai o nome da instância da resposta da API"""
    
    for inst in instances:
        # Tentar diferentes estruturas possíveis
        if isinstance(inst, dict):
            # Estrutura 1: {"instance": {"instanceName": "nome"}}
            if "instance" in inst and isinstance(inst["instance"], dict):
                name = inst["instance"].get("instanceName")
                if name:
                    return name
            
            # Estrutura 2: {"instanceName": "nome"}
            if "instanceName" in inst:
                return inst["instanceName"]
            
            # Estrutura 3: {"name": "nome"}
            if "name" in inst:
                return inst["name"]
    
    return None


async def main():
    """Função principal"""
    
    console.print(Panel.fit(
        "[bold]🚀 SDR IA SolarPrime - Setup Evolution API para EasyPanel[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    # Verificar configurações
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    current_instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    
    if not all([base_url, api_key]):
        console.print("[red]❌ EVOLUTION_API_URL ou EVOLUTION_API_KEY não configurados[/red]")
        return
    
    # Remover /manager se existir
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    console.print(f"\n[bold]📋 Configuração Atual:[/bold]")
    console.print(f"[yellow]Evolution API URL:[/yellow] {base_url}")
    console.print(f"[yellow]Instance Name no .env:[/yellow] {current_instance_name}")
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Buscar instâncias
        console.print("\n[bold]1️⃣ Buscando instâncias...[/bold]")
        
        try:
            response = await client.get(
                f"{base_url}/instance/fetchInstances",
                headers=headers
            )
            
            if response.status_code == 200:
                instances = response.json()
                
                if instances:
                    console.print(f"[green]✅ Encontradas {len(instances)} instância(s)[/green]")
                    
                    # Encontrar nome da instância
                    instance_name = find_instance_name(instances)
                    
                    if instance_name:
                        console.print(f"\n[green]✅ Instância encontrada: '{instance_name}'[/green]")
                        
                        if instance_name != current_instance_name:
                            console.print(f"[yellow]⚠️ Nome diferente do configurado no .env![/yellow]")
                            console.print(f"[yellow]Configure: EVOLUTION_INSTANCE_NAME={instance_name}[/yellow]")
                    else:
                        console.print("[yellow]⚠️ Instância existe mas nome não identificado[/yellow]")
                        console.print("[dim]Estrutura da resposta:[/dim]")
                        console.print(json.dumps(instances[0], indent=2)[:500] + "...")
                        
                        # Permitir entrada manual
                        instance_name = Prompt.ask("\nDigite o nome da instância manualmente")
                    
                    # 2. Configurar webhook para EasyPanel
                    console.print("\n[bold]2️⃣ Configurando webhook para EasyPanel...[/bold]")
                    
                    # Nome do serviço no EasyPanel
                    sdr_service = Prompt.ask(
                        "Nome do serviço SDR IA no EasyPanel",
                        default="sdr-ia"
                    )
                    
                    webhook_url = f"http://{sdr_service}:8000/webhook/whatsapp"
                    
                    webhook_config = {
                        "url": webhook_url,
                        "enabled": True,
                        "webhook_by_events": False,
                        "events": [
                            "MESSAGES_UPSERT",
                            "MESSAGES_UPDATE",
                            "CONNECTION_UPDATE",
                            "QRCODE_UPDATED",
                            "SEND_MESSAGE",
                            "PRESENCE_UPDATE"
                        ]
                    }
                    
                    console.print(f"[dim]Configurando webhook: {webhook_url}[/dim]")
                    
                    response = await client.post(
                        f"{base_url}/webhook/set/{instance_name}",
                        headers=headers,
                        json=webhook_config
                    )
                    
                    if response.status_code == 200:
                        console.print("[green]✅ Webhook configurado com sucesso![/green]")
                    else:
                        console.print(f"[red]❌ Erro ao configurar webhook: {response.status_code}[/red]")
                        console.print(f"[dim]{response.text}[/dim]")
                    
                    # 3. Verificar conexão WhatsApp
                    console.print("\n[bold]3️⃣ Verificando conexão WhatsApp...[/bold]")
                    
                    try:
                        response = await client.get(
                            f"{base_url}/instance/connectionState/{instance_name}",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            state_data = response.json()
                            state = state_data.get("state", "unknown")
                            
                            if state == "open":
                                console.print("[green]✅ WhatsApp conectado e pronto![/green]")
                            else:
                                console.print(f"[yellow]⚠️ WhatsApp não conectado: {state}[/yellow]")
                                console.print("[dim]Conecte usando o QR Code no Evolution Manager[/dim]")
                        
                    except Exception:
                        console.print("[yellow]⚠️ Não foi possível verificar estado da conexão[/yellow]")
                    
                    # 4. Mostrar configuração final
                    console.print("\n")
                    console.print(Panel(
                        "[bold green]✅ Configuração Completa para EasyPanel:[/bold green]\n\n"
                        "[yellow]Arquivo .env.easypanel:[/yellow]\n"
                        f"EVOLUTION_API_URL=http://evolution-api:8080\n"
                        f"EVOLUTION_API_KEY={api_key}\n"
                        f"EVOLUTION_INSTANCE_NAME={instance_name}\n"
                        f"WEBHOOK_BASE_URL=http://{sdr_service}:8000\n\n"
                        "[yellow]Próximos passos:[/yellow]\n"
                        "1. Atualize o .env.easypanel com os valores acima\n"
                        "2. Faça o deploy no EasyPanel\n"
                        "3. Configure as variáveis de ambiente\n"
                        "4. Teste enviando uma mensagem no WhatsApp",
                        border_style="green"
                    ))
                    
                else:
                    console.print("[red]❌ Nenhuma instância encontrada[/red]")
                    console.print("[yellow]Crie uma instância no Evolution Manager primeiro[/yellow]")
                    
        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")
            
            # Diagnóstico adicional
            console.print("\n[yellow]💡 Diagnóstico:[/yellow]")
            console.print("1. Verifique se a Evolution API está acessível")
            console.print("2. Confirme que a API Key está correta")
            console.print("3. Teste a URL no navegador")
            console.print(f"   {base_url}/instance/fetchInstances")


if __name__ == "__main__":
    asyncio.run(main())