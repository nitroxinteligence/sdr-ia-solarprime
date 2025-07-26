#!/usr/bin/env python3
"""
Create Evolution API Instance
=============================
Script para criar instância na Evolution API
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evolution_api import EvolutionAPIClient


async def create_instance():
    """Cria instância na Evolution API"""
    
    load_dotenv()
    
    client = EvolutionAPIClient()
    
    print("🚀 Criando instância na Evolution API...")
    print(f"Nome da instância: {client.instance_name}")
    print(f"URL da API: {client.base_url}")
    print("")
    
    try:
        async with client:
            # Verificar se já existe
            print("1️⃣ Verificando se instância já existe...")
            try:
                info = await client.get_instance_info()
                if info:
                    print("✅ Instância já existe!")
                    print(f"   Nome: {info.get('instance', {}).get('instanceName', 'N/A')}")
                    
                    # Verificar conexão
                    connection = await client.check_connection()
                    state = connection.get("state", "unknown")
                    
                    if state == "open":
                        print("✅ WhatsApp já está conectado!")
                        return True
                    else:
                        print(f"⚠️ WhatsApp desconectado (estado: {state})")
                        
                        # Obter QR Code
                        qr_data = await client.get_qrcode()
                        if qr_data and qr_data.get("qrcode"):
                            print("\n📱 QR Code disponível!")
                            print("   Acesse a URL abaixo para escanear:")
                            print(f"   {client.base_url}/instance/qrcode/{client.instance_name}")
                            
                            # Se tiver base64, mostrar preview
                            base64_data = qr_data.get("qrcode", {}).get("base64", "")
                            if base64_data:
                                print(f"\n   Preview: {base64_data[:50]}...")
                        
                        return True
                        
            except Exception as e:
                if "404" in str(e):
                    print("❌ Instância não existe, criando...")
                else:
                    raise
            
            # Criar instância
            print("\n2️⃣ Criando nova instância...")
            result = await client.create_instance()
            
            if result:
                print("✅ Instância criada com sucesso!")
                
                # Aguardar um pouco para a instância inicializar
                print("\n⏳ Aguardando inicialização...")
                await asyncio.sleep(3)
                
                # Obter QR Code
                print("\n3️⃣ Obtendo QR Code...")
                qr_data = await client.get_qrcode()
                
                if qr_data and qr_data.get("qrcode"):
                    print("✅ QR Code gerado!")
                    print("\n📱 INSTRUÇÕES PARA CONECTAR:")
                    print("─" * 50)
                    print("1. Abra o WhatsApp no seu celular")
                    print("2. Vá em Configurações > Dispositivos conectados")
                    print("3. Clique em 'Conectar dispositivo'")
                    print("4. Escaneie o QR Code na URL abaixo:")
                    print(f"\n   {client.base_url}/instance/qrcode/{client.instance_name}")
                    print("─" * 50)
                    
                    # Mostrar preview se disponível
                    base64_data = qr_data.get("qrcode", {}).get("base64", "")
                    if base64_data:
                        print(f"\n📄 Base64 Preview: {base64_data[:50]}...")
                    
                    # Configurar webhook
                    print("\n4️⃣ Configurando webhook...")
                    webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
                    webhook_endpoint = f"{webhook_url}/webhook/whatsapp"
                    
                    webhook_result = await client.create_webhook(
                        webhook_url=webhook_endpoint,
                        events=[
                            "MESSAGES_UPSERT",
                            "MESSAGES_UPDATE",
                            "CONNECTION_UPDATE",
                            "PRESENCE_UPDATE",
                            "QRCODE_UPDATED"
                        ]
                    )
                    
                    if webhook_result:
                        print("✅ Webhook configurado!")
                        print(f"   URL: {webhook_endpoint}")
                    else:
                        print("⚠️ Falha ao configurar webhook")
                    
                    print("\n✅ Tudo pronto! Escaneie o QR Code para conectar.")
                    return True
                    
                else:
                    print("❌ Erro ao obter QR Code")
                    return False
            else:
                print("❌ Falha ao criar instância")
                return False
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(create_instance())
    sys.exit(0 if success else 1)