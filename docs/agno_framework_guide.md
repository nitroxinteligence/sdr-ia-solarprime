# Guia Completo do AGnO Framework

## 📚 Visão Geral

O AGnO é um framework poderoso para criar agentes de IA autônomos com capacidades avançadas de raciocínio, memória persistente e processamento multimodal. Este guia contém implementações práticas para criar um sistema SDR completo.

## 🤖 1. Criando Agentes Corretamente

### Estrutura Básica de um Agente

```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.exa import ExaTools

# Agente básico com Gemini 2.5 Pro
agent = Agent(
    # Modelo principal
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    
    # Ferramentas disponíveis
    tools=[ExaTools()],
    
    # Descrição do agente
    description="Você é um SDR especialista em vendas B2B de energia solar",
    
    # Instruções específicas
    instructions="""
    1. Analise o perfil do lead
    2. Identifique pontos de dor específicos
    3. Personalize a abordagem
    4. Use dados do mercado solar
    """,
    
    # Formato esperado de saída
    expected_output="Um pitch personalizado em formato markdown",
    
    # Configurações adicionais
    markdown=True,
    show_tool_calls=True,
    debug_mode=True
)
```

### Executando o Agente

```python
# Execução simples
response = agent.run("Crie um pitch para uma indústria metalúrgica")

# Execução com streaming
response_stream = agent.run(
    "Analise este lead e crie uma abordagem",
    stream=True,
    stream_intermediate_steps=True
)

# Processando eventos em tempo real
for event in response_stream:
    if event.event == "RunResponseContent":
        print(f"Conteúdo: {event.content}")
    elif event.event == "ToolCallStarted":
        print(f"Ferramenta iniciada: {event.tool}")
```

## 🧠 2. Integração com Gemini 2.5 Pro

### Configuração Completa do Gemini

```python
from agno.models.google import Gemini
import os

# Método 1: Google AI Studio (mais simples)
os.environ["GOOGLE_API_KEY"] = "sua-api-key"

agent_gemini = Agent(
    model=Gemini(
        id="gemini-2.5-pro-exp-03-25",
        temperature=0.7,
        max_tokens=4096,
        grounding=True,  # Ativa busca contextual
        search=True      # Ativa busca web
    ),
    markdown=True
)

# Método 2: Vertex AI (para produção)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "seu-projeto"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

agent_vertex = Agent(
    model=Gemini(
        id="gemini-2.5-pro-exp-03-25",
        vertexai=True,
        project_id="seu-projeto",
        location="us-central1"
    ),
    markdown=True
)
```

## 💾 3. Memória e Storage com Banco de Dados Externo

### Configuração com PostgreSQL

```python
from agno.agent import Agent
from agno.memory import Memory
from agno.storage.postgres import PostgresStorage
from agno.models.google import Gemini

# Configurar storage PostgreSQL
storage = PostgresStorage(
    table_name="sdr_sessions",
    db_url="postgresql+psycopg://user:password@localhost:5432/sdr_db",
    auto_upgrade_schema=True
)

# Criar agente com memória persistente
agent_with_memory = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    
    # Configuração de memória
    memory=Memory(db=storage),
    storage=storage,
    
    # Configurações de histórico
    add_history_to_messages=True,
    num_history_runs=5,  # Últimas 5 interações
    
    # Memória personalizada do usuário
    enable_agentic_memory=True,  # Agente gerencia memórias
    enable_user_memories=True,   # Sempre salva insights
    
    # Estado da sessão
    session_state={
        "lead_info": {},
        "interaction_count": 0,
        "objections_handled": []
    },
    
    instructions="""
    Você é um SDR com memória persistente.
    
    Estado atual:
    - Lead: {lead_info}
    - Interações: {interaction_count}
    - Objeções tratadas: {objections_handled}
    """
)

# Usar com sessões específicas
response = agent_with_memory.run(
    "Quero informações sobre energia solar",
    user_id="lead_123",
    session_id="conversa_001"
)
```

### Implementação com Supabase

