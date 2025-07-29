"""
Test Message Buffer System
==========================
Script para testar o sistema de buffer de mensagens simulando
usuários que enviam múltiplas mensagens rapidamente
"""

import asyncio
import json
from datetime import datetime
from loguru import logger
from services.message_buffer_service import message_buffer_service
from services.redis_service import redis_service
from colorama import init, Fore, Style

# Inicializar colorama para saída colorida
init()

# Configurar logger para o teste
logger.add("tests/logs/test_buffer_{time}.log", rotation="1 MB")


class BufferTestScenarios:
    """Cenários de teste para o sistema de buffer"""
    
    @staticmethod
    def get_fragmented_messages():
        """Mensagens picotadas típicas de usuário"""
        return [
            {
                "content": "Oi",
                "type": "text",
                "delay": 0.5
            },
            {
                "content": "Eu vi o anúncio de vocês",
                "type": "text", 
                "delay": 1.2
            },
            {
                "content": "sobre energia solar",
                "type": "text",
                "delay": 0.8
            },
            {
                "content": "Queria saber mais informações",
                "type": "text",
                "delay": 1.5
            },
            {
                "content": "Quanto custa?",
                "type": "text",
                "delay": 2.0
            }
        ]
    
    @staticmethod
    def get_mixed_media_messages():
        """Mensagens com mídia intercalada"""
        return [
            {
                "content": "Aqui está minha conta",
                "type": "text",
                "delay": 1.0
            },
            {
                "content": "",
                "type": "image",
                "media_data": {"mimetype": "image/jpeg", "filename": "conta_luz.jpg"},
                "delay": 3.0
            },
            {
                "content": "É essa mesmo",
                "type": "text",
                "delay": 1.5
            },
            {
                "content": "Consegue fazer uma simulação?",
                "type": "text",
                "delay": 2.0
            }
        ]
    
    @staticmethod
    def get_rapid_fire_messages():
        """Mensagens muito rápidas (ansiedade)"""
        return [
            {
                "content": "oi",
                "type": "text",
                "delay": 0.1
            },
            {
                "content": "tudo bem?",
                "type": "text",
                "delay": 0.2
            },
            {
                "content": "preciso falar sobre energia solar",
                "type": "text",
                "delay": 0.3
            },
            {
                "content": "é urgente",
                "type": "text",
                "delay": 0.2
            },
            {
                "content": "pode me ajudar?",
                "type": "text",
                "delay": 0.1
            },
            {
                "content": "???",
                "type": "text",
                "delay": 0.5
            }
        ]
    
    @staticmethod
    def get_correction_messages():
        """Mensagens com correções"""
        return [
            {
                "content": "Meu consumo é de 500kw",
                "type": "text",
                "delay": 1.0
            },
            {
                "content": "Ops, quis dizer 500kwh",
                "type": "text",
                "delay": 2.0
            },
            {
                "content": "Por mês",
                "type": "text",
                "delay": 1.0
            }
        ]


async def simulate_user_messages(
    phone: str,
    messages: list,
    scenario_name: str
):
    """Simula envio de mensagens de um usuário"""
    
    print(f"\n{Fore.YELLOW}━━━ Cenário: {scenario_name} ━━━{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Telefone: {phone}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Total de mensagens: {len(messages)}{Style.RESET_ALL}\n")
    
    # Callback para processar mensagens consolidadas
    async def process_callback(consolidated_messages):
        print(f"\n{Fore.GREEN}✓ Buffer processado!{Style.RESET_ALL}")
        print(f"Mensagens consolidadas: {len(consolidated_messages)}")
        
        # Mostrar conteúdo consolidado
        text_content = []
        media_count = 0
        
        for msg in consolidated_messages:
            if msg["type"] == "text" and msg.get("content"):
                text_content.append(msg["content"])
            elif msg["type"] in ["image", "audio", "document"]:
                media_count += 1
        
        if text_content:
            print(f"\n{Fore.MAGENTA}Texto consolidado:{Style.RESET_ALL}")
            print(f'"{" ".join(text_content)}"')
        
        if media_count > 0:
            print(f"\n{Fore.MAGENTA}Mídia recebida: {media_count} arquivo(s){Style.RESET_ALL}")
    
    # Enviar mensagens com delays
    for i, msg in enumerate(messages):
        # Preparar dados da mensagem
        message_data = {
            "id": f"test_msg_{datetime.now().timestamp()}_{i}",
            "content": msg["content"],
            "type": msg["type"],
            "media_data": msg.get("media_data"),
            "timestamp": datetime.now().isoformat(),
            "pushName": f"Teste {scenario_name}"
        }
        
        # Adicionar ao buffer
        added = await message_buffer_service.add_message(
            phone=phone,
            message_data=message_data,
            process_callback=process_callback
        )
        
        if added:
            print(f"{Fore.BLUE}→ Mensagem {i+1}/{len(messages)} adicionada ao buffer{Style.RESET_ALL}")
            if msg["type"] == "text":
                print(f'  "{msg["content"]}"')
            else:
                print(f'  [{msg["type"].upper()}]')
        else:
            print(f"{Fore.RED}✗ Falha ao adicionar mensagem ao buffer{Style.RESET_ALL}")
        
        # Aguardar delay antes da próxima mensagem
        if i < len(messages) - 1:  # Não esperar após última mensagem
            delay = msg.get("delay", 1.0)
            print(f"{Fore.LIGHTBLACK_EX}  Aguardando {delay}s...{Style.RESET_ALL}")
            await asyncio.sleep(delay)
    
    # Aguardar processamento do buffer
    print(f"\n{Fore.YELLOW}⏳ Aguardando timeout do buffer ({message_buffer_service.timeout_seconds}s)...{Style.RESET_ALL}")
    await asyncio.sleep(message_buffer_service.timeout_seconds + 1)


