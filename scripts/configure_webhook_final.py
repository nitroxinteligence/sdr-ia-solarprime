#!/usr/bin/env python3
"""
Configure Webhook Final
======================
Configura o webhook para funcionar com EasyPanel.
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

load_dotenv()

console = Console()


async def main():
    """Função principal"""
    
    console.print(Panel.fit(
        "[bold]🚀 Configuração Final do Webhook para EasyPanel[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    # Configurações
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = "SDR IA SolarPrime"  # Nome correto da instância
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    console.print(f"\n[bold]📋 Configuração:[/bold]")
    console.print(f"[yellow]Evolution API:[/yellow] {base_url}")
    console.print(f"[yellow]Instance Name:[/yellow] {instance_name}")
    
    # URL do webhook para EasyPanel (comunicação interna)
    webhook_url = "http://sdr-ia:8000/webhook/whatsapp"
    
    console.print(f"\n[bold]🔧 Configurando webhook...[/bold]")
    console.print(f"[yellow]URL:[/yellow] {webhook_url}")
    console.print("[dim]Esta URL usa comunicação interna do EasyPanel[/dim]")
    
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
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{base_url}/webhook/set/{instance_name}",
                headers=headers,
                json=webhook_config
            )
            
            if response.status_code == 200:
                console.print("\n[green]✅ Webhook configurado com sucesso![/green]")
                
                # Verificar configuração
                response = await client.get(
                    f"{base_url}/webhook/find/{instance_name}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    webhook = response.json()
                    console.print(f"\n[bold]✅ Configuração atual:[/bold]")
                    console.print(f"URL: [green]{webhook.get('url')}[/green]")
                    console.print(f"Status: [green]{'Ativo' if webhook.get('enabled') else 'Inativo'}[/green]")
                    console.print(f"Eventos: [green]{len(webhook.get('events', []))} configurados[/green]")
                
            else:
                console.print(f"\n[red]❌ Erro ao configurar: {response.status_code}[/red]")
                console.print(f"[dim]{response.text}[/dim]")
                
        except Exception as e:
            console.print(f"\n[red]❌ Erro: {e}[/red]")
    
    # Mostrar configuração final para EasyPanel
    console.print("\n")
    console.print(Panel(
        "[bold green]✅ Configuração Completa para EasyPanel:[/bold green]\n\n"
        "[bold]Arquivo .env.easypanel:[/bold]\n"
        f"EVOLUTION_API_URL=http://evolution-api:8080\n"
        f"EVOLUTION_API_KEY={api_key}\n"
        f"EVOLUTION_INSTANCE_NAME=SDR IA SolarPrime\n"
        f"WEBHOOK_BASE_URL=http://sdr-ia:8000\n\n"
        "[bold]Importante:[/bold]\n"
        "• 'evolution-api' = nome do serviço Evolution API no EasyPanel\n"
        "• 'sdr-ia' = nome do serviço SDR IA no EasyPanel\n"
        "• Ambos devem estar na mesma rede Docker\n"
        "• Não use localhost ou IPs externos!",
        border_style="green"
    ))
    
    console.print("\n[bold]🚀 Próximos passos:[/bold]")
    console.print("1. Faça o deploy do SDR IA no EasyPanel")
    console.print("2. Configure as variáveis de ambiente")
    console.print("3. Certifique-se que os serviços estão na mesma rede")
    console.print("4. Teste enviando uma mensagem no WhatsApp")


if __name__ == "__main__":
    asyncio.run(main())