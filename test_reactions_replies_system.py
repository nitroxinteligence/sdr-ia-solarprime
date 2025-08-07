#!/usr/bin/env python3
"""
TESTE SISTEMA DE REAÇÕES E REPLIES - VALIDAÇÃO COMPLETA
Testa nova SEÇÃO 9: ESTRATÉGIA DE INTERAÇÃO AVANÇADA implementada no prompt
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Adicionar ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.agentic_sdr import create_agentic_sdr
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

class ReactionsRepliesSystemTester:
    """Testador completo do sistema de reações e replies"""
    
    def __init__(self):
        self.test_results = []
        
    async def create_test_lead(self) -> Dict[str, Any]:
        """Cria lead de teste válido"""
        return {
            'id': '12345678-1234-5678-9abc-123456789012',
            'name': 'Maria Santos',
            'phone_number': '5511999887766',
            'bill_value': 650.0,
            'email': 'maria.santos@email.com',
            'created_at': datetime.now().isoformat()
        }
    
    async def test_reaction_scenarios(self, sdr_agent) -> List[Dict[str, Any]]:
        """Testa cenários que devem gerar reações"""
        
        logger.info("🧪 TESTANDO CENÁRIOS DE REAÇÕES...")
        
        test_cases = [
            {
                'name': 'Confirmação Documento',
                'message': 'Oi Helen! Aqui está minha conta de luz 📄',
                'expected_reaction_types': ['✅', '👍', '⭐'],
                'should_have_reaction': True
            },
            {
                'name': 'Conta Alta - Reação Emocional',
                'message': 'Minha conta vem R$ 850 por mês... é muito caro!',
                'expected_reaction_types': ['😳', '💰', '📊'],
                'should_have_reaction': True
            },
            {
                'name': 'Interesse Solar',
                'message': 'Adorei saber sobre energia solar! Como funciona?',
                'expected_reaction_types': ['☀️', '⚡', '💡'],
                'should_have_reaction': True  
            },
            {
                'name': 'Fechamento/Decisão',
                'message': 'Perfeito! Quero fazer minha usina solar!',
                'expected_reaction_types': ['🎉', '🤝', '👏', '⭐'],
                'should_have_reaction': True
            },
            {
                'name': 'Pergunta Técnica Simples',  
                'message': 'Quantos anos dura uma placa solar?',
                'expected_reaction_types': [],
                'should_have_reaction': False  # Pergunta direta = resposta, não reação
            }
        ]
        
        results = []
        lead_data = await self.create_test_lead()
        
        for test_case in test_cases:
            logger.info(f"   📋 Testando: {test_case['name']}")
            
            try:
                response = await sdr_agent.process_message(
                    phone=lead_data['phone_number'],
                    message=test_case['message'],
                    lead_data=lead_data,
                    conversation_id='test-conv-reactions'
                )
                
                # Analisar resposta
                has_reaction = False
                reaction_used = None
                
                if isinstance(response, dict) and 'reaction' in response:
                    reaction = response.get('reaction')
                    if reaction:
                        has_reaction = True
                        reaction_used = reaction
                
                # Validar resultado
                test_passed = (has_reaction == test_case['should_have_reaction'])
                if has_reaction and test_case['expected_reaction_types']:
                    test_passed = reaction_used in test_case['expected_reaction_types']
                
                result = {
                    'test_name': test_case['name'],
                    'message': test_case['message'],
                    'expected_reaction': test_case['should_have_reaction'],
                    'has_reaction': has_reaction,
                    'reaction_used': reaction_used,
                    'test_passed': test_passed,
                    'response_text': response.get('text', '') if isinstance(response, dict) else str(response)
                }
                
                results.append(result)
                
                status = "✅ PASSOU" if test_passed else "❌ FALHOU"
                logger.info(f"      {status} - Reação: {reaction_used or 'Nenhuma'}")
                
            except Exception as e:
                logger.error(f"      ❌ ERRO: {e}")
                results.append({
                    'test_name': test_case['name'],
                    'test_passed': False,
                    'error': str(e)
                })
        
        return results
    
    async def test_reply_scenarios(self, sdr_agent) -> List[Dict[str, Any]]:
        """Testa cenários que devem gerar replies/citações"""
        
        logger.info("🧪 TESTANDO CENÁRIOS DE REPLIES...")
        
        test_cases = [
            {
                'name': 'Múltiplas Perguntas',
                'message': 'Helen, quanto custa uma usina? Quanto tempo demora para instalar? E a garantia?',
                'should_have_reply': True,
                'reason': 'Múltiplas perguntas (>2)'
            },
            {
                'name': 'Correção de Informação',
                'message': 'Na verdade minha conta é R$ 400, não R$ 650 como falei antes',
                'should_have_reply': True,
                'reason': 'Correção de dados'
            },
            {
                'name': 'Pergunta Técnica Específica',
                'message': 'Sobre aquele valor de R$ 650 que mencionei, qual seria minha economia mensal?',
                'should_have_reply': True,
                'reason': 'Referência a dados específicos'
            },
            {
                'name': 'Pergunta Simples',
                'message': 'Qual seu horário de funcionamento?',
                'should_have_reply': False,
                'reason': 'Pergunta simples e direta'
            }
        ]
        
        results = []
        lead_data = await self.create_test_lead()
        
        for test_case in test_cases:
            logger.info(f"   📋 Testando: {test_case['name']}")
            
            try:
                response = await sdr_agent.process_message(
                    phone=lead_data['phone_number'],
                    message=test_case['message'],
                    lead_data=lead_data,
                    conversation_id='test-conv-replies'
                )
                
                # Analisar resposta
                has_reply = False
                reply_to = None
                
                if isinstance(response, dict) and 'reply_to' in response:
                    reply_to = response.get('reply_to')
                    if reply_to:
                        has_reply = True
                
                # Validar resultado
                test_passed = (has_reply == test_case['should_have_reply'])
                
                result = {
                    'test_name': test_case['name'],
                    'message': test_case['message'],
                    'expected_reply': test_case['should_have_reply'],
                    'has_reply': has_reply,
                    'reply_to': reply_to,
                    'test_passed': test_passed,
                    'reason': test_case['reason'],
                    'response_text': response.get('text', '') if isinstance(response, dict) else str(response)
                }
                
                results.append(result)
                
                status = "✅ PASSOU" if test_passed else "❌ FALHOU"
                logger.info(f"      {status} - Reply: {'Sim' if has_reply else 'Não'} ({test_case['reason']})")
                
            except Exception as e:
                logger.error(f"      ❌ ERRO: {e}")
                results.append({
                    'test_name': test_case['name'],
                    'test_passed': False,
                    'error': str(e)
                })
        
        return results
    
    async def test_frequency_improvement(self, sdr_agent) -> Dict[str, Any]:
        """Testa se a frequência de reações/replies aumentou"""
        
        logger.info("🧪 TESTANDO FREQUÊNCIA DE INTERAÇÕES...")
        
        # Mensagens que devem gerar reações/replies com nova estratégia
        test_messages = [
            "Aqui está minha conta! R$ 750 por mês 📄",  # Deve reagir (documento + valor alto)
            "Adorei a proposta de energia solar! ☀️",     # Deve reagir (solar + interesse)
            "Quanto custa? Quando instala? Qual garantia?", # Deve citar (múltiplas perguntas)
            "Nossa, R$ 900 por mês é muito caro mesmo!", # Deve reagir (valor alto + emoção)
            "Quero agendar para amanhã às 14h por favor", # Deve reagir (decisão positiva)
        ]
        
        reactions_count = 0
        replies_count = 0
        total_tests = len(test_messages)
        lead_data = await self.create_test_lead()
        
        for i, message in enumerate(test_messages):
            logger.info(f"   📋 Teste {i+1}/{total_tests}: {message[:30]}...")
            
            try:
                response = await sdr_agent.process_message(
                    phone=lead_data['phone_number'],
                    message=message,
                    lead_data=lead_data,
                    conversation_id=f'test-conv-freq-{i}'
                )
                
                if isinstance(response, dict):
                    if response.get('reaction'):
                        reactions_count += 1
                        logger.info(f"      ✅ Reação: {response.get('reaction')}")
                    
                    if response.get('reply_to'):
                        replies_count += 1
                        logger.info(f"      ✅ Reply: {response.get('reply_to')}")
                
            except Exception as e:
                logger.error(f"      ❌ ERRO: {e}")
        
        # Calcular frequências
        reaction_frequency = (reactions_count / total_tests) * 100
        reply_frequency = (replies_count / total_tests) * 100
        
        # Benchmarks esperados (baseados na pesquisa 2025)
        expected_reaction_freq = 30  # 25-30% target
        expected_reply_freq = 20     # 15-20% target
        
        return {
            'total_tests': total_tests,
            'reactions_count': reactions_count,
            'replies_count': replies_count,
            'reaction_frequency': reaction_frequency,
            'reply_frequency': reply_frequency,
            'reaction_improved': reaction_frequency >= expected_reaction_freq * 0.8,  # 80% do target
            'reply_improved': reply_frequency >= expected_reply_freq * 0.8,
            'expected_reaction_freq': expected_reaction_freq,
            'expected_reply_freq': expected_reply_freq
        }
    
    async def generate_comprehensive_report(self, reaction_results: List, reply_results: List, frequency_results: Dict) -> Dict[str, Any]:
        """Gera relatório completo dos testes"""
        
        # Analisar resultados de reações
        reaction_passed = sum(1 for r in reaction_results if r.get('test_passed', False))
        reaction_total = len(reaction_results)
        reaction_success_rate = (reaction_passed / reaction_total * 100) if reaction_total > 0 else 0
        
        # Analisar resultados de replies
        reply_passed = sum(1 for r in reply_results if r.get('test_passed', False))
        reply_total = len(reply_results)
        reply_success_rate = (reply_passed / reply_total * 100) if reply_total > 0 else 0
        
        # Status geral
        overall_success = (reaction_success_rate >= 80 and reply_success_rate >= 80 and 
                          frequency_results['reaction_improved'] and frequency_results['reply_improved'])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_success': overall_success,
            'reaction_tests': {
                'passed': reaction_passed,
                'total': reaction_total,
                'success_rate': reaction_success_rate,
                'details': reaction_results
            },
            'reply_tests': {
                'passed': reply_passed,
                'total': reply_total,
                'success_rate': reply_success_rate,
                'details': reply_results
            },
            'frequency_analysis': frequency_results,
            'improvements_detected': {
                'reaction_system': reaction_success_rate >= 80,
                'reply_system': reply_success_rate >= 80,
                'frequency_boost': (frequency_results['reaction_improved'] and frequency_results['reply_improved'])
            }
        }

async def main():
    """Função principal de teste"""
    
    logger.info("🚀 INICIANDO TESTE SISTEMA REAÇÕES E REPLIES - NOVA ESTRATÉGIA")
    logger.info("="*80)
    
    tester = ReactionsRepliesSystemTester()
    
    try:
        # Inicializar AgenticSDR
        logger.info("🤖 Inicializando AgenticSDR com nova estratégia...")
        sdr_agent = await create_agentic_sdr()
        logger.info("✅ AgenticSDR pronto para testes!")
        
        # 1. TESTAR CENÁRIOS DE REAÇÕES
        logger.info("\\n" + "="*60)
        logger.info("📱 FASE 1: TESTANDO SISTEMA DE REAÇÕES")
        logger.info("="*60)
        reaction_results = await tester.test_reaction_scenarios(sdr_agent)
        
        # 2. TESTAR CENÁRIOS DE REPLIES
        logger.info("\\n" + "="*60)
        logger.info("💬 FASE 2: TESTANDO SISTEMA DE REPLIES")
        logger.info("="*60)
        reply_results = await tester.test_reply_scenarios(sdr_agent)
        
        # 3. TESTAR MELHORIA DE FREQUÊNCIA
        logger.info("\\n" + "="*60)
        logger.info("📊 FASE 3: TESTANDO FREQUÊNCIA DE INTERAÇÕES")
        logger.info("="*60)
        frequency_results = await tester.test_frequency_improvement(sdr_agent)
        
        # 4. GERAR RELATÓRIO FINAL
        logger.info("\\n" + "="*60)
        logger.info("📋 GERANDO RELATÓRIO FINAL")
        logger.info("="*60)
        final_report = await tester.generate_comprehensive_report(reaction_results, reply_results, frequency_results)
        
        # 5. EXIBIR RESULTADOS
        logger.info("\\n" + "="*80)
        logger.info("🎯 RELATÓRIO FINAL - SISTEMA REAÇÕES E REPLIES")
        logger.info("="*80)
        
        logger.info(f"📱 REAÇÕES:")
        logger.info(f"   ✅ Testes Passou: {final_report['reaction_tests']['passed']}/{final_report['reaction_tests']['total']}")
        logger.info(f"   📊 Taxa Sucesso: {final_report['reaction_tests']['success_rate']:.1f}%")
        
        logger.info(f"💬 REPLIES:")
        logger.info(f"   ✅ Testes Passou: {final_report['reply_tests']['passed']}/{final_report['reply_tests']['total']}")
        logger.info(f"   📊 Taxa Sucesso: {final_report['reply_tests']['success_rate']:.1f}%")
        
        logger.info(f"📈 FREQUÊNCIA:")
        logger.info(f"   📱 Reações: {frequency_results['reaction_frequency']:.1f}% (Target: {frequency_results['expected_reaction_freq']}%)")
        logger.info(f"   💬 Replies: {frequency_results['reply_frequency']:.1f}% (Target: {frequency_results['expected_reply_freq']}%)")
        
        logger.info(f"\\n🎯 MELHORIAS DETECTADAS:")
        for improvement, status in final_report['improvements_detected'].items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {improvement}: {'Sim' if status else 'Não'}")
        
        if final_report['overall_success']:
            logger.info("\\n🎉 SISTEMA 100% VALIDADO - NATURALIDADE MASSIVAMENTE MELHORADA!")
            logger.info("✨ Helen agora usa reações e replies de forma inteligente e natural!")
        else:
            logger.warning("\\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL - AJUSTES NECESSÁRIOS")
        
        # Salvar relatório detalhado
        with open('/Users/adm/Downloads/1. NitroX Agentics/SDR IA SolarPrime v0.2/REPORT_REACTIONS_REPLIES.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\\n📄 Relatório salvo: REPORT_REACTIONS_REPLIES.json")
        
        return final_report['overall_success']
        
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)