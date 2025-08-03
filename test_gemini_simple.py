#!/usr/bin/env python3
"""
Teste simples do Gemini com texto apenas
"""

import asyncio
from app.config import settings
import google.generativeai as genai

async def test_gemini_text():
    """Testa Gemini com texto apenas"""
    print("\n🔬 TESTE GEMINI - TEXTO APENAS")
    print("="*50)
    
    try:
        # Configurar API
        if not settings.google_api_key:
            print("❌ GOOGLE_API_KEY não configurada")
            return False
            
        genai.configure(api_key=settings.google_api_key)
        
        # Criar modelo
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Teste simples com texto
        print("📝 Enviando prompt de texto...")
        response = model.generate_content("Olá, você está funcionando? Responda em português.")
        
        print(f"✅ Resposta: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def main():
    print("\n" + "="*60)
    print("🚀 TESTE BÁSICO GEMINI API")
    print("="*60)
    
    success = await test_gemini_text()
    
    if success:
        print("\n✅ Gemini API está funcionando!")
        print("📝 O problema parece ser específico com imagens")
    else:
        print("\n❌ Problema com a API do Gemini")

if __name__ == "__main__":
    asyncio.run(main())