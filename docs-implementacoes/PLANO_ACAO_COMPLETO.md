# 🚀 Plano de Ação Completo - Agente SDR SolarPrime

## 📌 Visão Geral do Projeto

### Objetivo Principal
Desenvolver um agente de IA para automação completa do processo de vendas de energia solar via WhatsApp, desde a qualificação inicial até o agendamento de reuniões no CRM.

### Stack Tecnológico
- **Framework IA**: AGnO Framework (Python)
- **LLM**: Google Gemini 2.5 Pro
- **RAG/Database**: Supabase + pgvector
- **WhatsApp**: Evolution API
- **CRM**: Kommo (amoCRM)
- **Backend**: FastAPI + Uvicorn
- **Queue**: Redis + Celery
- **Deploy**: Ubuntu 22.04 + Docker

### Timeline Total: 14 dias úteis

---

## 📊 Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────┐
│                   CAMADA DE APRESENTAÇÃO                 │
├─────────────────────────────────────────────────────────┤
│  WhatsApp Business  │  Kommo CRM  │  Dashboard Admin    │
├─────────────────────────────────────────────────────────┤
│                    CAMADA DE APLICAÇÃO                   │
├─────────────────────────────────────────────────────────┤
│     FastAPI        │    Webhooks    │    REST API       │
├─────────────────────────────────────────────────────────┤
│                    CAMADA DE NEGÓCIO                     │
├─────────────────────────────────────────────────────────┤
│  AGnO Agent  │  RAG System  │  Qualification  │  Tasks  │
├─────────────────────────────────────────────────────────┤
│                     CAMADA DE DADOS                      │
├─────────────────────────────────────────────────────────┤
│    Supabase    │    Redis    │    pgvector    │  Logs  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Fase 1: Core do Agente de IA (Dias 1-3)

### Objetivo
Criar o agente base com AGnO Framework, integrado com Gemini 2.5 Pro, com prompts especializados para vendas de energia solar.

### 1.1 Setup Inicial do Projeto

```bash
# Criar estrutura do projeto
mkdir -p sdr-solarprime/{agents,services,models,config,utils,tests}
cd sdr-solarprime

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências base
pip install agno google-generativeai pydantic python-dotenv
```

### 1.2 Configuração do AGnO Framework

```python
# config/agent_config.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class AgentConfig(BaseModel):
    """Configuração do Agente SDR"""
    name: str = "Leonardo SolarPrime"
    role: str = "Consultor de Energia Solar"
    model: str = "gemini-2.5-pro"
    temperature: float = 0.7
    max_tokens: int = 2048
    
    personality_traits: Dict[str, Any] = {
        "tom": "profissional e amigável",
        "expertise": "energia solar e economia",
        "objetivo": "qualificar leads e agendar reuniões"
    }
```

### 1.3 Implementação do Agente Base

```python
# agents/sdr_agent.py
from agno import Agent, Message, Tool
from agno.models import GeminiModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SDRAgent(Agent):
    """Agente de vendas especializado em energia solar"""
    
    def __init__(self, config: AgentConfig):
        # Configurar modelo Gemini
        self.llm = GeminiModel(
            api_key=settings.GEMINI_API_KEY,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        
        # Inicializar agente
        super().__init__(
            name=config.name,
            model=self.llm,
            system_prompt=self._build_system_prompt(config),
            tools=self._setup_tools()
        )
        
        self.config = config
        self.conversation_state = {}
    
    def _build_system_prompt(self, config: AgentConfig) -> str:
        """Constrói o prompt do sistema"""
        return f"""
Você é {config.name}, um {config.role} da SolarPrime.

PERSONALIDADE:
- Tom: {config.personality_traits['tom']}
- Expertise: {config.personality_traits['expertise']}
- Objetivo: {config.personality_traits['objetivo']}

CONTEXTO:
A SolarPrime é líder em soluções de energia solar em Pernambuco, oferecendo:
1. Usinas solares próprias ou em terrenos parceiros
2. Compra de energia com desconto garantido
3. Zero investimento inicial
4. Economia de até 20% na conta de luz

PROCESSO DE QUALIFICAÇÃO:
1. Identificação: Nome e empresa do lead
2. Descoberta: Qual solução se adequa melhor
3. Valor: Análise da conta de luz atual
4. Concorrência: Verificar se já tem desconto
5. Agendamento: Marcar reunião se qualificado

REGRAS:
- Seja sempre cordial e profissional
- Use emojis com moderação (☀️ 💰 ✅)
- Responda de forma concisa e clara
- Foque em benefícios e economia
- Não mencione preços específicos
"""
    
    def _setup_tools(self) -> list:
        """Configura ferramentas do agente"""
        return [
            Tool(
                name="analyze_energy_bill",
                description="Analisa conta de energia para calcular economia",
                function=self._analyze_energy_bill
            ),
            Tool(
                name="check_qualification",
                description="Verifica se lead está qualificado",
                function=self._check_qualification
            ),
            Tool(
                name="schedule_meeting",
                description="Agenda reunião com consultor",
                function=self._schedule_meeting
            )
        ]
```

### 1.4 Sistema de Prompts Especializados

```python
# agents/prompts/sales_prompts.py

QUALIFICATION_PROMPTS = {
    "greeting": """
Olá! 👋 Seja muito bem-vindo(a) à SolarPrime!

Eu sou o {agent_name}, consultor especializado em energia solar. 
Estou aqui para ajudar você a economizar até 20% na sua conta de luz! ☀️💰

Antes de começarmos, posso saber seu nome?
""",
    
    "solution_discovery": """
Prazer, {lead_name}! 😊

Deixa eu entender melhor como posso te ajudar...

Você está buscando:
1️⃣ Instalar uma usina solar em sua propriedade
2️⃣ Economizar através da nossa fazenda solar (sem instalação)
3️⃣ Solução para sua empresa

Qual opção mais se adequa ao seu perfil?
""",
    
    "value_assessment": """
Excelente escolha! ✅

Para eu calcular exatamente quanto você vai economizar, 
preciso saber: qual o valor médio da sua conta de luz?

💡 Dica: Você pode me enviar uma foto da conta que eu analiso para você!
""",
    
    "competitor_check": """
Ótimo! Com esse valor, consigo garantir uma economia bem interessante! 📊

Só uma pergunta rápida: você já tem algum desconto na conta de luz 
ou já foi procurado por outras empresas de energia?
""",
    
    "meeting_proposal": """
{lead_name}, baseado no que conversamos, posso garantir que temos 
a solução perfeita para você economizar! 🎯

Que tal agendarmos uma reunião rápida para eu te mostrar:
✅ Quanto você vai economizar por mês
✅ Como funciona nossa solução
✅ Todas as garantias e benefícios

Você prefere esta semana ou a próxima?
"""
}
```

### 1.5 Sistema de Memória e Contexto

```python
# agents/memory/conversation_memory.py
from typing import Dict, List, Any
from datetime import datetime
import json

class ConversationMemory:
    """Sistema de memória para manter contexto das conversas"""
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
        self.lead_profiles: Dict[str, Dict] = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """Adiciona mensagem à memória"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        })
    
    def update_lead_profile(self, session_id: str, data: Dict):
        """Atualiza perfil do lead"""
        if session_id not in self.lead_profiles:
            self.lead_profiles[session_id] = {
                "created_at": datetime.now().isoformat(),
                "qualification_stage": "initial"
            }
        
        self.lead_profiles[session_id].update(data)
    
    def get_context(self, session_id: str) -> Dict:
        """Recupera contexto completo da conversa"""
        return {
            "messages": self.conversations.get(session_id, []),
            "profile": self.lead_profiles.get(session_id, {}),
            "message_count": len(self.conversations.get(session_id, []))
        }
    
    def get_stage(self, session_id: str) -> str:
        """Retorna estágio atual da qualificação"""
        profile = self.lead_profiles.get(session_id, {})
        return profile.get("qualification_stage", "initial")
```

### 1.6 Testes do Agente

```python
# tests/test_agent.py
import pytest
from agents.sdr_agent import SDRAgent
from config.agent_config import AgentConfig

@pytest.fixture
def agent():
    config = AgentConfig()
    return SDRAgent(config)

def test_agent_initialization(agent):
    """Testa inicialização do agente"""
    assert agent.name == "Leonardo SolarPrime"
    assert agent.config.temperature == 0.7

async def test_greeting_response(agent):
    """Testa resposta de saudação"""
    response = await agent.process_message(
        "Olá, gostaria de saber sobre energia solar"
    )
    
    assert "bem-vindo" in response.content.lower()
    assert "SolarPrime" in response.content

async def test_qualification_flow(agent):
    """Testa fluxo de qualificação"""
    # Simular conversa completa
    messages = [
        "Oi",
        "Meu nome é João",
        "Quero economizar na conta de luz",
        "Minha conta é de R$ 500",
        "Não tenho desconto"
    ]
    
    for msg in messages:
        response = await agent.process_message(msg)
        assert response.content is not None
```

