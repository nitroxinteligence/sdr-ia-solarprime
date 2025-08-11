# 📚 Guia Completo do AGNO Framework

## 🎯 Visão Geral

O AGNO é um framework poderoso para criação de agentes de IA autônomos com capacidades avançadas de memória, reasoning, multimodalidade e integração com bases de conhecimento.

### Componentes Principais
- **Model**: Controla o fluxo de execução
- **Tools**: Habilita interações externas
- **Instructions**: Guia o comportamento do agente
- **Memory**: Armazena e recupera detalhes de interação
- **Knowledge**: Busca informações específicas do domínio
- **Storage**: Mantém histórico de conversas e estado

## 🚀 Instalação e Setup

### Instalação Básica
```bash
pip install agno openai exa-py
```

### Setup com PostgreSQL e pgvector
```bash
# Executar PostgreSQL com pgvector via Docker
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -p 5532:5432 \
  --name pgvector \
  agnohq/pgvector:16
```

### Setup com Supabase
```python
# Configuração com Supabase (usando PostgreSQL)
db_url = "postgresql+psycopg://user:password@db.supabase.co:5432/postgres"
```

---

## 1. 🧠 Criando Agentes com Memória Persistente

### Exemplo Completo: Agente com Memória Multi-Nível

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory import Memory
from agno.storage.postgres import PostgresStorage
from agno.vectordb.pgvector import PgVector

# Configuração do banco de dados
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Configurar storage para sessões
storage = PostgresStorage(
    table_name="agent_sessions",
    db_url=db_url,
    auto_upgrade_schema=True  # Atualiza schema automaticamente
)

# Configurar memória vetorial para memories de longo prazo
memory_db = PgVector(
    table_name="agent_memories",
    db_url=db_url
)

# Criar agente com memória completa
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    
    # Storage de sessões (persistência de conversas)
    storage=storage,
    
    # Memória de trabalho
    memory=Memory(db=memory_db),
    
    # Habilitar memória agnética (personalização)
    enable_agentic_memory=True,
    
    # Habilitar resumos de sessão para conversas longas
    enable_session_summaries=True,
    
    # Adicionar histórico às mensagens
    add_history_to_messages=True,
    num_history_runs=3,  # Últimas 3 interações
    
    # Buscar em sessões anteriores
    read_chat_history=True,
    search_previous_sessions_history=True,
    
    description="Assistente inteligente com memória de longo prazo",
    instructions="""
    Você é um assistente que:
    1. Lembra de conversas anteriores
    2. Personaliza respostas baseado no histórico
    3. Mantém contexto entre sessões
    """
)

# Usar o agente com sessões de diferentes usuários
response = agent.run(
    "Olá, me conte sobre Python",
    user_id="user_123",
    session_id="session_456"
)

# Continuar a conversa mantendo contexto
response = agent.run(
    "Agora me dê exemplos práticos",
    user_id="user_123",
    session_id="session_456"
)

# Acessar memórias armazenadas
memories = agent.memory.get_memories(user_id="user_123")
for memory in memories:
    print(f"Memória: {memory.content}")
```

### Gerenciamento de Estado Persistente

```python
# Agente com estado personalizado
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    storage=storage,
    
    # Estado inicial da sessão
    session_state={
        "user_preferences": {},
        "task_list": [],
        "context_data": {}
    },
    
    # Incluir estado nas mensagens
    add_state_in_messages=True,
    
    instructions="""
    Estado atual:
    - Preferências: {user_preferences}
    - Tarefas: {task_list}
    - Contexto: {context_data}
    
    Atualize o estado conforme necessário.
    """
)

# Executar com estado customizado
response = agent.run(
    "Adicione 'estudar Python' na minha lista de tarefas",
    session_state={
        "task_list": ["revisar código", "fazer testes"]
    }
)
```

---

## 2. 🔗 Integração com pgvector e Supabase

### Setup Completo com Supabase

```python
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge import AgentKnowledge
from agno.agent import Agent

# Conexão com Supabase
SUPABASE_URL = "postgresql+psycopg://postgres:password@db.projectid.supabase.co:5432/postgres"

# Criar vector database com diferentes tipos de busca
vector_db = PgVector(
    table_name="knowledge_base",
    db_url=SUPABASE_URL,
    search_type=SearchType.hybrid,  # Busca híbrida (semântica + keyword)
    distance_metric="cosine",  # Métrica de distância
    enable_reranking=True,  # Habilitar reranking
    prefix_match=True  # Busca por prefixo
)

