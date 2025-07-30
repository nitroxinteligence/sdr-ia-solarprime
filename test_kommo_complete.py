#!/usr/bin/env python3
"""
Teste Completo - Integração Kommo CRM
=====================================
Testa TODAS as funcionalidades da integração com Kommo
"""

import asyncio
import sys
import random
import string
from datetime import datetime, timedelta
from loguru import logger
import os

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from services.kommo_auth_simple import KommoAuthSimple
from services.kommo_service import KommoService
from models.kommo_models import KommoLead, LeadStatus, SolutionType, TaskType, NoteType
from config.config import get_config


class KommoCompleteTest:
    """Testa todas as funcionalidades do Kommo CRM"""
    
    def __init__(self):
        self.config = get_config()
        self.kommo = KommoService()
        self.test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Dados de teste únicos
        self.test_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.test_phone = f"+5511998{random.randint(100000, 999999)}"
        self.test_name = f"Teste Completo {self.test_id}"
        self.test_lead_id = None
        self.test_contact_id = None
        
        logger.info(f"📋 ID do Teste: {self.test_id}")
        logger.info(f"📱 Telefone: {self.test_phone}")
    
    def log_test(self, name: str, success: bool, details: str = ""):
        """Registra resultado do teste"""
        self.test_results["total"] += 1
        
        if success:
            self.test_results["passed"] += 1
            logger.info(f"✅ {name}")
        else:
            self.test_results["failed"] += 1
            logger.error(f"❌ {name}")
        
        if details:
            logger.info(f"   → {details}")
        
        self.test_results["tests"].append({
            "name": name,
            "success": success,
            "details": details
        })
    
    async def test_1_authentication(self):
        """Teste 1: Autenticação com Long-Lived Token"""
        try:
            # Verificar se está usando o novo sistema
            auth = KommoAuthSimple(self.config)
            token = await auth.get_valid_token()
            
            if token and await auth.test_token():
                self.log_test("1. Autenticação", True, f"Token válido: {token[:30]}...")
            else:
                self.log_test("1. Autenticação", False, "Token inválido")
        except Exception as e:
            self.log_test("1. Autenticação", False, str(e))
    
    async def test_2_pipeline_config(self):
        """Teste 2: Configuração de Pipelines e Campos"""
        try:
            config = await self.kommo.get_pipeline_configuration()
            
            details = []
            if config.get("pipeline_id"):
                details.append(f"Pipeline: {config['pipeline_id']}")
            if config.get("stages"):
                details.append(f"Estágios: {len(config['stages'])}")
            if config.get("custom_fields"):
                details.append(f"Campos: {len(config['custom_fields'])}")
            
            self.log_test("2. Configuração Pipeline", True, " | ".join(details))
            
            # Mostrar estágios mapeados
            for stage, id in config.get("stages", {}).items():
                logger.info(f"   → {stage}: {id}")
                
        except Exception as e:
            self.log_test("2. Configuração Pipeline", False, str(e))
    
    async def test_3_create_lead(self):
        """Teste 3: Criar Lead Completo"""
        try:
            lead_data = KommoLead(
                name=self.test_name,
                phone=self.test_phone,
                whatsapp=self.test_phone,
                email=f"teste_{self.test_id}@kommo.test",
                energy_bill_value=1850.75,
                solution_type=SolutionType.OWN_PLANT,
                current_discount="15% com concorrente",
                competitor="Empresa Solar XYZ",
                qualification_score=92,
                ai_notes=f"Lead de teste completo - ID: {self.test_id}\nTeste realizado em: {datetime.now()}",
                tags=["Teste Completo", "Automação", f"ID_{self.test_id}", "Alta Prioridade"]
            )
            
            result = await self.kommo.create_or_update_lead(lead_data)
            
            if result and "id" in result:
                self.test_lead_id = result["id"]
                self.log_test("3. Criar Lead", True, f"Lead ID: {self.test_lead_id} - {self.test_name}")
            else:
                self.log_test("3. Criar Lead", False, "Lead não criado")
                
        except Exception as e:
            self.log_test("3. Criar Lead", False, str(e))
    
    async def test_4_find_lead(self):
        """Teste 4: Buscar Lead por WhatsApp"""
        try:
            # Aguardar indexação
            await asyncio.sleep(2)
            
            lead = await self.kommo.find_lead_by_whatsapp(self.test_phone)
            
            if lead:
                self.log_test("4. Buscar Lead", True, f"Encontrado: {lead['name']} (ID: {lead['id']})")
            else:
                self.log_test("4. Buscar Lead", False, "Lead não encontrado")
                
        except Exception as e:
            self.log_test("4. Buscar Lead", False, str(e))
    
    async def test_5_update_lead(self):
        """Teste 5: Atualizar Lead"""
        if not self.test_lead_id:
            self.log_test("5. Atualizar Lead", False, "Lead não criado anteriormente")
            return
        
        try:
            update_data = KommoLead(
                name=f"{self.test_name} - ATUALIZADO",
                phone=self.test_phone,
                whatsapp=self.test_phone,
                energy_bill_value=2500.00,
                solution_type=SolutionType.PARTNER_PLANT,
                qualification_score=98,
                ai_notes="Lead atualizado com sucesso\nValor aumentado\nMudou para usina parceira",
                tags=["Atualizado", "Valor Alto"]
            )
            
            result = await self.kommo.update_lead(self.test_lead_id, update_data)
            
            if result:
                self.log_test("5. Atualizar Lead", True, "Dados atualizados com sucesso")
            else:
                self.log_test("5. Atualizar Lead", False, "Falha na atualização")
                
        except Exception as e:
            self.log_test("5. Atualizar Lead", False, str(e))
    
    async def test_6_pipeline_stages(self):
        """Teste 6: Movimentar Lead entre Estágios"""
        if not self.test_lead_id:
            self.log_test("6. Movimentar Estágios", False, "Lead não criado")
            return
        
        try:
            stages = [
                (LeadStatus.IN_QUALIFICATION, "Em Qualificação"),
                (LeadStatus.QUALIFIED, "Qualificado"),
                (LeadStatus.MEETING_SCHEDULED, "Reunião Agendada")
            ]
            
            results = []
            for status, name in stages:
                success = await self.kommo.move_lead_stage(self.test_lead_id, status)
                results.append(f"{name}: {'✓' if success else '✗'}")
                await asyncio.sleep(1)
            
            all_success = all("✓" in r for r in results)
            self.log_test("6. Movimentar Estágios", all_success, " | ".join(results))
            
        except Exception as e:
            self.log_test("6. Movimentar Estágios", False, str(e))
    
    async def test_7_add_notes(self):
        """Teste 7: Adicionar Notas ao Lead"""
        if not self.test_lead_id:
            self.log_test("7. Adicionar Notas", False, "Lead não criado")
            return
        
        try:
            notes = [
                ("📝 Nota de qualificação", NoteType.COMMON),
                ("📞 Ligação realizada com sucesso", NoteType.CALL_OUT),
                ("💬 Cliente respondeu via WhatsApp", NoteType.SMS_IN)
            ]
            
            success_count = 0
            for text, note_type in notes:
                full_text = f"{text}\nTeste: {self.test_id}\nHora: {datetime.now()}"
                if await self.kommo.add_note(self.test_lead_id, full_text, note_type):
                    success_count += 1
            
            self.log_test("7. Adicionar Notas", 
                         success_count == len(notes), 
                         f"{success_count}/{len(notes)} notas adicionadas")
            
        except Exception as e:
            self.log_test("7. Adicionar Notas", False, str(e))
    
    async def test_8_add_tags(self):
        """Teste 8: Adicionar Tags ao Lead"""
        if not self.test_lead_id:
            self.log_test("8. Adicionar Tags", False, "Lead não criado")
            return
        
        try:
            tags = [
                "🔥 Lead Quente",
                "💰 Alto Valor",
                "✅ Qualificado",
                f"📅 {datetime.now().strftime('%Y-%m-%d')}"
            ]
            
            success = await self.kommo.add_tags_to_lead(self.test_lead_id, tags)
            self.log_test("8. Adicionar Tags", success, f"Tags: {', '.join(tags)}")
            
        except Exception as e:
            self.log_test("8. Adicionar Tags", False, str(e))
    
    async def test_9_create_contact(self):
        """Teste 9: Criar e Associar Contato"""
        if not self.test_lead_id:
            self.log_test("9. Criar Contato", False, "Lead não criado")
            return
        
        try:
            contact_data = {
                "name": f"Contato {self.test_name}",
                "phone": self.test_phone,
                "whatsapp": self.test_phone,
                "email": f"contato_{self.test_id}@kommo.test"
            }
            
            contact = await self.kommo.create_contact(contact_data)
            
            if contact and "id" in contact:
                self.test_contact_id = contact["id"]
                
                # Associar ao lead
                linked = await self.kommo.link_contact_to_lead(self.test_contact_id, self.test_lead_id)
                
                self.log_test("9. Criar Contato", linked, 
                             f"Contato {self.test_contact_id} {'associado' if linked else 'não associado'}")
            else:
                self.log_test("9. Criar Contato", False, "Contato não criado")
                
        except Exception as e:
            self.log_test("9. Criar Contato", False, str(e))
    
    async def test_10_schedule_meeting(self):
        """Teste 10: Agendar Reunião"""
        if not self.test_lead_id:
            self.log_test("10. Agendar Reunião", False, "Lead não criado")
            return
        
        try:
            # Agendar para amanhã às 15h
            meeting_time = datetime.now() + timedelta(days=1)
            meeting_time = meeting_time.replace(hour=15, minute=0, second=0, microsecond=0)
            
            success = await self.kommo.schedule_meeting(
                self.test_lead_id,
                meeting_time,
                f"Reunião de demonstração - Teste {self.test_id}"
            )
            
            self.log_test("10. Agendar Reunião", success, 
                         f"Agendada para {meeting_time.strftime('%d/%m/%Y %H:%M')}")
            
        except Exception as e:
            self.log_test("10. Agendar Reunião", False, str(e))
    
    async def test_11_get_lead_details(self):
        """Teste 11: Obter Detalhes Completos do Lead"""
        if not self.test_lead_id:
            self.log_test("11. Detalhes do Lead", False, "Lead não criado")
            return
        
        try:
            lead = await self.kommo.get_lead(self.test_lead_id)
            
            if lead:
                details = []
                details.append(f"Nome: {lead.get('name', 'N/A')}")
                details.append(f"Status: {lead.get('status_id', 'N/A')}")
                details.append(f"Pipeline: {lead.get('pipeline_id', 'N/A')}")
                
                # Verificar campos customizados
                custom_fields = lead.get('custom_fields_values', [])
                if custom_fields:
                    details.append(f"Campos Custom: {len(custom_fields)}")
                
                self.log_test("11. Detalhes do Lead", True, " | ".join(details))
            else:
                self.log_test("11. Detalhes do Lead", False, "Lead não encontrado")
                
        except Exception as e:
            self.log_test("11. Detalhes do Lead", False, str(e))
    
    async def test_12_search_slots(self):
        """Teste 12: Buscar Horários Disponíveis"""
        try:
            tomorrow = datetime.now() + timedelta(days=1)
            slots = await self.kommo.search_available_slots(tomorrow)
            
            if slots:
                self.log_test("12. Buscar Horários", True, 
                             f"{len(slots)} horários disponíveis para {tomorrow.strftime('%d/%m/%Y')}")
            else:
                self.log_test("12. Buscar Horários", False, "Nenhum horário disponível")
                
        except Exception as e:
            self.log_test("12. Buscar Horários", False, str(e))
    
    async def run_all_tests(self):
        """Executa todos os testes em sequência"""
        logger.info("=" * 80)
        logger.info("🧪 TESTE COMPLETO - INTEGRAÇÃO KOMMO CRM")
        logger.info("=" * 80)
        
        # Lista de todos os testes
        tests = [
            self.test_1_authentication,
            self.test_2_pipeline_config,
            self.test_3_create_lead,
            self.test_4_find_lead,
            self.test_5_update_lead,
            self.test_6_pipeline_stages,
            self.test_7_add_notes,
            self.test_8_add_tags,
            self.test_9_create_contact,
            self.test_10_schedule_meeting,
            self.test_11_get_lead_details,
            self.test_12_search_slots
        ]
        
        # Executar cada teste
        for test in tests:
            logger.info(f"\n{'─' * 60}")
            try:
                await test()
            except Exception as e:
                logger.error(f"Erro não tratado em {test.__name__}: {e}")
                self.log_test(test.__name__, False, f"Erro não tratado: {e}")
            
            # Pequena pausa entre testes
            await asyncio.sleep(1)
        
        # Exibir resumo
        self.print_summary()
    
    def print_summary(self):
        """Exibe resumo detalhado dos testes"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("=" * 80)
        
        logger.info(f"Total de testes: {self.test_results['total']}")
        logger.info(f"✅ Passaram: {self.test_results['passed']}")
        logger.info(f"❌ Falharam: {self.test_results['failed']}")
        
        if self.test_results['total'] > 0:
            success_rate = (self.test_results['passed'] / self.test_results['total']) * 100
            logger.info(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        # Listar testes que falharam
        failed = [t for t in self.test_results["tests"] if not t["success"]]
        if failed:
            logger.info("\n⚠️  Testes que falharam:")
            for test in failed:
                logger.info(f"   - {test['name']}: {test['details']}")
        
        # Informações de limpeza
        if self.test_lead_id:
            logger.info(f"\n🧹 Lead de teste criado:")
            logger.info(f"   - ID: {self.test_lead_id}")
            logger.info(f"   - Nome: {self.test_name}")
            logger.info(f"   - WhatsApp: {self.test_phone}")
            logger.info("   ⚠️  Lembre-se de excluir manualmente no Kommo!")
        
        logger.info("=" * 80)
        
        # Status final
        if self.test_results['failed'] == 0:
            logger.info("🎉 TODOS OS TESTES PASSARAM! Integração 100% funcional!")
        else:
            logger.warning("⚠️  Alguns testes falharam. Verifique os erros acima.")


async def main():
    """Função principal"""
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar token
    token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
    if not token:
        logger.error("❌ KOMMO_LONG_LIVED_TOKEN não encontrado no .env!")
        logger.info("   Execute: python setup_kommo_integration.py")
        return
    
    # Executar testes
    tester = KommoCompleteTest()
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")


if __name__ == "__main__":
    asyncio.run(main())