### 📋 Checklist Fase 1

- [ ] Ambiente Python 3.11 configurado
- [ ] AGnO Framework instalado
- [ ] Estrutura de pastas criada
- [ ] Configuração do agente implementada
- [ ] Sistema de prompts especializado
- [ ] Memória de conversação funcionando
- [ ] Integração com Gemini testada
- [ ] Testes unitários passando
- [ ] Logs configurados

---

## 💾 Fase 2: RAG com Supabase (Dias 4-5)

### Objetivo
Implementar sistema RAG (Retrieval Augmented Generation) usando Supabase e pgvector para o agente acessar conhecimento sobre energia solar.

### 2.1 Setup Supabase

```sql
-- migrations/001_create_knowledge_base.sql

-- Habilitar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de documentos
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de embeddings
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para busca vetorial
CREATE INDEX embeddings_embedding_idx ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Função de busca por similaridade
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    filter_category text DEFAULT NULL
)
RETURNS TABLE (
    document_id UUID,
    chunk_text TEXT,
    similarity float,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.document_id,
        e.chunk_text,
        1 - (e.embedding <=> query_embedding) as similarity,
        d.metadata
    FROM embeddings e
    JOIN documents d ON d.id = e.document_id
    WHERE (filter_category IS NULL OR d.category = filter_category)
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### 2.2 Cliente Supabase

```python
# services/supabase_service.py
from supabase import create_client, Client
from typing import List, Dict, Optional
import numpy as np
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    """Serviço para interação com Supabase"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    async def store_document(
        self,
        title: str,
        content: str,
        category: str,
        metadata: Dict = None
    ) -> str:
        """Armazena documento na base de conhecimento"""
        try:
            # Inserir documento
            result = self.client.table('documents').insert({
                'title': title,
                'content': content,
                'category': category,
                'metadata': metadata or {}
            }).execute()
            
            document_id = result.data[0]['id']
            
            # Processar chunks e embeddings
            await self._process_document_chunks(document_id, content)
            
            logger.info(f"Documento armazenado: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Erro ao armazenar documento: {str(e)}")
            raise
    
    async def search_similar(
        self,
        query: str,
        k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Busca documentos similares"""
        # Gerar embedding da query
        query_embedding = await self._generate_embedding(query)
        
        # Buscar no banco
        result = self.client.rpc(
            'search_documents',
            {
                'query_embedding': query_embedding.tolist(),
                'match_count': k,
                'filter_category': category
            }
        ).execute()
        
        return result.data
```

### 2.3 Sistema de Embeddings

```python
# services/embeddings_service.py
import google.generativeai as genai
from typing import List, Tuple
import numpy as np
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

class EmbeddingsService:
    """Serviço para gerar embeddings de texto"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = 'models/text-embedding-004'
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Configurar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=self._token_length,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def _token_length(self, text: str) -> int:
        """Calcula número de tokens"""
        return len(self.tokenizer.encode(text))
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Gera embedding para um texto"""
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return np.array(result['embedding'])
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {str(e)}")
            raise
    
    def split_text(self, text: str) -> List[str]:
        """Divide texto em chunks"""
        return self.text_splitter.split_text(text)
    
    async def process_document(
        self,
        content: str
    ) -> List[Tuple[str, np.ndarray]]:
        """Processa documento completo em chunks com embeddings"""
        chunks = self.split_text(content)
        embeddings = []
        
        for chunk in chunks:
            embedding = await self.generate_embedding(chunk)
            embeddings.append((chunk, embedding))
        
        return embeddings
```

### 2.4 Pipeline de Ingestão

```python
# services/knowledge_ingestion.py
from typing import List, Dict
import asyncio
from services.supabase_service import SupabaseService
from services.embeddings_service import EmbeddingsService
import logging

logger = logging.getLogger(__name__)

class KnowledgeIngestionPipeline:
    """Pipeline para ingerir conhecimento no sistema RAG"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.embeddings = EmbeddingsService()
    
    async def ingest_documents(self, documents: List[Dict]):
        """Ingere múltiplos documentos"""
        tasks = []
        for doc in documents:
            task = self.ingest_single_document(
                title=doc['title'],
                content=doc['content'],
                category=doc['category'],
                metadata=doc.get('metadata', {})
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        logger.info(f"Ingeridos {len(results)} documentos")
        return results
    
    async def ingest_single_document(
        self,
        title: str,
        content: str,
        category: str,
        metadata: Dict = None
    ):
        """Ingere um único documento"""
        # Armazenar documento
        doc_id = await self.supabase.store_document(
            title=title,
            content=content,
            category=category,
            metadata=metadata
        )
        
        # Processar embeddings
        chunks_with_embeddings = await self.embeddings.process_document(content)
        
        # Armazenar embeddings
        for idx, (chunk, embedding) in enumerate(chunks_with_embeddings):
            await self.supabase.store_embedding(
                document_id=doc_id,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=embedding
            )
        
        return doc_id
```

### 2.5 Base de Conhecimento Inicial

```python
# scripts/populate_knowledge_base.py

SOLAR_KNOWLEDGE = [
    {
        "title": "Benefícios da Energia Solar",
        "category": "beneficios",
        "content": """
A energia solar oferece diversos benefícios:

1. ECONOMIA GARANTIDA
- Redução de até 95% na conta de luz
- Proteção contra aumentos tarifários
- Retorno do investimento em 3-5 anos
- 25 anos de energia gratuita após payback

2. SUSTENTABILIDADE
- Energia 100% limpa e renovável
- Reduz emissão de CO2
- Contribui para um planeta mais sustentável
- Valoriza o imóvel em até 10%

3. INDEPENDÊNCIA ENERGÉTICA
- Menos dependência da rede elétrica
- Proteção contra apagões (com bateria)
- Controle sobre seu consumo
- Possibilidade de vender excedente
"""
    },
    {
        "title": "Tipos de Sistemas Solares",
        "category": "sistemas",
        "content": """
SISTEMAS ON-GRID (Conectado à Rede)
- Mais comum e econômico
- Injeta energia excedente na rede
- Gera créditos para usar à noite
- Não funciona em quedas de energia

SISTEMAS OFF-GRID (Isolado)
- Independente da rede elétrica
- Usa baterias para armazenamento
- Ideal para locais remotos
- Maior investimento inicial

SISTEMAS HÍBRIDOS
- Combina on-grid e off-grid
- Máxima segurança energética
- Funciona mesmo sem rede
- Solução mais completa
"""
    },
    {
        "title": "Processo de Instalação",
        "category": "instalacao",
        "content": """
ETAPAS DA INSTALAÇÃO SOLAR:

1. ANÁLISE TÉCNICA (1-2 dias)
- Visita técnica ao local
- Análise do telhado e estrutura
- Estudo de sombreamento
- Dimensionamento do sistema

2. PROJETO E HOMOLOGAÇÃO (15-30 dias)
- Elaboração do projeto elétrico
- Submissão à concessionária
- Aguardo da aprovação
- Preparação dos equipamentos

3. INSTALAÇÃO (2-3 dias)
- Instalação dos painéis
- Montagem do inversor
- Cabeamento e conexões
- Testes de funcionamento

