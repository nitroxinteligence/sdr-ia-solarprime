"""
Testes abrangentes para todas as tabelas do Supabase
Sistema SDR IA SolarPrime v0.2
"""
import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from app.integrations.supabase_client import supabase_client


class SupabaseTableTester:
    """Classe para testar todas as tabelas do Supabase"""
    
    def __init__(self):
        self.client = supabase_client.client
        self.test_results = {}
        self.test_data_ids = {}  # Armazena IDs para limpeza posterior
    
    async def cleanup_test_data(self):
        """Limpa todos os dados de teste criados"""
        for table, ids in self.test_data_ids.items():
            if ids:
                try:
                    for test_id in ids:
                        self.client.table(table).delete().eq('id', test_id).execute()
                    logger.info(f"✅ Limpeza realizada na tabela {table}: {len(ids)} registros")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao limpar {table}: {e}")
    
    # ==================== TESTE: LEADS ====================
    
    async def test_leads_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela leads"""
        logger.info("\n🔍 Testando tabela: leads")
        results = {"table": "leads", "tests": {}}
        
        try:
            # CREATE
            lead_data = {
                'phone_number': '+5581999999999',
                'name': 'Teste Lead Automático',
                'email': f'teste_{uuid.uuid4().hex[:8]}@exemplo.com',
                'property_type': 'casa',
                'bill_value': 500.00,
                'consumption_kwh': 350,
                'current_stage': 'INITIAL_CONTACT',
                'qualification_score': 75,
                'interested': True,
                'qualification_status': 'PENDING'
            }
            
            create_result = self.client.table('leads').insert(lead_data).execute()
            if create_result.data:
                lead_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('leads', []).append(lead_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Lead criado com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
                logger.error("  ❌ CREATE: Falha ao criar lead")
            
            # READ
            read_result = self.client.table('leads').select("*").eq('id', lead_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Lead lido com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {'qualification_status': 'QUALIFIED', 'qualification_score': 90}
            update_result = self.client.table('leads').update(update_data).eq('id', lead_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Lead atualizado com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
            
            # DELETE
            delete_result = self.client.table('leads').delete().eq('id', lead_id).execute()
            if delete_result:
                results["tests"]["delete"] = "✅ PASSOU"
                logger.info("  ✅ DELETE: Lead deletado com sucesso")
                self.test_data_ids['leads'].remove(lead_id)
            else:
                results["tests"]["delete"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: CONVERSATIONS ====================
    
    async def test_conversations_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela conversations"""
        logger.info("\n🔍 Testando tabela: conversations")
        results = {"table": "conversations", "tests": {}}
        
        try:
            # Criar lead primeiro (dependência) - usar phone único
            lead_data = {
                'phone_number': f'+5581{uuid.uuid4().hex[:8]}',
                'name': 'Lead para Conversa',
                'current_stage': 'INITIAL_CONTACT'
            }
            lead_result = self.client.table('leads').insert(lead_data).execute()
            lead_id = lead_result.data[0]['id'] if lead_result.data else None
            if lead_id:
                self.test_data_ids.setdefault('leads', []).append(lead_id)
            
            # CREATE conversation - usar phone único
            conv_data = {
                'phone_number': f'+5581{uuid.uuid4().hex[:8]}',
                'lead_id': lead_id,
                'status': 'ACTIVE',
                'total_messages': 0,
                'session_id': f'session_{uuid.uuid4().hex[:8]}'  # Adicionar session_id obrigatório
            }
            
            create_result = self.client.table('conversations').insert(conv_data).execute()
            if create_result.data:
                conv_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('conversations', []).append(conv_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Conversa criada com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('conversations').select("*").eq('id', conv_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Conversa lida com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {'status': 'COMPLETED', 'total_messages': 1}
            update_result = self.client.table('conversations').update(update_data).eq('id', conv_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Conversa atualizada com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: MESSAGES ====================
    
    async def test_messages_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela messages"""
        logger.info("\n🔍 Testando tabela: messages")
        results = {"table": "messages", "tests": {}}
        
        try:
            # Usar conversa existente ou criar uma
            conv_result = self.client.table('conversations').select("id").limit(1).execute()
            conv_id = conv_result.data[0]['id'] if conv_result.data else None
            
            # CREATE message
            msg_data = {
                'conversation_id': conv_id,
                'content': 'Mensagem de teste automático',
                'role': 'user',
                'media_type': 'text',
                'media_data': {'teste': True}
            }
            
            create_result = self.client.table('messages').insert(msg_data).execute()
            if create_result.data:
                msg_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('messages', []).append(msg_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Mensagem criada com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('messages').select("*").eq('id', msg_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Mensagem lida com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {'media_data': {'teste': True, 'updated': True}}
            update_result = self.client.table('messages').update(update_data).eq('id', msg_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Mensagem atualizada com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: AGENT_SESSIONS ====================
    
    async def test_agent_sessions_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela agent_sessions"""
        logger.info("\n🔍 Testando tabela: agent_sessions")
        results = {"table": "agent_sessions", "tests": {}}
        
        try:
            # CREATE session
            session_data = {
                'session_id': f'test_session_{uuid.uuid4().hex[:8]}',
                'phone_number': '+5581777777777',
                'state': {
                    'current_step': 'greeting',
                    'context': {'teste': True}
                }
            }
            
            create_result = self.client.table('agent_sessions').insert(session_data).execute()
            if create_result.data:
                session_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('agent_sessions', []).append(session_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Sessão criada com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('agent_sessions').select("*").eq('id', session_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Sessão lida com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {
                'state': {
                    'current_step': 'qualification',
                    'context': {'teste': True, 'updated': True}
                },
                'last_interaction': datetime.utcnow().isoformat()
            }
            update_result = self.client.table('agent_sessions').update(update_data).eq('id', session_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Sessão atualizada com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: FOLLOW_UPS ====================
    
    async def test_follow_ups_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela follow_ups"""
        logger.info("\n🔍 Testando tabela: follow_ups")
        results = {"table": "follow_ups", "tests": {}}
        
        try:
            # Usar lead existente ou criar um
            lead_result = self.client.table('leads').select("id").limit(1).execute()
            lead_id = lead_result.data[0]['id'] if lead_result.data else None
            
            # CREATE follow-up (ajustar para estrutura real da tabela)
            followup_data = {
                'lead_id': lead_id,
                'phone_number': f'+5581{uuid.uuid4().hex[:8]}',  # phone_number é obrigatório
                'follow_up_type': 'DAILY_NURTURING',
                'scheduled_at': (datetime.utcnow() + timedelta(days=1)).isoformat(),
                'status': 'PENDING',  # Valores válidos: PENDING, EXECUTING, COMPLETED, FAILED, CANCELLED
                'priority': 'MEDIUM',  # Valores válidos: LOW, MEDIUM, HIGH, URGENT
                'custom_message': 'Follow-up de teste automático'
            }
            
            create_result = self.client.table('follow_ups').insert(followup_data).execute()
            if create_result.data:
                followup_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('follow_ups', []).append(followup_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Follow-up criado com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('follow_ups').select("*").eq('id', followup_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Follow-up lido com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {
                'status': 'EXECUTING',
                'attempts': 1,
                'last_attempt_at': datetime.utcnow().isoformat()
            }
            update_result = self.client.table('follow_ups').update(update_data).eq('id', followup_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Follow-up atualizado com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: KNOWLEDGE_BASE ====================
    
    async def test_knowledge_base_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela knowledge_base"""
        logger.info("\n🔍 Testando tabela: knowledge_base")
        results = {"table": "knowledge_base", "tests": {}}
        
        try:
            # CREATE knowledge
            kb_data = {
                'question': 'Teste: Quanto custa a energia solar?',
                'answer': 'Resposta de teste: O custo varia conforme o projeto.',
                'category': 'teste',
                'keywords': ['teste', 'custo', 'energia'],
                'metadata': {'tipo': 'teste_automatico'}
            }
            
            create_result = self.client.table('knowledge_base').insert(kb_data).execute()
            if create_result.data:
                kb_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('knowledge_base', []).append(kb_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Conhecimento criado com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('knowledge_base').select("*").eq('id', kb_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Conhecimento lido com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {
                'answer': 'Resposta atualizada: O custo médio é R$ 15.000',
                'keywords': ['teste', 'custo', 'energia', 'atualizado']
            }
            update_result = self.client.table('knowledge_base').update(update_data).eq('id', kb_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Conhecimento atualizado com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: EMBEDDINGS ====================
    
    async def test_embeddings_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela embeddings"""
        logger.info("\n🔍 Testando tabela: embeddings")
        results = {"table": "embeddings", "tests": {}}
        
        try:
            # Verificar se a tabela existe primeiro
            test_select = self.client.table('embeddings').select("id").limit(1).execute()
            
            # CREATE embedding
            embedding_data = {
                'content': 'Conteúdo de teste para embedding',
                'content_type': 'KNOWLEDGE_BASE',
                'embedding': [0.1] * 768,  # Vector de teste com 768 dimensões
                'metadata': {'teste': True}
            }
            
            create_result = self.client.table('embeddings').insert(embedding_data).execute()
            if create_result.data:
                emb_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('embeddings', []).append(emb_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Embedding criado com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('embeddings').select("*").eq('id', emb_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Embedding lido com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {'metadata': {'teste': True, 'atualizado': True}}
            update_result = self.client.table('embeddings').update(update_data).eq('id', emb_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Embedding atualizado com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            if "Could not find" in str(e) or "does not exist" in str(e):
                results["error"] = "Tabela embeddings não existe no Supabase"
                logger.warning("  ⚠️ Tabela embeddings não encontrada")
            else:
                results["error"] = str(e)
                logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: LEADS_QUALIFICATIONS ====================
    
    async def test_leads_qualifications_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela leads_qualifications"""
        logger.info("\n🔍 Testando tabela: leads_qualifications")
        results = {"table": "leads_qualifications", "tests": {}}
        
        try:
            # Parece que leads_qualifications não existe como tabela separada
            # Vou testar se a tabela existe
            test_query = self.client.table('leads_qualifications').select("*").limit(1).execute()
            
            # Se chegou aqui, a tabela existe, mas pode estar vazia
            results["tests"]["exists"] = "✅ TABELA EXISTE"
            logger.info("  ✅ A tabela leads_qualifications existe")
            
            # Marcar como SKIP pois não sabemos a estrutura
            results["tests"]["create"] = "⏭️ PULADO"
            results["tests"]["read"] = "⏭️ PULADO"
            results["tests"]["update"] = "⏭️ PULADO"
            logger.warning("  ⚠️ Testes pulados pois a estrutura da tabela é desconhecida")
                
        except Exception as e:
            if "does not exist" in str(e) or "Could not find" in str(e):
                results["error"] = "Tabela leads_qualifications não existe ou está integrada na tabela leads"
                logger.warning("  ⚠️ Tabela não encontrada (pode estar integrada em leads)")
            else:
                results["error"] = str(e)
                logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: ANALYTICS ====================
    
    async def test_analytics_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela analytics"""
        logger.info("\n🔍 Testando tabela: analytics")
        results = {"table": "analytics", "tests": {}}
        
        try:
            # CREATE analytics event (event_category pode não existir na tabela real)
            analytics_data = {
                'event_type': 'CONVERSATION_START',
                'event_data': {
                    'action': 'test_action',
                    'value': 100,
                    'metadata': {'teste': True}
                },
                'phone_number': '+5581555555555',
                'session_id': f'test_session_{uuid.uuid4().hex[:8]}'
            }
            
            create_result = self.client.table('analytics').insert(analytics_data).execute()
            if create_result.data:
                analytics_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('analytics', []).append(analytics_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Evento analytics criado com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('analytics').select("*").eq('id', analytics_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Evento analytics lido com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE (analytics geralmente não é atualizado, mas vamos testar)
            update_data = {'event_data': {'action': 'test_action', 'value': 200, 'updated': True}}
            update_result = self.client.table('analytics').update(update_data).eq('id', analytics_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Evento analytics atualizado com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== TESTE: PROFILES ====================
    
    async def test_profiles_table(self) -> Dict[str, Any]:
        """Testa operações CRUD na tabela profiles"""
        logger.info("\n🔍 Testando tabela: profiles")
        results = {"table": "profiles", "tests": {}}
        
        try:
            # CREATE profile
            profile_data = {
                'phone_number': f'+5581{uuid.uuid4().hex[:8]}',
                'name': 'Usuário Teste',
                'email': f'teste_{uuid.uuid4().hex[:8]}@exemplo.com',
                'preferences': {
                    'theme': 'dark',
                    'language': 'pt-BR'
                },
                'total_messages': 0,
                'interaction_count': 0
            }
            
            create_result = self.client.table('profiles').insert(profile_data).execute()
            if create_result.data:
                profile_id = create_result.data[0]['id']
                self.test_data_ids.setdefault('profiles', []).append(profile_id)
                results["tests"]["create"] = "✅ PASSOU"
                logger.info("  ✅ CREATE: Profile criado com sucesso")
            else:
                results["tests"]["create"] = "❌ FALHOU"
            
            # READ
            read_result = self.client.table('profiles').select("*").eq('id', profile_id).single().execute()
            if read_result.data:
                results["tests"]["read"] = "✅ PASSOU"
                logger.info("  ✅ READ: Profile lido com sucesso")
            else:
                results["tests"]["read"] = "❌ FALHOU"
            
            # UPDATE
            update_data = {
                'name': 'Usuário Teste Atualizado',
                'preferences': {'theme': 'light', 'language': 'en-US'}
            }
            update_result = self.client.table('profiles').update(update_data).eq('id', profile_id).execute()
            if update_result.data:
                results["tests"]["update"] = "✅ PASSOU"
                logger.info("  ✅ UPDATE: Profile atualizado com sucesso")
            else:
                results["tests"]["update"] = "❌ FALHOU"
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"  ❌ Erro no teste: {e}")
        
        return results
    
    # ==================== EXECUTAR TODOS OS TESTES ====================
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de tabelas"""
        logger.info("🚀 Iniciando testes de todas as tabelas do Supabase")
        logger.info("=" * 60)
        
        all_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tables": {},
            "summary": {
                "total_tables": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0
            }
        }
        
        # Lista de métodos de teste
        test_methods = [
            self.test_leads_table,
            self.test_conversations_table,
            self.test_messages_table,
            self.test_agent_sessions_table,
            self.test_follow_ups_table,
            self.test_knowledge_base_table,
            self.test_embeddings_table,
            self.test_leads_qualifications_table,
            self.test_analytics_table,
            self.test_profiles_table
        ]
        
        # Executar cada teste
        for test_method in test_methods:
            try:
                result = await test_method()
                table_name = result["table"]
                all_results["tables"][table_name] = result
                all_results["summary"]["total_tables"] += 1
                
                # Contar sucessos e falhas
                if "error" in result:
                    all_results["summary"]["errors"] += 1
                else:
                    passed = sum(1 for test, status in result["tests"].items() if "PASSOU" in status)
                    failed = sum(1 for test, status in result["tests"].items() if "FALHOU" in status)
                    
                    if passed > 0 and failed == 0:
                        all_results["summary"]["passed"] += 1
                    elif failed > 0:
                        all_results["summary"]["failed"] += 1
                        
            except Exception as e:
                logger.error(f"Erro ao executar teste: {e}")
                all_results["summary"]["errors"] += 1
        
        # Limpeza de dados de teste
        logger.info("\n🧹 Realizando limpeza de dados de teste...")
        await self.cleanup_test_data()
        
        return all_results
    
    def generate_report(self, results: Dict[str, Any]):
        """Gera relatório detalhado dos testes"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO DE TESTES - TABELAS SUPABASE")
        logger.info("=" * 60)
        
        # Resumo geral
        summary = results["summary"]
        logger.info(f"\n📈 Resumo Geral:")
        logger.info(f"  Total de tabelas testadas: {summary['total_tables']}")
        logger.info(f"  ✅ Tabelas OK: {summary['passed']}")
        logger.info(f"  ❌ Tabelas com falhas: {summary['failed']}")
        logger.info(f"  ⚠️ Tabelas com erros: {summary['errors']}")
        
        # Taxa de sucesso
        if summary['total_tables'] > 0:
            success_rate = (summary['passed'] / summary['total_tables']) * 100
            logger.info(f"  📊 Taxa de sucesso: {success_rate:.1f}%")
        
        # Detalhes por tabela
        logger.info(f"\n📋 Detalhes por Tabela:")
        logger.info("-" * 60)
        
        for table_name, table_results in results["tables"].items():
            status_icon = "✅" if "error" not in table_results else "❌"
            logger.info(f"\n{status_icon} {table_name.upper()}")
            
            if "error" in table_results:
                logger.info(f"  ⚠️ Erro: {table_results['error']}")
            else:
                for test_name, test_status in table_results["tests"].items():
                    logger.info(f"  {test_name:10} : {test_status}")
        
        # Recomendações
        logger.info(f"\n💡 Recomendações:")
        if summary['errors'] > 0:
            logger.info("  1. Verificar se todas as tabelas estão criadas no Supabase")
            logger.info("  2. Executar scripts SQL de criação de tabelas se necessário")
            logger.info("  3. Verificar permissões e políticas RLS")
        
        if summary['failed'] > 0:
            logger.info("  1. Revisar estrutura das tabelas com falhas")
            logger.info("  2. Verificar constraints e foreign keys")
            logger.info("  3. Validar tipos de dados e campos obrigatórios")
        
        if summary['passed'] == summary['total_tables']:
            logger.info("  ✅ Todas as tabelas estão funcionando corretamente!")
            logger.info("  💚 Sistema de banco de dados está 100% operacional!")
        
        logger.info("\n" + "=" * 60)
        logger.info("Relatório concluído em: " + datetime.utcnow().isoformat())
        logger.info("=" * 60)


async def main():
    """Função principal de execução dos testes"""
    try:
        tester = SupabaseTableTester()
        
        # Executar todos os testes
        results = await tester.run_all_tests()
        
        # Gerar relatório
        tester.generate_report(results)
        
        # Salvar resultados em arquivo JSON
        with open('test_results_supabase.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("\n📁 Resultados salvos em: test_results_supabase.json")
        
        # Retornar código de saída baseado nos resultados
        if results["summary"]["errors"] == 0 and results["summary"]["failed"] == 0:
            logger.info("\n✅ TODOS OS TESTES PASSARAM!")
            return 0
        else:
            logger.warning("\n⚠️ Alguns testes falharam. Verifique o relatório acima.")
            return 1
            
    except Exception as e:
        logger.error(f"Erro crítico na execução dos testes: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)