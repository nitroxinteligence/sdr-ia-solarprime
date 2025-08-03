#!/usr/bin/env python3
"""
Teste do Gemini Vision com biblioteca nativa do Google
"""

import asyncio
from app.config import settings
import google.generativeai as genai
from PIL import Image as PILImage
import base64
from io import BytesIO

async def test_gemini_vision_native():
    """Testa Gemini Vision com biblioteca nativa"""
    print("\n🔬 TESTE GEMINI VISION - BIBLIOTECA NATIVA")
    print("="*50)
    
    try:
        # Configurar API
        if not settings.google_api_key:
            print("❌ GOOGLE_API_KEY não configurada")
            return False
            
        genai.configure(api_key=settings.google_api_key)
        
        # Criar modelo com visão
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Carregar e otimizar imagem
        print("📸 Carregando imagem...")
        with open("20250715_164305.png", 'rb') as f:
            img_bytes = f.read()
        
        print(f"   Tamanho original: {len(img_bytes):,} bytes")
        
        # Otimizar imagem
        img = PILImage.open(BytesIO(img_bytes))
        print(f"   Dimensões: {img.width}x{img.height}")
        
        # Redimensionar se necessário
        max_dim = 512  # Bem pequeno para teste
        if img.width > max_dim or img.height > max_dim:
            ratio = min(max_dim / img.width, max_dim / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, PILImage.Resampling.LANCZOS)
            print(f"   Redimensionada: {img.width}x{img.height}")
        
        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Salvar como JPEG otimizado
        output = BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True)
        optimized_bytes = output.getvalue()
        print(f"   Otimizada: {len(optimized_bytes):,} bytes")
        
        # Reabrir imagem otimizada com PIL
        img = PILImage.open(BytesIO(optimized_bytes))
        
        print("\n📤 Enviando para Gemini Vision...")
        
        # Enviar imagem e prompt
        response = model.generate_content([
            "Descreva brevemente o que você vê nesta imagem em português.",
            img
        ])
        
        print(f"\n✅ SUCESSO! Resposta do Gemini:")
        print(f"📝 {response.text}")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "="*60)
    print("🚀 TESTE GEMINI VISION - BIBLIOTECA NATIVA")
    print("="*60)
    
    success = await test_gemini_vision_native()
    
    print("\n" + "="*60)
    if success:
        print("✨ TESTE BEM-SUCEDIDO!")
        print("📊 Solução identificada:")
        print("   • Usar PIL Image diretamente")
        print("   • Redimensionar para <= 512px")
        print("   • Converter para RGB/JPEG")
    else:
        print("⚠️  Teste falhou")

if __name__ == "__main__":
    asyncio.run(main())