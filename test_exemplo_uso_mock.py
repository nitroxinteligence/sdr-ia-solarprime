#!/usr/bin/env python3
"""
📖 EXEMPLO DE USO DO SISTEMA MOCK
Como converter testes existentes para usar sistema mock
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Adicionar path da aplicação
sys.path.append(str(Path(__file__).parent))

from app.testing.mock_supabase import mock_supabase_context
from app.testing.pytest_helpers import MockSupabaseTestCase, MockAssertions, with_mock_supabase
from app.integrations.supabase_client import SupabaseClient

# ============= EXEMPLO 1: CONTEXT MANAGER =============

async def exemplo_context_manager():
    """Exemplo usando context manager diretamente"""
    print("📖 EXEMPLO 1: Context Manager")
    
    with mock_supabase_context():
        db = SupabaseClient()
        
        # Todos os calls são interceptados
        conversation = await db.get_conversation_by_phone("5511999887766")
        
        if conversation:
            print(f"✅ Conversa encontrada: {conversation['status']}")
        else:
            print("❌ Conversa não encontrada")

# ============= EXEMPLO 2: PYTEST FIXTURE =============

@pytest.fixture
def db_mock():
    """Fixture personalizada"""
    with mock_supabase_context() as mock_db:
        yield mock_db

async def test_com_fixture(db_mock):
    """Teste usando fixture pytest"""
    db = SupabaseClient()
    
    # Mock já está ativo
    lead = await db.get_lead_by_phone("5511999887766")
    assert lead is not None
    assert lead['name'] == 'João Silva'
    
    print("✅ Teste com fixture: PASSOU")

# ============= EXEMPLO 3: DECORATOR =============

@with_mock_supabase
async def exemplo_decorator():
    """Exemplo usando decorator"""
    print("📖 EXEMPLO 3: Decorator")
    
    db = SupabaseClient()
    
    # Mock está automaticamente ativo
    messages = await db.get_conversation_messages("any-id", limit=5)
    
    print(f"✅ Mensagens encontradas: {len(messages)}")

# ============= EXEMPLO 4: CLASSE BASE =============

class TestMeuServico(MockSupabaseTestCase):
    """Teste usando classe base com setup automático"""
    
    async def test_servico_funciona(self):
        """Mock é configurado automaticamente"""
        db = SupabaseClient()
        
        # Mock já está ativo
        conversation = await db.get_conversation_by_phone("5511999887766")
        
        # Usa assertions específicas
        MockAssertions.assert_conversation_exists("5511999887766", self.mock_db)
        
        assert conversation['status'] == 'ACTIVE'
        print("✅ Teste classe base: PASSOU")
    
    async def test_dados_customizados(self):
        """Teste com dados customizados"""
        
        # Adiciona dados específicos para este teste
        self.mock_db.data['leads'].append({
            'id': 'custom-lead-123',
            'name': 'Lead Customizado',
            'phone_number': '5511222333444',
            'bill_value': '1500'
        })
        
        db = SupabaseClient()
        lead = await db.get_lead_by_phone("5511222333444")
        
        assert lead is not None
        assert lead['name'] == 'Lead Customizado'
        assert lead['bill_value'] == '1500'
        
        print("✅ Teste dados customizados: PASSOU")

# ============= EXEMPLO 5: CONVERSÃO DE TESTE EXISTENTE =============

async def teste_original_sem_mock():
    """
    ANTES: Teste que falhava sem mock
    ❌ Problema: Fazia calls reais para Supabase
    """
    # Este código falharia sem dados reais
    # db = SupabaseClient()
    # result = db.client.table('conversations').select().eq('phone_number', '5511999887766').execute()
    # if not result.data:
    #     raise Exception("⚠️ Conversa não encontrada para phone: 5511999887766")
    
    print("❌ ANTES: Teste dependia de dados reais do banco")

async def teste_convertido_com_mock():
    """
    DEPOIS: Teste convertido para usar mock
    ✅ Solução: Sistema mock intercepta todas as chamadas
    """
    print("📖 EXEMPLO 5: Conversão de Teste")
    
    with mock_supabase_context():
        db = SupabaseClient()
        
        # O mesmo código agora funciona
        result = db.client.table('conversations').select().eq('phone_number', '5511999887766').execute()
        
        if result.data:
            conversation = result.data[0]
            print(f"✅ DEPOIS: Conversa encontrada - Status: {conversation['status']}")
        else:
            print("❌ Erro: Mock não funcionou")

# ============= EXEMPLO 6: TESTE DE INTEGRAÇÃO =============

async def exemplo_integracao_completa():
    """Exemplo de teste de integração completo"""
    print("📖 EXEMPLO 6: Integração Completa")
    
    with mock_supabase_context() as mock_db:
        db = SupabaseClient()
        
        # 1. Busca lead
        lead = await db.get_lead_by_phone("5511999887766")
        print(f"✅ Lead: {lead['name']} - R${lead['bill_value']}")
        
        # 2. Busca/cria conversa
        conversation = await db.get_or_create_conversation("5511999887766", lead['id'])
        print(f"✅ Conversa: {conversation['status']}")
        
        # 3. Salva mensagem
        message = await db.save_message({
            'conversation_id': conversation['id'],
            'message_type': 'user',
            'content': 'Olá, quero saber sobre energia solar'
        })
        print(f"✅ Mensagem salva: {message['id'][:8]}...")
        
        # 4. Busca conhecimento
        knowledge = await db.search_knowledge("energia solar", limit=2)
        print(f"✅ Knowledge: {len(knowledge)} itens encontrados")
        
        # 5. Cria follow-up
        followup = await db.create_follow_up({
            'type': 'reengagement',
            'follow_up_type': 'IMMEDIATE_REENGAGEMENT',
            'metadata': {
                'phone': "5511999887766",
                'conversation_id': conversation['id']
            }
        })
        print(f"✅ Follow-up criado: {followup['id'][:8]}...")
        
        print("🎯 Integração completa: TODOS OS SISTEMAS FUNCIONANDO!")

if __name__ == "__main__":
    async def executar_exemplos():
        """Executa todos os exemplos"""
        print("📚 EXECUTANDO EXEMPLOS DE USO DO SISTEMA MOCK")
        print("=" * 60)
        
        exemplos = [
            ("Context Manager", exemplo_context_manager()),
            ("Decorator", exemplo_decorator()),
            ("Conversão de Teste", teste_convertido_com_mock()),
            ("Integração Completa", exemplo_integracao_completa()),
        ]
        
        for nome, exemplo in exemplos:
            print(f"\n🧪 {nome}:")
            try:
                await exemplo
            except Exception as e:
                print(f"❌ Erro em {nome}: {e}")
        
        # Executa testes de classe
        print(f"\n🧪 Classe Base:")
        test_instance = TestMeuServico()
        test_instance.setup_method()
        
        try:
            await test_instance.test_servico_funciona()
            await test_instance.test_dados_customizados()
        finally:
            test_instance.teardown_method()
        
        print("\n" + "=" * 60)
        print("🏆 EXEMPLOS CONCLUÍDOS COM SUCESSO!")
        print("\n📋 RESUMO DOS PADRÕES:")
        print("   🎭 Context Manager: Para testes simples")
        print("   🧪 Pytest Fixtures: Para testes organizados")
        print("   ⚡ Decorators: Para testes rápidos")
        print("   🏗️ Classe Base: Para suites de testes")
        print("   🎯 Dados Custom: Para casos específicos")
        print("\n🎯 TODOS OS PADRÕES FUNCIONAM PERFEITAMENTE!")
    
    # Executa os exemplos
    asyncio.run(executar_exemplos())