# Criar base de conhecimento
knowledge = AgentKnowledge(
    vector_db=vector_db,
    num_documents=10,  # Número de documentos a recuperar
    search_strategy="agentic"  # Estratégia de busca inteligente
)

# Adicionar documentos à base
from agno.knowledge.document import Document

# Adicionar documentos individuais
knowledge.add_document(
    Document(
        content="Python é uma linguagem de programação de alto nível...",
        metadata={"category": "programming", "language": "pt-br"}
    )
)

# Agente com knowledge base
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge,
    search_knowledge=True,  # Busca dinâmica
    instructions="Use a base de conhecimento para responder perguntas técnicas"
)
```

### Busca Híbrida Avançada

```python
# Configuração avançada de busca híbrida
hybrid_vector_db = PgVector(
    table_name="hybrid_search",
    db_url=SUPABASE_URL,
    search_type=SearchType.hybrid,
    
    # Configurações de busca vetorial
    vector_weight=0.7,  # Peso da busca semântica
    keyword_weight=0.3,  # Peso da busca por palavra-chave
    
    # Configurações de performance
    use_async=True,  # Operações assíncronas
    connection_pool_size=10,
    
    # Indexação
    create_indexes=True,
    index_type="ivfflat",  # Tipo de índice vetorial
    lists=100  # Número de listas para o índice
)

# Realizar busca customizada
results = await hybrid_vector_db.search(
    query="técnicas de machine learning",
    limit=5,
    filters={"category": "ml"},
    rerank=True
)
```

---

## 3. 🎨 Implementação Multimodal (Imagens, Áudio, Documentos)

### Agente de Análise de Imagens

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils import Image
from agno.tools.dall_e import DallETools

# Agente multimodal com visão e geração de imagem
vision_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),  # Modelo com capacidade de visão
    tools=[DallETools()],  # Ferramenta para gerar imagens
    markdown=True,
    instructions="Analise imagens e gere novas baseado em descrições"
)

# Analisar imagem
response = vision_agent.run(
    "Descreva esta imagem em detalhes e sugira melhorias",
    images=[
        Image(url="https://example.com/product.jpg"),
        Image(path="/local/path/image.png")  # Imagem local
    ]
)

# Gerar nova imagem baseada em análise
response = vision_agent.run(
    "Gere uma versão melhorada da imagem analisada"
)
```

### Agente de Processamento de Áudio

```python
from agno.models.openai import OpenAIChat
from agno.utils import Audio

# Agente com capacidade de áudio
audio_agent = Agent(
    model=OpenAIChat(
        id="gpt-4o",
        audio={
            "voice": "alloy",  # Voz para respostas
            "format": "mp3"
        }
    ),
    instructions="Processe áudio e responda com voz"
)

# Processar arquivo de áudio
response = audio_agent.run(
    "Transcreva e resuma este áudio",
    audio=Audio(path="/path/to/audio.mp3")
)

# Resposta com áudio
audio_response = audio_agent.run(
    "Explique o conceito em áudio",
    return_audio=True
)
```

### Processamento de Documentos (PDF, DOCX)

```python
from agno.knowledge import PDFKnowledgeBase, DocxKnowledgeBase
from agno.document_reader import PDFReader, DocxReader

# Base de conhecimento com PDFs
pdf_knowledge = PDFKnowledgeBase(
    sources=[
        "https://example.com/manual.pdf",
        "/local/path/document.pdf"
    ],
    vector_db=vector_db,
    chunk_size=500,  # Tamanho dos chunks
    chunk_overlap=50  # Sobreposição entre chunks
)

# Leitor de documentos individual
pdf_reader = PDFReader(pdf="/path/to/document.pdf")
docx_reader = DocxReader(file="/path/to/document.docx")

# Processar documentos
pdf_content = pdf_reader.read()
docx_content = docx_reader.read()

# Agente com múltiplas fontes de documentos
doc_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=pdf_knowledge,
    search_knowledge=True,
    instructions="""
    Use os documentos carregados para responder perguntas.
    Sempre cite a fonte e página quando aplicável.
    """
)
```

---

## 4. 🤔 Reasoning com Gemini 2.0 Flash Thinking

### Configuração do Gemini 2.0 Flash com Reasoning

