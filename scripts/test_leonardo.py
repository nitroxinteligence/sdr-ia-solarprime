#!/usr/bin/env python3
"""
Teste Rápido - Leonardo Ferraz
==============================
Verifica se o prompt humanizado está funcionando
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

async def test_leonardo():
    """Testa o agente Leonardo Ferraz"""
    console.clear()
    console.print(Panel.fit(
        "[bold green]🌟 Teste do Leonardo Ferraz - SDR SolarPrime[/bold green]\n"
        "[cyan]Agora com prompts humanizados e estilo brasileiro![/cyan]",
        border_style="green"
    ))
    
    agent = SDRAgent()
    phone = "5511987654321"
    
    # Inicia conversa
    console.print("\n[bold cyan]Iniciando conversa com Leonardo Ferraz...[/bold cyan]\n")
    response, metadata = await agent.start_conversation(phone)
    
    console.print(Panel(
        response,
        title="🌟 Leonardo Ferraz",
        border_style="yellow"
    ))
    
    # Loop de conversa
    console.print("\n[dim]Digite 'sair' para encerrar[/dim]\n")
    
    while True:
        # Recebe mensagem do usuário
        user_input = Prompt.ask("[bold cyan]Você[/bold cyan]")
        
        if user_input.lower() == 'sair':
            break
        
        # Processa mensagem
        response, metadata = await agent.process_message(user_input, phone)
        
        # Mostra resposta
        console.print(f"\n[dim]Estágio: {metadata['stage']} | Sentimento: {metadata.get('sentiment', 'neutro')}[/dim]")
        console.print(Panel(
            response,
            title="🌟 Leonardo Ferraz",
            border_style="yellow"
        ))
        
        # Mostra informações coletadas
        if metadata.get('lead_info'):
            info = metadata['lead_info']
            if any(info.get(k) for k in ['name', 'property_type', 'bill_value']):
                console.print("\n[bold green]📊 Informações Coletadas:[/bold green]")
                if info.get('name'):
                    console.print(f"   Nome: [yellow]{info['name']}[/yellow]")
                if info.get('property_type'):
                    console.print(f"   Imóvel: [yellow]{info['property_type']}[/yellow]")
                if info.get('bill_value'):
                    console.print(f"   Conta: [yellow]{info['bill_value']}[/yellow]")
                console.print()

if __name__ == "__main__":
    asyncio.run(test_leonardo())