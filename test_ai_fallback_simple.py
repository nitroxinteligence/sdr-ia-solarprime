#!/usr/bin/env python3
"""
Teste Simplificado do Sistema de Fallback AI
===========================================
Testa apenas a lógica de fallback sem dependências externas
"""

import asyncio
import os
from dotenv import load_dotenv
import httpx
from loguru import logger
import sys

# Configurar logging
logger.remove()
logger.add(sys.stdout, level="DEBUG")

# Carregar variáveis de ambiente
load_dotenv()


async def test_gemini_api():
    """Testa conexão com Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return False, "API key não configurada"
    
    try:
        # Testar chamada simples ao Gemini
        from google import genai
        
        client = genai.Client(api_key=api_key)
        model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        
        response = await client.models.generate_content(
            model=model_id,
            config=genai.GenerateContentConfig(
                system_instruction="Você é um assistente que responde de forma breve.",
                temperature=0.7,
                candidate_count=1,
                max_output_tokens=100,
            ),
            contents=genai.Content(
                parts=[genai.Part(text="Responda apenas: OK")]
            ),
        )
        
        return True, "Gemini API funcionando"
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            return False, "Gemini sobrecarregado (503)"
        return False, f"Erro HTTP: {e.response.status_code}"
    except Exception as e:
        return False, f"Erro: {str(e)}"


async def test_openai_api():
    """Testa conexão com OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE":
        return False, "API key não configurada"
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente que responde de forma breve."},
                {"role": "user", "content": "Responda apenas: OK"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        return True, f"OpenAI API funcionando ({model})"
        
    except Exception as e:
        return False, f"Erro: {str(e)}"


async def simulate_fallback():
    """Simula o comportamento de fallback"""
    print("\n4. Simulando comportamento de fallback...")
    
    # Tentar Gemini primeiro
    print("   Tentando Gemini...")
    gemini_ok, gemini_msg = await test_gemini_api()
    
    if gemini_ok:
        print(f"   ✅ {gemini_msg} - Usando modelo primário")
        return "gemini"
    else:
        print(f"   ❌ {gemini_msg}")
        
        if os.getenv("ENABLE_FALLBACK", "true").lower() == "true":
            print("   Ativando fallback para OpenAI...")
            openai_ok, openai_msg = await test_openai_api()
            
            if openai_ok:
                print(f"   ✅ {openai_msg} - Usando modelo de fallback")
                return "openai"
            else:
                print(f"   ❌ {openai_msg}")
                print("   ⚠️  Nenhum modelo disponível!")
                return None
        else:
            print("   ⚠️  Fallback desabilitado")
            return None


async def main():
    """Função principal de teste"""
    print("=== TESTE SIMPLIFICADO DO SISTEMA DE FALLBACK AI ===\n")
    
    # 1. Verificar configuração
    print("1. Verificando configuração:")
    print(f"   - Gemini API Key: {'✅ Configurada' if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'YOUR_GEMINI_API_KEY_HERE' else '❌ Não configurada'}")
    print(f"   - OpenAI API Key: {'✅ Configurada' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'YOUR_OPENAI_API_KEY_HERE' else '❌ Não configurada'}")
    print(f"   - Fallback habilitado: {'✅ Sim' if os.getenv('ENABLE_FALLBACK', 'true').lower() == 'true' else '❌ Não'}")
    print(f"   - Modelo Gemini: {os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')}")
    print(f"   - Modelo OpenAI: {os.getenv('OPENAI_MODEL', 'gpt-4.1-nano')}")
    print()
    
    # 2. Testar Gemini
    print("2. Testando Gemini API:")
    gemini_ok, gemini_msg = await test_gemini_api()
    print(f"   {'✅' if gemini_ok else '❌'} {gemini_msg}")
    print()
    
    # 3. Testar OpenAI
    print("3. Testando OpenAI API:")
    openai_ok, openai_msg = await test_openai_api()
    print(f"   {'✅' if openai_ok else '❌'} {openai_msg}")
    print()
    
    # 4. Simular fallback
    modelo_usado = await simulate_fallback()
    
    print("\n=== RESULTADO DO TESTE ===")
    if modelo_usado:
        print(f"✅ Sistema de fallback funcionando! Modelo usado: {modelo_usado}")
    else:
        print("❌ Sistema indisponível - configure as API keys")
        print("\nPara configurar:")
        print("1. Edite o arquivo .env")
        print("2. Adicione sua GEMINI_API_KEY")
        print("3. Adicione sua OPENAI_API_KEY (para fallback)")


if __name__ == "__main__":
    asyncio.run(main())