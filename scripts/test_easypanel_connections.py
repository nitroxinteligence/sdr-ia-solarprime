#!/usr/bin/env python3
"""
Testa conexões internas no Easypanel
=====================================
Execute este script após o deploy para verificar conexões
"""

import asyncio
import os
import sys
import httpx
import redis.asyncio as redis
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
console = Console()

async def test_connections():
    """Testa todas as conexões internas no Easypanel"""
    
    results = []
    
    console.print("[bold cyan]🔍 Testando Conexões Internas no Easypanel[/bold cyan]\n")
    
    # 1. Testar Redis
    console.print("[yellow]1. Testando Redis...[/yellow]")
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        r = await redis.from_url(redis_url)
        
        # Teste de ping
        pong = await r.ping()
        if pong:
            # Teste de escrita/leitura
            await r.set("test_key", "test_value", ex=10)
            value = await r.get("test_key")
            
            if value == "test_value":
                results.append(("Redis", "✅ Conectado", redis_url, "Leitura/Escrita OK"))
            else:
                results.append(("Redis", "⚠️ Conectado", redis_url, "Erro na leitura"))
        
        await r.close()
        
    except Exception as e:
        results.append(("Redis", "❌ Erro", redis_url, str(e)))
    
    # 2. Testar Evolution API
    console.print("[yellow]2. Testando Evolution API...[/yellow]")
    try:
        evolution_url = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
        api_key = os.getenv("EVOLUTION_API_KEY", "")
        
        async with httpx.AsyncClient() as client:
            # Teste de health/status
            response = await client.get(
                f"{evolution_url}/instance/fetchInstances",
                headers={"apikey": api_key},
                timeout=10.0
            )
            
            if response.status_code == 200:
                results.append(("Evolution API", "✅ Conectado", evolution_url, f"Status {response.status_code}"))
                
                # Verificar instância específica
                instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "Teste-Agente")
                try:
                    instance_response = await client.get(
                        f"{evolution_url}/instance/connectionState/{instance_name}",
                        headers={"apikey": api_key},
                        timeout=5.0
                    )
                    
                    if instance_response.status_code == 200:
                        data = instance_response.json()
                        state = data.get("instance", {}).get("state", "unknown")
                        results.append(("WhatsApp Instance", "✅ OK", instance_name, f"Estado: {state}"))
                    else:
                        results.append(("WhatsApp Instance", "⚠️ Aviso", instance_name, f"Status {instance_response.status_code}"))
                        
                except Exception as e:
                    results.append(("WhatsApp Instance", "❌ Erro", instance_name, str(e)))
                    
            else:
                results.append(("Evolution API", "❌ Erro", evolution_url, f"Status {response.status_code}"))
                
    except Exception as e:
        results.append(("Evolution API", "❌ Erro", evolution_url or "N/A", str(e)))
    
    # 3. Testar Supabase
    console.print("[yellow]3. Testando Supabase...[/yellow]")
    try:
        from services.database import db
        
        # Tentar uma query simples
        result = await db.from_("leads").select("id").limit(1).execute()
        
        if result:
            results.append(("Supabase", "✅ Conectado", "supabase.co", "Query OK"))
        else:
            results.append(("Supabase", "⚠️ Conectado", "supabase.co", "Sem dados"))
            
    except Exception as e:
        results.append(("Supabase", "❌ Erro", "supabase.co", str(e)))
    
    # 4. Testar Gemini API
    console.print("[yellow]4. Testando Gemini API...[/yellow]")
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            
            # Listar modelos disponíveis
            models = list(genai.list_models())
            if models:
                results.append(("Gemini API", "✅ Conectado", "generativeai.google", f"{len(models)} modelos"))
            else:
                results.append(("Gemini API", "⚠️ Conectado", "generativeai.google", "Sem modelos"))
        else:
            results.append(("Gemini API", "❌ Erro", "generativeai.google", "API Key não configurada"))
            
    except Exception as e:
        results.append(("Gemini API", "❌ Erro", "generativeai.google", str(e)))
    
    # Exibir resultados
    console.print("\n[bold]📊 Resultados dos Testes:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Serviço", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Endpoint", style="yellow")
    table.add_column("Detalhes", style="dim")
    
    for service, status, endpoint, details in results:
        table.add_row(service, status, endpoint, details)
    
    console.print(table)
    
    # Resumo
    total = len(results)
    success = len([r for r in results if "✅" in r[1]])
    warnings = len([r for r in results if "⚠️" in r[1]])
    errors = len([r for r in results if "❌" in r[1]])
    
    console.print(f"\n[bold]Resumo:[/bold]")
    console.print(f"✅ Sucesso: {success}/{total}")
    console.print(f"⚠️  Avisos: {warnings}/{total}")
    console.print(f"❌ Erros: {errors}/{total}")
    
    if errors == 0:
        console.print("\n[bold green]🎉 Todas as conexões principais estão funcionando![/bold green]")
    else:
        console.print("\n[bold red]⚠️  Algumas conexões precisam de atenção![/bold red]")
    
    # Dicas de configuração
    if errors > 0:
        console.print("\n[yellow]💡 Dicas:[/yellow]")
        console.print("1. Verifique se os serviços estão na mesma rede no Easypanel")
        console.print("2. Use nomes de serviço internos (ex: 'redis', 'evolution-api')")
        console.print("3. Confirme que as variáveis de ambiente estão corretas")
        console.print("4. Verifique os logs no painel do Easypanel")

if __name__ == "__main__":
    asyncio.run(test_connections())