```python
from agno.models.gemini import Gemini
from agno.agent import Agent

# Configurar Gemini 2.0 Flash
gemini_agent = Agent(
    model=Gemini(
        id="gemini-2.0-flash",
        # Configurações de reasoning
        reasoning=True,  # Habilitar reasoning
        temperature=0.7,
        max_tokens=4096,
        
        # Configurações Vertex AI (opcional)
        vertexai=True,
        project_id="your-gcp-project",
        location="us-central1"
    ),
    
    # Habilitar reasoning no agente
    reasoning=True,
    show_full_reasoning=True,  # Mostrar processo de reasoning
    
    instructions="""
    Use reasoning profundo para:
    1. Analisar o problema sistematicamente
    2. Considerar múltiplas perspectivas
    3. Validar cada passo do raciocínio
    4. Fornecer resposta estruturada
    """
)

# Exemplo de uso com reasoning complexo
response = gemini_agent.run(
    """
    Problema: Uma empresa precisa otimizar sua logística de entrega.
    Eles têm 5 centros de distribuição e 100 pontos de entrega.
    Analise e proponha uma solução otimizada.
    """,
    stream=True,
    show_full_reasoning=True
)

# Processar eventos de reasoning
for event in response:
    if event.event == "ReasoningStep":
        print(f"Passo de Reasoning: {event.content}")
    elif event.event == "RunResponseContent":
        print(f"Resposta: {event.content}")
```

### Agente de Reasoning Multi-Step

```python
from agno.tools import Calculator, WebSearch

# Agente com reasoning e ferramentas
reasoning_agent = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    reasoning=True,
    
    # Ferramentas para reasoning
    tools=[Calculator(), WebSearch()],
    
    # Configuração de reasoning
    reasoning_config={
        "max_reasoning_steps": 10,
        "validate_each_step": True,
        "use_tools_in_reasoning": True
    },
    
    instructions="""
    Para problemas complexos:
    1. Decomponha em sub-problemas
    2. Use ferramentas para validar informações
    3. Construa solução iterativamente
    4. Valide resultado final
    """
)

# Problema complexo que requer múltiplos passos
response = reasoning_agent.run(
    """
    Calcule o ROI de um investimento de R$ 100.000 em energia solar,
    considerando economia mensal de R$ 800, vida útil de 25 anos,
    e inflação energética de 8% ao ano.
    """
)
```

---

## 5. 📚 Knowledge Base com Search Avançado

### Sistema de Knowledge Base Completo

```python
from agno.knowledge import AgentKnowledge
from agno.knowledge.document import Document
from agno.vectordb.pgvector import PgVector, SearchType

# Configurar base de conhecimento com search híbrido
knowledge_base = AgentKnowledge(
    vector_db=PgVector(
        table_name="company_knowledge",
        db_url=db_url,
        search_type=SearchType.hybrid
    ),
    
    # Configurações de busca
    num_documents=5,  # Documentos por busca
    search_strategy="agentic",  # Busca inteligente
    
    # Reranking
    enable_reranking=True,
    reranker_model="cohere",
    
    # Configurações de chunking
    chunk_size=1000,
    chunk_overlap=200,
    
    # Metadados
    default_metadata={
        "company": "SolarPrime",
        "version": "v0.2"
    }
)

# Adicionar diferentes tipos de conteúdo
knowledge_base.add_documents([
    Document(
        content="Manual técnico de instalação...",
        metadata={"type": "manual", "category": "technical"}
    ),
    Document(
        content="Políticas de vendas e comissões...",
        metadata={"type": "policy", "category": "sales"}
    ),
    Document(
        content="FAQ para clientes sobre energia solar...",
        metadata={"type": "faq", "category": "customer"}
    )
])

# Agente com knowledge base e search customizado
kb_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    search_knowledge=True,
    
    # Função de search customizada
    custom_retriever=lambda query: knowledge_base.search(
        query=query,
        filters={"category": "technical"},
        hybrid_alpha=0.7  # Peso para busca semântica
    ),
    
    instructions="""
    Use a base de conhecimento para:
    1. Responder perguntas técnicas com precisão
    2. Citar fontes quando relevante
    3. Sugerir documentos relacionados
    """
)
```

### Implementação de RAG Agnético

```python
# RAG Agnético - o agente decide quando buscar
agentic_rag_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    
    # RAG Agnético - busca dinâmica
    search_knowledge=True,
    agentic_search=True,
    
    # Configurações de RAG
    rag_config={
        "search_before_response": True,
        "min_confidence_to_search": 0.7,
        "max_searches_per_query": 3,
        "include_sources": True
    },
    
    instructions="""
    Decida quando buscar na base de conhecimento:
    - Se a pergunta for específica sobre produtos/serviços
    - Se precisar de informações técnicas precisas
    - Se o usuário pedir referências
    
    Não busque para conversas gerais ou cumprimentos.
    """
)
```

