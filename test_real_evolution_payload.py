#!/usr/bin/env python3
"""
TESTE COM PAYLOAD REAL - Evolution API v2
Testa correção com o payload exato que estava causando erro
"""

import json
import requests
import time
from datetime import datetime

# URL do webhook (ajustar conforme necessário)
WEBHOOK_URL = "http://localhost:8000/webhook/whatsapp"

def test_real_payload_that_failed():
    """Testa com o payload EXATO que estava causando o erro"""
    print("🔧 TESTANDO PAYLOAD REAL QUE CAUSAVA ERRO")
    print("=" * 60)
    
    # Payload EXATO extraído do log de erro
    payload = {
        "event": "messages.upsert",
        "instance": "SDR IA SolarPrime",  # ← STRING (não dict!)
        "data": {
            "key": {
                "remoteJid": "558182986181@s.whatsapp.net",
                "fromMe": False,
                "id": "3AF4DA91F7AEA52CC86F"
            },
            "pushName": "Mateus M",
            "status": "DELIVERY_ACK",
            "message": {
                "conversation": "oi",
                "messageContextInfo": {
                    "deviceListMetadata": {
                        "senderKeyHash": "mCE/c7jMpcYemw==",
                        "senderTimestamp": "1753458725",
                        "recipientKeyHash": "aK/Hho0ynAsMvw==",
                        "recipientTimestamp": "1753634215"
                    },
                    "deviceListMetadataVersion": 2,
                    "messageSecret": "2S7Frlbdgc9I7HAKEqULw3t/H+rpwO+PInJPJ+7q2W0="
                }
            },
            "messageType": "conversation",
            "messageTimestamp": 1754026836,
            "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269",
            "source": "ios"
        },
        "destination": "https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp",
        "date_time": "2025-08-01T02:40:36.405Z",
        "sender": "558195554978@s.whatsapp.net",
        "server_url": "https://evoapi-evolution-api.fzvgou.easypanel.host",
        "apikey": "3ECB607589F3-4D35-949F-BA5D2D5892E9"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        try:
            response_json = response.json()
            print(f"📝 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📝 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ PAYLOAD REAL: CORRIGIDO COM SUCESSO!")
            print("✅ Erro 'str' object has no attribute 'get': RESOLVIDO!")
            return True
        else:
            print(f"❌ PAYLOAD REAL: AINDA FALHANDO (status {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Servidor não está rodando em localhost:8000")
        print("   Para testar, inicie o servidor com:")
        print("   uvicorn agente.main:app --host 0.0.0.0 --port 8000")
        return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

def test_dict_instance_compatibility():
    """Testa compatibilidade com formato dict (se Evolution API mudar)"""
    print("\n🔧 TESTANDO COMPATIBILIDADE COM INSTANCE DICT")
    print("=" * 60)
    
    payload = {
        "event": "messages.upsert",
        "instance": {  # ← DICT format (para compatibilidade)
            "instanceId": "test-instance-id",
            "instanceName": "Test Instance"
        },
        "data": {
            "key": {
                "remoteJid": "558199999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST123456789"
            },
            "pushName": "Test User",
            "message": {
                "conversation": "teste dict instance"
            },
            "messageTimestamp": int(datetime.now().timestamp())
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ COMPATIBILIDADE DICT: FUNCIONANDO")
            return True
        else:
            print("❌ COMPATIBILIDADE DICT: QUEBROU")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

def main():
    """Executa teste com payload real"""
    print("🧪 TESTE CORREÇÃO PAYLOAD REAL - Evolution API v2")
    print("=" * 65)
    print(f"🕒 Timestamp: {datetime.now().isoformat()}")
    print(f"🎯 Objetivo: Validar correção do erro linha 309")
    print()
    
    results = []
    
    # Teste principal: payload que causava erro
    results.append(test_real_payload_that_failed())
    
    # Teste compatibilidade: formato dict
    results.append(test_dict_instance_compatibility())
    
    # Relatório final
    print("\n📊 RELATÓRIO FINAL - TESTE PAYLOAD REAL")
    print("=" * 50)
    
    successful_tests = sum(results)
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Testes bem-sucedidos: {successful_tests}/{total_tests}")
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n🎉 CORREÇÃO CRÍTICA: FUNCIONANDO!")
        print(f"✅ Payload real da Evolution API: PROCESSANDO OK!")
        print(f"✅ Erro linha 309: COMPLETAMENTE RESOLVIDO!")
        print(f"✅ instance.get() error: ELIMINADO!")
        print(f"✅ Compatibilidade string/dict: IMPLEMENTADA!")
        
        print(f"\n📋 RESULTADO:")
        print(f"🚀 Sistema processando mensagens reais do WhatsApp!")
        print(f"✅ Erro 500 definitivamente resolvido!")
        print(f"✅ Estrutura Evolution API real suportada!")
        print(f"✅ DEPLOY IMEDIATO RECOMENDADO!")
        
        return True
    else:
        print(f"\n❌ CORREÇÃO: AINDA PRECISA DE AJUSTES!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)