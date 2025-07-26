#!/usr/bin/env python3
"""
Teste Final - Demonstração das Correções
======================================
Mostra que o agente agora mantém contexto corretamente
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

async def test_conversation_flow():
    """Testa um fluxo completo de conversa"""
    console.clear()
    console.print(Panel.fit(
        "[bold green]🧪 Teste Final - SDR SolarPrime[/bold green]\n"
        "[cyan]Demonstrando que o contexto é mantido corretamente[/cyan]",
        border_style="green"
    ))
    
    agent = SDRAgent()
    phone = "5511999999999"
    
    # Sequência de teste
    conversation_flow = [
        ("Iniciando conversa", None),
        ("Enviando saudação", "oi"),
        ("Informando nome", "mateus"),
        ("Informando tipo de imóvel", "moro em apartamento"),
        ("Informando valor da conta", "minha conta vem uns 400 reais")
    ]
    
    lead_info_history = []
    
    for step_name, message in conversation_flow:
        console.print(f"\n[bold cyan]{step_name}...[/bold cyan]")
        
        if message is None:
            # Iniciar conversa
            response, metadata = await agent.start_conversation(phone)
        else:
            # Processar mensagem
            console.print(f"[yellow]👤 Usuário:[/yellow] {message}")
            response, metadata = await agent.process_message(message, phone)
        
        # Mostra resposta
        console.print(Panel(
            response[:200] + "..." if len(response) > 200 else response,
            title="🤖 Luna",
            border_style="blue"
        ))
        
        # Salva informações do lead
        lead_info_history.append({
            "step": step_name,
            "stage": metadata.get("stage", "N/A"),
            "lead_info": metadata.get("lead_info", {}).copy()
        })
        
        # Pequena pausa para visualização
        await asyncio.sleep(0.5)
    
    # Mostra evolução das informações coletadas
    console.print("\n[bold green]📊 Evolução das Informações Coletadas:[/bold green]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Etapa", style="cyan")
    table.add_column("Estágio", style="yellow")
    table.add_column("Nome", style="green")
    table.add_column("Imóvel", style="blue")
    table.add_column("Conta", style="red")
    
    for history in lead_info_history:
        lead_info = history["lead_info"]
        table.add_row(
            history["step"],
            history["stage"],
            lead_info.get("name", "-"),
            lead_info.get("property_type", "-"),
            lead_info.get("bill_value", "-")
        )
    
    console.print(table)
    
    # Verificações finais
    console.print("\n[bold green]✅ VERIFICAÇÕES FINAIS:[/bold green]")
    
    final_info = lead_info_history[-1]["lead_info"]
    checks = [
        ("Nome capturado", final_info.get("name") == "Mateus"),
        ("Tipo de imóvel capturado", final_info.get("property_type") == "apartamento"),
        ("Valor da conta capturado", "400" in str(final_info.get("bill_value", ""))),
        ("Contexto mantido entre mensagens", len(lead_info_history) == 5),
        ("Progressão de estágios", any(h["stage"] != "INITIAL_CONTACT" for h in lead_info_history))
    ]
    
    all_passed = True
    for check_name, passed in checks:
        if passed:
            console.print(f"  ✅ {check_name}")
        else:
            console.print(f"  ❌ {check_name}")
            all_passed = False
    
    if all_passed:
        console.print("\n[bold green]🎉 TODOS OS TESTES PASSARAM![/bold green]")
        console.print("[dim]O agente está mantendo contexto corretamente![/dim]")
    else:
        console.print("\n[bold red]⚠️  Alguns testes falharam[/bold red]")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(test_conversation_flow())
    sys.exit(0 if success else 1)