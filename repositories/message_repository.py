"""
Message Repository
==================
Repositório para operações com mensagens
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from loguru import logger

from models.message import Message, MessageCreate
from repositories.base import BaseRepository
from services.database import db


class MessageRepository(BaseRepository[Message]):
    """Repositório de Mensagens"""
    
    def __init__(self):
        super().__init__(Message, "messages")
    
    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 100
    ) -> List[Message]:
        """Lista mensagens de uma conversa"""
        try:
            result = db.messages.select("*")\
                .eq("conversation_id", str(conversation_id))\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    async def get_last_messages(
        self,
        conversation_id: UUID,
        count: int = 10
    ) -> List[Message]:
        """Obtém últimas N mensagens"""
        try:
            result = db.messages.select("*")\
                .eq("conversation_id", str(conversation_id))\
                .order("created_at", desc=True)\
                .limit(count)\
                .execute()
            
            # Reverter ordem para cronológica
            messages = [Message(**item) for item in result.data]
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error getting last messages: {e}")
            return []
    
    async def save_user_message(
        self,
        conversation_id: UUID,
        content: str,
        whatsapp_message_id: Optional[str] = None,
        media_type: Optional[str] = None,
        media_url: Optional[str] = None,
        media_data: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Salva mensagem do usuário"""
        message_data = MessageCreate(
            conversation_id=conversation_id,
            whatsapp_message_id=whatsapp_message_id,
            role="user",
            content=content,
            media_type=media_type,
            media_url=media_url,
            media_data=media_data
        )
        
        # Converter UUIDs para string antes de salvar
        data = message_data.dict()
        if 'conversation_id' in data and data['conversation_id']:
            data['conversation_id'] = str(data['conversation_id'])
        return await self.create(data)
    
    async def save_assistant_message(
        self,
        conversation_id: UUID,
        content: str
    ) -> Message:
        """Salva mensagem do assistente"""
        message_data = MessageCreate(
            conversation_id=conversation_id,
            role="assistant",
            content=content
        )
        
        # Converter UUIDs para string antes de salvar
        data = message_data.dict()
        if 'conversation_id' in data and data['conversation_id']:
            data['conversation_id'] = str(data['conversation_id'])
        return await self.create(data)
    
    async def get_messages_with_media(
        self,
        conversation_id: UUID
    ) -> List[Message]:
        """Lista mensagens com mídia"""
        try:
            result = db.messages.select("*")\
                .eq("conversation_id", str(conversation_id))\
                .not_.is_("media_type", None)\
                .order("created_at", desc=False)\
                .execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting messages with media: {e}")
            return []
    
    async def search_messages(
        self,
        query: str,
        conversation_id: Optional[UUID] = None
    ) -> List[Message]:
        """Busca mensagens por conteúdo"""
        try:
            search_query = db.messages.select("*")\
                .ilike("content", f"%{query}%")
            
            if conversation_id:
                search_query = search_query.eq("conversation_id", str(conversation_id))
            
            result = search_query.limit(50).execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []
    
    async def get_recent_messages(
        self,
        hours: int = 24
    ) -> List[Message]:
        """Lista mensagens recentes"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            result = db.messages.select("*")\
                .gte("created_at", cutoff_time.isoformat())\
                .order("created_at", desc=True)\
                .execute()
            
            return [Message(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    async def count_conversation_messages(
        self,
        conversation_id: UUID,
        role: Optional[str] = None
    ) -> int:
        """Conta mensagens de uma conversa"""
        filters = {"conversation_id": str(conversation_id)}
        
        if role:
            filters["role"] = role
        
        return await self.count(filters)
    
    async def get_conversation_context(
        self,
        conversation_id: UUID,
        max_messages: int = 20
    ) -> str:
        """Obtém contexto da conversa formatado"""
        messages = await self.get_last_messages(conversation_id, max_messages)
        
        context_parts = []
        for msg in messages:
            role_label = "Cliente" if msg.role == "user" else "Luna"
            context_parts.append(f"{role_label}: {msg.content}")
        
        return "\n".join(context_parts)
    
    async def get_full_conversation_context(
        self,
        conversation_id: UUID,
        limit: int = 100,
        include_media: bool = True
    ) -> Dict[str, Any]:
        """Busca contexto completo incluindo análise"""
        # Buscar mensagens
        messages = await self.get_conversation_messages(conversation_id, limit=limit)
        
        # Se incluir mídia, buscar mensagens com mídia
        media_messages = []
        if include_media:
            media_messages = await self.get_messages_with_media(conversation_id)
        
        # Analisar padrões
        patterns = await self._analyze_conversation_patterns(messages)
        
        # Extrair insights do usuário
        insights = await self._extract_user_insights(messages)
        
        # Gerar resumo
        summary = await self._generate_conversation_summary(messages)
        
        return {
            "messages": messages,
            "media_messages": media_messages,
            "patterns": patterns,
            "insights": insights,
            "summary": summary,
            "total_messages": len(messages),
            "conversation_duration": self._calculate_conversation_duration(messages)
        }
    
    async def _analyze_conversation_patterns(self, messages: List[Message]) -> Dict[str, Any]:
        """Analisa padrões na conversa"""
        if not messages:
            return {}
        
        patterns = {
            "avg_response_time": None,
            "message_frequency": {},
            "topics_discussed": [],
            "user_engagement": "low",
            "conversation_stage": "initial"
        }
        
        # Analisar tempo de resposta
        response_times = []
        for i in range(1, len(messages)):
            if messages[i].role != messages[i-1].role:
                time_diff = (messages[i].created_at - messages[i-1].created_at).total_seconds()
                if time_diff < 3600:  # Ignorar gaps maiores que 1 hora
                    response_times.append(time_diff)
        
        if response_times:
            patterns["avg_response_time"] = sum(response_times) / len(response_times)
        
        # Analisar frequência de mensagens
        user_messages = [m for m in messages if m.role == "user"]
        patterns["user_message_count"] = len(user_messages)
        
        # Determinar engajamento
        if len(user_messages) > 10:
            patterns["user_engagement"] = "high"
        elif len(user_messages) > 5:
            patterns["user_engagement"] = "medium"
        
        # Detectar tópicos discutidos
        topics_keywords = {
            "preço": ["preço", "valor", "custo", "investimento", "caro", "barato"],
            "economia": ["economia", "economizar", "redução", "desconto", "poupar"],
            "técnico": ["instalação", "telhado", "painéis", "inversor", "kwh", "potência"],
            "dúvidas": ["dúvida", "pergunta", "como", "quanto", "quando", "onde"],
            "interesse": ["quero", "interesse", "gostaria", "preciso", "simular"]
        }
        
        all_content = " ".join([m.content.lower() for m in messages if m.content])
        
        for topic, keywords in topics_keywords.items():
            if any(keyword in all_content for keyword in keywords):
                patterns["topics_discussed"].append(topic)
        
        return patterns
    
    async def _extract_user_insights(self, messages: List[Message]) -> Dict[str, Any]:
        """Extrai insights sobre o usuário"""
        insights = {
            "objections": [],
            "interests": [],
            "questions_asked": [],
            "pain_points": [],
            "decision_factors": [],
            "sentiment_trend": []
        }
        
        # Palavras-chave para detecção
        objection_keywords = ["caro", "não tenho", "não posso", "difícil", "problema", "preocupado"]
        interest_keywords = ["interessante", "legal", "quero saber", "me conta", "como funciona"]
        
        user_messages = [m for m in messages if m.role == "user" and m.content]
        
        for msg in user_messages:
            content_lower = msg.content.lower()
            
            # Detectar objeções
            for keyword in objection_keywords:
                if keyword in content_lower:
                    insights["objections"].append({
                        "keyword": keyword,
                        "message": msg.content[:100],
                        "timestamp": msg.created_at.isoformat()
                    })
                    break
            
            # Detectar interesses
            for keyword in interest_keywords:
                if keyword in content_lower:
                    insights["interests"].append({
                        "keyword": keyword,
                        "message": msg.content[:100],
                        "timestamp": msg.created_at.isoformat()
                    })
                    break
            
            # Detectar perguntas
            if "?" in content_lower:
                insights["questions_asked"].append(msg.content[:100])
        
        return insights
    
    async def _generate_conversation_summary(self, messages: List[Message]) -> str:
        """Gera resumo da conversa"""
        if not messages:
            return "Conversa sem mensagens"
        
        # Pegar primeira e última mensagem
        first_msg = messages[0]
        last_msg = messages[-1]
        
        # Contar mensagens por role
        user_count = len([m for m in messages if m.role == "user"])
        assistant_count = len([m for m in messages if m.role == "assistant"])
        
        summary = f"Conversa iniciada em {first_msg.created_at.strftime('%d/%m/%Y %H:%M')} "
        summary += f"com {len(messages)} mensagens ({user_count} do cliente, {assistant_count} da Luna). "
        
        # Adicionar último status
        if last_msg.role == "user":
            summary += "Aguardando resposta da Luna."
        else:
            summary += "Aguardando resposta do cliente."
        
        return summary
    
    def _calculate_conversation_duration(self, messages: List[Message]) -> float:
        """Calcula duração da conversa em minutos"""
        if len(messages) < 2:
            return 0
        
        first_msg = messages[0]
        last_msg = messages[-1]
        
        duration = (last_msg.created_at - first_msg.created_at).total_seconds() / 60
        return round(duration, 2)
    
    async def delete_conversation_messages(self, conversation_id: UUID) -> bool:
        """Deleta todas as mensagens de uma conversa"""
        try:
            response = await self.client.table("messages")\
                .delete()\
                .eq("conversation_id", str(conversation_id))\
                .execute()
            
            logger.info(f"Deletadas mensagens da conversa {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar mensagens: {e}")
            return False


# Instância global
message_repository = MessageRepository()