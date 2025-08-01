"""
Exemplo de uso das WhatsApp Tools com AGnO Framework
"""

import asyncio
from agente.tools.whatsapp import (
    SendTextMessageTool,
    SendAudioMessageTool,
    SendImageMessageTool,
    SendDocumentMessageTool,
    SendLocationMessageTool,
    TypeSimulationTool,
    MessageChunkingTool,
    MessageBufferTool,
    ClearBufferTool,
    GetBufferStatusTool
)


async def example_usage():
    """Demonstra o uso de cada WhatsApp Tool"""
    
    phone = "5511999999999"  # Número de exemplo
    
    # 1. Enviar mensagem de texto simples
    print("\n=== 1. Enviando mensagem de texto ===")
    result = await SendTextMessageTool(
        phone=phone,
        text="Olá! Esta é uma mensagem de teste do SDR IA SolarPrime."
    )
    print(f"Resultado: {result}")
    
    
    # 2. Simular digitação antes de enviar
    print("\n=== 2. Simulando digitação ===")
    result = await TypeSimulationTool(
        phone=phone,
        text="Estou digitando esta mensagem... pode levar alguns segundos!",
        send_after=True
    )
    print(f"Duração da digitação: {result['typing_duration']}s")
    
    
    # 3. Enviar imagem com legenda
    print("\n=== 3. Enviando imagem ===")
    result = await SendImageMessageTool(
        phone=phone,
        image_url="https://example.com/solar-panel.jpg",
        caption="Confira nossos painéis solares de última geração!"
    )
    print(f"Imagem enviada: {result['success']}")
    
    
    # 4. Enviar documento PDF
    print("\n=== 4. Enviando documento ===")
    result = await SendDocumentMessageTool(
        phone=phone,
        document_url="https://example.com/proposta-solar.pdf",
        caption="Segue sua proposta personalizada de energia solar",
        filename="Proposta_SolarPrime_2024.pdf"
    )
    print(f"Documento enviado: {result['success']}, tipo: {result['document_type']}")
    
    
    # 5. Enviar áudio
    print("\n=== 5. Enviando áudio ===")
    result = await SendAudioMessageTool(
        phone=phone,
        audio_url="https://example.com/welcome-message.mp3",
        caption="Mensagem de boas-vindas da equipe SolarPrime"
    )
    print(f"Áudio enviado: {result['success']}")
    
    
    # 6. Enviar localização
    print("\n=== 6. Enviando localização ===")
    result = await SendLocationMessageTool(
        phone=phone,
        latitude=-8.1127,
        longitude=-34.8963,
        name="SolarPrime Boa Viagem",
        address="Av. Conselheiro Aguiar, 3456 - Boa Viagem, Recife - PE"
    )
    print(f"Localização enviada: {result['success']}")
    
    
    # 7. Dividir mensagem longa em chunks
    print("\n=== 7. Dividindo mensagem longa ===")
    long_text = """
    Olá! Sou Helen da SolarPrime, especialista em energia solar.
    
    Gostaria de compartilhar com você os benefícios da energia solar:
    
    1. Economia de até 95% na conta de luz
    2. Proteção contra aumentos tarifários
    3. Valorização do imóvel em até 10%
    4. Contribuição para o meio ambiente
    5. Retorno do investimento em 3-5 anos
    
    Além disso, oferecemos:
    - Projeto personalizado
    - Instalação profissional
    - Garantia de 25 anos nos painéis
    - Monitoramento em tempo real
    - Financiamento facilitado
    
    Gostaria de agendar uma visita técnica gratuita?
    """ * 3  # Triplicando para simular texto muito longo
    
    result = await MessageChunkingTool(
        text=long_text,
        max_chars=500,
        prefer_sentences=True
    )
    print(f"Texto dividido em {result['total_chunks']} chunks")
    print(f"Tamanho médio: {result['average_chunk_size']} caracteres")
    
    
    # 8. Usar buffer de mensagens
    print("\n=== 8. Usando buffer de mensagens ===")
    
    # Adicionar várias mensagens ao buffer
    await MessageBufferTool(
        phone=phone,
        message="Primeira informação sobre energia solar...",
        auto_send=True
    )
    
    await asyncio.sleep(1)  # Simula delay entre mensagens
    
    await MessageBufferTool(
        phone=phone,
        message="Segunda informação importante...",
        auto_send=True
    )
    
    await asyncio.sleep(1)
    
    await MessageBufferTool(
        phone=phone,
        message="Terceira e última informação!",
        force_send=True  # Força envio consolidado
    )
    
    # Verificar status do buffer
    status = await GetBufferStatusTool(phone=phone)
    print(f"Status do buffer: {status}")
    
    
    # 9. Exemplo de fluxo completo de conversa
    print("\n=== 9. Fluxo completo de conversa ===")
    
    # Simula digitação
    await TypeSimulationTool(
        phone=phone,
        text="Olá! Vi seu interesse em energia solar. Posso ajudar?",
        send_after=True
    )
    
    await asyncio.sleep(2)
    
    # Envia imagem ilustrativa
    await SendImageMessageTool(
        phone=phone,
        image_url="https://example.com/beneficios-solar.jpg",
        caption="Veja os principais benefícios da energia solar!"
    )
    
    await asyncio.sleep(1)
    
    # Envia documento
    await SendDocumentMessageTool(
        phone=phone,
        document_url="https://example.com/guia-solar.pdf",
        caption="Preparei este guia exclusivo para você",
        filename="Guia_Energia_Solar_2024.pdf"
    )
    
    # Limpa buffer ao final
    await ClearBufferTool(phone=phone)
    
    print("\nExemplo concluído!")


