#!/usr/bin/env python3
"""
Teste do Processamento de Imagens com AGnO Framework
====================================================
Testa o processamento de imagens de contas de luz com Gemini e fallback OpenAI
"""

import asyncio
import os
import base64
from dotenv import load_dotenv
from agents.sdr_agent import SDRAgent
from loguru import logger
import sys

# Configurar logging
logger.remove()
logger.add(sys.stdout, level="DEBUG")

# Carregar variáveis de ambiente
load_dotenv()


async def test_image_processing():
    """Testa o processamento de imagem"""
    
    print("=== TESTE DO PROCESSAMENTO DE IMAGENS ===\n")
    
    # 1. Verificar configuração
    print("1. Verificando configuração:")
    print(f"   - Gemini API Key: {'✅ Configurada' if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'YOUR_GEMINI_API_KEY_HERE' else '❌ Não configurada'}")
    print(f"   - OpenAI API Key: {'✅ Configurada' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'YOUR_OPENAI_API_KEY_HERE' else '❌ Não configurada'}")
    print(f"   - Fallback habilitado: {'✅ Sim' if os.getenv('ENABLE_FALLBACK', 'true').lower() == 'true' else '❌ Não'}")
    print()
    
    # 2. Inicializar agente
    print("2. Inicializando agente SDR...")
    try:
        agent = SDRAgent()
        print("   ✅ Agente inicializado com sucesso")
        print()
    except Exception as e:
        print(f"   ❌ Erro ao inicializar agente: {e}")
        return
    
    # 3. Preparar dados de teste
    print("3. Preparando dados de teste...")
    
    # Exemplo de imagem base64 (você pode substituir por uma imagem real)
    # Esta é uma imagem de teste pequena em base64
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    # Diferentes formatos de teste
    test_cases = [
        {
            "name": "Imagem via URL",
            "media_type": "image",
            "media_data": {
                "url": "https://via.placeholder.com/400x600.png?text=Conta+de+Luz+Teste"
            }
        },
        {
            "name": "Imagem via Base64",
            "media_type": "image", 
            "media_data": {
                "base64": test_image_base64
            }
        }
    ]
    
    # 4. Testar processamento
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n4.{i}. Testando: {test_case['name']}")
        
        try:
            # Processar mensagem com imagem
            response, metadata = await agent.process_message(
                message="Aqui está minha conta de luz para análise",
                phone_number="5511999999999",
                message_id=f"TEST_IMG_{i}",
                media_type=test_case["media_type"],
                media_data=test_case["media_data"]
            )
            
            print(f"   ✅ Imagem processada com sucesso")
            print(f"   - Modelo usado: {metadata.get('model_used', 'unknown')}")
            print(f"   - Tempo de resposta: {metadata.get('response_time', 'N/A')}s")
            
            # Verificar se dados foram extraídos
            if metadata.get('media_processed'):
                print(f"   - Mídia processada: {metadata['media_processed']}")
            
            # Mostrar preview da resposta
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"   - Resposta: {preview}")
            
        except Exception as e:
            print(f"   ❌ Erro ao processar: {e}")
            import traceback
            traceback.print_exc()
    
    # 5. Testar com imagem real (se disponível)
    print("\n5. Teste com imagem real:")
    print("   Para testar com uma imagem real de conta de luz:")
    print("   1. Coloque o arquivo em: test_data/conta_luz.jpg")
    print("   2. Ou forneça uma URL de imagem válida")
    
    # Verificar se existe imagem de teste local
    test_image_path = "test_data/conta_luz.jpg"
    if os.path.exists(test_image_path):
        print(f"\n   ✅ Imagem de teste encontrada: {test_image_path}")
        print("   Processando...")
        
        try:
            response, metadata = await agent.process_message(
                message="Analisar esta conta de luz",
                phone_number="5511999999999",
                message_id="TEST_IMG_REAL",
                media_type="image",
                media_data={"path": test_image_path}
            )
            
            print(f"   ✅ Imagem real processada com sucesso")
            print(f"   - Modelo usado: {metadata.get('model_used', 'unknown')}")
            
            # Verificar extração de dados
            lead_info = metadata.get('lead_info', {})
            if lead_info.get('bill_value'):
                print(f"   - Valor da conta extraído: {lead_info['bill_value']}")
            if lead_info.get('consumption_kwh'):
                print(f"   - Consumo extraído: {lead_info['consumption_kwh']} kWh")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar imagem real: {e}")
    else:
        print(f"   ℹ️  Nenhuma imagem de teste encontrada em: {test_image_path}")
    
    print("\n=== TESTE CONCLUÍDO ===")


if __name__ == "__main__":
    asyncio.run(test_image_processing())