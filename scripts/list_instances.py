#!/usr/bin/env python3
"""
List Evolution API Instances
============================
Script para listar instâncias na Evolution API
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evolution_api import EvolutionAPIClient


async def list_instances():
    """Lista todas as instâncias"""
    
    load_dotenv()
    
    client = EvolutionAPIClient()
    
    print("📋 Listando instâncias na Evolution API...")
    print(f"URL: {client.base_url}")
    print(f"API Key: {client.api_key[:10]}...{client.api_key[-10:]}")
    print("")
    
    try:
        async with client:
            # Tentar listar todas as instâncias
            print("Tentando endpoint: /instance/fetchInstances")
            
            response = await client.client.get(
                "/instance/fetchInstances",
                headers={
                    "apikey": client.api_key,
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                instances = response.json()
                
                print("\n📦 Resposta completa:")
                print(json.dumps(instances, indent=2, ensure_ascii=False))
                
                if isinstance(instances, list) and len(instances) > 0:
                    print(f"\n✅ Encontradas {len(instances)} instâncias:\n")
                    
                    for idx, instance in enumerate(instances):
                        if isinstance(instance, dict):
                            # Mostrar todas as chaves disponíveis
                            print(f"\n{idx + 1}. Instância:")
                            for key, value in instance.items():
                                print(f"   {key}: {value}")
                        else:
                            print(f"{idx + 1}. {instance}")
                elif isinstance(instances, dict):
                    # Pode ser um objeto único
                    print("\n📋 Dados da instância:")
                    for key, value in instances.items():
                        print(f"   {key}: {value}")
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                print(f"Resposta: {response.text}")
                
                # Tentar outro endpoint
                print("\n🔍 Tentando endpoint alternativo...")
                
                # Tentar verificar instância específica
                try:
                    connection = await client.check_connection()
                    print("\n✅ Consegui verificar conexão da instância atual!")
                    print(f"Estado: {connection.get('state', 'unknown')}")
                    
                    if connection.get('state') == 'open':
                        print("WhatsApp está conectado!")
                    else:
                        print("WhatsApp NÃO está conectado")
                        
                except Exception as e2:
                    print(f"❌ Erro ao verificar conexão: {e2}")
                    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        
        # Sugestões
        print("\n💡 Possíveis soluções:")
        print("1. Verifique se a API key está correta")
        print("2. Verifique se a URL da API está correta")
        print("3. A instância pode já estar criada e acessível")
        print("4. Tente acessar diretamente o painel da Evolution API")


if __name__ == "__main__":
    asyncio.run(list_instances())