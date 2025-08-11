"""
Sistema de Logs Avançado com Emojis para Debug
Logs detalhados de todos os componentes do sistema
"""

import sys
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
from app.config import settings


class EmojiLogger:
    """Logger com emojis para melhor visualização de debug"""
    
    # Emojis por categoria
    EMOJIS = {
        # AGENTIC SDR
        "agentic_start": "🤖",
        "agentic_thinking": "🧠", 
        "agentic_decision": "💭",
        "agentic_response": "💬",
        "agentic_context": "📊",
        "agentic_reasoning": "🔮",
        "agentic_multimodal": "📱",
        
        # SDR TEAMS
        "team_start": "👥",
        "team_coordinate": "🎯",
        "team_delegate": "🔄",
        "team_member_ready": "✅",
        "team_member_skip": "⏭️",
        "team_qualification": "✅",
        "team_calendar": "📅",
        "team_followup": "🔔",
        "team_crm": "💼",
        "team_knowledge": "📚",
        "team_bill_analyzer": "📋",
        
        # SUPABASE
        "supabase_connect": "🗄️",
        "supabase_query": "🔍",
        "supabase_insert": "📝",
        "supabase_update": "✏️", 
        "supabase_delete": "🗑️",
        "supabase_error": "❌",
        "supabase_success": "✅",
        
        # EVOLUTION API
        "evolution_webhook": "📨",
        "evolution_send": "📤",
        "evolution_receive": "📥",
        "evolution_media": "🎬",
        "evolution_error": "🚨",
        "evolution_success": "✅",
        
        # WEBHOOKS
        "webhook_receive": "📞",
        "webhook_process": "⚙️",
        "webhook_forward": "➡️",
        
        # SISTEMA
        "system_start": "🚀",
        "system_ready": "✅",
        "system_error": "💥",
        "system_warning": "⚠️",
        "system_info": "ℹ️",
        "system_debug": "🔧",
        
        # PERFORMANCE
        "perf_timer": "⏱️",
        "perf_fast": "⚡",
        "perf_slow": "🐌",
        "perf_memory": "🧮",
        
        # STATUS
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "debug": "🔍"
    }
    
    @classmethod
    def setup_logger(cls):
        """Configura o logger com formato customizado"""
        
        # Remove handler padrão
        logger.remove()
        
        # Formato com emojis e cores
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Handler para console com cores
        logger.add(
            sys.stdout,
            format=log_format,
            level="DEBUG" if settings.debug else "INFO",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # Handler para arquivo sem cores
        logger.add(
            "logs/sdr_debug.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="1 day",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Handler para erros críticos
        logger.add(
            "logs/sdr_errors.log", 
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="1 day",
            retention="30 days",
            compression="zip"
        )
    
    @classmethod
    def log_with_emoji(cls, level: str, category: str, message: str, **kwargs):
        """Log com emoji baseado na categoria"""
        emoji = cls.EMOJIS.get(category, "📝")
        formatted_message = f"{emoji} {message}"
        
        if kwargs:
            formatted_message += f" | Data: {kwargs}"
        
        getattr(logger, level.lower())(formatted_message)
    
    # Métodos para AGENTIC SDR
    @classmethod
    def agentic_start(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "agentic_start", f"AGENTIC SDR: {message}", **kwargs)
    
    @classmethod 
    def agentic_thinking(cls, message: str, **kwargs):
        cls.log_with_emoji("DEBUG", "agentic_thinking", f"Análise: {message}", **kwargs)
    
    @classmethod
    def agentic_decision(cls, message: str, score: float = None, **kwargs):
        if score:
            kwargs["decision_score"] = score
        cls.log_with_emoji("INFO", "agentic_decision", f"Decisão: {message}", **kwargs)
    
    @classmethod
    def agentic_context(cls, message: str, messages_analyzed: int = None, **kwargs):
        if messages_analyzed:
            kwargs["messages_count"] = messages_analyzed
        cls.log_with_emoji("DEBUG", "agentic_context", f"Contexto: {message}", **kwargs)
    
    @classmethod
    def agentic_reasoning(cls, message: str, model: str = None, **kwargs):
        if model:
            kwargs["reasoning_model"] = model
        cls.log_with_emoji("DEBUG", "agentic_reasoning", f"Reasoning: {message}", **kwargs)
    
    @classmethod
    def agentic_multimodal(cls, message: str, media_type: str = None, **kwargs):
        if media_type:
            kwargs["media_type"] = media_type
        cls.log_with_emoji("DEBUG", "agentic_multimodal", f"Multimodal: {message}", **kwargs)
    
    @classmethod
    def agentic_response(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "agentic_response", f"Resposta: {message}", **kwargs)
    
    # Métodos para SDR TEAMS
    @classmethod
    def team_start(cls, team_name: str, message: str, **kwargs):
        cls.log_with_emoji("INFO", "team_start", f"TEAM {team_name.upper()}: {message}", **kwargs)
    
    @classmethod
    def team_coordinate(cls, message: str, agents_count: int = None, **kwargs):
        if agents_count:
            kwargs["agents_active"] = agents_count
        cls.log_with_emoji("DEBUG", "team_coordinate", f"Coordenação: {message}", **kwargs)
    
    @classmethod
    def team_delegate(cls, agent_name: str, task: str, **kwargs):
        cls.log_with_emoji("DEBUG", "team_delegate", f"Delegando para {agent_name}: {task}", **kwargs)
    
    @classmethod
    def team_member_ready(cls, agent_name: str, status: str, **kwargs):
        cls.log_with_emoji("INFO", "team_member_ready", f"{agent_name} {status}", **kwargs)
    
    @classmethod
    def team_member_skip(cls, agent_name: str, status: str, **kwargs):
        cls.log_with_emoji("DEBUG", "team_member_skip", f"{agent_name} {status}", **kwargs)
    
    @classmethod
    def team_qualification(cls, message: str, criteria_met: int = None, **kwargs):
        if criteria_met:
            kwargs["criteria_passed"] = criteria_met
        cls.log_with_emoji("INFO", "team_qualification", f"Qualificação: {message}", **kwargs)
    
    @classmethod
    def team_calendar(cls, message: str, event_id: str = None, **kwargs):
        if event_id:
            kwargs["calendar_event"] = event_id
        cls.log_with_emoji("INFO", "team_calendar", f"Calendário: {message}", **kwargs)
    
    @classmethod
    def team_followup(cls, message: str, follow_type: str = None, **kwargs):
        if follow_type:
            kwargs["followup_type"] = follow_type
        cls.log_with_emoji("INFO", "team_followup", f"Follow-up: {message}", **kwargs)
    
    @classmethod
    def team_crm(cls, message: str, lead_id: str = None, action: str = None, **kwargs):
        if lead_id:
            kwargs["lead_id"] = lead_id
        if action:
            kwargs["crm_action"] = action
        cls.log_with_emoji("DEBUG", "team_crm", f"CRM: {message}", **kwargs)
    
    @classmethod
    def team_knowledge(cls, message: str, query: str = None, **kwargs):
        if query:
            kwargs["search_query"] = query
        cls.log_with_emoji("DEBUG", "team_knowledge", f"Knowledge: {message}", **kwargs)
    
    @classmethod
    def team_bill_analyzer(cls, message: str, bill_value: float = None, **kwargs):
        if bill_value:
            kwargs["bill_amount"] = bill_value
        cls.log_with_emoji("INFO", "team_bill_analyzer", f"Análise Conta: {message}", **kwargs)
    
    # Métodos para SUPABASE
    @classmethod
    def supabase_connect(cls, message: str, **kwargs):
        cls.log_with_emoji("DEBUG", "supabase_connect", f"Supabase Connect: {message}", **kwargs)
    
    @classmethod
    def supabase_query(cls, table: str, operation: str, **kwargs):
        kwargs.update({"table": table, "operation": operation})
        cls.log_with_emoji("DEBUG", "supabase_query", f"Query {table}: {operation}", **kwargs)
    
    @classmethod
    def supabase_insert(cls, table: str, count: int = 1, **kwargs):
        kwargs.update({"table": table, "records_inserted": count})
        cls.log_with_emoji("DEBUG", "supabase_insert", f"Insert {table}: {count} registros", **kwargs)
    
    @classmethod
    def supabase_update(cls, table: str, count: int = 1, **kwargs):
        kwargs.update({"table": table, "records_updated": count})
        cls.log_with_emoji("DEBUG", "supabase_update", f"Update {table}: {count} registros", **kwargs)
    
    # 🚀 NOVO: Métodos para Services diretos
    @classmethod
    def service_ready(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "system_ready", f"Service: {message}", **kwargs)
    
    @classmethod
    def service_warning(cls, message: str, **kwargs):
        cls.log_with_emoji("WARNING", "system_warning", f"Service: {message}", **kwargs)
    
    @classmethod
    def service_error(cls, message: str, **kwargs):
        cls.log_with_emoji("ERROR", "system_error", f"Service: {message}", **kwargs)
    
    @classmethod
    def service_call(cls, message: str, **kwargs):
        cls.log_with_emoji("DEBUG", "webhook_process", f"Service Call: {message}", **kwargs)
    
    @classmethod
    def calendar_event(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "team_calendar", f"Calendar: {message}", **kwargs)
    
    @classmethod
    def crm_event(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "team_crm", f"CRM: {message}", **kwargs)
    
    @classmethod
    def crm_note(cls, message: str, **kwargs):
        cls.log_with_emoji("DEBUG", "team_crm", f"CRM Note: {message}", **kwargs)
    
    @classmethod
    def followup_event(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "team_followup", f"FollowUp: {message}", **kwargs)
    
    @classmethod
    def supabase_error(cls, error: str, table: str = None, **kwargs):
        if table:
            kwargs["table"] = table
        cls.log_with_emoji("ERROR", "supabase_error", f"Erro Supabase: {error}", **kwargs)
    
    @classmethod
    def supabase_success(cls, message: str, execution_time: float = None, **kwargs):
        if execution_time:
            kwargs["execution_ms"] = round(execution_time * 1000, 2)
        cls.log_with_emoji("DEBUG", "supabase_success", f"Sucesso: {message}", **kwargs)
    
    # Métodos para EVOLUTION API
    @classmethod
    def evolution_webhook(cls, event: str, instance: str, **kwargs):
        kwargs.update({"event_type": event, "instance": instance})
        cls.log_with_emoji("INFO", "evolution_webhook", f"Webhook: {event} de {instance}", **kwargs)
    
    @classmethod
    def evolution_send(cls, to: str, message_type: str, **kwargs):
        kwargs.update({"recipient": to, "type": message_type})
        cls.log_with_emoji("INFO", "evolution_send", f"Enviando {message_type} para {to}", **kwargs)
    
    @classmethod
    def evolution_receive(cls, from_user: str, message_type: str, **kwargs):
        kwargs.update({"sender": from_user, "type": message_type})
        cls.log_with_emoji("INFO", "evolution_receive", f"Recebido {message_type} de {from_user}", **kwargs)
    
    @classmethod
    def evolution_media(cls, media_type: str, size: int = None, **kwargs):
        if size:
            kwargs["file_size_bytes"] = size
        cls.log_with_emoji("DEBUG", "evolution_media", f"Processando mídia {media_type}", **kwargs)
    
    @classmethod
    def evolution_error(cls, error: str, **kwargs):
        cls.log_with_emoji("ERROR", "evolution_error", f"Erro Evolution: {error}", **kwargs)
    
    # Métodos para WEBHOOKS
    @classmethod
    def webhook_receive(cls, endpoint: str, source: str, **kwargs):
        kwargs.update({"endpoint": endpoint, "source": source})
        cls.log_with_emoji("INFO", "webhook_receive", f"Webhook recebido: {endpoint} de {source}", **kwargs)
    
    @classmethod
    def webhook_process(cls, message: str, processing_time: float = None, **kwargs):
        if processing_time:
            kwargs["processing_ms"] = round(processing_time * 1000, 2)
        cls.log_with_emoji("DEBUG", "webhook_process", f"Processando: {message}", **kwargs)
    
    # Métodos para SISTEMA
    @classmethod
    def system_start(cls, component: str, **kwargs):
        cls.log_with_emoji("INFO", "system_start", f"Iniciando {component}", **kwargs)
    
    @classmethod
    def system_ready(cls, component: str, startup_time = None, **kwargs):
        if startup_time is not None and not isinstance(startup_time, str):
            try:
                kwargs["startup_ms"] = round(float(startup_time) * 1000, 2)
            except (ValueError, TypeError):
                pass  # Se não conseguir converter, ignora o startup_time
        cls.log_with_emoji("INFO", "system_ready", f"{component} pronto", **kwargs)
    
    @classmethod
    def system_error(cls, component: str, error: str, **kwargs):
        kwargs["component"] = component
        cls.log_with_emoji("ERROR", "system_error", f"Erro em {component}: {error}", **kwargs)
    
    @classmethod
    def system_warning(cls, message: str, **kwargs):
        cls.log_with_emoji("WARNING", "system_warning", message, **kwargs)
    
    @classmethod
    def system_info(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "system_info", message, **kwargs)
    
    @classmethod
    def system_debug(cls, message: str, **kwargs):
        cls.log_with_emoji("DEBUG", "system_debug", message, **kwargs)
    
    @classmethod
    def system_success(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "success", message, **kwargs)
    
    @classmethod
    def system_shutdown(cls, component: str, message: str = "", **kwargs):
        """Log de shutdown de componente"""
        kwargs["component"] = component
        full_message = f"Parando {component}"
        if message:
            full_message += f": {message}"
        cls.log_with_emoji("INFO", "system_info", full_message, **kwargs)
    
    @classmethod
    def whatsapp_sent(cls, message: str, **kwargs):
        """Log de mensagem WhatsApp enviada"""
        cls.log_with_emoji("INFO", "evolution_send", f"WhatsApp: {message}", **kwargs)
    
    @classmethod
    def evolution_success(cls, message: str, **kwargs):
        """Log de sucesso na Evolution API"""
        cls.log_with_emoji("INFO", "evolution_success", message, **kwargs)
    
    # Métodos para PERFORMANCE
    @classmethod
    def perf_timer(cls, operation: str, duration_ms: float, **kwargs):
        kwargs["duration_ms"] = round(duration_ms, 2)
        
        # Escolhe emoji baseado na performance
        if duration_ms < 100:
            emoji = "⚡"  # Muito rápido
        elif duration_ms < 500:
            emoji = "⏱️"  # Normal
        else:
            emoji = "🐌"  # Lento
            
        cls.log_with_emoji("DEBUG", "perf_timer", f"{emoji} {operation}: {duration_ms:.2f}ms", **kwargs)
    
    @classmethod
    def perf_memory(cls, component: str, memory_mb: float, **kwargs):
        kwargs.update({"component": component, "memory_mb": round(memory_mb, 2)})
        cls.log_with_emoji("DEBUG", "perf_memory", f"Memória {component}: {memory_mb:.2f}MB", **kwargs)


# Configurar logger no import
EmojiLogger.setup_logger()

# Exportar instância principal
emoji_logger = EmojiLogger()