#!/usr/bin/env python3
"""
Configure Webhook for EasyPanel
===============================
Configura o webhook da Evolution API para comunicação interna no EasyPanel.
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

console = Console()


async def get_current_webhook_config(base_url: str, api_key: str, instance_name: str):
    """Obtém a configuração atual do webhook"""
    
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
                return response.json()
            return None
            
        except Exception:
            return None


async def configure_webhook(
    base_url: str,
    api_key: str,
    instance_name: str,
    webhook_url: str,
    events: list = None
):
    """Configura o webhook na Evolution API"""
    
    if events is None:
        events = [
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "CONNECTION_UPDATE",
            "QRCODE_UPDATED",
            "SEND_MESSAGE",
            "PRESENCE_UPDATE"
        ]
    
    webhook_config = {
        "url": webhook_url,
        "enabled": True,
        "webhook_by_events": False,
        "webhook_base64": False,
        "events": events
    }
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{base_url}/webhook/set/{instance_name}",
                headers=headers,
                json=webhook_config
            )
            
            return response.status_code == 200, response
            
        except Exception as e:
            return False, str(e)


async def test_internal_connectivity(service_name: str, port: int):
    """Testa se a URL interna do serviço é acessível"""
    
    internal_url = f"http://{service_name}:{port}/health"
    
    console.print(f"\n[yellow]🔍 Testando conectividade interna: {internal_url}[/yellow]")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(internal_url)
            if response.status_code == 200:
                console.print("[green]✅ Serviço acessível internamente![/green]")
                return True
            else:
                console.print(f"[red]❌ Serviço respondeu com status {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Não foi possível conectar: {e}[/red]")
            return False


async def main():
    """Função principal"""
    
    console.print(Panel.fit(
        "[bold]🚀 SDR IA SolarPrime - Configurar Webhook para EasyPanel[/bold]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="bold blue"
    ))
    
    # Verificar configurações
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    
    if not all([base_url, api_key]):
        console.print("[red]❌ EVOLUTION_API_URL ou EVOLUTION_API_KEY não configurados no .env[/red]")
        return
    
    # Remover /manager se existir
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    # Se não tiver nome da instância, pedir ao usuário
    if not instance_name:
        console.print("[yellow]⚠️  EVOLUTION_INSTANCE_NAME não configurado[/yellow]")
        instance_name = Prompt.ask("Digite o nome da instância")
    
    # Configurações do EasyPanel
    console.print("\n[bold blue]📋 Configuração para EasyPanel:[/bold blue]")
    console.print("[dim]Os serviços no EasyPanel se comunicam usando nomes internos[/dim]\n")
    
    # Nome do serviço SDR IA no EasyPanel
    sdr_service_name = Prompt.ask(
        "Nome do serviço SDR IA no EasyPanel",
        default="sdr-ia"
    )
    
    # Porta interna (sempre 8000 para o FastAPI)
    internal_port = 8000
    
    # URL do webhook usando comunicação interna
    webhook_url = f"http://{sdr_service_name}:{internal_port}/webhook/whatsapp"
    
    # Mostrar configuração atual
    console.print("\n[bold]📍 Configuração Atual:[/bold]")
    current_config = await get_current_webhook_config(base_url, api_key, instance_name)
    
    if current_config:
        console.print(f"[yellow]URL Atual:[/yellow] {current_config.get('url', 'Não configurada')}")
        console.print(f"[yellow]Status:[/yellow] {'✅ Ativo' if current_config.get('enabled') else '❌ Inativo'}")
        console.print(f"[yellow]Eventos:[/yellow] {len(current_config.get('events', []))} configurados")
    else:
        console.print("[dim]Webhook não configurado ainda[/dim]")
    
    # Mostrar nova configuração
    console.print("\n[bold]🔧 Nova Configuração:[/bold]")
    console.print(f"[green]URL do Webhook:[/green] {webhook_url}")
    console.print(f"[green]Instância:[/green] {instance_name}")
    console.print(f"[green]Comunicação:[/green] Interna (EasyPanel)")
    
    # Confirmar
    if not Confirm.ask("\n[yellow]Deseja aplicar esta configuração?[/yellow]"):
        console.print("[red]Operação cancelada[/red]")
        return
    
    # Configurar webhook
    with console.status("[yellow]Configurando webhook...[/yellow]"):
        success, response = await configure_webhook(
            base_url,
            api_key,
            instance_name,
            webhook_url
        )
    
    if success:
        console.print("\n[green]✅ Webhook configurado com sucesso![/green]")
        
        # Instruções adicionais
        console.print("\n")
        console.print(Panel(
            "[bold green]🎯 Próximos Passos:[/bold green]\n\n"
            f"1. [yellow]Deploy no EasyPanel:[/yellow]\n"
            f"   - Nome do serviço: [cyan]{sdr_service_name}[/cyan]\n"
            f"   - Porta interna: [cyan]{internal_port}[/cyan]\n"
            f"   - Não expor porta externamente\n\n"
            f"2. [yellow]Variáveis de Ambiente no EasyPanel:[/yellow]\n"
            f"   - EVOLUTION_API_URL=http://evolution-api:8080\n"
            f"   - WEBHOOK_BASE_URL=http://{sdr_service_name}:{internal_port}\n"
            f"   - EVOLUTION_INSTANCE_NAME={instance_name}\n\n"
            f"3. [yellow]Teste a integração:[/yellow]\n"
            f"   - Envie uma mensagem no WhatsApp\n"
            f"   - Verifique os logs do serviço",
            border_style="green"
        ))
        
        # Salvar configuração
        save_config = Confirm.ask("\n[yellow]Deseja salvar essas configurações no .env.easypanel?[/yellow]")
        
        if save_config:
            env_content = f"""# Evolution API - Comunicação Interna EasyPanel
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY={api_key}
EVOLUTION_INSTANCE_NAME={instance_name}

# Webhook - URL Interna
WEBHOOK_BASE_URL=http://{sdr_service_name}:{internal_port}

# Outras configurações necessárias
# GEMINI_API_KEY=sua-gemini-key
# SUPABASE_URL=sua-supabase-url
# SUPABASE_KEY=sua-supabase-key
"""
            
            with open(".env.easypanel", "w") as f:
                f.write(env_content)
            
            console.print("\n[green]✅ Configurações salvas em .env.easypanel[/green]")
            console.print("[dim]Lembre-se de adicionar as outras variáveis necessárias![/dim]")
        
    else:
        console.print(f"\n[red]❌ Erro ao configurar webhook[/red]")
        console.print(f"[dim]Detalhes: {response}[/dim]")
        
        # Dicas de troubleshooting
        console.print("\n[yellow]💡 Dicas de Troubleshooting:[/yellow]")
        console.print("1. Verifique se a instância existe e está conectada")
        console.print("2. Confirme que a API key está correta")
        console.print("3. Teste a conexão com a Evolution API")
        console.print("4. Execute o script list_evolution_instances.py para verificar")


if __name__ == "__main__":
    asyncio.run(main())