4. ATIVAÇÃO (5-10 dias)
- Vistoria da concessionária
- Troca do medidor
- Ativação do sistema
- Início da geração
"""
    }
]

async def populate_knowledge_base():
    """Popula base de conhecimento inicial"""
    pipeline = KnowledgeIngestionPipeline()
    await pipeline.ingest_documents(SOLAR_KNOWLEDGE)
    print("✅ Base de conhecimento populada com sucesso!")

if __name__ == "__main__":
    asyncio.run(populate_knowledge_base())
```

### 2.6 Integração RAG com Agente

```python
# agents/tools/rag_tool.py
from agno import Tool
from services.supabase_service import SupabaseService
from typing import List, Dict

class RAGTool(Tool):
    """Ferramenta RAG para o agente"""
    
    def __init__(self):
        super().__init__(
            name="search_knowledge",
            description="Busca informações na base de conhecimento sobre energia solar"
        )
        self.supabase = SupabaseService()
    
    async def execute(self, query: str, category: Optional[str] = None) -> str:
        """Executa busca na base de conhecimento"""
        # Buscar documentos relevantes
        results = await self.supabase.search_similar(
            query=query,
            k=3,
            category=category
        )
        
        if not results:
            return "Não encontrei informações específicas sobre isso."
        
        # Formatar resposta
        context = "\n\n".join([
            f"[{r['similarity']:.2f}] {r['chunk_text']}"
            for r in results
        ])
        
        return f"Baseado em nosso conhecimento:\n\n{context}"

# Atualizar agente para incluir RAG
class SDRAgentWithRAG(SDRAgent):
    def _setup_tools(self) -> list:
        tools = super()._setup_tools()
        tools.append(RAGTool())
        return tools
```

### 📋 Checklist Fase 2

- [ ] Supabase configurado com pgvector
- [ ] Migrações do banco executadas
- [ ] Sistema de embeddings funcionando
- [ ] Pipeline de ingestão implementado
- [ ] Base de conhecimento populada
- [ ] RAG integrado ao agente
- [ ] Busca por similaridade testada
- [ ] Performance de busca otimizada

---

## 🔌 Fase 3: API e Webhooks Base (Dias 6-7)

### Objetivo
Criar API FastAPI robusta com sistema de filas para processar mensagens assincronamente.

### 3.1 Estrutura FastAPI

```python
# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from api.routes import webhooks, health, admin
from services.redis_service import RedisService
from config.settings import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação SDR SolarPrime...")
    
    # Inicializar Redis
    redis = RedisService()
    await redis.connect()
    
    # Inicializar agente
    from agents.sdr_agent import SDRAgentWithRAG
    app.state.agent = SDRAgentWithRAG(AgentConfig())
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")
    await redis.disconnect()

# Criar aplicação
app = FastAPI(
    title="SDR IA SolarPrime",
    description="API do agente de vendas inteligente para energia solar",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
```

### 3.2 Sistema de Filas com Celery

```python
# services/celery_app.py
from celery import Celery
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Criar app Celery
celery_app = Celery(
    'sdr_solarprime',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configurações
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutos
    task_soft_time_limit=240,  # 4 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configurar beat schedule para tarefas periódicas
celery_app.conf.beat_schedule = {
    'send-weekly-report': {
        'task': 'services.tasks.send_weekly_report',
        'schedule': crontab(
            hour=9,
            minute=0,
            day_of_week=1  # Segunda-feira
        ),
    },
    'cleanup-old-conversations': {
        'task': 'services.tasks.cleanup_old_conversations',
        'schedule': crontab(hour=3, minute=0),  # 3h da manhã
    },
    'check-pending-followups': {
        'task': 'services.tasks.check_pending_followups',
        'schedule': 60.0,  # A cada minuto
    },
}
```

### 3.3 Tarefas Assíncronas

```python
# services/tasks.py
from services.celery_app import celery_app
from typing import Dict, Any
import logging
from services.message_processor import MessageProcessor
from services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_whatsapp_message(self, message_data: Dict[str, Any]):
    """Processa mensagem do WhatsApp de forma assíncrona"""
    try:
        logger.info(f"Processando mensagem: {message_data.get('id')}")
        
        processor = MessageProcessor()
        result = processor.process(message_data)
        
        logger.info(f"Mensagem processada com sucesso: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        
        # Retry com backoff exponencial
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

@celery_app.task
def send_weekly_report():
    """Envia relatório semanal"""
    try:
        generator = ReportGenerator()
        report = generator.generate_weekly_report()
        
        # Enviar via WhatsApp
        from services.whatsapp_service import WhatsAppService
        whatsapp = WhatsAppService()
        whatsapp.send_message(
            settings.WHATSAPP_GROUP_ID,
            report
        )
        
        logger.info("Relatório semanal enviado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao enviar relatório: {str(e)}")
        raise

@celery_app.task
def schedule_follow_up(lead_id: str, delay_minutes: int):
    """Agenda follow-up para um lead"""
    from datetime import datetime, timedelta
    
    # Agendar tarefa para executar após delay
    eta = datetime.now() + timedelta(minutes=delay_minutes)
    
    send_follow_up_message.apply_async(
        args=[lead_id],
        eta=eta
    )
    
    logger.info(f"Follow-up agendado para lead {lead_id} em {delay_minutes} minutos")

@celery_app.task
def send_follow_up_message(lead_id: str):
    """Envia mensagem de follow-up"""
    try:
        # Buscar dados do lead
        from services.lead_service import LeadService
        lead_service = LeadService()
        lead = lead_service.get_lead(lead_id)
        
        if not lead:
            logger.error(f"Lead {lead_id} não encontrado")
            return
        
        # Enviar mensagem personalizada
        from services.whatsapp_service import WhatsAppService
        whatsapp = WhatsAppService()
        
        message = f"""Oi {lead['name']}! 👋

Percebi que paramos nossa conversa sobre energia solar.

Ainda tem interesse em economizar na conta de luz? 
Posso te mostrar quanto você economizaria! 💰☀️"""
        
        whatsapp.send_message(lead['phone'], message)
        
        # Atualizar status do lead
        lead_service.update_lead(lead_id, {
            'last_follow_up': datetime.now(),
            'follow_up_count': lead.get('follow_up_count', 0) + 1
        })
        
    except Exception as e:
        logger.error(f"Erro ao enviar follow-up: {str(e)}")
        raise
```

### 3.4 Redis Service

```python
# services/redis_service.py
import redis.asyncio as redis
from typing import Optional, Any, Dict
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Serviço para interação com Redis"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {str(e)}")
            raise
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Erro ao obter do cache: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ):
        """Armazena valor no cache"""
        try:
            json_value = json.dumps(value)
            await self.redis.set(key, json_value, ex=expire)
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {str(e)}")
    
    async def delete(self, key: str):
        """Remove valor do cache"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {str(e)}")
    
    async def get_conversation_state(self, session_id: str) -> Dict:
        """Obtém estado da conversa"""
        key = f"conversation:{session_id}"
        state = await self.get(key)
        return state or {"stage": "initial", "messages": []}
    
    async def save_conversation_state(
        self,
        session_id: str,
        state: Dict,
        ttl: int = 86400  # 24 horas
    ):
        """Salva estado da conversa"""
        key = f"conversation:{session_id}"
        await self.set(key, state, expire=ttl)
