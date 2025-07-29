"""
Test Buffer Integration with SDR Agent V2
=========================================
Testa a integração completa do sistema de buffer com o agente SDR
"""

import asyncio
import json
from datetime import datetime
from loguru import logger
from colorama import init, Fore, Style
from agents.sdr_agent_v2 import SDRAgentV2
from config.config import Config
from services.message_buffer_service import message_buffer_service

# Inicializar colorama
init()

# Configurar logger
logger.add("tests/logs/test_buffer_integration_{time}.log", rotation="1 MB")


class IntegrationTestScenarios:
    """Cenários de teste de integração"""
    
    @staticmethod
    def get_qualification_flow():
        """Fluxo típico de qualificação"""
        return [
            {
                "messages": [
                    {"content": "Oi", "type": "text", "delay": 0.5},
                    {"content": "Vi o anúncio de vocês", "type": "text", "delay": 1.0},
                    {"content": "Sobre energia solar", "type": "text", "delay": 0.8}
                ],
                "expected_stage": "IDENTIFICATION",
                "description": "Primeiro contato"
            },
            {
                "messages": [
                    {"content": "Meu nome é João Silva", "type": "text", "delay": 0.5},
                    {"content": "Moro em casa própria", "type": "text", "delay": 1.2},
                    {"content": "Em Boa Viagem", "type": "text", "delay": 0.8}
                ],
                "expected_stage": "DISCOVERY",
                "description": "Identificação e descoberta"
            },
            {
                "messages": [
                    {"content": "Minha conta vem uns 400 reais", "type": "text", "delay": 1.0},
                    {"content": "Às vezes mais", "type": "text", "delay": 0.8},
                    {"content": "No verão chega a 500", "type": "text", "delay": 1.2}
                ],
                "expected_stage": "QUALIFICATION",
                "description": "Informações de consumo"
            }
        ]
    
    @staticmethod
    def get_urgent_inquiry():
        """Consulta urgente"""
        return [
            {
                "messages": [
                    {"content": "Preciso urgente", "type": "text", "delay": 0.2},
                    {"content": "Quanto custa?", "type": "text", "delay": 0.3},
                    {"content": "Vocês financiam?", "type": "text", "delay": 0.2},
                    {"content": "Tem desconto à vista?", "type": "text", "delay": 0.4},
                    {"content": "Me liga por favor", "type": "text", "delay": 0.3},
                    {"content": "11 99999-8888", "type": "text", "delay": 0.5}
                ],
                "expected_intents": ["urgência", "dúvida", "interesse"],
                "description": "Cliente ansioso com múltiplas perguntas"
            }
        ]


