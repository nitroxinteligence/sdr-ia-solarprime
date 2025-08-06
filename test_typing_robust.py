#!/usr/bin/env python3
"""
TESTE ROBUSTO - Sistema de Typing SDR IA SolarPrime
Validação completa de todos os componentes e cenários
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_section(text):
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}▶ {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

class TypingSystemTest:
    """Classe principal para testes robustos do sistema de typing"""
    
    def __init__(self):
        self.test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "errors": []
        }
        
    async def run_all_tests(self):
        """Executa todos os testes do sistema"""
        print_header("TESTE ROBUSTO - SISTEMA DE TYPING")
        print_info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Teste de Configurações
        await self.test_configurations()
        
        # 2. Teste do TypingController
        await self.test_typing_controller()
        
        # 3. Teste de Integração com Evolution API
        await self.test_evolution_integration()
        
        # 4. Teste do Webhook
        await self.test_webhook_behavior()
        
        # 5. Teste de Cenários Reais
        await self.test_real_scenarios()
        
        # 6. Teste de Performance
        await self.test_performance()
        
        # 7. Teste de Edge Cases
        await self.test_edge_cases()
        
        # Relatório Final
        self.generate_report()
    
    async def test_configurations(self):
        """Testa todas as configurações do sistema"""
        print_section("1. TESTE DE CONFIGURAÇÕES")
        
        try:
            from app.config import settings
            
            # Verificar configurações críticas
            tests = [
                ("enable_typing_simulation", True, "Typing deve estar habilitado"),
                ("simulate_reading_time", False, "Tempo de leitura deve estar DESABILITADO"),
                ("typing_duration_base", lambda x: x > 0, "Duração base deve ser positiva"),
                ("typing_duration_per_char", lambda x: x > 0, "Duração por char deve ser positiva"),
                ("typing_duration_max", lambda x: x > 0, "Duração máxima deve ser positiva"),
            ]
            
            for attr, expected, desc in tests:
                self.test_results["total"] += 1
                value = getattr(settings, attr, None)
                
                if callable(expected):
                    passed = expected(value) if value is not None else False
                else:
                    passed = value == expected
                
                if passed:
                    print_success(f"{attr}: {value} - {desc}")
                    self.test_results["passed"] += 1
                else:
                    print_error(f"{attr}: {value} (esperado: {expected}) - {desc}")
                    self.test_results["failed"] += 1
                    self.test_results["errors"].append(f"Config {attr}: {value} != {expected}")
                    
        except Exception as e:
            print_error(f"Erro ao testar configurações: {e}")
            self.test_results["errors"].append(f"Config error: {str(e)}")
    
    async def test_typing_controller(self):
        """Testa o TypingController em detalhes"""
        print_section("2. TESTE DO TYPING CONTROLLER")
        
        try:
            from app.services.typing_controller import typing_controller, TypingContext, TypingDecision
            
            # Cenários de teste
            scenarios = [
                (TypingContext.USER_MESSAGE, 100, False, "Usuário enviando mensagem"),
                (TypingContext.AGENT_RESPONSE, 100, True, "Agente respondendo"),
                (TypingContext.SYSTEM_MESSAGE, 100, False, "Mensagem do sistema"),
                (TypingContext.MEDIA_UPLOAD, 100, False, "Upload de mídia"),
            ]
            
            for context, msg_len, should_show, desc in scenarios:
                self.test_results["total"] += 1
                decision = typing_controller.should_show_typing(context, msg_len)
                
                if decision.should_show == should_show:
                    print_success(f"{desc}: should_show={decision.should_show} ✓")
                    if decision.duration:
                        print_info(f"  Duração calculada: {decision.duration}s")
                    print_info(f"  Motivo: {decision.reason}")
                    self.test_results["passed"] += 1
                else:
                    print_error(f"{desc}: should_show={decision.should_show} (esperado: {should_show})")
                    self.test_results["failed"] += 1
                    self.test_results["errors"].append(f"TypingController {context}: {decision.should_show} != {should_show}")
            
            # Teste de cálculo de duração
            print_info("\nTestando cálculo de duração:")
            test_lengths = [0, 50, 100, 350, 1000]
            for length in test_lengths:
                decision = typing_controller.should_show_typing(TypingContext.AGENT_RESPONSE, length)
                print_info(f"  {length} chars → {decision.duration}s")
                
        except Exception as e:
            print_error(f"Erro ao testar TypingController: {e}")
            self.test_results["errors"].append(f"TypingController error: {str(e)}")
    
    async def test_evolution_integration(self):
        """Testa integração com Evolution API"""
        print_section("3. TESTE DE INTEGRAÇÃO COM EVOLUTION API")
        
        try:
            from app.integrations.evolution import EvolutionAPIClient
            
            # Mock do httpx
            with patch('app.integrations.evolution.httpx.AsyncClient') as mock_client:
                # Configurar mock
                mock_async_client = MagicMock()
                mock_client.return_value.__aenter__.return_value = mock_async_client
                
                # Mock da resposta
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json = Mock(return_value={"success": True})
                mock_response.raise_for_status = Mock()
                
                # Fazer request retornar a resposta mockada
                mock_async_client.request = AsyncMock(return_value=mock_response)
                
                # Criar cliente
                evolution = EvolutionAPIClient()
                
                # Teste 1: send_typing com user_message (não deve chamar API)
                self.test_results["total"] += 1
                await evolution.send_typing("5511999999999", 100, context="user_message")
                
                if mock_async_client.request.call_count == 0:
                    print_success("send_typing(user_message): Nenhuma chamada à API ✓")
                    self.test_results["passed"] += 1
                else:
                    print_error("send_typing(user_message): Chamou API quando não deveria")
                    self.test_results["failed"] += 1
                
                # Reset mock
                mock_async_client.request.reset_mock()
                
                # Teste 2: send_typing com agent_response (deve chamar API)
                self.test_results["total"] += 1
                await evolution.send_typing("5511999999999", 100, context="agent_response")
                
                # Pequeno delay para garantir que async terminou
                await asyncio.sleep(0.1)
                
                if mock_async_client.request.call_count > 0:
                    print_success("send_typing(agent_response): Chamou API corretamente ✓")
                    self.test_results["passed"] += 1
                    
                    # Verificar payload
                    call_args = mock_async_client.request.call_args
                    if call_args:
                        payload = call_args.kwargs.get('json', {})
                        print_info(f"  Payload enviado: {json.dumps(payload, indent=2)}")
                else:
                    print_error("send_typing(agent_response): Não chamou API")
                    self.test_results["failed"] += 1
                    
        except Exception as e:
            print_error(f"Erro ao testar integração Evolution: {e}")
            self.test_results["errors"].append(f"Evolution integration error: {str(e)}")
    
    async def test_webhook_behavior(self):
        """Testa comportamento do webhook"""
        print_section("4. TESTE DO WEBHOOK")
        
        try:
            # Verificar se código problemático foi removido
            self.test_results["total"] += 1
            
            with open("app/api/webhooks.py", "r") as f:
                webhook_content = f.read()
                
            # Verificar que não há mais simulate_reading_time ativo
            lines = webhook_content.split('\n')
            problematic_lines = []
            
            for i, line in enumerate(lines, 1):
                if "simulate_reading_time" in line and "REMOVIDO" not in line and "#" not in line:
                    problematic_lines.append((i, line.strip()))
            
            if not problematic_lines:
                print_success("Webhook não tem mais código de simulate_reading_time ativo ✓")
                self.test_results["passed"] += 1
                
                # Verificar se tem comentário explicativo
                if "REMOVIDO:" in webhook_content and "tempo de leitura" in webhook_content:
                    print_info("  Encontrado comentário explicativo sobre remoção")
            else:
                print_error("Webhook ainda tem código problemático:")
                for line_num, line in problematic_lines:
                    print_error(f"  Linha {line_num}: {line}")
                self.test_results["failed"] += 1
                
        except Exception as e:
            print_error(f"Erro ao testar webhook: {e}")
            self.test_results["errors"].append(f"Webhook test error: {str(e)}")
    
    async def test_real_scenarios(self):
        """Testa cenários reais de uso"""
        print_section("5. TESTE DE CENÁRIOS REAIS")
        
        scenarios = [
            {
                "name": "Usuário envia 'Oi'",
                "context": "user_message",
                "message": "Oi",
                "should_show_typing": False
            },
            {
                "name": "Agente responde com mensagem curta",
                "context": "agent_response",
                "message": "Olá! Como posso ajudar?",
                "should_show_typing": True
            },
            {
                "name": "Usuário envia áudio",
                "context": "user_message",
                "message": "[Áudio transcrito]: Quero saber sobre energia solar",
                "should_show_typing": False
            },
            {
                "name": "Agente responde com mensagem longa",
                "context": "agent_response",
                "message": "A energia solar é uma excelente opção..." + "texto longo" * 50,
                "should_show_typing": True
            }
        ]
        
        from app.services.typing_controller import typing_controller, TypingContext
        
        for scenario in scenarios:
            self.test_results["total"] += 1
            
            context_map = {
                "user_message": TypingContext.USER_MESSAGE,
                "agent_response": TypingContext.AGENT_RESPONSE,
                "system_message": TypingContext.SYSTEM_MESSAGE
            }
            
            context = context_map.get(scenario["context"], TypingContext.SYSTEM_MESSAGE)
            decision = typing_controller.should_show_typing(context, len(scenario["message"]))
            
            if decision.should_show == scenario["should_show_typing"]:
                print_success(f"{scenario['name']}: Comportamento correto ✓")
                self.test_results["passed"] += 1
            else:
                print_error(f"{scenario['name']}: Comportamento incorreto")
                self.test_results["failed"] += 1
    
    async def test_performance(self):
        """Testa performance do sistema"""
        print_section("6. TESTE DE PERFORMANCE")
        
        import time
        from app.services.typing_controller import typing_controller, TypingContext
        
        # Teste de velocidade de decisão
        self.test_results["total"] += 1
        
        iterations = 1000
        start = time.time()
        
        for _ in range(iterations):
            typing_controller.should_show_typing(TypingContext.AGENT_RESPONSE, 100)
        
        elapsed = time.time() - start
        avg_time = (elapsed / iterations) * 1000  # em ms
        
        print_info(f"Tempo médio por decisão: {avg_time:.3f}ms ({iterations} iterações)")
        
        if avg_time < 1.0:  # Menos de 1ms é excelente
            print_success("Performance excelente! ✓")
            self.test_results["passed"] += 1
        elif avg_time < 10.0:  # Menos de 10ms é aceitável
            print_warning("Performance aceitável")
            self.test_results["passed"] += 1
            self.test_results["warnings"] += 1
        else:
            print_error("Performance precisa melhorar")
            self.test_results["failed"] += 1
    
    async def test_edge_cases(self):
        """Testa casos extremos"""
        print_section("7. TESTE DE EDGE CASES")
        
        from app.services.typing_controller import typing_controller, TypingContext
        
        edge_cases = [
            ("Mensagem vazia", "", 0),
            ("Mensagem gigante", "x" * 10000, 10000),
            ("Caracteres especiais", "🚀💡✨" * 10, 30),
            ("Quebras de linha", "linha1\nlinha2\nlinha3", 20),
        ]
        
        for name, message, length in edge_cases:
            self.test_results["total"] += 1
            
            try:
                decision = typing_controller.should_show_typing(TypingContext.AGENT_RESPONSE, length)
                print_success(f"{name}: Processado sem erros ✓ (duração: {decision.duration}s)")
                self.test_results["passed"] += 1
            except Exception as e:
                print_error(f"{name}: Erro ao processar - {e}")
                self.test_results["failed"] += 1
    
    def generate_report(self):
        """Gera relatório final dos testes"""
        print_header("RELATÓRIO FINAL")
        
        # Estatísticas
        success_rate = (self.test_results["passed"] / self.test_results["total"] * 100) if self.test_results["total"] > 0 else 0
        
        print_info(f"Total de testes: {self.test_results['total']}")
        print_success(f"Testes aprovados: {self.test_results['passed']}")
        print_error(f"Testes falhados: {self.test_results['failed']}")
        print_warning(f"Avisos: {self.test_results['warnings']}")
        
        print(f"\n{Colors.BOLD}Taxa de sucesso: {success_rate:.1f}%{Colors.ENDC}")
        
        # Status final
        if success_rate == 100:
            print_header("✅ SISTEMA 100% VALIDADO!")
            print_success("O sistema de typing está funcionando perfeitamente!")
        elif success_rate >= 90:
            print_header("⚠️  SISTEMA FUNCIONAL COM PEQUENOS PROBLEMAS")
            print_warning("O sistema está funcional mas precisa de ajustes menores.")
        else:
            print_header("❌ SISTEMA COM PROBLEMAS CRÍTICOS")
            print_error("O sistema precisa de correções antes do deploy!")
        
        # Erros encontrados
        if self.test_results["errors"]:
            print_section("ERROS ENCONTRADOS:")
            for error in self.test_results["errors"]:
                print_error(f"  • {error}")
        
        # Recomendações
        print_section("RECOMENDAÇÕES:")
        if success_rate == 100:
            print_success("  • Sistema pronto para deploy em produção")
            print_success("  • Continuar monitorando logs após deploy")
        else:
            print_warning("  • Corrigir os erros encontrados antes do deploy")
            print_warning("  • Executar os testes novamente após correções")
        
        print(f"\n{Colors.OKCYAN}Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")

# Executar os testes
async def main():
    test_suite = TypingSystemTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())