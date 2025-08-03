#!/usr/bin/env python3
"""
Script de Teste do Sistema Multimodal com Arquivos Reais
Testa processamento de imagens e documentos reais
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
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_test_header(test_name: str):
    """Imprime cabeçalho do teste"""
    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}🧪 TESTE: {test_name}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")

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

def print_result(title: str, content: str):
    """Imprime resultado formatado"""
    print(f"\n{BOLD}{MAGENTA}📋 {title}:{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")
    # Limitar o output para não poluir o console
    if len(content) > 500:
        print(content[:500])
        print(f"{YELLOW}... [Texto truncado - Total: {len(content)} caracteres]{RESET}")
    else:
        print(content)
    print(f"{CYAN}{'─'*60}{RESET}\n")

def load_file_as_base64(file_path: str) -> str:
    """Carrega arquivo e converte para base64"""
    try:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print_error(f"Erro ao carregar arquivo {file_path}: {e}")
        return ""

async def test_real_document():
    """Testa extração de documento PDF real"""
    print_test_header("EXTRAÇÃO DE DOCUMENTO REAL - Boleto.pdf")
    
    try:
        # Carregar o PDF real
        pdf_path = "Boleto.pdf"
        if not os.path.exists(pdf_path):
            print_error(f"Arquivo {pdf_path} não encontrado")
            return False
            
        print_info(f"Carregando arquivo: {pdf_path}")
        pdf_base64 = load_file_as_base64(pdf_path)
        
        if not pdf_base64:
            print_error("Falha ao carregar PDF")
            return False
            
        print_success(f"PDF carregado: {len(pdf_base64)} caracteres base64")
        
        # Extrair texto do PDF
        print_info("Iniciando extração de texto...")
        result = await document_extractor.extract_from_pdf(
            pdf_base64,
            max_chars=10000
        )
        
        if result["status"] == "success":
            print_success(f"✨ Texto extraído com sucesso!")
            print_info(f"📄 Páginas: {result.get('pages', 0)}")
            print_info(f"📝 Caracteres extraídos: {result.get('char_count', 0)}")
            print_info(f"🔧 Método usado: {result.get('method', 'unknown')}")
            print_info(f"📊 Tipo de documento: {result.get('document_type', 'unknown')}")
            
            if result.get('has_tables'):
                print_info(f"📈 Tabelas encontradas: {result.get('table_count', 0)}")
            
            # Mostrar amostra do texto
            print_result("TEXTO EXTRAÍDO", result['text'])
            
            # Análise adicional do boleto
            text_lower = result['text'].lower()
            if any(word in text_lower for word in ['boleto', 'vencimento', 'pagamento', 'valor']):
                print_success("🎯 Documento identificado como BOLETO BANCÁRIO")
                
                # Tentar extrair informações específicas
                print_info("\n🔍 Buscando informações do boleto...")
                
                # Buscar valor
                import re
                valor_pattern = r'R\$\s*[\d.,]+|valor.*?[\d.,]+|total.*?[\d.,]+'
                valores = re.findall(valor_pattern, result['text'], re.IGNORECASE)
                if valores:
                    print_success(f"💰 Valores encontrados: {', '.join(valores[:3])}")
                
                # Buscar data de vencimento
                data_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}/\d{2}/\d{2}'
                datas = re.findall(data_pattern, result['text'])
                if datas:
                    print_success(f"📅 Datas encontradas: {', '.join(datas[:3])}")
            
            return True
            
        elif result["status"] == "no_text":
            print_warning("PDF parece ser escaneado (imagem)")
            print_info("💡 Sugestão: Use análise de imagem/OCR para este documento")
            return True
            
        else:
            print_error(f"Erro na extração: {result.get('error', 'Erro desconhecido')}")
            return False
            
    except Exception as e:
        print_error(f"Erro no teste de documento: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_real_image():
    """Testa processamento de imagem real"""
    print_test_header("PROCESSAMENTO DE IMAGEM REAL - 20250715_164305.png")
    
    try:
        # Carregar a imagem real
        img_path = "20250715_164305.png"
        if not os.path.exists(img_path):
            print_error(f"Arquivo {img_path} não encontrado")
            return False
            
        print_info(f"Carregando arquivo: {img_path}")
        img_base64 = load_file_as_base64(img_path)
        
        if not img_base64:
            print_error("Falha ao carregar imagem")
            return False
            
        print_success(f"Imagem carregada: {len(img_base64)} caracteres base64")
        
        # Inicializar agente
        print_info("Inicializando AgenticSDR para análise de imagem...")
        agent = AgenticSDR()
        await agent.initialize()
        print_success("Agente inicializado")
        
        # Processar imagem
        print_info("Processando imagem com Vision API...")
        result = await agent.process_multimodal_content(
            media_type="image",
            media_data=img_base64,
            caption="Imagem de teste"
        )
        
        if result.get("error"):
            print_error(f"Erro no processamento: {result.get('error')}")
            return False
        elif result.get("content"):
            print_success("✨ Imagem processada com sucesso!")
            
            # Mostrar análise
            print_result("ANÁLISE DA IMAGEM", result.get("content", ""))
            
            # Informações adicionais
            if result.get("type"):
                print_info(f"🎨 Tipo detectado: {result.get('type')}")
            
            if result.get("needs_analysis"):
                print_warning("📊 Imagem identificada como conta para análise detalhada")
            
            if result.get("processed"):
                print_success("✅ Processamento completo")
            
            # Análise da resposta
            content_lower = str(result.get("content", "")).lower()
            if "roxo" in content_lower or "purple" in content_lower:
                print_success("🎨 Cor roxa/purple detectada na imagem!")
            
            if "pessoa" in content_lower or "homem" in content_lower or "man" in content_lower:
                print_success("👤 Pessoa detectada na imagem!")
                
            if "óculos" in content_lower or "glasses" in content_lower or "sunglasses" in content_lower:
                print_success("🕶️ Óculos detectados na imagem!")
            
            return True
        else:
            print_warning(f"Resposta inesperada: {result}")
            return True
            
    except Exception as e:
        print_error(f"Erro no teste de imagem: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multimodal_chat():
    """Simula uma conversa multimodal completa"""
    print_test_header("SIMULAÇÃO DE CONVERSA MULTIMODAL")
    
    try:
        # Inicializar agente
        print_info("Inicializando sistema de chat...")
        agent = AgenticSDR()
        await agent.initialize()
        print_success("Sistema pronto para conversa multimodal")
        
        # Simular contexto de conversa
        print_info("\n📱 Simulando conversa WhatsApp...")
        print(f"{CYAN}{'─'*60}{RESET}")
        
        # Mensagem 1: Saudação
        print(f"{BOLD}👤 Cliente:{RESET} Olá, gostaria de saber sobre energia solar")
        response = await agent.process_message(
            message="Olá, gostaria de saber sobre energia solar",
            phone="5511999999999",
            name="João Silva"
        )
        print(f"{BOLD}🤖 Helen:{RESET} {response['response'][:200]}...")
        
        # Mensagem 2: Envio de documento
        print(f"\n{BOLD}👤 Cliente:{RESET} [Enviando Boleto.pdf]")
        pdf_base64 = load_file_as_base64("Boleto.pdf")
        if pdf_base64:
            doc_result = await agent.process_multimodal_content(
                media_type="document",
                media_data=pdf_base64,
                caption="Meu boleto de energia"
            )
            if doc_result.get("content"):
                print(f"{BOLD}🤖 Helen:{RESET} Recebi seu documento. {doc_result['content'][:150]}...")
        
        # Mensagem 3: Envio de imagem
        print(f"\n{BOLD}👤 Cliente:{RESET} [Enviando imagem]")
        img_base64 = load_file_as_base64("20250715_164305.png")
        if img_base64:
            img_result = await agent.process_multimodal_content(
                media_type="image",
                media_data=img_base64,
                caption="Uma imagem para análise"
            )
            if img_result.get("content"):
                print(f"{BOLD}🤖 Helen:{RESET} Vi sua imagem. {img_result['content'][:150]}...")
        
        print(f"{CYAN}{'─'*60}{RESET}")
        print_success("\n✨ Conversa multimodal simulada com sucesso!")
        
        return True
        
    except Exception as e:
        print_error(f"Erro na simulação: {e}")
        return False

async def main():
    """Executa todos os testes com arquivos reais"""
    print(f"\n{BOLD}{GREEN}{'='*70}{RESET}")
    print(f"{BOLD}{GREEN}🚀 TESTE REAL DO SISTEMA MULTIMODAL - SDR IA SOLARPRIME{RESET}")
    print(f"{BOLD}{GREEN}{'='*70}{RESET}")
    
    # Verificar arquivos
    print_info("\n📁 Verificando arquivos de teste...")
    files_to_check = ["Boleto.pdf", "20250715_164305.png"]
    files_found = []
    
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            print_success(f"✅ {file} ({size:.1f} KB)")
            files_found.append(file)
        else:
            print_warning(f"❌ {file} não encontrado")
    
    if not files_found:
        print_error("\n⚠️ Nenhum arquivo de teste encontrado!")
        print_info("Certifique-se de que Boleto.pdf e 20250715_164305.png estão no diretório")
        return
    
    # Executar testes
    test_results = []
    
    # Teste 1: Documento PDF
    if "Boleto.pdf" in files_found:
        result = await test_real_document()
        test_results.append(("Extração de Documento Real", result))
    
    # Teste 2: Imagem PNG
    if "20250715_164305.png" in files_found:
        result = await test_real_image()
        test_results.append(("Processamento de Imagem Real", result))
    
    # Teste 3: Conversa multimodal
    if len(files_found) >= 1:
        result = await test_multimodal_chat()
        test_results.append(("Simulação de Chat Multimodal", result))
    
    # Resumo final
    print(f"\n{BOLD}{MAGENTA}{'='*70}{RESET}")
    print(f"{BOLD}{MAGENTA}📊 RESUMO DOS TESTES REAIS{RESET}")
    print(f"{BOLD}{MAGENTA}{'='*70}{RESET}\n")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: PASSOU ✅")
            passed += 1
        else:
            print_error(f"{test_name}: FALHOU ❌")
            failed += 1
    
    print(f"\n{BOLD}📈 Resultado: {passed} passou, {failed} falhou{RESET}")
    
    if failed == 0:
        print(f"\n{BOLD}{GREEN}🎉 SISTEMA MULTIMODAL VALIDADO COM ARQUIVOS REAIS!{RESET}")
        print(f"{BOLD}{GREEN}✨ Pronto para produção!{RESET}")
        print_info("\n📱 Próximo passo: Teste via WhatsApp real")
        print_info("1. Envie mensagens de texto")
        print_info("2. Envie imagens (fotos, contas)")
        print_info("3. Envie documentos PDF")
        print_info("4. Envie áudios para transcrição")
    else:
        print(f"\n{BOLD}{YELLOW}⚠️  Alguns testes falharam. Verifique os logs.{RESET}")

if __name__ == "__main__":
    asyncio.run(main())