async def test_agent_buffer_integration():
    """Testa integração completa com o agente"""
    
    print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🤖 TESTE DE INTEGRAÇÃO: BUFFER + SDR AGENT V2{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    
    # Criar configuração e agente
    config = Config()
    agent = SDRAgentV2(config)
    
    # Inicializar agente
    print(f"\n{Fore.YELLOW}Inicializando SDR Agent V2...{Style.RESET_ALL}")
    try:
        await agent.initialize()
        print(f"{Fore.GREEN}✓ Agente inicializado com sucesso{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Erro ao inicializar agente: {e}{Style.RESET_ALL}")
        return
    
    # Testar fluxo de qualificação
    print(f"\n{Fore.CYAN}━━━ Testando Fluxo de Qualificação ━━━{Style.RESET_ALL}")
    
    phone = "5511999888777"
    qualification_flow = IntegrationTestScenarios.get_qualification_flow()
    
    for step in qualification_flow:
        print(f"\n{Fore.YELLOW}📍 {step['description']}{Style.RESET_ALL}")
        
        # Simular envio das mensagens
        messages_to_send = []
        
        for msg in step['messages']:
            messages_to_send.append({
                "id": f"test_{datetime.now().timestamp()}",
                "content": msg["content"],
                "type": msg["type"],
                "timestamp": datetime.now().isoformat(),
                "pushName": "João Silva"
            })
            
            print(f"{Fore.BLUE}→ \"{msg['content']}\"{Style.RESET_ALL}")
            await asyncio.sleep(msg["delay"])
        
        # Processar com o agente
        try:
            response, metadata = await agent.process_buffered_messages(
                messages=messages_to_send,
                phone_number=phone,
                consolidated_content=" ".join([m["content"] for m in messages_to_send]),
                media_items=[]
            )
            
            print(f"\n{Fore.GREEN}✓ Resposta do agente:{Style.RESET_ALL}")
            print(f'"{response}"')
            
            print(f"\n{Fore.MAGENTA}Metadados:{Style.RESET_ALL}")
            print(f"- Estágio: {metadata.get('stage', 'N/A')}")
            print(f"- Lead Score: {metadata.get('lead_score', 0)}")
            print(f"- Tempo de resposta: {metadata.get('response_time', 0):.2f}s")
            print(f"- Mensagens bufferizadas: {metadata.get('buffered_messages', 0)}")
            
            if metadata.get('buffer_analysis'):
                analysis = metadata['buffer_analysis']
                print(f"\n{Fore.MAGENTA}Análise do Buffer:{Style.RESET_ALL}")
                print(f"- Fragmentado: {'Sim' if analysis.get('fragmented') else 'Não'}")
                print(f"- Urgente: {'Sim' if analysis.get('urgent') else 'Não'}")
                print(f"- Tem perguntas: {'Sim' if analysis.get('has_questions') else 'Não'}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Erro ao processar: {e}{Style.RESET_ALL}")
        
        await asyncio.sleep(3)  # Pausa entre etapas
    
    # Testar consulta urgente
    print(f"\n{Fore.CYAN}━━━ Testando Consulta Urgente ━━━{Style.RESET_ALL}")
    
    phone_urgent = "5511888999777"
    urgent_scenario = IntegrationTestScenarios.get_urgent_inquiry()[0]
    
    print(f"\n{Fore.YELLOW}📍 {urgent_scenario['description']}{Style.RESET_ALL}")
    
    # Preparar mensagens
    urgent_messages = []
    for msg in urgent_scenario['messages']:
        urgent_messages.append({
            "id": f"urgent_{datetime.now().timestamp()}",
            "content": msg["content"],
            "type": msg["type"],
            "timestamp": datetime.now().isoformat(),
            "pushName": "Cliente Urgente"
        })
        print(f"{Fore.BLUE}→ \"{msg['content']}\"{Style.RESET_ALL}")
        await asyncio.sleep(msg["delay"])
    
    # Processar
    try:
        response, metadata = await agent.process_buffered_messages(
            messages=urgent_messages,
            phone_number=phone_urgent,
            consolidated_content=" ".join([m["content"] for m in urgent_messages]),
            media_items=[]
        )
        
        print(f"\n{Fore.GREEN}✓ Resposta do agente:{Style.RESET_ALL}")
        print(f'"{response}"')
        
        # Verificar se detectou urgência
        if metadata.get('buffer_analysis', {}).get('urgent'):
            print(f"\n{Fore.YELLOW}⚡ URGÊNCIA DETECTADA!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}✗ Erro ao processar consulta urgente: {e}{Style.RESET_ALL}")


async def test_media_buffer():
    """Testa buffer com mensagens de mídia"""
    
    print(f"\n{Fore.CYAN}━━━ Testando Buffer com Mídia ━━━{Style.RESET_ALL}")
    
    config = Config()
    agent = SDRAgentV2(config)
    await agent.initialize()
    
    phone = "5511777888999"
    
    # Simular mensagens com conta de luz
    messages = [
        {
            "id": "media_1",
            "content": "Boa tarde",
            "type": "text",
            "timestamp": datetime.now().isoformat(),
            "pushName": "Maria Santos"
        },
        {
            "id": "media_2",
            "content": "Segue minha conta de luz",
            "type": "text",
            "timestamp": datetime.now().isoformat(),
            "pushName": "Maria Santos"
        },
        {
            "id": "media_3",
            "content": "",
            "type": "image",
            "timestamp": datetime.now().isoformat(),
            "pushName": "Maria Santos",
            "media_data": {
                "mimetype": "image/jpeg",
                "filename": "conta_luz.jpg"
            }
        },
        {
            "id": "media_4",
            "content": "Consegue fazer a simulação?",
            "type": "text",
            "timestamp": datetime.now().isoformat(),
            "pushName": "Maria Santos"
        }
    ]
    
    # Processar
    try:
        response, metadata = await agent.process_buffered_messages(
            messages=messages,
            phone_number=phone,
            consolidated_content="Boa tarde Segue minha conta de luz Consegue fazer a simulação?",
            media_items=[{
                "type": "image",
                "content": "",
                "media_data": messages[2]["media_data"],
                "message_id": "media_3"
            }]
        )
        
        print(f"\n{Fore.GREEN}✓ Resposta do agente:{Style.RESET_ALL}")
        print(f'"{response}"')
        
        print(f"\n{Fore.MAGENTA}Mídia detectada: {metadata.get('media_count', 0)} arquivo(s){Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}✗ Erro ao processar com mídia: {e}{Style.RESET_ALL}")


async def test_performance_metrics():
    """Testa métricas de performance do buffer"""
    
    print(f"\n{Fore.CYAN}━━━ Teste de Performance ━━━{Style.RESET_ALL}")
    
    config = Config()
    agent = SDRAgentV2(config)
    await agent.initialize()
    
    # Diferentes tamanhos de buffer
    test_cases = [
        ("Pequeno", 3),
        ("Médio", 7),
        ("Grande", 15)
    ]
    
    for case_name, message_count in test_cases:
        print(f"\n{Fore.YELLOW}📊 Buffer {case_name}: {message_count} mensagens{Style.RESET_ALL}")
        
        phone = f"5511999{message_count:03d}000"
        messages = []
        
        # Criar mensagens
        for i in range(message_count):
            messages.append({
                "id": f"perf_{i}",
                "content": f"Mensagem de teste número {i+1}",
                "type": "text",
                "timestamp": datetime.now().isoformat(),
                "pushName": "Teste Performance"
            })
        
        # Medir tempo
        start_time = datetime.now()
        
        try:
            response, metadata = await agent.process_buffered_messages(
                messages=messages,
                phone_number=phone,
                consolidated_content=" ".join([m["content"] for m in messages]),
                media_items=[]
            )
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            print(f"{Fore.GREEN}✓ Processado em {total_time:.2f}s{Style.RESET_ALL}")
            print(f"  - Tempo médio por mensagem: {total_time/message_count:.3f}s")
            print(f"  - Dentro do limite de 30s: {'✓' if total_time < 30 else '✗'}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Erro no teste de performance: {e}{Style.RESET_ALL}")


async def run_integration_tests():
    """Executa todos os testes de integração"""
    
    # Teste principal de integração
    await test_agent_buffer_integration()
    
    # Teste com mídia
    await test_media_buffer()
    
    # Teste de performance
    await test_performance_metrics()
    
    print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ TESTES DE INTEGRAÇÃO CONCLUÍDOS!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())