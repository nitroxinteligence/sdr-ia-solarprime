#!/usr/bin/env python3
"""
Atualiza webhook para URL de produção
=====================================
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

async def update_webhook_production():
    """Atualiza webhook para URL de produção"""
    
    base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "Teste-Agente")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    console.print(Panel.fit(
        "[bold green]🚀 Configurar Webhook para Produção[/bold green]",
        border_style="green"
    ))
    
    console.print("\n[cyan]Cole a URL do seu deploy (Railway/Render/VPS):[/cyan]")
    console.print("[dim]Exemplo: https://sdr-ia.railway.app[/dim]")
    
    production_url = input("\nURL de produção: ").strip()
    
    if not production_url:
        console.print("[red]❌ URL não pode estar vazia![/red]")
        return
    
    # Garantir que tem https
    if not production_url.startswith("http"):
        production_url = f"https://{production_url}"
    
    # Remover barra final se houver
    production_url = production_url.rstrip("/")
    
    webhook_url = f"{production_url}/webhook/whatsapp"
    
    console.print(f"\n[yellow]Configurando webhook: {webhook_url}[/yellow]")
    
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
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                console.print("\n[bold green]✅ Webhook configurado com sucesso![/bold green]")
                
                # Verificar configuração
                check_response = await client.get(
                    f"{base_url}/webhook/find/{instance_name}",
                    headers={"apikey": api_key}
                )
                
                if check_response.status_code == 200:
                    data = check_response.json()
                    console.print(f"\n[cyan]Detalhes do Webhook:[/cyan]")
                    console.print(f"URL: {data.get('url', 'N/A')}")
                    console.print(f"Eventos: {', '.join(data.get('events', []))}")
                    console.print(f"Status: {'✅ Ativo' if data.get('enabled', False) else '❌ Inativo'}")
                
                console.print("\n[bold green]🎉 PRONTO PARA PRODUÇÃO![/bold green]")
                console.print("\n[cyan]Teste enviando uma mensagem no WhatsApp![/cyan]")
                
                # Salvar URL em .env.production
                console.print("\n[yellow]Salvando configuração de produção...[/yellow]")
                
                with open(".env.production", "w") as f:
                    f.write(f"# Configuração de Produção\n")
                    f.write(f"WEBHOOK_BASE_URL={production_url}\n")
                    f.write(f"PRODUCTION_URL={production_url}\n")
                    f.write(f"# Webhook URL: {webhook_url}\n")
                
                console.print("[green]✅ Configuração salva em .env.production[/green]")
                
            else:
                console.print(f"[red]❌ Erro ao configurar webhook: {response.text}[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Erro: {str(e)}[/red]")

if __name__ == "__main__":
    asyncio.run(update_webhook_production())