```python
from agno.storage.postgres import PostgresStorage
from agno.vectordb.pgvector import PgVector

# Configurar Supabase
SUPABASE_URL = "postgresql://postgres:senha@db.supabase.co:5432/postgres"

# Storage para sessões
storage = PostgresStorage(
    table_name="agent_sessions",
    db_url=SUPABASE_URL,
    auto_upgrade_schema=True
)

# Vector DB para knowledge base
vector_db = PgVector(
    table_name="knowledge_embeddings",
    db_url=SUPABASE_URL,
    search_type="hybrid"  # Busca híbrida (vetor + texto)
)
```

## 🎨 4. Multimodal: Processamento de Imagens e Áudio

### Agente com Análise de Imagens

```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.utils import Image

# Agente multimodal para análise de imagens
agent_visual = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    description="Analista de instalações solares",
    markdown=True
)

# Analisar imagem de telhado
response = agent_visual.run(
    "Analise este telhado para instalação solar. Identifique área disponível, inclinação e obstáculos.",
    images=[
        Image(url="https://exemplo.com/telhado.jpg"),
        Image(file_path="/caminho/local/telhado2.png")
    ]
)
```

### Agente com Processamento de Áudio

```python
from agno.models.openai import OpenAIChat

# Agente com entrada e saída de áudio
agent_audio = Agent(
    model=OpenAIChat(
        id="gpt-4o-audio-preview",
        modalities=["text", "audio"],
        audio={
            "voice": "alloy",
            "format": "wav"
        }
    ),
    description="SDR com capacidade de voz"
)

# Processar áudio e responder com áudio
audio_response = agent_audio.run(
    "Responda esta ligação de um lead interessado",
    audio_input="/caminho/para/audio_lead.wav"
)

# Salvar resposta em áudio
with open("resposta_sdr.wav", "wb") as f:
    f.write(audio_response.audio_content)
```

## 🔄 5. Workflows para Follow-up

### Workflow de Qualificação e Follow-up

```python
from agno.workflow import Workflow
from agno.agent import Agent
from agno.models.google import Gemini

# Agentes especializados
agent_qualificador = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    description="Especialista em qualificação de leads",
    instructions="Avalie: orçamento, timeline, decisor, necessidade"
)

agent_follow_up = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    description="Especialista em follow-up",
    instructions="Crie mensagem personalizada baseada na qualificação"
)

agent_objection = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    description="Especialista em quebra de objeções",
    reasoning=True,  # Ativa raciocínio para objeções complexas
    instructions="Use lógica estruturada para quebrar objeções"
)

# Criar workflow
workflow_sdr = Workflow(
    name="Pipeline SDR Completo",
    steps=[
        # Passo 1: Qualificação
        {
            "name": "qualificar_lead",
            "agent": agent_qualificador,
            "input": "lead_data"
        },
        
        # Passo 2: Decisão condicional
        {
            "name": "avaliar_qualificacao",
            "type": "condition",
            "condition": lambda result: result.score > 7,
            "if_true": "follow_up_quente",
            "if_false": "nurturing"
        },
        
        # Passo 3A: Follow-up para lead quente
        {
            "name": "follow_up_quente",
            "agent": agent_follow_up,
            "instructions": "Lead qualificado - abordagem direta"
        },
        
        # Passo 3B: Nurturing para lead frio
        {
            "name": "nurturing",
            "agent": agent_follow_up,
            "instructions": "Lead frio - educar primeiro"
        }
    ]
)

# Executar workflow
result = workflow_sdr.run({
    "lead_data": {
        "empresa": "Metalúrgica ABC",
        "funcionarios": 200,
        "consumo_kwh": 50000,
        "interesse": "reduzir custos"
    }
})
```

### Workflow com Loop para Refinamento

```python
from agno.workflow import Workflow, Loop

# Workflow iterativo para melhorar pitch
workflow_refinamento = Workflow(
    name="Refinamento de Pitch",
    steps=[
        # Criar pitch inicial
        agent_follow_up,
        
        # Loop de refinamento
        Loop(
            name="refinar_pitch",
            agent=agent_follow_up,
            max_iterations=3,
            condition=lambda result: result.quality_score < 9,
            instructions="Melhore: clareza, personalização e CTA"
        )
    ]
)
```

## 🔍 6. PgVector com Supabase para Knowledge Base

### Configuração Completa com Supabase

