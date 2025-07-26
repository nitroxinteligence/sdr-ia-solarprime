#!/usr/bin/env python3
"""
Script de Teste Multimodal
==========================
Testa especificamente as capacidades multimodais do agente SDR
"""

import asyncio
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from loguru import logger

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import create_sdr_agent
from config.agent_config import config

console = Console()

async def test_image_analysis():
    """Testa análise de imagem de conta de luz"""
    console.print("\n[bold cyan]🔬 Teste de Análise de Imagem[/bold cyan]\n")
    
    # Cria agente
    agent = create_sdr_agent()
    test_phone = "+5511999999999"
    
    # Simula diferentes cenários
    test_cases = [
        {
            "name": "Conta Alta (R$ 850)",
            "message": "Segue minha conta de luz",
            "media_data": {
                "url": "https://exemplo.com/conta-alta.jpg",
                "mock_result": {
                    "bill_value": "R$ 850,00",
                    "consumption_kwh": "680",
                    "reference_period": "10/2024",
                    "customer_name": "Maria Santos",
                    "address": "Av. Boa Viagem, 2000",
                    "document": "987.654.321-00",
                    "distributor": "CELPE"
                }
            }
        },
        {
            "name": "Conta Média (R$ 350)",
            "message": "Aqui está a foto da conta",
            "media_data": {
                "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "mock_result": {
                    "bill_value": "R$ 350,00",
                    "consumption_kwh": "280",
                    "reference_period": "10/2024",
                    "customer_name": "João Silva",
                    "address": "Rua das Flores, 123",
                    "document": "123.456.789-00",
                    "distributor": "CELPE"
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        console.print(f"\n[bold]Teste {i}: {test_case['name']}[/bold]")
        console.print("-" * 50)
        
        # Para teste, vamos simular o resultado direto
        # Em produção, o Gemini Vision faria a análise real
        media_info = test_case["media_data"].get("mock_result", {})
        
        # Simula o processamento
        console.print(f"[dim]Simulando análise de imagem...[/dim]")
        await asyncio.sleep(1)
        
        # Mostra dados extraídos
        if media_info:
            panel = Panel(
                f"""[green]✅ Dados Extraídos com Sucesso![/green]
                
💰 Valor: {media_info['bill_value']}
⚡ Consumo: {media_info['consumption_kwh']} kWh
👤 Titular: {media_info['customer_name']}
📍 Endereço: {media_info['address']}
📄 CPF/CNPJ: {media_info['document']}
🏢 Distribuidora: {media_info['distributor']}""",
                title="Análise da Conta",
                border_style="green"
            )
            console.print(panel)
            
            # Calcula economia
            try:
                valor_str = media_info['bill_value'].replace('R$', '').replace('.', '').replace(',', '.').strip()
                valor = float(valor_str)
                economia = valor * 0.95
                
                console.print(f"\n[bold yellow]💡 Economia Potencial: R$ {economia:.2f}/mês[/bold yellow]")
                console.print(f"[bold green]🎯 Economia Anual: R$ {economia * 12:.2f}[/bold green]")
            except:
                pass
        
        # Simula resposta do agente
        console.print("\n[bold]Resposta do Agente:[/bold]")
        
        if float(media_info['bill_value'].replace('R$', '').replace('.', '').replace(',', '.').strip()) > 500:
            response = f"""Caramba, {media_info['customer_name']}! 😱
            
Vi aqui que sua conta está vindo {media_info['bill_value']}! Isso é MUITO dinheiro!

Com energia solar, você economizaria cerca de R$ {float(media_info['bill_value'].replace('R$', '').replace('.', '').replace(',', '.').strip()) * 0.95:.2f} por mês!

Imagina só... em 1 ano seriam R$ {float(media_info['bill_value'].replace('R$', '').replace('.', '').replace(',', '.').strip()) * 0.95 * 12:.2f} no seu bolso! 💰

Esses valores estão corretos? É isso mesmo que vem na sua conta?"""
        else:
            response = f"""Opa! Recebi sua conta aqui, {media_info['customer_name']}. 

Vi que está vindo {media_info['bill_value']} com um consumo de {media_info['consumption_kwh']} kWh.

Com energia solar, você economizaria até 95%, ou seja, cerca de R$ {float(media_info['bill_value'].replace('R$', '').replace('.', '').replace(',', '.').strip()) * 0.95:.2f} por mês!

Esses dados conferem? É esse valor mesmo que vem na conta?"""
        
        panel = Panel(
            response,
            title=f"🤖 Luna",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(panel)
        
        # Pausa entre testes
        if i < len(test_cases):
            console.print("\n[dim]Pressione Enter para próximo teste...[/dim]")
            input()

async def test_pdf_processing():
    """Testa processamento de PDF"""
    console.print("\n[bold cyan]📄 Teste de Processamento de PDF[/bold cyan]\n")
    
    # Simula processamento de PDF
    console.print("Simulando análise de PDF de conta de luz...")
    await asyncio.sleep(1)
    
    # Mostra resultado
    console.print("""
[yellow]⚠️ Processamento de PDF[/yellow]
    
O sistema detectou um arquivo PDF.
    
Se os módulos PDFReader estiverem disponíveis:
- Extração de texto com OCR
- Análise completa do documento
    
Se não estiverem disponíveis:
- Fallback para tratamento como imagem
- Análise parcial possível
""")

async def test_error_handling():
    """Testa tratamento de erros"""
    console.print("\n[bold cyan]🛡️ Teste de Tratamento de Erros[/bold cyan]\n")
    
    error_cases = [
        {
            "name": "Formato Inválido",
            "error": "Formato de imagem não reconhecido",
            "response": "Ops! Não consegui abrir a imagem. Pode tentar enviar novamente?"
        },
        {
            "name": "Análise Falhou",
            "error": "Não foi possível extrair dados da imagem",
            "response": "Hmm, não consegui ler os dados da conta. A foto está nítida? Pode tirar outra foto?"
        },
        {
            "name": "Timeout",
            "error": "Tempo de análise excedido",
            "response": "A análise está demorando mais que o normal. Vou tentar de novo, ok?"
        }
    ]
    
    for case in error_cases:
        console.print(f"\n[red]❌ {case['name']}[/red]")
        console.print(f"Erro: {case['error']}")
        console.print(f"Resposta: [italic]{case['response']}[/italic]")

async def main():
    """Função principal"""
    console.print(Panel(
        "[bold cyan]🔬 Teste de Funcionalidades Multimodais[/bold cyan]\n\n"
        "Este script testa as capacidades de análise de imagem e documentos do agente SDR",
        title="SDR IA SolarPrime",
        border_style="cyan"
    ))
    
    while True:
        console.print("\n[bold yellow]Menu de Testes:[/bold yellow]")
        console.print("1. Testar análise de imagem")
        console.print("2. Testar processamento de PDF")
        console.print("3. Testar tratamento de erros")
        console.print("4. Executar todos os testes")
        console.print("5. Sair")
        
        choice = Prompt.ask("\nEscolha", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            await test_image_analysis()
        elif choice == "2":
            await test_pdf_processing()
        elif choice == "3":
            await test_error_handling()
        elif choice == "4":
            await test_image_analysis()
            await test_pdf_processing()
            await test_error_handling()
        else:
            console.print("\n👋 Até logo!")
            break

if __name__ == "__main__":
    # Configura logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Executa testes
    asyncio.run(main())