---

## 6. 🔄 Mantendo Contexto e Sessões

### Sistema Completo de Sessões Multi-Usuário

```python
from agno.agent import Agent
from agno.storage.postgres import PostgresStorage
from agno.memory import Memory

# Storage para múltiplos usuários
multi_user_storage = PostgresStorage(
    table_name="multi_user_sessions",
    db_url=db_url,
    auto_upgrade_schema=True
)

# Agente com suporte multi-usuário
multi_user_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    storage=multi_user_storage,
    memory=Memory.v2(),  # Versão 2 para multi-usuário
    
    # Configurações de sessão
    add_history_to_messages=True,
    num_history_runs=5,
    
    # Buscar em sessões anteriores
    search_previous_sessions_history=True,
    max_previous_sessions=3,
    
    # Estado da sessão
    session_state={
        "user_profile": {},
        "conversation_topics": [],
        "pending_tasks": []
    },
    
    instructions="""
    Mantenha contexto personalizado para cada usuário:
    1. Lembre de preferências individuais
    2. Continue conversas anteriores naturalmente
    3. Sugira retomar tópicos pendentes
    """
)

# Gerenciar múltiplas sessões
users = ["alice", "bob", "charlie"]

for user in users:
    # Criar ou continuar sessão
    response = multi_user_agent.run(
        f"Olá, sou {user}. Vamos continuar nossa conversa?",
        user_id=user,
        session_id=f"{user}_session_001"
    )
    
    # Acessar histórico do usuário
    history = multi_user_storage.get_session_history(
        user_id=user,
        limit=10
    )
```

### Gerenciamento Avançado de Estado

```python
# Agente com estado complexo e transições
stateful_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    storage=storage,
    
    # Estado inicial complexo
    session_state={
        "workflow_stage": "initial",
        "collected_data": {},
        "validation_status": {},
        "next_steps": []
    },
    
    # Incluir estado no contexto
    add_state_in_messages=True,
    
    # Função para atualizar estado
    state_updater=lambda state, response: {
        **state,
        "workflow_stage": determine_next_stage(response),
        "collected_data": extract_data(response)
    },
    
    instructions="""
    Gerencie o fluxo de trabalho baseado no estado:
    
    Stage: {workflow_stage}
    Data: {collected_data}
    Status: {validation_status}
    
    Guie o usuário pelo processo apropriado.
    """
)

# Função auxiliar para transições de estado
def determine_next_stage(response):
    if "dados completos" in response.lower():
        return "validation"
    elif "validado" in response.lower():
        return "processing"
    elif "processado" in response.lower():
        return "complete"
    return "collecting"
```

---

## 7. 💾 Storage com PostgreSQL

### Configuração Completa de Storage

```python
from agno.storage.postgres import PostgresStorage
from agno.storage.sqlite import SqliteStorage
import asyncio

# Storage PostgreSQL com configurações avançadas
pg_storage = PostgresStorage(
    table_name="agent_data",
    db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    
    # Configurações de schema
    auto_upgrade_schema=True,
    schema_version="2.0",
    
    # Pool de conexões
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    
    # Configurações de performance
    use_async=True,
    batch_size=100,
    
    # Backup e recuperação
    enable_backup=True,
    backup_interval=3600  # 1 hora
)

# Storage SQLite para desenvolvimento
dev_storage = SqliteStorage(
    db_file="agent_dev.db",
    auto_upgrade_schema=True
)

# Agent com storage e recuperação de dados
storage_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    storage=pg_storage,
    
    # Configurações de persistência
    save_runs=True,
    save_messages=True,
    save_tool_calls=True,
    
    instructions="Mantenha registro completo de todas as interações"
)

# Operações com storage
async def manage_storage():
    # Salvar run
    run_id = await pg_storage.save_run(
        user_id="user_123",
        session_id="session_456",
        messages=[...],
        metadata={"source": "web", "priority": "high"}
    )
    
    # Recuperar sessões
    sessions = await pg_storage.get_sessions(
        user_id="user_123",
        limit=10,
        order_by="created_at DESC"
    )
    
    # Buscar por metadados
    priority_runs = await pg_storage.search_runs(
        filters={"priority": "high"},
        date_range=("2024-01-01", "2024-12-31")
    )
    
    # Exportar dados
    export_data = await pg_storage.export_to_json(
        user_id="user_123",
        include_metadata=True
    )
    
    # Limpar dados antigos
    await pg_storage.cleanup_old_sessions(
        days_to_keep=30,
        keep_summaries=True
    )

# Executar operações
asyncio.run(manage_storage())
```