```python
from agno.agent import Agent, AgentKnowledge
from agno.models.google import Gemini
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge import PDFKnowledgeBase
import os

# Configurar Supabase
SUPABASE_URL = "postgresql://postgres:sua-senha@db.projeto.supabase.co:5432/postgres"

# Criar vector database
vector_db = PgVector(
    table_name="solar_knowledge",
    db_url=SUPABASE_URL,
    search_type=SearchType.hybrid,  # Busca híbrida
    distance="cosine",  # Métrica de similaridade
    vector_score_weight=0.7  # Peso para busca vetorial vs texto
)

# Criar knowledge base com documentos
knowledge_base = PDFKnowledgeBase(
    urls=[
        "https://exemplo.com/manual_solar.pdf",
        "https://exemplo.com/casos_sucesso.pdf"
    ],
    vector_db=vector_db
)

# Adicionar conhecimento específico
knowledge_base.load_text("""
Benefícios da Energia Solar para Indústrias:
1. Redução de 95% na conta de luz
2. ROI médio de 3-5 anos
3. Valorização do imóvel em 8%
4. Créditos de carbono
5. Marketing verde
""")

# Criar agente com knowledge base
agent_rag = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    knowledge=knowledge_base,
    search_knowledge=True,  # Busca automática
    description="SDR com conhecimento profundo sobre energia solar",
    instructions="""
    Sempre que responder:
    1. Busque informações relevantes na base de conhecimento
    2. Use dados e casos reais
    3. Cite fontes quando apropriado
    """
)

# Usar o agente
response = agent_rag.run(
    "Quais os benefícios para uma indústria metalúrgica?"
)
```

## 🎯 7. Reasoning para Quebra de Objeções

### Agente com Raciocínio Avançado

```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat

# Método 1: Usando modelo de raciocínio dedicado
agent_reasoning = Agent(
    model=OpenAIChat(id="o3-mini", reasoning_effort="high"),
    description="Especialista em quebra de objeções complexas",
    tools=[],  # Adicione ferramentas necessárias
    instructions="""
    Quando receber uma objeção:
    1. Analise a objeção profundamente
    2. Identifique a raiz do problema
    3. Desenvolva argumentos lógicos
    4. Apresente solução estruturada
    """
)

# Método 2: Ativando reasoning em agente normal
agent_objection_handler = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    reasoning=True,  # Ativa sistema de raciocínio
    markdown=True,
    description="Quebrador de objeções com raciocínio estruturado",
    instructions="""
    Use o seguinte framework para quebrar objeções:
    
    1. RECONHECER: Valide a preocupação do cliente
    2. RECONTEXTUALIZAR: Mude a perspectiva
    3. RESOLVER: Apresente solução específica
    4. REFORÇAR: Mostre benefícios adicionais
    """
)

# Executar com raciocínio visível
response = agent_objection_handler.run(
    """
    Objeção do cliente: "O investimento inicial é muito alto e 
    não temos capital disponível agora."
    """,
    show_full_reasoning=True,  # Mostra cadeia de pensamento
    stream=True
)

# Processar resposta com raciocínio
for event in response:
    if hasattr(event, 'reasoning'):
        print("🧠 Raciocínio:", event.reasoning)
    if hasattr(event, 'content'):
        print("💬 Resposta:", event.content)
```

### Sistema Multi-Agente para Objeções Complexas

```python
from agno.agent import Agent, Team
from agno.models.google import Gemini

# Agente analisador de objeções
analyst = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    description="Analista de objeções",
    instructions="Identifique: tipo, intensidade e causa raiz"
)

# Agente estrategista
strategist = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    reasoning=True,
    description="Estrategista de respostas",
    instructions="Desenvolva estratégia personalizada"
)

# Agente comunicador
communicator = Agent(
    model=Gemini(id="gemini-2.5-pro-exp-03-25"),
    description="Especialista em comunicação persuasiva",
    instructions="Transforme estratégia em mensagem convincente"
)

# Criar time para quebra de objeções
objection_team = Team(
    agents=[analyst, strategist, communicator],
    name="Time Quebra-Objeções",
    instructions="""
    Trabalhem juntos para:
    1. Analisar a objeção
    2. Desenvolver estratégia
    3. Criar resposta persuasiva
    """
)

# Usar o time
response = objection_team.run(
    "Cliente: Já temos contrato de energia por mais 2 anos"
)
```

