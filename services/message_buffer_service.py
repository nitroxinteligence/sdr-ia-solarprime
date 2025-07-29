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
from services.redis_service import redis_service


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
            
        try:
            # Criar chave única para o buffer deste número
            buffer_key = f"msg_buffer:{phone}"
            
            # Adicionar timestamp à mensagem
            message_data["buffered_at"] = datetime.now().isoformat()
            
            # Adicionar mensagem ao buffer (Redis LPUSH)
            await redis_service.connect()
            
            if redis_service.client:
                # Converter para JSON para armazenar no Redis
                message_json = json.dumps(message_data, ensure_ascii=False)
                await redis_service.client.lpush(buffer_key, message_json)
                
                # Verificar se excedeu limite de mensagens
                buffer_size = await redis_service.client.llen(buffer_key)
                if buffer_size >= self.max_messages:
                    logger.warning(f"Buffer excedeu limite ({self.max_messages}) para {phone}")
                    await self._process_buffer(phone)
                    return True
            else:
                # Fallback se Redis não estiver disponível
                logger.warning("Redis não disponível, processando mensagem imediatamente")
                return False
            
            # Salvar callback para este número
            self._process_callbacks[phone] = process_callback
            
            # Cancelar timer existente se houver
            if phone in self._active_timers:
                self._active_timers[phone].cancel()
                logger.debug(f"Timer resetado para {phone}")
            
            # Criar novo timer
            self._active_timers[phone] = asyncio.create_task(
                self._wait_and_process(phone)
            )
            
            logger.info(f"Mensagem adicionada ao buffer para {phone} - Timer: {self.timeout_seconds}s")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem ao buffer: {e}")
            return False
    
    async def _wait_and_process(self, phone: str):
        """Aguarda timeout e processa buffer"""
        try:
            # Aguardar timeout
            await asyncio.sleep(self.timeout_seconds)
            
            # Processar buffer apenas se ainda estivermos no timer ativo
            if phone in self._active_timers and self._active_timers[phone] == asyncio.current_task():
                await self._process_buffer(phone)
            
        except asyncio.CancelledError:
            # Timer foi cancelado (nova mensagem chegou)
            logger.debug(f"Timer cancelado para {phone}")
        except Exception as e:
            logger.error(f"Erro no timer do buffer: {e}")
        finally:
            # Limpar timer apenas se for o timer atual
            if phone in self._active_timers and self._active_timers[phone] == asyncio.current_task():
                del self._active_timers[phone]
    
    async def _process_buffer(self, phone: str):
        """Processa todas as mensagens do buffer"""
        try:
            buffer_key = f"msg_buffer:{phone}"
            
            # Obter todas as mensagens do buffer
            await redis_service.connect()
            
            if not redis_service.client:
                logger.error("Redis não disponível para processar buffer")
                return
            
            # Obter mensagens (LRANGE para pegar todas)
            messages_json = await redis_service.client.lrange(buffer_key, 0, -1)
            
            if not messages_json:
                logger.warning(f"Buffer vazio para {phone}")
                return
            
            # Converter de JSON e reverter ordem (LPUSH adiciona no início)
            messages = []
            for msg_json in reversed(messages_json):
                try:
                    msg_str = msg_json.decode() if isinstance(msg_json, bytes) else msg_json
                    messages.append(json.loads(msg_str))
                except Exception as e:
                    logger.error(f"Erro ao decodificar mensagem do buffer: {e}")
            
            # Limpar buffer
            await redis_service.client.delete(buffer_key)
            
            # Obter callback
            callback = self._process_callbacks.get(phone)
            if not callback:
                logger.error(f"Callback não encontrado para {phone}")
                return
            
            logger.info(f"Processando {len(messages)} mensagens do buffer para {phone}")
            
            # Executar callback com todas as mensagens
            await callback(messages)
            
            # Limpar callback
            if phone in self._process_callbacks:
                del self._process_callbacks[phone]
                
        except Exception as e:
            logger.error(f"Erro ao processar buffer para {phone}: {e}", exc_info=True)
    
    async def get_buffer_status(self, phone: str) -> Dict[str, Any]:
        """Obtém status do buffer para um número"""
        try:
            buffer_key = f"msg_buffer:{phone}"
            
            await redis_service.connect()
            if not redis_service.client:
                return {"error": "Redis não disponível"}
            
            # Obter tamanho do buffer
            buffer_size = await redis_service.client.llen(buffer_key)
            
            # Verificar se há timer ativo
            has_active_timer = phone in self._active_timers
            
            return {
                "phone": phone,
                "buffer_size": buffer_size,
                "has_active_timer": has_active_timer,
                "timeout_seconds": self.timeout_seconds,
                "enabled": self.enabled
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do buffer: {e}")
            return {"error": str(e)}
    
    async def force_process(self, phone: str) -> bool:
        """Força processamento imediato do buffer"""
        try:
            # Cancelar timer se existir
            if phone in self._active_timers:
                self._active_timers[phone].cancel()
            
            # Processar buffer
            await self._process_buffer(phone)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao forçar processamento: {e}")
            return False
    
    async def clear_buffer(self, phone: str) -> bool:
        """Limpa buffer sem processar"""
        try:
            buffer_key = f"msg_buffer:{phone}"
            
            # Cancelar timer se existir
            if phone in self._active_timers:
                self._active_timers[phone].cancel()
                del self._active_timers[phone]
            
            # Limpar buffer no Redis
            await redis_service.connect()
            if redis_service.client:
                await redis_service.client.delete(buffer_key)
            
            # Limpar callback
            if phone in self._process_callbacks:
                del self._process_callbacks[phone]
            
            logger.info(f"Buffer limpo para {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar buffer: {e}")
            return False
    
    def is_buffer_active(self, phone: str) -> bool:
        """Verifica se há buffer ativo para o número"""
        return phone in self._active_timers


# Instância global
message_buffer_service = MessageBufferService()