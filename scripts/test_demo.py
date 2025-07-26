#!/usr/bin/env python3
"""
Teste do Agente Demo - Sem API Key
==================================
Permite testar o agente sem necessidade de API key
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.demo_agent import DemoSDRAgent

console = Console()

async def run_demo():
    """Executa o modo demo do agente"""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]🤖 SDR SolarPrime - MODO DEMONSTRAÇÃO[/bold cyan]\n"
        "[yellow]Funcionando sem API key do Gemini[/yellow]",
        border_style="cyan"
    ))
    
    # Cria agente demo
    agent = DemoSDRAgent()
    phone = "+5511999999999"
    
    # Inicia conversa
    console.print("\n[bold green]Iniciando conversa...[/bold green]\n")
    response, metadata = await agent.start_conversation(phone)
    
    console.print(Panel(response, title="🤖 Luna", border_style="blue"))
    console.print(f"[dim]Stage: {metadata['stage']} | Delay: {metadata['typing_delay']:.1f}s[/dim]\n")
    
    # Loop de conversa
    while True:
        try:
            user_input = Prompt.ask("[bold]Você[/bold]")
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                break
            
            # Simula digitação
            console.print("[dim]Agente digitando...[/dim]")
            await asyncio.sleep(1.5)
            
            # Processa mensagem
            response, metadata = await agent.process_message(user_input, phone)
            
            # Mostra resposta
            console.print(Panel(response, title="🤖 Luna", border_style="blue"))
            console.print(f"[dim]Stage: {metadata['stage']} | Intent: {metadata.get('intent', 'N/A')} | Sentiment: {metadata['sentiment']}[/dim]\n")
            
            # Se chegou no agendamento ou fechou, oferece reiniciar
            if metadata['stage'] in ['SCHEDULING', 'CLOSED']:
                if Prompt.ask("\n[yellow]Conversa finalizada. Deseja iniciar uma nova?[/yellow]", 
                             choices=["s", "n"], default="n") == "s":
                    response, metadata = await agent.start_conversation(phone)
                    console.print("\n" + Panel(response, title="🤖 Luna", border_style="blue"))
                else:
                    break
                    
        except KeyboardInterrupt:
            console.print("\n[red]Conversa interrompida[/red]")
            break
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")
            break
    
    # Mostra resumo
    console.print("\n[bold]📊 Resumo da Conversa:[/bold]")
    summary = agent.get_conversation_summary(phone)
    for key, value in summary.items():
        console.print(f"  {key}: {value}")

if __name__ == "__main__":
    console.print("[bold yellow]⚠️  MODO DEMONSTRAÇÃO[/bold yellow]")
    console.print("Este modo usa respostas pré-definidas para teste sem API key.\n")
    
    asyncio.run(run_demo())