#!/usr/bin/env python3
"""
Verifica instâncias disponíveis na Evolution API
"""

import httpx
import os
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

async def check_instances():
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/instance/fetchInstances", headers=headers)
            
            if response.status_code == 200:
                instances = response.json()
                
                print("🔍 Instâncias na Evolution API:")
                print("=" * 50)
                
                if not instances:
                    print("❌ Nenhuma instância encontrada!")
                    print("\n💡 Você precisa criar uma instância primeiro.")
                    print("   Use: python scripts/create_instance.py")
                else:
                    for idx, inst in enumerate(instances, 1):
                        instance_data = inst.get("instance", {})
                        name = instance_data.get("instanceName", "Unknown")
                        status = instance_data.get("status", "unknown")
                        
                        print(f"\n{idx}. Nome: {name}")
                        print(f"   Status: {status}")
                        print(f"   ID: {instance_data.get('instanceId', 'N/A')}")
                        
                        if status == "open":
                            print("   ✅ WhatsApp Conectado")
                        else:
                            print("   ⚠️ WhatsApp Desconectado")
                
                print("\n" + "=" * 50)
                print("📝 Para usar uma instância existente:")
                print("   Atualize EVOLUTION_INSTANCE_NAME no .env")
                print("\n📱 Para criar nova instância:")
                print("   python scripts/create_instance.py")
                
                return instances
            else:
                print(f"❌ Erro: {response.status_code}")
                print(response.text)
                return []
                
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(check_instances())