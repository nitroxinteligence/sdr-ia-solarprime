#!/usr/bin/env python3
"""
Test Multimodal Production - Teste de produção completo com arquivos reais
Testa 100% da funcionalidade multimodal com imagem, PDF e áudio reais
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.agentic_sdr import AgenticSDR
from app.utils.logger import emoji_logger, logger
from app.config import settings


class MultimodalProductionTester:
    """Testador de produção para sistema multimodal"""
    
    def __init__(self):
        self.agent = None
        self.results = {
            "image": None,
            "pdf": None,
            "audio": None,
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
        
    async def setup(self):
        """Inicializa o agente SDR"""
        try:
            emoji_logger.system_info("🚀 Inicializando AgenticSDR para testes de produção...")
            self.agent = AgenticSDR()
            
            # Verificar se foi inicializado corretamente
            if not hasattr(self.agent, 'multimodal_enabled'):
                raise Exception("AgenticSDR não foi inicializado corretamente")
            
            # Verificar se multimodal está habilitado
            if not self.agent.multimodal_enabled:
                emoji_logger.system_warning("⚠️ Multimodal desabilitado. Habilitando...")
                self.agent.multimodal_enabled = True
            
            emoji_logger.system_info("✅ AgenticSDR inicializado com sucesso")
            emoji_logger.system_info(f"  • Multimodal: {'Habilitado' if self.agent.multimodal_enabled else 'Desabilitado'}")
            emoji_logger.system_info(f"  • Modelo: {getattr(self.agent, 'model_name', 'N/A')}")
            return True
        except Exception as e:
            emoji_logger.system_error("AgenticSDR Init", f"Erro ao inicializar: {str(e)}")
            logger.exception("Erro completo:")
            return False
    
    def encode_file_to_base64(self, file_path: str) -> str:
        """Codifica arquivo para base64"""
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            emoji_logger.system_error(f"Erro ao codificar arquivo {file_path}: {str(e)}")
            return None
    
    async def test_image(self):
        """Testa processamento de imagem real"""
        emoji_logger.system_info("\n" + "="*80)
        emoji_logger.system_info("🖼️  TESTE DE IMAGEM - 20250715_164305.png")
        emoji_logger.system_info("="*80)
        
        try:
            # Carregar imagem real
            image_path = "tests/20250715_164305.png"
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(image_path)
            emoji_logger.system_info(f"📊 Tamanho do arquivo: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Codificar para base64
            image_base64 = self.encode_file_to_base64(image_path)
            if not image_base64:
                raise Exception("Falha ao codificar imagem")
            
            emoji_logger.system_info(f"📏 Base64 length: {len(image_base64):,} caracteres")
            
            # Testar processamento
            start_time = datetime.now()
            result = await self.agent.process_multimodal_content(
                media_type="image",
                media_data=image_base64,
                caption="Teste de produção - imagem real"
            )
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Verificar resultado
            if result.get('status') == 'error' or 'error' in result:
                emoji_logger.system_error("Image Test", f"Erro no processamento: {result.get('error', 'Unknown error')}")
                self.results['image'] = {
                    "status": "failed",
                    "error": result.get('error'),
                    "processing_time": processing_time
                }
                self.results['summary']['failed'] += 1
            else:
                emoji_logger.system_info(f"✅ Imagem processada com sucesso em {processing_time:.2f}s")
                emoji_logger.system_info(f"📝 Tipo detectado: {result.get('type', 'unknown')}")
                emoji_logger.system_info(f"📄 Conteúdo extraído: {len(result.get('content', '')):.0f} caracteres")
                
                # Mostrar preview da análise
                content = result.get('content', '')
                if content:
                    preview = content[:300] + "..." if len(content) > 300 else content
                    emoji_logger.system_info(f"\n🔍 Preview da análise:\n{preview}")
                
                self.results['image'] = {
                    "status": "success",
                    "type": result.get('type'),
                    "content_length": len(result.get('content', '')),
                    "processing_time": processing_time,
                    "has_analysis": bool(result.get('content'))
                }
                self.results['summary']['passed'] += 1
                
        except Exception as e:
            emoji_logger.system_error("Image Test Exception", f"Exceção durante teste: {str(e)}")
            logger.exception("Erro completo:")
            self.results['image'] = {
                "status": "error",
                "error": str(e)
            }
            self.results['summary']['failed'] += 1
            self.results['summary']['errors'].append(f"Imagem: {str(e)}")
        
        self.results['summary']['total_tests'] += 1
    
    async def test_pdf(self):
        """Testa processamento de PDF real"""
        emoji_logger.system_info("\n" + "="*80)
        emoji_logger.system_info("📄 TESTE DE PDF - Boleto.pdf")
        emoji_logger.system_info("="*80)
        
        try:
            # Carregar PDF real
            pdf_path = "tests/Boleto.pdf"
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(pdf_path)
            emoji_logger.system_info(f"📊 Tamanho do arquivo: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Codificar para base64
            pdf_base64 = self.encode_file_to_base64(pdf_path)
            if not pdf_base64:
                raise Exception("Falha ao codificar PDF")
            
            emoji_logger.system_info(f"📏 Base64 length: {len(pdf_base64):,} caracteres")
            
            # Testar processamento
            start_time = datetime.now()
            result = await self.agent.process_multimodal_content(
                media_type="document",
                media_data=pdf_base64,
                caption="Teste de produção - PDF real (boleto)"
            )
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Verificar resultado
            if result.get('status') == 'error' or 'error' in result:
                emoji_logger.system_error("PDF Test", f"Erro no processamento: {result.get('error', 'Unknown error')}")
                self.results['pdf'] = {
                    "status": "failed",
                    "error": result.get('error'),
                    "processing_time": processing_time
                }
                self.results['summary']['failed'] += 1
            else:
                emoji_logger.system_info(f"✅ PDF processado com sucesso em {processing_time:.2f}s")
                emoji_logger.system_info(f"📝 Tipo documento: {result.get('document_type', 'unknown')}")
                emoji_logger.system_info(f"📄 Conteúdo extraído: {len(result.get('content', '')):.0f} caracteres")
                emoji_logger.system_info(f"📑 Páginas: {result.get('pages', 'N/A')}")
                emoji_logger.system_info(f"🔧 Método: {result.get('method', 'unknown')}")
                
                # Mostrar preview do conteúdo extraído
                content = result.get('content', '')
                if content:
                    preview = content[:300] + "..." if len(content) > 300 else content
                    emoji_logger.system_info(f"\n🔍 Preview do conteúdo:\n{preview}")
                
                # Mostrar análise do agente
                analysis = result.get('analysis', '')
                if analysis:
                    analysis_preview = analysis[:300] + "..." if len(analysis) > 300 else analysis
                    emoji_logger.system_info(f"\n🤖 Análise do agente:\n{analysis_preview}")
                
                self.results['pdf'] = {
                    "status": "success",
                    "document_type": result.get('document_type'),
                    "pages": result.get('pages'),
                    "content_length": len(result.get('content', '')),
                    "has_analysis": bool(result.get('analysis')),
                    "processing_time": processing_time,
                    "method": result.get('method')
                }
                self.results['summary']['passed'] += 1
                
        except Exception as e:
            emoji_logger.system_error("PDF Test Exception", f"Exceção durante teste: {str(e)}")
            logger.exception("Erro completo:")
            self.results['pdf'] = {
                "status": "error",
                "error": str(e)
            }
            self.results['summary']['failed'] += 1
            self.results['summary']['errors'].append(f"PDF: {str(e)}")
        
        self.results['summary']['total_tests'] += 1
    
    async def test_audio(self):
        """Testa processamento de áudio real"""
        emoji_logger.system_info("\n" + "="*80)
        emoji_logger.system_info("🎵 TESTE DE ÁUDIO - WhatsApp Audio 2025-08-03 at 22.31.42.opus")
        emoji_logger.system_info("="*80)
        
        try:
            # Carregar áudio real
            audio_path = "tests/WhatsApp Audio 2025-08-03 at 22.31.42.opus"
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(audio_path)
            emoji_logger.system_info(f"📊 Tamanho do arquivo: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Codificar para base64
            audio_base64 = self.encode_file_to_base64(audio_path)
            if not audio_base64:
                raise Exception("Falha ao codificar áudio")
            
            emoji_logger.system_info(f"📏 Base64 length: {len(audio_base64):,} caracteres")
            
            # Testar processamento
            start_time = datetime.now()
            result = await self.agent.process_multimodal_content(
                media_type="audio",
                media_data=audio_base64,
                caption="Teste de produção - áudio real WhatsApp"
            )
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Verificar resultado
            if result.get('status') == 'error' or 'error' in result:
                emoji_logger.system_error("Audio Test", f"Erro no processamento: {result.get('error', 'Unknown error')}")
                self.results['audio'] = {
                    "status": "failed",
                    "error": result.get('error'),
                    "processing_time": processing_time
                }
                self.results['summary']['failed'] += 1
            else:
                emoji_logger.system_info(f"✅ Áudio processado com sucesso em {processing_time:.2f}s")
                emoji_logger.system_info(f"📝 Transcrição: {result.get('transcription', 'N/A')}")
                emoji_logger.system_info(f"🔧 Método: {result.get('transcription_method', 'unknown')}")
                emoji_logger.system_info(f"⏱️ Duração: {result.get('duration', 'N/A')}s")
                
                # Verificar se há transcrição
                transcription = result.get('transcription', '')
                if transcription:
                    emoji_logger.system_info(f"\n🎤 Transcrição completa:\n{transcription}")
                else:
                    emoji_logger.system_warning("⚠️ Nenhuma transcrição foi retornada")
                
                self.results['audio'] = {
                    "status": "success",
                    "has_transcription": bool(transcription),
                    "transcription_length": len(transcription),
                    "duration": result.get('duration'),
                    "processing_time": processing_time,
                    "method": result.get('transcription_method')
                }
                self.results['summary']['passed'] += 1
                
        except Exception as e:
            emoji_logger.system_error("Audio Test Exception", f"Exceção durante teste: {str(e)}")
            logger.exception("Erro completo:")
            self.results['audio'] = {
                "status": "error",
                "error": str(e)
            }
            self.results['summary']['failed'] += 1
            self.results['summary']['errors'].append(f"Áudio: {str(e)}")
        
        self.results['summary']['total_tests'] += 1
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        emoji_logger.system_info("\n" + "="*80)
        emoji_logger.system_info("📊 RESUMO DOS TESTES DE PRODUÇÃO")
        emoji_logger.system_info("="*80)
        
        summary = self.results['summary']
        success_rate = (summary['passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        
        emoji_logger.system_info(f"📈 Total de testes: {summary['total_tests']}")
        emoji_logger.system_info(f"✅ Testes aprovados: {summary['passed']}")
        emoji_logger.system_info(f"❌ Testes falhados: {summary['failed']}")
        emoji_logger.system_info(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        # Detalhes por tipo
        emoji_logger.system_info("\n🔍 Detalhes por tipo de mídia:")
        
        # Imagem
        if self.results['image']:
            img = self.results['image']
            status_emoji = "✅" if img['status'] == 'success' else "❌"
            emoji_logger.system_info(f"\n🖼️  Imagem: {status_emoji} {img['status'].upper()}")
            if img['status'] == 'success':
                emoji_logger.system_info(f"  • Tempo: {img['processing_time']:.2f}s")
                emoji_logger.system_info(f"  • Conteúdo: {img['content_length']} caracteres")
                emoji_logger.system_info(f"  • Análise: {'Sim' if img['has_analysis'] else 'Não'}")
            else:
                emoji_logger.system_info(f"  • Erro: {img.get('error', 'Unknown')}")
        
        # PDF
        if self.results['pdf']:
            pdf = self.results['pdf']
            status_emoji = "✅" if pdf['status'] == 'success' else "❌"
            emoji_logger.system_info(f"\n📄 PDF: {status_emoji} {pdf['status'].upper()}")
            if pdf['status'] == 'success':
                emoji_logger.system_info(f"  • Tempo: {pdf['processing_time']:.2f}s")
                emoji_logger.system_info(f"  • Páginas: {pdf.get('pages', 'N/A')}")
                emoji_logger.system_info(f"  • Conteúdo: {pdf['content_length']} caracteres")
                emoji_logger.system_info(f"  • Análise: {'Sim' if pdf['has_analysis'] else 'Não'}")
                emoji_logger.system_info(f"  • Método: {pdf.get('method', 'N/A')}")
            else:
                emoji_logger.system_info(f"  • Erro: {pdf.get('error', 'Unknown')}")
        
        # Áudio
        if self.results['audio']:
            audio = self.results['audio']
            status_emoji = "✅" if audio['status'] == 'success' else "❌"
            emoji_logger.system_info(f"\n🎵 Áudio: {status_emoji} {audio['status'].upper()}")
            if audio['status'] == 'success':
                emoji_logger.system_info(f"  • Tempo: {audio['processing_time']:.2f}s")
                emoji_logger.system_info(f"  • Transcrição: {'Sim' if audio['has_transcription'] else 'Não'}")
                if audio['has_transcription']:
                    emoji_logger.system_info(f"  • Tamanho: {audio['transcription_length']} caracteres")
                emoji_logger.system_info(f"  • Duração: {audio.get('duration', 'N/A')}s")
                emoji_logger.system_info(f"  • Método: {audio.get('method', 'N/A')}")
            else:
                emoji_logger.system_info(f"  • Erro: {audio.get('error', 'Unknown')}")
        
        # Erros gerais
        if summary['errors']:
            emoji_logger.system_info("\n⚠️ Erros encontrados:")
            for error in summary['errors']:
                emoji_logger.system_error("Summary", f"  • {error}")
        
        # Salvar resultados em JSON
        output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        emoji_logger.system_info(f"\n💾 Resultados salvos em: {output_file}")
        
        # Conclusão
        emoji_logger.system_info("\n" + "="*80)
        if success_rate == 100:
            emoji_logger.system_info("🎉 TODOS OS TESTES PASSARAM! Sistema multimodal 100% funcional!")
        elif success_rate >= 66:
            emoji_logger.system_info("✅ Sistema multimodal parcialmente funcional")
        else:
            emoji_logger.system_error("Final Status", "Sistema multimodal com problemas críticos")
        emoji_logger.system_info("="*80)
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        emoji_logger.system_info("\n" + "🚀 "*20)
        emoji_logger.system_info("INICIANDO TESTES DE PRODUÇÃO MULTIMODAL")
        emoji_logger.system_info("Validando 100% do sistema com arquivos reais")
        emoji_logger.system_info("🚀 "*20 + "\n")
        
        # Setup
        if not await self.setup():
            emoji_logger.system_error("❌ Falha na inicialização. Abortando testes.")
            return
        
        # Executar testes
        await self.test_image()
        await self.test_pdf()
        await self.test_audio()
        
        # Resumo
        self.print_summary()


async def main():
    """Função principal"""
    tester = MultimodalProductionTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # Configurar logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Executar testes
    asyncio.run(main())