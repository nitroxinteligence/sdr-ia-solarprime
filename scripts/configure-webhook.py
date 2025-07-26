#!/usr/bin/env python3
"""
=============================================================================
SDR IA SolarPrime - Configurador de Webhook Evolution API
=============================================================================
Script interativo para configurar webhook na Evolution API com validações
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evolution_api import EvolutionAPIClient

console = Console()

class WebhookConfigurator:
    def __init__(self):
        self.client = EvolutionAPIClient()
        self.webhook_url = None
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
        
    async def check_connection(self) -> bool:
        """Verifica conexão com Evolution API"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Verificando conexão com Evolution API...", total=1)
            
            try:
                async with self.client as client:
                    status = await client.check_connection()
                    progress.update(task, advance=1)
                    
                    if status.get("state") == "open":
                        console.print("✅ [green]Conexão ativa com WhatsApp![/green]")
                        return True
                    else:
                        console.print(f"⚠️  [yellow]Status da conexão: {status.get('state', 'unknown')}[/yellow]")
                        return True  # Continuar mesmo se não conectado
            except Exception as e:
                progress.update(task, advance=1)
                console.print(f"❌ [red]Erro ao conectar: {e}[/red]")
                return False
    
    async def get_current_webhook(self) -> Optional[Dict[str, Any]]:
        """Obtém configuração atual do webhook"""
        try:
            async with self.client as client:
                webhook_info = await client.get_webhook_info()
                return webhook_info
        except Exception as e:
            console.print(f"[yellow]Não foi possível obter webhook atual: {e}[/yellow]")
            return None
    
    def display_current_config(self, webhook_info: Dict[str, Any]):
        """Exibe configuração atual do webhook"""
        if not webhook_info:
            console.print("[yellow]Nenhum webhook configurado atualmente[/yellow]")
            return
            
        webhook = webhook_info.get("webhook", {})
        
        table = Table(title="Configuração Atual do Webhook")
        table.add_column("Propriedade", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Ativo", "✅ Sim" if webhook.get("enabled") else "❌ Não")
        table.add_row("URL", webhook.get("url", "Não configurada"))
        table.add_row("Por Eventos", "✅ Sim" if webhook.get("webhookByEvents") else "❌ Não")
        table.add_row("Base64", "✅ Sim" if webhook.get("webhookBase64") else "❌ Não")
        
        console.print(table)
        
        if webhook.get("events"):
            console.print("\n[cyan]Eventos configurados:[/cyan]")
            for event in webhook.get("events", []):
                console.print(f"  • {event}")
    
    def get_webhook_url(self) -> str:
        """Solicita URL do webhook ao usuário"""
        console.print("\n[bold cyan]Configuração da URL do Webhook[/bold cyan]")
        console.print("A URL deve ser HTTPS em produção (HTTP apenas para desenvolvimento)")
        
        while True:
            url = Prompt.ask(
                "Digite a URL do webhook",
                default=os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000") + "/webhook/whatsapp"
            )
            
            # Validar URL
            if not url.startswith(("http://", "https://")):
                console.print("[red]URL deve começar com http:// ou https://[/red]")
                continue
                
            if "localhost" in url or "127.0.0.1" in url:
                console.print("[yellow]⚠️  URL local detectada - use apenas para desenvolvimento![/yellow]")
                
            if not url.endswith("/webhook/whatsapp"):
                console.print("[yellow]⚠️  URL não termina com /webhook/whatsapp[/yellow]")
                if not Confirm.ask("Deseja continuar mesmo assim?"):
                    continue
                    
            self.webhook_url = url
            return url
    
    def select_events(self) -> list:
        """Permite selecionar eventos para o webhook"""
        all_events = [
            ("MESSAGES_UPSERT", "Nova mensagem recebida", True),
            ("MESSAGES_UPDATE", "Atualização de status de mensagem", True),
            ("CONNECTION_UPDATE", "Mudança no status da conexão", True),
            ("QRCODE_UPDATED", "QR Code atualizado", True),
            ("MESSAGES_SET", "Conjunto inicial de mensagens", False),
            ("MESSAGES_DELETE", "Mensagem deletada", False),
            ("SEND_MESSAGE", "Mensagem enviada", True),
            ("CONTACTS_SET", "Conjunto inicial de contatos", False),
            ("CONTACTS_UPSERT", "Novo contato ou atualização", False),
            ("CONTACTS_UPDATE", "Atualização de contato", False),
            ("PRESENCE_UPDATE", "Atualização de presença (online/offline)", True),
            ("CHATS_SET", "Conjunto inicial de chats", False),
            ("CHATS_UPSERT", "Novo chat ou atualização", False),
            ("CHATS_UPDATE", "Atualização de chat", False),
            ("CHATS_DELETE", "Chat deletado", False),
            ("GROUPS_UPSERT", "Novo grupo ou atualização", False),
            ("GROUP_UPDATE", "Atualização de grupo", False),
            ("GROUP_PARTICIPANTS_UPDATE", "Mudança em participantes do grupo", False),
            ("CALL", "Chamada recebida", False),
            ("APPLICATION_STARTUP", "Aplicação iniciada", True),
            ("LABELS_EDIT", "Etiquetas editadas", False),
            ("LABELS_ASSOCIATION", "Associação de etiquetas", False),
            ("TYPEBOT_START", "Typebot iniciado", False),
            ("TYPEBOT_CHANGE_STATUS", "Mudança de status do Typebot", False)
        ]
        
        console.print("\n[bold cyan]Seleção de Eventos[/bold cyan]")
        console.print("Escolha quais eventos deseja receber no webhook:")
        
        # Perguntar se quer usar configuração recomendada
        if Confirm.ask("\nDeseja usar a configuração recomendada de eventos?", default=True):
            selected = [event[0] for event in all_events if event[2]]
            console.print(f"[green]✅ {len(selected)} eventos selecionados[/green]")
            return selected
        
        # Seleção manual
        selected_events = []
        for event, description, recommended in all_events:
            rec_text = " [green](recomendado)[/green]" if recommended else ""
            if Confirm.ask(f"Incluir {event} - {description}{rec_text}?", default=recommended):
                selected_events.append(event)
        
        if not selected_events:
            console.print("[red]Nenhum evento selecionado! Usando eventos essenciais.[/red]")
            selected_events = ["MESSAGES_UPSERT", "CONNECTION_UPDATE", "QRCODE_UPDATED"]
        
        return selected_events
    
    def get_webhook_options(self) -> Dict[str, Any]:
        """Solicita opções adicionais do webhook"""
        console.print("\n[bold cyan]Opções Adicionais[/bold cyan]")
        
        webhook_by_events = Confirm.ask(
            "Separar webhooks por tipo de evento? (recomendado: Não)",
            default=False
        )
        
        webhook_base64 = Confirm.ask(
            "Codificar payloads em Base64? (recomendado: Não)",
            default=False
        )
        
        return {
            "webhook_by_events": webhook_by_events,
            "webhook_base64": webhook_base64
        }
    
    async def test_webhook(self) -> bool:
        """Testa o webhook configurado"""
        console.print("\n[bold cyan]Teste do Webhook[/bold cyan]")
        
        if not Confirm.ask("Deseja testar o webhook agora?", default=True):
            return True
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Enviando webhook de teste...", total=1)
            
            try:
                # Fazer chamada de teste ao endpoint local
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.webhook_url.replace("/webhook/whatsapp", "/webhook/test"),
                        timeout=10.0
                    )
                    progress.update(task, advance=1)
                    
                    if response.status_code == 200:
                        console.print("✅ [green]Webhook de teste recebido com sucesso![/green]")
                        return True
                    else:
                        console.print(f"⚠️  [yellow]Webhook retornou status {response.status_code}[/yellow]")
                        return True  # Não é erro crítico
                        
            except httpx.ConnectError:
                progress.update(task, advance=1)
                console.print("⚠️  [yellow]Não foi possível conectar ao webhook (normal se for URL externa)[/yellow]")
                return True
            except Exception as e:
                progress.update(task, advance=1)
                console.print(f"⚠️  [yellow]Erro no teste: {e}[/yellow]")
                return True
    
    async def configure_webhook(
        self,
        webhook_url: str,
        events: list,
        webhook_by_events: bool,
        webhook_base64: bool
    ) -> bool:
        """Configura o webhook na Evolution API"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Configurando webhook...", total=1)
            
            try:
                async with self.client as client:
                    result = await client.create_webhook(
                        webhook_url=webhook_url,
                        events=events,
                        webhook_by_events=webhook_by_events,
                        webhook_base64=webhook_base64
                    )
                    progress.update(task, advance=1)
                    
                    console.print("✅ [green]Webhook configurado com sucesso![/green]")
                    return True
                    
            except Exception as e:
                progress.update(task, advance=1)
                console.print(f"❌ [red]Erro ao configurar webhook: {e}[/red]")
                return False
    
    def save_configuration(self, config: Dict[str, Any]):
        """Salva configuração em arquivo"""
        config_file = "webhook_config.json"
        
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            console.print(f"[green]✅ Configuração salva em {config_file}[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Não foi possível salvar configuração: {e}[/yellow]")
    
    async def run(self):
        """Executa o configurador"""
        console.clear()
        
        # Banner
        panel = Panel.fit(
            "[bold cyan]SDR IA SolarPrime[/bold cyan]\n"
            "Configurador de Webhook Evolution API v2",
            border_style="cyan"
        )
        console.print(panel)
        
        # Verificar conexão
        console.print("\n[bold]Passo 1: Verificando Conexão[/bold]")
        if not await self.check_connection():
            if not Confirm.ask("Deseja continuar mesmo sem conexão?"):
                return
        
        # Mostrar configuração atual
        console.print("\n[bold]Passo 2: Configuração Atual[/bold]")
        current_webhook = await self.get_current_webhook()
        self.display_current_config(current_webhook)
        
        if current_webhook and current_webhook.get("webhook", {}).get("enabled"):
            if not Confirm.ask("\nDeseja substituir a configuração atual?", default=True):
                console.print("[yellow]Configuração cancelada[/yellow]")
                return
        
        # Obter URL do webhook
        console.print("\n[bold]Passo 3: URL do Webhook[/bold]")
        webhook_url = self.get_webhook_url()
        
        # Selecionar eventos
        console.print("\n[bold]Passo 4: Eventos do Webhook[/bold]")
        events = self.select_events()
        
        # Opções adicionais
        console.print("\n[bold]Passo 5: Opções Adicionais[/bold]")
        options = self.get_webhook_options()
        
        # Resumo da configuração
        console.print("\n[bold]Resumo da Configuração:[/bold]")
        table = Table()
        table.add_column("Configuração", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("URL", webhook_url)
        table.add_row("Eventos", f"{len(events)} selecionados")
        table.add_row("Por Eventos", "✅ Sim" if options["webhook_by_events"] else "❌ Não")
        table.add_row("Base64", "✅ Sim" if options["webhook_base64"] else "❌ Não")
        
        console.print(table)
        
        # Confirmar configuração
        if not Confirm.ask("\nConfirmar configuração?", default=True):
            console.print("[yellow]Configuração cancelada[/yellow]")
            return
        
        # Configurar webhook
        console.print("\n[bold]Passo 6: Aplicando Configuração[/bold]")
        success = await self.configure_webhook(
            webhook_url=webhook_url,
            events=events,
            webhook_by_events=options["webhook_by_events"],
            webhook_base64=options["webhook_base64"]
        )
        
        if not success:
            console.print("[red]Falha na configuração. Verifique os logs.[/red]")
            return
        
        # Testar webhook
        console.print("\n[bold]Passo 7: Teste do Webhook[/bold]")
        await self.test_webhook()
        
        # Salvar configuração
        config = {
            "webhook_url": webhook_url,
            "events": events,
            "webhook_by_events": options["webhook_by_events"],
            "webhook_base64": options["webhook_base64"],
            "configured_at": datetime.now().isoformat(),
            "instance_name": self.instance_name
        }
        self.save_configuration(config)
        
        # Instruções finais
        console.print("\n[bold green]✅ Webhook configurado com sucesso![/bold green]")
        console.print("\n[bold]Próximos passos:[/bold]")
        console.print("1. Verifique os logs da aplicação para confirmar recebimento")
        console.print("2. Envie uma mensagem de teste pelo WhatsApp")
        console.print("3. Monitore o endpoint /webhook/status")
        
        if "localhost" in webhook_url:
            console.print("\n[yellow]⚠️  Atenção: Você está usando uma URL local.[/yellow]")
            console.print("Para produção, use uma URL pública com HTTPS!")

async def main():
    """Função principal"""
    configurator = WebhookConfigurator()
    try:
        await configurator.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuração interrompida pelo usuário[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())