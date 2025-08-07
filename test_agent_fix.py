#!/usr/bin/env python3
"""
Script de teste para validar as correções do travamento do agente

Este script simula múltiplas mensagens sequenciais para verificar se o problema
de travamento foi resolvido.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# URL do webhook local
WEBHOOK_URL = "http://localhost:8002/webhook/whatsapp/messages-upsert"

# Mensagens de teste
TEST_MESSAGES = [
    {
        "content": "Oi, gostaria de saber sobre energia solar",
        "phone": "5511999999901",
        "delay": 2
    },
    {
        "content": "Quanto custa?",
        "phone": "5511999999901",
        "delay": 3
    },
    {
        "content": "Minha conta vem uns 300 reais",
        "phone": "5511999999901",
        "delay": 2
    },
    {
        "content": "Como funciona a instalação?",
        "phone": "5511999999902",  # Diferente número para testar concorrência
        "delay": 1
    }
]

def create_webhook_payload(phone: str, message: str, message_id: str):
    """Cria payload simulando mensagem do WhatsApp"""
    return {
        "data": {
            "key": {
                "remoteJid": f"{phone}@s.whatsapp.net",
                "fromMe": False,
                "id": message_id
            },
            "message": {
                "conversation": message
            },
            "messageTimestamp": str(int(time.time())),
            "pushName": "Teste User"
        }
    }

async def send_message(session: aiohttp.ClientSession, phone: str, message: str, index: int):
    """Envia uma mensagem para o webhook"""
    message_id = f"TEST_{int(time.time())}_{index}"
    payload = create_webhook_payload(phone, message, message_id)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📤 Enviando mensagem {index + 1}:")
    print(f"   Phone: {phone}")
    print(f"   Message: {message}")
    print(f"   ID: {message_id}")
    
    try:
        start_time = time.time()
        async with session.post(WEBHOOK_URL, json=payload) as response:
            elapsed = time.time() - start_time
            
            if response.status == 200:
                print(f"   ✅ Resposta recebida em {elapsed:.2f}s")
                result = await response.json()
                print(f"   📥 Resultado: {result}")
            else:
                print(f"   ❌ Erro: Status {response.status}")
                text = await response.text()
                print(f"   📥 Resposta: {text}")
                
    except asyncio.TimeoutError:
        print(f"   ⏰ TIMEOUT após 30 segundos!")
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

async def test_sequential_messages():
    """Testa envio sequencial de mensagens"""
    print("🧪 TESTE 1: Mensagens Sequenciais")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for i, msg_data in enumerate(TEST_MESSAGES):
            await send_message(
                session,
                msg_data["phone"],
                msg_data["content"],
                i
            )
            
            if i < len(TEST_MESSAGES) - 1:
                print(f"\n⏳ Aguardando {msg_data['delay']}s antes da próxima mensagem...")
                await asyncio.sleep(msg_data["delay"])

async def test_concurrent_messages():
    """Testa envio concorrente de mensagens"""
    print("\n\n🧪 TESTE 2: Mensagens Concorrentes")
    print("=" * 50)
    print("Enviando 3 mensagens simultaneamente...")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(3):
            phone = f"551199999990{i+3}"
            message = f"Teste concorrente {i+1} - Quero saber sobre energia solar"
            task = send_message(session, phone, message, i + 100)
            tasks.append(task)
        
        # Envia todas ao mesmo tempo
        await asyncio.gather(*tasks)

async def test_timeout_recovery():
    """Testa recuperação após timeout"""
    print("\n\n🧪 TESTE 3: Recuperação após Timeout")
    print("=" * 50)
    
    # Mensagem muito longa que pode causar timeout
    long_message = """
    Olá! Eu tenho várias perguntas sobre energia solar:
    1. Como funciona exatamente o sistema?
    2. Qual o custo de instalação?
    3. Quanto tempo demora para instalar?
    4. Preciso de autorização da prefeitura?
    5. E se chover muito, ainda funciona?
    6. Qual a garantia dos equipamentos?
    7. Vocês fazem manutenção?
    8. Posso vender energia de volta para a concessionária?
    9. Qual economia real vou ter?
    10. Vocês têm financiamento?
    """ * 5  # Multiplica para tornar ainda maior
    
    async with aiohttp.ClientSession() as session:
        await send_message(session, "5511999999999", long_message, 200)
        
        # Testa se o sistema se recupera após um possível timeout
        print("\n⏳ Aguardando 5s para testar recuperação...")
        await asyncio.sleep(5)
        
        # Envia mensagem simples para verificar se ainda funciona
        await send_message(session, "5511999999999", "Oi", 201)

async def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO AGENTE CORRIGIDO")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print("\n" + "=" * 60 + "\n")
    
    # Verifica se o servidor está rodando
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8002/health") as response:
                if response.status == 200:
                    print("✅ Servidor está rodando!")
                else:
                    print("❌ Servidor não está respondendo corretamente")
                    return
    except Exception as e:
        print(f"❌ Erro ao conectar no servidor: {e}")
        print("💡 Certifique-se de que o servidor está rodando na porta 8002")
        return
    
    # Executa os testes
    await test_sequential_messages()
    await test_concurrent_messages()
    await test_timeout_recovery()
    
    print("\n\n✅ TESTES CONCLUÍDOS!")
    print("=" * 60)
    print("\n📋 CHECKLIST DE VERIFICAÇÃO:")
    print("  [ ] Todas as mensagens foram processadas?")
    print("  [ ] Não houve travamentos após a primeira mensagem?")
    print("  [ ] Mensagens concorrentes foram processadas corretamente?")
    print("  [ ] Sistema se recuperou após timeout?")
    print("  [ ] Logs mostram criação de nova instância para cada requisição?")
    print("  [ ] Timeouts foram detectados e tratados adequadamente?")

if __name__ == "__main__":
    asyncio.run(main())