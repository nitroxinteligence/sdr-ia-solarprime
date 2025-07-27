#!/usr/bin/env python3
"""
Configure Webhook Correctly
==========================
Configura o webhook usando a estrutura correta da API.
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json

load_dotenv()

console = Console()


async def main():
    """Função principal"""
    
    console.print(Panel.fit(
        "[bold]🚀 Configuração Correta do Webhook para EasyPanel[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    # Configurações
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = "SDR IA SolarPrime"
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    console.print(f"\n[bold]📋 Configuração:[/bold]")
    console.print(f"[yellow]Evolution API:[/yellow] {base_url}")
    console.print(f"[yellow]Instance Name:[/yellow] {instance_name}")
    
    # URL do webhook para EasyPanel
    webhook_url = "http://sdr-ia:8000/webhook/whatsapp"
    
    console.print(f"\n[bold]🔧 Configurando webhook...[/bold]")
    console.print(f"[yellow]URL:[/yellow] {webhook_url}")
    
    # Estrutura correta para Evolution API v2
    webhook_payload = {
        "webhook": {
            "url": webhook_url,
            "enabled": True,
            "webhookByEvents": False,
            "webhookBase64": False,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "CONNECTION_UPDATE",
                "QRCODE_UPDATED",
                "SEND_MESSAGE",
                "PRESENCE_UPDATE"
            ]
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Tentar primeiro com a estrutura completa
            console.print("[dim]Tentando configurar webhook...[/dim]")
            
            response = await client.post(
                f"{base_url}/webhook/set/{instance_name}",
                headers=headers,
                json=webhook_payload
            )
            
            if response.status_code == 200:
                console.print("\n[green]✅ Webhook configurado com sucesso![/green]")
            else:
                console.print(f"[yellow]Primeira tentativa falhou: {response.status_code}[/yellow]")
                console.print(f"[dim]{response.text}[/dim]")
                
                # Tentar estrutura alternativa
                console.print("\n[dim]Tentando estrutura alternativa...[/dim]")
                
                alt_payload = {
                    "url": webhook_url,
                    "enabled": True,
                    "events": [
                        "MESSAGES_UPSERT",
                        "MESSAGES_UPDATE",
                        "CONNECTION_UPDATE",
                        "QRCODE_UPDATED",
                        "SEND_MESSAGE",
                        "PRESENCE_UPDATE"
                    ]
                }
                
                response = await client.put(
                    f"{base_url}/webhook/set/{instance_name}",
                    headers=headers,
                    json=alt_payload
                )
                
                if response.status_code == 200:
                    console.print("[green]✅ Webhook configurado com estrutura alternativa![/green]")
                else:
                    console.print(f"[red]❌ Erro na segunda tentativa: {response.status_code}[/red]")
                    console.print(f"[dim]{response.text}[/dim]")
                    
                    # Tentar via instance update
                    console.print("\n[dim]Tentando via update de instância...[/dim]")
                    
                    instance_payload = {
                        "Webhook": {
                            "url": webhook_url,
                            "enabled": True
                        }
                    }
                    
                    response = await client.put(
                        f"{base_url}/instance/update/{instance_name}",
                        headers=headers,
                        json=instance_payload
                    )
                    
                    if response.status_code == 200:
                        console.print("[green]✅ Webhook configurado via update![/green]")
                    else:
                        console.print(f"[red]❌ Todas as tentativas falharam[/red]")
            
            # Verificar configuração atual
            console.print("\n[bold]Verificando configuração atual...[/bold]")
            
            response = await client.get(
                f"{base_url}/webhook/find/{instance_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                webhook = response.json()
                console.print(f"\n[bold]✅ Webhook atual:[/bold]")
                console.print(f"URL: [green]{webhook.get('url')}[/green]")
                console.print(f"Status: [green]{'Ativo' if webhook.get('enabled') else 'Inativo'}[/green]")
                console.print(f"Eventos: [green]{len(webhook.get('events', []))} configurados[/green]")
                
                # Se ainda está com localhost, mostrar comando manual
                if "localhost" in webhook.get('url', ''):
                    console.print("\n[yellow]⚠️ Webhook ainda está com localhost![/yellow]")
                    console.print("\n[bold]Alternativa: Configure manualmente no Evolution Manager[/bold]")
                    console.print("1. Acesse: Configurations → Webhook")
                    console.print(f"2. URL: {webhook_url}")
                    console.print("3. Ative todos os eventos necessários")
                    console.print("4. Salve as configurações")
                    
        except Exception as e:
            console.print(f"\n[red]❌ Erro: {e}[/red]")
    
    # Configuração final
    console.print("\n")
    console.print(Panel(
        "[bold green]📝 Resumo Final:[/bold green]\n\n"
        "[bold]Para funcionar no EasyPanel:[/bold]\n\n"
        "1. [yellow]Configure o webhook manualmente[/yellow] no Evolution Manager:\n"
        f"   • URL: http://sdr-ia:8000/webhook/whatsapp\n"
        "   • Ative todos os eventos\n\n"
        "2. [yellow]No arquivo .env.easypanel:[/yellow]\n"
        "   EVOLUTION_API_URL=http://evolution-api:8080\n"
        "   EVOLUTION_INSTANCE_NAME=SDR IA SolarPrime\n"
        "   WEBHOOK_BASE_URL=http://sdr-ia:8000\n\n"
        "3. [yellow]Deploy no EasyPanel:[/yellow]\n"
        "   • Nome do serviço: sdr-ia\n"
        "   • Mesma rede que evolution-api\n"
        "   • Porta interna: 8000",
        border_style="green"
    ))


if __name__ == "__main__":
    asyncio.run(main())