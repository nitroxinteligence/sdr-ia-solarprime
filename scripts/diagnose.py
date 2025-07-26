#!/usr/bin/env python3
"""
Script de Diagnóstico Completo - SDR IA SolarPrime
"""

import asyncio
import os
import sys
import httpx
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

console = Console()


async def check_environment():
    """Verifica variáveis de ambiente"""
    console.print("\n[bold cyan]1. Verificando Variáveis de Ambiente[/bold cyan]")
    
    required_vars = {
        "EVOLUTION_API_URL": os.getenv("EVOLUTION_API_URL"),
        "EVOLUTION_API_KEY": os.getenv("EVOLUTION_API_KEY"),
        "EVOLUTION_INSTANCE_NAME": os.getenv("EVOLUTION_INSTANCE_NAME"),
        "WEBHOOK_BASE_URL": os.getenv("WEBHOOK_BASE_URL"),
        "REDIS_HOST": os.getenv("REDIS_HOST"),
        "REDIS_PORT": os.getenv("REDIS_PORT"),
        "SUPABASE_URL": os.getenv("SUPABASE_URL")
    }
    
    table = Table(title="Variáveis de Ambiente")
    table.add_column("Variável", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Valor", style="yellow")
    
    all_ok = True
    for var, value in required_vars.items():
        if value:
            status = "✅ OK"
            display_value = value[:30] + "..." if len(value) > 30 else value
            # Ocultar chaves sensíveis
            if "KEY" in var or "PASSWORD" in var:
                display_value = "***" + value[-4:] if len(value) > 4 else "***"
        else:
            status = "❌ Faltando"
            display_value = "Não configurado"
            all_ok = False
        
        table.add_row(var, status, display_value)
    
    console.print(table)
    return all_ok


async def check_redis():
    """Verifica conexão com Redis"""
    console.print("\n[bold cyan]2. Verificando Redis[/bold cyan]")
    
    try:
        from services.redis_service import redis_service
        await redis_service.connect()
        await redis_service.set("test_key", "test_value", ttl=10)
        value = await redis_service.get("test_key")
        
        if value == "test_value":
            console.print("✅ [green]Redis conectado e funcionando[/green]")
            console.print(f"   Host: {os.getenv('REDIS_HOST', 'localhost')}")
            console.print(f"   Port: {os.getenv('REDIS_PORT', '6379')}")
            return True
        else:
            console.print("⚠️  [yellow]Redis conectado mas com problemas[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"❌ [red]Redis não conectado: {e}[/red]")
        console.print("ℹ️  [yellow]Sistema usará fallback em memória[/yellow]")
        return False


async def check_evolution_api():
    """Verifica conexão com Evolution API"""
    console.print("\n[bold cyan]3. Verificando Evolution API[/bold cyan]")
    
    try:
        from services.evolution_api import evolution_client
        
        # Inicializar cliente
        await evolution_client.initialize()
        
        # Verificar conexão
        status = await evolution_client.check_connection()
        
        table = Table(title="Status Evolution API")
        table.add_column("Propriedade", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("URL", evolution_client.base_url)
        table.add_row("Instance", evolution_client.instance_name)
        table.add_row("Estado", status.get("state", "unknown"))
        
        if status.get("state") == "open":
            table.add_row("WhatsApp", "✅ Conectado")
        elif status.get("state") == "close":
            table.add_row("WhatsApp", "❌ Desconectado (precisa QR Code)")
        else:
            table.add_row("WhatsApp", f"⚠️  {status.get('state', 'unknown')}")
        
        console.print(table)
        
        # Verificar webhook
        webhook_info = await evolution_client.get_webhook_info()
        if webhook_info and webhook_info.get("webhook", {}).get("enabled"):
            console.print("✅ [green]Webhook configurado e ativo[/green]")
            console.print(f"   URL: {webhook_info.get('webhook', {}).get('url', 'N/A')}")
        else:
            console.print("❌ [red]Webhook não configurado[/red]")
        
        return status.get("state") == "open"
        
    except Exception as e:
        console.print(f"❌ [red]Erro ao conectar Evolution API: {e}[/red]")
        return False


async def check_fastapi():
    """Verifica se a API FastAPI está rodando"""
    console.print("\n[bold cyan]4. Verificando API FastAPI[/bold cyan]")
    
    try:
        async with httpx.AsyncClient() as client:
            # Verificar health
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                console.print("✅ [green]API rodando em http://localhost:8000[/green]")
                
                # Verificar status do webhook
                response = await client.get("http://localhost:8000/webhook/status")
                webhook_status = response.json()
                
                if webhook_status.get("status") == "active":
                    console.print("✅ [green]Endpoint webhook ativo[/green]")
                else:
                    console.print("⚠️  [yellow]Endpoint webhook com problemas[/yellow]")
                
                return True
            else:
                console.print(f"⚠️  [yellow]API respondendo com status {response.status_code}[/yellow]")
                return False
                
    except httpx.ConnectError:
        console.print("❌ [red]API não está rodando![/red]")
        console.print("   Execute: python -m uvicorn api.main:app --reload")
        return False
    except Exception as e:
        console.print(f"❌ [red]Erro ao verificar API: {e}[/red]")
        return False


async def check_supabase():
    """Verifica conexão com Supabase"""
    console.print("\n[bold cyan]5. Verificando Supabase[/bold cyan]")
    
    try:
        from services.database import db
        
        # Tentar uma query simples
        result = db.client.table("profiles").select("id").limit(1).execute()
        
        console.print("✅ [green]Supabase conectado[/green]")
        console.print(f"   URL: {os.getenv('SUPABASE_URL', 'N/A')[:40]}...")
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Erro ao conectar Supabase: {e}[/red]")
        return False


async def test_webhook():
    """Testa o webhook enviando uma mensagem de teste"""
    console.print("\n[bold cyan]6. Testando Webhook[/bold cyan]")
    
    webhook_url = "http://localhost:8000/webhook/whatsapp"
    
    test_payload = {
        "event": "MESSAGES_UPSERT",
        "instance": os.getenv("EVOLUTION_INSTANCE_NAME", "test"),
        "data": {
            "key": {
                "id": f"TEST_{datetime.now().timestamp()}",
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False
            },
            "message": {
                "conversation": "Teste de diagnóstico"
            },
            "messageTimestamp": int(datetime.now().timestamp()),
            "pushName": "Diagnóstico"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=test_payload,
                timeout=5.0
            )
            
            if response.status_code == 200:
                console.print("✅ [green]Webhook respondeu corretamente[/green]")
                console.print(f"   Resposta: {response.json()}")
                return True
            else:
                console.print(f"⚠️  [yellow]Webhook retornou status {response.status_code}[/yellow]")
                return False
                
    except Exception as e:
        console.print(f"❌ [red]Erro ao testar webhook: {e}[/red]")
        return False


async def main():
    """Executa todos os diagnósticos"""
    console.clear()
    
    panel = Panel.fit(
        "[bold cyan]SDR IA SolarPrime - Diagnóstico Completo[/bold cyan]\n"
        f"Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        border_style="cyan"
    )
    console.print(panel)
    
    results = {
        "environment": await check_environment(),
        "redis": await check_redis(),
        "evolution_api": await check_evolution_api(),
        "fastapi": await check_fastapi(),
        "supabase": await check_supabase(),
        "webhook": False
    }
    
    # Só testa webhook se API estiver rodando
    if results["fastapi"]:
        results["webhook"] = await test_webhook()
    
    # Resumo
    console.print("\n[bold cyan]RESUMO DO DIAGNÓSTICO[/bold cyan]")
    
    table = Table()
    table.add_column("Componente", style="cyan")
    table.add_column("Status", style="green")
    
    status_map = {
        "environment": "Variáveis de Ambiente",
        "redis": "Redis Cache",
        "evolution_api": "Evolution API",
        "fastapi": "API FastAPI",
        "supabase": "Supabase Database",
        "webhook": "Webhook"
    }
    
    all_ok = True
    for key, name in status_map.items():
        status = "✅ OK" if results.get(key) else "❌ Falhou"
        if not results.get(key):
            all_ok = False
        table.add_row(name, status)
    
    console.print(table)
    
    if all_ok:
        console.print("\n✅ [bold green]Sistema completamente operacional![/bold green]")
    else:
        console.print("\n⚠️  [bold yellow]Sistema com problemas - verifique os componentes marcados[/bold yellow]")
        
        console.print("\n[bold]Sugestões de correção:[/bold]")
        
        if not results["environment"]:
            console.print("1. Configure as variáveis faltantes no arquivo .env")
        
        if not results["fastapi"]:
            console.print("2. Inicie a API: python -m uvicorn api.main:app --reload")
        
        if not results["evolution_api"]:
            console.print("3. Verifique se Evolution API está rodando e acessível")
            console.print("   URL atual: " + os.getenv("EVOLUTION_API_URL", "não configurada"))
        
        if results["evolution_api"] and not results["webhook"]:
            console.print("4. Configure o webhook: python scripts/quick-webhook-setup.py")
    
    console.print("\n[dim]Diagnóstico concluído[/dim]")


if __name__ == "__main__":
    asyncio.run(main())