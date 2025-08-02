"""
Configurações centralizadas do sistema SDR Agent
Carrega todas as variáveis de ambiente necessárias
"""

import os
from datetime import time
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# ===========================
# CAMINHOS BASE
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENTE_DIR = BASE_DIR / "agente"
CREDENTIALS_DIR = BASE_DIR / "credentials"

# ===========================
# CONFIGURAÇÕES BÁSICAS
# ===========================
API_PORT = int(os.getenv("API_PORT", "8000"))
PORT = API_PORT  # Alias para compatibilidade com agente/main.py
HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TZ = os.getenv("TZ", "America/Sao_Paulo")

# ===========================
# GOOGLE GEMINI AI
# ===========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ===========================
# GOOGLE CALENDAR
# ===========================
GOOGLE_USE_SERVICE_ACCOUNT = os.getenv("GOOGLE_USE_SERVICE_ACCOUNT", "true").lower() == "true"
GOOGLE_SERVICE_ACCOUNT_EMAIL = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL", "")
GOOGLE_PRIVATE_KEY = os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "")
GOOGLE_PRIVATE_KEY_ID = os.getenv("GOOGLE_PRIVATE_KEY_ID", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
DISABLE_GOOGLE_CALENDAR = os.getenv("DISABLE_GOOGLE_CALENDAR", "false").lower() == "true"

# Configurações de agendamento
CALENDAR_BUSINESS_HOURS = {
    "start": time(8, 0),  # 8:00
    "end": time(18, 0),   # 18:00
}
CALENDAR_SLOT_DURATION = 60  # minutos
CALENDAR_MIN_INTERVAL = 10   # minutos entre agendamentos

CALENDAR_DEFAULT_SLOTS = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]

# ===========================
# EVOLUTION API (WHATSAPP)
# ===========================
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "sdr-agent")

# ===========================
# SUPABASE
# ===========================
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# ===========================
# REDIS
# ===========================
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = bool(REDIS_URL and REDIS_URL != "redis://localhost:6379")

# ===========================
# KOMMO CRM
# ===========================
KOMMO_SUBDOMAIN = os.getenv("KOMMO_SUBDOMAIN", "")
KOMMO_LONG_LIVED_TOKEN = os.getenv("KOMMO_LONG_LIVED_TOKEN", "")
KOMMO_BASE_URL = f"https://{KOMMO_SUBDOMAIN}.kommo.com" if KOMMO_SUBDOMAIN else ""

# Pipeline stages mapping
KOMMO_STAGES = {
    "NOVO_LEAD": "novo lead",
    "EM_NEGOCIACAO": "em negociação",
    "EM_QUALIFICACAO": "em qualificação", 
    "QUALIFICADO": "qualificado",
    "REUNIAO_AGENDADA": "reunião agendada",
    "NAO_INTERESSADO": "não interessado"
}

# ===========================
# CONFIGURAÇÕES DO AGENTE
# ===========================
BUSINESS_HOURS_START = int(os.getenv("BUSINESS_HOURS_START", "8"))
BUSINESS_HOURS_END = int(os.getenv("BUSINESS_HOURS_END", "18"))
BUSINESS_DAYS = os.getenv("BUSINESS_DAYS", "1,2,3,4,5").split(",")

# Follow-up
FOLLOW_UP_ENABLED = os.getenv("FOLLOW_UP_ENABLED", "true").lower() == "true"
FOLLOW_UP_DELAY_MINUTES = 30  # Primeira tentativa após 30 minutos
FOLLOW_UP_DELAY_HOURS = 24    # Segunda tentativa após 24 horas
FOLLOW_UP_MAX_ATTEMPTS = 2

# Delay de resposta (simula digitação)
AI_RESPONSE_DELAY_SECONDS = int(os.getenv("AI_RESPONSE_DELAY_SECONDS", "2"))
AI_TYPING_DELAY_MAX = 15  # Máximo de 15 segundos para mensagens grandes

# Message chunking
MESSAGE_CHUNK_MAX_WORDS = 30
MESSAGE_CHUNK_MIN_WORDS = 3
MESSAGE_CHUNK_MAX_CHARS = 1200
MESSAGE_CHUNK_JOIN_PROBABILITY = 0.6

# Relatórios
REPORT_ENABLED = os.getenv("REPORT_ENABLED", "true").lower() == "true"
REPORT_DAY_OF_WEEK = int(os.getenv("REPORT_DAY_OF_WEEK", "1"))
REPORT_TIME = os.getenv("REPORT_TIME", "09:00")
REPORT_WHATSAPP_GROUP = os.getenv("REPORT_WHATSAPP_GROUP", "")

# ===========================
# SEGURANÇA
# ===========================
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
WEBHOOK_SIGNATURE_SECRET = os.getenv("WEBHOOK_SIGNATURE_SECRET", "")

# ===========================
# MONITORING
# ===========================
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ===========================
# VALIDAÇÕES
# ===========================
def validate_config():
    """Valida se todas as configurações críticas estão presentes"""
    errors = []
    
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY não configurada")
    
    if not EVOLUTION_API_URL:
        errors.append("EVOLUTION_API_URL não configurada")
    
    if not EVOLUTION_API_KEY:
        errors.append("EVOLUTION_API_KEY não configurada")
    
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL não configurada")
    
    if not SUPABASE_SERVICE_KEY:
        errors.append("SUPABASE_SERVICE_KEY não configurada")
    
    if not KOMMO_SUBDOMAIN:
        errors.append("KOMMO_SUBDOMAIN não configurado")
    
    if not KOMMO_LONG_LIVED_TOKEN:
        errors.append("KOMMO_LONG_LIVED_TOKEN não configurado")
    
    if GOOGLE_USE_SERVICE_ACCOUNT and not DISABLE_GOOGLE_CALENDAR:
        if not GOOGLE_SERVICE_ACCOUNT_EMAIL:
            errors.append("GOOGLE_SERVICE_ACCOUNT_EMAIL não configurado")
        if not GOOGLE_PRIVATE_KEY:
            errors.append("GOOGLE_PRIVATE_KEY não configurado")
    
    return errors

# Executar validação ao importar
config_errors = validate_config()
if config_errors and not DEBUG:
    print("⚠️  Erros de configuração encontrados:")
    for error in config_errors:
        print(f"   - {error}")