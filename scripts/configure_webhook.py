#!/usr/bin/env python3
"""
Configure Evolution API Webhook
===============================
Script para configurar webhook na Evolution API
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evolution_api import EvolutionAPIClient


async def configure_webhook():
    """Configura webhook na Evolution API"""
    
    load_dotenv()
    
    client = EvolutionAPIClient()
    webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
    webhook_endpoint = f"{webhook_url}/webhook/whatsapp"
    
    print("🔗 Configurando Webhook Evolution API")
    print("=" * 50)
    print(f"Instance: {client.instance_name}")
    print(f"Webhook URL: {webhook_endpoint}")
    print("")
    
    try:
        async with client:
            # 1. Verificar webhook atual
            print("1️⃣ Verificando configuração atual...")
            
            current_webhook = await client.get_webhook_info()
            
            if current_webhook:
                print("📋 Webhook atual:")
                print(json.dumps(current_webhook, indent=2))
                
                if current_webhook.get("url") == webhook_endpoint:
                    print("\n✅ Webhook já está configurado corretamente!")
                    return True
                else:
                    print("\n⚠️ Webhook configurado com URL diferente")
            else:
                print("❌ Nenhum webhook configurado")
            
            # 2. Configurar novo webhook
            print("\n2️⃣ Configurando novo webhook...")
            
            events = [
                "MESSAGES_UPSERT",      # Novas mensagens
                "MESSAGES_UPDATE",      # Status de mensagens  
                "CONNECTION_UPDATE",    # Status da conexão
                "PRESENCE_UPDATE",      # Presença online/offline
                "QRCODE_UPDATED"        # QR Code atualizado
            ]
            
            result = await client.create_webhook(
                webhook_url=webhook_endpoint,
                events=events,
                webhook_by_events=False,
                webhook_base64=False
            )
            
            if result:
                print("✅ Webhook configurado com sucesso!")
                print("\n📋 Configuração:")
                print(f"   URL: {webhook_endpoint}")
                print(f"   Eventos: {', '.join(events)}")
                
                # 3. Verificar novamente
                print("\n3️⃣ Verificando configuração...")
                
                new_webhook = await client.get_webhook_info()
                if new_webhook:
                    print("✅ Webhook verificado e ativo!")
                    
                    # 4. Testar webhook (opcional)
                    print("\n4️⃣ Deseja testar o webhook? (s/n)")
                    if input().lower() == 's':
                        print("\nEnviando mensagem de teste...")
                        print("⚠️ Para testar completamente:")
                        print("1. Certifique-se que sua aplicação está rodando em", webhook_url)
                        print("2. Envie uma mensagem para o WhatsApp conectado")
                        print("3. Verifique os logs da aplicação")
                
                return True
            else:
                print("❌ Falha ao configurar webhook")
                return False
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(configure_webhook())
    sys.exit(0 if success else 1)