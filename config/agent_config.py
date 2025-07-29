"""
Configuração do Agente SDR SolarPrime
====================================
Configurações centralizadas para o agente de IA usando AGnO Framework
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class GeminiConfig(BaseModel):
    """Configurações do Google Gemini"""
    api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model: str = Field(default="gemini-2.5-pro")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)
    top_p: float = Field(default=0.95)
    top_k: int = Field(default=40)

class OpenAIConfig(BaseModel):
    """Configurações do OpenAI (Fallback)"""
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = Field(default="gpt-4.1-nano")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)

class AgentPersonality(BaseModel):
    """Personalidade e características do agente"""
    name: str = Field(default="Luna")
    role: str = Field(default="Consultora de Energia Solar")
    company: str = Field(default="SolarPrime Boa Viagem")
    
    # Características da personalidade
    traits: List[str] = Field(default_factory=lambda: [
        "profissional",
        "empática",
        "consultiva",
        "educativa",
        "persuasiva",
        "paciente"
    ])
    
    # Tom de voz
    voice_tone: str = Field(default="amigável e profissional")
    
    # Objetivos
    goals: List[str] = Field(default_factory=lambda: [
        "qualificar leads de forma natural",
        "educar sobre energia solar",
        "identificar necessidades específicas",
        "agendar reuniões com consultores",
        "manter conversação fluida e humana"
    ])

class SalesStages(BaseModel):
    """Estágios do processo de vendas"""
    stages: Dict[str, str] = Field(default_factory=lambda: {
        "INITIAL_CONTACT": "Primeiro contato e apresentação",
        "IDENTIFICATION": "Identificação do lead (nome)",
        "DISCOVERY": "Descoberta de necessidades (tipo de imóvel, consumo)",
        "QUALIFICATION": "Qualificação (valor da conta, interesse)",
        "OBJECTION_HANDLING": "Tratamento de objeções",
        "SCHEDULING": "Agendamento de reunião",
        "FOLLOW_UP": "Acompanhamento pós-contato"
    })
    
    # Perguntas-chave por estágio
    key_questions: Dict[str, List[str]] = Field(default_factory=lambda: {
        "IDENTIFICATION": [
            "Posso saber seu nome?",
            "Com quem tenho o prazer de falar?"
        ],
        "DISCOVERY": [
            "Você mora em casa ou apartamento?",
            "É proprietário(a) do imóvel?",
            "Tem interesse em economizar na conta de energia?"
        ],
        "QUALIFICATION": [
            "Qual o valor médio da sua conta de energia?",
            "Já considerou energia solar antes?",
            "Conhece os benefícios da energia solar?"
        ]
    })

class SolarSolutions(BaseModel):
    """Soluções de energia solar oferecidas"""
    solutions: Dict[str, Dict[str, str]] = Field(default_factory=lambda: {
        "RESIDENCIAL": {
            "name": "Solar Residencial",
            "description": "Sistema completo para sua casa",
            "benefits": "Economia de até 95% na conta de luz"
        },
        "EMPRESARIAL": {
            "name": "Solar Empresarial", 
            "description": "Soluções para empresas e comércios",
            "benefits": "Redução de custos operacionais"
        },
        "RURAL": {
            "name": "Solar Rural",
            "description": "Energia para propriedades rurais",
            "benefits": "Independência energética no campo"
        },
        "CONDOMINIO": {
            "name": "Solar Condomínio",
            "description": "Economia para áreas comuns",
            "benefits": "Redução do condomínio"
        },
        "FAZENDA_SOLAR": {
            "name": "Fazenda Solar",
            "description": "Investimento em usina solar compartilhada",
            "benefits": "Economia sem instalação no telhado"
        }
    })

class ConversationRules(BaseModel):
    """Regras de conversação e comportamento"""
    max_message_length: int = Field(default=500)
    typing_simulation: bool = Field(default=True)
    typing_speed_wpm: int = Field(default=200)
    
    # Horários de atendimento
    business_hours: Dict[str, str] = Field(default_factory=lambda: {
        "start": "08:00",
        "end": "18:00",
        "timezone": "America/Sao_Paulo"
    })
    
    # Tempos de resposta (em segundos)
    response_delays: Dict[str, int] = Field(default_factory=lambda: {
        "min": 3,
        "max": 8,
        "typing_base": 2
    })
    
    # Regras de conversa
    rules: List[str] = Field(default_factory=lambda: [
        "Sempre ser respeitoso e profissional",
        "Não insistir se o lead não tiver interesse",
        "Focar em benefícios, não em características técnicas",
        "Usar linguagem simples e acessível",
        "Responder perguntas antes de fazer novas",
        "Máximo 3 tentativas de contato sem resposta"
    ])

class MemoryConfig(BaseModel):
    """Configurações de memória e contexto"""
    context_window_size: int = Field(default=10)  # Últimas N mensagens
    long_term_memory: bool = Field(default=True)
    memory_summary_threshold: int = Field(default=20)  # Resumir após N mensagens
    
    # Informações a lembrar
    remember_fields: List[str] = Field(default_factory=lambda: [
        "nome",
        "tipo_imovel",
        "valor_conta",
        "interesse_nivel",
        "objecoes",
        "preferencias",
        "historico_interacoes"
    ])

class SDRConfig(BaseSettings):
    """Configuração principal do SDR"""
    # Configurações dos componentes
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    personality: AgentPersonality = Field(default_factory=AgentPersonality)
    sales_stages: SalesStages = Field(default_factory=SalesStages)
    solutions: SolarSolutions = Field(default_factory=SolarSolutions)
    conversation: ConversationRules = Field(default_factory=ConversationRules)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    
    # Configurações de fallback e retry
    enable_fallback: bool = Field(default_factory=lambda: os.getenv("ENABLE_FALLBACK", "true").lower() == "true")
    max_retries: int = Field(default_factory=lambda: int(os.getenv("MAX_AI_RETRIES", "3")))
    retry_delay: int = Field(default_factory=lambda: int(os.getenv("RETRY_DELAY_SECONDS", "2")))
    response_cache_ttl: int = Field(default_factory=lambda: int(os.getenv("RESPONSE_CACHE_TTL_MINUTES", "60")))
    
    # Configurações gerais
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")
    log_level: str = Field(default="INFO")
    
    # Configurações de follow-up
    enable_follow_up: bool = Field(default_factory=lambda: os.getenv("ENABLE_FOLLOW_UP", "true").lower() == "true")
    follow_up_delay_minutes: int = Field(default_factory=lambda: int(os.getenv("FOLLOW_UP_DELAY_MINUTES", "30")))
    follow_up_second_delay_hours: int = Field(default_factory=lambda: int(os.getenv("FOLLOW_UP_SECOND_DELAY_HOURS", "24")))
    
    # Configurações de follow-up inteligente
    enable_intelligent_follow_up: bool = Field(default_factory=lambda: os.getenv("ENABLE_INTELLIGENT_FOLLOW_UP", "true").lower() == "true")
    follow_up_context_messages: int = Field(default_factory=lambda: int(os.getenv("FOLLOW_UP_CONTEXT_MESSAGES", "100")))
    follow_up_min_interest_level: int = Field(default_factory=lambda: int(os.getenv("FOLLOW_UP_MIN_INTEREST_LEVEL", "3")))
    
    # Mensagens padrão
    default_messages: Dict[str, str] = Field(default_factory=lambda: {
        "greeting": """Olá! 👋 Sou a {name} da {company}!

