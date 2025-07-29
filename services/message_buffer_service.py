"""
Message Buffer Service
======================
Serviço para gerenciar buffer de mensagens consecutivas do WhatsApp
Detecta quando usuário está enviando múltiplas mensagens e aguarda finalização
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
from services.redis_fallback import get_redis_fallback_service


class MessageBufferService:
    """Gerencia buffer de mensagens para processar múltiplas mensagens como contexto único"""
    
    def __init__(self):
        self.enabled = os.getenv("MESSAGE_BUFFER_ENABLED", "true").lower() == "true"
        self.timeout_seconds = float(os.getenv("MESSAGE_BUFFER_TIMEOUT", "8"))
        self.max_messages = int(os.getenv("MESSAGE_BUFFER_MAX_MESSAGES", "20"))
        self.min_interval = float(os.getenv("MESSAGE_BUFFER_MIN_INTERVAL", "0.5"))
        
        # Timers ativos por número de telefone
        self._active_timers: Dict[str, asyncio.Task] = {}
        
        # Callbacks para processar mensagens consolidadas
        self._process_callbacks: Dict[str, Any] = {}
        
        # Buffer local de mensagens como fallback
        self._local_buffers: Dict[str, List[Dict[str, Any]]] = {}
        
        # Locks para evitar condições de corrida
        self._locks: Dict[str, asyncio.Lock] = {}
        
        # Flags para indicar se buffer está sendo processado
        self._processing: Dict[str, bool] = {}
        
        # Obter instância do redis fallback
        self.redis_service = None
        
        logger.info(f"MessageBufferService iniciado - Enabled: {self.enabled}, Timeout: {self.timeout_seconds}s")
    
    async def add_message(
        self, 
        phone: str, 
        message_data: Dict[str, Any],
        process_callback: Any
    ) -> bool:
        """
        Adiciona mensagem ao buffer e gerencia timer
        
        Args:
            phone: Número do telefone
            message_data: Dados da mensagem (incluindo content, type, etc)
            process_callback: Função async para processar mensagens consolidadas
            
        Returns:
            bool: True se mensagem foi adicionada ao buffer, False se deve processar imediatamente
        """
        if not self.enabled:
            return False
            
        # Garantir que temos um lock para este telefone
        if phone not in self._locks:
            self._locks[phone] = asyncio.Lock()
            
        async with self._locks[phone]:
            try:
                # Verificar se já está processando
                if self._processing.get(phone, False):
                    logger.warning(f"Buffer já está sendo processado para {phone}, ignorando nova mensagem")
                    return False
                
                # Adicionar timestamp à mensagem
                message_data["buffered_at"] = datetime.now().isoformat()
                
                # Inicializar buffer local se não existir
                if phone not in self._local_buffers:
                    self._local_buffers[phone] = []
                
                # Adicionar mensagem ao buffer local
                self._local_buffers[phone].append(message_data)
                logger.info(f"Mensagem adicionada ao buffer para {phone}. Total no buffer: {len(self._local_buffers[phone])}")
                
                # Verificar se excedeu limite de mensagens
                if len(self._local_buffers[phone]) >= self.max_messages:
                    logger.warning(f"Buffer excedeu limite ({self.max_messages}) para {phone}")
                    # Marcar como processando e processar imediatamente
                    self._processing[phone] = True
                    # Cancelar timer se existir
                    if phone in self._active_timers:
                        self._active_timers[phone].cancel()
                        del self._active_timers[phone]
                    # Processar buffer
                    asyncio.create_task(self._process_buffer_with_lock(phone))
                    return True
                
                # Salvar callback para este número
                self._process_callbacks[phone] = process_callback
                
                # Cancelar timer existente se houver
                if phone in self._active_timers:
                    logger.debug(f"Cancelando timer existente para {phone}")
                    self._active_timers[phone].cancel()
                
                # Criar novo timer
                self._active_timers[phone] = asyncio.create_task(
                    self._wait_and_process(phone)
                )
                
                logger.info(f"Timer criado/resetado para {phone} - Aguardando {self.timeout_seconds}s para processar {len(self._local_buffers[phone])} mensagens")
                return True
                
            except Exception as e:
                logger.error(f"Erro ao adicionar mensagem ao buffer: {e}", exc_info=True)
                return False
    
    async def _wait_and_process(self, phone: str):
        """Aguarda timeout e processa buffer"""
        try:
            logger.debug(f"Timer iniciado para {phone} - aguardando {self.timeout_seconds}s")
            # Aguardar timeout
            await asyncio.sleep(self.timeout_seconds)
            
            # Garantir que temos um lock
            if phone not in self._locks:
                self._locks[phone] = asyncio.Lock()
            
            async with self._locks[phone]:
                # Verificar se ainda somos o timer ativo e se não está processando
                if (phone in self._active_timers and 
                    self._active_timers[phone] == asyncio.current_task() and
                    not self._processing.get(phone, False)):
                    
                    logger.info(f"Timer expirado para {phone} - iniciando processamento")
                    # Marcar como processando
                    self._processing[phone] = True
                    # Remover do active_timers
                    del self._active_timers[phone]
                    
                    # Processar buffer em task separada
                    asyncio.create_task(self._process_buffer_with_lock(phone))
                else:
                    logger.debug(f"Timer expirado mas condições não atendidas para {phone} - processando: {self._processing.get(phone, False)}")
            
        except asyncio.CancelledError:
            # Timer foi cancelado (nova mensagem chegou)
            logger.debug(f"Timer cancelado para {phone} - nova mensagem deve ter chegado")
        except Exception as e:
            logger.error(f"Erro no timer do buffer: {e}", exc_info=True)
        finally:
            # Limpar timer apenas se for o timer atual
            if phone in self._active_timers and self._active_timers[phone] == asyncio.current_task():
                logger.debug(f"Limpando timer para {phone}")
                del self._active_timers[phone]
    
    async def _process_buffer_with_lock(self, phone: str):
        """Processa buffer com proteção de lock e limpeza de flags"""
        try:
            await self._process_buffer(phone)
        finally:
            # Sempre limpar flag de processamento
            if phone in self._processing:
                del self._processing[phone]
                logger.debug(f"Flag de processamento limpa para {phone}")

    async def _process_buffer(self, phone: str):
        """Processa todas as mensagens do buffer"""
        try:
            # Obter mensagens do buffer local
            messages = self._local_buffers.get(phone, [])
            
            if not messages:
                logger.warning(f"Buffer vazio para {phone}")
                return
            
            logger.info(f"Iniciando processamento de {len(messages)} mensagens do buffer para {phone}")
            
            # Copiar e limpar buffer local ANTES de processar (evita reprocessamento)
            messages_to_process = messages.copy()
            self._local_buffers[phone] = []
            
            # Obter callback
            callback = self._process_callbacks.get(phone)
            if not callback:
                logger.error(f"Callback não encontrado para {phone}")
                # Restaurar mensagens no buffer se não houver callback
                self._local_buffers[phone] = messages_to_process
                return
            
            # Log detalhado das mensagens sendo processadas
            for i, msg in enumerate(messages_to_process):
                logger.debug(f"  Mensagem {i+1}: {msg.get('content', '')[:50]}... (tipo: {msg.get('type')})")
            
            # Executar callback com todas as mensagens
            logger.info(f"Executando callback para processar {len(messages_to_process)} mensagens de {phone}")
            await callback(messages_to_process)
            
            # Limpar callback
            if phone in self._process_callbacks:
                del self._process_callbacks[phone]
                
            logger.info(f"Processamento concluído para {phone} - {len(messages_to_process)} mensagens processadas")
                
        except Exception as e:
            logger.error(f"Erro ao processar buffer para {phone}: {e}", exc_info=True)
            # Em caso de erro, restaurar mensagens no buffer se possível
            if 'messages_to_process' in locals() and phone not in self._local_buffers:
                self._local_buffers[phone] = messages_to_process
                logger.warning(f"Mensagens restauradas no buffer devido a erro para {phone}")
    
    async def get_buffer_status(self, phone: str) -> Dict[str, Any]:
        """Obtém status do buffer para um número"""
        try:
            # Obter tamanho do buffer local
            buffer_size = len(self._local_buffers.get(phone, []))
            
            # Verificar se há timer ativo
            has_active_timer = phone in self._active_timers
            
            # Verificar se está processando
            is_processing = self._processing.get(phone, False)
            
            return {
                "phone": phone,
                "buffer_size": buffer_size,
                "has_active_timer": has_active_timer,
                "is_processing": is_processing,
                "timeout_seconds": self.timeout_seconds,
                "enabled": self.enabled,
                "has_lock": phone in self._locks
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do buffer: {e}")
            return {"error": str(e)}
    
    async def force_process(self, phone: str) -> bool:
        """Força processamento imediato do buffer"""
        # Garantir que temos um lock
        if phone not in self._locks:
            self._locks[phone] = asyncio.Lock()
            
        async with self._locks[phone]:
            try:
                # Verificar se já está processando
                if self._processing.get(phone, False):
                    logger.warning(f"Buffer já está sendo processado para {phone}")
                    return False
                
                # Cancelar timer se existir
                if phone in self._active_timers:
                    self._active_timers[phone].cancel()
                    del self._active_timers[phone]
                
                # Marcar como processando
                self._processing[phone] = True
                
                # Processar buffer
                asyncio.create_task(self._process_buffer_with_lock(phone))
                return True
                
            except Exception as e:
                logger.error(f"Erro ao forçar processamento: {e}")
                return False
    
    async def clear_buffer(self, phone: str) -> bool:
        """Limpa buffer sem processar"""
        # Garantir que temos um lock
        if phone not in self._locks:
            self._locks[phone] = asyncio.Lock()
            
        async with self._locks[phone]:
            try:
                # Verificar se está processando
                if self._processing.get(phone, False):
                    logger.warning(f"Não é possível limpar buffer - processamento em andamento para {phone}")
                    return False
                
                # Cancelar timer se existir
                if phone in self._active_timers:
                    self._active_timers[phone].cancel()
                    del self._active_timers[phone]
                
                # Limpar buffer local
                if phone in self._local_buffers:
                    num_messages = len(self._local_buffers[phone])
                    del self._local_buffers[phone]
                    logger.info(f"Buffer limpo para {phone} - {num_messages} mensagens descartadas")
                
                # Limpar callback
                if phone in self._process_callbacks:
                    del self._process_callbacks[phone]
                
                return True
                
            except Exception as e:
                logger.error(f"Erro ao limpar buffer: {e}")
                return False
    
    def is_buffer_active(self, phone: str) -> bool:
        """Verifica se há buffer ativo para o número"""
        return phone in self._active_timers


# Instância global
message_buffer_service = MessageBufferService()