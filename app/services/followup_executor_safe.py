"""
FollowUp Executor com tratamento de erros robusto
ZERO COMPLEXIDADE - Funciona mesmo com falhas parciais
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.utils.logger import emoji_logger
from app.config import settings
from app.database.supabase_client import supabase_client

class FollowUpExecutorSafe:
    """Executor de follow-ups com fallback seguro"""
    
    def __init__(self):
        """Inicializa executor de forma segura"""
        self.db = None
        self.running = False
        self.check_interval = 60  # 1 minuto
        self.enabled = getattr(settings, 'ENABLE_FOLLOWUP_AGENT', True)
        
        # Inicializa DB se disponível
        try:
            self.db = supabase_client
            emoji_logger.log_with_emoji("INFO", "Service", "✅ FollowUp Executor inicializado")
        except Exception as e:
            emoji_logger.log_with_emoji("WARNING", "Service", f"⚠️ FollowUp sem DB: {str(e)}")
            self.enabled = False
    
    async def start(self):
        """Inicia loop de verificação de follow-ups"""
        if not self.enabled:
            emoji_logger.log_with_emoji("INFO", "Service", "ℹ️ FollowUp Executor desabilitado")
            return
            
        self.running = True
        emoji_logger.log_with_emoji("INFO", "Service", "🔄 Iniciando FollowUp Executor")
        
        # Loop principal com tratamento de erros
        while self.running:
            try:
                await self._check_and_execute_followups()
            except Exception as e:
                emoji_logger.log_with_emoji("ERROR", "Service", f"❌ Erro no FollowUp loop: {str(e)}")
            
            # Aguarda próximo ciclo
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Para o executor"""
        self.running = False
        emoji_logger.info("Service", "⏹️ FollowUp Executor parado")
    
    async def _check_and_execute_followups(self):
        """Verifica e executa follow-ups pendentes com segurança"""
        if not self.db:
            return
            
        try:
            now = datetime.now()
            
            # Busca follow-ups pendentes
            result = self.db.client.table('follow_ups').select("*").eq(
                'status', 'PENDING'
            ).lte(
                'scheduled_at', now.isoformat()
            ).execute()
            
            if not result or not result.data:
                return
            
            emoji_logger.info("Service", f"📋 {len(result.data)} follow-ups pendentes")
            
            # Processa cada follow-up
            for followup in result.data:
                try:
                    await self._execute_single_followup(followup)
                except Exception as e:
                    emoji_logger.error("Service", f"❌ Erro em follow-up {followup.get('id')}: {str(e)}")
                    
        except Exception as e:
            emoji_logger.error("Service", f"❌ Erro ao buscar follow-ups: {str(e)}")
    
    async def _execute_single_followup(self, followup: Dict[str, Any]):
        """Executa um follow-up individual com segurança"""
        try:
            followup_id = followup.get('id')
            followup_type = followup.get('type', 'UNKNOWN')
            phone = followup.get('phone_number')
            
            if not phone:
                emoji_logger.warning("Service", f"⚠️ Follow-up {followup_id} sem telefone")
                return
            
            emoji_logger.info("Service", f"🚀 Executando follow-up {followup_type} para {phone}")
            
            # Marca como processando para evitar duplicação
            self.db.client.table('follow_ups').update({
                'status': 'PROCESSING',
                'executed_at': datetime.now().isoformat()
            }).eq('id', followup_id).execute()
            
            # Executa ação baseada no tipo
            success = await self._execute_followup_action(followup)
            
            # Atualiza status final
            final_status = 'COMPLETED' if success else 'FAILED'
            self.db.client.table('follow_ups').update({
                'status': final_status,
                'completed_at': datetime.now().isoformat() if success else None
            }).eq('id', followup_id).execute()
            
            emoji_logger.info("Service", f"✅ Follow-up {followup_id} {final_status}")
            
        except Exception as e:
            emoji_logger.error("Service", f"❌ Erro executando follow-up: {str(e)}")
    
    async def _execute_followup_action(self, followup: Dict[str, Any]) -> bool:
        """Executa ação específica do follow-up"""
        try:
            followup_type = followup.get('type', '')
            phone = followup.get('phone_number')
            message = followup.get('message', '')
            
            # Por enquanto, apenas loga a ação
            # TODO: Integrar com Evolution API para enviar mensagem
            emoji_logger.info("Service", f"📨 Follow-up {followup_type}: {phone} - {message[:50]}...")
            
            # Simula envio bem-sucedido
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            emoji_logger.error("Service", f"❌ Erro na ação do follow-up: {str(e)}")
            return False

# Instância global
_executor_instance = None

def get_followup_executor() -> FollowUpExecutorSafe:
    """Retorna instância singleton do executor"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = FollowUpExecutorSafe()
    return _executor_instance

async def start_followup_executor():
    """Inicia o executor de follow-ups"""
    executor = get_followup_executor()
    await executor.start()