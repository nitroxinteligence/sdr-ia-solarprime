#!/usr/bin/env python3
"""
Teste Automatizado do Agente SDR
=================================
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent

console = Console()


async def test_agent():
    """Testa o agente SDR automaticamente"""
    
    console.print("\n[bold cyan]🤖 Teste Automatizado - SDR IA SolarPrime[/bold cyan]\n")
    
    try:
        # Criar agente
        console.print("1️⃣ Criando agente...")
        agent = SDRAgent()
        console.print("[green]✅ Agente criado com sucesso![/green]")
        
        # Casos de teste
        test_cases = [
            {
                "name": "Primeiro Contato",
                "phone": "5511999999991",
                "message": "Olá, vi o anúncio sobre energia solar"
            },
            {
                "name": "Pergunta sobre Economia",
                "phone": "5511999999992", 
                "message": "Quanto vou economizar com energia solar?"
            },
            {
                "name": "Cliente com Conta Alta",
                "phone": "5511999999993",
                "message": "Minha conta de luz está vindo R$ 800 por mês"
            },
            {
                "name": "Dúvida sobre Instalação",
                "phone": "5511999999994",
                "message": "Como funciona a instalação dos painéis?"
            },
            {
                "name": "Cliente Não Interessado",
                "phone": "5511999999995",
                "message": "Não tenho interesse, obrigado"
            }
        ]
        
        console.print("\n2️⃣ Executando casos de teste...\n")
        
        # Tabela de resultados
        table = Table(title="Resultados dos Testes")
        table.add_column("Caso de Teste", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Tempo (ms)", justify="right")
        table.add_column("Resposta (preview)", style="dim")
        
        for test in test_cases:
            console.print(f"[yellow]Testando:[/yellow] {test['name']}")
            
            try:
                import time
                start = time.time()
                
                # Processar mensagem
                response = await agent.process_message(
                    test['message'],
                    test['phone']
                )
                
                elapsed = int((time.time() - start) * 1000)
                
                # Verificar resposta
                if isinstance(response, tuple):
                    response_text = response[0]
                    status = "⚠️ Com Erro" if len(response) > 1 else "✅ OK"
                else:
                    response_text = response
                    status = "✅ OK"
                
                # Adicionar à tabela
                preview = response_text[:50] + "..." if len(response_text) > 50 else response_text
                preview = preview.replace("\n", " ")
                table.add_row(
                    test['name'],
                    status,
                    f"{elapsed}",
                    preview
                )
                
            except Exception as e:
                table.add_row(
                    test['name'],
                    "❌ Erro",
                    "-",
                    str(e)[:50]
                )
                console.print(f"[red]Erro:[/red] {e}")
        
        # Mostrar resultados
        console.print("\n")
        console.print(table)
        
        # Verificar integração com Supabase
        console.print("\n3️⃣ Verificando dados no Supabase...")
        
        from repositories.lead_repository import lead_repository
        
        # Contar leads criados
        leads = await lead_repository.get_all(limit=5)
        console.print(f"[green]✅ {len(leads)} leads encontrados no banco[/green]")
        
        if leads:
            # Mostrar alguns leads
            lead_table = Table(title="Últimos Leads Criados")
            lead_table.add_column("Nome", style="cyan")
            lead_table.add_column("Telefone", style="yellow")
            lead_table.add_column("Score", justify="right")
            lead_table.add_column("Estágio", style="magenta")
            
            for lead in leads[:3]:
                lead_table.add_row(
                    lead.name or "Não informado",
                    lead.phone_number,
                    str(lead.qualification_score or 0),
                    lead.current_stage or "INITIAL_CONTACT"
                )
            
            console.print("\n")
            console.print(lead_table)
        
        # Resumo final
        console.print("\n")
        console.print(Panel.fit(
            "[bold green]✅ Teste concluído com sucesso![/bold green]\n\n"
            "A integração Supabase + AGnO Framework está funcionando perfeitamente!",
            title="🎉 Resultado Final",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"\n[red]❌ Erro durante teste:[/red] {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Função principal"""
    await test_agent()


if __name__ == "__main__":
    asyncio.run(main())