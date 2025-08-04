#!/usr/bin/env python3
"""
Script de teste para descriptografia de mídia do WhatsApp
"""

import asyncio
import base64
from app.integrations.evolution import evolution_client
from loguru import logger

async def test_decrypt():
    """Testa a descriptografia de mídia com dados de exemplo"""
    
    # Exemplo de dados criptografados (você pode substituir com dados reais)
    # Este é um exemplo fictício - substitua com dados reais do webhook
    test_data = {
        "encrypted_data": b"",  # Dados criptografados em bytes
        "media_key": "",  # MediaKey em base64 do webhook
        "media_type": "image"  # Tipo de mídia
    }
    
    # Se você tem dados reais do webhook, use-os aqui:
    # test_data = {
    #     "encrypted_data": base64.b64decode("..."),  # Converta de base64 se necessário
    #     "media_key": "bKAgOYLhpEHewOz/Fcfb...",  # MediaKey do webhook
    #     "media_type": "image"
    # }
    
    logger.info("=" * 60)
    logger.info("TESTE DE DESCRIPTOGRAFIA DE MÍDIA DO WHATSAPP")
    logger.info("=" * 60)
    
    if not test_data["encrypted_data"] or not test_data["media_key"]:
        logger.warning("Por favor, adicione dados de teste reais no script")
        logger.info("Você pode obter esses dados dos logs do webhook quando receber uma mídia")
        return
    
    # Teste 1: Descriptografia direta
    logger.info("\n📦 Teste 1: Descriptografia direta")
    logger.info(f"Tamanho dos dados criptografados: {len(test_data['encrypted_data'])} bytes")
    logger.info(f"MediaKey (primeiros 20 chars): {test_data['media_key'][:20]}...")
    
    result = evolution_client.decrypt_whatsapp_media(
        encrypted_data=test_data["encrypted_data"],
        media_key_base64=test_data["media_key"],
        media_type=test_data["media_type"]
    )
    
    if result:
        logger.success(f"✅ Descriptografia bem-sucedida! Tamanho: {len(result)} bytes")
        
        # Verificar os primeiros bytes para identificar o formato
        if result[:4] == b'\xff\xd8\xff\xe0':
            logger.info("📷 Formato detectado: JPEG")
        elif result[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            logger.info("🖼️ Formato detectado: PNG")
        elif result[:4] == b'\x52\x49\x46\x46':
            logger.info("🎵 Formato detectado: RIFF/WebP/WAV")
        else:
            logger.info(f"❓ Magic bytes: {result[:8].hex()}")
    else:
        logger.error("❌ Falha na descriptografia")
    
    # Teste 2: Download com descriptografia integrada
    logger.info("\n📦 Teste 2: Download com descriptografia integrada")
    
    test_download_data = {
        "mediaUrl": "https://example.com/media",  # URL da mídia
        "mediaKey": test_data["media_key"],
        "mediaType": test_data["media_type"]
    }
    
    logger.info("Testando download_media com mediaKey...")
    # Este teste só funcionará com uma URL real
    # result = await evolution_client.download_media(test_download_data)
    logger.info("⚠️ Teste de download pulado (precisa de URL real)")
    
    logger.info("\n" + "=" * 60)
    logger.info("TESTE CONCLUÍDO")
    logger.info("=" * 60)

if __name__ == "__main__":
    # Configurar logging
    logger.add("test_media_decrypt.log", rotation="10 MB")
    
    # Executar teste
    asyncio.run(test_decrypt())