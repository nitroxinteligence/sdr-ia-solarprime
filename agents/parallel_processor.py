"""
Parallel Processor
==================
Processamento paralelo otimizado para performance <30s
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from loguru import logger

from agents.sdr_agent_v2 import SDRAgentV2
from services.cache_service import cache_service, get_cached_lead_data, cache_lead_data
from repositories.lead_repository import lead_repository
from repositories.conversation_repository import conversation_repository
from repositories.message_repository import message_repository
from agents.knowledge.solarprime_knowledge import SolarPrimeKnowledge
from config.config import config


class ParallelProcessor:
    """Processador paralelo para otimização de performance"""
    
    def __init__(self):
        self.sdr_agent = None
        self.knowledge = None
        self._initialized = False
        
    async def initialize(self):
        """Inicializa recursos uma única vez"""
        if not self._initialized:
            # Criar agente e knowledge base
            self.sdr_agent = SDRAgentV2(config)
            self.knowledge = SolarPrimeKnowledge()
            
            # Inicializar em paralelo
            await asyncio.gather(
                self.sdr_agent.initialize(),
                self.knowledge.load_from_supabase()
            )
            
            self._initialized = True
            logger.info("ParallelProcessor inicializado")
            
    async def process_message_optimized(
        self,
        message_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Processa mensagem com máxima performance usando paralelismo
        
        Args:
            message_data: Dados da mensagem incluindo phone, content, type, etc.
            
        Returns:
            Tuple com resposta e metadata
        """
        start_time = datetime.now()
        
        # Garantir inicialização
        if not self._initialized:
            await self.initialize()
            
        phone = message_data['phone']
        
        try:
            # Executar carregamento de contexto em paralelo
            context_tasks = [
                self._load_lead_data_cached(phone),
                self._load_conversation_history_cached(phone),
                self._prepare_knowledge_context(message_data['content'])
            ]
            
            # Adicionar pré-processamento de mídia se houver
            if message_data.get('media_type') and message_data.get('media_data'):
                context_tasks.append(
                    self._preprocess_media(
                        message_data['media_type'],
                        message_data['media_data']
                    )
                )
                
            # Executar todas as tarefas em paralelo
            results = await asyncio.gather(*context_tasks, return_exceptions=True)
            
            # Processar resultados
            lead_data = results[0] if not isinstance(results[0], Exception) else {}
            conversation_history = results[1] if not isinstance(results[1], Exception) else []
            knowledge_context = results[2] if not isinstance(results[2], Exception) else ""
            media_processed = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else None
            
            # Log de erros se houver
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Erro na tarefa paralela {i}: {result}")
                    
            # Criar contexto completo
            full_context = {
                'lead_data': lead_data,
                'conversation_history': conversation_history,
                'knowledge_context': knowledge_context,
                'media_processed': media_processed
            }
            
            # Processar com timeout agressivo
            response, metadata = await asyncio.wait_for(
                self.sdr_agent.process_message(
                    message=message_data['content'],
                    phone_number=phone,
                    media_type=message_data.get('media_type'),
                    media_data=media_processed,
                    message_id=message_data.get('message_id')
                ),
                timeout=20.0  # 20s timeout máximo
            )
            
            # Calcular tempo total
            total_time = (datetime.now() - start_time).total_seconds()
            metadata['total_processing_time'] = total_time
            
            # Atualizar cache com novos dados
            if 'lead_info' in metadata:
                await cache_lead_data(phone, metadata['lead_info'])
                
            # Log de performance
            if total_time < 15:
                logger.info(f"✅ Resposta rápida em {total_time:.2f}s")
            elif total_time < 25:
                logger.warning(f"⚠️ Resposta em {total_time:.2f}s")
            else:
                logger.error(f"❌ Resposta lenta: {total_time:.2f}s")
                
            return response, metadata
            
        except asyncio.TimeoutError:
            logger.error("Timeout no processamento (>20s)")
            return "Desculpe a demora! Vamos continuar? 😊", {
                'error': 'timeout',
                'total_processing_time': 20.0
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento paralelo: {e}", exc_info=True)
            return "Ops, tive um probleminha. Pode repetir? 🙏", {
                'error': str(e),
                'total_processing_time': (datetime.now() - start_time).total_seconds()
            }
            
    async def _load_lead_data_cached(self, phone: str) -> Dict[str, Any]:
        """Carrega dados do lead com cache agressivo"""
        # Tentar cache primeiro
        cached = await get_cached_lead_data(phone)
        if cached:
            logger.debug(f"Lead data from cache: {phone}")
            return cached
            
        # Carregar do banco
        profile = await lead_repository.get_or_create_profile(phone)
        lead = await lead_repository.get_lead_by_phone(phone)
        
        data = {
            'phone': phone,
            'profile_id': str(profile.id),
            'created_at': profile.created_at.isoformat()
        }
        
        if lead:
            data.update({
                'lead_id': str(lead.id),
                'name': lead.name,
                'email': lead.email,
                'property_type': lead.property_type,
                'bill_value': lead.bill_value,
                'consumption_kwh': lead.consumption_kwh,
                'current_stage': lead.current_stage,
                'qualification_score': lead.qualification_score
            })
            
        # Cachear para próximas requisições
        await cache_lead_data(phone, data)
        
        return data
        
    async def _load_conversation_history_cached(self, phone: str) -> List[Dict[str, Any]]:
        """Carrega histórico com cache"""
        conversation = await conversation_repository.get_or_create_conversation(phone)
        cache_key = f"conversation:{conversation.id}:messages"
        
        # Tentar cache
        cached = await cache_service.get_or_compute(
            key=cache_key,
            compute_fn=lambda: message_repository.get_conversation_messages(
                conversation_id=conversation.id,
                limit=10  # Apenas últimas 10 mensagens
            ),
            ttl=600  # 10 minutos
        )
        
        if asyncio.iscoroutine(cached):
            messages = await cached
        else:
            messages = cached
            
        return [
            {
                'role': msg.sender_type,
                'content': msg.content,
                'timestamp': msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
    async def _prepare_knowledge_context(self, message: str) -> str:
        """Prepara contexto de conhecimento com cache"""
        cache_key = f"knowledge:query:{message[:50]}"  # Primeiros 50 chars
        
        return await cache_service.get_or_compute(
            key=cache_key,
            compute_fn=lambda: self.knowledge.get_relevant_knowledge(message, max_results=2),
            ttl=1800  # 30 minutos
        )
        
    async def _preprocess_media(self, media_type: str, media_data: Any) -> Any:
        """Pré-processa mídia para o agente"""
        # Por ora, apenas retorna os dados
        # Futuramente pode fazer resize de imagens, etc.
        return media_data
        
    async def warmup_cache(self, phone_numbers: List[str]):
        """Aquece o cache para uma lista de números"""
        logger.info(f"Aquecendo cache para {len(phone_numbers)} números")
        
        tasks = []
        for phone in phone_numbers:
            tasks.extend([
                self._load_lead_data_cached(phone),
                self._load_conversation_history_cached(phone)
            ])
            
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Cache aquecido")
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        cache_stats = cache_service.get_stats()
        
        return {
            'cache_stats': cache_stats,
            'initialized': self._initialized
        }


# Instância global
parallel_processor = ParallelProcessor()