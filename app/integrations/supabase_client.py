"""
Cliente Supabase para o SDR IA SolarPrime
Gerencia todas as operações com o banco de dados
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from supabase import create_client, Client
from loguru import logger
from app.utils.logger import emoji_logger
import asyncio

from app.config import settings


class SupabaseClient:
    """Cliente para interação com Supabase"""
    
    def __init__(self):
        """Inicializa o cliente Supabase"""
        self.client: Client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_service_key
        )
        emoji_logger.supabase_connect("Cliente inicializado com sucesso")
    
    async def test_connection(self) -> bool:
        """Testa conexão com o Supabase"""
        try:
            # Tenta fazer uma query simples
            result = self.client.table('leads').select("id").limit(1).execute()
            emoji_logger.supabase_success("Conexão estabelecida")
            return True
        except Exception as e:
            emoji_logger.supabase_error(f"Erro de conexão: {str(e)}")
            return False
    
    # ============= LEADS =============
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo lead"""
        try:
            # Adiciona timestamps
            lead_data['created_at'] = datetime.now().isoformat()
            lead_data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table('leads').insert(lead_data).execute()
            
            if result.data:
                emoji_logger.supabase_insert("leads", 1, lead_id=result.data[0]['id'])
                return result.data[0]
            
            raise Exception("Erro ao criar lead")
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao criar lead: {str(e)}", table="leads")
            raise
    
    async def get_lead_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Busca lead por telefone"""
        try:
            result = self.client.table('leads').select("*").eq('phone_number', phone).execute()
            
            if result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao buscar lead: {str(e)}", table="leads")
            return None
    
    async def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza dados do lead"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table('leads').update(update_data).eq('id', lead_id).execute()
            
            if result.data:
                emoji_logger.supabase_update("leads", 1, lead_id=lead_id)
                return result.data[0]
            
            raise Exception("Erro ao atualizar lead")
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao atualizar lead: {str(e)}", table="leads")
            raise
    
    async def get_qualified_leads(self) -> List[Dict[str, Any]]:
        """Retorna leads qualificados"""
        try:
            result = self.client.table('leads').select("*").eq(
                'qualification_status', 'QUALIFIED'
            ).execute()
            
            return result.data or []
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao buscar leads qualificados: {str(e)}", table="leads")
            return []
    
    # ============= CONVERSATIONS =============
    
    async def get_or_create_conversation(self, phone: str, lead_id: Optional[str] = None) -> Dict[str, Any]:
        """Busca ou cria uma conversa para o telefone"""
        try:
            # Primeiro tenta buscar conversa existente
            conversation = await self.get_conversation_by_phone(phone)
            
            if conversation:
                return conversation
            
            # Se não existe, cria nova
            return await self.create_conversation(phone, lead_id)
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao obter/criar conversa: {str(e)}", table="conversations")
            raise
    
    async def create_conversation(self, phone: str, lead_id: Optional[str] = None) -> Dict[str, Any]:
        """Cria uma nova conversa"""
        try:
            conversation_data = {
                'phone_number': phone,
                'lead_id': lead_id,
                'status': 'ACTIVE',
                'total_messages': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.client.table('conversations').insert(conversation_data).execute()
            
            if result.data:
                emoji_logger.supabase_insert("conversations", 1, conversation_id=result.data[0]['id'])
                return result.data[0]
            
            raise Exception("Erro ao criar conversa")
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao criar conversa: {str(e)}", table="conversations")
            raise
    
    async def get_conversation_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Busca conversa por telefone"""
        try:
            result = self.client.table('conversations').select("*").eq(
                'phone_number', phone
            ).execute()
            
            if result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao buscar conversa: {str(e)}", table="conversations")
            return None
    
    async def update_conversation(self, conversation_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza dados da conversa"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            update_data['last_message_at'] = datetime.now().isoformat()
            
            result = self.client.table('conversations').update(update_data).eq(
                'id', conversation_id
            ).execute()
            
            if result.data:
                return result.data[0]
            
            raise Exception("Erro ao atualizar conversa")
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao atualizar conversa: {str(e)}", table="conversations")
            raise
    
    # ============= MESSAGES =============
    
    async def save_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva mensagem no banco"""
        try:
            message_data['created_at'] = datetime.now().isoformat()
            
            result = self.client.table('messages').insert(message_data).execute()
            
            if result.data:
                # Incrementa contador de mensagens na conversa
                if message_data.get('conversation_id'):
                    await self._increment_message_count(message_data['conversation_id'])
                
                return result.data[0]
            
            raise Exception("Erro ao salvar mensagem")
            
        except Exception as e:
            emoji_logger.supabase_error(f"Erro ao salvar mensagem: {str(e)}", table="messages")
            raise
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retorna mensagens de uma conversa"""
        try:
            result = self.client.table('messages').select("*").eq(
                'conversation_id', conversation_id
            ).order('created_at', desc=False).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens: {str(e)}")
            return []
    
    async def _increment_message_count(self, conversation_id: str):
        """Incrementa contador de mensagens na conversa"""
        try:
            # Busca conversa atual
            conv = self.client.table('conversations').select("total_messages").eq(
                'id', conversation_id
            ).execute()
            
            if conv.data:
                current_count = conv.data[0].get('total_messages', 0)
                
                # Atualiza contador
                self.client.table('conversations').update({
                    'total_messages': current_count + 1,
                    'last_message_at': datetime.now().isoformat()
                }).eq('id', conversation_id).execute()
                
        except Exception as e:
            logger.error(f"Erro ao incrementar contador: {str(e)}")
    
    # ============= FOLLOW-UPS =============
    
    async def create_follow_up(self, follow_up_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um follow-up"""
        try:
            follow_up_data['created_at'] = datetime.now().isoformat()
            follow_up_data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table('follow_ups').insert(follow_up_data).execute()
            
            if result.data:
                logger.info(f"Follow-up criado: {result.data[0]['id']}")
                return result.data[0]
            
            raise Exception("Erro ao criar follow-up")
            
        except Exception as e:
            logger.error(f"Erro ao criar follow-up: {str(e)}")
            raise
    
    async def get_pending_follow_ups(self) -> List[Dict[str, Any]]:
        """Retorna follow-ups pendentes"""
        try:
            now = datetime.now().isoformat()
            
            result = self.client.table('follow_ups').select("*").eq(
                'status', 'PENDING'
            ).lte('scheduled_at', now).order('priority', desc=True).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Erro ao buscar follow-ups: {str(e)}")
            return []
    
    async def update_follow_up_status(
        self,
        follow_up_id: str,
        status: str,
        executed_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Atualiza status do follow-up"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if executed_at:
                update_data['executed_at'] = executed_at.isoformat()
            
            result = self.client.table('follow_ups').update(update_data).eq(
                'id', follow_up_id
            ).execute()
            
            if result.data:
                return result.data[0]
            
            raise Exception("Erro ao atualizar follow-up")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar follow-up: {str(e)}")
            raise
    
    # ============= KNOWLEDGE BASE =============
    
    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca na base de conhecimento"""
        try:
            # Busca full-text em português
            result = self.client.rpc('search_knowledge', {
                'search_query': query,
                'result_limit': limit
            }).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Erro ao buscar conhecimento: {str(e)}")
            # Fallback para busca simples
            try:
                result = self.client.table('knowledge_base').select("*").ilike(
                    'content', f'%{query}%'
                ).limit(limit).execute()
                
                return result.data or []
            except:
                return []
    
    async def add_knowledge(self, knowledge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona item à base de conhecimento"""
        try:
            knowledge_data['created_at'] = datetime.now().isoformat()
            knowledge_data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table('knowledge_base').insert(knowledge_data).execute()
            
            if result.data:
                logger.info(f"Conhecimento adicionado: {result.data[0]['id']}")
                return result.data[0]
            
            raise Exception("Erro ao adicionar conhecimento")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar conhecimento: {str(e)}")
            raise
    
    # ============= ANALYTICS =============
    
    async def log_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra evento de analytics"""
        try:
            event_data['timestamp'] = datetime.now().isoformat()
            event_data['created_at'] = datetime.now().isoformat()
            
            result = self.client.table('analytics').insert(event_data).execute()
            
            if result.data:
                return result.data[0]
            
            raise Exception("Erro ao registrar evento")
            
        except Exception as e:
            logger.error(f"Erro ao registrar evento: {str(e)}")
            raise
    
    async def get_daily_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do dia"""
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
            
            # Total de leads do dia
            leads = self.client.table('leads').select("id", count='exact').gte(
                'created_at', today_start
            ).execute()
            
            # Leads qualificados do dia
            qualified = self.client.table('leads').select("id", count='exact').gte(
                'created_at', today_start
            ).eq('qualification_status', 'QUALIFIED').execute()
            
            # Conversas ativas
            active_convs = self.client.table('conversations').select("id", count='exact').eq(
                'status', 'ACTIVE'
            ).execute()
            
            # Reuniões agendadas hoje
            meetings = self.client.table('leads').select("id", count='exact').gte(
                'meeting_scheduled_at', today_start
            ).execute()
            
            return {
                'date': datetime.now().date().isoformat(),
                'total_leads': leads.count if leads else 0,
                'qualified_leads': qualified.count if qualified else 0,
                'active_conversations': active_convs.count if active_convs else 0,
                'meetings_scheduled': meetings.count if meetings else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                'date': datetime.now().date().isoformat(),
                'total_leads': 0,
                'qualified_leads': 0,
                'active_conversations': 0,
                'meetings_scheduled': 0
            }
    
    # ============= SESSION MANAGEMENT =============
    
    async def get_agent_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Busca sessão do agente"""
        try:
            result = self.client.table('agent_sessions').select("*").eq(
                'session_id', session_id
            ).execute()
            
            if result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar sessão: {str(e)}")
            return None
    
    async def save_agent_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva sessão do agente"""
        try:
            existing = await self.get_agent_session(session_data['session_id'])
            
            if existing:
                # Atualiza sessão existente
                session_data['updated_at'] = datetime.now().isoformat()
                session_data['last_interaction'] = datetime.now().isoformat()
                
                result = self.client.table('agent_sessions').update(session_data).eq(
                    'session_id', session_data['session_id']
                ).execute()
            else:
                # Cria nova sessão
                session_data['created_at'] = datetime.now().isoformat()
                session_data['updated_at'] = datetime.now().isoformat()
                session_data['last_interaction'] = datetime.now().isoformat()
                
                result = self.client.table('agent_sessions').insert(session_data).execute()
            
            if result.data:
                return result.data[0]
            
            raise Exception("Erro ao salvar sessão")
            
        except Exception as e:
            logger.error(f"Erro ao salvar sessão: {str(e)}")
            raise
    
    async def cleanup_old_sessions(self, days: int = 30):
        """Limpa sessões antigas"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.client.table('agent_sessions').delete().lt(
                'last_interaction', cutoff_date
            ).execute()
            
            logger.info(f"Sessões antigas limpas: {len(result.data) if result.data else 0}")
            
        except Exception as e:
            logger.error(f"Erro ao limpar sessões: {str(e)}")
    
    async def close(self):
        """Fecha conexão com Supabase"""
        # Supabase client não precisa de close explícito
        logger.info("Cliente Supabase encerrado")
    
    async def test_connection(self) -> bool:
        """Testa a conexão com o Supabase"""
        try:
            # Faz uma query simples para testar
            response = self.client.table("leads").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao testar conexão com Supabase: {e}")
            return False
    
    async def save_qualification(self, qualification_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Salva resultado de qualificação"""
        try:
            response = self.client.table("leads_qualifications").insert(qualification_data).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao salvar qualificação: {e}")
            return None
    
    async def get_latest_qualification(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Obtém última qualificação do lead"""
        try:
            response = self.client.table("leads_qualifications")\
                .select("*")\
                .eq("lead_id", lead_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter qualificação: {e}")
            return None
    
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca lead por ID"""
        try:
            response = self.client.table("leads").select("*").eq("id", lead_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar lead por ID: {e}")
            return None

# Singleton global
supabase_client = SupabaseClient()