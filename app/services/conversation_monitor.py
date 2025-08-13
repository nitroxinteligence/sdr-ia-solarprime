"""
Conversation Monitor - Monitoramento de conversas e agendamento de follow-ups
Sistema SIMPLES e FUNCIONAL para detectar inatividade e agendar reengajamento
ZERO complexidade, MÁXIMA eficiência
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from app.utils.logger import emoji_logger
from app.config import settings
from app.database.supabase_client import SupabaseClient

class ConversationMonitor:
    """
    Monitor de conversas para follow-up automático
    Detecta leads inativos e agenda reengajamento inteligente
    """
    
    def __init__(self):
        """Inicializa o monitor de conversas"""
        self.db = SupabaseClient()
        self.active_conversations = {}  # phone -> last_message_time
        self.follow_up_status = {}  # phone -> follow_up_stage
        self.is_monitoring = False
        
    async def initialize(self):
        """Inicializa o monitor de conversas e inicia monitoramento em background"""
        try:
            emoji_logger.system_ready("📊 ConversationMonitor inicializado")
            self.is_monitoring = True
            
            # Iniciar monitoramento em background
            asyncio.create_task(self._monitor_loop())
            
            emoji_logger.system_info("✅ ConversationMonitor: Loop de monitoramento iniciado")
        except Exception as e:
            emoji_logger.system_error("ConversationMonitor", f"Erro ao inicializar: {e}")
    
    async def register_message(self, 
                              phone: str, 
                              is_from_user: bool,
                              lead_info: Optional[Dict[str, Any]] = None):
        """
        Registra uma mensagem na conversa
        
        Args:
            phone: Número do telefone
            is_from_user: True se mensagem do usuário, False se do bot
            lead_info: Informações do lead (opcional)
        """
        try:
            # Normalizar número do telefone
            clean_phone = self._normalize_phone(phone)
            
            # Atualizar timestamp da última mensagem
            self.active_conversations[clean_phone] = datetime.now()
            
            # Se é mensagem do usuário, resetar status de follow-up
            if is_from_user:
                self.follow_up_status[clean_phone] = 'active'
                emoji_logger.system_debug(f"📨 Conversa ativa registrada: {clean_phone[:8]}...")
            else:
                emoji_logger.system_debug(f"🤖 Resposta do bot registrada: {clean_phone[:8]}...")
                
        except Exception as e:
            emoji_logger.system_error("ConversationMonitor", f"Erro ao registrar mensagem: {e}")
    
    def _normalize_phone(self, phone: str) -> str:
        """
        Normaliza o número do telefone
        
        Args:
            phone: Número do telefone
            
        Returns:
            Número normalizado com DDI 55
        """
        # Remover caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Adicionar DDI brasileiro se não tiver
        if not clean_phone.startswith('55'):
            clean_phone = '55' + clean_phone
            
        return clean_phone
    
    async def _monitor_loop(self):
        """Loop de monitoramento em background - executa a cada 60 segundos"""
        while self.is_monitoring:
            try:
                await self._check_inactive_conversations()
                await asyncio.sleep(60)  # Verificar a cada 1 minuto
            except Exception as e:
                emoji_logger.system_error("ConversationMonitor", f"Erro no monitor loop: {e}")
                await asyncio.sleep(60)  # Continuar mesmo com erro
    
    async def _check_inactive_conversations(self):
        """Verifica conversas inativas e agenda follow-ups quando necessário"""
        try:
            now = datetime.now()
            
            # Fazer cópia da lista para evitar modificação durante iteração
            conversations_copy = list(self.active_conversations.items())
            
            for phone, last_message_time in conversations_copy:
                # Calcular tempo de inatividade
                inactive_time = now - last_message_time
                current_status = self.follow_up_status.get(phone, 'active')
                
                # Follow-up de 30 minutos (IMMEDIATE_REENGAGEMENT)
                if (inactive_time > timedelta(minutes=30) and 
                    current_status != 'followup_30min_sent'):
                    
                    await self._schedule_followup(phone, 'IMMEDIATE_REENGAGEMENT')
                    self.follow_up_status[phone] = 'followup_30min_sent'
                    emoji_logger.system_info(f"⏰ Follow-up 30min agendado: {phone[:8]}...")
                
                # Follow-up de 24 horas (DAILY_NURTURING)
                elif (inactive_time > timedelta(hours=24) and 
                      current_status != 'followup_24h_sent'):
                    
                    await self._schedule_followup(phone, 'DAILY_NURTURING')
                    self.follow_up_status[phone] = 'followup_24h_sent'
                    emoji_logger.system_info(f"📅 Follow-up 24h agendado: {phone[:8]}...")
                
                # Remover conversas muito antigas (7 dias)
                elif inactive_time > timedelta(days=7):
                    del self.active_conversations[phone]
                    if phone in self.follow_up_status:
                        del self.follow_up_status[phone]
                    emoji_logger.system_debug(f"🗑️ Conversa antiga removida: {phone[:8]}...")
                    
        except Exception as e:
            emoji_logger.system_error("ConversationMonitor", f"Erro ao verificar conversas inativas: {e}")
    
    async def _schedule_followup(self, phone: str, followup_type: str):
        """
        Agenda um follow-up no banco de dados
        
        Args:
            phone: Número do telefone normalizado
            followup_type: Tipo do follow-up (IMMEDIATE_REENGAGEMENT ou DAILY_NURTURING)
        """
        try:
            # Buscar lead pelo telefone (Supabase é síncrono, não usa await)
            lead_result = self.db.client.table('leads').select("*").eq('phone_number', phone).execute()
            
            if lead_result.data and len(lead_result.data) > 0:
                lead = lead_result.data[0]
                
                # Preparar dados do follow-up
                followup_data = {
                    'lead_id': lead['id'],
                    'phone_number': phone,
                    'type': followup_type,  # Campo obrigatório
                    'scheduled_at': datetime.now().isoformat(),
                    'status': 'pending',
                    'message': '',  # Vazio para usar IA na geração
                    'follow_up_type': followup_type,  # Duplicado por compatibilidade
                    'priority': 'medium',
                    'attempt': 0,
                    'metadata': {
                        'source': 'conversation_monitor',
                        'inactive_since': self.active_conversations.get(phone, datetime.now()).isoformat()
                    }
                }
                
                # Inserir no banco (Supabase é síncrono, não usa await)
                self.db.client.table('follow_ups').insert(followup_data).execute()
                emoji_logger.system_info(f"✅ Follow-up agendado no banco: {followup_type} para {phone[:8]}...")
                
            else:
                emoji_logger.system_warning(f"⚠️ Lead não encontrado para telefone: {phone[:8]}...")
                
        except Exception as e:
            emoji_logger.system_error("ConversationMonitor", f"Erro ao agendar follow-up: {e}")
    
    async def shutdown(self):
        """Desliga o monitor de conversas"""
        self.is_monitoring = False
        emoji_logger.system_info("🛑 ConversationMonitor desligado")

# Singleton pattern - instância única global
_conversation_monitor = None

def get_conversation_monitor() -> ConversationMonitor:
    """
    Retorna a instância singleton do ConversationMonitor
    
    Returns:
        ConversationMonitor: Instância única do monitor
    """
    global _conversation_monitor
    if _conversation_monitor is None:
        _conversation_monitor = ConversationMonitor()
    return _conversation_monitor