#!/usr/bin/env python3
"""
Teste Final - Sistema Multimodal SDR IA SolarPrime
"""

import asyncio
import base64
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_extractor import document_extractor
from app.utils.logger import emoji_logger

async def test_pdf():
    """Testa extração de PDF"""
    print("\n🧪 TESTE PDF - Boleto.pdf")
    print("="*50)
    
    # Carregar PDF
    with open("Boleto.pdf", "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode()
    
    result = await document_extractor.extract_from_pdf(pdf_base64)
    
    if result["status"] == "success":
        print(f"✅ PDF extraído com sucesso!")
        print(f"📄 Páginas: {result.get('pages', 0)}")
        print(f"📝 Caracteres: {result.get('char_count', 0)}")
        print(f"📊 Tipo: {result.get('document_type', 'unknown')}")
        
        # Buscar valores
        import re
        valores = re.findall(r'R\$\s*[\d.,]+', result['text'])[:3]
        if valores:
            print(f"💰 Valores encontrados: {', '.join(valores)}")
        return True
    else:
        print(f"❌ Erro: {result.get('error')}")
        return False

async def main():
    print("\n" + "="*60)
    print("🚀 TESTE FINAL - SISTEMA MULTIMODAL")
    print("="*60)
    
    # Testar PDF
    pdf_ok = await test_pdf()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    if pdf_ok:
        print("✅ Extração de PDF: FUNCIONANDO")
        print("\n🎉 SISTEMA MULTIMODAL PARCIALMENTE VALIDADO!")
        print("📝 Nota: Processamento de imagem com Vision API requer")
        print("    configuração adicional do Gemini com suporte a imagens.")
        print("\n✨ PRÓXIMOS PASSOS:")
        print("1. Testar via WhatsApp real")
        print("2. Enviar PDFs e documentos")
        print("3. Enviar áudios para transcrição")
        print("4. Validar análise de contas de luz")
    else:
        print("❌ Sistema com problemas")

if __name__ == "__main__":
    asyncio.run(main())