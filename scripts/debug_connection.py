#!/usr/bin/env python3
"""
Debug Evolution API Connection
==============================
Script para debugar resposta da API
"""

import asyncio
import os
import sys
import json
import httpx
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evolution_api import EvolutionAPIClient


async def debug_connection():
    """Debug detalhado da conexão"""
    
    load_dotenv()
    
    client = EvolutionAPIClient()
    
    print("🔍 Debug de Conexão Evolution API")
    print("=" * 50)
    print(f"URL Base: {client.base_url}")
    print(f"Instance: {client.instance_name}")
    print("")
    
    async with httpx.AsyncClient() as http_client:
        # 1. Testar endpoint de status
        print("1️⃣ Testando endpoint connectionState...")
        url = f"{client.base_url}/instance/connectionState/{client.instance_name}"
        print(f"   URL: {url}")
        
        try:
            response = await http_client.get(
                url,
                headers={
                    "apikey": client.api_key,
                    "Content-Type": "application/json"
                }
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Response:")
            print(json.dumps(response.json(), indent=2))
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print("")
        
        # 2. Testar através do client
        print("2️⃣ Testando através do EvolutionAPIClient...")
        
        try:
            async with client:
                result = await client.check_connection()
                print(f"   Resultado:")
                print(json.dumps(result, indent=2))
                
                # Mapear estado
                state = result.get("state", "unknown")
                if state == "open":
                    print("\n   ✅ WhatsApp está conectado!")
                else:
                    print(f"\n   ⚠️ WhatsApp estado: {state}")
                    
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print("")
        
        # 3. Testar outros endpoints
        print("3️⃣ Testando outros endpoints...")
        
        # fetchInstances
        print("\n   a) fetchInstances...")
        try:
            response = await http_client.get(
                f"{client.base_url}/instance/fetchInstances",
                headers={
                    "apikey": client.api_key,
                    "Content-Type": "application/json"
                }
            )
            
            instances = response.json()
            if isinstance(instances, list) and len(instances) > 0:
                instance = instances[0]
                print(f"      Status de conexão: {instance.get('connectionStatus', 'N/A')}")
                print(f"      Owner JID: {instance.get('ownerJid', 'N/A')}")
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")


if __name__ == "__main__":
    asyncio.run(debug_connection())