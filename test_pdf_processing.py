#!/usr/bin/env python3
"""
Test PDF Processing
===================
Script para testar e diagnosticar problemas no processamento de PDF
"""

import asyncio
import os
from datetime import datetime
from loguru import logger

# Configurar logging detalhado
logger.add("pdf_test.log", level="DEBUG", rotation="10 MB")

async def test_pdf_flow():
    """Testa o fluxo completo de processamento de PDF"""
    
    logger.info("=== TESTE DE PROCESSAMENTO DE PDF ===")
    
    # 1. Testar com arquivo local
    test_pdf_path = "/tmp/test_conta_luz.pdf"
    
    if os.path.exists(test_pdf_path):
        logger.info(f"✅ Arquivo PDF de teste encontrado: {test_pdf_path}")
        
        # Simular dados que viriam do WhatsApp
        pdf_data = {
            "path": test_pdf_path,
            "mimetype": "application/pdf",
            "filename": "test_conta_luz.pdf"
        }
        
        # Testar processamento
        from agents.sdr_agent import create_sdr_agent
        agent = create_sdr_agent()
        
        logger.info("🔄 Iniciando processamento do PDF...")
        
        try:
            result = await agent._process_pdf_with_ocr(pdf_data)
            
            if result:
                logger.success("✅ PDF processado com sucesso!")
                logger.info(f"Resultado: {result}")
            else:
                logger.error("❌ Processamento retornou None")
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar PDF: {e}", exc_info=True)
            
    else:
        logger.warning(f"⚠️ Arquivo de teste não encontrado: {test_pdf_path}")
        logger.info("Crie um PDF de teste com uma conta de luz neste caminho")
    
    # 2. Testar download de mídia
    logger.info("\n=== TESTE DE DOWNLOAD DE MÍDIA ===")
    
    from services.evolution_api import evolution_client
    
    # Simular um message_id (você precisará de um real)
    test_message_id = "BAE5F1234567890"  # Substitua por um ID real
    
    try:
        logger.info(f"Tentando baixar mídia com ID: {test_message_id}")
        media_data = await evolution_client.download_media(test_message_id)
        
        if media_data:
            logger.success(f"✅ Mídia baixada: {len(media_data)} bytes")
        else:
            logger.warning("⚠️ download_media retornou None")
            
    except Exception as e:
        logger.error(f"❌ Erro ao baixar mídia: {e}")
    
    # 3. Verificar configuração do Gemini
    logger.info("\n=== VERIFICAÇÃO DO GEMINI ===")
    
    from config.config import get_config
    config = get_config()
    
    if config.gemini.api_key:
        logger.success("✅ API Key do Gemini configurada")
    else:
        logger.error("❌ API Key do Gemini não configurada!")
    
    logger.info(f"Modelo configurado: {config.gemini.model}")
    
    # 4. Teste de conversão PDF para imagem
    logger.info("\n=== TESTE DE CONVERSÃO PDF PARA IMAGEM ===")
    
    try:
        from pdf2image import convert_from_path
        logger.success("✅ pdf2image está instalado")
        
        if os.path.exists(test_pdf_path):
            images = convert_from_path(test_pdf_path, first_page=1, last_page=1)
            if images:
                logger.success(f"✅ PDF convertido para {len(images)} imagem(ns)")
            else:
                logger.error("❌ Conversão não retornou imagens")
                
    except ImportError:
        logger.warning("⚠️ pdf2image não está instalado")
        logger.info("Instale com: pip install pdf2image")
        logger.info("No Ubuntu: sudo apt-get install poppler-utils")
        logger.info("No macOS: brew install poppler")
    
    logger.info("\n=== DIAGNÓSTICO COMPLETO ===")
    
    # Resumo dos problemas encontrados
    logger.info("\n📋 RESUMO:")
    logger.info("1. Verifique se o arquivo PDF está sendo salvo corretamente pelo WhatsApp service")
    logger.info("2. Confirme que o Evolution API está baixando a mídia corretamente")
    logger.info("3. Certifique-se de que o pdf2image e poppler estão instalados")
    logger.info("4. Verifique os logs para ver exatamente onde o processo falha")
    
    logger.info("\n💡 SOLUÇÃO PROPOSTA:")
    logger.info("O problema parece estar no fato de que o PDF não está sendo")
    logger.info("corretamente passado do WhatsApp service para o agente.")
    logger.info("O 'path' existe mas o arquivo pode ter sido deletado ou")
    logger.info("não foi salvo corretamente.")


async def test_media_processing():
    """Testa especificamente o processamento de mídia do WhatsApp"""
    
    from services.whatsapp_service import whatsapp_service
    
    logger.info("\n=== TESTE DE PROCESSAMENTO DE MÍDIA ===")
    
    # Simular dados de mídia
    test_media_info = {
        "mimetype": "application/pdf",
        "filename": "Boleto.pdf"
    }
    
    # Simular processamento
    result = await whatsapp_service._process_media(
        message_id="test_message_123",
        media_type="document",
        media_info=test_media_info
    )
    
    if result:
        logger.success("✅ Mídia processada pelo WhatsApp service")
        logger.info(f"Resultado: {result}")
        
        # Verificar se o arquivo existe
        if 'path' in result and os.path.exists(result['path']):
            logger.success(f"✅ Arquivo existe: {result['path']}")
            logger.info(f"Tamanho: {os.path.getsize(result['path'])} bytes")
        else:
            logger.error("❌ Arquivo não encontrado após processamento")
    else:
        logger.error("❌ _process_media retornou None")


async def main():
    """Executa todos os testes"""
    await test_pdf_flow()
    await test_media_processing()


if __name__ == "__main__":
    asyncio.run(main())