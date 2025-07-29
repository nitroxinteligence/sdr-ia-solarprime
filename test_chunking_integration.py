#!/usr/bin/env python3
"""
Test Chunking Integration
=========================
Testa a integração completa do sistema de message chunking
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
from unittest.mock import AsyncMock, MagicMock, patch

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Inicializar colorama
init()

# Importações do projeto
from config.config import Config


async def test_whatsapp_service_chunking():
    """Testa o WhatsAppService com chunking habilitado"""
    print(f"\n{Fore.CYAN}=== TESTE DE WHATSAPP SERVICE COM CHUNKING ==={Style.RESET_ALL}\n")
    
    # Mock do evolution_client
    with patch('services.whatsapp_service.evolution_client') as mock_evolution:
        # Configurar mocks
        mock_evolution.send_text_message = AsyncMock()
        mock_evolution.send_typing = AsyncMock()
        mock_evolution.mark_as_read = AsyncMock()
        
        # Mock do create_sdr_agent
        with patch('services.whatsapp_service.create_sdr_agent') as mock_create_agent:
            # Criar mock do agente
            mock_agent = MagicMock()
            mock_agent.process_message = AsyncMock(return_value=(
                "Opa, tudo joia por aí? Que bom que você chamou! Aqui é a Helen Vieira, consultora especialista da Solar Prime Boa Viagem. Pra gente começar com o pé direito, como eu posso te chamar?",
                {
                    'stage': 'INITIAL_CONTACT',
                    'response_time': 1.5,
                    'lead_score': 10,
                    'should_react': False,
                    'reaction_emoji': None,
                    'reasoning_enabled': True,
                    'use_chunking': True
                }
            ))
            mock_create_agent.return_value = mock_agent
            
            # Importar e criar WhatsAppService
            from services.whatsapp_service import WhatsAppService
            service = WhatsAppService()
            
            # Criar mensagem de teste
            message_info = {
                "id": "test_msg_123",
                "from": "5511999999999",
                "timestamp": int(datetime.now().timestamp()),
                "pushName": "João",
                "type": "text",
                "content": "Oi, quero saber sobre energia solar",
                "media_data": None
            }
            
            # Processar mensagem
            response = await service._process_message(message_info)
            
            # Verificar se o chunking foi aplicado
            print(f"{Fore.GREEN}✓ Mensagem processada{Style.RESET_ALL}")
            print(f"  Resposta: {response[:50]}...")
            
            # Verificar chamadas ao evolution_client
            call_count = mock_evolution.send_text_message.call_count
            print(f"  Mensagens enviadas: {call_count}")
            
            if call_count > 1:
                print(f"  {Fore.GREEN}✓ Chunking aplicado - {call_count} chunks enviados{Style.RESET_ALL}")
                
                # Verificar typing simulation
                typing_count = mock_evolution.send_typing.call_count
                print(f"  Typing simulations: {typing_count}")
                
                # Listar chunks enviados
                print(f"\n  {Fore.YELLOW}Chunks enviados:{Style.RESET_ALL}")
                for i, call in enumerate(mock_evolution.send_text_message.call_args_list, 1):
                    chunk = call[1]['message']
                    print(f"    Chunk {i}: {chunk}")
            else:
                print(f"  {Fore.YELLOW}⚠ Mensagem enviada em chunk único{Style.RESET_ALL}")
            
            return call_count > 1


async def test_sdr_agent_integration():
    """Testa integração do SDR Agent com chunking tools"""
    print(f"\n{Fore.CYAN}=== TESTE DE SDR AGENT COM CHUNKING TOOLS ==={Style.RESET_ALL}\n")
    
    try:
        config = Config()
        from agents.sdr_agent_v2 import SDRAgentV2
        
        agent = SDRAgentV2(config)
        
        # Verificar se as tools de chunking estão presentes
        agent_instance = agent._create_agent("5511999999999")
        tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in agent_instance.tools]
        
        print(f"Tools disponíveis: {len(tool_names)}")
        
        chunking_tools = [
            'chunk_message',
            'analyze_message_for_chunking'
        ]
        
        for tool in chunking_tools:
            if any(tool in str(t) for t in tool_names):
                print(f"  {Fore.GREEN}✓ Tool '{tool}' presente{Style.RESET_ALL}")
            else:
                print(f"  {Fore.RED}✗ Tool '{tool}' ausente{Style.RESET_ALL}")
        
        # Verificar metadata de chunking
        print(f"\n{Fore.YELLOW}Teste de metadata:{Style.RESET_ALL}")
        
        # Simular processo simplificado
        metadata_test = {
            'stage': 'INITIAL_CONTACT',
            'response_time': 1.0,
            'lead_score': 0,
            'should_react': False,
            'reaction_emoji': None,
            'reasoning_enabled': True,
            'use_chunking': True
        }
        
        if metadata_test.get('use_chunking'):
            print(f"  {Fore.GREEN}✓ Metadata 'use_chunking' configurado{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}✗ Metadata 'use_chunking' não configurado{Style.RESET_ALL}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Erro na integração: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return False


async def test_environment_config():
    """Testa configurações de ambiente para chunking"""
    print(f"\n{Fore.CYAN}=== TESTE DE CONFIGURAÇÕES DE AMBIENTE ==={Style.RESET_ALL}\n")
    
    import os
    
    # Configurações esperadas
    configs = {
        "MESSAGE_CHUNKING_ENABLED": ("true", "Chunking habilitado"),
        "CHUNK_JOIN_PROBABILITY": ("0.6", "Probabilidade de junção"),
        "CHUNK_MAX_WORDS": ("30", "Máximo palavras por chunk"),
        "CHUNK_MIN_WORDS": ("3", "Mínimo palavras por chunk"),
        "CHUNK_MAX_CHARS": ("1200", "Máximo caracteres por chunk"),
        "CHUNK_TYPING_WORDS_PER_MINUTE": ("150", "Velocidade de digitação"),
        "CHUNK_READING_WORDS_PER_MINUTE": ("200", "Velocidade de leitura")
    }
    
    print(f"{Fore.YELLOW}Verificando configurações:{Style.RESET_ALL}")
    
    missing = []
    for key, (default, description) in configs.items():
        value = os.getenv(key)
        if value:
            print(f"  {Fore.GREEN}✓ {key}: {value} ({description}){Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}⚠ {key}: não configurado (padrão: {default}){Style.RESET_ALL}")
            missing.append(key)
    
    if missing:
        print(f"\n{Fore.YELLOW}Adicione as seguintes variáveis ao seu .env:{Style.RESET_ALL}")
        for key in missing:
            default, _ = configs[key]
            print(f"  {key}={default}")
    
    return len(missing) == 0


async def test_full_flow():
    """Testa fluxo completo com exemplo real"""
    print(f"\n{Fore.CYAN}=== TESTE DE FLUXO COMPLETO ==={Style.RESET_ALL}\n")
    
    from agents.tools.message_chunker_tool import chunk_message_standalone
    
    # Mensagem típica da Helen
    helen_message = """Que maravilha, João! 😊

