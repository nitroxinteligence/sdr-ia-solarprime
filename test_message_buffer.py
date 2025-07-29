#!/usr/bin/env python3
"""
Test Message Buffer
===================
Script para testar o sistema de buffer de mensagens
"""

import asyncio
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.message_buffer_service import message_buffer_service

console = Console()


async def test_buffer():
    """Testa o sistema de buffer"""
    
    console.print(Panel(
        "[bold]🧪 Teste do Sistema de Buffer de Mensagens[/bold]\n"
        "Este teste simula o envio de múltiplas mensagens picotadas",
        border_style="blue"
    ))
    
    # Configurações
    phone = "5511999999999"
    messages_to_send = [
        "Olá, tudo bem?",
        "Gostaria de saber mais sobre energia solar",
        "Minha conta de luz está muito alta",
        "Chega a R$ 800 por mês",
        "Vocês podem me ajudar?"
    ]
    
    # Variável para armazenar mensagens processadas
    processed_messages = []
    
    # Callback para processar mensagens
    async def process_callback(messages):
        console.print(f"\n[green]✅ Callback executado com {len(messages)} mensagens![/green]")
        for i, msg in enumerate(messages):
            console.print(f"  {i+1}. {msg.get('content', '')}")
        processed_messages.extend(messages)
    
    # Testar envio de mensagens
    console.print(f"\n[yellow]📤 Enviando {len(messages_to_send)} mensagens...[/yellow]")
    
    for i, content in enumerate(messages_to_send):
        message_data = {
            "id": f"TEST_{i}_{datetime.now().timestamp()}",
            "content": content,
            "type": "text",
            "media_data": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Adicionar ao buffer
        added = await message_buffer_service.add_message(
            phone=phone,
            message_data=message_data,
            process_callback=process_callback
        )
        
        if added:
            console.print(f"  ✅ Mensagem {i+1} adicionada ao buffer")
        else:
            console.print(f"  ❌ Mensagem {i+1} não foi bufferizada")
        
        # Status do buffer
        status = await message_buffer_service.get_buffer_status(phone)
        console.print(f"     Buffer: {status['buffer_size']} mensagens, Timer ativo: {status['has_active_timer']}")
        
        # Pequeno delay entre mensagens
        await asyncio.sleep(0.5)
    
    # Aguardar processamento
    console.print(f"\n[yellow]⏳ Aguardando timeout do buffer ({message_buffer_service.timeout_seconds}s)...[/yellow]")
    
    # Aguardar um pouco mais que o timeout
    await asyncio.sleep(message_buffer_service.timeout_seconds + 1)
    
    # Verificar resultado
    console.print(f"\n[bold]📊 Resultado:[/bold]")
    console.print(f"Mensagens enviadas: {len(messages_to_send)}")
    console.print(f"Mensagens processadas: {len(processed_messages)}")
    
    if len(processed_messages) == len(messages_to_send):
        console.print("[green]✅ Todas as mensagens foram processadas juntas![/green]")
    else:
        console.print("[red]❌ Nem todas as mensagens foram processadas[/red]")
    
    # Testar force process
    if Confirm.ask("\n[yellow]Testar processamento forçado?[/yellow]"):
        # Enviar mais algumas mensagens
        console.print("\n[yellow]📤 Enviando mais 3 mensagens...[/yellow]")
        
        for i in range(3):
            message_data = {
                "id": f"TEST_FORCE_{i}_{datetime.now().timestamp()}",
                "content": f"Mensagem forçada {i+1}",
                "type": "text",
                "media_data": None,
                "timestamp": datetime.now().isoformat()
            }
            
            await message_buffer_service.add_message(
                phone=phone,
                message_data=message_data,
                process_callback=process_callback
            )
        
        # Status antes de forçar
        status = await message_buffer_service.get_buffer_status(phone)
        console.print(f"\nBuffer antes: {status['buffer_size']} mensagens")
        
        # Forçar processamento
        console.print("[yellow]⚡ Forçando processamento...[/yellow]")
        await message_buffer_service.force_process(phone)
        
        # Status depois
        await asyncio.sleep(0.5)
        status = await message_buffer_service.get_buffer_status(phone)
        console.print(f"Buffer depois: {status['buffer_size']} mensagens")


async def main():
    """Função principal"""
    try:
        # Verificar configurações
        console.print("[bold]⚙️  Configurações:[/bold]")
        console.print(f"Buffer habilitado: {message_buffer_service.enabled}")
        console.print(f"Timeout: {message_buffer_service.timeout_seconds}s")
        console.print(f"Máximo de mensagens: {message_buffer_service.max_messages}")
        
        if not message_buffer_service.enabled:
            console.print("\n[red]❌ Buffer desabilitado! Configure MESSAGE_BUFFER_ENABLED=true[/red]")
            return
        
        await test_buffer()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Teste interrompido[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Erro: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())