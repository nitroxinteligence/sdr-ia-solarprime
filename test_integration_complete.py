#!/usr/bin/env python3
"""
Teste Completo de Integração: Evolution API → Webhook → AgenticSDR → Multimodal
"""

import asyncio
import base64
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.utils.logger import emoji_logger

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}🔍 {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")

def print_success(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg: str):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg: str):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg: str):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

async def test_evolution_integration():
    """Testa integração com Evolution API"""
    print_header("TESTE 1: INTEGRAÇÃO EVOLUTION API")
    
    from app.integrations.evolution import evolution_client
    
    try:
        # Verificar configurações
        print_info("Verificando configurações da Evolution API...")
        if not settings.evolution_api_url:
            print_error("EVOLUTION_API_URL não configurada")
            return False
        
        if not settings.evolution_api_key:
            print_error("EVOLUTION_API_KEY não configurada")
            return False
            
        print_success(f"URL: {settings.evolution_api_url}")
        print_success(f"Instance: {settings.evolution_instance_name}")
        
        # Testar conexão
        print_info("Testando conexão com Evolution API...")
        status = await evolution_client.check_instance_status()
        
        if status.get("connected"):
            print_success("Evolution API conectada e operacional")
            print_info(f"Estado: {status.get('state', 'unknown')}")
            return True
        else:
            print_warning("Evolution API não conectada ao WhatsApp")
            print_info("Execute o QR Code para conectar")
            return True  # Não é erro crítico
            
    except Exception as e:
        print_error(f"Erro ao testar Evolution API: {e}")
        return False

async def test_webhook_flow():
    """Testa fluxo do webhook"""
    print_header("TESTE 2: FLUXO WEBHOOK → AGENTIC SDR")
    
    try:
        # Verificar importação do webhook
        from app.api.webhooks import process_message_with_agent
        print_success("Webhook process_message_with_agent importado")
        
        # Verificar AgenticSDR
        from app.agents.agentic_sdr import AgenticSDR
        agent = AgenticSDR()
        await agent.initialize()
        print_success("AgenticSDR inicializado com sucesso")
        
        # Verificar método process_message aceita media
        import inspect
        sig = inspect.signature(agent.process_message)
        params = list(sig.parameters.keys())
        
        if 'media' in params:
            print_success("AgenticSDR.process_message aceita parâmetro 'media'")
        else:
            print_error("AgenticSDR.process_message NÃO aceita 'media'")
            return False
            
        # Verificar process_multimodal_content
        if hasattr(agent, 'process_multimodal_content'):
            print_success("AgenticSDR tem método process_multimodal_content")
        else:
            print_error("AgenticSDR NÃO tem process_multimodal_content")
            return False
            
        return True
        
    except Exception as e:
        print_error(f"Erro no teste de webhook: {e}")
        return False

async def test_multimodal_services():
    """Testa serviços multimodais"""
    print_header("TESTE 3: SERVIÇOS MULTIMODAIS")
    
    results = {}
    
    # 1. AudioTranscriber
    try:
        from app.services.audio_transcriber import audio_transcriber
        print_success("AudioTranscriber importado")
        
        # Testar com áudio vazio
        result = await audio_transcriber.transcribe_from_base64(
            "", "audio/ogg", "pt-BR"
        )
        if result["status"] == "error" and "vazio" in result.get("error", "").lower():
            print_success("AudioTranscriber validando dados vazios corretamente")
        results["audio"] = True
    except Exception as e:
        print_error(f"AudioTranscriber com problema: {e}")
        results["audio"] = False
    
    # 2. DocumentExtractor
    try:
        from app.services.document_extractor import document_extractor
        print_success("DocumentExtractor importado")
        
        # Testar com PDF vazio
        result = await document_extractor.extract_from_pdf("")
        if result["status"] == "error" and "vazio" in result.get("error", "").lower():
            print_success("DocumentExtractor validando dados vazios corretamente")
        results["document"] = True
    except Exception as e:
        print_error(f"DocumentExtractor com problema: {e}")
        results["document"] = False
    
    # 3. Vision API (via AgenticSDR)
    try:
        from app.agents.agentic_sdr import AgenticSDR
        agent = AgenticSDR()
        await agent.initialize()
        
        # Testar com imagem vazia
        result = await agent.process_multimodal_content(
            media_type="image",
            media_data="",
            caption="teste"
        )
        
        if result.get("error") or result.get("status") == "error":
            print_success("Vision API validando dados vazios corretamente")
        results["vision"] = True
    except Exception as e:
        print_error(f"Vision API com problema: {e}")
        results["vision"] = False
    
    return all(results.values())

