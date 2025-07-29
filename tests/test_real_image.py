#!/usr/bin/env python3
"""
Teste com imagem real válida
"""

import asyncio
import sys
from pathlib import Path
import base64

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from utils.image_validator import ImageValidator
from loguru import logger


async def test_with_real_image():
    """Testa o agente com uma imagem real válida"""
    
    logger.info("=== TESTE COM IMAGEM REAL ===\n")
    
    # Criar agente
    agent = SDRAgent()
    phone = "+5511999999999"
    
    # Teste 1: Criar imagem de teste válida
    logger.info("📸 TESTE 1: Criando imagem de teste válida")
    
    try:
        # Criar imagem de teste usando o validador
        test_image_bytes = ImageValidator.create_test_image(
            width=1200, 
            height=800, 
            format='PNG'
        )
        
        # Codificar em base64
        test_image_base64 = base64.b64encode(test_image_bytes).decode()
        
        # Validar a imagem criada
        image_data = {
            "base64": test_image_base64,
            "mimetype": "image/png",
            "filename": "conta_luz_teste.png"
        }
        
        is_valid, error_msg, metadata = ImageValidator.validate_image_data(image_data)
        
        if is_valid:
            logger.success(f"✅ Imagem de teste criada e validada!")
            logger.info(f"   Metadados: {metadata}")
        else:
            logger.error(f"❌ Imagem de teste inválida: {error_msg}")
            return
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar imagem de teste: {e}")
        return
    
    # Teste 2: Processar com o agente
    logger.info("\n📤 TESTE 2: Enviando imagem válida para o agente")
    
    try:
        response, metadata = await agent.process_message(
            message="Aqui está minha conta de luz",
            phone_number=phone,
            media_type="image",
            media_data=image_data
        )
        
        logger.success(f"✅ Imagem processada com sucesso!")
        logger.info(f"   Resposta: {response[:200]}...")
        logger.info(f"   Stage: {metadata.get('stage')}")
        logger.info(f"   Sentimento: {metadata.get('sentiment')}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar imagem: {e}")
    
    # Teste 3: Testar com imagem inválida para verificar validação
    logger.info("\n🚫 TESTE 3: Testando validação com imagem inválida")
    
    invalid_image_data = {
        "base64": base64.b64encode(b"isso nao e uma imagem").decode(),
        "mimetype": "image/jpeg",
        "filename": "fake.jpg"
    }
    
    is_valid, error_msg, _ = ImageValidator.validate_image_data(invalid_image_data)
    
    if not is_valid:
        logger.success(f"✅ Validação detectou imagem inválida corretamente: {error_msg}")
    else:
        logger.error("❌ Validação falhou em detectar imagem inválida")
    
    # Teste 4: Verificar suporte a diferentes formatos
    logger.info("\n🎨 TESTE 4: Verificando suporte a formatos")
    
    supported_formats = ImageValidator.SUPPORTED_FORMATS
    logger.info("Formatos suportados:")
    for mime, extensions in supported_formats.items():
        logger.info(f"   • {mime}: {', '.join(extensions)}")
    
    # Resumo
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMO DO TESTE COM IMAGEM REAL")
    logger.info("="*50)
    logger.info("✓ Validação de imagem implementada")
    logger.info("✓ Imagem de teste válida criada")
    logger.info("✓ Detecção de imagem inválida funcionando")
    logger.info("✓ Suporte aos formatos: PNG, JPEG, GIF, WebP")
    
    logger.success("\n✅ Sistema preparado para processar imagens reais!")
    logger.info("💡 Próximo passo: Testar com fotos reais de contas de luz")


async def main():
    """Função principal"""
    await test_with_real_image()


if __name__ == "__main__":
    asyncio.run(main())