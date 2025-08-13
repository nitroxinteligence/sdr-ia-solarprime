"""
AgenticSDR Refatorado - ZERO complexidade, MÁXIMA modularidade
Sistema modular com singleton pattern e execução direta
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from app.core.model_manager import ModelManager
from app.core.multimodal_processor import MultimodalProcessor
from app.core.lead_manager import LeadManager
from app.core.context_analyzer import ContextAnalyzer
from app.core.team_coordinator import TeamCoordinator
from app.services.conversation_monitor import get_conversation_monitor
from app.utils.logger import emoji_logger
from app.config import settings

# Singleton instance
_singleton_instance = None
_singleton_lock = None

class AgenticSDR:
    """
    SDR Agent ULTRA-SIMPLIFICADO e MODULAR
    Mantém 100% da funcionalidade com ZERO complexidade
    """
    
    def __init__(self):
        
        # Módulos
        self.model_manager = ModelManager()
        self.multimodal = MultimodalProcessor()
        self.lead_manager = LeadManager()
        self.context_analyzer = ContextAnalyzer()
        self.team_coordinator = TeamCoordinator()
        self.conversation_monitor = get_conversation_monitor()
        
        # Estado
        self.is_initialized = False
        self.conversation_history = []
        self.current_lead_info = {}
        self.current_phone = None
        
    async def initialize(self):
        """Inicialização assíncrona SIMPLES"""
        if self.is_initialized:
            return
        
        emoji_logger.system_event("🚀 Inicializando AgenticSDR Modular...")
        
        try:
            # Inicializar módulos
            self.model_manager.initialize()
            self.multimodal.initialize()
            self.lead_manager.initialize()
            self.context_analyzer.initialize()
            await self.team_coordinator.initialize()
            await self.conversation_monitor.initialize()
            
            # Configurar agent com model manager
            self.model_manager_instance = self.model_manager
            
            self.is_initialized = True
            emoji_logger.system_ready(
                "✅ AgenticSDR Modular inicializado com sucesso!",
                modules=[
                    "ModelManager", "MultimodalProcessor", 
                    "LeadManager", "ContextAnalyzer", "TeamCoordinator"
                ]
            )
            
        except Exception as e:
            emoji_logger.system_error("AgenticSDR", error=f"Erro na inicialização: {e}")
            raise
    
    def _get_instructions(self) -> str:
        """Instruções SIMPLES e DIRETAS para o agent"""
        return """
        Você é a Helen Vieira, consultora de energia solar da SolarPrime.
        
        🎯 OBJETIVO: Qualificar leads e agendar reuniões com o Leonardo (especialista).
        
        💬 PERSONALIDADE:
        - Consultora profissional e empática
        - Tom amigável e acolhedor
        - Use emojis com moderação (sol ☀️, energia ⚡, economia 💰)
        - Seja natural e humanizada
        - Demonstre entusiasmo genuíno pela economia do cliente
        
        📋 PROCESSO SIMPLES:
        1. Cumprimente calorosamente e se apresente
        2. Pergunte sobre a conta de luz e situação atual
        3. Explique benefícios personalizados da energia solar
        4. Agende reunião com Leonardo quando qualificado
        5. Registre todas informações no CRM
        
        ⚡ GATILHOS DE AÇÃO:
        - Valor da conta > R$ 300 → Qualificar e agendar
        - Perguntas técnicas → "O Leonardo vai adorar explicar isso!"
        - Objeções → Contornar com histórias de sucesso
        - Hesitação → Oferecer análise sem compromisso
        - Sem interesse → Agendar follow-up educativo
        
        💡 ABORDAGEM:
        - Foque na economia e não no produto
        - Use exemplos reais de outros clientes
        - Personalize sempre com o nome do lead
        - Mostre que entende a dor da conta alta
        
        🚫 EVITE:
        - Termos técnicos sem explicação
        - Pressão ou insistência excessiva
        - Promessas irreais de economia
        - Mensagens robóticas ou templates
        - Respostas genéricas sem personalização
        """
    
    async def process_message(self, message: str, metadata: Dict[str, Any] = None) -> str:
        """
        Processa mensagem de forma MODULAR
        
        Args:
            message: Mensagem do usuário
            metadata: Metadados (mídia, phone, etc)
            
        Returns:
            Resposta do agent
        """
        if not self.is_initialized:
            await self.initialize()
        
        emoji_logger.conversation_event(f"💬 Recebida: {message[:100]}...")
        
        # Extrair telefone dos metadados
        phone = metadata.get("phone") if metadata else None
        if phone:
            self.current_phone = phone
            # Registrar mensagem do usuário no monitor de conversas
            await self.conversation_monitor.register_message(
                phone=phone,
                is_from_user=True,
                lead_info=self.current_lead_info
            )
        
        try:
            # 1. Processar mídia se houver
            media_context = ""
            if metadata and metadata.get("media"):
                media_result = await self.multimodal.process_media(metadata["media"])
                if media_result.get("success"):
                    media_context = self._format_media_context(media_result)
                    emoji_logger.multimodal_event("📎 Mídia processada com sucesso")
            
            # 2. Atualizar histórico
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # 3. Analisar contexto
            context = self.context_analyzer.analyze_context(
                self.conversation_history,
                message
            )
            
            # 4. Extrair informações do lead e detectar mudanças
            lead_info = self.lead_manager.extract_lead_info(self.conversation_history)
            
            # 🔍 DETECÇÃO DE MUDANÇAS
            lead_changes = self._detect_lead_changes(self.current_lead_info, lead_info)
            self.current_lead_info.update(lead_info)
            
            # 🚀 SINCRONIZAÇÃO REAL-TIME COM CRM
            if lead_changes and self.current_phone:
                await self._sync_lead_changes(lead_changes)
            
            # 5. Executar serviços necessários
            service_results = await self.team_coordinator.execute_services(
                message,
                context,
                self.current_lead_info
            )
            
            # 6. Gerar resposta com contexto completo
            response = await self._generate_response(
                message,
                context,
                self.current_lead_info,
                service_results,
                media_context
            )
            
            # 7. Atualizar histórico com resposta
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # 8. Registrar resposta do bot no monitor de conversas
            if self.current_phone:
                await self.conversation_monitor.register_message(
                    phone=self.current_phone,
                    is_from_user=False,
                    lead_info=self.current_lead_info
                )
            
            emoji_logger.conversation_event(f"✅ Resposta: {response[:100]}...")
            return response
            
        except Exception as e:
            import traceback
            emoji_logger.system_error("AgenticSDR", error=f"Erro ao processar mensagem: {e}")
            emoji_logger.system_error("AgenticSDR", error=f"Traceback: {traceback.format_exc()}")
            return "Desculpe, tive um problema ao processar sua mensagem. Pode repetir? 🤔"
    
    async def _generate_response(self,
                                message: str,
                                context: Dict[str, Any],
                                lead_info: Dict[str, Any],
                                service_results: List[Dict[str, Any]],
                                media_context: str) -> str:
        """
        Gera resposta usando o ModelManager
        
        Args:
            message: Mensagem original
            context: Contexto analisado
            lead_info: Informações do lead
            service_results: Resultados dos serviços
            media_context: Contexto de mídia
            
        Returns:
            Resposta gerada
        """
        # Construir prompt com todas as informações
        prompt = self._build_prompt(
            message,
            context,
            lead_info,
            service_results,
            media_context
        )
        
        # Usar reasoning para casos complexos
        use_reasoning = (
            context.get("conversation_stage") in ["negociação", "objeção"] or
            len(service_results) > 0
        )
        
        # Gerar resposta
        response = await self.model_manager.get_response(
            prompt,
            system_prompt=self._get_instructions(),
            use_reasoning=use_reasoning
        )
        
        if not response:
            response = self._get_fallback_response(context)
        
        return response
    
    def _build_prompt(self,
                     message: str,
                     context: Dict[str, Any],
                     lead_info: Dict[str, Any],
                     service_results: List[Dict[str, Any]],
                     media_context: str) -> str:
        """Constrói prompt com contexto completo"""
        
        prompt_parts = [
            f"Mensagem do cliente: {message}"
        ]
        
        # Adicionar contexto
        if context.get("conversation_stage"):
            prompt_parts.append(f"Estágio da conversa: {context['conversation_stage']}")
        
        if context.get("user_intent"):
            prompt_parts.append(f"Intenção detectada: {context['user_intent']}")
        
        if context.get("urgency_level"):
            prompt_parts.append(f"Urgência: {context['urgency_level']}")
        
        # Adicionar informações do lead
        if lead_info.get("bill_value"):
            prompt_parts.append(f"Valor da conta: R$ {lead_info['bill_value']}")
        
        if lead_info.get("qualification_score"):
            prompt_parts.append(f"Score do lead: {lead_info['qualification_score']}/100")
        
        # Adicionar resultados de serviços
        for result in service_results:
            if result.get("service") == "calendar":
                prompt_parts.append("✅ Reunião agendada com sucesso!")
            elif result.get("service") == "crm":
                prompt_parts.append("✅ Lead atualizado no CRM")
            elif result.get("service") == "followup":
                prompt_parts.append("✅ Follow-up agendado")
        
        # Adicionar contexto de mídia
        if media_context:
            prompt_parts.append(f"Mídia recebida: {media_context}")
        
        # Adicionar instrução de ação
        prompt_parts.append(f"\nAção recomendada: {context.get('action_needed', 'conversar')}")
        prompt_parts.append("\nResponda de forma natural, amigável e profissional.")
        
        return "\n".join(prompt_parts)
    
    def _format_media_context(self, media_result: Dict[str, Any]) -> str:
        """Formata contexto de mídia para o prompt"""
        if media_result.get("type") == "image":
            if media_result.get("analysis", {}).get("is_bill"):
                value = media_result["analysis"].get("bill_value")
                if value:
                    return f"Conta de luz detectada com valor de R$ {value:.2f}"
                return "Imagem de conta de luz recebida"
            elif media_result.get("text"):
                return f"Imagem com texto: {media_result['text'][:100]}..."
            return "Imagem recebida"
        
        elif media_result.get("type") == "audio":
            if media_result.get("text"):
                return f"Áudio transcrito: {media_result['text'][:100]}..."
            return "Áudio recebido"
        
        elif media_result.get("type") == "document":
            return f"Documento {media_result.get('metadata', {}).get('doc_type', 'desconhecido')} recebido"
        
        return "Mídia recebida"
    
    def _get_fallback_response(self, context: Dict[str, Any]) -> str:
        """Resposta fallback baseada no contexto"""
        stage = context.get("conversation_stage", "início")
        
        responses = {
            "início": "Olá! 👋 Sou a Helen da SolarPrime. Como posso ajudar você a economizar na conta de luz?",
            "exploração": "Interessante! Me conta mais sobre sua situação atual com energia elétrica.",
            "qualificação": "Quanto você costuma pagar na conta de luz? Isso me ajuda a calcular sua economia.",
            "negociação": "Entendo suas preocupações. Que tal conversarmos melhor sobre isso?",
            "acompanhamento": "Fico à disposição para qualquer dúvida! Quando podemos conversar novamente?"
        }
        
        return responses.get(stage, "Como posso ajudar você hoje? 😊")
    
    def _detect_lead_changes(self, old_info: Dict[str, Any], new_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 Detecta mudanças significativas no lead
        
        Args:
            old_info: Informações anteriores do lead
            new_info: Novas informações extraídas
            
        Returns:
            Dicionário com campos que mudaram
        """
        changes = {}
        
        # Campos importantes para monitorar
        important_fields = [
            'name', 'email', 'bill_value', 'qualification_score',
            'current_stage', 'chosen_flow', 'phone', 'company',
            'address', 'cpf', 'consumption_kwh'
        ]
        
        for field in important_fields:
            old_value = old_info.get(field)
            new_value = new_info.get(field)
            
            # Detectar mudança (novo valor ou alteração)
            if new_value is not None and old_value != new_value:
                changes[field] = new_value
                emoji_logger.service_event(
                    f"🔄 Campo alterado: {field}",
                    old=old_value,
                    new=new_value
                )
        
        return changes
    
    async def _sync_lead_changes(self, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        🚀 Sincroniza mudanças importantes com o CRM
        
        Args:
            changes: Campos que mudaram
            
        Returns:
            Resultado da sincronização ou None
        """
        if not changes or not self.current_phone:
            return None
        
        # Campos que trigger sync imediato
        sync_triggers = [
            'bill_value', 'qualification_score', 'current_stage',
            'chosen_flow', 'name', 'email', 'company'
        ]
        
        # Verificar se há mudanças importantes
        should_sync = any(field in changes for field in sync_triggers)
        
        if should_sync:
            emoji_logger.service_event(
                "🔄 Sincronizando mudanças com CRM",
                fields=list(changes.keys())
            )
            
            try:
                # Preparar dados completos do lead
                sync_data = self.current_lead_info.copy()
                sync_data['phone'] = self.current_phone
                
                # Chamar sync através do TeamCoordinator
                result = await self.team_coordinator.sync_lead_to_crm(sync_data)
                
                if result.get("success"):
                    emoji_logger.system_success("✅ Lead sincronizado com CRM")
                    return result
                else:
                    emoji_logger.service_warning(f"Sync parcial: {result.get('message')}")
                    
            except Exception as e:
                emoji_logger.service_error(f"Erro no sync: {e}")
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do agent"""
        return {
            "initialized": self.is_initialized,
            "modules": {
                "model_manager": self.model_manager.get_model_info(),
                "multimodal": self.multimodal.is_enabled(),
                "team_coordinator": self.team_coordinator.get_service_status()
            },
            "conversation": {
                "messages": len(self.conversation_history),
                "lead_score": self.current_lead_info.get("qualification_score", 0),
                "stage": self.current_lead_info.get("stage", "novo")
            }
        }

# ============= SINGLETON PATTERN =============

async def get_agentic_agent() -> AgenticSDR:
    """
    Retorna instância singleton do AgenticSDR
    
    Returns:
        Instância única e inicializada do AgenticSDR
    """
    global _singleton_instance, _singleton_lock
    
    if _singleton_lock is None:
        _singleton_lock = asyncio.Lock()
    
    if _singleton_instance is None:
        async with _singleton_lock:
            if _singleton_instance is None:
                emoji_logger.system_event("🏗️ Criando instância singleton do AgenticSDR...")
                _singleton_instance = AgenticSDR()
                await _singleton_instance.initialize()
                emoji_logger.system_ready("✅ Singleton AgenticSDR criado e inicializado")
    
    return _singleton_instance

async def reset_agent():
    """Reseta o agent singleton (útil para testes)"""
    global _singleton_instance, _singleton_lock
    
    if _singleton_lock is None:
        _singleton_lock = asyncio.Lock()
        
    async with _singleton_lock:
        if _singleton_instance:
            emoji_logger.system_warning("🔄 Resetando singleton AgenticSDR...")
            _singleton_instance = None

# ============= PRE-WARMING =============

async def prewarm_agent(max_retries: int = 3):
    """
    Pre-aquece o agent na inicialização
    
    Args:
        max_retries: Número máximo de tentativas
    """
    for attempt in range(max_retries):
        try:
            emoji_logger.system_event(f"🔥 Pre-warming AgenticSDR (tentativa {attempt + 1}/{max_retries})...")
            
            agent = await get_agentic_agent()
            
            # Teste simples
            test_response = await agent.process_message("teste de inicialização")
            
            if test_response:
                emoji_logger.system_ready("✅ AgenticSDR pre-warmed com sucesso!")
                return True
                
        except Exception as e:
            emoji_logger.system_error("AgenticSDR", error=f"Erro no pre-warming (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Backoff exponencial
    
    emoji_logger.system_error("AgenticSDR", error="Falha no pre-warming após todas as tentativas")
    return False