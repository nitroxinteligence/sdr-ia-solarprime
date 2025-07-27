#!/usr/bin/env python3
"""
Test Webhook Directly
====================
Testa o webhook diretamente com a Evolution API.
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
        "[bold]🔍 Teste Direto do Webhook - SDR IA SolarPrime[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    # Configurações
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    console.print(f"\n[bold]📋 Configuração:[/bold]")
    console.print(f"[yellow]URL:[/yellow] {base_url}")
    console.print(f"[yellow]Instance:[/yellow] {instance_name}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Buscar todas as instâncias
        console.print("\n[bold]1️⃣ Buscando instâncias...[/bold]")
        
        try:
            response = await client.get(
                f"{base_url}/instance/fetchInstances",
                headers=headers
            )
            
            if response.status_code == 200:
                instances = response.json()
                console.print(f"[green]✅ Resposta recebida[/green]")
                
                # Mostrar estrutura bruta
                console.print("\n[dim]Estrutura da resposta:[/dim]")
                console.print(json.dumps(instances, indent=2)[:1000] + "...")
                
                # Tentar encontrar o nome
                if instances and len(instances) > 0:
                    first = instances[0]
                    
                    # Diferentes tentativas de extrair o nome
                    possible_names = []
                    
                    if isinstance(first, dict):
                        # Tentar instance.instanceName
                        if "instance" in first:
                            inst = first["instance"]
                            if isinstance(inst, dict) and "instanceName" in inst:
                                possible_names.append(inst["instanceName"])
                        
                        # Tentar diretamente
                        if "instanceName" in first:
                            possible_names.append(first["instanceName"])
                        
                        if "name" in first:
                            possible_names.append(first["name"])
                    
                    console.print(f"\n[yellow]Nomes encontrados:[/yellow] {possible_names}")
                    
                    # Usar o primeiro nome válido
                    real_name = next((n for n in possible_names if n and n != "N/A"), None)
                    
                    if real_name:
                        console.print(f"\n[green]✅ Nome da instância: '{real_name}'[/green]")
                        
                        if real_name != instance_name:
                            console.print(f"[red]⚠️ Nome diferente do configurado![/red]")
                            console.print(f"[yellow]Use: EVOLUTION_INSTANCE_NAME={real_name}[/yellow]")
                        
                        instance_name = real_name
                    else:
                        # Se não encontrou, usar o nome da imagem
                        console.print("\n[yellow]⚠️ Nome não encontrado na estrutura[/yellow]")
                        console.print("[yellow]Baseado na imagem, o nome é: SDR IA SolarPrime[/yellow]")
                        instance_name = "SDR IA SolarPrime"
                
        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")
        
        # 2. Verificar webhook atual
        console.print(f"\n[bold]2️⃣ Verificando webhook de '{instance_name}'...[/bold]")
        
        try:
            response = await client.get(
                f"{base_url}/webhook/find/{instance_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                webhook = response.json()
                console.print("[green]✅ Webhook encontrado[/green]")
                console.print(f"URL atual: {webhook.get('url')}")
                console.print(f"Status: {'Ativo' if webhook.get('enabled') else 'Inativo'}")
                
                # Se está apontando para localhost, precisamos corrigir
                if "localhost" in webhook.get('url', ''):
                    console.print("\n[yellow]⚠️ Webhook está apontando para localhost![/yellow]")
                    console.print("[yellow]Para EasyPanel, precisa usar comunicação interna[/yellow]")
                    
                    # Perguntar se quer corrigir
                    console.print("\n[bold]Deseja configurar para EasyPanel? (s/n):[/bold] ", end="")
                    if input().lower() == 's':
                        webhook_url = "http://sdr-ia:8000/webhook/whatsapp"
                        
                        webhook_config = {
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
                        
                        response = await client.post(
                            f"{base_url}/webhook/set/{instance_name}",
                            headers=headers,
                            json=webhook_config
                        )
                        
                        if response.status_code == 200:
                            console.print(f"\n[green]✅ Webhook atualizado para: {webhook_url}[/green]")
                        else:
                            console.print(f"[red]❌ Erro: {response.status_code}[/red]")
                            console.print(f"[dim]{response.text}[/dim]")
                
            else:
                console.print(f"[red]❌ Erro ao buscar webhook: {response.status_code}[/red]")
                console.print(f"[dim]{response.text}[/dim]")
                
        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")
        
        # 3. Testar conexão
        console.print(f"\n[bold]3️⃣ Testando conexão da instância...[/bold]")
        
        try:
            response = await client.get(
                f"{base_url}/instance/connectionState/{instance_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                state = response.json()
                console.print(f"[green]✅ Estado: {state.get('state')}[/green]")
            else:
                console.print(f"[yellow]⚠️ Não foi possível verificar estado[/yellow]")
                
        except Exception as e:
            console.print(f"[dim]Erro: {e}[/dim]")
        
        # 4. Resumo final
        console.print("\n")
        console.print(Panel(
            "[bold]📝 Resumo:[/bold]\n\n"
            f"✅ Nome correto da instância: [yellow]SDR IA SolarPrime[/yellow]\n"
            f"✅ Webhook deve apontar para: [yellow]http://sdr-ia:8000/webhook/whatsapp[/yellow]\n\n"
            "[bold]Para EasyPanel:[/bold]\n"
            "1. Use comunicação interna entre serviços\n"
            "2. evolution-api → sdr-ia via rede interna\n"
            "3. Não use localhost ou IPs externos",
            border_style="green"
        ))


if __name__ == "__main__":
    asyncio.run(main())