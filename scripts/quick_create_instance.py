#!/usr/bin/env python3
"""
Script rápido para criar instância na Evolution API
"""

import httpx
import asyncio
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def create_instance():
    """Cria instância na Evolution API"""
    
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "Teste-Agente")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Criando instância '{instance_name}'...")
    print(f"URL: {base_url}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Verificar se já existe
            response = await client.get(
                f"{base_url}/instance/fetchInstances",
                headers=headers
            )
            
            if response.status_code == 200:
                instances = response.json()
                for inst in instances:
                    if inst.get("instance", {}).get("instanceName") == instance_name:
                        print(f"✅ Instância '{instance_name}' já existe!")
                        return True
            
            # Criar nova instância
            print(f"📱 Criando nova instância...")
            
            payload = {
                "instanceName": instance_name,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS"
            }
            
            response = await client.post(
                f"{base_url}/instance/create",
                headers=headers,
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ Instância criada com sucesso!")
                
                # Obter informações da instância
                instance_data = result.get("instance", {})
                
                # Configurar webhook
                webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
                webhook_payload = {
                    "url": f"{webhook_url}/webhook/whatsapp",
                    "enabled": True,
                    "events": [
                        "MESSAGES_UPSERT",
                        "MESSAGES_UPDATE", 
                        "CONNECTION_UPDATE",
                        "PRESENCE_UPDATE",
                        "SEND_MESSAGE",
                        "QRCODE_UPDATED"
                    ]
                }
                
                print("\n⚙️ Configurando webhook...")
                webhook_response = await client.post(
                    f"{base_url}/webhook/set/{instance_name}",
                    headers=headers,
                    json=webhook_payload
                )
                
                if webhook_response.status_code in [200, 201]:
                    print("✅ Webhook configurado!")
                else:
                    print(f"⚠️ Erro ao configurar webhook: {webhook_response.status_code}")
                
                # Mostrar QR Code
                qr_code = result.get("qrcode", {})
                if qr_code:
                    print("\n📱 QR CODE DISPONÍVEL!")
                    print("=" * 50)
                    print("Opções para conectar:")
                    print(f"1. Acesse: {base_url}/instance/qrcode/{instance_name}")
                    print("2. Ou use o código base64 abaixo:")
                    
                    base64_code = qr_code.get("base64", "")
                    if base64_code:
                        print(f"\n{base64_code[:100]}...")
                        print("\n(código completo muito longo para exibir)")
                    
                    pairingCode = qr_code.get("pairingCode")
                    if pairingCode:
                        print(f"\n3. Ou use o código de pareamento: {pairingCode}")
                    
                    print("\n📲 No WhatsApp:")
                    print("   1. Abra o WhatsApp")
                    print("   2. Vá em Configurações > Dispositivos conectados")
                    print("   3. Toque em 'Conectar dispositivo'")
                    print("   4. Escaneie o QR Code")
                    print("=" * 50)
                
                return True
                
            else:
                print(f"❌ Erro ao criar instância: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


if __name__ == "__main__":
    asyncio.run(create_instance())