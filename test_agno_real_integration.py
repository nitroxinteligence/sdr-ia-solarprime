#!/usr/bin/env python3
"""
Test AGnO Real Integration
==========================
Script para testar a integração real entre Evolution API, WhatsApp Service e AGnO Framework
"""

import asyncio
import os
import sys
from datetime import datetime
from loguru import logger
import base64
import json
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

# Configurar logging detalhado
logger.add("agno_integration_test.log", level="DEBUG", rotation="10 MB")

async def test_evolution_api_download():
    """Testa se Evolution API está baixando mídia corretamente"""
    from services.evolution_api import evolution_client
    
    logger.info("=== TESTE 1: EVOLUTION API DOWNLOAD ===")
    
    # Inicializar cliente
    await evolution_client.initialize()
    
    # Verificar conexão
    status = await evolution_client.check_connection()
    logger.info(f"Status da conexão: {status}")
    
    if status.get("state") != "open":
        logger.error("❌ Evolution API não está conectada ao WhatsApp")
        return False
    
    logger.success("✅ Evolution API conectada")
    
    # Simular download (você precisará de um message_id real)
    test_message_id = os.getenv("TEST_MESSAGE_ID", "")
    if test_message_id:
        logger.info(f"Tentando baixar mídia: {test_message_id}")
        media_data = await evolution_client.download_media(test_message_id)
        
        if media_data:
            logger.success(f"✅ Mídia baixada: {len(media_data)} bytes")
            
            # Salvar para análise
            with open("/tmp/test_media_download.bin", "wb") as f:
                f.write(media_data)
            logger.info("Mídia salva em /tmp/test_media_download.bin")
            
            return media_data
        else:
            logger.error("❌ Download retornou None")
    else:
        logger.warning("⚠️ TEST_MESSAGE_ID não configurado")
    
    return None


async def test_image_validation():
    """Testa validação de imagem com dados reais"""
    logger.info("\n=== TESTE 2: VALIDAÇÃO DE IMAGEM ===")
    
    # Tentar carregar uma imagem de teste real
    test_images = [
        "/tmp/test_media_download.bin",  # Do teste anterior
        "./test_data/conta_luz.jpg",     # Imagem local de teste
        "./test_data/test_image.png"     # Outra imagem de teste
    ]
    
    from PIL import Image as PILImage
    import io
    import magic
    
    for image_path in test_images:
        if os.path.exists(image_path):
            logger.info(f"\n📋 Testando: {image_path}")
            
            try:
                with open(image_path, "rb") as f:
                    content = f.read()
                
                logger.info(f"Tamanho: {len(content)} bytes")
                
                # Verificar tipo MIME
                mime_type = magic.from_buffer(content, mime=True)
                logger.info(f"MIME Type: {mime_type}")
                
                # Tentar abrir como imagem
                img = PILImage.open(io.BytesIO(content))
                logger.info(f"Formato: {img.format}")
                logger.info(f"Dimensões: {img.size}")
                logger.info(f"Modo: {img.mode}")
                
                logger.success(f"✅ Imagem válida: {image_path}")
                
                return content  # Retornar primeira imagem válida
                
            except Exception as e:
                logger.error(f"❌ Erro ao validar {image_path}: {e}")
    
    logger.warning("⚠️ Nenhuma imagem de teste encontrada")
    return None


async def test_agno_image_creation():
    """Testa criação de objeto Image do AGnO"""
    logger.info("\n=== TESTE 3: CRIAÇÃO DE OBJETO AGNO IMAGE ===")
    
    from agents.sdr_agent import create_sdr_agent
    
    # Obter conteúdo de imagem válido
    image_content = await test_image_validation()
    
    if not image_content:
        logger.error("❌ Sem conteúdo de imagem para testar")
        return None
    
    # Criar agente
    agent = create_sdr_agent()
    
    # Testar criação com diferentes formatos
    test_cases = [
        {
            "name": "Conteúdo binário direto",
            "data": {
                "content": image_content,
                "mimetype": "image/jpeg"
            }
        },
        {
            "name": "Base64",
            "data": {
                "base64": base64.b64encode(image_content).decode(),
                "mimetype": "image/jpeg"
            }
        },
        {
            "name": "Dados completos",
            "data": {
                "content": image_content,
                "base64": base64.b64encode(image_content).decode(),
                "mimetype": "image/jpeg",
                "size": len(image_content)
            }
        }
    ]
    
    for test in test_cases:
        logger.info(f"\n🧪 {test['name']}")
        
        try:
            image_obj = agent._create_agno_image(test['data'])
            
            if image_obj:
                logger.success("✅ Objeto Image criado com sucesso")
                logger.info(f"Tipo: {type(image_obj)}")
                
                # Verificar atributos
                if hasattr(image_obj, 'content'):
                    logger.info(f"Content presente: {len(image_obj.content) if image_obj.content else 0} bytes")
                if hasattr(image_obj, 'url'):
                    logger.info(f"URL: {image_obj.url}")
                
                return image_obj
            else:
                logger.error("❌ Falha ao criar objeto Image")
                
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
    
    return None


