# 🚀 Guia Completo - AGnO Framework no SDR SolarPrime

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura Refatorada](#arquitetura-refatorada)
3. [Componentes Principais](#componentes-principais)
4. [API Correta do AGnO](#api-correta-do-agno)
5. [Recursos Avançados](#recursos-avançados)
6. [Guia de Uso](#guia-de-uso)
7. [Migração do Código Antigo](#migração-do-código-antigo)

---

## 🎯 Visão Geral

O SDR SolarPrime foi completamente refatorado para usar 100% o AGnO Framework, aproveitando todos os recursos nativos da plataforma.

### Principais Benefícios
- ✅ **Reasoning Nativo**: Chain of thought automático
- ✅ **Memory Management**: Sessões persistentes por lead
- ✅ **Agent Sessions**: Contexto mantido entre conversas
- ✅ **Structured Outputs**: Respostas JSON estruturadas
- ✅ **Multi-Agent Support**: Preparado para teams e workflows

---

## 🏗️ Arquitetura Refatorada

### Antes (Incorreto)
```python
# ❌ ERRADO - API inexistente
from agno import Agent, Message, Swarm
from agno.models import ModelClient

class GeminiClient(ModelClient):  # Desnecessário
    def generate(self, messages, **kwargs):
        # Implementação manual
```

### Depois (Correto)
```python
# ✅ CORRETO - API oficial
from agno.agent import Agent, AgentMemory, AgentSession
from agno.models.google import Gemini

# Configuração direta
model = Gemini(id="gemini-2.0-flash-exp", api_key=api_key)
agent = Agent(
    name="Luna",
    model=model,
    reasoning=True,  # Chain of thought nativo
    memory=AgentMemory(...)
)
```

---

## 🔧 Componentes Principais

### 1. Modelo Gemini
```python
from agno.models.google import Gemini

model = Gemini(
    id="gemini-2.0-flash-exp",  # ou outro modelo
    api_key=config.gemini.api_key
)
```

### 2. Agente Principal
```python
agent = Agent(
    # Identificação
    name="Luna",
    description="Consultora de energia solar",
    
    # Instruções e comportamento
    instructions=system_prompt,
    
    # Modelo e configurações
    model=model,
    temperature=0.7,
    max_tokens=2048,
    
    # Recursos avançados
    reasoning=True,      # Chain of thought
    markdown=True,       # Suporte markdown
    memory=AgentMemory(...),  # Memória persistente
    
    # Ferramentas (opcional)
    tools=[],
    show_tool_calls=False
)
```

### 3. Sessões por Lead
```python
# Criar sessão para cada número
session = agent.create_session()

# Executar com sessão
response = agent.run(prompt, session=session)

# Sessão mantém contexto automaticamente
```

### 4. Memória Nativa
```python
memory = AgentMemory(
    role="Você é Luna, consultora solar",
    instructions="Lembre-se das informações dos leads"
)
```

---

## 📚 API Correta do AGnO

### Métodos Principais

#### 1. agent.run()
```python
# Execução síncrona
response = agent.run(
    "Mensagem do usuário",
    session=session,
    stream=False
)

# Com streaming
response = agent.run(
    "Mensagem",
    session=session,
    stream=True
)
```

#### 2. agent.print_response()
```python
# Imprime resposta diretamente
agent.print_response(
    "Mensagem",
    session=session,
    stream=True
)
```

#### 3. Sessões
```python
# Criar nova sessão
session = agent.create_session()

# Sessão tem ID único
session_id = session.id

# Contexto mantido automaticamente
```

---

## 🚀 Recursos Avançados

### 1. Reasoning (Chain of Thought)
```python
agent = Agent(
    reasoning=True,  # Ativa reasoning
    # Agent "pensa" antes de responder
)
```

### 2. Structured Outputs
```python
analysis_agent = Agent(
    structured_outputs=True,  # Força saída JSON
    temperature=0.3  # Mais determinístico
)

result = analysis_agent.run("Analise e retorne JSON")
data = json.loads(result.content)
```

### 3. Teams (Multi-Agent)
```python
from agno.agent import Team

team = Team(
    members=[
        Agent(name="Analisador", role="Analisa contexto"),
        Agent(name="Vendedor", role="Gera respostas de vendas")
    ]
)
```

### 4. Knowledge Base (RAG)
```python
from agno.agent import AgentKnowledge

knowledge = AgentKnowledge(
    vector_db=PgVector(...),
    num_documents=5
)

agent = Agent(
    knowledge=knowledge,
    search_knowledge=True
)
```

---

## 📖 Guia de Uso

### 1. Inicialização
```python
# 1. Criar modelo
model = Gemini(id="gemini-2.0-flash-exp", api_key=key)

# 2. Criar agente
agent = Agent(
    name="Luna",
    model=model,
    reasoning=True,
    memory=AgentMemory(...)
)

# 3. Criar sessão por lead
session = agent.create_session()
```

### 2. Processamento de Mensagens
```python
async def process_message(message: str, phone: str):
    # Obter ou criar sessão
    session = get_or_create_session(phone)
    
    # Analisar contexto
    analysis = await analyze_context(message)
    
    # Construir prompt com contexto
    prompt = build_context_prompt(message, analysis)
    
    # Executar agente
    response = await asyncio.to_thread(
        agent.run,
        prompt,
        session=session
    )
    
    return response.content
```

### 3. Análise de Contexto
```python
# Criar agente especializado
analysis_agent = Agent(
    name="Analisador",
    model=model,
    structured_outputs=True,
    temperature=0.3
)

# Executar análise
result = analysis_agent.run(analysis_prompt)
data = json.loads(result.content)
```

---

## 🔄 Migração do Código Antigo

### Mudanças Necessárias

| Antigo | Novo |
|--------|------|
| `from agno import Agent` | `from agno.agent import Agent` |
| `from agno import Message` | `from agno.agent import Message` |
| `from agno import Swarm` | ❌ Não existe - remover |
| `ModelClient` customizado | ❌ Não necessário |
| `self.swarm.run()` | `agent.run()` |
| `ConversationMemory` | `AgentMemory` + `AgentSession` |

### Exemplo de Migração

**Antes:**
```python
# Cliente customizado
class GeminiClient(ModelClient):
    def generate(self, messages):
        # Implementação manual

# Uso com Swarm
response = await self.swarm.run(
    agent=self.agent,
    messages=messages
)
```

**Depois:**
```python
# Direto com AGnO
model = Gemini(id="gemini-2.0-flash-exp", api_key=key)
agent = Agent(name="Luna", model=model)

# Execução simples
response = agent.run(prompt, session=session)
```

---

## 🎯 Melhores Práticas

### 1. Use Sessões Sempre
```python
# ✅ BOM - Mantém contexto
session = agent.create_session()
response = agent.run(prompt, session=session)

# ❌ RUIM - Perde contexto
response = agent.run(prompt)
```

### 2. Aproveite o Reasoning
```python
# ✅ BOM - Agent "pensa" antes
agent = Agent(reasoning=True)

# Para debug, veja o reasoning
response = agent.run(prompt)
# response.reasoning contém o pensamento
```

### 3. Use Agentes Especializados
```python
# ✅ BOM - Agente para cada tarefa
analysis_agent = Agent(name="Analisador", temperature=0.3)
sales_agent = Agent(name="Vendedor", temperature=0.7)

# ❌ RUIM - Um agente para tudo
universal_agent = Agent(name="Faz Tudo")
```

### 4. Configure Corretamente
```python
# ✅ BOM - Configurações específicas
agent = Agent(
    name="Luna",
    temperature=0.7,      # Criatividade controlada
    max_tokens=2048,      # Limite adequado
    top_p=0.95,          # Diversidade
    reasoning=True,       # Chain of thought
    markdown=True        # Formatação rica
)
```

---

## 🚨 Troubleshooting

### Erro: "cannot import name 'Agent'"
```python
# ❌ Errado
from agno import Agent

# ✅ Correto
from agno.agent import Agent
```

### Erro: "No module named 'agno.models'"
```python
# ❌ Errado
from agno.models import Gemini

# ✅ Correto
from agno.models.google import Gemini
```

### Resposta vazia ou None
```python
# Verificar extração correta
if hasattr(response, 'content'):
    return response.content
elif hasattr(response, 'messages'):
    return response.messages[-1].content
else:
    return str(response)
```

---

## 📚 Recursos Adicionais

- [Documentação Oficial AGnO](https://docs.agno.com)
- [Exemplos de Código](https://github.com/agno-framework/examples)
- [API Reference](https://docs.agno.com/api)

---

## 🎉 Conclusão

O SDR SolarPrime agora utiliza 100% o AGnO Framework com:
- ✅ API correta e oficial
- ✅ Reasoning nativo (chain of thought)
- ✅ Memória persistente por sessão
- ✅ Preparado para multi-agent e workflows
- ✅ Código mais limpo e manutenível

**Próximos passos**: Implementar Knowledge Base (RAG) e Tools customizadas!