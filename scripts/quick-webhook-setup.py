#!/usr/bin/env python3
"""
Script rápido para configurar webhook após correções
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

from services.evolution_api import evolution_client


async def quick_setup():
    """Configura webhook rapidamente com configurações padrão"""
    
    print("🚀 Configurando webhook Evolution API...")
    
    try:
        # Verificar conexão primeiro
        status = await evolution_client.check_connection()
        print(f"📱 Status da conexão: {status.get('state', 'unknown')}")
        
        if status.get("state") != "open":
            print("⚠️  WhatsApp não está conectado. Conecte primeiro!")
            return
        
        # Configurar webhook
        webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
        webhook_url = f"{webhook_url}/webhook/whatsapp"
        
        print(f"🔗 Configurando webhook para: {webhook_url}")
        
        # Eventos essenciais para SDR
        events = [
            "MESSAGES_UPSERT",      # Novas mensagens
            "MESSAGES_UPDATE",      # Status de mensagens
            "CONNECTION_UPDATE",    # Status da conexão
            "PRESENCE_UPDATE",      # Presença online/offline
            "SEND_MESSAGE",         # Confirmação de envio
            "QRCODE_UPDATED"        # QR Code atualizado
        ]
        
        result = await evolution_client.create_webhook(
            webhook_url=webhook_url,
            events=events,
            webhook_by_events=False,
            webhook_base64=False
        )
        
        print("✅ Webhook configurado com sucesso!")
        print(f"📊 Eventos configurados: {len(events)}")
        
        # Verificar configuração
        webhook_info = await evolution_client.get_webhook_info()
        if webhook_info and webhook_info.get("webhook", {}).get("enabled"):
            print("✅ Webhook está ativo e funcionando!")
        else:
            print("⚠️  Webhook configurado mas pode não estar ativo")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    print("\n📋 Próximos passos:")
    print("1. Teste enviando uma mensagem pelo WhatsApp")
    print("2. Verifique os logs: tail -f logs/app.log")
    print("3. Monitore métricas: curl http://localhost:8000/admin/webhook/metrics")


if __name__ == "__main__":
    asyncio.run(quick_setup())