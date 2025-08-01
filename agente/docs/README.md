# 🤖 SDR Agent - Nova Arquitetura Modular

Sistema SDR inteligente para qualificação e agendamento de leads via WhatsApp usando AGnO Framework.

## 📁 Estrutura do Projeto

```
agente/
├── core/                    # Núcleo do sistema
│   ├── __init__.py
│   ├── config.py           # Configurações centralizadas
│   ├── types.py            # Tipos e modelos Pydantic
│   ├── logger.py           # Configuração de logging com Loguru
│   └── agent.py            # Agente principal (SDRAgent)
│
├── services/               # Serviços externos
│   ├── __init__.py
│   ├── supabase_service.py # Cliente Supabase (base de dados)
│   ├── evolution_service.py # Cliente Evolution API (WhatsApp)
│   ├── kommo_service.py    # Cliente Kommo CRM
│   └── calendar_service.py # Cliente Google Calendar
│
├── repositories/           # Camada de repositórios
│   ├── __init__.py
│   ├── lead_repository.py       # Gerenciamento de leads
│   ├── conversation_repository.py # Gerenciamento de conversas
│   ├── message_repository.py     # Gerenciamento de mensagens
│   └── followup_repository.py    # Sistema de follow-ups
│
├── utils/                  # Utilitários
│   ├── __init__.py
│   ├── formatters.py       # Formatadores (telefone, moeda, etc)
│   └── validators.py       # Validadores (CPF, email, etc)
│
├── tools/                  # Tools AGnO (próxima fase)
├── prompts/               # Prompts do sistema
└── migrations/            # Scripts SQL
```

## 🚀 Progresso da Implementação

### ✅ Fase 1: Estrutura Base (100%)
- [X] Estrutura de diretórios
- [X] Configurações centralizadas
- [X] Tipos e modelos Pydantic
- [X] Sistema de logging
- [X] Utilitários (formatters e validators)

### ✅ Fase 2: Services (100%)
- [X] **SupabaseService**: CRUD completo, retry logic, método especial get_last_messages()
- [X] **EvolutionAPIService**: Envio de mensagens, mídia, simulação de digitação
- [X] **KommoService**: Gestão de leads no CRM, pipeline stages, cache
- [X] **GoogleCalendarService**: Agendamento com Meet, FreeBusy API, timezone

### ✅ Fase 3: Repositories (100%)
- [X] **LeadRepository**: Qualificação, scoring, sincronização com CRM
- [X] **ConversationRepository**: Sessões com timeout, histórico formatado
- [X] **MessageRepository**: Multimodal, chunks tracking, busca full-text
- [X] **FollowUpRepository**: Follow-ups inteligentes, mensagens contextualizadas

### 🔄 Fase 4: Tools AGnO (Próxima)
- [ ] WhatsApp Tools (8 tools)
- [ ] Kommo Tools (6 tools)
- [ ] Calendar Tools (5 tools)
- [ ] Database Tools (6 tools)
- [ ] Media Tools (3 tools)
- [ ] Utility Tools (2 tools)

### 📝 Fase 5: SDRAgent Principal
- [ ] Integração com AGnO Framework
- [ ] Carregamento de prompts
- [ ] Orquestração de tools
- [ ] Lógica principal

## 🔧 Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Google Calendar
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
GOOGLE_PROJECT_ID=your-project-id

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://your-evolution-api.com
EVOLUTION_API_KEY=your-api-key
EVOLUTION_INSTANCE_NAME=your-instance

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Kommo CRM
KOMMO_SUBDOMAIN=yoursubdomain
KOMMO_LONG_LIVED_TOKEN=your-token
```

### Instalação

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar migrações SQL no Supabase
# (execute os arquivos em agente/migrations/)
```

## 📚 Uso

### Services

```python
from agente.services import get_supabase_service, get_evolution_service

# Obter serviço
supabase = get_supabase_service()
evolution = get_evolution_service()

# Usar serviço
lead = await supabase.get_lead_by_phone("+5511999999999")
await evolution.send_text_message("+5511999999999", "Olá!")
```

### Repositories

```python
from agente.repositories import get_lead_repository, get_conversation_repository

# Obter repository
lead_repo = get_lead_repository()
conv_repo = get_conversation_repository()

# Usar repository
lead = await lead_repo.create_lead("+5511999999999", "João Silva")
conversation, is_new = await conv_repo.get_or_create_conversation("+5511999999999", "session-123")
```

## 🏗️ Arquitetura

### Fluxo de Dados

```
WhatsApp → Evolution API → Webhook → SDRAgent → Repositories → Services → Database
                                         ↓
                                      Tools AGnO
                                         ↓
                                    Gemini 2.5 Pro
```

### Decisões Técnicas

1. **Arquitetura**: Toda lógica no prompt, tools apenas para ações externas
2. **Estado**: Usar apenas Supabase (não usar storage/memory do AGnO)
3. **Contexto**: Sempre recuperar últimas 100 mensagens
4. **Follow-ups**: 30min → 24h → marcar como "NÃO INTERESSADO"
5. **Reasoning**: Ativar apenas para situações complexas

## 🧪 Testes

```bash
# Rodar testes unitários
pytest tests/unit/

# Rodar testes de integração
pytest tests/integration/

# Rodar com coverage
pytest --cov=agente --cov-report=html
```

## 📖 Documentação Adicional

- [Análise Completa](./NOVO_AGENTE_SDR_ANALISE.md) - Documento detalhado da arquitetura
- [Evolution API Docs](https://doc.evolution-api.com/v2)
- [Kommo API Docs](https://developers.kommo.com)
- [AGnO Framework](https://docs.agno.dev)

## 🤝 Contribuindo

1. Sempre use type hints
2. Adicione docstrings em todos os métodos
3. Use async/await para operações I/O
4. Siga os padrões estabelecidos
5. Teste antes de commitar