"""
Message Buffer Service - Simples e eficiente usando asyncio.Queue
"""
import asyncio
from typing import Dict, List, Optional
from loguru import logger
from app.utils.logger import emoji_logger

class MessageBuffer:
    """
    Buffer inteligente - processa imediatamente se agente está livre,
    só aguarda timeout se agente está ocupado processando
    """
    
    def __init__(self, timeout: float = 10.0, max_size: int = 10):
        """
        Inicializa o buffer
        
        Args:
            timeout: Tempo máximo de espera em segundos
            max_size: Número máximo de mensagens no buffer
        """
        self.timeout = timeout
        self.max_size = max_size
        self.queues: Dict[str, asyncio.Queue] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.processing_locks: Dict[str, asyncio.Lock] = {}  # Lock por usuário
        
        emoji_logger.system_info(f"Buffer Inteligente inicializado (timeout={timeout}s, max={max_size})")
    
    async def add_message(self, phone: str, content: str, message_data: Dict) -> None:
        """
        Adiciona mensagem ao buffer
        
        Args:
            phone: Número do telefone
            content: Conteúdo da mensagem
            message_data: Dados completos da mensagem
        """
        # Cria queue se não existe
        if phone not in self.queues:
            self.queues[phone] = asyncio.Queue(maxsize=self.max_size)
            # Inicia task de processamento
            self.tasks[phone] = asyncio.create_task(
                self._process_queue(phone)
            )
        
        # Adiciona mensagem
        message = {
            "content": content,
            "data": message_data
        }
        
        try:
            # Tenta adicionar sem bloquear
            self.queues[phone].put_nowait(message)
            emoji_logger.system_debug(f"Mensagem adicionada ao buffer para {phone}")
        except asyncio.QueueFull:
            # Se cheio, força processamento
            emoji_logger.system_info("Buffer cheio, forçando processamento")
            # Adiciona None para sinalizar processamento
            await self.queues[phone].put(None)
            # Espera esvaziar e adiciona
            await self.queues[phone].put(message)
    
    async def _process_queue(self, phone: str) -> None:
        """
        Processa queue - INTELIGENTE: imediato se livre, com timeout se ocupado
        
        Args:
            phone: Número do telefone
        """
        # Cria lock para este usuário se não existe
        if phone not in self.processing_locks:
            self.processing_locks[phone] = asyncio.Lock()
        
        lock = self.processing_locks[phone]
        queue = self.queues[phone]
        
        try:
            # CORREÇÃO: Usar try_acquire para evitar race condition
            acquired_immediately = False
            try:
                # Tenta adquirir lock sem bloquear
                acquired_immediately = lock.locked() == False
                
                if acquired_immediately:
                    # Agente LIVRE → processa IMEDIATAMENTE
                    emoji_logger.system_debug(f"Agente livre para {phone}, processando imediatamente!")
                    first_message = await queue.get()
                    messages = [first_message]
                    
                    # Coleta mensagens rápidas que chegaram juntas (sem timeout)
                    try:
                        while True:
                            messages.append(queue.get_nowait())
                    except asyncio.QueueEmpty:
                        pass
                else:
                    # Agente OCUPADO → aguarda timeout para agrupar mensagens
                    emoji_logger.system_debug(f"Agente ocupado para {phone}, aguardando timeout...")
                    messages = await self._collect_with_timeout(queue)
                
                # Processa com lock garantido (sem race condition)
                if messages:
                    async with lock:
                        await self._process_messages(phone, messages)
                        
            except Exception as e:
                logger.error(f"Erro no processamento de queue: {e}")
                
        except Exception as e:
            logger.error(f"Erro ao processar queue: {e}")
        finally:
            # Limpa recursos
            self.queues.pop(phone, None)
            self.tasks.pop(phone, None)
            self.processing_locks.pop(phone, None)
    
    async def _collect_with_timeout(self, queue: asyncio.Queue) -> List[Dict]:
        """Coleta mensagens com timeout (modo agente ocupado)"""
        messages = []
        
        try:
            while True:
                message = await asyncio.wait_for(queue.get(), timeout=self.timeout)
                if message is None:  # Sinal para processar
                    break
                messages.append(message)
        except asyncio.TimeoutError:
            pass  # Timeout normal, processa o que coletou
        
        return messages
    
    async def _process_messages(self, phone: str, messages: List[Dict]) -> None:
        """
        Processa mensagens acumuladas
        
        Args:
            phone: Número do telefone
            messages: Lista de mensagens
        """
        from app.api.webhooks import process_message_with_agent
        
        # Combina conteúdo das mensagens
        combined_content = "\n".join([msg["content"] for msg in messages])
        
        emoji_logger.system_info(
            f"Processando {len(messages)} mensagens combinadas",
            phone=phone,
            total_chars=len(combined_content)
        )
        
        # Usa dados da última mensagem (mais recente)
        last_message = messages[-1]["data"]
        message_id = last_message.get("key", {}).get("id", "")
        
        # Processa com o agente
        await process_message_with_agent(
            phone=phone,
            message_content=combined_content,
            original_message=last_message,
            message_id=message_id
        )
    
    async def shutdown(self) -> None:
        """Cancela todas as tasks ativas"""
        for task in self.tasks.values():
            task.cancel()
        
        # Espera tasks terminarem
        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
        
        self.queues.clear()
        self.tasks.clear()

# Instância global
message_buffer: Optional[MessageBuffer] = None

def get_message_buffer() -> MessageBuffer:
    """Retorna instância global do buffer"""
    global message_buffer
    if not message_buffer:
        message_buffer = MessageBuffer()
    return message_buffer

def set_message_buffer(buffer: MessageBuffer) -> None:
    """Define instância global do buffer"""
    global message_buffer
    message_buffer = buffer