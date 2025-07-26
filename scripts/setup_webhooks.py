#!/usr/bin/env python3
"""
Setup Webhooks
==============
Configura webhooks na Evolution API
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.evolution_api import evolution_client

load_dotenv()


async def setup_webhooks():
    """Configura webhooks na Evolution API"""
    
    print("🔧 Configurando webhooks na Evolution API...")
    
    # Obter URL base da API
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    webhook_url = f"{api_base_url}/webhook/whatsapp"
    
    print(f"📍 URL do webhook: {webhook_url}")
    
    try:
                    # Verificar conexão primeiro
            if not await evolution_client.check_connection():
                print("❌ Evolution API não está conectada!")
                print("   Verifique se a Evolution API está rodando e configurada corretamente.")
                return
            
            print("✅ Evolution API conectada!")
            
            # Configurar webhook
            result = await evolution_client.create_webhook(
                webhook_url=webhook_url,
                events=[
                    "MESSAGES_UPSERT",      # Novas mensagens
                    "MESSAGES_UPDATE",      # Atualizações de status
                    "CONNECTION_UPDATE",    # Status da conexão
                    "GROUP_UPDATE",         # Atualizações de grupos
                    "GROUP_PARTICIPANTS_UPDATE"  # Participantes de grupos
                ]
            )
            
            print(f"✅ Webhook configurado com sucesso!")
            print(f"   Resposta: {result}")
            
            # Instruções finais
            print("\n📝 Próximos passos:")
            print("1. Certifique-se que a API está rodando:")
            print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
            print("\n2. Se estiver em produção, configure o webhook com HTTPS:")
            print(f"   API_BASE_URL=https://seudominio.com.br")
            print("\n3. Configure o WEBHOOK_SECRET para segurança:")
            print("   WEBHOOK_SECRET=seu_secret_aqui")
            
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
        print("\nVerifique:")
        print("- Se a Evolution API está rodando")
        print("- Se as variáveis de ambiente estão configuradas:")
        print("  - EVOLUTION_API_URL")
        print("  - EVOLUTION_API_KEY")
        print("  - EVOLUTION_INSTANCE_NAME")


async def test_webhook():
    """Testa o webhook configurado"""
    
    print("\n🧪 Testando webhook...")
    
    import httpx
    
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    test_url = f"{api_base_url}/webhook/test"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await evolution_client.post(test_url)
            
            if response.status_code == 200:
                print("✅ Teste do webhook bem-sucedido!")
                print(f"   Resposta: {response.json()}")
            else:
                print(f"❌ Falha no teste: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro ao testar webhook: {e}")
        print("   Certifique-se que a API está rodando!")


async def main():
    """Função principal"""
    
    print("🚀 SDR SolarPrime - Configuração de Webhooks\n")
    
    # Configurar webhooks
    await setup_webhooks()
    
    # Perguntar se quer testar
    print("\n")
    test = input("Deseja testar o webhook? (s/n): ").lower()
    
    if test == 's':
        await test_webhook()
    
    print("\n✅ Configuração concluída!")


if __name__ == "__main__":
    asyncio.run(main())