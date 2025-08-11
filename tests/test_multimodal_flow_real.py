#!/usr/bin/env python3
"""
Test Multimodal Flow Real - Testa o fluxo completo via webhooks
"""

import asyncio
import json
import base64
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.agentic_sdr import AgenticSDR
from app.utils.logger import emoji_logger


async def test_audio_flow_real():
    """Testa fluxo real de áudio como vem do webhook"""
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("🎵 TESTE: Fluxo Real de Áudio (via webhook)")
    emoji_logger.system_info("="*60)
    
    # Carregar arquivo de áudio real
    audio_path = Path("tests/WhatsApp Audio 2025-08-03 at 22.31.42.opus")
    if not audio_path.exists():
        emoji_logger.system_error("Test Setup", f"Arquivo de áudio não encontrado: {audio_path}")
        return False
        
    with open(audio_path, "rb") as f:
        audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Simular estrutura que vem do webhook
    webhook_message = {
        "key": {
            "remoteJid": "5511999998888@s.whatsapp.net",
            "fromMe": False,
            "id": "TEST_AUDIO_001"
        },
        "message": "",  # Mensagem vazia para áudio
        "messageType": "audioMessage",
        "messageTimestamp": 1736132800,
        "pushName": "João Teste Audio",
        "media": {
            "mimetype": "audio/ogg",
            "data": audio_base64,
            "filename": "audio_test.opus"
        }
    }
    
    # Criar AGENTIC SDR
    agno_sdr = AgenticSDR()
    await agno_sdr.initialize()
    
    # Simular dados do lead
    lead_data = {
        "name": "João Teste Audio",
        "phone": "5511999998888",
        "lead_id": "test_lead_audio"
    }
    
    # Processar mensagem completa
    try:
        response = await agno_sdr.process_message(
            phone="5511999998888",
            message="",
            lead_data=lead_data,
            conversation_id="test_audio_conv",
            media=webhook_message.get("media")
        )
        
        emoji_logger.system_info(f"\n📤 Resposta do agente: {response}")
        
        # Extrair texto da resposta (pode ser dict ou string)
        response_text = response.get("text", "") if isinstance(response, dict) else str(response)
        
        # Verificar se a resposta está baseada na transcrição
        # IMPORTANTE: O áudio real diz "bom dia, mas eu não passo CPF por áudio viu"
        # Então vamos verificar palavras relacionadas a CPF/dados pessoais
        keywords = ["cpf", "dados", "segurança", "proteção", "áudio", "e-mail", "email"]
        found = any(keyword in response_text.lower() for keyword in keywords)
        
        if found:
            emoji_logger.system_info("✅ SUCESSO: Agente respondeu baseado na transcrição real!")
        else:
            emoji_logger.system_error("Test Failed", "Agente NÃO usou a transcrição do áudio")
            
        return found
        
    except Exception as e:
        emoji_logger.system_error("Test Error", f"Erro ao processar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_image_flow_real():
    """Testa fluxo real de imagem como vem do webhook"""
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("🖼️ TESTE: Fluxo Real de Imagem (via webhook)")
    emoji_logger.system_info("="*60)
    
    # Carregar imagem real
    image_path = Path("tests/20250715_164305.png")
    if not image_path.exists():
        emoji_logger.system_error("Test Setup", f"Arquivo de imagem não encontrado: {image_path}")
        return False
        
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Simular estrutura que vem do webhook
    webhook_message = {
        "key": {
            "remoteJid": "5511888887777@s.whatsapp.net",
            "fromMe": False,
            "id": "TEST_IMAGE_001"
        },
        "message": "Aqui está minha conta de luz",
        "messageType": "imageMessage",
        "messageTimestamp": 1736132900,
        "pushName": "Maria Teste Imagem",
        "media": {
            "mimetype": "image/png",
            "data": image_base64,
            "filename": "conta_luz.png",
            "caption": "Minha conta de luz"
        }
    }
    
    # Criar AGENTIC SDR
    agno_sdr = AgenticSDR()
    await agno_sdr.initialize()
    
    # Simular dados do lead
    lead_data = {
        "name": "Maria Teste Imagem",
        "phone": "5511888887777",
        "lead_id": "test_lead_image"
    }
    
    # Processar mensagem completa
    try:
        response = await agno_sdr.process_message(
            phone="5511888887777",
            message="Aqui está minha conta de luz",
            lead_data=lead_data,
            conversation_id="test_image_conv",
            media=webhook_message.get("media")
        )
        
        emoji_logger.system_info(f"\n📤 Resposta do agente: {response}")
        
        # Extrair texto da resposta (pode ser dict ou string)
        response_text = response.get("text", "") if isinstance(response, dict) else str(response)
        
        # Verificar se a resposta menciona análise da conta
        keywords = ["conta", "consumo", "kwh", "economia", "análise"]
        found = any(keyword in response_text.lower() for keyword in keywords)
        
        if found:
            emoji_logger.system_info("✅ SUCESSO: Agente respondeu baseado na análise da imagem!")
        else:
            emoji_logger.system_error("Test Failed", "Agente NÃO usou a análise da imagem")
            
        return found
        
    except Exception as e:
        emoji_logger.system_error("Test Error", f"Erro ao processar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_pdf_flow_real():
    """Testa fluxo real de PDF como vem do webhook"""
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("📄 TESTE: Fluxo Real de PDF (via webhook)")
    emoji_logger.system_info("="*60)
    
    # Carregar PDF real
    pdf_path = Path("tests/Boleto.pdf")
    if not pdf_path.exists():
        emoji_logger.system_error("Test Setup", f"Arquivo PDF não encontrado: {pdf_path}")
        return False
        
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    
    # Simular estrutura que vem do webhook
    webhook_message = {
        "key": {
            "remoteJid": "5511777776666@s.whatsapp.net",
            "fromMe": False,
            "id": "TEST_PDF_001"
        },
        "message": "Segue o boleto",
        "messageType": "documentMessage",
        "messageTimestamp": 1736133000,
        "pushName": "Carlos Teste PDF",
        "media": {
            "mimetype": "application/pdf",
            "data": pdf_base64,
            "filename": "boleto.pdf",
            "caption": "Boleto para análise"
        }
    }
    
    # Criar AGENTIC SDR
    agno_sdr = AgenticSDR()
    await agno_sdr.initialize()
    
    # Simular dados do lead
    lead_data = {
        "name": "Carlos Teste PDF",
        "phone": "5511777776666",
        "lead_id": "test_lead_pdf"
    }
    
    # Processar mensagem completa
    try:
        response = await agno_sdr.process_message(
            phone="5511777776666",
            message="Segue o boleto",
            lead_data=lead_data,
            conversation_id="test_pdf_conv",
            media=webhook_message.get("media")
        )
        
        emoji_logger.system_info(f"\n📤 Resposta do agente: {response}")
        
        # Extrair texto da resposta (pode ser dict ou string)
        response_text = response.get("text", "") if isinstance(response, dict) else str(response)
        
        # Verificar se a resposta menciona o documento
        keywords = ["boleto", "documento", "pdf", "análise", "valor"]
        found = any(keyword in response_text.lower() for keyword in keywords)
        
        if found:
            emoji_logger.system_info("✅ SUCESSO: Agente respondeu baseado no conteúdo do PDF!")
        else:
            emoji_logger.system_error("Test Failed", "Agente NÃO usou o conteúdo do PDF")
            
        return found
        
    except Exception as e:
        emoji_logger.system_error("Test Error", f"Erro ao processar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Executa todos os testes de fluxo real"""
    emoji_logger.system_info("\n" + "🚀 "*20)
    emoji_logger.system_info("TESTE DE FLUXO REAL MULTIMODAL")
    emoji_logger.system_info("Simulando exatamente como vem dos webhooks")
    emoji_logger.system_info("🚀 "*20 + "\n")
    
    results = {
        "audio": False,
        "image": False,
        "pdf": False
    }
    
    try:
        # Testar cada tipo
        results["audio"] = await test_audio_flow_real()
        results["image"] = await test_image_flow_real()
        results["pdf"] = await test_pdf_flow_real()
        
    except Exception as e:
        emoji_logger.system_error("Test Error", f"Erro durante testes: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Resumo final
    emoji_logger.system_info("\n" + "="*60)
    emoji_logger.system_info("📊 RESUMO DOS TESTES DE FLUXO REAL")
    emoji_logger.system_info("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for media_type, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        emoji_logger.system_info(f"{media_type.upper()}: {status}")
    
    emoji_logger.system_info(f"\nTaxa de Sucesso: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        emoji_logger.system_info("\n🎉 TODOS OS TESTES PASSARAM! Fluxo real funcionando 100%!")
    else:
        emoji_logger.system_error("Final Result", f"Alguns testes falharam ({total-passed} de {total})")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"flow_real_test_results_{timestamp}.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "results": results,
            "passed": passed,
            "total": total,
            "success_rate": f"{passed/total*100:.0f}%"
        }, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())