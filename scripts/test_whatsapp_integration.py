#!/usr/bin/env python3
"""
Test WhatsApp Integration
=========================
Testa a integração completa com WhatsApp
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.evolution_api import evolution_client
from services.whatsapp_service import whatsapp_service
from dotenv import load_dotenv

load_dotenv()


async def test_evolution_connection():
    """Testa conexão com Evolution API"""
    
    print("1️⃣ Testando conexão com Evolution API...")
    
    try:
                    connected = await evolution_client.check_connection()
            
            if connected:
                print("✅ Evolution API conectada!")
            else:
                print("❌ Evolution API não está conectada")
                print("   Verifique se a Evolution API está rodando")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    return True


async def test_send_message():
    """Testa envio de mensagem"""
    
    print("\n2️⃣ Testando envio de mensagem...")
    
    # Número de teste
    test_number = input("Digite o número para teste (com DDD, sem +55): ")
    
    if not test_number:
        print("❌ Número não fornecido")
        return False
    
    try:
        result = await whatsapp_service.send_message(
            phone=test_number,
            message=(
                "🤖 *Teste de Integração - SDR SolarPrime*\n\n"
                "Olá! Esta é uma mensagem de teste do sistema.\n"
                f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                "_Esta mensagem foi enviada automaticamente._"
            )
        )
        
        if result["status"] == "success":
            print("✅ Mensagem enviada com sucesso!")
            print(f"   ID: {result.get('message_id')}")
        else:
            print("❌ Falha ao enviar mensagem")
            print(f"   Erro: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False
    
    return True


async def test_webhook_processing():
    """Testa processamento de webhook"""
    
    print("\n3️⃣ Testando processamento de webhook...")
    
    # Simular webhook de mensagem
    test_webhook = {
        "event": "MESSAGES_UPSERT",
        "instance": "test",
        "data": {
            "key": {
                "id": "TEST_MSG_123",
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False
            },
            "message": {
                "conversation": "Olá, quero saber sobre energia solar"
            },
            "messageTimestamp": int(datetime.now().timestamp()),
            "pushName": "Cliente Teste"
        }
    }
    
    try:
        result = await whatsapp_service.process_webhook(test_webhook)
        
        if result["status"] == "success":
            print("✅ Webhook processado com sucesso!")
            print(f"   Resultado: {result}")
        else:
            print("❌ Falha no processamento do webhook")
            print(f"   Resultado: {result}")
            
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        return False
    
    return True


async def test_multimodal():
    """Testa processamento multimodal"""
    
    print("\n4️⃣ Testando processamento multimodal...")
    
    # Simular webhook com imagem
    test_webhook = {
        "event": "MESSAGES_UPSERT",
        "instance": "test",
        "data": {
            "key": {
                "id": "TEST_IMG_123",
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False
            },
            "message": {
                "imageMessage": {
                    "caption": "Segue minha conta de luz",
                    "mimetype": "image/jpeg"
                }
            },
            "messageTimestamp": int(datetime.now().timestamp()),
            "pushName": "Cliente Teste"
        }
    }
    
    try:
        result = await whatsapp_service.process_webhook(test_webhook)
        print("✅ Processamento multimodal testado!")
        print(f"   Resultado: {result}")
        
    except Exception as e:
        print(f"❌ Erro no teste multimodal: {e}")
        return False
    
    return True


async def test_reasoning_metrics():
    """Testa métricas de reasoning"""
    
    print("\n5️⃣ Testando métricas de reasoning...")
    
    try:
        # Obter métricas para um número de teste
        metrics = await whatsapp_service.get_reasoning_metrics("5511999999999@s.whatsapp.net")
        
        print("✅ Métricas obtidas:")
        print(f"   Métricas: {metrics.get('metrics', {})}")
        print(f"   Qualidade: {metrics.get('quality', {})}")
        
    except Exception as e:
        print(f"❌ Erro ao obter métricas: {e}")
        return False
    
    return True


async def main():
    """Função principal"""
    
    print("🚀 SDR SolarPrime - Teste de Integração WhatsApp\n")
    print("Este script testa a integração completa com WhatsApp.\n")
    
    # Verificar configurações
    print("📋 Verificando configurações...")
    
    configs = {
        "EVOLUTION_API_URL": os.getenv("EVOLUTION_API_URL"),
        "EVOLUTION_API_KEY": os.getenv("EVOLUTION_API_KEY"),
        "EVOLUTION_INSTANCE_NAME": os.getenv("EVOLUTION_INSTANCE_NAME"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
    }
    
    missing = [k for k, v in configs.items() if not v]
    
    if missing:
        print("❌ Configurações faltando:")
        for config in missing:
            print(f"   - {config}")
        print("\nConfigure as variáveis no arquivo .env")
        return
    
    print("✅ Todas as configurações encontradas!\n")
    
    # Executar testes
    tests = [
        ("Conexão Evolution API", test_evolution_connection),
        ("Envio de Mensagem", test_send_message),
        ("Processamento de Webhook", test_webhook_processing),
        ("Processamento Multimodal", test_multimodal),
        ("Métricas de Reasoning", test_reasoning_metrics)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'='*50}")
        result = await test_func()
        results.append((name, result))
        
        if not result and name == "Conexão Evolution API":
            print("\n⚠️ Sem conexão com Evolution API, parando testes...")
            break
    
    # Resumo
    print(f"\n{'='*50}")
    print("📊 Resumo dos Testes:\n")
    
    for name, result in results:
        status = "✅ Passou" if result else "❌ Falhou"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! A integração está funcionando!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")


if __name__ == "__main__":
    asyncio.run(main())