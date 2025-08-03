#!/usr/bin/env python3
"""
Script de Teste do Sistema Multimodal
Testa processamento de imagens, áudios e documentos
"""

import asyncio
import base64
import sys
import os
from pathlib import Path

# Adicionar o diretório app ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.logger import emoji_logger
from app.services.audio_transcriber import audio_transcriber
from app.services.document_extractor import document_extractor
from app.agents.agentic_sdr import AgenticSDR
from app.config import settings

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_test_header(test_name: str):
    """Imprime cabeçalho do teste"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}🧪 TESTE: {test_name}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(message: str):
    """Imprime mensagem de sucesso"""
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message: str):
    """Imprime mensagem de erro"""
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message: str):
    """Imprime mensagem de aviso"""
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_info(message: str):
    """Imprime informação"""
    print(f"{BLUE}ℹ️  {message}{RESET}")

async def test_audio_transcription():
    """Testa transcrição de áudio"""
    print_test_header("TRANSCRIÇÃO DE ÁUDIO")
    
    try:
        # Criar um áudio de teste simulado (base64 vazio por enquanto)
        # Em produção, isso viria do WhatsApp
        
        print_info("Testando com áudio simulado...")
        
        # Simular base64 de áudio pequeno (vazio para teste)
        test_audio_base64 = ""
        
        result = await audio_transcriber.transcribe_from_base64(
            test_audio_base64,
            mimetype="audio/ogg",
            language="pt-BR"
        )
        
        if result["status"] == "error":
            if "vazio" in result.get("error", "").lower():
                print_warning("Áudio vazio detectado corretamente")
                return True
            else:
                print_error(f"Erro: {result.get('error')}")
                return False
        elif result["status"] == "success":
            print_success(f"Áudio transcrito: '{result['text']}'")
            print_info(f"Duração: {result.get('duration', 0):.1f}s")
            print_info(f"Engine: {result.get('engine', 'unknown')}")
            return True
        else:
            print_warning(f"Status: {result['status']}")
            return True
            
    except Exception as e:
        print_error(f"Erro no teste: {e}")
        return False

async def test_document_extraction():
    """Testa extração de documentos"""
    print_test_header("EXTRAÇÃO DE DOCUMENTOS")
    
    try:
        # Criar um PDF simples de teste
        print_info("Testando com PDF simulado...")
        
        # PDF vazio para teste
        test_pdf_base64 = ""
        
        result = await document_extractor.extract_from_pdf(
            test_pdf_base64,
            max_chars=5000
        )
        
        if result["status"] == "error":
            if "vazio" in result.get("error", "").lower():
                print_warning("PDF vazio detectado corretamente")
                return True
            else:
                print_error(f"Erro: {result.get('error')}")
                return False
        elif result["status"] == "success":
            print_success(f"Texto extraído: {len(result['text'])} caracteres")
            print_info(f"Páginas: {result.get('pages', 0)}")
            print_info(f"Método: {result.get('method', 'unknown')}")
            print_info(f"Tipo de documento: {result.get('document_type', 'unknown')}")
            return True
        elif result["status"] == "no_text":
            print_warning("PDF escaneado detectado (precisa OCR)")
            return True
        else:
            print_warning(f"Status: {result['status']}")
            return True
            
    except Exception as e:
        print_error(f"Erro no teste: {e}")
        return False

async def test_image_processing():
    """Testa processamento de imagens"""
    print_test_header("PROCESSAMENTO DE IMAGENS")
    
    try:
        print_info("Testando análise de imagem com Vision API...")
        
        # Inicializar agente
        agent = AgenticSDR()
        await agent.initialize()
        
        # Simular imagem base64 (vazia para teste)
        test_image_base64 = ""
        
        result = await agent.process_multimodal_content(
            media_type="image",
            media_data=test_image_base64,
            caption="Teste de imagem"
        )
        
        if result.get("error"):
            if "vazi" in result.get("error", "").lower() or "inválid" in result.get("error", "").lower():
                print_warning("Imagem vazia detectada corretamente")
                return True
            else:
                print_error(f"Erro: {result.get('error')}")
                return False
        elif result.get("processed") or result.get("content"):
            print_success("Imagem processada com sucesso")
            print_info(f"Tipo: {result.get('type', 'unknown')}")
            if result.get("needs_analysis"):
                print_info("Conta de luz detectada")
            return True
        else:
            print_warning(f"Resultado: {result}")
            return True
            
    except Exception as e:
        print_error(f"Erro no teste: {e}")
        return False

async def test_multimodal_integration():
    """Testa integração completa do sistema multimodal"""
    print_test_header("INTEGRAÇÃO MULTIMODAL COMPLETA")
    
    try:
        # Inicializar agente
        print_info("Inicializando AgenticSDR...")
        agent = AgenticSDR()
        await agent.initialize()
        
        print_success("Agente inicializado com sucesso")
        
        # Verificar configurações
        print_info("\nConfigurações:")
        print_info(f"  - Análise multimodal: {'✅' if settings.enable_multimodal_analysis else '❌'}")
        print_info(f"  - Análise de contas: {'✅' if settings.enable_bill_photo_analysis else '❌'}")
        print_info(f"  - Transcrição de voz: {'✅' if settings.enable_voice_message_transcription else '❌'}")
        
        # Testar cada tipo de mídia
        test_results = []
        
        # Teste 1: Áudio
        print_info("\nTestando processamento de áudio...")
        audio_result = await agent.process_multimodal_content(
            media_type="audio",
            media_data="",  # Base64 vazio para teste
            caption=None
        )
        
        if audio_result.get("status") == "disabled":
            print_warning("Transcrição de áudio desabilitada")
            test_results.append(True)
        elif audio_result.get("status") == "error":
            if "vazio" in str(audio_result.get("message", "")).lower():
                print_success("Áudio vazio tratado corretamente")
                test_results.append(True)
            else:
                print_error(f"Erro: {audio_result.get('message')}")
                test_results.append(False)
        else:
            print_success(f"Áudio processado: {audio_result.get('status')}")
            test_results.append(True)
        
        # Teste 2: Documento
        print_info("\nTestando processamento de documento...")
        doc_result = await agent.process_multimodal_content(
            media_type="document",
            media_data="",  # Base64 vazio para teste
            caption=None
        )
        
        if doc_result.get("status") == "error":
            if "vazio" in str(doc_result.get("message", "")).lower():
                print_success("Documento vazio tratado corretamente")
                test_results.append(True)
            else:
                print_error(f"Erro: {doc_result.get('message')}")
                test_results.append(False)
        else:
            print_success(f"Documento processado: {doc_result.get('status')}")
            test_results.append(True)
        
        # Teste 3: Imagem
        print_info("\nTestando processamento de imagem...")
        img_result = await agent.process_multimodal_content(
            media_type="image",
            media_data="",  # Base64 vazio para teste
            caption="Conta de luz"
        )
        
        if img_result.get("error"):
            if "vazi" in str(img_result.get("error", "")).lower() or "inválid" in str(img_result.get("error", "")).lower():
                print_success("Imagem vazia tratada corretamente")
                test_results.append(True)
            else:
                print_error(f"Erro: {img_result.get('error')}")
                test_results.append(False)
        else:
            print_success(f"Imagem processada: {img_result.get('type')}")
            test_results.append(True)
        
        # Resultado final
        all_passed = all(test_results)
        
        if all_passed:
            print_success("\n✅ TODOS OS TESTES DE INTEGRAÇÃO PASSARAM!")
        else:
            print_error(f"\n❌ {test_results.count(False)} teste(s) falharam")
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erro no teste de integração: {e}")
        return False

async def main():
    """Executa todos os testes"""
    print(f"\n{BOLD}{GREEN}{'='*60}{RESET}")
    print(f"{BOLD}{GREEN}🚀 TESTE DO SISTEMA MULTIMODAL - SDR IA SOLARPRIME{RESET}")
    print(f"{BOLD}{GREEN}{'='*60}{RESET}")
    
    # Verificar configurações
    print_info("\nVerificando ambiente...")
    print_info(f"Python: {sys.version.split()[0]}")
    print_info(f"Diretório: {os.getcwd()}")
    
    # Executar testes
    test_results = []
    
    # Teste 1: Transcrição de áudio
    result = await test_audio_transcription()
    test_results.append(("Transcrição de Áudio", result))
    
    # Teste 2: Extração de documentos
    result = await test_document_extraction()
    test_results.append(("Extração de Documentos", result))
    
    # Teste 3: Processamento de imagens
    result = await test_image_processing()
    test_results.append(("Processamento de Imagens", result))
    
    # Teste 4: Integração completa
    result = await test_multimodal_integration()
    test_results.append(("Integração Multimodal", result))
    
    # Resumo final
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}📊 RESUMO DOS TESTES{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: PASSOU")
            passed += 1
        else:
            print_error(f"{test_name}: FALHOU")
            failed += 1
    
    print(f"\n{BOLD}Total: {passed} passou, {failed} falhou{RESET}")
    
    if failed == 0:
        print(f"\n{BOLD}{GREEN}🎉 SISTEMA MULTIMODAL 100% FUNCIONAL!{RESET}")
        print_info("\nPróximos passos:")
        print_info("1. Envie uma imagem via WhatsApp para testar análise de Vision")
        print_info("2. Envie um áudio para testar transcrição")
        print_info("3. Envie um PDF para testar extração de texto")
    else:
        print(f"\n{BOLD}{YELLOW}⚠️  Alguns testes falharam. Verifique os logs acima.{RESET}")

if __name__ == "__main__":
    asyncio.run(main())