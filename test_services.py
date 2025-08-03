#!/usr/bin/env python3
"""
Script de teste para os serviços Message Buffer e Message Splitter
"""
import asyncio
from app.services.message_buffer import MessageBuffer
from app.services.message_splitter import MessageSplitter
from app.config import settings

async def test_message_splitter():
    """Testa o Message Splitter"""
    print("\n=== TESTANDO MESSAGE SPLITTER ===")
    
    # Cria instância do splitter
    splitter = MessageSplitter(max_length=150, add_indicators=False)
    
    # Testa com mensagens de diferentes tamanhos
    test_messages = [
        # Mensagem curta (não deve quebrar)
        "Olá! Como posso ajudá-lo hoje?",
        
        # Mensagem média (não deve quebrar)
        "Perfeito! Vi que você tem interesse em economizar na conta de luz. Nossa solução oferece 20% de desconto garantido.",
        
        # Mensagem longa (deve quebrar em frases naturais)
        "Excelente escolha! Nossa solução de energia solar traz economia imediata na sua conta de luz. "
        "Você pode economizar até 30% todos os meses. "
        "Além disso, oferecemos instalação profissional e garantia de 25 anos nos painéis. "
        "Gostaria de agendar uma visita técnica gratuita para avaliarmos seu imóvel?",
        
        # Mensagem muito longa
        "Olá! Seja muito bem-vindo à Solar Prime! Meu nome é Helen Vieira e sou consultora especialista aqui da Solar Prime em Recife. "
        "Estou aqui para te ajudar a economizar na conta de luz através de energia solar limpa e renovável. "
        "Nossa empresa é líder no mercado de energia solar, com mais de 10 anos de experiência e milhares de clientes satisfeitos. "
        "Oferecemos as melhores soluções em energia solar, com equipamentos de primeira linha e equipe técnica altamente qualificada. "
        "Além da economia, você estará contribuindo para um planeta mais sustentável. "
        "Posso te fazer algumas perguntas para entender melhor sua necessidade?"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n--- Teste {i} ---")
        print(f"Original ({len(msg)} chars): {msg[:100]}...")
        
        chunks = splitter.split_message(msg)
        
        print(f"Dividido em {len(chunks)} parte(s):")
        for j, chunk in enumerate(chunks, 1):
            print(f"  Parte {j} ({len(chunk)} chars): {chunk}")

async def test_message_buffer():
    """Testa o Message Buffer"""
    print("\n=== TESTANDO MESSAGE BUFFER ===")
    
    # Cria instância do buffer (sem Redis para teste simples)
    buffer = MessageBuffer(redis_client=None, timeout=2.0)  # 2 segundos para teste
    
    # Simula mensagens chegando
    phone = "5511999999999"
    
    # Callback para processar mensagens
    async def process_messages(messages):
        print(f"\n[CALLBACK] Processando {len(messages)} mensagem(s):")
        for msg in messages:
            print(f"  - {msg['content']}")
        combined = "\n".join([m['content'] for m in messages])
        print(f"[COMBINADO] ({len(combined)} chars): {combined}")
    
    print("\nSimulando mensagens chegando...")
    
    # Primeira mensagem
    await buffer.add_message(
        phone=phone,
        message="Olá, boa tarde!",
        message_data={"id": "msg1"},
        callback=process_messages
    )
    print("Mensagem 1 adicionada ao buffer")
    
    # Aguarda 0.5 segundos
    await asyncio.sleep(0.5)
    
    # Segunda mensagem (ainda dentro do timeout)
    await buffer.add_message(
        phone=phone,
        message="Gostaria de saber sobre energia solar",
        message_data={"id": "msg2"},
        callback=process_messages
    )
    print("Mensagem 2 adicionada ao buffer")
    
    # Aguarda 0.5 segundos
    await asyncio.sleep(0.5)
    
    # Terceira mensagem (ainda dentro do timeout)
    await buffer.add_message(
        phone=phone,
        message="Minha conta está muito alta",
        message_data={"id": "msg3"},
        callback=process_messages
    )
    print("Mensagem 3 adicionada ao buffer")
    
    # Aguarda o timeout para processar
    print("\nAguardando timeout de 2 segundos...")
    await asyncio.sleep(3)
    
    print("\n--- Teste com timeout mais longo ---")
    
    # Nova sequência com timeout reiniciado
    await buffer.add_message(
        phone=phone,
        message="Tenho outra dúvida",
        message_data={"id": "msg4"},
        callback=process_messages
    )
    print("Nova mensagem adicionada")
    
    # Aguarda processamento
    await asyncio.sleep(3)

async def test_integration():
    """Testa a integração dos dois serviços"""
    print("\n=== TESTANDO INTEGRAÇÃO ===")
    
    buffer = MessageBuffer(redis_client=None, timeout=2.0)
    splitter = MessageSplitter(max_length=150, add_indicators=False)
    
    phone = "5511888888888"
    
    # Callback que usa o splitter
    async def process_and_split(messages):
        combined = "\n".join([m['content'] for m in messages])
        print(f"\n[BUFFER] Recebeu {len(messages)} mensagem(s), total: {len(combined)} chars")
        
        # Simula resposta do agente
        response = (
            "Olá! Vi que você tem várias dúvidas sobre energia solar. "
            "Vou te explicar tudo! Nossa solução oferece economia de até 30% na conta de luz. "
            "A instalação é feita por profissionais certificados em apenas 2 dias. "
            "Os painéis têm garantia de 25 anos e começam a gerar economia desde o primeiro mês. "
            "Além disso, você contribui para um planeta mais sustentável. "
            "Gostaria de agendar uma visita técnica gratuita?"
        )
        
        print(f"\n[AGENTE] Resposta gerada: {len(response)} chars")
        
        # Divide a resposta se necessário
        chunks = splitter.split_message(response)
        print(f"\n[SPLITTER] Dividiu em {len(chunks)} parte(s):")
        for i, chunk in enumerate(chunks, 1):
            print(f"  Enviando parte {i}/{len(chunks)}: {chunk}")
            await asyncio.sleep(0.5)  # Simula delay entre chunks
    
    # Simula múltiplas mensagens chegando
    await buffer.add_message(phone, "Oi", {"id": "1"}, process_and_split)
    await asyncio.sleep(0.3)
    await buffer.add_message(phone, "Quero saber sobre energia solar", {"id": "2"}, process_and_split)
    await asyncio.sleep(0.3)
    await buffer.add_message(phone, "Quanto custa?", {"id": "3"}, process_and_split)
    await asyncio.sleep(0.3)
    await buffer.add_message(phone, "E a instalação?", {"id": "4"}, process_and_split)
    
    # Aguarda processamento
    await asyncio.sleep(4)

async def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE DOS SERVIÇOS MESSAGE BUFFER E MESSAGE SPLITTER")
    print("=" * 60)
    
    # Mostra configurações
    print("\nCONFIGURAÇÕES:")
    print(f"  Buffer habilitado: {settings.enable_message_buffer}")
    print(f"  Buffer timeout: {settings.message_buffer_timeout}s")
    print(f"  Splitter habilitado: {settings.enable_message_splitter}")
    print(f"  Tamanho máximo: {settings.message_max_length} chars")
    print(f"  Delay entre chunks: {settings.message_chunk_delay}s")
    
    # Executa testes
    await test_message_splitter()
    await test_message_buffer()
    await test_integration()
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())