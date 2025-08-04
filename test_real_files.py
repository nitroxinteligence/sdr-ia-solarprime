#!/usr/bin/env python3
"""
Teste com Arquivos Reais do Sistema Multimodal AGNO
Testa com imagem PNG, PDF e áudio OPUS reais
"""

import asyncio
import base64
from pathlib import Path
from datetime import datetime
import json

# Configurar ambiente
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Arquivo .env carregado: {env_path}")

from app.agents.agentic_sdr import AgenticSDR
from app.utils.logger import emoji_logger


class RealFilesTester:
    """Testador com arquivos reais"""
    
    def __init__(self):
        self.sdr = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "files_tested": [],
            "results": {}
        }
    
    async def setup(self):
        """Inicializa o AgenticSDR"""
        print("\n🔧 INICIALIZANDO SISTEMA...")
        print("=" * 80)
        
        try:
            self.sdr = AgenticSDR()
            print("✅ AgenticSDR inicializado com sucesso!")
            
            # Verificar componentes
            if hasattr(self.sdr, 'agno_media_detector'):
                print("✅ Detector de mídia disponível")
            
            if self.sdr.multimodal_enabled:
                print("✅ Sistema multimodal habilitado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    async def test_real_image(self):
        """Testa com a imagem PNG real"""
        print("\n🖼️ TESTE 1: IMAGEM PNG REAL")
        print("-" * 40)
        
        image_path = Path("20250715_164305.png")
        
        if not image_path.exists():
            print(f"❌ Arquivo não encontrado: {image_path}")
            return
        
        try:
            # Ler arquivo
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            print(f"📸 Arquivo: {image_path.name}")
            print(f"📊 Tamanho: {len(image_bytes):,} bytes ({len(image_bytes)/1024:.1f} KB)")
            
            # Verificar formato com detector
            detection = self.sdr.agno_media_detector.detect_media_type(image_bytes[:100])
            print(f"🔍 Formato detectado: {detection.get('format', 'unknown')}")
            
            # Codificar em base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Processar com AgenticSDR
            print("🔄 Processando com AGNO Framework...")
            result = await self.sdr.process_multimodal_content(
                media_type="image",
                media_data=image_base64,
                caption="Imagem de pessoa com roupa roxa"
            )
            
            # Avaliar resultado
            if result.get("status") == "success":
                print("✅ Processamento bem-sucedido!")
                
                # Mostrar análise
                analysis = result.get("analysis", {})
                if isinstance(analysis, dict):
                    content = analysis.get("content", "")
                else:
                    content = str(analysis)
                
                print(f"📝 Análise da imagem:")
                print(f"   {content[:200]}..." if len(content) > 200 else f"   {content}")
                
                self.results["results"]["image"] = {
                    "status": "success",
                    "file": image_path.name,
                    "size": len(image_bytes),
                    "format": detection.get('format'),
                    "analysis_preview": content[:200]
                }
            else:
                print(f"❌ Erro: {result.get('message', 'Erro desconhecido')}")
                self.results["results"]["image"] = {
                    "status": "error",
                    "error": result.get('message')
                }
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            self.results["results"]["image"] = {
                "status": "exception",
                "error": str(e)
            }
    
    async def test_real_pdf(self):
        """Testa com o PDF real (Boleto)"""
        print("\n📄 TESTE 2: PDF REAL (BOLETO)")
        print("-" * 40)
        
        pdf_path = Path("Boleto.pdf")
        
        if not pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            return
        
        try:
            # Ler arquivo
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            
            print(f"📄 Arquivo: {pdf_path.name}")
            print(f"📊 Tamanho: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
            
            # Verificar formato com detector
            detection = self.sdr.agno_media_detector.detect_media_type(pdf_bytes[:100])
            print(f"🔍 Formato detectado: {detection.get('format', 'unknown')}")
            
            # Codificar em base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Processar com AgenticSDR
            print("🔄 Processando com AGNO Framework...")
            result = await self.sdr.process_multimodal_content(
                media_type="pdf",
                media_data=pdf_base64,
                caption="Boleto bancário"
            )
            
            # Avaliar resultado
            if result.get("status") in ["success", "partial"]:
                print("✅ Processamento realizado!")
                
                content = result.get("content", "")
                if content:
                    print(f"📝 Conteúdo extraído:")
                    print(f"   {content[:300]}..." if len(content) > 300 else f"   {content}")
                
                # Verificar se detectou informações do boleto
                content_lower = content.lower() if content else ""
                if any(word in content_lower for word in ["boleto", "pagamento", "vencimento", "valor"]):
                    print("✅ Informações de boleto detectadas!")
                
                self.results["results"]["pdf"] = {
                    "status": "success",
                    "file": pdf_path.name,
                    "size": len(pdf_bytes),
                    "format": detection.get('format'),
                    "content_preview": content[:300] if content else "N/A"
                }
            else:
                print(f"⚠️ Aviso: {result.get('message', 'Processamento limitado')}")
                self.results["results"]["pdf"] = {
                    "status": "warning",
                    "message": result.get('message')
                }
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            self.results["results"]["pdf"] = {
                "status": "exception",
                "error": str(e)
            }
    
    async def test_real_audio(self):
        """Testa com o áudio OPUS real do WhatsApp"""
        print("\n🎵 TESTE 3: ÁUDIO OPUS REAL (WHATSAPP)")
        print("-" * 40)
        
        audio_path = Path("WhatsApp Audio 2025-08-03 at 22.31.42.opus")
        
        if not audio_path.exists():
            print(f"❌ Arquivo não encontrado: {audio_path}")
            return
        
        try:
            # Ler arquivo
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            
            print(f"🎤 Arquivo: {audio_path.name}")
            print(f"📊 Tamanho: {len(audio_bytes):,} bytes ({len(audio_bytes)/1024:.1f} KB)")
            
            # Verificar formato com detector
            detection = self.sdr.agno_media_detector.detect_media_type(audio_bytes[:100])
            print(f"🔍 Formato detectado: {detection.get('format', 'unknown')}")
            
            # Codificar em base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Processar com AgenticSDR
            print("🔄 Processando com AGNO Framework...")
            result = await self.sdr.process_multimodal_content(
                media_type="audio",
                media_data=audio_base64,
                caption="Áudio do WhatsApp"
            )
            
            # Avaliar resultado
            if result.get("status") == "success":
                print("✅ Transcrição bem-sucedida!")
                
                transcription = result.get("transcription", "")
                if transcription and transcription != "[Áudio não compreendido]":
                    print(f"📝 Transcrição:")
                    print(f"   \"{transcription}\"")
                else:
                    print("⚠️ Áudio processado mas não transcrito claramente")
                
                self.results["results"]["audio"] = {
                    "status": "success",
                    "file": audio_path.name,
                    "size": len(audio_bytes),
                    "format": "opus",
                    "transcription": transcription
                }
                
            elif result.get("status") == "unclear":
                print("⚠️ Áudio processado mas não compreendido")
                self.results["results"]["audio"] = {
                    "status": "unclear",
                    "message": result.get("message")
                }
                
            else:
                print(f"❌ Erro: {result.get('message', 'Erro desconhecido')}")
                self.results["results"]["audio"] = {
                    "status": "error",
                    "error": result.get('message')
                }
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            self.results["results"]["audio"] = {
                "status": "exception",
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """Executa todos os testes com arquivos reais"""
        print("\n🚀 TESTE COM ARQUIVOS REAIS - SISTEMA MULTIMODAL AGNO")
        print("=" * 80)
        
        # Setup
        if not await self.setup():
            print("❌ Falha na inicialização. Abortando testes.")
            return self.results
        
        # Executar testes
        await self.test_real_image()
        await self.test_real_pdf()
        await self.test_real_audio()
        
        # Relatório final
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - ARQUIVOS REAIS")
        print("=" * 80)
        
        # Análise dos resultados
        total_tests = len(self.results["results"])
        successful = sum(1 for r in self.results["results"].values() 
                        if r.get("status") in ["success", "partial"])
        
        success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Taxa de Sucesso: {success_rate:.1f}%")
        print(f"✅ Testes Bem-sucedidos: {successful}/{total_tests}")
        
        # Detalhes por arquivo
        print("\n📋 Resultados por Arquivo:")
        for test_type, result in self.results["results"].items():
            status = result.get("status", "unknown")
            icon = {
                "success": "✅",
                "partial": "⚠️",
                "warning": "⚠️",
                "unclear": "🔍",
                "error": "❌",
                "exception": "💥"
            }.get(status, "❓")
            
            print(f"\n  {icon} {test_type.upper()}:")
            if "file" in result:
                print(f"     Arquivo: {result['file']}")
            if "size" in result:
                print(f"     Tamanho: {result['size']:,} bytes")
            if "format" in result:
                print(f"     Formato: {result['format']}")
            print(f"     Status: {status}")
            
            if status == "success":
                if test_type == "audio" and "transcription" in result:
                    print(f"     Transcrição: {result['transcription'][:100]}...")
                elif test_type == "image" and "analysis_preview" in result:
                    print(f"     Análise: {result['analysis_preview'][:100]}...")
                elif test_type == "pdf" and "content_preview" in result:
                    print(f"     Conteúdo: {result['content_preview'][:100]}...")
        
        # Salvar resultados
        results_file = Path("real_files_test_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados detalhados salvos em: {results_file}")
        
        # Conclusão
        print("\n" + "=" * 80)
        if success_rate >= 66:
            print("🎉 SISTEMA MULTIMODAL VALIDADO COM ARQUIVOS REAIS!")
        else:
            print("⚠️ SISTEMA PRECISA DE AJUSTES PARA ARQUIVOS REAIS")
        
        return self.results


async def main():
    """Função principal"""
    tester = RealFilesTester()
    results = await tester.run_all_tests()
    
    # Código de saída baseado no sucesso
    successful = sum(1 for r in results["results"].values() 
                    if r.get("status") in ["success", "partial"])
    exit_code = 0 if successful >= 2 else 1
    
    print(f"\n🏁 Teste finalizado. Código de saída: {exit_code}")
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)