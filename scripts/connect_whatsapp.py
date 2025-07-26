#!/usr/bin/env python3
"""
Script para conectar WhatsApp na Evolution API
=============================================
"""

import asyncio
import os
import sys
import qrcode
from io import StringIO
from rich.console import Console
from rich.panel import Panel
import httpx
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

console = Console()

async def connect_whatsapp():
    """Conecta WhatsApp gerando QR Code"""
    
    base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "Teste-Agente")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    console.print(Panel.fit(
        "[bold cyan]🔗 Conectando WhatsApp na Evolution API[/bold cyan]",
        border_style="cyan"
    ))
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Verificar se instância existe
            console.print(f"\n[yellow]Verificando instância: {instance_name}[/yellow]")
            
            check_response = await client.get(
                f"{base_url}/instance/connectionState/{instance_name}",
                headers={"apikey": api_key},
                timeout=10.0
            )
            
            if check_response.status_code == 404:
                # Criar nova instância
                console.print("[yellow]Instância não existe. Criando...[/yellow]")
                
                create_response = await client.post(
                    f"{base_url}/instance/create",
                    headers={"apikey": api_key},
                    json={
                        "instanceName": instance_name,
                        "qrcode": True,
                        "integration": "WHATSAPP-BAILEYS"
                    }
                )
                
                if create_response.status_code != 201:
                    console.print(f"[red]Erro ao criar instância: {create_response.text}[/red]")
                    return
                
                console.print("[green]✅ Instância criada com sucesso![/green]")
            
            # 2. Gerar QR Code
            console.print("\n[yellow]Gerando QR Code...[/yellow]")
            
            # Conectar instância
            connect_response = await client.get(
                f"{base_url}/instance/connect/{instance_name}",
                headers={"apikey": api_key},
                timeout=30.0
            )
            
            if connect_response.status_code == 200:
                data = connect_response.json()
                
                if "qrcode" in data:
                    qr_data = data["qrcode"].get("code", "")
                    
                    if qr_data:
                        # Gerar QR Code no terminal
                        qr = qrcode.QRCode()
                        qr.add_data(qr_data)
                        qr.make()
                        
                        # Exibir QR Code
                        console.print("\n[bold green]📱 ESCANEIE O QR CODE COM SEU WHATSAPP:[/bold green]\n")
                        
                        f = StringIO()
                        qr.print_ascii(out=f)
                        f.seek(0)
                        console.print(f.read())
                        
                        console.print("\n[yellow]Instruções:[/yellow]")
                        console.print("1. Abra o WhatsApp no seu celular")
                        console.print("2. Vá em Configurações > Aparelhos conectados")
                        console.print("3. Clique em 'Conectar um aparelho'")
                        console.print("4. Escaneie o QR Code acima")
                        
                        # Aguardar conexão
                        console.print("\n[cyan]Aguardando conexão...[/cyan]")
                        
                        for i in range(60):  # Aguarda até 60 segundos
                            await asyncio.sleep(2)
                            
                            # Verificar status
                            status_response = await client.get(
                                f"{base_url}/instance/connectionState/{instance_name}",
                                headers={"apikey": api_key}
                            )
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                state = status_data.get("instance", {}).get("state", "")
                                
                                if state == "open":
                                    console.print("\n[bold green]✅ WHATSAPP CONECTADO COM SUCESSO![/bold green]")
                                    
                                    # Configurar webhook
                                    webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
                                    
                                    console.print(f"\n[yellow]Configurando webhook: {webhook_url}/webhook/whatsapp[/yellow]")
                                    
                                    webhook_response = await client.post(
                                        f"{base_url}/webhook/set/{instance_name}",
                                        headers={"apikey": api_key},
                                        json={
                                            "webhook": {
                                                "url": f"{webhook_url}/webhook/whatsapp",
                                                "events": [
                                                    "MESSAGES_UPSERT",
                                                    "MESSAGES_UPDATE",
                                                    "CONNECTION_UPDATE"
                                                ]
                                            }
                                        }
                                    )
                                    
                                    if webhook_response.status_code == 200:
                                        console.print("[green]✅ Webhook configurado![/green]")
                                    
                                    console.print("\n[bold green]🎉 TUDO PRONTO! O AGENTE JÁ ESTÁ RESPONDENDO NO WHATSAPP![/bold green]")
                                    console.print("\n[cyan]Envie uma mensagem para testar![/cyan]")
                                    return
                                
                                elif i % 5 == 0:
                                    console.print(f"[dim]Estado atual: {state}[/dim]")
                        
                        console.print("\n[red]⏱️ Tempo esgotado. Tente novamente.[/red]")
                    else:
                        console.print("[red]Erro: QR Code vazio[/red]")
                else:
                    # Pode já estar conectado
                    state = connect_response.json().get("instance", {}).get("state", "")
                    if state == "open":
                        console.print("[green]✅ WhatsApp já está conectado![/green]")
                    else:
                        console.print(f"[yellow]Estado: {state}[/yellow]")
                        console.print("[yellow]Use o painel web para conectar[/yellow]")
            else:
                console.print(f"[red]Erro: {connect_response.text}[/red]")
                
        except Exception as e:
            console.print(f"[red]Erro: {str(e)}[/red]")
            console.print("\n[yellow]Alternativa: Acesse o painel web em:[/yellow]")
            console.print(f"{base_url}/manager")

if __name__ == "__main__":
    asyncio.run(connect_whatsapp())