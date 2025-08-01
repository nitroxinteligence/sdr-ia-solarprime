"""
Exemplo de uso das Media Tools do AGnO Framework
"""
import asyncio
from loguru import logger
from process_image import ProcessImageTool
from process_audio import ProcessAudioTool
from process_document import ProcessDocumentTool

async def test_media_tools():
    """Demonstra o uso das ferramentas de processamento de mídia"""
    
    logger.info("=== Testando Media Tools ===")
    
    # Exemplo 1: Processar imagem de conta de luz
    logger.info("\n1. Processando imagem de conta de luz:")
    image_result = await ProcessImageTool(
        media_url="https://example.com/conta_luz.jpg",
        context="conta de luz do cliente",
        extract_text=True
    )
    logger.info(f"Resultado: {image_result}")
    
    # Exemplo 2: Processar áudio com pergunta
    logger.info("\n2. Processando áudio com pergunta do cliente:")
    audio_result = await ProcessAudioTool(
        media_url="https://example.com/pergunta_cliente.ogg",
        context="pergunta sobre instalação",
        language="pt-BR"
    )
    logger.info(f"Resultado: {audio_result}")
    
    # Exemplo 3: Processar PDF de conta de luz
    logger.info("\n3. Processando PDF de conta de energia:")
    doc_result = await ProcessDocumentTool(
        media_url="https://example.com/fatura_energia.pdf",
        document_type="conta_luz",
        extract_specific_data=["valor_total", "consumo_kwh", "historico_consumo"]
    )
    logger.info(f"Resultado: {doc_result}")
    
    # Exemplo 4: Processar imagem genérica
    logger.info("\n4. Processando imagem do telhado:")
    image_telhado = await ProcessImageTool(
        media_url="https://example.com/foto_telhado.png",
        context="foto do telhado para instalação"
    )
    logger.info(f"Resultado: {image_telhado}")
    
    # Exemplo 5: Processar documento genérico
    logger.info("\n5. Processando documento sem tipo específico:")
    doc_generic = await ProcessDocumentTool(
        media_url="https://example.com/documento.pdf"
    )
    logger.info(f"Resultado: {doc_generic}")

if __name__ == "__main__":
    # Executar os testes
    asyncio.run(test_media_tools())