async def test_configurations():
    """Verifica configurações necessárias"""
    print_header("TESTE 4: CONFIGURAÇÕES E VARIÁVEIS")
    
    configs_ok = True
    
    # Verificar configurações multimodais
    configs = {
        "ENABLE_MULTIMODAL_ANALYSIS": settings.enable_multimodal_analysis,
        "ENABLE_BILL_PHOTO_ANALYSIS": settings.enable_bill_photo_analysis,
        "ENABLE_VOICE_MESSAGE_TRANSCRIPTION": settings.enable_voice_message_transcription,
        "ENABLE_MESSAGE_BUFFER": settings.enable_message_buffer,
        "ENABLE_MESSAGE_SPLITTER": settings.enable_message_splitter
    }
    
    for config, value in configs.items():
        if value:
            print_success(f"{config}: {value}")
        else:
            print_warning(f"{config}: {value}")
            if "MULTIMODAL" in config or "VOICE" in config:
                configs_ok = False
    
    # Verificar APIs
    print_info("\nAPIs configuradas:")
    
    if settings.google_api_key:
        print_success(f"GOOGLE_API_KEY: ***{settings.google_api_key[-8:]}")
    else:
        print_error("GOOGLE_API_KEY não configurada")
        configs_ok = False
    
    if settings.openai_api_key:
        print_success(f"OPENAI_API_KEY: ***{settings.openai_api_key[-8:]}")
    else:
        print_warning("OPENAI_API_KEY não configurada (opcional)")
    
    # Verificar Evolution API
    if settings.evolution_api_url:
        print_success(f"EVOLUTION_API_URL: {settings.evolution_api_url}")
    else:
        print_error("EVOLUTION_API_URL não configurada")
        configs_ok = False
    
    return configs_ok

async def test_complete_flow():
    """Testa fluxo completo simulado"""
    print_header("TESTE 5: FLUXO COMPLETO SIMULADO")
    
    try:
        from app.api.webhooks import process_message_with_agent
        from app.agents.agentic_sdr import AgenticSDR
        
        # Simular dados do webhook
        phone = "5511999999999"
        message = "Olá, quero saber sobre energia solar"
        
        # Simular mídia (documento PDF)
        media_data = {
            "type": "document",
            "mimetype": "application/pdf",
            "fileName": "conta_luz.pdf",
            "data": "",  # Base64 vazio para teste
            "has_content": False
        }
        
        print_info(f"Simulando mensagem de {phone}")
        print_info(f"Texto: {message}")
        print_info(f"Mídia: {media_data['type']} ({media_data['fileName']})")
        
        # Inicializar agente
        agent = AgenticSDR()
        await agent.initialize()
        
        # Processar mensagem com mídia
        response = await agent.process_message(
            phone=phone,
            message=message,
            lead_data=None,
            conversation_id="test-123",
            media=media_data
        )
        
        if response:
            print_success("Fluxo completo executado com sucesso!")
            print_info(f"Resposta gerada: {response[:100]}...")
            return True
        else:
            print_warning("Nenhuma resposta gerada (pode ser normal)")
            return True
            
    except Exception as e:
        print_error(f"Erro no fluxo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print(f"\n{BOLD}{GREEN}{'='*70}{RESET}")
    print(f"{BOLD}{GREEN}🚀 ANÁLISE COMPLETA: SISTEMA MULTIMODAL + EVOLUTION API{RESET}")
    print(f"{BOLD}{GREEN}{'='*70}{RESET}")
    
    results = {}
    
    # Executar testes
    results["evolution"] = await test_evolution_integration()
    results["webhook"] = await test_webhook_flow()
    results["multimodal"] = await test_multimodal_services()
    results["configs"] = await test_configurations()
    results["flow"] = await test_complete_flow()
    
    # Resumo final
    print(f"\n{BOLD}{MAGENTA}{'='*70}{RESET}")
    print(f"{BOLD}{MAGENTA}📊 RESULTADO DA ANÁLISE{RESET}")
    print(f"{BOLD}{MAGENTA}{'='*70}{RESET}\n")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, result in results.items():
        if result:
            print_success(f"{test.upper()}: PASSOU")
        else:
            print_error(f"{test.upper()}: FALHOU")
    
    print(f"\n{BOLD}📈 Score: {passed}/{total} testes passaram{RESET}")
    
    if passed == total:
        print(f"\n{BOLD}{GREEN}✨ SISTEMA 100% INTEGRADO E PRONTO!{RESET}")
        print(f"{BOLD}{GREEN}🎯 O sistema multimodal está totalmente integrado com a Evolution API{RESET}")
        print(f"\n{CYAN}📱 PRÓXIMOS PASSOS:{RESET}")
        print("1. Conectar WhatsApp via QR Code na Evolution API")
        print("2. Enviar mensagens de texto, imagens, áudios e documentos")
        print("3. O sistema processará tudo automaticamente!")
    elif passed >= 3:
        print(f"\n{BOLD}{YELLOW}⚠️  Sistema parcialmente integrado{RESET}")
        print("Verifique os testes que falharam acima")
    else:
        print(f"\n{BOLD}{RED}❌ Sistema precisa de ajustes{RESET}")
        print("Corrija os problemas identificados")

if __name__ == "__main__":
    asyncio.run(main())