## 🚀 8. Implementação Completa: SDR Autônomo

### Sistema SDR Completo com Todas as Funcionalidades

```python
from agno.agent import Agent, AgentKnowledge
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage
from agno.vectordb.pgvector import PgVector
from agno.workflow import Workflow
from agno.memory import Memory
import os

class SDRSystem:
    def __init__(self, supabase_url: str, google_api_key: str):
        """Sistema SDR completo com AGnO"""
        
        # Configurar credenciais
        os.environ["GOOGLE_API_KEY"] = google_api_key
        
        # Configurar storage
        self.storage = PostgresStorage(
            table_name="sdr_sessions",
            db_url=supabase_url,
            auto_upgrade_schema=True
        )
        
        # Configurar vector database
        self.vector_db = PgVector(
            table_name="knowledge_base",
            db_url=supabase_url,
            search_type="hybrid"
        )
        
        # Criar knowledge base
        self.knowledge = AgentKnowledge(vector_db=self.vector_db)
        self._load_knowledge()
        
        # Criar agente principal
        self.main_agent = self._create_main_agent()
        
        # Criar agentes especializados
        self.qualifier = self._create_qualifier()
        self.objection_handler = self._create_objection_handler()
        self.follow_up = self._create_follow_up()
        
        # Criar workflow
        self.workflow = self._create_workflow()
    
    def _load_knowledge(self):
        """Carrega base de conhecimento"""
        self.knowledge.load_text("""
        INFORMAÇÕES SOLARPRIME:
        
        1. PRODUTOS:
        - Sistemas fotovoltaicos de 50kWp a 5MWp
        - Financiamento próprio com carência de 6 meses
        - Garantia de 25 anos nos painéis
        - Manutenção preventiva inclusa por 2 anos
        
        2. CASOS DE SUCESSO:
        - Metalúrgica Santos: -92% na conta, ROI 3.2 anos
        - Indústria Têxtil Norte: -89% na conta, ROI 3.8 anos
        - Shopping Plaza: -94% na conta, ROI 2.9 anos
        
        3. DIFERENCIAIS:
        - Tecnologia de rastreamento solar (+15% eficiência)
        - App de monitoramento em tempo real
        - Seguro all-risk incluso
        - Time próprio de instalação certificado
        """)
    
    def _create_main_agent(self) -> Agent:
        """Cria agente SDR principal"""
        return Agent(
            model=Gemini(id="gemini-2.5-pro-exp-03-25"),
            memory=Memory(db=self.storage),
            storage=self.storage,
            knowledge=self.knowledge,
            search_knowledge=True,
            add_history_to_messages=True,
            num_history_runs=10,
            enable_agentic_memory=True,
            enable_user_memories=True,
            session_state={
                "lead_stage": "inicial",
                "interactions": 0,
                "objections": [],
                "interests": [],
                "next_action": None
            },
            description="SDR Sênior da SolarPrime",
            instructions="""
            Você é um SDR experiente da SolarPrime, especialista em vendas B2B
            de energia solar para indústrias e grandes empresas.
            
            OBJETIVOS:
            1. Qualificar leads usando BANT
            2. Identificar dores e necessidades
            3. Superar objeções com dados
            4. Agendar reunião com consultor
            
            PERSONALIDADE:
            - Profissional mas acessível
            - Consultivo, não pushy
            - Data-driven nas argumentações
            - Empático com as dores do cliente
            
            SEMPRE:
            - Use casos de sucesso relevantes
            - Personalize para o segmento
            - Foque em ROI e economia
            - Crie senso de urgência sem pressionar
            
            Estado atual do lead:
            - Estágio: {lead_stage}
            - Interações: {interactions}
            - Objeções: {objections}
            - Interesses: {interests}
            """,
            markdown=True,
            show_tool_calls=True
        )
    
    def _create_qualifier(self) -> Agent:
        """Cria agente qualificador"""
        return Agent(
            model=Gemini(id="gemini-2.5-pro-exp-03-25"),
            description="Especialista em qualificação BANT",
            instructions="""
            Qualifique o lead usando BANT:
            
            BUDGET: Capacidade de investimento
            AUTHORITY: É decisor ou influenciador?
            NEED: Qual a necessidade real?
            TIMELINE: Quando pretende implementar?
            
            Atribua score de 0-10 para cada critério.
            Score total > 28: Lead Quente
            Score 20-28: Lead Morno  
            Score < 20: Lead Frio
            """
        )
    
    def _create_objection_handler(self) -> Agent:
        """Cria agente para quebra de objeções"""
        return Agent(
            model=Gemini(id="gemini-2.5-pro-exp-03-25"),
            reasoning=True,
            knowledge=self.knowledge,
            search_knowledge=True,
            description="Especialista em quebra de objeções",
            instructions="""
            Framework de Quebra de Objeções:
            
            1. RECONHECER: "Entendo sua preocupação sobre..."
            2. RECONTEXTUALIZAR: Mude a perspectiva
            3. RESOLVER: Apresente solução específica com dados
            4. REFORÇAR: Mostre caso similar de sucesso
            5. REDIRECIONAR: Volte para os benefícios
            
            Use sempre:
            - Dados concretos
            - Casos de sucesso similares
            - Garantias e seguranças
            - Senso de urgência (aumento de tarifa, etc)
            """
        )
    
    def _create_follow_up(self) -> Agent:
        """Cria agente de follow-up"""
        return Agent(
            model=Gemini(id="gemini-2.5-pro-exp-03-25"),
            description="Especialista em follow-up e nurturing",
            instructions="""
            Crie mensagens de follow-up baseadas em:
            
            1. Estágio do lead
            2. Última interação
            3. Objeções mencionadas
            4. Interesses demonstrados
            
            Templates:
            - Lead Quente: Urgência + Benefício + CTA direto
            - Lead Morno: Educação + Caso de sucesso + CTA suave
            - Lead Frio: Conteúdo de valor + Construir relacionamento
            
            Sempre personalize com nome e empresa.
            """
        )
    
    def _create_workflow(self) -> Workflow:
        """Cria workflow completo do SDR"""
        return Workflow(
            name="Pipeline SDR SolarPrime",
            steps=[
                # 1. Primeira interação
                {
                    "name": "initial_contact",
                    "agent": self.main_agent,
                    "output": "initial_response"
                },
                
                # 2. Qualificação
                {
                    "name": "qualification",
                    "agent": self.qualifier,
                    "input": "initial_response",
                    "output": "qualification_score"
                },
                
                # 3. Roteamento baseado em qualificação
                {
                    "name": "routing",
                    "type": "router",
                    "condition": lambda x: x["qualification_score"]["total"],
                    "routes": {
                        "hot": lambda x: x >= 28,
                        "warm": lambda x: 20 <= x < 28,
                        "cold": lambda x: x < 20
                    }
                },
                
                # 4. Tratamento por tipo de lead
                {
                    "name": "hot_lead_handling",
                    "agent": self.main_agent,
                    "when": "route == 'hot'",
                    "instructions": "Agende reunião imediatamente"
                },
                
                {
                    "name": "warm_lead_handling",
                    "agent": self.follow_up,
                    "when": "route == 'warm'",
                    "instructions": "Nurturing com urgência média"
                },
                
                {
                    "name": "cold_lead_handling",
                    "agent": self.follow_up,
                    "when": "route == 'cold'",
                    "instructions": "Educação e construção de relacionamento"
                }
            ]
        )
    
    def process_lead(self, lead_info: dict, message: str, 
                     user_id: str, session_id: str) -> dict:
        """Processa interação com lead"""
        
        # Atualizar contexto
        self.main_agent.session_state["lead_info"] = lead_info
        
        # Executar agente principal
        response = self.main_agent.run(
            message=message,
            user_id=user_id,
            session_id=session_id,
            stream=False
        )
        
        # Se houver objeção, acionar especialista
        if self._detect_objection(message):
            objection_response = self.objection_handler.run(
                f"Objeção: {message}\nContexto: {lead_info}"
            )
            response = objection_response
        
        # Atualizar estado
        self.main_agent.session_state["interactions"] += 1
        
        return {
            "response": response,
            "next_action": self._determine_next_action(response),
            "lead_stage": self.main_agent.session_state["lead_stage"]
        }
    
    def run_workflow(self, lead_info: dict, initial_message: str) -> dict:
        """Executa workflow completo"""
        
        result = self.workflow.run({
            "lead_info": lead_info,
            "message": initial_message
        })
        
        return result
    
    def _detect_objection(self, message: str) -> bool:
        """Detecta se mensagem contém objeção"""
        objection_keywords = [
            "muito caro", "não temos dinheiro", "não é prioridade",
            "já temos fornecedor", "não confio", "preciso pensar",
            "não é o momento", "orçamento apertado"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in objection_keywords)
    
    def _determine_next_action(self, response: str) -> str:
        """Determina próxima ação baseada na resposta"""
        if "agendar" in response.lower():
            return "schedule_meeting"
        elif "enviar" in response.lower() and "proposta" in response.lower():
            return "send_proposal"
        elif "follow" in response.lower() or "retorno" in response.lower():
            return "schedule_follow_up"
        else:
            return "continue_conversation"

# Exemplo de uso
if __name__ == "__main__":
    # Inicializar sistema
    sdr = SDRSystem(
        supabase_url="postgresql://postgres:senha@db.projeto.supabase.co:5432/postgres",
        google_api_key="sua-api-key-google"
    )
    
    # Processar lead
    lead_info = {
        "empresa": "Metalúrgica Industrial SA",
        "contato": "João Silva",
        "cargo": "Diretor Financeiro",
        "funcionarios": 500,
        "segmento": "Metalurgia",
        "consumo_mensal_kwh": 180000,
        "gasto_mensal_energia": 126000
    }
    
    # Primeira interação
    result = sdr.process_lead(
        lead_info=lead_info,
        message="Olá, vi que vocês trabalham com energia solar. Quanto custa?",
        user_id="lead_001",
        session_id="session_001"
    )
    
    print("Resposta:", result["response"])
    print("Próxima ação:", result["next_action"])
    
    # Ou executar workflow completo
    workflow_result = sdr.run_workflow(
        lead_info=lead_info,
        initial_message="Estamos interessados em reduzir custos com energia"
    )
```

