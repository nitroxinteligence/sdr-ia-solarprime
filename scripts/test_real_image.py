#!/usr/bin/env python3
"""
Script para testar com imagem real
==================================
Teste do agente com uma imagem real de conta de luz
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import create_sdr_agent

async def test_with_real_image():
    """Testa o agente com uma imagem real"""
    # Cria o agente
    agent = create_sdr_agent()
    
    # Caminho da imagem real (você precisa colocar uma imagem aqui)
    image_path = "/path/to/your/conta_luz.jpg"  # ALTERE ESTE CAMINHO
    
    # URL de uma imagem online (alternativa)
    image_url = "https://example.com/conta_luz.jpg"  # OU USE UMA URL
    
    print("🚀 Testando análise de imagem real...")
    
    # Teste com arquivo local
    try:
        response, metadata = await agent.process_message(
            "Segue minha conta de luz",
            "+5511999999999",
            media_type="image",
            media_data={"path": image_path}  # ou {"url": image_url}
        )
        
        print("\n📸 Resposta do agente:")
        print(response)
        
        if metadata.get("lead_info", {}).get("bill_value"):
            print("\n✅ Dados extraídos:")
            print(f"Valor: {metadata['lead_info']['bill_value']}")
            print(f"Consumo: {metadata['lead_info'].get('consumption_kwh', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_with_real_image())