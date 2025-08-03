#!/usr/bin/env python3
"""
Script de teste para validar o processamento de mídia do WhatsApp
"""

import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, Any

# Simular estrutura de mensagem da Evolution API
def create_test_image_message() -> Dict[str, Any]:
    """Cria uma mensagem de teste com imagem"""
    return {
        "instance": "solarprime",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST123"
            },
            "pushName": "Cliente Teste",
            "message": {
                "imageMessage": {
                    "url": "https://mmg.whatsapp.net/v/t62.7118-24/test.enc",
                    "mimetype": "image/jpeg",
                    "caption": "Conta de luz para análise",
                    "fileSha256": "abc123",
                    "fileLength": "245780",
                    "height": 1920,
                    "width": 1080,
                    "mediaKey": "key123",
                    "jpegThumbnail": base64.b64encode(b"thumbnail_data_here").decode()
                }
            },
            "messageTimestamp": str(int(datetime.now().timestamp()))
        }
    }

def create_test_document_message() -> Dict[str, Any]:
    """Cria uma mensagem de teste com documento"""
    return {
        "instance": "solarprime",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST456"
            },
            "pushName": "Cliente Teste",
            "message": {
                "documentMessage": {
                    "url": "https://mmg.whatsapp.net/v/t62.7119-24/test.enc",
                    "mimetype": "application/pdf",
                    "fileName": "conta_energia.pdf",
                    "fileSha256": "def456",
                    "fileLength": "512000",
                    "mediaKey": "key456",
                    "jpegThumbnail": base64.b64encode(b"pdf_thumb").decode()
                }
            },
            "messageTimestamp": str(int(datetime.now().timestamp()))
        }
    }

def create_test_audio_message() -> Dict[str, Any]:
    """Cria uma mensagem de teste com áudio"""
    return {
        "instance": "solarprime",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST789"
            },
            "pushName": "Cliente Teste",
            "message": {
                "audioMessage": {
                    "url": "https://mmg.whatsapp.net/v/t62.7117-24/test.enc",
                    "mimetype": "audio/ogg; codecs=opus",
                    "fileSha256": "ghi789",
                    "fileLength": "128000",
                    "seconds": 15,
                    "ptt": True,  # Push to talk (nota de voz)
                    "mediaKey": "key789"
                }
            },
            "messageTimestamp": str(int(datetime.now().timestamp()))
        }
    }

async def test_media_extraction():
    """Testa a extração de dados de mídia"""
    
    print("🧪 Testando extração de dados de mídia...")
    print("-" * 50)
    
    # Teste 1: Imagem
    print("\n📷 Teste 1: Processamento de Imagem")
    img_msg = create_test_image_message()
    img_data = img_msg["data"]["message"]["imageMessage"]
    
    print(f"  URL: {img_data.get('url', 'N/A')}")
    print(f"  Caption: {img_data.get('caption', 'N/A')}")
    print(f"  MimeType: {img_data.get('mimetype', 'N/A')}")
    print(f"  FileSize: {img_data.get('fileLength', 'N/A')} bytes")
    print(f"  Thumbnail: {'Presente' if img_data.get('jpegThumbnail') else 'Ausente'}")
    
    # Teste 2: Documento
    print("\n📄 Teste 2: Processamento de Documento")
    doc_msg = create_test_document_message()
    doc_data = doc_msg["data"]["message"]["documentMessage"]
    
    print(f"  URL: {doc_data.get('url', 'N/A')}")
    print(f"  FileName: {doc_data.get('fileName', 'N/A')}")
    print(f"  MimeType: {doc_data.get('mimetype', 'N/A')}")
    print(f"  FileSize: {doc_data.get('fileLength', 'N/A')} bytes")
    
    # Teste 3: Áudio
    print("\n🎤 Teste 3: Processamento de Áudio")
    audio_msg = create_test_audio_message()
    audio_data = audio_msg["data"]["message"]["audioMessage"]
    
    print(f"  URL: {audio_data.get('url', 'N/A')}")
    print(f"  Duration: {audio_data.get('seconds', 'N/A')} segundos")
    print(f"  MimeType: {audio_data.get('mimetype', 'N/A')}")
    print(f"  IsVoiceNote: {audio_data.get('ptt', False)}")
    print(f"  FileSize: {audio_data.get('fileLength', 'N/A')} bytes")
    
    print("\n" + "-" * 50)
    print("✅ Teste de extração concluído!")

async def test_media_processing_flow():
    """Testa o fluxo completo de processamento"""
    
    print("\n🔄 Testando fluxo de processamento...")
    print("-" * 50)
    
    # Simular o processamento no webhook
    test_message = create_test_image_message()
    original_message = test_message["data"]
    
    # Código similar ao webhook
    media_data = None
    if original_message.get("message", {}).get("imageMessage"):
        img_msg = original_message["message"]["imageMessage"]
        
        print("\n1️⃣ Detectando mídia na mensagem...")
        print(f"   Tipo: Imagem")
        print(f"   URL presente: {'✅' if img_msg.get('url') else '❌'}")
        print(f"   Thumbnail presente: {'✅' if img_msg.get('jpegThumbnail') else '❌'}")
        
        # Simular decisão de download
        image_base64 = None
        if img_msg.get("url"):
            print("\n2️⃣ Tentando baixar imagem completa...")
            print(f"   URL: {img_msg['url'][:50]}...")
            # Aqui seria feito o download real
            print("   ⚠️ Download simulado (em produção, usaria evolution_client.download_media)")
            image_base64 = "IMAGEM_COMPLETA_BASE64_AQUI"
        
        if not image_base64:
            print("\n3️⃣ Usando thumbnail como fallback...")
            image_base64 = img_msg.get("jpegThumbnail", "")
        
        media_data = {
            "type": "image",
            "mimetype": img_msg.get("mimetype", "image/jpeg"),
            "caption": img_msg.get("caption", ""),
            "data": image_base64,
            "has_full_image": bool(image_base64 and img_msg.get("url")),
            "file_size": img_msg.get("fileLength", 0)
        }
        
        print("\n4️⃣ Dados de mídia preparados:")
        print(f"   Tipo: {media_data['type']}")
        print(f"   Caption: {media_data['caption']}")
        print(f"   Imagem completa: {'✅' if media_data['has_full_image'] else '❌'}")
        print(f"   Tamanho: {media_data['file_size']} bytes")
    
    print("\n" + "-" * 50)
    print("✅ Fluxo de processamento testado!")
    
    return media_data

def main():
    """Função principal"""
    print("\n🚀 TESTE DE PROCESSAMENTO DE MÍDIA WHATSAPP")
    print("=" * 50)
    
    # Executar testes
    asyncio.run(test_media_extraction())
    media_result = asyncio.run(test_media_processing_flow())
    
    if media_result:
        print("\n📊 Resultado Final:")
        print(json.dumps(media_result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 50)
    print("🎉 Todos os testes concluídos!")

if __name__ == "__main__":
    main()