async def test_agno_processing():
    """Testa processamento completo com AGnO"""
    logger.info("\n=== TESTE 4: PROCESSAMENTO COM AGNO ===")
    
    from agents.sdr_agent import create_sdr_agent
    
    # Criar agente
    agent = create_sdr_agent()
    
    # Obter imagem válida
    image_content = await test_image_validation()
    if not image_content:
        logger.error("❌ Sem imagem para processar")
        return
    
    # Criar dados de mídia completos
    media_data = {
        "content": image_content,
        "base64": base64.b64encode(image_content).decode(),
        "mimetype": "image/jpeg",
        "size": len(image_content)
    }
    
    # Testar processamento
    try:
        logger.info("🤖 Processando imagem com AGnO...")
        
        result = await agent._process_media(
            media_type="image",
            media_data=media_data
        )
        
        if result:
            logger.success("✅ Processamento concluído")
            logger.info(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            logger.error("❌ Processamento retornou None")
            
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {e}", exc_info=True)


async def test_full_pipeline():
    """Testa pipeline completo: WhatsApp → Evolution → AGnO"""
    logger.info("\n=== TESTE 5: PIPELINE COMPLETO ===")
    
    from services.whatsapp_service import whatsapp_service
    
    # Simular webhook real
    webhook_data = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "id": os.getenv("TEST_MESSAGE_ID", "TEST_123"),
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False
            },
            "messageTimestamp": int(datetime.now().timestamp()),
            "pushName": "Teste Real",
            "message": {
                "imageMessage": {
                    "caption": "Conta de luz para análise",
                    "mimetype": "image/jpeg",
                    "url": "https://mmg.whatsapp.net/...",
                    "directPath": "/v/t62.7119-24/...",
                    "mediaKey": "test_key",
                    "fileLength": "245632",
                    "height": 1920,
                    "width": 1080
                }
            }
        }
    }
    
    logger.info("📨 Simulando recepção de imagem via webhook")
    
    try:
        # Processar webhook
        result = await whatsapp_service.process_webhook(webhook_data)
        
        logger.info(f"Resultado: {json.dumps(result, indent=2)}")
        
        if result.get("status") == "success":
            logger.success("✅ Pipeline completo funcionou!")
        else:
            logger.error(f"❌ Pipeline falhou: {result}")
            
    except Exception as e:
        logger.error(f"❌ Erro no pipeline: {e}", exc_info=True)


async def create_test_image():
    """Cria uma imagem de teste se não existir"""
    logger.info("\n=== CRIANDO IMAGEM DE TESTE ===")
    
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Criar diretório de teste
    os.makedirs("test_data", exist_ok=True)
    
    # Criar imagem de teste
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Adicionar texto
    text = "CONTA DE LUZ TESTE\nValor: R$ 250,00\nConsumo: 350 kWh"
    draw.text((50, 50), text, fill='black')
    
    # Salvar
    img_path = "test_data/conta_luz_teste.jpg"
    img.save(img_path, "JPEG")
    
    logger.success(f"✅ Imagem de teste criada: {img_path}")
    
    # Retornar bytes
    with open(img_path, "rb") as f:
        return f.read()


async def main():
    """Executa todos os testes"""
    logger.info("🚀 INICIANDO TESTES DE INTEGRAÇÃO AGNO REAL")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Criar imagem de teste se necessário
    await create_test_image()
    
    # Executar testes em sequência
    tests = [
        ("Evolution API Download", test_evolution_api_download),
        ("Validação de Imagem", test_image_validation),
        ("Criação AGnO Image", test_agno_image_creation),
        ("Processamento AGnO", test_agno_processing),
        ("Pipeline Completo", test_full_pipeline)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Executando: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            await test_func()
            results.append((test_name, "✅ PASSOU"))
        except Exception as e:
            logger.error(f"Teste falhou: {e}", exc_info=True)
            results.append((test_name, f"❌ FALHOU: {str(e)}"))
    
    # Resumo final
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("="*60)
    
    for test_name, result in results:
        logger.info(f"{test_name}: {result}")
    
    # Diagnóstico
    logger.info("\n💡 DIAGNÓSTICO:")
    logger.info("1. Se Evolution API falhou: Verificar conexão e configuração")
    logger.info("2. Se validação falhou: Verificar formato da imagem")
    logger.info("3. Se AGnO falhou: Verificar instalação do framework")
    logger.info("4. Se pipeline falhou: Verificar integração entre serviços")
    
    logger.info("\n🔧 PRÓXIMOS PASSOS:")
    logger.info("1. Configure TEST_MESSAGE_ID com um ID real de mensagem")
    logger.info("2. Certifique-se que Evolution API está conectada")
    logger.info("3. Verifique logs detalhados em agno_integration_test.log")


if __name__ == "__main__":
    # Instalar dependências se necessário
    try:
        import magic
    except ImportError:
        logger.warning("python-magic não instalado. Instalando...")
        os.system("pip install python-magic-bin")
    
    asyncio.run(main())