## 📊 9. Métricas e Monitoramento

```python
from agno.agent import Agent
from datetime import datetime
import json

class SDRMetrics:
    def __init__(self, storage):
        self.storage = storage
        
    def track_interaction(self, user_id: str, session_id: str, 
                         interaction_type: str, outcome: str):
        """Registra interação para análise"""
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "type": interaction_type,
            "outcome": outcome
        }
        
        # Salvar no storage
        self.storage.save_metric(metric)
    
    def get_conversion_rate(self, period_days: int = 30) -> float:
        """Calcula taxa de conversão"""
        # Implementar lógica de cálculo
        pass
    
    def get_objection_patterns(self) -> dict:
        """Analisa padrões de objeções"""
        # Implementar análise
        pass
```

## 🎯 10. Melhores Práticas

### 1. **Estrutura de Prompts**
```python
instructions = """
CONTEXTO: {context}
OBJETIVO: {objective}
RESTRIÇÕES: {constraints}
FORMATO: {output_format}

PASSO A PASSO:
1. {step1}
2. {step2}
3. {step3}

EXEMPLOS:
{examples}
"""
```

### 2. **Gestão de Estado**
- Use `session_state` para informações importantes
- Mantenha histórico limitado (5-10 interações)
- Limpe memórias antigas periodicamente

### 3. **Otimização de Performance**
- Use cache para knowledge base
- Implemente batching para múltiplos leads
- Use async para operações paralelas

### 4. **Segurança**
- Nunca exponha API keys no código
- Use variáveis de ambiente
- Implemente rate limiting
- Valide inputs dos usuários

### 5. **Monitoramento**
- Registre todas as interações
- Monitore taxa de sucesso
- Analise padrões de falha
- Ajuste prompts baseado em dados

## 🚀 Conclusão

Este guia fornece uma implementação completa de um sistema SDR autônomo usando o AGnO Framework com:

✅ Agentes inteligentes com Gemini 2.5 Pro
✅ Memória persistente com PostgreSQL/Supabase
✅ Knowledge base com PgVector
✅ Processamento multimodal
✅ Workflows automatizados
✅ Sistema de reasoning para objeções
✅ Métricas e monitoramento

O sistema está pronto para ser adaptado e expandido conforme as necessidades específicas do seu negócio de energia solar.