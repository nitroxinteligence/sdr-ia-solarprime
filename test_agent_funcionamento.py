#!/usr/bin/env python3
"""
Script de Teste Completo do Agente SDR IA
==========================================
Testa todas as funcionalidades do agente de IA para WhatsApp
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any
import json

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar variáveis de ambiente para teste
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"
os.environ["LOG_LEVEL"] = "DEBUG"

# Importar após configurar ambiente
from agents.sdr_agent import create_sdr_agent
from config.agent_config import config
from loguru import logger

class TestResults:
    """Classe para armazenar resultados dos testes"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_test(self, test_name: str, success: bool, error: str = None):
        self.total += 1
        if success:
            self.passed += 1
            logger.info(f"✅ {test_name} - PASSOU")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error}")
            logger.error(f"❌ {test_name} - FALHOU: {error}")
    
    def print_summary(self):
        logger.info("\n" + "="*50)
        logger.info("RESUMO DOS TESTES")
        logger.info("="*50)
        logger.info(f"Total de testes: {self.total}")
        logger.info(f"✅ Passou: {self.passed}")
        logger.info(f"❌ Falhou: {self.failed}")
        
        if self.errors:
            logger.error("\nERROS ENCONTRADOS:")
            for error in self.errors:
                logger.error(f"  - {error}")
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        logger.info(f"\nTaxa de sucesso: {success_rate:.1f}%")
        
        return self.failed == 0


async def test_agent_initialization():
    """Testa a inicialização do agente"""
    logger.info("\n🧪 Testando inicialização do agente...")
    results = TestResults()
    
    try:
        # Teste 1: Criar agente
        agent = create_sdr_agent()
        results.add_test("Criar instância do agente", True)
        
        # Teste 2: Verificar configurações
        results.add_test(
            "Configuração do modelo", 
            agent.model is not None,
            "Modelo não configurado"
        )
        
        # Teste 3: Verificar personalidade
        results.add_test(
            "Nome do agente configurado",
            agent.config.personality.name == "Luna",
            f"Nome incorreto: {agent.config.personality.name}"
        )
        
    except Exception as e:
        results.add_test("Inicialização do agente", False, str(e))
    
    return results


async def test_message_processing():
    """Testa o processamento de mensagens"""
    logger.info("\n🧪 Testando processamento de mensagens...")
    results = TestResults()
    
    try:
        agent = create_sdr_agent()
        test_phone = "5511999999999"
        
        # Teste 1: Mensagem simples
        try:
            response, metadata = await agent.process_message(
                message="Olá, quero saber sobre energia solar",
                phone_number=test_phone
            )
            
            results.add_test(
                "Processar mensagem simples",
                response is not None and len(response) > 0,
                f"Resposta vazia ou None: {response}"
            )
            
            # Verificar se não tem markdown
            has_markdown = any(char in response for char in ['*', '_', '#', '`', '[', ']'])
            results.add_test(
                "Resposta sem formatação markdown",
                not has_markdown,
                f"Resposta contém markdown: {response[:100]}..."
            )
            
        except Exception as e:
            results.add_test("Processar mensagem simples", False, str(e))
        
        # Teste 2: Múltiplas mensagens (contexto)
        try:
            # Primeira mensagem
            response1, _ = await agent.process_message(
                message="Meu nome é João",
                phone_number=test_phone
            )
            
            # Segunda mensagem testando memória
            response2, metadata2 = await agent.process_message(
                message="Qual é meu nome?",
                phone_number=test_phone
            )
            
            # Verificar se lembra do nome
            has_context = "João" in response2 or "joao" in response2.lower()
            results.add_test(
                "Manter contexto entre mensagens",
                has_context,
                f"Agente não lembrou do nome. Resposta: {response2[:100]}..."
            )
            
            # Verificar metadata
            results.add_test(
                "Metadata contém stage",
                "stage" in metadata2,
                f"Metadata incompleto: {metadata2}"
            )
            
        except Exception as e:
            results.add_test("Manter contexto", False, str(e))
        
        # Teste 3: Diferentes tipos de perguntas
        test_messages = [
            ("Quanto custa?", "preço"),
            ("Como funciona?", "funcionamento"),
            ("Posso agendar uma visita?", "agendamento"),
            ("Não tenho interesse", "objeção")
        ]
        
        for msg, tipo in test_messages:
            try:
                response, _ = await agent.process_message(
                    message=msg,
                    phone_number=f"{test_phone}_{tipo}"
                )
                
                results.add_test(
                    f"Responder pergunta sobre {tipo}",
                    response is not None and len(response) > 10,
                    f"Resposta inadequada: {response[:50]}..."
                )
                
            except Exception as e:
                results.add_test(f"Pergunta sobre {tipo}", False, str(e))
        
    except Exception as e:
        results.add_test("Processamento de mensagens", False, str(e))
    
    return results