### Monitoramento e Análise de Storage

```python
# Sistema de monitoramento de storage
class StorageMonitor:
    def __init__(self, storage: PostgresStorage):
        self.storage = storage
    
    async def get_statistics(self):
        """Obter estatísticas de uso"""
        stats = await self.storage.get_stats()
        return {
            "total_sessions": stats["session_count"],
            "total_messages": stats["message_count"],
            "storage_size_mb": stats["storage_size"] / 1024 / 1024,
            "average_session_length": stats["avg_session_messages"],
            "active_users": stats["unique_users"]
        }
    
    async def analyze_usage_patterns(self):
        """Analisar padrões de uso"""
        patterns = await self.storage.analyze_patterns()
        return {
            "peak_hours": patterns["peak_usage_hours"],
            "common_topics": patterns["frequent_topics"],
            "user_engagement": patterns["engagement_metrics"]
        }
    
    async def generate_report(self):
        """Gerar relatório completo"""
        stats = await self.get_statistics()
        patterns = await self.analyze_usage_patterns()
        
        return {
            "statistics": stats,
            "patterns": patterns,
            "recommendations": self.get_recommendations(stats, patterns)
        }
    
    def get_recommendations(self, stats, patterns):
        """Gerar recomendações baseadas em análise"""
        recommendations = []
        
        if stats["storage_size_mb"] > 1000:
            recommendations.append("Considere arquivar sessões antigas")
        
        if stats["average_session_length"] > 50:
            recommendations.append("Habilite resumos de sessão para economizar tokens")
        
        return recommendations

# Usar monitor
monitor = StorageMonitor(pg_storage)
report = await monitor.generate_report()
print(report)
```

---

## 🎯 Exemplo Completo: Agente SDR Inteligente

```python
from agno.agent import Agent
from agno.models.gemini import Gemini
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from agno.memory import Memory
from agno.knowledge import AgentKnowledge
from agno.vectordb.pgvector import PgVector, SearchType
from agno.tools import EmailTools, CalendarTools, CRMTools

# Configuração completa para SDR IA
class SolarPrimeSDR:
    def __init__(self, db_url: str):
        # Configurar storage
        self.storage = PostgresStorage(
            table_name="sdr_sessions",
            db_url=db_url,
            auto_upgrade_schema=True
        )
        
        # Configurar knowledge base
        self.knowledge = AgentKnowledge(
            vector_db=PgVector(
                table_name="solar_knowledge",
                db_url=db_url,
                search_type=SearchType.hybrid
            ),
            num_documents=5
        )
        
        # Criar agente principal
        self.agent = self._create_agent()
    
    def _create_agent(self):
        return Agent(
            # Modelo com reasoning
            model=Gemini(
                id="gemini-2.0-flash",
                reasoning=True
            ),
            
            # Storage e memória
            storage=self.storage,
            memory=Memory.v2(),
            enable_agentic_memory=True,
            enable_session_summaries=True,
            
            # Knowledge base
            knowledge=self.knowledge,
            search_knowledge=True,
            
            # Ferramentas
            tools=[
                EmailTools(),
                CalendarTools(),
                CRMTools()
            ],
            
            # Estado da sessão
            session_state={
                "lead_stage": "initial_contact",
                "lead_data": {},
                "interaction_history": [],
                "next_actions": []
            },
            
            # Configurações
            add_history_to_messages=True,
            num_history_runs=5,
            add_state_in_messages=True,
            
            # Instruções
            instructions="""
            Você é um SDR especialista em energia solar da SolarPrime.
            
            Objetivos:
            1. Qualificar leads interessados em energia solar
            2. Identificar necessidades e pain points
            3. Agendar reuniões com consultores
            4. Manter follow-up inteligente
            
            Use o conhecimento sobre:
            - Benefícios da energia solar
            - Economia na conta de luz
            - Sustentabilidade
            - Incentivos fiscais
            
            Estado atual do lead: {lead_stage}
            Dados coletados: {lead_data}
            
            Sempre:
            - Seja consultivo, não pushy
            - Personalize baseado no histórico
            - Sugira próximos passos claros
            """
        )
    
    async def process_lead(self, lead_info: dict, message: str):
        """Processar interação com lead"""
        response = await self.agent.run(
            message=message,
            user_id=lead_info["email"],
            session_id=f"lead_{lead_info['id']}",
            session_state={
                "lead_data": lead_info,
                "lead_stage": self.determine_stage(lead_info)
            }
        )
        
        return response
    
    def determine_stage(self, lead_info: dict) -> str:
        """Determinar estágio do lead"""
        if not lead_info.get("contacted"):
            return "initial_contact"
        elif not lead_info.get("qualified"):
            return "qualification"
        elif not lead_info.get("meeting_scheduled"):
            return "scheduling"
        else:
            return "nurturing"

# Usar o SDR
sdr = SolarPrimeSDR(db_url="postgresql+psycopg://ai:ai@localhost:5532/ai")

# Processar lead
lead = {
    "id": "12345",
    "name": "João Silva",
    "email": "joao@example.com",
    "phone": "11999999999",
    "monthly_bill": 500,
    "city": "São Paulo"
}

response = await sdr.process_lead(
    lead_info=lead,
    message="Olá! Vi que você tem interesse em energia solar. Sua conta de luz é de R$ 500/mês?"
)
```

