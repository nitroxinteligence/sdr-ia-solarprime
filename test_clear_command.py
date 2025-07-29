#!/usr/bin/env python3
"""
Test Clear Command
==================
Script para testar o comando #CLEAR do WhatsApp
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

from services.whatsapp_service import whatsapp_service
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from repositories.lead_repository import lead_repository

console = Console()


async def test_clear_command():
    """Testa o comando #CLEAR"""
    
    console.print(Panel(
        "[bold]🧪 Teste do Comando #CLEAR[/bold]\n"
        "Este teste simulará o envio do comando #CLEAR",
        border_style="blue"
    ))
    
    # Pedir número de telefone
    phone = Prompt.ask("Digite o número de WhatsApp (com código do país)", default="5511999999999")
    
    # Verificar se existe conversa
    console.print("\n[yellow]🔍 Verificando dados existentes...[/yellow]")
    
    conversation = await conversation_repository.get_conversation_by_phone(phone)
    if conversation:
        console.print(f"✅ Conversa encontrada: ID {conversation.id}")
        messages = await message_repository.get_conversation_messages(conversation.id)
        console.print(f"📩 Total de mensagens: {len(messages)}")
    else:
        console.print("❌ Nenhuma conversa encontrada para este número")
    
    lead = await lead_repository.get_lead_by_phone(phone)
    if lead:
        console.print(f"✅ Lead encontrado: {lead.name}")
    else:
        console.print("❌ Nenhum lead encontrado")
    
    # Confirmar execução
    if not Confirm.ask("\n[yellow]Deseja testar o comando #CLEAR?[/yellow]"):
        console.print("[red]Teste cancelado[/red]")
        return
    
    # Simular mensagem com comando #CLEAR
    message_info = {
        "id": f"TEST_{datetime.now().timestamp()}",
        "from": phone,
        "content": "#CLEAR",
        "type": "text",
        "media_data": None,
        "timestamp": datetime.now().timestamp(),
        "pushName": "Teste"
    }
    
    console.print("\n[green]📤 Enviando comando #CLEAR...[/green]")
    
    try:
        # Processar comando
        result = await whatsapp_service._handle_clear_command(phone, message_info)
        
        console.print("\n[green]✅ Comando executado com sucesso![/green]")
        console.print(f"\nResposta:\n{result}")
        
        # Verificar se dados foram limpos
        console.print("\n[yellow]🔍 Verificando se dados foram limpos...[/yellow]")
        
        conversation_after = await conversation_repository.get_conversation_by_phone(phone)
        if conversation_after:
            messages_after = await message_repository.get_conversation_messages(conversation_after.id)
            console.print(f"📩 Mensagens após limpeza: {len(messages_after)}")
        else:
            console.print("✅ Conversa removida")
        
        lead_after = await lead_repository.get_lead_by_phone(phone)
        if lead_after:
            console.print("❌ Lead ainda existe")
        else:
            console.print("✅ Lead removido")
        
    except Exception as e:
        console.print(f"\n[red]❌ Erro ao executar comando: {e}[/red]")
        import traceback
        traceback.print_exc()


async def main():
    """Função principal"""
    try:
        await test_clear_command()
    except KeyboardInterrupt:
        console.print("\n[yellow]Teste interrompido[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Erro: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())