#!/usr/bin/env python3
"""
Debug do problema de Vision API
"""

import asyncio
import base64
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

async def test_vision_debug():
    """Teste debug da Vision API"""
    print("\n🔬 DEBUG VISION API")
    print("="*50)
    
    try:
        # Inicializar AgenticSDR
        from app.agents.agentic_sdr import AgenticSDR
        agent = AgenticSDR()
        await agent.initialize()
        print("✅ AgenticSDR inicializado")
        
        # Carregar imagem teste
        img_path = "20250715_164305.png"
        if Path(img_path).exists():
            with open(img_path, 'rb') as f:
                img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            print(f"✅ Imagem: {len(img_bytes):,} bytes → {len(img_base64):,} chars base64")
        else:
            # Criar imagem base64 mínima para teste
            img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            print("⚠️  Usando imagem teste mínima")
        
        # Testar com debug
        print("\n📸 Chamando process_multimodal_content...")
        result = await agent.process_multimodal_content(
            media_type="image",
            media_data=img_base64,
            caption="Teste debug"
        )
        
        print(f"\n📊 Resultado:")
        print(f"   Tipo: {type(result)}")
        print(f"   Valor: {result}")
        
        if result:
            print("\n✅ Detalhes do resultado:")
            for key, value in result.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
        else:
            print("\n❌ Resultado é None ou vazio")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vision_debug())