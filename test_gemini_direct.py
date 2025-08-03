#!/usr/bin/env python3
"""
Teste direto com Gemini Vision API
"""

import asyncio
import base64
import os
from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Image
from io import BytesIO
from PIL import Image as PILImage

async def test_gemini_vision():
    """Testa Gemini Vision diretamente"""
    print("\n🔬 TESTE DIRETO GEMINI VISION")
    print("="*50)
    
    try:
        # Carregar imagem
        img_path = "20250715_164305.png"
        if not os.path.exists(img_path):
            print(f"❌ Arquivo {img_path} não encontrado")
            return False
            
        with open(img_path, 'rb') as f:
            original_bytes = f.read()
        
        print(f"📸 Imagem original: {len(original_bytes):,} bytes")
        
        # Otimizar imagem
        print("🔧 Otimizando imagem...")
        img = PILImage.open(BytesIO(original_bytes))
        print(f"   Dimensões originais: {img.width}x{img.height}")
        
        # Redimensionar para max 1024x1024
        max_dim = 1024
        if img.width > max_dim or img.height > max_dim:
            ratio = min(max_dim / img.width, max_dim / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, PILImage.Resampling.LANCZOS)
            print(f"   Redimensionada para: {img.width}x{img.height}")
        
        # Converter para JPEG
        output = BytesIO()
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                rgb_img.paste(img, mask=img.split()[-1])
            else:
                rgb_img.paste(img)
            img = rgb_img
        
        img.save(output, format='JPEG', quality=80, optimize=True)
        optimized_bytes = output.getvalue()
        print(f"✅ Imagem otimizada: {len(optimized_bytes):,} bytes ({len(optimized_bytes)/len(original_bytes)*100:.1f}%)")
        
        # Criar agente
        print("\n🤖 Inicializando Gemini...")
        
        # Carregar configuração
        from app.config import settings
        
        if not settings.google_api_key:
            print("❌ GOOGLE_API_KEY não configurada")
            return False
            
        model = Gemini(
            id="gemini-2.5-pro",
            api_key=settings.google_api_key
        )
        agent = Agent(
            name="Vision Test",
            model=model,
            instructions="Você é um assistente de análise de imagens.",
            markdown=True
        )
        
        # Testar com imagem otimizada
        print("📤 Enviando imagem otimizada...")
        image_obj = Image(content=optimized_bytes)
        
        prompt = "Descreva brevemente o que você vê nesta imagem."
        
        if hasattr(agent, 'arun'):
            result = await agent.arun(prompt, images=[image_obj])
        else:
            result = await agent.run(prompt, images=[image_obj])
        
        # Extrair resposta
        if hasattr(result, 'content'):
            content = result.content
        elif isinstance(result, dict) and 'content' in result:
            content = result['content']
        else:
            content = str(result)
        
        print(f"\n✅ SUCESSO! Gemini analisou a imagem:")
        print(f"📝 {content[:200]}...")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "="*60)
    print("🚀 TESTE DIRETO GEMINI VISION API")
    print("="*60)
    
    success = await test_gemini_vision()
    
    print("\n" + "="*60)
    if success:
        print("✨ TESTE BEM-SUCEDIDO!")
        print("📊 Solução identificada:")
        print("   • Redimensionar imagens grandes")
        print("   • Converter para JPEG com compressão")
        print("   • Manter dimensões <= 1024x1024")
    else:
        print("⚠️  Teste falhou - verifique os logs")

if __name__ == "__main__":
    asyncio.run(main())