"""
Auto Chunking System - Sistema de chunking automático para mensagens grandes
Funciona independentemente do LLM, aplicando chunking quando necessário
VERSÃO INTELIGENTE: Detecta se mensagem já foi humanizada pelo AGnO e faz bypass
"""

import asyncio
import re
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
        
        # Padrões para detectar mensagens já humanizadas pelo AGnO/Helen (pós-sanitização)
        self.humanization_patterns = [
            # Padrões de apresentação Helen Vieira (melhorados)
            r'Oi!?\s+Muito\s+prazer,?\s+me\s+chamo\s+Helen\s+Vieira',  # Apresentação completa
            r'Meu\s+nome\s+é\s+Helen\s+Vieira',                        # Apresentação alternativa
            r'Sou\s+consultora\s+(da\s+)?Solar\s+Prime',               # Identificação profissional
            r'Sou\s+consultora\s+especialista',                        # Descrição profissional
            
            # Padrões de quebra natural (indicam chunking já aplicado)
            r'\n\s*\n',                                                 # Quebras duplas (natural chunking)
            r'(Oi!?\s+[^.!?]*[.!?])\s*\n+\s*(Sou\s+[^.!?]*[.!?])',   # Padrão: saudação → quebra → profissão
            
            # Padrões de perguntas típicas Helen
            r'Qual\s+(o\s+)?seu\s+nome\?',                             # Pergunta nome
            r'Como\s+posso\s+te\s+chamar\?',                           # Pergunta tratamento
            r'Antes\s+de\s+começarmos,?\s+',                           # Início de qualificação
            
            # Marcadores de pausa do humanizer (se ainda presentes)
            r'\[pausa\s+\d+\.?\d*s\]',                                # Marcadores explícitos
            
            # Padrões de estrutura Helen (indicam processamento AGnO)
            r'Helen\s+Vieira.*Solar\s+Prime',                          # Nome + empresa na mesma frase
            r'(consultora|especialista).*energia\s+solar',             # Profissão + área
        ]
        
        module_logger.info(
            "AutoChunkingManager initialized with intelligent humanization detection",
            threshold=self.auto_chunk_threshold,
            max_chars_per_chunk=self.max_chars_per_chunk,
            humanization_patterns=len(self.humanization_patterns)
        )
    
    def is_already_humanized(self, text: str) -> bool:
        """
        Detecta se mensagem já foi processada pelo HelenHumanizer/AGnO
        
        Args:
            text: Texto da mensagem para analisar
            
        Returns:
            True se mensagem já foi humanizada (deve fazer bypass)
        """
        if not text:
            return False
        
        # Verificar padrões de humanização Helen Vieira
        matches_found = []
        for pattern in self.humanization_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                matches_found.append(pattern)
        
        is_humanized = len(matches_found) >= 2  # Pelo menos 2 padrões = humanizada
        
        if is_humanized:
            module_logger.info(
                "Mensagem já humanizada detectada - BYPASS auto-chunking",
                patterns_matched=len(matches_found),
                text_length=len(text)
            )
        
        return is_humanized
    
    def should_chunk_message(self, text: str) -> bool:
        """
        Determina se uma mensagem deve ser dividida em chunks
        
        Args:
            text: Texto da mensagem
            
        Returns:
            True se deve fazer chunking
        """
        return len(text) > self.auto_chunk_threshold
    
    def extract_humanized_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrai chunks de uma mensagem já humanizada pelo AGnO
        
        Args:
            text: Texto humanizado para extrair chunks
            
        Returns:
            Lista de chunks extraídos com delay
        """
        try:
            # Detectar separadores naturais de humanização
            # Padrão: quebras duplas de linha indicam separação natural
            raw_chunks = re.split(r'\n\s*\n+', text.strip())
            
            chunks = []
            for i, chunk_text in enumerate(raw_chunks):
                chunk_text = chunk_text.strip()
                if not chunk_text:
                    continue
                
                # Extrair delay se houver marcadores [pausa Xs]
                delay_ms = self.min_delay_ms  # Default
                delay_match = re.search(r'\[pausa\s+(\d+\.?\d*)s\]', chunk_text)
                if delay_match:
                    delay_seconds = float(delay_match.group(1))
                    delay_ms = int(delay_seconds * 1000)
                    # Remover marcador de pausa do texto
                    chunk_text = re.sub(r'\[pausa\s+\d+\.?\d*s\]', '', chunk_text).strip()
                
                chunks.append({
                    "text": chunk_text,
                    "delay_ms": delay_ms,
                    "chunk_index": i,
                    "words": len(chunk_text.split()),
                    "chars": len(chunk_text)
                })
            
            module_logger.info(
                "Chunks extraídos de mensagem humanizada",
                total_chunks=len(chunks),
                avg_chunk_size=sum(c["chars"] for c in chunks) / len(chunks) if chunks else 0
            )
            
            return chunks
            
        except Exception as e:
            module_logger.error(f"Erro ao extrair chunks humanizados: {e}")
            # Fallback: retornar texto como chunk único
            return [{
                "text": text,
                "delay_ms": self.min_delay_ms,
                "chunk_index": 0,
                "words": len(text.split()),
                "chars": len(text)
            }]
    
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
            # 🧠 BYPASS INTELIGENTE: Verificar se já foi humanizada pelo AGnO
            if self.is_already_humanized(text):
                module_logger.info(
                    "🎭 BYPASS: Mensagem já humanizada detectada - usando chunks pré-processados",
                    phone=phone[:4] + "****",
                    text_length=len(text)
                )
                
                # Extrair chunks da resposta já humanizada
                humanized_chunks = self.extract_humanized_chunks(text)
                
                # Enviar chunks humanizados sequencialmente
                evolution_service = get_evolution_service()
                sent_chunks = []
                
                for i, chunk in enumerate(humanized_chunks):
                    chunk_text = chunk.get("text", "")
                    chunk_delay = chunk.get("delay_ms", self.min_delay_ms)
                    
                    if not chunk_text.strip():
                        continue
                    
                    try:
                        # Delay antes do envio (exceto primeiro chunk)
                        if i > 0:
                            await asyncio.sleep(chunk_delay / 1000.0)
                        
                        result = await evolution_service.send_text_message(
                            phone=phone, 
                            text=chunk_text
                        )
                        
                        sent_chunks.append({
                            "chunk_index": i,
                            "text": chunk_text[:50] + "..." if len(chunk_text) > 50 else chunk_text,
                            "chars": len(chunk_text),
                            "delay_ms": chunk_delay,
                            "evolution_result": result
                        })
                        
                        module_logger.debug(
                            f"✅ Chunk humanizado {i+1}/{len(humanized_chunks)} enviado",
                            chars=len(chunk_text),
                            delay_ms=chunk_delay
                        )
                        
                    except Exception as chunk_error:
                        module_logger.error(
                            f"❌ Erro ao enviar chunk humanizado {i+1}: {chunk_error}"
                        )
                        sent_chunks.append({
                            "chunk_index": i,
                            "error": str(chunk_error),
                            "chars": len(chunk_text)
                        })
                
                # Atualizar estatísticas
                self.stats["messages_chunked"] += 1
                self.stats["total_chunks_sent"] += len(sent_chunks)
                self.stats["total_characters_processed"] += len(text)
                
                return {
                    "success": True,
                    "chunked": True,
                    "humanized_bypass": True,
                    "total_chunks": len(humanized_chunks),
                    "successful_chunks": len([c for c in sent_chunks if "error" not in c]),
                    "chunks_sent": sent_chunks,
                    "message_length": len(text),
                    "processing_time_ms": 0  # Bypass é instantâneo
                }
            
            # Verificar se precisa de chunking normal
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