async def test_buffer_status():
    """Testa obtenção de status do buffer"""
    
    print(f"\n{Fore.YELLOW}━━━ Teste de Status do Buffer ━━━{Style.RESET_ALL}")
    
    phone = "5511999888777"
    
    # Adicionar algumas mensagens
    for i in range(3):
        await message_buffer_service.add_message(
            phone=phone,
            message_data={
                "id": f"status_test_{i}",
                "content": f"Mensagem de teste {i+1}",
                "type": "text",
                "timestamp": datetime.now().isoformat()
            },
            process_callback=lambda msgs: print(f"Processadas {len(msgs)} mensagens")
        )
        await asyncio.sleep(0.5)
    
    # Obter status
    status = await message_buffer_service.get_buffer_status(phone)
    
    print(f"\n{Fore.GREEN}Status do Buffer:{Style.RESET_ALL}")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # Limpar buffer
    await message_buffer_service.clear_buffer(phone)
    print(f"\n{Fore.YELLOW}Buffer limpo{Style.RESET_ALL}")


async def test_force_process():
    """Testa processamento forçado do buffer"""
    
    print(f"\n{Fore.YELLOW}━━━ Teste de Processamento Forçado ━━━{Style.RESET_ALL}")
    
    phone = "5511888777666"
    processed = False
    
    async def process_callback(messages):
        nonlocal processed
        processed = True
        print(f"{Fore.GREEN}✓ Callback executado com {len(messages)} mensagens{Style.RESET_ALL}")
    
    # Adicionar mensagens
    for i in range(3):
        await message_buffer_service.add_message(
            phone=phone,
            message_data={
                "id": f"force_test_{i}",
                "content": f"Mensagem {i+1}",
                "type": "text",
                "timestamp": datetime.now().isoformat()
            },
            process_callback=process_callback
        )
    
    print(f"{Fore.BLUE}3 mensagens adicionadas ao buffer{Style.RESET_ALL}")
    
    # Forçar processamento imediato
    print(f"{Fore.YELLOW}Forçando processamento...{Style.RESET_ALL}")
    await message_buffer_service.force_process(phone)
    
    # Verificar se foi processado
    await asyncio.sleep(0.5)
    if processed:
        print(f"{Fore.GREEN}✓ Processamento forçado funcionou!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Processamento forçado falhou{Style.RESET_ALL}")


async def run_all_tests():
    """Executa todos os testes"""
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🧪 TESTE DO SISTEMA DE BUFFER DE MENSAGENS{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    
    # Verificar conexão com Redis
    print(f"\n{Fore.YELLOW}Verificando conexão com Redis...{Style.RESET_ALL}")
    await redis_service.connect()
    
    if redis_service.client:
        print(f"{Fore.GREEN}✓ Redis conectado!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Redis não disponível - testes podem falhar{Style.RESET_ALL}")
        return
    
    # Executar cenários de teste
    scenarios = [
        ("Mensagens Fragmentadas", "5511999999001", BufferTestScenarios.get_fragmented_messages()),
        ("Mensagens com Mídia", "5511999999002", BufferTestScenarios.get_mixed_media_messages()),
        ("Mensagens Rápidas", "5511999999003", BufferTestScenarios.get_rapid_fire_messages()),
        ("Mensagens com Correção", "5511999999004", BufferTestScenarios.get_correction_messages())
    ]
    
    for scenario_name, phone, messages in scenarios:
        await simulate_user_messages(phone, messages, scenario_name)
        await asyncio.sleep(2)  # Pausa entre cenários
    
    # Testes adicionais
    await test_buffer_status()
    await test_force_process()
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ TODOS OS TESTES CONCLUÍDOS!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    # Executar testes
    asyncio.run(run_all_tests())