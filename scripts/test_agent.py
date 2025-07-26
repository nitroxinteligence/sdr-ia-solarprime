#!/usr/bin/env python3
"""
Script de Teste do Agente SDR
=============================
Testa o agente de IA no terminal de forma interativa
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown
from loguru import logger

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importações locais
from agents.sdr_agent import create_sdr_agent
from config.agent_config import config, validate_config
from utils.helpers import format_phone_number, get_greeting_by_time

# Console rico para output formatado
console = Console()

class AgentTester:
    """Classe para testar o agente de forma interativa"""
    
    def __init__(self):
        """Inicializa o testador"""
        self.agent = None
        self.test_phone = "+5511999999999"
        self.conversation_active = False
        
    async def setup(self):
        """Configura o ambiente de teste"""
        console.print("\n[bold cyan]🤖 SDR IA SolarPrime - Modo de Teste[/bold cyan]\n")
        
        # Valida configuração
        try:
            validate_config()
            console.print("✅ Configuração validada com sucesso!", style="green")
        except ValueError as e:
            console.print(f"❌ Erro de configuração: {e}", style="red")
            console.print("\n💡 Dica: Verifique se o arquivo .env está configurado corretamente")
            return False
        
        # Cria o agente
        try:
            self.agent = create_sdr_agent()
            console.print("✅ Agente criado com sucesso!", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Erro ao criar agente: {e}", style="red")
            return False
    
    async def run_interactive_test(self):
        """Executa teste interativo"""
        if not await self.setup():
            return
        
        # Mostra informações do agente
        self._show_agent_info()
        
        # Menu principal
        while True:
            console.print("\n[bold yellow]📋 Menu de Teste[/bold yellow]")
            console.print("1. Iniciar nova conversa")
            console.print("2. Testar resposta específica")
            console.print("3. Simular envio de imagem (conta de luz)")
            console.print("4. Ver métricas da conversa")
            console.print("5. Testar casos específicos")
            console.print("6. Sair")
            
            choice = Prompt.ask("\nEscolha uma opção", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                await self._start_conversation()
            elif choice == "2":
                await self._test_specific_response()
            elif choice == "3":
                await self._simulate_image_upload()
            elif choice == "4":
                await self._show_conversation_metrics()
            elif choice == "5":
                await self._test_specific_cases()
            elif choice == "6":
                console.print("\n👋 Até logo!", style="cyan")
                break
    
    async def _start_conversation(self):
        """Inicia uma conversa interativa"""
        console.print("\n[bold green]🚀 Iniciando Nova Conversa[/bold green]\n")
        
        # Pergunta se quer personalizar o telefone
        custom_phone = Prompt.ask(
            "Digite o número de telefone (ou Enter para usar padrão)",
            default=self.test_phone
        )
        self.test_phone = format_phone_number(custom_phone)
        
        # Inicia conversa
        response, metadata = await self.agent.start_conversation(self.test_phone)
        self._display_agent_response(response, metadata)
        
        # Loop de conversa
        self.conversation_active = True
        while self.conversation_active:
            # Recebe input do usuário
            user_input = Prompt.ask("\n[cyan]Você[/cyan]")
            
            if user_input.lower() in ['/sair', '/exit', '/quit']:
                self.conversation_active = False
                console.print("\n👋 Conversa encerrada", style="yellow")
                break
            
            # Processa mensagem
            console.print("\n[dim]Agente digitando...[/dim]")
            response, metadata = await self.agent.process_message(
                user_input,
                self.test_phone
            )
            
            # Simula delay de digitação
            await asyncio.sleep(metadata.get("typing_delay", 3))
            
            # Exibe resposta
            self._display_agent_response(response, metadata)
    
    async def _test_specific_response(self):
        """Testa uma resposta específica"""
        console.print("\n[bold blue]🧪 Teste de Resposta Específica[/bold blue]\n")
        
        # Recebe mensagem
        test_message = Prompt.ask("Digite a mensagem de teste")
        
        # Processa
        console.print("\n[dim]Processando...[/dim]")
        response, metadata = await self.agent.process_message(
            test_message,
            self.test_phone
        )
        
        # Exibe resultado
        self._display_agent_response(response, metadata)
        
        # Mostra análise
        console.print("\n[bold]📊 Análise da Resposta:[/bold]")
        table = Table()
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Estágio", metadata.get("stage", "N/A"))
        table.add_row("Sentimento", metadata.get("sentiment", "N/A"))
        table.add_row("Delay de Digitação", f"{metadata.get('typing_delay', 0):.1f}s")
        table.add_row("Deve Agendar?", "Sim" if metadata.get("should_schedule") else "Não")
        
        console.print(table)
    
    async def _simulate_image_upload(self):
        """Simula upload de imagem"""
        console.print("\n[bold magenta]📸 Simulação de Upload de Imagem[/bold magenta]\n")
        
        # Menu de opções de teste
        console.print("Escolha o tipo de simulação:")
        console.print("1. URL de imagem (conta de luz exemplo)")
        console.print("2. Dados base64 simulados")
        console.print("3. Caminho de arquivo local")
        console.print("4. PDF de conta de luz")
        
        choice = Prompt.ask("Escolha", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            # Simula URL de imagem
            console.print("Simulando envio de conta de luz via URL...")
            media_data = {
                "url": "https://exemplo.com/conta-luz.jpg"  # URL simulada
            }
            message = "Aqui está minha conta de luz"
            
        elif choice == "2":
            # Simula dados base64
            console.print("Simulando envio de conta de luz em base64...")
            # Base64 simulado (não é uma imagem real)
            media_data = {
                "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
            message = "Segue a foto da minha conta"
            
        elif choice == "3":
            # Simula caminho de arquivo
            console.print("Simulando envio de arquivo local...")
            media_data = {
                "path": "/tmp/conta_luz_exemplo.jpg"  # Caminho simulado
            }
            message = "Está aqui a conta"
            
        else:
            # Simula PDF
            console.print("Simulando envio de PDF...")
            media_data = {
                "url": "https://exemplo.com/conta.pdf",
                "mime_type": "application/pdf"
            }
            message = "Enviei o PDF da conta"
            media_type = "document"
        
        # Define tipo de mídia
        media_type = "document" if choice == "4" else "image"
        
        # Processa mensagem com mídia
        console.print(f"\n[dim]Processando {media_type}...[/dim]")
        
        try:
            response, metadata = await self.agent.process_message(
                message,
                self.test_phone,
                media_type=media_type,
                media_data=media_data
            )
            
            # Simula delay de análise
            await asyncio.sleep(2)
            
            # Exibe resposta
            self._display_agent_response(response, metadata)
            
            # Mostra dados extraídos se houver
            if metadata.get("lead_info", {}).get("bill_value"):
                console.print("\n[bold green]✅ Dados Extraídos da Conta:[/bold green]")
                lead_info = metadata["lead_info"]
                
                table = Table()
                table.add_column("Campo", style="cyan")
                table.add_column("Valor", style="green")
                
                if lead_info.get("bill_value"):
                    table.add_row("Valor da Conta", lead_info["bill_value"])
                if lead_info.get("consumption_kwh"):
                    table.add_row("Consumo", f"{lead_info['consumption_kwh']} kWh")
                if lead_info.get("customer_name"):
                    table.add_row("Titular", lead_info["customer_name"])
                if lead_info.get("address"):
                    table.add_row("Endereço", lead_info["address"])
                    
                console.print(table)
                
        except Exception as e:
            console.print(f"[red]❌ Erro ao processar mídia: {e}[/red]")
            if config.debug:
                console.print_exception()
    
    async def _show_conversation_metrics(self):
        """Mostra métricas da conversa"""
        console.print("\n[bold yellow]📈 Métricas da Conversa[/bold yellow]\n")
        
        # Obtém resumo da conversa
        summary = self.agent.get_conversation_summary(self.test_phone)
        
        # Tabela de métricas
        table = Table(title="Informações do Lead")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        
        # Informações do lead
        lead_info = summary.get("lead_info", {})
        for key, value in lead_info.items():
            if key not in ['current_stage', 'last_interaction']:
                table.add_row(key.replace("_", " ").title(), str(value))
        
        table.add_row("Estágio Atual", summary.get("current_stage", "N/A"))
        table.add_row("Sessão Ativa", "Sim" if summary.get("session_active") else "Não")
        
        if summary.get("last_interaction"):
            table.add_row("Última Interação", summary["last_interaction"])
        
        console.print(table)
        
        # Informações adicionais
        if lead_info:
            console.print("\n[bold]📋 Status da Qualificação:[/bold]")
            console.print(f"• Nome: {'✅' if lead_info.get('name') else '❌'} {'Capturado' if lead_info.get('name') else 'Pendente'}")
            console.print(f"• Tipo de Imóvel: {'✅' if lead_info.get('property_type') else '❌'} {'Identificado' if lead_info.get('property_type') else 'Pendente'}")
            console.print(f"• Valor da Conta: {'✅' if lead_info.get('bill_value') else '❌'} {'Informado' if lead_info.get('bill_value') else 'Pendente'}")
    
    async def _test_specific_cases(self):
        """Testa casos específicos"""
        console.print("\n[bold purple]🎯 Casos de Teste Específicos[/bold purple]\n")
        
        cases = [
            ("Objeção de Custo", "Mas energia solar não é muito caro?"),
            ("Pergunta Técnica", "Como funciona em dias nublados?"),
            ("Interesse Alto", "Quero muito economizar na conta de luz!"),
            ("Sem Interesse", "Não tenho interesse, obrigado"),
            ("Valor da Conta", "Minha conta vem uns 450 reais por mês"),
            ("Agendamento", "Sim, quero marcar uma reunião para saber mais")
        ]
        
        console.print("Escolha um caso de teste:")
        for i, (name, _) in enumerate(cases, 1):
            console.print(f"{i}. {name}")
        
        choice = Prompt.ask("Escolha", choices=[str(i) for i in range(1, len(cases) + 1)])
        case_name, case_message = cases[int(choice) - 1]
        
        console.print(f"\n[bold]Testando: {case_name}[/bold]")
        console.print(f"Mensagem: {case_message}\n")
        
        # Processa
        response, metadata = await self.agent.process_message(
            case_message,
            self.test_phone
        )
        
        self._display_agent_response(response, metadata)
    
    def _show_agent_info(self):
        """Mostra informações do agente"""
        info = Panel(
            f"""[bold cyan]Agente:[/bold cyan] {config.personality.name}
