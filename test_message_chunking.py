#!/usr/bin/env python3
"""
Test Message Chunking System
============================
Testa o sistema de divisão de mensagens em chunks
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Inicializar colorama
init()

from agents.tools.message_chunker_tool import (
    chunk_message_standalone, 
    split_into_sentences,
    convert_markdown_headers,
    calculate_typing_delay,
    calculate_reading_time,
    analyze_message_for_chunking
)


async def test_basic_chunking():
    """Testa divisão básica de mensagens"""
    print(f"\n{Fore.CYAN}=== TESTE DE CHUNKING BÁSICO ==={Style.RESET_ALL}\n")
    
    test_messages = [
        # Saudação inicial típica
        "Opa, tudo joia por aí? Que bom que você chamou! Aqui é a Helen Vieira, consultora especialista da Solar Prime Boa Viagem. Pra gente começar com o pé direito, como eu posso te chamar?",
        
        # Explicação técnica
        "Olha, deixa eu te explicar rapidinho como funciona. A gente instala uma usina de energia solar em fazendas aqui pertinho, em Gravatá. Você continua recebendo energia normalmente pela rede elétrica, mas com um desconto garantido de 20% na sua conta todo mês. É tipo um cashback permanente na conta de luz!",
        
        # Lista de benefícios
        "Os benefícios são sensacionais: 1. Economia garantida de 20% todo mês. 2. Sem investimento inicial. 3. Sem obras na sua casa. 4. Energia 100% limpa e renovável. 5. Contrato flexível sem multas.",
        
        # Mensagem com valores
        "Com uma conta de R$ 5.000, você economizaria R$ 1.000 todo mês! Em um ano, são R$ 12.000 de economia. É dinheiro que fica no seu bolso pra investir no que realmente importa pro seu negócio."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"{Fore.YELLOW}Teste {i}: {message[:50]}...{Style.RESET_ALL}")
        
        result = await chunk_message_standalone(
            message=message,
            join_probability=0.6
        )
        
        chunks = result["chunks"]
        delays = result["delays"]
        
        print(f"  Chunks: {len(chunks)}")
        for j, (chunk, delay) in enumerate(zip(chunks, delays), 1):
            print(f"  {Fore.GREEN}Chunk {j} ({delay}ms): {chunk}{Style.RESET_ALL}")
        
        print(f"  Tempo total de leitura: {result['total_reading_time']/1000:.1f}s\n")


async def test_special_cases():
    """Testa casos especiais de splitting"""
    print(f"\n{Fore.CYAN}=== TESTE DE CASOS ESPECIAIS ==={Style.RESET_ALL}\n")
    
    # Teste com URLs
    print(f"{Fore.YELLOW}1. Teste com URL:{Style.RESET_ALL}")
    message_url = "Acesse nosso site https://solarprime.com.br/economia para mais informações. Lá você encontra nossa calculadora de economia."
    
    sentences = split_into_sentences(message_url)
    print(f"  Sentenças: {sentences}")
    print(f"  {Fore.GREEN}✓ URL preservada{Style.RESET_ALL}" if "https://solarprime.com.br/economia" in sentences[0] else f"  {Fore.RED}✗ URL quebrada{Style.RESET_ALL}")
    
    # Teste com abreviações
    print(f"\n{Fore.YELLOW}2. Teste com abreviações:{Style.RESET_ALL}")
    message_abbr = "A Dra. Silva e o Sr. João confirmaram. A empresa Solar Prime Ltda. atende das 8h às 18h."
    
    sentences = split_into_sentences(message_abbr)
    print(f"  Sentenças: {len(sentences)}")
    for s in sentences:
        print(f"  - {s}")
    
    # Teste com emojis
    print(f"\n{Fore.YELLOW}3. Teste com emojis:{Style.RESET_ALL}")
    message_emoji = "Que maravilha! 🎉 Você vai adorar economizar todo mês. É sério! 😊 Vamos agendar?"
    
    sentences = split_into_sentences(message_emoji)
    print(f"  Sentenças: {len(sentences)}")
    for s in sentences:
        print(f"  - {s}")
    
    # Teste com lista numerada
    print(f"\n{Fore.YELLOW}4. Teste com lista numerada:{Style.RESET_ALL}")
    message_list = "Veja os passos: 1. Análise da sua conta. 2. Proposta personalizada. 3. Assinatura digital. 4. Economia imediata!"
    
    result = await chunk_message_standalone(
        message=message_list,
        join_probability=0.3  # Menor probabilidade para manter items separados
    )
    
    print(f"  Chunks: {len(result['chunks'])}")
    for chunk in result['chunks']:
        print(f"  - {chunk}")


async def test_markdown_conversion():
    """Testa conversão de markdown"""
    print(f"\n{Fore.CYAN}=== TESTE DE CONVERSÃO MARKDOWN ==={Style.RESET_ALL}\n")
    
    messages = [
        "# Proposta Solar Prime\nEconomize 20% todo mês!",
        "## Benefícios\n- Sem investimento\n- Sem obras",
        "### Importante\nContrato sem multas!"
    ]
    
    for msg in messages:
        converted = convert_markdown_headers(msg)
        print(f"Original:   {repr(msg)}")
        print(f"Convertido: {repr(converted)}")
        print()


async def test_delay_calculation():
    """Testa cálculo de delays"""
    print(f"\n{Fore.CYAN}=== TESTE DE CÁLCULO DE DELAYS ==={Style.RESET_ALL}\n")
    
    test_texts = [
        ("Oi!", 3),
        ("Como vai você?", 10),
        ("Esta é uma mensagem um pouco mais longa para testar o cálculo.", 30),
        ("Você sabia que pode economizar até 20% na conta de luz?", 25)
    ]
    
    for text, word_count in test_texts:
        typing_delay = calculate_typing_delay(text)
        reading_time = calculate_reading_time(text)
        
        print(f"Texto: '{text}'")
        print(f"  Palavras: {word_count}")
        print(f"  Delay digitação: {typing_delay}ms ({typing_delay/1000:.1f}s)")
        print(f"  Tempo leitura: {reading_time}ms ({reading_time/1000:.1f}s)")
        print()


async def test_stage_based_chunking():
    """Testa chunking baseado em estágio da conversa"""
    print(f"\n{Fore.CYAN}=== TESTE DE CHUNKING POR ESTÁGIO ==={Style.RESET_ALL}\n")
    
    stages = {
        "INITIAL_CONTACT": {
            "message": "Opa, tudo joia? Aqui é a Helen da Solar Prime! Como posso te chamar?",
            "context": {"stage": "INITIAL_CONTACT"}
        },
        "QUALIFICATION": {
            "message": "Perfeito! Deixa eu te explicar: nossa solução garante 20% de desconto na conta de luz, sem você precisar investir nada ou fazer obras. A economia começa no primeiro mês!",
            "context": {"stage": "QUALIFICATION"}
        },
        "TECHNICAL_INFO": {
            "message": "Com uma conta de R$ 3.000, você economiza R$ 600 por mês. São R$ 7.200 por ano! O investimento se paga em menos de 18 meses.",
            "context": {"stage": "DISCOVERY"}
        }
    }
    
    for stage_name, data in stages.items():
        print(f"{Fore.YELLOW}Estágio: {stage_name}{Style.RESET_ALL}")
        
        # Analisar estratégia de chunking
        analysis = await analyze_message_for_chunking(
            agent=None,
            message=data["message"],
            context=data["context"]
        )
        
        print(f"  Deve dividir: {analysis['should_chunk']}")
        print(f"  Probabilidade junção: {analysis['join_probability']}")
        print(f"  Máx palavras/chunk: {analysis['max_chunk_words']}")
        print(f"  Razão: {analysis['reasoning']}")
        print()


async def test_real_scenario():
    """Testa cenário real de conversa"""
    print(f"\n{Fore.CYAN}=== TESTE DE CENÁRIO REAL ==={Style.RESET_ALL}\n")
    
    # Simular uma resposta completa que seria dividida
    full_response = """Que ótimo, Maria! Fico super feliz com seu interesse.

