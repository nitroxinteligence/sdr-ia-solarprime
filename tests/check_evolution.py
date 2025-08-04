#!/usr/bin/env python3
"""
Script para verificar e diagnosticar conexão com Evolution API
"""
import asyncio
import httpx
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from loguru import logger

async def check_evolution():
    """Verifica conexão com Evolution API"""
    
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO DE CONEXÃO - EVOLUTION API")
    print("="*60 + "\n")
    
    # URLs possíveis para testar
    urls_to_test = [
        settings.evolution_api_url,
        "http://localhost:8080",
        "http://evolution-api:8080",
        "http://127.0.0.1:8080",
        "http://host.docker.internal:8080"
    ]
    
    print("📋 Configuração atual:")
    print(f"   URL: {settings.evolution_api_url}")
    print(f"   Instance: {settings.evolution_instance_name}")
    print(f"   API Key: {'***' + settings.evolution_api_key[-4:] if settings.evolution_api_key else 'NÃO CONFIGURADA'}")
    print()
    
    print("🔄 Testando URLs possíveis...\n")
    
    working_url = None
    
    for url in urls_to_test:
        try:
            print(f"   Testando: {url}")
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ FUNCIONANDO! Evolution API v{data.get('version', '?')}")
                    print(f"      Status: {data.get('status')}")
                    print(f"      Message: {data.get('message')}")
                    working_url = url
                    break
                else:
                    print(f"   ❌ Status {response.status_code}")
                    
        except httpx.ConnectError:
            print(f"   ❌ Conexão recusada")
        except httpx.TimeoutException:
            print(f"   ❌ Timeout")
        except Exception as e:
            print(f"   ❌ Erro: {type(e).__name__}")
    
    print("\n" + "="*60)
    
    if working_url:
        print("✅ EVOLUTION API ENCONTRADA!")
        print(f"\n📝 Atualize o arquivo .env com:")
        print(f"   EVOLUTION_API_URL={working_url}")
        
        if working_url != settings.evolution_api_url:
            print(f"\n⚠️  URL atual está incorreta!")
            print(f"   Configurada: {settings.evolution_api_url}")
            print(f"   Funcionando: {working_url}")
            
        # Testa a instância
        print(f"\n🔍 Verificando instância '{settings.evolution_instance_name}'...")
        try:
            async with httpx.AsyncClient(
                timeout=5.0,
                headers={"apikey": settings.evolution_api_key}
            ) as client:
                response = await client.get(
                    f"{working_url}/instance/connectionState/{settings.evolution_instance_name}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    state = data.get('state', 'unknown')
                    print(f"   Status da instância: {state}")
                    
                    if state == 'open':
                        print("   ✅ WhatsApp conectado e funcionando!")
                    else:
                        print("   ⚠️  WhatsApp não está conectado")
                        print("   Execute: GET /instance/connect/{instance} para gerar QR Code")
                elif response.status_code == 404:
                    print("   ❌ Instância não encontrada")
                    print("   Execute: POST /instance/create para criar a instância")
                else:
                    print(f"   ❌ Erro {response.status_code}: {response.text[:100]}")
                    
        except Exception as e:
            print(f"   ❌ Erro ao verificar instância: {e}")
            
    else:
        print("❌ EVOLUTION API NÃO ENCONTRADA!")
        print("\n📝 Possíveis soluções:")
        print("   1. Inicie a Evolution API:")
        print("      docker-compose up -d evolution-api")
        print("   2. Verifique se a porta 8080 está liberada")
        print("   3. Verifique o arquivo docker-compose.yml")
        print("   4. Se estiver usando EasyPanel, verifique a URL do serviço")
    
    print("\n" + "="*60 + "\n")
    
    return working_url is not None

if __name__ == "__main__":
    success = asyncio.run(check_evolution())
    sys.exit(0 if success else 1)