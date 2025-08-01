#!/usr/bin/env python3
"""
DIAGNÓSTICO KOMMO CRM - Token e Autenticação
Verifica se o token está válido e funcionando corretamente
"""

import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Setup do ambiente
root_dir = Path(__file__).parent
load_dotenv(root_dir / '.env')

KOMMO_SUBDOMAIN = os.getenv('KOMMO_SUBDOMAIN', '')
KOMMO_LONG_LIVED_TOKEN = os.getenv('KOMMO_LONG_LIVED_TOKEN', '')
KOMMO_BASE_URL = f"https://{KOMMO_SUBDOMAIN}.kommo.com"

print("🔍 DIAGNÓSTICO KOMMO CRM - TOKEN E AUTENTICAÇÃO")
print("=" * 60)
print(f"📊 Configuração atual:")
print(f"   🌐 Subdomain: {KOMMO_SUBDOMAIN}")
print(f"   🔗 Base URL: {KOMMO_BASE_URL}")
print(f"   🔑 Token: {KOMMO_LONG_LIVED_TOKEN[:20]}...")

async def test_kommo_token():
    """Testa o token do Kommo em diferentes endpoints"""
    
    headers = {
        'Authorization': f'Bearer {KOMMO_LONG_LIVED_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'SDR-IA-SolarPrime/1.0'
    }
    
    test_endpoints = [
        ('/api/v4/account', 'GET', 'Informações da conta'),
        ('/api/v4/users', 'GET', 'Lista de usuários'),
        ('/api/v4/leads/pipelines', 'GET', 'Pipelines'),
        ('/api/v4/leads/custom_fields', 'GET', 'Campos customizados')
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint, method, description in test_endpoints:
            print(f"\n🧪 TESTANDO: {description}")
            print(f"   📍 Endpoint: {method} {endpoint}")
            
            try:
                url = f"{KOMMO_BASE_URL}{endpoint}"
                response = await client.request(method, url, headers=headers)
                
                print(f"   📊 Status Code: {response.status_code}")
                print(f"   📋 Headers: {dict(response.headers)}")
                
                # Verificar se é HTML ou JSON
                content_type = response.headers.get('content-type', '')
                print(f"   📄 Content-Type: {content_type}")
                
                if 'html' in content_type.lower():
                    print(f"   ❌ ERRO: Recebendo HTML em vez de JSON!")
                    print(f"   📝 Primeiras 200 chars: {response.text[:200]}")
                elif 'json' in content_type.lower():
                    try:
                        data = response.json()
                        print(f"   ✅ JSON válido recebido")
                        print(f"   📦 Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                        
                        # Log específico para cada endpoint
                        if endpoint == '/api/v4/account':
                            account_name = data.get('name', 'N/A')
                            account_id = data.get('id', 'N/A')
                            print(f"   👤 Conta: {account_name} (ID: {account_id})")
                        
                        elif endpoint == '/api/v4/leads/pipelines':
                            pipelines = data.get('_embedded', {}).get('pipelines', [])
                            print(f"   📋 Pipelines encontrados: {len(pipelines)}")
                            for pipeline in pipelines[:2]:  # Primeiros 2
                                name = pipeline.get('name', 'N/A')
                                pipeline_id = pipeline.get('id', 'N/A')
                                print(f"      - {name} (ID: {pipeline_id})")
                        
                    except json.JSONDecodeError as e:
                        print(f"   ❌ ERRO JSON: {str(e)}")
                        print(f"   📝 Response: {response.text[:200]}")
                else:
                    print(f"   ⚠️ Content-Type inesperado")
                    print(f"   📝 Response: {response.text[:200]}")
                
            except httpx.TimeoutException:
                print(f"   ❌ TIMEOUT na requisição")
            except httpx.RequestError as e:
                print(f"   ❌ ERRO na requisição: {str(e)}")
            except Exception as e:
                print(f"   ❌ ERRO inesperado: {str(e)}")

async def test_create_lead():
    """Testa criação de lead simples"""
    print(f"\n🧪 TESTE: Criação de Lead")
    
    headers = {
        'Authorization': f'Bearer {KOMMO_LONG_LIVED_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Lead de teste simples
    test_lead = {
        "name": f"[DIAGNÓSTICO] Lead Teste {int(datetime.now().timestamp())}",
        "price": 50000
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            url = f"{KOMMO_BASE_URL}/api/v4/leads"
            response = await client.post(url, headers=headers, json=[test_lead])
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   📄 Content-Type: {response.headers.get('content-type', '')}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                leads = data.get('_embedded', {}).get('leads', [])
                if leads:
                    lead = leads[0]
                    print(f"   ✅ Lead criado com sucesso!")
                    print(f"   🆔 ID: {lead.get('id')}")
                    print(f"   👤 Nome: {lead.get('name')}")
                else:
                    print(f"   ⚠️ Lead criado mas sem dados na resposta")
            else:
                print(f"   ❌ Falha na criação do lead")
                print(f"   📝 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ ERRO: {str(e)}")

async def main():
    """Função principal de diagnóstico"""
    print(f"\n⏰ Iniciando diagnóstico em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not KOMMO_SUBDOMAIN or not KOMMO_LONG_LIVED_TOKEN:
        print("❌ ERRO: Variáveis KOMMO_SUBDOMAIN ou KOMMO_LONG_LIVED_TOKEN não configuradas!")
        return False
    
    await test_kommo_token()
    await test_create_lead()
    
    print(f"\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    result = asyncio.run(main())