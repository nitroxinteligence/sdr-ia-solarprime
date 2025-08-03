"""
Configurações centralizadas do SDR IA SolarPrime
"""
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis de ambiente - força override de variáveis existentes
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path, override=True)

# Debug: mostra se .env foi encontrado
if env_path.exists():
    print(f"✅ Arquivo .env encontrado: {env_path}")
else:
    print(f"⚠️ Arquivo .env NÃO encontrado: {env_path}")

class Settings(BaseSettings):
    """Configurações do sistema"""
    
    # OpenAI
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    # Google Gemini
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    
    # Evolution API
    evolution_api_url: str = Field(default="http://localhost:8080", env="EVOLUTION_API_URL")
    evolution_api_key: str = Field(default="", env="EVOLUTION_API_KEY")
    evolution_instance_name: str = Field(default="sdr-ia-solarprime", env="EVOLUTION_INSTANCE_NAME")
    
    # Supabase
    supabase_url: str = Field(default="", env="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(default="", env="SUPABASE_SERVICE_KEY")
    supabase_db_url: str = Field(default="", env="SUPABASE_DB_URL")  # URL PostgreSQL direta
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_username: str = Field(default="default", env="REDIS_USERNAME")
    
    # Google Calendar
    google_use_service_account: bool = Field(default=True, env="GOOGLE_USE_SERVICE_ACCOUNT")
    google_service_account_email: str = Field(default="", env="GOOGLE_SERVICE_ACCOUNT_EMAIL")
    google_private_key: str = Field(default="", env="GOOGLE_PRIVATE_KEY")
    google_project_id: str = Field(default="", env="GOOGLE_PROJECT_ID")
    google_private_key_id: str = Field(default="", env="GOOGLE_PRIVATE_KEY_ID")
    google_client_id: str = Field(default="", env="GOOGLE_CLIENT_ID")
    google_calendar_id: str = Field(default="", env="GOOGLE_CALENDAR_ID")
    disable_google_calendar: bool = Field(default=False, env="DISABLE_GOOGLE_CALENDAR")
    
    # Kommo CRM
    kommo_client_id: str = Field(default="", env="KOMMO_CLIENT_ID")
    kommo_base_url: str = Field(default="https://api-c.kommo.com", env="KOMMO_BASE_URL")
    kommo_client_secret: str = Field(default="", env="KOMMO_CLIENT_SECRET")
    kommo_subdomain: str = Field(default="", env="KOMMO_SUBDOMAIN")
    kommo_redirect_uri: str = Field(default="", env="KOMMO_REDIRECT_URI")
    kommo_pipeline_id: str = Field(default="", env="KOMMO_PIPELINE_ID")
    kommo_long_lived_token: str = Field(default="", env="KOMMO_LONG_LIVED_TOKEN")
    
    # URLs da API
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    webhook_base_url: str = Field(default="http://localhost:8000", env="WEBHOOK_BASE_URL")
    
    # Configurações do Agente
    agente_response_delay_seconds: int = Field(default=2, env="AGENTE_RESPONSE_DELAY_SECONDS")
    
    # Relatórios
    report_day_of_week: str = Field(default="monday", env="REPORT_DAY_OF_WEEK")
    report_time: str = Field(default="09:00", env="REPORT_TIME")
    whatsapp_group_id: str = Field(default="", env="WHATSAPP_GROUP_ID")
    
    # Horários de funcionamento
    business_hours_start: str = Field(default="08:00", env="BUSINESS_HOURS_START")
    business_hours_end: str = Field(default="20:00", env="BUSINESS_HOURS_END")
    timezone: str = Field(default="America/Sao_Paulo", env="TIMEZONE")
    
    # Configurações do Sistema
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    
    # AGnO Framework
    agno_model: str = Field(default="gemini-2.5-pro")
    agno_fallback_model: str = Field(default="o1-mini")
    agno_max_tokens: int = Field(default=4096)
    agno_temperature: float = Field(default=0.7)
    agno_reasoning_enabled: bool = Field(default=True)
    
    # Limites e Timeouts
    max_message_length: int = Field(default=4096)
    webhook_timeout: int = Field(default=30)
    typing_simulation_delay: float = Field(default=2.0)
    max_follow_up_attempts: int = Field(default=3)
    
    # ============= CONTROLE DE AGENTES =============
    # Agentes especializados do SDR Team
    enable_qualification_agent: bool = Field(default=True, env="ENABLE_QUALIFICATION_AGENT")
    enable_calendar_agent: bool = Field(default=True, env="ENABLE_CALENDAR_AGENT")
    enable_followup_agent: bool = Field(default=True, env="ENABLE_FOLLOWUP_AGENT")
    enable_knowledge_agent: bool = Field(default=True, env="ENABLE_KNOWLEDGE_AGENT")
    enable_crm_agent: bool = Field(default=True, env="ENABLE_CRM_AGENT")
    enable_bill_analyzer_agent: bool = Field(default=True, env="ENABLE_BILL_ANALYZER_AGENT")
    
    # Agente principal
    enable_agentic_sdr: bool = Field(default=True, env="ENABLE_AGENTIC_SDR")
    enable_sdr_team: bool = Field(default=True, env="ENABLE_SDR_TEAM")
    
    # ============= TIMING E HUMANIZAÇÃO =============
    # Tempos de digitação (segundos)
    typing_duration_short: float = Field(default=2.0, env="TYPING_DURATION_SHORT")
    typing_duration_medium: float = Field(default=4.0, env="TYPING_DURATION_MEDIUM")
    typing_duration_long: float = Field(default=7.0, env="TYPING_DURATION_LONG")
    typing_speed_chars_per_second: int = Field(default=50, env="TYPING_SPEED_CHARS_PER_SECOND")
    
    # Delays de resposta (segundos)
    response_delay_min: float = Field(default=1.0, env="RESPONSE_DELAY_MIN")
    response_delay_max: float = Field(default=5.0, env="RESPONSE_DELAY_MAX")
    response_delay_thinking: float = Field(default=8.0, env="RESPONSE_DELAY_THINKING")
    
    # Intervalos entre ações
    delay_between_messages: float = Field(default=1.5, env="DELAY_BETWEEN_MESSAGES")
    delay_before_media: float = Field(default=2.0, env="DELAY_BEFORE_MEDIA")
    delay_after_media: float = Field(default=3.0, env="DELAY_AFTER_MEDIA")
    
    # Comportamentos humanos
    simulate_reading_time: bool = Field(default=True, env="SIMULATE_READING_TIME")
    reading_speed_wpm: int = Field(default=200, env="READING_SPEED_WPM")
    response_time_variation: float = Field(default=0.3, env="RESPONSE_TIME_VARIATION")
    
    # ============= FUNCIONALIDADES =============
    # Análise e Contexto
    enable_context_analysis: bool = Field(default=True, env="ENABLE_CONTEXT_ANALYSIS")
    enable_sentiment_analysis: bool = Field(default=True, env="ENABLE_SENTIMENT_ANALYSIS")
    enable_emotional_triggers: bool = Field(default=True, env="ENABLE_EMOTIONAL_TRIGGERS")
    enable_lead_scoring: bool = Field(default=True, env="ENABLE_LEAD_SCORING")
    
    # Recursos Avançados
    enable_multimodal_analysis: bool = Field(default=True, env="ENABLE_MULTIMODAL_ANALYSIS")
    enable_bill_photo_analysis: bool = Field(default=True, env="ENABLE_BILL_PHOTO_ANALYSIS")
    enable_voice_message_transcription: bool = Field(default=False, env="ENABLE_VOICE_MESSAGE_TRANSCRIPTION")
    enable_auto_translation: bool = Field(default=False, env="ENABLE_AUTO_TRANSLATION")
    
    # Integrações
    enable_calendar_integration: bool = Field(default=True, env="ENABLE_CALENDAR_INTEGRATION")
    enable_crm_integration: bool = Field(default=True, env="ENABLE_CRM_INTEGRATION")
    enable_knowledge_base: bool = Field(default=True, env="ENABLE_KNOWLEDGE_BASE")
    enable_follow_up_automation: bool = Field(default=True, env="ENABLE_FOLLOW_UP_AUTOMATION")
    
    # Comunicação
    enable_emoji_usage: bool = Field(default=True, env="ENABLE_EMOJI_USAGE")
    enable_audio_messages: bool = Field(default=False, env="ENABLE_AUDIO_MESSAGES")
    enable_sticker_responses: bool = Field(default=False, env="ENABLE_STICKER_RESPONSES")
    enable_reaction_messages: bool = Field(default=True, env="ENABLE_REACTION_MESSAGES")
    
    # ============= QUALIFICAÇÃO =============
    # Scores e thresholds
    min_qualification_score: int = Field(default=7, env="MIN_QUALIFICATION_SCORE")
    auto_schedule_threshold: int = Field(default=9, env="AUTO_SCHEDULE_THRESHOLD")
    bill_value_threshold: float = Field(default=200.0, env="BILL_VALUE_THRESHOLD")
    
    # Comportamentos
    auto_request_bill_photo: bool = Field(default=True, env="AUTO_REQUEST_BILL_PHOTO")
    require_decision_maker: bool = Field(default=True, env="REQUIRE_DECISION_MAKER")
    max_qualification_attempts: int = Field(default=3, env="MAX_QUALIFICATION_ATTEMPTS")
    
    # ============= IA E MODELOS =============
    # Modelos principais
    primary_ai_model: str = Field(default="gemini-2.5-pro", env="PRIMARY_AI_MODEL")
    fallback_ai_model: str = Field(default="o1-mini", env="FALLBACK_AI_MODEL")
    enable_model_fallback: bool = Field(default=True, env="ENABLE_MODEL_FALLBACK")
    
    # Configurações de geração
    ai_max_tokens: int = Field(default=4096, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")
    ai_top_p: float = Field(default=0.9, env="AI_TOP_P")
    ai_frequency_penalty: float = Field(default=0.1, env="AI_FREQUENCY_PENALTY")
    
    # Streaming e processamento
    enable_streaming_responses: bool = Field(default=True, env="ENABLE_STREAMING_RESPONSES")
    enable_parallel_agent_processing: bool = Field(default=True, env="ENABLE_PARALLEL_AGENT_PROCESSING")
    max_reasoning_depth: int = Field(default=3, env="MAX_REASONING_DEPTH")
    
    @validator('google_private_key')
    def process_private_key(cls, v):
        """Processa a chave privada do Google para formato correto"""
        if v:
            return v.replace('\\n', '\n')
        return v
    
    def get_google_credentials(self) -> Dict[str, Any]:
        """Retorna credenciais do Google formatadas para autenticação"""
        return {
            "type": "service_account",
            "project_id": self.google_project_id,
            "private_key_id": self.google_private_key_id,
            "private_key": self.google_private_key,
            "client_email": self.google_service_account_email,
            "client_id": self.google_client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.google_service_account_email}"
        }
    
    def get_redis_url(self) -> str:
        """Constrói a URL do Redis com autenticação se necessário"""
        if self.redis_password:
            return f"redis://{self.redis_username}:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"
    
    def get_postgres_url(self) -> str:
        """Retorna a URL de conexão PostgreSQL do Supabase"""
        import os
        
        # Tenta pegar direto do ambiente primeiro
        db_url = os.getenv('SUPABASE_DB_URL') or self.supabase_db_url
        
        if db_url and db_url != "":
            # Oculta senha para log
            safe_url = db_url.split('@')[1] if '@' in db_url else db_url
            print(f"✅ PostgreSQL URL configurada: ...@{safe_url}")
            return db_url
        
        # Fallback para localhost se não estiver configurada
        print("⚠️ SUPABASE_DB_URL não encontrada, usando localhost (desenvolvimento)")
        return "postgresql://postgres:postgres@localhost:5432/postgres"
    
    def is_business_hours(self) -> bool:
        """Verifica se está dentro do horário comercial"""
        from datetime import datetime
        import pytz
        
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")
        
        return self.business_hours_start <= current_time <= self.business_hours_end
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment

# Instância global das configurações
settings = Settings()

# Constantes do sistema
QUALIFICATION_STAGES = [
    "INITIAL_CONTACT",
    "IDENTIFYING_NEED",
    "QUALIFYING",
    "DISCOVERY",
    "PRESENTING_SOLUTION",
    "HANDLING_OBJECTIONS",
    "SCHEDULING",
    "FOLLOW_UP"
]

QUALIFICATION_STATUS = [
    "PENDING",
    "QUALIFIED",
    "NOT_QUALIFIED"
]

SOLUTION_TYPES = [
    "USINA_PROPRIA",
    "USINA_TERRENO_PARCEIRO",
    "ASSINATURA_COMERCIAL",
    "ASSINATURA_RESIDENCIAL",
    "MERCADO_LIVRE",
    "MOBILIDADE_ELETRICA"
]

FOLLOW_UP_TYPES = [
    "IMMEDIATE_REENGAGEMENT",
    "DAILY_NURTURING",
    "MEETING_CONFIRMATION",
    "MEETING_REMINDER",
    "ABANDONMENT_CHECK",
    "CUSTOM"
]

# Mensagens padrão da Helen
HELEN_MESSAGES = {
    "greeting": "Oii! Seja muito bem-vindo à Solar Prime! 🌞\nMeu nome é Helen Vieira\nSou consultora especialista aqui da Solar Prime em Recife",
    "ask_name": "Antes de começarmos, como posso chamá-lo?",
    "identify_need": "{name}, me conte: você está buscando uma forma de economizar na sua energia ou tem interesse em instalar uma usina solar?",
    "ask_bill_value": "{name}, para eu preparar a melhor proposta para você, preciso saber: qual o valor aproximado da sua conta de luz mensal?",
    "high_bill_reaction": "Eita... 😳\nPera aí\nR${value} por mês???\nMeu Deus, isso é quase 2 salários mínimos\nTodo mês...",
    "present_solution": "{name}, com uma conta de *R${value}*, nossa solução traz desconto de *20%* líquido garantido em contrato",
    "schedule_meeting": "{name}, que tal agendarmos uma apresentação de 30 minutos?",
    "follow_up_immediate": "Olá, {name}! Vi que nossa conversa ficou pela metade. Posso continuar te ajudando?",
    "follow_up_daily": "{name}, se ainda tiver interesse em economizar na conta de luz, estarei aqui. Nossa solução realmente pode fazer a diferença",
    "meeting_confirmation": "Oi {name}! Passando para confirmar nossa reunião de amanhã às {time}. Você confirma presença?",
    "meeting_reminder": "{name}, nossa reunião é daqui a 2 horas! Estou preparando tudo para te mostrar como economizar na sua conta de luz 💡"
}