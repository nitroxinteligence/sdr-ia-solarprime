#!/usr/bin/env python3
"""
Diagnose Evolution Instance Issues
==================================
Script para diagnosticar problemas com instâncias da Evolution API.
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from datetime import datetime
import json

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

console = Console()


async def test_evolution_api():
    """Testa conexão e endpoints da Evolution API"""
    
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    console.print(Panel.fit(
        "[bold]🔍 Diagnóstico Detalhado da Evolution API[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    console.print(f"\n[bold]📋 Configurações:[/bold]")
    console.print(f"[yellow]URL:[/yellow] {base_url}")
    console.print(f"[yellow]API Key:[/yellow] {'*' * 10}{api_key[-4:] if api_key else 'Não configurada'}")
    console.print(f"[yellow]Instance Name:[/yellow] {instance_name}")
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Testar fetchInstances
        console.print("\n[bold]1️⃣ Testando /instance/fetchInstances[/bold]")
        try:
            response = await client.get(
                f"{base_url}/instance/fetchInstances",
                headers=headers
            )
            
            console.print(f"[dim]Status: {response.status_code}[/dim]")
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"[green]✅ Resposta recebida - {len(data)} instância(s)[/green]")
                
                # Mostrar estrutura da resposta
                if data:
                    console.print("\n[yellow]Estrutura da resposta:[/yellow]")
                    syntax = Syntax(json.dumps(data[0], indent=2), "json", theme="monokai")
                    console.print(syntax)
                    
                    # Analisar estrutura
                    first_item = data[0]
                    console.print("\n[yellow]Análise da estrutura:[/yellow]")
                    
                    # Verificar diferentes possíveis estruturas
                    if isinstance(first_item, dict):
                        if "instance" in first_item:
                            inst = first_item["instance"]
                            console.print(f"Nome: {inst.get('instanceName', 'N/A')}")
                            console.print(f"Status: {inst.get('status', 'N/A')}")
                            console.print(f"ID: {inst.get('instanceId', 'N/A')}")
                        elif "instanceName" in first_item:
                            console.print(f"Nome: {first_item.get('instanceName', 'N/A')}")
                            console.print(f"Status: {first_item.get('status', 'N/A')}")
                            console.print(f"ID: {first_item.get('id', 'N/A')}")
                        else:
                            console.print("[red]Estrutura não reconhecida[/red]")
                            console.print(f"Chaves disponíveis: {list(first_item.keys())}")
            else:
                console.print(f"[red]❌ Erro: {response.status_code}[/red]")
                console.print(f"[dim]{response.text}[/dim]")
                
        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")
        
        # 2. Tentar criar instância se não existir
        console.print("\n[bold]2️⃣ Verificando se precisa criar instância[/bold]")
        
        if instance_name:
            # Verificar se instância específica existe
            try:
                response = await client.get(
                    f"{base_url}/instance/connectionState/{instance_name}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    state = response.json()
                    console.print(f"[green]✅ Instância '{instance_name}' existe[/green]")
                    console.print(f"[dim]Estado: {state}[/dim]")
                elif response.status_code == 404:
                    console.print(f"[yellow]⚠️ Instância '{instance_name}' não encontrada[/yellow]")
                    
                    # Oferecer criar
                    console.print("\n[yellow]Deseja criar a instância? (s/n):[/yellow] ", end="")
                    create = input().lower() == 's'
                    
                    if create:
                        # Criar instância
                        create_payload = {
                            "instanceName": instance_name,
                            "qrcode": True,
                            "integration": "WHATSAPP-BAILEYS"
                        }
                        
                        response = await client.post(
                            f"{base_url}/instance/create",
                            headers=headers,
                            json=create_payload
                        )
                        
                        if response.status_code in [200, 201]:
                            console.print("[green]✅ Instância criada com sucesso![/green]")
                            result = response.json()
                            console.print(f"[dim]{json.dumps(result, indent=2)}[/dim]")
                        else:
                            console.print(f"[red]❌ Erro ao criar: {response.status_code}[/red]")
                            console.print(f"[dim]{response.text}[/dim]")
                            
            except Exception as e:
                console.print(f"[dim]Erro ao verificar estado: {e}[/dim]")
        
        # 3. Verificar webhook global
        console.print("\n[bold]3️⃣ Verificando Webhook Global[/bold]")
        try:
            response = await client.get(
                f"{base_url}/webhook/find",
                headers=headers
            )
            
            if response.status_code == 200:
                webhook = response.json()
                console.print("[green]✅ Webhook global encontrado[/green]")
                syntax = Syntax(json.dumps(webhook, indent=2), "json", theme="monokai")
                console.print(syntax)
        except Exception as e:
            console.print(f"[dim]Sem webhook global: {e}[/dim]")
        
        # 4. Sugestões
        console.print("\n")
        console.print(Panel(
            "[bold yellow]💡 Próximos Passos:[/bold yellow]\n\n"
            "1. Se a instância tem nome vazio ou 'N/A':\n"
            "   - Acesse o Evolution Manager\n"
            "   - Crie uma nova instância com nome específico\n"
            "   - Use QR Code para conectar o WhatsApp\n\n"
            "2. Para configurar o webhook:\n"
            "   - Use o nome correto da instância\n"
            "   - Configure para comunicação interna do EasyPanel\n\n"
            "3. Se ainda tiver problemas:\n"
            "   - Verifique a versão da Evolution API\n"
            "   - Confirme que a API Key tem permissões corretas",
            border_style="yellow"
        ))


async def test_webhook_endpoints():
    """Testa diferentes formas de configurar webhook"""
    
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    console.print("\n[bold]4️⃣ Testando Endpoints de Webhook[/bold]")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Tentar diferentes endpoints
        endpoints = [
            f"/webhook/set/{instance_name}",
            f"/webhook/instance/{instance_name}",
            f"/webhook/update/{instance_name}",
            "/webhook/set"
        ]
        
        for endpoint in endpoints:
            console.print(f"\n[dim]Testando {endpoint}...[/dim]")
            
            try:
                # Primeiro GET para ver estrutura
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=headers
                )
                console.print(f"GET: {response.status_code}")
                
            except Exception as e:
                console.print(f"[dim]GET falhou: {e}[/dim]")


async def main():
    """Função principal"""
    await test_evolution_api()
    await test_webhook_endpoints()


if __name__ == "__main__":
    asyncio.run(main())