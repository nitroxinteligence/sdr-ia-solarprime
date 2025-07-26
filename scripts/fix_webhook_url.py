#!/usr/bin/env python3
"""
Corrige a URL do webhook para usar ngrok ou URL pública
========================================================
"""

import asyncio
import os
import sys
import httpx
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
console = Console()

async def fix_webhook():
    """Corrige a URL do webhook"""
    
    base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "Teste-Agente")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    console.print(Panel.fit(
        "[bold red]🚨 PROBLEMA IDENTIFICADO![/bold red]\n\n"
        "O webhook está configurado como 'localhost:8000' mas a Evolution API\n"
        "está hospedada externamente e não consegue acessar seu localhost!",
        border_style="red"
    ))
    
    console.print("\n[bold yellow]SOLUÇÕES DISPONÍVEIS:[/bold yellow]\n")
    console.print("1. Usar ngrok para expor sua API local")
    console.print("2. Usar serveo.net (sem instalação)")
    console.print("3. Usar localtunnel")
    console.print("4. Configurar manualmente uma URL pública")
    
    choice = input("\nEscolha uma opção (1-4): ")
    
    webhook_url = None
    
    if choice == "1":
        console.print("\n[cyan]Instalando e configurando ngrok...[/cyan]")
        console.print("\n1. Instale o ngrok:")
        console.print("   brew install ngrok/ngrok/ngrok")
        console.print("\n2. Execute em outro terminal:")
        console.print("   ngrok http 8000")
        console.print("\n3. Copie a URL https que aparecer (ex: https://abc123.ngrok.io)")
        
        ngrok_url = input("\nCole a URL do ngrok aqui: ").strip()
        if ngrok_url:
            webhook_url = f"{ngrok_url}/webhook/whatsapp"
    
    elif choice == "2":
        console.print("\n[cyan]Usando serveo.net (mais fácil)...[/cyan]")
        console.print("\nExecute este comando em OUTRO terminal:")
        console.print("[bold green]ssh -R 80:localhost:8000 serveo.net[/bold green]")
        console.print("\nVocê verá algo como: 'Forwarding HTTP traffic from https://xyz.serveo.net'")
        
        serveo_url = input("\nCole a URL do serveo aqui: ").strip()
        if serveo_url:
            webhook_url = f"{serveo_url}/webhook/whatsapp"
    
    elif choice == "3":
        console.print("\n[cyan]Usando localtunnel...[/cyan]")
        console.print("\n1. Instale: npm install -g localtunnel")
        console.print("2. Execute: lt --port 8000")
        
        lt_url = input("\nCole a URL do localtunnel aqui: ").strip()
        if lt_url:
            webhook_url = f"{lt_url}/webhook/whatsapp"
    
    elif choice == "4":
        webhook_url = input("\nDigite a URL pública completa do webhook: ").strip()
    
    if webhook_url:
        console.print(f"\n[yellow]Atualizando webhook para: {webhook_url}[/yellow]")
        
        async with httpx.AsyncClient() as client:
            try:
                # Atualizar webhook
                response = await client.post(
                    f"{base_url}/webhook/set/{instance_name}",
                    headers={"apikey": api_key},
                    json={
                        "webhook": {
                            "url": webhook_url,
                            "events": [
                                "MESSAGES_UPSERT",
                                "MESSAGES_UPDATE", 
                                "CONNECTION_UPDATE",
                                "SEND_MESSAGE"
                            ],
                            "webhookByEvents": False,
                            "webhookBase64": False
                        }
                    }
                )
                
                if response.status_code == 200:
                    console.print("[bold green]✅ Webhook atualizado com sucesso![/bold green]")
                    console.print(f"\nWebhook URL: {webhook_url}")
                    console.print("\n[cyan]TESTE AGORA: Envie uma mensagem no WhatsApp![/cyan]")
                    
                    # Verificar configuração
                    check_response = await client.get(
                        f"{base_url}/webhook/find/{instance_name}",
                        headers={"apikey": api_key}
                    )
                    
                    if check_response.status_code == 200:
                        data = check_response.json()
                        console.print(f"\n[dim]Webhook ID: {data.get('id', 'N/A')}[/dim]")
                        console.print(f"[dim]Eventos: {', '.join(data.get('events', []))}[/dim]")
                else:
                    console.print(f"[red]Erro ao atualizar webhook: {response.text}[/red]")
                    
            except Exception as e:
                console.print(f"[red]Erro: {str(e)}[/red]")
    else:
        console.print("[red]Nenhuma URL fornecida![/red]")

if __name__ == "__main__":
    asyncio.run(fix_webhook())