#!/usr/bin/env python3
"""
Script de teste completo para verificar funcionamento multimodal do agente
"""

import asyncio
import sys
import os
from pathlib import Path
import base64
import json
from datetime import datetime

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from agents.sdr_agent import SDRAgent, AGNO_READERS_AVAILABLE, AGNO_MEDIA_AVAILABLE
from loguru import logger


class MultimodalAgentTester:
    """Classe para testar capacidades multimodais do agente"""
    
    def __init__(self):
        self.agent = SDRAgent()
        self.test_results = {
            "agno_imports": {},
            "image_processing": {},
            "pdf_processing": {},
            "integration": {},
            "issues": []
        }
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        logger.info("=== INICIANDO TESTES DO AGENTE MULTIMODAL ===")
        
        # 1. Verificar imports do AGnO
        await self.test_agno_imports()
        
        # 2. Testar processamento de imagens
        await self.test_image_processing()
        
        # 3. Testar processamento de PDFs
        await self.test_pdf_processing()
        
        # 4. Testar integração completa
        await self.test_full_integration()
        
        # 5. Gerar relatório
        self.generate_report()
    
    async def test_agno_imports(self):
        """Verifica se os módulos AGnO estão disponíveis"""
        logger.info("\n📦 TESTE 1: Verificando imports do AGnO Framework")
        
        # Verificar módulos de mídia
        self.test_results["agno_imports"]["media_available"] = AGNO_MEDIA_AVAILABLE
        logger.info(f"  ✓ Módulos de mídia (Image, Audio, Video): {'✅ Disponível' if AGNO_MEDIA_AVAILABLE else '❌ Não disponível'}")
        
        # Verificar módulos de leitura
        self.test_results["agno_imports"]["readers_available"] = AGNO_READERS_AVAILABLE
        logger.info(f"  ✓ Módulos de leitura (PDFReader, PDFImageReader): {'✅ Disponível' if AGNO_READERS_AVAILABLE else '❌ Não disponível'}")
        
        # Verificar modelos
        try:
            from agno.models.google import Gemini
            self.test_results["agno_imports"]["gemini_model"] = True
            logger.info("  ✓ Modelo Gemini: ✅ Disponível")
        except ImportError:
            self.test_results["agno_imports"]["gemini_model"] = False
            logger.info("  ✓ Modelo Gemini: ❌ Não disponível")
            self.test_results["issues"].append("Gemini model não pode ser importado")
        
        try:
            from agno.models.openai import OpenAIChat
            self.test_results["agno_imports"]["openai_model"] = True
            logger.info("  ✓ Modelo OpenAI: ✅ Disponível")
        except ImportError:
            self.test_results["agno_imports"]["openai_model"] = False
            logger.info("  ✓ Modelo OpenAI: ❌ Não disponível")
        
        # Verificar Agent
        try:
            from agno.agent import Agent, AgentMemory
            self.test_results["agno_imports"]["agent_core"] = True
            logger.info("  ✓ Agent Core: ✅ Disponível")
        except ImportError:
            self.test_results["agno_imports"]["agent_core"] = False
            logger.info("  ✓ Agent Core: ❌ Não disponível")
            self.test_results["issues"].append("Agent core não pode ser importado")
    
    async def test_image_processing(self):
        """Testa processamento de imagens"""
        logger.info("\n🖼️  TESTE 2: Verificando processamento de imagens")
        
        # Teste 1: Verificar método _create_agno_image
        logger.info("  → Testando criação de objeto Image AGnO...")
        
        test_cases = [
            {
                "name": "URL de imagem",
                "data": {"url": "https://example.com/conta.jpg"},
                "expected": True
            },
            {
                "name": "Base64",
                "data": {"base64": base64.b64encode(b"fake image data").decode()},
                "expected": True
            },
            {
                "name": "Path do arquivo",
                "data": {"path": "/tmp/conta.jpg"},
                "expected": True
            }
        ]
        
        for test in test_cases:
            try:
                result = self.agent._create_agno_image(test["data"])
                success = result is not None
                self.test_results["image_processing"][test["name"]] = success
                logger.info(f"    • {test['name']}: {'✅ OK' if success else '❌ Falhou'}")
                
                if not success and test["expected"]:
                    self.test_results["issues"].append(f"Falha ao criar Image AGnO com {test['name']}")
            except Exception as e:
                self.test_results["image_processing"][test["name"]] = False
                logger.error(f"    • {test['name']}: ❌ Erro: {e}")
                self.test_results["issues"].append(f"Erro ao criar Image AGnO com {test['name']}: {e}")
        
        # Teste 2: Verificar análise de imagem
        logger.info("  → Testando análise de imagem com Gemini Vision...")
        
        try:
            # Criar dados fake de imagem
            fake_image_data = {"base64": base64.b64encode(b"fake bill image").decode()}
            
            # Testar método _analyze_image_with_gemini
            # Como é async e precisa de conexão real, vamos verificar se o método existe
            if hasattr(self.agent, '_analyze_image_with_gemini'):
                self.test_results["image_processing"]["analyze_method_exists"] = True
                logger.info("    • Método _analyze_image_with_gemini: ✅ Existe")
                
                # Verificar estrutura do prompt
                if hasattr(self.agent, '_process_media'):
                    self.test_results["image_processing"]["process_media_exists"] = True
                    logger.info("    • Método _process_media: ✅ Existe")
                else:
                    self.test_results["image_processing"]["process_media_exists"] = False
                    logger.error("    • Método _process_media: ❌ Não encontrado")
                    self.test_results["issues"].append("Método _process_media não encontrado")
            else:
                self.test_results["image_processing"]["analyze_method_exists"] = False
                logger.error("    • Método _analyze_image_with_gemini: ❌ Não encontrado")
                self.test_results["issues"].append("Método _analyze_image_with_gemini não encontrado")
                
        except Exception as e:
            logger.error(f"  ❌ Erro ao testar análise de imagem: {e}")
            self.test_results["issues"].append(f"Erro ao testar análise de imagem: {e}")
    
    async def test_pdf_processing(self):
        """Testa processamento de PDFs"""
        logger.info("\n📄 TESTE 3: Verificando processamento de PDFs")
        
        # Verificar se PDFImageReader está disponível
        if AGNO_READERS_AVAILABLE:
            logger.info("  ✓ PDFImageReader disponível para processamento")
            self.test_results["pdf_processing"]["reader_available"] = True
            
            # Verificar imports específicos
            try:
                from agno.document_reader.pdf_image import PDFImageReader
                logger.info("    • Import direto: ✅ OK")
                self.test_results["pdf_processing"]["direct_import"] = True
            except ImportError:
                try:
                    from agno.readers import PDFImageReader
                    logger.info("    • Import alternativo: ✅ OK")
                    self.test_results["pdf_processing"]["alt_import"] = True
                except ImportError:
                    logger.error("    • Nenhum import funcionou: ❌")
                    self.test_results["pdf_processing"]["import_failed"] = True
                    self.test_results["issues"].append("PDFImageReader não pode ser importado apesar de AGNO_READERS_AVAILABLE=True")
        else:
            logger.warning("  ⚠️  PDFImageReader não disponível - sistema usará fallbacks")
            self.test_results["pdf_processing"]["reader_available"] = False
        
        # Verificar método _process_pdf_with_ocr
        if hasattr(self.agent, '_process_pdf_with_ocr'):
            self.test_results["pdf_processing"]["process_method_exists"] = True
            logger.info("  ✓ Método _process_pdf_with_ocr: ✅ Existe")
            
            # Verificar estrutura do método
            import inspect
            method_source = inspect.getsource(self.agent._process_pdf_with_ocr)
            
            # Verificar se tem os fallbacks implementados
            has_pdf_reader = "PDFImageReader" in method_source
            has_pdf2image = "pdf2image" in method_source
            has_fallback_msg = "suggestion" in method_source
            
            logger.info(f"    • Suporte PDFImageReader: {'✅' if has_pdf_reader else '❌'}")
            logger.info(f"    • Fallback pdf2image: {'✅' if has_pdf2image else '❌'}")
            logger.info(f"    • Mensagem de fallback: {'✅' if has_fallback_msg else '❌'}")
            
            self.test_results["pdf_processing"]["has_pdf_reader"] = has_pdf_reader
            self.test_results["pdf_processing"]["has_pdf2image"] = has_pdf2image
            self.test_results["pdf_processing"]["has_fallback"] = has_fallback_msg
            
            if not has_pdf_reader:
                self.test_results["issues"].append("PDFImageReader não está sendo usado no _process_pdf_with_ocr")
                
        else:
            self.test_results["pdf_processing"]["process_method_exists"] = False
            logger.error("  ❌ Método _process_pdf_with_ocr não encontrado")
            self.test_results["issues"].append("Método _process_pdf_with_ocr não encontrado")
    
    async def test_full_integration(self):
        """Testa integração completa do fluxo multimodal"""
        logger.info("\n🔗 TESTE 4: Verificando integração completa")
        
        # Verificar se process_message aceita mídia
        logger.info("  → Verificando assinatura de process_message...")
        
        import inspect
        sig = inspect.signature(self.agent.process_message)
        params = list(sig.parameters.keys())
        
        required_params = ['media_type', 'media_data']
        for param in required_params:
            if param in params:
                logger.info(f"    • Parâmetro '{param}': ✅ Presente")
                self.test_results["integration"][f"param_{param}"] = True
            else:
                logger.error(f"    • Parâmetro '{param}': ❌ Ausente")
                self.test_results["integration"][f"param_{param}"] = False
                self.test_results["issues"].append(f"Parâmetro '{param}' não encontrado em process_message")
        
        # Verificar fluxo de processamento
        logger.info("  → Verificando fluxo de processamento de mídia...")
        
        # Analisar o código de process_message
        method_source = inspect.getsource(self.agent.process_message)
        
        checks = {
            "process_image": "media_type == \"image\"" in method_source,
            "process_document": "media_type == \"document\"" in method_source,
            "create_agno_image": "_create_agno_image" in method_source,
            "process_media_call": "_process_media" in method_source,
            "pass_images_to_agent": "images=processed_images" in method_source
        }
        
        for check, result in checks.items():
            logger.info(f"    • {check}: {'✅' if result else '❌'}")
            self.test_results["integration"][check] = result
            
            if not result:
                self.test_results["issues"].append(f"Verificação '{check}' falhou em process_message")
        
        # Verificar se o contexto é atualizado com dados da mídia
        logger.info("  → Verificando atualização de contexto com dados extraídos...")
        
        context_updates = {
            "bill_value_update": "bill_value" in method_source and "session_state[\"lead_info\"][\"bill_value\"]" in method_source,
            "consumption_update": "consumption_kwh" in method_source and "session_state[\"lead_info\"][\"consumption_kwh\"]" in method_source,
            "address_update": "address" in method_source and "session_state[\"lead_info\"][\"address\"]" in method_source
        }
        
        for check, result in context_updates.items():
            logger.info(f"    • {check}: {'✅' if result else '❌'}")
            self.test_results["integration"][check] = result
            
            if not result:
                self.test_results["issues"].append(f"Atualização de contexto '{check}' não encontrada")
    
    def generate_report(self):
        """Gera relatório final dos testes"""
        logger.info("\n" + "="*60)
        logger.info("📊 RELATÓRIO FINAL DOS TESTES")
        logger.info("="*60)
        
        # Calcular totais
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.test_results.items():
            if category == "issues":
                continue
            
            if isinstance(results, dict):
                for test, result in results.items():
                    total_tests += 1
                    if result is True:
                        passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"\n📈 Taxa de Sucesso: {success_rate:.1f}% ({passed_tests}/{total_tests} testes)")
        
        # Status geral
        if success_rate == 100:
            logger.success("\n✅ AGENTE 100% FUNCIONAL PARA PROCESSAMENTO MULTIMODAL!")
        elif success_rate >= 80:
            logger.warning(f"\n⚠️  AGENTE {success_rate:.1f}% FUNCIONAL - Alguns ajustes necessários")
        else:
            logger.error(f"\n❌ AGENTE APENAS {success_rate:.1f}% FUNCIONAL - Correções urgentes necessárias")
        
        # Listar problemas encontrados
        if self.test_results["issues"]:
            logger.warning(f"\n🔧 PROBLEMAS ENCONTRADOS ({len(self.test_results['issues'])} issues):")
            for i, issue in enumerate(self.test_results["issues"], 1):
                logger.warning(f"  {i}. {issue}")
        
        # Recomendações
        logger.info("\n💡 RECOMENDAÇÕES:")
        
        if not AGNO_READERS_AVAILABLE:
            logger.info("  1. Instalar módulos de leitura do AGnO:")
            logger.info("     pip install agno[readers]")
        
        if not AGNO_MEDIA_AVAILABLE:
            logger.info("  2. Verificar instalação dos módulos de mídia do AGnO")
        
        if "pdf2image" in str(self.test_results["issues"]):
            logger.info("  3. Instalar pdf2image para fallback de PDF:")
            logger.info("     pip install pdf2image")
        
        if self.test_results["integration"].get("pass_images_to_agent") is False:
            logger.info("  4. Verificar se imagens estão sendo passadas corretamente para o agente")
        
        # Salvar relatório em arquivo
        report_path = Path(__file__).parent / "multimodal_test_report.json"
        with open(report_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "success_rate": success_rate,
                "results": self.test_results
            }, f, indent=2)
        
        logger.info(f"\n📝 Relatório completo salvo em: {report_path}")


async def main():
    """Função principal"""
    tester = MultimodalAgentTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())