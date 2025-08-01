"""
Auto Chunking System - Sistema de chunking automático para mensagens grandes
Funciona independentemente do LLM, aplicando chunking quando necessário
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from agente.core.logger import logger, setup_module_logger
from agente.tools.whatsapp.message_chunking import chunk_message
from agente.services import get_evolution_service

# Logger específico para o módulo
module_logger = setup_module_logger("auto_chunking")


class AutoChunkingManager:
    """
    Gerenciador de chunking automático para mensagens grandes
    
    Funcionalidades:
    - Detecção automática de mensagens que precisam de chunking
    - Envio automático de chunks com delays naturais
    - Configurações personalizáveis de limites
    - Integração transparente com Evolution API
    """
    
    def __init__(self):
        """Inicializa o gerenciador de chunking automático"""
        # Configurações de chunking
        self.auto_chunk_threshold = 800  # Caracteres - limite para ativar chunking automático
        self.max_chars_per_chunk = 600   # Caracteres por chunk
        self.min_delay_ms = 1500         # Delay mínimo entre chunks
        self.max_delay_ms = 4000         # Delay máximo entre chunks
        
        # Estatísticas
        self.stats = {
            "messages_chunked": 0,
            "total_chunks_sent": 0,
            "total_characters_processed": 0
        }
        
        module_logger.info(
            "AutoChunkingManager initialized",
            threshold=self.auto_chunk_threshold,
            max_chars_per_chunk=self.max_chars_per_chunk
        )
    
    def should_chunk_message(self, text: str) -> bool:
        """
        Determina se uma mensagem deve ser dividida em chunks
        
        Args:
            text: Texto da mensagem
            
        Returns:
            True se deve fazer chunking
        """
        return len(text) > self.auto_chunk_threshold
    
    async def process_and_send_chunks(
        self, 
        phone: str, 
        text: str,
        force_chunk: bool = False
    ) -> Dict[str, Any]:
        """
        Processa mensagem e envia chunks automaticamente se necessário
        
        Args:
            phone: Número de telefone do destinatário
            text: Texto da mensagem
            force_chunk: Força chunking mesmo se abaixo do threshold
            
        Returns:
            Resultado do processamento e envio
        """
        try:
            # Verificar se precisa de chunking
            if not force_chunk and not self.should_chunk_message(text):
                # Enviar mensagem normal sem chunking
                evolution_service = get_evolution_service()
                result = await evolution_service.send_text_message(phone=phone, text=text)
                
                return {
                    "success": True,
                    "chunked": False,
                    "total_chunks": 1,
                    "message_length": len(text),
                    "evolution_result": result
                }
            
            module_logger.info(
                "Auto-chunking message",
                phone=phone[:4] + "****",
                text_length=len(text),
                threshold=self.auto_chunk_threshold
            )
            
            # Dividir mensagem em chunks
            chunk_result = await chunk_message(
                text=text,
                max_chars=self.max_chars_per_chunk,
                prefer_sentences=True,
                min_delay_ms=self.min_delay_ms,
                max_delay_ms=self.max_delay_ms
            )
            
            if not chunk_result.get("success"):
                # Falha no chunking - enviar mensagem original
                module_logger.warning("Chunking failed, sending original message")
                evolution_service = get_evolution_service()
                result = await evolution_service.send_text_message(phone=phone, text=text)
                
                return {
                    "success": True,
                    "chunked": False,
                    "chunking_failed": True,
                    "total_chunks": 1,
                    "evolution_result": result
                }
            
            chunks = chunk_result.get("chunks", [])
            total_chunks = chunk_result.get("total_chunks", 0)
            
            if total_chunks == 0:
                # Nenhum chunk criado - enviar original
                evolution_service = get_evolution_service()
                result = await evolution_service.send_text_message(phone=phone, text=text)
                
                return {
                    "success": True,
                    "chunked": False,
                    "no_chunks_created": True,
                    "total_chunks": 1,
                    "evolution_result": result
                }
            
            # Enviar chunks sequencialmente com delays
            evolution_service = get_evolution_service()
            sent_chunks = []
            
            for i, chunk in enumerate(chunks):
                chunk_text = chunk.get("text", "")
                chunk_delay = chunk.get("delay_ms", self.min_delay_ms)
                
                if not chunk_text.strip():
                    continue
                
                module_logger.debug(
                    f"Sending chunk {i+1}/{total_chunks}",
                    phone=phone[:4] + "****",
                    chunk_length=len(chunk_text),
                    delay_ms=chunk_delay
                )
                
                # Enviar chunk
                send_result = await evolution_service.send_text_message(
                    phone=phone,
                    text=chunk_text
                )
                
                sent_chunks.append({
                    "chunk_index": i + 1,
                    "text": chunk_text,
                    "length": len(chunk_text),
                    "delay_ms": chunk_delay,
                    "send_result": send_result,
                    "success": bool(send_result)
                })
                
                # Aplicar delay antes do próximo chunk (exceto no último)
                if i < len(chunks) - 1:
                    delay_seconds = chunk_delay / 1000.0
                    module_logger.debug(f"Waiting {delay_seconds:.1f}s before next chunk")
                    await asyncio.sleep(delay_seconds)
            
            # Atualizar estatísticas
            self.stats["messages_chunked"] += 1
            self.stats["total_chunks_sent"] += len(sent_chunks)
            self.stats["total_characters_processed"] += len(text)
            
            # Calcular sucessos
            successful_chunks = sum(1 for chunk in sent_chunks if chunk["success"])
            
            module_logger.info(
                "Auto-chunking completed",
                phone=phone[:4] + "****",
                total_chunks=len(sent_chunks),
                successful_chunks=successful_chunks,
                total_length=len(text)
            )
            
            return {
                "success": successful_chunks > 0,
                "chunked": True,
                "total_chunks": len(sent_chunks),
                "successful_chunks": successful_chunks,
                "failed_chunks": len(sent_chunks) - successful_chunks,
                "original_length": len(text),
                "chunks_sent": sent_chunks,
                "chunk_result": chunk_result,
                "stats": self.stats.copy()
            }
            
        except Exception as e:
            module_logger.error(
                f"Error in auto-chunking: {str(e)}",
                phone=phone[:4] + "****",
                text_length=len(text)
            )
            
            # Fallback: tentar enviar mensagem original
            try:
                evolution_service = get_evolution_service()
                fallback_result = await evolution_service.send_text_message(phone=phone, text=text)
                
                return {
                    "success": bool(fallback_result),
                    "chunked": False,
                    "error": str(e),
                    "fallback_sent": True,
                    "evolution_result": fallback_result
                }
                
            except Exception as fallback_error:
                return {
                    "success": False,
                    "chunked": False,
                    "error": str(e),
                    "fallback_error": str(fallback_error)
                }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de uso do auto-chunking
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            **self.stats,
            "auto_chunk_threshold": self.auto_chunk_threshold,
            "max_chars_per_chunk": self.max_chars_per_chunk,
            "average_chunks_per_message": (
                self.stats["total_chunks_sent"] / max(1, self.stats["messages_chunked"])
            ),
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_auto_chunking_manager: Optional[AutoChunkingManager] = None


def get_auto_chunking_manager() -> AutoChunkingManager:
    """
    Retorna instância singleton do Auto Chunking Manager
    
    Returns:
        Instância do gerenciador
    """
    global _auto_chunking_manager
    if _auto_chunking_manager is None:
        _auto_chunking_manager = AutoChunkingManager()
    return _auto_chunking_manager