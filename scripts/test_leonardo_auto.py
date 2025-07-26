#!/usr/bin/env python3
"""
Teste Automatizado - Leonardo Ferraz
====================================
Verifica características do prompt humanizado
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from rich.console import Console
from rich.table import Table

console = Console()

async def test_leonardo_characteristics():
    """Testa características do Leonardo Ferraz"""
    console.print("\n[bold green]🌟 Teste de Características - Leonardo Ferraz[/bold green]\n")
    
    agent = SDRAgent()
    phone = "5511999888777"
    
    # Teste 1: Saudação inicial
    console.print("[cyan]1. Testando saudação inicial...[/cyan]")
    response, _ = await agent.start_conversation(phone)
    
    # Verifica características
    checks = {
        "Nome Leonardo": "Leonardo" in response,
        "Empresa SolarPrime": "SolarPrime" in response or "Solar Prime" in response,
        "Linguagem brasileira": any(word in response for word in ["Opa", "tudo joia", "Olha só", "cara", "Nossa"]),
        "Emoji presente": any(emoji in response for emoji in ["☀️", "😊", "🌟", "💡", "⚡"]),
        "Tom entusiasmado": "!" in response,
        "Menciona economia": "economia" in response.lower() or "economizar" in response.lower()
    }
    
    # Mostra resultados
    table = Table(title="Verificação da Saudação")
    table.add_column("Característica", style="cyan")
    table.add_column("Status", style="green")
    
    for check, result in checks.items():
        table.add_row(check, "✅ OK" if result else "❌ Falhou")
    
    console.print(table)
    
    # Teste 2: Resposta a nome
    console.print("\n[cyan]2. Testando resposta ao nome...[/cyan]")
    response2, meta2 = await agent.process_message("João Paulo", phone)
    
    checks2 = {
        "Usa o nome": "João Paulo" in response2,
        "Tom caloroso": any(word in response2 for word in ["Prazer", "legal", "massa", "show"]),
        "Não repete apresentação": not ("Leonardo Ferraz" in response2 and "especialista" in response2),
        "Linguagem natural": any(word in response2 for word in ["cara", "olha", "né", "pra"])
    }
    
    table2 = Table(title="Verificação da Resposta ao Nome")
    table2.add_column("Característica", style="cyan")
    table2.add_column("Status", style="green")
    
    for check, result in checks2.items():
        table2.add_row(check, "✅ OK" if result else "❌ Falhou")
    
    console.print(table2)
    
    # Teste 3: Resposta sobre conta alta
    console.print("\n[cyan]3. Testando resposta a conta alta...[/cyan]")
    response3, meta3 = await agent.process_message("minha conta vem uns 5000 reais", phone)
    
    checks3 = {
        "Reação entusiasmada": any(word in response3 for word in ["Nossa", "Cara", "MARAVILHA", "😱"]),
        "Menciona valor": "5" in response3 or "5000" in response3 or "5.000" in response3,
        "Demonstra empolgação": response3.count("!") >= 2,
        "Usa CAPS estratégico": any(word.isupper() and len(word) > 3 for word in response3.split()),
        "Menciona economia específica": "%" in response3 or "desconto" in response3.lower()
    }
    
    table3 = Table(title="Verificação da Resposta a Conta Alta")
    table3.add_column("Característica", style="cyan")
    table3.add_column("Status", style="green")
    
    for check, result in checks3.items():
        table3.add_row(check, "✅ OK" if result else "❌ Falhou")
    
    console.print(table3)
    
    # Resumo final
    console.print("\n[bold green]📊 RESUMO DO TESTE[/bold green]")
    console.print(f"Nome coletado: {meta3['lead_info'].get('name', 'Não coletado')}")
    console.print(f"Valor da conta: {meta3['lead_info'].get('bill_value', 'Não coletado')}")
    console.print(f"Estágio atual: {meta3['stage']}")
    
    # Mostra trechos da conversa
    console.print("\n[bold yellow]💬 Trechos da Conversa:[/bold yellow]")
    console.print(f"\n[dim]Saudação:[/dim]\n{response[:200]}...")
    console.print(f"\n[dim]Resposta ao nome:[/dim]\n{response2[:200]}...")
    console.print(f"\n[dim]Resposta à conta:[/dim]\n{response3[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_leonardo_characteristics())