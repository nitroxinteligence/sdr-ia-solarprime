# 02. Desenvolvimento do Agente IA - AGnO Framework + Gemini 2.5 Pro

Este documento detalha a implementação do agente de IA usando AGnO Framework com Google Gemini 2.5 Pro como modelo de linguagem.

## 📋 Índice

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Configuração do AGnO Framework](#2-configuração-do-agno-framework)
3. [Integração com Gemini 2.5 Pro](#3-integração-com-gemini-25-pro)
4. [Estrutura do Agente](#4-estrutura-do-agente)
5. [Sistema de Prompts](#5-sistema-de-prompts)
6. [Ferramentas Customizadas](#6-ferramentas-customizadas)
7. [Memória e Contexto](#7-memória-e-contexto)
8. [Fluxo de Qualificação](#8-fluxo-de-qualificação)
9. [Testes e Validação](#9-testes-e-validação)
10. [Otimizações e Performance](#10-otimizações-e-performance)

---

## 1. Visão Geral da Arquitetura

### 1.1 Componentes Principais

```
┌─────────────────────────────────────────────────────┐
│                  AGENTE PRINCIPAL                   │
│  ┌─────────────────────────────────────────────┐  │
│  │           Google Gemini 2.5 Pro              │  │
│  │         (Reasoning & Conversation)           │  │
│  └─────────────────────────────────────────────┘  │
│                         │                           │
│  ┌─────────────────────────────────────────────┐  │
│  │              AGnO Framework                  │  │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────────┐ │  │
│  │  │  Tools   │ │  Memory  │ │  Knowledge  │ │  │
│  │  └─────────┘ └──────────┘ └─────────────┘ │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 1.2 Fluxo de Processamento

1. **Recepção**: Mensagem chega via webhook
2. **Processamento**: AGnO processa com contexto
3. **Raciocínio**: Gemini 2.5 Pro analisa e decide
4. **Ação**: Executa ferramentas necessárias
5. **Resposta**: Gera resposta contextualizada

---

## 2. Configuração do AGnO Framework

### 2.1 Instalação e Setup Inicial

```bash
# Ativar ambiente virtual
cd ~/sdr-solarprime
source venv/bin/activate

# Instalar AGnO e dependências
pip install agno google-generativeai

# Verificar instalação
python -c "import agno; print(f'AGnO version: {agno.__version__}')"
```

### 2.2 Estrutura Base do Projeto

```bash
# Criar estrutura de agentes
mkdir -p agents/{tools,knowledge,prompts}
touch agents/__init__.py
touch agents/sales_agent.py
touch agents/tools/__init__.py
touch agents/knowledge/__init__.py
```

---

## 3. Integração com Gemini 2.5 Pro

### 3.1 Configuração do Cliente Gemini

```python
# config/gemini_config.py
from typing import Optional
from pydantic_settings import BaseSettings
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class GeminiConfig(BaseSettings):
    """Configurações do Google Gemini para produção"""
    api_key: str
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    top_k: int = 40
    timeout: int = 30  # Timeout em segundos
    retry_attempts: int = 3  # Tentativas em caso de erro
    
    class Config:
        env_prefix = "GEMINI_"
        case_sensitive = False

def setup_gemini(config: GeminiConfig) -> genai.GenerativeModel:
    """Configura e retorna o modelo Gemini para produção"""
    try:
        genai.configure(api_key=config.api_key)
        
        generation_config = {
            "temperature": config.temperature,
            "top_p": config.top_p,
            "top_k": config.top_k,
            "max_output_tokens": config.max_tokens,
            "candidate_count": 1,  # Apenas uma resposta
            "stop_sequences": []   # Sem sequências de parada customizadas
        }
        
        # Configurações de segurança para produção (conversacional)
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
        
        model = genai.GenerativeModel(
            model_name=config.model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        logger.info(f"Modelo Gemini {config.model_name} configurado com sucesso")
        return model
        
    except Exception as e:
        logger.error(f"Erro ao configurar Gemini: {e}")
        raise
```

### 3.2 Adapter para AGnO

```python
# agents/models/gemini_adapter.py
from agno.models.base import Model
from typing import Iterator, List, Dict, Any, Optional
import google.generativeai as genai

class GeminiModel(Model):
    """Adapter do Gemini para AGnO Framework"""
    
    def __init__(
        self,
        id: str = "gemini-2.5-pro",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        super().__init__(name=id)
        self.model_id = id
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Configurar Gemini
        if api_key:
            genai.configure(api_key=api_key)
        
        self.client = genai.GenerativeModel(
            model_name=id,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40),
            }
        )
        
        # Iniciar chat session
        self.chat_session = self.client.start_chat(history=[])
    
    def invoke(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Invoca o modelo com mensagens"""
        # Converter mensagens para formato Gemini
        prompt = self._format_messages(messages)
        
        # Gerar resposta
        response = self.chat_session.send_message(prompt)
        
        return {
            "content": response.text,
            "role": "assistant",
            "model": self.model_id
        }
    
    def stream(self, messages: List[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """Stream de respostas do modelo"""
        prompt = self._format_messages(messages)
        
        response_stream = self.chat_session.send_message(
            prompt,
            stream=True
        )
        
        for chunk in response_stream:
            if chunk.text:
                yield {
                    "content": chunk.text,
                    "role": "assistant",
                    "model": self.model_id
                }
    
    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Formata mensagens para o Gemini"""
        formatted = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted.append(f"Sistema: {content}")
            elif role == "user":
                formatted.append(f"Usuário: {content}")
            elif role == "assistant":
                formatted.append(f"Assistente: {content}")
        
        return "\n\n".join(formatted)
```

---

## 4. Estrutura do Agente

### 4.1 Agente Principal de Vendas

```python
# agents/sales_agent.py
from agno.agent import Agent
from agno.tools import Toolkit
from agno.storage import SqlAgentStorage
from agno.memory import AgentMemory
from agno.knowledge import AgentKnowledge
from typing import Optional, Dict, Any, List
import logging

from agents.models.gemini_adapter import GeminiModel
from agents.tools.lead_tools import LeadTools
from agents.tools.crm_tools import CRMTools
from agents.tools.qualification_tools import QualificationTools
from agents.prompts.sales_prompts import SYSTEM_PROMPT, get_stage_prompt

logger = logging.getLogger(__name__)

class SolarPrimeSalesAgent:
    """Agente de vendas SDR para SolarPrime"""
    
    def __init__(
        self,
        gemini_api_key: str,
        supabase_url: str,
        supabase_key: str,
        redis_url: str,
        kommo_config: Dict[str, str]
    ):
        # Configurar modelo
        self.model = GeminiModel(
            id="gemini-2.5-pro",
            api_key=gemini_api_key,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Configurar storage
        self.storage = SqlAgentStorage(
            table_name="agent_sessions",
            db_url=f"{supabase_url}/rest/v1",
            db_api_key=supabase_key
        )
        
        # Configurar ferramentas
        self.tools = [
            LeadTools(supabase_url, supabase_key),
            CRMTools(kommo_config),
            QualificationTools()
        ]
        
        # Criar agente
        self.agent = Agent(
            name="Leonardo - Consultor SolarPrime",
            role="Consultor de vendas especializado em energia solar",
            model=self.model,
            tools=self.tools,
            storage=self.storage,
            description="Sou o Leonardo, consultor da SolarPrime. Ajudo pessoas a economizarem na conta de luz com energia solar.",
            instructions=[
                SYSTEM_PROMPT,
                "Sempre mantenha um tom consultivo e profissional",
                "Use emojis apropriados para WhatsApp",
                "Seja proativo em coletar informações de qualificação",
                "Sempre busque agendar uma reunião quando o lead estiver qualificado"
            ],
            markdown=False,  # WhatsApp não suporta markdown
            show_tool_calls=False,
            add_datetime_to_instructions=True,
            memory=AgentMemory(
                db_url=f"{supabase_url}/rest/v1",
                db_api_key=supabase_key
            ),
            # Configurações de reasoning
            reasoning=True,  # Ativa reasoning do Gemini 2.5
            reasoning_steps=5,
            show_reasoning=False  # Não mostrar reasoning para o usuário
        )
        
        self.qualification_stage = {}  # Rastrear estágio por conversa
    
    async def process_message(
        self,
        message: str,
        sender_id: str,
        sender_name: Optional[str] = None,
        message_type: str = "text",
        media_url: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Processa mensagem recebida e retorna resposta"""
        
        # Criar ou recuperar sessão
        if not session_id:
            session_id = f"whatsapp_{sender_id}"
        
        # Determinar estágio atual da qualificação
        current_stage = self.qualification_stage.get(session_id, 0)
        
        # Adicionar contexto do estágio ao prompt
        stage_context = get_stage_prompt(current_stage)
        
        # Processar diferentes tipos de mensagem
        if message_type == "image" and media_url:
            message = f"[Usuário enviou uma imagem: {media_url}]\n{message}"
        elif message_type == "audio" and message:
            message = f"[Transcrição de áudio]: {message}"
        elif message_type == "document" and media_url:
            message = f"[Usuário enviou um documento: {media_url}]\n{message}"
        
        # Adicionar contexto do usuário
        user_context = f"Nome: {sender_name or 'Não identificado'}\nID: {sender_id}"
        
        # Montar prompt completo
        full_prompt = f"{stage_context}\n\n{user_context}\n\nMensagem: {message}"
        
        try:
            # Processar com o agente
            response = await self.agent.arun(
                full_prompt,
                session_id=session_id,
                stream=False
            )
            
            # Atualizar estágio se necessário
            self._update_qualification_stage(session_id, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return "Desculpe, tive um problema técnico. Pode repetir sua mensagem? 🤔"
    
    def _update_qualification_stage(self, session_id: str, response: str):
        """Atualiza o estágio de qualificação baseado na resposta"""
        current_stage = self.qualification_stage.get(session_id, 0)
        
        # Lógica simples de progressão
        # Em produção, isso seria mais sofisticado
        stage_keywords = {
            0: ["nome", "chamo", "sou"],
            1: ["usina", "desconto", "energia"],
            2: ["conta", "valor", "reais"],
            3: ["desconto", "empresa", "concorrente"],
            4: ["reunião", "agendar", "horário"]
        }
        
        # Verificar se deve avançar de estágio
        if current_stage < 4:
            keywords = stage_keywords.get(current_stage + 1, [])
            if any(keyword in response.lower() for keyword in keywords):
                self.qualification_stage[session_id] = current_stage + 1
                logger.info(f"Sessão {session_id} avançou para estágio {current_stage + 1}")
```

---

## 5. Sistema de Prompts

### 5.1 Prompts Base do Sistema

```python
# agents/prompts/sales_prompts.py
from typing import Dict, List

SYSTEM_PROMPT = """Você é o Leonardo, consultor de vendas da SolarPrime em Boa Viagem, Pernambuco.

CONTEXTO:
- Empresa: SolarPrime - Líder em energia solar no Nordeste
- Sua função: Qualificar leads e agendar reuniões para apresentar soluções de energia solar
- Tom: Consultivo, profissional mas amigável, use emojis apropriados
- Objetivo: Coletar informações de qualificação e agendar reunião

INFORMAÇÕES DA EMPRESA:
- Oferecemos 5 soluções principais de energia solar
- Economia mínima garantida de 20% na conta de luz
- Zero investimento inicial para o cliente
- Usina fica com o cliente após o contrato
- Atendemos residências e empresas

REGRAS IMPORTANTES:
1. SEMPRE seja proativo em fazer perguntas de qualificação
2. NUNCA mencione preços específicos - apenas agende reunião
3. Se o lead mencionar concorrentes (Origo, Setta), destaque nossos diferenciais
4. Use linguagem simples e evite termos técnicos
5. Sempre tente agendar uma reunião quando o lead estiver qualificado

PROCESSO DE QUALIFICAÇÃO:
1. Identificar o nome do lead
2. Entender qual solução ele busca
3. Descobrir valor da conta de luz
4. Verificar se já tem desconto com concorrentes
5. Agendar reunião

Lembre-se: Você está no WhatsApp. Mantenha mensagens curtas e conversacionais."""

def get_stage_prompt(stage: int) -> str:
    """Retorna prompt específico para cada estágio"""
    stage_prompts = {
        0: """ESTÁGIO: Identificação
OBJETIVO: Descobrir o nome do lead
AÇÃO: Cumprimente calorosamente e pergunte o nome
EXEMPLO: 'Olá! 👋 Seja muito bem-vindo(a) à SolarPrime! Eu sou o Leonardo, seu consultor de energia solar. 
Antes de começarmos, qual é o seu nome?'""",

        1: """ESTÁGIO: Descoberta de Solução
OBJETIVO: Entender qual solução o lead busca
AÇÃO: Pergunte sobre o interesse (usina própria ou desconto)
EXEMPLO: 'Prazer, [NOME]! 😊 Você está buscando instalar uma usina solar ou prefere apenas ter desconto na sua conta de luz sem investimento?'""",

        2: """ESTÁGIO: Valor da Conta
OBJETIVO: Descobrir o valor médio da conta de luz
AÇÃO: Pergunte o valor ou peça foto da conta
EXEMPLO: '[NOME], para eu preparar a melhor proposta para você, qual o valor médio da sua conta de luz? 
Se preferir, pode enviar uma foto da conta que eu analiso para você! 📱'""",

        3: """ESTÁGIO: Análise Competitiva
OBJETIVO: Verificar se já tem desconto/concorrentes
AÇÃO: Pergunte sobre descontos atuais
EXEMPLO: 'Entendi! Você já possui algum desconto na sua conta de luz? 
Se sim, qual a porcentagem e com qual empresa?'""",

        4: """ESTÁGIO: Agendamento
OBJETIVO: Agendar reunião presencial ou online
AÇÃO: Ofereça opções de horário para reunião
EXEMPLO: 'Excelente, [NOME]! Tenho uma proposta personalizada que vai te surpreender! 💡
Vamos agendar uma reunião rápida para eu te mostrar exatamente quanto você vai economizar?
Pode ser presencial aqui em Boa Viagem ou online. Qual você prefere?'"""
    }
    
    return stage_prompts.get(stage, stage_prompts[0])

# Respostas para objeções comuns
OBJECTION_HANDLERS = {
    "caro": "Entendo sua preocupação! 😊 A grande vantagem é que você começa a economizar desde o primeiro mês SEM investir nada. Vamos agendar uma conversa rápida para eu te mostrar os números?",
    
    "não tenho interesse": "Sem problemas! Mas deixa eu te fazer uma pergunta rápida: se você pudesse economizar 20% ou mais na sua conta de luz sem investir nada, valeria a pena conhecer? 🤔",
    
    "já tenho desconto": "Que ótimo que você já economiza! 👏 Mas sabia que podemos analisar se conseguimos um desconto ainda maior? Muitos clientes que já tinham desconto conseguiram economizar ainda mais conosco. Vale a pena comparar!",
    
    "origo": "Conheço bem a Origo! Eles são uma boa empresa. Nossa vantagem é que além do desconto, a usina fica com você no final do contrato. Vamos comparar as propostas? 📊",
    
    "setta": "A Setta também trabalha com energia solar! Nossa diferença é o atendimento personalizado e a garantia de economia mínima de 20%. Que tal conhecer nossa proposta? 🌟"
}
```

### 5.2 Templates de Mensagens

```python
# agents/prompts/message_templates.py
from typing import Dict, List
from datetime import datetime, timedelta

class MessageTemplates:
    """Templates de mensagens para diferentes situações"""
    
    @staticmethod
    def welcome_message(time_of_day: str) -> str:
        """Mensagem de boas-vindas baseada no horário"""
        greetings = {
            "morning": "Bom dia",
            "afternoon": "Boa tarde", 
            "evening": "Boa noite"
        }
        greeting = greetings.get(time_of_day, "Olá")
        
        return f"{greeting}! ☀️ Bem-vindo(a) à SolarPrime, líder em energia solar no Nordeste! Eu sou o Leonardo, seu consultor. Como posso ajudar você a economizar na conta de luz hoje?"
    
    @staticmethod
    def reengagement_message(last_stage: int, lead_name: str = "") -> str:
        """Mensagem de reengajamento baseada no último estágio"""
        name = lead_name if lead_name else "amigo(a)"
        
        messages = {
            0: f"Oi! 👋 Vi que você demonstrou interesse em energia solar. Ainda posso ajudar?",
            1: f"Olá, {name}! Você estava me contando sobre seu interesse em energia solar. Vamos continuar? 😊",
            2: f"Oi, {name}! Ficamos na parte do valor da sua conta de luz. Pode me informar para preparar sua proposta? 📊",
            3: f"{name}, estava preparando sua análise de economia! Você já tem algum desconto na conta de luz atualmente?",
            4: f"{name}, tenho ótimas notícias sobre sua economia! Vamos agendar nossa reunião? 📅"
        }
        
        return messages.get(last_stage, messages[0])
    
    @staticmethod
    def appointment_confirmation(date: datetime, is_online: bool = False) -> str:
        """Mensagem de confirmação de agendamento"""
        location = "online via Google Meet" if is_online else "presencial em nosso escritório em Boa Viagem"
        
        return f"""✅ Reunião agendada com sucesso!

📅 Data: {date.strftime('%d/%m/%Y')}
🕐 Horário: {date.strftime('%H:%M')}
📍 Local: {location}

Vou te enviar um lembrete no dia! Até lá, já vou preparando sua proposta personalizada de economia! 💡"""
    
    @staticmethod
    def followup_messages() -> Dict[str, str]:
        """Mensagens de follow-up por tipo"""
        return {
            "no_response_30min": "Oi! 👋 Vi que você começou a conversar sobre energia solar. Ainda está aí? Adoraria ajudar você a economizar! 💡",
            
            "no_response_24h": "Olá! ☀️ Ontem você demonstrou interesse em economizar na conta de luz. Que tal continuarmos? Tenho uma proposta especial para você!",
            
            "appointment_reminder": "Oi, {name}! 😊 Passando para confirmar nossa reunião amanhã às {time}. Você confirma presença? 
Já preparei uma análise completa da sua economia!",
            
            "missed_appointment": "Olá, {name}! Tentei contato para nossa reunião mas não consegui falar com você. 
Vamos reagendar? Tenho alguns horários disponíveis hoje e amanhã! 📅",
            
            "post_meeting": "Oi, {name}! Foi ótimo conversar com você! 🤝 
Como combinamos, aqui está o resumo da nossa proposta:
✅ Economia mínima de 20%
✅ Zero investimento inicial  
✅ Usina fica com você no final

Quando podemos fechar? 🌟"
        }
    
    @staticmethod
    def value_propositions() -> List[str]:
        """Propostas de valor para usar nas conversas"""
        return [
            "💰 Economia garantida mínima de 20% na conta de luz",
            "🏠 A usina solar fica com você no final do contrato", 
            "💸 Zero investimento inicial - você começa a economizar imediatamente",
            "🛡️ Proteção contra aumentos de tarifa e bandeiras tarifárias",
            "🌱 Energia limpa e sustentável para sua casa ou empresa",
            "📊 Acompanhamento mensal da sua economia em tempo real",
            "🔧 Manutenção completa inclusa durante todo o contrato",
            "⚡ Instalação rápida e sem transtornos"
        ]
```

---

## 6. Ferramentas Customizadas

### 6.1 Ferramentas de Lead

```python
# agents/tools/lead_tools.py
from agno.tools import Toolkit
from typing import Optional, Dict, Any
import httpx
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LeadTools(Toolkit):
    """Ferramentas para gerenciar leads"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        super().__init__(name="lead_tools")
        self.supabase_url = supabase_url
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Registrar ferramentas
        self.register(self.create_lead)
        self.register(self.update_lead)
        self.register(self.get_lead_info)
        self.register(self.calculate_savings)
    
    def create_lead(self, name: str, phone: str, source: str = "whatsapp") -> Dict[str, Any]:
        """Cria um novo lead no sistema
        
        Args:
            name: Nome completo do lead
            phone: Número de telefone
            source: Fonte do lead (padrão: whatsapp)
            
        Returns:
            Dados do lead criado
        """
        lead_data = {
            "name": name,
            "phone": phone,
            "source": source,
            "status": "novo",
            "created_at": datetime.utcnow().isoformat(),
            "qualification_stage": 0
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.supabase_url}/rest/v1/leads",
                    json=lead_data,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()[0]
        except Exception as e:
            logger.error(f"Erro ao criar lead: {e}")
            return {"error": str(e)}
    
    def update_lead(
        self, 
        lead_id: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Atualiza informações do lead
        
        Args:
            lead_id: ID do lead
            **kwargs: Campos a atualizar (stage, bill_value, has_discount, etc)
            
        Returns:
            Lead atualizado
        """
        update_data = {
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        try:
            with httpx.Client() as client:
                response = client.patch(
                    f"{self.supabase_url}/rest/v1/leads?id=eq.{lead_id}",
                    json=update_data,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()[0]
        except Exception as e:
            logger.error(f"Erro ao atualizar lead: {e}")
            return {"error": str(e)}
    
    def get_lead_info(self, phone: str) -> Optional[Dict[str, Any]]:
        """Busca informações de um lead pelo telefone
        
        Args:
            phone: Número de telefone
            
        Returns:
            Dados do lead ou None
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.supabase_url}/rest/v1/leads?phone=eq.{phone}",
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"Erro ao buscar lead: {e}")
            return None
    
    def calculate_savings(
        self, 
        bill_value: float, 
        discount_percentage: float = 20.0
    ) -> Dict[str, float]:
        """Calcula economia estimada
        
        Args:
            bill_value: Valor atual da conta
            discount_percentage: Percentual de desconto
            
        Returns:
            Cálculos de economia
        """
        monthly_savings = bill_value * (discount_percentage / 100)
        annual_savings = monthly_savings * 12
        
        return {
            "monthly_bill": bill_value,
            "discount_percentage": discount_percentage,
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(annual_savings, 2),
            "new_monthly_bill": round(bill_value - monthly_savings, 2)
        }
```

### 6.2 Ferramentas de CRM

```python
# agents/tools/crm_tools.py
from agno.tools import Toolkit
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
import logging
from kommo.client import Client as KommoClient

logger = logging.getLogger(__name__)

class CRMTools(Toolkit):
    """Ferramentas para integração com Kommo CRM"""
    
    def __init__(self, kommo_config: Dict[str, str]):
        super().__init__(name="crm_tools")
        
        # Configurar cliente Kommo
        self.kommo_client = KommoClient(
            client_id=kommo_config["client_id"],
            client_secret=kommo_config["client_secret"],
            code=kommo_config.get("code"),
            domain=kommo_config["subdomain"],
            redirect_uri=kommo_config["redirect_uri"]
        )
        
        # IDs dos pipelines e estágios
        self.pipeline_id = kommo_config.get("pipeline_id", 1234567)
        self.stages = {
            "novo": 123456,
            "qualificando": 123457,
            "qualificado": 123458,
            "reuniao_agendada": 123459,
            "reuniao_confirmada": 123460
        }
        
        # Registrar ferramentas
        self.register(self.create_crm_lead)
        self.register(self.update_crm_stage)
        self.register(self.schedule_meeting)
        self.register(self.get_available_slots)
    
    def create_crm_lead(
        self, 
        name: str, 
        phone: str,
        email: Optional[str] = None,
        bill_value: Optional[float] = None,
        source: str = "WhatsApp"
    ) -> Dict[str, Any]:
        """Cria lead no Kommo CRM
        
        Args:
            name: Nome do lead
            phone: Telefone
            email: Email opcional
            bill_value: Valor da conta
            source: Fonte do lead
            
        Returns:
            Lead criado no CRM
        """
        try:
            lead_data = {
                "name": f"{name} - WhatsApp",
                "pipeline_id": self.pipeline_id,
                "status_id": self.stages["novo"],
                "custom_fields_values": [
                    {
                        "field_id": 123123,  # Campo telefone
                        "values": [{"value": phone}]
                    },
                    {
                        "field_id": 123124,  # Campo fonte
                        "values": [{"value": source}]
                    }
                ]
            }
            
            if email:
                lead_data["custom_fields_values"].append({
                    "field_id": 123125,
                    "values": [{"value": email}]
                })
            
            if bill_value:
                lead_data["price"] = int(bill_value)
            
            # Criar lead
            response = self.kommo_client.create_lead(lead_data)
            
            logger.info(f"Lead criado no CRM: {response.get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao criar lead no CRM: {e}")
            return {"error": str(e)}
    
    def update_crm_stage(
        self, 
        lead_id: int, 
        stage: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atualiza estágio do lead no funil
        
        Args:
            lead_id: ID do lead no CRM
            stage: Nome do estágio
            notes: Notas adicionais
            
        Returns:
            Lead atualizado
        """
        try:
            stage_id = self.stages.get(stage)
            if not stage_id:
                return {"error": f"Estágio inválido: {stage}"}
            
            update_data = {
                "status_id": stage_id,
                "updated_at": int(datetime.now().timestamp())
            }
            
            response = self.kommo_client.update_lead(lead_id, update_data)
            
            # Adicionar nota se fornecida
            if notes:
                self.kommo_client.create_note(
                    entity_type="leads",
                    entity_id=lead_id,
                    note_type="common",
                    text=notes
                )
            
            logger.info(f"Lead {lead_id} movido para estágio {stage}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estágio: {e}")
            return {"error": str(e)}
    
    def get_available_slots(
        self, 
        days_ahead: int = 7,
        duration_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """Busca horários disponíveis para reunião
        
        Args:
            days_ahead: Dias à frente para buscar
            duration_minutes: Duração da reunião
            
        Returns:
            Lista de slots disponíveis
        """
        # Em produção, isso consultaria o calendário real
        # Por ora, retorna slots fictícios
        slots = []
        current_date = datetime.now()
        
        for days in range(1, days_ahead + 1):
            date = current_date + timedelta(days=days)
            
            # Pular finais de semana
            if date.weekday() in [5, 6]:
                continue
            
            # Horários disponíveis (9h às 18h)
            for hour in [9, 10, 11, 14, 15, 16, 17]:
                slot_time = date.replace(hour=hour, minute=0, second=0)
                
                slots.append({
                    "datetime": slot_time.isoformat(),
                    "date": slot_time.strftime("%d/%m/%Y"),
                    "time": slot_time.strftime("%H:%M"),
                    "duration": duration_minutes,
                    "available": True
                })
        
        return slots[:10]  # Retornar apenas 10 opções
    
    def schedule_meeting(
        self,
        lead_id: int,
        scheduled_datetime: datetime,
        duration_minutes: int = 30,
        is_online: bool = False,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Agenda reunião com o lead
        
        Args:
            lead_id: ID do lead no CRM
            scheduled_datetime: Data e hora da reunião
            duration_minutes: Duração
            is_online: Se é online ou presencial
            notes: Observações
            
        Returns:
            Dados da reunião agendada
        """
        try:
            # Criar tarefa no CRM
            task_data = {
                "text": f"Reunião com lead - {'Online' if is_online else 'Presencial'}",
                "complete_till": int(scheduled_datetime.timestamp()),
                "task_type_id": 1,  # Tipo: Reunião
                "entity_type": "leads",
                "entity_id": lead_id
            }
            
            response = self.kommo_client.create_task(task_data)
            
            # Atualizar lead para estágio "reunião agendada"
            self.update_crm_stage(lead_id, "reuniao_agendada", notes)
            
            # Adicionar nota com detalhes
            meeting_notes = f"""
Reunião agendada:
📅 Data: {scheduled_datetime.strftime('%d/%m/%Y')}
🕐 Horário: {scheduled_datetime.strftime('%H:%M')}
⏱️ Duração: {duration_minutes} minutos
📍 Local: {'Online (Google Meet)' if is_online else 'Presencial - Escritório Boa Viagem'}
"""
            
            self.kommo_client.create_note(
                entity_type="leads",
                entity_id=lead_id,
                note_type="common",
                text=meeting_notes
            )
            
            logger.info(f"Reunião agendada para lead {lead_id}")
            return {
                "task_id": response.get("id"),
                "scheduled_at": scheduled_datetime.isoformat(),
                "status": "scheduled"
            }
            
        except Exception as e:
            logger.error(f"Erro ao agendar reunião: {e}")
            return {"error": str(e)}
```

### 6.3 Ferramentas de Qualificação

```python
# agents/tools/qualification_tools.py
from agno.tools import Toolkit
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QualificationTools(Toolkit):
    """Ferramentas para qualificação de leads"""
    
    def __init__(self):
        super().__init__(name="qualification_tools")
        
        # Critérios de qualificação
        self.qualification_criteria = {
            "min_bill_value": 200.0,  # Valor mínimo da conta
            "max_discount_competitor": 15.0,  # Desconto máximo com concorrente
            "preferred_solutions": ["usina_propria", "desconto_premium"],
            "hot_lead_bill": 1000.0  # Valor para lead quente
        }
        
        # Registrar ferramentas
        self.register(self.extract_name)
        self.register(self.extract_phone)
        self.register(self.extract_bill_value)
        self.register(self.identify_solution)
        self.register(self.calculate_lead_score)
        self.register(self.check_qualification)
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extrai nome do texto
        
        Args:
            text: Texto da mensagem
            
        Returns:
            Nome extraído ou None
        """
        # Padrões comuns
        patterns = [
            r"(?:me chamo|meu nome é|sou o?a?)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)",
            r"(?:é|sou)\s+([A-Z][a-zA-Z]+)",
            r"^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Validar nome (pelo menos 2 caracteres)
                if len(name) >= 2:
                    return name.title()
        
        return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extrai número de telefone
        
        Args:
            text: Texto da mensagem
            
        Returns:
            Telefone formatado ou None
        """
        # Remover caracteres não numéricos
        numbers = re.sub(r'[^\d]', '', text)
        
        # Padrões brasileiros
        patterns = [
            r'(\d{2})(\d{5})(\d{4})',  # 11 dígitos
            r'(\d{2})(\d{4})(\d{4})',   # 10 dígitos
        ]
        
        for pattern in patterns:
            match = re.match(pattern, numbers)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    return f"({groups[0]}) {groups[1]}-{groups[2]}"
        
        return None
    
    def extract_bill_value(self, text: str) -> Optional[float]:
        """Extrai valor da conta de luz
        
        Args:
            text: Texto da mensagem
            
        Returns:
            Valor extraído ou None
        """
        # Padrões de valor em reais
        patterns = [
            r'R\$?\s*(\d{1,}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            r'(\d{1,}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*reais',
            r'(\d{1,}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:por mês|mensal)',
            r'(?:pago|conta|valor)\s*(?:de|é)?\s*(\d{1,}(?:[.,]\d{3})*(?:[.,]\d{2})?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                # Normalizar separadores
                value_str = value_str.replace('.', '').replace(',', '.')
                
                try:
                    value = float(value_str)
                    # Validar range razoável
                    if 50.0 <= value <= 50000.0:
                        return value
                except ValueError:
                    continue
        
        return None
    
    def identify_solution(self, text: str) -> Dict[str, Any]:
        """Identifica solução desejada pelo lead
        
        Args:
            text: Texto da mensagem
            
        Returns:
            Solução identificada e confiança
        """
        solutions = {
            "usina_propria": {
                "keywords": ["usina", "instalar", "telhado", "casa", "propriedade", "minha casa"],
                "description": "Usina solar em propriedade própria"
            },
            "usina_parceira": {
                "keywords": ["terreno", "parceiro", "fazenda", "aluguel"],
                "description": "Usina em terreno parceiro"
            },
            "desconto_premium": {
                "keywords": ["desconto", "conta acima", "4000", "4 mil", "empresa"],
                "description": "Desconto para contas acima de R$ 4.000"
            },
            "desconto_standard": {
                "keywords": ["desconto", "economizar", "reduzir conta"],
                "description": "Desconto para contas abaixo de R$ 4.000"
            },
            "investimento": {
                "keywords": ["investir", "investimento", "retorno", "lucro"],
                "description": "Usina como investimento"
            }
        }
        
        text_lower = text.lower()
        matches = []
        
        for solution_id, solution_data in solutions.items():
            keywords = solution_data["keywords"]
            match_count = sum(1 for kw in keywords if kw in text_lower)
            
            if match_count > 0:
                confidence = min(match_count / len(keywords), 1.0)
                matches.append({
                    "solution_id": solution_id,
                    "description": solution_data["description"],
                    "confidence": confidence,
                    "matched_keywords": match_count
                })
        
        # Ordenar por confiança
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        if matches:
            return matches[0]
        else:
            return {
                "solution_id": "unknown",
                "description": "Solução não identificada",
                "confidence": 0.0
            }
    
    def calculate_lead_score(
        self,
        name: Optional[str] = None,
        bill_value: Optional[float] = None,
        solution: Optional[str] = None,
        has_competitor: bool = False,
        competitor_discount: Optional[float] = None,
        engagement_level: str = "medium"
    ) -> Dict[str, Any]:
        """Calcula score de qualificação do lead
        
        Args:
            name: Nome do lead
            bill_value: Valor da conta
            solution: Solução identificada
            has_competitor: Se tem concorrente
            competitor_discount: Desconto do concorrente
            engagement_level: Nível de engajamento
            
        Returns:
            Score e classificação
        """
        score = 0
        factors = []
        
        # Fator: Nome identificado (10 pontos)
        if name:
            score += 10
            factors.append("Nome identificado (+10)")
        
        # Fator: Valor da conta (até 40 pontos)
        if bill_value:
            if bill_value >= self.qualification_criteria["hot_lead_bill"]:
                score += 40
                factors.append(f"Conta alta: R$ {bill_value:.2f} (+40)")
            elif bill_value >= self.qualification_criteria["min_bill_value"]:
                points = int(20 + (bill_value / 100))
                score += points
                factors.append(f"Conta média: R$ {bill_value:.2f} (+{points})")
            else:
                score += 5
                factors.append(f"Conta baixa: R$ {bill_value:.2f} (+5)")
        
        # Fator: Solução preferida (até 20 pontos)
        if solution in self.qualification_criteria["preferred_solutions"]:
            score += 20
            factors.append(f"Solução preferida: {solution} (+20)")
        elif solution and solution != "unknown":
            score += 10
            factors.append(f"Solução identificada: {solution} (+10)")
        
        # Fator: Concorrência (até 20 pontos)
        if has_competitor:
            if competitor_discount and competitor_discount < self.qualification_criteria["max_discount_competitor"]:
                score += 20
                factors.append(f"Oportunidade vs concorrente (+20)")
            else:
                score += 10
                factors.append("Tem concorrente mas podemos competir (+10)")
        else:
            score += 15
            factors.append("Sem concorrente (+15)")
        
        # Fator: Engajamento (até 10 pontos)
        engagement_scores = {
            "high": 10,
            "medium": 5,
            "low": 2
        }
        eng_score = engagement_scores.get(engagement_level, 5)
        score += eng_score
        factors.append(f"Engajamento {engagement_level} (+{eng_score})")
        
        # Classificação
        if score >= 80:
            classification = "HOT 🔥"
        elif score >= 60:
            classification = "WARM 🌟"
        elif score >= 40:
            classification = "COOL ❄️"
        else:
            classification = "COLD 🧊"
        
        return {
            "score": score,
            "max_score": 100,
            "classification": classification,
            "factors": factors,
            "recommendation": self._get_recommendation(score, classification)
        }
    
    def _get_recommendation(self, score: int, classification: str) -> str:
        """Gera recomendação baseada no score"""
        if classification == "HOT 🔥":
            return "Agendar reunião IMEDIATAMENTE! Lead altamente qualificado."
        elif classification == "WARM 🌟":
            return "Continuar qualificação e agendar reunião em breve."
        elif classification == "COOL ❄️":
            return "Nutrir lead com mais informações antes de agendar."
        else:
            return "Qualificar melhor ou considerar para campanhas futuras."
    
    def check_qualification(
        self,
        lead_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Verifica se lead está qualificado para agendamento
        
        Args:
            lead_data: Dados do lead
            
        Returns:
            (está_qualificado, campos_faltantes)
        """
        required_fields = ["name", "phone", "bill_value", "solution"]
        missing_fields = []
        
        for field in required_fields:
            if not lead_data.get(field):
                missing_fields.append(field)
        
        # Verificar valor mínimo
        bill_value = lead_data.get("bill_value", 0)
        if bill_value < self.qualification_criteria["min_bill_value"]:
            missing_fields.append("bill_value_minimum")
        
        is_qualified = len(missing_fields) == 0
        
        return is_qualified, missing_fields
```

---

## 7. Memória e Contexto

### 7.1 Sistema de Memória Persistente

```python
# agents/memory/conversation_memory.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Sistema de memória para conversas"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.client: Client = create_client(supabase_url, supabase_key)
        self.conversations_table = "conversations"
        self.messages_table = "messages"
    
    async def save_message(
        self,
        session_id: str,
        sender_id: str,
        message: str,
        message_type: str = "text",
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Salva mensagem no histórico
        
        Args:
            session_id: ID da sessão
            sender_id: ID do remetente
            message: Conteúdo da mensagem
            message_type: Tipo (text, image, audio, etc)
            role: Papel (user, assistant)
            metadata: Metadados adicionais
            
        Returns:
            Mensagem salva
        """
        message_data = {
            "session_id": session_id,
            "sender_id": sender_id,
            "content": message,
            "type": message_type,
            "role": role,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            response = self.client.table(self.messages_table).insert(message_data).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            return {}
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50,
        include_system: bool = False
    ) -> List[Dict[str, Any]]:
        """Recupera histórico da conversa
        
        Args:
            session_id: ID da sessão
            limit: Limite de mensagens
            include_system: Incluir mensagens do sistema
            
        Returns:
            Lista de mensagens
        """
        try:
            query = self.client.table(self.messages_table)\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .limit(limit)
            
            if not include_system:
                query = query.in_("role", ["user", "assistant"])
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            return []
    
    async def get_conversation_summary(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Gera resumo da conversa
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Resumo com dados principais
        """
        try:
            # Buscar conversa
            conv_response = self.client.table(self.conversations_table)\
                .select("*")\
                .eq("session_id", session_id)\
                .single()\
                .execute()
            
            if not conv_response.data:
                return {}
            
            conversation = conv_response.data
            
            # Buscar estatísticas
            messages = await self.get_conversation_history(session_id)
            
            summary = {
                "session_id": session_id,
                "lead_name": conversation.get("lead_name"),
                "lead_phone": conversation.get("lead_phone"),
                "started_at": conversation.get("created_at"),
                "last_message_at": messages[-1]["created_at"] if messages else None,
                "total_messages": len(messages),
                "qualification_stage": conversation.get("qualification_stage", 0),
                "lead_score": conversation.get("lead_score", 0),
                "solution_identified": conversation.get("solution_type"),
                "bill_value": conversation.get("bill_value"),
                "has_competitor": conversation.get("has_competitor", False),
                "is_qualified": conversation.get("is_qualified", False),
                "appointment_scheduled": conversation.get("appointment_scheduled", False)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
            return {}
    
    async def update_conversation_data(
        self,
        session_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Atualiza dados da conversa
        
        Args:
            session_id: ID da sessão
            **kwargs: Campos a atualizar
            
        Returns:
            Conversa atualizada
        """
        update_data = {
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        try:
            # Verificar se conversa existe
            exists = self.client.table(self.conversations_table)\
                .select("id")\
                .eq("session_id", session_id)\
                .execute()
            
            if exists.data:
                # Atualizar
                response = self.client.table(self.conversations_table)\
                    .update(update_data)\
                    .eq("session_id", session_id)\
                    .execute()
            else:
                # Criar nova
                update_data["session_id"] = session_id
                update_data["created_at"] = datetime.utcnow().isoformat()
                response = self.client.table(self.conversations_table)\
                    .insert(update_data)\
                    .execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Erro ao atualizar conversa: {e}")
            return {}
    
    async def get_active_conversations(
        self,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Lista conversas ativas nas últimas X horas
        
        Args:
            hours: Horas para considerar ativa
            
        Returns:
            Lista de conversas ativas
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        try:
            response = self.client.table(self.conversations_table)\
                .select("*")\
                .gte("updated_at", cutoff_time.isoformat())\
                .eq("status", "active")\
                .execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar conversas ativas: {e}")
            return []
```

### 7.2 Context Manager

```python
# agents/memory/context_manager.py
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    """Gerencia contexto da conversa para o agente"""
    
    def __init__(self):
        self.contexts: Dict[str, Dict[str, Any]] = {}
    
    def build_context(
        self,
        session_id: str,
        conversation_summary: Dict[str, Any],
        recent_messages: List[Dict[str, Any]],
        lead_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Constrói contexto para o agente
        
        Args:
            session_id: ID da sessão
            conversation_summary: Resumo da conversa
            recent_messages: Mensagens recentes
            lead_data: Dados do lead
            
        Returns:
            Contexto formatado
        """
        context_parts = []
        
        # Dados do lead
        if lead_data or conversation_summary.get("lead_name"):
            context_parts.append("=== INFORMAÇÕES DO LEAD ===")
            context_parts.append(f"Nome: {lead_data.get('name') or conversation_summary.get('lead_name', 'Não identificado')}")
            context_parts.append(f"Telefone: {lead_data.get('phone') or conversation_summary.get('lead_phone', 'Não identificado')}")
            
            if bill_value := conversation_summary.get("bill_value"):
                context_parts.append(f"Valor da conta: R$ {bill_value:.2f}")
            
            if solution := conversation_summary.get("solution_identified"):
                context_parts.append(f"Solução de interesse: {solution}")
            
            if conversation_summary.get("has_competitor"):
                context_parts.append("⚠️ Lead tem concorrente")
            
            context_parts.append(f"Score de qualificação: {conversation_summary.get('lead_score', 0)}/100")
            context_parts.append("")
        
        # Status da conversa
        context_parts.append("=== STATUS DA CONVERSA ===")
        context_parts.append(f"Estágio atual: {self._get_stage_name(conversation_summary.get('qualification_stage', 0))}")
        context_parts.append(f"Total de mensagens: {conversation_summary.get('total_messages', 0)}")
        
        if last_message := conversation_summary.get("last_message_at"):
            context_parts.append(f"Última mensagem: {self._format_time_ago(last_message)}")
        
        if conversation_summary.get("appointment_scheduled"):
            context_parts.append("✅ Reunião já agendada")
        
        context_parts.append("")
        
        # Histórico recente
        if recent_messages:
            context_parts.append("=== HISTÓRICO RECENTE ===")
            for msg in recent_messages[-5:]:  # Últimas 5 mensagens
                role = "Cliente" if msg["role"] == "user" else "Você"
                time = self._format_time(msg["created_at"])
                context_parts.append(f"[{time}] {role}: {msg['content'][:100]}...")
            context_parts.append("")
        
        # Próximos passos sugeridos
        next_steps = self._suggest_next_steps(conversation_summary)
        if next_steps:
            context_parts.append("=== PRÓXIMOS PASSOS SUGERIDOS ===")
            for step in next_steps:
                context_parts.append(f"• {step}")
        
        return "\n".join(context_parts)
    
    def _get_stage_name(self, stage: int) -> str:
        """Retorna nome do estágio"""
        stages = {
            0: "Identificação",
            1: "Descoberta de Solução",
            2: "Valor da Conta",
            3: "Análise Competitiva",
            4: "Agendamento"
        }
        return stages.get(stage, "Desconhecido")
    
    def _format_time_ago(self, timestamp: str) -> str:
        """Formata tempo decorrido"""
        try:
            time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.utcnow()
            diff = now - time.replace(tzinfo=None)
            
            if diff.days > 0:
                return f"há {diff.days} dias"
            elif diff.seconds > 3600:
                return f"há {diff.seconds // 3600} horas"
            elif diff.seconds > 60:
                return f"há {diff.seconds // 60} minutos"
            else:
                return "agora mesmo"
        except:
            return timestamp
    
    def _format_time(self, timestamp: str) -> str:
        """Formata horário"""
        try:
            time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return time.strftime("%H:%M")
        except:
            return timestamp
    
    def _suggest_next_steps(self, summary: Dict[str, Any]) -> List[str]:
        """Sugere próximos passos baseado no contexto"""
        steps = []
        stage = summary.get("qualification_stage", 0)
        
        if not summary.get("lead_name"):
            steps.append("Descobrir o nome do lead")
        
        if stage == 0:
            steps.append("Perguntar sobre interesse (usina ou desconto)")
        elif stage == 1:
            steps.append("Solicitar valor da conta de luz")
        elif stage == 2:
            steps.append("Verificar se tem desconto com concorrentes")
        elif stage == 3 and not summary.get("appointment_scheduled"):
            steps.append("Oferecer agendamento de reunião")
        
        if summary.get("lead_score", 0) >= 80 and not summary.get("appointment_scheduled"):
            steps.append("🔥 PRIORIDADE: Agendar reunião - Lead HOT!")
        
        return steps
```

---

## 8. Fluxo de Qualificação

### 8.1 Implementação do Fluxo

```python
# agents/flows/qualification_flow.py
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class QualificationStage(Enum):
    """Estágios do processo de qualificação"""
    IDENTIFICATION = 0
    SOLUTION_DISCOVERY = 1
    BILL_VALUE = 2
    COMPETITIVE_ANALYSIS = 3
    SCHEDULING = 4
    QUALIFIED = 5

class QualificationFlow:
    """Gerencia o fluxo de qualificação de leads"""
    
    def __init__(self):
        self.stage_questions = {
            QualificationStage.IDENTIFICATION: [
                "Qual é o seu nome?",
                "Como você gostaria de ser chamado?",
                "Pode me dizer seu nome?"
            ],
            QualificationStage.SOLUTION_DISCOVERY: [
                "Você está buscando instalar uma usina solar ou prefere apenas ter desconto na conta?",
                "Tem interesse em produzir sua própria energia ou apenas economizar?",
                "Quer uma usina solar ou desconto na conta de luz?"
            ],
            QualificationStage.BILL_VALUE: [
                "Qual o valor médio da sua conta de luz?",
                "Quanto você paga de energia por mês?",
                "Pode me enviar uma foto da sua conta de luz?"
            ],
            QualificationStage.COMPETITIVE_ANALYSIS: [
                "Você já tem algum desconto na conta de luz?",
                "Já contratou alguma empresa de energia solar?",
                "Tem desconto com alguma empresa como Origo ou Setta?"
            ],
            QualificationStage.SCHEDULING: [
                "Vamos agendar uma reunião para eu te mostrar a economia?",
                "Que tal marcarmos um horário para conversarmos melhor?",
                "Quando você tem disponibilidade para uma reunião rápida?"
            ]
        }
        
        self.stage_validations = {
            QualificationStage.IDENTIFICATION: self._validate_name,
            QualificationStage.SOLUTION_DISCOVERY: self._validate_solution,
            QualificationStage.BILL_VALUE: self._validate_bill_value,
            QualificationStage.COMPETITIVE_ANALYSIS: self._validate_competition,
            QualificationStage.SCHEDULING: self._validate_scheduling
        }
    
    def get_current_stage(
        self,
        lead_data: Dict[str, Any]
    ) -> QualificationStage:
        """Determina estágio atual baseado nos dados
        
        Args:
            lead_data: Dados do lead
            
        Returns:
            Estágio atual
        """
        if lead_data.get("appointment_scheduled"):
            return QualificationStage.QUALIFIED
        
        if not lead_data.get("name"):
            return QualificationStage.IDENTIFICATION
        
        if not lead_data.get("solution_type"):
            return QualificationStage.SOLUTION_DISCOVERY
        
        if not lead_data.get("bill_value"):
            return QualificationStage.BILL_VALUE
        
        if lead_data.get("competition_checked") is False:
            return QualificationStage.COMPETITIVE_ANALYSIS
        
        return QualificationStage.SCHEDULING
    
    def process_response(
        self,
        current_stage: QualificationStage,
        response: str,
        lead_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[QualificationStage]]:
        """Processa resposta e atualiza dados
        
        Args:
            current_stage: Estágio atual
            response: Resposta do lead
            lead_data: Dados atuais
            
        Returns:
            (dados_atualizados, próximo_estágio)
        """
        # Validar resposta para o estágio atual
        validation_func = self.stage_validations.get(current_stage)
        
        if validation_func:
            is_valid, extracted_data = validation_func(response)
            
            if is_valid:
                # Atualizar dados do lead
                lead_data.update(extracted_data)
                lead_data["last_updated"] = datetime.utcnow().isoformat()
                
                # Determinar próximo estágio
                next_stage = self._get_next_stage(current_stage)
                
                logger.info(f"Estágio {current_stage.name} concluído. Próximo: {next_stage.name if next_stage else 'FIM'}")
                
                return lead_data, next_stage
            else:
                # Resposta inválida, permanecer no mesmo estágio
                logger.info(f"Resposta inválida para estágio {current_stage.name}")
                return lead_data, current_stage
        
        return lead_data, current_stage
    
    def _get_next_stage(
        self,
        current_stage: QualificationStage
    ) -> Optional[QualificationStage]:
        """Retorna próximo estágio"""
        stage_order = [
            QualificationStage.IDENTIFICATION,
            QualificationStage.SOLUTION_DISCOVERY,
            QualificationStage.BILL_VALUE,
            QualificationStage.COMPETITIVE_ANALYSIS,
            QualificationStage.SCHEDULING,
            QualificationStage.QUALIFIED
        ]
        
        current_index = stage_order.index(current_stage)
        
        if current_index < len(stage_order) - 1:
            return stage_order[current_index + 1]
        
        return None
    
    def _validate_name(self, response: str) -> Tuple[bool, Dict[str, Any]]:
        """Valida nome do lead"""
        # Usar ferramenta de extração
        from agents.tools.qualification_tools import QualificationTools
        tools = QualificationTools()
        
        name = tools.extract_name(response)
        
        if name:
            return True, {"name": name}
        
        return False, {}
    
    def _validate_solution(self, response: str) -> Tuple[bool, Dict[str, Any]]:
        """Valida solução escolhida"""
        from agents.tools.qualification_tools import QualificationTools
        tools = QualificationTools()
        
        solution = tools.identify_solution(response)
        
        if solution["confidence"] > 0.5:
            return True, {
                "solution_type": solution["solution_id"],
                "solution_confidence": solution["confidence"]
            }
        
        return False, {}
    
    def _validate_bill_value(self, response: str) -> Tuple[bool, Dict[str, Any]]:
        """Valida valor da conta"""
        from agents.tools.qualification_tools import QualificationTools
        tools = QualificationTools()
        
        value = tools.extract_bill_value(response)
        
        if value:
            return True, {"bill_value": value}
        
        return False, {}
    
    def _validate_competition(self, response: str) -> Tuple[bool, Dict[str, Any]]:
        """Valida informações de concorrência"""
        response_lower = response.lower()
        
        data = {"competition_checked": True}
        
        # Verificar se tem concorrente
        if any(word in response_lower for word in ["sim", "tenho", "já", "desconto"]):
            data["has_competitor"] = True
            
            # Identificar concorrente
            competitors = {
                "origo": ["origo"],
                "setta": ["setta", "seta"],
                "outras": ["outra", "empresa", "companhia"]
            }
            
            for comp_name, keywords in competitors.items():
                if any(kw in response_lower for kw in keywords):
                    data["competitor_name"] = comp_name
                    break
            
            # Extrair desconto se mencionado
            import re
            discount_match = re.search(r'(\d+)\s*%', response)
            if discount_match:
                data["competitor_discount"] = float(discount_match.group(1))
        else:
            data["has_competitor"] = False
        
        return True, data
    
    def _validate_scheduling(self, response: str) -> Tuple[bool, Dict[str, Any]]:
        """Valida interesse em agendar"""
        response_lower = response.lower()
        
        positive_indicators = [
            "sim", "claro", "vamos", "pode", "quero",
            "interesse", "legal", "ótimo", "perfeito", "bora"
        ]
        
        negative_indicators = [
            "não", "depois", "agora não", "pensar", "ver",
            "calma", "espera", "talvez"
        ]
        
        positive_count = sum(1 for word in positive_indicators if word in response_lower)
        negative_count = sum(1 for word in negative_indicators if word in response_lower)
        
        if positive_count > negative_count:
            return True, {"wants_appointment": True}
        elif negative_count > positive_count:
            return True, {"wants_appointment": False}
        
        return False, {}
```

---

## 9. Testes e Validação

### 9.1 Testes Unitários

```python
# tests/test_sales_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from agents.sales_agent import SolarPrimeSalesAgent
from agents.flows.qualification_flow import QualificationStage

@pytest.fixture
def mock_config():
    """Configuração mock para testes"""
    return {
        "gemini_api_key": "test_key",
        "supabase_url": "https://test.supabase.co",
        "supabase_key": "test_key",
        "redis_url": "redis://localhost:6379/0",
        "kommo_config": {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "subdomain": "test"
        }
    }

@pytest.fixture
def sales_agent(mock_config):
    """Instância do agente para testes"""
    with patch('agents.sales_agent.GeminiModel'):
        with patch('agents.sales_agent.SqlAgentStorage'):
            agent = SolarPrimeSalesAgent(**mock_config)
            return agent

class TestSalesAgent:
    """Testes do agente de vendas"""
    
    @pytest.mark.asyncio
    async def test_process_initial_message(self, sales_agent):
        """Testa processamento da primeira mensagem"""
        response = await sales_agent.process_message(
            message="Oi, quero saber sobre energia solar",
            sender_id="123456",
            sender_name=None
        )
        
        # Deve cumprimentar e pedir nome
        assert "bem-vindo" in response.lower() or "olá" in response.lower()
        assert "nome" in response.lower()
    
    @pytest.mark.asyncio
    async def test_name_extraction(self, sales_agent):
        """Testa extração de nome"""
        # Simular conversa em andamento
        session_id = "whatsapp_123456"
        sales_agent.qualification_stage[session_id] = 0
        
        response = await sales_agent.process_message(
            message="Meu nome é João Silva",
            sender_id="123456",
            session_id=session_id
        )
        
        # Deve avançar para próximo estágio
        assert sales_agent.qualification_stage[session_id] == 1
        assert "joão" in response.lower() or "prazer" in response.lower()
    
    @pytest.mark.asyncio
    async def test_solution_identification(self, sales_agent):
        """Testa identificação de solução"""
        session_id = "whatsapp_123456"
        sales_agent.qualification_stage[session_id] = 1
        
        response = await sales_agent.process_message(
            message="Quero instalar uma usina solar na minha casa",
            sender_id="123456",
            session_id=session_id
        )
        
        # Deve perguntar sobre valor da conta
        assert "conta" in response.lower() or "valor" in response.lower()
    
    @pytest.mark.asyncio
    async def test_bill_value_extraction(self, sales_agent):
        """Testa extração de valor da conta"""
        session_id = "whatsapp_123456"
        sales_agent.qualification_stage[session_id] = 2
        
        response = await sales_agent.process_message(
            message="Minha conta vem uns R$ 850 por mês",
            sender_id="123456",
            session_id=session_id
        )
        
        # Deve perguntar sobre concorrentes
        assert "desconto" in response.lower() or "empresa" in response.lower()

class TestQualificationFlow:
    """Testes do fluxo de qualificação"""
    
    def test_stage_progression(self):
        """Testa progressão de estágios"""
        from agents.flows.qualification_flow import QualificationFlow
        
        flow = QualificationFlow()
        lead_data = {}
        
        # Estágio inicial
        stage = flow.get_current_stage(lead_data)
        assert stage == QualificationStage.IDENTIFICATION
        
        # Após nome
        lead_data["name"] = "João"
        stage = flow.get_current_stage(lead_data)
        assert stage == QualificationStage.SOLUTION_DISCOVERY
        
        # Após solução
        lead_data["solution_type"] = "usina_propria"
        stage = flow.get_current_stage(lead_data)
        assert stage == QualificationStage.BILL_VALUE
    
    def test_response_validation(self):
        """Testa validação de respostas"""
        from agents.flows.qualification_flow import QualificationFlow
        
        flow = QualificationFlow()
        
        # Teste nome válido
        lead_data = {}
        updated_data, next_stage = flow.process_response(
            QualificationStage.IDENTIFICATION,
            "Meu nome é Maria Santos",
            lead_data
        )
        
        assert updated_data.get("name") == "Maria Santos"
        assert next_stage == QualificationStage.SOLUTION_DISCOVERY
        
        # Teste valor inválido
        lead_data = {"name": "Maria"}
        updated_data, next_stage = flow.process_response(
            QualificationStage.BILL_VALUE,
            "Não sei o valor exato",
            lead_data
        )
        
        assert "bill_value" not in updated_data
        assert next_stage == QualificationStage.BILL_VALUE  # Permanece no mesmo

class TestQualificationTools:
    """Testes das ferramentas de qualificação"""
    
    def test_name_extraction(self):
        """Testa extração de nomes"""
        from agents.tools.qualification_tools import QualificationTools
        
        tools = QualificationTools()
        
        test_cases = [
            ("Oi, me chamo Pedro Silva", "Pedro Silva"),
            ("Meu nome é Ana", "Ana"),
            ("Sou o Carlos", "Carlos"),
            ("Maria Fernanda", "Maria Fernanda"),
            ("boa tarde", None)
        ]
        
        for text, expected in test_cases:
            result = tools.extract_name(text)
            assert result == expected
    
    def test_bill_value_extraction(self):
        """Testa extração de valores"""
        from agents.tools.qualification_tools import QualificationTools
        
        tools = QualificationTools()
        
        test_cases = [
            ("Pago R$ 450,00", 450.0),
            ("conta de 1.200 reais", 1200.0),
            ("Cerca de R$ 2.500,00 por mês", 2500.0),
            ("uns 800", 800.0),
            ("não sei", None)
        ]
        
        for text, expected in test_cases:
            result = tools.extract_bill_value(text)
            assert result == expected
    
    def test_lead_scoring(self):
        """Testa cálculo de score"""
        from agents.tools.qualification_tools import QualificationTools
        
        tools = QualificationTools()
        
        # Lead quente
        result = tools.calculate_lead_score(
            name="João Silva",
            bill_value=1500.0,
            solution="usina_propria",
            has_competitor=False,
            engagement_level="high"
        )
        
        assert result["score"] >= 80
        assert result["classification"] == "HOT 🔥"
        
        # Lead frio
        result = tools.calculate_lead_score(
            name=None,
            bill_value=150.0,
            solution="unknown",
            has_competitor=True,
            competitor_discount=25.0,
            engagement_level="low"
        )
        
        assert result["score"] < 40
        assert result["classification"] == "COLD 🧊"
```

### 9.2 Script de Teste Manual

```python
# tests/manual_test.py
"""
Script para teste manual do agente
"""
import asyncio
import os
from dotenv import load_dotenv
from agents.sales_agent import SolarPrimeSalesAgent

load_dotenv()

async def test_conversation():
    """Testa conversa com o agente"""
    
    # Configurar agente
    agent = SolarPrimeSalesAgent(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
        redis_url=os.getenv("REDIS_URL"),
        kommo_config={
            "client_id": os.getenv("KOMMO_CLIENT_ID"),
            "client_secret": os.getenv("KOMMO_CLIENT_SECRET"),
            "subdomain": os.getenv("KOMMO_SUBDOMAIN"),
            "redirect_uri": os.getenv("KOMMO_REDIRECT_URI")
        }
    )
    
    print("=== Teste de Conversa com Agente SDR SolarPrime ===")
    print("Digite 'sair' para encerrar\n")
    
    session_id = "test_session_123"
    sender_id = "test_user"
    
    # Simular conversa
    while True:
        user_input = input("\nVocê: ")
        
        if user_input.lower() == 'sair':
            break
        
        print("\nAgente está digitando...")
        
        response = await agent.process_message(
            message=user_input,
            sender_id=sender_id,
            sender_name="Usuário Teste",
            session_id=session_id
        )
        
        print(f"\nLeonardo: {response}")
    
    print("\n=== Conversa encerrada ===")

if __name__ == "__main__":
    asyncio.run(test_conversation())
```

---

## 10. Otimizações e Performance

### 10.1 Cache de Respostas

```python
# agents/optimization/response_cache.py
from typing import Optional, Dict, Any
import hashlib
import json
import redis
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class ResponseCache:
    """Cache para respostas frequentes"""
    
    def __init__(self, redis_url: str, ttl_seconds: int = 3600):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = ttl_seconds
        self.prefix = "agent_response:"
    
    def get_cache_key(
        self,
        message: str,
        stage: int,
        context: Dict[str, Any]
    ) -> str:
        """Gera chave de cache"""
        # Criar hash do contexto relevante
        cache_data = {
            "message": message.lower().strip(),
            "stage": stage,
            "has_name": bool(context.get("lead_name")),
            "has_bill": bool(context.get("bill_value")),
            "has_competitor": context.get("has_competitor", False)
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return self.prefix + hashlib.md5(cache_str.encode()).hexdigest()
    
    async def get(
        self,
        message: str,
        stage: int,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Busca resposta no cache"""
        try:
            key = self.get_cache_key(message, stage, context)
            cached = self.redis_client.get(key)
            
            if cached:
                logger.info(f"Cache hit para mensagem: {message[:50]}...")
                return cached.decode('utf-8')
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cache: {e}")
            return None
    
    async def set(
        self,
        message: str,
        stage: int,
        context: Dict[str, Any],
        response: str
    ):
        """Salva resposta no cache"""
        try:
            key = self.get_cache_key(message, stage, context)
            self.redis_client.setex(
                key,
                timedelta(seconds=self.ttl),
                response
            )
            logger.info(f"Resposta cacheada para: {message[:50]}...")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
```

### 10.2 Otimização de Prompts

```python
# agents/optimization/prompt_optimizer.py
from typing import Dict, Any, List
import re

class PromptOptimizer:
    """Otimiza prompts para reduzir tokens"""
    
    @staticmethod
    def optimize_context(context: str, max_tokens: int = 1000) -> str:
        """Otimiza contexto removendo redundâncias"""
        
        # Remover linhas vazias múltiplas
        context = re.sub(r'\n{3,}', '\n\n', context)
        
        # Comprimir seções repetitivas
        context = context.replace("=== ", "# ")
        context = context.replace("---", "")
        
        # Truncar se necessário
        if len(context) > max_tokens * 4:  # Aproximação
            context = context[:max_tokens * 4] + "\n[...contexto truncado]"
        
        return context.strip()
    
    @staticmethod
    def optimize_history(
        messages: List[Dict[str, Any]],
        max_messages: int = 10
    ) -> List[Dict[str, Any]]:
        """Otimiza histórico de mensagens"""
        
        # Manter apenas mensagens recentes relevantes
        relevant_messages = []
        
        # Sempre incluir mensagens com informações importantes
        important_keywords = [
            "nome", "conta", "valor", "desconto", "reunião",
            "agendar", "usina", "energia"
        ]
        
        for msg in messages[-max_messages:]:
            content = msg.get("content", "").lower()
            
            # Incluir se tem palavra importante ou é recente
            if any(kw in content for kw in important_keywords):
                relevant_messages.append(msg)
            elif len(relevant_messages) < max_messages // 2:
                relevant_messages.append(msg)
        
        return relevant_messages
```

### 10.3 Monitoramento de Performance

```python
# agents/monitoring/performance_monitor.py
from typing import Dict, Any
import time
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitora performance do agente"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            "response_time": [],
            "token_usage": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        self.start_time = time.time()
    
    async def track_response_time(self, coro):
        """Rastreia tempo de resposta"""
        start = time.time()
        
        try:
            result = await coro
            elapsed = time.time() - start
            self.metrics["response_time"].append(elapsed)
            
            if elapsed > 5.0:
                logger.warning(f"Resposta lenta: {elapsed:.2f}s")
            
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            raise e
    
    def record_token_usage(self, tokens: int):
        """Registra uso de tokens"""
        self.metrics["token_usage"].append(tokens)
    
    def record_cache_hit(self):
        """Registra cache hit"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Registra cache miss"""
        self.metrics["cache_misses"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas"""
        uptime = time.time() - self.start_time
        
        response_times = self.metrics["response_time"]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        token_usage = self.metrics["token_usage"]
        avg_tokens = sum(token_usage) / len(token_usage) if token_usage else 0
        
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_rate = self.metrics["cache_hits"] / cache_total if cache_total > 0 else 0
        
        return {
            "uptime_seconds": uptime,
            "total_requests": len(response_times),
            "average_response_time": avg_response,
            "max_response_time": max(response_times) if response_times else 0,
            "average_tokens": avg_tokens,
            "total_tokens": sum(token_usage),
            "cache_hit_rate": cache_rate,
            "error_count": self.metrics["errors"],
            "requests_per_minute": len(response_times) / (uptime / 60) if uptime > 0 else 0
        }
    
    def log_stats(self):
        """Loga estatísticas"""
        stats = self.get_stats()
        logger.info(f"""
Performance Stats:
- Uptime: {stats['uptime_seconds']:.0f}s
- Requests: {stats['total_requests']}
- Avg Response: {stats['average_response_time']:.2f}s
- Cache Hit Rate: {stats['cache_hit_rate']:.2%}
- Errors: {stats['error_count']}
        """)
```

---

## 🎉 Conclusão

Parabéns! Você implementou o agente de IA usando AGnO Framework com Google Gemini 2.5 Pro. 

### Próximos Passos:
1. Testar o agente localmente
2. Implementar o sistema RAG: [03-rag-supabase.md](03-rag-supabase.md)
3. Criar a API e webhooks: [04-api-webhooks.md](04-api-webhooks.md)

### Checklist de Conclusão:
- [ ] Agente AGnO configurado
- [ ] Gemini 2.5 Pro integrado
- [ ] Sistema de prompts implementado
- [ ] Ferramentas customizadas criadas
- [ ] Fluxo de qualificação funcionando
- [ ] Testes básicos passando
- [ ] Performance otimizada

---

**💡 Dica**: Execute o script de teste manual para validar o comportamento do agente antes de prosseguir.