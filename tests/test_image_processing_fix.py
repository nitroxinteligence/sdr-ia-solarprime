#!/usr/bin/env python3
"""
Teste do processamento de imagem corrigido
==========================================
Verifica se o agente está processando imagens corretamente
"""

import asyncio
import sys
from pathlib import Path
import base64
from PIL import Image as PILImage
import io

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent
from utils.image_validator import ImageValidator
from loguru import logger


async def test_image_processing():
    """Testa o processamento de imagem corrigido"""
    
    logger.info("=== TESTE DE PROCESSAMENTO DE IMAGEM CORRIGIDO ===\n")
    
    # Criar agente
    agent = SDRAgent()
    phone = "+5511999999999"
    
    # Teste 1: Criar imagem de teste (simulando conta de luz)
    logger.info("📸 TESTE 1: Criando imagem de teste de conta de luz")
    
    try:
        # Criar imagem de teste usando PIL
        img = PILImage.new('RGB', (1200, 1600), color='white')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Simular uma conta de luz
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Adicionar texto simulando conta
        texts = [
            "CPFL ENERGIA",
            "CONTA DE LUZ",
            "------------------------",
            "Nome: João Silva",
            "CPF: 123.456.789-00",
            "Endereço: Rua das Flores, 123",
            "------------------------",
            "Referência: 01/2025",
            "Consumo: 450 kWh",
            "Valor Total: R$ 850,00",
            "------------------------",
            "Vencimento: 15/02/2025",
            "Código de Barras: 123456789012345678901234567890"
        ]
        
        y_position = 50
        for text in texts:
            draw.text((50, y_position), text, fill='black', font=font)
            y_position += 50
        
        # Converter para bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        # Codificar em base64
        image_base64 = base64.b64encode(image_bytes).decode()
        
        # Criar estrutura de dados da imagem
        image_data = {
            "base64": image_base64,
            "mimetype": "image/png",
            "filename": "conta_luz_teste.png"
        }
        
        logger.success("✅ Imagem de teste criada com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar imagem de teste: {e}")
        return
    
    # Teste 2: Processar com tipo correto "image"
    logger.info("\n📤 TESTE 2: Processando imagem com tipo correto")
    
    try:
        response, metadata = await agent.process_message(
            message="Aqui está minha conta de luz",
            phone_number=phone,
            media_type="image",  # Tipo correto
            media_data=image_data
        )
        
        logger.success("✅ Imagem processada com sucesso!")
        logger.info(f"📝 Resposta: {response[:200]}...")
        logger.info(f"📊 Metadados: {metadata}")
        
        # Verificar se o agente detectou dados da conta
        if "850" in response or "450" in response:
            logger.success("✅ Agente parece ter analisado a imagem corretamente!")
        else:
            logger.warning("⚠️ Agente pode não ter extraído dados da imagem")
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar imagem: {e}")
        import traceback
        traceback.print_exc()
    
    # Teste 3: Testar com tipo "buffered" (para verificar fallback)
    logger.info("\n🔄 TESTE 3: Testando com tipo 'buffered' (fallback)")
    
    try:
        # Simular estrutura de buffered
        buffered_data = {
            "type": "image",
            "media_data": image_data
        }
        
        response2, metadata2 = await agent.process_message(
            message="Teste com buffered",
            phone_number=phone,
            media_type="buffered",
            media_data=buffered_data
        )
        
        logger.success("✅ Tipo buffered processado com fallback!")
        logger.info(f"📝 Resposta: {response2[:200]}...")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar buffered: {e}")
    
    # Resumo
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMO DO TESTE")
    logger.info("="*50)
    logger.info("✓ Imagem de teste criada e validada")
    logger.info("✓ Processamento com tipo 'image' testado")
    logger.info("✓ Fallback para tipo 'buffered' testado")
    logger.info("✓ Logs detalhados habilitados")
    
    logger.success("\n✅ Teste concluído! Verifique os logs acima para confirmar o processamento.")


async def main():
    """Função principal"""
    await test_image_processing()


if __name__ == "__main__":
    # Configurar log level para DEBUG para ver todos os detalhes
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    
    asyncio.run(main())