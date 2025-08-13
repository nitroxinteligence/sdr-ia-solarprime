"""
🧪 TESTE SIMPLIFICADO: Integração KommoCRM com Sistema Refatorado
Testa movimentação real de cards usando apenas os módulos existentes
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Importações do sistema - APENAS MÓDULOS QUE EXISTEM
from app.agents.agentic_sdr_refactored import get_agentic_agent
from app.teams.sdr_team import SDRTeam
from app.services.crm_service_100_real import CRMServiceReal
from app.integrations.supabase_client import supabase_client
from app.utils.logger import emoji_logger
from app.config import settings

class KommoSimpleTest:
    """Teste simplificado da integração Kommo"""
    
    def __init__(self):
        self.crm_service = CRMServiceReal()
        self.sdr_team = SDRTeam()
        self.agent = None
        self.test_results = []
        
    async def setup(self):
        """Inicializa componentes"""
        emoji_logger.system_info("🚀 TESTE SIMPLIFICADO KOMMOCRM")
        emoji_logger.system_info("=" * 60)
        
        try:
            # Criar agente
            self.agent = await get_agentic_agent()
            emoji_logger.system_success("✅ AgenticSDR Refactored criado")
            
            # Inicializar CRM
            await self.crm_service.initialize()
            emoji_logger.system_success("✅ CRM Service inicializado")
            
            return True
            
        except Exception as e:
            emoji_logger.system_error("Setup", f"Erro no setup: {e}")
            return False
    
    async def test_create_and_move_lead(self):
        """Testa criação de lead e movimentação básica"""
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 1: CRIAR E MOVER LEAD")
        emoji_logger.system_info("-" * 40)
        
        try:
            # Criar lead
            test_phone = f"5511999{datetime.now().strftime('%H%M%S')}"
            test_name = f"Teste Simples {datetime.now().strftime('%H:%M')}"
            
            emoji_logger.system_info(f"📝 Criando lead: {test_name}")
            
            # Usar método real do CRM service
            lead_data = {
                "phone": test_phone,
                "name": test_name,
                "email": f"teste{datetime.now().strftime('%H%M%S')}@test.com",
                "source": "teste_automatizado"
            }
            result = await self.crm_service.create_or_update_lead(lead_data)
            
            # O método retorna um dict com success e lead_id
            if result and isinstance(result, dict):
                if result.get("success") and result.get("lead_id"):
                    lead_id = str(result["lead_id"])
                    emoji_logger.system_success(f"✅ Lead criado: ID={lead_id}")
                else:
                    emoji_logger.system_error("Test", f"Falha ao criar lead: {result.get('message', 'Erro desconhecido')}")
                    return False
            else:
                emoji_logger.system_error("Test", f"Resultado inesperado: {result}")
                return False
            
            # Testar movimentação para "Em Qualificação"
            emoji_logger.system_info("📍 Movendo para EM QUALIFICAÇÃO...")
            
            update_result = await self.crm_service.update_lead_stage(
                lead_id=lead_id,
                stage="em_qualificacao",
                notes="Teste automatizado - movendo para qualificação"
            )
            
            if update_result.get("success"):
                emoji_logger.system_success("✅ Lead movido para EM QUALIFICAÇÃO")
                
                # Mover para QUALIFICADO
                emoji_logger.system_info("📍 Movendo para QUALIFICADO...")
                
                update_result = await self.crm_service.update_lead_stage(
                    lead_id=lead_id,
                    stage="qualificado",
                    notes="Teste automatizado - lead qualificado"
                )
                
                if update_result.get("success"):
                    emoji_logger.system_success("✅ Lead movido para QUALIFICADO")
                    return True
                else:
                    emoji_logger.system_error("Test", "Falha ao mover para QUALIFICADO")
                    return False
            else:
                emoji_logger.system_error("Test", "Falha ao mover para EM QUALIFICAÇÃO")
                return False
                
        except Exception as e:
            emoji_logger.system_error("Test", f"Erro no teste: {e}")
            return False
    
    async def test_agent_conversation(self):
        """Testa conversa simples com o agente"""
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 2: CONVERSA COM AGENTE")
        emoji_logger.system_info("-" * 40)
        
        try:
            test_phone = f"5511998{datetime.now().strftime('%H%M%S')}"
            
            # Criar lead no Supabase
            emoji_logger.system_info("📝 Criando lead no Supabase...")
            
            lead_data = await supabase_client.create_lead({
                "phone_number": test_phone,
                "name": "Teste Conversa",
                "qualification_score": 0
            })
            
            if not lead_data:
                emoji_logger.system_error("Test", "Falha ao criar lead no Supabase")
                return False
            
            emoji_logger.system_success(f"✅ Lead criado no Supabase: {lead_data.get('id')}")
            
            # Criar conversa
            conversation = await supabase_client.get_or_create_conversation(
                test_phone,
                lead_data["id"]
            )
            
            if not conversation:
                emoji_logger.system_error("Test", "Falha ao criar conversa")
                return False
            
            emoji_logger.system_success(f"✅ Conversa criada: {conversation.get('id')}")
            
            # Simular mensagens
            messages = [
                "Olá, quero saber sobre energia solar",
                "Meu nome é João Teste",
                "Pago R$ 5000 de energia"
            ]
            
            for msg in messages:
                emoji_logger.system_info(f"💬 Enviando: {msg}")
                
                # AgenticSDR Refactored usa metadata
                metadata = {
                    "phone": test_phone,
                    "lead_data": lead_data,
                    "conversation_id": conversation["id"]
                }
                
                response = await self.agent.process_message(
                    message=msg,
                    metadata=metadata
                )
                
                if response:
                    if isinstance(response, dict):
                        emoji_logger.system_debug(
                            f"🤖 Resposta: {response.get('response', '')[:100]}..."
                        )
                        emoji_logger.system_debug(
                            f"📊 Score: {response.get('qualification_score', 0)}"
                        )
                    else:
                        emoji_logger.system_debug(f"🤖 Resposta: {str(response)[:100]}...")
                else:
                    emoji_logger.system_warning("Resposta vazia do agente")
                
                await asyncio.sleep(1)
            
            emoji_logger.system_success("✅ Conversa processada com sucesso")
            return True
            
        except Exception as e:
            emoji_logger.system_error("Test", f"Erro no teste de conversa: {e}")
            return False
    
    async def test_sdr_team_integration(self):
        """Testa integração com SDR Team"""
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 3: SDR TEAM INTEGRATION")
        emoji_logger.system_info("-" * 40)
        
        try:
            # Verificar se SDR Team está disponível
            emoji_logger.system_info("🤝 Verificando SDR Team...")
            
            # Testar CRM Agent
            if hasattr(self.sdr_team, 'crm_agent'):
                emoji_logger.system_success("✅ CRM Agent disponível")
                
                # Testar criação de lead via team
                test_result = await self.sdr_team.crm_agent.create_or_update_lead({
                    "phone": f"5511997{datetime.now().strftime('%H%M%S')}",
                    "name": "Teste SDR Team",
                    "email": "teste_team@test.com",
                    "source": "teste_sdr_team"
                })
                
                if test_result.get("success"):
                    emoji_logger.system_success("✅ Lead criado via SDR Team")
                else:
                    emoji_logger.system_warning("⚠️ Falha ao criar lead via team")
            else:
                emoji_logger.system_warning("⚠️ CRM Agent não disponível no SDR Team")
            
            # Testar Follow-up Agent
            if hasattr(self.sdr_team, 'followup_agent'):
                emoji_logger.system_success("✅ Follow-up Agent disponível")
            else:
                emoji_logger.system_warning("⚠️ Follow-up Agent não disponível")
            
            # Testar Calendar Agent
            if hasattr(self.sdr_team, 'calendar_agent'):
                emoji_logger.system_success("✅ Calendar Agent disponível")
            else:
                emoji_logger.system_warning("⚠️ Calendar Agent não disponível")
            
            return True
            
        except Exception as e:
            emoji_logger.system_error("Test", f"Erro no teste SDR Team: {e}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        
        # Setup inicial
        if not await self.setup():
            emoji_logger.system_error("Test", "Setup falhou - abortando testes")
            return False
        
        results = {
            "create_and_move": False,
            "agent_conversation": False,
            "sdr_team": False
        }
        
        try:
            # Executar testes
            results["create_and_move"] = await self.test_create_and_move_lead()
            await asyncio.sleep(2)
            
            results["agent_conversation"] = await self.test_agent_conversation()
            await asyncio.sleep(2)
            
            results["sdr_team"] = await self.test_sdr_team_integration()
            
        except Exception as e:
            emoji_logger.system_error("Test Suite", f"Erro crítico: {e}")
        
        # Relatório final
        emoji_logger.system_info("")
        emoji_logger.system_info("=" * 60)
        emoji_logger.system_info("📊 RELATÓRIO FINAL")
        emoji_logger.system_info("=" * 60)
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        
        for test_name, result in results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            emoji_logger.system_info(f"{status} - {test_name}")
        
        emoji_logger.system_info("")
        emoji_logger.system_info(f"📈 RESULTADO: {passed}/{total} testes passaram")
        
        if passed == total:
            emoji_logger.system_success("🎉 TODOS OS TESTES PASSARAM!")
            emoji_logger.system_success("✅ Sistema funcionando corretamente!")
        else:
            emoji_logger.system_warning(f"⚠️ {total - passed} testes falharam")
        
        # Salvar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": f"{(passed/total*100) if total > 0 else 0:.1f}%"
        }
        
        with open("test_kommo_simple_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        emoji_logger.system_info("📝 Relatório salvo: test_kommo_simple_report.json")
        
        return passed == total

async def main():
    """Execução principal"""
    tester = KommoSimpleTest()
    success = await tester.run_all_tests()
    
    # Aguardar um pouco para permitir limpeza de recursos
    await asyncio.sleep(0.5)
    
    import sys
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
    except RuntimeError as e:
        if "Event loop is closed" not in str(e):
            raise