Estou entrando em contato porque temos uma oportunidade incrível de economia na sua conta de energia através da energia solar. 

Você tem interesse em conhecer como pode economizar até 95% na sua conta de luz?""",
        
        "no_interest": """Entendo perfeitamente! Agradeço sua atenção.

Caso mude de ideia ou queira saber mais sobre energia solar no futuro, estarei sempre à disposição.

Tenha um excelente dia!""",
        
        "scheduling_prompt": """Que ótimo! Fico feliz com seu interesse!

Para apresentar a melhor solução para você, um de nossos consultores especializados pode fazer uma análise personalizada sem compromisso.

Quando seria melhor para você:
Amanhã às 10h ou 14h ou Quinta-feira às 9h ou 16h?

Ou prefere sugerir outro horário?"""
    })
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignora campos extras do .env

# Instância global de configuração
config = SDRConfig()

# Função helper para obter configuração
def get_config() -> SDRConfig:
    """Retorna a configuração do SDR"""
    return config

# Validação de configuração na inicialização
def validate_config():
    """Valida se todas as configurações necessárias estão presentes"""
    errors = []
    
    if not config.gemini.api_key:
        errors.append("GEMINI_API_KEY não configurada")
    
    if errors:
        raise ValueError(f"Erros de configuração: {', '.join(errors)}")

# Exporta componentes principais
__all__ = [
    "SDRConfig",
    "GeminiConfig", 
    "AgentPersonality",
    "SalesStages",
    "SolarSolutions",
    "ConversationRules",
    "MemoryConfig",
    "config",
    "get_config",
    "validate_config"
]