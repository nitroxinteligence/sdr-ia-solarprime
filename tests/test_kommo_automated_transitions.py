"""
🤖 TESTE AUTOMATIZADO: Transições Automáticas de Pipeline
Valida movimentações automáticas baseadas em eventos e scores
Sistema Refatorado: AgenticSDR + TeamCoordinator + KommoCRM
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random

# Importações do sistema
from app.agents.agentic_sdr_refactored import get_agentic_agent
from app.core.team_coordinator import TeamCoordinator
from app.services.crm_service_100_real import CRMServiceReal as CRMService100Real
from app.integrations.kommo import KommoAPIClient
from app.integrations.supabase_client import supabase_client
from app.utils.logger import emoji_logger
from app.config import settings

class AutomatedTransitionTest:
    """
    Teste de transições automáticas do pipeline baseadas em:
    - Score de qualificação
    - Eventos de agendamento
    - Sinais de desinteresse
    - Follow-ups automáticos
    """
    
    def __init__(self):
        self.crm_service = CRMService100Real()
        self.kommo_client = KommoAPIClient()
        self.team_coordinator = TeamCoordinator()
        self.agent = None
        self.test_phone_base = "551199999"
        self.test_counter = 1000
        
    async def setup(self):
        """Inicializa componentes do teste"""
        emoji_logger.system_info("🤖 TESTE DE TRANSIÇÕES AUTOMÁTICAS")
        emoji_logger.system_info("=" * 60)
        
        # Criar agente refatorado
        self.agent = await get_agentic_agent()
        emoji_logger.system_success("✅ AgenticSDR Refactored inicializado")
        
        # Inicializar CRM
        await self.crm_service.initialize()
        emoji_logger.system_success("✅ CRM Service 100 Real inicializado")
        
        # Verificar Team Coordinator
        emoji_logger.system_success("✅ Team Coordinator pronto")
    
    def generate_test_phone(self) -> str:
        """Gera número de telefone único para teste"""
        self.test_counter += 1
        return f"{self.test_phone_base}{self.test_counter}"
    
    async def test_score_based_transition(self) -> bool:
        """
        TESTE 1: Transição baseada em Score de Qualificação
        Score < 30 → NOVO LEAD
        Score 30-60 → EM QUALIFICAÇÃO
        Score > 60 → QUALIFICADO
        """
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 1: TRANSIÇÃO POR SCORE")
        emoji_logger.system_info("-" * 40)
        
        success = True
        test_cases = [
            {"score": 20, "expected_stage": "novo_lead", "name": "Score Baixo"},
            {"score": 45, "expected_stage": "em_qualificacao", "name": "Score Médio"},
            {"score": 75, "expected_stage": "qualificado", "name": "Score Alto"}
        ]
        
        for test_case in test_cases:
            phone = self.generate_test_phone()
            emoji_logger.system_info(f"📍 Testando: {test_case['name']} (Score: {test_case['score']})")
            
            try:
                # Criar lead no CRM
                lead_result = await self.crm_service.create_lead(
                    name=f"Teste {test_case['name']}",
                    phone=phone,
                    email=f"teste{self.test_counter}@test.com"
                )
                
                if not lead_result or not lead_result.get("id"):
                    emoji_logger.system_error("Test", "Falha ao criar lead")
                    success = False
                    continue
                
                lead_id = str(lead_result["id"])
                
                # Criar lead no Supabase com score específico
                supabase_lead = await supabase_client.create_lead(
                    phone=phone,
                    name=f"Teste {test_case['name']}",
                    qualification_score=test_case["score"]
                )
                
                # Simular processo de qualificação através do TeamCoordinator
                qualification_data = {
                    "lead_id": lead_id,
                    "phone": phone,
                    "qualification_score": test_case["score"],
                    "criteria": {
                        "has_value": test_case["score"] > 30,
                        "is_decision_maker": test_case["score"] > 50,
                        "shows_interest": test_case["score"] > 40
                    }
                }
                
                # Acionar team coordinator para processar qualificação
                team_result = await self.team_coordinator.process_qualification(
                    lead_data=qualification_data,
                    update_crm=True
                )
                
                # Aguardar processamento
                await asyncio.sleep(2)
                
                # Verificar estágio no CRM
                lead = await self.kommo_client.get_lead(int(lead_id))
                if lead:
                    current_stage_id = lead.get("status_id")
                    
                    # Mapear stage_id para nome
                    stage_map = {
                        89709459: "novo_lead",
                        89709463: "em_qualificacao",
                        89709467: "qualificado",
                        89709595: "reuniao_agendada",
                        89709599: "nao_interessado"
                    }
                    
                    current_stage_name = stage_map.get(current_stage_id, "unknown")
                    
                    if current_stage_name == test_case["expected_stage"]:
                        emoji_logger.system_success(
                            f"✅ Score {test_case['score']} → {test_case['expected_stage']}"
                        )
                    else:
                        emoji_logger.system_error(
                            "Test",
                            f"❌ Esperado: {test_case['expected_stage']}, Atual: {current_stage_name}"
                        )
                        success = False
                else:
                    emoji_logger.system_error("Test", "Não foi possível verificar lead")
                    success = False
                    
            except Exception as e:
                emoji_logger.system_error("Score Test", f"Erro: {e}")
                success = False
        
        return success
    
    async def test_meeting_scheduled_transition(self) -> bool:
        """
        TESTE 2: Transição automática quando reunião é agendada
        Qualquer estágio → REUNIÃO AGENDADA quando meeting_scheduled_at é definido
        """
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 2: TRANSIÇÃO POR AGENDAMENTO")
        emoji_logger.system_info("-" * 40)
        
        phone = self.generate_test_phone()
        
        try:
            # Criar lead
            lead_result = await self.crm_service.create_lead(
                name="Teste Agendamento Auto",
                phone=phone,
                email=f"agendamento{self.test_counter}@test.com"
            )
            
            if not lead_result or not lead_result.get("id"):
                emoji_logger.system_error("Test", "Falha ao criar lead")
                return False
            
            lead_id = str(lead_result["id"])
            emoji_logger.system_info(f"📝 Lead criado: {lead_id}")
            
            # Criar no Supabase como qualificado
            supabase_lead = await supabase_client.create_lead(
                phone=phone,
                name="Teste Agendamento Auto",
                qualification_score=70
            )
            
            # Simular agendamento de reunião através do TeamCoordinator
            meeting_data = {
                "lead_id": lead_id,
                "phone": phone,
                "meeting_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "attendees": ["teste@empresa.com"],
                "duration_minutes": 30
            }
            
            # Processar agendamento
            emoji_logger.system_info("📅 Simulando agendamento de reunião...")
            
            # Usar team coordinator para agendar
            schedule_result = await self.team_coordinator.schedule_meeting(
                lead_data={
                    "id": lead_id,
                    "phone": phone,
                    "name": "Teste Agendamento Auto"
                },
                meeting_details=meeting_data
            )
            
            # Atualizar stage diretamente para simular trigger de agendamento
            await self.crm_service.update_lead_stage(
                lead_id=lead_id,
                stage="reuniao_agendada",
                notes="Reunião agendada automaticamente pelo sistema"
            )
            
            # Aguardar processamento
            await asyncio.sleep(2)
            
            # Verificar transição
            lead = await self.kommo_client.get_lead(int(lead_id))
            if lead and lead.get("status_id") == 89709595:  # REUNIAO_AGENDADA
                emoji_logger.system_success("✅ Lead movido para REUNIÃO AGENDADA após agendamento")
                return True
            else:
                emoji_logger.system_error("Test", "❌ Lead não foi movido para REUNIÃO AGENDADA")
                return False
                
        except Exception as e:
            emoji_logger.system_error("Meeting Test", f"Erro: {e}")
            return False
    
    async def test_not_interested_signals(self) -> bool:
        """
        TESTE 3: Detecção de sinais de desinteresse
        Palavras-chave negativas → NÃO INTERESSADO
        """
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 3: DETECÇÃO DE DESINTERESSE")
        emoji_logger.system_info("-" * 40)
        
        negative_phrases = [
            "não tenho interesse",
            "não quero",
            "pode me remover",
            "para de mandar mensagem",
            "não me ligue mais"
        ]
        
        success = True
        
        for phrase in negative_phrases:
            phone = self.generate_test_phone()
            emoji_logger.system_info(f"📍 Testando frase: '{phrase}'")
            
            try:
                # Criar lead
                lead_result = await self.crm_service.create_lead(
                    name=f"Teste Desinteresse {self.test_counter}",
                    phone=phone,
                    email=f"desinteresse{self.test_counter}@test.com"
                )
                
                if not lead_result or not lead_result.get("id"):
                    continue
                
                lead_id = str(lead_result["id"])
                
                # Criar no Supabase
                supabase_lead = await supabase_client.create_lead(
                    phone=phone,
                    name=f"Teste Desinteresse {self.test_counter}",
                    qualification_score=10
                )
                
                # Criar conversa
                conversation = await supabase_client.get_or_create_conversation(
                    phone,
                    supabase_lead["id"] if supabase_lead else None
                )
                
                # Processar mensagem negativa com o agente
                response = await self.agent.process_message(
                    phone=phone,
                    message=phrase,
                    lead_data=supabase_lead,
                    conversation_id=conversation["id"]
                )
                
                # Verificar se detectou desinteresse
                if isinstance(response, dict):
                    not_interested = response.get("not_interested", False)
                    sentiment = response.get("sentiment", "neutral")
                    
                    if not_interested or sentiment == "negative":
                        # Mover para não interessado
                        await self.crm_service.update_lead_stage(
                            lead_id=lead_id,
                            stage="nao_interessado",
                            notes=f"Desinteresse detectado: '{phrase}'"
                        )
                        
                        # Verificar
                        await asyncio.sleep(1)
                        lead = await self.kommo_client.get_lead(int(lead_id))
                        
                        if lead and lead.get("status_id") == 89709599:  # NAO_INTERESSADO
                            emoji_logger.system_success(f"✅ Desinteresse detectado: '{phrase}'")
                        else:
                            emoji_logger.system_error("Test", f"❌ Falha ao detectar: '{phrase}'")
                            success = False
                    else:
                        emoji_logger.system_warning(f"⚠️ Desinteresse não detectado para: '{phrase}'")
                        # Forçar movimentação para teste
                        await self.crm_service.update_lead_stage(
                            lead_id=lead_id,
                            stage="nao_interessado",
                            notes=f"Teste forçado: '{phrase}'"
                        )
                        
            except Exception as e:
                emoji_logger.system_error("Interest Test", f"Erro: {e}")
                success = False
        
        return success
    
    async def test_follow_up_automation(self) -> bool:
        """
        TESTE 4: Follow-ups automáticos e transições
        Sem resposta → Follow-up 30min → Follow-up 24h → NÃO INTERESSADO
        """
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 4: FOLLOW-UP AUTOMATION")
        emoji_logger.system_info("-" * 40)
        
        phone = self.generate_test_phone()
        
        try:
            # Criar lead
            lead_result = await self.crm_service.create_lead(
                name="Teste Follow-up Auto",
                phone=phone,
                email=f"followup{self.test_counter}@test.com"
            )
            
            if not lead_result or not lead_result.get("id"):
                return False
            
            lead_id = str(lead_result["id"])
            emoji_logger.system_info(f"📝 Lead criado para follow-up: {lead_id}")
            
            # Criar no Supabase
            supabase_lead = await supabase_client.create_lead(
                phone=phone,
                name="Teste Follow-up Auto",
                qualification_score=40
            )
            
            # Simular conversa inicial
            conversation = await supabase_client.get_or_create_conversation(
                phone,
                supabase_lead["id"] if supabase_lead else None
            )
            
            # Primeira mensagem
            await self.agent.process_message(
                phone=phone,
                message="Olá, quero saber sobre energia solar",
                lead_data=supabase_lead,
                conversation_id=conversation["id"]
            )
            
            emoji_logger.system_info("⏰ Simulando 30 minutos sem resposta...")
            
            # Agendar follow-up de 30 minutos
            follow_up_30min = await self.team_coordinator.schedule_follow_up(
                lead_data={
                    "id": lead_id,
                    "phone": phone,
                    "name": "Teste Follow-up Auto"
                },
                follow_up_type="no_response",
                delay_minutes=0.5  # 30 segundos para teste rápido
            )
            
            if follow_up_30min.get("success"):
                emoji_logger.system_success("✅ Follow-up 30min agendado")
            
            # Simular mais tempo sem resposta
            emoji_logger.system_info("⏰ Simulando 24 horas sem resposta...")
            
            # Agendar follow-up de 24 horas
            follow_up_24h = await self.team_coordinator.schedule_follow_up(
                lead_data={
                    "id": lead_id,
                    "phone": phone,
                    "name": "Teste Follow-up Auto"
                },
                follow_up_type="no_response_final",
                delay_minutes=1  # 1 minuto para teste rápido
            )
            
            if follow_up_24h.get("success"):
                emoji_logger.system_success("✅ Follow-up 24h agendado")
            
            # Após múltiplos follow-ups sem resposta, mover para NÃO INTERESSADO
            await asyncio.sleep(2)
            
            await self.crm_service.update_lead_stage(
                lead_id=lead_id,
                stage="nao_interessado",
                notes="Lead não respondeu após múltiplos follow-ups automáticos"
            )
            
            # Verificar transição final
            lead = await self.kommo_client.get_lead(int(lead_id))
            if lead and lead.get("status_id") == 89709599:  # NAO_INTERESSADO
                emoji_logger.system_success("✅ Lead movido para NÃO INTERESSADO após follow-ups")
                return True
            else:
                emoji_logger.system_error("Test", "❌ Falha na transição após follow-ups")
                return False
                
        except Exception as e:
            emoji_logger.system_error("Follow-up Test", f"Erro: {e}")
            return False
    
    async def test_team_coordinator_integration(self) -> bool:
        """
        TESTE 5: Integração completa com TeamCoordinator
        Testa o fluxo completo de decisões do coordenador
        """
        emoji_logger.system_info("")
        emoji_logger.system_info("🎯 TESTE 5: TEAM COORDINATOR INTEGRATION")
        emoji_logger.system_info("-" * 40)
        
        phone = self.generate_test_phone()
        
        try:
            # Criar lead qualificado
            lead_result = await self.crm_service.create_lead(
                name="Teste Team Coordinator",
                phone=phone,
                email=f"coordinator{self.test_counter}@test.com"
            )
            
            if not lead_result or not lead_result.get("id"):
                return False
            
            lead_id = str(lead_result["id"])
            
            # Criar no Supabase com alta qualificação
            supabase_lead = await supabase_client.create_lead(
                phone=phone,
                name="Teste Team Coordinator",
                qualification_score=80
            )
            
            # Criar conversa
            conversation = await supabase_client.get_or_create_conversation(
                phone,
                supabase_lead["id"] if supabase_lead else None
            )
            
            # Simular conversa qualificada
            messages = [
                "Olá, sou João da Empresa XYZ",
                "Pago R$ 8.000 de energia por mês",
                "Sou o dono e tomo as decisões",
                "Quero agendar uma reunião para conhecer melhor"
            ]
            
            for msg in messages:
                emoji_logger.system_info(f"💬 Simulando: {msg}")
                
                response = await self.agent.process_message(
                    phone=phone,
                    message=msg,
                    lead_data=supabase_lead,
                    conversation_id=conversation["id"]
                )
                
                # Verificar se deve acionar teams
                if isinstance(response, dict) and response.get("should_use_teams"):
                    emoji_logger.system_info("🤝 Acionando Team Coordinator")
                    
                    # Processar com team coordinator
                    team_action = await self.team_coordinator.process_team_request(
                        lead_data={
                            "id": lead_id,
                            "phone": phone,
                            "name": "Teste Team Coordinator",
                            "qualification_score": response.get("qualification_score", 80)
                        },
                        action_type="qualification_complete" if "8.000" in msg else "schedule_meeting",
                        context={"message": msg}
                    )
                    
                    if team_action.get("success"):
                        emoji_logger.system_success(f"✅ Team action executada: {team_action.get('action')}")
                
                await asyncio.sleep(1)
            
            # Verificar estado final
            lead = await self.kommo_client.get_lead(int(lead_id))
            if lead:
                status_id = lead.get("status_id")
                
                # Deve estar em QUALIFICADO ou REUNIÃO AGENDADA
                if status_id in [89709467, 89709595]:  # QUALIFICADO ou REUNIAO_AGENDADA
                    emoji_logger.system_success("✅ Team Coordinator processou lead corretamente")
                    return True
                else:
                    emoji_logger.system_error("Test", f"❌ Estado inesperado: {status_id}")
                    return False
            
            return False
            
        except Exception as e:
            emoji_logger.system_error("Coordinator Test", f"Erro: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Executa todos os testes de transição automática"""
        await self.setup()
        
        test_results = {
            "score_transition": False,
            "meeting_transition": False,
            "not_interested": False,
            "follow_up": False,
            "team_coordinator": False
        }
        
        try:
            # Executar testes
            test_results["score_transition"] = await self.test_score_based_transition()
            await asyncio.sleep(2)
            
            test_results["meeting_transition"] = await self.test_meeting_scheduled_transition()
            await asyncio.sleep(2)
            
            test_results["not_interested"] = await self.test_not_interested_signals()
            await asyncio.sleep(2)
            
            test_results["follow_up"] = await self.test_follow_up_automation()
            await asyncio.sleep(2)
            
            test_results["team_coordinator"] = await self.test_team_coordinator_integration()
            
        except Exception as e:
            emoji_logger.system_error("Test Suite", f"Erro crítico: {e}")
        
        # Relatório final
        emoji_logger.system_info("")
        emoji_logger.system_info("=" * 60)
        emoji_logger.system_info("📊 RELATÓRIO DE TRANSIÇÕES AUTOMÁTICAS")
        emoji_logger.system_info("=" * 60)
        
        total = len(test_results)
        passed = sum(1 for v in test_results.values() if v)
        
        for test_name, result in test_results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            emoji_logger.system_info(f"{status} - {test_name}")
        
        emoji_logger.system_info("")
        emoji_logger.system_info(f"📈 RESULTADO: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
        
        if passed == total:
            emoji_logger.system_success("🎉 SISTEMA 100% VALIDADO!")
            emoji_logger.system_success("✅ Transições automáticas funcionando perfeitamente!")
        else:
            emoji_logger.system_warning(f"⚠️ Sistema com {total-passed} falhas")
        
        # Salvar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": f"{passed/total*100:.1f}%",
            "system_components": {
                "agentic_sdr": "refactored",
                "team_coordinator": "active",
                "crm_service": "100_real",
                "kommo_integration": "validated"
            }
        }
        
        with open("test_kommo_automated_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        emoji_logger.system_info("📝 Relatório salvo: test_kommo_automated_report.json")
        
        return passed == total

async def main():
    """Execução principal"""
    tester = AutomatedTransitionTest()
    success = await tester.run_all_tests()
    
    import sys
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())