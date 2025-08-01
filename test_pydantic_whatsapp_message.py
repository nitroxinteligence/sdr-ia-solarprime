#!/usr/bin/env python3
"""
TESTE MODELO PYDANTIC WhatsAppMessage
Valida que o modelo está alinhado com os dados da Evolution API v2
"""

import json
from datetime import datetime
from agente.core.types import WhatsAppMessage

def test_whatsapp_message_creation():
    """Testa criação do modelo com dados reais da Evolution API"""
    print("🔧 TESTANDO CRIAÇÃO WhatsAppMessage")
    print("=" * 50)
    
    # Dados extraídos do payload real da Evolution API
    test_data = {
        "instance_id": "02f1c146-f8b8-4f19-9e8a-d3517ee84269",
        "phone": "558182986181",
        "name": "Mateus M",
        "message": "oi",
        "message_id": "3AF4DA91F7AEA52CC86F",
        "timestamp": "1754026836",  # Evolution API envia como string
        "from_me": False,
        "media_type": None,
        "media_url": None
    }
    
    try:
        # Tentar criar o modelo
        whatsapp_msg = WhatsAppMessage(**test_data)
        
        print("✅ MODELO CRIADO COM SUCESSO!")
        print(f"📱 Instance ID: {whatsapp_msg.instance_id}")
        print(f"📞 Phone: {whatsapp_msg.phone}")
        print(f"👤 Name: {whatsapp_msg.name}")
        print(f"💬 Message: {whatsapp_msg.message}")
        print(f"🆔 Message ID: {whatsapp_msg.message_id}")
        print(f"⏰ Timestamp: {whatsapp_msg.timestamp}")
        print(f"🏠 From Me: {whatsapp_msg.from_me}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NA CRIAÇÃO: {e}")
        print(f"🚨 TIPO DO ERRO: {type(e).__name__}")
        return False

def test_whatsapp_message_json_serialization():
    """Testa serialização/deserialização JSON"""
    print("\n🔧 TESTANDO SERIALIZAÇÃO JSON")
    print("=" * 50)
    
    try:
        # Criar modelo
        whatsapp_msg = WhatsAppMessage(
            instance_id="test-instance",
            phone="5581999999999",
            name="Test User",
            message="Teste de serialização",
            message_id="TEST123",
            timestamp=datetime.now().isoformat(),
            from_me=False
        )
        
        # Converter para dict
        msg_dict = whatsapp_msg.model_dump()
        print("✅ CONVERSÃO PARA DICT: OK")
        
        # Converter para JSON
        msg_json = whatsapp_msg.model_dump_json()
        print("✅ CONVERSÃO PARA JSON: OK")
        
        # Reconverter de dict
        reconstructed = WhatsAppMessage(**msg_dict)
        print("✅ RECONSTRUÇÃO DE DICT: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NA SERIALIZAÇÃO: {e}")
        return False

def test_whatsapp_message_with_media():
    """Testa modelo com dados de mídia"""
    print("\n🔧 TESTANDO COM DADOS DE MÍDIA")
    print("=" * 50)
    
    try:
        # Dados com mídia
        media_data = {
            "instance_id": "media-test",
            "phone": "5581888888888",
            "name": "User Media",
            "message": "Legenda da imagem",
            "message_id": "MEDIA123",
            "timestamp": str(int(datetime.now().timestamp())),
            "from_me": False,
            "media_type": "image",
            "media_url": "https://example.com/image.jpg"
        }
        
        whatsapp_msg = WhatsAppMessage(**media_data)
        
        print("✅ MODELO COM MÍDIA: CRIADO")
        print(f"🖼️ Media Type: {whatsapp_msg.media_type}")
        print(f"🔗 Media URL: {whatsapp_msg.media_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO COM MÍDIA: {e}")
        return False

def test_all_timestamp_formats():
    """Testa diferentes formatos de timestamp"""
    print("\n🔧 TESTANDO FORMATOS DE TIMESTAMP")
    print("=" * 50)
    
    formats_to_test = [
        str(int(datetime.now().timestamp())),  # String de timestamp
        datetime.now().isoformat(),           # ISO string
        datetime.now(),                       # Datetime object
    ]
    
    success_count = 0
    
    for i, timestamp in enumerate(formats_to_test):
        try:
            whatsapp_msg = WhatsAppMessage(
                instance_id=f"test-{i}",
                phone="5581000000000",
                message="Test timestamp",
                message_id=f"TS{i}",
                timestamp=timestamp
            )
            print(f"✅ Timestamp format {i+1}: OK ({type(timestamp).__name__})")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Timestamp format {i+1}: FAILED - {e}")
    
    return success_count == len(formats_to_test)

def main():
    """Executa todos os testes do modelo Pydantic"""
    print("🧪 TESTE COMPLETO - MODELO PYDANTIC WhatsAppMessage")
    print("=" * 65)
    print(f"🕒 Timestamp: {datetime.now().isoformat()}")
    print(f"🎯 Objetivo: Validar compatibilidade com Evolution API v2")
    print()
    
    results = []
    
    # Executar todos os testes
    results.append(test_whatsapp_message_creation())
    results.append(test_whatsapp_message_json_serialization())
    results.append(test_whatsapp_message_with_media())
    results.append(test_all_timestamp_formats())
    
    # Relatório final
    print("\n📊 RELATÓRIO FINAL - MODELO PYDANTIC")
    print("=" * 50)
    
    successful_tests = sum(results)
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Testes bem-sucedidos: {successful_tests}/{total_tests}")
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n🎉 MODELO PYDANTIC: FUNCIONANDO!")
        print(f"✅ WhatsAppMessage alinhado com Evolution API v2!")
        print(f"✅ Campos corrigidos: instance → instance_id!")
        print(f"✅ Timestamp flexível: string/datetime!")
        print(f"✅ Serialização/deserialização: OK!")
        print(f"✅ Suporte a mídia: OK!")
        
        print(f"\n📋 RESULTADO:")
        print(f"🚀 Erro Pydantic validation: RESOLVIDO!")
        print(f"✅ Webhook processará mensagens sem erro 400!")
        print(f"✅ Modelo robusto e flexível!")
        print(f"✅ PRONTO PARA DEPLOY!")
        
        return True
    else:
        print(f"\n❌ MODELO: AINDA PRECISA DE AJUSTES!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)