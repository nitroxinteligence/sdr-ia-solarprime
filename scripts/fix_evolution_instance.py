#!/usr/bin/env python3
"""
Script para corrigir problemas com instância Evolution API
"""

import httpx
import asyncio
import os
from dotenv import load_dotenv
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

load_dotenv()

console = Console()

async def main():
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "Teste-Agente")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"🔧 Corrigindo instância '{instance_name}'...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Primeiro, tentar obter status da instância
            print("\n1️⃣ Verificando status da instância...")
            try:
                response = await client.get(
                    f"{base_url}/instance/connectionState/{instance_name}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    state_data = response.json()
                    state = state_data.get("state", "unknown")
                    print(f"   Status atual: {state}")
                    
                    if state == "open":
                        print("   ✅ WhatsApp já está conectado!")
                        return True
                    elif state == "close":
                        print("   ⚠️ WhatsApp desconectado")
                else:
                    print(f"   Erro ao verificar status: {response.status_code}")
            except:
                print("   ❌ Não foi possível verificar status")
            
            # 2. Tentar conectar/reconectar
            print("\n2️⃣ Tentando conectar instância...")
            try:
                response = await client.get(
                    f"{base_url}/instance/connect/{instance_name}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("   ✅ Comando de conexão enviado")
                    
                    # Verificar se tem QR Code
                    qrcode = result.get("qrcode")
                    if qrcode:
                        pairingCode = qrcode.get("pairingCode")
                        base64 = qrcode.get("base64", "")
                        
                        print("\n📱 QR CODE DISPONÍVEL!")
                        print("=" * 60)
                        
                        if pairingCode:
                            print(f"🔢 CÓDIGO DE PAREAMENTO: {pairingCode}")
                            print("\nComo usar o código:")
                            print("1. No WhatsApp, vá em Configurações > Dispositivos conectados")
                            print("2. Toque em 'Conectar dispositivo'")
                            print("3. Escolha 'Conectar com número de telefone'")
                            print(f"4. Digite o código: {pairingCode}")
                        
                        print(f"\n🌐 Ou acesse para ver QR Code:")
                        print(f"   {base_url}/instance/qrcode/{instance_name}")
                        
                        if base64:
                            print(f"\n📄 Base64 (primeiros 100 chars):")
                            print(f"   {base64[:100]}...")
                        
                        print("=" * 60)
                    else:
                        print("   ⚠️ QR Code não disponível no momento")
                else:
                    print(f"   ❌ Erro ao conectar: {response.status_code}")
                    print(f"   Resposta: {response.text}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # 3. Verificar/configurar webhook
            print("\n3️⃣ Verificando webhook...")
            try:
                response = await client.get(
                    f"{base_url}/webhook/find/{instance_name}",
                    headers=headers
                )
                
                webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
                expected_url = f"{webhook_url}/webhook/whatsapp"
                
                if response.status_code == 200:
                    webhook_data = response.json()
                    current_url = webhook_data.get("url", "")
                    enabled = webhook_data.get("enabled", False)
                    
                    if current_url == expected_url and enabled:
                        print(f"   ✅ Webhook já configurado corretamente")
                        print(f"   URL: {current_url}")
                    else:
                        print(f"   ⚠️ Webhook precisa ser atualizado")
                        # Configurar webhook
                        webhook_payload = {
                            "url": expected_url,
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
                        
                        response = await client.post(
                            f"{base_url}/webhook/set/{instance_name}",
                            headers=headers,
                            json=webhook_payload
                        )
                        
                        if response.status_code in [200, 201]:
                            print(f"   ✅ Webhook atualizado!")
                            print(f"   URL: {expected_url}")
                        else:
                            print(f"   ❌ Erro ao atualizar webhook")
                else:
                    print(f"   ❌ Erro ao verificar webhook: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            print("\n✅ Processo concluído!")
            print("\n📋 Próximos passos:")
            print("1. Se apareceu código de pareamento, use-o no WhatsApp")
            print("2. Ou escaneie o QR Code na URL fornecida")
            print("3. Após conectar, teste enviando uma mensagem")
            print("4. Monitore os logs: tail -f app.log")
            
        except Exception as e:
            print(f"\n❌ Erro geral: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(main())