async def example_chunking_and_sending():
    """Exemplo avançado: divide mensagem longa e envia chunks com delays naturais"""
    
    phone = "5511999999999"
    
    # Mensagem longa para demonstração
    long_message = """
    Olá! Sou Helen Vieira, sua consultora de energia solar na SolarPrime.
    
    Percebi que você tem interesse em reduzir sua conta de energia e gostaria 
    de compartilhar algumas informações importantes sobre energia solar.
    
    A energia solar fotovoltaica é uma tecnologia limpa e renovável que 
    converte a luz do sol diretamente em eletricidade. Com os avanços 
    tecnológicos e a redução dos custos, tornou-se uma opção extremamente 
    viável para residências e empresas.
    
    Nossos clientes economizam em média 85% na conta de luz, com alguns 
    chegando a 95% de economia. O investimento se paga entre 3 a 5 anos, 
    e depois disso, você tem energia praticamente gratuita por mais de 
    20 anos!
    
    Gostaria de saber mais sobre como a energia solar pode beneficiar 
    especificamente o seu caso?
    """
    
    # Divide em chunks
    chunk_result = await MessageChunkingTool(
        text=long_message,
        max_chars=300,
        prefer_sentences=True,
        min_delay_ms=2000,
        max_delay_ms=4000
    )
    
    if chunk_result['success']:
        print(f"\nEnviando mensagem em {chunk_result['total_chunks']} partes:")
        
        for i, chunk in enumerate(chunk_result['chunks']):
            # Simula digitação para cada chunk
            await TypeSimulationTool(
                phone=phone,
                text=chunk['text'],
                send_after=True
            )
            
            print(f"  ✓ Parte {i+1}/{chunk_result['total_chunks']} enviada")
            
            # Aguarda o delay calculado para o próximo chunk
            if i < len(chunk_result['chunks']) - 1:
                delay_seconds = chunk['delay_ms'] / 1000
                print(f"    Aguardando {delay_seconds}s antes do próximo chunk...")
                await asyncio.sleep(delay_seconds)
    
    print("\nMensagem longa enviada com sucesso em chunks!")


if __name__ == "__main__":
    # Executa os exemplos
    asyncio.run(example_usage())
    
    # Descomente para executar o exemplo avançado
    # asyncio.run(example_chunking_and_sending())