```

### 3.5 Endpoints Base

```python
# api/routes/webhooks.py
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from typing import Dict, Any
import logging
from services.tasks import process_whatsapp_message

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Webhook para receber mensagens do WhatsApp"""
    try:
        # Obter dados da requisição
        data = await request.json()
        
        # Log para debug
        logger.info(f"Webhook recebido: {data}")
        
        # Validar dados
        if not data.get("event") or not data.get("instance"):
            raise HTTPException(status_code=400, detail="Dados inválidos")
        
        # Processar diferentes tipos de eventos
        event_type = data.get("event")
        
        if event_type == "messages.upsert":
            # Nova mensagem recebida
            message = data.get("data", {})
            
            # Adicionar à fila de processamento
            process_whatsapp_message.delay(message)
            
            return {"status": "queued", "message": "Mensagem adicionada à fila"}
        
        elif event_type == "messages.update":
            # Atualização de status de mensagem
            logger.info(f"Status atualizado: {data}")
            return {"status": "ok"}
        
        else:
            logger.warning(f"Evento não tratado: {event_type}")
            return {"status": "ignored", "event": event_type}
            
    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# api/routes/health.py
from fastapi import APIRouter, Depends
from typing import Dict
import asyncio
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check() -> Dict:
    """Verifica saúde da aplicação"""
    checks = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Verificar Redis
    try:
        from services.redis_service import RedisService
        redis = RedisService()
        await redis.connect()
        await redis.redis.ping()
        await redis.disconnect()
        checks["checks"]["redis"] = "ok"
    except:
        checks["checks"]["redis"] = "error"
        checks["status"] = "unhealthy"
    
    # Verificar Supabase
    try:
        from services.supabase_service import SupabaseService
        supabase = SupabaseService()
        await supabase.health_check()
        checks["checks"]["supabase"] = "ok"
    except:
        checks["checks"]["supabase"] = "error"
        checks["status"] = "unhealthy"
    
    return checks

# api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from api.auth import verify_admin_token

router = APIRouter()

@router.get("/stats", dependencies=[Depends(verify_admin_token)])
async def get_stats() -> Dict:
    """Obtém estatísticas do sistema"""
    # Implementar coleta de estatísticas
    return {
        "total_conversations": 150,
        "active_conversations": 12,
        "leads_qualified": 89,
        "meetings_scheduled": 34,
        "conversion_rate": 22.7
    }

@router.post("/broadcast", dependencies=[Depends(verify_admin_token)])
async def send_broadcast(message: Dict) -> Dict:
    """Envia mensagem em massa"""
    # Implementar envio em massa
    return {"status": "sent", "recipients": message.get("recipients", [])}
```

### 📋 Checklist Fase 3

- [ ] FastAPI configurado e rodando
- [ ] Redis conectado e funcionando
- [ ] Celery worker e beat configurados
- [ ] Tarefas assíncronas implementadas
- [ ] Webhooks base funcionando
- [ ] Sistema de cache implementado
- [ ] Health checks ativos
- [ ] Logs estruturados
- [ ] Testes de integração

---

## 📱 Fase 4: Integração Evolution API (Dias 8-9)

### Objetivo
Integrar completamente com Evolution API para receber e enviar mensagens WhatsApp, processar mídia e gerenciar conversas.

### 4.1 Cliente Evolution API

```python
# services/evolution_client.py
import httpx
from typing import Dict, Any, Optional, List
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

logger = logging.getLogger(__name__)

class EvolutionClient:
    """Cliente para interação com Evolution API"""
    
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance = settings.EVOLUTION_INSTANCE_NAME
        
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_instance(self) -> Dict:
        """Cria nova instância do WhatsApp"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/instance/create",
                headers=self.headers,
                json={
                    "instanceName": self.instance,
                    "token": settings.EVOLUTION_INSTANCE_TOKEN,
                    "qrcode": True,
                    "webhook": {
                        "url": f"{settings.WEBHOOK_URL}/whatsapp",
                        "events": [
                            "messages.upsert",
                            "messages.update",
                            "connection.update",
                            "contacts.upsert"
                        ]
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_qrcode(self) -> Optional[str]:
        """Obtém QR Code para conectar"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instance/qrcode/{self.instance}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("qrcode")
            return None
    
    async def get_connection_status(self) -> Dict:
        """Verifica status da conexão"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instance/connectionState/{self.instance}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def send_text(
        self,
        number: str,
        text: str,
        quoted_message_id: Optional[str] = None
    ) -> Dict:
        """Envia mensagem de texto"""
        # Formatar número
        formatted_number = self._format_number(number)
        
        payload = {
            "number": formatted_number,
            "text": text
        }
        
        if quoted_message_id:
            payload["quoted"] = {"messageId": quoted_message_id}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/message/sendText/{self.instance}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def send_media(
        self,
        number: str,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "image"
    ) -> Dict:
        """Envia mídia (imagem, vídeo, documento)"""
        formatted_number = self._format_number(number)
        
        endpoint_map = {
            "image": "sendImage",
            "video": "sendVideo",
            "document": "sendDocument",
            "audio": "sendAudio"
        }
        
        endpoint = endpoint_map.get(media_type, "sendDocument")
        
        payload = {
            "number": formatted_number,
            "mediaUrl": media_url
        }
        
        if caption:
            payload["caption"] = caption
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/message/{endpoint}/{self.instance}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def send_buttons(
        self,
        number: str,
        text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict:
        """Envia mensagem com botões"""
        formatted_number = self._format_number(number)
        
        payload = {
            "number": formatted_number,
            "text": text,
            "buttons": buttons,
            "footerText": "SolarPrime - Energia Solar"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/message/sendButtons/{self.instance}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def send_list(
        self,
        number: str,
        title: str,
        description: str,
        button_text: str,
        sections: List[Dict]
    ) -> Dict:
        """Envia lista de opções"""
        formatted_number = self._format_number(number)
        
        payload = {
            "number": formatted_number,
            "title": title,
            "description": description,
            "buttonText": button_text,
            "sections": sections,
            "footerText": "SolarPrime - Energia Solar"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/message/sendList/{self.instance}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def set_typing(
        self,
        number: str,
        duration: int = 3000
    ):
        """Simula digitação"""
        formatted_number = self._format_number(number)
        
        payload = {
            "number": formatted_number,
            "duration": duration
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/sendTyping/{self.instance}",
                headers=self.headers,
                json=payload
            )
            # Não falhar se typing não funcionar
            if response.status_code != 200:
                logger.warning(f"Erro ao enviar typing: {response.text}")
    
    async def download_media(self, message_id: str) -> bytes:
        """Baixa mídia recebida"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/message/downloadMedia/{self.instance}/{message_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.content
    
    def _format_number(self, number: str) -> str:
        """Formata número para padrão internacional"""
        # Remove caracteres não numéricos
        clean_number = ''.join(filter(str.isdigit, number))
        
        # Adiciona código do país se não tiver
        if not clean_number.startswith('55'):
            clean_number = '55' + clean_number
        
        # Adiciona @s.whatsapp.net
        return f"{clean_number}@s.whatsapp.net"
```

### 4.2 Serviço WhatsApp

```python
# services/whatsapp_service.py
from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime
from services.evolution_client import EvolutionClient
from services.media_processor import MediaProcessor
from config.settings import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Serviço principal para gerenciar WhatsApp"""
    
    def __init__(self):
        self.client = EvolutionClient()
        self.media_processor = MediaProcessor()
    
    async def send_message(
        self,
        number: str,
        message: str,
        typing_time: int = 2
    ) -> Dict:
        """Envia mensagem com simulação de digitação"""
        try:
            # Simular digitação
            if typing_time > 0:
                await self.client.set_typing(number, typing_time * 1000)
                await asyncio.sleep(typing_time)
            
            # Enviar mensagem
            result = await self.client.send_text(number, message)
            
            # Log para tracking
            logger.info(f"Mensagem enviada para {number}: {result.get('id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            raise
    
    async def send_media_message(
        self,
        number: str,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "image"
    ) -> Dict:
        """Envia mídia com caption"""
        try:
            result = await self.client.send_media(
                number=number,
                media_url=media_url,
                caption=caption,
                media_type=media_type
            )
            
            logger.info(f"Mídia enviada para {number}: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao enviar mídia: {str(e)}")
            raise
    
    async def send_interactive_buttons(
        self,
        number: str,
        text: str,
        options: List[str]
    ) -> Dict:
        """Envia mensagem com botões interativos"""
        buttons = [
            {"buttonId": f"btn_{i}", "buttonText": {"displayText": opt}}
            for i, opt in enumerate(options)
        ]
        
        return await self.client.send_buttons(number, text, buttons)
    
    async def send_options_list(
        self,
        number: str,
        title: str,
        description: str,
        options: Dict[str, List[Dict]]
    ) -> Dict:
        """Envia lista de opções organizadas"""
        sections = []
        
        for section_title, items in options.items():
            rows = [
                {
                    "title": item["title"],
                    "description": item.get("description", ""),
                    "rowId": item["id"]
                }
                for item in items
            ]
            
            sections.append({
                "title": section_title,
                "rows": rows
            })
        
        return await self.client.send_list(
            number=number,
            title=title,
            description=description,
            button_text="Ver Opções",
            sections=sections
        )
    
    async def process_incoming_message(
        self,
        message_data: Dict
    ) -> Dict:
        """Processa mensagem recebida"""
        try:
            # Extrair informações da mensagem
            message_info = self._extract_message_info(message_data)
            
            # Se for mídia, processar
            if message_info["type"] in ["image", "document", "audio"]:
                media_result = await self.media_processor.process_media(
                    message_id=message_info["id"],
                    media_type=message_info["type"],
                    message_data=message_data
                )
                message_info["media_result"] = media_result
            
            # Retornar informações processadas
            return message_info
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            raise
    
    def _extract_message_info(self, message_data: Dict) -> Dict:
        """Extrai informações relevantes da mensagem"""
        msg = message_data.get("message", {})
        
        # Determinar tipo de mensagem
        message_type = "text"
        content = ""
        
        if "imageMessage" in msg:
            message_type = "image"
            content = msg["imageMessage"].get("caption", "")
        elif "documentMessage" in msg:
            message_type = "document"
            content = msg["documentMessage"].get("caption", "")
        elif "audioMessage" in msg:
            message_type = "audio"
            content = "[Áudio recebido]"
        elif "videoMessage" in msg:
            message_type = "video"
            content = msg["videoMessage"].get("caption", "")
        elif "conversation" in msg:
            content = msg["conversation"]
        elif "extendedTextMessage" in msg:
            content = msg["extendedTextMessage"]["text"]
        
        return {
            "id": message_data.get("key", {}).get("id"),
            "from": message_data.get("key", {}).get("remoteJid"),
            "pushName": message_data.get("pushName"),
            "type": message_type,
            "content": content,
            "timestamp": message_data.get("messageTimestamp"),
            "raw": message_data
        }
```

### 4.3 Processador de Mídia

```python
# services/media_processor.py
import io
import logging
from typing import Dict, Any, Optional
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import PyPDF2
import aiofiles

logger = logging.getLogger(__name__)

class MediaProcessor:
    """Processa diferentes tipos de mídia"""
    
    def __init__(self):
        self.evolution_client = EvolutionClient()
    
    async def process_media(
        self,
        message_id: str,
        media_type: str,
        message_data: Dict
    ) -> Dict:
        """Processa mídia baseado no tipo"""
        try:
            # Baixar mídia
            media_bytes = await self.evolution_client.download_media(message_id)
            
            # Processar baseado no tipo
            if media_type == "image":
                return await self.process_image(media_bytes)
            elif media_type == "document":
                return await self.process_document(media_bytes, message_data)
            elif media_type == "audio":
                return await self.process_audio(media_bytes)
            else:
                return {"type": media_type, "processed": False}
                
        except Exception as e:
            logger.error(f"Erro ao processar mídia: {str(e)}")
            return {"error": str(e), "processed": False}
    
    async def process_image(self, image_bytes: bytes) -> Dict:
        """Processa imagem (OCR para contas de luz)"""
        try:
            # Abrir imagem
            image = Image.open(io.BytesIO(image_bytes))
            
            # Fazer OCR
            text = pytesseract.image_to_string(image, lang='por')
            
            # Analisar se é conta de luz
            energy_bill_data = self._analyze_energy_bill(text)
            
            return {
                "type": "image",
                "processed": True,
                "text": text,
                "is_energy_bill": energy_bill_data is not None,
                "bill_data": energy_bill_data
            }
            
        except Exception as e:
            logger.error(f"Erro no OCR: {str(e)}")
            return {"type": "image", "processed": False, "error": str(e)}
    
    async def process_document(
        self,
        document_bytes: bytes,
        message_data: Dict
    ) -> Dict:
        """Processa documento (PDF)"""
        try:
            # Verificar se é PDF
            filename = message_data.get("message", {}).get(
                "documentMessage", {}
            ).get("fileName", "")
            
            if filename.lower().endswith('.pdf'):
                # Processar PDF
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(document_bytes))
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # Analisar conteúdo
                energy_bill_data = self._analyze_energy_bill(text)
                
                return {
                    "type": "document",
                    "processed": True,
                    "filename": filename,
                    "pages": len(pdf_reader.pages),
                    "text": text[:1000],  # Primeiros 1000 caracteres
                    "is_energy_bill": energy_bill_data is not None,
                    "bill_data": energy_bill_data
                }
            else:
                return {
                    "type": "document",
                    "processed": False,
                    "reason": "Formato não suportado"
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar documento: {str(e)}")
            return {"type": "document", "processed": False, "error": str(e)}
    
    async def process_audio(self, audio_bytes: bytes) -> Dict:
        """Processa áudio (transcrição)"""
        try:
            # Converter para WAV
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Transcrever
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_io) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='pt-BR')
            
            return {
                "type": "audio",
                "processed": True,
                "transcription": text,
                "duration": len(audio) / 1000  # Em segundos
            }
            
        except Exception as e:
            logger.error(f"Erro na transcrição: {str(e)}")
            return {"type": "audio", "processed": False, "error": str(e)}
    
    def _analyze_energy_bill(self, text: str) -> Optional[Dict]:
        """Analisa texto para extrair dados de conta de luz"""
        import re
        
        # Padrões para encontrar valores
        patterns = {
            "valor": r"(?:total|valor|pagar|fatura)[\s:]*R?\$?\s*([\d.,]+)",
            "kwh": r"(\d+)\s*kWh",
            "mes": r"(?:referente|mês|período)[\s:]*([\w\s]+)",
            "vencimento": r"(?:vencimento|vence)[\s:]*([\d/]+)"
        }
        
        data = {}
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[key] = match.group(1).strip()
        
        # Se encontrou pelo menos valor, considerar como conta
        if "valor" in data:
            # Limpar valor
            data["valor"] = float(
                data["valor"].replace(".", "").replace(",", ".")
            )
            return data
        
        return None
```

### 4.4 Processador de Mensagens

```python
# services/message_processor.py
from typing import Dict, Any
import logging
from datetime import datetime
from services.whatsapp_service import WhatsAppService
from services.redis_service import RedisService
from agents.sdr_agent import SDRAgentWithRAG
from services.lead_service import LeadService
from config.settings import settings

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Processa mensagens recebidas do WhatsApp"""
    
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.redis = RedisService()
        self.agent = SDRAgentWithRAG(AgentConfig())
        self.lead_service = LeadService()
    
    async def process(self, message_data: Dict) -> Dict:
        """Processa mensagem completa"""
        try:
            # Processar mensagem recebida
            message_info = await self.whatsapp.process_incoming_message(
                message_data
            )
            
            # Ignorar mensagens do bot
            if message_info["from"].startswith(settings.BOT_NUMBER):
                return {"status": "ignored", "reason": "self_message"}
            
            # Obter ou criar sessão
            session_id = message_info["from"]
            conversation_state = await self.redis.get_conversation_state(
                session_id
            )
            
            # Atualizar contexto do agente
            self.agent.update_context(conversation_state)
            
            # Processar com o agente
            response = await self._process_with_agent(
                message_info,
                conversation_state
            )
            
            # Enviar resposta
            if response["text"]:
                await self.whatsapp.send_message(
                    number=message_info["from"],
                    message=response["text"],
                    typing_time=self._calculate_typing_time(response["text"])
                )
            
            # Enviar mídia se houver
            if response.get("media"):
                await self.whatsapp.send_media_message(
                    number=message_info["from"],
                    media_url=response["media"]["url"],
                    caption=response["media"].get("caption"),
                    media_type=response["media"]["type"]
                )
            
            # Atualizar estado da conversa
            conversation_state["messages"].append({
                "role": "user",
                "content": message_info["content"],
                "timestamp": datetime.now().isoformat()
            })
            conversation_state["messages"].append({
                "role": "assistant",
                "content": response["text"],
                "timestamp": datetime.now().isoformat()
            })
            conversation_state["stage"] = response.get("stage", "in_progress")
            
            await self.redis.save_conversation_state(
                session_id,
                conversation_state
            )
            
            # Atualizar lead no sistema
            await self._update_lead_data(message_info, response)
            
            # Agendar follow-up se necessário
            if response.get("schedule_followup"):
                from services.tasks import schedule_follow_up
                schedule_follow_up.delay(
                    session_id,
                    response["followup_delay"]
                )
            
            return {
                "status": "processed",
                "response": response,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _process_with_agent(
        self,
        message_info: Dict,
        conversation_state: Dict
    ) -> Dict:
        """Processa mensagem com o agente de IA"""
        # Preparar contexto
        context = {
            "user_name": message_info.get("pushName", ""),
            "message_type": message_info["type"],
            "conversation_stage": conversation_state.get("stage", "initial"),
            "message_count": len(conversation_state.get("messages", []))
        }
        
        # Se for mídia, adicionar resultado do processamento
        if message_info.get("media_result"):
            context["media_result"] = message_info["media_result"]
        
        # Processar com agente
        agent_response = await self.agent.process_message(
            message=message_info["content"],
            context=context
        )
        
        # Extrair resposta estruturada
        return {
            "text": agent_response.content,
            "stage": agent_response.metadata.get("stage", "in_progress"),
            "confidence": agent_response.metadata.get("confidence", 0.8),
            "schedule_followup": agent_response.metadata.get(
                "schedule_followup", False
            ),
            "followup_delay": agent_response.metadata.get(
                "followup_delay", 30
            ),
            "lead_data": agent_response.metadata.get("lead_data", {})
        }
    
    async def _update_lead_data(
        self,
        message_info: Dict,
        response: Dict
    ):
        """Atualiza dados do lead"""
        lead_data = response.get("lead_data", {})
        
        if lead_data:
            # Adicionar informações básicas
            lead_data.update({
                "phone": message_info["from"],
                "name": lead_data.get("name") or message_info.get("pushName"),
                "last_interaction": datetime.now(),
                "stage": response["stage"]
            })
            
            # Salvar/atualizar lead
            await self.lead_service.upsert_lead(lead_data)
    
    def _calculate_typing_time(self, text: str) -> int:
        """Calcula tempo de digitação baseado no texto"""
        # ~200 caracteres por minuto
        chars_per_second = 200 / 60
        typing_time = len(text) / chars_per_second
        
        # Limitar entre 1 e 5 segundos
        return max(1, min(5, int(typing_time)))
```

### 📋 Checklist Fase 4

- [ ] Evolution API instalada e rodando
- [ ] Instância WhatsApp criada e conectada
- [ ] Cliente Evolution implementado
- [ ] Processamento de mídia funcionando
- [ ] OCR para contas de luz
- [ ] Transcrição de áudio
- [ ] Webhooks recebendo mensagens
- [ ] Simulação de digitação
- [ ] Testes end-to-end

---

## 💼 Fase 5: Integração Kommo CRM (Dias 10-11)

### Objetivo
Integrar completamente com Kommo CRM para gestão de leads, pipeline de vendas e agendamento.

### 5.1 Cliente Kommo

```python
# services/kommo_client.py
import httpx
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

logger = logging.getLogger(__name__)

class KommoClient:
    """Cliente para integração com Kommo CRM"""
    
    def __init__(self):
        self.base_url = f"https://{settings.KOMMO_SUBDOMAIN}.amocrm.ru/api/v4"
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
    
    async def authenticate(self):
        """Autentica com OAuth2"""
        # Implementar fluxo OAuth2
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_lead(self, lead_data: Dict) -> Dict:
        """Cria novo lead no Kommo"""
        headers = await self._get_headers()
        
        payload = {
            "name": lead_data["name"],
            "price": lead_data.get("potential_value", 0),
            "status_id": lead_data.get("status_id", 142),  # Novo lead
            "pipeline_id": settings.KOMMO_PIPELINE_ID,
            "custom_fields_values": self._format_custom_fields(lead_data),
            "_embedded": {
                "tags": self._format_tags(lead_data)
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/leads",
                headers=headers,
                json=[payload]
            )
            response.raise_for_status()
            
            result = response.json()
            return result["_embedded"]["leads"][0]
    
    async def update_lead(self, lead_id: int, data: Dict) -> Dict:
        """Atualiza lead existente"""
        headers = await self._get_headers()
        
        payload = {
            "id": lead_id,
            "custom_fields_values": self._format_custom_fields(data)
        }
        
        if "status_id" in data:
            payload["status_id"] = data["status_id"]
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/leads/{lead_id}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def create_contact(self, contact_data: Dict) -> Dict:
        """Cria contato no Kommo"""
        headers = await self._get_headers()
        
        payload = {
            "name": contact_data["name"],
            "custom_fields_values": [
                {
                    "field_code": "PHONE",
                    "values": [{"value": contact_data["phone"]}]
                }
            ]
        }
        
        if contact_data.get("email"):
            payload["custom_fields_values"].append({
                "field_code": "EMAIL",
                "values": [{"value": contact_data["email"]}]
            })
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/contacts",
                headers=headers,
                json=[payload]
            )
            response.raise_for_status()
            
            result = response.json()
            return result["_embedded"]["contacts"][0]
    
    async def link_contact_to_lead(
        self,
        contact_id: int,
        lead_id: int
    ):
        """Vincula contato a um lead"""
        headers = await self._get_headers()
        
        payload = {
            "entity_id": lead_id,
            "to_entity_id": contact_id,
            "to_entity_type": "contacts"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/leads/{lead_id}/link",
                headers=headers,
                json=[payload]
            )
            response.raise_for_status()
    
    async def create_task(self, task_data: Dict) -> Dict:
        """Cria tarefa no Kommo"""
        headers = await self._get_headers()
        
        payload = {
            "text": task_data["text"],
            "complete_till": int(task_data["complete_till"].timestamp()),
            "entity_id": task_data["entity_id"],
            "entity_type": task_data.get("entity_type", "leads"),
            "task_type_id": task_data.get("task_type_id", 1)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tasks",
                headers=headers,
                json=[payload]
            )
            response.raise_for_status()
            
            result = response.json()
            return result["_embedded"]["tasks"][0]
    
    async def add_note(
        self,
        entity_id: int,
        text: str,
        entity_type: str = "leads"
    ):
        """Adiciona nota a uma entidade"""
        headers = await self._get_headers()
        
        payload = {
            "entity_id": entity_id,
            "note_type": "common",
            "params": {
                "text": text
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{entity_type}/{entity_id}/notes",
                headers=headers,
                json=[payload]
            )
            response.raise_for_status()
    
    async def _get_headers(self) -> Dict:
        """Obtém headers com token válido"""
        if not self.access_token or self._is_token_expired():
            await self._refresh_access_token()
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _format_custom_fields(self, data: Dict) -> List[Dict]:
        """Formata campos customizados"""
        fields = []
        
        # Mapear campos
        field_mapping = {
            "phone": 12345,  # ID do campo telefone
            "whatsapp": 12346,  # ID do campo WhatsApp
            "energy_bill_value": 12347,  # Valor da conta
            "solution_type": 12348,  # Tipo de solução
            "qualification_score": 12349  # Score
        }
        
        for key, field_id in field_mapping.items():
            if key in data:
                fields.append({
                    "field_id": field_id,
                    "values": [{"value": data[key]}]
                })
        
        return fields
    
    def _format_tags(self, data: Dict) -> List[Dict]:
        """Formata tags do lead"""
        tags = ["WhatsApp", "Bot"]
        
        # Adicionar tags baseadas nos dados
        if data.get("qualification_score", 0) >= 70:
            tags.append("Hot Lead")
        elif data.get("qualification_score", 0) >= 40:
            tags.append("Warm Lead")
        else:
            tags.append("Cold Lead")
        
        if data.get("solution_type"):
            tags.append(data["solution_type"])
        
        return [{"name": tag} for tag in tags]
```

### 5.2 Serviço de Leads

```python
# services/lead_service.py
from typing import Dict, Optional, List
import logging
from datetime import datetime
from services.kommo_client import KommoClient
from services.supabase_service import SupabaseService
from models.lead import Lead, LeadStatus

logger = logging.getLogger(__name__)

class LeadService:
    """Serviço para gerenciar leads"""
    
    def __init__(self):
        self.kommo = KommoClient()
        self.supabase = SupabaseService()
    
    async def upsert_lead(self, lead_data: Dict) -> Lead:
        """Cria ou atualiza lead"""
        try:
            # Buscar lead existente
            existing_lead = await self.get_lead_by_phone(
                lead_data["phone"]
            )
            
            if existing_lead:
                # Atualizar lead existente
                return await self.update_lead(
                    existing_lead.id,
                    lead_data
                )
            else:
                # Criar novo lead
                return await self.create_lead(lead_data)
                
        except Exception as e:
            logger.error(f"Erro ao upsert lead: {str(e)}")
            raise
    
    async def create_lead(self, lead_data: Dict) -> Lead:
        """Cria novo lead"""
        # Criar no Supabase
        lead = Lead(
            name=lead_data["name"],
            phone=lead_data["phone"],
            whatsapp=lead_data.get("whatsapp", lead_data["phone"]),
            email=lead_data.get("email"),
            status=LeadStatus.NEW,
            qualification_score=lead_data.get("qualification_score", 0),
            energy_bill_value=lead_data.get("energy_bill_value"),
            solution_type=lead_data.get("solution_type"),
            metadata=lead_data.get("metadata", {})
        )
        
        # Salvar no banco
        saved_lead = await self.supabase.create_lead(lead)
        
        # Criar no Kommo
        kommo_lead = await self.kommo.create_lead({
            "name": lead.name,
            "phone": lead.phone,
            "whatsapp": lead.whatsapp,
            "energy_bill_value": lead.energy_bill_value,
            "solution_type": lead.solution_type,
            "qualification_score": lead.qualification_score,
            "potential_value": self._calculate_potential_value(lead)
        })
        
        # Criar contato e vincular
        contact = await self.kommo.create_contact({
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email
        })
        
        await self.kommo.link_contact_to_lead(
            contact["id"],
            kommo_lead["id"]
        )
        
        # Adicionar nota inicial
        await self.kommo.add_note(
            kommo_lead["id"],
            f"Lead criado via WhatsApp Bot\nScore: {lead.qualification_score}"
        )
        
        # Atualizar lead com IDs do Kommo
        lead.kommo_lead_id = kommo_lead["id"]
        lead.kommo_contact_id = contact["id"]
        
        await self.supabase.update_lead(lead.id, {
            "kommo_lead_id": kommo_lead["id"],
            "kommo_contact_id": contact["id"]
        })
        
        logger.info(f"Lead criado: {lead.id} - {lead.name}")
        return lead
    
    async def update_lead(
        self,
        lead_id: str,
        data: Dict
    ) -> Lead:
        """Atualiza lead existente"""
        # Buscar lead
        lead = await self.supabase.get_lead(lead_id)
        
        if not lead:
            raise ValueError(f"Lead {lead_id} não encontrado")
        
        # Atualizar no banco
        updated_lead = await self.supabase.update_lead(lead_id, data)
        
        # Atualizar no Kommo se tiver ID
        if lead.kommo_lead_id:
            await self.kommo.update_lead(lead.kommo_lead_id, data)
            
            # Adicionar nota sobre atualização
            changes = self._get_changes_summary(lead, data)
            if changes:
                await self.kommo.add_note(
                    lead.kommo_lead_id,
                    f"Lead atualizado:\n{changes}"
                )
        
        return updated_lead
    
    async def move_to_stage(
        self,
        lead_id: str,
        stage: LeadStatus
    ):
        """Move lead para novo estágio"""
        lead = await self.supabase.get_lead(lead_id)
        
        if not lead:
            raise ValueError(f"Lead {lead_id} não encontrado")
        
        # Mapear status para ID do Kommo
        status_mapping = {
            LeadStatus.NEW: 142,
            LeadStatus.QUALIFYING: 143,
            LeadStatus.QUALIFIED: 144,
            LeadStatus.MEETING_SCHEDULED: 145,
            LeadStatus.IN_NEGOTIATION: 146,
            LeadStatus.WON: 142,  # Sucesso
            LeadStatus.LOST: 143  # Perdido
        }
        
        # Atualizar status
        await self.update_lead(lead_id, {
            "status": stage,
            "kommo_status_id": status_mapping.get(stage)
        })
        
        # Executar ações baseadas no estágio
        await self._execute_stage_actions(lead, stage)
    
    async def schedule_meeting(
        self,
        lead_id: str,
        meeting_datetime: datetime,
        duration_minutes: int = 60
    ):
        """Agenda reunião para um lead"""
        lead = await self.supabase.get_lead(lead_id)
        
        if not lead or not lead.kommo_lead_id:
            raise ValueError(f"Lead {lead_id} não encontrado ou sem Kommo ID")
        
        # Criar tarefa de reunião
        task = await self.kommo.create_task({
            "text": f"Reunião com {lead.name} - Energia Solar",
            "complete_till": meeting_datetime,
            "entity_id": lead.kommo_lead_id,
            "entity_type": "leads",
            "task_type_id": 2  # Meeting
        })
        
        # Atualizar lead
        await self.update_lead(lead_id, {
            "meeting_scheduled_at": meeting_datetime,
            "status": LeadStatus.MEETING_SCHEDULED
        })
        
        # Adicionar nota
        await self.kommo.add_note(
            lead.kommo_lead_id,
            f"Reunião agendada para {meeting_datetime.strftime('%d/%m/%Y às %H:%M')}"
        )
        
        return task
    
    def _calculate_potential_value(self, lead: Lead) -> float:
        """Calcula valor potencial do lead"""
        if not lead.energy_bill_value:
            return 0
        
        # Economia de 20% ao mês
        monthly_savings = lead.energy_bill_value * 0.20
        
        # Valor do contrato (25 anos)
        contract_value = monthly_savings * 12 * 25
        
        # Aplicar desconto baseado no score
        if lead.qualification_score >= 70:
            return contract_value * 0.8  # 80% de chance
        elif lead.qualification_score >= 40:
            return contract_value * 0.5  # 50% de chance
        else:
            return contract_value * 0.2  # 20% de chance
    
    def _get_changes_summary(self, lead: Lead, new_data: Dict) -> str:
        """Gera resumo das mudanças"""
        changes = []
        
        for key, new_value in new_data.items():
            old_value = getattr(lead, key, None)
            if old_value != new_value:
                changes.append(f"- {key}: {old_value} → {new_value}")
        
        return "\n".join(changes)
    
    async def _execute_stage_actions(self, lead: Lead, stage: LeadStatus):
        """Executa ações específicas por estágio"""
        if stage == LeadStatus.QUALIFIED:
            # Agendar tarefa de contato
            await self.kommo.create_task({
                "text": "Entrar em contato para agendar reunião",
                "complete_till": datetime.now().replace(hour=9, minute=0),
                "entity_id": lead.kommo_lead_id,
                "task_type_id": 1  # Call
            })
        
        elif stage == LeadStatus.MEETING_SCHEDULED:
            # Enviar confirmação via WhatsApp
            from services.whatsapp_service import WhatsAppService
            whatsapp = WhatsAppService()
            
            await whatsapp.send_message(
                lead.phone,
                f"""✅ Reunião confirmada, {lead.name}!

📅 Data: {lead.meeting_scheduled_at.strftime('%d/%m/%Y')}
⏰ Horário: {lead.meeting_scheduled_at.strftime('%H:%M')}

Vou enviar um lembrete no dia! 😊"""
            )
```

### 5.3 Pipeline de Vendas

```python
# services/sales_pipeline.py
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from services.lead_service import LeadService
from services.kommo_client import KommoClient
from models.lead import LeadStatus

logger = logging.getLogger(__name__)

class SalesPipeline:
    """Gerencia o pipeline de vendas"""
    
    def __init__(self):
        self.lead_service = LeadService()
        self.kommo = KommoClient()
    
    async def qualify_lead(self, lead_id: str) -> Dict:
        """Qualifica lead e move no pipeline"""
        lead = await self.lead_service.get_lead(lead_id)
        
        if not lead:
            raise ValueError(f"Lead {lead_id} não encontrado")
        
        # Calcular score de qualificação
        score = self._calculate_qualification_score(lead)
        
        # Atualizar score
        await self.lead_service.update_lead(lead_id, {
            "qualification_score": score
        })
        
        # Determinar próximo estágio
        if score >= 70:
            # Lead quente - agendar reunião
            await self.lead_service.move_to_stage(
                lead_id,
                LeadStatus.QUALIFIED
            )
            
            # Criar tarefa urgente
            await self.kommo.create_task({
                "text": "🔥 LEAD QUENTE - Contatar URGENTE",
                "complete_till": datetime.now() + timedelta(hours=1),
                "entity_id": lead.kommo_lead_id,
                "task_type_id": 1
            })
            
            return {
                "status": "hot_lead",
                "score": score,
                "action": "urgent_contact"
            }
            
        elif score >= 40:
            # Lead morno - nutrir
            await self.lead_service.move_to_stage(
                lead_id,
                LeadStatus.QUALIFYING
            )
            
            return {
                "status": "warm_lead",
                "score": score,
                "action": "nurture"
            }
            
        else:
            # Lead frio - follow-up futuro
            return {
                "status": "cold_lead",
                "score": score,
                "action": "future_followup"
            }
    
    def _calculate_qualification_score(self, lead: Lead) -> int:
        """Calcula score de qualificação"""
        score = 0
        
        # Valor da conta (40 pontos)
        if lead.energy_bill_value:
            if lead.energy_bill_value >= 1000:
                score += 40
            elif lead.energy_bill_value >= 500:
                score += 30
            elif lead.energy_bill_value >= 300:
                score += 20
            else:
                score += 10
        
        # Tipo de solução (20 pontos)
        if lead.solution_type:
            if lead.solution_type in ["usina_propria", "usina_parceira"]:
                score += 20
            else:
                score += 10
        
        # Engajamento (20 pontos)
        if lead.metadata.get("message_count", 0) >= 5:
            score += 20
        elif lead.metadata.get("message_count", 0) >= 3:
            score += 10
        
        # Urgência (20 pontos)
        if lead.metadata.get("urgency") == "immediate":
            score += 20
        elif lead.metadata.get("urgency") == "this_month":
            score += 15
        elif lead.metadata.get("urgency") == "planning":
            score += 5
        
        return min(score, 100)
    
    async def get_pipeline_stats(self) -> Dict:
        """Obtém estatísticas do pipeline"""
        # Buscar leads por estágio
        stats = {
            "total_leads": 0,
            "by_stage": {},
            "conversion_rates": {},
            "average_values": {}
        }
        
        # Implementar coleta de estatísticas
        # ...
        
        return stats
```

### 5.4 Sistema de Follow-up com CRM

```python
# services/crm_followup.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from services.lead_service import LeadService
from services.whatsapp_service import WhatsAppService
from services.kommo_client import KommoClient
from models.lead import LeadStatus

logger = logging.getLogger(__name__)

class CRMFollowUpService:
    """Gerencia follow-ups integrados com CRM"""
    
    def __init__(self):
        self.lead_service = LeadService()
        self.whatsapp = WhatsAppService()
        self.kommo = KommoClient()
    
    async def schedule_followup(
        self,
        lead_id: str,
        followup_type: str,
        delay_hours: int = 24
    ):
        """Agenda follow-up para um lead"""
        lead = await self.lead_service.get_lead(lead_id)
        
        if not lead:
            raise ValueError(f"Lead {lead_id} não encontrado")
        
        # Calcular horário do follow-up
        followup_time = datetime.now() + timedelta(hours=delay_hours)
        
        # Criar tarefa no Kommo
        task = await self.kommo.create_task({
            "text": f"Follow-up automático - {followup_type}",
            "complete_till": followup_time,
            "entity_id": lead.kommo_lead_id,
            "task_type_id": 1
        })
        
        # Agendar envio da mensagem
        from services.tasks import send_followup_message
        send_followup_message.apply_async(
            args=[lead_id, followup_type],
            eta=followup_time
        )
        
        # Adicionar nota
        await self.kommo.add_note(
            lead.kommo_lead_id,
            f"Follow-up agendado: {followup_type} em {delay_hours}h"
        )
        
        return task
    
    async def execute_followup(
        self,
        lead_id: str,
        followup_type: str
    ):
        """Executa follow-up"""
        lead = await self.lead_service.get_lead(lead_id)
        
        if not lead:
            logger.error(f"Lead {lead_id} não encontrado")
            return
        
        # Obter mensagem de follow-up
        message = self._get_followup_message(lead, followup_type)
        
        # Enviar mensagem
        await self.whatsapp.send_message(lead.phone, message)
        
        # Atualizar lead
        await self.lead_service.update_lead(lead_id, {
            "last_followup_at": datetime.now(),
            "followup_count": lead.metadata.get("followup_count", 0) + 1
        })
        
        # Adicionar nota no CRM
        await self.kommo.add_note(
            lead.kommo_lead_id,
            f"Follow-up enviado: {followup_type}"
        )
        
        # Verificar se precisa agendar próximo
        if self._should_schedule_next_followup(lead, followup_type):
            await self.schedule_followup(
                lead_id,
                "second_attempt",
                48  # 48 horas
            )
    
    def _get_followup_message(
        self,
        lead: Lead,
        followup_type: str
    ) -> str:
        """Obtém mensagem de follow-up personalizada"""
        templates = {
            "first_attempt": f"""Oi {lead.name}! 👋

Vi que você demonstrou interesse em economizar na conta de luz.

Já fez as contas de quanto economizaria com energia solar? 
Posso te mostrar agora mesmo! 💰☀️""",
            
            "second_attempt": f"""Olá {lead.name}!

Não quero ser insistente, mas não posso deixar você perder 
essa oportunidade de economizar!

Que tal agendarmos 15 minutinhos para eu te mostrar 
os números? Prometo que vale a pena! 😊""",
            
            "meeting_reminder": f"""Bom dia {lead.name}! ☀️

Passando para confirmar nossa reunião de hoje sobre 
seu projeto de energia solar.

Está tudo certo para às {lead.meeting_scheduled_at.strftime('%H:%M')}? 

Me confirma por favor! 📅""",
            
            "reengagement": f"""Oi {lead.name}! 

Faz um tempinho que não conversamos...

A conta de luz continua alta? Ainda podemos 
fazer algo a respeito! 💡

Vamos retomar nossa conversa? 🤝"""
        }
        
        return templates.get(
            followup_type,
            "Olá! Tudo bem? Vamos continuar nossa conversa?"
        )
    
    def _should_schedule_next_followup(
        self,
        lead: Lead,
        followup_type: str
    ) -> bool:
        """Verifica se deve agendar próximo follow-up"""
        # Máximo de 3 follow-ups
        if lead.metadata.get("followup_count", 0) >= 3:
            return False
        
        # Não fazer follow-up se já agendou reunião
        if lead.status == LeadStatus.MEETING_SCHEDULED:
            return False
        
        # Continuar se for primeiro attempt
        return followup_type == "first_attempt"
```

### 📋 Checklist Fase 5

- [ ] Cliente Kommo implementado
- [ ] OAuth2 configurado
- [ ] CRUD de leads funcionando
- [ ] Pipeline de vendas automatizado
- [ ] Sistema de follow-up integrado
- [ ] Agendamento de reuniões
- [ ] Sincronização bidireccional
- [ ] Webhooks do Kommo
- [ ] Relatórios implementados

---

## 🚀 Fase 6: Deploy e Otimização (Dias 12-14)

### Objetivo
Deploy completo em produção com monitoramento, otimizações e documentação final.

### 6.1 Preparação para Deploy

```bash
# scripts/prepare_deploy.sh
#!/bin/bash

echo "🚀 Preparando para deploy..."

# Verificar ambiente
python scripts/check_environment.py

# Executar testes
pytest tests/ -v

# Build da aplicação
docker build -t sdr-solarprime:latest .

# Verificar segurança
bandit -r . -ll

# Gerar documentação
sphinx-build -b html docs/ docs/_build/

echo "✅ Aplicação pronta para deploy!"
```

### 6.2 Docker Compose Produção

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: sdr-solarprime:latest
    container_name: sdr-api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.prod
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

  celery-worker:
    image: sdr-solarprime:latest
    container_name: sdr-celery-worker
    restart: always
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.prod
    depends_on:
      - redis
    command: celery -A services.celery_app worker --loglevel=info --concurrency=4

  celery-beat:
    image: sdr-solarprime:latest
    container_name: sdr-celery-beat
    restart: always
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.prod
    depends_on:
      - redis
    command: celery -A services.celery_app beat --loglevel=info

  redis:
    image: redis:7-alpine
    container_name: sdr-redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes

  nginx:
    image: nginx:alpine
    container_name: sdr-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api

volumes:
  redis-data:
```

### 6.3 Monitoramento

```python
# services/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Métricas
messages_processed = Counter(
    'sdr_messages_processed_total',
    'Total de mensagens processadas',
    ['status']
)

response_time = Histogram(
    'sdr_response_time_seconds',
    'Tempo de resposta do agente'
)

active_conversations = Gauge(
    'sdr_active_conversations',
    'Conversas ativas no momento'
)

leads_qualified = Counter(
    'sdr_leads_qualified_total',
    'Total de leads qualificados',
    ['score_range']
)

def track_metrics(metric_type):
    """Decorator para rastrear métricas"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Registrar sucesso
                if metric_type == "message":
                    messages_processed.labels(status="success").inc()
                
                return result
                
            except Exception as e:
                # Registrar erro
                if metric_type == "message":
                    messages_processed.labels(status="error").inc()
                raise
                
            finally:
                # Registrar tempo
                duration = time.time() - start_time
                response_time.observe(duration)
        
        return wrapper
    return decorator
```

### 6.4 Otimizações de Performance

```python
# config/optimizations.py
from functools import lru_cache
import asyncio
from typing import Dict, Any

class PerformanceOptimizer:
    """Otimizações de performance"""
    
    def __init__(self):
        self._cache = {}
        self._locks = {}
    
    @lru_cache(maxsize=1000)
    def get_cached_response(self, query: str) -> Optional[str]:
        """Cache de respostas comuns"""
        # Implementar cache inteligente
        pass
    
    async def batch_process_messages(
        self,
        messages: List[Dict]
    ) -> List[Dict]:
        """Processa mensagens em lote"""
        tasks = []
        
        for msg in messages:
            task = self._process_single_message(msg)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def optimize_database_queries(self):
        """Otimiza queries do banco"""
        # Criar índices
        await self.supabase.execute("""
            CREATE INDEX IF NOT EXISTS idx_leads_phone 
            ON leads(phone);
            
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id, created_at);
            
            CREATE INDEX IF NOT EXISTS idx_embeddings_similarity 
            ON embeddings USING ivfflat (embedding vector_cosine_ops);
        """)
```

### 6.5 Script de Deploy Final

```bash
# scripts/deploy.sh
#!/bin/bash

set -e

echo "🚀 Iniciando deploy em produção..."

# Backup do banco
echo "📦 Fazendo backup..."
./scripts/backup_database.sh

# Parar serviços
echo "🛑 Parando serviços..."
docker-compose -f docker-compose.prod.yml down

# Atualizar código
echo "📥 Atualizando código..."
git pull origin main

# Build e deploy
echo "🏗️ Building..."
docker-compose -f docker-compose.prod.yml build

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Verificar saúde
echo "🏥 Verificando saúde..."
sleep 30
curl -f http://localhost:8000/health || exit 1

# Aplicar migrações
echo "🗃️ Aplicando migrações..."
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

echo "✅ Deploy concluído com sucesso!"

# Notificar equipe
curl -X POST $SLACK_WEBHOOK -d '{"text":"Deploy SDR SolarPrime concluído com sucesso! 🚀"}'
```

### 📋 Checklist Fase 6

- [ ] Testes completos passando
- [ ] Docker images otimizadas
- [ ] SSL/TLS configurado
- [ ] Monitoramento ativo
- [ ] Logs centralizados
- [ ] Backup automatizado
- [ ] Documentação completa
- [ ] Equipe treinada
- [ ] Sistema em produção

---

## 🎉 Conclusão

Parabéns! Você agora tem um plano completo para desenvolver o **Agente SDR SolarPrime** do zero.

### Resumo das Entregas

1. **Agente de IA** com AGnO Framework e Gemini 2.5 Pro
2. **Sistema RAG** completo com Supabase
3. **API robusta** com FastAPI e sistema de filas
4. **Integração WhatsApp** via Evolution API
5. **CRM automatizado** com Kommo
6. **Deploy otimizado** com monitoramento

### Próximos Passos

1. Seguir o plano fase por fase
2. Testar cada componente isoladamente
3. Integrar progressivamente
4. Validar com usuários reais
5. Otimizar baseado em métricas

### Tempo Total Estimado: 14 dias úteis

---

**💡 Lembre-se**: Este é um plano vivo. Ajuste conforme necessário durante o desenvolvimento!