---

## 📊 Métricas e Monitoramento

```python
# Sistema de métricas para agentes
class AgentMetrics:
    def __init__(self, agent: Agent, storage: PostgresStorage):
        self.agent = agent
        self.storage = storage
    
    async def collect_metrics(self):
        """Coletar métricas de performance"""
        return {
            "response_time": await self.measure_response_time(),
            "token_usage": await self.calculate_token_usage(),
            "success_rate": await self.calculate_success_rate(),
            "user_satisfaction": await self.get_satisfaction_score()
        }
    
    async def measure_response_time(self):
        """Medir tempo médio de resposta"""
        runs = await self.storage.get_recent_runs(limit=100)
        times = [run.duration for run in runs]
        return sum(times) / len(times) if times else 0
    
    async def calculate_token_usage(self):
        """Calcular uso de tokens"""
        runs = await self.storage.get_recent_runs(limit=100)
        total_tokens = sum(run.token_count for run in runs)
        return {
            "total": total_tokens,
            "average_per_run": total_tokens / len(runs) if runs else 0
        }
    
    async def generate_dashboard(self):
        """Gerar dashboard de métricas"""
        metrics = await self.collect_metrics()
        
        return {
            "performance": {
                "avg_response_time": f"{metrics['response_time']:.2f}s",
                "tokens_per_run": metrics['token_usage']['average_per_run']
            },
            "quality": {
                "success_rate": f"{metrics['success_rate']:.1%}",
                "satisfaction": metrics['user_satisfaction']
            },
            "recommendations": self.get_optimization_suggestions(metrics)
        }
```

---

## 🚀 Best Practices

### 1. **Otimização de Performance**
```python
# Use cache para knowledge base
knowledge_base.enable_caching(ttl=3600)

# Batch operations
await storage.batch_save(runs)

# Async operations
async with storage.async_session() as session:
    await session.save_run(...)
```

### 2. **Segurança**
```python
# Sanitize inputs
from agno.security import sanitize_input
clean_input = sanitize_input(user_message)

# Criptografia de dados sensíveis
storage.enable_encryption(key=os.getenv("ENCRYPTION_KEY"))
```

### 3. **Escalabilidade**
```python
# Pool de conexões
storage.configure_pool(
    min_size=5,
    max_size=20,
    timeout=30
)

# Rate limiting
agent.configure_rate_limit(
    requests_per_minute=60,
    burst_size=10
)
```

### 4. **Debugging e Logs**
```python
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
agent.enable_debug_mode()

# Rastrear eventos
agent.on_event("reasoning_step", lambda e: print(f"Reasoning: {e}"))
agent.on_event("tool_call", lambda e: print(f"Tool: {e}"))
```

---

## 📚 Recursos Adicionais

- **Documentação Oficial**: https://docs.agno.com
- **Exemplos**: https://github.com/agnohq/agno-examples
- **Community**: https://discord.gg/agno
- **Support**: support@agno.com

## 🎓 Próximos Passos

1. Experimente com diferentes modelos e configurações
2. Implemente knowledge bases específicas do domínio
3. Integre com sistemas existentes via ferramentas customizadas
4. Monitore e otimize baseado em métricas
5. Scale com múltiplos agentes especializados

---

*Última atualização: Janeiro 2025*
*Framework Version: AGNO v0.2*