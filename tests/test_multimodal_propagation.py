#!/usr/bin/env python3
"""
Test Multimodal Propagation - Verifica se dados multimodais chegam ao agente
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.teams.sdr_team import SDRTeam
from app.utils.logger import emoji_logger


async def test_audio_propagation():
    """Testa se transcrição de áudio chega ao agente"""
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("🎵 TESTE: Propagação de Áudio para Agente")
    emoji_logger.system_info("="*60)
    
    # Criar contexto enriquecido com transcrição
    enriched_context = {
        "phone": "11999998888",
        "message": "",  # Mensagem vazia, conteúdo está na transcrição
        "lead_data": {
            "name": "João Teste",
            "phone": "11999998888"
        },
        "conversation_id": "test_audio_001",
        "multimodal_result": {
            "type": "audio",
            "transcription": "Olá, gostaria de saber o preço dos painéis solares para minha casa",
            "duration": 5.0,
            "status": "transcribed",
            "engine": "google_speech"
        }
    }
    
    # Criar SDR Team
    team = SDRTeam()
    
    # Processar mensagem com contexto enriquecido
    response = await team.process_message_with_context(
        enriched_context
    )
    
    # Verificar se a resposta menciona o conteúdo do áudio
    emoji_logger.system_info(f"\n📤 Resposta do agente: {response}")
    
    # Análise
    keywords = ["painel", "solar", "preço", "casa"]
    found = any(keyword in response.lower() for keyword in keywords)
    
    if found:
        emoji_logger.system_info("✅ SUCESSO: Agente respondeu baseado na transcrição do áudio!")
    else:
        emoji_logger.system_error("Test Failed", "Agente NÃO usou a transcrição do áudio na resposta")
    
    return found


async def test_image_propagation():
    """Testa se análise de imagem chega ao agente"""
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("🖼️ TESTE: Propagação de Imagem para Agente")
    emoji_logger.system_info("="*60)
    
    # Criar contexto enriquecido com análise de conta de luz
    enriched_context = {
        "phone": "11888887777",
        "message": "Analisei minha conta",
        "lead_data": {
            "name": "Maria Teste",
            "phone": "11888887777"
        },
        "conversation_id": "test_image_001",
        "multimodal_result": {
            "type": "bill_image",
            "needs_analysis": True,
            "content": """Análise da conta de luz:
            - Consumo: 297 kWh
            - Valor total: R$ 287,45
            - Vencimento: 15/07/2025
            - Empresa: Neoenergia Pernambuco
            - Potencial economia com solar: R$ 230,00/mês"""
        }
    }
    
    # Criar SDR Team
    team = SDRTeam()
    
    # Processar mensagem com contexto enriquecido
    response = await team.process_message_with_context(
        enriched_context
    )
    
    # Verificar se a resposta menciona dados da conta
    emoji_logger.system_info(f"\n📤 Resposta do agente: {response}")
    
    # Análise
    keywords = ["297", "287", "economia", "230", "kwh", "neoenergia"]
    found = any(keyword in response.lower() for keyword in keywords)
    
    if found:
        emoji_logger.system_info("✅ SUCESSO: Agente respondeu baseado na análise da imagem!")
    else:
        emoji_logger.system_error("Test Failed", "Agente NÃO usou a análise da imagem na resposta")
    
    return found


async def test_pdf_propagation():
    """Testa se conteúdo de PDF chega ao agente"""
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("📄 TESTE: Propagação de PDF para Agente")
    emoji_logger.system_info("="*60)
    
    # Criar contexto enriquecido com PDF processado
    enriched_context = {
        "phone": "11777776666",
        "message": "Recebi a proposta",
        "lead_data": {
            "name": "Carlos Teste",
            "phone": "11777776666"
        },
        "conversation_id": "test_pdf_001",
        "multimodal_result": {
            "type": "document",
            "document_type": "pdf",
            "content": """Extração do documento:
            PROPOSTA COMERCIAL - ENERGIA SOLAR
            Cliente: Carlos Silva
            Endereço: Rua das Flores, 123
            
            Sistema proposto:
            - 10 painéis de 550W
            - Inversor 5kW
            - Geração estimada: 750 kWh/mês
            - Investimento: R$ 25.000,00
            - Economia anual: R$ 4.200,00""",
            "analysis": "Documento identificado como proposta comercial de sistema solar",
            "pages": 2,
            "status": "processed"
        }
    }
    
    # Criar SDR Team
    team = SDRTeam()
    
    # Processar mensagem com contexto enriquecido
    response = await team.process_message_with_context(
        enriched_context
    )
    
    # Verificar se a resposta menciona dados do PDF
    emoji_logger.system_info(f"\n📤 Resposta do agente: {response}")
    
    # Análise
    keywords = ["10 painéis", "550w", "750", "25.000", "4.200", "5kw"]
    found = any(keyword in response.lower() for keyword in keywords)
    
    if found:
        emoji_logger.system_info("✅ SUCESSO: Agente respondeu baseado no conteúdo do PDF!")
    else:
        emoji_logger.system_error("Test Failed", "Agente NÃO usou o conteúdo do PDF na resposta")
    
    return found


async def main():
    """Executa todos os testes de propagação"""
    emoji_logger.system_info("\n" + "🚀 "*20)
    emoji_logger.system_info("TESTE DE PROPAGAÇÃO MULTIMODAL")
    emoji_logger.system_info("Verificando se dados chegam ao agente e são usados nas respostas")
    emoji_logger.system_info("🚀 "*20 + "\n")
    
    results = {
        "audio": False,
        "image": False,
        "pdf": False
    }
    
    try:
        # Testar cada tipo
        results["audio"] = await test_audio_propagation()
        results["image"] = await test_image_propagation()
        results["pdf"] = await test_pdf_propagation()
        
    except Exception as e:
        emoji_logger.system_error("Test Error", f"Erro durante testes: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Resumo final
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("📊 RESUMO DOS TESTES DE PROPAGAÇÃO")
    emoji_logger.system_info("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for media_type, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        emoji_logger.system_info(f"{media_type.upper()}: {status}")
    
    emoji_logger.system_info(f"\nTaxa de Sucesso: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        emoji_logger.system_info("\n🎉 TODOS OS TESTES PASSARAM! Propagação funcionando 100%!")
    else:
        emoji_logger.system_error("Final Result", f"Alguns testes falharam ({total-passed} de {total})")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"propagation_test_results_{timestamp}.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "results": results,
            "passed": passed,
            "total": total,
            "success_rate": f"{passed/total*100:.0f}%"
        }, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())