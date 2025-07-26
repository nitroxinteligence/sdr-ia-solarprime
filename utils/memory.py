"""
Sistema de Memória de Conversação [DEPRECATED]
===============================================
NOTA: Este módulo está deprecado. O AGnO Framework agora gerencia
a memória nativamente através de AgentMemory e AgentSession.

Este arquivo é mantido apenas para compatibilidade com código legado.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

class ConversationMemory:
    """Gerencia memória e contexto das conversas"""
    
    def __init__(self, max_context_size: int = 10):
        """
        Inicializa o sistema de memória
        
        Args:
            max_context_size: Número máximo de mensagens no contexto
        """
        self.max_context_size = max_context_size
        self.conversations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.lead_profiles: Dict[str, Dict[str, Any]] = {}
        self.conversation_summaries: Dict[str, str] = {}
        
        logger.info("Sistema de memória inicializado")
    
    async def add_message(
        self, 
        phone_number: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Adiciona uma mensagem ao histórico
        
        Args:
            phone_number: Número do telefone
            role: 'user' ou 'assistant'
            content: Conteúdo da mensagem
            metadata: Metadados adicionais
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[phone_number].append(message)
        
        # Verifica se precisa resumir
        if len(self.conversations[phone_number]) > 20:
            await self._create_summary(phone_number)
        
        logger.debug(f"Mensagem adicionada para {phone_number}")
    
    async def get_context(
        self, 
        phone_number: str,
        include_summary: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtém o contexto da conversa
        
        Args:
            phone_number: Número do telefone
            include_summary: Se deve incluir resumo anterior
            
        Returns:
            Lista de mensagens do contexto
        """
        conversation = self.conversations.get(phone_number, [])
        
        # Se não há conversa, retorna vazio
        if not conversation:
            return []
        
        # Pega as últimas N mensagens
        recent_messages = conversation[-self.max_context_size:]
        
        # Se tem resumo e deve incluir
        if include_summary and phone_number in self.conversation_summaries:
            summary_message = {
                "role": "system",
                "content": f"Resumo da conversa anterior: {self.conversation_summaries[phone_number]}",
                "timestamp": recent_messages[0]["timestamp"] if recent_messages else datetime.now().isoformat()
            }
            return [summary_message] + recent_messages
        
        return recent_messages
    
    async def get_lead_profile(self, phone_number: str) -> Dict[str, Any]:
        """
        Obtém o perfil do lead
        
        Args:
            phone_number: Número do telefone
            
        Returns:
            Dicionário com informações do lead
        """
        if phone_number not in self.lead_profiles:
            self.lead_profiles[phone_number] = {
                "phone": phone_number,
                "created_at": datetime.now().isoformat(),
                "interactions": 0,
                "stage": "INITIAL_CONTACT",
                "info": {}
            }
        
        # Atualiza contador de interações
        self.lead_profiles[phone_number]["interactions"] += 1
        self.lead_profiles[phone_number]["last_interaction"] = datetime.now().isoformat()
        
        return self.lead_profiles[phone_number]
    
    async def update_lead_profile(
        self, 
        phone_number: str, 
        updates: Dict[str, Any]
    ) -> None:
        """
        Atualiza o perfil do lead
        
        Args:
            phone_number: Número do telefone
            updates: Dicionário com atualizações
        """
        profile = await self.get_lead_profile(phone_number)
        
        # Atualiza informações
        if "info" in updates:
            profile["info"].update(updates["info"])
            del updates["info"]
        
        profile.update(updates)
        profile["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Perfil atualizado para {phone_number}")
    
    async def _create_summary(self, phone_number: str) -> None:
        """
        Cria um resumo da conversa
        
        Args:
            phone_number: Número do telefone
        """
        try:
            conversation = self.conversations[phone_number]
            
            # Pega mensagens antigas (que serão resumidas)
            old_messages = conversation[:-self.max_context_size]
            
            # Cria resumo simples
            summary_parts = []
            lead_info = {}
            
            for msg in old_messages:
                if msg["role"] == "user":
                    # Extrai informações chave
                    content_lower = msg["content"].lower()
                    
                    # Nome
                    if "meu nome é" in content_lower or "me chamo" in content_lower:
                        parts = msg["content"].split()
                        for i, part in enumerate(parts):
                            if part.lower() in ["é", "chamo"] and i + 1 < len(parts):
                                lead_info["name"] = parts[i + 1].strip(".,!?")
                    
                    # Valor da conta
                    if "r$" in content_lower:
                        import re
                        values = re.findall(r'R\$\s*(\d+(?:\.\d{3})*(?:,\d{2})?)', msg["content"])
                        if values:
                            lead_info["bill_value"] = f"R$ {values[0]}"
                    
                    # Tipo de imóvel
                    if "casa" in content_lower:
                        lead_info["property_type"] = "casa"
                    elif "apartamento" in content_lower or "apto" in content_lower:
                        lead_info["property_type"] = "apartamento"
            
            # Monta resumo
            summary = f"Lead identificado"
            if lead_info:
                info_parts = []
                if "name" in lead_info:
                    info_parts.append(f"Nome: {lead_info['name']}")
                if "property_type" in lead_info:
                    info_parts.append(f"Imóvel: {lead_info['property_type']}")
                if "bill_value" in lead_info:
                    info_parts.append(f"Conta: {lead_info['bill_value']}")
                
                if info_parts:
                    summary += f" - {', '.join(info_parts)}"
            
            summary += f". Total de {len(old_messages)} mensagens anteriores."
            
            self.conversation_summaries[phone_number] = summary
            
            # Remove mensagens antigas
            self.conversations[phone_number] = conversation[-self.max_context_size:]
            
            logger.info(f"Resumo criado para {phone_number}: {summary}")
            
        except Exception as e:
            logger.error(f"Erro ao criar resumo: {e}")
    
    def get_active_conversations(
        self, 
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Obtém conversas ativas nas últimas N horas
        
        Args:
            hours: Número de horas para considerar ativa
            
        Returns:
            Lista de conversas ativas
        """
        active = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for phone, messages in self.conversations.items():
            if messages:
                last_msg = messages[-1]
                last_time = datetime.fromisoformat(last_msg["timestamp"])
                
                if last_time > cutoff:
                    active.append({
                        "phone": phone,
                        "last_message": last_msg["content"][:50] + "...",
                        "last_interaction": last_msg["timestamp"],
                        "message_count": len(messages)
                    })
        
        return sorted(active, key=lambda x: x["last_interaction"], reverse=True)
    
    def clear_old_conversations(self, days: int = 30) -> int:
        """
        Limpa conversas antigas
        
        Args:
            days: Número de dias para manter
            
        Returns:
            Número de conversas removidas
        """
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0
        
        phones_to_remove = []
        for phone, messages in self.conversations.items():
            if messages:
                last_time = datetime.fromisoformat(messages[-1]["timestamp"])
                if last_time < cutoff:
                    phones_to_remove.append(phone)
        
        for phone in phones_to_remove:
            del self.conversations[phone]
            if phone in self.lead_profiles:
                del self.lead_profiles[phone]
            if phone in self.conversation_summaries:
                del self.conversation_summaries[phone]
            removed += 1
        
        logger.info(f"Removidas {removed} conversas antigas")
        return removed
    
    def export_conversation(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Exporta uma conversa completa
        
        Args:
            phone_number: Número do telefone
            
        Returns:
            Dicionário com todos os dados da conversa
        """
        if phone_number not in self.conversations:
            return None
        
        return {
            "phone": phone_number,
            "messages": self.conversations[phone_number],
            "profile": self.lead_profiles.get(phone_number, {}),
            "summary": self.conversation_summaries.get(phone_number, ""),
            "exported_at": datetime.now().isoformat()
        }
    
    def import_conversation(self, data: Dict[str, Any]) -> bool:
        """
        Importa uma conversa exportada
        
        Args:
            data: Dados da conversa exportada
            
        Returns:
            True se importado com sucesso
        """
        try:
            phone = data.get("phone")
            if not phone:
                return False
            
            self.conversations[phone] = data.get("messages", [])
            self.lead_profiles[phone] = data.get("profile", {})
            
            if "summary" in data:
                self.conversation_summaries[phone] = data["summary"]
            
            logger.info(f"Conversa importada para {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao importar conversa: {e}")
            return False

# Instância global de memória (para desenvolvimento)
# Em produção, usar Redis ou banco de dados
_memory_instance = None

def get_memory() -> ConversationMemory:
    """Obtém instância global de memória"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance

# Exporta componentes
__all__ = ["ConversationMemory", "get_memory"]