Olha só, a Solar Prime é a maior empresa de energia solar compartilhada do Nordeste. Nós temos mais de 10 mil clientes satisfeitos economizando todo mês.

Nossa solução é perfeita pra quem quer economizar mas não pode ou não quer instalar painéis solares. Funciona assim: nós temos grandes usinas solares em Gravatá, pertinho daqui. A energia que produzimos lá é injetada na rede da Neoenergia.

Você continua recebendo energia normalmente, mas com um desconto garantido de 20% aplicado direto na sua conta todo mês. É como se fosse um cashback permanente!

O melhor de tudo: sem investimento, sem obras, sem dor de cabeça. Você só assina o contrato digitalmente e pronto, já começa a economizar.

Que tal a gente fazer uma simulação com o valor da sua conta pra você ver quanto vai economizar?"""
    
    # Dividir em chunks
    result = await chunk_message_standalone(
        message=full_response,
        join_probability=0.5,
        max_chunk_words=25
    )
    
    chunks = result["chunks"]
    delays = result["delays"]
    
    print(f"Resposta original: {len(full_response)} caracteres")
    print(f"Dividida em: {len(chunks)} chunks")
    print(f"Tempo total: {sum(delays)/1000:.1f}s\n")
    
    # Simular envio
    print(f"{Fore.GREEN}Simulação de envio:{Style.RESET_ALL}")
    total_time = 0
    
    for i, (chunk, delay) in enumerate(zip(chunks, delays), 1):
        if i > 1:
            print(f"{Fore.LIGHTBLACK_EX}  [digitando por {delay/1000:.1f}s...]{Style.RESET_ALL}")
            total_time += delay/1000
        
        print(f"{Fore.CYAN}  Helen ({datetime.now().strftime('%H:%M:%S')}): {chunk}{Style.RESET_ALL}")
        total_time += 0.5  # Tempo de envio
    
    print(f"\n{Fore.GREEN}Tempo total da conversa: {total_time:.1f}s{Style.RESET_ALL}")


async def main():
    """Executa todos os testes"""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🧪 TESTE DO SISTEMA DE MESSAGE CHUNKING{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    
    # Executar testes
    await test_basic_chunking()
    await test_special_cases()
    await test_markdown_conversion()
    await test_delay_calculation()
    await test_stage_based_chunking()
    await test_real_scenario()
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ TESTES CONCLUÍDOS!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    # Executar testes
    asyncio.run(main())