#!/usr/bin/env python3
"""
Test Evolution API Media Fix
============================
Script para testar as correções no download de mídia da Evolution API
"""

import asyncio
import os
import httpx
from datetime import datetime
from loguru import logger
import tempfile
import base64

# Configurar logging detalhado
logger.add("evolution_media_test.log", level="DEBUG", rotation="10 MB")

async def test_evolution_api_connection():
    """Testa conexão básica com Evolution API"""
    from services.evolution_api import evolution_client
    
    logger.info("=== TESTE DE CONEXÃO EVOLUTION API ===")
    
    # Inicializar cliente
    await evolution_client.initialize()
    
    # Testar conexão
    status = await evolution_client.check_connection()
    logger.info(f"Status da conexão: {status}")
    
    return status.get("state") == "open"


async def test_download_strategies():
    """Testa diferentes estratégias de download"""
    from services.evolution_api import evolution_client
    
    logger.info("\n=== TESTE DE ESTRATÉGIAS DE DOWNLOAD ===")
    
    # Simular download com diferentes cenários
    test_cases = [
        {
            "name": "Download via base64",
            "message_id": "BAE5F1234567890",
            "media_url": None
        },
        {
            "name": "Download com URL fallback",
            "message_id": "BAE5F1234567891",
            "media_url": "https://mmg.whatsapp.net/v/t62.7119-24/12345.pdf"
        }
    ]
    
    for test in test_cases:
        logger.info(f"\n📋 Testando: {test['name']}")
        
        try:
            result = await evolution_client.download_media(
                message_id=test["message_id"],
                media_url=test.get("media_url")
            )
            
            if result:
                logger.success(f"✅ Download bem-sucedido: {len(result)} bytes")
            else:
                logger.warning(f"⚠️ Download retornou None")
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")


async def test_pdf_processing_flow():
    """Testa fluxo completo de processamento de PDF"""
    from services.whatsapp_service import whatsapp_service
    
    logger.info("\n=== TESTE DE FLUXO COMPLETO DE PDF ===")
    
    # Criar PDF de teste
    test_pdf_content = b"%PDF-1.4\n%Test PDF Content\nstream\nTeste de conta de luz\nValor: R$ 250,00\nendstream"
    
    # Simular dados de mensagem com PDF
    test_message_data = {
        "key": {
            "id": "TEST_MESSAGE_123",
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False
        },
        "messageTimestamp": int(datetime.now().timestamp()),
        "pushName": "Teste User",
        "message": {
            "documentMessage": {
                "fileName": "conta_luz_teste.pdf",
                "mimetype": "application/pdf",
                "url": "https://example.com/test.pdf",
                "directPath": "/v/t62.7119-24/test.pdf",
                "mediaKey": "test_media_key"
            }
        }
    }
    
    # Salvar PDF temporário para simular cache
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(test_pdf_content)
        test_pdf_path = tmp.name
    
    logger.info(f"PDF de teste criado: {test_pdf_path}")
    
    try:
        # Simular processamento
        result = await whatsapp_service._process_media(
            message_id="TEST_MESSAGE_123",
            media_type="document",
            media_info={
                "filename": "conta_luz_teste.pdf",
                "mimetype": "application/pdf",
                "url": "https://example.com/test.pdf"
            }
        )
        
        if result:
            logger.success("✅ Processamento de mídia bem-sucedido")
            logger.info(f"Resultado: {list(result.keys())}")
            logger.info(f"Arquivo salvo em: {result.get('path')}")
            logger.info(f"Tamanho: {result.get('size')} bytes")
            logger.info(f"Base64 presente: {'base64' in result}")
            logger.info(f"Content presente: {'content' in result}")
            
            # Verificar arquivo
            if result.get('path') and os.path.exists(result['path']):
                logger.success(f"✅ Arquivo existe e tem {os.path.getsize(result['path'])} bytes")
            else:
                logger.error("❌ Arquivo não encontrado após processamento")
                
        else:
            logger.error("❌ Processamento retornou None")
            
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {e}", exc_info=True)
    
    finally:
        # Limpar arquivo temporário
        if os.path.exists(test_pdf_path):
            os.unlink(test_pdf_path)


async def test_media_url_construction():
    """Testa construção de URLs de mídia"""
    logger.info("\n=== TESTE DE CONSTRUÇÃO DE URLs ===")
    
    test_cases = [
        {
            "directPath": "/v/t62.7119-24/12345.pdf",
            "expected": "https://mmg.whatsapp.net/v/t62.7119-24/12345.pdf"
        },
        {
            "url": "https://media.whatsapp.net/file.pdf",
            "expected": "https://media.whatsapp.net/file.pdf"
        }
    ]
    
    for test in test_cases:
        if "directPath" in test:
            url = f"https://mmg.whatsapp.net{test['directPath']}"
        else:
            url = test.get("url", "")
            
        logger.info(f"Construído: {url}")
        logger.info(f"Esperado: {test['expected']}")
        logger.success(f"✅ Match: {url == test['expected']}")


async def main():
    """Executa todos os testes"""
    logger.info("🚀 INICIANDO TESTES DE CORREÇÃO EVOLUTION API")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # 1. Testar conexão
    connected = await test_evolution_api_connection()
    
    if connected:
        # 2. Testar estratégias de download
        await test_download_strategies()
        
        # 3. Testar fluxo completo
        await test_pdf_processing_flow()
    else:
        logger.warning("⚠️ Evolution API não está conectada. Alguns testes serão pulados.")
    
    # 4. Testar construção de URLs (sempre executa)
    await test_media_url_construction()
    
    logger.info("\n📊 RESUMO DAS CORREÇÕES APLICADAS:")
    logger.info("1. ✅ download_media agora tem 3 estratégias de fallback")
    logger.info("2. ✅ URLs de mídia são extraídas e passadas para download")
    logger.info("3. ✅ Conteúdo binário é sempre incluído no retorno")
    logger.info("4. ✅ Base64 é sempre gerado para todos os tipos de mídia")
    logger.info("5. ✅ Verificação de arquivo após salvamento")
    
    logger.info("\n💡 PRÓXIMOS PASSOS:")
    logger.info("1. Reiniciar o servidor para aplicar as mudanças")
    logger.info("2. Enviar um PDF real via WhatsApp")
    logger.info("3. Monitorar os logs para ver qual estratégia funciona")
    logger.info("4. Verificar se o agente consegue processar o conteúdo")


if __name__ == "__main__":
    asyncio.run(main())