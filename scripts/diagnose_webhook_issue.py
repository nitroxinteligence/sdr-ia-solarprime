#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de webhook
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv
import json
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

async def test_evolution_api():
    """Testa conexão com Evolution API"""
    print("\n🔍 Testando Evolution API...")
    
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    
    print(f"URL: {base_url}")
    print(f"Instance: {instance_name}")
    print(f"API Key: {'✅ Configurada' if api_key else '❌ Não configurada'}")
    
    if not all([base_url, api_key, instance_name]):
        print("❌ Configuração incompleta da Evolution API")
        return False
    
    # Remover /manager da URL se existir
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Testar conexão básica
            response = await client.get(f"{base_url}/instance/fetchInstances", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                instances = response.json()
                print(f"✅ Conexão com Evolution API OK - {len(instances)} instâncias encontradas")
                
                # Procurar nossa instância
                our_instance = None
                for instance in instances:
                    if instance.get("instance", {}).get("instanceName") == instance_name:
                        our_instance = instance
                        break
                
                if our_instance:
                    status = our_instance.get("instance", {}).get("status")
                    print(f"✅ Instância '{instance_name}' encontrada - Status: {status}")
                    
                    # Verificar se está conectada ao WhatsApp
                    if status == "open":
                        print("✅ WhatsApp conectado e operacional")
                        return True
                    else:
                        print(f"⚠️ WhatsApp não está conectado - Status: {status}")
                        return False
                else:
                    print(f"❌ Instância '{instance_name}' não encontrada")
                    print("Instâncias disponíveis:")
                    for inst in instances:
                        print(f"  - {inst.get('instance', {}).get('instanceName')}")
                    return False
            else:
                print(f"❌ Erro ao conectar: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False


async def test_webhook_configuration():
    """Testa configuração do webhook"""
    print("\n🔍 Verificando configuração do webhook...")
    
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    webhook_url = os.getenv("WEBHOOK_BASE_URL", "")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Buscar configuração do webhook
            response = await client.get(
                f"{base_url}/webhook/find/{instance_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                webhook_config = response.json()
                print("✅ Configuração de webhook encontrada:")
                print(f"  - URL: {webhook_config.get('url', 'Não configurada')}")
                print(f"  - Enabled: {webhook_config.get('enabled', False)}")
                print(f"  - Events: {webhook_config.get('events', [])}")
                
                # Verificar se está apontando para nosso servidor
                configured_url = webhook_config.get('url', '')
                if webhook_url and webhook_url in configured_url:
                    print("✅ Webhook está apontando para nosso servidor")
                else:
                    print(f"⚠️ Webhook pode estar apontando para outro servidor")
                    print(f"  - Esperado: {webhook_url}")
                    print(f"  - Configurado: {configured_url}")
                
                return webhook_config
            else:
                print(f"❌ Webhook não configurado ou erro: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao verificar webhook: {e}")
            return None


async def send_test_message():
    """Envia mensagem de teste"""
    print("\n🔍 Enviando mensagem de teste...")
    
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    test_phone = os.getenv("TEST_PHONE_NUMBER", "")
    
    if not test_phone:
        print("⚠️ TEST_PHONE_NUMBER não configurado no .env")
        print("Configure para testar envio de mensagens")
        return False
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    # Formatar número
    test_phone = test_phone.replace("+", "").replace(" ", "").replace("-", "")
    if not test_phone.endswith("@s.whatsapp.net"):
        test_phone = f"{test_phone}@s.whatsapp.net"
    
    payload = {
        "number": test_phone,
        "text": f"🤖 Teste de diagnóstico SDR SolarPrime - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/message/sendText/{instance_name}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                print("✅ Mensagem enviada com sucesso!")
                result = response.json()
                print(f"  - ID: {result.get('key', {}).get('id')}")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False


async def test_local_api():
    """Testa API local"""
    print("\n🔍 Testando API local...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Testar health
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API local rodando - {data.get('app')} v{data.get('version')}")
                print(f"  - Status: {data.get('status')}")
                print(f"  - Agent: {data.get('agent')}")
            else:
                print(f"❌ API local com problema: {response.status_code}")
                return False
            
            # Testar webhook status
            response = await client.get("http://localhost:8000/webhook/status")
            if response.status_code == 200:
                status = response.json()
                print("\n✅ Webhook endpoint ativo:")
                config = status.get('config', {})
                print(f"  - Evolution API: {'✅' if config.get('evolution_api_configured') else '❌'}")
                print(f"  - Base URL: {config.get('base_url', 'não configurada')}")
                return True
            else:
                print(f"❌ Webhook endpoint com problema: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ API local não está rodando: {e}")
        return False


async def main():
    """Executa diagnóstico completo"""
    print("=" * 60)
    print("🔧 DIAGNÓSTICO DO SISTEMA SDR SOLARPRIME")
    print("=" * 60)
    
    # 1. Testar API local
    api_ok = await test_local_api()
    
    # 2. Testar Evolution API
    evolution_ok = await test_evolution_api()
    
    # 3. Verificar webhook
    webhook_config = await test_webhook_configuration()
    
    # 4. Enviar mensagem de teste (opcional)
    if evolution_ok and api_ok:
        await send_test_message()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    issues = []
    
    if not api_ok:
        issues.append("❌ API local não está funcionando corretamente")
    
    if not evolution_ok:
        issues.append("❌ Evolution API não está conectada ao WhatsApp")
    
    if not webhook_config or not webhook_config.get('enabled'):
        issues.append("❌ Webhook não está configurado ou desabilitado")
    
    if issues:
        print("\n🚨 PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n💡 SOLUÇÕES SUGERIDAS:")
        
        if not api_ok:
            print("\n1. Verificar se a API está rodando:")
            print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        
        if not evolution_ok:
            print("\n2. Reconectar WhatsApp na Evolution API:")
            print("   - Acesse o painel da Evolution API")
            print("   - Gere novo QR Code")
            print("   - Escaneie com WhatsApp")
        
        if not webhook_config or not webhook_config.get('enabled'):
            print("\n3. Configurar webhook:")
            print("   python scripts/configure_webhook.py")
    else:
        print("\n✅ Sistema aparentemente funcionando!")
        print("Se ainda não recebe mensagens, verifique:")
        print("  - Se o webhook está acessível externamente")
        print("  - Se há firewall bloqueando")
        print("  - Logs em tempo real: tail -f app.log")


if __name__ == "__main__":
    asyncio.run(main())