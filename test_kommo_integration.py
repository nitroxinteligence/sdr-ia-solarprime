#!/usr/bin/env python3
"""
Script de Teste Completo para Integração Kommo CRM
==================================================
Este script testa todas as funcionalidades da integração com Kommo CRM
usando as credenciais de produção do arquivo .env
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import random
import string

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from services.kommo_service import KommoService
from models.kommo_models import (
    KommoLead, LeadStatus, SolutionType, TaskType, NoteType
)
from config.config import get_config


class KommoIntegrationTester:
    """Classe para testar todas as funcionalidades do Kommo CRM"""
    
    def __init__(self):
        self.kommo = KommoService()
        self.config = get_config()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Gerar dados de teste únicos
        self.test_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.test_phone = f"+5511999{random.randint(100000, 999999)}"
        self.test_name = f"Teste {self.test_id}"
        self.test_lead_id = None
        self.test_contact_id = None
        
        logger.info(f"Iniciando testes com ID: {self.test_id}")
        logger.info(f"Telefone de teste: {self.test_phone}")
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado de um teste"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{status} - {test_name}")
        if details:
            logger.info(f"  Detalhes: {details}")
        
        self.test_results["tests"].append({
            "name": test_name,
            "success": success,
            "details": details
        })
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
    
    async def test_authentication(self):
        """Testa autenticação e obtenção de token"""
        test_name = "Autenticação OAuth"
        try:
            # Tentar obter token válido
            token = await self.kommo.auth.get_valid_token()
            
            if token:
                self.log_test(test_name, True, f"Token obtido: {token[:20]}...")
            else:
                self.log_test(test_name, False, "Falha ao obter token")
                
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_pipeline_configuration(self):
        """Testa carregamento de configurações do pipeline"""
        test_name = "Configuração de Pipeline"
        try:
            # Obter configuração do pipeline
            config = await self.kommo.get_pipeline_configuration()
            
            if config and "pipeline_id" in config:
                details = f"Pipeline ID: {config['pipeline_id']}, "
                details += f"Estágios: {len(config.get('stages', {}))}, "
                details += f"Campos: {len(config.get('custom_fields', {}))}"
                self.log_test(test_name, True, details)
                
                # Exibir detalhes
                logger.info("📋 Estágios encontrados:")
                for stage_key, stage_id in config.get('stages', {}).items():
                    logger.info(f"   - {stage_key}: {stage_id}")
                    
                logger.info("📋 Campos personalizados encontrados:")
                for field_key, field_id in config.get('custom_fields', {}).items():
                    logger.info(f"   - {field_key}: {field_id}")
            else:
                self.log_test(test_name, False, "Configuração não carregada")
                
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_create_lead(self):
        """Testa criação de lead"""
        test_name = "Criação de Lead"
        try:
            # Criar lead de teste
            lead_data = KommoLead(
                name=self.test_name,
                phone=self.test_phone,
                whatsapp=self.test_phone,
                email=f"teste_{self.test_id}@example.com",
                energy_bill_value=1200.50,
                solution_type=SolutionType.OWN_PLANT,
                current_discount="Sem desconto",
                competitor="Nenhum",
                qualification_score=85,  # Corrigido para inteiro
                ai_notes="Lead de teste criado via script de integração",
                tags=["Teste", "Automação", f"ID_{self.test_id}"]
            )
            
            result = await self.kommo.create_or_update_lead(lead_data)
            
            if result and "id" in result:
                self.test_lead_id = result["id"]
                self.log_test(test_name, True, f"Lead criado - ID: {self.test_lead_id}")
            else:
                self.log_test(test_name, False, "Lead não retornou ID")
                
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_find_lead_by_whatsapp(self):
        """Testa busca de lead por WhatsApp"""
        test_name = "Busca Lead por WhatsApp"
        try:
            # Aguardar um pouco para garantir que o lead foi indexado
            await asyncio.sleep(2)
            
            # Buscar lead pelo número
            lead = await self.kommo.find_lead_by_whatsapp(self.test_phone)
            
            if lead:
                self.log_test(test_name, True, f"Lead encontrado - ID: {lead['id']}")
            else:
                self.log_test(test_name, False, "Lead não encontrado")
                
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_update_lead(self):
        """Testa atualização de lead"""
        test_name = "Atualização de Lead"
        try:
            if not self.test_lead_id:
                self.log_test(test_name, False, "Lead de teste não criado")
                return
            
            # Atualizar lead
            lead_data = KommoLead(
                name=f"{self.test_name} - Atualizado",
                phone=self.test_phone,
                whatsapp=self.test_phone,
                energy_bill_value=1500.00,
                solution_type=SolutionType.PARTNER_PLANT,
                qualification_score=95,  # Corrigido para inteiro
                ai_notes="Lead atualizado com novos dados",
                tags=["Teste", "Atualizado"]
            )
            
            result = await self.kommo.update_lead(self.test_lead_id, lead_data)
            
            if result:
                self.log_test(test_name, True, "Lead atualizado com sucesso")
            else:
                self.log_test(test_name, False, "Falha na atualização")
                
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_move_lead_stage(self):
        """Testa movimentação de lead entre estágios"""
        test_name = "Movimentação de Estágios"
        try:
            if not self.test_lead_id:
                self.log_test(test_name, False, "Lead de teste não criado")
                return
            
            # Testar movimentação por diferentes estágios
            stages_to_test = [
                LeadStatus.IN_QUALIFICATION,
                LeadStatus.QUALIFIED,
                LeadStatus.MEETING_SCHEDULED
            ]
            
            all_success = True
            details = []
            
            for stage in stages_to_test:
                success = await self.kommo.move_lead_stage(self.test_lead_id, stage)
                if success:
                    details.append(f"{stage.value}: OK")
                else:
                    all_success = False
                    details.append(f"{stage.value}: Falhou")
                
                # Pequena pausa entre movimentações
                await asyncio.sleep(1)
            
            self.log_test(test_name, all_success, " | ".join(details))
            
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_add_note(self):
        """Testa adição de nota ao lead"""
        test_name = "Adição de Nota"
        try:
            if not self.test_lead_id:
                self.log_test(test_name, False, "Lead de teste não criado")
                return
            
            # Adicionar nota
            note_text = f"""
            🧪 Nota de Teste - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Esta é uma nota de teste para verificar a integração com Kommo CRM.
            
            Dados do teste:
            - ID do teste: {self.test_id}
            - Telefone: {self.test_phone}
            - Timestamp: {datetime.now().isoformat()}
            """
            
            success = await self.kommo.add_note(self.test_lead_id, note_text)
            
            self.log_test(test_name, success, "Nota adicionada" if success else "Falha ao adicionar")
            
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_add_tags(self):
        """Testa adição de tags ao lead"""
        test_name = "Adição de Tags"
        try:
            if not self.test_lead_id:
                self.log_test(test_name, False, "Lead de teste não criado")
                return
            
            # Adicionar tags
            tags = [
                "Teste Automatizado",
                f"Script {self.test_id}",
                datetime.now().strftime("%Y-%m-%d")
            ]
            
            success = await self.kommo.add_tags_to_lead(self.test_lead_id, tags)
            
            self.log_test(test_name, success, f"Tags: {', '.join(tags)}" if success else "Falha")
            
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_create_contact(self):
        """Testa criação de contato"""
        test_name = "Criação de Contato"
        try:
            # Criar contato
            contact_data = {
                "name": f"Contato {self.test_name}",
                "phone": self.test_phone,
                "email": f"contato_{self.test_id}@example.com"
            }
            
            contact = await self.kommo.create_contact(contact_data)
            
            if contact and "id" in contact:
                self.test_contact_id = contact["id"]
                self.log_test(test_name, True, f"Contato criado - ID: {self.test_contact_id}")
            else:
                self.log_test(test_name, False, "Contato não retornou ID")
                
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_link_contact_to_lead(self):
        """Testa associação de contato com lead"""
        test_name = "Associação Contato-Lead"
        try:
            if not self.test_lead_id or not self.test_contact_id:
                self.log_test(test_name, False, "Lead ou contato não criados")
                return
            
            # Associar contato ao lead
            success = await self.kommo.link_contact_to_lead(
                self.test_contact_id,
                self.test_lead_id
            )
            
            self.log_test(test_name, success, "Contato associado" if success else "Falha")
            
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_schedule_meeting(self):
        """Testa agendamento de reunião"""
        test_name = "Agendamento de Reunião"
        try:
            if not self.test_lead_id:
                self.log_test(test_name, False, "Lead de teste não criado")
                return
            
            # Agendar reunião para amanhã às 14h
            meeting_time = datetime.now() + timedelta(days=1)
            meeting_time = meeting_time.replace(hour=14, minute=0, second=0)
            
            success = await self.kommo.schedule_meeting(
                self.test_lead_id,
                meeting_time,
                "Reunião de teste agendada via script"
            )
            
            self.log_test(
                test_name, 
                success, 
                f"Reunião agendada para {meeting_time}" if success else "Falha"
            )
            
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def test_get_lead_details(self):
        """Testa obtenção de detalhes do lead"""
        test_name = "Detalhes do Lead"
        try:
            if not self.test_lead_id:
                self.log_test(test_name, False, "Lead de teste não criado")
                return
            
            # Obter detalhes
            lead = await self.kommo.get_lead(self.test_lead_id)
            
            if lead:
                details = f"Nome: {lead.get('name', 'N/A')}, "
                details += f"Status: {lead.get('status_id', 'N/A')}, "
                details += f"Pipeline: {lead.get('pipeline_id', 'N/A')}"
                self.log_test(test_name, True, details)
            else:
                self.log_test(test_name, False, "Lead não encontrado")
                
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        logger.info("=" * 80)
        logger.info("🧪 INICIANDO TESTES DE INTEGRAÇÃO KOMMO CRM")
        logger.info("=" * 80)
        
        # Lista de testes a executar
        tests = [
            self.test_authentication,
            self.test_pipeline_configuration,
            self.test_create_lead,
            self.test_find_lead_by_whatsapp,
            self.test_update_lead,
            self.test_move_lead_stage,
            self.test_add_note,
            self.test_add_tags,
            self.test_create_contact,
            self.test_link_contact_to_lead,
            self.test_schedule_meeting,
            self.test_get_lead_details
        ]
        
        # Executar testes em sequência
        for test in tests:
            logger.info(f"\n📋 Executando: {test.__name__}")
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
        """Exibe resumo dos testes"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("=" * 80)
        
        total = self.test_results["passed"] + self.test_results["failed"]
        
        logger.info(f"Total de testes: {total}")
        logger.info(f"✅ Passaram: {self.test_results['passed']}")
        logger.info(f"❌ Falharam: {self.test_results['failed']}")
        
        if total > 0:
            success_rate = (self.test_results['passed'] / total) * 100
            logger.info(f"Taxa de sucesso: {success_rate:.1f}%")
        
        # Listar testes que falharam
        failed_tests = [t for t in self.test_results["tests"] if not t["success"]]
        if failed_tests:
            logger.info("\n⚠️  Testes que falharam:")
            for test in failed_tests:
                logger.info(f"   - {test['name']}: {test['details']}")
        
        # Informações de limpeza
        if self.test_lead_id:
            logger.info(f"\n🧹 Lead de teste criado - ID: {self.test_lead_id}")
            logger.info("   Para limpar: Exclua manualmente no Kommo CRM")
        
        logger.info("=" * 80)


async def main():
    """Função principal"""
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # Criar e executar testes
    tester = KommoIntegrationTester()
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal durante os testes: {e}")
    
    logger.info("\n✅ Testes concluídos!")


if __name__ == "__main__":
    asyncio.run(main())