[bold cyan]Empresa:[/bold cyan] {config.personality.company}
[bold cyan]Modelo:[/bold cyan] {config.gemini.model}
[bold cyan]Personalidade:[/bold cyan] {config.personality.voice_tone}
[bold cyan]Características:[/bold cyan] {', '.join(config.personality.traits[:3])}...""",
            title="🤖 Informações do Agente",
            border_style="cyan"
        )
        console.print(info)
    
    def _display_agent_response(self, response: str, metadata: dict):
        """Exibe resposta do agente formatada"""
        # Painel com a resposta
        panel = Panel(
            response,
            title=f"🤖 {config.personality.name}",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
        
        # Mostra metadados em modo debug
        if config.debug:
            console.print(
                f"\n[dim]Debug: Estágio={metadata.get('stage')}, "
                f"Sentimento={metadata.get('sentiment')}, "
                f"Delay={metadata.get('typing_delay', 0):.1f}s[/dim]"
            )

async def main():
    """Função principal"""
    # Configura logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO" if not config.debug else "DEBUG"
    )
    
    # Cria e executa testador
    tester = AgentTester()
    try:
        await tester.run_interactive_test()
    except KeyboardInterrupt:
        console.print("\n\n👋 Teste interrompido pelo usuário", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Erro durante teste: {e}", style="red")
        if config.debug:
            console.print_exception()

if __name__ == "__main__":
    # Limpa tela
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Executa teste
    asyncio.run(main())