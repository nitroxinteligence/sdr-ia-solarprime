#!/usr/bin/env python3
"""
Teste simples da Vision API com AGNO
"""

import asyncio
import base64
import os
from agno.agent import Agent
from agno.models.google import Gemini

async def test_vision():
    try:
        # Carregar a imagem
        img_path = "20250715_164305.png"
        if not os.path.exists(img_path):
            print(f"❌ Arquivo {img_path} não encontrado")
            return
            
        with open(img_path, 'rb') as f:
            img_base64 = base64.b64encode(f.read()).decode()
        
        print(f"✅ Imagem carregada: {len(img_base64)} caracteres base64")
        
        # Criar agente com Gemini
        print("🤖 Inicializando agente com Gemini...")
        
        # Configurar modelo Gemini
        model = Gemini(id="gemini-2.5-pro")
        
        agent = Agent(
            name="Vision Test Agent",
            model=model,
            instructions="Você é um assistente de análise de imagens.",
            show_tool_calls=True,
            markdown=True
        )
        
        # Preparar prompt
        prompt = """Analise esta imagem e descreva o que você vê.
        
        Por favor, identifique:
        - Cores principais
        - Objetos ou pessoas
        - Contexto geral da imagem
        """
        
        print("📸 Enviando imagem para análise...")
        
        # Testar diferentes formas de chamar
        try:
            # Criar objeto Image
            from agno.media import Image
            
            # Método 1: Tentar com data URL
            data_url = f"data:image/png;base64,{img_base64}"
            
            # Método 2: Com arun
            if hasattr(agent, 'arun'):
                print("Usando arun()...")
                # Tentar com data URL
                result = await agent.arun(prompt, images=[{"url": data_url}])
            else:
                print("Usando run()...")
                result = await agent.run(prompt, images=[{"url": data_url}])
            
            print(f"\nTipo do resultado: {type(result)}")
            print(f"Resultado tem 'content'? {hasattr(result, 'content')}")
            print(f"Resultado tem 'get'? {hasattr(result, 'get')}")
            
            # Extrair conteúdo
            if hasattr(result, 'content'):
                content = result.content
            elif isinstance(result, dict):
                content = result.get('content', str(result))
            else:
                content = str(result)
            
            print(f"\n✨ Análise da imagem:\n{content}")
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vision())