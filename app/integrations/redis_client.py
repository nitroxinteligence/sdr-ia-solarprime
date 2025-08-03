"""
Redis Client - Cache e Filas
"""
import redis.asyncio as redis
import json
import pickle
from typing import Optional, Any, List, Dict
from datetime import datetime, timedelta
from loguru import logger
from app.config import settings

class RedisClient:
    """Cliente Redis para cache e filas"""
    
    def __init__(self):
        self.redis_url = settings.get_redis_url()
        self.redis_client = None
        self.default_ttl = 3600  # 1 hora padrão
        
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50
            )
            
            # Testa conexão
            await self.redis_client.ping()
            logger.info("Conectado ao Redis com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")
            raise
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Desconectado do Redis")
    
    # ==================== CACHE ====================
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor ou None se não existir
        """
        try:
            value = await self.redis_client.get(key)
            
            if value:
                # Tenta deserializar JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Se não for JSON, retorna como string
                    return value
                    
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter cache {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Define valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: Tempo de vida em segundos
            
        Returns:
            True se sucesso
        """
        try:
            # Serializa para JSON se necessário
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            # Define com TTL
            if ttl is None:
                ttl = self.default_ttl
            
            await self.redis_client.setex(key, ttl, value)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir cache {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Remove chave do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            True se removido
        """
        try:
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Verifica se chave existe
        
        Args:
            key: Chave do cache
            
        Returns:
            True se existe
        """
        try:
            return await self.redis_client.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Erro ao verificar cache {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        Define TTL para chave existente
        
        Args:
            key: Chave do cache
            ttl: Tempo de vida em segundos
            
        Returns:
            True se sucesso
        """
        try:
            return await self.redis_client.expire(key, ttl)
            
        except Exception as e:
            logger.error(f"Erro ao definir TTL {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """
        Obtém TTL restante de uma chave
        
        Args:
            key: Chave do cache
            
        Returns:
            TTL em segundos ou -1 se não tem TTL
        """
        try:
            return await self.redis_client.ttl(key)
            
        except Exception as e:
            logger.error(f"Erro ao obter TTL {key}: {e}")
            return -1
    
    # ==================== CACHE ESPECÍFICO ====================
    
    async def cache_conversation(
        self,
        phone: str,
        conversation_data: Dict[str, Any],
        ttl: int = 7200  # 2 horas
    ):
        """
        Cache de conversa
        
        Args:
            phone: Número do telefone
            conversation_data: Dados da conversa
            ttl: Tempo de vida
        """
        key = f"conversation:{phone}"
        await self.set(key, conversation_data, ttl)
    
    async def get_conversation(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Obtém conversa do cache
        
        Args:
            phone: Número do telefone
            
        Returns:
            Dados da conversa ou None
        """
        key = f"conversation:{phone}"
        return await self.get(key)
    
    async def cache_lead_info(
        self,
        phone: str,
        lead_data: Dict[str, Any],
        ttl: int = 86400  # 24 horas
    ):
        """
        Cache de informações do lead
        
        Args:
            phone: Número do telefone
            lead_data: Dados do lead
            ttl: Tempo de vida
        """
        key = f"lead:{phone}"
        await self.set(key, lead_data, ttl)
    
    async def get_lead_info(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações do lead do cache
        
        Args:
            phone: Número do telefone
            
        Returns:
            Dados do lead ou None
        """
        key = f"lead:{phone}"
        return await self.get(key)
    
    # ==================== FILAS ====================
    
    async def enqueue(
        self,
        queue_name: str,
        data: Any,
        priority: int = 0
    ) -> bool:
        """
        Adiciona item à fila
        
        Args:
            queue_name: Nome da fila
            data: Dados a enfileirar
            priority: Prioridade (0 = normal, 1 = alta)
            
        Returns:
            True se sucesso
        """
        try:
            # Cria payload com timestamp
            payload = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "priority": priority
            }
            
            # Serializa
            value = json.dumps(payload)
            
            # Adiciona à fila apropriada
            if priority > 0:
                queue_key = f"queue:priority:{queue_name}"
                await self.redis_client.lpush(queue_key, value)
            else:
                queue_key = f"queue:{queue_name}"
                await self.redis_client.rpush(queue_key, value)
            
            logger.debug(f"Item adicionado à fila {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enfileirar em {queue_name}: {e}")
            return False
    
    async def dequeue(
        self,
        queue_name: str,
        timeout: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Remove item da fila
        
        Args:
            queue_name: Nome da fila
            timeout: Timeout em segundos (0 = não bloqueia)
            
        Returns:
            Item da fila ou None
        """
        try:
            # Verifica fila de prioridade primeiro
            priority_key = f"queue:priority:{queue_name}"
            normal_key = f"queue:{queue_name}"
            
            # Tenta fila de prioridade
            value = await self.redis_client.lpop(priority_key)
            
            # Se não tem, tenta fila normal
            if not value:
                if timeout > 0:
                    # Bloqueia esperando item
                    result = await self.redis_client.blpop(normal_key, timeout)
                    if result:
                        value = result[1]
                else:
                    value = await self.redis_client.lpop(normal_key)
            
            if value:
                return json.loads(value)
                
            return None
            
        except Exception as e:
            logger.error(f"Erro ao desenfileirar de {queue_name}: {e}")
            return None
    
    async def queue_size(self, queue_name: str) -> int:
        """
        Obtém tamanho da fila
        
        Args:
            queue_name: Nome da fila
            
        Returns:
            Número de itens na fila
        """
        try:
            priority_key = f"queue:priority:{queue_name}"
            normal_key = f"queue:{queue_name}"
            
            priority_size = await self.redis_client.llen(priority_key)
            normal_size = await self.redis_client.llen(normal_key)
            
            return priority_size + normal_size
            
        except Exception as e:
            logger.error(f"Erro ao obter tamanho da fila {queue_name}: {e}")
            return 0
    
    # ==================== FILAS ESPECÍFICAS ====================
    
    async def enqueue_follow_up(
        self,
        phone: str,
        message: str,
        scheduled_at: datetime,
        follow_up_type: str
    ):
        """
        Enfileira follow-up
        
        Args:
            phone: Número do telefone
            message: Mensagem de follow-up
            scheduled_at: Quando enviar
            follow_up_type: Tipo de follow-up
        """
        data = {
            "phone": phone,
            "message": message,
            "scheduled_at": scheduled_at.isoformat(),
            "type": follow_up_type
        }
        
        await self.enqueue("follow_ups", data)
    
    async def enqueue_message(
        self,
        phone: str,
        message: str,
        priority: int = 0
    ):
        """
        Enfileira mensagem para envio
        
        Args:
            phone: Número do telefone
            message: Mensagem a enviar
            priority: Prioridade
        """
        data = {
            "phone": phone,
            "message": message,
            "type": "text"
        }
        
        await self.enqueue("messages", data, priority)
    
    # ==================== RATE LIMITING ====================
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Verifica rate limit
        
        Args:
            key: Chave do rate limit
            max_requests: Máximo de requisições
            window_seconds: Janela de tempo em segundos
            
        Returns:
            True se permitido, False se excedeu limite
        """
        try:
            rate_key = f"rate:{key}"
            
            # Incrementa contador
            current = await self.redis_client.incr(rate_key)
            
            # Define TTL na primeira requisição
            if current == 1:
                await self.redis_client.expire(rate_key, window_seconds)
            
            # Verifica se excedeu
            return current <= max_requests
            
        except Exception as e:
            logger.error(f"Erro ao verificar rate limit {key}: {e}")
            return True  # Permite em caso de erro
    
    async def get_rate_limit_remaining(
        self,
        key: str,
        max_requests: int
    ) -> int:
        """
        Obtém requisições restantes
        
        Args:
            key: Chave do rate limit
            max_requests: Máximo de requisições
            
        Returns:
            Número de requisições restantes
        """
        try:
            rate_key = f"rate:{key}"
            current = await self.redis_client.get(rate_key)
            
            if current:
                remaining = max_requests - int(current)
                return max(0, remaining)
                
            return max_requests
            
        except Exception as e:
            logger.error(f"Erro ao obter rate limit {key}: {e}")
            return max_requests
    
    # ==================== LOCKS ====================
    
    async def acquire_lock(
        self,
        key: str,
        ttl: int = 10
    ) -> bool:
        """
        Adquire lock distribuído
        
        Args:
            key: Chave do lock
            ttl: Tempo de vida do lock
            
        Returns:
            True se adquiriu lock
        """
        try:
            lock_key = f"lock:{key}"
            
            # Tenta definir com NX (only if not exists)
            result = await self.redis_client.set(
                lock_key,
                "1",
                nx=True,
                ex=ttl
            )
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Erro ao adquirir lock {key}: {e}")
            return False
    
    async def release_lock(self, key: str) -> bool:
        """
        Libera lock
        
        Args:
            key: Chave do lock
            
        Returns:
            True se liberou
        """
        try:
            lock_key = f"lock:{key}"
            return await self.delete(lock_key)
            
        except Exception as e:
            logger.error(f"Erro ao liberar lock {key}: {e}")
            return False
    
    # ==================== PUBSUB ====================
    
    async def publish(self, channel: str, message: Any):
        """
        Publica mensagem em canal
        
        Args:
            channel: Nome do canal
            message: Mensagem a publicar
        """
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
                
            await self.redis_client.publish(channel, message)
            logger.debug(f"Mensagem publicada em {channel}")
            
        except Exception as e:
            logger.error(f"Erro ao publicar em {channel}: {e}")
    
    async def subscribe(self, channels: List[str]):
        """
        Inscreve em canais
        
        Args:
            channels: Lista de canais
            
        Returns:
            PubSub object
        """
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(*channels)
            logger.info(f"Inscrito em canais: {channels}")
            return pubsub
            
        except Exception as e:
            logger.error(f"Erro ao inscrever em canais: {e}")
            return None
    
    # ==================== ANALYTICS ====================
    
    async def increment_counter(
        self,
        counter_name: str,
        amount: int = 1
    ) -> int:
        """
        Incrementa contador
        
        Args:
            counter_name: Nome do contador
            amount: Quantidade a incrementar
            
        Returns:
            Valor atual do contador
        """
        try:
            key = f"counter:{counter_name}"
            return await self.redis_client.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Erro ao incrementar contador {counter_name}: {e}")
            return 0
    
    async def get_counter(self, counter_name: str) -> int:
        """
        Obtém valor do contador
        
        Args:
            counter_name: Nome do contador
            
        Returns:
            Valor do contador
        """
        try:
            key = f"counter:{counter_name}"
            value = await self.redis_client.get(key)
            return int(value) if value else 0
            
        except Exception as e:
            logger.error(f"Erro ao obter contador {counter_name}: {e}")
            return 0
    
    async def reset_counter(self, counter_name: str):
        """
        Reseta contador
        
        Args:
            counter_name: Nome do contador
        """
        key = f"counter:{counter_name}"
        await self.delete(key)
    
    # ==================== SESSIONS ====================
    
    async def save_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: int = 3600
    ):
        """
        Salva sessão
        
        Args:
            session_id: ID da sessão
            data: Dados da sessão
            ttl: Tempo de vida
        """
        key = f"session:{session_id}"
        await self.set(key, data, ttl)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dados da sessão ou None
        """
        key = f"session:{session_id}"
        return await self.get(key)
    
    async def extend_session(self, session_id: str, ttl: int = 3600):
        """
        Estende TTL da sessão
        
        Args:
            session_id: ID da sessão
            ttl: Novo TTL
        """
        key = f"session:{session_id}"
        await self.expire(key, ttl)
    
    async def end_session(self, session_id: str):
        """
        Encerra sessão
        
        Args:
            session_id: ID da sessão
        """
        key = f"session:{session_id}"
        await self.delete(key)


# Singleton global
redis_client = RedisClient()