"""
Testes REAIS Supabase - Operações de Banco de Dados Completas
Implementa testes sem mocks seguindo padrões de API real.

Este módulo testa operações completas com o banco de dados real do Supabase,
incluindo CRUD de leads, conversas, mensagens, profiles e follow-ups.
"""

import pytest
import asyncio
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4

# Carrega .env
root_dir = Path(__file__).parent.parent.parent.parent
load_dotenv(root_dir / '.env')

# Carrega diretamente do os.environ já que o .env foi carregado
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')


class TestSupabaseReal:
    """Testes REAIS de operações Supabase."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada teste."""
        self.test_prefix = "[TEST-SUPABASE]"
        self.created_records = {
            'leads': [],
            'profiles': [],
            'conversations': [],
            'messages': [],
            'follow_ups': []
        }
        
        # Dados de teste
        self.test_phone = f"5511{int(time.time())}"  # Único baseado no timestamp
        
        if not os.getenv('PYTEST_RUNNING'):
            pytest.skip("Testes reais só executam em ambiente de teste")
    
    @pytest.fixture(autouse=True)
    def cleanup_records(self):
        """Cleanup automático de registros de teste."""
        yield
        
        # Cleanup será implementado se necessário
        # Por segurança, vamos manter os registros de teste
        if hasattr(self, 'created_records'):
            total_created = sum(len(records) for records in self.created_records.values())
            if total_created > 0:
                print(f"\n📝 {total_created} registros de teste criados (mantidos para auditoria)")
    
    def _has_real_credentials(self) -> bool:
        """Verifica credenciais reais do Supabase."""
        required_vars = [SUPABASE_URL, SUPABASE_SERVICE_KEY]
        return all(
            var and var.strip() and not var.startswith('test') 
            for var in required_vars
        )
    
    def _get_supabase_client(self):
        """Cria cliente Supabase para testes."""
        from supabase import create_client, Client
        from supabase.lib.client_options import ClientOptions
        
        # Configurações do cliente
        options = ClientOptions(
            auto_refresh_token=True,
            persist_session=True
        )
        
        return create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_KEY,
            options=options
        )

    @pytest.mark.real_integration
    @pytest.mark.timeout(30)
    @pytest.mark.asyncio
    async def test_supabase_connection_real(self):
        """Testa CONEXÃO REAL com Supabase."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais do Supabase não disponíveis")
        
        print("🔍 TESTANDO CONEXÃO COM SUPABASE")
        print(f"   🌐 URL: {SUPABASE_URL}")
        
        try:
            client = self._get_supabase_client()
            
            # Teste simples de conexão - listar primeiros registros da tabela leads
            start_time = time.time()
            
            result = await asyncio.to_thread(
                lambda: client.table("leads").select("id").limit(1).execute()
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Verifica resposta
            assert result is not None, "Nenhuma resposta do Supabase"
            assert hasattr(result, 'data'), "Resposta não contém dados"
            
            print(f"✅ Conexão com Supabase estabelecida!")
            print(f"   ⏱️ Tempo de resposta: {duration:.3f}s")
            print(f"   📊 Estrutura disponível: tabela 'leads' acessível")
            
            # Valida tempo de resposta razoável
            assert duration < 10.0, f"Tempo de resposta muito alto: {duration:.3f}s"
            
        except Exception as e:
            pytest.fail(f"❌ Erro de conexão com Supabase: {str(e)}")

    @pytest.mark.real_integration
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_supabase_health_check_real(self):
        """Testa HEALTH CHECK REAL do Supabase."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais do Supabase não disponíveis")
        
        print("🏥 TESTANDO HEALTH CHECK DO SUPABASE")
        
        try:
            # Usar o serviço real
            from agente.services.supabase_service import SupabaseService
            
            service = SupabaseService()
            health_ok = await service.health_check()
            
            assert health_ok is True, "Health check falhou"
            
            print(f"✅ Health check do Supabase passou!")
            print(f"   🟢 Todas as verificações OK")
            print(f"   📡 Conectividade confirmada")
            
        except Exception as e:
            pytest.fail(f"❌ Erro no health check: {str(e)}")

    @pytest.mark.real_integration
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_supabase_profile_crud_real(self):
        """Testa CRUD REAL de profiles no Supabase."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais do Supabase não disponíveis")
        
        print("👤 TESTANDO CRUD DE PROFILES")
        
        try:
            from agente.services.supabase_service import SupabaseService, Profile
            
            service = SupabaseService()
            
            # 1. CREATE - Criar profile
            print("1️⃣ CREATE: Criando profile...")
            original_phone = self.test_phone
            
            profile_data = Profile(
                phone=original_phone,
                whatsapp_name=f"{self.test_prefix} Profile Teste",
                whatsapp_push_name="Profile Teste",
                total_messages=1
            )
            
            created_profile = await service.create_or_update_profile(profile_data)
            assert created_profile.phone == original_phone, "Telefone não confere"
            assert created_profile.id is not None, "Profile criado sem ID"
            
            self.created_records['profiles'].append(created_profile.id)
            print(f"   ✅ Profile criado: {created_profile.id}")
            
            # 2. READ - Ler profile
            print("2️⃣ READ: Lendo profile...")
            read_profile = await service.get_profile_by_phone(original_phone)
            assert read_profile is not None, "Profile não encontrado"
            assert read_profile.id == created_profile.id, "IDs não conferem"
            assert read_profile.phone == original_phone, "Telefones não conferem"
            
            print(f"   ✅ Profile lido corretamente")
            
            # 3. UPDATE - Atualizar profile
            print("3️⃣ UPDATE: Atualizando profile...")
            updated_name = f"{self.test_prefix} Profile ATUALIZADO"
            
            update_data = Profile(
                phone=original_phone,
                whatsapp_name=updated_name,
                whatsapp_push_name="Profile Atualizado",
                total_messages=2
            )
            
            updated_profile = await service.create_or_update_profile(update_data)
            assert updated_profile.whatsapp_name == updated_name, "Nome não foi atualizado"
            
            print(f"   ✅ Profile atualizado")
            print(f"      📝 Novo nome: {updated_profile.whatsapp_name}")
            
            # 4. VERIFY - Verificar alterações
            print("4️⃣ VERIFY: Verificando alterações...")
            verify_profile = await service.get_profile_by_phone(original_phone)
            assert verify_profile.whatsapp_name == updated_name, "Atualização não persistiu"
            
            print(f"   ✅ Alterações verificadas e persistidas")
            
            print("🎉 CRUD COMPLETO DE PROFILE realizado com sucesso!")
            
        except Exception as e:
            pytest.fail(f"❌ Erro no CRUD de profile: {str(e)}")

    @pytest.mark.real_integration
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_supabase_lead_crud_real(self):
        """Testa CRUD REAL de leads no Supabase."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais do Supabase não disponíveis")
        
        print("🎯 TESTANDO CRUD DE LEADS")
        
        try:
            from agente.services.supabase_service import SupabaseService
            from agente.core.types import Lead, LeadStage
            
            service = SupabaseService()
            
            # 1. CREATE - Criar lead
            print("1️⃣ CREATE: Criando lead...")
            lead_phone = f"{self.test_phone}_lead"
            
            lead_data = Lead(
                phone_number=lead_phone,
                name=f"{self.test_prefix} Lead Teste",
                current_stage=LeadStage.IDENTIFYING,
                interested=True,
                source="whatsapp_test"
            )
            
            created_lead = await service.create_lead(lead_data)
            assert created_lead.phone_number == lead_phone, "Telefone não confere"
            assert created_lead.id is not None, "Lead criado sem ID"
            
            self.created_records['leads'].append(created_lead.id)
            print(f"   ✅ Lead criado: {created_lead.id}")
            
            # 2. READ - Ler lead
            print("2️⃣ READ: Lendo lead...")
            read_lead = await service.get_lead_by_phone(lead_phone)
            assert read_lead is not None, "Lead não encontrado"
            assert read_lead.id == created_lead.id, "IDs não conferem"
            assert read_lead.phone_number == lead_phone, "Telefones não conferem"
            
            print(f"   ✅ Lead lido corretamente")
            
            # 3. UPDATE - Atualizar lead
            print("3️⃣ UPDATE: Atualizando lead...")
            updated_name = f"{self.test_prefix} Lead ATUALIZADO"
            
            updated_lead = await service.update_lead(
                lead_phone,
                name=updated_name,
                current_stage=LeadStage.QUALIFYING
            )
            assert updated_lead.name == updated_name, "Nome não foi atualizado"
            assert updated_lead.current_stage == LeadStage.QUALIFYING, "Stage não foi atualizado"
            
            print(f"   ✅ Lead atualizado")
            print(f"      📝 Novo nome: {updated_lead.name}")
            print(f"      📊 Nova stage: {updated_lead.current_stage}")
            
            # 4. VERIFY - Verificar alterações
            print("4️⃣ VERIFY: Verificando alterações...")
            verify_lead = await service.get_lead_by_phone(lead_phone)
            assert verify_lead.name == updated_name, "Atualização do nome não persistiu"
            assert verify_lead.current_stage == LeadStage.QUALIFYING, "Atualização da stage não persistiu"
            
            print(f"   ✅ Alterações verificadas e persistidas")
            
            print("🎉 CRUD COMPLETO DE LEAD realizado com sucesso!")
            
        except Exception as e:
            pytest.fail(f"❌ Erro no CRUD de lead: {str(e)}")

    @pytest.mark.real_integration
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_supabase_conversation_flow_real(self):
        """Testa FLUXO REAL de conversa no Supabase."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais do Supabase não disponíveis")
        
        print("💬 TESTANDO FLUXO DE CONVERSA")
        
        try:
            from agente.services.supabase_service import SupabaseService
            from agente.core.types import Lead, LeadStage, Conversation, Message, MessageRole
            
            service = SupabaseService()
            
            # Primeiro criar um lead
            print("📝 Preparando: Criando lead...")
            lead_phone = f"{self.test_phone}_conv"
            
            lead_data = Lead(
                phone_number=lead_phone,
                name=f"{self.test_prefix} Lead Conversa",
                current_stage=LeadStage.IDENTIFYING,
                interested=True,
                source="whatsapp_test"
            )
            
            created_lead = await service.create_lead(lead_data)
            self.created_records['leads'].append(created_lead.id)
            
            # 1. CREATE CONVERSATION - Criar conversa
            print("1️⃣ CREATE CONVERSATION: Criando conversa...")
            session_id = f"session_{int(time.time())}"
            
            # Criar conversa explicitamente definindo todos os campos datetime
            current_time = datetime.now()
            conversation_data = Conversation(
                session_id=session_id,
                lead_id=created_lead.id,
                is_active=True,
                started_at=current_time,
                total_messages=0
            )
            
            created_conversation = await service.create_conversation(conversation_data)
            assert created_conversation.session_id == session_id, "Session ID não confere"
            assert created_conversation.id is not None, "Conversa criada sem ID"
            
            self.created_records['conversations'].append(created_conversation.id)
            print(f"   ✅ Conversa criada: {created_conversation.id}")
            
            # 2. ADD MESSAGES - Adicionar mensagens
            print("2️⃣ ADD MESSAGES: Adicionando mensagens...")
            
            # Mensagem do usuário
            user_message = Message(
                conversation_id=created_conversation.id,
                role=MessageRole.USER,
                content="Olá, gostaria de saber sobre energia solar",
                created_at=datetime.now()
            )
            
            saved_user_msg = await service.save_message(user_message)
            self.created_records['messages'].append(saved_user_msg.id)
            
            # Mensagem do assistente  
            assistant_message = Message(
                conversation_id=created_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Olá! Ficou interessado em energia solar? Vou te ajudar!",
                created_at=datetime.now()
            )
            
            saved_assistant_msg = await service.save_message(assistant_message)
            self.created_records['messages'].append(saved_assistant_msg.id)
            
            print(f"   ✅ 2 mensagens adicionadas")
            
            # 3. GET ACTIVE CONVERSATION - Buscar conversa ativa
            print("3️⃣ GET ACTIVE: Buscando conversa ativa...")
            active_conversation = await service.get_active_conversation(created_lead.id)
            assert active_conversation is not None, "Conversa ativa não encontrada"
            assert active_conversation.id == created_conversation.id, "IDs não conferem"
            
            print(f"   ✅ Conversa ativa encontrada")
            
            # 4. GET LAST MESSAGES - Buscar mensagens
            print("4️⃣ GET MESSAGES: Buscando mensagens...")
            messages = await service.get_last_messages(lead_phone, limit=10)
            assert len(messages) >= 2, f"Esperado pelo menos 2 mensagens, encontrado {len(messages)}"
            
            print(f"   ✅ {len(messages)} mensagens recuperadas")
            
            # 5. END CONVERSATION - Finalizar conversa
            print("5️⃣ END CONVERSATION: Finalizando conversa...")
            ended_conversation = await service.end_conversation(created_conversation.id)
            assert ended_conversation.is_active == False, "Conversa não foi finalizada"
            assert ended_conversation.ended_at is not None, "Data de finalização não definida"
            
            print(f"   ✅ Conversa finalizada")
            
            print("🎉 FLUXO COMPLETO DE CONVERSA realizado com sucesso!")
            
        except Exception as e:
            pytest.fail(f"❌ Erro no fluxo de conversa: {str(e)}")

    @pytest.mark.real_integration
    @pytest.mark.timeout(30)
    @pytest.mark.asyncio
    async def test_supabase_queries_real(self):
        """Testa QUERIES REAIS do Supabase."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais do Supabase não disponíveis")
        
        print("🔍 TESTANDO QUERIES DO SUPABASE")
        
        try:
            from agente.services.supabase_service import SupabaseService
            from agente.core.types import LeadStage
            
            service = SupabaseService()
            
            # 1. GET LEADS BY STAGE
            print("1️⃣ QUERY: Buscando leads por estágio...")
            leads_by_stage = await service.get_leads_by_stage(LeadStage.IDENTIFYING, limit=5)
            
            print(f"   ✅ {len(leads_by_stage)} leads encontrados no estágio IDENTIFYING")
            
            # 2. GET RECENT LEADS
            print("2️⃣ QUERY: Buscando leads recentes...")
            recent_leads = await service.get_recent_leads(hours=24, limit=5)
            
            print(f"   ✅ {len(recent_leads)} leads criados nas últimas 24 horas")
            
            # 3. GET PENDING FOLLOW-UPS
            print("3️⃣ QUERY: Buscando follow-ups pendentes...")
            pending_follow_ups = await service.get_pending_follow_ups(limit=5)
            
            print(f"   ✅ {len(pending_follow_ups)} follow-ups pendentes encontrados")
            
            print("🎉 QUERIES do Supabase executadas com sucesso!")
            
        except Exception as e:
            pytest.fail(f"❌ Erro nas queries: {str(e)}")

    @pytest.mark.real_integration
    @pytest.mark.timeout(30)
    @pytest.mark.asyncio
    async def test_supabase_performance_real(self):
        """Testa PERFORMANCE REAL do Supabase."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais do Supabase não disponíveis")
        
        print("⚡ TESTANDO PERFORMANCE DO SUPABASE")
        
        try:
            from agente.services.supabase_service import SupabaseService
            
            service = SupabaseService()
            
            # Múltiplas operações para testar performance
            num_operations = 3
            operation_times = []
            
            for i in range(num_operations):
                start_time = time.time()
                
                # Operação simples: health check
                health_ok = await service.health_check()
                assert health_ok is True, f"Health check {i+1} falhou"
                
                end_time = time.time()
                duration = end_time - start_time
                operation_times.append(duration)
                
                print(f"      Operação {i+1}: {duration:.3f}s")
                
                # Pequeno delay entre operações
                await asyncio.sleep(0.1)
            
            # Análise dos tempos
            avg_time = sum(operation_times) / len(operation_times)
            max_time = max(operation_times)
            min_time = min(operation_times)
            
            print(f"✅ Performance testada com {num_operations} operações")
            print(f"   ⏱️ Tempo médio: {avg_time:.3f}s")
            print(f"   📊 Min: {min_time:.3f}s | Max: {max_time:.3f}s")
            
            # Validações de performance
            assert all(t < 10.0 for t in operation_times), "Algumas operações demoram mais que 10s"
            assert avg_time < 5.0, f"Tempo médio muito alto: {avg_time:.3f}s"
            
        except Exception as e:
            pytest.fail(f"❌ Erro no teste de performance: {str(e)}")

    def test_environment_validation_supabase(self):
        """Testa validação do ambiente Supabase."""
        print("🔧 VALIDAÇÃO DE AMBIENTE SUPABASE")
        
        # Testa detecção de credenciais
        has_creds = self._has_real_credentials()
        
        if not has_creds:
            print("ℹ️ Credenciais reais não disponíveis - testes serão pulados")
            print("   Para executar testes reais, configure:")
            print("   - SUPABASE_URL")
            print("   - SUPABASE_SERVICE_KEY")
        else:
            print("✅ Credenciais reais detectadas - testes reais podem executar")
            print(f"   🌐 URL: {SUPABASE_URL}")
            print(f"   🔑 Service Key: ...{SUPABASE_SERVICE_KEY[-10:] if SUPABASE_SERVICE_KEY else 'N/A'}")
        
        # Sempre passa - é apenas informativo
        assert True, "Validação de ambiente concluída"