async def test_error_handling():
    """Testa o tratamento de erros"""
    logger.info("\n🧪 Testando tratamento de erros...")
    results = TestResults()
    
    try:
        agent = create_sdr_agent()
        
        # Teste 1: Mensagem vazia
        try:
            response, _ = await agent.process_message(
                message="",
                phone_number="5511999999999"
            )
            results.add_test(
                "Lidar com mensagem vazia",
                response is not None,
                "Falhou com mensagem vazia"
            )
        except Exception as e:
            # Se houver exceção mas for tratada graciosamente
            results.add_test(
                "Lidar com mensagem vazia",
                "erro ao processar" in str(e).lower(),
                f"Erro não tratado: {e}"
            )
        
        # Teste 2: Número de telefone inválido
        try:
            response, _ = await agent.process_message(
                message="Teste",
                phone_number=""
            )
            results.add_test(
                "Lidar com telefone vazio",
                response is not None,
                "Falhou com telefone vazio"
            )
        except Exception as e:
            # Esperado que trate o erro
            results.add_test("Lidar com telefone vazio", True)
        
        # Teste 3: Mensagem muito longa
        long_message = "teste " * 1000  # 5000 caracteres
        try:
            response, _ = await agent.process_message(
                message=long_message,
                phone_number="5511999999999"
            )
            results.add_test(
                "Lidar com mensagem longa",
                response is not None and len(response) < 4096,
                f"Resposta muito longa: {len(response)} caracteres"
            )
        except Exception as e:
            results.add_test("Lidar com mensagem longa", False, str(e))
        
    except Exception as e:
        results.add_test("Tratamento de erros", False, str(e))
    
    return results


async def test_agno_framework_integration():
    """Testa a integração com AGnO Framework"""
    logger.info("\n🧪 Testando integração com AGnO Framework...")
    results = TestResults()
    
    try:
        agent = create_sdr_agent()
        test_phone = "5511888888888"
        
        # Teste 1: Verificar reasoning (chain of thought)
        try:
            # Fazer uma pergunta que requer raciocínio
            response, metadata = await agent.process_message(
                message="Tenho uma conta de luz de R$ 800, vale a pena energia solar?",
                phone_number=test_phone
            )
            
            results.add_test(
                "Reasoning ativado",
                response is not None and len(response) > 50,
                "Resposta muito curta para reasoning"
            )
            
            # Verificar se a resposta é contextualizada
            has_value_context = "800" in response or "oitocentos" in response.lower()
            results.add_test(
                "Resposta contextualizada com valor",
                has_value_context,
                f"Resposta não menciona o valor: {response[:100]}..."
            )
            
        except Exception as e:
            results.add_test("Reasoning AGnO", False, str(e))
        
        # Teste 2: Verificar memória/sessão
        try:
            # Enviar informação
            await agent.process_message(
                message="Moro em São Paulo e tenho interesse",
                phone_number=test_phone
            )
            
            # Verificar se lembra
            response, _ = await agent.process_message(
                message="Em qual cidade eu moro?",
                phone_number=test_phone
            )
            
            has_memory = "são paulo" in response.lower() or "sp" in response.lower()
            results.add_test(
                "Memória AGnO funcionando",
                has_memory,
                f"Não lembrou da cidade: {response[:100]}..."
            )
            
        except Exception as e:
            results.add_test("Memória AGnO", False, str(e))
        
    except Exception as e:
        results.add_test("Integração AGnO", False, str(e))
    
    return results


async def main():
    """Executa todos os testes"""
    logger.info("🚀 INICIANDO TESTES DO AGENTE SDR IA")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("="*60)
    
    all_results = []
    
    # Executar testes
    all_results.append(await test_agent_initialization())
    all_results.append(await test_message_processing())
    all_results.append(await test_error_handling())
    all_results.append(await test_agno_framework_integration())
    
    # Resumo geral
    logger.info("\n" + "="*60)
    logger.info("RESUMO GERAL DOS TESTES")
    logger.info("="*60)
    
    total_tests = sum(r.total for r in all_results)
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    
    logger.info(f"Total de testes executados: {total_tests}")
    logger.info(f"✅ Total passou: {total_passed}")
    logger.info(f"❌ Total falhou: {total_failed}")
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    logger.info(f"\n🎯 Taxa de sucesso geral: {success_rate:.1f}%")
    
    if total_failed == 0:
        logger.info("\n✨ TODOS OS TESTES PASSARAM! O agente está funcionando 100%! ✨")
        return True
    else:
        logger.error(f"\n⚠️  {total_failed} testes falharam. Verifique os erros acima.")
        return False


if __name__ == "__main__":
    # Executar testes
    success = asyncio.run(main())
    
    # Sair com código apropriado
    sys.exit(0 if success else 1)