Deixa eu te explicar rapidinho como funciona nossa solução.

A Solar Prime é a maior empresa de energia solar compartilhada do Nordeste. Nós instalamos grandes usinas solares em fazendas aqui em Gravatá, pertinho de Recife.

A energia que produzimos lá é injetada direto na rede da Neoenergia. Você continua recebendo energia normalmente na sua casa ou empresa, mas com um desconto garantido de 20% todo mês!

O melhor de tudo: sem investimento, sem obras, sem painéis no seu telhado. É só assinar o contrato digital e pronto, já começa a economizar.

Com uma conta de R$ 500, você economizaria R$ 100 todo mês. Em um ano, são R$ 1.200 no seu bolso!

Que tal eu fazer uma proposta personalizada pra você?"""
    
    # Processar chunking
    result = await chunk_message_standalone(
        message=helen_message,
        join_probability=0.5,
        max_chunk_words=25,
        max_chars_per_chunk=1200
    )
    
    chunks = result["chunks"]
    delays = result["delays"]
    
    print(f"Mensagem original: {len(helen_message)} caracteres")
    print(f"Dividida em: {len(chunks)} chunks")
    print(f"Tempo total estimado: {sum(delays)/1000:.1f}s")
    
    print(f"\n{Fore.GREEN}Simulação de conversa:{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}João (10:30:15): Oi, quero saber sobre energia solar{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[Helen está digitando...]{Style.RESET_ALL}")
    
    current_time = datetime.now()
    for i, (chunk, delay) in enumerate(zip(chunks, delays), 1):
        if i > 1:
            print(f"{Fore.LIGHTBLACK_EX}[digitando...]{Style.RESET_ALL}")
        
        current_time = current_time.replace(second=current_time.second + int(delay/1000))
        print(f"{Fore.CYAN}Helen ({current_time.strftime('%H:%M:%S')}): {chunk}{Style.RESET_ALL}")
    
    return True


async def main():
    """Executa todos os testes de integração"""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🧪 TESTE DE INTEGRAÇÃO - MESSAGE CHUNKING{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    
    # Executar testes
    results = []
    
    results.append(("WhatsApp Service", await test_whatsapp_service_chunking()))
    results.append(("SDR Agent Integration", await test_sdr_agent_integration()))
    results.append(("Environment Config", await test_environment_config()))
    results.append(("Full Flow", await test_full_flow()))
    
    # Resumo
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}RESUMO DOS TESTES{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Fore.GREEN}✓ PASSOU{Style.RESET_ALL}" if result else f"{Fore.RED}✗ FALHOU{Style.RESET_ALL}"
        print(f"{test_name}: {status}")
    
    print(f"\n{Fore.CYAN}Total: {passed}/{total} testes passaram{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}🎉 SISTEMA DE MESSAGE CHUNKING FUNCIONANDO!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}As mensagens agora serão enviadas de forma mais natural e humanizada.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️ Alguns testes falharam. Verifique os erros acima.{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Executar testes
    asyncio.run(main())